from typing import Annotated, Optional
from pydantic import BaseModel, Field, field_validator


class ChatRequestDTO(BaseModel):
    """Data Transfer Object for chat execution requests using Annotated fields."""

    session_id: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=128,
            description="Client-generated session identifier (1-128 chars)",
        ),
    ]
    message: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            description="User message content (1-4000 chars after trim)",
        ),
    ]
    system_prompt: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Optional session-scoped system prompt override",
        ),
    ] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("message cannot be empty or whitespace only")
        if len(trimmed) > 4000:
            raise ValueError("message cannot exceed 4000 characters")
        return trimmed

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("session_id cannot be empty")
        if len(trimmed) > 128:
            raise ValueError("session_id cannot exceed 128 characters")
        return trimmed
