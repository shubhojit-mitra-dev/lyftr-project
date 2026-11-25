"""Comprehensive tests for LiteLLM Gateway, Response Caching, Provider Failover, and Simulation."""

import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config.constants import (
    DEFAULT_PRIMARY_MODEL,
    DEFAULT_PRIMARY_API_BASE,
    DEFAULT_FALLBACK_MODEL,
)
from app.core.container import get_container, get_gateway as get_gateway_dep, get_repository as get_storage_dep
from app.infrastructure.gateway.litellm_gateway import LiteLLMGateway

class LLMGateway(LiteLLMGateway):
    def __init__(self, raw_keys_str: str = "", enable_failure_simulation: bool = True):
        super().__init__(raw_keys_str=raw_keys_str or "mock-nv-key,mock-gemini-key", enable_failure_simulation=enable_failure_simulation)

from app.infrastructure.database.sqlite_repository import SQLiteMessageRepository as StorageRepository
from app.main import app

gateway = get_container().gateway
settings = get_container().app_config

def build_key_pool(raw_keys):
    gw = LLMGateway(raw_keys_str=",".join(raw_keys))
    return gw.key_pool

def parse_simulate_failure_header(header_val):
    gw = LLMGateway(raw_keys_str="dummy_key_1,dummy_key_2")
    return gw.parse_simulate_failure_header(header_val)



@pytest.fixture
def mock_keys():
    return ["mock-nv-key", "mock-gemini-key"]


def test_build_key_pool():
    """Verify provider key mapping rules."""
    raw = ["nvapi-test-primary", "AQ.test-gemini", "sk-test-openai", "custom-placeholder"]
    pool = build_key_pool(raw)

    assert len(pool) == 4
    # key_1: NVIDIA NIM
    assert pool[0].key_id == "key_1"
    assert pool[0].model == DEFAULT_PRIMARY_MODEL
    assert pool[0].api_base == DEFAULT_PRIMARY_API_BASE

    # key_2: Gemini
    assert pool[1].key_id == "key_2"
    assert pool[1].model == DEFAULT_FALLBACK_MODEL
    assert pool[1].api_base is None

    # key_3: OpenAI
    assert pool[2].key_id == "key_3"
    assert pool[2].model == "openai/gpt-4o-mini"

    # key_4: Alternating index fallback
    assert pool[3].key_id == "key_4"
    assert pool[3].model == DEFAULT_FALLBACK_MODEL


def test_parse_simulate_failure_header():
    """Verify parsing of X-Simulate-Failure header values."""
    assert parse_simulate_failure_header(None) == {}
    assert parse_simulate_failure_header("") == {}
    assert parse_simulate_failure_header("key_1=429") == {"key_1": 429}
    assert parse_simulate_failure_header("key_1=429, key_2=500") == {"key_1": 429, "key_2": 500}
    assert parse_simulate_failure_header(" *=503 ") == {"*": 503}
    # Invalid status codes are ignored
    assert parse_simulate_failure_header("key_1=200, key_2=404, key_3=429") == {"key_3": 429}


@pytest.mark.asyncio
async def test_gateway_normal_completion(mock_keys):
    """Test normal live inference on key_1."""
    messages = [{"role": "user", "content": "Hello gateway normal"}]
    reply, meta = await gateway.complete(
        messages=messages,
        configured_keys=mock_keys,
        mock_response="Primary response",
    )

    assert reply == "Primary response"
    assert meta.resolution_source == "LIVE_INFERENCE"
    assert meta.key_id == "key_1"
    assert meta.fallback_attempts == 0
    assert meta.input_tokens > 0
    assert meta.output_tokens > 0
    assert meta.latency_ms >= 1


@pytest.mark.asyncio
async def test_gateway_response_caching(mock_keys):
    """Test caching behavior: second identical request hits cache."""
    messages = [{"role": "user", "content": "What is the boiling point of water?"}]

    # 1. First call: Live Inference
    reply1, meta1 = await gateway.complete(
        messages=messages,
        configured_keys=mock_keys,
        mock_response="100 degrees Celsius",
    )
    assert meta1.resolution_source == "LIVE_INFERENCE"
    assert meta1.key_id == "key_1"
    assert meta1.fallback_attempts == 0

    # 2. Second call with exact same messages: Cache Hit
    reply2, meta2 = await gateway.complete(
        messages=messages,
        configured_keys=mock_keys,
        mock_response="Different mock text that must NOT be returned",
    )
    assert meta2.resolution_source == "LLM_CACHE"
    assert meta2.key_id is None
    assert meta2.fallback_attempts == 0
    assert reply2 == reply1 == "100 degrees Celsius"
    assert meta2.input_tokens == meta1.input_tokens
    assert meta2.output_tokens == meta1.output_tokens


@pytest.mark.asyncio
async def test_gateway_failover_simulation_key_1(mock_keys):
    """Test X-Simulate-Failure key_1=429 fails over to key_2."""
    messages = [{"role": "user", "content": "Test failover simulation 429"}]
    reply, meta = await gateway.complete(
        messages=messages,
        x_simulate_failure="key_1=429",
        configured_keys=mock_keys,
        mock_response="Secondary key response",
    )

    assert reply == "Secondary key response"
    assert meta.resolution_source == "LIVE_INFERENCE"
    assert meta.key_id == "key_2"
    assert meta.fallback_attempts == 1


