"""Data Transfer Object for Root Endpoint."""

from typing import Annotated
from pydantic import BaseModel, Field


class RootResponseDTO(BaseModel):
    """Schema representing root endpoint informational links."""

    message: Annotated[
        str,
        Field(
            default="Welcome to LLM Chatbot Gateway API. Interactive API documentation is available at /docs, alternative documentation at /redoc, and health check at /health.",
            description="Welcome and informational message",
        ),
    ]
    docs: Annotated[
        str,
        Field(default="/docs", description="Interactive Swagger API documentation URL"),
    ]
    redoc: Annotated[
        str,
        Field(default="/redoc", description="ReDoc API documentation URL"),
    ]
    health: Annotated[
        str,
        Field(default="/health", description="System health verification endpoint"),
    ]

