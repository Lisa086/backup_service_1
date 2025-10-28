from pydantic import BaseModel, EmailStr
from typing import Optional

class ConfigBase(BaseModel):
    default_provider: str = "local"
    
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_bucket: Optional[str] = None
    aws_region: Optional[str] = "us-east-1"
    
    azure_connection_string: Optional[str] = None
    azure_container: Optional[str] = None
    
    gcs_project_id: Optional[str] = None
    gcs_bucket: Optional[str] = None
    gcs_credentials_path: Optional[str] = None
    
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    email: Optional[EmailStr] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: Optional[bool] = True

class ConfigCreate(ConfigBase):
    pass

class ConfigUpdate(ConfigBase):
    pass

class ConfigResponse(ConfigBase):
    user_id: str
    
    class Config:
        from_attributes = True
