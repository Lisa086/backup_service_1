import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
import os
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)

class CloudStorageProvider:
    def upload_file(self, file: BinaryIO, filename: str) -> str:
        raise NotImplementedError
    
    def download_file(self, filename: str) -> bytes:
        raise NotImplementedError
    
    def delete_file(self, filename: str) -> bool:
        raise NotImplementedError
    
    def list_files(self) -> list:
        raise NotImplementedError

class S3Provider(CloudStorageProvider):
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not all([self.aws_access_key, self.aws_secret_key, self.bucket_name]):
            raise ValueError("AWS ключи не настроены. Установите AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY и AWS_BUCKET_NAME")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region
        )
    
    def upload_file(self, file: BinaryIO, filename: str) -> str:
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, filename)
            return f"s3://{self.bucket_name}/{filename}"
        except Exception as e:
            logger.error(f"Ошибка загрузки в S3: {e}")
            raise Exception("Ошибка при загрузке в облако S3")
    
    def download_file(self, filename: str) -> bytes:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Ошибка скачивания из S3: {e}")
            raise Exception("Ошибка при скачивании из облака S3")
    
    def delete_file(self, filename: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления из S3: {e}")
            raise Exception("Ошибка при удалении из облака S3")
    
    def list_files(self) -> list:
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            logger.error(f"Ошибка получения списка из S3: {e}")
            raise Exception("Ошибка при получении списка из облака S3")

class AzureBlobProvider(CloudStorageProvider):
    def __init__(self):
        self.connection_string = os.getenv('AZURE_CONNECTION_STRING')
        self.container_name = os.getenv('AZURE_CONTAINER_NAME')
        
        if not all([self.connection_string, self.container_name]):
            raise ValueError("Параметры Azure не настроены. Установите AZURE_CONNECTION_STRING и AZURE_CONTAINER_NAME")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
    
    def upload_file(self, file: BinaryIO, filename: str) -> str:
        try:
            blob_client = self.container_client.get_blob_client(filename)
            blob_client.upload_blob(file, overwrite=True)
            return f"azure://{self.container_name}/{filename}"
        except Exception as e:
            logger.error(f"Ошибка загрузки в Azure: {e}")
            raise Exception("Ошибка при загрузке в облако Azure")
    
    def download_file(self, filename: str) -> bytes:
        try:
            blob_client = self.container_client.get_blob_client(filename)
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Ошибка скачивания из Azure: {e}")
            raise Exception("Ошибка при скачивании из облака Azure")
    
    def delete_file(self, filename: str) -> bool:
        try:
            blob_client = self.container_client.get_blob_client(filename)
            blob_client.delete_blob()
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления из Azure: {e}")
            raise Exception("Ошибка при удалении из облака Azure")
    
    def list_files(self) -> list:
        try:
            return [blob.name for blob in self.container_client.list_blobs()]
        except Exception as e:
            logger.error(f"Ошибка получения списка из Azure: {e}")
            raise Exception("Ошибка при получении списка из облака Azure")

class GCSProvider(CloudStorageProvider):
    def __init__(self):
        self.credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.bucket_name = os.getenv('GOOGLE_BUCKET_NAME')
        
        if not self.bucket_name:
            raise ValueError("Параметры GCS не настроены. Установите GOOGLE_BUCKET_NAME и GOOGLE_CREDENTIALS_PATH")
        
        if self.credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
        
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)
    
    def upload_file(self, file: BinaryIO, filename: str) -> str:
        try:
            blob = self.bucket.blob(filename)
            blob.upload_from_file(file)
            return f"gs://{self.bucket_name}/{filename}"
        except Exception as e:
            logger.error(f"Ошибка загрузки в GCS: {e}")
            raise Exception("Ошибка при загрузке в облако GCS")
    
    def download_file(self, filename: str) -> bytes:
        try:
            blob = self.bucket.blob(filename)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Ошибка скачивания из GCS: {e}")
            raise Exception("Ошибка при скачивании из облака GCS")
    
    def delete_file(self, filename: str) -> bool:
        try:
            blob = self.bucket.blob(filename)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления из GCS: {e}")
            raise Exception("Ошибка при удалении из облака GCS")
    
    def list_files(self) -> list:
        try:
            blobs = self.storage_client.list_blobs(self.bucket_name)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Ошибка получения списка из GCS: {e}")
            raise Exception("Ошибка при получении списка из облака GCS")

def get_provider(provider_type: str) -> CloudStorageProvider:
    providers = {
        "s3": S3Provider,
        "azure": AzureBlobProvider,
        "gcs": GCSProvider
    }
    
    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(f"Неизвестный провайдер: {provider_type}")
    
    return provider_class()
