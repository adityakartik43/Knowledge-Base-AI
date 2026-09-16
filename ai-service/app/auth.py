from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import get_settings

service_api_key_header = APIKeyHeader(name="X-Service-Api-Key", auto_error=False)


def verify_service_api_key(
    api_key: str | None = Security(service_api_key_header),
) -> None:
    settings = get_settings()

    if not api_key or api_key != settings.service_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing service API key",
        )
