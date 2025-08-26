# DAIP-LIVE 系统内核服务全面API接口文档

## 📋 文档概述

本文档提供了DAIP-LIVE系统内核服务的全面API接口说明，包括所有服务类、方法、调用接口和示例代码。本文档作为后续开发和测试的权威指南。

## 🏗️ 系统架构概览

DAIP-LIVE采用分层架构设计，包含以下核心层次：

1. **内核服务层** (`src/core_services/`) - 核心业务逻辑
2. **应用服务层** (`src/application/`) - 应用流程编排
3. **API接口层** (`src/api/`) - HTTP REST API
4. **CLI接口层** (`src/cli/`) - 命令行接口

## 🔧 内核服务详细说明

### 1. RoleManager 角色管理服务

#### 服务描述
管理和维护AI角色定义，提供角色加载、验证、检索和搜索功能。

#### 核心方法

```python
class RoleManager:
    def __init__(self, roles_directory: Path = ROLES_DIR)
    def _load_roles(self) -> None
    def get_role(self, role_id: str) -> Optional[Role]
    def get_all_roles(self) -> dict[str, Role]
    def add_role(self, role: Role) -> bool
    def update_role(self, role_id: str, updates: dict) -> bool
    def delete_role(self, role_id: str) -> bool
    def search_roles(self, query: str) -> list[Role]
    def get_role_context(self, role_id: str) -> Optional[dict]
```

#### 数据模型

```python
@dataclass
class Role:
    id: str                    # 角色唯一标识符
    name: str                  # 角色名称
    description: str           # 角色描述
    system_prompt: str         # 系统提示词
    capabilities: List[str]     # 能力列表
    tags: List[str]            # 标签列表
```

#### 使用示例

```python
# 初始化角色管理器
role_manager = RoleManager()

# 获取所有角色
all_roles = role_manager.get_all_roles()

# 获取特定角色
ai_ethicist = role_manager.get_role("ai_ethicist")

# 搜索角色
matching_roles = role_manager.search_roles("AI ethics")

# 获取角色上下文
role_context = role_manager.get_role_context("ai_ethicist")
```

#### 配置要求
- 角色目录路径：默认 `roles/`
- 角色文件格式：JSON
- 必需字段：`name`, `description`, `system_prompt`

---

### 2. WikiService 维基服务

#### 服务描述
提供版本化的知识库管理，支持协作编辑、版本控制和智能搜索。

#### 核心方法

```python
class WikiService:
    def __init__(self, wiki_directory: str = "daip_mvp_project/memory_bank/wiki/")
    def create_entry(self, entry_name: str, content: str, creator: str, tags: list[str] = None) -> bool
    def get_entry(self, entry_name: str, version: str = None) -> Optional[dict]
    def update_entry(self, entry_name: str, new_content: str, editor: str, change_summary: str = "") -> bool
    def delete_entry(self, entry_name: str) -> bool
    def get_entry_history(self, entry_name: str) -> List[WikiVersion]
    def search_entries(self, query: str, limit: int = 10) -> List[dict]
    def propose_edit(self, entry_name: str, new_content: str, author: str, change_summary: str = "") -> str
    def approve_edit(self, proposal_id: str, approver: str) -> bool
    def reject_edit(self, proposal_id: str, reason: str) -> bool
    def list_all_entries(self) -> List[str]
    def get_entry_metadata(self, entry_name: str) -> Optional[WikiEntryMetadata]
```

#### 数据模型

```python
@dataclass
class WikiEntryMetadata:
    entry_name: str
    creator: str
    created_at: str
    last_editor: str
    last_modified: str
    tags: list[str]
    category: str
    versions: list[str]

@dataclass
class WikiVersion:
    entry_name: str
    version: str
    author: str
    timestamp: str
    content: str
    change_summary: str

@dataclass
class WikiProposal:
    proposal_id: str
    entry_name: str
    author: str
    timestamp: str
    base_version: str
    new_content: str
    change_summary: str
    status: EditStatus
```

#### 使用示例

```python
# 初始化维基服务
wiki_service = WikiService()

# 创建条目
success = wiki_service.create_entry(
    entry_name="AI Ethics Guidelines",
    content="Ethical guidelines for AI development...",
    creator="admin",
    tags=["AI", "Ethics", "Guidelines"]
)

# 获取条目
entry = wiki_service.get_entry("AI Ethics Guidelines")

# 更新条目
success = wiki_service.update_entry(
    entry_name="AI Ethics Guidelines",
    new_content="Updated ethical guidelines...",
    editor="user123",
    change_summary="Added new section on transparency"
)

# 搜索条目
results = wiki_service.search_entries("AI ethics")

# 提出编辑建议
proposal_id = wiki_service.propose_edit(
    entry_name="AI Ethics Guidelines",
    new_content="Proposed changes...",
    author="user456",
    change_summary="Improved clarity"
)

# 批准编辑
wiki_service.approve_edit(proposal_id, "admin")
```

#### 配置要求
- 维基目录：默认 `daip_mvp_project/memory_bank/wiki/`
- 向量数据库：ChromaDB
- 嵌入模型：nomic-embed-text

---

### 3. DebateManager 辩论管理服务

#### 服务描述
协调多角色辩论系统，提供结构化辩论协议和共识机制。

#### 核心方法

