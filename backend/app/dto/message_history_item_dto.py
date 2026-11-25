from typing import Annotated, Literal, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_serializer


class MessageHistoryItemDTO(BaseModel):
    """Data Transfer Object for individual session messages in history response."""

    role: Annotated[
        Literal["user", "assistant"],
        Field(..., description="Message role (user | assistant)"),
    ]
    content: Annotated[
        str,
        Field(..., min_length=1, description="Message text content"),
    ]
    metadata: Annotated[
        Optional[dict[str, Any]],
        Field(
            default=None,
            description="Telemetry metadata for assistant messages; None for user turns",
        ),
    ] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("content cannot be empty")
        return trimmed

    @model_serializer(mode="wrap")
    def serialize_model(self, handler: Any) -> dict[str, Any]:
        data = handler(self)
        if data.get("metadata") is None:
            data.pop("metadata", None)
        return data
