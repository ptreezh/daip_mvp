from datetime import datetime

import pytest

from daip_live.core.models import KnowledgeSource
from daip_live.persistence.database import DatabaseManager


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Fixture to create a DatabaseManager with an in-memory SQLite DB for testing."""
    return DatabaseManager(db_path=":memory:")


class TestKnowledgeSourceDB:
    def test_get_non_existent_source(self, db_manager: DatabaseManager):
        """Tests that getting a source that does not exist returns None."""
        assert db_manager.get_knowledge_source_by_path("non_existent_file.txt") is None

    def test_upsert_as_insert(self, db_manager: DatabaseManager):
        """Tests that upsert correctly inserts a new record."""
        source = KnowledgeSource(
            file_path="/path/to/file.txt",
            file_hash="abc",
            status="pending",
        )

        upserted_source = db_manager.upsert_knowledge_source(source)

        assert upserted_source.id is not None
        assert upserted_source.file_path == "/path/to/file.txt"
        assert upserted_source.file_hash == "abc"
        assert upserted_source.created_at is not None

        retrieved_source = db_manager.get_knowledge_source_by_path("/path/to/file.txt")
        assert retrieved_source is not None
        assert retrieved_source.id == upserted_source.id

    def test_upsert_as_update(self, db_manager: DatabaseManager):
        """Tests that upsert correctly updates an existing record."""
        # Insert initial record
        initial_source = db_manager.upsert_knowledge_source(
            KnowledgeSource(
                file_path="/path/to/update.txt",
                file_hash="123",
                status="indexed",
            )
        )

        # Now, create an updated version and upsert it
        updated_source_data = KnowledgeSource(
            file_path="/path/to/update.txt",  # Same path
            file_hash="456",  # New hash
            status="pending",  # New status
            indexed_at=datetime.now(),
        )
        upserted_source = db_manager.upsert_knowledge_source(updated_source_data)

        assert upserted_source.id == initial_source.id  # ID should not change
        assert upserted_source.file_hash == "456"  # Hash should be updated
        assert upserted_source.status == "pending"  # Status should be updated
        assert upserted_source.indexed_at is not None

    def test_get_all_sources(self, db_manager: DatabaseManager):
        """Tests retrieving all knowledge sources."""
        assert db_manager.get_all_knowledge_sources() == []  # Should be empty initially

        db_manager.upsert_knowledge_source(
            KnowledgeSource(file_path="f1.txt", file_hash="h1", status="indexed")
        )
        db_manager.upsert_knowledge_source(
            KnowledgeSource(file_path="f2.txt", file_hash="h2", status="pending")
        )

        all_sources = db_manager.get_all_knowledge_sources()
        assert len(all_sources) == 2
        assert {s.file_path for s in all_sources} == {"f1.txt", "f2.txt"}

    def test_delete_source(self, db_manager: DatabaseManager):
        """Tests deleting a knowledge source."""
        db_manager.upsert_knowledge_source(
            KnowledgeSource(file_path="delete_me.txt", file_hash="h", status="indexed")
        )

        # Verify it exists
        assert db_manager.get_knowledge_source_by_path("delete_me.txt") is not None

        # Delete it
        db_manager.delete_knowledge_source("delete_me.txt")

        # Verify it's gone
        assert db_manager.get_knowledge_source_by_path("delete_me.txt") is None
