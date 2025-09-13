"""This module contains the KnowledgeManager class."""

import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np

from daip_live.core.interfaces import IKnowledgeManager, IModelProvider
from daip_live.core.models import KnowledgeBaseChanges, KnowledgeSource, KnowledgeBaseConfig
from daip_live.persistence.database import DatabaseManager


class KnowledgeManager(IKnowledgeManager):
    """Manages the lifecycle of documents and the vector search index."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        model_provider: IModelProvider,
        config: KnowledgeBaseConfig,
    ):
        self.db_manager = db_manager
        self.model_provider = model_provider
        self.config = config
        self.knowledge_dir = Path(self.config.directory)
        self.index_path = self.knowledge_dir / "index.faiss"

        # Dimension for the embedding model, e.g., all-MiniLM-L6-v2 has 384
        embedding_dim = 384 # TODO: Make this configurable

        if self.index_path.exists():
            self.faiss_index = faiss.read_index(str(self.index_path))
        else:
            self.faiss_index = faiss.IndexFlatL2(embedding_dim)

    @staticmethod
    def _get_file_hash(file_path: Path) -> str:
        """Helper to compute SHA256 hash of a file."""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def _scan_and_detect_changes(self) -> KnowledgeBaseChanges:
        """Compares files on disk with records in the DB to find changes."""
        db_sources = {s.file_path: s for s in self.db_manager.get_all_knowledge_sources()}
        
        # Only process text files, skip binary files like .faiss, .pkl, etc.
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.csv', '.log'}
        disk_files = {
            str(p) for p in self.knowledge_dir.rglob("*") 
            if p.is_file() and (
                p.suffix.lower() in text_extensions or
                not p.suffix  # Include files without extensions
            )
        }

        changes = KnowledgeBaseChanges()

        for file_path_str in disk_files:
            file_path = Path(file_path_str)
            db_record = db_sources.get(file_path_str)

            if not db_record:
                changes.added.append(file_path_str)
            else:
                current_hash = self._get_file_hash(file_path)
                if current_hash != db_record.file_hash:
                    changes.updated.append((file_path_str, db_record))
                else:
                    changes.unchanged.append(db_record)

        db_files = set(db_sources.keys())
        deleted_files = db_files - disk_files
        for file_path_str in deleted_files:
            changes.deleted.append(db_sources[file_path_str])

        return changes

    async def sync_knowledge_base(self) -> Dict[str, int]:
        """Scans the knowledge directory, processes changes, and updates the index."""
        changes = self._scan_and_detect_changes()
        summary = {
            "added": 0, "updated": 0, "removed": 0, "unchanged": len(changes.unchanged)
        }

        # Process added files
        for file_path_str in changes.added:
            file_path = Path(file_path_str)
            try:
                content = await asyncio.to_thread(file_path.read_text, encoding="utf-8")
                file_hash = await asyncio.to_thread(self._get_file_hash, file_path)
                embedding = await self.model_provider.embed(content)
            except (UnicodeDecodeError, IOError) as e:
                self._logger.warning(f"Skipping file {file_path_str} due to read error: {e}")
                summary["added"] -= 1  # Don't count this as added
                continue

            source = KnowledgeSource(file_path=file_path_str, file_hash=file_hash, status="indexed")
            new_source = await asyncio.to_thread(self.db_manager.upsert_knowledge_source, source)
            new_id = new_source.id

            if self.faiss_index and new_id is not None:
                # FAISS requires a 2D array for additions
                self.faiss_index.add_with_ids(np.array([embedding], dtype=np.float32), np.array([new_id], dtype=np.int64))

            summary["added"] += 1

        # Process deleted files
        for source in changes.deleted:
            if self.faiss_index and source.id is not None:
                self.faiss_index.remove_ids(np.array([source.id], dtype=np.int64))
            await asyncio.to_thread(self.db_manager.delete_knowledge_source, file_path=source.file_path)
            summary["removed"] += 1

        # Process updated files
        for file_path_str, old_source in changes.updated:
            # Essentially a delete then an add
            if self.faiss_index and old_source.id is not None:
                self.faiss_index.remove_ids(np.array([old_source.id], dtype=np.int64))

            file_path = Path(file_path_str)
            try:
                content = await asyncio.to_thread(file_path.read_text, encoding="utf-8")
                file_hash = await asyncio.to_thread(self._get_file_hash, file_path)
                embedding = await self.model_provider.embed(content)
            except (UnicodeDecodeError, IOError) as e:
                self._logger.warning(f"Skipping file {file_path_str} due to read error: {e}")
                summary["updated"] -= 1  # Don't count this as updated
                continue

            source = KnowledgeSource(file_path=file_path_str, file_hash=file_hash, status="indexed", id=old_source.id)
            updated_source = await asyncio.to_thread(self.db_manager.upsert_knowledge_source, source)
            updated_id = updated_source.id

            if self.faiss_index and updated_id is not None:
                self.faiss_index.add_with_ids(np.array([embedding], dtype=np.float32), np.array([updated_id], dtype=np.int64))

            summary["updated"] += 1

        # Persist the index to disk
        if self.faiss_index:
            faiss.write_index(self.faiss_index, str(self.index_path))

        return summary

    async def search(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Searches for the most relevant documents for a given query text.
        """
        if not self.faiss_index or self.faiss_index.ntotal == 0:
            return []

        # 1. Get the embedding for the query text.
        query_embedding = await self.model_provider.embed(query_text)
        query_vector = np.array([query_embedding], dtype=np.float32)

        # 2. Search the FAISS index.
        # D: distances, I: indices (our database IDs)
        distances, ids = self.faiss_index.search(query_vector, top_k)

        # 3. Retrieve the corresponding sources from the database.
        if ids.size == 0:
            return []

        # The returned ids is a 2D array, e.g., [[1, 5, 3]]. Flatten it.
        # FAISS returns -1 for empty slots, so we filter them out.
        source_ids = [int(i) for i in ids[0] if i != -1]
        if not source_ids:
            return []

        # This method needs to be implemented in the DatabaseManager
        sources = await asyncio.to_thread(self.db_manager.get_knowledge_sources_by_ids, source_ids)

        # 4. Format the results.
        # Create a mapping from id to source for easy lookup
        source_map = {s.id: s for s in sources}

        results = []
        for i, source_id in enumerate(source_ids):
            source = source_map.get(source_id)
            if source:
                results.append({
                    "file_path": source.file_path,
                    "distance": float(distances[0][i]),
                    "status": source.status,
                    "indexed_at": source.indexed_at
                })

        return results
