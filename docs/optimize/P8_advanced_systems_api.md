# P8 高级功能系统 - API参考 (P8 Advanced Systems - API Reference)

## 📋 核心类与方法

### 高级系统基类
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List

class AdvancedSystem(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> AsyncGenerator[AdvancedEvent, None]:
        """执行高级系统功能"""
        pass
    
    @abstractmethod
    def get_status(self) -> SystemStatus:
        """获取系统状态"""
        pass
```

## 🔧 P8.1 辩论系统 API

### DebateManager
```python
class DebateManager:
    async def run_debate(self, topic: str, roles: List[str], rounds: int) -> AsyncGenerator[DebateEvent, None]:
        """运行辩论流程"""
    
    def get_debate_model_summary(self, roles: List[str]) -> Dict:
        """获取辩论模型摘要"""
    
    async def get_debate_statistics(self, session_id: str) -> DebateStatistics:
        """获取辩论统计信息"""
    
    def get_available_roles(self) -> List[str]:
        """获取可用角色列表"""
    
    async def save_debate_transcript(self, session_id: str, filename: str) -> bool:
        """保存辩论记录"""
```

### 辩论事件类型
```python
from pydantic import BaseModel
from typing import Literal

class DebateStartEvent(BaseModel):
    type: Literal["debate_start"]
    topic: str
    roles: List[str]
    rounds: int
    session_id: str

class DebateRoundStartEvent(BaseModel):
    type: Literal["round_start"]
    round_number: int
    topic: str

class DebateTurnCompleteEvent(BaseModel):
    type: Literal["turn_complete"]
    participant: str
    content: str
    content_preview: str

class DebateCompleteEvent(BaseModel):
    type: Literal["debate_complete"]
    summary: str
    consensus: Optional[str]
```

## 🔧 P8.2 人类助手系统 API

### PersonalAssistant
```python
class PersonalAssistant:
    async def handle_request(self, user_request: str) -> AsyncGenerator[AssistantEvent, None]:
        """处理用户请求"""
    
    def decompose_task(self, complex_task: str) -> List[SubTask]:
        """任务分解"""
    
    async def execute_workflow(self, workflow_definition: WorkflowDefinition) -> WorkflowResult:
        """执行工作流"""
```

## 🔧 P8.3 维基系统 API

### WikiManager
```python
class WikiManager:
    async def create_page(self, title: str, content: str, author: str) -> WikiPage:
        """创建维基页面"""
    
    async def search_pages(self, query: str, top_k: int = 10) -> List[WikiPage]:
        """搜索维基页面"""
    
    async def update_page(self, title: str, content: str, author: str) -> WikiPage:
        """更新维基页面"""
    
    def get_page_history(self, title: str) -> List[PageVersion]:
        """获取页面历史"""
```

## 🧩 高级数据模型

### 系统状态模型
```python
from pydantic import BaseModel
from typing import Dict, Any

class SystemStatus(BaseModel):
    system_name: str
    status: Literal["idle", "running", "error", "completed"]
    active_sessions: int
    performance_metrics: Dict[str, Any]
```

## 🔌 通用接口

### 事件类型
- **DebateEvent**: 辩论相关事件
- **AssistantEvent**: 助手相关事件
- **WikiEvent**: 维基相关事件

### 状态管理
- **会话管理**: 跨系统的会话状态
- **历史跟踪**: 操作历史记录
- **性能监控**: 系统性能指标

---
> **需要实现详情？** 查看 [P8_advanced_systems_detailed.md](P8_advanced_systems_detailed.md)  
> **需要集成指南？** 查看 [P8_advanced_systems_integration.md](P8_advanced_systems_integration.md)