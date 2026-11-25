from typing import Annotated, Literal
from pydantic import BaseModel, Field


class HealthResponseDTO(BaseModel):
    """Data Transfer Object for system liveness and readiness probe response."""

    status: Annotated[Literal["ok", "degraded", "error"], Field(..., description="Overall service status")]
    keys_configured: Annotated[int, Field(..., ge=0, description="Count of loaded LLM provider API keys")]
    cache_enabled: Annotated[bool, Field(..., description="Whether LiteLLM response caching is active")]
