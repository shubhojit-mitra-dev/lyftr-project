from typing import Annotated
from pydantic import BaseModel, Field, field_validator
from app.dto.message_history_item_dto import MessageHistoryItemDTO


class SessionHistoryResponseDTO(BaseModel):
    """Data Transfer Object for conversation session history response."""

    session_id: Annotated[str, Field(..., description="Target session identifier")]
    messages: Annotated[list[MessageHistoryItemDTO], Field(..., description="Chronological message list")]

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("session_id cannot be empty")
        return trimmed
