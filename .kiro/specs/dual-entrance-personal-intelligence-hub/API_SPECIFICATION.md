# Personal Intelligence Hub - API接口规范

**文档状态:** 最终版 - 可用于实施
**版本:** 1.0
**日期:** 2025-08-06

## 📋 文档范围

本文档详细定义了Personal Intelligence Hub双入口系统的API接口规范，包括WebSocket协议、REST API端点、数据模型和错误处理。

---

## 🔄 WebSocket 协议

### 连接管理
```javascript
// 客户端连接示例
const ws = new WebSocket('ws://localhost:8000/ws/session/{session_id}');

// 连接建立
ws.onopen = function(event) {
    console.log('WebSocket connected');
    
    // 发送认证消息
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'user_jwt_token',
        session_id: 'session_123'
    }));
};

// 消息接收
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    handleMessage(data);
};

// 错误处理
ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

// 连接关闭
ws.onclose = function(event) {
    console.log('WebSocket disconnected');
};
```

### 消息格式标准
```json
{
  "type": "message_type",
  "session_id": "session_identifier",
  "timestamp": "2025-08-06T10:30:00Z",
  "data": {
    // 具体消息数据
  }
}
```

---

## 📡 WebSocket 消息类型

### 1. 认证消息
#### 客户端 → 服务器
```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "session_id": "session_123",
  "user_id": "user_456"
}
```

#### 服务器 → 客户端
```json
{
  "type": "auth_response",
  "success": true,
  "session_id": "session_123",
  "user_info": {
    "user_id": "user_456",
    "username": "john_doe",
    "preferences": {
      "preferred_entrance": "secretariat",
      "theme": "light"
    }
  }
}
```

### 2. Secretariat 消息
#### 用户任务提交
```json
{
  "type": "secretariat_task",
  "message": "分析AI在医疗领域的应用趋势",
  "session_id": "secretariat_session_123",
  "priority": "normal",
  "context": {
    "user_expertise": "intermediate",
    "time_sensitivity": "high"
  }
}
```

#### 任务状态更新
```json
{
  "type": "task_status",
  "session_id": "secretariat_session_123",
  "task_id": "task_789",
  "status": "processing",
  "progress": {
    "current_step": "analyzing_data",
    "percentage": 45,
    "estimated_time_remaining": 120
  },
  "timestamp": "2025-08-06T10:30:15Z"
}
```

#### 任务结果
```json
{
  "type": "secretariat_result",
  "session_id": "secretariat_session_123",
  "task_id": "task_789",
  "content": "AI在医疗领域的应用趋势分析报告...",
  "metadata": {
    "workflow_id": "workflow_456",
    "execution_time": 245.3,
    "agent_count": 5,
    "tokens_used": 12500,
    "confidence_score": 0.87
  },
  "timestamp": "2025-08-06T10:34:00Z"
}
```

#### 透明度数据请求
```json
{
  "type": "request_transparency",
  "session_id": "secretariat_session_123",
  "task_id": "task_789",
  "detail_level": "full"
}
```

#### 透明度数据响应
```json
{
  "type": "transparency_data",
  "session_id": "secretariat_session_123",
  "task_id": "task_789",
  "workflow_steps": [
    {
      "step_id": "step_1",
      "name": "intent_analysis",
      "description": "分析用户意图",
      "status": "completed",
      "duration": 2.1,
      "output": "分析医疗AI应用趋势"
    },
    {
      "step_id": "step_2",
      "name": "team_formation",
      "description": "组建专家团队",
      "status": "completed",
      "duration": 1.5,
      "output": "医疗专家、技术专家、伦理专家"
    }
  ],
  "agent_activities": [
    {
      "agent_id": "medical_expert_1",
      "role": "医疗专家",
      "activities": [
        {
          "activity": "分析医疗数据",
          "duration": 45.2,
          "contribution": "提供了关键的临床应用案例"
        }
      ]
    }
  ],
  "resource_usage": {
    "total_tokens": 12500,
    "execution_time": 245.3,
    "memory_usage": "45MB"
  }
}
```

### 3. Forum 消息
#### 论坛会话创建
```json
{
  "type": "create_forum_session",
  "topic": "AI在医疗领域的伦理考量",
  "session_id": "forum_session_123",
  "participants": ["medical_expert", "ethics_expert", "ai_researcher"],
  "settings": {
    "max_duration": 1800,
    "consensus_threshold": 0.7
  }
}
```

