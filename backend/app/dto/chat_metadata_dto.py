from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field


class ChatMetadataDTO(BaseModel):
    """Data Transfer Object for telemetry metadata using Annotated fields."""

    resolution_source: Annotated[
        Literal["LIVE_INFERENCE", "LLM_CACHE"],
        Field(..., description="Resolution origin: LIVE_INFERENCE or LLM_CACHE"),
    ]
    model: Annotated[str, Field(..., description="LiteLLM model name that produced reply")]
    latency_ms: Annotated[int, Field(..., ge=0, description="Server latency in milliseconds")]
    input_tokens: Annotated[int, Field(..., ge=0, description="Prompt tokens for this request only")]
    output_tokens: Annotated[int, Field(..., ge=0, description="Completion tokens for this reply")]
    key_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="ID of key that answered (key_1, key_2...). null on cache hit",
        ),
    ] = None
    fallback_attempts: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="Failed provider attempts before success. 0 on cache hit",
        ),
    ] = 0
