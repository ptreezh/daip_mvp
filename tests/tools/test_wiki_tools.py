import shutil
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.tools import wiki_tools


class TestWikiTools(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for wiki files and mock dependencies."""
        self.test_dir = Path("tests/temp_wiki_data")
        self.test_dir.mkdir(exist_ok=True)

        # Patch the WIKI_DIR constant in the wiki_tools module to use our temp dir
        self.wiki_dir_patcher = patch("src.tools.wiki_tools.WIKI_DIR", self.test_dir)
        self.wiki_dir_patcher.start()

        # Mock the factory function to control the VectorStore instance used by the tools
        self.get_vs_patcher = patch("src.tools.wiki_tools._get_vector_store")
        self.mock_get_vector_store = self.get_vs_patcher.start()
        self.mock_vector_store_instance = MagicMock()
        self.mock_get_vector_store.return_value = self.mock_vector_store_instance

    def tearDown(self):
        """Clean up the temporary directory and stop patches."""
        shutil.rmtree(self.test_dir)
        self.wiki_dir_patcher.stop()
        self.get_vs_patcher.stop()

    def test_sanitize_filename(self):
        """Tests the filename sanitization logic."""
        self.assertEqual(wiki_tools._sanitize_filename("What is AI?"), "what_is_ai.md")
        self.assertEqual(
            wiki_tools._sanitize_filename("  leading/trailing spaces  "),
            "leading_trailing_spaces.md",
        )
        self.assertEqual(wiki_tools._sanitize_filename("!@#$%^&*()"), "untitled.md")

    def test_write_wiki_entry(self):
        """Tests writing a wiki entry to a file and adding it to the vector store."""
        title = "Test Title"
        content = "This is the content."

        result = wiki_tools.write_wiki_entry(title, content)

        # Check that the file was written correctly
        expected_file = self.test_dir / "test_title.md"
        self.assertTrue(expected_file.exists())
        self.assertEqual(expected_file.read_text(encoding="utf-8"), content)
        self.assertIn("Successfully saved", result)

        # Check that the vector store was called correctly
        self.mock_vector_store_instance.add_entry.assert_called_once_with(
            doc_id="test_title.md", content=content, metadata={"title": title}
        )

    def test_read_wiki_entry(self):
        """Tests reading an existing wiki entry."""
        title = "Existing Entry"
        content = "Content of existing entry."
        (self.test_dir / "existing_entry.md").write_text(content, encoding="utf-8")

        result = wiki_tools.read_wiki_entry(title)
        self.assertEqual(result, content)

    def test_list_wiki_entries(self):
        """Tests listing all available wiki entries."""
        (self.test_dir / "alpha_entry.md").touch()
        (self.test_dir / "beta_entry.md").touch()

        result = wiki_tools.list_wiki_entries()
        self.assertIn("alpha entry", result)
        self.assertIn("beta entry", result)
        # Check that the output is sorted alphabetically
        self.assertTrue(result.find("alpha entry") < result.find("beta entry"))

    def test_search_wiki_success(self):
        """Tests a successful semantic search and result formatting."""
        mock_results = {
            "documents": [["doc content 1", "doc content 2"]],
            "metadatas": [[{"title": "Result 1"}, {"title": "Result 2"}]],
        }
        self.mock_vector_store_instance.search.return_value = mock_results

        result = wiki_tools.search_wiki("some query")

        self.mock_vector_store_instance.search.assert_called_once_with(
            "some query", n_results=3
        )
        self.assertIn("Found 2 relevant results", result)
        self.assertIn("Title: Result 1", result)
        self.assertIn("Content Snippet: doc content 1", result)

    def test_search_wiki_no_results(self):
        """Tests a semantic search that returns no results."""
        self.mock_vector_store_instance.search.return_value = {"documents": []}

        result = wiki_tools.search_wiki("obscure query")

        self.assertIn("No relevant wiki entries found", result)