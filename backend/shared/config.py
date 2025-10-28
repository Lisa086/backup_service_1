from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://mongodb:27017"
    redis_url: str = "redis://redis:6379"
    secret_key: str = "секретный-ключВпродакшене"
    
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"
    
    azure_connection_string: str = ""
    azure_container_name: str = ""
    
    google_credentials_path: str = ""
    google_bucket_name: str = ""
    
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