```python
class DebateManager:
    def __init__(self, role_manager: RoleManager, llm_manager: 'LLMManager')
    def create_debate(self, topic: str, roles: list[str], config: DebateConfig) -> str
    def start_debate(self, debate_id: str) -> bool
    def get_debate_status(self, debate_id: str) -> DebateStatus
    def add_intervention(self, debate_id: str, content: str, author: str = "User") -> bool
    def get_consensus(self, debate_id: str) -> Optional[dict]
    def export_results(self, debate_id: str, format: str = "json") -> dict
    def pause_debate(self, debate_id: str) -> bool
    def resume_debate(self, debate_id: str) -> bool
    def end_debate(self, debate_id: str) -> bool
    def get_debate_history(self, debate_id: str) -> List[DebateTurn]
```

#### 数据模型

```python
@dataclass
class DebateConfig:
    topic: str
    roles: list[str]
    rounds: int = 3
    time_limit_per_turn: int = 300
    consensus_strategy: str = "simple_majority"
    rules: dict = None

@dataclass
class DebateTurn:
    round_number: int
    role_name: str
    content: str
    timestamp: str
    metadata: dict = None

@dataclass
class DebateResult:
    debate_id: str
    topic: str
    participants: list[str]
    history: List[DebateTurn]
    consensus: dict
    synthesis: str
    metadata: dict
```

#### 使用示例

```python
# 初始化辩论管理器
debate_manager = DebateManager(role_manager, llm_manager)

# 创建辩论配置
config = DebateConfig(
    topic="AI in Healthcare: Benefits and Risks",
    roles=["AI Ethicist", "Healthcare Professional", "Technology Expert"],
    rounds=3,
    consensus_strategy="weighted_vote"
)

# 创建辩论
debate_id = debate_manager.create_debate(topic, roles, config)

# 开始辩论
debate_manager.start_debate(debate_id)

# 添加用户干预
debate_manager.add_intervention(debate_id, "Consider the ethical implications...")

# 获取辩论状态
status = debate_manager.get_debate_status(debate_id)

# 获取共识
consensus = debate_manager.get_consensus(debate_id)

# 导出结果
results = debate_manager.export_results(debate_id, format="markdown")
```

#### 配置要求
- 依赖RoleManager和LLMManager
- 共识策略：simple_majority, weighted_vote, consensus_building
- 时间限制：可配置每轮时间限制

---

### 4. ChatService 聊天服务

#### 服务描述
管理实时聊天会话，支持多角色AI对话和消息处理。

#### 核心方法

```python
class ChatService:
    def __init__(self, app_state: 'AppState')
    def create_chat_engine(self, engine_id: str, model_type: str = "default") -> bool
    def send_message_to_room(self, engine_id: str, room_id: str, content: str, sender_name: str = "User") -> bool
    def generate_responses_for_room(self, engine_id: str, room_id: str, target_roles: list[str] = None) -> List[ChatMessage]
    def get_room_details(self, engine_id: str, room_id: str) -> Optional[ChatRoom]
    def list_all_rooms(self, engine_id: str) -> List[ChatRoom]
    def create_room(self, engine_id: str, room_name: str, participants: list[str] = None) -> str
    def delete_room(self, engine_id: str, room_id: str) -> bool
    def get_room_history(self, engine_id: str, room_id: str) -> List[ChatMessage]
```

#### 数据模型

```python
class ChatMessage(BaseModel):
    sender_name: str
    content: str
    message_type: str = "text"
    metadata: Optional[dict] = None

class MultiRoleChatRequest(BaseModel):
    topic: str
    roles: list[str]
    messages: list[ChatMessage]

class MultiRoleChatResponse(BaseModel):
    new_message: ChatMessage
```

#### 使用示例

```python
# 初始化聊天服务
chat_service = ChatService(app_state)

# 创建聊天引擎
chat_service.create_chat_engine("default_engine", "gpt-3.5-turbo")

# 创建聊天室
room_id = chat_service.create_room("default_engine", "AI Ethics Discussion", ["AI Ethicist", "Philosopher"])

# 发送消息
chat_service.send_message_to_room("default_engine", room_id, "What are the main ethical concerns in AI?")

# 生成AI响应
responses = chat_service.generate_responses_for_room("default_engine", room_id)

# 获取房间详情
room_details = chat_service.get_room_details("default_engine", room_id)

# 获取房间历史
history = chat_service.get_room_history("default_engine", room_id)
```

#### 配置要求
- 依赖AppState和RoleManager
- 支持多种LLM模型
- 消息持久化：可选

---

### 5. MemoryService 记忆服务

#### 服务描述
管理AI代理的持久化记忆和上下文，提供记忆存储、检索和相似性搜索。

#### 核心方法

```python
class MemoryService:
    def __init__(self, data_dir: str = "data/memory_banks")
    def store_memory(self, agent_id: str, content: str, tags: list[str] = None, source: str = None) -> str
    def retrieve_memories(self, agent_id: str, query: str = None, limit: int = 10) -> List[MemoryEntry]
    def search_similar_memories(self, query: str, top_k: int = 5) -> List[MemoryEntry]
    def update_memory(self, memory_id: str, content: str = None, tags: list[str] = None) -> bool
    def delete_memory(self, memory_id: str) -> bool
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryEntry]
    def get_agent_memories(self, agent_id: str, limit: int = 50) -> List[MemoryEntry]
    def consolidate_memories(self, agent_id: str) -> bool
```

#### 数据模型

```python
@dataclass
class MemoryEntry:
    memory_id: str
    agent_id: str
    content: str
    tags: list[str]
    source: str
    timestamp: str
    embedding: list[float]
    importance_score: float
```

#### 使用示例

