"""
Paper metadata model for document tools.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """Metadata for academic papers."""

    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    language: str = "en"
