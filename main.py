from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import error_logs, notifications, files, minio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://uteam.top", "https://uteam.top/api", "http://localhost:4200", "https://ucomand.ru"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(error_logs.router, prefix="/log-error",  tags=["Error Logs"] )
app.include_router(notifications.router, prefix="/notify", tags=["Notifications"])
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(minio.router, prefix="/minio", tags=["MinIO"]) 