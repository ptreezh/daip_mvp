"""Implements the DatabaseManager for all database interactions."""

from typing import Optional

from sqlalchemy import create_engine, delete, insert, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from daip_live.core.models import AgentState, DialogueTurn, KnowledgeSource, Session
from daip_live.persistence.tables import (
    dialogue_turns_table,
    knowledge_sources_table,
    metadata_obj,
    sessions_table,
)


class DatabaseManager:
    """Encapsulates all direct interactions with the SQLite database."""

    def __init__(self, db_path: str = ":memory:"):
        if db_path is None:
            db_path = ":memory:"
        if db_path == ":memory:":
            # StaticPool shares a single connection across threads so that
            # asyncio.to_thread calls see the same in-memory database.
            self.engine: Engine = create_engine(
                "sqlite:///:memory:",
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )
        elif db_path.startswith("sqlite:///"):
            self.engine: Engine = create_engine(db_path)
        else:
            self.engine: Engine = create_engine(f"sqlite:///{db_path}")
        self._create_tables()

    def _create_tables(self):
        metadata_obj.create_all(self.engine)

    # --- Session Methods (New Implementation) ---

    def save_session(self, session: Session):
        """Saves or updates a session and its dialogue turns in a transaction."""
        session_dict = session.model_dump()  # Pydantic v2 compatibility
        session_history = session_dict.pop("history", [])

        # Convert AgentState enum to its string value for storage
        session_dict["status"] = session_dict["status"].name

        upsert_stmt = sqlite_insert(sessions_table).values(session_dict)
        upsert_stmt = upsert_stmt.on_conflict_do_update(
            index_elements=["session_id"], set_=dict(upsert_stmt.excluded)
        )

        with self.engine.begin() as conn:
            # 1. Upsert the session record
            conn.execute(upsert_stmt)

            # 2. Delete old dialogue turns for this session to ensure consistency
            conn.execute(
                delete(dialogue_turns_table).where(
                    dialogue_turns_table.c.session_id == session.session_id
                )
            )

            # 3. Insert new dialogue turns if any
            if session_history:
                turns_to_insert = [
                    {"session_id": session.session_id, **turn}
                    for turn in session_history
                ]
                conn.execute(insert(dialogue_turns_table), turns_to_insert)

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieves a full session, including its dialogue history."""
        session_stmt = select(sessions_table).where(
            sessions_table.c.session_id == session_id
        )
        turns_stmt = (
            select(dialogue_turns_table)
            .where(dialogue_turns_table.c.session_id == session_id)
            .order_by(dialogue_turns_table.c.timestamp)
        )

        with self.engine.connect() as conn:
            session_row = conn.execute(session_stmt).first()
            if not session_row:
                return None

            session_data = dict(session_row._asdict())
            # Convert status string back to AgentState enum
            session_data["status"] = AgentState[session_data["status"]]

            turns_rows = conn.execute(turns_stmt).all()
            history = [DialogueTurn(**row._asdict()) for row in turns_rows]
            session_data["history"] = history

        return Session(**session_data)

    def list_sessions(self) -> list[Session]:
        """Retrieves all sessions (metadata only, without history)."""
        stmt = select(sessions_table).order_by(sessions_table.c.start_time.desc())
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).all()

        sessions = []
        for row in rows:
            session_data = dict(row._asdict())
            session_data["status"] = AgentState[session_data["status"]]
            sessions.append(Session(**session_data))
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Deletes a session and its associated dialogue turns."""
        with self.engine.begin() as conn:
            # Delete dialogue turns first (foreign key dependency)
            conn.execute(
                delete(dialogue_turns_table).where(
                    dialogue_turns_table.c.session_id == session_id
                )
            )
            # Delete the session
            session_deleted = conn.execute(
                delete(sessions_table).where(sessions_table.c.session_id == session_id)
            )
            return session_deleted.rowcount > 0

    def clear_all_sessions(self) -> int:
        """Deletes all sessions and their dialogue turns from the database."""
        with self.engine.begin() as conn:
            # Order matters due to foreign key constraints
            conn.execute(delete(dialogue_turns_table))
            result = conn.execute(delete(sessions_table))
            return result.rowcount

    # --- Context Manager Support for Database Operations ---

    def get_connection(self):
        """
        Get a database connection for general database operations.

        This method provides a context manager for database operations
        that don't involve session-specific data retrieval.

        Usage:
            with db_manager.get_connection() as conn:
                result = conn.execute("SELECT 1").fetchone()

        Returns:
            SQLAlchemy connection context manager
        """
        return self.engine.connect()

    # For backward compatibility, make get_session work as both session retriever and connection provider  # noqa: E501
    def __call__(self, session_id: Optional[str] = None):
        """
        Make DatabaseManager callable to provide flexible access patterns.

        This allows the manager to work in multiple ways:
        1. db_manager(session_id) -> Get specific session
        2. db_manager() -> Get connection context manager
        3. with db_manager() as conn: -> Use as context manager

        Args:
            session_id: Optional session ID to retrieve

        Returns:
            Session object if session_id provided,
            Connection context manager if no session_id
        """
        if session_id is not None:
            return self.get_session(session_id)
        else:
            return self.get_connection()

    # --- Knowledge Source Methods (Unchanged) ---

    def get_knowledge_source_by_path(self, file_path: str) -> Optional[KnowledgeSource]:
        stmt = select(knowledge_sources_table).where(
            knowledge_sources_table.c.file_path == file_path
        )
        with self.engine.connect() as conn:
            row = conn.execute(stmt).first()
        return KnowledgeSource(**row._asdict()) if row else None

    def get_all_knowledge_sources(self) -> list[KnowledgeSource]:
        stmt = select(knowledge_sources_table)
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).all()
        return [KnowledgeSource(**row._asdict()) for row in rows]

    def upsert_knowledge_source(self, source: KnowledgeSource) -> KnowledgeSource:
        insert_stmt = sqlite_insert(knowledge_sources_table).values(
            source.model_dump(exclude_none=True)
        )
        update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["file_path"],
            set_={
                "file_hash": insert_stmt.excluded.file_hash,
                "status": insert_stmt.excluded.status,
                "indexed_at": insert_stmt.excluded.indexed_at,
            },
        ).returning(knowledge_sources_table)

        with self.engine.begin() as conn:
            result = conn.execute(update_stmt)
            upserted_row = result.first()

        if not upserted_row:
            raise RuntimeError("Failed to upsert knowledge source.")

        return KnowledgeSource(**upserted_row._asdict())

    def delete_knowledge_source(self, file_path: str) -> None:
        stmt = delete(knowledge_sources_table).where(
            knowledge_sources_table.c.file_path == file_path
        )
        with self.engine.begin() as conn:
            conn.execute(stmt)

    def get_knowledge_sources_by_ids(self, ids: list[int]) -> list[KnowledgeSource]:
        """Retrieves a list of KnowledgeSource objects by their primary key IDs."""
        stmt = select(knowledge_sources_table).where(
            knowledge_sources_table.c.id.in_(ids)
        )
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).all()
        return [KnowledgeSource(**row._asdict()) for row in rows]
