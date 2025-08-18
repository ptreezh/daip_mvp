# Unified Command-Line Interface - 阶段 2: 智能体助手 - 修订版详细设计规范

**文档状态:** 修订版详细设计规范
**版本:** 1.1
**日期:** 2025-08-18
**焦点:** CLI智能助手的详细设计规范，遵循TDD原则和kiro SPECS规范，根据用户故事反馈进行修订。

## 1. 总体架构设计

基于工作流驱动的智能个人助手将采用分层架构设计，主要包括以下组件：

1. **CLI层**：处理用户输入和输出显示，支持精简指令
2. **应用服务层**：PersonalAssistantService作为核心协调器，增加会话管理功能
3. **领域服务层**：包括入口选择、工作流编排、用户干预、共识跟踪等服务
4. **用例层**：SecretariatUseCase和ForumUseCase处理具体业务逻辑
5. **领域层**：包含实体、值对象和聚合
6. **基础设施层**：与底层服务和外部系统交互

## 2. 核心组件详细设计

### 2.1 PersonalAssistantService (应用服务层)

#### 2.1.1 职责
作为统一AI助手服务，协调不同入口类型并提供智能用户支持：
- 初始化服务和默认用户
- 创建和管理会话，支持默认会话和历史会话管理
- 处理用户输入并路由到相应入口
- 提供会话状态、任务状态和透明度数据
- 支持入口切换和建议
- 提供系统健康状态和用户统计信息

#### 2.1.2 接口设计
```python
class PersonalAssistantService:
    async def initialize(self) -> None
    async def create_session(self, user_id: str, context: dict[str, Any] = None) -> dict[str, Any]
    async def process_user_input(self, session_id: str, user_input: dict[str, Any]) -> dict[str, Any]
    async def get_session_status(self, session_id: str) -> dict[str, Any]
    async def get_task_status(self, task_id: str) -> dict[str, Any]
    async def get_transparency_data(self, session_id: str) -> dict[str, Any]
    async def switch_entrance(self, session_id: str, target_entrance: str) -> dict[str, Any]
    async def get_entrance_suggestions(self, session_id: str) -> list[dict[str, Any]]
    async def get_system_health(self) -> dict[str, Any]
    async def cleanup_expired_sessions(self, timeout_hours: int = 24) -> int
    async def get_user_statistics(self, user_id: str) -> dict[str, Any]
    # 新增会话管理接口
    async def get_recent_session(self, user_id: str) -> str
    async def get_session_list(self, user_id: str) -> list[dict[str, Any]]
    async def set_default_session(self, user_id: str, session_id: str) -> None
    async def generate_session_topic(self, user_input: str) -> str
```

### 2.2 EntranceSelectorService (领域服务层)

#### 2.2.1 职责
智能选择最适合的入口类型（Secretariat/Forum）：
- 分析用户偏好和上下文特征
- 预测最优入口类型
- 记录选择历史和学习用户反馈

#### 2.2.2 接口设计
```python
class EntranceSelectorService:
    async def select_entrance(self, user: User, context: dict[str, Any]) -> EntranceType
    def learn_from_feedback(self, user_id: str, entrance: EntranceType, satisfaction: float) -> None
    def get_user_preferences(self, user_id: str) -> dict[str, Any]
```

### 2.3 WorkflowOrchestratorService (领域服务层)

#### 2.3.1 职责
协调任务执行流程：
- 规划工作流
- 启动和执行工作流步骤
- 跟踪工作流进度
- 处理工作流完成和失败

#### 2.3.2 接口设计
```python
class WorkflowOrchestratorService:
    async def plan_workflow(self, intent: dict[str, Any]) -> dict[str, Any]
    async def start_workflow(self, workflow_id: str, workflow_plan: dict[str, Any]) -> bool
    async def execute_step(self, workflow_id: str, step_id: str) -> dict[str, Any]
    def get_workflow_progress(self, workflow_id: str) -> dict[str, Any]
    def complete_workflow(self, workflow_id: str) -> None
    def fail_workflow(self, workflow_id: str, error: str) -> None
```

