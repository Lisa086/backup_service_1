FROM python:3.11-slim

WORKDIR /app

# Copy shared files FIRST
COPY shared/ /app/shared/

# Copy auth_service for dependencies
COPY auth_service/ /app/auth_service/

# Copy service files
COPY alert_service/ /app/alert_service/

# Install dependencies from alert_service folder
RUN pip install --no-cache-dir -r /app/alert_service/requirements.txt

# Expose port
EXPOSE 8004

# Run the service
CMD ["uvicorn", "alert_service.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]
