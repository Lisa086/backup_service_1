FROM python:3.11-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY auth_service/ /app/auth_service/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt argon2-cffi boto3

EXPOSE 8001

CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
