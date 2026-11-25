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

    def __contains__(self, key: str) -> bool:
        val = getattr(self, key, None)
        return val is not None

    def __getitem__(self, item: Any) -> Any:
        if isinstance(item, int):
            fields = [self.id, self.session_id, self.role, self.content, self.metadata, self.created_at]
            return fields[item]
        return getattr(self, str(item))

    def is_assistant(self) -> bool:
        return self.role == "assistant"

    def is_user(self) -> bool:
        return self.role == "user"
