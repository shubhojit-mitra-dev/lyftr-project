import os
from functools import lru_cache
from dotenv import load_dotenv

from app.domain.interfaces.repository_interface import IMessageRepository
from app.domain.interfaces.gateway_interface import ILLMGateway
from app.infrastructure.database.sqlite_repository import SQLiteMessageRepository
from app.infrastructure.gateway.litellm_gateway import LiteLLMGateway
from app.services.chat_service import ChatService

load_dotenv()


class Container:
    """Dependency Injection and Inversion of Control (IoC) container."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
        self.llm_api_keys = os.getenv("LLM_API_KEYS", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.enable_failure_simulation = (
            os.getenv("ENABLE_FAILURE_SIMULATION", "true").lower() == "true"
        )
        self.allowed_origins = [
            o.strip()
            for o in os.getenv(
                "ALLOWED_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000,*",
            ).split(",")
            if o.strip()
        ]

        self.repository: IMessageRepository = SQLiteMessageRepository(self.database_url)
        self.gateway: ILLMGateway = LiteLLMGateway(
            raw_keys_str=self.llm_api_keys,
            openai_key=self.openai_api_key,
            gemini_key=self.gemini_api_key,
            enable_failure_simulation=self.enable_failure_simulation,
        )
        self.chat_service = ChatService(self.repository, self.gateway)


@lru_cache(maxsize=1)
def get_container() -> Container:
    """Singleton IoC container instance."""
    return Container()


def get_chat_service() -> ChatService:
    """FastAPI dependency for ChatService."""
    return get_container().chat_service


def get_repository() -> IMessageRepository:
    """FastAPI dependency for MessageRepository."""
    return get_container().repository


def get_gateway() -> ILLMGateway:
    """FastAPI dependency for LLMGateway."""
    return get_container().gateway