@pytest.mark.asyncio
async def test_gateway_failover_simulation_500(mock_keys):
    """Test X-Simulate-Failure key_1=500 fails over to key_2."""
    messages = [{"role": "user", "content": "Test failover simulation 500"}]
    reply, meta = await gateway.complete(
        messages=messages,
        x_simulate_failure="key_1=500",
        configured_keys=mock_keys,
        mock_response="Secondary key response 500",
    )

    assert reply == "Secondary key response 500"
    assert meta.resolution_source == "LIVE_INFERENCE"
    assert meta.key_id == "key_2"
    assert meta.fallback_attempts == 1


@pytest.mark.asyncio
async def test_gateway_simulation_disabled_ignores_header(mock_keys):
    """When simulation is disabled, X-Simulate-Failure header is ignored."""
    messages = [{"role": "user", "content": "Test simulation disabled"}]
    reply, meta = await gateway.complete(
        messages=messages,
        x_simulate_failure="key_1=429",
        configured_keys=mock_keys,
        enable_simulation=False,
        mock_response="Primary response",
    )

    assert reply == "Primary response"
    assert meta.resolution_source == "LIVE_INFERENCE"
    assert meta.key_id == "key_1"
    assert meta.fallback_attempts == 0


@pytest.mark.asyncio
async def test_cross_session_cache_sharing():
    """Verify PRD Sec 3: The same first message sent in a new session returns LLM_CACHE."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_cache_sessions.db")
        repo = StorageRepository(db_path=test_db)
        await repo.init_db()

        app.dependency_overrides[get_storage_dep] = lambda: repo

        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            os.environ["LITELLM_MOCK_RESPONSE"] = "Consistent cached answer"
            try:
                # Session 1
                resp1 = await client.post(
                    "/chat",
                    json={"session_id": "session-alpha", "message": "What is 2+2?"},
                )
                assert resp1.status_code == 200
                d1 = resp1.json()
                assert d1["metadata"]["resolution_source"] == "LIVE_INFERENCE"
                assert d1["metadata"]["key_id"] == "key_1"
                assert d1["reply"] == "Consistent cached answer"

                # Session 2 with exact same message
                resp2 = await client.post(
                    "/chat",
                    json={"session_id": "session-beta", "message": "What is 2+2?"},
                )
                assert resp2.status_code == 200
                d2 = resp2.json()
                assert d2["metadata"]["resolution_source"] == "LLM_CACHE"
                assert d2["metadata"]["key_id"] is None
                assert d2["metadata"]["fallback_attempts"] == 0
                assert d2["reply"] == d1["reply"]

                # Session 3 with different message must NOT hit cache
                resp3 = await client.post(
                    "/chat",
                    json={"session_id": "session-gamma", "message": "What is 3+3?"},
                )
                assert resp3.status_code == 200
                d3 = resp3.json()
                assert d3["metadata"]["resolution_source"] == "LIVE_INFERENCE"
                assert d3["metadata"]["key_id"] == "key_1"
            finally:
                os.environ.pop("LITELLM_MOCK_RESPONSE", None)
                app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_gateway_failover_all_keys_exhausted(mock_keys):
    """Test simulation of all keys failing returns 503."""
    from fastapi import HTTPException

    messages = [{"role": "user", "content": "Test all keys failing"}]
    with pytest.raises(HTTPException) as exc_info:
        await gateway.complete(
            messages=messages,
            x_simulate_failure="*=429",
            configured_keys=mock_keys,
            mock_response="Should not be returned",
        )

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "all providers unavailable"


@pytest.mark.asyncio
async def test_chat_api_simulation_and_persistence():
    """Test full API stack with failure simulation, failover, and zero persistence on 503."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_chat_failover.db")
        repo = StorageRepository(db_path=test_db)
        await repo.init_db()

        # Custom gateway instance with mock keys
        custom_gateway = LLMGateway()

        app.dependency_overrides[get_storage_dep] = lambda: repo
        app.dependency_overrides[get_gateway_dep] = lambda: custom_gateway

        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            session_id = "s-failover-session-1"

            # 1. Send request with key_1=429 -> Succeeded on key_2
            os.environ["LITELLM_MOCK_RESPONSE"] = "Answer from key 2"
            try:
                resp1 = await client.post(
                    "/chat",
                    json={"session_id": session_id, "message": "Test failover message"},
                    headers={"X-Simulate-Failure": "key_1=429"},
                )
                assert resp1.status_code == 200
                data1 = resp1.json()
                assert data1["session_id"] == session_id
                assert data1["metadata"]["key_id"] == "key_2"
                assert data1["metadata"]["fallback_attempts"] == 1
                assert data1["metadata"]["resolution_source"] == "LIVE_INFERENCE"

                # Check turn is stored in history
                hist1 = await client.get(f"/sessions/{session_id}/messages")
                assert hist1.status_code == 200
                assert len(hist1.json()["messages"]) == 2

                # 2. Send request with *=429 -> Clean 503
                resp2 = await client.post(
                    "/chat",
                    json={"session_id": session_id, "message": "This message must fail"},
                    headers={"X-Simulate-Failure": "*=429"},
                )
                assert resp2.status_code == 503
                assert resp2.json() == {"detail": "all providers unavailable"}

                # Check history has NOT grown (zero persistence on 503)
                hist2 = await client.get(f"/sessions/{session_id}/messages")
                assert hist2.status_code == 200
                assert len(hist2.json()["messages"]) == 2
                assert hist2.json()["messages"][-1]["content"] == "Answer from key 2"

            finally:
                os.environ.pop("LITELLM_MOCK_RESPONSE", None)
                app.dependency_overrides.clear()
