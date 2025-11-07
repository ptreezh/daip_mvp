# 辩论系统优化设计规范

## 📋 文档信息
- **文档版本**: v1.0
- **创建日期**: 2025-09-16
- **功能名称**: 辩论系统架构优化
- **开发方式**: TDD驱动开发
- **优先级**: 高

## 🎯 优化目标

### 核心问题
当前辩论系统存在以下关键问题：
1. **会话管理混乱**: 所有角色共享单一Session实例
2. **Ollama实例冗余**: 每个模型配置创建独立Provider实例
3. **记忆系统不完善**: 缺乏角色独立的上下文管理
4. **回合非独立**: 所有轮次在同一会话中连续进行

### 优化目标
1. **分时复用**: 实现单一Ollama实例的模型切换
2. **独立会话**: 为每个角色建立独立会话
3. **分层记忆**: 实现角色独立的记忆系统
4. **回合独立**: 每轮辩论作为独立会话处理

## 📐 技术设计规范

### 1. Ollama实例管理器设计

```python
class OllamaInstanceManager:
    """Ollama实例管理器 - 确保分时复用"""

    def __init__(self):
        self._current_model = None
        self._lock = asyncio.Lock()
        self._provider = None

    async def generate_with_model(self, model_name: str, prompt: str, **kwargs):
        """分时复用单一Ollama实例生成回复"""
        async with self._lock:
            # 模型切换（如果需要）
            if self._current_model != model_name:
                await self._switch_model(model_name)

            # 生成回复
            return await self._generate(prompt, **kwargs)

    async def _switch_model(self, model_name: str):
        """切换当前模型"""
        # 实现模型切换逻辑
        pass
```

**设计要点**:
- 单一实例管理，避免资源竞争
- 异步锁确保并发安全
- 模型状态缓存优化性能

### 2. 角色独立会话管理

```python
class RoleDebateSession:
    """角色独立辩论会话"""

    def __init__(self, role_name: str, role_persona: str, model_config: ModelConfig):
        self.role_name = role_name
        self.role_persona = role_persona
        self.model_config = model_config
        self.personal_history = []     # 角色个人历史
        self.stance_memory = {}        # 立场记忆
        self.argument_tracker = {}     # 论点追踪
        self.round_memories = {}       # 轮次记忆

class EnhancedDebateManager:
    """增强辩论管理器"""

    def __init__(self, ...):
        self.ollama_manager = OllamaInstanceManager()
        self.role_sessions = {}        # 角色独立会话
        self.shared_debate_context = {} # 共享辩论上下文
```

**设计要点**:
- 每个角色拥有独立会话实例
- 个人历史与共享上下文分离
- 立场记忆和论点追踪

### 3. 分层记忆系统

```python
class LayeredMemorySystem:
    """分层记忆系统"""

    def __init__(self):
        self.shared_factual_history = []   # 共享事实历史
        self.role_personal_memories = {}   # 角色个人记忆
        self.round_summaries = {}          # 轮次摘要
        self.stance_evolution = {}         # 立场演化

    def get_role_context(self, role_name: str, current_round: int):
        """获取角色特定上下文"""
        # 组合共享历史和个人记忆
        pass

    def update_role_memory(self, role_name: str, content: str, round_num: int):
        """更新角色记忆"""
        # 更新个人记忆和立场
        pass
```

**设计要点**:
- 共享事实历史与个人观点分离
- 轮次摘要防止上下文过长
- 立场演化追踪角色一致性

### 4. 上下文感知提示词构建

```python
def build_context_aware_prompt(self, role_name: str, current_round: int, topic: str):
    """构建上下文感知的提示词"""

    role_session = self.role_sessions[role_name]

    prompt = f"""Debate Topic: {topic}
Current Round: {current_round}

Your Role: {role_session.role_persona}
Your Assigned Model: {role_session.model_config.model_name}

Your Previous Arguments:
{self._format_role_arguments(role_session.personal_history)}

Your Core Stance: {role_session.stance_memory.get('core_stance', 'Developing...')}

Opponent Arguments Summary:
{self._format_opponent_summary(role_session.opponent_summary)}

What is your argument for this round? Please maintain your role consistency."""

    return prompt
```

**设计要点**:
- 角色特定上下文
- 历史论点追踪
- 立场一致性要求

## 🧪 测试规范

### 1. 回归测试要求
- **现有功能**: 所有现有辩论功能必须正常工作
- **API兼容性**: 保持现有API接口不变
- **事件系统**: 现有事件流保持兼容
- **数据存储**: 现有数据库结构保持兼容

### 2. 新功能测试
- **分时复用测试**: 验证单一Ollama实例正确切换模型
- **独立会话测试**: 验证角色会话独立性
- **记忆系统测试**: 验证分层记忆正确性
- **性能测试**: 验证优化后性能提升

### 3. 边界条件测试
- **并发安全测试**: 多个角色同时调用的安全性
- **模型切换测试**: 频繁模型切换的稳定性
- **内存管理测试**: 大量轮次下的内存使用
- **错误恢复测试**: 模型调用失败的处理

## 📊 性能指标

### 1. 资源使用
- **Ollama实例**: 从N个减少到1个
- **内存使用**: 减少30-50%
- **并发能力**: 提升200%

### 2. 响应时间
- **模型切换**: <100ms
- **回复生成**: <2000ms
- **状态更新**: <50ms

### 3. 准确性指标
- **角色一致性**: >90%
- **立场保持**: >85%
- **上下文相关**: >95%

## 🔄 实施计划

### Phase 1: TDD开发 (当前阶段)
- [x] 创建设计规范文档
- [ ] 编写回归测试用例
- [ ] 编写新功能测试用例
- [ ] 运行测试验证失败
- [ ] 实现功能使测试通过
- [ ] 重构优化代码

### Phase 2: 核心功能实现
- [ ] 实现OllamaInstanceManager
- [ ] 实现RoleDebateSession
- [ ] 实现LayeredMemorySystem
- [ ] 集成到现有系统

### Phase 3: 测试验证
- [ ] 运行所有回归测试
- [ ] 运行新功能测试
- [ ] 性能基准测试
- [ ] 手动功能测试

### Phase 4: 文档更新
- [ ] 更新技术文档
- [ ] 更新用户指南
- [ ] 更新API文档
- [ ] 更新部署指南

## ✅ 验收标准

### 1. 功能验收
- [ ] 单一Ollama实例分时复用
- [ ] 角色独立会话管理
- [ ] 分层记忆系统工作正常
- [ ] 上下文感知提示词生效

### 2. 性能验收
- [ ] Ollama实例数量减少到1个
- [ ] 内存使用减少30%以上
- [ ] 响应时间满足要求

### 3. 兼容性验收
- [ ] 现有API接口保持不变
- [ ] 现有数据库结构兼容
- [ ] 现有事件流兼容

### 4. 测试验收
- [ ] 所有回归测试通过
- [ ] 新功能测试通过
- [ ] 性能测试达标
- [ ] 手动测试验证

---

**文档状态**: ✅ 设计完成
**开发方式**: TDD驱动
**下一步**: 编写回归测试用例
**预计完成时间**: 2025-09-16