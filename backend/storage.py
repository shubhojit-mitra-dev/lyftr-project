"""SQLite storage repository for LLM Chatbot session history.

Follows the schema specification in docs/PRD.md:
- messages table with auto-increment id, session_id, role, content, metadata (JSON), created_at (ISO-8601)
- Compound index on (session_id, created_at)
- Atomic turn insertion (both user and assistant messages or neither)
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import aiosqlite

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages (session_id, created_at);
"""


def parse_sqlite_url(url: str) -> str:
    """Extract filesystem path from SQLite connection string."""
    if url.startswith("sqlite:////"):
        # e.g. sqlite:////data/app.db -> /data/app.db
        return "/" + url[len("sqlite:////") :]
    elif url.startswith("sqlite:///"):
        # e.g. sqlite:///data/app.db or sqlite:///./data/app.db
        return url[len("sqlite:///") :]
    elif url.startswith("sqlite://"):
        return url[len("sqlite://") :]
    return url


def resolve_db_path(database_url: Optional[str] = None) -> str:
    """Resolve database path with graceful fallback for local development."""
    raw_url = database_url or os.getenv("DATABASE_URL", "sqlite:////data/app.db")
    target_path = parse_sqlite_url(raw_url)

    # Determine directory
    target_dir = os.path.dirname(os.path.abspath(target_path)) or "."
    try:
        os.makedirs(target_dir, exist_ok=True)
        # Test write permissions
        test_file = os.path.join(target_dir, ".perm_check")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return os.path.abspath(target_path)
    except (PermissionError, OSError) as exc:
        logger.warning(
            "Target database directory %s not writable (%s). Falling back to ./data/app.db",
            target_dir,
            exc,
        )
        fallback_dir = os.path.abspath("./data")
        os.makedirs(fallback_dir, exist_ok=True)
        filename = os.path.basename(target_path) or "app.db"
        return os.path.join(fallback_dir, filename)


class StorageRepository:
    """Asynchronous SQLite repository for multi-turn session persistence."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or resolve_db_path()

    async def init_db(self) -> None:
        """Initialize database schema, pragmas, and indexes."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode = WAL;")
            await db.execute("PRAGMA synchronous = NORMAL;")
            await db.execute("PRAGMA busy_timeout = 5000;")
            await db.executescript(SCHEMA_SQL)
            await db.commit()
        logger.info("SQLite database initialized at: %s", self.db_path)

    async def health_check(self) -> bool:
        """Verify database connectivity."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT 1") as cursor:
                    row = await cursor.fetchone()
                    return row is not None and row[0] == 1
        except Exception as exc:
            logger.error("Database health check failed: %s", exc)
            return False

    async def session_exists(self, session_id: str) -> bool:
        """Check if any messages exist for the given session_id."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM messages WHERE session_id = ? LIMIT 1",
                (session_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve stored history for a session, oldest first, without system prompt."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT role, content, metadata, created_at "
                "FROM messages "
                "WHERE session_id = ? AND role IN ('user', 'assistant') "
                "ORDER BY id ASC",
                (session_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    item: dict[str, Any] = {
                        "role": row["role"],
                        "content": row["content"],
                    }
                    if row["role"] == "assistant" and row["metadata"]:
                        try:
                            item["metadata"] = json.loads(row["metadata"])
                        except (json.JSONDecodeError, TypeError):
                            item["metadata"] = None
                    result.append(item)
                return result

    async def add_turn(
        self,
        session_id: str,
        user_content: str,
        assistant_content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Atomically persist a complete user/assistant turn.

        Ensures atomic persistence: both messages are committed, or neither.
        """
        now = datetime.now(timezone.utc).isoformat()
        metadata_json = json.dumps(metadata) if metadata is not None else None

        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Use a transaction to guarantee all-or-nothing
                await db.execute("BEGIN IMMEDIATE")
                await db.execute(
                    "INSERT INTO messages (session_id, role, content, metadata, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (session_id, "user", user_content, None, now),
                )
                await db.execute(
                    "INSERT INTO messages (session_id, role, content, metadata, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (session_id, "assistant", assistant_content, metadata_json, now),
                )
                await db.commit()
            except Exception as exc:
                await db.rollback()
                logger.error("Failed to commit conversation turn atomically: %s", exc)
                raise


# Global singleton instance
storage = StorageRepository()
