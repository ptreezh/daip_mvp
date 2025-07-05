import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import List
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call
import yaml

from src.core_services.wiki_service import (
    EditStatus,
    WikiEntryMetadata,
    WikiProposal,
    WikiService,
    WikiVersion,
)


class TestWikiService(TestCase):
    def setUp(self):
        # Create a temporary directory for file-based operations (wiki entries)
        self.test_dir = tempfile.mkdtemp()

        # Mock external dependencies (ChromaDB and Ollama)
        self.mock_chroma_client = MagicMock()
        self.mock_chroma_collection = MagicMock()
        self.mock_chroma_client.get_or_create_collection.return_value = self.mock_chroma_collection

        # Patch the classes/functions in the module where they are USED
        self.chroma_patcher = patch('src.core_services.wiki_service.chromadb.PersistentClient', return_value=self.mock_chroma_client)
        self.ollama_patcher = patch('src.core_services.wiki_service.ollama.embeddings')

        self.mock_chroma_patcher = self.chroma_patcher.start()
        self.mock_ollama_embeddings = self.ollama_patcher.start()

        # Configure a default return value for the embedding mock to be used across tests
        self.mock_ollama_embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

        self.wiki_service = WikiService(wiki_directory=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        # Stop the patchers to clean up
        self.chroma_patcher.stop()
        self.ollama_patcher.stop()

    def _create_test_entry(
        self,
        entry_name: str = "test_entry",
        content: str = "This is a test entry.",
        author_role: str = "test_author",
        tags: List[str] = ["test"],
        category: str = "test",
    ) -> WikiVersion:
        return self.wiki_service.create_entry(
            entry_name, content, author_role, tags, category
        )

    def test_create_entry(self):
        entry_name = "new_entry"
        content = "Content of the new entry."
        author = "creator"
        tags = ["new", "test"]
        category = "testing"

        wiki_version = self.wiki_service.create_entry(entry_name, content, author, tags, category)
        self.assertIsNotNone(wiki_version)

        # Verify directory and files
        entry_path = Path(self.test_dir) / entry_name
        self.assertTrue(entry_path.exists())
        self.assertTrue((entry_path / "versions").exists())
        self.assertTrue((entry_path / "proposals").exists())
        self.assertTrue((entry_path / "entry.json").exists())

        # Verify metadata
        with open(entry_path / "entry.json", "r") as f:
            metadata = WikiEntryMetadata(**json.load(f))
            self.assertEqual(metadata.entry_name, entry_name)
            self.assertEqual(metadata.creator, author)
            self.assertEqual(metadata.tags, tags)
            self.assertEqual(metadata.category, category)
            self.assertEqual(metadata.versions, ["1.0.0"])

        # Verify version content
        version_file = entry_path / "versions" / "1.0.0.md"
        self.assertTrue(version_file.exists())
        with open(version_file, "r") as f:
            file_content = f.read()
            parts = file_content.split("---", 2)
            front_matter = yaml.safe_load(parts[1])
            self.assertEqual(front_matter["version"], "1.0.0")
            self.assertEqual(front_matter["author"], author)
            self.assertEqual(parts[2].strip(), content)

        self.assertEqual(wiki_version.content, content)

        # Verify that the vector index was updated
        self.mock_ollama_embeddings.assert_called_once_with(model="nomic-embed-text", prompt=content)
        self.mock_chroma_collection.upsert.assert_called_once_with(
            ids=[entry_name],
            embeddings=[[0.1, 0.2, 0.3]],
            documents=[content]
        )

    def test_get_entry(self):
        # Setup: Create an entry first
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name

        # Test retrieval
        retrieved_entry = self.wiki_service.get_entry(entry_name)
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry.entry_name, entry_name)
        self.assertEqual(retrieved_entry.version, "1.0.0")
        self.assertEqual(retrieved_entry.content, "This is a test entry.")

    def test_propose_edit(self):
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        new_content = "This is the edited content."
        author = "editor"
        change_summary = "Updated the content."

        # Propose edit
        proposal_id = self.wiki_service.propose_edit(
            entry_name, new_content, author, change_summary
        )
        self.assertIsNotNone(proposal_id)

        # Verify proposal file
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        self.assertTrue(proposal_file.exists())

        with open(proposal_file, "r") as f:
            proposal_data = json.load(f)
            # Convert status string from JSON back to Enum before instantiation
            proposal_data["status"] = EditStatus(proposal_data["status"])
            proposal = WikiProposal(**proposal_data)
            self.assertEqual(proposal.entry_name, entry_name)
            self.assertEqual(proposal.new_content, new_content)
            self.assertEqual(proposal.author, author)
            self.assertEqual(proposal.change_summary, change_summary)
            self.assertEqual(proposal.status, EditStatus.PROPOSED)

    def test_apply_proposal(self):
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        new_content = "New content after edit."
        proposal_id = self.wiki_service.propose_edit(
            entry_name, new_content, "editor", "Change summary"
        )

        # Apply proposal
        success = self.wiki_service._apply_proposal(entry_name, proposal_id)
        self.assertTrue(success)

        # Verify new version
        metadata = self.wiki_service._read_entry_metadata(entry_name)
        self.assertIn("1.0.1", metadata.versions)

        new_version = self.wiki_service.get_entry(entry_name, version="1.0.1")
        self.assertEqual(new_version.content, "New content after edit.")

        # Verify proposal status
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        with open(proposal_file, "r") as f:
            proposal_data = json.load(f)
            self.assertEqual(proposal_data["status"], EditStatus.APPLIED.value)

        # Verify that the vector index was updated twice: once on creation, once on apply
        self.assertEqual(self.mock_chroma_collection.upsert.call_count, 2)
        # Check the last call was with the new content
        last_upsert_call = self.mock_chroma_collection.upsert.call_args
        self.assertEqual(last_upsert_call.kwargs['ids'], [entry_name])
        self.assertEqual(last_upsert_call.kwargs['documents'], [new_content])

    def test_get_entry_latest_version(self):
        # Setup: Create an entry and apply a proposal to create a new version
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        self.wiki_service.propose_edit(
            entry_name, "Updated content", "editor", "Updating"
        )
        self.wiki_service._apply_proposal(
            entry_name,
            next(iter(os.listdir(Path(self.test_dir) / entry_name / "proposals")))[:-5],
        )  # Apply the first proposal we find

        # Retrieve the latest version
        latest_entry = self.wiki_service.get_entry(entry_name)
        self.assertEqual(latest_entry.version, "1.0.1")
        self.assertEqual(latest_entry.content, "Updated content")

    def test_get_nonexistent_entry(self):
        entry = self.wiki_service.get_entry("nonexistent_entry")
        self.assertIsNone(entry)

    def test_create_entry_already_exists(self):
        entry_name = "duplicate_entry"
        self._create_test_entry(entry_name=entry_name)
        # Try to create it again
        result = self.wiki_service.create_entry(
            entry_name, "some content", "author", [], "cat"
        )
        self.assertIsNone(result)

    def test_get_entry_specific_version(self):
        entry_name = "multi_version_entry"
        self._create_test_entry(entry_name=entry_name, content="Version 1.0.0")
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "Version 1.0.1", "editor", "Update to 1.0.1"
        )
        self.wiki_service._apply_proposal(entry_name, proposal_id)

        # Get latest (should be 1.0.1)
        latest_version = self.wiki_service.get_entry(entry_name)
        self.assertEqual(latest_version.version, "1.0.1")
        self.assertEqual(latest_version.content, "Version 1.0.1")

        # Get specific old version (1.0.0)
        old_version = self.wiki_service.get_entry(entry_name, version="1.0.0")
        self.assertIsNotNone(old_version)
        self.assertEqual(old_version.version, "1.0.0")
        self.assertEqual(old_version.content, "Version 1.0.0")

    def test_get_entry_version_not_found(self):
        created_entry = self._create_test_entry()
        entry = self.wiki_service.get_entry(created_entry.entry_name, version="9.9.9")
        self.assertIsNone(entry)

    def test_apply_nonexistent_proposal(self):
        created_entry = self._create_test_entry()
        success = self.wiki_service._apply_proposal(
            created_entry.entry_name, "nonexistent-proposal-id"
        )
        self.assertFalse(success)

    def test_propose_edit_for_nonexistent_entry(self):
        proposal_id = self.wiki_service.propose_edit(
            "nonexistent-entry", "some content", "editor", "summary"
        )
        self.assertIsNone(proposal_id)

    def test_get_entry_with_malformed_metadata(self):
        entry_name = "malformed_meta"
        self._create_test_entry(entry_name=entry_name)
        # Corrupt the metadata file
        metadata_file = Path(self.test_dir) / entry_name / "entry.json"
        metadata_file.write_text("{'invalid_json':", encoding="utf-8")
        entry = self.wiki_service.get_entry(entry_name)
        self.assertIsNone(entry)  # Should fail gracefully

    def test_get_entry_with_malformed_version_file(self):
        entry_name = "malformed_version"
        self._create_test_entry(entry_name=entry_name)
        # Corrupt the version file (remove frontmatter)
        version_file = Path(self.test_dir) / entry_name / "versions" / "1.0.0.md"
        version_file.write_text("Just content, no frontmatter.", encoding="utf-8")
        entry = self.wiki_service.get_entry(entry_name)
        self.assertIsNone(entry)  # Should fail gracefully

    def test_search(self):
        """Tests the semantic search functionality."""
        # Arrange
        query = "find relevant stuff"
        mock_query_result = {
            'ids': [['entry1', 'entry2']],
            'documents': [['content of entry 1', 'content of entry 2']],
            # other keys like distances, metadatas can be omitted for this test
        }
        self.mock_chroma_collection.query.return_value = mock_query_result

        # Act
        results = self.wiki_service.search(query, top_k=2)

        # Assert
        self.mock_ollama_embeddings.assert_called_with(model="nomic-embed-text", prompt=query) # Check if query was embedded
        self.mock_chroma_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]],
            n_results=2
        )
        self.assertEqual(len(results), 2)
        self.assertIn("[entry1]: content of entry 1...", results[0]) # Check snippet formatting
        self.assertIn("[entry2]: content of entry 2...", results[1])

    def test_search_no_results(self):
        """Tests that search returns an empty list when no matches are found."""
        self.mock_chroma_collection.query.return_value = {} # Simulate no results from Chroma
        results = self.wiki_service.search("nonexistent_term")
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    main()