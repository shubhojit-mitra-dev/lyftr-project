# Backend Service — Resilient LLM Gateway & Persistent Chat API

An enterprise-grade FastAPI application engineered with Domain-Driven Design (DDD), SOLID design principles, Aspect-Oriented Programming (AOP), Inversion of Control (IoC), and Structural Subtyping via Python `typing.Protocol`.

---

## 1. Architecture & Package Structure

The backend follows clean layered architecture and strict Single Responsibility Principle (SRP):

```
backend/
├── app/
│   ├── main.py                               # Application entrypoint & lifespan factory
│   ├── api/
│   │   ├── middleware/
│   │   │   ├── error_handler.py              # AOP Global exception filter & audit logging
│   │   │   └── __init__.py
│   │   └── v1/
│   │       ├── controllers/
│   │       │   ├── chat_controller.py        # Controller handling request/response lifecycle
│   │       │   └── __init__.py
│   │       └── routes/
│   │           ├── chat_routes.py            # Declarative route mappings with Annotated dependencies
│   │           └── __init__.py
│   ├── core/
│   │   ├── config/
│   │   │   ├── settings.py                   # AppConfig loaded from environment
│   │   │   └── __init__.py
│   │   ├── logging/
│   │   │   ├── logger.py                     # Structlog structured logger integration
│   │   │   └── __init__.py
│   │   ├── container.py                      # IoC Dependency Injection Container
│   │   └── __init__.py
│   ├── domain/
│   │   ├── models/
│   │   │   ├── message.py                    # Pure Domain Entities (MessageEntity, ProviderKeyEntity)
│   │   │   └── __init__.py
│   │   └── protocols/
│   │       ├── repository_protocol.py        # MessageRepositoryProtocol (Duck typing / structural subtyping)
│   │       ├── gateway_protocol.py           # LLMGatewayProtocol (Duck typing / structural subtyping)
│   │       └── __init__.py
│   ├── dto/
│   │   ├── chat_dto.py                       # Data Transfer Objects using Annotated & Pydantic v2
│   │   └── __init__.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── sqlite_repository.py          # Asynchronous SQLite persistence implementation
│   │   │   └── __init__.py
│   │   └── gateway/
│   │       ├── litellm_gateway.py            # LiteLLM provider fallback & caching implementation
│   │       └── __init__.py
│   └── services/
│       ├── chat_service.py                   # Domain Service orchestrating business workflows
│       └── __init__.py
├── Dockerfile                                # Multi-stage Python 3.12-slim production build
├── pyproject.toml                            # Dependencies & tool configurations
└── tests/                                    # 33 comprehensive unit and integration tests
```

---

## 2. Design Patterns & Principles Applied

### Single Responsibility & Decoupled Routing
- **Routes (`app.api.v1.routes.chat_routes`)**: Strictly map HTTP methods (`GET`, `POST`), request status codes, and type annotations via `typing.Annotated`.
- **Controllers (`app.api.v1.controllers.chat_controller`)**: Coordinate HTTP action execution and delegate business workflows to services.
- **Service Layer (`app.services.chat_service`)**: Encapsulates conversation history retrieval, prompt context assembly, model execution, and turn persistence.
- **Infrastructure (`app.infrastructure.*`)**: Concrete SQLite and LiteLLM implementations isolated behind interfaces.

### Dependency Inversion & Structural Subtyping (Duck Typing)
- The service layer never depends on concrete database or gateway classes.
- Protocols (`MessageRepositoryProtocol` and `LLMGatewayProtocol`) enforce contracts structurally without rigid nominal inheritance.

### Aspect-Oriented Programming (AOP) & Uniform Error Handling
- `LoggingAOPMiddleware`: Intercepts and logs every inbound request and outbound response with correlation timestamps.
- `global_exception_handler`: Traps uncaught exceptions and `RequestValidationError`, formatting clean JSON error shapes (`{"detail": ...}`) and preventing stack trace or HTML disclosure.

### Structured Logging via Structlog
- Integrates Python standard logging with `structlog`.
- Outputs human-readable logs in local terminals and machine-readable JSON logs in production environments.

---

## 3. Running & Testing

### Run Locally with UV
```bash
# Sync dependencies
uv sync

# Run FastAPI server with uvicorn
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Tests
```bash
uv run pytest -v
# 33 passing unit & integration tests covering gateway, storage, schemas, and API
```

### Run Static Type Check
```bash
uv run mypy -p app --ignore-missing-imports
```
