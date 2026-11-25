from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.container import get_container
from app.core.logging.logger import configure_structlog, get_logger
from app.api.v1.routes.chat_routes import router as chat_router
from app.api.middleware.error_handler import (
    global_exception_handler,
    LoggingAOPMiddleware,
)

configure_structlog()
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle bootstrapper."""
    container = get_container()
    logger.info("Initializing persistent storage schema...")
    await container.repository.init_db()
    logger.info("Application context fully initialized and ready to receive traffic.")
    yield
    logger.info("Application context terminating.")


def create_application() -> FastAPI:
    """FastAPI Application Factory adhering to DDD clean architecture."""
    container = get_container()
    app = FastAPI(
        title="LLM Chatbot with Key Failover & Caching",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(LoggingAOPMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=container.app_config.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(RequestValidationError, global_exception_handler)

    app.include_router(chat_router)
    return app


app = create_application()
