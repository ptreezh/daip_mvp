"""
Models for document operations.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """Metadata for academic papers."""
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: str = ""
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    language: str = "en"
    source: str = "local"
    file_path: str = ""
    file_hash: Optional[str] = None


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
    metadata: dict = Field(default_factory=dict)


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
    metadata: dict = Field(default_factory=dict)


class PaperDownloadResult(BaseModel):
    """Result of paper download operations."""
    paper_id: str
    title: str
    source: str
    success: bool
    file_path: str
    metadata: Optional[PaperMetadata] = None
    download_time: float
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


__all__ = ['PaperMetadata', 'DocumentConversionResult', 'PPTGenerationResult', 'PaperDownloadResult']