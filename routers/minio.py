from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from minio import Minio
from minio.error import S3Error
import mimetypes
import urllib.parse
import os
import uuid

router = APIRouter()

# MinIO клиент
minio_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False  # Установите True, если MinIO работает через HTTPS
)


bucket_name = "images-bucket"

# Проверяем наличие бакета, создаем если отсутствует
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)


@router.post("/upload", tags=["MinIO"])
async def upload_image(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}_{file.filename}"
        minio_client.put_object(
            bucket_name,
            file_name,
            file.file,
            length=-1,
            part_size=100 * 1024 * 1024,
            content_type=file.content_type,
        )
        return {"file_id": file_id, "file_name": file_name}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}", tags=["MinIO"])
async def get_image(file_id: str):
    try:
        # Ищем объект с заданным префиксом
        objects = list(minio_client.list_objects(bucket_name, prefix=file_id))
        if not objects:
            raise HTTPException(status_code=404, detail="File not found")
        
        obj = objects[0]

        # Получаем объект из MinIO
        file_data = minio_client.get_object(bucket_name, obj.object_name)

        # Определяем MIME-тип файла
        mime_type, _ = mimetypes.guess_type(obj.object_name)
        if not mime_type:
            mime_type = "application/octet-stream"  # Тип по умолчанию

        # Кодируем имя файла для Content-Disposition
        encoded_filename = urllib.parse.quote(obj.object_name)

        # Возвращаем объект как поток
        return StreamingResponse(
            file_data,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            },
        )
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}", tags=["MinIO"])
async def delete_image(file_id: str):
    try:
        objects = list(minio_client.list_objects(bucket_name, prefix=file_id))
        if not objects:
            raise HTTPException(status_code=404, detail="File not found")
        
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
        return {"message": "File deleted successfully"}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{file_id}", tags=["MinIO"])
async def update_image(file_id: str, file: UploadFile = File(...)):
    try:
        # Проверяем, существует ли файл
        objects = list(minio_client.list_objects(bucket_name, prefix=file_id))
        if not objects:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Удаляем старый файл
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
        
        # Загрузка нового файла
        file_name = f"{file_id}_{file.filename}"
        minio_client.put_object(
            bucket_name,
            file_name,
            file.file,
            length=-1,
            part_size=100 * 1024 * 1024,
            content_type=file.content_type,
        )
        return {"message": "File updated successfully", "file_name": file_name}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))