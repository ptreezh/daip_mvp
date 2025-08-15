#!/usr/bin/env python3
"""Personal Intelligence Hub - Wiki Models

Wiki相关的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class WikiUpdateSource(Enum):
    """Wiki更新来源"""
    CONSENSUS_NODE = "consensus_node"
    FACT_EXTRACTION = "fact_extraction"
    USER = "user"
    SYSTEM = "system"


class WikiPageStatus(Enum):
    """Wiki页面状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class WikiPage:
    """Wiki页面"""
    id: str
    title: str
    content: str
    quality_score: float
    version: int
    created_at: datetime
    updated_at: datetime
    status: WikiPageStatus = WikiPageStatus.DRAFT
    tags: list[str] = None
    metadata: dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WikiSearchResult:
    """Wiki搜索结果"""
    page_id: str
    title: str
    content_preview: str
    quality_score: float
    relevance_score: float
    last_updated: datetime


@dataclass
class WikiUpdate:
    """Wiki更新记录"""
    id: str
    page_id: str
    source: WikiUpdateSource
    content: str
    quality_score: float
    timestamp: datetime
    metadata: dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConsensusNodeFact:
    """共识节点事实"""
    id: str
    content: str
    confidence: float
    source_agents: list[str]
    timestamp: datetime
    metadata: dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}