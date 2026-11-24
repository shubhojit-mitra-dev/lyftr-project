from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Header

from app.dto.chat_dto import (
    ChatRequestDTO,
    ChatResponseDTO,
    SessionHistoryResponseDTO,
    HealthResponseDTO,
)
from app.services.chat_service import ChatService
from app.api.v1.controllers.chat_controller import ChatController
from app.core.container import (
    get_repository as get_storage_dep,
    get_gateway as get_gateway_dep,
)
from app.domain.protocols.repository_protocol import MessageRepositoryProtocol
from app.domain.protocols.gateway_protocol import LLMGatewayProtocol

router = APIRouter()


def get_chat_controller(
    repo: Annotated[MessageRepositoryProtocol, Depends(get_storage_dep)],
    gw: Annotated[LLMGatewayProtocol, Depends(get_gateway_dep)],
) -> ChatController:
    """Dependency provider injecting protocols into ChatService and ChatController."""
    service = ChatService(repository=repo, gateway=gw)
    return ChatController(service=service)


@router.get("/health", response_model=HealthResponseDTO, status_code=200)
async def health_endpoint(
    controller: Annotated[ChatController, Depends(get_chat_controller)],
) -> HealthResponseDTO:
    """System health check endpoint verifying database and key pool status."""
    return await controller.handle_health_check()


@router.post("/chat", response_model=ChatResponseDTO, status_code=200)
async def chat_endpoint(
    request: ChatRequestDTO,
    controller: Annotated[ChatController, Depends(get_chat_controller)],
    x_simulate_failure: Annotated[Optional[str], Header(alias="X-Simulate-Failure")] = None,
) -> ChatResponseDTO:
    """Execute chat turn with conversation history memory, caching, and auto-failover."""
    return await controller.handle_chat(
        request=request,
        x_simulate_failure=x_simulate_failure,
    )


@router.get("/sessions/{session_id}/messages", response_model=SessionHistoryResponseDTO, status_code=200)
async def session_messages_endpoint(
    session_id: str,
    controller: Annotated[ChatController, Depends(get_chat_controller)],
) -> SessionHistoryResponseDTO:
    """Retrieve full chronological conversation history for a given session."""
    return await controller.handle_get_session_messages(session_id=session_id)
