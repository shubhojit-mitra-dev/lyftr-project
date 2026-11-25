from typing import Protocol, Optional, Any, runtime_checkable
from app.domain.models.message import MessageEntity


@runtime_checkable
class MessageRepositoryProtocol(Protocol):
    """Structural subtyping protocol for database persistence operations."""

    async def init_db(self) -> None:
        ...

    async def get_messages(self, session_id: str) -> list[MessageEntity]:
        ...

    async def session_exists(self, session_id: str) -> bool:
        ...

    async def add_turn(
        self,
        session_id: str,
        user_content: str,
        assistant_content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        ...

    async def health_check(self) -> bool:
        ...