```python
# 初始化记忆服务
memory_service = MemoryService()

# 存储记忆
memory_id = memory_service.store_memory(
    agent_id="ai_ethicist",
    content="AI transparency is crucial for building trust...",
    tags=["transparency", "trust", "AI ethics"],
    source="debate_001"
)

# 检索记忆
memories = memory_service.retrieve_memories("ai_ethicist", query="transparency")

# 相似性搜索
similar_memories = memory_service.search_similar_memories("AI ethical considerations")

# 更新记忆
memory_service.update_memory(memory_id, content="Updated content about transparency...")

# 获取代理记忆
agent_memories = memory_service.get_agent_memories("ai_ethicist")

# 记忆整合
memory_service.consolidate_memories("ai_ethicist")
```

#### 配置要求
- 数据目录：默认 `data/memory_banks`
- 向量数据库：ChromaDB
- 嵌入模型：nomic-embed-text

---

### 6. ExpertService 专家服务

#### 服务描述
管理专家知识、技能和可用性，提供专家搜索和批量导入功能。

#### 核心方法

```python
class ExpertService:
    def __init__(self, app_state: 'AppState')
    def get_all_experts(self) -> List[Expert]
    def create_expert(self, expert_data: dict) -> Expert
    def update_expert(self, expert_id: str, updates: dict) -> bool
    def delete_expert(self, expert_id: str) -> bool
    def get_expert_by_id(self, expert_id: str) -> Optional[Expert]
    def search_experts_by_embedding(self, query: str, top_k: int = 5) -> List[dict]
    def batch_import_experts(self, roles_data: list, overwrite: bool = False, validate_only: bool = False) -> dict
    def get_experts_by_category(self, category: str) -> List[Expert]
    def get_experts_by_specialty(self, specialty: str) -> List[Expert]
    def update_expert_availability(self, expert_id: str, availability: str) -> bool
```

#### 数据模型

```python
@dataclass
class Expert:
    name: str
    category: str
    specialties: list[str]
    skills: list[str]
    availability: str
    experience_years: int
    reputation_score: float
    languages: list[str]
    location: str
    education: list[str]
    certifications: list[str]
    projects: list[str]
```

#### 使用示例

```python
# 初始化专家服务
expert_service = ExpertService(app_state)

# 获取所有专家
all_experts = expert_service.get_all_experts()

# 创建专家
expert_data = {
    "name": "AI Ethics Expert",
    "category": "AI Ethics",
    "specialties": ["AI Ethics", "Responsible AI"],
    "skills": ["Ethical Analysis", "Policy Development"],
    "availability": "available"
}
expert = expert_service.create_expert(expert_data)

# 搜索专家
results = expert_service.search_experts_by_embedding("AI ethics specialist")

# 批量导入
import_data = [
    {"name": "Expert 1", "category": "Technology", "specialties": ["AI", "ML"]},
    {"name": "Expert 2", "category": "Ethics", "specialties": ["AI Ethics"]}
]
result = expert_service.batch_import_experts(import_data)

# 按类别获取专家
ethics_experts = expert_service.get_experts_by_category("AI Ethics")
```

#### 配置要求
- 依赖AppState和向量数据库
- 支持批量导入和验证
- 可用性跟踪

---

### 7. IntegratedLLMManager 集成LLM管理器

#### 服务描述
提供统一、优化的LLM调用服务，支持多角色对话和上下文优化。

#### 核心方法

```python
class IntegratedLLMManager:
    def __init__(self)
    def initialize(self) -> bool
    def call_llm_for_role(self, role_id: str, user_input: str, task_context: str = "", additional_context: dict = None) -> str
    def call_llm_for_multi_role_debate(self, participating_roles: list[str], debate_topic: str, debate_context: dict = None, round_number: int = 1) -> dict
    def get_role_context(self, role_id: str) -> Optional[RoleContext]
    def update_role_context(self, role_id: str, new_context: dict) -> bool
    def get_performance_stats(self) -> dict
    def clear_role_context(self, role_id: str) -> bool
    def set_model_parameters(self, role_id: str, parameters: dict) -> bool
```

#### 数据模型

```python
@dataclass
class RoleContext:
    role_id: str
    role_name: str
    conversation_history: list[dict]
    memory_context: dict
    task_context: str
    last_updated: str

@dataclass
class OptimizedLLMCall:
    role_id: str
    prompts: dict
    response: str
    metrics: dict
    timestamp: str
```

#### 使用示例

```python
# 初始化LLM管理器
llm_manager = IntegratedLLMManager()
llm_manager.initialize()

# 单角色调用
response = llm_manager.call_llm_for_role(
    role_id="ai_ethicist",
    user_input="What are the ethical implications of AI in healthcare?",
    task_context="Ethical analysis",
    additional_context={"domain": "healthcare"}
)

# 多角色辩论调用
debate_response = llm_manager.call_llm_for_multi_role_debate(
    participating_roles=["ai_ethicist", "healthcare_professional"],
    debate_topic="AI in Healthcare",
    debate_context={"focus": "ethical implications"},
    round_number=1
)

# 获取角色上下文
context = llm_manager.get_role_context("ai_ethicist")

# 更新角色上下文
llm_manager.update_role_context("ai_ethicist", {"new_info": "updated context"})

# 获取性能统计
stats = llm_manager.get_performance_stats()
```

#### 配置要求
- LLM提供商：Ollama, OpenAI等
- 上下文优化：自动
- 性能跟踪：启用

---

### 8. UserProfileService 用户档案服务

#### 服务描述
管理用户档案、偏好设置和交互历史。

#### 核心方法

