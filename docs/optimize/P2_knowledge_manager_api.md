# P2 知识管理器 - API参考 (P2 Knowledge Manager - API Reference)

## 📋 核心类与方法

### KnowledgeManager
```python
class KnowledgeManager:
    async def search(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """语义搜索相关知识"""
    
    async def add_document(self, content: str, metadata: Dict = None) -> bool:
        """添加新文档到知识库"""
    
    async def sync_knowledge_base(self) -> Dict:
        """同步知识库，返回统计信息"""
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """根据ID获取文档"""
```

### VectorStore接口
```python
class VectorStore(ABC):
    @abstractmethod
    async def search(self, query_vector: List[float], top_k: int) -> List[Tuple[str, float]]:
        """向量搜索"""
    
    @abstractmethod
    async def add_vectors(self, texts: List[str], vectors: List[List[float]], metadatas: List[Dict] = None):
        """添加向量到存储"""
    
    @abstractmethod
    def delete(self, doc_ids: List[str]) -> bool:
        """删除文档"""
```

## 🧩 数据模型

### 知识文档模型
```python
from pydantic import BaseModel
from typing import List, Dict, Optional

class KnowledgeDocument(BaseModel):
    id: str
    content: str
    title: str
    source: str
    created_at: datetime
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None

class SearchResult(BaseModel):
    document: KnowledgeDocument
    similarity: float
    snippet: str
```

## 🔧 依赖接口

### 依赖的外部组件
- `FAISS`: 向量数据库
- `Pydantic`: 数据验证
- `P3 ModelProvider`: 用于文本嵌入

## 📡 操作模式
- **异步搜索**: 支持异步语义搜索
- **批量操作**: 支持批量文档处理
- **增量更新**: 支持知识库增量更新

---
> **需要实现详情？** 查看 [P2_knowledge_manager_detailed.md](P2_knowledge_manager_detailed.md)  
> **需要集成指南？** 查看 [P2_knowledge_manager_integration.md](P2_knowledge_manager_integration.md)