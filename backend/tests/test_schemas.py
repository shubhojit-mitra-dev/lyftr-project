"""Unit tests for Pydantic schemas validating PRD contract specifications."""

import json
import pytest
from pydantic import ValidationError

from schemas import (
    ChatMetadata,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MessageItem,
    SessionHistoryResponse,
)


def test_chat_request_valid():
    req = ChatRequest(session_id="s-123", message="  Hello world!  ", system_prompt="Be helpful")
    assert req.session_id == "s-123"
    assert req.message == "Hello world!"
    assert req.system_prompt == "Be helpful"


def test_chat_request_rejects_empty_or_whitespace_message():
    with pytest.raises(ValidationError) as exc:
        ChatRequest(session_id="s-1", message="   ")
    assert "message cannot be empty" in str(exc.value)


def test_chat_request_rejects_empty_session_id():
    with pytest.raises(ValidationError) as exc:
        ChatRequest(session_id="   ", message="Hello")
    assert "session_id cannot be empty" in str(exc.value)


def test_chat_request_rejects_message_exceeding_4000_chars():
    long_msg = "a" * 4001
    with pytest.raises(ValidationError) as exc:
        ChatRequest(session_id="s-1", message=long_msg)
    assert "cannot exceed 4000 characters" in str(exc.value)


def test_chat_request_rejects_session_id_exceeding_128_chars():
    long_session = "s" * 129
    with pytest.raises(ValidationError) as exc:
        ChatRequest(session_id=long_session, message="Hello")
    assert "session_id" in str(exc.value)


def test_chat_metadata_live_inference():
    meta = ChatMetadata(
        resolution_source="LIVE_INFERENCE",
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        latency_ms=750,
        input_tokens=30,
        output_tokens=15,
        key_id="key_1",
        fallback_attempts=0,
    )
    data = meta.model_dump()
    assert data["resolution_source"] == "LIVE_INFERENCE"
    assert data["key_id"] == "key_1"
    assert data["fallback_attempts"] == 0


def test_chat_metadata_cache_hit():
    meta = ChatMetadata(
        resolution_source="LLM_CACHE",
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        latency_ms=12,
        input_tokens=30,
        output_tokens=15,
        key_id=None,
        fallback_attempts=0,
    )
    data = meta.model_dump()
    assert data["resolution_source"] == "LLM_CACHE"
    assert data["key_id"] is None
    assert data["fallback_attempts"] == 0


def test_chat_response_serialization():
    resp = ChatResponse(
        session_id="s-7f3a",
        reply="The capital of France is Paris.",
        metadata=ChatMetadata(
            resolution_source="LIVE_INFERENCE",
            model="gemini/gemini-2.0-flash",
            latency_ms=812,
            input_tokens=42,
            output_tokens=9,
            key_id="key_1",
            fallback_attempts=0,
        ),
    )
    data = resp.model_dump()
    assert data["session_id"] == "s-7f3a"
    assert data["reply"] == "The capital of France is Paris."
    assert data["metadata"]["key_id"] == "key_1"


def test_message_item_omits_metadata_when_none():
    user_item = MessageItem(role="user", content="Hello")
    user_json = json.loads(user_item.model_dump_json())
    assert "metadata" not in user_json
    assert user_json == {"role": "user", "content": "Hello"}

    asst_item = MessageItem(
        role="assistant",
        content="Hi there",
        metadata={"resolution_source": "LIVE_INFERENCE", "input_tokens": 10, "output_tokens": 5},
    )
    asst_json = json.loads(asst_item.model_dump_json())
    assert "metadata" in asst_json
    assert asst_json["metadata"]["resolution_source"] == "LIVE_INFERENCE"


def test_session_history_response():
    resp = SessionHistoryResponse(
        session_id="s-7f3a",
        messages=[
            MessageItem(role="user", content="What is the capital of France?"),
            MessageItem(
                role="assistant",
                content="The capital of France is Paris.",
                metadata={"resolution_source": "LIVE_INFERENCE", "input_tokens": 42, "output_tokens": 9},
            ),
        ],
    )
    data = json.loads(resp.model_dump_json())
    assert data["session_id"] == "s-7f3a"
    assert len(data["messages"]) == 2
    assert "metadata" not in data["messages"][0]
    assert "metadata" in data["messages"][1]


def test_health_response():
    health = HealthResponse(status="ok", keys_configured=2, cache_enabled=True)
    data = health.model_dump()
    assert data == {"status": "ok", "keys_configured": 2, "cache_enabled": True}
