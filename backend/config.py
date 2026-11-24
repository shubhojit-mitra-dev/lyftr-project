"""Application configuration loaded from environment variables."""

import os
from typing import List
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class Settings:
    """Settings loaded from environment variables with sensible defaults."""

    def __init__(self) -> None:
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
        self.ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        self.ENABLE_FAILURE_SIMULATION: bool = (
            os.getenv("ENABLE_FAILURE_SIMULATION", "true").lower() in ("true", "1", "yes")
        )
        self.LLM_API_KEYS_RAW: str = os.getenv("LLM_API_KEYS", "")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    @property
    def cors_origins(self) -> List[str]:
        """Return parsed list of allowed CORS origins."""
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    def get_configured_keys(self) -> List[str]:
        """Return ordered list of available API keys.

        Keys are ordered key_1, key_2, ... per docs/PRD.md.
        """
        keys = []
        if self.LLM_API_KEYS_RAW:
            keys = [k.strip() for k in self.LLM_API_KEYS_RAW.split(",") if k.strip()]

        # Fallback to distinct individual provider keys if LLM_API_KEYS is empty
        if not keys:
            if self.OPENAI_API_KEY:
                keys.append(self.OPENAI_API_KEY.strip())
            if self.GEMINI_API_KEY:
                keys.append(self.GEMINI_API_KEY.strip())

        return keys


settings = Settings()
