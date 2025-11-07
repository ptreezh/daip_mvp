"""
Paper metadata model for document tools.
"""
from typing import List, Optional
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