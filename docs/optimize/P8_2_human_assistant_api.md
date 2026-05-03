# P8.2 人类助手系统 - API参考 (P8.2 Human Assistant System - API Reference)

## 📋 核心类与方法

### PersonalAssistant
```python
class PersonalAssistant:
    async def handle_request(self, user_request: str) -> AsyncGenerator[AssistantEvent, None]:
        """处理用户请求"""
    
    def decompose_task(self, complex_task: str) -> List[SubTask]:
        """任务分解"""
    
    async def execute_workflow(self, workflow_definition: WorkflowDefinition) -> WorkflowResult:
        """执行工作流"""
    
    def get_capabilities(self) -> List[str]:
        """获取助手能力列表"""
    
    async def learn_from_interaction(self, interaction: InteractionLog) -> LearningResult:
        """从交互中学习"""
```

## 🧩 事件类型

### 助手事件
```python
from pydantic import BaseModel
from typing import Literal, List, Optional, Dict, Any

class AssistantStartEvent(BaseModel):
    type: Literal["assistant_start"]
    request: str
    timestamp: datetime

class TaskDecompositionEvent(BaseModel):
    type: Literal["task_decomposition"]
    original_task: str
    subtasks: List[str]
    timestamp: datetime

class ToolUseEvent(BaseModel):
    type: Literal["tool_use"]
    tool_name: str
    tool_args: Dict[str, Any]
    result: str
    timestamp: datetime

class InformationRetrievalEvent(BaseModel):
    type: Literal["information_retrieval"]
    query: str
    sources: List[str]
    timestamp: datetime

class ResponseGenerationEvent(BaseModel):
    type: Literal["response_generation"]
    draft_response: str
    timestamp: datetime

class AssistantCompleteEvent(BaseModel):
    type: Literal["assistant_complete"]
    final_response: str
    execution_time: float
    tools_used: List[str]
    timestamp: datetime

AssistantEvent = Union[
    AssistantStartEvent, TaskDecompositionEvent, ToolUseEvent,
    InformationRetrievalEvent, ResponseGenerationEvent, AssistantCompleteEvent
]
```

## 🔧 数据模型

### 任务和工作流模型
```python
class SubTask(BaseModel):
    id: str
    description: str
    dependencies: List[str]
    required_tools: List[str]
    priority: int = 1

class WorkflowDefinition(BaseModel):
    name: str
    description: str
    tasks: List[SubTask]
    context: Dict[str, Any]

class WorkflowResult(BaseModel):
    success: bool
    results: Dict[str, Any]
    execution_time: float
    errors: List[str]
```

### 学习模型
```python
class InteractionLog(BaseModel):
    user_input: str
    assistant_response: str
    tools_used: List[str]
    context: Dict[str, Any]
    outcome: Literal["success", "partial_success", "failure"]

class LearningResult(BaseModel):
    learned_patterns: List[str]
    improvement_suggestions: List[str]
    knowledge_updates: Dict[str, Any]
```

## 🔌 集成接口

### 依赖的外部组件
- `P5 AgentExecutor`: 任务执行引擎
- `P2 KnowledgeManager`: 知识检索
- `P4 ToolManager`: 工具执行
- `P3 ModelProvider`: AI模型调用

### 交互模式
- **事件流**: `AsyncGenerator[AssistantEvent, None]`
- **上下文感知**: 基于会话历史的智能响应
- **任务自动化**: 自动化复杂工作流执行

---
> **需要实现详情？** 查看 [P8_2_human_assistant_detailed.md](P8_2_human_assistant_detailed.md)  
> **需要集成指南？** 查看 [P8_2_human_assistant_integration.md](P8_2_human_assistant_integration.md)