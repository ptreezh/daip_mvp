from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.kernel.vector_store import VectorStore

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def vector_store_with_mocks():
    """
    Pytest fixture to set up a VectorStore instance with mocked ChromaDB dependencies.
    """
    with patch("src.kernel.vector_store.chromadb") as mock_chromadb:
        mock_persistent_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_persistent_client
        mock_collection = MagicMock()
        mock_persistent_client.get_or_create_collection.return_value = mock_collection

        # Initialize the VectorStore, which will now use the mocks
        vector_store = VectorStore()
        yield vector_store, mock_collection


@patch("src.kernel.vector_store.ollama.embeddings", new_callable=AsyncMock)
async def test_add_entry(mock_embeddings, vector_store_with_mocks):
    """Tests that add_entry correctly calls the embedding model and upserts to the collection."""
    vector_store, mock_collection = vector_store_with_mocks
    mock_embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}
    doc_id = "test_doc_01"
    content = "This is a test document."
    metadata = {"title": "Test Doc"}

    await vector_store.add_entry(doc_id, content, metadata)

    # Verify ollama.embeddings was called with the correct content
    mock_embeddings.assert_awaited_once_with(
        model=vector_store.embedding_model, prompt=content
    )

    # Verify collection.upsert was called with the correct arguments
    mock_collection.upsert.assert_called_once_with(
        ids=[doc_id],
        embeddings=[[0.1, 0.2, 0.3]],
        documents=[content],
        metadatas=[metadata],
    )


@patch("src.kernel.vector_store.ollama.embeddings", new_callable=AsyncMock)
async def test_search(mock_embeddings, vector_store_with_mocks):
    """Tests that search correctly calls the embedding model and queries the collection."""
    vector_store, mock_collection = vector_store_with_mocks
    mock_embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}
    query = "A test query"
    mock_search_result = {
        "ids": [["doc1"]],
        "documents": [["result document"]],
        "metadatas": [[{"title": "Result"}]],
    }
    mock_collection.query.return_value = mock_search_result

    result = await vector_store.search(query, n_results=1)

    # Verify ollama.embeddings was called with the correct query
    mock_embeddings.assert_awaited_once_with(model=vector_store.embedding_model, prompt=query)

    # Verify collection.query was called with the correct arguments
    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2, 0.3]], n_results=1
    )

    # Verify the result is passed through correctly
    assert result == mock_search_result