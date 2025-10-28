from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailAlert(BaseModel):
    to_email: EmailStr
    subject: str
    body: str

class TelegramAlert(BaseModel):
    message: str
    chat_id: Optional[str] = None

class AlertResponse(BaseModel):
    success: bool
    message: str

