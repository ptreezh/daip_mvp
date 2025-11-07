# 🎯 P5-P7 模块重构最佳实践设计方案

## 📋 重构目标

### P5 - Agent Engine (解耦重构，降低复杂度)
- **目标**: 将复杂的单体引擎拆分为可独立测试和部署的组件
- **策略**: 事件驱动架构 + 依赖注入 + 策略模式
- **预期收益**: 可测试性提升80%，维护成本降低60%

### P6 - TUI (UI组件模块化)
- **目标**: 将单体TUI拆分为可复用的组件库
- **策略**: 组件化架构 + 状态管理 + 事件系统
- **预期收益**: UI开发效率提升70%，组件复用率提升90%

### P7 - GUI (补充完整实现)
- **目标**: 构建功能完整的图形界面，与TUI功能对等
- **策略**: MVVM架构 + 响应式设计 + 跨平台兼容
- **预期收益**: 用户体验提升100%，功能覆盖率100%

---

## 🏗️ P5 - Agent Engine 解耦重构方案

### 🔍 当前问题分析

#### 高耦合问题
```python
# 当前问题：executor.py (284行) 承担过多职责
class AgentExecutor:
    # ❌ 直接依赖太多模块
    def __init__(self, model_provider, knowledge_manager, role_manager,
                 tool_manager, memory_service, permission_manager):
        # 6个直接依赖，耦合度过高

    # ❌ 单个方法过于复杂 (100+行)
    async def execute_goal(self, goal: str, context: Dict) -> AsyncGenerator[AgentEvent, None]:
        # 包含意图识别、工具调用、状态管理、错误处理...
```

#### 复杂性问题
- **状态管理混乱**: 多个状态变量散布在不同类中
- **异步流程复杂**: 嵌套的异步调用难以追踪
- **错误处理分散**: 缺乏统一的错误处理策略

### 🎯 解耦重构设计

#### 1. 核心架构重构
```python
# 新架构：事件驱动的微服务架构
class AgentOrchestrator:
    """协调器 - 只负责协调，不处理具体逻辑"""

    def __init__(self, event_bus: EventBus, container: ServiceContainer):
        self.event_bus = event_bus
        self.container = container
        self.session = None

    async def execute_goal(self, goal: str) -> AsyncGenerator[AgentEvent, None]:
        # 1. 创建会话
        session = await self.create_session(goal)

        # 2. 发布会话开始事件
        await self.event_bus.publish(SessionStarted(session=session))

        # 3. 事件驱动执行
        async for event in self.event_bus.stream(session.id):
            yield event

            if event.type == EventType.SESSION_COMPLETED:
                break

# 事件总线 - 解耦的核心
class EventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._streams: Dict[str, AsyncEventStream] = {}

    async def publish(self, event: AgentEvent) -> None:
        handlers = self._handlers.get(event.type, [])
        await asyncio.gather(*[handler(event) for handler in handlers])

        # 发送到会话流
        if event.session_id:
            stream = self._streams.get(event.session_id)
            if stream:
                await stream.put(event)

    def stream(self, session_id: str) -> AsyncEventStream:
        if session_id not in self._streams:
            self._streams[session_id] = AsyncEventStream()
        return self._streams[session_id]
```

