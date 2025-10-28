from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.auth_utils import get_password_hash, verify_password
from .schemas import UserCreate
from bson import ObjectId

async def create_user(db: AsyncIOMotorClient, user: UserCreate) -> dict:
    user_dict = {
        "email": user.email,
        "username": user.username,
        "hashed_password": get_password_hash(user.password),
        "is_active": True,
        "is_superuser": False
    }
    result = await db.backup_db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    return user_dict

async def get_user_by_email(db: AsyncIOMotorClient, email: str) -> Optional[dict]:
    user = await db.backup_db.users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
    return user

async def authenticate_user(db: AsyncIOMotorClient, email: str, password: str) -> Optional[dict]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

