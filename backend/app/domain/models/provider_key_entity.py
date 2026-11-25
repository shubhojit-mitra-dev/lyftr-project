from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderKeyEntity:
    """Domain representation of an LLM provider key configuration."""

    key_id: str
    api_key: str
    model: str
    api_base: Optional[str] = None
    display_model: Optional[str] = None
