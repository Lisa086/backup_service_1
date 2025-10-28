from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_service.dependencies import get_current_user
from .notifications import email_notifier, telegram_notifier
from .schemas import EmailAlert, TelegramAlert, AlertResponse

app = FastAPI(title="Alert Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "Alert Service", "status": "running"}

@app.post("/send-email", response_model=AlertResponse)
async def send_email_alert(
    alert: EmailAlert,
    current_user: dict = Depends(get_current_user)
):
    success = email_notifier.send_email(alert.to_email, alert.subject, alert.body)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return AlertResponse(success=True, message="Email sent successfully")

@app.post("/send-telegram", response_model=AlertResponse)
async def send_telegram_alert(
    alert: TelegramAlert,
    current_user: dict = Depends(get_current_user)
):
    success = await telegram_notifier.send_message(alert.message, alert.chat_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send Telegram message")
    
    return AlertResponse(success=True, message="Telegram message sent successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