#### 用户干预
```json
{
  "type": "user_intervention",
  "session_id": "forum_session_123",
  "message": {
    "content": "我认为应该考虑患者隐私保护的重要性",
    "intent": "comment",
    "target_agent": "ethics_expert"
  },
  "timestamp": "2025-08-06T10:30:00Z"
}
```

#### Agent消息
```json
{
  "type": "agent_message",
  "session_id": "forum_session_123",
  "agent_id": "ethics_expert_1",
  "agent_name": "伦理专家",
  "content": "患者隐私保护确实是关键问题...",
  "message_type": "response",
  "confidence": 0.92,
  "target_message_id": "msg_456",
  "timestamp": "2025-08-06T10:30:05Z"
}
```

#### 共识更新
```json
{
  "type": "consensus_update",
  "session_id": "forum_session_123",
  "consensus_level": 0.75,
  "key_points": [
    {
      "point": "隐私保护是必要的",
      "support_level": 0.9,
      "agents_agreeing": ["ethics_expert", "medical_expert"]
    },
    {
      "point": "需要平衡创新和监管",
      "support_level": 0.6,
      "agents_agreeing": ["ai_researcher", "medical_expert"]
    }
  ],
  "discussion_status": "active",
  "timestamp": "2025-08-06T10:35:00Z"
}
```

#### 论坛控制
```json
{
  "type": "forum_control",
  "session_id": "forum_session_123",
  "action": "pause",
  "reason": "用户请求暂停讨论",
  "timestamp": "2025-08-06T10:40:00Z"
}
```

---

## 🌐 REST API 端点

### 1. 会话管理
#### 创建会话
```http
POST /api/sessions
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "entrance_type": "secretariat|forum",
  "user_id": "user_123",
  "initial_context": {
    "topic": "AI医疗应用",
    "preferences": {
      "language": "zh-CN",
      "detail_level": "comprehensive"
    }
  }
}
```

#### 响应
```json
{
  "session_id": "session_456",
  "entrance_type": "secretariat",
  "created_at": "2025-08-06T10:30:00Z",
  "websocket_url": "ws://localhost:8000/ws/session/session_456",
  "status": "active"
}
```

#### 获取会话信息
```http
GET /api/sessions/{session_id}
Authorization: Bearer <jwt_token>
```

#### 响应
```json
{
  "session_id": "session_456",
  "user_id": "user_123",
  "entrance_type": "secretariat",
  "status": "active",
  "created_at": "2025-08-06T10:30:00Z",
  "last_activity": "2025-08-06T10:35:00Z",
  "metadata": {
    "task_count": 3,
    "total_duration": 325
  }
}
```

### 2. 用户管理
#### 获取用户信息
```http
GET /api/users/{user_id}
Authorization: Bearer <jwt_token>
```

#### 响应
```json
{
  "user_id": "user_123",
  "username": "john_doe",
  "email": "john@example.com",
  "preferences": {
    "preferred_entrance": "secretariat",
    "language": "zh-CN",
    "theme": "light",
    "notification_settings": {
      "task_completion": true,
      "forum_updates": false
    }
  },
  "usage_stats": {
    "total_sessions": 25,
    "total_tasks": 87,
    "avg_session_duration": 450
  }
}
```

#### 更新用户偏好
```http
PUT /api/users/{user_id}/preferences
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "preferred_entrance": "forum",
  "language": "zh-CN",
  "theme": "dark"
}
```

### 3. 任务管理
#### 获取任务历史
```http
GET /api/sessions/{session_id}/tasks
Authorization: Bearer <jwt_token>
```

#### 响应
```json
{
  "tasks": [
    {
      "task_id": "task_789",
      "session_id": "session_456",
      "type": "secretariat",
      "content": "分析AI在医疗领域的应用趋势",
      "status": "completed",
      "created_at": "2025-08-06T10:30:00Z",
      "completed_at": "2025-08-06T10:34:00Z",
      "duration": 240,
      "metadata": {
        "workflow_id": "workflow_456",
        "agent_count": 5
      }
    }
  ]
}
```

#### 获取任务详情
```http
GET /api/tasks/{task_id}
Authorization: Bearer <jwt_token>
```

