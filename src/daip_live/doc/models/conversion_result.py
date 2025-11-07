"""
Core document models for enhanced knowledge tools.
Following Pydantic patterns as specified in the DAIP-LIVE Constitution.
"""
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentConversionResult(BaseModel):
    """Result of document conversion operations."""
    source_format: str
    target_format: str
    source_path: str
    target_path: str
    success: bool
    converted_size: int = 0
    conversion_time: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class PPTGenerationResult(BaseModel):
    """Result of PowerPoint generation operations."""
    source_content: str
    presentation_title: str
    slide_count: int
    output_path: str
    success: bool
    generation_time: float = 0.0
    error_message: Optional[str] = None
    slide_titles: List[str] = Field(default_factory=list)


class PaperDownloadResult(BaseModel):
    """Result of paper download operations."""
    paper_id: str
    title: str
    source: str
    success: bool
    file_path: str
    metadata: Optional['PaperMetadata'] = None  # Forward reference to avoid circular import
    download_time: float
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)