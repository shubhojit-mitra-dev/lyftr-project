"""Data Transfer Objects package re-exports."""

from app.dto.chat_request_dto import ChatRequestDTO
from app.dto.chat_metadata_dto import ChatMetadataDTO
from app.dto.chat_response_dto import ChatResponseDTO
from app.dto.message_history_item_dto import MessageHistoryItemDTO
from app.dto.session_history_response_dto import SessionHistoryResponseDTO
from app.dto.health_response_dto import HealthResponseDTO

# Backward-compatibility aliases
ChatRequest = ChatRequestDTO
ChatResponse = ChatResponseDTO
ChatMetadata = ChatMetadataDTO
SessionHistoryResponse = SessionHistoryResponseDTO
MessageHistoryItem = MessageHistoryItemDTO
HealthResponse = HealthResponseDTO

__all__ = [
    "ChatRequestDTO",
    "ChatMetadataDTO",
    "ChatResponseDTO",
    "MessageHistoryItemDTO",
    "SessionHistoryResponseDTO",
    "HealthResponseDTO",
    "ChatRequest",
    "ChatResponse",
    "ChatMetadata",
    "SessionHistoryResponse",
    "MessageHistoryItem",
    "HealthResponse",
]
