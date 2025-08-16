"""@Time    : 2025-07-04 11:00:00
@Author  : DAIP-LIVE Team
@File    : test_memory_service.py
@Description:
    Unit tests for the MemoryService, including SSKG integration.
"""
import sqlite3
from pathlib import Path

import pytest

from src.core_services.memory_service import MemoryService


@pytest.fixture()
def temp_memory_dir(tmp_path: Path) -> str:
    """Create a temporary directory for memory data."""
    return str(tmp_path)


class TestMemoryServiceSSKG:
    """Test suite for the SSKG functionality within MemoryService."""

    def test_add_and_query_fact(self, temp_memory_dir: str):
        """Tests adding a single fact and querying it back with a specific predicate.
        """
        # Arrange
        memory_service = MemoryService(data_dir=temp_memory_dir)

        # Act
        memory_service.add_fact_to_sskg("Socrates", "is_a", "philosopher", metadata={"source": "test"})
        results = memory_service.query_sskg("Socrates", "is_a")

        # Assert
        assert len(results) == 1
        fact = results[0]
        assert fact["subject"] == "Socrates"
        assert fact["predicate"] == "is_a"
        assert fact["object"] == "philosopher"
        assert fact["metadata"]["source"] == "test"

    def test_query_by_subject_only(self, temp_memory_dir: str):
        """Tests querying for all facts related to a single subject.
        """
        # Arrange
        memory_service = MemoryService(data_dir=temp_memory_dir)
        memory_service.add_fact_to_sskg("Socrates", "is_a", "philosopher")
        memory_service.add_fact_to_sskg("Socrates", "taught", "Plato")
        memory_service.add_fact_to_sskg("Plato", "wrote", "The Republic")  # This should not be returned

        # Act
        socrates_facts = memory_service.query_sskg("Socrates")

        # Assert
        assert len(socrates_facts) == 2
        predicates = {fact["predicate"] for fact in socrates_facts}
        assert "is_a" in predicates
        assert "taught" in predicates

    def test_query_non_existent_subject(self, temp_memory_dir: str):
        """Tests that querying for a non-existent subject returns an empty list."""
        # Arrange
        memory_service = MemoryService(data_dir=temp_memory_dir)

        # Act
        results = memory_service.query_sskg("Aristotle")

        # Assert
        assert results == []

    def test_sskg_persistence(self, temp_memory_dir: str):
        """Tests that the SSKG is saved on close and reloaded on init."""
        # Arrange: Create first instance, add a fact, and close it to trigger save.
        memory_service_1 = MemoryService(data_dir=temp_memory_dir)
        memory_service_1.add_fact_to_sskg("DAIP-LIVE", "is_a", "project")
        memory_service_1.close()

        # Act: Create a second instance pointing to the same directory.
        memory_service_2 = MemoryService(data_dir=temp_memory_dir)
        results = memory_service_2.query_sskg("DAIP-LIVE")

        # Assert: The fact should be present in the new instance.
        assert len(results) == 1
        assert results[0]["object"] == "project"


class TestMemoryServiceDatabase:
    """Test suite for the database functionality (SQLite) within MemoryService."""

    def test_add_and_retrieve_single_memory(self, temp_memory_dir: str):
        """Tests adding a single memory and retrieving it."""
        # Arrange
        memory_service = MemoryService(data_dir=temp_memory_dir)
        role_id = "test_role_1"
        content = "This is a test memory."

        # Act
        memory_id = memory_service.add_memory(
            role_id=role_id,
            content=content,
            memory_type="dialogue",
            importance=0.8,
        )
        retrieved_memories = memory_service.retrieve_memories(role_id=role_id, limit=1)

        # Assert
        assert len(retrieved_memories) == 1
        memory = retrieved_memories[0]
        assert memory.id == memory_id
        assert memory.role_id == role_id
        assert memory.content == content
        assert memory.memory_type == "dialogue"
        assert memory.importance == 0.8
        memory_service.close()

    def test_retrieve_with_filters(self, temp_memory_dir: str):
        """Tests retrieving memories with various filters."""
        # Arrange
        memory_service = MemoryService(data_dir=temp_memory_dir)
        role_id = "test_role_2"
        memory_service.add_memory(role_id, "Knowledge memory", "knowledge", 0.9, project_id="proj_A")
        memory_service.add_memory(role_id, "Dialogue memory 1", "dialogue", 0.5, project_id="proj_A")
        memory_service.add_memory(role_id, "Dialogue memory 2", "dialogue", 0.7, project_id="proj_B")
        memory_service.add_memory(role_id, "Low importance memory", "experience", 0.2)

        # Act & Assert
        # Filter by memory_type
        dialogue_memories = memory_service.retrieve_memories(role_id, memory_types=["dialogue"])
        assert len(dialogue_memories) == 2
        assert all(m.memory_type == "dialogue" for m in dialogue_memories)

        # Filter by project_id
        proj_a_memories = memory_service.retrieve_memories(role_id, project_id="proj_A")
        assert len(proj_a_memories) == 2
        assert all(m.project_id == "proj_A" for m in proj_a_memories)

        # Filter by min_importance
        high_importance_memories = memory_service.retrieve_memories(role_id, min_importance=0.6)
        assert len(high_importance_memories) == 2
        assert all(m.importance >= 0.6 for m in high_importance_memories)
        memory_service.close()

    def test_retrieve_limit_and_order(self, temp_memory_dir: str):
        """Tests the limit and ordering of retrieved memories."""
        # Arrange
        memory_service = MemoryService(data_dir=temp_memory_dir)
        role_id = "test_role_3"
        memory_service.add_memory(role_id, "Memory A (low importance)", "dialogue", 0.3)
        memory_service.add_memory(role_id, "Memory B (high importance)", "dialogue", 0.9)
        memory_service.add_memory(role_id, "Memory C (medium importance)", "dialogue", 0.6)

        # Act
        retrieved_memories = memory_service.retrieve_memories(role_id, limit=2)

        # Assert
        assert len(retrieved_memories) == 2
        # Should be ordered by importance DESC, then timestamp DESC
        assert retrieved_memories[0].content == "Memory B (high importance)"
        assert retrieved_memories[1].content == "Memory C (medium importance)"
        memory_service.close()

    def test_retrieve_from_non_existent_role(self, temp_memory_dir: str):
        """Ensures retrieving memories for a role with no entries returns an empty list."""
        # Arrange
        memory_service = MemoryService(data_dir=temp_memory_dir)

        # Act
        retrieved_memories = memory_service.retrieve_memories(role_id="non_existent_role")

        # Assert
        assert retrieved_memories == []
        memory_service.close()

    def test_close_service_closes_db_connection(self, temp_memory_dir: str):
        """Tests that the close method correctly closes the database connection."""
        memory_service = MemoryService(data_dir=temp_memory_dir)
        memory_service.close()
        with pytest.raises(sqlite3.ProgrammingError, match="Cannot operate on a closed database."):
            memory_service.conn.execute("SELECT 1")