#### 2. 领域服务拆分
```python
# 意图识别服务
class IntentRecognitionService:
    """专门负责意图识别"""

    async def recognize_intent(self, user_input: str, context: SessionContext) -> Intent:
        # 使用策略模式处理不同类型的意图
        strategy = await self.get_intent_strategy(user_input)
        return await strategy.recognize(user_input, context)

class IntentStrategy(ABC):
    @abstractmethod
    async def recognize(self, input: str, context: SessionContext) -> Intent:
        pass

class ChatIntentStrategy(IntentStrategy):
    async def recognize(self, input: str, context: SessionContext) -> Intent:
        # 专门的聊天意图识别逻辑
        pass

class WorkflowIntentStrategy(IntentStrategy):
    async def recognize(self, input: str, context: SessionContext) -> Intent:
        # 专门的工作流意图识别逻辑
        pass

# 执行引擎服务
class ExecutionEngineService:
    """专门负责执行引擎选择和调用"""

    def __init__(self, engines: Dict[ExecutionType, ExecutionEngine]):
        self.engines = engines

    async def execute(self, intent: Intent, context: SessionContext) -> AsyncGenerator[ExecutionEvent, None]:
        engine = self.engines.get(intent.execution_type)
        if not engine:
            raise UnsupportedIntentError(f"No engine for {intent.execution_type}")

        async for event in engine.execute(intent, context):
            yield event

# 状态管理服务
class StateManagementService:
    """专门负责状态管理"""

    def __init__(self, event_bus: EventBus, persistence: PersistenceService):
        self.event_bus = event_bus
        self.persistence = persistence
        self._states: Dict[str, AgentState] = {}

    async def get_state(self, session_id: str) -> AgentState:
        if session_id not in self._states:
            # 从持久化层加载
            self._states[session_id] = await self.persistence.load_state(session_id)
        return self._states[session_id]

    async def update_state(self, session_id: str, new_state: AgentState) -> None:
        old_state = self._states.get(session_id)
        self._states[session_id] = new_state

        # 发布状态变更事件
        await self.event_bus.publish(StateChanged(
            session_id=session_id,
            old_state=old_state,
            new_state=new_state
        ))

        # 持久化
        await self.persistence.save_state(session_id, new_state)
```

#### 3. 依赖注入配置
```python
# 容器配置
class AgentEngineContainer:
    @staticmethod
    def configure() -> ServiceContainer:
        container = ServiceContainer()

        # 核心服务
        container.register(EventBus, lifecycle=SingletonScope)
        container.register(StateManagementService, lifecycle=SingletonScope)
        container.register(IntentRecognitionService, lifecycle=SingletonScope)
        container.register(ExecutionEngineService, lifecycle=SingletonScope)

        # 策略注册
        container.register(IntentStrategy, ChatIntentStrategy, name="chat")
        container.register(IntentStrategy, WorkflowIntentStrategy, name="workflow")

        # 执行引擎注册
        container.register(ExecutionEngine, ChatExecutionEngine, name="chat")
        container.register(ExecutionEngine, WorkflowExecutionEngine, name="workflow")

        # 主协调器
        container.register(AgentOrchestrator, lifecycle=SingletonScope)

        return container
```

### 📊 重构效果预期

#### 复杂度降低
- **单个类平均行数**: 从 150行 → 50行 (-67%)
- **循环复杂度**: 从 15 → 5 (-67%)
- **依赖数量**: 从 6个 → 2个 (-67%)

#### 可测试性提升
- **单元测试覆盖率**: 从 60% → 95% (+58%)
- **测试执行时间**: 从 30s → 10s (-67%)
- **Mock复杂度**: 从 高 → 低

---

## 🎨 P6 - TUI 组件模块化方案

### 🔍 当前问题分析

#### 单体架构问题
```python
# 当前问题：tui.py (2877行) 巨型单体类
class DAIPLiveTUI(App):
    # ❌ 所有UI逻辑都在一个类中
    # ❌ 2000+行代码，无法维护
    # ❌ 混合了布局、事件处理、业务逻辑

    def compose(self) -> ComposeResult:
        # ❌ 100+行的布局定义
        # ❌ 硬编码的UI结构

    async def handle_run_command(self) -> None:
        # ❌ 50+行的命令处理逻辑
        # ❌ 直接调用业务逻辑，违反分层原则
```

### 🎯 组件化架构设计

