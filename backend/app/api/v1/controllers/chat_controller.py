from typing import Optional
from app.dto.chat_dto import (
    ChatRequestDTO,
    ChatResponseDTO,
    SessionHistoryResponseDTO,
    HealthResponseDTO,
    RootResponseDTO,
)
from app.services.chat_service import ChatService


class ChatController:
    """Decoupled Controller handling business action invocations."""

    def __init__(self, service: ChatService) -> None:
        self._service = service

    def handle_root(self) -> RootResponseDTO:
        return RootResponseDTO(
            message="Welcome to LLM Chatbot Gateway API. Interactive API documentation is available at /docs, alternative documentation at /redoc, and health check at /health.",
            docs="/docs",
            redoc="/redoc",
            health="/health",
        )

    async def handle_health_check(self) -> HealthResponseDTO:
        return await self._service.check_health()

    async def handle_chat(
        self,
        request: ChatRequestDTO,
        x_simulate_failure: Optional[str] = None,
    ) -> ChatResponseDTO:
        return await self._service.execute_chat(
            request=request,
            x_simulate_failure=x_simulate_failure,
        )

    async def handle_get_session_messages(
        self,
        session_id: str,
    ) -> SessionHistoryResponseDTO:
        return await self._service.get_session_history(session_id)
