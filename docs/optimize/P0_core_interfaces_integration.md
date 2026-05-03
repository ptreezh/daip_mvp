# P0 核心接口与类型 - 集成指南 (P0 Core Interfaces & Types - Integration Guide)

## 🔗 与其他模块的集成

### 与P5代理引擎集成
```python
# P5使用P0定义的事件流
from daip_live.core.models import AgentEvent, ThoughtEvent, ToolCallEvent

class AgentExecutor:
    async def chat_run(self, initial_goal: str) -> AsyncGenerator[AgentEvent, None]:
        yield ThoughtEvent(content="Processing initial goal")
        # ... 更多事件
```

### 与P3模型提供者集成
```python
# P3实现P0定义的接口
from daip_live.core.interfaces import IModelProvider
from daip_live.core.models import AgentStatus

class LiteLLMProvider(IModelProvider):
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        # 实现生成方法
        pass
```

### 与P4工具管理集成
```python
# P4实现P0定义的工具接口
from daip_live.core.interfaces import ITool

class FileOperationTool(ITool):
    def execute(self, **kwargs) -> Any:
        # 实现工具执行
        pass
```

## 🔄 事件流集成

### 事件消费模式
```python
# TUI消费P0定义的事件流
from daip_live.core.models import AgentEvent, AgentStatus

async def consume_event_stream(agent_executor):
    async for event in agent_executor.chat_run("user goal"):
        # 根据事件类型处理
        if event.type == "thought":
            handle_thought_event(event.content)
        elif event.type == "tool_call":
            handle_tool_call_event(event.tool_name, event.args)
```

### 状态监控集成
```python
# 实时状态监控
status: AgentStatus = agent_executor.get_status()
print(f"Current state: {status.state}, Model: {status.model_name}")
```

## 🔌 使用示例

### 模型提供者实现
```python
from daip_live.core.interfaces import IModelProvider
from daip_live.core.models import AgentStatus

class CustomModelProvider(IModelProvider):
    async def generate(self, prompt: str, params: Dict):
        # 实现生成逻辑
        yield "response chunk"
    
    def embed(self, text: str):
        # 实现嵌入逻辑
        return [0.1, 0.2, 0.3]
```

### 异常处理模式
```python
from daip_live.core.exceptions import DAIPError, ToolError

try:
    result = await tool_manager.execute_tool("file_operation", {"path": "/tmp"})
except ToolError as e:
    # 处理工具错误
    print(f"Tool execution failed: {e}")
except DAIPError as e:
    # 处理通用DAIP错误
    print(f"DAIP operation failed: {e}")
```

## ⚡ 性能考虑
- **事件序列化**: 使用Pydantic模型确保高效序列化
- **类型安全**: 利用类型提示提高IDE支持和错误检测
- **内存优化**: 事件流模式避免将所有数据加载到内存

## 🐛 常见集成问题
- **接口实现不完整**: 确保实现接口的所有抽象方法
- **模型验证失败**: Pydantic模型字段类型不匹配
- **事件处理延迟**: 事件消费者处理逻辑过于复杂

---
> **需要API详情？** 查看 [P0_core_interfaces_api.md](P0_core_interfaces_api.md)  
> **需要实现详情？** 查看 [P0_core_interfaces_detailed.md](P0_core_interfaces_detailed.md)