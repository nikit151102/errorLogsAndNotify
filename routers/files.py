from fastapi import File, UploadFile, APIRouter
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse  # Make sure FileResponse is imported
import os
import mimetypes

router = APIRouter()

# Указываем директорию, куда будем сохранять файлы
UPLOAD_DIRECTORY = "uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Эндпоинт для отправки файла
@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    
    # Сохраняем файл
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"filename": file.filename, "message": "File uploaded successfully"}

# Эндпоинт для перезаписи файла
@router.post("/overwriteFile/") 
async def overwrite_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    
    # Перезаписываем файл (если файл существует)
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"filename": file.filename, "message": "File overwritten successfully"}

# Эндпоинт для получения файла
@router.get("/files/{filename}")
async def get_file(filename: str):
    file_location = os.path.join(UPLOAD_DIRECTORY, filename)
    
    if os.path.exists(file_location):
        mime_type, _ = mimetypes.guess_type(file_location)
        if mime_type is None:
            mime_type = "application/octet-stream"  
        
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"  
        }

        return FileResponse(file_location, media_type=mime_type, headers=headers)
    
    raise HTTPException(status_code=404, detail="File not found")

# Эндпоинт для получения всех файлов в директории
@router.get("/files/")
async def list_files():
    files = os.listdir(UPLOAD_DIRECTORY)
    if not files:
        return {"message": "No files found"}
    return {"files": files}

# Эндпоинт для удаления файла
@router.delete("/files/{filename}")
async def delete_file(filename: str):
    file_location = os.path.join(UPLOAD_DIRECTORY, filename)
    if os.path.exists(file_location):
        os.remove(file_location)
        return {"message": f"File '{filename}' deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")