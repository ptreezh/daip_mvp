import asyncio
import logging
import uuid
<<<<<<< HEAD
from typing import Any, Dict
=======
from typing import Any
>>>>>>> feature/core-services-refactor

from fastapi import HTTPException, UploadFile

try:
    from src.document_parser import (
        DocumentParser,
        DocumentParserConfig,
        ParsingResult,
    )

    DOCUMENT_PARSER_AVAILABLE = True
except ImportError:
    DOCUMENT_PARSER_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentService:
    """Service layer for handling document processing, including uploading,
    parsing, and retrieving task results.
    """

    def __init__(self, app_state: Any): # Use Any to avoid circular import type hint
        self.app_state = app_state
        if not DOCUMENT_PARSER_AVAILABLE:
            logger.warning("Document parser is not available. Document processing will be disabled.")
            raise HTTPException(status_code=503, detail="Document parser not available")

    async def process_uploaded_document(
        self, file: UploadFile, chunk_strategy: str, chunk_size: int, chunk_overlap: int
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handles the entire document upload and parsing workflow.
        Returns a dictionary with the task_id and a summary message.
        """
        task_id = str(uuid.uuid4())
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"Starting to parse document: {file.filename}, Size: {file_size} bytes")

        file_type = file.filename.split(".")[-1].lower() if file.filename else ""

        if chunk_strategy == "auto":
            config = DocumentParserConfig.get_optimal_config(file_type, file_size)
            chunk_strategy = config["chunk_strategy"]
            chunk_size = config["chunk_size"]
            chunk_overlap = config["chunk_overlap"]

        parser = DocumentParser(
            chunk_strategy=chunk_strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        result = parser.parse_document(file.filename or "unknown_file", file_content)

        self.app_state.parsing_tasks[task_id] = {
            "filename": file.filename,
            "file_size": file_size,
            "status": "completed" if result.success else "failed",
            "result": result,
            "timestamp": asyncio.get_event_loop().time(),
        }

        if not result.success:
            logger.error(f"Document parsing failed: {file.filename}, Error: {result.error_message}")
            raise HTTPException(status_code=500, detail=f"Document parsing failed: {result.error_message}")

        logger.info(f"Document parsed successfully: {file.filename}, created {len(result.chunks)} chunks.")
        return {
            "task_id": task_id,
            "message": f"Document parsed successfully, created {len(result.chunks)} chunks.",
        }

    def get_parsing_task_result(self, task_id: str) -> dict[str, Any]:
        """Retrieves and formats the result of a specific parsing task."""
        if task_id not in self.app_state.parsing_tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        return self.app_state.parsing_tasks[task_id]