```python
class UserProfileService:
    def __init__(self, data_dir: str = "data/user_profiles")
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]
    def create_user_profile(self, user_id: str, profile_data: dict) -> bool
    def update_user_profile(self, user_id: str, updates: dict) -> bool
    def get_user_preferences(self, user_id: str) -> Optional[dict]
    def update_user_preferences(self, user_id: str, preferences: dict) -> bool
    def track_user_interaction(self, user_id: str, interaction: dict) -> bool
    def get_user_history(self, user_id: str, limit: int = 50) -> List[dict]
    def delete_user_profile(self, user_id: str) -> bool
```

#### 数据模型

```python
@dataclass
class UserProfile:
    user_id: str
    preferences: dict
    interaction_history: List[dict]
    created_at: str
    last_updated: str
    metadata: dict
```

#### 使用示例

```python
# 初始化用户档案服务
profile_service = UserProfileService()

# 创建用户档案
profile_service.create_user_profile("user123", {
    "preferences": {
        "language": "zh-CN",
        "theme": "dark",
        "notification_enabled": True
    }
})

# 获取用户档案
profile = profile_service.get_user_profile("user123")

# 更新用户偏好
profile_service.update_user_preferences("user123", {
    "theme": "light",
    "notification_enabled": False
})

# 跟踪用户交互
profile_service.track_user_interaction("user123", {
    "action": "debate_participation",
    "topic": "AI Ethics",
    "timestamp": "2025-01-01T12:00:00Z"
})

# 获取用户历史
history = profile_service.get_user_history("user123")
```

#### 配置要求
- 数据目录：默认 `data/user_profiles`
- 隐私设置：可配置
- 交互跟踪：可选

---

### 9. IntentAnalysisService 意图分析服务

#### 服务描述
分析用户输入以确定意图和路由到适当的服务。

#### 核心方法

```python
class IntentAnalysisService:
    def __init__(self, user_profile_service: UserProfileService, llm_interface: 'LLMInterface')
    def analyze_intent(self, user_input: str, context: dict = None) -> IntentAnalysis
    def extract_entities(self, user_input: str) -> List[dict]
    def classify_task_type(self, user_input: str) -> TaskType
    def get_confidence_score(self, user_input: str, intent: str) -> float
    def suggest_actions(self, intent: IntentAnalysis) -> List[str]
    def get_intent_history(self, user_id: str) -> List[dict]
```

#### 数据模型

```python
@dataclass
class IntentAnalysis:
    intent_type: TaskType
    entities: List[dict]
    confidence: float
    context: dict
    suggested_actions: List[str]
    timestamp: str

class TaskType(Enum):
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    DISCUSSION = "discussion"
    DEBATE = "debate"
    RESEARCH = "research"
    CREATION = "creation"
```

#### 使用示例

```python
# 初始化意图分析服务
intent_service = IntentAnalysisService(user_profile_service, llm_interface)

# 分析意图
analysis = intent_service.analyze_intent(
    user_input="I want to start a debate about AI ethics",
    context={"user_id": "user123"}
)

# 提取实体
entities = intent_service.extract_entities("Start a debate about AI ethics with experts")

# 分类任务类型
task_type = intent_service.classify_task_type("What are the ethical implications of AI?")

# 获取置信度
confidence = intent_service.get_confidence_score("Start debate", "debate")

# 获取建议操作
actions = intent_service.suggest_actions(analysis)
```

#### 配置要求
- 依赖用户档案服务和LLM接口
- 意图分类模型：可配置
- 置信度阈值：可调整

---

### 10. TaskManager 任务管理器

#### 服务描述
管理任务生命周期、执行和监控。

#### 核心方法

```python
class TaskManager:
    def __init__(self, task_directory: str = "data/tasks")
    def create_task(self, session_id: str, content: str, intent_type: IntentType, priority: TaskPriority = TaskPriority.MEDIUM) -> str
    def get_task(self, task_id: str) -> Optional[Task]
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool
    def get_task_history(self, task_id: str) -> List[TaskEvent]
    def cancel_task(self, task_id: str) -> bool
    def pause_task(self, task_id: str) -> bool
    def resume_task(self, task_id: str) -> bool
    def get_tasks_by_session(self, session_id: str) -> List[Task]
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]
    def get_task_statistics(self) -> dict
```

#### 数据模型

```python
@dataclass
class Task:
    task_id: str
    session_id: str
    content: str
    intent_type: IntentType
    priority: TaskPriority
    status: TaskStatus
    created_at: str
    updated_at: str
    metadata: dict

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
```

#### 使用示例

```python
# 初始化任务管理器
task_manager = TaskManager()

# 创建任务
task_id = task_manager.create_task(
    session_id="session123",
    content="Analyze ethical implications of AI in healthcare",
    intent_type=IntentType.ANALYSIS,
    priority=TaskPriority.HIGH
)

# 获取任务
task = task_manager.get_task(task_id)

# 更新任务状态
task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)

# 暂停任务
task_manager.pause_task(task_id)

# 恢复任务
task_manager.resume_task(task_id)

# 获取会话任务
session_tasks = task_manager.get_tasks_by_session("session123")

# 获取任务统计
stats = task_manager.get_task_statistics()
```

#### 配置要求
- 任务目录：默认 `data/tasks`
- 优先级设置：可配置
- 超时设置：可调整

---

### 11. ChatRulePrimitive 聊天规则原语

#### 服务描述
管理和执行聊天室规则，如内容过滤、频率限制和参与人数限制。

#### 核心方法

```python
class ChatRulePrimitive(InstitutionalPrimitive):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]
```

#### 数据模型

```python
class ChatRuleConfiguration(BaseModel):
    rule_id: str
    name: str
    description: str
    rule_type: ChatRuleType
    prohibited_keywords: List[str]
    max_message_length: Optional[int]
    max_messages_per_minute: Optional[int]
    min_participants: int
    max_participants: int
```

