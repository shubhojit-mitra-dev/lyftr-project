from typing import Optional
from fastapi import APIRouter, Depends, Header

from app.dto.chat_dto import (
    ChatRequestDTO,
    ChatResponseDTO,
    SessionHistoryResponseDTO,
    HealthResponseDTO,
)
from app.services.chat_service import ChatService
from app.core.container import get_chat_service

router = APIRouter()


@router.get("/health", response_model=HealthResponseDTO, status_code=200)
async def health_check(
    service: ChatService = Depends(get_chat_service),
) -> HealthResponseDTO:
    """System health check endpoint verifying database reachability and key pool readiness."""
    return await service.check_health()


@router.post("/chat", response_model=ChatResponseDTO, status_code=200)
async def chat(
    request: ChatRequestDTO,
    x_simulate_failure: Optional[str] = Header(default=None, alias="X-Simulate-Failure"),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponseDTO:
    """Execute chat turn with conversation history memory, caching, and auto-failover."""
    return await service.execute_chat(request, x_simulate_failure=x_simulate_failure)


@router.get("/sessions/{session_id}/messages", response_model=SessionHistoryResponseDTO, status_code=200)
async def get_session_messages(
    session_id: str,
    service: ChatService = Depends(get_chat_service),
) -> SessionHistoryResponseDTO:
    """Retrieve full chronological conversation history for a given session."""
    return await service.get_session_history(session_id)
