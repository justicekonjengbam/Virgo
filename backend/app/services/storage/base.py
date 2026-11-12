from abc import ABC, abstractmethod


class BaseStorageService(ABC):
    """Abstract interface for private document storage."""

    @abstractmethod
    def upload(self, file_data: bytes, key: str, content_type: str, metadata: dict | None = None) -> str:
        """Uploads file data to storage under key. Returns key."""
        pass

    @abstractmethod
    def generate_signed_url(self, key: str, expires_in_seconds: int = 300) -> str:
        """Generates a short-lived signed URL or token URL for authorized preview."""
        pass

    @abstractmethod
    def download(self, key: str) -> tuple[bytes, str]:
        """Downloads file data and returns (bytes, content_type)."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Deletes file under key. Returns True if deleted or did not exist."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Checks if file exists under key."""
        pass