#### 使用示例

```python
# 初始化聊天规则原语
config = {
    "rule_id": "rate_limit_rule",
    "name": "Rate Limit",
    "description": "Limit messages per minute",
    "rule_type": "rate_limit",
    "max_messages_per_minute": 5
}
chat_rule_primitive = ChatRulePrimitive("rate_limiter", config)

# 执行规则
inputs = {
    "chat_session": {"session_id": "s1", "participants": ["u1", "u2"]},
    "message": {"message_id": "m1", "author_id": "u1", "content": "Hello"}
}
result = await chat_rule_primitive.execute(inputs, execution_context)
```

---

## 🌐 HTTP API 接口

### 1. Chat API (`/chat`)

#### 端点列表

```python
# 简化多角色聊天
POST /chat/multi_role_chat_simple
Request: MultiRoleChatRequest
Response: MultiRoleChatResponse

# 创建聊天引擎
POST /chat/multi_chat/create_engine
Parameters: engine_id, model_type
Response: {"success": bool, "engine_id": str, "message": str}

# 发送消息
POST /chat/multi_chat/send_message
Parameters: room_id, content, sender_name, engine_id
Response: {"success": bool, "message": str}

# 生成AI响应
POST /chat/multi_chat/generate_responses
Parameters: room_id, target_roles, engine_id
Response: {"success": bool, "responses": list}

# 获取房间详情
GET /chat/multi_chat/room/{room_id}
Parameters: engine_id
Response: {"success": bool, "room": dict}

# 列出所有房间
GET /chat/multi_chat/rooms
Parameters: engine_id
Response: {"success": bool, "rooms": list}
```

#### 使用示例

```python
import requests

# 简化多角色聊天
response = requests.post("http://localhost:8000/chat/multi_role_chat_simple", json={
    "topic": "AI Ethics",
    "roles": ["AI Ethicist", "Philosopher"],
    "messages": [
        {"sender_name": "User", "content": "What are the main ethical concerns?"}
    ]
})

# 创建聊天引擎
response = requests.post("http://localhost:8000/chat/multi_chat/create_engine", params={
    "engine_id": "my_engine",
    "model_type": "gpt-3.5-turbo"
})

# 发送消息
response = requests.post("http://localhost:8000/chat/multi_chat/send_message", params={
    "room_id": "room123",
    "content": "Hello AI roles!",
    "sender_name": "User",
    "engine_id": "my_engine"
})
```

---

### 2. Roles API (`/roles`)

#### 端点列表

```python
# 获取所有角色
GET /roles/
Response: {"roles": list[str]}

# 创建角色
POST /roles/create
Request: Role
Response: Role

# 智能创建角色
POST /roles/create_smart
Request: SmartRoleCreateRequest
Response: {"success": bool, "role": dict, "analysis": dict, "message": str}

# 批量导入角色
POST /roles/batch_import
Request: BatchRoleImportRequest
Response: {"success": bool, "imported": int, "failed": int, "errors": list}

# 向量搜索角色
POST /roles/search_embedding
Parameters: query, top_k
Response: {"roles": list}
```

#### 使用示例

```python
import requests

# 获取所有角色
response = requests.get("http://localhost:8000/roles/")
roles = response.json()["roles"]

# 创建角色
response = requests.post("http://localhost:8000/roles/create", json={
    "name": "AI Ethics Expert",
    "desc": "Expert in AI ethics and responsible AI development",
    "capabilities": ["Ethical Analysis", "Policy Development"]
})

# 智能创建角色
response = requests.post("http://localhost:8000/roles/create_smart", json={
    "role_name": "Healthcare AI Specialist",
    "role_definition": "Expert in AI applications in healthcare...",
    "category": "Healthcare",
    "specialties": ["AI in Healthcare", "Medical Ethics"]
})

# 批量导入
response = requests.post("http://localhost:8000/roles/batch_import", json={
    "roles": [
        {"name": "Expert 1", "desc": "Description 1"},
        {"name": "Expert 2", "desc": "Description 2"}
    ],
    "overwrite_existing": False
})

# 向量搜索
response = requests.post("http://localhost:8000/roles/search_embedding", params={
    "query": "AI ethics specialist",
    "top_k": 5
})
```

---

### 3. Knowledge Management API (`/knowledge`)

#### 端点列表

```python
# 获取知识概览
GET /knowledge/
Response: {"status": str, "message": str}

# 搜索知识库
GET /knowledge/search
Parameters: query, limit
Response: {"query": str, "results": list, "total": int, "limit": int}

# 创建知识条目
POST /knowledge/create
Request: dict
Response: {"id": str, "status": str, "data": dict}
```

#### 使用示例

```python
import requests

# 获取知识概览
response = requests.get("http://localhost:8000/knowledge/")

# 搜索知识库
response = requests.get("http://localhost:8000/knowledge/search", params={
    "query": "AI ethics guidelines",
    "limit": 10
})

# 创建知识条目
response = requests.post("http://localhost:8000/knowledge/create", json={
    "title": "AI Ethics Guidelines",
    "content": "Comprehensive guidelines for ethical AI development...",
    "tags": ["AI", "Ethics", "Guidelines"]
})
```

---

## 💻 CLI 命令接口

### 1. 主要命令组

