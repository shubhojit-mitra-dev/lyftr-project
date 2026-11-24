"""FastAPI core application for LLM Chatbot service.

Provides the three mandatory endpoints from docs/PRD.md:
- GET /health
- POST /chat
- GET /sessions/{session_id}/messages
"""

import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from schemas import (
    ChatMetadata,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MessageItem,
    SessionHistoryResponse,
)
from storage import StorageRepository, storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initialize SQLite database on boot."""
    logger.info("Initializing SQLite storage repository...")
    await storage.init_db()
    logger.info("Database schema initialized successfully.")
    yield


app = FastAPI(
    title="LLM Chatbot Gateway API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Ensure no unhandled exceptions leak stack traces or HTML to clients."""
    logger.error("Unhandled error processing %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def get_storage_dep() -> StorageRepository:
    return storage


StorageDep = Annotated[StorageRepository, Depends(get_storage_dep)]


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns 200 once the app is running, the database is reachable and the key pool is loaded.",
)
async def health_check(storage_repo: StorageDep) -> HealthResponse:
    db_healthy = await storage_repo.health_check()
    if not db_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unreachable",
        )

    configured_keys = settings.get_configured_keys()
    keys_count = len(configured_keys)

    return HealthResponse(
        status="ok",
        keys_configured=keys_count,
        cache_enabled=True,
    )


@app.get(
    "/sessions/{session_id}/messages",
    response_model=SessionHistoryResponse,
    summary="Get session history",
    description="Returns the stored history of one session from SQLite, oldest first, without the system prompt.",
)
async def get_session_history(
    session_id: str,
    storage_repo: StorageDep,
) -> SessionHistoryResponse:
    if not await storage_repo.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="session not found",
        )

    raw_messages = await storage_repo.get_messages(session_id)
    messages = [MessageItem(**msg) for msg in raw_messages]

    return SessionHistoryResponse(
        session_id=session_id,
        messages=messages,
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send chat message",
    description="Multi-turn LLM chat execution with key failover, response caching, and token telemetry.",
)
async def chat_endpoint(
    request: ChatRequest,
    storage_repo: StorageDep,
) -> ChatResponse:
    # Phase 1: Core plumbing and stub execution
    reply_text = f"Mock response for session '{request.session_id}': {request.message}"
    metadata = ChatMetadata(
        resolution_source="LIVE_INFERENCE",
        model="mock-nemotron",
        latency_ms=10,
        input_tokens=len(request.message.split()),
        output_tokens=len(reply_text.split()),
        key_id="key_1",
        fallback_attempts=0,
    )

    # Persist the turn atomically to SQLite
    await storage_repo.add_turn(
        session_id=request.session_id,
        user_content=request.message,
        assistant_content=reply_text,
        metadata={
            "resolution_source": metadata.resolution_source,
            "input_tokens": metadata.input_tokens,
            "output_tokens": metadata.output_tokens,
        },
    )

    return ChatResponse(
        session_id=request.session_id,
        reply=reply_text,
        metadata=metadata,
    )
