import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """AOP-style Global Exception filter ensuring uniform JSON error responses."""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    if isinstance(exc, RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


class LoggingAOPMiddleware(BaseHTTPMiddleware):
    """Aspect-Oriented Request/Response audit logger middleware."""

    async def dispatch(self, request: Request, call_next):
        logger.debug(f"[AOP Incoming] {request.method} {request.url.path}")
        response = await call_next(request)
        logger.debug(f"[AOP Outgoing] {request.method} {request.url.path} -> {response.status_code}")
        return response