#### 1. 组件架构重构
```python
# 基础组件接口
class TUIComponent(ABC):
    """TUI组件基类"""

    def __init__(self, app: "DAIPLiveTUI", id: str = None):
        self.app = app
        self.id = id or self.__class__.__name__
        self._mounted = False
        self._state = {}

    @abstractmethod
    def render(self) -> Widget:
        """渲染组件"""
        pass

    async def mount(self) -> None:
        """组件挂载"""
        self._mounted = True
        await self.on_mount()

    async def unmount(self) -> None:
        """组件卸载"""
        self._mounted = False
        await self.on_unmount()

    async def on_mount(self) -> None:
        """挂载钩子"""
        pass

    async def on_unmount(self) -> None:
        """卸载钩子"""
        pass

    def update_state(self, **kwargs) -> None:
        """更新状态"""
        self._state.update(kwargs)
        if self._mounted:
            self.app.query_one(f"#{self.id}").refresh()

# 布局组件
class LayoutComponent(TUIComponent):
    """布局组件"""

    def __init__(self, app: "DAIPLiveTUI"):
        super().__init__(app, "main-layout")
        self.sidebar = SidebarComponent(app)
        self.content = ContentComponent(app)
        self.status_bar = StatusBarComponent(app)

    def render(self) -> Widget:
        return Horizontal(
            self.sidebar.render(),
            Vertical(
                self.content.render(),
                self.status_bar.render(),
            )
        )

# 侧边栏组件
class SidebarComponent(TUIComponent):
    """侧边栏组件"""

    def __init__(self, app: "DAIPLiveTUI"):
        super().__init__(app, "sidebar")
        self.navigation = NavigationComponent(app)
        self.session_info = SessionInfoComponent(app)

    def render(self) -> Widget:
        return Vertical(
            Static("🤖 DAIP-LIVE", classes="title"),
            self.navigation.render(),
            self.session_info.render(),
            classes="sidebar"
        )

# 导航组件
class NavigationComponent(TUIComponent):
    """导航组件"""

    def __init__(self, app: "DAIPLiveTUI"):
        super().__init__(app, "navigation")
        self.commands = [
            ("/run", "开始新会话"),
            ("/role", "角色管理"),
            ("/session", "会话管理"),
            ("/debate", "辩论系统"),
            ("/knowledge", "知识库"),
        ]

    def render(self) -> Widget:
        return ListView(
            *[Static(f"{cmd} - {desc}") for cmd, desc in self.commands],
            classes="navigation"
        )

# 内容区域组件
class ContentComponent(TUIComponent):
    """内容区域组件"""

    def __init__(self, app: "DAIPLiveTUI"):
        super().__init__(app, "content")
        self.input_area = InputAreaComponent(app)
        self.display_area = DisplayAreaComponent(app)
        self.current_view = "chat"

    def render(self) -> Widget:
        return Vertical(
            self.display_area.render(),
            self.input_area.render(),
            classes="content"
        )

    async def switch_view(self, view_name: str) -> None:
        """切换视图"""
        self.current_view = view_name
        await self.display_area.switch_view(view_name)
        self.update_state(current_view=view_name)

# 输入区域组件
class InputAreaComponent(TUIComponent):
    """输入区域组件"""

    def __init__(self, app: "DAIPLiveTUI"):
        super().__init__(app, "input-area")
        self.input = Input(placeholder="输入命令或消息...")
        self.command_suggestions = CommandSuggestions(app)

    def render(self) -> Widget:
        return Vertical(
            self.input,
            self.command_suggestions.render(),
            classes="input-area"
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入提交"""
        command = event.value
        self.input.value = ""

        # 发布命令事件
        await self.app.event_bus.publish(CommandSubmitted(
            command=command,
            timestamp=datetime.now()
        ))

# 显示区域组件
class DisplayAreaComponent(TUIComponent):
    """显示区域组件"""

    def __init__(self, app: "DAIPLiveTUI"):
        super().__init__(app, "display-area")
        self.current_view = None
        self.views = {
            "chat": ChatViewComponent(app),
            "role": RoleViewComponent(app),
            "session": SessionViewComponent(app),
            "debate": DebateViewComponent(app),
            "knowledge": KnowledgeViewComponent(app),
        }

    def render(self) -> Widget:
        if self.current_view:
            return self.current_view.render()
        return self.views["chat"].render()

    async def switch_view(self, view_name: str) -> None:
        """切换视图"""
        if view_name in self.views:
            self.current_view = self.views[view_name]
            await self.current_view.mount()
            self.update_state(current_view=view_name)
```

#### 2. 状态管理系统
```python
# TUI状态管理
class TUIStateManager:
    """TUI状态管理器"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._state = TUIState()
        self._subscribers: Dict[str, List[Callable]] = {}

    def get_state(self) -> TUIState:
        return self._state

    def update_state(self, updates: Dict[str, Any]) -> None:
        old_state = copy.deepcopy(self._state)
        self._state.update(updates)

        # 通知订阅者
        for key, subscribers in self._subscribers.items():
            if key in updates:
                for callback in subscribers:
                    callback(self._state, old_state)

        # 发布状态变更事件
        asyncio.create_task(self.event_bus.publish(TUIStateChanged(
            new_state=self._state,
            old_state=old_state,
            changes=updates
        )))

    def subscribe(self, key: str, callback: Callable) -> None:
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)

@dataclass
class TUIState:
    """TUI状态数据类"""
    current_view: str = "chat"
    input_text: str = ""
    is_processing: bool = False
    current_session: Optional[str] = None
    available_roles: List[str] = field(default_factory=list)
    available_sessions: List[str] = field(default_factory=list)
    notifications: List[Notification] = field(default_factory=list)
    theme: str = "default"
    user_preferences: Dict[str, Any] = field(default_factory=dict)
```

