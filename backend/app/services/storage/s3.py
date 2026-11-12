from app.core.config import get_settings
from app.services.storage.base import BaseStorageService


class S3StorageService(BaseStorageService):
    """
    Private object storage service for AWS S3 and Cloudflare R2.
    Enforces server-side encryption and signed URLs for document access.
    """

    def __init__(self):
        settings = get_settings()
        self.bucket = settings.s3_bucket_name
        self.region = settings.s3_region
        self.endpoint_url = settings.s3_endpoint_url
        self.access_key = settings.s3_access_key_id
        self.secret_key = settings.s3_secret_access_key

        try:
            import boto3
            from botocore.config import Config
        except ImportError as exc:
            raise RuntimeError("boto3 is required for S3StorageService. Run `pip install boto3`.") from exc

        client_kwargs = {
            "region_name": self.region,
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
            "config": Config(signature_version="s3v4"),
        }
        if self.endpoint_url:
            client_kwargs["endpoint_url"] = self.endpoint_url

        self.client = boto3.client("s3", **client_kwargs)

    def upload(self, file_data: bytes, key: str, content_type: str, metadata: dict | None = None) -> str:
        upload_kwargs = {
            "Bucket": self.bucket,
            "Key": key,
            "Body": file_data,
            "ContentType": content_type,
            "ServerSideEncryption": "AES256",  # Provider-level encryption at rest
        }
        if metadata:
            upload_kwargs["Metadata"] = {k: str(v) for k, v in metadata.items()}

        self.client.put_object(**upload_kwargs)
        return key

    def download(self, key: str) -> tuple[bytes, str]:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        data = response["Body"].read()
        content_type = response.get("ContentType", "application/octet-stream")
        return data, content_type

    def delete(self, key: str) -> bool:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return True

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def generate_signed_url(self, key: str, expires_in_seconds: int = 300) -> str:
        """Generates a short-lived presigned GET URL with strict expiration."""
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in_seconds,
        )

