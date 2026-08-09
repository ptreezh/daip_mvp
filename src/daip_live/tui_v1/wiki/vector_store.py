"""
Vector Storage for Wiki Knowledge Base

Handles document embeddings, similarity search, and vector storage operations.
"""

import json
import logging
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .document import Document

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result with document and similarity score"""

    document: Document
    score: float
    chunk_id: Optional[str] = None
    chunk_text: Optional[str] = None

    def __post_init__(self):
        """Validate search result"""
        if not 0 <= self.score <= 1:
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")


class VectorStore:
    """Vector storage and similarity search implementation"""

    def __init__(
        self,
        dimension: int,
        index_type: str = "faiss",
        persist_path: Optional[str] = None,
        max_size: int = 10000,
    ):
        self.dimension = dimension
        self.index_type = index_type
        self.persist_path = Path(persist_path) if persist_path else None
        self.max_size = max_size
        self.documents: dict[str, Document] = {}
        self.embeddings: np.ndarray = np.zeros((0, dimension), dtype=np.float32)
        self.document_ids: list[str] = []
        self.chunk_embeddings: dict[str, list[dict[str, Any]]] = {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at

        # Initialize index
        self._init_index()

        if self.persist_path:
            self._ensure_persist_dir()

    def _init_index(self) -> None:
        """Initialize the vector index"""
        try:
            if self.index_type == "faiss":
                import faiss

                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product
                logger.info("Initialized FAISS index")
            else:
                # Fallback to numpy-based search
                self.index = None
                logger.info("Using numpy-based vector search")
        except ImportError:
            logger.warning("FAISS not available, using numpy-based search")
            self.index = None

    def _ensure_persist_dir(self) -> None:
        """Ensure persistence directory exists"""
        if self.persist_path:
            self.persist_path.mkdir(parents=True, exist_ok=True)

    def add_document(self, document: Document) -> bool:
        """Add a document to the vector store"""
        try:
            if not document.embedding:
                logger.warning(f"Document {document.id} has no embedding")
                return False

            if len(document.embedding) != self.dimension:
                logger.error(
                    f"Embedding dimension mismatch: expected {self.dimension}, got {len(document.embedding)}"  # noqa: E501
                )
                return False

            # Check if document already exists
            if document.id in self.documents:
                logger.warning(f"Document {document.id} already exists, updating")
                self.delete_document(document.id)

            # Add document
            self.documents[document.id] = document
            self.document_ids.append(document.id)

            # Add embedding
            embedding_array = np.array([document.embedding], dtype=np.float32)
            if self.embeddings.shape[0] == 0:
                self.embeddings = embedding_array
            else:
                self.embeddings = np.vstack([self.embeddings, embedding_array])

            # Add to index
            if self.index:
                self.index.add(embedding_array)
                logger.debug(
                    f"Added embedding to FAISS index for document {document.id}"
                )

            # Add chunk embeddings if available
            if document.chunk_embeddings:
                self.chunk_embeddings[document.id] = document.chunk_embeddings
                logger.debug(
                    f"Added {len(document.chunk_embeddings)} chunk embeddings for document {document.id}"  # noqa: E501
                )

            # Check size limit
            if len(self.documents) > self.max_size:
                logger.warning(
                    f"Vector store size ({len(self.documents)}) exceeds max_size ({self.max_size})"  # noqa: E501
                )

            self.updated_at = datetime.now()
            logger.info(f"Added document {document.id} to vector store")
            return True

        except Exception as e:
            logger.error(f"Error adding document {document.id}: {e}")
            return False

    def add_documents_batch(self, documents: list[Document]) -> int:
        """Add multiple documents in batch"""
        added_count = 0
        for document in documents:
            if self.add_document(document):
                added_count += 1
        logger.info(f"Added {added_count}/{len(documents)} documents in batch")
        return added_count

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector store"""
        try:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found in vector store")
                return False

            # Remove document
            del self.documents[document_id]

            # Remove from document_ids
            if document_id in self.document_ids:
                self.document_ids.remove(document_id)

            # Rebuild embeddings and index
            self._rebuild_index()

            # Remove chunk embeddings
            if document_id in self.chunk_embeddings:
                del self.chunk_embeddings[document_id]

            self.updated_at = datetime.now()
            logger.info(f"Deleted document {document_id} from vector store")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    def _rebuild_index(self) -> None:
        """Rebuild the vector index"""
        try:
            # Rebuild embeddings array
            new_embeddings = []
            for doc_id in self.document_ids:
                if doc_id in self.documents and self.documents[doc_id].embedding:
                    new_embeddings.append(self.documents[doc_id].embedding)

            if new_embeddings:
                self.embeddings = np.array(new_embeddings, dtype=np.float32)
            else:
                self.embeddings = np.zeros((0, self.dimension), dtype=np.float32)

            # Rebuild FAISS index
            if self.index and len(new_embeddings) > 0:
                import faiss

                self.index = faiss.IndexFlatIP(self.dimension)
                self.index.add(self.embeddings)
                logger.debug(
                    f"Rebuilt FAISS index with {len(new_embeddings)} embeddings"
                )

        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")

    def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        threshold: float = 0.0,
        include_chunks: bool = False,
    ) -> list[SearchResult]:
        """Search for similar documents"""
        try:
            if len(query_vector) != self.dimension:
                raise ValueError(
                    f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}"  # noqa: E501
                )

            if len(self.documents) == 0:
                return []

            query_array = np.array([query_vector], dtype=np.float32)

            if self.index:
                # Use FAISS for search
                scores, indices = self.index.search(
                    query_array, min(top_k, len(self.documents))
                )
                results = []

                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self.document_ids) and score >= threshold:
                        doc_id = self.document_ids[idx]
                        document = self.documents[doc_id]
                        results.append(
                            SearchResult(document=document, score=float(score))
                        )
            else:
                # Use numpy for search
                similarities = np.dot(self.embeddings, query_vector.T).flatten()
                top_indices = np.argsort(similarities)[::-1][:top_k]

                results = []
                for idx in top_indices:
                    if similarities[idx] >= threshold:
                        doc_id = self.document_ids[idx]
                        document = self.documents[doc_id]
                        results.append(
                            SearchResult(
                                document=document, score=float(similarities[idx])
                            )
                        )

            # Add chunk results if requested
            if include_chunks:
                chunk_results = self._search_chunks(query_vector, top_k, threshold)
                results.extend(chunk_results)

            # Sort by score
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []

    def _search_chunks(
        self, query_vector: list[float], top_k: int, threshold: float
    ) -> list[SearchResult]:
        """Search within document chunks"""
        chunk_results = []
        query_array = np.array(query_vector, dtype=np.float32)

        for doc_id, chunks in self.chunk_embeddings.items():
            document = self.documents.get(doc_id)
            if not document:
                continue

            for chunk_info in chunks:
                chunk_embedding = chunk_info["embedding"]
                if len(chunk_embedding) != self.dimension:
                    continue

                # Calculate similarity
                similarity = np.dot(query_array, np.array(chunk_embedding)).item()

                if similarity >= threshold:
                    chunk_result = SearchResult(
                        document=document,
                        score=similarity,
                        chunk_id=chunk_info["chunk_id"],
                        chunk_text=chunk_info["text"],
                    )
                    chunk_results.append(chunk_result)

        # Sort and return top results
        chunk_results.sort(key=lambda x: x.score, reverse=True)
        return chunk_results[:top_k]

    def size(self) -> int:
        """Get number of documents in store"""
        return len(self.documents)

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        return self.documents.get(document_id)

    def get_all_documents(self) -> list[Document]:
        """Get all documents"""
        return list(self.documents.values())

    def get_statistics(self) -> dict[str, Any]:
        """Get vector store statistics"""
        doc_types = {}
        for doc in self.documents.values():
            doc_type = doc.document_type.value
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        total_chunks = sum(len(chunks) for chunks in self.chunk_embeddings.values())

        return {
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "index_type": self.index_type,
            "document_types": doc_types,
            "total_chunks": total_chunks,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "max_size": self.max_size,
            "size_utilization": len(self.documents) / self.max_size
            if self.max_size > 0
            else 0,
        }

    def save(self) -> bool:
        """Save vector store to disk"""
        if not self.persist_path:
            logger.warning("No persist path configured")
            return False

        try:
            # Save documents
            docs_file = self.persist_path / "documents.pkl"
            with open(docs_file, "wb") as f:
                pickle.dump(self.documents, f)

            # Save embeddings
            embeddings_file = self.persist_path / "embeddings.npy"
            np.save(embeddings_file, self.embeddings)

            # Save metadata
            metadata = {
                "dimension": self.dimension,
                "index_type": self.index_type,
                "document_ids": self.document_ids,
                "chunk_embeddings": self.chunk_embeddings,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "max_size": self.max_size,
            }

            metadata_file = self.persist_path / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            # Save FAISS index if available
            if self.index:
                index_file = self.persist_path / "faiss.index"
                import faiss

                faiss.write_index(self.index, str(index_file))

            logger.info(f"Saved vector store to {self.persist_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False

    def load(self) -> bool:
        """Load vector store from disk"""
        if not self.persist_path:
            logger.warning("No persist path configured")
            return False

        try:
            # Load metadata
            metadata_file = self.persist_path / "metadata.json"
            if not metadata_file.exists():
                logger.warning("No metadata file found")
                return False

            with open(metadata_file, encoding="utf-8") as f:
                metadata = json.load(f)

            self.dimension = metadata["dimension"]
            self.index_type = metadata["index_type"]
            self.document_ids = metadata["document_ids"]
            self.chunk_embeddings = metadata["chunk_embeddings"]
            self.created_at = datetime.fromisoformat(metadata["created_at"])
            self.updated_at = datetime.fromisoformat(metadata["updated_at"])
            self.max_size = metadata.get("max_size", 10000)

            # Load documents
            docs_file = self.persist_path / "documents.pkl"
            with open(docs_file, "rb") as f:
                self.documents = pickle.load(f)

            # Load embeddings
            embeddings_file = self.persist_path / "embeddings.npy"
            self.embeddings = np.load(embeddings_file)

            # Rebuild index
            self._init_index()
            if self.index and len(self.embeddings) > 0:
                self.index.add(self.embeddings)

            logger.info(f"Loaded vector store from {self.persist_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False

    def clear(self) -> None:
        """Clear all documents from store"""
        self.documents.clear()
        self.document_ids.clear()
        self.chunk_embeddings.clear()
        self.embeddings = np.zeros((0, self.dimension), dtype=np.float32)
        self._init_index()
        self.updated_at = datetime.now()
        logger.info("Cleared vector store")

    def __len__(self) -> int:
        """Get number of documents"""
        return len(self.documents)

    def __str__(self) -> str:
        """String representation"""
        return f"VectorStore({len(self.documents)} docs, {self.dimension}D)"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"VectorStore(size={len(self.documents)}, dimension={self.dimension}, "
            f"index_type={self.index_type}, persist_path={self.persist_path})"
        )
