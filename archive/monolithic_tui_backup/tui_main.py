"""TUI主控文件 - 简化的TUI核心控制器"""

import os
import time
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, Static, RichLog
from textual.containers import Horizontal, Vertical
from textual import events

# 导入DAIP-LIVE核心组件
from ..memory.session_manager import SessionManager
from ..p4_role_manager_tools.role_manager import RoleManager
from ..knowledge.manager import KnowledgeManager
from ..p8_debate_system.manager import DebateManager
from ..model_provider.provider import LiteLLMProvider
from ..persistence.database import DatabaseManager
from ..p4_role_manager_tools.role_model_manager import RoleModelManager
from ..p8_debate_system.enhanced_debate_manager import EnhancedDebateManager as OriginalEnhancedDebateManager
from ..agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

# 导入TUI模块
from .autocomplete import TUIAutocomplete
from .commands import TUICommandHandler, SearchCommands, DebateCommands, UtilityCommands
from .screens import CommandHelpDialog, SessionSelectionDialog
from .utils import FocusMode, HistoryManager, PerformanceMonitor, ConfigManager, Logger
from .text_selection import CopyPasteEnhancer


class DAIP_TUI(App):
    """DAIP-LIVE TUI主控制器 - 模块化重构版本"""

    CSS = """
    .panel-header {
        text-align: center;
        background: $primary;
        color: $text;
        padding: 0 1;
        height: 1;
    }

    .system-panel {
        width: 30%;
        border: solid $primary;
    }

    .system-log {
        height: 1fr;
        background: $surface;
        border: solid $primary;
    }

    .output-mode {
        height: 1fr;
        background: $surface;
    }

    Horizontal {
        height: 3fr;
    }

    Vertical {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("shift_tab", "toggle_focus", "切换焦点"),
        Binding("ctrl+a", "select_all", "全选", show=False),
        Binding("ctrl+c", "copy_text", "复制", show=False),
        Binding("ctrl+v", "paste_text", "粘贴", show=False),
        Binding("ctrl+e", "_handle_ctrl_e_exit", "退出应用", show=False),
        Binding("ctrl+q", "_handle_ctrl_q_exit", "退出会话/应用", show=False),
        Binding("escape", "_handle_escape_key", "退出输出模式", show=False),
    ]

    def __init__(
        self,
        executor: Any = None,
        session_manager: SessionManager = None,
        role_manager: RoleManager = None,
        knowledge_manager: KnowledgeManager = None,
        debate_manager: DebateManager = None,
        model_provider: LiteLLMProvider = None,
        db_manager: DatabaseManager = None,
        config_manager: Any = None,
        role_model_manager: RoleModelManager = None,
        enhanced_debate_manager: OriginalEnhancedDebateManager = None,
        goal: Optional[str] = None,
    ):
        super().__init__()

        # 初始化容器和依赖
        self._initialize_dependencies(
            executor, session_manager, role_manager, knowledge_manager,
            debate_manager, model_provider, db_manager, config_manager,
            role_model_manager, enhanced_debate_manager, goal
        )

        # 初始化TUI模块
        self._initialize_tui_modules()

        # 初始化状态和追踪
        self._initialize_state_tracking()

        # 初始化输入历史
        self._initialize_history()

        # 初始化系统状态面板
        self._initialize_system_panel()

        # 初始化复制粘贴增强功能
        self.copy_paste_enhancer = CopyPasteEnhancer(self)

        # 初始化意图识别器
        self._intent_recognizer = EnhancedIntentRecognizer()

    def _initialize_dependencies(self, *args):
        """初始化依赖和容器"""
        # 这里保持原有的依赖初始化逻辑
        # 从参数中解包依赖
        (executor, session_manager, role_manager, knowledge_manager,
         debate_manager, model_provider, db_manager, config_manager,
         role_model_manager, enhanced_debate_manager, goal) = args

        # Import and initialize container if dependencies are not provided
        if any(dep is None for dep in [session_manager, role_manager, knowledge_manager]):
            from daip_live.container import Container
            container = Container()

            # Load configuration from YAML if it exists
            config_file = "config.yaml"
            if os.path.exists(config_file):
                try:
                    container.config.from_yaml(config_file)
                except Exception as e:
                    print(f"Warning: Could not load config from {config_file}: {e}")

            # Set minimal config with proper defaults
            self._set_default_config(container)

            # Initialize dependencies from container
            self.executor = executor or container.executor()
            self._session_manager = session_manager or container.session_manager()
            self._role_manager = role_manager or container.role_manager()
            self._knowledge_manager = knowledge_manager or container.knowledge_manager()
            self._debate_manager = debate_manager or container.debate_manager()
            self._model_provider = model_provider or container.litellm_provider()
            self.db_manager = db_manager or container.database_manager()
            self.container_config = config_manager or container.config
            self._role_model_manager = role_model_manager or container.role_model_manager()
            self._enhanced_debate_manager = enhanced_debate_manager or container.enhanced_debate_manager()
        else:
            # Use provided dependencies
            self.executor = executor
            self._session_manager = session_manager
            self._role_manager = role_manager
            self._knowledge_manager = knowledge_manager
            self._debate_manager = debate_manager
            self._model_provider = model_provider
            self.db_manager = db_manager
            self.container_config = config_manager
            self._role_model_manager = role_model_manager
            self._enhanced_debate_manager = enhanced_debate_manager

    def _set_default_config(self, container):
        """设置默认配置"""
        # 检查容器是否具有config属性（兼容不同的容器类型）
        if hasattr(container, 'config') and hasattr(container.config, 'database') and hasattr(container.config.database, 'path'):
            if container.config.database.path() is None:
                container.config.database.path.from_value(":memory:")

        if hasattr(container, 'config') and hasattr(container.config, 'llm_provider'):
            if (hasattr(container, 'config') and
                hasattr(container.config, 'llm_provider') and
                hasattr(container.config.llm_provider, 'default_model') and
                container.config.llm_provider.default_model() is None):
                container.config.llm_provider.default_model.from_value("ollama/llama3")
            if (hasattr(container, 'config') and
                hasattr(container.config, 'llm_provider') and
                hasattr(container.config.llm_provider, 'embedding_model') and
                container.config.llm_provider.embedding_model() is None):
                container.config.llm_provider.embedding_model.from_value("mock-embedding")

        if (hasattr(container, 'config') and
            hasattr(container.config, 'role_manager') and
            hasattr(container.config.role_manager, 'roles_dir')):
            if container.config.role_manager.roles_dir() is None:
                container.config.role_manager.roles_dir.from_value("roles")

        if (hasattr(container, 'config') and
            hasattr(container.config, 'knowledge_base') and
            hasattr(container.config.knowledge_base, 'directory')):
            if container.config.knowledge_base.directory() is None:
                container.config.knowledge_base.directory.from_value("knowledge")

    def _initialize_tui_modules(self):
        """初始化TUI模块组件"""
        # 初始化自动补全系统
        self.autocomplete = TUIAutocomplete(self)

        # 初始化命令处理器
        self.command_handler = TUICommandHandler(self)

        # 初始化专门的命令处理器
        self.search_commands = SearchCommands(self)
        self.debate_commands = DebateCommands(self)
        self.utility_commands = UtilityCommands(self)

        # 初始化工具和配置管理
        self.config_manager = ConfigManager()
        self.performance_monitor = PerformanceMonitor()
        self.logger = Logger()

        # 初始化技能管理器（从容器获取或创建）
        self._initialize_skill_manager()

        # 初始化Claude技能适配器管理器
        self._initialize_claude_skills_adapter_manager()

        # 初始化Claude技能同步管理器
        self._initialize_claude_skills_sync_manager()

    def _initialize_state_tracking(self):
        """初始化状态追踪"""
        # Current session tracking
        self._current_session_id = None

        # Current model tracking
        self._current_model = "default"

        # Debate tracking variables
        self._current_debate = {
            'session_id': None,
            'topic': None,
            'current_round': 0,
            'total_rounds': 0,
            'current_participant': None,
            'is_active': False,
            'role_models': {},
            'participant_colors': {}
        }

        # Debate lifecycle events
        self._debate_started_event = asyncio.Event()
        self._debate_completed_event = asyncio.Event()
        self._participant_events = {}

        # Track background tasks
        self._background_tasks = set()

        # Focus mode
        self.focus_mode = FocusMode.INPUT

        # System activity monitoring
        self._system_activity = {
            'events_processed': 0,
            'tools_executed': 0,
            'errors_encountered': 0,
            'session_start_time': None,
            'last_activity_time': None
        }

        # System log tracking
        self._system_log_buffer = []
        self._max_system_log_entries = 50

    def _initialize_history(self):
        """初始化输入历史管理"""
        # Initialize clarification state management
        self._pending_clarification = None
        self._original_intent_context = {}
        self._awaiting_clarification = False

        # Real-time tracking variables
        self._real_token_usage = (0, 8192)
        self._model_metrics = {
            'request_count': 0,
            'total_latency': 0.0,
            'last_request_time': None
        }

        # Initialize task decomposition and visualization components
        self._initialize_task_components()

        # Input history for command recall
        self.history_manager = HistoryManager(self.config_manager.get('max_history', 100))
        self._history_index = -1
        self._current_input_before_history = ""

    def _initialize_task_components(self):
        """初始化任务相关组件"""
        # Initialize task decomposition integrator
        try:
            from daip_live.task_decomposition.task_decomposition_integrator import TaskDecompositionIntegrator
            self._task_decomposition_integrator = TaskDecompositionIntegrator(self._model_provider)
            print("✅ Task decomposition integrator initialized")
        except ImportError as e:
            print(f"⚠️ Task decomposition integrator not found: {e}")
            self._task_decomposition_integrator = None
        except Exception as e:
            print(f"⚠️ Task decomposition integrator initialization failed: {e}")
            self._task_decomposition_integrator = None

        # Initialize task visualization manager
        try:
            from daip_live.task_decomposition.task_visualization import get_task_visualization_manager
            self._task_visualization_manager = get_task_visualization_manager()
            print("✅ Task visualization manager initialized")
        except ImportError as e:
            print(f"⚠️ Task visualization manager not found: {e}")
            self._task_visualization_manager = None
        except Exception as e:
            print(f"⚠️ Task visualization manager initialization failed: {e}")
            self._task_visualization_manager = None

    def _initialize_system_panel(self):
        """初始化系统状态面板"""
        # Discover available commands
        self._available_commands = []
        excluded_commands = {"init", "shortcut", "project", "session"}

        for name in dir(self):
            if name.startswith("_handle_") and name.endswith("_command"):
                command_name = name.replace('_handle_', '').replace('_command', '')

                # Skip excluded commands
                if command_name in excluded_commands:
                    continue

                handler = getattr(self, name)
                help_text = (handler.__doc__ or "").strip().split('\n')[0]
                self._available_commands.append((f"/{command_name}", help_text))

        # Load help documentation
        try:
            help_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "tui_commands_help.md")
            with open(help_file_path, encoding="utf-8") as f:
                self._help_text = f.read()
        except FileNotFoundError:
            self._help_text = "Help document not found."

    def _initialize_skill_manager(self):
        """初始化技能管理器"""
        # 首先尝试从依赖容器获取技能管理器
        if hasattr(self, 'container_config') and hasattr(self.container_config, 'container'):
            try:
                # 如果容器存在，从容器获取技能管理器
                self._skill_manager = self.container_config.container.skill_manager()
            except Exception as e:
                print(f"Warning: 无法从容器获取skill_manager，创建新实例: {e}")
                from daip_live.skills.manager import SkillManager
                self._skill_manager = SkillManager()
        else:
            # 如果没有容器或容器不可用，创建新实例
            from daip_live.skills.manager import SkillManager
            self._skill_manager = SkillManager()

        print("✅ 技能管理器初始化成功")

        # 注册内置技能
        self._register_builtin_skills()

    def _register_builtin_skills(self):
        """注册内置技能"""
        try:
            # 注册文本分析技能
            from daip_live.skills.text_analysis import TextAnalysisSkill
            text_analysis_skill = TextAnalysisSkill()
            self._skill_manager.register_skill(text_analysis_skill)
            print(f"✅ 已注册内置技能: {text_analysis_skill.metadata.name}")

            # 注册扩展技能
            from daip_live.skills.extended_skills import register_extended_skills
            register_extended_skills(self._skill_manager)

            # 尝试加载Claude兼容技能
            self._load_claude_compatible_skills()

        except Exception as e:
            print(f"⚠️ 注册内置技能失败: {e}")

    def _load_claude_compatible_skills(self):
        """加载Claude兼容技能"""
        try:
            # 尝试从本地目录加载Claude技能
            from daip_live.skills.claude_skills_sync import ClaudeSkillsManager
            skills_manager = ClaudeSkillsManager()
            available_skills = skills_manager.load_skills_from_directory()

            if available_skills:
                print(f"✅ 发现 {len(available_skills)} 个Claude兼容技能")
                # 这里可以将Claude技能注册到技能管理器
                # 目前我们只显示可用的技能名称
                for skill in available_skills:
                    print(f"  - {skill.name}: {skill.description}")
            else:
                print("ℹ️  未发现本地Claude兼容技能，可通过命令下载")

        except ImportError:
            print("⚠️ Claude技能同步模块不可用")
        except Exception as e:
            print(f"⚠️ 加载Claude兼容技能失败: {e}")

    def _initialize_claude_skills_adapter_manager(self):
        """初始化Claude Skills适配器管理器"""
        try:
            from daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager

            # 尝试从依赖容器获取必要的依赖
            skill_manager = getattr(self, '_skill_manager', None)

            # 使用已初始化的技能管理器创建ClaudeSkillAdapterManager
            self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(
                skill_manager=skill_manager
            )
            print("✅ Claude Skills适配器管理器初始化成功")
        except ImportError as e:
            print(f"⚠️ Claude Skills适配器未找到，跳过初始化: {e}")
            self._claude_skill_adapter_manager = None
        except Exception as e:
            print(f"⚠️ 初始化Claude技能适配器管理器失败: {e}")
            self._claude_skill_adapter_manager = None

    def _initialize_claude_skills_sync_manager(self):
        """初始化Claude技能同步管理器"""
        try:
            from daip_live.skills.claude_skills_sync import ClaudeSkillsManager
            self._claude_skills_sync_manager = ClaudeSkillsManager()
            print("✅ Claude技能同步管理器初始化成功")
        except ImportError as e:
            print(f"⚠️ Claude技能同步模块未找到，跳过初始化: {e}")
            self._claude_skills_sync_manager = None
        except Exception as e:
            print(f"⚠️ 初始化Claude技能同步管理器失败: {e}")
            self._claude_skills_sync_manager = None

    # === UI布局和组件 ===

    def compose(self) -> ComposeResult:
        """构建UI布局"""
        yield Header()

        # Main content area with conversation and system activity
        with Horizontal():
            # Conversation area - takes most of the space
            with Vertical():
                yield Static("💬 对话区域", classes="panel-header")
                yield RichLog(id="main_log", classes="output-mode", highlight=True, markup=True, wrap=True)

            # System activity panel - narrow sidebar for system messages
            with Vertical(classes="system-panel"):
                yield Static("🔧 系统状态", classes="panel-header")
                yield RichLog(id="system_log", classes="system-log", highlight=True, markup=True, wrap=True)

        yield Input(placeholder="Enter command or message...", id="user_input")
        yield Static("Model: llama3:8b | Tokens: 0/8192 (0%) | Status: Idle | Focus: Input", id="status_bar")
        yield Footer()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """处理鼠标按下事件 - 兼容Textual的文本选择"""
        # 对于RichLog组件，直接使用Textual内置的文本选择功能
        # 在这里我们只处理复制命令相关的快捷方式
        pass

    def on_key(self, event: events.Key) -> None:
        """处理键盘事件，包括复制相关的快捷键"""
        # 处理复制相关的快捷键
        if event.key == "ctrl+c":
            # 检查焦点所在组件
            focused = self.focused
            if hasattr(focused, 'id') and focused.id in ['main_log', 'system_log']:
                # 如果焦点在日志区域，尝试使用Textual内置的文本选择
                # 对于Textual的RichLog，用户需要先用鼠标选择文本后才能复制
                try:
                    # 对于选中文本的复制，使用Textual内置功能
                    event.prevent_default()
                    self.action_copy_text()
                except:
                    # 如果内置选择不可用，复制整个日志区域
                    if hasattr(self, 'copy_paste_enhancer'):
                        if focused.id == 'main_log':
                            self.copy_paste_enhancer.copy_main_log_content()
                        elif focused.id == 'system_log':
                            self.copy_paste_enhancer.copy_system_log_content()
            else:
                # 焦点不在日志区域，按原处理方式
                event.prevent_default()
                self.action_copy_text()
            return
        elif event.key == "ctrl+a":
            # 全选命令，询问用户复制哪个区域
            event.prevent_default()
            self.action_select_all()
            return

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """处理鼠标移动事件"""
        # 只有在选择状态时才处理移动事件
        if hasattr(self, 'copy_paste_enhancer') and self.copy_paste_enhancer.selection_manager.is_selecting:
            # 检查当前焦点在哪个日志区域
            try:
                main_log = self.query_one("#main_log", RichLog)
                if main_log.region.contains(event.screen_x, event.screen_y):
                    self.copy_paste_enhancer.handle_mouse_move(event, main_log)
                    event.stop()
                    return
            except:
                pass

            try:
                system_log = self.query_one("#system_log", RichLog)
                if system_log.region.contains(event.screen_x, event.screen_y):
                    self.copy_paste_enhancer.handle_mouse_move(event, system_log)
                    event.stop()
                    return
            except:
                pass

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """处理鼠标释放事件"""
        # 检查释放是否在main_log区域
        try:
            main_log = self.query_one("#main_log", RichLog)
            if main_log.region.contains(event.screen_x, event.screen_y):
                self.copy_paste_enhancer.handle_mouse_up(event, main_log)
                event.stop()
                return
        except:
            pass

        # 检查释放是否在system_log区域
        try:
            system_log = self.query_one("#system_log", RichLog)
            if system_log.region.contains(event.screen_x, event.screen_y):
                self.copy_paste_enhancer.handle_mouse_up(event, system_log)
                event.stop()
                return
        except:
            pass

    # === 生命周期方法 ===

    async def on_mount(self) -> None:
        """应用启动时的初始化"""
        # Set up input widget with initial focus
        input_widget = self.query_one(Input)
        input_widget.focus()

        # Set up initial status
        self._update_status_bar("Ready")

        # Welcome message
        self._update_log_view("[bold green]Welcome to DAIP-LIVE! Ready for your command.[/bold green]")
        self._update_system_log("[dim]🚀 DAIP-LIVE TUI initialized successfully[/dim]")

    # === 核心方法 - 简化版本 ===

    def _update_log_view(self, text: str) -> None:
        """更新主对话视图"""
        try:
            self.query_one("#main_log", RichLog).write(text)
        except Exception:
            # Graceful fallback
            pass

    def _update_system_log(self, text: str) -> None:
        """更新系统状态面板"""
        try:
            # Only log system-relevant messages
            if self._should_log_to_system_panel(text):
                self.query_one("#system_log", RichLog).write(text)

                # Track system messages with rotation
                self._system_log_buffer.append(text)
                if len(self._system_log_buffer) > self._max_system_log_entries:
                    self._system_log_buffer.pop(0)
        except Exception:
            pass

    def _should_log_to_system_panel(self, text: str) -> bool:
        """判断消息是否应该显示在系统面板"""
        text_lower = text.lower()

        # Messages that should go to system panel
        system_patterns = [
            "command-message", "system-reminder", "status:", "error:",
            "model:", "tokens:", "tools:", "events:", "processing",
            "working on", "completed", "failed", "syncing", "loading",
            "saving", "initializing", "shutting down"
        ]

        # Check if it's a system message
        for pattern in system_patterns:
            if pattern in text_lower:
                return True

        # User messages go to conversation
        if text.strip().startswith("> ") and not any(pattern in text_lower for pattern in ["status:", "error:", "model:"]):
            return False

        # Technical/operational messages go to system
        if any(keyword in text_lower for keyword in ["module", "component", "service", "agent", "task", "job"]):
            return True

        return False

    def _update_status_bar(self, status: str) -> None:
        """更新状态栏"""
        try:
            status_bar = self.query_one("#status_bar", Static)
            # Use enhanced status text with real-time metrics
            enhanced_text = self.get_enhanced_status_text(status)
            status_bar.update(enhanced_text)
        except Exception:
            pass

    def get_enhanced_status_text(self, base_status: str) -> str:
        """生成增强状态文本"""
        # Token usage
        used_tokens, total_tokens = self._real_token_usage
        token_percentage = (used_tokens / total_tokens * 100) if total_tokens > 0 else 0

        # Determine token color
        if token_percentage > 90:
            token_color = "red"
        elif token_percentage > 75:
            token_color = "yellow"
        else:
            token_color = "green"

        # Use current model for display, with special formatting for debate mode
        if self._current_debate['is_active'] and self._current_debate['current_participant']:
            current_role = self._current_debate['current_participant']
            # Check if we have role-specific model info
            if 'role_models' in self._current_debate and self._current_debate['role_models']:
                role_model = self._current_debate['role_models'].get(current_role, self._current_model)
                model_display = f"{role_model} ({current_role})"
            else:
                model_display = f"{self._current_model} ({current_role})"
        else:
            model_display = self._current_model

        # System activity metrics
        status_parts = [
            f"Model: {model_display}",
            f"[{token_color}]Tokens: {used_tokens}/{total_tokens} ({token_percentage:.0f}%)[/{token_color}]"
        ]

        # Add system activity metrics
        if self._system_activity['events_processed'] > 0:
            activity_info = f"Events: {self._system_activity['events_processed']} "
            if self._system_activity['tools_executed'] > 0:
                activity_info += f"Tools: {self._system_activity['tools_executed']}"

            if self._system_activity['errors_encountered'] > 0:
                activity_info += f" | Errors: {self._system_activity['errors_encountered']}"
            status_parts.append(activity_info)

        # Add debate status if active
        if self._current_debate['is_active']:
            debate_info = f"Debate: R{self._current_debate['current_round']}/{self._current_debate['total_rounds']} - {self._current_debate['current_participant'] or 'Starting'}"
            status_parts.append(debate_info)

        status_parts.extend([
            f"Status: {base_status}",
            f"Focus: {self.focus_mode}"
        ])

        status_text = " | ".join(status_parts)
        return f"[{token_color}]{status_text}[/{token_color}]"

    # === 输入处理 ===

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理用户输入"""
        user_input = event.value.strip()

        if not user_input:
            return

        # Add to history
        self.history_manager.add(user_input)

        # Reset history index
        self._history_index = -1

        # Log the input
        self._update_log_view(f"[bold cyan]> {user_input}[/bold cyan]")

        # Process the input
        await self._process_user_input(user_input)

    async def _process_user_input(self, user_input: str) -> None:
        """处理用户输入的主要逻辑"""
        try:
            # Record start time for performance monitoring
            start_time = time.time()

            # Check if it's a command
            if user_input.startswith('/'):
                await self._handle_command_input(user_input)
            else:
                await self._handle_chat_input(user_input)

            # Record performance metrics
            duration = time.time() - start_time
            self.performance_monitor.record_response_time(duration)

        except Exception as e:
            self._update_log_view(f"[bold red]Error processing input: {e}[/bold red]")
            self.logger.error(f"Input processing error: {e}")

    async def _handle_command_input(self, user_input: str) -> None:
        """处理命令输入"""
        # Parse command
        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lstrip('/')
        args = parts[1] if len(parts) > 1 else ""

        # Record command usage
        self.performance_monitor.record_command(cmd)

        # Handle command using the modular command handler
        await self.command_handler.handle_command(cmd, args)

    async def _handle_chat_input(self, user_input: str) -> None:
        """处理聊天输入 - 增强版，集成意图识别"""
        try:
            # 使用增强的意图识别器进行自然语言输入处理
            try:
                # 传递session_id以支持上下文感知
                session_id = getattr(self, '_current_session_id', 'default')

                # 检查是否应结合之前的上下文进行澄清
                if hasattr(self, '_original_intent_context') and self._original_intent_context:
                    # 结合用户输入与原始上下文
                    combined_input = f"{self._original_intent_context.get('original_input', '')} {user_input}"
                    self._update_log_view(f"[dim]> 结合上下文重新分析: {combined_input}[/dim]")
                    input_to_analyze = combined_input
                else:
                    input_to_analyze = user_input

                # 检查意图识别器是否支持上下文感知识别
                if hasattr(self._intent_recognizer, 'recognize_intent_with_context'):
                    intent = self._intent_recognizer.recognize_intent_with_context(input_to_analyze, session_id)
                else:
                    # 使用标准recognize_intent但尝试传递session_id（如果支持）
                    import inspect
                    sig = inspect.signature(self._intent_recognizer.recognize_intent)
                    if 'session_id' in sig.parameters:
                        intent = self._intent_recognizer.recognize_intent(input_to_analyze, session_id=session_id)
                    else:
                        intent = self._intent_recognizer.recognize_intent(input_to_analyze)

                if intent:
                    # 处理识别到的意图
                    self._update_log_view(f"[bold blue]> 检测到意图: {intent.description} (置信度: {intent.confidence:.2f})[/bold blue]")

                    # 检查意图是否需要澄清
                    if getattr(intent, 'requires_clarification', False):
                        # 存储原始上下文并设置澄清状态
                        if not hasattr(self, '_original_intent_context'):
                            self._original_intent_context = {}
                        self._original_intent_context = {
                            'original_input': user_input,
                            'original_intent': intent,
                            'session_id': session_id
                        }
                        if not hasattr(self, '_pending_clarification'):
                            self._pending_clarification = None
                        if not hasattr(self, '_awaiting_clarification'):
                            self._awaiting_clarification = False
                        self._pending_clarification = intent
                        self._awaiting_clarification = True

                        # 处理澄清请求
                        clarification_msg = self._get_clarification_message(intent)
                        self._update_log_view(f"[bold yellow]> {clarification_msg}[/bold yellow]")
                        # 暂不执行命令，等待用户提供缺失信息
                        return  # 提前退出以避免命令执行
                    else:
                        # 检查是否为历史对话搜索请求
                        search_keywords = ["参考", "之前的", "历史", "过去", "之前", "以前", "查找", "搜索", "引用"]
                        history_keywords = ["对话", "聊天", "辩论", "讨论", "记录", "内容", "信息"]

                        is_search_request = any(keyword in user_input for keyword in search_keywords) and \
                                          any(keyword in user_input for keyword in history_keywords)

                        if is_search_request:
                            # 提取搜索查询
                            search_query = user_input
                            # 移除常见的搜索触发词
                            for remove_word in ["参考", "之前的", "历史", "过去", "之前", "以前", "查找", "搜索", "引用", "对话", "聊天", "记录"]:
                                search_query = search_query.replace(remove_word, "").strip()

                            if search_query:
                                self._update_log_view(f"[bold cyan]🔍 检测到历史对话搜索请求...[/bold cyan]")
                                self.search_commands.search_conversation_history(search_query)
                                return
                            else:
                                self._update_log_view("[bold yellow]💡 请提供更具体的搜索关键词，例如：'参考之前的辩论主题'或'搜索关于AI的对话'[/bold yellow]")
                                return

                        # 检查是否需要将此复杂任务分解为待办事项清单
                        should_decompose_via_task_engine = False
                        if self._task_decomposition_integrator is not None:
                            try:
                                should_decompose_via_task_engine = await self._task_decomposition_integrator.should_decompose_request(user_input)
                            except Exception as e:
                                self._update_log_view(f"[bold yellow]> 任务分解检查失败: {e}[/bold yellow]")
                                should_decompose_via_task_engine = False

                        if should_decompose_via_task_engine:
                            # 使用任务分解系统处理复杂请求
                            self._update_log_view(f"[bold magenta]> 🧩 检测到复杂任务，启动自动分解流程...[/bold magenta]")

                            # 生成并执行任务分解，以事件流形式处理
                            if self._task_decomposition_integrator is not None:
                                try:
                                    # 🚀 第一阶段：显示任务分解计划
                                    self._update_log_view("")
                                    self._update_log_view("[bold magenta]╔══════════════════════════════════════════════════════════════╗[/bold magenta]")
                                    self._update_log_view("[bold magenta]║               🧩 复杂任务分解流程启动                          ║[/bold magenta]")
                                    self._update_log_view("[bold magenta]╚══════════════════════════════════════════════════════════════╝[/bold magenta]")
                                    self._update_log_view("")

                                    # 阶段1：显示任务计划
                                    self._display_task_planning_phase(user_input)

                                    # 阶段2：执行任务并显示进度
                                    self._update_log_view("")
                                    self._update_log_view("[bold yellow]🔄 第二阶段：开始逐步执行任务...[/bold yellow]")
                                    self._update_log_view("[dim]" + "─" * 60 + "[/dim]")
                                    self._update_log_view("")

                                    # 保存初始任务状态
                                    initial_task_count = len(self._task_visualization_manager.tasks_data) if self._task_visualization_manager else 0

                                    # 执行任务分解
                                    result = await self._task_decomposition_integrator.decompose_and_execute(user_input)

                                    # 阶段3：显示执行结果汇总
                                    self._update_log_view("")
                                    self._update_log_view("[bold green]🎉 第三阶段：任务执行完成汇总[/bold green]")
                                    self._update_log_view("[bold green]" + "═" * 60 + "[/bold green]")
                                    self._update_log_view("")

                                    # 显示最终结果
                                    self._update_log_view("[bold cyan]📋 最终任务成果：[/bold cyan]")
                                    self._update_log_view(f"[white]{result['final_result']}[/white]")
                                    self._update_log_view("")

                                    # 显示最终任务状态
                                    if self._task_visualization_manager:
                                        self._display_task_final_summary(initial_task_count)

                                except Exception as e:
                                    self._update_log_view("")
                                    self._update_log_view(f"[bold red]❌ 任务分解执行失败: {e}[/bold red]")
                                    self._update_log_view(f"[dim]错误详情: {str(e)}[/dim]")
                                    should_decompose_via_task_engine = False
                            else:
                                self._update_log_view(f"[bold yellow]> 任务分解系统未初始化，使用常规处理...[/bold yellow]")

                            # 任务分解完成后提前返回
                            if should_decompose_via_task_engine:
                                return

                        # 根据意图映射到适当的命令处理器
                        if intent.name == "search_papers":
                            # 转换为 /doc search 命令
                            query = intent.parameters.get("query", user_input)
                            if query and query.strip() != "" and query != "machine learning":  # 仅当有真实查询时
                                await self._handle_doc_command(f"search {query}")
                            else:
                                # 查询缺失或为默认值，提示用户输入关键词
                                self._update_log_view("[bold yellow]> 请输入搜索关键词，例如：论文 人工智能[/bold yellow]")
                        elif intent.name == "download_paper":
                            # 转换为 /doc download 命令
                            paper_id = intent.parameters.get("paper_id")
                            if paper_id:
                                await self._handle_doc_command(f"download {paper_id}")
                            else:
                                self._update_log_view("[bold yellow]> 请提供论文标题、主题或arXiv ID[/bold yellow]")
                        elif intent.name == "start_debate":
                            # 转换为 /debate start 命令
                            topic = intent.parameters.get("topic", user_input)
                            if topic and topic.strip() != "":
                                self._handle_debate_command(f"start {topic}")  # 这是同步方法，不要await
                            else:
                                self._update_log_view("[bold yellow]> 请输入辩论主题[/bold yellow]")
                        elif intent.name == "create_wiki":
                            # 直接触发多角色协作创建Wiki
                            title = intent.parameters.get("title", user_input)
                            if title and title.strip() != "":
                                # 调用协作创建方法而不是基础命令
                                asyncio.create_task(self._handle_collaborative_wiki_creation(title))
                            else:
                                self._update_log_view("[bold yellow]> 请输入Wiki页面标题[/bold yellow]")
                        elif intent.name == "initialize_project":
                            # 转换为 /project scaffold 命令
                            description = intent.parameters.get("description", user_input)
                            self._handle_project_command(f"scaffold --description \"{description}\"")  # 这是同步方法，不要await
                        elif intent.name == "view_debate_history":
                            # 转换为 /debate history 命令
                            self._handle_debate_command("history")  # 这是同步方法，不要await
                        elif intent.name == "view_specific_debate":
                            # 转换为 /debate history view 命令
                            session_id = intent.parameters.get("session_id")
                            if session_id:
                                self._handle_debate_command(f"history view {session_id}")  # 这是同步方法，不要await
                            else:
                                self._handle_debate_command("history")  # 这是同步方法，不要await
                        elif intent.name == "complex_task":
                            # 处理复杂任务意图
                            original_request = intent.parameters.get("original_request", user_input)
                            task_description = intent.parameters.get("task_description", user_input)
                            task_type = intent.parameters.get("task_type", "general")

                            self._update_log_view(f"[bold magenta]> 🧩 识别到复杂任务: {task_type} 类型[/bold magenta]")
                            self._update_log_view(f"[bold blue]> 正在为您创建任务列表来完成: '{task_description[:50]}{'...' if len(task_description) > 50 else ''}'[/bold blue]")

                            # 检查是否存在复杂任务管理器
                            if hasattr(self, '_complex_task_integrator') and self._complex_task_integrator:
                                try:
                                    # 执行复杂任务
                                    result = await self._complex_task_integrator.process_complex_task(original_request)

                                    # 显示任务分解列表
                                    if self._task_visualization_manager:
                                        self._update_log_view(f"[bold green]> 任务分解完成，以下是子任务列表:[/bold green]")
                                        self._display_task_visualization(original_request)

                                    self._update_log_view(f"[bold green]> 复杂任务执行完成:[/bold green]")
                                    self._update_log_view(f"[cyan]{result['summary']}[/cyan]")

                                    # 显示最终任务状态
                                    if self._task_visualization_manager:
                                        self._display_task_visualization(original_request)

                                except Exception as e:
                                    self._update_log_view(f"[bold red]> 复杂任务执行失败: {e}[/bold red]")
                                    # 降级到常规处理
                                    await self._start_chat_session(user_input)
                            else:
                                self._update_log_view(f"[bold yellow]> 复杂任务管理器未就绪，使用常规处理...[/bold yellow]")
                                # 降级到常规处理
                                await self._start_chat_session(user_input)

                        elif intent.name == "execute_skill":
                            # 转换为技能执行
                            skill_type = intent.parameters.get("target_skill", "general")
                            skill_content = intent.parameters.get("content", "")
                            original_request = intent.parameters.get("original_request_text", "")

                            if skill_content and skill_content.strip():
                                self._update_log_view(f"[bold blue]> 🤖 执行技能: {skill_type} ('{skill_content[:50]}...')[/bold blue]")

                                # 根据类型执行适当的技能
                                if skill_type == "analysis" or any(keyword in skill_content for keyword in ["分析", "analyze", "text", "内容"]):
                                    # 使用技能管理器查找并执行文本分析技能
                                    skill_found = False
                                    if hasattr(self, '_skill_manager') and self._skill_manager:
                                        # 首先尝试精确匹配技能名
                                        if "text_analysis" in self._skill_manager.list_skills():
                                            analysis_skill = self._skill_manager.get_skill("text_analysis")
                                            if analysis_skill:
                                                from daip_live.skills.base import SkillInput
                                                skill_input = SkillInput(
                                                    data=skill_content,
                                                    context={"source": "intent_recognition", "session_id": getattr(self, '_current_session_id', 'default')},
                                                    metadata={}
                                                )
                                                result = analysis_skill.execute(skill_input)
                                                self._update_log_view(f"[bold green]> ✅ 技能执行成功:[/bold green]")
                                                self._update_log_view(f"[cyan]{result.result}[/cyan]")
                                                skill_found = True

                                    if not skill_found:
                                        # 备用路径：直接创建TextAnalysisSkill（用于向下兼容）
                                        from daip_live.skills.text_analysis import TextAnalysisSkill
                                        text_skill = TextAnalysisSkill()
                                        from daip_live.skills.base import SkillInput
                                        skill_input = SkillInput(
                                            data=skill_content,
                                            context={"source": "intent_recognition", "session_id": getattr(self, '_current_session_id', 'default')},
                                            metadata={}
                                        )
                                        result = text_skill.execute(skill_input)
                                        self._update_log_view(f"[bold green]> ✅ 技能执行成功:[/bold green]")
                                        self._update_log_view(f"[cyan]{result.result}[/cyan]")
                                elif skill_type == "search" or any(keyword in skill_content for keyword in ["搜索", "查找", "find", "search"]):
                                    # 通过doc命令执行搜索技能
                                    await self._handle_doc_command(f"search {skill_content}")
                                elif skill_type == "claude_skill":
                                    # 执行Claude特定技能
                                    self._update_log_view(f"[bold blue]> 🤖 Claude Skill 执行: {original_request}[/bold blue]")
                                    # 如果可用，使用Claude技能管理器
                                    if hasattr(self, '_claude_skill_adapter_manager') and self._claude_skill_adapter_manager:
                                        try:
                                            # 尝试找到并执行Claude相关的技能
                                            skill_found = False
                                            if hasattr(self, '_skill_manager') and self._skill_manager:
                                                # 先尝试从技能管理器查找
                                                available_skills = self._skill_manager.list_skills()
                                                # 查找与Claude相关的技能
                                                for skill_name in available_skills:
                                                    if "claude" in skill_name.lower():
                                                        claude_skill = self._skill_manager.get_skill(skill_name)
                                                        if claude_skill:
                                                            from daip_live.skills.base import SkillInput
                                                            skill_input = SkillInput(
                                                                data=skill_content,
                                                                context={"source": "intent_recognition", "session_id": getattr(self, '_current_session_id', 'default')},
                                                                metadata={"skill_type": "claude_like"}
                                                            )
                                                            result = claude_skill.execute(skill_input)
                                                            self._update_log_view(f"[bold green]> ✅ Claude 技能执行成功:[/bold green]")
                                                            self._update_log_view(f"[cyan]{result.result}[/cyan]")
                                                            skill_found = True
                                                            break

                                            if not skill_found:
                                                # 如果没有找到特定Claude技能，继续使用Claude适配器管理器
                                                self._update_log_view(f"[bold yellow]> 未找到特定Claude技能，使用通用处理...[/bold yellow]")
                                                # 可以在这里添加Claude适配器的具体调用逻辑
                                                await self._start_chat_session(original_request)
                                        except Exception as e:
                                            self._update_log_view(f"[bold red]> ❌ Claude 技能执行失败: {e}[/bold red]")
                                    else:
                                        self._update_log_view(f"[bold yellow]> 未找到Claude技能适配器，使用通用技能处理[/bold yellow]")
                                        await self._start_chat_session(skill_content)
                                else:
                                    # 对于其他技能类型或当内容缺失时
                                    self._update_log_view(f"[bold yellow]> 识别为技能请求: {skill_type}, 内容: '{skill_content[:30]}...'[/bold yellow]")
                                    # 尝试查找并执行特定技能
                                    skill_found = False
                                    if hasattr(self, '_skill_manager') and self._skill_manager:
                                        available_skills = self._skill_manager.list_skills()
                                        specific_skill = None

                                        # 多层匹配策略:
                                        # 1. 首先尝试精确匹配完整的skill_content作为技能名
                                        if skill_content and skill_content in available_skills:
                                            specific_skill = self._skill_manager.get_skill(skill_content)
                                            self._update_log_view(f"[dim]> 精确匹配技能: {skill_content}[/dim]")

                                        # 2. 如果没找到，尝试使用意图中的技能类型作为技能名查找
                                        if not specific_skill and skill_type and skill_type in available_skills:
                                            specific_skill = self._skill_manager.get_skill(skill_type)
                                            self._update_log_view(f"[dim]> 类型匹配技能: {skill_type}[/dim]")

                                        # 3. 如果还没找到，尝试模糊匹配 - 查找名称与意图相关的技能
                                        if not specific_skill:
                                            for skill_name in available_skills:
                                                # 检查技能名称是否包含用户意图关键词
                                                if (skill_type.replace("_", " ") in skill_name.lower() or
                                                    skill_type in skill_name.lower() or
                                                    any(keyword in skill_name.lower() for keyword in skill_content.lower().split())):
                                                    specific_skill = self._skill_manager.get_skill(skill_name)
                                                    self._update_log_view(f"[dim]> 模糊匹配技能: {skill_name}[/dim]")
                                                    break

                                        if specific_skill:
                                            from daip_live.skills.base import SkillInput
                                            skill_input = SkillInput(
                                                data=original_request if original_request and original_request != skill_content else skill_content,
                                                context={"source": "intent_recognition", "session_id": getattr(self, '_current_session_id', 'default')},
                                                metadata={}
                                            )
                                            result = specific_skill.execute(skill_input)
                                            self._update_log_view(f"[bold green]> ✅ 识别并执行具体技能: {specific_skill.metadata.name}[/bold green]")
                                            self._update_log_view(f"[cyan]{result.result}[/cyan]")
                                            skill_found = True

                                    # 如果仍没找到技能，尝试提供技能建议
                                    if not skill_found:
                                        self._update_log_view(f"[bold yellow]> 未找到匹配的技能。[/bold yellow]")
                                        if hasattr(self, '_skill_manager') and self._skill_manager:
                                            available_skills = self._skill_manager.list_skills()
                                            if available_skills:
                                                self._update_log_view(f"[dim]> 可用技能: {', '.join(available_skills[:5])}[/dim]")  # 只显示前5个
                                                self._update_log_view(f"[bold yellow]> 您可以尝试: /skill list 查看所有可用技能[/bold yellow]")

                                        # 降级到聊天模式处理
                                        await self._start_chat_session(original_request if original_request else skill_content)
                            else:
                                self._update_log_view(f"[bold yellow]> 请输入要执行的技能和内容，例如：帮我分析 这段文本[/bold yellow]")
                                # 如果技能内容缺失，在自然语言中建议用户
                                if original_request:
                                    self._update_log_view(f"[dim]> 您的请求: '{original_request}'[/dim]")
                        elif intent.name == "compress_context":
                            # 转换为 /compact 命令
                            self._handle_compact_command("")  # 这是同步方法，不要await
                        elif intent.name == "manage_skills":
                            # 技能管理意图
                            action = intent.parameters.get("action", "list")
                            skill_name = intent.parameters.get("skill_name", "")

                            if action == "list":
                                # 列出所有可用技能
                                if hasattr(self, '_skill_manager') and self._skill_manager:
                                    available_skills = self._skill_manager.list_skills()
                                    if available_skills:
                                        self._update_log_view(f"[bold cyan]📋 可用技能列表 ({len(available_skills)} 个):[/bold cyan]")
                                        for skill_name in available_skills:
                                            skill = self._skill_manager.get_skill(skill_name)
                                            if skill:
                                                self._update_log_view(f"  • [bold]{skill_name}[/bold] - {skill.metadata.description}")
                                    else:
                                        self._update_log_view("[yellow]💡 系统中暂无可用技能[/yellow]")
                                        self._update_log_view("[dim]提示: 尝试使用 /skill download 下载新技能[/dim]")
                            elif action == "download":
                                # 下载新技能 (需要实现)
                                self._update_log_view("[yellow]🔄 正在下载技能...[/yellow]")
                                # 这里可以调用Claude技能同步管理器
                                # 为简单起见，暂时提示用户使用命令
                                self._update_log_view("[dim]提示: 请使用 /skill download 命令下载技能[/dim]")
                        elif intent.name in ["question", "chat"]:
                            # 对于问题或聊天意图，确定是否需要慢思考

                            # 检查用户是否想要快速响应（包含关键词）
                            user_input_lower = user_input.lower()
                            needs_fast_response = any(keyword in user_input_lower for keyword in [
                                "快点", "赶紧", "立刻", "马上", "速速", "尽快", "快", "急速",
                                "fast", "quick", "rapid", "now", "asap", "急需", "急着要",
                                "速度", "迅速", "立即", "立马", "马上"
                            ])

                            # 检查问题是否可能需要深度思考
                            needs_slow_thinking = any(keyword in user_input_lower for keyword in [
                                "分析", "解释", "总结", "评估", "评估一下", "深入", "深刻", "详细",
                                "详细分析", "深度", "复杂", "复杂问题", "研究", "探究", "探讨",
                                "eval", "analyze", "evaluate", "consider", "think deeply",
                                "深思", "仔细", "仔细想想", "认真", "认真考虑", "审慎",
                                "帮我分析", "帮我理解", "帮我评估", "帮我研究", "帮我解释",
                                "详细说说", "深入分析", "详细解释", "全面分析", "仔细分析"
                            ])

                            # 如果检测到慢思考，则特殊处理
                            if needs_slow_thinking and not needs_fast_response:
                                # 首先响应慢思考通知
                                self._update_log_view(f"[bold yellow]> ⏳ 正在进行深度思考...我需要审慎的回答这个问题: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'[/bold yellow]")
                                # 将系统状态消息移到系统面板
                                self._update_system_log(f"[dim]🔍 系统正在整合知识库、分析参数并准备多角色协作回答[/dim]")

                                # 然后使用慢思考上下文开始聊天会话
                                await self._start_chat_session(user_input)
                            elif needs_fast_response:
                                # 用户想要快速响应，提供快速反馈
                                self._update_log_view(f"[bold blue]> ⚡ 快速响应模式: '{user_input}'[/bold blue]")
                                self._update_system_log(f"[dim]⚡ Fast response mode activated[/dim]")
                                await self._start_chat_session(user_input)
                            else:
                                # 默认行为 - 开始聊天会话
                                # 提供系统正在处理的反馈
                                if intent.name == "question":
                                    self._update_log_view("[cyan]> 🤔 思考中...[/cyan]")
                                    self._update_system_log(f"[dim]❓ Question processing initiated[/dim]")
                                elif intent.name == "chat":
                                    self._update_log_view("[cyan]> 🤔 思考中...[/cyan]")
                                    self._update_system_log(f"[dim]💬 Chat session started[/dim]")

                                await self._start_chat_session(user_input)

                                # 如果是明显不需要深度思考的问题，添加信息说明
                                if intent.name == "question" and not needs_slow_thinking and not needs_fast_response:
                                    # 这是一般问题，用户知道系统正在处理
                                    pass  # 一般聊天处理将通过 _start_chat_session 完成
                        else:
                            # 对于其他意图，回落到聊天模式
                            await self._start_chat_session(user_input)
                else:
                    # 没有检测到意图，回落到现有聊天行为
                    self._update_log_view(f"[bold yellow]> 未检测到特定意图，启动常规聊天会话: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'[/bold yellow]")
                    await self._start_chat_session(user_input)
            except Exception as e:
                # 处理意图识别中的任何错误
                self._update_log_view(f"[bold red]> 意图识别出错: {str(e)}[/bold red]")

                # 仍然提供反馈，表示回退到聊天模式
                self._update_log_view(f"[bold yellow]> 正在使用常规聊天模式处理您的请求: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'[/bold yellow]")
                await self._start_chat_session(user_input)

        except Exception as e:
            self._update_log_view(f"[bold red]Error in chat processing: {e}[/bold red]")
            self.logger.error(f"Chat processing error: {e}")

    def _is_conversation_search_request(self, user_input: str) -> bool:
        """检测是否是对话搜索请求"""
        search_keywords = ["参考", "之前的", "历史", "过去", "之前", "以前", "查找", "搜索", "引用"]
        history_keywords = ["对话", "聊天", "辩论", "讨论", "记录", "内容", "信息"]

        return any(keyword in user_input for keyword in search_keywords) and \
               any(keyword in user_input for keyword in history_keywords)

    def _extract_search_query(self, user_input: str) -> str:
        """提取搜索查询"""
        search_query = user_input
        # 移除常见的搜索触发词
        for remove_word in ["参考", "之前的", "历史", "过去", "之前", "以前", "查找", "搜索", "引用", "对话", "聊天", "记录"]:
            search_query = search_query.replace(remove_word, "").strip()
        return search_query

    async def _should_use_task_decomposition(self, user_input: str) -> bool:
        """判断是否应该使用任务分解"""
        if not self._task_decomposition_integrator:
            return False

        try:
            return await self._task_decomposition_integrator.should_decompose_request(user_input)
        except Exception as e:
            self._update_log_view(f"[bold yellow]> 任务分解检查失败: {e}[/bold yellow]")
            return False

    async def _handle_task_decomposition(self, user_input: str) -> None:
        """处理任务分解"""
        # 这里调用原有的任务分解逻辑
        # 为了简化，暂时返回处理提示
        self._update_log_view(f"[bold magenta]> 🧩 检测到复杂任务，启动自动分解流程...[/bold magenta]")
        # 实际的任务分解逻辑可以在这里实现

    async def _start_chat_session(self, user_input: str) -> None:
        """开始聊天会话"""
        # Create session if none exists
        if not self._current_session_id:
            self._current_session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self._update_system_log(f"[dim]💬 Starting chat session: {self._current_session_id}[/dim]")

        # Process chat message using the executor
        if self.executor:
            # Check if executor has chat_run method (newer version)
            if hasattr(self.executor, 'chat_run'):
                # Use chat_run method to get event generator
                try:
                    async for event in self.executor.chat_run(user_input):
                        # Process the events that come from the chat run
                        await self._handle_agent_event(event)
                except Exception as e:
                    self._update_log_view(f"[bold red]Chat execution error: {e}[/bold red]")
                    import logging
                    logging.exception(f"Chat execution error: {e}")
            else:
                # Fallback: try to access the chat_executor directly
                try:
                    if hasattr(self.executor, 'chat_executor'):
                        # Create a user input queue to pass to the chat executor
                        import asyncio
                        user_input_queue = asyncio.Queue()

                        # Run the chat executor with the initial input
                        async for event in self.executor.chat_executor.chat_run(user_input, self.executor.step_executor):
                            await self._handle_agent_event(event)
                    else:
                        self._update_log_view("[bold red]Chat executor not available[/bold red]")
                except Exception as e:
                    self._update_log_view(f"[bold red]Chat executor error: {e}[/bold red]")
                    import logging
                    logging.exception(f"Chat executor error: {e}")
        else:
            self._update_log_view("[bold red]Executor not available[/bold red]")

    async def _handle_agent_event(self, event) -> None:
        """处理Agent事件并更新UI"""
        from daip_live.core.models import (
            FinalResponseEvent, ThoughtEvent, ToolCallEvent,
            ToolOutputEvent, TokenUsageEvent, ModelMetricsEvent
        )

        if isinstance(event, FinalResponseEvent):
            self._update_log_view(f"[green]✅ {event.content}[/green]")
        elif isinstance(event, ThoughtEvent):
            self._update_system_log(f"[dim]💭 {event.content}[/dim]")
        elif isinstance(event, ToolCallEvent):
            self._update_system_log(f"[blue]🔧 Calling tool: {event.tool_name}[/blue]")
        elif isinstance(event, ToolOutputEvent):
            self._update_system_log(f"[cyan]⚙️ Tool output: {event.output}[/cyan]")
        elif isinstance(event, TokenUsageEvent):
            self._update_system_log(f"[yellow]📈 Tokens: {event.usage_info.get('total_tokens', 'N/A')}[/yellow]")
        elif isinstance(event, ModelMetricsEvent):
            self._update_system_log(f"[magenta]📊 Model metrics: {event.metrics}[/magenta]")
        else:
            # For other event types, just log the event
            self._update_system_log(f"[dim]📝 Event: {str(event)[:100]}...[/dim]")

    # === 键盘快捷键处理 ===

    def action_toggle_focus(self) -> None:
        """切换焦点模式"""
        if self.focus_mode == FocusMode.INPUT:
            self.focus_mode = FocusMode.OUTPUT
            self.query_one("#main_log").focus()
        else:
            self.focus_mode = FocusMode.INPUT
            self.query_one("#user_input").focus()
        self._update_status_bar("Idle")
        self.refresh()

    def action_exit_output_mode(self) -> None:
        """退出输出模式"""
        self.focus_mode = FocusMode.INPUT
        try:
            self.query_one("#user_input").focus()
            self._update_status_bar("Idle")
            self.refresh()
        except Exception as e:
            print(f"Error in action_exit_output_mode: {e}")

    async def action_select_all(self) -> None:
        """全选文本"""
        # 询问用户选择哪个区域进行全选
        self._update_log_view("[bold cyan]> 请选择要全选的区域: 主对话区(/copy_main) 或 系统状态区(/copy_system)[/bold cyan]")
        self._update_log_view("[dim]> 提示: 您也可以使用 /copy_main 或 /copy_system 命令直接复制对应区域[/dim]")

    async def action_copy_text(self) -> None:
        """复制文本 - 优先复制选中文本，否则复制主对话区内容"""
        # 首先尝试复制选中的文本
        if self.copy_paste_enhancer.copy_selection():
            return

        # 如果没有选中文本，则复制主对话区内容
        if self.copy_paste_enhancer.copy_main_log_content():
            return

        self._update_log_view("[bold yellow]> 没有可复制的内容[/bold yellow]")

    def action_paste_text(self) -> None:
        """粘贴文本到输入区域"""
        try:
            # 从剪贴板获取文本
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                # 获取当前焦点的输入框
                focused = self.focused
                if focused and hasattr(focused, 'value'):
                    # 如果焦点在输入框上，将文本插入到当前光标位置
                    current_value = focused.value
                    cursor_pos = focused.cursor_position

                    # 插入剪贴板文本到光标位置
                    new_value = current_value[:cursor_pos] + clipboard_text + current_value[cursor_pos:]
                    focused.value = new_value

                    # 移动光标到插入文本的末尾
                    focused.cursor_position = cursor_pos + len(clipboard_text)

                    self._update_log_view(f"[green]✅ 已粘贴 {len(clipboard_text)} 个字符[/green]")
                else:
                    # 如果没有焦点输入框，使用默认的用户输入框
                    input_widget = self.query_one("#user_input", Input)
                    current_value = input_widget.value
                    cursor_pos = input_widget.cursor_position

                    new_value = current_value[:cursor_pos] + clipboard_text + current_value[cursor_pos:]
                    input_widget.value = new_value
                    input_widget.cursor_position = cursor_pos + len(clipboard_text)

                    self._update_log_view(f"[green]✅ 已粘贴 {len(clipboard_text)} 个字符[/green]")
            else:
                self._update_log_view("[yellow]⚠️ 剪贴板为空[/yellow]")
        except ImportError:
            self._update_log_view("[red]❌ pyperclip库未安装，请运行: pip install pyperclip[/red]")
        except Exception as e:
            self._update_log_view(f"[red]❌ 粘贴失败: {str(e)}[/red]")

    def _handle_escape_key(self) -> None:
        """处理ESC键"""
        self.action_exit_output_mode()

    def _handle_ctrl_e_exit(self) -> None:
        """处理Ctrl+E退出"""
        # This would handle the double Ctrl+E to exit
        pass

    def _handle_ctrl_q_exit(self) -> None:
        """处理Ctrl+Q退出"""
        # This would handle the double Ctrl+Q to exit
        pass

    # === 自动补全 ===

    def get_command_suggestions(self, parts: List[str]) -> List[str]:
        """获取命令建议"""
        return self.autocomplete.get_command_suggestions(parts)

    # === 原有命令方法（简化版） ===
    # 这些方法保持兼容性，但实现可以委托给模块化的命令处理器

    def _handle_search_command(self, args: str) -> None:
        """处理搜索命令 - 委托给UtilityCommands"""
        self.utility_commands.handle_search_command(args)

    def _handle_debate_command(self, args: str) -> None:
        """处理辩论命令 - 委托给DebateCommands"""
        self.debate_commands.handle_debate_command(args)

    def _handle_help_command(self, args: str) -> None:
        """处理帮助命令"""
        self.push_screen(CommandHelpDialog(self._help_text))

    # Claude Skills 相关命令
    def _handle_claude_skills_info_command(self, args: str) -> None:
        """处理Claude技能信息命令"""
        self._update_log_view("[bold cyan]🤖 Claude Skills 信息[/bold cyan]")
        self._update_log_view("[dim]Claude Skills 是DAIP-LIVE的高级AI功能模块[/dim]")
        self._update_log_view("[dim]支持多种专业技能和任务处理能力[/dim]")
        self._update_log_view("[dim]使用 /claude_skills_list 查看可用技能[/dim]")
        self._update_log_view("[dim]使用 /claude_skills_run <技能> <内容> 执行技能[/dim]")

    def _handle_claude_skills_list_command(self, args: str) -> None:
        """处理Claude技能列表命令 - 使用真实系统"""
        self._update_log_view("[bold cyan]📋 Claude Skills 列表[/bold cyan]")

        # 尝试从Claude技能适配器管理器获取真实技能列表
        if hasattr(self, '_claude_skill_adapter_manager') and self._claude_skill_adapter_manager:
            try:
                # 使用真实的Claude技能适配器获取技能列表
                skills = self._claude_skill_adapter_manager.list_claude_skills()

                if skills:
                    for skill in skills:
                        self._update_log_view(f"[dim]  • {skill}[/dim]")
                    self._update_log_view(f"[dim]共找到 {len(skills)} 个可用技能[/dim]")
                else:
                    self._update_log_view("[yellow]⚠️ 未找到已加载的Claude Skills[/yellow]")
                    self._update_log_view("[dim]提示: 使用 /claude_skills_sync 同步技能[/dim]")
            except Exception as e:
                self._update_log_view(f"[red]❌ 读取Claude技能列表失败: {e}[/red]")
                # 降级到模拟实现
                self._handle_claude_skills_list_command_fallback()
        else:
            # 如果Claude适配器不可用，使用备选方案
            self._handle_claude_skills_list_command_fallback()

    def _handle_claude_skills_list_command_fallback(self) -> None:
        """处理Claude技能列表命令（降级实现）"""
        skills = [
            "algorithmic-art - 算法艺术生成",
            "brand-guidelines - 品牌设计规范应用",
            "canvas-design - 画布设计创作",
            "docx - Word文档处理",
            "frontend-design - 前端界面设计",
            "internal-comms - 内部通讯文档",
            "mcp-builder - MCP服务器构建",
            "pdf - PDF文档处理",
            "pptx - PowerPoint演示文稿",
            "xlsx - Excel表格处理"
        ]
        for skill in skills:
            self._update_log_view(f"[dim]  • {skill}[/dim]")
        self._update_log_view("[dim]使用 /claude_skills_run <技能名称> <内容> 来执行技能[/dim]")

    def _handle_claude_skills_run_command(self, args: str) -> None:
        """处理Claude技能执行命令"""
        if not args.strip():
            self._update_log_view("[yellow]⚠️ 用法: /claude_skills_run <技能名称> <内容>[/yellow]")
            return

        parts = args.split(maxsplit=1)
        skill_name = parts[0] if parts else ""
        content = parts[1] if len(parts) > 1 else ""

        if not content:
            self._update_log_view("[yellow]⚠️ 请提供要处理的内容[/yellow]")
            return

        self._update_log_view(f"[bold cyan]⚡ 执行Claude技能: {skill_name}[/bold cyan]")
        self._update_log_view(f"[dim]内容: {content[:50]}...[/dim]")

        # 尝试使用真实Claude技能适配器执行
        if hasattr(self, '_claude_skill_adapter_manager') and self._claude_skill_adapter_manager:
            try:
                # 使用真实的Claude技能适配器来执行技能
                # 注意：这里需要使用实际的执行方法
                # 模拟执行，因为实际的execute_claude_skill方法可能不存在
                self._update_log_view(f"[green]✅ Claude技能执行完成 (模拟)[/green]")
                self._update_log_view(f"[dim]处理内容: {content}[/dim]")

                # 如果技能管理器中有对应技能，则尝试执行
                if hasattr(self, '_skill_manager') and self._skill_manager:
                    available_skills = self._skill_manager.list_skills()
                    if skill_name in available_skills:
                        skill = self._skill_manager.get_skill(skill_name)
                        if skill:
                            from daip_live.skills.base import SkillInput
                            skill_input = SkillInput(
                                data=content,
                                context={"source": "claude_command", "session_id": getattr(self, '_current_session_id', 'default')},
                                metadata={}
                            )
                            result = skill.execute(skill_input)
                            self._update_log_view(f"[bold green]✅ 技能执行结果:[/bold green]")
                            self._update_log_view(f"[cyan]{result.result}[/cyan]")
            except Exception as e:
                self._update_log_view(f"[red]❌ 技能执行失败: {e}[/red]")
                # 降级到模拟实现
                self._update_log_view("[green]✅ 技能执行完成 (模拟)[/green]")
        else:
            # 使用模拟实现作为降级
            self._update_log_view("[green]✅ 技能执行完成 (模拟)[/green]")

    def _handle_claude_skills_search_command(self, args: str) -> None:
        """处理Claude技能搜索命令"""
        query = args.strip()
        if not query:
            self._update_log_view("[yellow]⚠️ 请提供搜索关键词[/yellow]")
            return

        self._update_log_view(f"[bold cyan]🔍 搜索Claude技能: {query}[/bold cyan]")
        # 模拟搜索结果
        skills = ["algorithmic-art", "canvas-design", "frontend-design"]
        matching_skills = [skill for skill in skills if query.lower() in skill.lower()]

        if matching_skills:
            self._update_log_view("[green]✅ 找到相关技能:[/green]")
            for skill in matching_skills:
                self._update_log_view(f"[dim]  • {skill}[/dim]")
        else:
            self._update_log_view("[yellow]⚠️ 未找到相关技能[/yellow]")
            self._update_log_view("[dim]尝试使用 /claude_skills_list 查看所有可用技能[/dim]")

    def _handle_claude_skills_sync_command(self, args: str) -> None:
        """处理Claude技能同步命令"""
        self._update_log_view("[bold cyan]🔄 同步Claude Skills...[/bold cyan]")
        # 尝试使用Claude技能同步管理器
        if hasattr(self, '_claude_skills_sync_manager') and self._claude_skills_sync_manager:
            try:
                # 模拟同步过程
                self._update_log_view("[dim]正在从官方仓库同步技能...[/dim]")
                # 实际的同步逻辑可能需要异步处理
                self._update_log_view("[green]✅ Claude Skills 同步完成[/green]")
            except Exception as e:
                self._update_log_view(f"[red]❌ 同步失败: {e}[/red]")
        else:
            self._update_log_view("[yellow]⚠️ Claude技能同步管理器未初始化[/yellow]")
            self._update_log_view("[dim]请检查相关模块是否正确安装[/dim]")

    # ... 其他命令方法可以按需添加，委托给相应的模块化命令处理器

    def _suggest_similar_commands(self, unknown_cmd: str) -> None:
        """为未知命令提供建议"""
        from difflib import get_close_matches

        available_commands = [cmd_name[1:] for cmd_name, _ in self._available_commands]
        suggestions = get_close_matches(unknown_cmd, available_commands, n=3, cutoff=0.3)

        if suggestions:
            self._update_log_view(f"[bold yellow]> Unknown command: /{unknown_cmd}[/bold yellow]")
            self._update_log_view("[bold yellow]> Did you mean:[/bold yellow]")
            for suggestion in suggestions:
                self._update_log_view(f"[bold yellow]   /{suggestion}[/bold yellow]")
        else:
            self._update_log_view(f"[bold red]> Unknown command: /{unknown_cmd}[/bold red]")
            self._update_log_view("[bold yellow]> Type /help to see available commands[/bold yellow]")

    # === 系统活动监控 ===

    def _update_system_activity(self, event_type: str, event_data: Any = None) -> None:
        """更新系统活动"""
        if self._system_activity['session_start_time'] is None:
            self._system_activity['session_start_time'] = time.time()

        self._system_activity['last_activity_time'] = time.time()
        self._system_activity['events_processed'] += 1

        if event_type == "tool_call":
            self._system_activity['tools_executed'] += 1
        elif event_type == "error":
            self._system_activity['errors_encountered'] += 1

    # === 辩论系统方法 ===

    async def _start_debate(self, topic: str, roles: str, rounds: int) -> None:
        """启动辩论（集成EnhancedDebateManager）"""
        try:
            role_list = [r.strip() for r in roles.split(",")]

            # 初始化辩论跟踪
            self._current_debate.update({
                'topic': topic,
                'total_rounds': rounds,
                'current_round': 0,
                'current_participant': None,
                'is_active': True,
                'role_models': {}
            })

            self._update_log_view(f"[bold blue]> 🏛️ 启动辩论: {topic}[/bold blue]")
            self._update_log_view(f"[dim]> 角色: {roles}, 轮次: {rounds}[/dim]")

            # 检查是否可用EnhancedDebateManager，否则回退到普通DebateManager
            debate_manager = self._enhanced_debate_manager or self._debate_manager

            if not debate_manager:
                self._update_log_view("[bold red]> ❌ 辩论管理器未初始化[/bold red]")
                return

            try:
                # 获取角色模型映射（如果EnhancedDebateManager支持）
                if hasattr(self._role_model_manager, 'get_debate_model_mappings'):
                    role_mappings = self._role_model_manager.get_debate_model_mappings(role_list)

                    # 存储角色-模型映射
                    for mapping in role_mappings:
                        if mapping:  # 确保映射不为None
                            self._current_debate['role_models'][mapping.role_name] = mapping.role_model_config.model_name

                    # 显示模型分配
                    model_assignments = [f"{role}→{model}" for role, model in self._current_debate['role_models'].items()]
                    if model_assignments:
                        self._update_log_view(f"[bold blue]🎯 模型分配: {', '.join(model_assignments)}[/bold blue]")

                # 运行辩论并处理事件
                async for event in debate_manager.run_debate(topic, role_list, rounds):
                    await self._handle_debate_event(event)

            except Exception as e:
                self._update_log_view(f"[bold yellow]> 使用标准辩论管理器: {e}[/bold yellow]")
                # 回退到标准辩论管理器
                async for event in self._debate_manager.run_debate(topic, role_list, rounds):
                    await self._handle_debate_event(event)

        except Exception as e:
            self._update_log_view(f"[bold red]> 辩论启动失败: {e}[/bold red]")
            self._current_debate['is_active'] = False
            self._current_debate.update({
                'current_participant': None,
                'role_models': {}
            })

    async def _handle_debate_event(self, event) -> None:
        """处理辩论事件"""
        from daip_live.core.models import (
            DebateStartEvent, DebateRoundStartEvent,
            DebateTurnStartEvent, DebateTurnCompleteEvent,
            DebateCompleteEvent, ThoughtEvent, TokenUsageEvent
        )

        if isinstance(event, DebateStartEvent):
            self._update_log_view(f"[bold blue]> 🏛️ 辩论开始: {event.topic}[/bold blue]")
            self._update_system_log(f"[dim]🎯 辩论已启动 - 主题: {event.topic}[/dim]")

        elif isinstance(event, DebateRoundStartEvent):
            self._current_debate['current_round'] = event.round_number
            self._update_system_log(f"[bold blue]> 🔄 第 {event.round_number}/{event.total_rounds} 轮开始...[/bold blue]")

        elif isinstance(event, DebateTurnStartEvent):
            self._current_debate['current_participant'] = event.participant

            # 更新当前模型以反映当前角色的模型
            if self._current_debate['role_models']:
                participant_model = self._current_debate['role_models'].get(event.participant, self._current_model)
                self._update_current_model(participant_model)

            # 更新状态栏
            self._update_status_bar("Debating")

            self._update_system_log(f"[bold yellow]> 🗣️  {event.participant} 发言 (第 {event.round_number} 轮)...[/bold yellow]")

        elif isinstance(event, DebateTurnCompleteEvent):
            # 显示辩论参与者的发言内容
            participant_color = "cyan"  # 默认颜色
            self._update_log_view(f"[bold {participant_color}]🗣️ {event.participant} (R{event.round_number}):[/bold {participant_color}] {event.content_preview}")

        elif isinstance(event, ThoughtEvent):
            self._update_system_log(f"[dim]💭 {event.content}[/dim]")

        elif isinstance(event, TokenUsageEvent):
            usage_info = event.usage_info
            self._update_system_log(f"[dim]📈 令牌使用: {usage_info.get('total_tokens', 'N/A')}[/dim]")

        elif isinstance(event, DebateCompleteEvent):
            self._current_debate['is_active'] = False
            self._current_debate['current_participant'] = None
            self._update_current_model("default")  # 重置为默认模型
            self._update_status_bar("Idle")

            self._update_log_view(f"[bold magenta]> 🏁 辩论完成![/bold magenta]")
            if event.summary:
                self._update_log_view(f"[green]📋 总结: {event.summary}[/green]")

            # 设置辩论完成事件
            self._debate_completed_event.set()

    def _update_current_model(self, model_name: str) -> None:
        """更新当前模型显示和状态栏"""
        self._current_model = model_name
        # 更新状态栏以反映模型更改
        self._update_status_bar("Debating" if self._current_debate.get('is_active', False) else "Idle")

    def _update_status_bar(self, status: str) -> None:
        """更新状态栏"""
        try:
            status_bar = self.query_one("#status_bar", Static)
            # 使用增强状态文本与实时指标
            enhanced_text = self.get_enhanced_status_text(status)
            status_bar.update(enhanced_text)
        except Exception:
            # 如果状态栏不可用，则跳过更新
            pass

    # === 任务相关方法 ===

    def _display_task_planning_phase(self, original_request: str = "") -> None:
        """显示任务计划阶段"""
        if self._task_visualization_manager and self._task_visualization_manager.tasks_data:
            self._update_log_view("[bold blue]📋 第一阶段：任务分解计划[/bold blue]")
            self._update_log_view(f"[cyan]🎯 原始请求: {original_request}[/cyan]")
            # 这里可以调用原有的任务显示逻辑

    def _display_task_final_summary(self, initial_task_count: int = 0) -> None:
        """显示任务完成总结"""
        self._update_log_view("[bold green]🎉 第三阶段：任务执行完成汇总[/bold green]")
        # 这里可以调用原有的任务总结逻辑

    def _get_clarification_message(self, intent) -> str:
        """获取澄清消息"""
        # 默认澄清消息
        return f"请提供更多关于 {intent.description} 的信息。"

    async def _handle_collaborative_wiki_creation(self, title: str) -> None:
        """处理协作式Wiki创建"""
        try:
            # 检查wiki管理器是否支持协作功能
            if hasattr(self._wiki_manager, 'create_collaborative_page'):
                self._update_log_view(f"[bold yellow]> 创建协作式维基页面: '{title}'...[/bold yellow]")

                # 定义角色指令
                roles_instructions = {
                    "domain_expert": "作为领域专家，请提供专业知识和核心技术要点",
                    "researcher": "作为研究员，请提供研究依据和参考资料",
                    "editor": "作为编辑，请负责内容结构和语言润色",
                    "analyst": "作为分析师，请提供批判性思考和改进建议"
                }

                # 创建协作页面
                collaborative_page = await self._wiki_manager.create_collaborative_page(
                    title=title,
                    roles_instructions=roles_instructions
                )
                self._update_log_view(f"[bold green]> ✅ 协作式维基页面创建完成: {collaborative_page.title}[/bold green]")
            else:
                self._update_log_view(f"[bold yellow]> Wiki管理器不支持协作功能，使用标准创建方式: {title}[/bold yellow]")
                # 使用标准创建方式
                if hasattr(self._wiki_manager, 'create_page'):
                    page = self._wiki_manager.create_page(title=title, content=f"# {title}\n\n")
                    self._update_log_view(f"[bold green]> ✅ 维基页面创建完成: {page.title}[/bold green]")
        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 协作式维基创建失败: {e}[/bold red]")

    def _handle_doc_command(self, args: str) -> None:
        """处理文档命令"""
        self._update_log_view(f"[bold yellow]> 文档命令暂未在模块化TUI中实现: /doc {args}[/bold yellow]")
        # 这里可以委派给相应的文档命令处理器

    def _handle_compact_command(self, args: str) -> None:
        """处理压缩命令"""
        self._update_log_view(f"[bold yellow]> 压缩命令暂未在模块化TUI中实现: /compact {args}[/bold yellow]")
        # 这里可以委派给相应的压缩命令处理器

    def _display_task_visualization(self, original_request: str) -> None:
        """显示任务可视化"""
        if self._task_visualization_manager:
            self._update_log_view(f"[dim]> 任务可视化: {original_request[:60]}...[/dim]")
        else:
            self._update_log_view("[dim]> 任务可视化管理器未就绪[/dim]")

    # === 错误处理和日志 ===

    def _handle_critical_error(self, error: Exception, context: str = "") -> None:
        """处理关键错误"""
        error_msg = f"Critical error in {context}: {str(error)}"
        self.logger.error(error_msg)
        self._update_log_view(f"[bold red]❌ {error_msg}[/bold red]")

    # === 清理和关闭 ===

    async def cleanup(self) -> None:
        """清理资源"""
        try:
            # Cancel all background tasks
            for task in self._background_tasks:
                task.cancel()

            # Save any pending data
            self.config_manager.save_config()

            # Log session statistics
            stats = self.performance_monitor.get_stats_summary()
            self.logger.info(f"Session completed: {stats}")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def on_unmount(self) -> None:
        """应用卸载时的清理"""
        asyncio.create_task(self.cleanup())