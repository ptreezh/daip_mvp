# API参考 (API Reference)

## 📋 概述

本文档提供DAIP-LIVE系统的完整API参考。API分为内部Python API和外部REST API。

## 🏗️ 内部Python API

### P0 核心接口 (Core Interfaces)

#### IModelProvider
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

#### IKnowledgeManager
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

#### ITool
```python
from abc import ABC, abstractmethod

class ITool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具并返回结果"""
        pass
```

### P5 代理引擎 (Agent Engine)

#### AgentExecutor
```python
from typing import AsyncGenerator
from daip_live.core.models import AgentEvent

class AgentExecutor:
    def get_status(self) -> AgentStatus:
        """获取代理执行器的实时状态"""
        pass
    
    async def run(self, goal: str, ...) -> AsyncGenerator[AgentEvent, None]:
        """执行任务导向模式"""
        pass
    
    async def chat_run(self, initial_goal: str) -> AsyncGenerator[AgentEvent, None]:
        """执行对话模式"""
        pass
```

### P8 高级系统 (Advanced Systems)

#### DebateManager
```python
from typing import List, AsyncGenerator

class DebateManager:
    async def run_debate(self, topic: str, roles: List[str], rounds: int) -> AsyncGenerator[DebateEvent, None]:
        """运行辩论流程"""
        pass
```

## 🌐 外部REST API

### 基础路径
```
http://localhost:8000/api/v1
```

### 辩论API
```
GET    /debate/sessions          # 获取辩论会话列表
POST   /debate/start             # 开始新辩论
GET    /debate/{session_id}      # 获取特定辩论会话
DELETE /debate/{session_id}      # 删除辩论会话
```

### 维基API
```
GET    /wiki/pages              # 获取页面列表
GET    /wiki/pages/{title}      # 获取特定页面
POST   /wiki/pages              # 创建新页面
PUT    /wiki/pages/{title}      # 更新页面
DELETE /wiki/pages/{title}      # 删除页面
POST   /wiki/search             # 搜索页面
```

### 知识管理API
```
GET    /knowledge/search?q={query}&top_k={top_k}  # 语义搜索
POST   /knowledge/sync           # 同步知识库
GET    /knowledge/stats          # 获取知识库统计
```

### 代理API
```
POST   /agent/chat              # 启动聊天会话
POST   /agent/run               # 执行任务
GET    /agent/{id}/status       # 获取代理状态
```

## 📄 数据模型 (Pydantic Models)

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

## 🔐 认证与授权

### API密钥认证
大部分API端点需要在请求头中包含API密钥：
```
Authorization: Bearer your-api-key
```

### 工具权限
某些工具执行可能需要额外的用户授权确认。

## 📈 限流与性能

### 限流
- 默认每分钟50个请求
- 可在配置文件中调整

### 性能提示
- 使用流式响应处理长时间请求
- 批量操作以提高效率
- 合理设置top_k参数以平衡性能和准确性

## 📄 相关规格文档

- `docs/specs/WEB_API_REQUIREMENTS.md` - Web API需求规格
- `docs/p0_core_interfaces/README.md` - P0模块接口定义