import hashlib
from pathlib import Path

import numpy as np
import pytest

from daip_live.core.models import (
    KnowledgeBaseChanges,
    KnowledgeBaseConfig,
    KnowledgeSource,
)
from daip_live.knowledge.manager import KnowledgeManager


def _get_file_hash(file_path: Path) -> str:
    """Helper to compute SHA256 hash of a file."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


class TestKnowledgeManager:
    def test_initialization(self, mocker):
        """Tests that the KnowledgeManager can be initialized successfully."""
        mock_db_manager = mocker.Mock()
        mock_model_provider = mocker.Mock()
        config = KnowledgeBaseConfig(directory="/fake/knowledge")
        manager = KnowledgeManager(db_manager=mock_db_manager, model_provider=mock_model_provider, config=config)
        assert manager.db_manager == mock_db_manager
        assert manager.model_provider == mock_model_provider
        assert manager.config == config

    def test_scan_and_detect_changes(self, mocker, tmp_path: Path):
        """Tests the core logic of detecting file changes using the data contract."""
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "added.txt").write_text("new file")
        (knowledge_dir / "updated.txt").write_text("new content")
        (knowledge_dir / "unchanged.txt").write_text("same content")
        unchanged_source = KnowledgeSource(file_path=str(knowledge_dir / "unchanged.txt"), file_hash=_get_file_hash(knowledge_dir / "unchanged.txt"), status="indexed")
        updated_source_from_db = KnowledgeSource(file_path=str(knowledge_dir / "updated.txt"), file_hash="old_hash_value", status="indexed")
        deleted_source = KnowledgeSource(file_path=str(knowledge_dir / "deleted.txt"), file_hash="some_hash", status="indexed")
        mock_db_manager = mocker.Mock()
        mock_db_manager.get_all_knowledge_sources.return_value = [unchanged_source, updated_source_from_db, deleted_source]
        manager = KnowledgeManager(db_manager=mock_db_manager, model_provider=mocker.Mock(), config=KnowledgeBaseConfig(directory=str(knowledge_dir)))
        changes = manager._scan_and_detect_changes()
        assert isinstance(changes, KnowledgeBaseChanges)
        assert len(changes.added) == 1
        assert len(changes.updated) == 1
        assert len(changes.deleted) == 1
        assert len(changes.unchanged) == 1

    @pytest.mark.asyncio
    async def test_sync_knowledge_base_handles_added_files(self, mocker, tmp_path: Path):
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir()
        added_file = knowledge_dir / "new_doc.txt"
        added_file.write_text("This is a new document.")
        mock_db_manager = mocker.Mock()
        mock_db_manager.upsert_knowledge_source.side_effect = lambda s: s
        mock_model_provider = mocker.AsyncMock()
        mock_model_provider.embed.return_value = [0.1, 0.2, 0.3]
        mocker.patch("daip_live.knowledge.manager.faiss.write_index")
        manager = KnowledgeManager(db_manager=mock_db_manager, model_provider=mock_model_provider, config=KnowledgeBaseConfig(directory=str(knowledge_dir)))
        mock_changes = KnowledgeBaseChanges(added=[str(added_file)])
        mocker.patch.object(manager, '_scan_and_detect_changes', return_value=mock_changes)
        manager.faiss_index = mocker.Mock()
        manager.faiss_index.add = mocker.Mock()
        result = await manager.sync_knowledge_base()
        mock_db_manager.upsert_knowledge_source.assert_called_once()
        assert result == {"added": 1, "updated": 0, "removed": 0, "unchanged": 0}

    @pytest.mark.asyncio
    async def test_sync_knowledge_base_handles_deleted_files(self, mocker, tmp_path: Path):
        deleted_source = KnowledgeSource(id=42, file_path="/path/to/deleted.txt", file_hash="abc", status="indexed")
        mock_db_manager = mocker.Mock()
        mocker.patch("daip_live.knowledge.manager.faiss.write_index")
        manager = KnowledgeManager(db_manager=mock_db_manager, model_provider=mocker.AsyncMock(), config=KnowledgeBaseConfig(directory=str(tmp_path)))
        mock_changes = KnowledgeBaseChanges(deleted=[deleted_source])
        mocker.patch.object(manager, '_scan_and_detect_changes', return_value=mock_changes)
        manager.faiss_index = mocker.Mock()
        manager.faiss_index.remove_ids = mocker.Mock()
        result = await manager.sync_knowledge_base()
        mock_db_manager.delete_knowledge_source.assert_called_once_with(file_path="/path/to/deleted.txt")
        manager.faiss_index.remove_ids.assert_called_once()
        called_with = manager.faiss_index.remove_ids.call_args[0][0]
        assert np.array_equal(called_with, np.array([42]))
        assert result == {"added": 0, "updated": 0, "removed": 1, "unchanged": 0}

    @pytest.mark.asyncio
    async def test_sync_knowledge_base_handles_updated_files(self, mocker, tmp_path: Path):
        """Tests that sync_knowledge_base correctly processes an updated file."""
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir()
        updated_file = knowledge_dir / "updated_doc.txt"
        updated_file.write_text("new version of the document")

        old_source = KnowledgeSource(id=101, file_path=str(updated_file), file_hash="old_hash", status="indexed")

        mock_db_manager = mocker.Mock()
        mock_db_manager.upsert_knowledge_source.side_effect = lambda s: s
        mock_model_provider = mocker.AsyncMock()
        mock_model_provider.embed.return_value = [0.4, 0.5, 0.6]
        mocker.patch("daip_live.knowledge.manager.faiss.write_index")

        manager = KnowledgeManager(db_manager=mock_db_manager, model_provider=mock_model_provider, config=KnowledgeBaseConfig(directory=str(knowledge_dir)))

        mock_changes = KnowledgeBaseChanges(updated=[(str(updated_file), old_source)])
        mocker.patch.object(manager, '_scan_and_detect_changes', return_value=mock_changes)

        manager.faiss_index = mocker.Mock()
        manager.faiss_index.remove_ids = mocker.Mock()
        manager.faiss_index.add_with_ids = mocker.Mock()

        result = await manager.sync_knowledge_base()

        manager.faiss_index.remove_ids.assert_called_once()
        assert np.array_equal(manager.faiss_index.remove_ids.call_args[0][0], np.array([101]))
        mock_model_provider.embed.assert_called_once_with("new version of the document")
        manager.faiss_index.add_with_ids.assert_called_once()
        mock_db_manager.upsert_knowledge_source.assert_called_once()
        upserted_call_args = mock_db_manager.upsert_knowledge_source.call_args[0][0]
        assert upserted_call_args.file_hash != "old_hash"

        assert result == {"added": 0, "updated": 1, "removed": 0, "unchanged": 0}

    @pytest.mark.asyncio
    async def test_search_e2e(self, mocker, tmp_path: Path):
        """Tests the search method from query embedding to final result formatting."""
        # 1. Setup
        mock_db_manager = mocker.Mock()
        mock_model_provider = mocker.AsyncMock()
        manager = KnowledgeManager(db_manager=mock_db_manager, model_provider=mock_model_provider, config=KnowledgeBaseConfig(directory=str(tmp_path)))

        # 2. Mock dependencies
        # Mock the model provider's embed method
        mock_model_provider.embed.return_value = [0.1, 0.2, 0.3] # A dummy vector

        # Mock the FAISS index and its search method
        mock_faiss_index = mocker.Mock()
        # FAISS returns distances and IDs as 2D numpy arrays
        mock_distances = np.array([[0.1, 0.2]], dtype=np.float32)
        mock_ids = np.array([[101, 102]], dtype=np.int64)
        mock_faiss_index.search.return_value = (mock_distances, mock_ids)
        mock_faiss_index.ntotal = 2 # Pretend the index has items
        manager.faiss_index = mock_faiss_index

        # Mock the database manager's response
        mock_sources = [
            KnowledgeSource(id=101, file_path="/path/one.txt", file_hash="abc", status="indexed"),
            KnowledgeSource(id=102, file_path="/path/two.txt", file_hash="def", status="indexed"),
        ]
        mock_db_manager.get_knowledge_sources_by_ids.return_value = mock_sources

        # 3. Execute
        query = "test query"
        top_k = 2
        results = await manager.search(query, top_k=top_k)

        # 4. Assert
        # Ensure the mocks were called correctly
        mock_model_provider.embed.assert_called_once_with(query)
        mock_faiss_index.search.assert_called_once()
        # Check the query vector and k passed to faiss
        call_args = mock_faiss_index.search.call_args[0]
        assert np.array_equal(call_args[0], np.array([[0.1, 0.2, 0.3]], dtype=np.float32))
        assert call_args[1] == top_k
        mock_db_manager.get_knowledge_sources_by_ids.assert_called_once_with([101, 102])

        # Assert the final formatted result
        assert len(results) == 2
        assert results[0]["file_path"] == "/path/one.txt"
        assert results[0]["distance"] == pytest.approx(0.1)
        assert results[1]["file_path"] == "/path/two.txt"
        assert results[1]["distance"] == pytest.approx(0.2)
