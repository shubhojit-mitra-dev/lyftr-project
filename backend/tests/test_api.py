"""Integration tests for FastAPI application endpoints."""

import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.container import get_repository as get_storage_dep
from app.infrastructure.database.sqlite_repository import SQLiteMessageRepository as StorageRepository



@pytest.fixture
async def test_client():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_api.db")
        repo = StorageRepository(db_path=test_db)
        await repo.init_db()

        # Override dependency
        app.dependency_overrides[get_storage_dep] = lambda: repo

        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, repo

        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_endpoint(test_client):
    client, _ = test_client
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "keys_configured" in data
    assert data["cache_enabled"] is True


@pytest.mark.asyncio
async def test_sessions_not_found(test_client):
    client, _ = test_client
    resp = await client.get("/sessions/unknown-session-123/messages")
    assert resp.status_code == 404
    data = resp.json()
    assert data == {"detail": "session not found"}


@pytest.mark.asyncio
async def test_sessions_retrieval_after_turns(test_client):
    client, repo = test_client
    session_id = "s-test-session"

    # Add turns to repository
    await repo.add_turn(
        session_id=session_id,
        user_content="What is Paris?",
        assistant_content="Paris is the capital of France.",
        metadata={
            "resolution_source": "LIVE_INFERENCE",
            "input_tokens": 12,
            "output_tokens": 8,
        },
    )

    resp = await client.get(f"/sessions/{session_id}/messages")
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == session_id
    assert len(data["messages"]) == 2

    # User message
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][0]["content"] == "What is Paris?"
    assert "metadata" not in data["messages"][0]

    # Assistant message
    assert data["messages"][1]["role"] == "assistant"
    assert data["messages"][1]["content"] == "Paris is the capital of France."
    assert data["messages"][1]["metadata"] == {
        "resolution_source": "LIVE_INFERENCE",
        "input_tokens": 12,
        "output_tokens": 8,
    }


@pytest.mark.asyncio
async def test_chat_endpoint_valid_request(test_client, monkeypatch):
    monkeypatch.setenv("LITELLM_MOCK_RESPONSE", "Test AI response")
    client, _ = test_client
    payload = {
        "session_id": "s-post-chat-1",
        "message": "Hello AI!",
    }
    resp = await client.post("/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "s-post-chat-1"
    assert "reply" in data
    assert data["metadata"]["resolution_source"] == "LIVE_INFERENCE"

    # Verify session now exists in history
    hist_resp = await client.get("/sessions/s-post-chat-1/messages")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert len(hist_data["messages"]) == 2


@pytest.mark.asyncio
async def test_chat_endpoint_validation_errors(test_client):
    client, _ = test_client

    # Empty message
    resp = await client.post("/chat", json={"session_id": "s-1", "message": "   "})
    assert resp.status_code == 422
    assert "detail" in resp.json()

    # Empty session_id
    resp = await client.post("/chat", json={"session_id": "", "message": "Hello"})
    assert resp.status_code == 422
    assert "detail" in resp.json()

    # Message exceeding 4000 characters
    resp = await client.post("/chat", json={"session_id": "s-1", "message": "x" * 4001})
    assert resp.status_code == 422
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_generic_exception_handler(test_client):
    client, _ = test_client

    # Cause unhandled error by registering a route that raises Exception
    @app.get("/test-internal-error")
    async def error_route():
        raise RuntimeError("Unexpected failure")

    resp = await client.get("/test-internal-error")
    assert resp.status_code == 500
    assert resp.headers["content-type"] == "application/json"
    assert resp.json() == {"detail": "Internal server error"}
