from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any


@dataclass
class MessageEntity:
    """Core domain entity representing a message record in conversation history."""

    id: Optional[int] = None
    session_id: str = ""
    role: str = ""  # 'user' | 'assistant'
    content: str = ""
    metadata: Optional[dict[str, Any]] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def is_assistant(self) -> bool:
        return self.role == "assistant"

    def is_user(self) -> bool:
        return self.role == "user"


@dataclass
class ProviderKeyEntity:
    """Domain representation of an LLM provider key configuration."""

    key_id: str
    api_key: str
    model: str
    api_base: Optional[str] = None
