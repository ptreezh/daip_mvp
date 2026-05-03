# P0 核心接口与类型 (Core Interfaces & Types)

## 📋 概述

P0模块是DAIP-LIVE系统的基石，定义了跨所有模块共享的数据契约(Pydantic模型)和接口契约(抽象基类)。该模块确保了整个系统的类型安全性以及模块间的松耦合。

## 🔧 数据契约 (Data Contracts)

### AgentEvent 事件系统
```python
from pydantic import BaseModel
from typing import Literal, Union, Dict, Any

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

### 核心数据模型
- **`TodoItem`**: 定义待办任务
- **`Role`**: 定义AI代理配置
- **`Session`**: 定义用户会话元数据
- **`AssistantState`**: 表示助手统一状态

### 状态和上下文模型
- **`AgentState` (Enum)**: 代理执行器内部状态枚举
- **`SessionContext`**: 会话上下文信息

### 工作流模型
- **`ConsensusResult`**: 多代理共识结果
- **`AgentState`**: 代理状态枚举

## 🔌 接口契约 (Interface Contracts)

### 核心接口定义
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict

class IModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

class IKnowledgeManager(ABC):
    @abstractmethod
    def search(self, query_text: str, top_k: int) -> List[Dict]:
        pass
    
    @abstractmethod
    def sync_knowledge_base(self) -> Dict:
        pass

class ITool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass
```

## ⚡ 异常体系 (Exception Hierarchy)

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

## 🏗️ 设计原则

- **稳定性优先**: P0模块的API变更需谨慎考虑，因影响所有其他模块
- **类型安全**: 所有数据模型使用Pydantic进行类型和验证
- **接口隔离**: 接口契约确保模块间松耦合
- **可扩展性**: 事件系统支持异步流处理和UI实时更新

## 📁 相关代码

- `src/daip_live/core/models.py` - 所有Pydantic数据模型定义
- `src/daip_live/core/interfaces.py` - 所有接口契约定义