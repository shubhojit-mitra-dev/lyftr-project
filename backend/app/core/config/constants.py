"""Centralized provider model and endpoint constants for the application.

Any update to the default models or API endpoints should be configured here or
overridden via environment variables (PRIMARY_MODEL_NAME, PRIMARY_API_BASE, FALLBACK_MODEL_NAME).
"""

DEFAULT_PRIMARY_MODEL: str = "nvidia/nemotron-3.5-lightning-30b-a3b"
DEFAULT_PRIMARY_API_BASE: str = "https://integrate.api.nvidia.com/v1"
DEFAULT_FALLBACK_MODEL: str = "gemini/gemini-3.5-flash-lite"

