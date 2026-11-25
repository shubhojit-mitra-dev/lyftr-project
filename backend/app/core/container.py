from functools import lru_cache
from dotenv import load_dotenv

from app.core.config.settings import AppConfig
from app.domain.protocols.repository_protocol import MessageRepositoryProtocol
from app.domain.protocols.gateway_protocol import LLMGatewayProtocol
from app.infrastructure.database.sqlite_repository import SQLiteMessageRepository
from app.infrastructure.gateway.litellm_gateway import LiteLLMGateway
from app.services.chat_service import ChatService

load_dotenv()


class Container:
    """Dependency Injection and Inversion of Control (IoC) container."""

    def __init__(self) -> None:
        self.app_config = AppConfig()

        self.repository: MessageRepositoryProtocol = SQLiteMessageRepository(
            database_url=self.app_config.database_url
        )
        self.gateway: LLMGatewayProtocol = LiteLLMGateway(
            raw_keys_str=self.app_config.llm_api_keys,
            openai_key=self.app_config.openai_api_key,
            gemini_key=self.app_config.gemini_api_key,
            enable_failure_simulation=self.app_config.enable_failure_simulation,
            primary_model=self.app_config.primary_model,
            primary_base_url=self.app_config.primary_base_url,
            fallback_model=self.app_config.fallback_model,
        )
        self.chat_service = ChatService(
            repository=self.repository,
            gateway=self.gateway,
        )


@lru_cache(maxsize=1)
def get_container() -> Container:
    """Singleton IoC container instance."""
    return Container()


def get_chat_service() -> ChatService:
    """FastAPI dependency for ChatService."""
    return get_container().chat_service


def get_repository() -> MessageRepositoryProtocol:
    """FastAPI dependency for MessageRepository."""
    return get_container().repository


def get_gateway() -> LLMGatewayProtocol:
    """FastAPI dependency for LLMGateway."""
    return get_container().gateway
