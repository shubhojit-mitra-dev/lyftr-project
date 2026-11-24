from abc import ABC, abstractmethod
from typing import Optional, Any
from app.dto.chat_dto import ChatMetadataDTO


class ILLMGateway(ABC):
    """Abstract Gateway interface for model inference, caching, and failover routing."""

    @abstractmethod
    def complete(
        self,
        messages: list[dict[str, Any]],
        x_simulate_failure: Optional[str] = None,
    ) -> tuple[str, ChatMetadataDTO]:
        """Execute chat completion across provider pool with caching and failover."""
        pass

    @abstractmethod
    def get_configured_keys_count(self) -> int:
        """Return the count of loaded provider keys."""
        pass

    @abstractmethod
    def is_cache_enabled(self) -> bool:
        """Return whether response caching is active."""
        pass
