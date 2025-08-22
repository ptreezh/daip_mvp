# 基于KISS/YAGNI/SOLID的Wiki协作系统 - 极简实现方案

## 1. 核心设计原则

### KISS (Keep It Simple, Stupid)
- 只实现从用户意图到自动执行的最简路径
- 避免复杂的角色间交互和争议解决机制
- 用户只需表达意图，其余全部自动化

### YAGNI (You Aren't Gonna Need It)
- 不实现当前不需要的复杂功能
- 专注于核心的自动化协作流程
- 推迟实现多轮讨论、复杂规则等高级功能

### SOLID
- 单一职责：每个组件只负责一个核心功能
- 开闭原则：通过插件化支持扩展
- 依赖倒置：依赖于抽象接口而非具体实现

## 2. 简化后的系统架构

```
用户意图 -> 智能助手优化 -> 自动发起协作 -> 角色参与 -> 智能助手汇总 -> 自动执行
   ↑            ↓              ↓              ↓              ↓              ↓
  CLI      IntegratedLLM    ChatRoom    RoleManager    IntegratedLLM    WikiService
```

## 3. 极简实现方案

### 3.1 用户交互层 (极简)
```bash
# 用户只需表达意图
wiki collaborate "更新机器学习词条，添加最新的大语言模型进展"
```

### 3.2 智能助手优化层 (简化)
```python
class SimpleIntentOptimizer:
    """极简意图优化器"""
    
    def optimize(self, user_input: str) -> dict:
        """优化用户意图到协作任务参数"""
        # 简单的关键词提取和意图识别
        topic = self._extract_topic(user_input)
        task_type = self._determine_task_type(user_input)
        
        return {
            "topic": topic,
            "task_type": task_type,
            "optimized_intent": f"协作更新'{topic}'词条"
        }
```

### 3.3 自动任务发起层 (自动化)
```python
class SimpleCollaborationCoordinator:
    """极简协作协调器"""
    
    def __init__(self, chat_coordinator, llm_manager, wiki_service):
        self.chat_coordinator = chat_coordinator
        self.llm_manager = llm_manager
        self.wiki_service = wiki_service
    
    async def initiate_collaboration(self, optimized_intent: dict) -> str:
        """自动发起协作任务"""
        # 1. 创建聊天室
        room_id = self.chat_coordinator.create_chat_room(
            topic=optimized_intent["topic"],
            room_name=f"协作更新:{optimized_intent['topic']}",
            auto_recommend_roles=True
        )
        
        # 2. 自动启动会话
        session_id = self.chat_coordinator.start_session(room_id)
        
        # 3. 返回任务ID
        return f"collab_{room_id}"
```

### 3.4 角色参与层 (简化)
```python
class SimpleRoleCoordinator:
    """极简角色协调器"""
    
    async def coordinate_roles(self, room_id: str, task_context: str) -> List[dict]:
        """协调角色参与协作"""
        # 系统自动指派相关角色
        roles = self._assign_relevant_roles(task_context)
        
        # 收集角色反馈（并发执行）
        feedbacks = await self._collect_role_feedbacks(roles, task_context)
        
        return feedbacks
    
    async def _collect_role_feedbacks(self, roles: List[str], context: str) -> List[dict]:
        """并发收集角色反馈"""
        tasks = []
        for role_id in roles:
            task = self.llm_manager.call_llm_for_role(
                role_id=role_id,
                user_input=context,
                task_context="Wiki词条更新协作"
            )
            tasks.append(task)
        
        # 等待所有角色反馈
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        feedbacks = []
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                feedbacks.append({
                    "role_id": roles[i],
                    "role_name": result.get("role_name", roles[i]),
                    "feedback": result.get("response", ""),
                    "timestamp": datetime.now().isoformat()
                })
        
        return feedbacks
```

