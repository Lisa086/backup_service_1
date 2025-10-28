from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import connect_to_mongo, close_mongo_connection, get_database
from auth_service.dependencies import get_current_user
from .metrics import metrics_collector, get_metrics
from .schemas import HealthCheck, LogEntry, MetricsSnapshot

app = FastAPI(title="Monitor Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_time = time.time()

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"service": "Monitor Service", "status": "работает"}

@app.get("/health", response_model=HealthCheck)
async def health_check():
    uptime = time.time() - start_time
    return HealthCheck(
        status="здоровый",
        uptime=uptime,
        timestamp=datetime.utcnow()
    )

@app.get("/metrics")
async def prometheus_metrics():
    return Response(content=get_metrics(), media_type="text/plain")

@app.post("/logs", status_code=201)
async def create_log(
    log: LogEntry,
    db = Depends(get_database)
):
    log_dict = log.dict()
    await db.backup_db.logs.insert_one(log_dict)
    return {"message": "Лог успешно создан"}

@app.get("/logs")
async def get_logs(
    limit: int = 100,
    service: str = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    query = {}
    if service:
        query["service"] = service
    logs = await db.backup_db.logs.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"logs": logs, "count": len(logs)}

@app.get("/metrics/snapshot", response_model=MetricsSnapshot)
async def get_metrics_snapshot(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    total_uploads = await db.backup_db.files.count_documents({})
    active_users_count = await db.backup_db.users.count_documents({"is_active": True})
    return MetricsSnapshot(
        total_requests=0,
        active_users=active_users_count,
        total_uploads=total_uploads,
        total_downloads=0,
        storage_usage={"s3": 0, "azure": 0, "gcs": 0},
        timestamp=datetime.utcnow()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)