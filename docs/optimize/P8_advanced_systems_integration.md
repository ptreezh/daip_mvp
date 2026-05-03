# P8 高级功能系统 - 集成指南 (P8 Advanced Systems - Integration Guide)

## 🔗 与其他模块的集成

### 与P4角色管理集成 (辩论系统)
```python
# 辩论系统使用P4的角色管理功能
from daip_live.p4_role_manager_tools.role_manager import RoleManager

class DebateManager:
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager
    
    async def prepare_debate_participants(self, role_names: List[str]):
        # 加载辩论角色
        participants = []
        for role_name in role_names:
            role = self.role_manager.get_role_by_name(role_name)
            participants.append(role)
        return participants
```

### 与P5代理引擎集成 (人类助手)
```python
# 人类助手使用P5代理引擎执行任务
from daip_live.p5_agent_engine.executor import AgentExecutor

class PersonalAssistant:
    def __init__(self, agent_executor: AgentExecutor):
        self.agent_executor = agent_executor
    
    async def execute_user_request(self, request: str):
        # 通过代理引擎执行用户请求
        async for event in self.agent_executor.chat_run(request):
            yield event
```

### 与P2知识管理集成 (维基系统)
```python
# 维基系统与知识管理系统集成
from daip_live.p2_knowledge_manager.manager import KnowledgeManager

class WikiManager:
    def __init__(self, knowledge_manager: KnowledgeManager):
        self.knowledge_manager = knowledge_manager
    
    async def index_wiki_page(self, page: WikiPage):
        # 将维基页面添加到知识库
        await self.knowledge_manager.add_document(
            content=page.content,
            metadata={"title": page.title, "tags": page.tags}
        )
```

## 🔄 高级功能模式

### 辩论系统工作流
```python
# 完整辩论工作流
async def complete_debate_workflow(debate_manager: DebateManager, topic: str, roles: List[str]):
    # 1. 启动辩论
    debate_events = debate_manager.run_debate(topic, roles, rounds=3)
    
    # 2. 处理辩论事件
    async for event in debate_events:
        if isinstance(event, DebateStartEvent):
            print(f"辩论开始: {event.topic}")
        elif isinstance(event, DebateTurnCompleteEvent):
            print(f"{event.participant}: {event.content_preview}")
        elif isinstance(event, DebateCompleteEvent):
            print(f"辩论完成: {event.summary}")
```

### 助手任务分解
```python
# 任务分解示例
async def task_decomposition_example(assistant: PersonalAssistant, complex_task: str):
    # 分解复杂任务
    subtasks = assistant.decompose_task(complex_task)
    
    # 顺序执行子任务
    results = []
    for subtask in subtasks:
        result = await assistant.execute_subtask(subtask)
        results.append(result)
    
    # 综合结果
    final_result = assistant.synthesize_results(results)
    return final_result
```

## 🔌 使用示例

### 辩论系统使用
```python
from daip_live.p8_debate_system.manager import DebateManager

# 启动辩论
debate_manager = container.debate_manager()

# 运行辩论
async for event in debate_manager.run_debate(
    topic="人工智能对未来工作的影响",
    roles=["pro_arguer", "con_arguer", "neutral_observer"],
    rounds=3
):
    process_debate_event(event)
```

### 维基系统使用
```python
from daip_live.p8_wiki_system.manager import WikiManager

# 初始化维基管理器
wiki_manager = container.wiki_manager()

# 创建页面
page = await wiki_manager.create_page(
    title="Python编程基础",
    content="Python是一种高级编程语言...",
    author="user123"
)

# 搜索页面
results = await wiki_manager.search_pages("Python")
```

## ⚡ 性能考虑
- **并发控制**: 管理多用户同时操作
- **缓存策略**: 缓存频繁访问的内容
- **异步处理**: 使用异步操作提高响应速度

## 🐛 常见集成问题
- **角色配置**: 确保P4角色配置正确
- **事件处理**: 正确处理不同类型的事件
- **数据一致性**: 维护跨系统数据一致性

---
> **需要API详情？** 查看 [P8_advanced_systems_api.md](P8_advanced_systems_api.md)  
> **需要实现详情？** 查看 [P8_advanced_systems_detailed.md](P8_advanced_systems_detailed.md)