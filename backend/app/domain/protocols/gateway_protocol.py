from typing import Protocol, Optional, Any, runtime_checkable
from app.dto.chat_dto import ChatMetadataDTO


@runtime_checkable
class LLMGatewayProtocol(Protocol):
    """Structural subtyping protocol for model invocation and auto-failover."""

    def complete(
        self,
        messages: list[dict[str, Any]],
        x_simulate_failure: Optional[str] = None,
    ) -> tuple[str, ChatMetadataDTO]:
        ...

    def get_configured_keys_count(self) -> int:
        ...

    def is_cache_enabled(self) -> bool:
        ...