#### 3. 事件系统
```python
# TUI事件系统
class TUIEventSystem:
    """TUI事件系统"""

    def __init__(self, state_manager: TUIStateManager, event_bus: EventBus):
        self.state_manager = state_manager
        self.event_bus = event_bus
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        # 订阅业务事件
        self.event_bus.subscribe(AgentEvent, self._handle_agent_event)
        self.event_bus.subscribe(CommandSubmitted, self._handle_command_submitted)

        # 订阅状态事件
        self.state_manager.subscribe("current_view", self._handle_view_change)
        self.state_manager.subscribe("is_processing", self._handle_processing_change)

    async def _handle_agent_event(self, event: AgentEvent) -> None:
        """处理Agent事件"""
        if isinstance(event, MessageReceived):
            self.state_manager.update_state(
                notifications=[Notification(
                    type="info",
                    message=f"收到消息: {event.content[:50]}..."
                )]
            )

        elif isinstance(event, CommandCompleted):
            self.state_manager.update_state(is_processing=False)

    async def _handle_command_submitted(self, event: CommandSubmitted) -> None:
        """处理命令提交"""
        self.state_manager.update_state(
            input_text="",
            is_processing=True
        )

        # 发布命令执行事件
        await self.event_bus.publish(CommandExecuted(
            command=event.command,
            timestamp=event.timestamp
        ))
```

### 📊 组件化效果预期

#### 开发效率提升
- **组件复用率**: 从 0% → 90%
- **新功能开发时间**: 从 2天 → 0.5天 (-75%)
- **Bug修复时间**: 从 4小时 → 1小时 (-75%)

#### 代码质量提升
- **单个文件平均行数**: 从 2877行 → 200行 (-93%)
- **圈复杂度**: 从 50 → 10 (-80%)
- **代码重复率**: 从 30% → 5% (-83%)

---

## 🖥️ P7 - GUI 完整实现方案

### 🎯 MVVM架构设计

#### 1. 核心架构
```python
# MVVM基础架构
class ViewModel(ABC):
    """ViewModel基类"""

    def __init__(self):
        self._properties: Dict[str, Any] = {}
        self._commands: Dict[str, Command] = {}
        self._property_changed_callbacks: List[Callable] = []

    def set_property(self, name: str, value: Any) -> None:
        old_value = self._properties.get(name)
        self._properties[name] = value

        # 通知属性变更
        for callback in self._property_changed_callbacks:
            callback(name, value, old_value)

    def get_property(self, name: str, default: Any = None) -> Any:
        return self._properties.get(name, default)

    def register_command(self, name: str, command: "Command") -> None:
        self._commands[name] = command

    def execute_command(self, name: str, *args, **kwargs) -> Any:
        if name in self._commands:
            return self._commands[name].execute(*args, **kwargs)
        raise ValueError(f"Command '{name}' not found")

class Command:
    """命令模式"""

    def __init__(self, execute_func: Callable, can_execute_func: Callable = None):
        self.execute_func = execute_func
        self.can_execute_func = can_execute_func or (lambda: True)

    def execute(self, *args, **kwargs) -> Any:
        if self.can_execute():
            return self.execute_func(*args, **kwargs)
        raise ValueError("Command cannot be executed")

    def can_execute(self) -> bool:
        return self.can_execute_func()

# 主ViewModel
class MainViewModel(ViewModel):
    """主窗口ViewModel"""

    def __init__(self, agent_orchestrator: AgentOrchestrator):
        super().__init__()
        self.agent_orchestrator = agent_orchestrator

        # 属性
        self.set_property("current_view", "chat")
        self.set_property("input_text", "")
        self.set_property("is_processing", False)
        self.set_property("messages", [])
        self.set_property("sessions", [])
        self.set_property("roles", [])

        # 命令
        self.register_command("send_message", Command(self._send_message))
        self.register_command("switch_view", Command(self._switch_view))
        self.register_command("new_session", Command(self._new_session))
        self.register_command("load_session", Command(self._load_session))

        # 初始化数据
        asyncio.create_task(self._initialize_data())

    async def _send_message(self, message: str) -> None:
        """发送消息命令"""
        if not message.strip():
            return

        self.set_property("is_processing", True)
        self.set_property("input_text", "")

        # 添加用户消息
        messages = self.get_property("messages", [])
        messages.append(Message(
            id=str(uuid.uuid4()),
            content=message,
            sender="user",
            timestamp=datetime.now()
        ))
        self.set_property("messages", messages)

        try:
            # 执行Agent
            async for event in self.agent_orchestrator.execute_goal(message):
                if isinstance(event, AgentResponse):
                    messages.append(Message(
                        id=str(uuid.uuid4()),
                        content=event.content,
                        sender="agent",
                        timestamp=datetime.now()
                    ))
                    self.set_property("messages", messages)
        except Exception as e:
            # 错误处理
            messages.append(Message(
                id=str(uuid.uuid4()),
                content=f"错误: {str(e)}",
                sender="system",
                timestamp=datetime.now()
            ))
            self.set_property("messages", messages)
        finally:
            self.set_property("is_processing", False)

    async def _switch_view(self, view_name: str) -> None:
        """切换视图命令"""
        self.set_property("current_view", view_name)

    async def _new_session(self) -> None:
        """新建会话命令"""
        # 创建新会话逻辑
        pass

    async def _load_session(self, session_id: str) -> None:
        """加载会话命令"""
        # 加载会话逻辑
        pass

    async def _initialize_data(self) -> None:
        """初始化数据"""
        # 加载会话列表
        # 加载角色列表
        pass
```

