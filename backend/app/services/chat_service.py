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
        past_turns = await self._repository.get_messages(request.session_id)

        llm_messages: list[dict[str, Any]] = []
        if request.system_prompt and request.system_prompt.strip():
            llm_messages.append({"role": "system", "content": request.system_prompt.strip()})

        for turn in past_turns:
            role = turn.role if hasattr(turn, "role") else turn["role"]
            content = turn.content if hasattr(turn, "content") else turn["content"]
            llm_messages.append({"role": role, "content": content})

        llm_messages.append({"role": "user", "content": request.message})

        res = self._gateway.complete(
            messages=llm_messages,
            x_simulate_failure=x_simulate_failure,
        )
        if hasattr(res, "__await__"):
            reply_text, metadata = await res
        else:
            reply_text, metadata = res


        from schemas import ChatMetadata

        # Ensure metadata is converted into dict or ChatMetadata
        meta_dict = metadata.model_dump() if hasattr(metadata, "model_dump") else metadata
        if not isinstance(metadata, ChatMetadata):
            metadata = ChatMetadata(**meta_dict)

        await self._repository.add_turn(
            session_id=request.session_id,
            user_content=request.message,
            assistant_content=reply_text,
            metadata=meta_dict,
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

        turns = await self._repository.get_messages(session_id)
        items: list[MessageHistoryItemDTO] = []
        for turn in turns:
            role = turn.role if hasattr(turn, "role") else turn["role"]
            content = turn.content if hasattr(turn, "content") else turn["content"]
            meta = turn.metadata if hasattr(turn, "metadata") else turn.get("metadata")
            is_assistant = role == "assistant"
            items.append(
                MessageHistoryItemDTO(
                    role=role,
                    content=content,
                    metadata=meta if is_assistant else None,
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
