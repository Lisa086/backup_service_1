from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .schemas import ConfigCreate, ConfigUpdate
from datetime import datetime

async def create_config(db: AsyncIOMotorClient, user_id: str, config: ConfigCreate) -> dict:
    config_dict = config.dict()
    config_dict["user_id"] = user_id
    config_dict["created_at"] = datetime.utcnow()
    config_dict["updated_at"] = datetime.utcnow()
    result = await db.backup_db.configs.insert_one(config_dict)
    config_dict["_id"] = str(result.inserted_id)
    return config_dict

async def get_config_by_user(db: AsyncIOMotorClient, user_id: str) -> Optional[dict]:
    config = await db.backup_db.configs.find_one({"user_id": user_id})
    if config:
        config["_id"] = str(config["_id"])
    return config

async def update_config(db: AsyncIOMotorClient, user_id: str, config: ConfigUpdate) -> Optional[dict]:
    update_data = {k: v for k, v in config.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    result = await db.backup_db.configs.find_one_and_update(
        {"user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    if result:
        result["_id"] = str(result["_id"])
    return result
