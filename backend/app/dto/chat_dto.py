from typing import Literal, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ChatRequestDTO(BaseModel):
    """Data Transfer Object for chat execution requests."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Client-generated session identifier (1-128 chars)",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message content (1-4000 chars after trim)",
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional session-scoped system prompt override",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("message cannot be empty or whitespace only")
        if len(trimmed) > 4000:
            raise ValueError("message cannot exceed 4000 characters after trimming")
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


class ChatMetadataDTO(BaseModel):
    """Data Transfer Object for LLM inference/caching telemetry metadata."""

    resolution_source: Literal["LIVE_INFERENCE", "LLM_CACHE"] = Field(
        ...,
        description="Resolution origin of response: LIVE_INFERENCE or LLM_CACHE",
    )
    model: str = Field(..., description="LiteLLM model name that produced reply")
    latency_ms: int = Field(..., ge=0, description="Server-side latency in milliseconds")
    input_tokens: int = Field(..., ge=0, description="Prompt tokens for this request only")
    output_tokens: int = Field(..., ge=0, description="Completion tokens for this reply")
    key_id: Optional[str] = Field(
        default=None,
        description="ID of key that answered (key_1, key_2...). null on cache hit",
    )
    fallback_attempts: int = Field(
        default=0,
        ge=0,
        description="Failed provider attempts before success. 0 on cache hit",
    )


class ChatResponseDTO(BaseModel):
    """Data Transfer Object for successful chat response."""

    session_id: str = Field(..., description="Echo of client request session_id")
    reply: str = Field(..., min_length=1, description="Assistant generated text")
    metadata: ChatMetadataDTO = Field(..., description="Telemetry metadata")


class MessageHistoryItemDTO(BaseModel):
    """Data Transfer Object representing a single message turn in session history."""

    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Text content of turn")
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Turn metadata (attached to assistant turns only)",
    )


class SessionHistoryResponseDTO(BaseModel):
    """Data Transfer Object for session history listing."""

    session_id: str = Field(..., description="Queried session identifier")
    messages: list[MessageHistoryItemDTO] = Field(
        default_factory=list,
        description="Chronological message list (oldest first, no system prompt)",
    )


class HealthResponseDTO(BaseModel):
    """Data Transfer Object for service health status."""

    status: str = Field(default="ok", description="Overall service status")
    keys_configured: int = Field(..., ge=0, description="Count of loaded API keys")
    cache_enabled: bool = Field(..., description="Flag indicating cache readiness")