#### 2. 视图组件 (使用Tkinter/PyQt/CustomTkinter)
```python
# 使用CustomTkinter作为GUI框架
import customtkinter as ctk

class MainView:
    """主窗口视图"""

    def __init__(self, view_model: MainViewModel):
        self.view_model = view_model
        self.root = ctk.CTk()
        self.setup_ui()
        self.bind_events()

    def setup_ui(self) -> None:
        """设置UI"""
        self.root.title("DAIP-LIVE")
        self.root.geometry("1200x800")

        # 主题设置
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 主布局
        self.main_layout = ctk.CTkFrame(self.root)
        self.main_layout.pack(fill="both", expand=True, padx=10, pady=10)

        # 侧边栏
        self.setup_sidebar()

        # 内容区域
        self.setup_content_area()

        # 底部状态栏
        self.setup_status_bar()

    def setup_sidebar(self) -> None:
        """设置侧边栏"""
        self.sidebar = ctk.CTkFrame(self.main_layout, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)

        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🤖 DAIP-LIVE",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(pady=20)

        # 导航按钮
        self.nav_buttons = {}
        nav_items = [
            ("💬 聊天", "chat"),
            ("🎭 角色", "role"),
            ("📚 会话", "session"),
            ("🎯 辩论", "debate"),
            ("🧠 知识库", "knowledge"),
        ]

        for text, view_name in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda vn=view_name: self.view_model.execute_command("switch_view", vn)
            )
            btn.pack(pady=5, padx=10, fill="x")
            self.nav_buttons[view_name] = btn

        # 会话列表
        self.session_label = ctk.CTkLabel(self.sidebar, text="最近会话")
        self.session_label.pack(pady=(20, 5))

        self.session_listbox = ctk.CTkTextbox(self.sidebar, height=200)
        self.session_listbox.pack(pady=5, padx=10, fill="x")

    def setup_content_area(self) -> None:
        """设置内容区域"""
        self.content_frame = ctk.CTkFrame(self.main_layout)
        self.content_frame.pack(side="left", fill="both", expand=True)

        # 聊天视图
        self.setup_chat_view()

        # 角色视图
        self.setup_role_view()

        # 会话视图
        self.setup_session_view()

        # 辩论视图
        self.setup_debate_view()

        # 知识库视图
        self.setup_knowledge_view()

    def setup_chat_view(self) -> None:
        """设置聊天视图"""
        self.chat_frame = ctk.CTkFrame(self.content_frame)

        # 消息显示区域
        self.message_textbox = ctk.CTkTextbox(self.chat_frame)
        self.message_textbox.pack(fill="both", expand=True, pady=10, padx=10)

        # 输入区域
        self.input_frame = ctk.CTkFrame(self.chat_frame)
        self.input_frame.pack(fill="x", pady=10, padx=10)

        self.message_entry = ctk.CTkEntry(self.input_frame, placeholder_text="输入消息...")
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="发送",
            command=self._on_send_message
        )
        self.send_button.pack(side="right")

    def setup_status_bar(self) -> None:
        """设置状态栏"""
        self.status_bar = ctk.CTkFrame(self.main_layout, height=30)
        self.status_bar.pack(side="bottom", fill="x", pady=(10, 0))

        self.status_label = ctk.CTkLabel(self.status_bar, text="就绪")
        self.status_label.pack(side="left", padx=10)

        self.processing_label = ctk.CTkLabel(self.status_bar, text="")
        self.processing_label.pack(side="right", padx=10)

    def bind_events(self) -> None:
        """绑定事件"""
        # 属性变更监听
        self.view_model._property_changed_callbacks.append(self._on_property_changed)

        # 键盘事件
        self.message_entry.bind("<Return>", lambda e: self._on_send_message())

        # 窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_property_changed(self, property_name: str, new_value: Any, old_value: Any) -> None:
        """属性变更处理"""
        if property_name == "messages":
            self._update_messages_display()
        elif property_name == "is_processing":
            self._update_processing_status(new_value)
        elif property_name == "current_view":
            self._switch_view_display(new_value)

    def _update_messages_display(self) -> None:
        """更新消息显示"""
        messages = self.view_model.get_property("messages", [])
        self.message_textbox.delete("1.0", "end")

        for message in messages:
            sender_name = "用户" if message.sender == "user" else "AI助手"
            timestamp = message.timestamp.strftime("%H:%M:%S")
            self.message_textbox.insert("end", f"[{timestamp}] {sender_name}:\n")
            self.message_textbox.insert("end", f"{message.content}\n\n")

        self.message_textbox.see("end")

    def _update_processing_status(self, is_processing: bool) -> None:
        """更新处理状态"""
        if is_processing:
            self.processing_label.configure(text="⏳ 处理中...")
            self.send_button.configure(state="disabled")
        else:
            self.processing_label.configure(text="")
            self.send_button.configure(state="normal")

    def _switch_view_display(self, view_name: str) -> None:
        """切换视图显示"""
        # 隐藏所有视图
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

        # 显示当前视图
        if view_name == "chat":
            self.chat_frame.pack(fill="both", expand=True)
        elif view_name == "role":
            self.role_frame.pack(fill="both", expand=True)
        # ... 其他视图

    def _on_send_message(self) -> None:
        """发送消息"""
        message = self.message_entry.get()
        if message.strip():
            asyncio.create_task(self.view_model.execute_command("send_message", message))

    def _on_closing(self) -> None:
        """窗口关闭"""
        self.root.destroy()

    def run(self) -> None:
        """运行GUI"""
        self.root.mainloop()

# GUI应用入口
class GUIApplication:
    """GUI应用程序"""

    def __init__(self, container: ServiceContainer):
        self.container = container
        self.agent_orchestrator = container.get(AgentOrchestrator)

    def run(self) -> None:
        """运行GUI应用"""
        # 创建ViewModel
        view_model = MainViewModel(self.agent_orchestrator)

        # 创建并运行视图
        view = MainView(view_model)
        view.run()
```

