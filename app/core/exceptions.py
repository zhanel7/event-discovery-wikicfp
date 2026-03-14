"""Custom exceptions and global exception handlers."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class ConflictError(AppException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class BadRequestError(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


def _error_detail(message: str, key: str | None = None) -> dict:
    d: dict = {"msg": message}
    if key is not None:
        d["loc"] = ["body", key]
    return d


def _app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def _validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for e in exc.errors():
        loc = e.get("loc", ())
        # Remove "body" from loc for cleaner messages
        loc = [x for x in loc if x != "body"]
        errors.append({"loc": loc, "msg": e.get("msg", "Validation error")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )


def _generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app):
    """Register custom exception handlers on the FastAPI app."""
    app.add_exception_handler(AppException, _app_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(Exception, _generic_exception_handler)
