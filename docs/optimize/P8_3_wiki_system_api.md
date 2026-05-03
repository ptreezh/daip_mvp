# P8.3 维基系统 - API参考 (P8.3 Wiki System - API Reference)

## 📋 核心类与方法

### WikiManager
```python
class WikiManager:
    async def create_page(self, title: str, content: str, author: str, tags: List[str] = None) -> WikiPage:
        """创建维基页面"""
    
    async def get_page(self, title: str) -> Optional[WikiPage]:
        """获取维基页面"""
    
    async def update_page(self, title: str, content: str, author: str, summary: str = "") -> WikiPage:
        """更新维基页面"""
    
    async def delete_page(self, title: str, author: str) -> bool:
        """删除维基页面"""
    
    async def search_pages(self, query: str, top_k: int = 10, tags: List[str] = None) -> List[WikiPage]:
        """搜索维基页面"""
    
    def get_page_history(self, title: str) -> List[PageVersion]:
        """获取页面历史"""
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
    
    async def export_page(self, title: str, format: str = "markdown") -> str:
        """导出页面"""
```

## 🧩 数据模型

### 维基页面模型
```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PageVersion(BaseModel):
    version_id: str
    content: str
    author: str
    timestamp: datetime
    edit_summary: str

class WikiPage(BaseModel):
    title: str
    content: str
    author: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    version_history: List[PageVersion]
    linked_pages: List[str]
    metadata: Dict[str, Any]  # 扩展元数据

class WikiSearchResult(BaseModel):
    page: WikiPage
    relevance_score: float
    snippet: str
```

### 维基统计信息
```python
class WikiStatistics(BaseModel):
    total_pages: int
    total_authors: int
    most_popular_tags: List[Tuple[str, int]]
    recent_edits: List[WikiPage]
    growth_rate: float
```

## 🔧 事件类型

### 维基系统事件
```python
from typing import Literal, Union

class WikiPageCreatedEvent(BaseModel):
    type: Literal["page_created"]
    page_title: str
    author: str
    timestamp: datetime

class WikiPageUpdatedEvent(BaseModel):
    type: Literal["page_updated"]
    page_title: str
    author: str
    edit_summary: str
    timestamp: datetime

class WikiPageDeletedEvent(BaseModel):
    type: Literal["page_deleted"]
    page_title: str
    author: str
    timestamp: datetime

class WikiSearchEvent(BaseModel):
    type: Literal["search_performed"]
    query: str
    result_count: int
    timestamp: datetime

WikiEvent = Union[WikiPageCreatedEvent, WikiPageUpdatedEvent, WikiPageDeletedEvent, WikiSearchEvent]
```

## 🔌 集成接口

### 依赖的外部组件
- `P2 KnowledgeManager`: 知识检索和索引
- `P1 DatabaseManager`: 数据持久化
- `P0 IModelProvider`: 内容分析（可选）

### API端点
- **创建页面**: `POST /api/wiki/pages`
- **获取页面**: `GET /api/wiki/pages/{title}`
- **搜索页面**: `POST /api/wiki/search`
- **更新页面**: `PUT /api/wiki/pages/{title}`
- **删除页面**: `DELETE /api/wiki/pages/{title}`

---
> **需要实现详情？** 查看 [P8_3_wiki_system_detailed.md](P8_3_wiki_system_detailed.md)  
> **需要集成指南？** 查看 [P8_3_wiki_system_integration.md](P8_3_wiki_system_integration.md)