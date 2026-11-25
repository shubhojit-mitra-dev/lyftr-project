from typing import Annotated
from pydantic import BaseModel, Field
from app.dto.chat_metadata_dto import ChatMetadataDTO


class ChatResponseDTO(BaseModel):
    """Data Transfer Object for successful chat response."""

    session_id: Annotated[str, Field(..., description="Echo of client request session_id")]
    reply: Annotated[str, Field(..., min_length=1, description="Assistant generated text")]
    metadata: Annotated[ChatMetadataDTO, Field(..., description="Telemetry metadata")]