### 2.4 UserInterventionService (领域服务层)

#### 2.4.1 职责
优化和集成用户输入：
- 优化用户输入内容
- 分析干预影响
- 生成集成建议
- 记录优化历史

#### 2.4.2 接口设计
```python
class UserInterventionService:
    async def optimize_input(self, raw_input: str, intent_type: str, context: dict[str, Any]) -> str
    async def integrate_intervention(self, debate_id: str, user_intervention: dict[str, Any]) -> dict[str, Any]
    def get_optimization_stats(self) -> dict[str, Any]
```

### 2.5 ConsensusTrackingService (领域服务层)

#### 2.5.1 职责
实时计算和跟踪共识水平：
- 计算共识水平
- 添加Agent观点和消息
- 提取关键论点
- 获取辩论摘要

#### 2.5.2 接口设计
```python
class ConsensusTrackingService:
    async def calculate_consensus(self, debate_id: str) -> ConsensusLevel
    async def add_agent_opinion(self, debate_id: str, agent_id: str, opinion: str, confidence: float) -> None
    async def add_message(self, debate_id: str, message: dict[str, Any]) -> None
    async def extract_key_arguments(self, debate_id: str) -> list[dict[str, Any]]
    def get_debate_summary(self, debate_id: str) -> dict[str, Any]
```

### 2.6 SecretariatUseCase (用例层)

#### 2.6.1 职责
处理效率型用户的快速任务执行：
- 创建会话
- 提交和执行任务
- 获取任务进度和结果
- 提供透明度数据

#### 2.6.2 接口设计
```python
class SecretariatUseCase(BaseUseCase):
    async def create_session(self, user: User, entrance_type: EntranceType) -> Session
    async def submit_task(self, session_id: str, task_request: dict[str, Any]) -> dict[str, Any]
    async def get_task_progress(self, task_id: str) -> dict[str, Any]
    async def get_task_result(self, task_id: str) -> dict[str, Any]
    async def get_transparency_data(self, task_id: str) -> dict[str, Any]
```

### 2.7 ForumUseCase (用例层)

#### 2.7.1 职责
处理参与型用户的交互式讨论：
- 创建论坛会话和辩论
- 启动辩论
- 处理用户干预
- 获取辩论上下文和消息
- 控制辩论流程

#### 2.7.2 接口设计
```python
class ForumUseCase(BaseUseCase):
    async def create_forum_session(self, user: User, session_config: dict[str, Any]) -> Session
    async def start_debate(self, session_id: str) -> dict[str, Any]
    async def handle_user_intervention(self, session_id: str, intervention_data: dict[str, Any]) -> dict[str, Any]
    async def get_debate_context(self, session_id: str) -> dict[str, Any]
    async def get_debate_messages(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]
    async def control_debate(self, session_id: str, action: str) -> dict[str, Any]
```

## 3. CLI层详细设计

### 3.1 CLI命令结构
```
daip-cli assistant chat <query>           # 启动助手对话
daip-cli assist intv --content <text>     # 用户干预 (精简指令)
daip-cli assist cons                      # 查看共识水平 (精简指令)
daip-cli assist disag                     # 查看分歧点 (精简指令)
daip-cli assist sess                      # 查看会话列表 (精简指令)
daip-cli assist session --id <session_id> # 选择会话 (精简指令)
daip-cli assist style --role <role> --prompt <prompt> # 设置角色风格
```

### 3.2 默认会话管理设计
1. 系统维护一个默认会话ID，存储在用户配置中
2. 当用户执行需要会话ID的命令时，如果未指定会话ID，则使用默认会话
3. 创建新会话时，自动将新会话设为默认会话
4. 用户可以通过命令手动设置默认会话

