from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import connect_to_mongo, close_mongo_connection, get_database
from auth_service.dependencies import get_current_user
from .schemas import ConfigCreate, ConfigUpdate, ConfigResponse

app = FastAPI(title="Config Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"service": "Config Service", "status": "работает"}

@app.get("/config", response_model=ConfigResponse)
async def get_config(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    config = await db.backup_db.configs.find_one({"user_id": current_user["user_id"]})
    if not config:
        raise HTTPException(status_code=404, detail="Конфигурация не найдена")
    config["_id"] = str(config["_id"])
    return config

@app.post("/config", response_model=ConfigResponse)
async def create_config(
    config_data: ConfigCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    existing_config = await db.backup_db.configs.find_one({"user_id": current_user["user_id"]})
    if existing_config:
        raise HTTPException(status_code=400, detail="Конфигурация уже существует. Используйте PUT для обновления")
    config_dict = config_data.dict()
    config_dict["user_id"] = current_user["user_id"]
    result = await db.backup_db.configs.insert_one(config_dict)
    config_dict["_id"] = str(result.inserted_id)
    return config_dict

@app.put("/config", response_model=ConfigResponse)
async def update_config(
    config_data: ConfigUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    existing_config = await db.backup_db.configs.find_one({"user_id": current_user["user_id"]})
    if not existing_config:
        config_dict = config_data.dict()
        config_dict["user_id"] = current_user["user_id"]
        result = await db.backup_db.configs.insert_one(config_dict)
        config_dict["_id"] = str(result.inserted_id)
        return config_dict
    update_data = {k: v for k, v in config_data.dict().items() if v is not None}
    await db.backup_db.configs.update_one(
        {"user_id": current_user["user_id"]},
        {"$set": update_data}
    )
    updated_config = await db.backup_db.configs.find_one({"user_id": current_user["user_id"]})
    updated_config["_id"] = str(updated_config["_id"])
    return updated_config

@app.delete("/config")
async def delete_config(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    result = await db.backup_db.configs.delete_one({"user_id": current_user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Конфигурация не найдена")
    return {"message": "Конфигурация успешно удалена"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
