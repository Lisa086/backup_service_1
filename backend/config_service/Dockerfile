FROM python:3.11-slim

WORKDIR /app

COPY shared/ /app/shared/

COPY auth_service/ /app/auth_service/

COPY config_service/ /app/config_service/

RUN pip install --no-cache-dir -r /app/config_service/requirements.txt

EXPOSE 8003

CMD ["uvicorn", "config_service.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
