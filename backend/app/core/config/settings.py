import os
from app.core.config.constants import (
    DEFAULT_PRIMARY_MODEL,
    DEFAULT_PRIMARY_API_BASE,
    DEFAULT_FALLBACK_MODEL,
)


class AppConfig:
    """Core application settings populated from environment variables."""

    def __init__(self) -> None:
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
        self.llm_api_keys: str = os.getenv("LLM_API_KEYS", "")
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.enable_failure_simulation: bool = (
            os.getenv("ENABLE_FAILURE_SIMULATION", "true").lower() == "true"
        )
        origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,*",
        )
        self.allowed_origins: list[str] = [
            o.strip() for o in origins.split(",") if o.strip()
        ]
        # Abstracted provider defaults from centralized constants
        self.primary_model: str = os.getenv(
            "PRIMARY_MODEL_NAME", DEFAULT_PRIMARY_MODEL
        )
        self.primary_base_url: str = os.getenv(
            "PRIMARY_API_BASE", DEFAULT_PRIMARY_API_BASE
        )
        self.fallback_model: str = os.getenv(
            "FALLBACK_MODEL_NAME", DEFAULT_FALLBACK_MODEL
        )
