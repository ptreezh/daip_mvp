# P5 代理引擎 - 集成指南 (P5 Agent Engine - Integration Guide)

## 🔗 与其他模块的集成

### 与P3模型提供者集成
```python
# 在AgentExecutor中使用模型提供者
class AgentExecutor:
    def __init__(self, model_provider: IModelProvider):
        self.model_provider = model_provider

# 调用模型生成响应
response = await self.model_provider.generate(prompt, params)
```

### 与P4角色工具管理集成
```python
# 通过ToolManager安全执行工具
class AgentExecutor:
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager

# 执行工具调用
result = await self.tool_manager.execute_tool(name, args, session_context)
```

### 与P0核心接口集成
- 使用P0定义的`AgentEvent`事件流
- 符合P0定义的接口契约
- 使用P0定义的异常体系

## 🔄 事件流集成

### 事件生成
```python
async def chat_run(self, initial_goal: str) -> AsyncGenerator[AgentEvent, None]:
    yield ThoughtEvent(content="Processing initial goal")
    yield ToolCallEvent(tool_name="search", args={"query": initial_goal})
    # ... 更多事件
```

### UI层事件消费
```python
# TUI或GUI消费事件流
async for event in agent_executor.chat_run(goal):
    if isinstance(event, ThoughtEvent):
        display_thought(event.content)
    elif isinstance(event, ToolCallEvent):
        display_tool_call(event.tool_name, event.args)
    # ... 处理其他事件类型
```

## 🔌 使用示例

### 基本集成
```python
from daip_live.p5_agent_engine.executor import AgentExecutor
from daip_live.p3_model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.tool_manager import ToolManager

# 初始化组件
model_provider = LiteLLMProvider(config)
tool_manager = ToolManager()
agent_executor = AgentExecutor(model_provider, tool_manager)

# 运行代理
async for event in agent_executor.chat_run("Help me plan a project"):
    process_event(event)
```

### 高级集成（工作流）
```python
# 与P5工作流编排集成
from daip_live.p5_agent_engine.workflow_executor import WorkflowExecutor

workflow_executor = WorkflowExecutor(agent_executor)
workflow_result = await workflow_executor.execute_workflow(workflow_definition)
```

## ⚡ 性能考虑
- **异步处理**: 使用异步方法避免阻塞
- **事件缓冲**: 在高频率事件场景下使用缓冲
- **状态监控**: 定期调用`get_status()`监控性能

## 🐛 常见集成问题
- **循环导入**: 使用依赖注入避免循环导入
- **事件处理延迟**: 确保UI事件处理不过于复杂
- **状态同步**: 在多组件间保持状态一致

---
> **需要API详情？** 查看 [P5_agent_engine_api.md](P5_agent_engine_api.md)  
> **需要实现详情？** 查看 [P5_agent_engine_detailed.md](P5_agent_engine_detailed.md)