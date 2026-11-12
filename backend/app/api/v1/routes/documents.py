from fastapi import APIRouter, HTTPException, Response, status

from app.core.config import get_settings
from app.services.storage import get_storage_service
from app.services.storage.local import LocalStorageService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/preview/{token}", response_class=Response)
def preview_document(token: str) -> Response:
    """
    Renders a document securely using a verified, short-lived signed preview token.
    Access is strictly restricted to valid token holders. No public bucket URLs exist.
    """
    settings = get_settings()
    key, error = LocalStorageService.verify_preview_token(token, settings.jwt_secret_key)
    if error or not key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error or "Invalid or expired document preview token.",
        )

    storage = get_storage_service()
    try:
        file_bytes, content_type = storage.download(key)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found.")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to retrieve document.") from exc

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "private, no-cache, no-store, must-revalidate",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox",
            "X-Frame-Options": "SAMEORIGIN",
            "Cross-Origin-Resource-Policy": "same-origin",
        },
    )