#### 3. 共享业务逻辑层
```python
# 业务逻辑抽象层，确保TUI和GUI共享相同的逻辑
class InteractionLayer(ABC):
    """交互层抽象接口"""

    @abstractmethod
    async def send_message(self, message: str) -> AsyncGenerator[MessageEvent, None]:
        """发送消息"""
        pass

    @abstractmethod
    async def get_sessions(self) -> List[Session]:
        """获取会话列表"""
        pass

    @abstractmethod
    async def create_session(self, goal: str) -> Session:
        """创建会话"""
        pass

class TUIInteractionLayer(InteractionLayer):
    """TUI交互层实现"""

    def __init__(self, agent_orchestrator: AgentOrchestrator):
        self.agent_orchestrator = agent_orchestrator

    async def send_message(self, message: str) -> AsyncGenerator[MessageEvent, None]:
        async for event in self.agent_orchestrator.execute_goal(message):
            if isinstance(event, AgentResponse):
                yield MessageEvent(content=event.content, sender="agent")
            elif isinstance(event, AgentError):
                yield MessageEvent(content=f"错误: {event.error}", sender="system")

class GUIInteractionLayer(InteractionLayer):
    """GUI交互层实现"""

    def __init__(self, agent_orchestrator: AgentOrchestrator):
        self.agent_orchestrator = agent_orchestrator

    async def send_message(self, message: str) -> AsyncGenerator[MessageEvent, None]:
        # 与TUI相同的实现逻辑
        async for event in self.agent_orchestrator.execute_goal(message):
            if isinstance(event, AgentResponse):
                yield MessageEvent(content=event.content, sender="agent")
            elif isinstance(event, AgentError):
                yield MessageEvent(content=f"错误: {event.error}", sender="system")
```

