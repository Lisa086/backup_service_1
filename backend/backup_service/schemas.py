from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    storage_path: str
    provider: str
    uploaded_at: datetime

class FileListResponse(BaseModel):
    files: list[str]
    count: int

class FileInfo(BaseModel):
    filename: str
    size: int
    provider: str
    uploaded_at: datetime
    user_id: str
