from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserConfigInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    backup_schedule: Optional[str] = None  
    default_provider: str = "s3"
    notification_preferences: Dict[str, bool] = {
        "email": True,
        "telegram": False,
        "push": True
    }
    storage_settings: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

