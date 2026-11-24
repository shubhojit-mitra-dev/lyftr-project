from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.container import get_container
from app.api.v1.endpoints.chat_controller import router as chat_router
from app.api.middleware.error_handler import (
    global_exception_handler,
    LoggingAOPMiddleware,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle bootstrapper (Spring-style ApplicationListener)."""
    container = get_container()
    logger.info("Initializing database schema on startup...")
    await container.repository.init_db()
    logger.info("Application context fully loaded.")
    yield
    logger.info("Application context shutting down.")


def create_application() -> FastAPI:
    """FastAPI Application Factory adhering to clean architecture."""
    container = get_container()
    app = FastAPI(
        title="LLM Chatbot with Key Failover & Caching",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(LoggingAOPMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=container.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(RequestValidationError, global_exception_handler)

    app.include_router(chat_router)
    return app


app = create_application()


# Backward compatibility aliases for existing tests
from app.core.container import get_container as _gc
storage = _gc().repository
gateway = _gc().gateway
settings = _gc()
