FROM python:3.11-slim

WORKDIR /app

COPY shared/ /app/shared/

COPY auth_service/ /app/auth_service/

COPY backup_service/ /app/backup_service/

RUN pip install --no-cache-dir -r /app/backup_service/requirements.txt

EXPOSE 8002

CMD ["uvicorn", "backup_service.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
