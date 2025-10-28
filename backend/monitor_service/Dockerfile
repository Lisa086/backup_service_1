FROM python:3.11-slim

WORKDIR /app

COPY shared/ /app/shared/

COPY auth_service/ /app/auth_service/

COPY monitor_service/ /app/monitor_service/

RUN pip install --no-cache-dir -r /app/monitor_service/requirements.txt

EXPOSE 8005

CMD ["uvicorn", "monitor_service.main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]
