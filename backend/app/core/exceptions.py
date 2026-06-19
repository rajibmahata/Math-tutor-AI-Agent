"""
Custom exception handlers for consistent error responses.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 400, error_type: str = "app_error"):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            status_code=404,
            error_type="not_found",
        )


class DuplicateError(AppException):
    def __init__(self, resource: str, field: str):
        super().__init__(
            message=f"{resource} with this {field} already exists",
            status_code=409,
            error_type="duplicate",
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401, error_type="unauthorized")


class ForbiddenError(AppException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, status_code=403, error_type="forbidden")


class LLMProviderError(AppException):
    def __init__(self, provider: str, detail: str):
        super().__init__(
            message=f"LLM provider '{provider}' error: {detail}",
            status_code=503,
            error_type="llm_provider_error",
        )


def problem_detail(
    status: int,
    title: str,
    detail: str,
    error_type: str = "about:blank",
    instance: str = "",
    errors: list = None,
) -> dict:
    """RFC 7807 Problem Details format."""
    body = {
        "type": f"https://api.ganitmitra.com/errors/{error_type}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }
    if errors:
        body["errors"] = errors
    return body


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=problem_detail(
                status=exc.status_code,
                title=exc.error_type.replace("_", " ").title(),
                detail=exc.message,
                error_type=exc.error_type,
                instance=str(request.url),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=problem_detail(
                status=exc.status_code,
                title="HTTP Error",
                detail=exc.detail,
                error_type="http_error",
                instance=str(request.url),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        return JSONResponse(
            status_code=422,
            content=problem_detail(
                status=422,
                title="Validation Error",
                detail="The request contains invalid data.",
                error_type="validation_error",
                instance=str(request.url),
                errors=errors,
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        import logging
        logger = logging.getLogger("ganitmitra")
        logger.exception(f"Unhandled exception: {exc}")

        return JSONResponse(
            status_code=500,
            content=problem_detail(
                status=500,
                title="Internal Server Error",
                detail="An unexpected error occurred. Please try again later.",
                error_type="internal_error",
                instance=str(request.url),
            ),
        )
