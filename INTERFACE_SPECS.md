# 核心接口规范 - 真实多轮辩论系统

## 🎯 PersonalAssistantService 接口

### 位置
`personal_intelligence_hub/services/personal_assistant.py`

### 核心方法

#### 1. 意图分析
```python
async def analyze_intent(
    self, 
    user_input: str, 
    context: Optional[Dict] = None
) -> IntentResult
```
**功能**: 分析用户输入，确定工作流类型
**返回**: IntentResult(workflow_type, confidence, reasoning, topic)

#### 2. 团队组建
```python
async def assemble_team(
    self, 
    topic: str, 
    workflow_type: WorkflowType
) -> TeamProposal
```
**功能**: 根据话题和工作流类型选择合适的AI角色团队
**返回**: TeamProposal(agents, diversity_score, rationale, confirmation_message)

#### 3. 消息处理
```python
async def process_message(
    self, 
    user_input: str, 
    session_id: str
) -> str
```
**功能**: 处理用户消息，返回助手回复
**返回**: 格式化的回复字符串

#### 4. 命令执行
```python
async def execute_command(
    self, 
    command: str, 
    session_id: str
) -> str
```
**功能**: 执行特殊命令 (/consensus, /help, /status等)
**返回**: 命令执行结果

### 数据模型

#### IntentResult
```python
@dataclass
class IntentResult:
    workflowType: WorkflowType  # CRITICAL_REVIEW | MULTI_PERSPECTIVE
    confidence: float           # 0.0-1.0
    reasoning: str             # 选择理由
    topic: str                # 提取的话题
```

#### TeamProposal
```python
@dataclass
class TeamProposal:
    agents: List[str]          # 选中的AI角色名称
    diversity_score: float     # 团队多样性评分
    rationale: str            # 选择理由
    confirmation_message: str  # 确认消息
```

#### WorkflowType
```python
class WorkflowType(Enum):
    CRITICAL_REVIEW = "critical_review"      # 批判性审查
    MULTI_PERSPECTIVE = "multi_perspective"  # 多视角综合
    CUSTOM = "custom"                       # 自定义
```

## 🔧 IntentAnalysisService 接口

### 位置
`src/core_services/intent_analysis_service.py`

### 核心方法
```python
async def analyze_intent(
    self, 
    user_input: str, 
    user_id: str, 
    conversation_context: List[Dict[str, Any]]
) -> IntentAnalysis
```

### 数据模型
```python
class IntentAnalysis(BaseModel):
    user_input: str
    detected_intent: str
    confidence: float
    context_requirements: List[str]
    suggested_enhancements: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
```

## 🎨 ChatInterface 接口

### 位置
`frontend/components/chat_interface.py`

### 关键方法
```python
def __init__(self, personal_assistant: PersonalAssistantService)
async def handle_user_input(self, user_input: str) -> None
def add_message(self, sender: str, content: str) -> None
```

## 🔗 集成要点

### PersonalAssistant ↔ IntentAnalysis
- PersonalAssistant内部调用IntentAnalysisService
- 需要确保数据格式兼容

### PersonalAssistant ↔ RoleManager  
- assemble_team()方法依赖RoleManager获取可用角色
- 需要验证角色选择算法

### ChatInterface ↔ PersonalAssistant
- ChatInterface调用PersonalAssistant.process_message()
- 需要处理异步消息流

## ⚡ 性能要求

- **analyze_intent()**: <5秒
- **assemble_team()**: <10秒  
- **process_message()**: <30秒
- **execute_command()**: <15秒

## 🛡️ 错误处理

### 必需的异常处理
```python
try:
    result = await personal_assistant.process_message(user_input, session_id)
except Exception as e:
    logger.error(f"处理消息失败: {e}")
    return "抱歉，处理您的请求时出现问题。"
```

### 降级策略
- 后端服务不可用时使用本地规则
- LLM调用失败时提供默认回复
- 网络异常时使用缓存数据

---
**用途**: 为V0.1.1-V0.1.3任务提供精确的接口参考
**更新**: 2025-01-29