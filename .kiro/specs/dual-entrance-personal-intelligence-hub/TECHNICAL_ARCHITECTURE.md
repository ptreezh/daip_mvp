# Personal Intelligence Hub - 技术架构规范

**文档状态:** 最终版 - 可用于实施
**版本:** 1.0
**日期:** 2025-08-06

## 📋 文档范围

本文档详细定义了Personal Intelligence Hub双入口系统的整体技术架构，包括系统组件、服务集成、数据流和部署架构。

---

## 🏗️ 系统架构概览

### 架构原则
- **分层架构**: 清晰的关注点分离
- **服务化**: 微服务架构，独立部署和扩展
- **事件驱动**: 基于消息的异步通信
- **可扩展性**: 水平扩展和垂直扩展支持

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Secretariat   │  │      Forum      │                │
│  │   Interface     │  │   Interface     │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Protocol Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   WebSocket     │  │      REST        │                │
│  │   Handler       │  │      API         │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │ PersonalAssistant│  │  ForumService   │                │
│  │     Service      │  │                 │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │  WorkflowEngine │  │MultiAgentCollab │                │
│  │                 │  │   orationSystem │                │
│  └─────────────────┘  └─────────────────┘                │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │ SynthesisEngine │  │ ConsensusEngine │                │
│  │                 │  │                 │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   MemoryService │  │   WikiService   │                │
│  │                 │  │                 │                │
│  └─────────────────┘  └─────────────────┘                │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   SSKG Manager   │  │  Vector Store   │                │
│  │                 │  │   (ChromaDB)    │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 核心组件设计

### 1. PersonalAssistantService
```python
class PersonalAssistantService:
    """统一助手服务 - 处理所有用户交互"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        self.workflow_engine = app_state.workflow_engine
        self.multi_agent_system = app_state.multi_agent_collaboration_system
        self.synthesis_engine = app_state.synthesis_engine
        self.memory_service = app_state.memory_service
        
        # 入口选择器
        self.entrance_selector = EntranceSelector()
        
        # 会话管理
        self.session_manager = SessionManager()
        
    async def handle_user_request(self, request):
        """处理用户请求 - 统一入口"""
        # 1. 确定用户偏好的入口类型
        entrance_type = await self.entrance_selector.determine_entrance(
            request.user_id, request.context
        )
        
        # 2. 根据入口类型路由到相应的处理器
        if entrance_type == "secretariat":
            return await self.handle_secretariat_request(request)
        elif entrance_type == "forum":
            return await self.handle_forum_request(request)
        else:
            raise ValueError(f"Unknown entrance type: {entrance_type}")
            
    async def handle_secretariat_request(self, request):
        """处理Secretariat请求"""
        # 自动化工作流执行
        intent = await self.interpret_intent(request.message)
        workflow_result = await self.workflow_engine.execute_workflow(intent)
        final_result = await self.synthesis_engine.generate_report(workflow_result)
        
        return {
            "type": "secretariat_result",
            "content": final_result["content"],
            "metadata": {
                "workflow_id": workflow_result["workflow_id"],
                "execution_time": workflow_result["execution_time"]
            }
        }
        
    async def handle_forum_request(self, request):
        """处理Forum请求"""
        # 启动交互式讨论
        session_id = await self.session_manager.create_forum_session(
            request.user_id, request.message
        )
        
        return {
            "type": "forum_session_created",
            "session_id": session_id,
            "initial_agents": await self.multi_agent_system.get_initial_agents()
        }
```

### 2. EntranceSelector 入口选择器
```python
class EntranceSelector:
    """智能入口选择器 - 基于用户行为和偏好"""
    
    def __init__(self):
        self.user_preferences = {}
        self.behavior_tracker = BehaviorTracker()
        
    async def determine_entrance(self, user_id, context):
        """确定最适合的入口类型"""
        # 1. 检查用户历史偏好
        if user_id in self.user_preferences:
            preferred_entrance = self.user_preferences[user_id]
            return preferred_entrance
            
        # 2. 基于上下文智能选择
        context_features = await self._extract_context_features(context)
        prediction = await self._predict_entrance(context_features)
        
        return prediction
        
    async def _extract_context_features(self, context):
        """提取上下文特征"""
        return {
            "query_complexity": self._analyze_query_complexity(context),
            "user_expertise": self._assess_user_expertise(context),
            "time_sensitivity": self._assess_time_sensitivity(context),
            "interaction_history": self.behavior_tracker.get_recent_behavior(context.user_id)
        }
        
    async def _predict_entrance(self, features):
        """预测最适合的入口类型"""
        # 简化规则 - 实际可使用ML模型
        if features["time_sensitivity"] > 0.8:
            return "secretariat"
        elif features["query_complexity"] > 0.7:
            return "forum"
        else:
            return "secretariat"  # 默认
```

