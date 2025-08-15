import logging
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

import chromadb
import ollama


class VectorStore:
    """A wrapper for a vector database (ChromaDB) to handle storage
    and retrieval of wiki entry embeddings.
    """

    def __init__(self, path: str = "data/chroma_db", collection_name: str = "wiki"):
        """Initializes the VectorStore.

        Args:
            path: The directory to store the ChromaDB data.
            collection_name: The name of the collection to use.

        """
        try:
            self.client = chromadb.PersistentClient(path=path)
            self.collection = self.client.get_or_create_collection(name=collection_name)
            # Use a specific, recommended embedding model from Ollama
            self.embedding_model = "nomic-embed-text"
            logging.info(
                f"VectorStore initialized with ChromaDB at '{path}' and collection '{collection_name}'."
            )
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB client: {e}")
            raise

<<<<<<< HEAD
    async def add_entry(self, doc_id: str, content: str, metadata: Dict[str, Any]):
=======
    async def add_entry(self, doc_id: str, content: str, metadata: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """Generates an embedding for a document and upserts it into the collection.
        'Upsert' will add the document if it's new or update it if it exists.
        """
        try:
            response = await ollama.embeddings(model=self.embedding_model, prompt=content)
            embedding = response["embedding"]
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
            )
            logging.info(f"Upserted document '{doc_id}' into vector store.")
        except Exception as e:
            logging.error(f"Failed to add entry '{doc_id}' to vector store: {e}")

<<<<<<< HEAD
    async def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
=======
    async def search(self, query: str, n_results: int = 3) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Performs a semantic search for a given query.
        """
        try:
            response = await ollama.embeddings(model=self.embedding_model, prompt=query)
            query_embedding = response["embedding"]
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=n_results
            )
            return results
        except Exception as e:
            logging.error(f"Failed to perform search in vector store: {e}")
            return []
