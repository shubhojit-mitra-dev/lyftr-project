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


def parse_simulate_failure_header(header: Optional[str]) -> dict[str, int]:
    """Parse X-Simulate-Failure request header.

    Format: comma-separated <key_id>=<status> pairs or *=<status>.
    Valid statuses: 429, 500, 502, 503.
    """
    if not header:
        return {}

    valid_statuses = {429, 500, 502, 503}
    result: dict[str, int] = {}
    pairs = [p.strip() for p in header.split(",") if p.strip()]

    for pair in pairs:
        if "=" not in pair:
            continue
        target, status_str = pair.split("=", 1)
        target = target.strip()
        try:
            status_code = int(status_str.strip())
            if status_code in valid_statuses:
                result[target] = status_code
        except ValueError:
            continue

    return result


class LLMGateway:
    """Resilient LLM Gateway with provider pool routing, failover, and caching."""

    def __init__(self) -> None:
        pass

    def get_key_pool(self, raw_keys: List[str]) -> List[KeyConfig]:
        """Construct key pool from raw key list."""
        return build_key_pool(raw_keys)

    def check_cache(
        self,
        messages: List[dict[str, str]],
        key_pool: List[KeyConfig],
        start_time: float,
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
                        latency_ms = max(1, int(round((time.perf_counter() - start_time) * 1000)))

                        metadata = ChatMetadata(
                            resolution_source="LLM_CACHE",
                            model=model_name,
                            latency_ms=latency_ms,
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

    async def complete(
        self,
        messages: List[dict[str, str]],
        x_simulate_failure: Optional[str] = None,
        mock_response: Optional[str] = None,
        configured_keys: Optional[List[str]] = None,
        enable_simulation: Optional[bool] = None,
    ) -> Tuple[str, ChatMetadata]:
        """Execute chat completion across provider pool with auto-fallback and caching.

        Parameters:
        - messages: Full formatted conversation turn list (system + history + current user).
        - x_simulate_failure: Value of X-Simulate-Failure header (e.g. 'key_1=429').
        - mock_response: Optional string to return for deterministic testing.
        - configured_keys: Optional override for key pool during testing.
        - enable_simulation: Optional override for failure simulation switch.

        Returns:
        - (reply_text, ChatMetadata)
        """
        from config import settings

        start_time = time.perf_counter()

        raw_keys = configured_keys if configured_keys is not None else settings.get_configured_keys()
        key_pool = self.get_key_pool(raw_keys)
        if not key_pool:
            logger.error("Key pool is empty. No providers configured.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="all providers unavailable",
            )

        sim_switch = (
            enable_simulation if enable_simulation is not None else settings.ENABLE_FAILURE_SIMULATION
        )
        sim_map = parse_simulate_failure_header(x_simulate_failure) if sim_switch else {}
        is_simulation = bool(sim_map)

        # 1. Check cache when not simulating failure
        if not is_simulation:
            cached_result = self.check_cache(messages, key_pool, start_time)
            if cached_result is not None:
                return cached_result

        # 2. Sequential fallback execution across provider pool
        fallback_attempts = 0

        for key_cfg in key_pool:
            # Check for simulated failure on this key
            simulated_status = sim_map.get(key_cfg.key_id) or sim_map.get("*") if is_simulation else None
            if simulated_status is not None:
                logger.info(
                    "Simulating failure on %s with status HTTP %s",
                    key_cfg.key_id,
                    simulated_status,
                )
                fallback_attempts += 1
                continue

            try:
                resp = await self.execute_key(
                    key_cfg=key_cfg,
                    messages=messages,
                    mock_response=mock_response,
                    bypass_cache=is_simulation,
                )

                # Extract reply text
                choice = resp.choices[0]
                content = choice.message.content
                if not content and hasattr(choice.message, "reasoning_content"):
                    content = choice.message.reasoning_content
                reply = (content or "").strip()
                if not reply:
                    reply = "No response"

                latency_ms = max(1, int(round((time.perf_counter() - start_time) * 1000)))
                usage = getattr(resp, "usage", None)
                input_tokens = getattr(usage, "prompt_tokens", 0) or 0
                output_tokens = getattr(usage, "completion_tokens", 0) or 0
                model_name = getattr(resp, "model", None) or key_cfg.model

                # Check if LiteLLM internal cache hit occurred
                is_cache_hit = getattr(resp, "_hidden_params", {}).get("cache_hit") is True
                if is_cache_hit and not is_simulation:
                    metadata = ChatMetadata(
                        resolution_source="LLM_CACHE",
                        model=model_name,
                        latency_ms=latency_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        key_id=None,
                        fallback_attempts=0,
                    )
                else:
                    metadata = ChatMetadata(
                        resolution_source="LIVE_INFERENCE",
                        model=model_name,
                        latency_ms=latency_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        key_id=key_cfg.key_id,
                        fallback_attempts=fallback_attempts,
                    )

                return reply, metadata

            except Exception as exc:
                logger.warning(
                    "Provider %s failed with exception: %s (%s). Attempting failover.",
                    key_cfg.key_id,
                    exc,
                    type(exc).__name__,
                )
                fallback_attempts += 1
                continue

        # If all keys failed
        logger.error("All providers in key pool failed (exhausted %s attempts).", fallback_attempts)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="all providers unavailable",
        )


# Global singleton instance
gateway = LLMGateway()
