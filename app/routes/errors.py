from fastapi import HTTPException

from app.services.errors import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ServiceError,
)

_STATUS = {
    NotFoundError: 404,
    PermissionDeniedError: 403,
    ConflictError: 409,
    AuthenticationError: 401,
}


def to_http(exc: ServiceError) -> HTTPException:
    """Translate a service-layer error into the matching HTTP error."""
    return HTTPException(status_code=_STATUS.get(type(exc), 400), detail=str(exc))