### 3. SessionManager 会话管理器
```python
class SessionManager:
    """会话管理器 - 管理用户会话和状态"""
    
    def __init__(self):
        self.active_sessions = {}
        self.session_store = SessionStore()
        
    async def create_secretariat_session(self, user_id, initial_message):
        """创建Secretariat会话"""
        session_id = f"secretariat_{user_id}_{int(time.time())}"
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "type": "secretariat",
            "created_at": datetime.now(),
            "messages": [],
            "current_task": None,
            "status": "active"
        }
        
        self.active_sessions[session_id] = session
        await self.session_store.save_session(session)
        
        return session_id
        
    async def create_forum_session(self, user_id, topic):
        """创建Forum会话"""
        session_id = f"forum_{user_id}_{int(time.time())}"
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "type": "forum",
            "topic": topic,
            "created_at": datetime.now(),
            "participants": [],
            "messages": [],
            "status": "active"
        }
        
        self.active_sessions[session_id] = session
        await self.session_store.save_session(session)
        
        return session_id
        
    async def get_session(self, session_id):
        """获取会话信息"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # 从存储中加载
        session = await self.session_store.load_session(session_id)
        if session:
            self.active_sessions[session_id] = session
            
        return session
```

---

## 🔄 服务集成模式

### 1. DAIP服务集成
```python
class DAIPServiceIntegrator:
    """DAIP服务集成器 - 统一访问所有DAIP服务"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        
        # 核心服务
        self.workflow_engine = app_state.workflow_engine
        self.multi_agent_system = app_state.multi_agent_collaboration_system
        self.synthesis_engine = app_state.synthesis_engine
        self.consensus_engine = app_state.consensus_engine
        
        # 基础服务
        self.memory_service = app_state.memory_service
        self.wiki_service = app_state.wiki_service
        self.role_manager = app_state.role_manager
        self.sskg_manager = app_state.sskg_manager
        
    async def execute_secretariat_workflow(self, intent):
        """执行Secretariat工作流"""
        # 1. 组建团队
        team = await self.role_manager.form_team_for_intent(intent)
        
        # 2. 执行工作流
        workflow_result = await self.workflow_engine.execute_workflow({
            "intent": intent,
            "team": team,
            "mode": "automatic"
        })
        
        # 3. 生成报告
        final_report = await self.synthesis_engine.generate_report(workflow_result)
        
        return final_report
        
    async def execute_forum_collaboration(self, session_config):
        """执行Forum协作"""
        # 1. 选择Agent
        agents = await self.role_manager.select_agents_for_topic(session_config["topic"])
        
        # 2. 启动协作
        collaboration_id = await self.multi_agent_system.start_collaboration(
            session_config["session_id"],
            agents,
            session_config["topic"]
        )
        
        return collaboration_id
```

### 2. WebSocket通信管理
```python
class WebSocketManager:
    """WebSocket通信管理器"""
    
    def __init__(self):
        self.connections = {}
        self.message_handlers = {}
        
    async def handle_connection(self, websocket, session_id):
        """处理新连接"""
        self.connections[session_id] = websocket
        
        # 注册消息处理器
        self.message_handlers[session_id] = MessageHandler(session_id)
        
        try:
            async for message in websocket:
                await self.process_message(session_id, message)
        except WebSocketDisconnect:
            await self.handle_disconnect(session_id)
            
    async def process_message(self, session_id, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            handler = self.message_handlers.get(session_id)
            
            if handler:
                await handler.handle_message(data)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    async def send_message(self, session_id, message):
        """发送消息到客户端"""
        if session_id in self.connections:
            websocket = self.connections[session_id]
            await websocket.send_text(json.dumps(message))
            
    async def broadcast_to_session(self, session_id, message):
        """广播消息到会话的所有参与者"""
        # Forum模式下可能有多个连接
        await self.send_message(session_id, message)
```

---

## 🗄️ 数据存储设计

### 1. 会话数据模型
```python
class SessionModel:
    """会话数据模型"""
    
    def __init__(self):
        self.session_id: str = ""
        self.user_id: str = ""
        self.type: str = ""  # "secretariat" or "forum"
        self.created_at: datetime = None
        self.updated_at: datetime = None
        self.status: str = "active"  # "active", "completed", "expired"
        self.metadata: dict = {}
        
        # Secretariat特有
        self.current_task: dict = {}
        self.task_history: list = []
        
        # Forum特有
        self.topic: str = ""
        self.participants: list = []
        self.messages: list = []
        self.consensus_level: float = 0.0
```

