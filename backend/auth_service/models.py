from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserInDB(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

