from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timezone
from pathlib import Path
import sys
import os
import io
import re
import httpx
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs_storage

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import connect_to_mongo, close_mongo_connection, get_database
from auth_service.dependencies import get_current_user
from .schemas import FileUploadResponse, FileListResponse

REQUIRED_ENV_VARS = ["MONGODB_URL"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise ValueError(f"Переменная окружения {var} не установлена")

app = FastAPI(title="Backup Service", version="1.0.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".zip", ".doc", ".docx", ".csv", ".xlsx", ".mp4", ".mp3"
}
ALLOWED_MIME_TYPES = {
    "text/plain", "application/pdf", "image/png", "image/jpeg", 
    "application/zip", "application/msword", "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

LOCAL_STORAGE_PATH = Path("/app/local_storage")
LOCAL_STORAGE_PATH.mkdir(exist_ok=True, parents=True)

def secure_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    filename = filename.strip('. ')
    if not filename:
        raise HTTPException(status_code=400, detail="Недопустимое имя файла")
    return filename

def validate_file(filename: str, content: bytes, content_type: str):
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Тип файла не разрешен. Разрешенные типы: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE / 1024 / 1024}МБ"
        )

async def get_user_config(user_id: str):
    config_url = "http://config_service:8003/config"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                config_url,
                headers={"X-User-ID": user_id}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Ошибка получения конфигурации: {e}")
    return None

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"service": "Backup Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "здоровый", "service": "backup_service"}

