# P5 代理引擎 - API参考 (P5 Agent Engine - API Reference)

## 📋 核心类与方法

### AgentExecutor
```python
class AgentExecutor:
    def get_status(self) -> AgentStatus:
        """获取代理执行器的实时状态"""
    
    async def run(self, goal: str, ...) -> AsyncGenerator[AgentEvent, None]:
        """执行任务导向模式"""
    
    async def chat_run(self, initial_goal: str) -> AsyncGenerator[AgentEvent, None]:
        """执行对话模式"""
```

## 🧩 数据模型

### AgentStatus
```python
class AgentStatus(BaseModel):
    state: AgentState          # 当前状态
    model_name: str           # 使用的模型名称
    tokens_used: int          # 已使用token数
    tokens_total: int         # 总token数
```

### AgentState (枚举)
```python
class AgentState(Enum):
    INIT = "init"                    # 初始化
    RUNNING = "running"              # 运行中
    COMPLETED = "completed"          # 已完成
    FAILED = "failed"                # 失败
    IDLE = "idle"                    # 空闲
    OBSERVING = "observing"          # 观察中
    THINKING = "thinking"            # 思考中
    EVALUATING = "evaluating"        # 评估中
    REFLECTING = "reflecting"        # 反思中
    EXECUTING_TOOL = "executing_tool" # 执行工具
    RESPONDING = "responding"        # 响应中
    FINALIZING = "finalizing"        # 完成中
    ERROR = "error"                  # 错误
    EXPLORING = "exploring"          # 探索中
    SYNTHESIZING = "synthesizing"    # 综合中
```

### AgentEvent 及其子类型
```python
# 抽象基类
class AgentEvent(BaseModel):
    type: str

# 具体事件类型
class ThoughtEvent(AgentEvent):
    type: Literal["thought"]
    content: str

class ToolCallEvent(AgentEvent):
    type: Literal["tool_call"]
    tool_name: str
    args: Dict[str, Any]

class ToolOutputEvent(AgentEvent):
    type: Literal["tool_output"]
    tool_name: str
    status: Literal["success", "error"]
    output: str

class FinalResponseEvent(AgentEvent):
    type: Literal["final_response"]
    content: str

class ErrorEvent(AgentEvent):
    type: Literal["error"]
    message: str

class PermissionRequestEvent(AgentEvent):
    type: Literal["permission_request"]
    tool_name: str
    args: Dict[str, Any]

class ResponseChunkEvent(AgentEvent):
    type: Literal["response_chunk"]
    delta: str
```

## 🔧 依赖接口

### 依赖的外部服务
- `IModelProvider`: 模型提供者接口 (来自P3)
- `IKnowledgeManager`: 知识管理器接口 (来自P2)
- `ITool`: 工具接口 (来自P4)

## 📡 事件流处理
- **生成器模式**: 使用 `AsyncGenerator[AgentEvent, None]` 实现事件流
- **响应式**: 实时产生事件供UI层消费
- **类型安全**: 使用Pydantic模型确保事件结构一致性

---
> **需要实现详情？** 查看 [P5_agent_engine_detailed.md](P5_agent_engine_detailed.md)  
> **需要集成指南？** 查看 [P5_agent_engine_integration.md](P5_agent_engine_integration.md)