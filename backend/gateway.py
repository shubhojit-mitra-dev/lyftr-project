"""LiteLLM Gateway with provider pool management and response caching.

Implements the multi-provider key pool (NVIDIA NIM primary, Google Gemini fallback)
and LiteLLM response caching matching docs/PRD.md and ADR 001/003.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import litellm
from fastapi import HTTPException, status
from schemas import ChatMetadata

logger = logging.getLogger(__name__)

# Configure LiteLLM settings and caching
litellm.telemetry = False
litellm.suppress_debug_info = True

# Enable local in-memory caching
try:
    litellm.enable_cache(type="local")
except Exception as e:
    logger.warning("Failed to enable LiteLLM local cache: %s", e)


@dataclass
class KeyConfig:
    """Configuration for a single provider key in the key pool."""

    key_id: str
    api_key: str
    model: str
    api_base: Optional[str] = None


def build_key_pool(raw_keys: List[str]) -> List[KeyConfig]:
    """Map raw API keys into structured KeyConfig objects.

    Mapping Rules:
    - key_1 (Primary): NVIDIA NIM (openai/nvidia/nemotron-3.5-lightning-30b-a3b via custom base URL)
    - key_2 (Secondary): Google Gemini (gemini/gemini-3.5-flash-lite)
    - Subsequent keys: mapped based on key prefix (nvapi-, AIza/AQ., sk-) or alternating fallback.
    """
    key_pool: List[KeyConfig] = []
    for idx, key in enumerate(raw_keys):
        key_id = f"key_{idx + 1}"
        cleaned = key.strip()

        # Prefix matching
        if cleaned.startswith("nvapi-"):
            key_pool.append(
                KeyConfig(
                    key_id=key_id,
                    api_key=cleaned,
                    model="openai/nvidia/nemotron-3.5-lightning-30b-a3b",
                    api_base="https://integrate.api.nvidia.com/v1",
                )
            )
        elif cleaned.startswith("AIza") or cleaned.startswith("AQ."):
            key_pool.append(
                KeyConfig(
                    key_id=key_id,
                    api_key=cleaned,
                    model="gemini/gemini-3.5-flash-lite",
                    api_base=None,
                )
            )
        elif cleaned.startswith("sk-"):
            key_pool.append(
                KeyConfig(
                    key_id=key_id,
                    api_key=cleaned,
                    model="openai/gpt-4o-mini",
                    api_base=None,
                )
            )
        else:
            # Fallback based on position in key pool
            if idx == 0:
                key_pool.append(
                    KeyConfig(
                        key_id=key_id,
                        api_key=cleaned,
                        model="openai/nvidia/nemotron-3.5-lightning-30b-a3b",
                        api_base="https://integrate.api.nvidia.com/v1",
                    )
                )
            elif idx == 1:
                key_pool.append(
                    KeyConfig(
                        key_id=key_id,
                        api_key=cleaned,
                        model="gemini/gemini-3.5-flash-lite",
                        api_base=None,
                    )
                )
            elif idx % 2 == 0:
                key_pool.append(
                    KeyConfig(
                        key_id=key_id,
                        api_key=cleaned,
                        model="openai/nvidia/nemotron-3.5-lightning-30b-a3b",
                        api_base="https://integrate.api.nvidia.com/v1",
                    )
                )
            else:
                key_pool.append(
                    KeyConfig(
                        key_id=key_id,
                        api_key=cleaned,
                        model="gemini/gemini-3.5-flash-lite",
                        api_base=None,
                    )
                )

    return key_pool


class LLMGateway:
    """Resilient LLM Gateway with provider pool routing and response caching."""

    def __init__(self) -> None:
        pass

    def get_key_pool(self, raw_keys: List[str]) -> List[KeyConfig]:
        """Construct key pool from raw key list."""
        return build_key_pool(raw_keys)

    def check_cache(
        self,
        messages: List[dict[str, str]],
        key_pool: List[KeyConfig],
    ) -> Optional[Tuple[str, ChatMetadata]]:
        """Check if any model in the key pool has a cached response."""
        if not hasattr(litellm, "cache") or litellm.cache is None:
            return None

        for key_cfg in key_pool:
            try:
                cached: Optional[dict[str, Any]] = litellm.cache.get_cache(
                    model=key_cfg.model,
                    messages=messages,
                )
                if cached:
                    choices = cached.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        usage = cached.get("usage", {})
                        model_name = cached.get("model") or key_cfg.model

                        metadata = ChatMetadata(
                            resolution_source="LLM_CACHE",
                            model=model_name,
                            latency_ms=1,  # Sub-millisecond local cache hit
                            input_tokens=usage.get("prompt_tokens", 0) or 0,
                            output_tokens=usage.get("completion_tokens", 0) or 0,
                            key_id=None,
                            fallback_attempts=0,
                        )
                        return content, metadata
            except Exception as e:
                logger.debug("Cache check error for model %s: %s", key_cfg.model, e)

        return None

    async def execute_key(
        self,
        key_cfg: KeyConfig,
        messages: List[dict[str, str]],
        mock_response: Optional[str] = None,
        bypass_cache: bool = False,
    ) -> Any:
        """Execute a single completion call with the given key configuration."""
        kwargs: dict[str, Any] = {
            "model": key_cfg.model,
            "messages": messages,
            "api_key": key_cfg.api_key,
            "timeout": 30.0,
        }
        if key_cfg.api_base:
            kwargs["api_base"] = key_cfg.api_base
        if bypass_cache:
            kwargs["cache"] = {"no-cache": True, "no-store": True}
        if mock_response is not None:
            kwargs["mock_response"] = mock_response

        # Execute in worker thread to prevent event loop blocking
        return await asyncio.to_thread(litellm.completion, **kwargs)


# Global singleton instance
gateway = LLMGateway()
