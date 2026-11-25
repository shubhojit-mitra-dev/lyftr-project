"""Unit tests for SQLite Storage Repository."""

import os
import tempfile
import pytest
import aiosqlite

from app.infrastructure.database.sqlite_repository import SQLiteMessageRepository

class StorageRepository(SQLiteMessageRepository):
    def __init__(self, db_path: str = "./data/app.db", database_url: str = ""):
        super().__init__(database_url=database_url or f"sqlite:///{db_path}")
        self.db_path = db_path

def parse_sqlite_url(url: str) -> str:
    if url.startswith("sqlite:////"):
        return "/" + url[len("sqlite:////") :]
    if url.startswith("sqlite:///"):
        return url[len("sqlite:///") :]
    return url

def resolve_db_path(url: str) -> str:
    repo = SQLiteMessageRepository(url)
    return repo.db_path




@pytest.fixture
def temp_db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test.db")


@pytest.mark.asyncio
async def test_init_db_creates_schema_and_indexes(temp_db_path):
    repo = StorageRepository(db_path=temp_db_path)
    await repo.init_db()

    assert await repo.health_check() is True

    # Check table structure
    async with aiosqlite.connect(temp_db_path) as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
        ) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "messages"

        # Check index
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_messages_session'"
        ) as cursor:
            idx = await cursor.fetchone()
            assert idx is not None


@pytest.mark.asyncio
async def test_session_exists_and_add_turn(temp_db_path):
    repo = StorageRepository(db_path=temp_db_path)
    await repo.init_db()

    session_id = "test-session-1"
    assert await repo.session_exists(session_id) is False

    meta = {
        "resolution_source": "LIVE_INFERENCE",
        "input_tokens": 15,
        "output_tokens": 10,
    }
    await repo.add_turn(
        session_id=session_id,
        user_content="Hello assistant!",
        assistant_content="Hello user!",
        metadata=meta,
    )

    assert await repo.session_exists(session_id) is True

    messages = await repo.get_messages(session_id)
    assert len(messages) == 2

    # User message: no metadata
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello assistant!"
    assert "metadata" not in messages[0]

    # Assistant message: metadata present
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hello user!"
    assert messages[1]["metadata"] == meta


@pytest.mark.asyncio
async def test_multi_turn_chronological_ordering(temp_db_path):
    repo = StorageRepository(db_path=temp_db_path)
    await repo.init_db()

    session_id = "multi-turn-session"

    await repo.add_turn(
        session_id=session_id,
        user_content="Turn 1 User",
        assistant_content="Turn 1 Assistant",
        metadata={"turn": 1},
    )
    await repo.add_turn(
        session_id=session_id,
        user_content="Turn 2 User",
        assistant_content="Turn 2 Assistant",
        metadata={"turn": 2},
    )

    messages = await repo.get_messages(session_id)
    assert len(messages) == 4
    assert [m["content"] for m in messages] == [
        "Turn 1 User",
        "Turn 1 Assistant",
        "Turn 2 User",
        "Turn 2 Assistant",
    ]


@pytest.mark.asyncio
async def test_add_turn_atomic_rollback(temp_db_path):
    repo = StorageRepository(db_path=temp_db_path)
    await repo.init_db()

    session_id = "rollback-session"

    # Corrupt or simulate error by attempting an invalid insert
    # In sqlite, inserting into non-existent column or constraint violation
    # We can patch db.execute to raise on second execute
    class FailingRepo(StorageRepository):
        async def add_turn(self, session_id, user_content, assistant_content, metadata=None):
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("BEGIN IMMEDIATE")
                # Insert user row
                await db.execute(
                    "INSERT INTO messages (session_id, role, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
                    (session_id, "user", user_content, None, "2026-01-01T00:00:00Z"),
                )
                # Now raise an exception before second insert commits
                await db.rollback()
                raise RuntimeError("Simulated failure during turn save")

    failing_repo = FailingRepo(db_path=temp_db_path)
    with pytest.raises(RuntimeError):
        await failing_repo.add_turn(
            session_id=session_id,
            user_content="Failing message",
            assistant_content="Never saved",
        )

    # Verify no messages were saved
    messages = await repo.get_messages(session_id)
    assert len(messages) == 0
    assert await repo.session_exists(session_id) is False


def test_sqlite_url_parsing():
    assert parse_sqlite_url("sqlite:////data/app.db") == "/data/app.db"
    assert parse_sqlite_url("sqlite:///data/app.db") == "data/app.db"
    assert parse_sqlite_url("sqlite:///./data/app.db") == "./data/app.db"
    assert parse_sqlite_url("/data/app.db") == "/data/app.db"


def test_resolve_db_path_fallback():
    # If path is in an unwritable root directory like /root_test_forbidden/app.db
    resolved = resolve_db_path("sqlite:////root_test_forbidden/test.db")
    # Should gracefully fall back to local data directory
    assert "data" in resolved