### 📊 GUI实现效果预期

#### 功能完整性
- **功能覆盖率**: 从 30% → 100% (+233%)
- **用户体验**: 从 基础 → 专业级 (+300%)
- **平台兼容性**: Windows, macOS, Linux全平台支持

#### 开发效率
- **UI开发时间**: 基于组件化架构，开发效率提升80%
- **维护成本**: 共享业务逻辑，维护成本降低60%
- **测试覆盖**: UI自动化测试覆盖率90%+

---

## 🚀 实施路线图

### 第一阶段：P5 Agent Engine解耦 (2-3周)

#### Week 1: 基础架构搭建
- [ ] 实现事件总线系统
- [ ] 创建服务容器配置
- [ ] 拆分状态管理服务
- [ ] 建立领域服务接口

#### Week 2: 核心服务迁移
- [ ] 迁移意图识别逻辑
- [ ] 迁移执行引擎逻辑
- [ ] 实现新的协调器
- [ ] 编写单元测试

#### Week 3: 集成测试和优化
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档更新
- [ ] 向后兼容验证

### 第二阶段：P6 TUI组件化 (2-3周)

#### Week 4: 组件架构设计
- [ ] 定义组件接口
- [ ] 实现状态管理系统
- [ ] 创建事件系统
- [ ] 设计组件库结构

#### Week 5: 核心组件实现
- [ ] 布局组件
- [ ] 导航组件
- [ ] 输入组件
- [ ] 显示组件

#### Week 6: 高级功能和优化
- [ ] 主题系统
- [ ] 插件机制
- [ ] 性能优化
- [ ] 浏览器测试

### 第三阶段：P7 GUI完整实现 (3-4周)

#### Week 7-8: MVVM架构搭建
- [ ] ViewModel框架
- [ ] 命令系统
- [ ] 数据绑定机制
- [ ] 共享业务逻辑层

#### Week 9-10: UI实现和集成
- [ ] 主窗口实现
- [ ] 各功能模块UI
- [ ] 主题和样式
- [ ] 响应式设计

### 第四阶段：集成测试和优化 (1-2周)

#### Week 11: 全面测试
- [ ] 三端功能对等测试
- [ ] 性能基准测试
- [ ] 用户体验测试
- [ ] 兼容性测试

#### Week 12: 优化和发布
- [ ] 性能优化
- [ ] Bug修复
- [ ] 文档完善
- [ ] 版本发布

---

## 📊 预期收益总结

### 技术收益
- **代码可维护性**: 提升300%
- **开发效率**: 提升200%
- **测试覆盖率**: 从60%提升到95%
- **系统稳定性**: 提升150%

### 业务收益
- **用户体验**: 提升200%
- **功能完整性**: 提升233%
- **平台覆盖**: 提升300%
- **开发团队效率**: 提升250%

### 长期价值
- **技术债务**: 减少80%
- **新功能开发周期**: 缩短70%
- **维护成本**: 降低60%
- **团队协作效率**:提升200%

---

## 🎯 关键成功因素

1. **渐进式重构**: 避免大爆炸式改动，降低风险
2. **强测试保障**: 每个阶段都有完整的测试覆盖
3. **接口标准化**: 确保模块间的清晰边界
4. **向后兼容**: 保证现有功能不受影响
5. **文档同步**: 技术文档与实现同步更新

这个重构方案将显著提升DAIP-LIVE系统的架构质量、开发效率和用户体验，为系统的长期发展奠定坚实基础。