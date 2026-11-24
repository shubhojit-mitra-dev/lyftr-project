import logging
from typing import Optional, Any
from fastapi import HTTPException

from app.domain.interfaces.repository_interface import IMessageRepository
from app.domain.interfaces.gateway_interface import ILLMGateway
from app.dto.chat_dto import (
    ChatRequestDTO,
    ChatResponseDTO,
    SessionHistoryResponseDTO,
    MessageHistoryItemDTO,
    HealthResponseDTO,
)

logger = logging.getLogger(__name__)


class ChatService:
    """Application Service coordinating repository, gateway, and business logic."""

    def __init__(self, repository: IMessageRepository, gateway: ILLMGateway):
        self._repository = repository
        self._gateway = gateway

    async def execute_chat(
        self,
        request: ChatRequestDTO,
        x_simulate_failure: Optional[str] = None,
    ) -> ChatResponseDTO:
        """Process chat message, query previous context, invoke gateway, and persist turn."""
        past_entities = await self._repository.get_messages(request.session_id)

        llm_messages: list[dict[str, Any]] = []
        if request.system_prompt and request.system_prompt.strip():
            llm_messages.append({"role": "system", "content": request.system_prompt.strip()})

        for entity in past_entities:
            llm_messages.append({"role": entity.role, "content": entity.content})

        llm_messages.append({"role": "user", "content": request.message})

        reply_text, metadata = self._gateway.complete(
            messages=llm_messages,
            x_simulate_failure=x_simulate_failure,
        )

        await self._repository.add_turn(
            session_id=request.session_id,
            user_content=request.message,
            assistant_content=reply_text,
            metadata=metadata.model_dump(),
        )

        return ChatResponseDTO(
            session_id=request.session_id,
            reply=reply_text,
            metadata=metadata,
        )

    async def get_session_history(self, session_id: str) -> SessionHistoryResponseDTO:
        """Fetch session history excluding system prompt."""
        exists = await self._repository.session_exists(session_id)
        if not exists:
            raise HTTPException(status_code=404, detail="session not found")

        entities = await self._repository.get_messages(session_id)
        items: list[MessageHistoryItemDTO] = []
        for entity in entities:
            items.append(
                MessageHistoryItemDTO(
                    role=entity.role,
                    content=entity.content,
                    metadata=entity.metadata if entity.is_assistant() else None,
                )
            )

        return SessionHistoryResponseDTO(session_id=session_id, messages=items)

    async def check_health(self) -> HealthResponseDTO:
        """Verify repository and gateway readiness."""
        db_healthy = await self._repository.health_check()
        if not db_healthy:
            raise HTTPException(status_code=503, detail="database unreachable")

        return HealthResponseDTO(
            status="ok",
            keys_configured=self._gateway.get_configured_keys_count(),
            cache_enabled=self._gateway.is_cache_enabled(),
        )