```bash
# 个人助手命令
daip-cli pa chat <query>                    # 与个人助手对话
daip-cli pa status <task_id>               # 检查任务状态
daip-cli pa logs [--limit N]               # 查看日志

# 辩论管理命令
daip-cli debate start <topic>              # 开始辩论
    [--role ROLE] [--rounds N]             # 参数：角色、轮数
    [--consensus STR] [--save]             # 参数：共识策略、保存结果
    [--output FILE] [--verbose]            # 参数：输出文件、详细输出
daip-cli debate export-to-wiki <debate_id> # 导出辩论到维基
    [--title TITLE] [--format FORMAT]      # 参数：标题、格式

# 角色管理命令
daip-cli roles list                        # 列出所有角色
daip-cli roles create <name>              # 创建角色
daip-cli roles search <query>              # 搜索角色
daip-cli roles help                        # 显示角色命令的详细帮助

# 工作流命令
daip-cli workflow list                    # 列出工作流
daip-cli workflow start <workflow_id>      # 启动工作流
daip-cli workflow help                     # 显示工作流命令的详细帮助

# 聊天命令
daip-cli chat start <topic>               # 开始聊天
daip-cli chat history                     # 查看聊天历史

# 维基命令
daip-cli wiki create <title>              # 创建维基条目
daip-cli wiki edit <title>                # 编辑维基条目
daip-cli wiki search <query>              # 搜索维基

# 系统命令
daip-cli status                           # 检查系统状态
daip-cli help                             # 显示帮助
```

### 2. 使用示例

```bash
# 开始辩论
daip-cli debate start "AI in Healthcare" \
  --role "AI Ethicist" \
  --role "Healthcare Professional" \
  --rounds 3 \
  --consensus weighted_vote \
  --save \
  --output debate_results.txt

# 与个人助手对话
daip-cli pa chat "What are the ethical implications of AI in healthcare?"

# 检查系统状态
daip-cli status

# 创建维基条目
daip-cli wiki create "AI Ethics Guidelines" \
  --content "Comprehensive guidelines for ethical AI development..."

# 搜索角色
daip-cli roles search "AI ethics specialist"

# 获取角色命令帮助
daip-cli roles help

# 开始聊天
daip-cli chat start "AI Ethics Discussion" \
  --participants "AI Ethicist,Philosopher"
```

---

## 🔗 服务依赖关系

### 核心依赖图

```
AppState (中央状态管理)
├── RoleManager (角色管理)
├── LLMManager (LLM管理)
├── WikiService (维基服务)
├── MemoryService (记忆服务)
├── ExpertService (专家服务)
├── TaskManager (任务管理)
├── UserProfileService (用户档案)
├── IntentAnalysisService (意图分析)
└── ChatService (聊天服务)

PersonalAssistantRouter (个人助手路由器)
├── IntentAnalysisService
├── LLMManager
├── TaskOrchestrator
└── WorkflowEngine

API Layer (API层)
├── Chat Router
├── Roles Router
├── Knowledge Router
└── Other Routers

CLI Layer (CLI层)
├── Main CLI
├── Commands
└── Interactive Mode
```

### 初始化顺序

1. **配置加载** - 加载系统配置
2. **AppState初始化** - 创建中央状态管理器
3. **存储系统** - 初始化数据库和文件存储
4. **核心服务** - 按依赖顺序初始化服务
5. **应用服务** - 初始化应用层服务
6. **API/CLI接口** - 启动HTTP服务器和CLI接口

### 典型请求流程

```
用户输入 → CLI/API
    ↓
意图分析 → PersonalAssistantRouter
    ↓
服务路由 → 相应的核心服务
    ↓
LLM处理 → IntegratedLLMManager
    ↓
结果生成 → 响应格式化
    ↓
输出 → CLI/API响应
```

---

## ⚙️ 配置管理

### 1. 主配置文件 (`config.yaml`)

```yaml
version: "0.1.0"
llm:
  provider: "ollama"
  ollama:
    generation_model: "llama3:instruct"
    embedding_model: "nomic-embed-text:latest"
    host: "http://localhost:11434"
    timeout: 30
vector_store:
  chroma_db_path: "data/chroma_db"
  role_collection_name: "roles"
logging:
  level: "INFO"
  format: "%("asctime")s - %(name)s - %(levelname)s - %(message)s"
token_management:
  max_context_tokens: 4096
  cost_per_1k_input_tokens: 0.0
  cost_per_1k_output_tokens: 0.0
  enable_cost_tracking: true
  enable_context_optimization: true
  compression_threshold: 0.8
user_profile:
  data_dir: "data/user_profiles"
  max_interaction_history: 100
  enable_intent_tracking: true
session:
  auth_data_dir: "data/auth"
  session_expiry_minutes: 60
  token_expiry_minutes: 60
  enable_session_tracking: true
roles_config_path: "configs/roles.yaml"
log_level: "INFO"
allowed_origins: ["*"]
```

### 2. 环境变量配置

```bash
# LLM配置
export LLM_PROVIDER="ollama"
export OLLAMA_HOST="http://localhost:11434"
export EMBEDDING_MODEL="nomic-embed-text:latest"

# 数据库配置
export CHROMA_DB_PATH="data/chroma_db"
export POSTGRES_URL="postgresql://user:password@localhost/daip"

# 服务配置
export LOG_LEVEL="INFO"
export MAX_CONTEXT_TOKENS="4096"
export ENABLE_COST_TRACKING="true"

# 安全配置
export SECRET_KEY="your-secret-key"
export JWT_SECRET="your-jwt-secret"
```

### 3. 服务特定配置

```python
# RoleManager配置
ROLE_MANAGER_CONFIG = {
    "roles_directory": "roles",
    "validation_enabled": True,
    "auto_reload": False
}

# WikiService配置
WIKI_SERVICE_CONFIG = {
    "wiki_directory": "data/wiki",
    "vector_db_enabled": True,
    "version_control": True,
    "edit_approval": True
}

# ChatService配置
CHAT_SERVICE_CONFIG = {
    "default_model": "gpt-3.5-turbo",
    "max_history_length": 100,
    "response_timeout": 30
}
```

