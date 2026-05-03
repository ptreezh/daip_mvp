# P8.1 辩论系统 - 集成指南 (P8.1 Debate System - Integration Guide)

## 🔗 与其他模块的集成

### 与P4角色管理集成
```python
# 辩论系统使用P4的角色管理功能
from daip_live.p4_role_manager_tools.role_manager import RoleManager

class DebateManager:
    def __init__(self, role_manager: RoleManager, model_provider: IModelProvider):
        self.role_manager = role_manager
        self.model_provider = model_provider
    
    async def prepare_debate_participants(self, role_names: List[str]):
        participants = []
        for role_name in role_names:
            # 从P4获取角色配置
            role = self.role_manager.get_role_by_name(role_name)
            if role:
                participants.append({
                    "name": role.name,
                    "system_prompt": role.system_prompt,
                    "model_config": role.model_config
                })
        return participants
```

### 与P3模型提供者集成
```python
# 辩论系统调用不同模型进行角色扮演
class DebateManager:
    async def get_participant_response(self, participant: Dict, context: str):
        # 根据角色配置选择适当的模型
        model_config = participant["model_config"]
        prompt = f"{participant['system_prompt']}\n\n上下文: {context}\n\n请给出您的观点:"
        
        # 使用P3模型提供者生成响应
        async for chunk in self.model_provider.generate(prompt, model_config):
            yield chunk
```

## 🔄 辩论执行流程

### 完整辩论流程
```python
# 标准辩论执行模式
async def execute_complete_debate(debate_manager: DebateManager, topic: str, roles: List[str], rounds: int):
    # 1. 准备辩论参与者
    participants = await debate_manager.prepare_debate_participants(roles)
    
    # 2. 启动辩论事件流
    debate_events = debate_manager.run_debate(topic, roles, rounds)
    
    # 3. 处理辩论事件
    async for event in debate_events:
        if isinstance(event, DebateStartEvent):
            print(f"辩论开始: {event.topic}")
            yield event
        elif isinstance(event, DebateRoundStartEvent):
            print(f"第 {event.round_number} 轮开始")
            yield event
        elif isinstance(event, DebateTurnCompleteEvent):
            print(f"{event.participant}: {event.content_preview}")
            yield event
        elif isinstance(event, DebateCompleteEvent):
            print(f"辩论完成，摘要: {event.summary}")
            yield event
```

## 🔌 使用示例

### 基础辩论功能
```python
from daip_live.p8_debate_system.manager import DebateManager

# 初始化辩论管理器
debate_manager = container.debate_manager()

# 运行辩论
async for event in debate_manager.run_debate(
    topic="人工智能对就业市场的影响",
    roles=["pro_arguer", "con_arguer"],
    rounds=3
):
    # 根据事件类型处理
    if event.type == "turn_complete":
        print(f"{event.participant}: {event.content}")
    elif event.type == "debate_complete":
        print(f"辩论摘要: {event.summary}")
```

### 高级辩论配置
```python
# 使用自定义角色进行辩论
async def advanced_debate_example():
    # 定义自定义角色
    custom_roles = ["economist", "laborer", "policymaker"]
    
    # 获取角色模型摘要
    model_summary = debate_manager.get_debate_model_summary(custom_roles)
    print(f"模型配置: {model_summary}")
    
    # 运行多方辩论
    async for event in debate_manager.run_debate(
        topic="最低工资政策的经济影响",
        roles=custom_roles,
        rounds=5
    ):
        process_debate_event(event)
```

## ⚡ 性能考虑
- **模型选择**: 根据角色需求选择合适的模型
- **并行处理**: 可选的并行角色处理
- **缓存策略**: 缓存辩论配置和角色信息

## 🐛 常见集成问题
- **角色不可用**: 验证角色配置是否存在
- **模型不兼容**: 确保模型支持所需的参数
- **事件处理**: 正确处理所有辩论事件类型

---
> **需要API详情？** 查看 [P8_1_debate_system_api.md](P8_1_debate_system_api.md)  
> **需要实现详情？** 查看 [P8_1_debate_system_detailed.md](P8_1_debate_system_detailed.md)