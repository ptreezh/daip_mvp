import unittest
from unittest.mock import MagicMock, patch

from src.kernel.vector_store import VectorStore


class TestVectorStore(unittest.TestCase):
    @patch("src.kernel.vector_store.ollama")
    @patch("src.kernel.vector_store.chromadb")
    def setUp(self, mock_chromadb, mock_ollama):
        # Mock the ChromaDB client and its collection
        mock_persistent_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_persistent_client
        self.mock_collection = MagicMock()
        mock_persistent_client.get_or_create_collection.return_value = (
            self.mock_collection
        )

        # Mock the ollama module used by the VectorStore
        self.mock_ollama = mock_ollama
        self.mock_ollama.embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

        # Initialize the VectorStore, which will now use the mocks
        self.vector_store = VectorStore()

    def test_add_entry(self):
        """Tests that add_entry correctly calls the embedding model and upserts to the collection."""
        doc_id = "test_doc_01"
        content = "This is a test document."
        metadata = {"title": "Test Doc"}

        self.vector_store.add_entry(doc_id, content, metadata)

        # Verify ollama.embeddings was called with the correct content
        self.mock_ollama.embeddings.assert_called_once_with(
            model=self.vector_store.embedding_model, prompt=content
        )

        # Verify collection.upsert was called with the correct arguments
        self.mock_collection.upsert.assert_called_once_with(
            ids=[doc_id],
            embeddings=[[0.1, 0.2, 0.3]],
            documents=[content],
            metadatas=[metadata],
        )

    def test_search(self):
        """Tests that search correctly calls the embedding model and queries the collection."""
        query = "A test query"
        mock_search_result = {
            "ids": [["doc1"]],
            "documents": [["result document"]],
            "metadatas": [[{"title": "Result"}]],
        }
        self.mock_collection.query.return_value = mock_search_result

        result = self.vector_store.search(query, n_results=1)

        # Verify ollama.embeddings was called with the correct query
        self.mock_ollama.embeddings.assert_called_with(
            model=self.vector_store.embedding_model, prompt=query
        )

        # Verify collection.query was called with the correct arguments
        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]], n_results=1
        )

        # Verify the result is passed through correctly
        self.assertEqual(result, mock_search_result)