---

## 🧪 测试指南

### 1. 单元测试

```python
# 测试RoleManager
def test_role_manager():
    role_manager = RoleManager()
    
    # 测试角色加载
    roles = role_manager.get_all_roles()
    assert len(roles) > 0
    
    # 测试角色获取
    role = role_manager.get_role("ai_ethicist")
    assert role is not None
    assert role.name == "AI Ethicist"
    
    # 测试角色搜索
    results = role_manager.search_roles("ethics")
    assert len(results) > 0

# 测试WikiService
def test_wiki_service():
    wiki_service = WikiService()
    
    # 测试创建条目
    success = wiki_service.create_entry("Test Entry", "Test content", "test_user")
    assert success
    
    # 测试获取条目
    entry = wiki_service.get_entry("Test Entry")
    assert entry is not None
    
    # 测试搜索
    results = wiki_service.search_entries("test")
    assert len(results) > 0

# 测试ChatService
def test_chat_service():
    chat_service = ChatService(app_state)
    
    # 测试创建引擎
    success = chat_service.create_chat_engine("test_engine")
    assert success
    
    # 测试创建房间
    room_id = chat_service.create_room("test_engine", "Test Room")
    assert room_id is not None
    
    # 测试发送消息
    success = chat_service.send_message_to_room("test_engine", room_id, "Hello!")
    assert success
```

### 2. 集成测试

```python
# 测试完整辩论流程
def test_debate_flow():
    # 初始化服务
    role_manager = RoleManager()
    debate_manager = DebateManager(role_manager, llm_manager)
    
    # 创建辩论
    config = DebateConfig(
        topic="Test Topic",
        roles=["AI Ethicist", "Philosopher"],
        rounds=2
    )
    debate_id = debate_manager.create_debate("Test Topic", ["AI Ethicist", "Philosopher"], config)
    
    # 开始辩论
    success = debate_manager.start_debate(debate_id)
    assert success
    
    # 获取状态
    status = debate_manager.get_debate_status(debate_id)
    assert status is not None
    
    # 添加干预
    success = debate_manager.add_intervention(debate_id, "Test intervention")
    assert success
    
    # 获取共识
    consensus = debate_manager.get_consensus(debate_id)
    # 共识可能为None，取决于辩论状态

# 测试API端点
def test_api_endpoints():
    # 测试聊天API
    response = client.post("/chat/multi_role_chat_simple", json={
        "topic": "Test",
        "roles": ["AI Ethicist"],
        "messages": [{"sender_name": "User", "content": "Hello"}]
    })
    assert response.status_code == 200
    
    # 测试角色API
    response = client.get("/roles/")
    assert response.status_code == 200
    assert "roles" in response.json()
    
    # 测试知识API
    response = client.get("/knowledge/")
    assert response.status_code == 200

# 测试CLI命令
def test_cli_commands():
    # 测试状态命令
    result = runner.invoke(cli_app, ["status"])
    assert result.exit_code == 0
    
    # 测试帮助命令
    result = runner.invoke(cli_app, ["help"])
    assert result.exit_code == 0
    
    # 测试角色列表
    result = runner.invoke(cli_app, ["roles", "list"])
    assert result.exit_code == 0
```

### 3. 性能测试

```python
# 测试服务响应时间
def test_service_performance():
    import time
    
    # 测试RoleManager性能
    start_time = time.time()
    role_manager = RoleManager()
    roles = role_manager.get_all_roles()
    load_time = time.time() - start_time
    assert load_time < 5.0  # 应该在5秒内加载
    
    # 测试搜索性能
    start_time = time.time()
    results = role_manager.search_roles("AI")
    search_time = time.time() - start_time
    assert search_time < 1.0  # 搜索应该在1秒内完成
    
    # 测试LLM调用性能
    start_time = time.time()
    response = llm_manager.call_llm_for_role("ai_ethicist", "Hello")
    call_time = time.time() - start_time
    assert call_time < 30.0  # LLM调用应该在30秒内完成

# 测试并发处理
def test_concurrent_requests():
    import concurrent.futures
    
    def make_request():
        return client.post("/chat/multi_role_chat_simple", json={
            "topic": "Test",
            "roles": ["AI Ethicist"],
            "messages": [{"sender_name": "User", "content": "Hello"}]
        })
    
    # 并发发送10个请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        responses = [future.result() for future in futures]
    
    # 所有请求都应该成功
    for response in responses:
        assert response.status_code == 200
```

---

## 🚨 错误处理和故障排除

### 1. 常见错误类型

```python
# 服务初始化错误
class ServiceInitializationError(Exception):
    """服务初始化失败"""
    pass

# 配置错误
class ConfigurationError(Exception):
    """配置错误"""
    pass

# 数据库错误
class DatabaseError(Exception):
    """数据库操作错误"""
    pass

# LLM调用错误
class LLMCallError(Exception):
    """LLM调用失败"""
    pass

# 权限错误
class PermissionError(Exception):
    """权限不足"""
    pass
```

### 2. 错误处理最佳实践

#### CLI全局错误处理
`daip-cli.py` 入口文件包含一个全局异常处理块。这意味着任何在命令执行过程中未被捕获的异常都会被此处理器捕获，并向用户显示一个统一、友好的错误信息，而不是一个完整的Python错误堆栈。这极大地改善了用户体验，并有助于快速定位问题。