### 2. 消息数据模型
```python
class MessageModel:
    """消息数据模型"""
    
    def __init__(self):
        self.message_id: str = ""
        self.session_id: str = ""
        self.type: str = ""  # "user", "agent", "system"
        self.content: str = ""
        self.sender: str = ""
        self.timestamp: datetime = None
        self.metadata: dict = {}
        
        # Agent特有
        self.agent_role: str = ""
        self.confidence: float = 0.0
        
        # User特有
        self.intent: str = ""
        self.optimized: bool = False
```

### 3. 工作流数据模型
```python
class WorkflowModel:
    """工作流数据模型"""
    
    def __init__(self):
        self.workflow_id: str = ""
        self.session_id: str = ""
        self.intent: dict = {}
        self.steps: list = []
        self.status: str = "pending"  # "pending", "running", "completed", "failed"
        self.start_time: datetime = None
        self.end_time: datetime = None
        self.result: dict = {}
        self.metadata: dict = {}
```

---

## 🚀 部署架构

### 1. 容器化部署
```dockerfile
# Dockerfile示例
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY config.yaml .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose配置
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@db:5432/pih
    depends_on:
      - redis
      - db
    volumes:
      - ./data:/app/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=pih
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  postgres_data:
  chroma_data:
```

### 3. Kubernetes部署配置
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pih-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pih
  template:
    metadata:
      labels:
        app: pih
    spec:
      containers:
      - name: pih
        image: pih-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

---

## 🔒 安全架构

### 1. 认证和授权
```python
class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.jwt_handler = JWTHandler()
        self.permission_manager = PermissionManager()
        
    async def authenticate_user(self, token):
        """用户认证"""
        try:
            payload = self.jwt_handler.decode_token(token)
            user_id = payload["user_id"]
            
            # 验证用户权限
            if await self.permission_manager.has_access(user_id):
                return user_id
            else:
                raise PermissionError("User access denied")
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
```

### 2. 数据加密
```python
class EncryptionManager:
    """数据加密管理器"""
    
    def __init__(self):
        self.cipher_suite = Fernet.generate_key()
        
    def encrypt_sensitive_data(self, data):
        """加密敏感数据"""
        if isinstance(data, str):
            return self.cipher_suite.encrypt(data.encode())
        elif isinstance(data, dict):
            return {k: self.encrypt_sensitive_data(v) for k, v in data.items()}
        else:
            return data
            
    def decrypt_sensitive_data(self, encrypted_data):
        """解密敏感数据"""
        if isinstance(encrypted_data, bytes):
            return self.cipher_suite.decrypt(encrypted_data).decode()
        elif isinstance(encrypted_data, dict):
            return {k: self.decrypt_sensitive_data(v) for k, v in encrypted_data.items()}
        else:
            return encrypted_data
```

---

## 📊 监控和日志

### 1. 性能监控
```python
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        
    def start_timing(self, operation):
        """开始计时"""
        self.start_times[operation] = time.time()
        
    def end_timing(self, operation):
        """结束计时"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.record_metric(operation, duration)
            del self.start_times[operation]
            
    def record_metric(self, metric_name, value):
        """记录指标"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.now()
        })
        
    def get_metrics_summary(self):
        """获取指标摘要"""
        summary = {}
        for metric_name, values in self.metrics.items():
            if values:
                recent_values = [v["value"] for v in values[-100:]]  # 最近100个值
                summary[metric_name] = {
                    "avg": sum(recent_values) / len(recent_values),
                    "min": min(recent_values),
                    "max": max(recent_values),
                    "count": len(recent_values)
                }
        return summary
```

### 2. 日志管理
```python
class LogManager:
    """日志管理器"""
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pih.log'),
                logging.StreamHandler()
            ]
        )
        
    def log_user_action(self, user_id, action, details):
        """记录用户操作"""
        logger.info(f"User {user_id} performed {action}: {details}")
        
    def log_system_event(self, event_type, details):
        """记录系统事件"""
        logger.info(f"System event {event_type}: {details}")
        
    def log_error(self, error, context):
        """记录错误"""
        logger.error(f"Error in {context}: {error}")
```

---

## 🔗 相关文档

- [Secretariat规范](./SECRETARIAT_SPEC.md)
- [Forum规范](./FORUM_SPEC.md)
- [API接口规范](./API_SPECIFICATION.md)
- [实施计划规范](./IMPLEMENTATION_PLAN.md)

---

**版本历史**
- v1.0 (2025-08-06): 初始版本 - 技术架构规范定义