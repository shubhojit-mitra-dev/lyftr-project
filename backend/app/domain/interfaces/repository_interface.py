from abc import ABC, abstractmethod
from typing import Optional, Any
from app.domain.models.message import MessageEntity


class IMessageRepository(ABC):
    """Abstract Repository interface for persistent message and session storage."""

    @abstractmethod
    async def init_db(self) -> None:
        """Initialize database schema and requisite indexes."""
        pass

    @abstractmethod
    async def get_messages(self, session_id: str) -> list[MessageEntity]:
        """Retrieve chronological message turns for given session."""
        pass

    @abstractmethod
    async def session_exists(self, session_id: str) -> bool:
        """Check if session has any existing message history."""
        pass

    @abstractmethod
    async def add_turn(
        self,
        session_id: str,
        user_content: str,
        assistant_content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Atomically persist a user turn and corresponding assistant response."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify storage engine connectivity and read/write health."""
        pass
