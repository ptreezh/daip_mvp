"""
Document Ingestion for Wiki Knowledge Base

Handles document parsing, processing, and embedding generation.
"""

from typing import List, Dict, Any, Optional, Union
import os
import logging
from pathlib import Path
import asyncio
import hashlib
from datetime import datetime

from .document import Document, DocumentType, DocumentStatus

logger = logging.getLogger(__name__)


class DocumentIngestor:
    """Handles document ingestion and processing"""

    def __init__(self, embedding_model: Optional[str] = None):
        self.embedding_model = embedding_model
        self.supported_formats = {
            ".txt": DocumentType.TEXT,
            ".md": DocumentType.MARKDOWN,
            ".markdown": DocumentType.MARKDOWN,
            ".pdf": DocumentType.PDF,
            ".html": DocumentType.HTML,
            ".htm": DocumentType.HTML,
            ".json": DocumentType.JSON,
            ".csv": DocumentType.CSV,
            ".py": DocumentType.CODE,
            ".js": DocumentType.CODE,
            ".ts": DocumentType.CODE,
            ".java": DocumentType.CODE,
            ".cpp": DocumentType.CODE,
            ".c": DocumentType.CODE,
            ".h": DocumentType.CODE,
            ".cs": DocumentType.CODE,
            ".go": DocumentType.CODE,
            ".rs": DocumentType.CODE,
            ".php": DocumentType.CODE,
            ".rb": DocumentType.CODE,
            ".swift": DocumentType.CODE,
            ".kt": DocumentType.CODE,
            ".scala": DocumentType.CODE,
            ".sh": DocumentType.CODE,
            ".bash": DocumentType.CODE,
            ".zsh": DocumentType.CODE,
            ".sql": DocumentType.CODE,
            ".xml": DocumentType.CODE,
            ".yaml": DocumentType.CODE,
            ".yml": DocumentType.CODE,
            ".toml": DocumentType.CODE,
            ".ini": DocumentType.CODE,
            ".cfg": DocumentType.CODE,
            ".conf": DocumentType.CODE
        }
        logger.info(f"Initialized document ingestor with {len(self.supported_formats)} supported formats")

    def ingest_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        generate_embedding: bool = True
    ) -> Optional[Document]:
        """Ingest a single file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None

            # Determine document type
            doc_type = self._get_document_type(file_path)
            if doc_type is None:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                return None

            # Extract content
            content = self._extract_content(file_path, doc_type)
            if not content:
                logger.error(f"Failed to extract content from: {file_path}")
                return None

            # Generate title
            title = self._generate_title(file_path, content, doc_type)

            # Create document
            document = Document(
                title=title,
                content=content,
                file_path=str(file_path),
                document_type=doc_type,
                metadata=metadata or {}
            )

            # Add file metadata
            file_stats = file_path.stat()
            document.update_metadata("file_size", file_stats.st_size)
            document.update_metadata("file_modified", datetime.fromtimestamp(file_stats.st_mtime).isoformat())
            document.update_metadata("file_hash", self._calculate_file_hash(file_path))

            # Generate embedding if requested
            if generate_embedding:
                try:
                    embedding = self._generate_embedding(content)
                    if embedding:
                        document.set_embedding(embedding)
                        document.update_status(DocumentStatus.PROCESSED)
                    else:
                        document.update_status(DocumentStatus.FAILED, "Failed to generate embedding")
                except Exception as e:
                    logger.error(f"Error generating embedding for {file_path}: {e}")
                    document.update_status(DocumentStatus.FAILED, str(e))
            else:
                document.update_status(DocumentStatus.PROCESSED)

            logger.info(f"Successfully ingested document: {title}")
            return document

        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            return None

    def ingest_files_batch(
        self,
        file_paths: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        generate_embeddings: bool = True,
        max_concurrent: int = 5
    ) -> List[Document]:
        """Ingest multiple files in batch"""
        documents = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_file(file_path: str) -> Optional[Document]:
            async with semaphore:
                return self.ingest_file(file_path, metadata, generate_embeddings)

        async def process_batch() -> List[Document]:
            tasks = [process_file(file_path) for file_path in file_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            valid_docs = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing {file_paths[i]}: {result}")
                elif result is not None:
                    valid_docs.append(result)

            return valid_docs

        # Run async processing
        try:
            loop = asyncio.get_event_loop()
            documents = loop.run_until_complete(process_batch())
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            # Fallback to synchronous processing
            for file_path in file_paths:
                doc = self.ingest_file(file_path, metadata, generate_embeddings)
                if doc:
                    documents.append(doc)

        logger.info(f"Batch ingested {len(documents)}/{len(file_paths)} documents")
        return documents

    def ingest_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Document]:
        """Ingest all supported files from a directory"""
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return []

        import fnmatch

        files = []
        pattern_list = include_patterns or ["*"]
        exclude_list = exclude_patterns or []

        # Find all files
        for file_path in directory_path.rglob("*") if recursive else directory_path.iterdir():
            if file_path.is_file():
                # Check include patterns
                included = any(fnmatch.fnmatch(file_path.name, pattern) for pattern in pattern_list)

                # Check exclude patterns
                excluded = any(fnmatch.fnmatch(file_path.name, pattern) for pattern in exclude_list)

                if included and not excluded and file_path.suffix.lower() in self.supported_formats:
                    files.append(str(file_path))

        logger.info(f"Found {len(files)} files to ingest from {directory_path}")
        return self.ingest_files_batch(files, metadata)

    def _get_document_type(self, file_path: Path) -> Optional[DocumentType]:
        """Determine document type from file extension"""
        suffix = file_path.suffix.lower()
        return self.supported_formats.get(suffix)

    def _extract_content(self, file_path: Path, doc_type: DocumentType) -> str:
        """Extract content from file based on type"""
        try:
            if doc_type == DocumentType.TEXT:
                return self._extract_text_content(file_path)
            elif doc_type == DocumentType.MARKDOWN:
                return self._extract_markdown_content(file_path)
            elif doc_type == DocumentType.PDF:
                return self._extract_pdf_text(file_path)
            elif doc_type == DocumentType.HTML:
                return self._extract_html_content(file_path)
            elif doc_type == DocumentType.JSON:
                return self._extract_json_content(file_path)
            elif doc_type == DocumentType.CSV:
                return self._extract_csv_content(file_path)
            elif doc_type == DocumentType.CODE:
                return self._extract_text_content(file_path)  # Treat code as text
            else:
                return self._extract_text_content(file_path)  # Fallback
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            return ""

    def _extract_text_content(self, file_path: Path) -> str:
        """Extract content from text file"""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Could not decode file {file_path} with any supported encoding")

    def _extract_markdown_content(self, file_path: Path) -> str:
        """Extract content from markdown file"""
        content = self._extract_text_content(file_path)
        # Basic markdown processing could be added here
        return content

    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except ImportError:
            logger.warning("PyPDF2 not available, using mock PDF extraction")
            return f"Mock PDF content extracted from {file_path.name}"
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return f"Error extracting PDF content from {file_path.name}"

    def _extract_html_content(self, file_path: Path) -> str:
        """Extract text content from HTML file"""
        try:
            from bs4 import BeautifulSoup
            content = self._extract_text_content(file_path)
            soup = BeautifulSoup(content, 'html.parser')
            return soup.get_text()
        except ImportError:
            logger.warning("BeautifulSoup not available, returning raw HTML")
            return self._extract_text_content(file_path)
        except Exception as e:
            logger.error(f"Error extracting HTML content: {e}")
            return self._extract_text_content(file_path)

    def _extract_json_content(self, file_path: Path) -> str:
        """Extract content from JSON file"""
        try:
            import json
            content = self._extract_text_content(file_path)
            data = json.loads(content)
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error extracting JSON content: {e}")
            return self._extract_text_content(file_path)

    def _extract_csv_content(self, file_path: Path) -> str:
        """Extract content from CSV file"""
        try:
            import csv
            content = self._extract_text_content(file_path)
            reader = csv.reader(content.splitlines())
            rows = list(reader)
            return "\n".join([",".join(row) for row in rows])
        except Exception as e:
            logger.error(f"Error extracting CSV content: {e}")
            return self._extract_text_content(file_path)

    def _generate_title(self, file_path: Path, content: str, doc_type: DocumentType) -> str:
        """Generate document title"""
        # Try to get title from content first
        if doc_type == DocumentType.MARKDOWN:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    return line[2:].strip()
        elif doc_type == DocumentType.HTML:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    return title_tag.get_text().strip()
            except ImportError:
                pass
        elif doc_type == DocumentType.JSON:
            try:
                import json
                data = json.loads(content)
                if isinstance(data, dict) and 'title' in data:
                    return str(data['title'])
            except:
                pass

        # Fallback to filename
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""

    def _generate_embedding(self, content: str) -> Optional[List[float]]:
        """Generate embedding for content"""
        try:
            # This is a mock embedding generator
            # In a real implementation, this would use an actual embedding model
            import hashlib

            # Create a deterministic pseudo-embedding based on content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()

            # Convert hash to 768-dimensional embedding (common size)
            embedding = []
            for i in range(0, min(len(content_hash), 128), 2):
                hex_pair = content_hash[i:i+2]
                val = int(hex_pair, 16) / 255.0  # Normalize to 0-1
                # Replicate to reach desired dimension
                for _ in range(6):  # 128 * 6 = 768
                    embedding.append(val)

            # Ensure correct dimension
            embedding = embedding[:768]
            if len(embedding) < 768:
                embedding.extend([0.0] * (768 - len(embedding)))

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def get_supported_formats(self) -> Dict[str, DocumentType]:
        """Get supported file formats"""
        return self.supported_formats.copy()

    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        """Check if file format is supported"""
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats

    def update_embedding_model(self, model_name: str) -> None:
        """Update the embedding model"""
        self.embedding_model = model_name
        logger.info(f"Updated embedding model to: {model_name}")