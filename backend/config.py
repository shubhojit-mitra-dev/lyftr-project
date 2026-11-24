"""Application configuration loaded from environment variables."""

import os
from typing import List
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class Settings:
    """Settings loaded from environment variables with sensible defaults."""

    @property
    def DATABASE_URL(self) -> str:
        return os.getenv("DATABASE_URL", "sqlite:////data/app.db")

    @property
    def ALLOWED_ORIGINS(self) -> str:
        return os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    @property
    def ENABLE_FAILURE_SIMULATION(self) -> bool:
        return os.getenv("ENABLE_FAILURE_SIMULATION", "true").lower() in ("true", "1", "yes")

    @property
    def LLM_API_KEYS_RAW(self) -> str:
        return os.getenv("LLM_API_KEYS", "")

    @property
    def OPENAI_API_KEY(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def GEMINI_API_KEY(self) -> str:
        return os.getenv("GEMINI_API_KEY", "")

    @property
    def cors_origins(self) -> List[str]:
        """Return parsed list of allowed CORS origins."""
        raw = self.ALLOWED_ORIGINS
        if not raw or raw.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

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
