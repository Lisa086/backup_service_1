from prometheus_client import Counter, Histogram, Gauge, generate_latest
from typing import Dict
import time

request_count = Counter('http_requests_total', 'Общее число HTTP запросов', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'Время обработки HTTP запроса', ['method', 'endpoint'])
active_users = Gauge('active_users_total', 'Количество активных пользователей')
file_uploads = Counter('file_uploads_total', 'Всего загружено файлов', ['provider', 'status'])
file_downloads = Counter('file_downloads_total', 'Всего скачано файлов', ['provider', 'status'])
storage_usage = Gauge('storage_usage_bytes', 'Использование места хранения в байтах', ['provider'])

def get_metrics() -> bytes:
    return generate_latest()

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, status: int):
        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    
    def record_duration(self, method: str, endpoint: str, duration: float):
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def update_active_users(self, count: int):
        active_users.set(count)
    
    def record_upload(self, provider: str, success: bool):
        status = "success" if success else "failed"
        file_uploads.labels(provider=provider, status=status).inc()
    
    def record_download(self, provider: str, success: bool):
        status = "success" if success else "failed"
        file_downloads.labels(provider=provider, status=status).inc()
    
    def update_storage(self, provider: str, bytes_used: int):
        storage_usage.labels(provider=provider).set(bytes_used)

metrics_collector = MetricsCollector()