@app.post("/upload", response_model=FileUploadResponse)
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    provider: str = Query("local", description="Провайдер хранилища: local, s3, azure, gcs"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        file_content = await file.read()
        safe_filename = secure_filename(file.filename)
        validate_file(safe_filename, file_content, file.content_type)
        
        file_size = len(file_content)
        file_stream = io.BytesIO(file_content)
        
        if provider == "local":
            user_folder = LOCAL_STORAGE_PATH / current_user["user_id"]
            user_folder.mkdir(exist_ok=True, parents=True)
            file_path = user_folder / safe_filename
            with open(file_path, "wb") as f:
                f.write(file_content)
            storage_path = str(file_path)
        else:
            user_config = await get_user_config(current_user["user_id"])
            if not user_config:
                raise HTTPException(
                    status_code=400, 
                    detail="Пожалуйста, настройте параметры облачного хранилища в разделе Настройки"
                )
            if provider == "s3":
                if not all([user_config.get("aws_access_key"), user_config.get("aws_secret_key"), user_config.get("aws_bucket")]):
                    raise HTTPException(status_code=400, detail="AWS ключи не настроены")
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=user_config["aws_access_key"],
                    aws_secret_access_key=user_config["aws_secret_key"],
                    region_name=user_config.get("aws_region", "us-east-1")
                )
                s3_client.upload_fileobj(file_stream, user_config["aws_bucket"], safe_filename)
                storage_path = f"s3://{user_config['aws_bucket']}/{safe_filename}"
            elif provider == "azure":
                if not all([user_config.get("azure_connection_string"), user_config.get("azure_container")]):
                    raise HTTPException(status_code=400, detail="Azure параметры не настроены")
                blob_service = BlobServiceClient.from_connection_string(user_config["azure_connection_string"])
                blob_client = blob_service.get_blob_client(
                    container=user_config["azure_container"],
                    blob=safe_filename
                )
                file_stream.seek(0)
                blob_client.upload_blob(file_stream, overwrite=True)
                storage_path = f"azure://{user_config['azure_container']}/{safe_filename}"
            elif provider == "gcs":
                if not all([user_config.get("gcs_project_id"), user_config.get("gcs_bucket")]):
                    raise HTTPException(status_code=400, detail="Google Cloud параметры не настроены")
                client = gcs_storage.Client(project=user_config["gcs_project_id"])
                bucket = client.bucket(user_config["gcs_bucket"])
                blob = bucket.blob(safe_filename)
                file_stream.seek(0)
                blob.upload_from_file(file_stream)
                storage_path = f"gs://{user_config['gcs_bucket']}/{safe_filename}"
            else:
                raise HTTPException(status_code=400, detail="Неподдерживаемый провайдер")
        
        file_metadata = {
            "filename": safe_filename,
            "size": file_size,
            "storage_path": storage_path,
            "provider": provider,
            "user_id": current_user["user_id"],
            "uploaded_at": datetime.now(timezone.utc)
        }
        await db.backup_db.files.insert_one(file_metadata)
        
        return FileUploadResponse(
            filename=safe_filename,
            size=file_size,
            storage_path=storage_path,
            provider=provider,
            uploaded_at=file_metadata["uploaded_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

@app.get("/download/{filename}")
@limiter.limit("20/minute")
async def download_file(
    request: Request,
    filename: str,
    provider: str = Query("local", description="Провайдер хранилища: local, s3, azure, gcs"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        safe_filename = secure_filename(filename)
        file_doc = await db.backup_db.files.find_one({
            "filename": safe_filename,
            "user_id": current_user["user_id"],
            "provider": provider
        })
        if not file_doc:
            raise HTTPException(status_code=404, detail="Файл не найден или доступ запрещен")
        if provider == "local":
            user_folder = LOCAL_STORAGE_PATH / current_user["user_id"]
            file_path = user_folder / safe_filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Файл не найден на диске")
            with open(file_path, "rb") as f:
                file_content = f.read()
        else:
            user_config = await get_user_config(current_user["user_id"])
            if not user_config:
                raise HTTPException(status_code=400, detail="Конфигурация не найдена")
            if provider == "s3":
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=user_config["aws_access_key"],
                    aws_secret_access_key=user_config["aws_secret_key"],
                    region_name=user_config.get("aws_region", "us-east-1")
                )
                response = s3_client.get_object(Bucket=user_config["aws_bucket"], Key=safe_filename)
                file_content = response['Body'].read()
            elif provider == "azure":
                blob_service = BlobServiceClient.from_connection_string(user_config["azure_connection_string"])
                blob_client = blob_service.get_blob_client(
                    container=user_config["azure_container"],
                    blob=safe_filename
                )
                file_content = blob_client.download_blob().readall()
            elif provider == "gcs":
                client = gcs_storage.Client(project=user_config["gcs_project_id"])
                bucket = client.bucket(user_config["gcs_bucket"])
                blob = bucket.blob(safe_filename)
                file_content = blob.download_as_bytes()
            else:
                raise HTTPException(status_code=400, detail="Неподдерживаемый провайдер")
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка скачивания: {str(e)}")

@app.delete("/delete/{filename}")
@limiter.limit("10/minute")
async def delete_file(
    request: Request,
    filename: str,
    provider: str = Query("local", description="Провайдер хранилища: local, s3, azure, gcs"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        safe_filename = secure_filename(filename)
        file_doc = await db.backup_db.files.find_one({
            "filename": safe_filename,
            "user_id": current_user["user_id"],
            "provider": provider
        })
        if not file_doc:
            raise HTTPException(status_code=404, detail="Файл не найден или доступ запрещен")
        if provider == "local":
            user_folder = LOCAL_STORAGE_PATH / current_user["user_id"]
            file_path = user_folder / safe_filename
            if file_path.exists():
                file_path.unlink()
        else:
            user_config = await get_user_config(current_user["user_id"])
            if not user_config:
                raise HTTPException(status_code=400, detail="Конфигурация не найдена")
            if provider == "s3":
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=user_config["aws_access_key"],
                    aws_secret_access_key=user_config["aws_secret_key"],
                    region_name=user_config.get("aws_region", "us-east-1")
                )
                s3_client.delete_object(Bucket=user_config["aws_bucket"], Key=safe_filename)
            elif provider == "azure":
                blob_service = BlobServiceClient.from_connection_string(user_config["azure_connection_string"])
                blob_client = blob_service.get_blob_client(
                    container=user_config["azure_container"],
                    blob=safe_filename
                )
                blob_client.delete_blob()
            elif provider == "gcs":
                client = gcs_storage.Client(project=user_config["gcs_project_id"])
                bucket = client.bucket(user_config["gcs_bucket"])
                blob = bucket.blob(safe_filename)
                blob.delete()
        await db.backup_db.files.delete_one({
            "filename": safe_filename,
            "user_id": current_user["user_id"]
        })
        return {"message": f"Файл {safe_filename} успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления: {str(e)}")

@app.get("/list", response_model=FileListResponse)
@limiter.limit("30/minute")
async def list_files(
    request: Request,
    provider: str = Query("local", description="Провайдер хранилища: local, s3, azure, gcs"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        user_files = await db.backup_db.files.find({
            "user_id": current_user["user_id"],
            "provider": provider
        }).to_list(length=1000)
        filenames = [f["filename"] for f in user_files]
        return FileListResponse(files=filenames, count=len(filenames))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)