### 3.5 智能汇总层 (简化)
```python
class SimpleConsensusEngine:
    """极简共识引擎"""
    
    async def generate_consensus(self, feedbacks: List[dict], topic: str) -> str:
        """生成共识内容"""
        # 简单的文本合并策略
        if not feedbacks:
            return f"# {topic}\n\n暂无内容贡献。"
        
        # 合并所有角色的反馈
        content_parts = [f"# {topic}\n"]
        
        for feedback in feedbacks:
            content_parts.append(f"## {feedback['role_name']}的建议\n")
            content_parts.append(f"{feedback['feedback']}\n")
        
        return "\n".join(content_parts)
```

### 3.6 自动执行层 (简化)
```python
class SimpleExecutor:
    """极简执行器"""
    
    def __init__(self, wiki_service):
        self.wiki_service = wiki_service
    
    async def execute_update(self, topic: str, content: str) -> bool:
        """执行内容更新"""
        try:
            # 调用WikiService更新内容
            entry = self.wiki_service.create_entry(
                entry_name=topic,
                content=content,
                author_role="智能助手",
                tags=["自动生成", "协作更新"],
                category="自动创建"
            )
            
            return entry is not None
        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            return False
```

## 4. 完整工作流程

### 4.1 用户发起
```bash
wiki collaborate "更新机器学习词条，添加最新的大语言模型进展"
```

### 4.2 系统处理
1. **意图优化**：
   - 输入："更新机器学习词条，添加最新的大语言模型进展"
   - 输出：{"topic": "机器学习", "task_type": "update", "optimized_intent": "协作更新'机器学习'词条"}

2. **自动发起**：
   - 创建聊天室"协作更新:机器学习"
   - 自动推荐并指派相关角色（AI研究员、NLP专家等）
   - 启动会话

3. **角色参与**：
   - 并发调用相关角色的LLM
   - 收集各角色的专业反馈

4. **共识生成**：
   - 简单合并各角色反馈
   - 生成统一的内容

5. **自动执行**：
   - 调用WikiService创建/更新词条
   - 记录执行结果

### 4.3 用户反馈
```bash
✅ 维基词条"机器学习"已成功更新！
   内容由以下角色协作生成：
   - AI研究员: 提供了机器学习基础理论更新
   - NLP专家: 贡献了大语言模型最新进展
```

## 5. 实施计划

### 第1天：核心组件实现
- [ ] 实现SimpleIntentOptimizer（1小时）
- [ ] 实现SimpleCollaborationCoordinator（2小时）
- [ ] 实现SimpleRoleCoordinator（2小时）

### 第2天：共识与执行实现
- [ ] 实现SimpleConsensusEngine（1小时）
- [ ] 实现SimpleExecutor（1小时）
- [ ] 集成所有组件（2小时）

### 第3天：CLI命令与测试
- [ ] 实现wiki collaborate CLI命令（1小时）
- [ ] 编写测试用例（2小时）
- [ ] 系统测试与调试（1小时）

## 6. 验收标准

### 功能验收
- [ ] 用户能通过一句话发起协作任务
- [ ] 系统能自动指派相关角色
- [ ] 角色能并发提供专业反馈
- [ ] 系统能自动生成并执行更新

### 性能验收
- [ ] 从发起任务到完成更新 < 1分钟
- [ ] 角色反馈并发处理时间 < 30秒
- [ ] 系统可用性 > 99.9%

### 用户体验验收
- [ ] 用户只需一句话即可完成复杂任务
- [ ] 系统反馈清晰明了
- [ ] 用户满意度 > 4.5/5.0

## 7. KISS/YAGNI/SOLID原则验证

### KISS验证
- [ ] 用户交互：一句话完成
- [ ] 系统逻辑：线性流程，无复杂分支
- [ ] 代码实现：每个方法职责单一

### YAGNI验证
- [ ] 不实现角色间讨论机制
- [ ] 不实现复杂争议解决
- [ ] 不实现多轮协作
- [ ] 只实现必需的功能

### SOLID验证
- [ ] 单一职责：每个类只负责一个核心功能
- [ ] 开闭原则：通过接口设计支持扩展
- [ ] 依赖倒置：依赖于抽象接口
- [ ] 接口隔离：每个组件只依赖必需的接口