"""Defines the database schema using SQLAlchemy Core."""

from sqlalchemy import (
    JSON,  # Import JSON type
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
)

metadata_obj = MetaData()

sessions_table = Table(
    "sessions",
    metadata_obj,
    Column("session_id", String, primary_key=True),
    Column("session_type", String(50), nullable=False),
    Column("goal", Text, nullable=False),
    Column("participant_ids", JSON, nullable=False),  # Storing list of strings as JSON
    Column("start_time", DateTime, nullable=False),
    Column("end_time", DateTime, nullable=True),
    Column("status", String(50), nullable=False),
    Column("compressed_history", Text, nullable=True),  # Mid-term memory
    Column("summary", Text, nullable=True),
)

dialogue_turns_table = Table(
    "dialogue_turns",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "session_id",
        String,
        ForeignKey("sessions.session_id"),
        nullable=False,
        index=True,
    ),
    Column("participant_id", String, nullable=False),
    Column("timestamp", DateTime, nullable=False),
    Column("content", Text, nullable=False),
)

knowledge_sources_table = Table(
    "knowledge_sources",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("file_path", Text, nullable=False, unique=True),
    Column("file_hash", String(64), nullable=False),
    Column("status", String(50), nullable=False, default="pending"),
    Column("indexed_at", DateTime, nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)