#### 响应
```json
{
  "task_id": "task_789",
  "session_id": "session_456",
  "type": "secretariat",
  "content": "分析AI在医疗领域的应用趋势",
  "status": "completed",
  "created_at": "2025-08-06T10:30:00Z",
  "completed_at": "2025-08-06T10:34:00Z",
  "result": "AI在医疗领域的应用趋势分析报告...",
  "workflow_steps": [
    {
      "step_id": "step_1",
      "name": "intent_analysis",
      "status": "completed",
      "duration": 2.1
    }
  ],
  "agent_activities": [
    {
      "agent_id": "medical_expert_1",
      "role": "医疗专家",
      "contribution": "提供了关键的临床应用案例"
    }
  ]
}
```

### 4. 系统状态
#### 获取系统状态
```http
GET /api/system/status
Authorization: Bearer <jwt_token>
```

#### 响应
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 86400,
  "active_sessions": 15,
  "active_connections": 23,
  "system_load": {
    "cpu_usage": 0.45,
    "memory_usage": 0.67,
    "disk_usage": 0.34
  },
  "service_status": {
    "workflow_engine": "healthy",
    "multi_agent_system": "healthy",
    "synthesis_engine": "healthy",
    "memory_service": "healthy"
  }
}
```

---

## 📊 数据模型

### 1. 用户模型
```python
class User(BaseModel):
    user_id: str
    username: str
    email: str
    preferences: UserPreferences
    usage_stats: UsageStats
    created_at: datetime
    updated_at: datetime

class UserPreferences(BaseModel):
    preferred_entrance: str = "secretariat"
    language: str = "zh-CN"
    theme: str = "light"
    notification_settings: NotificationSettings

class NotificationSettings(BaseModel):
    task_completion: bool = True
    forum_updates: bool = False
    system_alerts: bool = True

class UsageStats(BaseModel):
    total_sessions: int = 0
    total_tasks: int = 0
    avg_session_duration: float = 0.0
    favorite_topics: List[str] = []
```

### 2. 会话模型
```python
class Session(BaseModel):
    session_id: str
    user_id: str
    entrance_type: str
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class SecretariatSession(Session):
    current_task: Optional[str] = None
    task_history: List[str] = []
    auto_transparency: bool = False

class ForumSession(Session):
    topic: str = ""
    participants: List[str] = []
    messages: List[Dict[str, Any]] = []
    consensus_level: float = 0.0
    is_paused: bool = False
```

### 3. 任务模型
```python
class Task(BaseModel):
    task_id: str
    session_id: str
    type: str
    content: str
    status: str = "pending"
    priority: str = "normal"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    metadata: Dict[str, Any] = {}

class SecretariatTask(Task):
    workflow_id: Optional[str] = None
    workflow_steps: List[Dict[str, Any]] = []
    agent_activities: List[Dict[str, Any]] = []
    execution_time: Optional[float] = None
    transparency_data: Optional[Dict[str, Any]] = None

class ForumTask(Task):
    topic: str = ""
    participants: List[str] = []
    messages: List[Dict[str, Any]] = []
    consensus_level: float = 0.0
    user_interventions: List[Dict[str, Any]] = []
```

### 4. 消息模型
```python
class Message(BaseModel):
    message_id: str
    session_id: str
    type: str
    content: str
    sender: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class UserMessage(Message):
    intent: str = "comment"
    optimized: bool = False
    target_agent: Optional[str] = None

class AgentMessage(Message):
    agent_id: str
    agent_role: str
    confidence: float = 0.0
    target_message_id: Optional[str] = None
    message_type: str = "response"

class SystemMessage(Message):
    system_event: str
    severity: str = "info"
    details: Dict[str, Any] = {}
```

---

## ❌ 错误处理

### 1. 错误代码定义
```python
class ErrorCode:
    # 认证错误 (1000-1999)
    AUTH_INVALID_TOKEN = 1001
    AUTH_EXPIRED_TOKEN = 1002
    AUTH_INSUFFICIENT_PERMISSIONS = 1003
    
    # 会话错误 (2000-2999)
    SESSION_NOT_FOUND = 2001
    SESSION_EXPIRED = 2002
    SESSION_INVALID_TYPE = 2003
    
    # 任务错误 (3000-3999)
    TASK_NOT_FOUND = 3001
    TASK_INVALID_STATE = 3002
    TASK_EXECUTION_FAILED = 3003
    
    # 系统错误 (4000-4999)
    SYSTEM_SERVICE_UNAVAILABLE = 4001
    SYSTEM_RESOURCE_EXHAUSTED = 4002
    SYSTEM_INTERNAL_ERROR = 4003
    
    # 验证错误 (5000-5999)
    VALIDATION_INVALID_INPUT = 5001
    VALIDATION_MISSING_PARAMETER = 5002
    VALIDATION_INVALID_FORMAT = 5003