### 3.3 精简指令设计
1. 支持"assist"作为"assistant"的别名
2. 支持以下精简指令：
   - "intv" 代替 "intervene"
   - "cons" 代替 "consensus"
   - "disag" 代替 "disagreements"
   - "sess" 代替 "sessions"
3. 精简指令通过Typer的别名功能实现

## 4. 会话管理设计

### 4.1 会话数据结构扩展
在Session实体中增加以下字段：
- `topic`: 会话主题（自动生成）
- `is_default`: 是否为默认会话

### 4.2 会话主题生成
1. 使用专门的LLM调用生成会话主题
2. 基于用户初始输入提取关键信息
3. 生成简洁明了的主题描述
4. 主题长度控制在50个字符以内

### 4.3 会话持久化
1. 会话信息存储在本地文件系统中
2. 每个会话对应一个JSON文件
3. 包含会话元数据和交互历史

## 5. 数据模型设计

### 5.1 核心实体扩展
- Session: 增加topic和is_default字段
- User: 增加default_session_id字段

### 5.2 值对象
- EntranceType: 入口类型枚举
- IntentType: 意图类型枚举
- TaskStatus: 任务状态枚举
- ConsensusLevel: 共识水平对象

### 5.3 聚合
- SessionAggregate: 会话聚合
- TaskAggregate: 任务聚合
- DebateAggregate: 辩论聚合

## 6. 工作流程设计

### 6.1 会话创建流程（含主题生成）
1. 用户发起会话创建请求
2. PersonalAssistantService调用EntranceSelectorService选择入口类型
3. 根据入口类型调用相应的用例服务创建会话
4. PersonalAssistantService调用主题生成服务生成会话主题
5. 保存会话并设置为默认会话
6. 返回会话信息

### 6.2 用户输入处理流程（支持默认会话）
1. 用户发送输入（可能未指定会话ID）
2. CLI层检查是否指定会话ID，未指定则获取默认会话ID
3. PersonalAssistantService根据会话入口类型路由到相应处理方法
4. 对于Secretariat入口，分析意图并创建任务
5. 对于Forum入口，优化输入并集成到辩论中
6. 返回处理结果给用户

### 6.3 任务执行流程
1. SecretariatUseCase提交任务并规划工作流
2. WorkflowOrchestratorService启动工作流
3. 异步执行工作流步骤
4. 生成最终结果并更新任务状态

### 6.4 共识跟踪流程
1. ForumUseCase处理用户干预时，将消息添加到ConsensusTrackingService
2. ConsensusTrackingService实时计算共识水平
3. 提取关键论点供用户查看

## 7. 错误处理设计

### 7.1 错误类型扩展
- 会话不存在错误
- 默认会话未设置错误
- 精简指令解析错误

### 7.2 处理策略
- 对于用户输入错误，返回友好的错误提示
- 对于系统内部错误，记录日志并返回通用错误信息
- 对于服务不可用错误，尝试重试或降级处理
- 对于数据验证错误，返回具体的验证失败信息

## 8. 性能优化设计

### 8.1 缓存策略扩展
- 缓存用户会话和任务信息
- 缓存常用的角色和配置信息
- 缓存默认会话ID

### 8.2 异步处理
- 使用异步IO处理用户请求
- 异步执行工作流步骤
- 异步处理用户干预

### 8.3 资源管理
- 及时清理过期会话
- 限制并发任务数量
- 优化内存使用

## 9. 安全设计

### 9.1 数据安全扩展
- 敏感数据加密存储
- 安全的会话管理
- 会话数据访问控制

### 9.2 访问控制
- 基本的用户身份验证
- 会话级别的权限控制
- 角色风格设置权限控制

### 9.3 输入验证
- 严格的输入参数验证
- 防止注入攻击
- 会话ID格式验证

## 10. 监控和日志设计

### 10.1 日志记录扩展
- 记录关键操作和错误信息
- 记录系统性能指标
- 记录会话管理操作

### 10.2 监控指标扩展
- 系统健康状态
- 任务执行统计
- 用户活动统计
- 会话管理统计