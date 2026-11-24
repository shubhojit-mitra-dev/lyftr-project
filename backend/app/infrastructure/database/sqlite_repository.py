import json
import logging
import os
from pathlib import Path
from typing import Optional, Any
import aiosqlite

from app.domain.models.message import MessageEntity
from app.domain.interfaces.repository_interface import IMessageRepository

logger = logging.getLogger(__name__)


class SQLiteMessageRepository(IMessageRepository):
    """Clean SQLite repository implementation adhering to IMessageRepository."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.db_path = self._resolve_db_path(database_url)

    def _resolve_db_path(self, url: str) -> str:
        """Parse sqlite:// URL and ensure target directory exists."""
        if url.startswith("sqlite:///"):
            path = url[len("sqlite:///") :]
        elif url.startswith("sqlite://"):
            path = url[len("sqlite://") :]
        else:
            path = url

        path_obj = Path(path)
        try:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            return str(path_obj)
        except (PermissionError, OSError) as e:
            fallback = Path("./data/app.db")
            fallback.parent.mkdir(parents=True, exist_ok=True)
            logger.warning(
                f"Cannot write to {path} ({e}). Falling back to local {fallback}"
            )
            return str(fallback)

    async def init_db(self) -> None:
        """Create messages table and compound index."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id  TEXT NOT NULL,
                    role        TEXT NOT NULL,
                    content     TEXT NOT NULL,
                    metadata    TEXT,
                    created_at  TEXT NOT NULL
                );
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages (session_id, created_at ASC);
                """
            )
            await db.commit()
            logger.info(f"SQLite repository initialized at {self.db_path}")

    async def get_messages(self, session_id: str) -> list[MessageEntity]:
        """Fetch all messages for session ordered oldest first."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, session_id, role, content, metadata, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (session_id,),
            )
            rows = await cursor.fetchall()
            messages: list[MessageEntity] = []
            for row in rows:
                meta = json.loads(row["metadata"]) if row["metadata"] else None
                messages.append(
                    MessageEntity(
                        id=row["id"],
                        session_id=row["session_id"],
                        role=row["role"],
                        content=row["content"],
                        metadata=meta,
                        created_at=row["created_at"],
                    )
                )
            return messages

    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM messages WHERE session_id = ? LIMIT 1",
                (session_id,),
            )
            row = await cursor.fetchone()
            return row is not None

    async def add_turn(
        self,
        session_id: str,
        user_content: str,
        assistant_content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Atomically persist user turn and assistant reply."""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("BEGIN TRANSACTION")
                u_entity = MessageEntity(session_id=session_id, role="user", content=user_content)
                await db.execute(
                    """
                    INSERT INTO messages (session_id, role, content, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (session_id, u_entity.role, u_entity.content, None, u_entity.created_at),
                )
                a_meta_json = json.dumps(metadata) if metadata else None
                a_entity = MessageEntity(
                    session_id=session_id,
                    role="assistant",
                    content=assistant_content,
                    metadata=metadata,
                )
                await db.execute(
                    """
                    INSERT INTO messages (session_id, role, content, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (session_id, a_entity.role, a_entity.content, a_meta_json, a_entity.created_at),
                )
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"Atomic add_turn transaction failed: {e}")
                raise e

    async def health_check(self) -> bool:
        """Verify DB responsiveness."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT 1")
                row = await cursor.fetchone()
                return row is not None and row[0] == 1
        except Exception as e:
            logger.error(f"SQLite health check failed: {e}")
            return False