```

### 2. 错误响应格式
```json
{
  "error": {
    "code": 1001,
    "message": "Invalid authentication token",
    "details": "Token expired or malformed",
    "timestamp": "2025-08-06T10:30:00Z",
    "request_id": "req_123"
  }
}
```

### 3. WebSocket错误处理
```json
{
  "type": "error",
  "code": 2001,
  "message": "Session not found",
  "session_id": "session_123",
  "timestamp": "2025-08-06T10:30:00Z",
  "action_required": "reconnect"
}
```

---

## 🔒 安全规范

### 1. 认证
```python
class AuthenticationMiddleware:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET")
        self.token_expiry = 3600  # 1 hour
        
    def create_token(self, user_id: str) -> str:
        """创建JWT令牌"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        
    def verify_token(self, token: str) -> Optional[str]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload["user_id"]
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
```

### 2. 授权
```python
class AuthorizationMiddleware:
    def __init__(self):
        self.role_permissions = {
            "user": ["read_own_sessions", "create_sessions"],
            "admin": ["read_all_sessions", "manage_system"],
            "viewer": ["read_public_sessions"]
        }
        
    def check_permission(self, user_id: str, permission: str) -> bool:
        """检查用户权限"""
        user_role = self.get_user_role(user_id)
        return permission in self.role_permissions.get(user_role, [])
```

### 3. 数据验证
```python
class DataValidator:
    @staticmethod
    def validate_session_data(session_data: dict) -> bool:
        """验证会话数据"""
        required_fields = ["session_id", "user_id", "entrance_type"]
        
        for field in required_fields:
            if field not in session_data:
                raise ValidationError(f"Missing required field: {field}")
                
        if session_data["entrance_type"] not in ["secretariat", "forum"]:
            raise ValidationError("Invalid entrance type")
            
        return True
        
    @staticmethod
    def validate_message_data(message_data: dict) -> bool:
        """验证消息数据"""
        required_fields = ["type", "content", "timestamp"]
        
        for field in required_fields:
            if field not in message_data:
                raise ValidationError(f"Missing required field: {field}")
                
        if len(message_data["content"]) > 10000:
            raise ValidationError("Message content too long")
            
        return True
```

---

## 📈 性能优化

### 1. 连接管理
```python
class ConnectionPool:
    def __init__(self, max_connections: int = 1000):
        self.max_connections = max_connections
        self.active_connections = {}
        self.connection_queue = asyncio.Queue()
        
    async def get_connection(self, session_id: str):
        """获取连接"""
        if len(self.active_connections) >= self.max_connections:
            await self.connection_queue.get()
            
        return WebSocketConnection(session_id)
        
    async def release_connection(self, session_id: str):
        """释放连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            await self.connection_queue.put(None)
```

### 2. 消息缓存
```python
class MessageCache:
    def __init__(self, cache_size: int = 10000):
        self.cache = {}
        self.cache_size = cache_size
        self.access_times = {}
        
    def get_message(self, message_id: str) -> Optional[dict]:
        """获取缓存消息"""
        if message_id in self.cache:
            self.access_times[message_id] = time.time()
            return self.cache[message_id]
        return None
        
    def set_message(self, message_id: str, message_data: dict):
        """设置缓存消息"""
        if len(self.cache) >= self.cache_size:
            self._evict_oldest()
            
        self.cache[message_id] = message_data
        self.access_times[message_id] = time.time()
        
    def _evict_oldest(self):
        """淘汰最旧的消息"""
        if self.access_times:
            oldest_id = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_id]
            del self.access_times[oldest_id]
```

---

## 🔗 相关文档

- [技术架构规范](./TECHNICAL_ARCHITECTURE.md)
- [Secretariat规范](./SECRETARIAT_SPEC.md)
- [Forum规范](./FORUM_SPEC.md)
- [实施计划规范](./IMPLEMENTATION_PLAN.md)

---

**版本历史**
- v1.0 (2025-08-06): 初始版本 - API接口规范定义