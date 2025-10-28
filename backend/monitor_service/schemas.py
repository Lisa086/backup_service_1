from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class HealthCheck(BaseModel):
    status: str
    uptime: float
    timestamp: datetime

class LogEntry(BaseModel):
    level: str
    service: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class MetricsSnapshot(BaseModel):
    total_requests: int
    active_users: int
    total_uploads: int
    total_downloads: int
    storage_usage: Dict[str, int]
    timestamp: datetime

