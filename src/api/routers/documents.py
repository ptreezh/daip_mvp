import asyncio
import logging

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)

from src.api.dependencies import AppStateDep, get_document_service
from src.models import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    DocumentParsingResponse,
    DocumentUploadResponse,
)

from src.core_services.document_service import DocumentService
# 导入文档解析器
try:
    from src.document_parser import (
        DocumentParser,
        DocumentParserConfig,
    )
    DOCUMENT_PARSER_AVAILABLE = True
except ImportError as e:
    DOCUMENT_PARSER_AVAILABLE = False
    logging.warning(f"Document parser not available: {e}")


router = APIRouter(
    prefix="/documents",
    tags=["Document Processing"],
)

logger = logging.getLogger(__name__)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    chunk_strategy: str = Form("auto"),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Upload and parse a document."""
    try:
        # Delegate all logic to the service layer
        result = await doc_service.process_uploaded_document(
            file, chunk_strategy, chunk_size, chunk_overlap
        )
        return DocumentUploadResponse(
            task_id=result["task_id"],
            filename=file.filename or "",
            file_size=file.tell(),
            status="completed",
            content=result["message"],
        )
    except HTTPException:
        raise  # Re-raise HTTPExceptions from the service
    except Exception as e:
        logger.error(f"Document upload processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@router.get("/parsing/{task_id}", response_model=DocumentParsingResponse)
async def get_parsing_result(task_id: str, doc_service: DocumentService = Depends(get_document_service)):
    """Get the result of a document parsing task."""
    task = doc_service.get_parsing_task_result(task_id)
    result = task["result"]

    if result.success:
        chunks_data = [chunk.dict() for chunk in result.chunks]
        return DocumentParsingResponse(
            task_id=task_id,
            status="completed",
            content=f"Parsing successful, {len(result.chunks)} chunks created.",
            parsing_stats=result.parsing_stats,
            chunks=chunks_data,
        )
    else:
        return DocumentParsingResponse(
            task_id=task_id,
            status="failed",
            content=result.error_message or "Unknown parsing error"
        )


@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    request: DocumentAnalysisRequest,
    state: AppStateDep,
    biz_type: str = Query("financial_report")
):
    """Analyze document content, using the parser for long content."""
    try:
        logger.info(f"Received document analysis request, content length: {len(request.content)}, biz_type: {biz_type}")
        task_id = str(uuid.uuid4())
        analysis_result = ""

        # Simplified analysis logic for demonstration
        if len(request.content) > 1000 and DOCUMENT_PARSER_AVAILABLE:
            parser = DocumentParser(chunk_strategy="recursive", chunk_size=1000, chunk_overlap=200)
            temp_content = request.content.encode("utf-8")
            result = parser.parse_document("temp_content.txt", temp_content)

            if result.success:
                analysis_result = f"# Analysis Report (Parsed)\n\n- Chunks: {len(result.chunks)}\n- Total Chars: {result.total_chars}"
            else:
                analysis_result = "# Analysis Report (Raw)\n\n- Parsing failed, using raw content."
        else:
            analysis_result = f"# Simple Analysis Report\n\n- Content Length: {len(request.content)} chars"

        response = DocumentAnalysisResponse(
            message_type="text",
            content=analysis_result,
            tool_calls=[{"name": "document_analysis", "status": "completed"}],
            task_id=task_id,
        )
        logger.info(f"Document analysis complete for task {task_id}")
        return response

    except Exception as e:
        logger.error(f"Error during document analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/tasks")
async def list_parsing_tasks(state: AppStateDep):
    """List all document parsing tasks."""
    task_list = [
        {
            "task_id": task_id,
            "filename": task.get("filename"),
            "file_size": task.get("file_size"),
            "status": task.get("status"),
            "timestamp": task.get("timestamp"),
        }
        for task_id, task in state.parsing_tasks.items()
    ]
    return {"total_tasks": len(task_list), "tasks": task_list}