```python
# 服务层错误处理
try:
    result = service.some_method()
except ServiceInitializationError as e:
    logger.error(f"Service initialization failed: {e}")
    # 尝试重新初始化服务
    service.reinitialize()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    # 检查配置文件
    validate_configuration()
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    # 检查数据库连接
    check_database_connection()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # 记录完整错误信息
    logger.exception("Full error traceback:")

# API层错误处理
@app.exception_handler(ServiceInitializationError)
async def service_init_error_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "Service temporarily unavailable"}
    )

@app.exception_handler(ConfigurationError)
async def config_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Configuration error"}
    )

@app.exception_handler(ValueError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

### 3. 故障排除指南

#### 服务无法启动

1. **检查配置文件**
   ```bash
   # 验证配置文件格式
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **检查依赖**
   ```bash
   # 检查Python依赖
   pip list | grep -E "(fastapi|ollama|chromadb)"
   
   # 检查系统依赖
   ollama list
   ```

3. **检查权限**
   ```bash
   # 检查数据目录权限
   ls -la data/
   chmod 755 data/
   ```

#### LLM调用失败

1. **检查LLM服务状态**
   ```bash
   # 检查Ollama服务
   ollama list
   
   # 测试LLM调用
   ollama run llama3:instruct "Hello"
   ```

2. **检查网络连接**
   ```bash
   # 测试连接
   curl http://localhost:11434/api/tags
   ```

3. **检查模型可用性**
   ```bash
   # 下载模型
   ollama pull llama3:instruct
   ollama pull nomic-embed-text
   ```

#### 数据库问题

1. **检查ChromaDB状态**
   ```bash
   # 检查数据库文件
   ls -la data/chroma_db/
   
   # 测试数据库连接
   python -c "import chromadb; client = chromadb.PersistentClient('data/chroma_db')"
   ```

2. **修复损坏的数据库**
   ```bash
   # 备份并重建数据库
   mv data/chroma_db data/chroma_db.backup
   # 服务会自动创建新的数据库
   ```

#### 性能问题

1. **检查内存使用**
   ```bash
   # 检查进程内存
   ps aux | grep python
   
   # 检查系统内存
   free -h
   ```

2. **优化配置**
   ```python
   # 减少上下文长度
   MAX_CONTEXT_TOKENS = 2048
   
   # 启用压缩
   ENABLE_CONTEXT_OPTIMIZATION = True
   
   # 增加超时时间
   LLM_TIMEOUT = 60
   ```

---

## 📊 监控和日志

### 1. 系统监控

```python
# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "role_manager": "ok",
            "wiki_service": "ok",
            "chat_service": "ok",
            "llm_manager": "ok"
        },
        "timestamp": datetime.now().isoformat()
    }

# 详细状态端点
@app.get("/status")
async def detailed_status():
    return {
        "version": "0.3.11",
        "uptime": time.time() - start_time,
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "active_sessions": len(session_manager.active_sessions),
        "total_requests": request_counter,
        "error_rate": error_counter / max(request_counter, 1)
    }
```

### 2. 日志配置

```python
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daip.log'),
        logging.StreamHandler()
    ]
)

# 创建日志记录器
logger = logging.getLogger(__name__)

# 结构化日志
def log_request(request, response_time):
    logger.info({
        "event": "api_request",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "response_time": response_time,
        "user_agent": request.headers.get("user-agent"),
        "timestamp": datetime.now().isoformat()
    })
```

### 3. 性能指标

```python
# 性能监控
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper

# 使用装饰器
@monitor_performance
async def api_endpoint():
    return {"message": "Hello World"}
```

---

## 🔄 扩展和定制

### 1. 添加新服务

```python
# 1. 创建服务类
class NewService:
    def __init__(self, config):
        self.config = config
        self.initialize()
    
    def initialize(self):
        # 初始化逻辑
        pass
    
    def core_method(self, param):
        # 核心方法
        return result

# 2. 在AppState中添加服务
class AppState:
    def __init__(self):
        # ... 其他服务
        self.new_service = NewService(config)

# 3. 创建API端点
@router.post("/new-service/method")
async def new_service_method(param: str):
    result = app_state.new_service.core_method(param)
    return {"result": result}
```

### 2. 添加新的LLM提供商

```python
# 1. 创建LLM提供商类
class CustomLLMProvider:
    def __init__(self, config):
        self.config = config
    
    async def generate(self, prompt, **kwargs):
        # 实现自定义LLM调用逻辑
        return response

# 2. 注册提供商
LLMFactory.register_provider("custom", CustomLLMProvider)

# 3. 使用自定义提供商
config = LLMConfig(provider="custom", model="custom-model")
llm = LLMFactory.create(config)
```

### 3. 自定义中间件

```python
# 1. 创建中间件
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # 前置处理
    start_time = time.time()
    
    # 调用下一个中间件
    response = await call_next(request)
    
    # 后置处理
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# 2. 认证中间件
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # 检查认证
    if not is_authenticated(request):
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"}
        )
    
    return await call_next(request)
```

---

## 📝 总结

本API文档提供了DAIP-LIVE系统内核服务的全面接口说明，包括：

1. **10个核心服务**的详细方法和使用示例
2. **HTTP API接口**的完整端点列表和调用示例
3. **CLI命令接口**的详细使用方法
4. **服务依赖关系**和初始化顺序
5. **配置管理**的最佳实践
6. **测试指南**包括单元测试、集成测试和性能测试
7. **错误处理**和故障排除指南
8. **监控和日志**的配置方法
9. **扩展和定制**的开发指南

本文档将作为后续开发和测试的重要参考，确保系统的稳定性和可维护性。

---

**文档版本**: v1.0  
**最后更新**: 2025-01-21  
**维护者**: DAIP-LIVE Team
