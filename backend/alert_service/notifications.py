import aiosmtplib
from email.message import EmailMessage
import os
import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using async SMTP client"""
        try:
            msg = EmailMessage()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.set_content(body, subtype='html')
            
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication error: {e}")
            return False
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if self.bot_token:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            self.base_url = None
    
    async def send_message(self, message: str, chat_id: Optional[str] = None) -> bool:
        """Send Telegram message with proper timeout and error handling"""
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return False
            
        try:
            target_chat_id = chat_id or self.chat_id
            if not target_chat_id:
                logger.error("Telegram chat_id not provided")
                return False
                
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": target_chat_id, "text": message}
                )
                
                if response.status_code == 200:
                    logger.info(f"Telegram message sent successfully to {target_chat_id}")
                    return True
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException as e:
            logger.error(f"Telegram timeout error: {e}")
            return False
        except httpx.HTTPError as e:
            logger.error(f"Telegram HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False

email_notifier = EmailNotifier()
telegram_notifier = TelegramNotifier()