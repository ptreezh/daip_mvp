import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

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
        tags: list[str] = ["test"],
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
        with open(entry_path / "entry.json") as f:
            metadata = WikiEntryMetadata(**json.load(f))
            self.assertEqual(metadata.entry_name, entry_name)
            self.assertEqual(metadata.creator, author)
            self.assertEqual(metadata.tags, tags)
            self.assertEqual(metadata.category, category)
            self.assertEqual(metadata.versions, ["1.0.0"])

        # Verify version content
        version_file = entry_path / "versions" / "1.0.0.md"
        self.assertTrue(version_file.exists())
        with open(version_file) as f:
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

        with open(proposal_file) as f:
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
        with open(proposal_file) as f:
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
        # When entry already exists, a new version should be created
        self.assertIsNotNone(result)
        self.assertEqual(result.entry_name, entry_name)
        self.assertEqual(result.content, "some content")
        self.assertEqual(result.author, "author")
        # Verify that a new version was created
        metadata = self.wiki_service._read_entry_metadata(entry_name)
        self.assertIn("1.0.1", metadata.versions)

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

    def test_list_all_entries(self):
        """Test listing all wiki entries."""
        # Create test entries
        self._create_test_entry(entry_name="entry1")
        self._create_test_entry(entry_name="entry2")
        self._create_test_entry(entry_name="entry3")
        
        # List all entries
        entries = self.wiki_service.list_all_entries()
        
        # Should return all entries in sorted order
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries, ["entry1", "entry2", "entry3"])

    def test_list_all_entries_empty(self):
        """Test listing entries when no entries exist."""
        entries = self.wiki_service.list_all_entries()
        self.assertEqual(len(entries), 0)

    def test_get_entry_statistics(self):
        """Test getting statistics about a wiki entry."""
        # Create a test entry
        entry_name = "stats_test"
        self._create_test_entry(entry_name=entry_name)
        
        # Get statistics
        stats = self.wiki_service.get_entry_statistics(entry_name)
        
        # Verify statistics structure
        self.assertEqual(stats["entry_name"], entry_name)
        self.assertEqual(stats["total_versions"], 1)
        self.assertEqual(stats["creator"], "test_author")
        self.assertEqual(stats["tags"], ["test"])
        self.assertEqual(stats["category"], "test")
        self.assertIn("created_at", stats)
        self.assertIn("last_modified", stats)

    def test_get_entry_statistics_nonexistent(self):
        """Test getting statistics for nonexistent entry."""
        stats = self.wiki_service.get_entry_statistics("nonexistent")
        self.assertEqual(stats, {})

    def test_export_entry_json(self):
        """Test exporting a wiki entry as JSON."""
        # Create a test entry
        entry_name = "export_test"
        self._create_test_entry(entry_name=entry_name)
        
        # Export as JSON
        export_path = Path(self.test_dir) / "export.json"
        result = self.wiki_service.export_entry(entry_name, str(export_path), "json")
        
        # Verify export succeeded
        self.assertTrue(result)
        self.assertTrue(export_path.exists())
        
        # Verify export content
        with open(export_path) as f:
            export_data = json.load(f)
        
        self.assertIn("metadata", export_data)
        self.assertIn("versions", export_data)
        self.assertEqual(export_data["metadata"]["entry_name"], entry_name)

    def test_export_entry_markdown(self):
        """Test exporting a wiki entry as Markdown."""
        # Create a test entry
        entry_name = "export_md_test"
        self._create_test_entry(entry_name=entry_name, content="Test content for markdown export")
        
        # Export as Markdown
        export_path = Path(self.test_dir) / "export.md"
        result = self.wiki_service.export_entry(entry_name, str(export_path), "markdown")
        
        # Verify export succeeded
        self.assertTrue(result)
        self.assertTrue(export_path.exists())
        
        # Verify export content
        content = export_path.read_text()
        self.assertIn(f"# {entry_name}", content)
        self.assertIn("Test content for markdown export", content)

    def test_export_entry_invalid_format(self):
        """Test exporting with invalid format."""
        entry_name = "export_invalid"
        self._create_test_entry(entry_name=entry_name)
        
        export_path = Path(self.test_dir) / "export.txt"
        result = self.wiki_service.export_entry(entry_name, str(export_path), "invalid")
        
        # Should fail with invalid format
        self.assertFalse(result)

    def test_import_entry_from_json(self):
        """Test importing a wiki entry from JSON."""
        # First create and export an entry
        entry_name = "import_source"
        self._create_test_entry(entry_name=entry_name)
        
        export_path = Path(self.test_dir) / "import_data.json"
        self.wiki_service.export_entry(entry_name, str(export_path), "json")
        
        # Modify the JSON to have a different entry name
        with open(export_path, 'r') as f:
            import_data = json.load(f)
        import_data["metadata"]["entry_name"] = "imported_entry"
        with open(export_path, 'w') as f:
            json.dump(import_data, f)
        
        # Import with the new name from modified JSON
        result = self.wiki_service.import_entry_from_json(str(export_path), overwrite=False)
        
        # Verify import succeeded
        self.assertTrue(result)
        
        # Verify imported entry exists
        imported_entry = self.wiki_service.get_entry("imported_entry")
        self.assertIsNotNone(imported_entry)
        self.assertEqual(imported_entry.content, "This is a test entry.")

    def test_import_entry_overwrite(self):
        """Test importing with overwrite enabled."""
        # Create source and target entries
        source_name = "source_entry"
        target_name = "target_entry"
        self._create_test_entry(entry_name=source_name, content="Source content")
        self._create_test_entry(entry_name=target_name, content="Target content")
        
        # Export source
        export_path = Path(self.test_dir) / "import_data.json"
        self.wiki_service.export_entry(source_name, str(export_path), "json")
        
        # Import and overwrite target (modify the JSON to have target_name as entry_name)
        with open(export_path, 'r') as f:
            import_data = json.load(f)
        import_data["metadata"]["entry_name"] = target_name
        with open(export_path, 'w') as f:
            json.dump(import_data, f)
        
        result = self.wiki_service.import_entry_from_json(str(export_path), overwrite=True)
        
        # Verify import succeeded and target was overwritten
        self.assertTrue(result)
        imported_entry = self.wiki_service.get_entry(target_name)
        self.assertEqual(imported_entry.content, "Source content")

    def test_import_entry_conflict_no_overwrite(self):
        """Test importing when entry exists and overwrite is disabled."""
        # Create source and target entries
        source_name = "source_entry"
        target_name = "target_entry"
        self._create_test_entry(entry_name=source_name)
        self._create_test_entry(entry_name=target_name)
        
        # Export source
        export_path = Path(self.test_dir) / "import_data.json"
        self.wiki_service.export_entry(source_name, str(export_path), "json")
        
        # Try to import without overwrite
        result = self.wiki_service.import_entry_from_json(str(export_path), overwrite=False)
        
        # Should fail due to conflict
        self.assertFalse(result)

    def test_delete_entry(self):
        """Test deleting a wiki entry."""
        # Create a test entry
        entry_name = "delete_test"
        self._create_test_entry(entry_name=entry_name)
        
        # Delete the entry
        result = self.wiki_service.delete_entry(entry_name, backup=False)
        
        # Verify deletion succeeded
        self.assertTrue(result)
        
        # Verify entry no longer exists
        entry_path = Path(self.test_dir) / entry_name
        self.assertFalse(entry_path.exists())

    def test_delete_entry_with_backup(self):
        """Test deleting a wiki entry with backup."""
        # Create a test entry
        entry_name = "delete_backup_test"
        self._create_test_entry(entry_name=entry_name)
        
        # Delete the entry with backup
        result = self.wiki_service.delete_entry(entry_name, backup=True)
        
        # Verify deletion succeeded
        self.assertTrue(result)
        
        # Verify backup was created
        backup_dir = Path(self.test_dir) / "backups"
        self.assertTrue(backup_dir.exists())
        backup_files = list(backup_dir.glob(f"{entry_name}_*"))
        self.assertEqual(len(backup_files), 1)

    def test_delete_nonexistent_entry(self):
        """Test deleting a nonexistent entry."""
        result = self.wiki_service.delete_entry("nonexistent", backup=False)
        self.assertFalse(result)

    def test_compare_versions(self):
        """Test comparing two versions of an entry."""
        # Create an entry
        entry_name = "compare_test"
        self._create_test_entry(entry_name=entry_name, content="Original content")
        
        # Edit the entry to create a new version
        self.wiki_service.propose_edit(
            entry_name=entry_name,
            new_content="Modified content with additional text",
            author_role="editor",
            change_summary="Test edit"
        )
        
        # Apply the proposal to create version 1.0.1
        proposals = self.wiki_service._get_entry_proposals(entry_name)
        if proposals:
            self.wiki_service._apply_proposal(entry_name, proposals[0].proposal_id)
        
        # Compare versions
        comparison = self.wiki_service.compare_versions(entry_name, "1.0.0", "1.0.1")
        
        # Verify comparison structure
        self.assertIn("version1", comparison)
        self.assertIn("version2", comparison)
        self.assertIn("changes", comparison)
        self.assertEqual(comparison["entry_name"], entry_name)

    def test_compare_versions_nonexistent(self):
        """Test comparing versions of nonexistent entry."""
        comparison = self.wiki_service.compare_versions("nonexistent", "1.0.0", "1.0.1")
        self.assertIn("error", comparison)

    def test_compare_versions_invalid_version(self):
        """Test comparing with invalid version."""
        entry_name = "compare_invalid"
        self._create_test_entry(entry_name=entry_name)
        
        comparison = self.wiki_service.compare_versions(entry_name, "1.0.0", "invalid_version")
        self.assertIn("error", comparison)

    def test_approve_proposal(self):
        """Test approving a valid proposal."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        new_content = "Approved content."
        proposal_id = self.wiki_service.propose_edit(
            entry_name, new_content, "editor", "Approval test"
        )
        self.assertIsNotNone(proposal_id)

        # Approve the proposal
        success = self.wiki_service.approve(entry_name, proposal_id)
        self.assertTrue(success)

        # Verify new version was created
        metadata = self.wiki_service._read_entry_metadata(entry_name)
        self.assertIn("1.0.1", metadata.versions)

        new_version = self.wiki_service.get_entry(entry_name, version="1.0.1")
        self.assertEqual(new_version.content, new_content)

        # Verify proposal status is updated
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        with open(proposal_file) as f:
            proposal_data = json.load(f)
            self.assertEqual(proposal_data["status"], EditStatus.APPLIED.value)

    def test_approve_nonexistent_proposal(self):
        """Test approving a nonexistent proposal."""
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        
        success = self.wiki_service.approve(entry_name, "nonexistent-proposal-id")
        self.assertFalse(success)

    def test_approve_proposal_for_nonexistent_entry(self):
        """Test approving a proposal for a nonexistent entry."""
        success = self.wiki_service.approve("nonexistent-entry", "some-proposal-id")
        self.assertFalse(success)

    def test_approve_already_applied_proposal(self):
        """Test approving an already applied proposal."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Apply the proposal first
        success_first = self.wiki_service.approve(entry_name, proposal_id)
        self.assertTrue(success_first)

        # Try to approve it again
        success_second = self.wiki_service.approve(entry_name, proposal_id)
        # Should succeed (idempotent operation)
        self.assertTrue(success_second)

    def test_approve_rejected_proposal(self):
        """Test approving a rejected proposal."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Manually reject the proposal by modifying its file
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        with open(proposal_file) as f:
            proposal_data = json.load(f)
        proposal_data["status"] = EditStatus.REJECTED.value
        with open(proposal_file, 'w') as f:
            json.dump(proposal_data, f, indent=4)

        # Try to approve the rejected proposal
        success = self.wiki_service.approve(entry_name, proposal_id)
        self.assertFalse(success)

    def test_approve_with_invalid_status(self):
        """Test approving a proposal with an invalid status."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Manually set an invalid status in the proposal file
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        with open(proposal_file) as f:
            proposal_data = json.load(f)
        proposal_data["status"] = "invalid_status"
        with open(proposal_file, 'w') as f:
            json.dump(proposal_data, f, indent=4)

        # Try to approve the proposal with invalid status
        success = self.wiki_service.approve(entry_name, proposal_id)
        self.assertFalse(success)

    def test_approve_with_malformed_proposal_file(self):
        """Test approving a proposal with a malformed JSON file."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Corrupt the proposal file
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        proposal_file.write_text("{ invalid json", encoding="utf-8")

        # Try to approve the malformed proposal
        success = self.wiki_service.approve(entry_name, proposal_id)
        self.assertFalse(success)

    def test_list_pending_proposals(self):
        """Test listing pending proposals."""
        # Setup: Create two entries with proposals
        entry1_name = "entry1"
        entry2_name = "entry2"
        self._create_test_entry(entry_name=entry1_name)
        self._create_test_entry(entry_name=entry2_name)
        
        # Create proposals for both entries
        proposal1_id = self.wiki_service.propose_edit(
            entry1_name, "Content for entry1", "author1", "Summary1"
        )
        proposal2_id = self.wiki_service.propose_edit(
            entry2_name, "Content for entry2", "author2", "Summary2"
        )
        
        # Approve one proposal to change its status
        self.wiki_service.approve(entry1_name, proposal1_id)
        
        # List pending proposals
        pending_proposals = self.wiki_service.list_pending_proposals()
        
        # Should only have one pending proposal (from entry2)
        self.assertEqual(len(pending_proposals), 1)
        self.assertEqual(pending_proposals[0]["entry_name"], entry2_name)
        self.assertEqual(pending_proposals[0]["proposal_id"], proposal2_id)
        self.assertEqual(pending_proposals[0]["author"], "author2")
        self.assertEqual(pending_proposals[0]["change_summary"], "Summary2")

    def test_list_pending_proposals_empty(self):
        """Test listing pending proposals when there are none."""
        # Create an entry but no proposals
        self._create_test_entry()
        
        # List pending proposals
        pending_proposals = self.wiki_service.list_pending_proposals()
        
        # Should be empty
        self.assertEqual(len(pending_proposals), 0)

    def test_list_pending_proposals_with_no_entries(self):
        """Test listing pending proposals when there are no entries."""
        # List pending proposals
        pending_proposals = self.wiki_service.list_pending_proposals()
        
        # Should be empty
        self.assertEqual(len(pending_proposals), 0)

    def test_reject_proposal(self):
        """Test rejecting a valid proposal."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        new_content = "Rejected content."
        proposal_id = self.wiki_service.propose_edit(
            entry_name, new_content, "editor", "Rejection test"
        )
        self.assertIsNotNone(proposal_id)

        # Reject the proposal
        success = self.wiki_service.reject(entry_name, proposal_id)
        self.assertTrue(success)

        # Verify proposal status is updated
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        with open(proposal_file) as f:
            proposal_data = json.load(f)
            self.assertEqual(proposal_data["status"], EditStatus.REJECTED.value)

        # Verify that no new version was created
        metadata = self.wiki_service._read_entry_metadata(entry_name)
        self.assertNotIn("1.0.1", metadata.versions)

    def test_reject_nonexistent_proposal(self):
        """Test rejecting a nonexistent proposal."""
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        
        success = self.wiki_service.reject(entry_name, "nonexistent-proposal-id")
        self.assertFalse(success)

    def test_reject_proposal_for_nonexistent_entry(self):
        """Test rejecting a proposal for a nonexistent entry."""
        success = self.wiki_service.reject("nonexistent-entry", "some-proposal-id")
        self.assertFalse(success)

    def test_reject_already_rejected_proposal(self):
        """Test rejecting an already rejected proposal."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Reject the proposal first
        success_first = self.wiki_service.reject(entry_name, proposal_id)
        self.assertTrue(success_first)

        # Try to reject it again
        success_second = self.wiki_service.reject(entry_name, proposal_id)
        # Should succeed (idempotent operation)
        self.assertTrue(success_second)

    def test_reject_applied_proposal(self):
        """Test rejecting an applied proposal."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Apply the proposal first
        self.wiki_service.approve(entry_name, proposal_id)

        # Try to reject the applied proposal
        success = self.wiki_service.reject(entry_name, proposal_id)
        self.assertFalse(success)

    def test_reject_with_invalid_status(self):
        """Test rejecting a proposal with an invalid status."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Manually set an invalid status in the proposal file
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        with open(proposal_file) as f:
            proposal_data = json.load(f)
        proposal_data["status"] = "invalid_status"
        with open(proposal_file, 'w') as f:
            json.dump(proposal_data, f, indent=4)

        # Try to reject the proposal with invalid status
        success = self.wiki_service.reject(entry_name, proposal_id)
        self.assertFalse(success)

    def test_reject_with_malformed_proposal_file(self):
        """Test rejecting a proposal with a malformed JSON file."""
        # Setup
        created_entry = self._create_test_entry()
        entry_name = created_entry.entry_name
        proposal_id = self.wiki_service.propose_edit(
            entry_name, "New content", "editor", "Test"
        )
        self.assertIsNotNone(proposal_id)

        # Corrupt the proposal file
        entry_path = Path(self.test_dir) / entry_name
        proposal_file = entry_path / "proposals" / f"{proposal_id}.json"
        proposal_file.write_text("{ invalid json", encoding="utf-8")

        # Try to reject the malformed proposal
        success = self.wiki_service.reject(entry_name, proposal_id)
        self.assertFalse(success)


if __name__ == "__main__":
    main()
