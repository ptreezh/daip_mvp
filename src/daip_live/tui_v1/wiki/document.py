"""
Document Management for Wiki Knowledge Base

Handles document representation, metadata, and status tracking.
"""

import logging
import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Supported document types"""

    TEXT = "text"
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    CODE = "code"


class DocumentStatus(Enum):
    """Document processing status"""

    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    PENDING = "pending"


class Document:
    """Represents a document in the knowledge base"""

    def __init__(
        self,
        title: str,
        content: str,
        file_path: str,
        document_type: DocumentType,
        document_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        self.id = document_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.file_path = file_path
        self.document_type = document_type
        self.status = DocumentStatus.PROCESSING
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.processed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.embedding: Optional[list[float]] = None
        self.embedding_dimension: Optional[int] = None
        self.chunk_embeddings: list[dict[str, Any]] = []  # For chunked embeddings
        self.tags: list[str] = self.metadata.get("tags", [])
        self.author = self.metadata.get("author")
        self.version = self.metadata.get("version")

    def update_status(
        self, status: DocumentStatus, error_message: Optional[str] = None
    ) -> None:
        """Update document status"""
        self.status = status
        self.updated_at = datetime.now()

        if status == DocumentStatus.PROCESSED:
            self.processed_at = self.updated_at
        elif status == DocumentStatus.FAILED:
            self.error_message = error_message

        logger.debug(f"Document {self.id} status updated to {status.value}")

    def set_embedding(self, embedding: list[float]) -> None:
        """Set document embedding"""
        self.embedding = embedding
        self.embedding_dimension = len(embedding)
        self.updated_at = datetime.now()
        logger.debug(
            f"Set embedding for document {self.id} (dimension: {self.embedding_dimension})"  # noqa: E501
        )

    def add_chunk_embedding(
        self,
        chunk_id: str,
        embedding: list[float],
        chunk_text: str,
        start_pos: int,
        end_pos: int,
    ) -> None:
        """Add chunk embedding for large documents"""
        chunk_info = {
            "chunk_id": chunk_id,
            "embedding": embedding,
            "text": chunk_text,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "created_at": datetime.now().isoformat(),
        }
        self.chunk_embeddings.append(chunk_info)
        logger.debug(f"Added chunk embedding {chunk_id} for document {self.id}")

    def get_word_count(self) -> int:
        """Get word count of document content"""
        # Remove markdown/HTML tags and count words
        clean_text = re.sub(r"<[^>]+>", " ", self.content)  # Remove HTML tags
        clean_text = re.sub(r"[#*`\[\]()]", " ", clean_text)  # Remove markdown symbols
        words = re.findall(r"\b\w+\b", clean_text)
        return len(words)

    def get_character_count(self) -> int:
        """Get character count of document content"""
        return len(self.content)

    def get_reading_time(self, wpm: int = 200) -> float:
        """Estimate reading time in minutes"""
        word_count = self.get_word_count()
        return max(0.1, word_count / wpm)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.metadata["tags"] = self.tags
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.metadata["tags"] = self.tags
            self.updated_at = datetime.now()

    def update_metadata(self, key: str, value: Any) -> None:
        """Update document metadata"""
        self.metadata[key] = value
        self.updated_at = datetime.now()

        # Update cached fields if relevant
        if key == "tags" and isinstance(value, list):
            self.tags = value
        elif key == "author":
            self.author = value
        elif key == "version":
            self.version = value

    def get_content_preview(self, max_length: int = 200) -> str:
        """Get a preview of document content"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length].rstrip() + "..."

    def get_chunks(self, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
        """Split document into chunks for processing"""
        if len(self.content) <= chunk_size:
            return [self.content]

        chunks = []
        start = 0

        while start < len(self.content):
            end = start + chunk_size
            if end >= len(self.content):
                chunks.append(self.content[start:])
                break

            # Try to break at word boundary
            chunk_end = end
            while chunk_end > start and self.content[chunk_end] not in ".!?\n ":
                chunk_end -= 1

            if chunk_end == start:
                chunk_end = end

            chunks.append(self.content[start:chunk_end])
            start = chunk_end - overlap

        return chunks

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "file_path": self.file_path,
            "document_type": self.document_type.value,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "processed_at": self.processed_at.isoformat()
            if self.processed_at
            else None,
            "error_message": self.error_message,
            "embedding": self.embedding,
            "embedding_dimension": self.embedding_dimension,
            "chunk_embeddings": self.chunk_embeddings,
            "tags": self.tags,
            "author": self.author,
            "version": self.version,
            "statistics": {
                "word_count": self.get_word_count(),
                "character_count": self.get_character_count(),
                "reading_time_minutes": self.get_reading_time(),
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create document from dictionary"""
        document = cls(
            title=data["title"],
            content=data["content"],
            file_path=data["file_path"],
            document_type=DocumentType(data["document_type"]),
            document_id=data.get("id"),
            metadata=data.get("metadata", {}),
        )

        if "status" in data:
            document.status = DocumentStatus(data["status"])

        if "created_at" in data:
            document.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            document.updated_at = datetime.fromisoformat(data["updated_at"])

        if "processed_at" in data and data["processed_at"]:
            document.processed_at = datetime.fromisoformat(data["processed_at"])

        if "error_message" in data:
            document.error_message = data["error_message"]

        if "embedding" in data:
            document.embedding = data["embedding"]
            document.embedding_dimension = len(data["embedding"])

        if "embedding_dimension" in data:
            document.embedding_dimension = data["embedding_dimension"]

        if "chunk_embeddings" in data:
            document.chunk_embeddings = data["chunk_embeddings"]

        if "tags" in data:
            document.tags = data["tags"]

        if "author" in data:
            document.author = data["author"]

        if "version" in data:
            document.version = data["version"]

        return document

    def __str__(self) -> str:
        """String representation"""
        return f"Document: {self.title} ({self.document_type.value})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"Document(id={self.id[:8]}..., title='{self.title}', "
            f"type={self.document_type.value}, status={self.status.value}, "
            f"words={self.get_word_count()})"
        )

    def __eq__(self, other) -> bool:
        """Equality comparison based on ID"""
        if isinstance(other, Document):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id)
