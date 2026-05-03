# P0 核心接口与类型 - API参考 (P0 Core Interfaces & Types - API Reference)

## 📋 核心接口定义

### IModelProvider 接口
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List

class IModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        """生成文本响应的异步生成器"""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """将文本转换为嵌入向量"""
        pass
```

### IKnowledgeManager 接口
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class IKnowledgeManager(ABC):
    @abstractmethod
    def search(self, query_text: str, top_k: int) -> List[Dict]:
        """根据查询文本搜索相关知识"""
        pass
    
    @abstractmethod
    def sync_knowledge_base(self) -> Dict:
        """同步知识库，返回变更统计"""
        pass
```

### ITool 接口
```python
from abc import ABC, abstractmethod

class ITool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具并返回结果"""
        pass
```

## 🧩 数据模型 (Pydantic Models)

### AgentEvent 及其子类型
```python
from pydantic import BaseModel
from typing import Literal, Dict, Any, Union

class ThoughtEvent(BaseModel):
    type: Literal["thought"]
    content: str

class ToolCallEvent(BaseModel):
    type: Literal["tool_call"]
    tool_name: str
    args: Dict[str, Any]

class ToolOutputEvent(BaseModel):
    type: Literal["tool_output"]
    tool_name: str
    status: Literal["success", "error"]
    output: str

class FinalResponseEvent(BaseModel):
    type: Literal["final_response"]
    content: str

class ErrorEvent(BaseModel):
    type: Literal["error"]
    message: str

class PermissionRequestEvent(BaseModel):
    type: Literal["permission_request"]
    tool_name: str
    args: Dict[str, Any]

class ResponseChunkEvent(BaseModel):
    type: Literal["response_chunk"]
    delta: str

AgentEvent = Union[
    ThoughtEvent, ToolCallEvent, ToolOutputEvent,
    FinalResponseEvent, ErrorEvent, PermissionRequestEvent,
    ResponseChunkEvent
]
```

### AgentStatus
```python
from daip_live.core.models import AgentState

class AgentStatus(BaseModel):
    """代理执行器的实时状态快照"""
    state: AgentState
    model_name: str
    tokens_used: int
    tokens_total: int
```

## 🚨 异常体系 (Exception Hierarchy)

```python
class DAIPError(Exception):
    """所有应用特定错误的基类"""
    pass

class ModelError(DAIPError):
    """与模型提供者相关的错误 (P3)"""
    pass

class ModelConnectionError(ModelError):
    pass

class ModelAuthenticationError(ModelError):
    pass

class ToolError(DAIPError):
    """与工具执行相关的错误 (P4)"""
    pass

class ToolInputError(ToolError):
    pass

class ToolPermissionError(ToolError):
    pass
```

---
> **需要实现详情？** 查看 [P0_core_interfaces_detailed.md](P0_core_interfaces_detailed.md)  
> **需要集成指南？** 查看 [P0_core_interfaces_integration.md](P0_core_interfaces_integration.md)