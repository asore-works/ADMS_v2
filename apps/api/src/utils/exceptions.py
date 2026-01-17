"""Custom exceptions and exception handlers"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class ADMSException(Exception):
    """Base exception for ADMS application"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail: str = "An unexpected error occurred"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class NotFoundError(ADMSException):
    """Resource not found"""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"


class BadRequestError(ADMSException):
    """Bad request"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"


class UnauthorizedError(ADMSException):
    """Authentication required"""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication required"


class ForbiddenError(ADMSException):
    """Access denied"""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Access denied"


class ConflictError(ADMSException):
    """Resource conflict"""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource conflict"


class ValidationError(ADMSException):
    """Validation error"""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Validation error"


class ServiceUnavailableError(ADMSException):
    """Service unavailable"""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable"


async def adms_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle ADMS custom exceptions"""
    if isinstance(exc, ADMSException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "type": exc.__class__.__name__,
            },
        )
    # Fallback for unexpected exceptions
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "type": "InternalServerError",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with FastAPI app

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(ADMSException, adms_exception_handler)
