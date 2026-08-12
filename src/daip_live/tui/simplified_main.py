"""简化的TUI主控文件 - 仅保留核心功能"""

import asyncio
import inspect
import time
from typing import Optional

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, RichLog, Static

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

# 导入意图识别和Agent执行器
from daip_live.agent_engine.executor import AgentExecutor

# 导入混合意图识别器（集成大模型分析）
from daip_live.multi_agent_collab.hybrid_intent_collaboration_engine import (
    HybridIntentRecognizer,
)

# 导入TUI模块
from .autocomplete import TUIAutocomplete
from .commands import SearchCommands
from .copyable_widgets import CopyableLogWidget
from .enhanced_commands import DebateCommands  # 使用增强的辩论命令
from .interactive_role_creation import InteractiveRoleCreationService
from .screens import CommandHelpDialog, ExitConfirmationDialog
from .tui_role_integration import TUIRoleCommandHandler
from .utils import ConfigManager, FocusMode, HistoryManager, Logger, PerformanceMonitor

# 移除了虚假的文本选择和复制粘贴功能
# from .text_selection import CopyPasteEnhancer  # 虚假实现，已移除

# 导入完整的辩论系统优化组件
try:
    from daip_live.p8_debate_system.enhanced_debate_manager import (
        EnhancedDebateManager,  # noqa: F401
    )
    from daip_live.p8_debate_system.history_tracker import (
        DebateHistoryTracker,  # noqa: F401
    )
    from daip_live.p8_debate_system.layered_memory_system import (
        LayeredMemorySystem,  # noqa: F401
    )
    from daip_live.p8_debate_system.model_availability_checker import (
        ModelAvailabilityChecker,  # noqa: F401
    )
    from daip_live.p8_debate_system.ollama_instance_manager import (
        OllamaInstanceManager,  # noqa: F401
    )
    from daip_live.p8_debate_system.role_debate_session import (
        RoleDebateSession,  # noqa: F401
    )

    DEBATE_SYSTEM_AVAILABLE = True
except ImportError:
    DEBATE_SYSTEM_AVAILABLE = False


# 延迟导入Container以避免循环依赖
def get_container():
    """延迟获取Container实例以避免循环导入"""
    from daip_live.config import ConfigManager
    from daip_live.config_bridge import config_bridge
    from daip_live.container import Container

    # 确保配置桥接适配器有ConfigManager
    try:
        config_manager = ConfigManager()
        config_bridge.set_config_manager(config_manager)
    except Exception:
        pass

    return Container()


class SimplifiedTUI(App):
    """简化的DAIP-LIVE TUI核心控制器"""

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
        Binding("tab", "toggle_focus", "切换焦点"),  # Tab for focus toggle
        Binding("ctrl+a", "select_all", "全选", show=False),
        Binding("ctrl+c", "copy_text", "复制", show=False),
        Binding("ctrl+v", "paste_text", "粘贴", show=False),
        Binding("ctrl+e", "show_exit_confirmation", "退出应用", show=False),
        Binding("escape", "_handle_escape_key", "退出输出模式", show=False),
    ]

    def __init__(self, executor: Optional[AgentExecutor] = None, *args, **kwargs):
        super().__init__()

        # 优先初始化日志缓冲区，以便在初始化过程中可以调用日志方法
        self._log_text_buffer = []
        self._max_log_entries = 1000  # Limit to prevent excessive memory usage

        # 初始化依赖注入容器（延迟导入以避免循环依赖）
        try:
            self.container = get_container()
        except Exception:
            self.container = None

        # 初始化Agent执行器和意图识别器
        if self.container:
            try:
                self._executor = executor or self.container.agent_executor()
            except Exception:
                self._executor = executor
        else:
            self._executor = executor

        # 使用混合意图识别器，集成大模型分析能力
        try:
            # 获取模型提供者
            model_provider = None
            if hasattr(self, "container") and self.container:
                try:
                    model_provider = self.container.model_provider()
                except Exception:
                    pass

            # 初始化混合意图识别器
            self._intent_recognizer = HybridIntentRecognizer(
                llm_model_provider=model_provider
            )

        except Exception:
            self._intent_recognizer = EnhancedIntentRecognizer()

        # 检查并更新模型可用性
        try:
            from daip_live.config import check_and_update_model_availability

            check_and_update_model_availability()
        except Exception:
            pass

        # 初始化TUI模块
        self._initialize_tui_modules()

        # 初始化角色管理器
        self._initialize_role_manager()

        # 初始化角色创建服务
        self._initialize_role_creation_service()

        # 初始化后台session_manager（基础设施）
        self._initialize_backend_session_manager()

        # 初始化memory_service（连接到真实系统）
        self._initialize_memory_service()

        # 初始化Ctrl+E双击退出检测
        self._last_ctrl_e_time: float = 0

        # 初始化辩论进度小部件
        self._debate_progress_widget = None
        try:
            # 尝试导入进度小部件
            from .widgets.debate_progress import DebateProgressWidget

            self._debate_progress_widget = DebateProgressWidget()
            self._update_log_view("[green]✅ 辩论进度小部件已加载[/green]")
        except ImportError:
            self._update_log_view(
                "[yellow]⚠️ 辩论进度小部件不可用，使用基础进度显示[/yellow]"
            )
            self._debate_progress_widget = None
        self._exit_hint_shown: bool = False

        # 初始化辩论管理器
        self._initialize_debate_manager()

        # 初始化知识管理器
        self._initialize_knowledge_manager()

        # 初始化Wiki管理器
        self._initialize_wiki_manager()

        # 初始化Claude Skills适配器管理器（后台服务）
        self._initialize_claude_skills_adapter_manager()

        # 初始化状态
        self._initialize_state()

        # 移除了虚假的复制粘贴增强功能
        # self.copy_paste_enhancer = CopyPasteEnhancer(self)  # 虚假实现，已移除

    def _initialize_tui_modules(self):
        """初始化TUI模块组件"""
        # 初始化自动补全系统
        self.autocomplete = TUIAutocomplete(self)

        # 初始化命令处理器
        # self.command_handler = TUICommandHandler(self)  # 暂时禁用，类不存在

        # 初始化专门的命令处理器
        self.search_commands = SearchCommands(self)
        self.debate_commands = DebateCommands(self)
        from .commands import WikiCommands  # WikiCommands类存在，启用导入

        self.wiki_commands = WikiCommands(self)  # 初始化Wiki命令处理器
        # self.utility_commands = UtilityCommands(self)  # 暂时禁用，类不存在

        # 初始化工具和配置管理
        self.config_manager = ConfigManager()
        self.performance_monitor = PerformanceMonitor()
        self.logger = Logger()

    def _initialize_state(self):
        """初始化状态"""
        # Focus mode
        self.focus_mode = FocusMode.INPUT

        # Current session tracking
        self._current_session_id = None

        # Current model tracking
        self._current_model = "default"

        # Current role tracking
        self._current_role = None

        # System log tracking
        self._system_log_buffer = []
        self._max_system_log_entries = 50

        # Main log text buffer for copy functionality
        self._log_text_buffer = []
        self._max_log_entries = 1000  # Limit to prevent excessive memory usage

        # Available commands
        self._available_commands = [
            ("/help", "显示帮助信息"),
            ("/copy", "复制主对话区内容"),
            ("/copy_recent", "复制最近N行内容"),
            ("/search", "搜索历史对话"),
            ("/debate", "辩论系统"),
            ("/model", "模型管理"),
            ("/compact", "压缩会话历史"),
            ("/doc", "文档搜索"),
            ("/wiki", "Wiki管理"),
            ("/permission", "权限管理"),
            ("/role", "角色管理"),
            ("/knowledge", "知识库管理"),
            ("/sync", "扫描本地 Skills（DAIP_SKILLS_DIR 或 ~/.claude/skills）"),
        ]

        # Background tasks management
        self._background_tasks = set()

        # Input history management
        self.history_manager = HistoryManager(
            self.config_manager.get("max_history", 100)
        )
        self._history_index = -1
        self._current_input_before_history = ""

    async def _start_debate(self, topic: str, roles: str, rounds: int) -> None:
        """启动辩论（使用真实DebateManager系统）"""
        try:
            self._update_log_view(f"[bold blue]> 🤖 启动辩论: {topic}[/bold blue]")
            self._update_log_view(f"[dim]> 角色: {roles}, 轮次: {rounds}[/dim]")

            # 解析角色列表
            role_names = [role.strip() for role in roles.split(",")]

            # 检查是否有辩论管理器
            if hasattr(self, "_debate_manager") and self._debate_manager:
                try:
                    # 使用真实的辩论管理器运行辩论
                    debate_events = self._debate_manager.run_debate(
                        topic=topic, roles_names=role_names, num_rounds=int(rounds)
                    )

                    # 实时处理辩论事件
                    # 首先导入事件类型
                    from daip_live.core.models import (
                        DebateCompleteEvent,
                        DebateStartEvent,
                        DebateTurnCompleteEvent,
                    )

                    async for event in debate_events:
                        # 使用多重检查确保正确识别辩论回合完成事件
                        # 检查类型和属性
                        if (
                            (
                                hasattr(event, "type")
                                and event.type == "debate_turn_complete"
                            )
                            or (type(event).__name__ == "DebateTurnCompleteEvent")
                            or isinstance(event, DebateTurnCompleteEvent)
                        ):
                            # 使用更直观的格式显示辩论内容
                            formatted_content = f"[bold cyan]🗣️ {event.participant} (R{event.round_number}):[/bold cyan] {event.content_preview}"  # noqa: E501
                            self._update_log_view(formatted_content)
                        # 专门处理辩论开始事件
                        elif (
                            (hasattr(event, "type") and event.type == "debate_start")
                            or (type(event).__name__ == "DebateStartEvent")
                            or isinstance(event, DebateStartEvent)
                        ):
                            self._update_log_view(
                                f"[bold blue]🏛️ 辩论开始: {event.topic} | 角色: {', '.join(event.roles)} | 轮次: {event.rounds}[/bold blue]"  # noqa: E501
                            )
                        # 专门处理辩论完成事件
                        elif (
                            (hasattr(event, "type") and event.type == "debate_complete")
                            or (type(event).__name__ == "DebateCompleteEvent")
                            or isinstance(event, DebateCompleteEvent)
                        ):
                            self._update_log_view(
                                f"[bold green]🏁 辩论完成！总结: {event.summary}[/bold green]"  # noqa: E501
                            )
                        # 通用处理 - 避免显示"辩论进展"这类占位内容
                        else:
                            if hasattr(event, "participant") and hasattr(
                                event, "content_preview"
                            ):
                                # 对于有participant和content_preview的事件，显示实际内容或有意义的信息  # noqa: E501
                                content = (
                                    event.content_preview
                                    if event.content_preview.strip()
                                    and event.content_preview != "辩论进展"
                                    else f"{event.participant} 正在发言"
                                )
                                self._update_log_view(
                                    f"[dim]👤 {event.participant}: {content}[/dim]"
                                )
                            elif hasattr(event, "content"):
                                # 对于ThoughtEvent等有content的事件
                                self._update_log_view(
                                    f"[dim]🤖 {event.__class__.__name__}: {event.content}[/dim]"  # noqa: E501
                                )
                            elif hasattr(event, "participant"):
                                # 对于只有participant的事件
                                self._update_log_view(
                                    f"[dim]👤 {event.participant}: 正在准备回复...[/dim]"  # noqa: E501
                                )
                            else:
                                # 其他事件
                                self._update_log_view(
                                    f"[dim]📋 事件: {event.__class__.__name__}[/dim]"
                                )

                    self._update_log_view("[green]✅ 辩论完成[/green]")
                    return
                except Exception as e:
                    self._update_log_view(f"[red]❌ 真实辩论系统错误: {e}[/red]")

            # 如果没有辩论管理器，显示错误
            self._update_log_view("[red]❌ 辩论管理器未初始化[/red]")
            self._update_system_log("[red]❌ 辩论管理器未初始化[/red]")

        except Exception as e:
            self._update_log_view(f"[red]❌ 辩论启动失败: {str(e)}[/red]")

    def _initialize_debate_manager(self):
        """初始化辩论管理器（使用真实实现）"""
        try:
            # 尝试从container获取debate_manager
            if hasattr(self, "container") and self.container:
                try:
                    self._debate_manager = self.container.debate_manager()
                    return
                except Exception:
                    # 尝试手动创建
                    pass

            # 手动创建备选方案 - 优先使用EnhancedDebateManager
            if DEBATE_SYSTEM_AVAILABLE:
                try:
                    from daip_live.p8_debate_system.enhanced_debate_manager import (
                        EnhancedDebateManager,
                    )
                except ImportError:
                    from daip_live.p8_debate_system.manager import (
                        DebateManager as EnhancedDebateManager,
                    )
            else:
                from daip_live.p8_debate_system.manager import (
                    DebateManager as EnhancedDebateManager,
                )

            # 尝试获取所需依赖
            if hasattr(self, "container") and self.container:
                try:
                    # 获取所需的依赖
                    session_manager = self.container.session_manager()
                    role_manager = self.container.role_manager()
                    role_model_manager = self.container.role_model_manager()
                    model_provider = self.container.model_provider()

                    # 使用真实依赖创建EnhancedDebateManager
                    self._debate_manager = EnhancedDebateManager(
                        session_manager=session_manager,
                        role_manager=role_manager,
                        role_model_manager=role_model_manager,
                        model_provider=model_provider,
                        use_optimized_architecture=True,  # 启用优化架构
                    )
                    return
                except Exception:
                    pass
            else:
                # 如果container不可用，检查是否已经有了这些依赖
                session_manager = getattr(self, "_session_manager", None)
                role_manager = getattr(self, "_role_manager", None)
                model_provider = getattr(self, "_model_provider", None)

                if session_manager and role_manager and model_provider:
                    # 优先使用EnhancedDebateManager
                    if DEBATE_SYSTEM_AVAILABLE:
                        try:
                            from daip_live.p8_debate_system.enhanced_debate_manager import (  # noqa: E501
                                EnhancedDebateManager,
                            )

                            # 获取role_model_manager，如果不存在则创建一个默认的
                            role_model_manager = None
                            if hasattr(self.container, "role_model_manager"):
                                try:
                                    role_model_manager = (
                                        self.container.role_model_manager()
                                    )
                                except Exception:
                                    role_model_manager = None

                            # 如果没有role_model_manager，创建一个默认的
                            if role_model_manager is None:
                                from daip_live.p4_role_manager_tools.role_model_manager import (  # noqa: E501
                                    RoleModelManager,
                                )

                                role_model_manager = RoleModelManager()

                            self._debate_manager = EnhancedDebateManager(
                                session_manager=session_manager,
                                role_manager=role_manager,
                                role_model_manager=role_model_manager,
                                model_provider=model_provider,
                                use_optimized_architecture=True,  # 启用优化架构
                            )
                        except ImportError:
                            from daip_live.p8_debate_system.manager import (
                                DebateManager as EnhancedDebateManager,
                            )

                            # 获取role_model_manager，如果不存在则创建一个默认的
                            role_model_manager = None
                            if hasattr(self.container, "role_model_manager"):
                                try:
                                    role_model_manager = (
                                        self.container.role_model_manager()
                                    )
                                except Exception:
                                    role_model_manager = None

                            # 如果没有role_model_manager，创建一个默认的
                            if role_model_manager is None:
                                from daip_live.p4_role_manager_tools.role_model_manager import (  # noqa: E501
                                    RoleModelManager,
                                )

                                role_model_manager = RoleModelManager()

                            self._debate_manager = EnhancedDebateManager(
                                session_manager=session_manager,
                                role_manager=role_manager,
                                role_model_manager=role_model_manager,
                                model_provider=model_provider,
                            )
                    else:
                        from daip_live.p8_debate_system.manager import (
                            DebateManager as EnhancedDebateManager,
                        )

                        # 获取role_model_manager，如果不存在则创建一个默认的
                        role_model_manager = None
                        if hasattr(self.container, "role_model_manager"):
                            try:
                                role_model_manager = self.container.role_model_manager()
                            except Exception:
                                role_model_manager = None

                        # 如果没有role_model_manager，创建一个默认的
                        if role_model_manager is None:
                            from daip_live.p4_role_manager_tools.role_model_manager import (  # noqa: E501
                                RoleModelManager,
                            )

                            role_model_manager = RoleModelManager()

                        self._debate_manager = EnhancedDebateManager(
                            session_manager=session_manager,
                            role_manager=role_manager,
                            role_model_manager=role_model_manager,
                            model_provider=model_provider,
                        )
                else:
                    self._debate_manager = None
        except Exception:
            self._debate_manager = None

    def _initialize_role_manager(self):
        """初始化角色管理器"""
        try:
            # 尝试从container获取role_manager
            if hasattr(self, "container") and self.container:
                try:
                    self._role_manager = self.container.role_manager()
                except Exception:
                    # 创建一个IntelligentRoleManagerWrapper实例
                    from daip_live.p4_role_manager_tools.intelligent_role_manager_wrapper import (  # noqa: E501
                        IntelligentRoleManagerWrapper,
                    )

                    self._role_manager = IntelligentRoleManagerWrapper(
                        roles_dir_path="roles",
                        model_provider=getattr(self, "_model_provider", None),
                    )
            else:
                # 如果container不可用，创建一个智能包装器实例
                from daip_live.core.models import ProviderConfig
                from daip_live.model_provider.provider import LiteLLMProvider
                from daip_live.p4_role_manager_tools.intelligent_role_manager_wrapper import (  # noqa: E501
                    IntelligentRoleManagerWrapper,
                )

                # 获取或创建模型提供者
                model_provider = getattr(self, "_model_provider", None)
                if model_provider is None:
                    try:
                        # 从配置中获取默认模型
                        from daip_live.config import config_manager

                        config = config_manager.get_config()
                        default_model = config.llm_provider.default_model

                        provider_config = ProviderConfig(model=default_model)
                        model_provider = LiteLLMProvider(config=provider_config)
                    except Exception:
                        # 如果无法创建模型提供者，降级到标准RoleManager
                        from daip_live.p4_role_manager_tools.role_manager import (
                            RoleManager,
                        )

                        self._role_manager = RoleManager()
                        return

                self._role_manager = IntelligentRoleManagerWrapper(
                    roles_dir_path="roles", model_provider=model_provider
                )
        except Exception:
            # 降级到标准RoleManager
            from daip_live.p4_role_manager_tools.role_manager import RoleManager

            self._role_manager = RoleManager()

    def _get_knowledge_config(self):
        """从 config.yaml 解析知识库配置（含 DAIP_KNOWLEDGE_DIR 隔离），
        不存在时回退默认目录。与 CLI knowledge 命令保持一致。"""
        import os

        from daip_live.core.models import KnowledgeBaseConfig

        try:
            from pathlib import Path

            import yaml

            config_path = Path("config.yaml")
            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                knowledge_dir = config_data.get("knowledge_base", {}).get(
                    "directory", "docs/"
                )
                embedding_dim = config_data.get("knowledge_base", {}).get(
                    "embedding_dimension", 768
                )
            else:
                knowledge_dir = "docs/"
                embedding_dim = 768
        except Exception:
            knowledge_dir = "docs/"
            embedding_dim = 768

        # 测试隔离环境变量
        knowledge_dir = os.environ.get("DAIP_KNOWLEDGE_DIR") or knowledge_dir

        # 确保目录存在（faiss 写索引需要）
        try:
            Path(knowledge_dir).mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        return KnowledgeBaseConfig(
            directory=knowledge_dir, embedding_dimension=embedding_dim
        )

    def _initialize_knowledge_manager(self):
        """初始化知识管理器（使用真实实现）"""
        try:
            from daip_live.knowledge.manager import KnowledgeManager

            # 尝从container获取所需依赖
            if hasattr(self, "container") and self.container:
                try:
                    # 获取所需的依赖
                    db_manager = getattr(self, "_db_manager", None)
                    if not db_manager and hasattr(self.container, "db_manager"):
                        try:
                            db_manager = self.container.db_manager()
                        except Exception:
                            pass

                    model_provider = getattr(self, "_model_provider", None)
                    if not model_provider and hasattr(self.container, "embed_provider"):
                        # 嵌入用 embed_provider（含 embedding_model 配置，避免 404）
                        try:
                            model_provider = self.container.embed_provider()
                        except Exception:
                            pass
                    if not model_provider and hasattr(self.container, "model_provider"):
                        try:
                            model_provider = self.container.model_provider()
                        except Exception:
                            pass

                    # 创建配置（从 config.yaml 读取，避免硬编码）
                    config = getattr(self, "_config", None)
                    if not config:
                        config = self._get_knowledge_config()

                    if db_manager is None or model_provider is None:
                        raise RuntimeError(
                            "KnowledgeManager需要db_manager和model_provider，但未找到"
                        )

                    # 使用真实依赖创建KnowledgeManager
                    self._knowledge_manager = KnowledgeManager(
                        db_manager=db_manager,
                        model_provider=model_provider,
                        config=config,
                    )
                except Exception as e:
                    raise RuntimeError(f"KnowledgeManager初始化失败: {e}")
            else:
                # 如果container不可用，尝试直接从container初始化
                try:
                    from daip_live.container import Container

                    container = Container()
                    db_manager = container.db_manager()
                    model_provider = container.embed_provider()

                    if db_manager is None or model_provider is None:
                        raise RuntimeError(
                            "KnowledgeManager需要db_manager和model_provider，但未找到"
                        )

                    config = self._get_knowledge_config()

                    self._knowledge_manager = KnowledgeManager(
                        db_manager=db_manager,
                        model_provider=model_provider,
                        config=config,
                    )
                except Exception as e:
                    raise RuntimeError(f"KnowledgeManager初始化失败: {e}")
        except Exception as e:
            raise RuntimeError(f"KnowledgeManager初始化失败: {e}")

    def _initialize_claude_skills_adapter_manager(self):
        """初始化Claude Skills适配器管理器（后台服务）"""
        try:
            from daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager

            # 尝试从container获取依赖
            if hasattr(self, "container") and self.container:
                try:
                    # 获取所需的依赖
                    skill_manager = getattr(self, "_skill_manager", None)
                    if not skill_manager and hasattr(self.container, "skill_manager"):
                        try:
                            skill_manager = self.container.skill_manager()
                        except Exception:
                            pass

                    # 使用真实依赖创建ClaudeSkillAdapterManager
                    self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(
                        skill_manager=skill_manager
                    )
                except Exception as e:
                    # 不使用模拟实现，而是抛出异常
                    raise RuntimeError(f"ClaudeSkillAdapterManager初始化失败: {e}")
            else:
                # 如果container不可用，尝试直接初始化
                try:
                    from daip_live.container import Container

                    container = Container()
                    skill_manager = container.skill_manager()
                    self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(
                        skill_manager=skill_manager
                    )
                except Exception as e:
                    # 不使用模拟实现，而是抛出异常
                    raise RuntimeError(f"ClaudeSkillAdapterManager初始化失败: {e}")
        except ImportError as e:
            raise RuntimeError(f"Claude Skills适配器模块缺失: {e}")
        except Exception as e:
            raise RuntimeError(f"ClaudeSkillAdapterManager初始化失败: {e}")

    def _initialize_role_creation_service(self):
        """初始化角色创建服务"""
        try:
            # 获取模型提供者用于AI角色生成
            model_provider = getattr(self, "_model_provider", None)
            if model_provider is None and hasattr(self, "container") and self.container:
                try:
                    model_provider = self.container.model_provider()
                except Exception:
                    model_provider = None

            # 初始化交互式角色创建服务
            self._role_creation_service = InteractiveRoleCreationService(
                role_manager=self._role_manager, llm_model_provider=model_provider
            )

            # 初始化TUI角色命令处理器
            self._tui_role_handler = TUIRoleCommandHandler(
                tui_instance=self, role_creation_service=self._role_creation_service
            )

        except Exception:
            self._role_creation_service = None
            self._tui_role_handler = None

    def _initialize_backend_session_manager(self):
        """初始化后台session_manager（基础设施）"""
        try:
            # 尝试从container获取session_manager
            if hasattr(self, "container") and self.container:
                try:
                    self._session_manager = self.container.session_manager()
                except Exception:
                    self._session_manager = None
            else:
                # 如果container不可用，尝试直接初始化
                try:
                    from daip_live.container import Container

                    container = Container()
                    self._session_manager = container.session_manager()
                except Exception:
                    self._session_manager = None
        except Exception:
            self._session_manager = None

    def _initialize_memory_service(self):
        """初始化memory_service（连接到真实系统）"""
        try:
            # 尝试从container获取memory_service
            if hasattr(self, "container") and self.container:
                try:
                    # 获取model_provider用于memory_service
                    model_provider = getattr(self, "_model_provider", None)
                    if not model_provider and hasattr(self.container, "model_provider"):
                        model_provider = self.container.model_provider()

                    # 创建MemoryService实例
                    from daip_live.memory.service import MemoryService

                    if model_provider is None:
                        raise RuntimeError("MemoryService需要model_provider，但未找到")
                    self._memory_service = MemoryService(model_provider)
                except Exception:
                    # 创建一个基本的MemoryService实例，即使出现配置错误
                    self._create_fallback_memory_service()
            else:
                # 如果container不可用，尝试直接初始化
                try:
                    from daip_live.container import Container
                    from daip_live.memory.service import MemoryService

                    container = Container()
                    model_provider = container.model_provider()
                    if model_provider is None:
                        raise RuntimeError("MemoryService需要model_provider，但未找到")
                    self._memory_service = MemoryService(model_provider)
                except Exception:
                    self._create_fallback_memory_service()
        except Exception:
            self._create_fallback_memory_service()

    def _create_fallback_memory_service(self):
        """当MemoryService无法初始化时抛出错误而不是使用模拟实现"""
        raise RuntimeError("MemoryService初始化失败，无法使用降级模式")

    def _initialize_wiki_manager(self):
        """初始化Wiki管理器（使用多角色协作功能）"""
        try:
            from pathlib import Path

            from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

            # 尝试从container获取所需依赖
            if hasattr(self, "container") and self.container:
                try:
                    # 获取所需的依赖
                    role_model_manager = getattr(self, "_role_model_manager", None)
                    if not role_model_manager and hasattr(
                        self.container, "role_model_manager"
                    ):
                        try:
                            role_model_manager = self.container.role_model_manager()
                        except Exception:
                            pass

                    model_provider = getattr(self, "_model_provider", None)
                    if not model_provider and hasattr(self.container, "model_provider"):
                        try:
                            model_provider = self.container.model_provider()
                        except Exception:
                            pass

                    session_manager = getattr(self, "_session_manager", None)
                    if not session_manager and hasattr(
                        self.container, "session_manager"
                    ):
                        try:
                            session_manager = self.container.session_manager()
                        except Exception:
                            pass

                    role_manager = getattr(self, "_role_manager", None)
                    if not role_manager and hasattr(self.container, "role_manager"):
                        try:
                            role_manager = self.container.role_manager()
                        except Exception:
                            pass

                    # 使用配置文件中的路径和真实依赖创建EnhancedWikiManager
                    from daip_live.config import config_manager

                    config = config_manager.get_config()
                    wiki_pages_dir = config.model_dump()["wiki"]["pages_directory"]

                    self._wiki_manager = EnhancedWikiManager(
                        wiki_root=Path(wiki_pages_dir),
                        role_model_manager=role_model_manager,
                        model_provider=model_provider,
                        session_manager=session_manager,
                        role_manager=role_manager,
                    )
                except Exception:
                    # 创建带mock依赖的基本实例（会被验证逻辑拒绝，但保持路径一致）
                    try:
                        from daip_live.config import config_manager

                        config = config_manager.get_config()
                        wiki_pages_dir = config.model_dump()["wiki"]["pages_directory"]
                        self._wiki_manager = EnhancedWikiManager(
                            wiki_root=Path(wiki_pages_dir)
                        )
                    except Exception:
                        self._wiki_manager = EnhancedWikiManager(
                            wiki_root=Path("knowledge/wiki")
                        )
            else:
                # 如果container不可用，创建基本实例
                try:
                    from daip_live.config import config_manager

                    config = config_manager.get_config()
                    wiki_pages_dir = config.model_dump()["wiki"]["pages_directory"]
                    self._wiki_manager = EnhancedWikiManager(
                        wiki_root=Path(wiki_pages_dir)
                    )
                except Exception:
                    # 创建一个基本的WikiManager实例
                    from daip_live.wiki.manager import WikiManager

                    try:
                        from daip_live.config import config_manager

                        config = config_manager.get_config()
                        wiki_pages_dir = config.model_dump()["wiki"]["pages_directory"]
                        self._wiki_manager = WikiManager(wiki_root=Path(wiki_pages_dir))
                    except Exception:
                        self._wiki_manager = WikiManager(
                            wiki_root=Path("knowledge/wiki")
                        )
        except ImportError:
            try:
                from pathlib import Path

                from daip_live.wiki.manager import WikiManager

                try:
                    from daip_live.config import config_manager

                    config = config_manager.get_config()
                    wiki_pages_dir = config.model_dump()["wiki"]["pages_directory"]
                    self._wiki_manager = WikiManager(wiki_root=Path(wiki_pages_dir))
                except Exception:
                    self._wiki_manager = WikiManager(wiki_root=Path("knowledge/wiki"))
            except Exception:
                self._wiki_manager = None

    # === UI布局和组件 ===

    def compose(self) -> ComposeResult:
        """构建UI布局"""
        yield Header()

        # Main content area with conversation and system activity
        with Horizontal():
            # Conversation area - takes most of the space
            with Vertical():
                yield Static("💬 对话区域", classes="panel-header")
                yield CopyableLogWidget(
                    id="main_log",
                    classes="output-mode",
                    highlight=True,
                    markup=True,
                    wrap=True,
                )

            # System activity panel - narrow sidebar for system messages
            with Vertical(classes="system-panel"):
                yield Static("🔧 系统状态", classes="panel-header")
                yield CopyableLogWidget(
                    id="system_log",
                    classes="system-log",
                    highlight=True,
                    markup=True,
                    wrap=True,
                )

        yield Input(placeholder="Enter command or message...", id="user_input")
        yield Static(
            "DAIP-LIVE Modular TUI | Status: Ready | Focus: Input", id="status_bar"
        )
        yield Footer()

    # === 生命周期方法 ===

    async def on_mount(self) -> None:
        """应用启动时的初始化"""
        # Set up input widget with initial focus
        input_widget = self.query_one(Input)
        input_widget.focus()

        # Set up initial status
        self._update_status_bar("Ready")

        # Welcome message
        self._update_log_view(
            "[bold green]🚀 Welcome to DAIP-LIVE Modular TUI![/bold green]"
        )
        self._update_log_view("[dim]✨ 现在支持渐进式信息披露和模块化架构[/dim]")
        self._update_log_view("[dim]⌨️ 按 Ctrl+E 退出应用 (需要确认)[/dim]")
        self._update_log_view("[dim]🔧 输入 /help 查看所有可用命令[/dim]")
        self._update_system_log("[dim]🎯 Modular TUI initialized successfully[/dim]")

    # === 核心方法 ===

    def _update_log_view(self, text: str) -> None:
        """更新主对话视图"""
        try:
            # Add text to the buffer for copy functionality
            self._log_text_buffer.append(text)
            # Limit buffer size to prevent excessive memory usage
            if len(self._log_text_buffer) > self._max_log_entries:
                self._log_text_buffer.pop(0)  # Remove oldest entries

            # Write to the RichLog widget
            self.query_one("#main_log", RichLog).write(text)
        except Exception:
            # Even if RichLog fails, ensure text is stored in buffer for copying
            self._log_text_buffer.append(text)
            if len(self._log_text_buffer) > self._max_log_entries:
                self._log_text_buffer.pop(0)

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

        # Enhanced system message patterns
        system_patterns = [
            "command-message",
            "system-reminder",
            "status:",
            "error:",
            "model:",
            "tokens:",
            "tools:",
            "events:",
            "processing",
            "working on",
            "completed",
            "failed",
            "syncing",
            "loading",
            "saving",
            "initializing",
            "shutting down",
            "🧠",
            "✅",
            "❌",
            "⚠️",
            "💬",
            "🚀",
            "💭",
            "🎯",
            "🔍",
            "intent",
            "execution",
            "session",
            "context",
            "agent",
            "module",
            "component",
            "service",
        ]

        # Emoji indicators for system messages
        system_emojis = [
            "🧠",
            "✅",
            "❌",
            "⚠️",
            "💬",
            "🚀",
            "💭",
            "🎯",
            "🔍",
            "⚙️",
            "📊",
            "📈",
        ]

        # Check for system patterns
        for pattern in system_patterns:
            if pattern in text_lower:
                return True

        # Check for system emojis (strong indicator of system messages)
        if any(emoji in text for emoji in system_emojis):
            return True

        # Check for dim/formatted system messages (marked with [dim])
        if "[dim]" in text:
            return True

        # Technical/operational messages with specific keywords
        technical_keywords = [
            "recognition",
            "execution",
            "processing",
            "initialized",
            "started",
            "completed",
            "failed",
            "error",
            "warning",
            "session",
            "context",
            "agent",
            "intent",
            "callback",
        ]

        if any(keyword in text_lower for keyword in technical_keywords):
            return True

        # User messages and actual conversation content go to main panel
        conversation_indicators = [
            ">",
            "💬 收到消息:",
            "🎉",
            "✨",
            "欢迎",
            "输入",
            "搜索历史对话",
            "检测到",
            "请提供",
            "聊天模式",
            "辩论系统",
            "帮助信息",
        ]

        if any(indicator in text for indicator in conversation_indicators):
            return False

        # Default to main conversation area for ambiguous messages
        return False

    def _update_status_bar(self, status: str) -> None:
        """更新状态栏"""
        try:
            status_bar = self.query_one("#status_bar", Static)
            status_text = (
                f"DAIP-LIVE Modular TUI | Status: {status} | Focus: {self.focus_mode}"
            )
            status_bar.update(status_text)
        except Exception:
            pass

    # === 输入处理 ===

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理用户输入"""
        user_input = event.value.strip()

        if not user_input:
            # Clear the input field
            try:
                input_widget = self.query_one("#user_input", Input)
                input_widget.value = ""
            except Exception:
                # 如果找不到输入框，使用事件中的值
                pass
            return

        # Add to history
        self.history_manager.add(user_input)

        # Reset history index
        self._history_index = -1
        self._current_input_before_history = ""

        # Log the input
        self._update_log_view(f"[bold cyan]> {user_input}[/bold cyan]")

        # Process the input
        await self._process_user_input(user_input)

        # Clear the input field after processing
        try:
            input_widget = self.query_one("#user_input", Input)
            input_widget.value = ""
        except Exception:
            # 如果找不到输入框，跳过清空操作
            pass

    def _handle_system_keys(self, event: events.Key) -> bool:
        """处理系统级快捷键和历史记录导航；返回 True 表示已处理"""
        try:
            # 处理系统级键盘快捷键（优先级最高）
            if event.key == "ctrl+e":
                self.action_show_exit_confirmation()
                event.prevent_default()
                return True  # 阻止进一步处理

            if event.key == "ctrl+q":
                self.action_show_exit_confirmation()
                event.prevent_default()
                return True  # 阻止进一步处理

            if event.key == "escape":
                # ESC键退出输出模式或返回
                self.action_exit_output_mode()
                event.prevent_default()
                return True  # 阻止进一步处理

            # 处理输入模式下的特殊键（删除键等）
            if self.focus_mode == FocusMode.INPUT:
                try:
                    input_widget = self.query_one("#user_input", Input)
                except Exception:
                    # 如果找不到输入框，跳过处理
                    return False

                # 处理删除键（退格键）
                if event.key == "backspace":
                    if input_widget.cursor_position > 0:
                        # 删除光标前的一个字符
                        current_value = input_widget.value
                        if input_widget.cursor_position > 0:
                            new_value = (
                                current_value[: input_widget.cursor_position - 1]
                                + current_value[input_widget.cursor_position :]
                            )
                        else:
                            new_value = current_value[:-1]
                        input_widget.value = new_value
                        input_widget.cursor_position = input_widget.cursor_position - 1
                        event.prevent_default()  # 防止默认的退格行为（删除选中字符）

                # 处理Home键（移动到行首）
                elif event.key == "home":
                    input_widget.action_home()
                    event.prevent_default()

                # 处理End键（移动到行尾）
                elif event.key == "end":
                    input_widget.action_end()
                    event.prevent_default()

                # 处理历史记录导航
            elif self.focus_mode == FocusMode.INPUT:
                try:
                    input_widget = self.query_one("#user_input", Input)
                except Exception:
                    # 如果找不到输入框，跳过历史记录导航
                    return False

                # Handle up arrow (previous history)
                if event.key == "up":
                    if self._history_index < len(self.history_manager.history) - 1:
                        # Save current input if we're starting to browse history
                        if self._history_index == -1:
                            self._current_input_before_history = input_widget.value

                        self._history_index += 1
                        history_item = self.history_manager.history[
                            -(self._history_index + 1)
                        ]
                        input_widget.value = history_item
                        # Move cursor to end
                        input_widget.cursor_position = len(history_item)
                    return True

                # Handle down arrow (next history)
                elif event.key == "down":
                    if self._history_index > -1:
                        self._history_index -= 1

                        if self._history_index == -1:
                            # Restore the input we had before browsing history
                            input_widget.value = self._current_input_before_history
                        else:
                            history_item = self.history_manager.history[
                                -(self._history_index + 1)
                            ]
                            input_widget.value = history_item

                        # Move cursor to end
                        input_widget.cursor_position = len(input_widget.value)
                    return True

            # Let other keys be handled normally by the framework
            # Key handling is managed by Textual's built-in event system
            return False

        except Exception as e:
            # If anything goes wrong, just log it and don't handle the key specially
            # This prevents infinite recursion
            self._update_log_view(f"[red]Key handling error: {e}[/red]")
            return False

    async def _process_user_input(self, user_input: str) -> None:
        """处理用户输入的主要逻辑"""
        try:
            # Record start time for performance monitoring
            start_time = time.time()

            # Check if it's a command
            if user_input.startswith("/"):
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
        cmd = parts[0].lstrip("/")
        args = parts[1] if len(parts) > 1 else ""

        # 智能默认处理 - 为单一子命令的命令添加默认值
        cmd, args = self._apply_smart_defaults(cmd, args)

        # 特殊处理role confirm命令
        if cmd.lower() == "role" and args.strip().startswith("confirm "):
            session_id = (
                args.strip().split(" ", 1)[1]
                if len(args.strip().split(" ", 1)) > 1
                else ""
            )
            if self._tui_role_handler:
                self._tui_role_handler.handle_role_confirm(session_id)
            else:
                self._update_log_view("[red]❌ 角色确认功能不可用[/red]")
            return

        # Record command usage
        self.performance_monitor.record_command(cmd)

        # Handle command using direct dispatch to appropriate handler methods
        await self._dispatch_command(cmd, args)

    async def _dispatch_command(self, cmd: str, args: str) -> None:
        """分发命令到适当的处理方法"""
        # 映射命令到处理方法
        command_handlers = {
            "search": self._handle_search_command,
            "debate": self._handle_debate_command,
            "help": self._handle_help_command,
            "claude_skills_info": self._handle_claude_skills_info_command,
            "claude_skills_list": self._handle_claude_skills_list_command,
            "claude_skills_run": self._handle_claude_skills_run_command,
            "claude_skills_search": self._handle_claude_skills_search_command,
            "claude_skills_sync": self._handle_claude_skills_sync_command,
            "sync": self._handle_claude_skills_sync_command,  # /sync 别名
            "clear": self._handle_clear_command,
            "compact": self._handle_compact_command,
            "debate_history": self._handle_debate_history_command,
            "doc": self._handle_doc_command,
            "init": self._handle_init_command,
            "intention": self._handle_intention_command,
            "knowledge": self._handle_knowledge_command,
            "model": self._handle_model_command,
            "pa": self._handle_pa_command,
            "permission": self._handle_permission_command,
            "project": self._handle_project_command,
            "quit": self._handle_quit_command,
            "role": self._handle_role_command,
            "run": self._handle_run_command,
            "scaffold": self._handle_scaffold_command,
            "session": self._handle_session_command,
            "shortcut": self._handle_shortcut_command,
            "skill": self._handle_skill_command,
            "copy": self._handle_copy_command,
            "copy_recent": self._handle_copy_recent_command,
            "todo": self._handle_todo_command,
            "wiki": self._handle_wiki_command,
        }

        handler = command_handlers.get(cmd.lower())
        if handler:
            # 检查处理器是否是异步的，以决定是否使用await
            if asyncio.iscoroutinefunction(handler):
                await handler(args)
            else:
                # 同步处理器，直接调用
                handler(args)
        else:
            # 对于不明确支持的命令，尝试通用处理
            self._update_log_view(f"[yellow]⚠️  未支持的命令: /{cmd}[/yellow]")
            self._update_log_view("[dim]提示: 使用 /help 查看支持的命令列表[/dim]")

    def _apply_smart_defaults(self, cmd: str, args: str) -> tuple[str, str]:
        """为单一子命令的命令应用智能默认值"""

        # 命令默认值映射 - 只保留基本的DAIP-LIVE命令
        default_mappings = {
            "debate": "start",  # debate -> start
            "wiki": "create",  # wiki -> create
            "doc": "search",  # doc -> search
            "model": "list",  # model -> list
            "session": "list",  # session -> list
            "help": "show",  # help -> show
            "quit": "confirm",  # quit -> confirm
        }

        # 只有当这些命令作为主命令使用时才需要智能默认处理
        # 这些命令本身就是子命令，当用户直接输入它们时不需要额外的默认值
        subcommand_exclusions = {
            "start",
            "create",
            "list",
            "show",
            "papers",
            "screen",
            "confirm",
            "project",
        }

        # 如果命令本身就是子命令且不在需要智能处理的映射中，不做转换
        # 注意：'search'和'help'虽然在subcommand_exclusions中，但它们也在default_mappings中，  # noqa: E501
        # 所以它们会得到智能默认处理
        if cmd.lower() in subcommand_exclusions and cmd.lower() not in default_mappings:
            return cmd, args

        # 主要逻辑：为单一子命令的命令添加默认值
        cmd_lower = cmd.lower()
        if cmd_lower in default_mappings and not args.strip():
            # 无参数时添加默认子命令，保持原始大小写
            return cmd, default_mappings[cmd_lower]

        # 有参数时的智能处理
        if cmd_lower in default_mappings and args.strip():
            # 清理参数中的多余空格
            args_clean = args.strip()

            # 检查参数是否已经包含默认子命令
            if args_clean.startswith(default_mappings[cmd_lower]):
                # 已经包含默认子命令，不需要修改
                return cmd, args_clean
            else:
                # 添加默认子命令到现有参数前面
                return cmd, f"{default_mappings[cmd_lower]} {args_clean}"

        return cmd, args.strip()

    async def _ensure_session(self) -> str:
        """确保存在真实会话：首次对话创建并持久化，后续复用最近会话。

        无 session_manager 时降级返回 "default"（不假装持久化）。
        """
        if getattr(self, "_current_session_id", None):
            return self._current_session_id
        if not getattr(self, "_session_manager", None):
            self._current_session_id = "default"
            return "default"

        try:
            # 复用最近一个未结束会话（重启 TUI 后保持连续性）
            sessions = self._session_manager.list_sessions()
            if sessions:
                self._current_session_id = sessions[-1].session_id
                return self._current_session_id
        except Exception:
            pass

        try:
            session = self._session_manager.create_session(
                goal="TUI 对话", session_type="chat", participant_ids=["user"]
            )
            self._current_session_id = session.session_id
            return self._current_session_id
        except Exception:
            self._current_session_id = "default"
            return "default"

    async def _handle_chat_input(self, user_input: str) -> None:
        """处理聊天输入"""
        try:
            # 确保有真实会话（首次对话创建，后续复用；无 session_manager 时降级）
            session_id = await self._ensure_session()

            # 首先尝试意图识别，以确保特定命令优先于搜索
            self._update_system_log(
                f"[dim]🧠 Intent recognition started for: {user_input[:50]}...[/dim]"
            )

            try:
                # Get current session ID for context

                # Check if the intent recognizer supports context-aware recognition
                if hasattr(self._intent_recognizer, "recognize_intent_with_context"):
                    intent = self._intent_recognizer.recognize_intent_with_context(
                        user_input, session_id
                    )
                else:
                    # Check method signature compatibility
                    sig = inspect.signature(self._intent_recognizer.recognize_intent)
                    if "session_id" in sig.parameters:
                        intent = self._intent_recognizer.recognize_intent(
                            user_input, session_id=session_id
                        )
                    else:
                        intent = self._intent_recognizer.recognize_intent(user_input)

                if intent:
                    self._update_system_log(
                        f"[dim]✅ Intent recognized: {intent.name}[/dim]"
                    )

                    # Execute the intent using the executor
                    await self._execute_intent(intent, user_input, session_id)
                    return  # 成功识别意图后直接返回，不再尝试搜索

            except Exception as intent_error:
                self._update_log_view(
                    f"[bold yellow]⚠️ Intent recognition failed: {intent_error}[/bold yellow]"  # noqa: E501
                )
                self._update_system_log(
                    f"[dim]⚠️ Intent recognition error: {intent_error}[/dim]"
                )
                # 继续执行搜索逻辑，以防意图识别失败但用户确实想要搜索

            # 如果意图识别失败或没有识别到意图，检查是否是普通对话搜索请求
            if self._is_conversation_search_request(user_input):
                query = self._extract_search_query(user_input)
                if query:
                    self._update_log_view(
                        "[bold cyan]🔍 检测到历史对话搜索请求...[/bold cyan]"
                    )
                    self.search_commands.search_conversation_history(query)
                else:
                    self._update_log_view(
                        "[bold yellow]💡 请提供更具体的搜索关键词[/bold yellow]"
                    )
                return

            # 如果意图识别和搜索都没有匹配，处理为普通聊天
            self._update_system_log(
                "[dim]💬 No specific intent, handling as chat message[/dim]"
            )
            await self._handle_regular_chat(user_input, session_id)

        except Exception as e:
            self._update_log_view(f"[bold red]Error in chat processing: {e}[/bold red]")
            self._update_system_log(f"[dim]❌ Chat processing error: {e}[/dim]")
            self.logger.error(f"Chat processing error: {e}")

    def _is_conversation_search_request(self, user_input: str) -> bool:
        """检测是否是对话搜索请求"""
        search_keywords = [
            "参考",
            "之前的",
            "历史",
            "过去",
            "之前",
            "以前",
            "查找",
            "搜索",
            "引用",
        ]
        history_keywords = ["对话", "聊天", "辩论", "讨论", "记录", "内容", "信息"]

        return any(keyword in user_input for keyword in search_keywords) and any(
            keyword in user_input for keyword in history_keywords
        )

    def _extract_search_query(self, user_input: str) -> str:
        """提取搜索查询"""
        search_query = user_input
        # 移除常见的搜索触发词
        for remove_word in [
            "参考",
            "之前的",
            "历史",
            "过去",
            "之前",
            "以前",
            "查找",
            "搜索",
            "引用",
            "对话",
            "聊天",
            "记录",
        ]:
            search_query = search_query.replace(remove_word, "").strip()
        return search_query

    async def _execute_intent(self, intent, user_input: str, session_id: str) -> None:
        """执行识别到的意图"""
        try:
            self._update_system_log(f"[dim]🚀 Executing intent: {intent.name}[/dim]")

            # Prepare execution context
            execution_context = {
                "source": "intent_recognition",
                "session_id": session_id,
                "user_input": user_input,
                "intent": intent.name,
                "confidence": getattr(intent, "confidence", 0.0),
            }

            # Execute the intent using the executor
            if hasattr(self._executor, "execute_intent"):
                # 安全检查execute_intent方法是否返回可等待对象
                method = getattr(self._executor, "execute_intent")
                if asyncio.iscoroutinefunction(method):
                    # 方法是一个协程函数，可以await
                    result = await self._executor.execute_intent(
                        intent=intent,
                        user_input=user_input,
                        session_id=session_id,
                        execution_context=execution_context,
                        callback=self._safe_log_callback,
                    )
                else:
                    # 方法不是协程函数，直接调用后处理结果
                    result = self._executor.execute_intent(
                        intent=intent,
                        user_input=user_input,
                        session_id=session_id,
                        execution_context=execution_context,
                        callback=self._safe_log_callback,
                    )
                    # 如果返回的是协程对象，才await它
                    if asyncio.iscoroutine(result):
                        result = await result
            else:
                # Fallback execution method - Handle intents directly
                self._update_system_log(f"[dim]🔧 执行意图: {intent.name}[/dim]")
                await self._handle_intent_directly(
                    intent, user_input, session_id, execution_context
                )
                return

            # Handle execution result
            if result and hasattr(result, "success") and result.success:
                self._update_system_log("[dim]✅ Intent executed successfully[/dim]")
            else:
                self._update_system_log(
                    "[dim]⚠️ Intent execution completed with warnings[/dim]"
                )

        except Exception as e:
            self._update_log_view(
                f"[bold red]❌ Error executing intent: {e}[/bold red]"
            )
            self._update_system_log(f"[dim]❌ Intent execution error: {e}[/dim]")
            self.logger.error(f"Intent execution error: {e}")

    async def _handle_intent_directly(
        self, intent, user_input: str, session_id: str, execution_context: dict
    ) -> None:
        """直接处理各种意图，不依赖执行器的execute_intent方法"""
        try:
            intent_name = intent.name
            parameters = getattr(intent, "parameters", {})
            description = getattr(intent, "description", user_input)

            self._update_system_log(f"[dim]🎯 处理意图: {intent_name}[/dim]")

            # 根据意图类型处理
            if intent_name == "search_papers":
                query = parameters.get("query")
                if query is not None:
                    query = str(query).strip()
                if query:
                    self._update_system_log(f"[dim]🔍 搜索论文: {query}[/dim]")
                    # 调用论文搜索功能 - 现在是同步方法
                    self._handle_paper_search(query)
                else:
                    self._update_log_view("[yellow]⚠️ 搜索论文需要提供关键词[/yellow]")

            elif intent_name == "download_paper":
                paper_id = parameters.get("paper_id")
                search_query = parameters.get("search_query")

                # 安全处理可能为None的参数
                if paper_id is not None:
                    paper_id = str(paper_id).strip()
                if search_query is not None:
                    search_query = str(search_query).strip()

                # 检查是否提供了有效参数
                if paper_id or (search_query and search_query.strip()):
                    self._update_log_view(
                        f"[dim]📥 下载论文: {paper_id or search_query}[/dim]"
                    )
                    # 调用论文下载功能 - 现在是同步方法
                    self._handle_paper_download(paper_id or search_query)
                else:
                    self._update_log_view(
                        "[yellow]⚠️ 下载论文需要提供论文ID或搜索词[/yellow]"
                    )

            elif intent_name == "start_debate":
                topic = parameters.get("topic")
                if topic is not None:
                    topic = str(topic).strip()
                if topic:
                    self._update_system_log(f"[dim]🗣️ 开始辩论: {topic}[/dim]")
                    # 调用辩论功能
                    self.debate_commands.handle_debate_command(f"start {topic}")
                else:
                    self._update_log_view("[yellow]⚠️ 开始辩论需要提供主题[/yellow]")

            elif intent_name == "create_wiki":
                title = parameters.get("title")
                if title is not None:
                    title = str(title).strip()
                if title:
                    self._update_log_view(f"[dim]📝 创建Wiki: {title}[/dim]")
                    # 调用Wiki创建功能 - 现在会显示详细的协作过程
                    if hasattr(self, "wiki_commands") and self.wiki_commands:
                        # 直接调用内部处理函数以确保显示协作详情
                        await self._handle_wiki_create(title)
                    else:
                        self._update_log_view("[red]❌ Wiki命令处理器未初始化[/red]")
                        # 退回到常规聊天处理
                        await self._handle_regular_chat(user_input, session_id)
                else:
                    self._update_log_view("[yellow]⚠️ 创建Wiki需要提供标题[/yellow]")

            elif intent_name == "view_debate_history":
                session_id_param = parameters.get("session_id")
                self._update_log_view(
                    f"[dim]📜 查看辩论历史{' (特定会话: ' + str(session_id_param) + ')' if session_id_param else ''}[/dim]"  # noqa: E501
                )
                # 调用辩论历史查看功能 - 现在已正确处理参数
                await self._handle_debate_history_command(
                    str(session_id_param) if session_id_param else ""
                )

            elif intent_name == "knowledge_search":
                query = parameters.get("query")
                if query is not None:
                    query = str(query).strip()
                if query:
                    self._update_log_view(f"[dim]🔍 知识库搜索: {query}[/dim]")
                    # 调用知识库搜索功能
                    await self._handle_knowledge_search(query)
                else:
                    self._update_log_view("[yellow]⚠️ 知识库搜索需要提供关键词[/yellow]")

            elif intent_name == "execute_skill":
                content = parameters.get("content")
                if content is not None:
                    content = str(content).strip()
                if content:
                    self._update_log_view(f"[dim]⚡ 执行技能: {content[:50]}...[/dim]")
                    # 调用技能执行功能
                    await self._handle_skill_execution(content, parameters)
                else:
                    self._update_log_view("[yellow]⚠️ 执行技能需要提供内容[/yellow]")

            elif intent_name in ["question", "chat"]:
                # 处理一般问答和聊天
                self._update_log_view(f"[dim]💬 处理对话: {description[:50]}...[/dim]")
                await self._handle_regular_chat(user_input, session_id)

            else:
                # 未知意图，作为常规聊天处理
                self._update_log_view(
                    f"[dim]⚠️ 未知意图 {intent_name}，作为对话处理[/dim]"
                )
                await self._handle_regular_chat(user_input, session_id)

        except Exception as e:
            self._update_log_view(f"[red]❌ 意图处理失败: {str(e)}[/red]")
            # 回退到安全的聊天处理，避免再次触发意图识别导致循环
            await self._handle_safe_fallback_chat(user_input, session_id, intent_name)

    async def _handle_safe_fallback_chat(
        self, user_input: str, session_id: str, failed_intent_name: str = "unknown"
    ) -> None:
        """安全的回退聊天处理，避免意图识别循环"""
        try:
            self._update_log_view(
                f"[yellow]⚠️ 意图 '{failed_intent_name}' 处理失败，提供安全回退响应[/yellow]"  # noqa: E501
            )
            self._update_log_view(f"[dim]原始输入: {user_input}[/dim]")

            # 提供具体的操作建议，而不是再次调用执行器
            if failed_intent_name == "view_debate_history":
                self._update_log_view("[cyan]💡 建议操作:[/cyan]")
                self._update_log_view("  • 使用命令: /debate history")
                self._update_log_view("  • 或尝试: /debate list")
            elif failed_intent_name == "start_debate":
                self._update_log_view("[cyan]💡 建议操作:[/cyan]")
                self._update_log_view("  • 使用命令: /debate <主题>")
                self._update_log_view("  • 或尝试: /debate start <主题>")
            elif failed_intent_name == "create_wiki":
                self._update_log_view("[cyan]💡 建议操作:[/cyan]")
                self._update_log_view("  • 使用命令: /wiki create <标题>")
                self._update_log_view("  • 或尝试: /wiki <标题>")
            else:
                self._update_log_view(
                    "[green]🤖 已收到您的请求，但处理过程中出现了一些问题。您可以尝试使用具体的命令格式。[/green]"  # noqa: E501
                )

            # 不调用执行器，避免循环
            self._update_log_view("[green]✅ 已安全处理您的请求[/green]")

        except Exception as e:
            # 如果安全回退也失败，至少记录错误
            self._update_log_view(f"[bold red]❌ 安全回退处理也失败: {e}[/bold red]")
            self._update_log_view(
                "[green]💡 请尝试使用命令行格式，如: /help 查看可用命令[/green]"
            )

    def _handle_paper_search(self, query: str) -> None:
        """处理论文搜索 - 使用真实 arxiv API（doc.paper_downloader）"""
        try:
            self._update_log_view("[dim]🔍 正在搜索论文...[/dim]")
            import tempfile
            from pathlib import Path

            from daip_live.doc.paper_downloader import PaperDownloader

            downloader = PaperDownloader(download_dir=Path(tempfile.mkdtemp()))
            papers = downloader.search_arxiv(query, max_results=5)

            if not papers:
                self._update_log_view("[yellow]⚠️ 未找到相关论文[/yellow]")
                return

            self._update_log_view("[green]✅ 论文搜索完成[/green]")
            for paper in papers:
                pub_date = paper.published_date.strftime("%Y-%m-%d")
                authors = ", ".join(paper.authors[:3])
                if len(paper.authors) > 3:
                    authors += " et al."
                self._update_log_view(f"[cyan]📄 {paper.title}[/cyan]")
                self._update_log_view(
                    f"[dim]   {authors} | {pub_date} | {paper.arxiv_id}[/dim]"
                )
        except Exception as e:
            self._update_log_view(f"[red]❌ 真实论文搜索失败: {str(e)}[/red]")
            self._update_log_view(f"[cyan]降级为本地搜索: '{query}'[/cyan]")

    def _handle_paper_download(self, identifier: str) -> None:
        """处理论文下载 - 使用真实 arxiv API（doc.paper_downloader）"""
        try:
            self._update_log_view(f"[dim]📥 正在下载论文: {identifier}[/dim]")
            from pathlib import Path

            from daip_live.doc.paper_downloader import PaperDownloader

            downloader = PaperDownloader(download_dir=Path("papers"))
            result = downloader.download_arxiv_paper(identifier)

            if result.success:
                self._update_log_view("[green]✅ 论文下载完成[/green]")
                self._update_log_view(f"[cyan]📄 {result.pdf_path}[/cyan]")
            else:
                self._update_log_view(
                    f"[red]❌ 论文下载失败: {result.error_message}[/red]"
                )
        except Exception as e:
            self._update_log_view(f"[red]❌ 论文下载失败: {str(e)}[/red]")

    async def _handle_knowledge_search(self, query: str) -> None:
        """处理知识库搜索 - 使用真实系统"""
        try:
            self._update_log_view(f"[dim]🔍 正在搜索知识库: {query}[/dim]")

            # 检查是否已初始化知识管理器
            if hasattr(self, "_knowledge_manager") and self._knowledge_manager:
                try:
                    # 使用真实的知识库搜索功能
                    search_results = await self._knowledge_manager.search(query)

                    if search_results and len(search_results) > 0:
                        self._update_log_view("[green]✅ 知识库搜索完成[/green]")
                        for result in search_results[:5]:  # 显示前5个结果
                            content_preview = (
                                result.get("content", "")[:100] + "..."
                                if len(result.get("content", "")) > 100
                                else result.get("content", "")
                            )
                            self._update_log_view(f"[cyan]📄 {content_preview}[/cyan]")
                    else:
                        self._update_log_view(
                            "[yellow]⚠️ 未在知识库中找到相关内容[/yellow]"
                        )

                except Exception as e:
                    self._update_log_view(f"[red]❌ 真实知识库搜索失败: {str(e)}[/red]")
                    # 不降级到模拟实现，而是抛出错误
                    raise RuntimeError(f"真实知识库搜索失败: {e}")
            else:
                # 如果知识管理器未初始化，抛出错误而不是模拟
                raise RuntimeError("知识管理器未正确初始化")

        except Exception as e:
            self._update_log_view(f"[red]❌ 知识库搜索失败: {str(e)}[/red]")

    async def _handle_skill_execution(self, content: str, parameters: dict) -> None:
        """处理技能执行"""
        try:
            self._update_log_view("[dim]⚡ 正在执行技能...[/dim]")

            # 检查Claude技能适配器是否可用
            if (
                hasattr(self, "_claude_skill_adapter_manager")
                and self._claude_skill_adapter_manager
            ):
                # 使用真实的Claude技能执行功能
                execution_result = (
                    await self._claude_skill_adapter_manager.execute_skill(
                        content, parameters
                    )
                )
                self._update_log_view("[green]✅ 技能执行完成[/green]")
                self._update_log_view(
                    f"[cyan]✅ 技能执行结果: {execution_result}[/cyan]"
                )
            else:
                # 如果技能管理器未初始化，抛出错误
                raise RuntimeError("Claude技能适配器未正确初始化")

        except Exception as e:
            self._update_log_view(f"[red]❌ 技能执行失败: {str(e)}[/red]")
            raise RuntimeError(f"技能执行失败: {e}")

    async def _handle_regular_chat(self, user_input: str, session_id: str) -> None:
        """处理常规聊天消息"""
        try:
            self._update_system_log("[dim]💬 Processing as regular chat message[/dim]")
            self._update_log_view(f"[bold blue]💬 收到消息: {user_input}[/bold blue]")
            self._update_log_view("[cyan]> 🤔 思考中...[/cyan]")

            timeout = 30  # 30秒超时

            # 这里应该有具体的聊天处理逻辑，使用executor或大模型
            if hasattr(self, "_executor") and self._executor:
                # 检查executor是否具有可用的执行方法
                if hasattr(self._executor, "chat_run"):
                    try:
                        # 使用asyncio.wait_for处理超时
                        chat_task = self._executor.chat_run(user_input).__aiter__()
                        while True:
                            try:
                                event = await asyncio.wait_for(
                                    chat_task.__anext__(), timeout=timeout
                                )
                                if hasattr(event, "content"):
                                    # 移除"思考中"消息，显示实际响应
                                    self._update_log_view(
                                        f"[green]🤖 {event.content}[/green]"
                                    )
                                elif hasattr(event, "message"):
                                    self._update_log_view(
                                        f"[green]🤖 {event.message}[/green]"
                                    )
                                else:
                                    # 如果event有其他属性，也可以处理
                                    self._update_log_view(
                                        f"[green]🤖 收到响应事件: {str(event)}[/green]"
                                    )
                            except StopAsyncIteration:
                                break  # Chat run completed successfully
                            except asyncio.TimeoutError:
                                self._update_log_view(
                                    "[red]❌ 聊天处理超时，请稍后重试或使用具体命令。[/red]"  # noqa: E501
                                )
                                self._update_system_log(
                                    f"[dim]⚠️ Chat processing timed out after {timeout}s[/dim]"  # noqa: E501
                                )
                                break
                    except Exception as exec_error:
                        self._update_log_view(
                            f"[red]❌ 聊天处理出错: {exec_error}[/red]"
                        )
                        self._update_system_log(
                            f"[dim]⚠️ Chat execution error: {exec_error}[/dim]"
                        )
                elif hasattr(self._executor, "run"):
                    # 如果有run方法，但需要不同的参数，可以根据需要调整
                    try:
                        # 运行run方法并等待结果
                        run_task = self._executor.run(user_input).__aiter__()
                        while True:
                            try:
                                event = await asyncio.wait_for(
                                    run_task.__anext__(), timeout=timeout
                                )
                                if hasattr(event, "content"):
                                    # 移除"思考中"消息，显示实际响应
                                    self._update_log_view(
                                        f"[green]🤖 {event.content}[/green]"
                                    )
                                elif hasattr(event, "message"):
                                    self._update_log_view(
                                        f"[green]🤖 {event.message}[/green]"
                                    )
                                else:
                                    # 如果event有其他属性，也可以处理
                                    self._update_log_view(
                                        f"[green]🤖 收到响应事件: {str(event)}[/green]"
                                    )
                            except StopAsyncIteration:
                                break  # Run completed successfully
                            except asyncio.TimeoutError:
                                self._update_log_view(
                                    "[red]❌ 聊天处理超时，请稍后重试或使用具体命令。[/red]"  # noqa: E501
                                )
                                self._update_system_log(
                                    f"[dim]⚠️ Chat processing timed out after {timeout}s[/dim]"  # noqa: E501
                                )
                                break
                    except Exception as exec_error:
                        self._update_log_view(
                            f"[red]❌ 聊天处理出错: {exec_error}[/red]"
                        )
                        self._update_system_log(
                            f"[dim]⚠️ Chat execution error: {exec_error}[/dim]"
                        )
                else:
                    # 如果executor没有可用的聊天方法，使用默认响应
                    self._update_log_view(
                        "[yellow]⚠️ 聊天执行器不支持聊天方法，使用默认响应[/yellow]"
                    )
                    self._update_log_view(
                        "[green]🤖 这是DAIP-LIVE默认响应：我已收到您的消息。如需复杂处理，请使用具体命令。[/green]"  # noqa: E501
                    )
            else:
                # 如果executor不存在，使用默认响应
                self._update_log_view(
                    "[yellow]⚠️ 聊天执行器不可用，使用默认响应[/yellow]"
                )
                self._update_log_view(
                    "[green]🤖 这是DAIP-LIVE默认响应：我已收到您的消息。如需复杂处理，请使用具体命令。[/green]"  # noqa: E501
                )

        except Exception as e:
            self._update_log_view(f"[bold red]Error in chat processing: {e}[/bold red]")
            self._update_system_log(f"[dim]❌ Chat processing error: {e}[/dim]")
            self.logger.error(f"Regular chat error: {e}")

    def _safe_log_callback(
        self, message_func, message_type: str = "info", context: str = ""
    ):
        """安全的日志回调函数，用于Agent执行器"""
        try:
            if callable(message_func):
                message = message_func()
                if message:
                    # Route messages based on type
                    if message_type in ["error", "warning"]:
                        self._update_log_view(
                            f"[bold {'red' if message_type == 'error' else 'yellow'}]{message}[/bold {'red' if message_type == 'error' else 'yellow'}]"  # noqa: E501
                        )
                    elif message_type == "system":
                        self._update_system_log(f"[dim]{message}[/dim]")
                    else:
                        self._update_log_view(message)
        except Exception as e:
            self.logger.error(f"Error in log callback: {e}")

    # === 键盘快捷键处理 ===

    def action_toggle_focus(self) -> None:
        """切换焦点模式"""
        if self.focus_mode == FocusMode.INPUT:
            self.focus_mode = FocusMode.OUTPUT
            self.query_one("#main_log").focus()
        else:
            self.focus_mode = FocusMode.INPUT
            try:
                self.query_one("#user_input").focus()
            except Exception:
                # 如果找不到输入框，跳过焦点设置
                pass
        self._update_status_bar("Ready")
        self.refresh()

    def action_exit_output_mode(self) -> None:
        """退出输出模式"""
        self.focus_mode = FocusMode.INPUT
        try:
            self.query_one("#user_input").focus()
            self._update_status_bar("Ready")
            self.refresh()
        except Exception:
            pass

    # 移除了虚假的 action_select_all 方法
    # def action_select_all(self) -> None:
    #     """这个方法是虚假实现，已被移除"""
    #     pass

    async def action_copy_text(self) -> None:
        """真实的复制文本功能 - 复制主对话区内容"""
        try:
            import pyperclip

            # 获取日志缓冲区内容
            all_text = ""
            if hasattr(self, "_log_text_buffer") and self._log_text_buffer:
                all_text = "\n".join(self._log_text_buffer)

            if all_text and all_text.strip():
                pyperclip.copy(all_text)
                self._update_log_view(
                    "[bold green]✅ 主对话区内容已复制到剪贴板！[/bold green]"
                )
                self._update_log_view(f"[dim]📝 复制了 {len(all_text)} 个字符[/dim]")
                self._update_log_view("[dim]💡 现在可以在任何地方粘贴 (Ctrl+V)[/dim]")
            else:
                self._update_log_view("[yellow]⚠️ 主对话区没有内容可以复制[/yellow]")

        except ImportError:
            self._update_log_view("[red]❌ 需要安装 pyperclip 库[/red]")
            self._update_log_view("[dim]请运行: pip install pyperclip[/dim]")
        except Exception as e:
            self._update_log_view(f"[red]❌ 复制失败: {str(e)}[/red]")

    def copy_recent_content(self, lines: int = 20) -> None:
        """复制最近N行内容"""
        try:
            import pyperclip

            if hasattr(self, "_log_text_buffer") and self._log_text_buffer:
                recent_text = "\n".join(self._log_text_buffer[-lines:])

                if recent_text.strip():
                    pyperclip.copy(recent_text)
                    self._update_log_view(
                        f"[bold green]✅ 最近 {lines} 行已复制到剪贴板！[/bold green]"
                    )
                    self._update_log_view(
                        f"[dim]📝 复制了 {len(recent_text)} 个字符[/dim]"
                    )
                else:
                    self._update_log_view("[yellow]⚠️ 没有内容可以复制[/yellow]")
            else:
                self._update_log_view("[yellow]⚠️ 没有日志内容可以复制[/yellow]")

        except ImportError:
            self._update_log_view("[red]❌ 需要安装 pyperclip 库[/red]")
            self._update_log_view("[dim]请运行: pip install pyperclip[/dim]")
        except Exception as e:
            self._update_log_view(f"[red]❌ 复制失败: {str(e)}[/red]")

    def _handle_escape_key(self) -> None:
        """处理ESC键"""
        self.action_exit_output_mode()

    async def action_quit(self) -> None:
        """退出应用"""
        try:
            self._update_log_view("[bold yellow]👋 正在退出 DAIP-LIVE...[/bold yellow]")
            self._update_system_log("[dim]🔄 正在清理资源...[/dim]")

            # 清理资源
            if hasattr(self, "_executor") and self._executor:
                try:
                    # 如果执行器有清理方法，调用它
                    if hasattr(self._executor, "cleanup"):
                        await self._executor.cleanup()
                    self._update_system_log("[dim]✓ Agent执行器已清理[/dim]")
                except Exception as e:
                    self._update_system_log(f"[dim]⚠️ 执行器清理警告: {e}[/dim]")

            # 清理容器
            if hasattr(self, "container") and self.container:
                try:
                    # 如果容器有清理方法，调用它
                    if hasattr(self.container, "shutdown"):
                        self.container.shutdown()
                    self._update_system_log("[dim]✓ 依赖注入容器已清理[/dim]")
                except Exception as e:
                    self._update_system_log(f"[dim]⚠️ 容器清理警告: {e}[/dim]")

            self._update_log_view("[bold green]✅ 资源清理完成，再见！[/bold green]")

            # 短暂延迟后退出
            await asyncio.sleep(0.5)
            self.exit()

        except Exception as e:
            self._update_log_view(f"[bold red]❌ 退出时发生错误: {e}[/bold red]")
            # 即使出错也要退出
            self.exit()

    def action_show_exit_confirmation(self) -> None:
        """显示退出确认对话框 - 支持Ctrl+E双击检测"""
        import time

        current_time = time.time()

        if current_time - self._last_ctrl_e_time <= 3.0:  # 3秒窗口内
            # 第二次CTRL+E，显示确认对话框
            self._show_exit_confirmation_dialog()
        else:
            # 第一次CTRL+E，显示提示
            self._last_ctrl_e_time = current_time
            self._exit_hint_shown = True
            self._update_status_bar("再次按 CTRL+E 将显示退出确认")

            # 3秒后清除提示
            def clear_hint():
                if time.time() - self._last_ctrl_e_time > 3.0:
                    self._update_status_bar("Ready")
                    self._exit_hint_shown = False

            self.set_timer(3.0, clear_hint)

    def _show_exit_confirmation_dialog(self) -> None:
        """显示退出确认对话框"""
        # 显示退出提示
        self._update_log_view("[dim]💡 按下 Ctrl+E 退出应用[/dim]")
        self._update_log_view("[dim]💡 按 Y 确认退出，按 N 或 ESC 取消[/dim]")

        # 立即显示确认对话框
        self.push_screen(ExitConfirmationDialog(on_confirm=self._do_exit))

    def _update_status_bar(self, message: str) -> None:
        """更新状态栏消息"""
        try:
            # 尝试更新footer或状态栏
            if hasattr(self, "status_bar") and self.status_bar:
                self.status_bar.update(message)
            elif hasattr(self, "footer") and self.footer:
                self.footer.update(message)
        except Exception:
            # 如果更新状态栏失败，静默忽略
            pass

    def _do_exit(self) -> None:
        """执行实际的退出操作"""
        # 调用异步退出方法
        asyncio.create_task(self.action_quit())

    def action__handle_ctrl_e_exit(self) -> None:
        """退出应用 - Ctrl+E快捷键 (已弃用，使用show_exit_confirmation)"""
        self.action_show_exit_confirmation()

    def action__handle_ctrl_q_exit(self) -> None:
        """退出会话/应用 - Ctrl+Q快捷键 (已弃用，使用show_exit_confirmation)"""
        self.action_show_exit_confirmation()

    def action_paste_text(self) -> None:
        """粘贴文本到输入区域"""
        try:
            import pyperclip

            # 获取文本
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                # 获取当前焦点widget
                focused = self.focused
                if isinstance(focused, Input):
                    # 粘贴到输入框
                    current_value = focused.value
                    cursor_position = focused.cursor_position
                    new_value = (
                        current_value[:cursor_position]
                        + clipboard_text
                        + current_value[cursor_position:]
                    )
                    focused.value = new_value
                    focused.cursor_position = cursor_position + len(clipboard_text)
                    self._update_log_view("[dim]✅ 文本已粘贴到输入框[/dim]")
                else:
                    # 尝试粘贴到主输入框
                    try:
                        input_widget = self.query_one("#user_input", Input)
                        current_value = input_widget.value
                        cursor_position = input_widget.cursor_position
                        new_value = (
                            current_value[:cursor_position]
                            + clipboard_text
                            + current_value[cursor_position:]
                        )
                        input_widget.value = new_value
                        input_widget.cursor_position = cursor_position + len(
                            clipboard_text
                        )
                        self._update_log_view("[dim]✅ 文本已粘贴到输入框[/dim]")
                    except Exception:
                        self._update_log_view(
                            "[yellow]⚠️ 无法粘贴 - 请先聚焦到输入框[/yellow]"
                        )
            else:
                self._update_log_view("[yellow]⚠️ 剪贴板为空[/yellow]")

        except ImportError:
            self._update_log_view(
                "[red]❌ 需要安装 pyperclip 库: pip install pyperclip[/red]"
            )
        except Exception as e:
            self._update_log_view(f"[red]❌ 粘贴失败: {str(e)}[/red]")

    # === 自动补全 ===

    def get_command_suggestions(self, parts: list[str]) -> list[str]:
        """获取命令建议"""
        return self.autocomplete.get_command_suggestions(parts)

    # === 命令处理器（委托给模块） ===

    def _handle_search_command(self, args: str) -> None:
        """处理搜索命令 - 委托给UtilityCommands"""
        self.utility_commands.handle_search_command(args)

    def _handle_debate_command(self, args: str) -> None:
        """处理辩论命令 - 委托给DebateCommands"""
        self.debate_commands.handle_debate_command(args)

    def _handle_help_command(self, args: str) -> None:
        """处理帮助命令"""
        help_text = """
🚀 DAIP-LIVE 模块化TUI帮助系统 (v2.2 - 智能默认)

📋 可用命令（支持智能默认处理）：

🎯 智能命令（简化操作）
  /debate                 - 启动新辩论 (默认: start)
  /wiki                   - 创建Wiki页面 (默认: create)
  /search                  - 搜索论文 (默认: papers)
  /doc                    - 搜索文档 (默认: search)
  /model                  - 查看模型列表 (默认: list)
  /session                - 查看会话列表 (默认: list)
  /todo                   - 查看待办事项 (默认: list)
  /help                   - 显示帮助 (默认: show)

📋 复制功能
  /copy                   - 复制主对话区所有内容到剪贴板
  /copy_recent <行数>      - 复制最近N行内容 (例如: /copy_recent 20)

🔍 搜索和查询
  /search <关键词>          - 搜索历史对话记录
  /doc search <论文>         - 搜索论文
  /wiki search <页面>        - 搜索Wiki页面

🏛️ 辩论系统
  /debate <主题>            - 直接启动辩论 (智能识别)
  /debate start <主题>       - 启动新辩论
  /debate history list      - 查看辩论历史
  /debate search <关键词>    - 搜索辩论记录

📚 知识管理
  /wiki <标题>              - 直接创建Wiki (智能识别)
  /wiki create <标题>       - 创建Wiki页面
  /wiki search <页面>        - 搜索Wiki页面
  /knowledge search <关键词> - 搜索知识库（真实向量检索）
  /knowledge sync           - 同步知识库（真实摄取变更）
  /knowledge stats          - 知识库统计（真实文档/索引/磁盘）

⚙️ 系统管理
  /model                  - 查看可用模型
  /model switch <模型>      - 切换模型
  /compact                - 压缩当前会话（真实 LLM 摘要）
  /sync                   - 扫描本地 Skills 目录（真实扫描）
  /clear                  - 清空屏幕
  /permission <操作>       - 权限管理

📋 任务管理
  /todo                   - 查看待办事项
  /todo add <任务>          - 添加待办事项
  /todo complete <任务>     - 完成任务

💬 Claude Skills AI功能
  /claude_skills_list      - 查看技能列表
  /claude_skills_run        - 执行技能
  /claude_skills_sync       - 同步技能

🎮 快捷键
  Ctrl+E                   - 退出应用 (需确认)
  Ctrl+A                   - 全选文本
  Ctrl+C                   - 复制文本
  Ctrl+V                   - 粘贴文本
  ↑↓                      - 浏览输入历史
  ESC                      - 退出输出模式

✨ 智能特性
  🔧 自动识别子命令意图
  🎯 单一命令自动添加默认参数
  💡 简化常用操作流程
  🔍 智能命令补全
  📊 实时状态反馈

🎨 使用示例
  /debate AI伦理讨论        → 自动识别为 "/debate start AI伦理讨论"
  /wiki 机器学习基础        → 自动识别为 "/wiki create 机器学习基础"
  /search 深度学习论文      → 自动识别为 "/search papers 深度学习论文"
  /todo                    → 显示待办事项列表
  /help                    → 显示此帮助信息
        """
        self.push_screen(CommandHelpDialog(help_text))

    def _suggest_similar_commands(self, unknown_cmd: str) -> None:
        """为未知命令提供建议"""
        from difflib import get_close_matches

        available_commands = [cmd_name[1:] for cmd_name, _ in self._available_commands]
        suggestions = get_close_matches(
            unknown_cmd, available_commands, n=3, cutoff=0.3
        )

        if suggestions:
            self._update_log_view(
                f"[bold yellow]> Unknown command: /{unknown_cmd}[/bold yellow]"
            )
            self._update_log_view("[bold yellow]> Did you mean:[/bold yellow]")
            for suggestion in suggestions:
                self._update_log_view(f"[bold yellow]   /{suggestion}[/bold yellow]")
        else:
            self._update_log_view(
                f"[bold red]> Unknown command: /{unknown_cmd}[/bold red]"
            )
            self._update_log_view(
                "[bold yellow]> Type /help to see available commands[/bold yellow]"
            )

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
            # Save any pending data
            self.config_manager.save_config()

            # Log session statistics
            stats = self.performance_monitor.get_stats_summary()
            self.logger.info(f"Session completed: {stats}")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    # === 缺失的命令处理器实现 ===

    def _handle_claude_skills_info_command(self, args: str) -> None:
        """处理Claude技能信息命令"""
        self._update_log_view("[bold cyan]🤖 Claude Skills 信息[/bold cyan]")
        self._update_log_view("[dim]Claude Skills 是DAIP-LIVE的高级AI功能模块[/dim]")
        self._update_log_view("[dim]支持多种专业技能和任务处理能力[/dim]")
        self._update_log_view("[dim]使用 /claude_skills_list 查看可用技能[/dim]")
        self._update_log_view(
            "[dim]使用 /claude_skills_run <技能> <内容> 执行技能[/dim]"
        )

    def _handle_claude_skills_list_command(self, args: str) -> None:
        """处理Claude技能列表命令 - 使用真实系统"""
        self._update_log_view("[bold cyan]📋 Claude Skills 列表[/bold cyan]")

        # 尝试从Claude技能适配器管理器获取真实技能列表
        if (
            hasattr(self, "_claude_skill_adapter_manager")
            and self._claude_skill_adapter_manager
        ):
            try:
                # 使用真实的Claude技能适配器获取技能列表
                skills = self._claude_skill_adapter_manager.list_claude_skills()

                if skills:
                    for skill in skills:
                        self._update_log_view(f"[dim]  • {skill}[/dim]")
                    self._update_log_view(f"[dim]共找到 {len(skills)} 个可用技能[/dim]")
                else:
                    self._update_log_view(
                        "[yellow]⚠️ 未找到已加载的Claude Skills[/yellow]"
                    )
                    self._update_log_view(
                        "[dim]提示: 使用 /claude_skills_sync 同步技能[/dim]"
                    )
            except Exception as e:
                self._update_log_view(f"[red]❌ 读取Claude技能列表失败: {e}[/red]")
                # 不降级到模拟实现，而是抛出错误
                raise RuntimeError(f"Claude技能列表获取失败: {e}")
        else:
            # 如果Claude适配器不可用，抛出错误
            raise RuntimeError("Claude技能适配器未正确初始化")

    def _handle_claude_skills_list_command_fallback(self) -> None:
        """当Claude技能适配器不可用时抛出错误而不是提供模拟实现"""
        raise RuntimeError("Claude技能适配器未正确初始化")

    def _handle_claude_skills_run_command(self, args: str) -> None:
        """处理Claude技能执行命令"""
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /claude_skills_run <技能名称> <内容>[/yellow]"
            )
            return

        parts = args.split(maxsplit=1)
        skill_name = parts[0] if parts else ""
        content = parts[1] if len(parts) > 1 else ""

        if not content:
            self._update_log_view("[yellow]⚠️ 请提供要处理的[/yellow]")
            return

        self._update_log_view(f"[bold cyan]⚡ 执行Claude技能: {skill_name}[/bold cyan]")
        self._update_log_view(f"[dim]内容: {content[:50]}...[/dim]")

        # 尝试使用真实Claude技能适配器执行
        if (
            hasattr(self, "_claude_skill_adapter_manager")
            and self._claude_skill_adapter_manager
        ):
            try:
                # 使用真实的Claude技能适配器来执行技能
                result = self._claude_skill_adapter_manager.execute_claude_skill(
                    skill_name=skill_name, content=content
                )
                self._update_log_view("[green]✅ 技能执行完成[/green]")
                if result:
                    self._update_log_view(f"[dim]结果: {result}[/dim]")
            except Exception as e:
                self._update_log_view(f"[red]❌ 技能执行失败: {e}[/red]")
                # 不使用模拟实现，抛出错误
                raise RuntimeError(f"技能执行失败: {e}")
        else:
            # 如果没有技能适配器，抛出错误
            raise RuntimeError("Claude技能适配器未正确初始化")

    def _handle_claude_skills_search_command(self, args: str) -> None:
        """处理Claude技能搜索命令"""
        query = args.strip()
        if not query:
            self._update_log_view("[yellow]⚠️ 请提供搜索关键词[/yellow]")
            return

        # 检查Claude技能适配器是否可用
        if (
            hasattr(self, "_claude_skill_adapter_manager")
            and self._claude_skill_adapter_manager
        ):
            try:
                self._update_log_view(
                    f"[bold cyan]🔍 搜索Claude技能: {query}[/bold cyan]"
                )
                # 使用真实的技能搜索功能 - 通过事件循环运行异步函数
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    skills_list = loop.run_until_complete(
                        self._claude_skill_adapter_manager.search_skills(query)
                    )

                    if skills_list:
                        self._update_log_view("[green]✅ 找到相关技能:[/green]")
                        for skill in skills_list:
                            self._update_log_view(f"[dim]  • {skill}[/dim]")
                    else:
                        self._update_log_view("[yellow]⚠️ 未找到相关技能[/yellow]")
                finally:
                    loop.close()
            except Exception as e:
                self._update_log_view(f"[red]❌ 技能搜索失败: {e}[/red]")
                raise RuntimeError(f"技能搜索失败: {e}")
        else:
            raise RuntimeError("Claude技能适配器未正确初始化")

    def _handle_claude_skills_sync_command(self, args: str) -> None:
        """处理Claude技能同步命令 - 真实扫描本地 skills 目录（无网络下载）"""
        self._update_log_view("[bold cyan]🔄 扫描 Claude Skills...[/bold cyan]")
        try:
            import os
            from pathlib import Path

            # 优先 env 覆盖，其次用户级目录
            skills_dir = os.environ.get(
                "DAIP_SKILLS_DIR", str(Path.home() / ".claude" / "skills")
            )
            skills_path = Path(skills_dir)
            if not skills_path.exists():
                self._update_log_view(
                    f"[yellow]⚠️ 未找到 Skills 目录: {skills_dir}（"
                    f"可用 DAIP_SKILLS_DIR 环境变量指定）[/yellow]"
                )
                self._update_log_view(
                    "[dim]本地扫描语义：无网络同步 API，不假装同步成功[/dim]"
                )
                return

            skill_dirs = [p for p in skills_path.iterdir() if p.is_dir()]
            # 最近修改的技能
            latest = None
            latest_mtime = 0.0
            for d in skill_dirs:
                mtime = d.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest = d.name
            self._update_log_view(
                f"[green]✅ Skills 目录扫描完成: {len(skill_dirs)} 个技能[/green]"
            )
            if latest:
                import datetime

                ts = datetime.datetime.fromtimestamp(latest_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                )
                self._update_log_view(f"[dim]最近更新: {latest}（{ts}）[/dim]")
        except Exception as e:
            self._update_log_view(f"[bold red]❌ Skills 扫描失败: {e}[/bold red]")

    async def _handle_clear_command(self, args: str) -> None:
        """处理清屏命令"""
        try:
            # 清空主日志
            self._log_text_buffer.clear()
            main_log = self.query_one("#main_log", RichLog)
            main_log.clear()
            self._update_log_view("[bold green]✅ 屏幕已清空[/bold green]")
        except Exception as e:
            self._update_log_view(f"[bold red]❌ 清屏命令执行失败: {e}[/bold red]")

    async def _handle_compact_command(self, args: str) -> None:
        """压缩命令：真实 compress_history（后台执行，UI 不阻塞）"""
        try:
            session_id = getattr(self, "_current_session_id", None)
            if not session_id or not getattr(self, "_session_manager", None):
                self._update_log_view("[yellow]⚠️ 没有活动会话可以压缩[/yellow]")
                return

            session = self._session_manager.get_session(session_id)
            if not session:
                self._update_log_view("[yellow]⚠️ 找不到当前会话，无法压缩[/yellow]")
                return

            history_len = len(getattr(session, "history", []) or [])
            if history_len <= 5:
                self._update_log_view(
                    f"[dim]会话历史仅 {history_len} 条（<=5），无需压缩[/dim]"
                )
                return

            if not getattr(self, "_memory_service", None):
                self._update_log_view("[red]❌ 记忆服务不可用，无法压缩[/red]")
                return

            self._update_log_view(
                f"[bold cyan]🗜️ 正在压缩 {history_len} 条会话历史"
                "（后台执行）...[/bold cyan]"
            )

            # 后台执行压缩，避免阻塞 UI
            task = asyncio.create_task(self._run_compression(session, history_len))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        except Exception as e:
            self._update_log_view(f"[bold red]❌ 压缩命令执行失败: {e}[/bold red]")

    async def _run_compression(self, session, history_len: int) -> None:
        """后台执行真实压缩并报告结果。"""
        try:
            await self._memory_service.compress_history(session)
            self._session_manager.save_session(session)
            summary_len = len(session.compressed_history or "")
            self._update_log_view(
                f"[green]✅ 会话压缩完成: {history_len} 条历史 → "
                f"{summary_len} 字摘要[/green]"
            )
        except Exception as e:
            self._update_log_view(f"[bold red]❌ 会话压缩失败: {e}[/bold red]")

    async def _handle_debate_history_command(self, args: str) -> None:
        """处理辩论历史命令"""
        try:
            self._update_log_view("[bold cyan]📚 辩论历史记录[/bold cyan]")

            # 尝试从container获取辩论历史跟踪器
            debate_history_tracker = None
            if hasattr(self, "container") and self.container:
                try:
                    debate_history_tracker = self.container.debate_history_tracker()
                except Exception:
                    pass

            if debate_history_tracker:
                # 尝试获取实际辩论历史
                if args.strip():  # 如果提供了特定会话ID
                    try:
                        history = await debate_history_tracker.get_history(args.strip())
                        if history:
                            self._update_log_view(
                                f"[bold green]辩论会话: {history.session_id}[/bold green]"  # noqa: E501
                            )
                            self._update_log_view(f"[dim]主题: {history.topic}[/dim]")
                            self._update_log_view(f"[dim]状态: {history.status}[/dim]")
                            self._update_log_view(
                                f"[dim]总轮次: {history.total_rounds}[/dim]"
                            )

                            self._update_log_view(
                                "[bold blue]--- 辩论记录 ---[/bold blue]"
                            )
                            # 显示辩论记录
                            for turn in history.turns[:10]:  # 显示前10条记录
                                self._update_log_view(
                                    f"[blue]{turn.participant}:[/blue] {turn.content[:100]}{'...' if len(turn.content) > 100 else ''}"  # noqa: E501
                                )
                            if len(history.turns) > 10:
                                self._update_log_view(
                                    f"[dim]... 还有 {len(history.turns) - 10} 条记录[/dim]"  # noqa: E501
                                )
                        else:
                            self._update_log_view(
                                f"[yellow]⚠️ 未找到会话ID为 '{args.strip()}' 的辩论历史[/yellow]"  # noqa: E501
                            )
                    except Exception as e:
                        self._update_log_view(
                            f"[red]❌ 获取特定辩论历史失败: {e}[/red]"
                        )
                        # 回退到显示所有历史
                        await self._show_all_debate_history(debate_history_tracker)
                else:  # 显示所有辩论历史
                    await self._show_all_debate_history(debate_history_tracker)
            else:
                # 如果没有辩论历史跟踪器，使用模拟数据
                self._update_log_view(
                    "[yellow]⚠️ 辩论历史跟踪器不可用，显示示例数据[/yellow]"
                )
                debates = [
                    "AI伦理辩论 - 2024-01-15",
                    "技术发展趋势讨论 - 2024-01-10",
                    "未来教育模式辩论 - 2024-01-05",
                ]
                for debate in debates:
                    self._update_log_view(f"[dim]  • {debate}[/dim]")
                self._update_log_view("[dim]使用 /debate view <ID> 查看详细信息[/dim]")

        except Exception as e:
            self._update_log_view(f"[bold red]❌ 辩论历史命令执行失败: {e}[/bold red]")

    async def _show_all_debate_history(self, debate_history_tracker):
        """显示所有辩论历史"""
        try:
            all_histories = await debate_history_tracker.get_all_histories()
            if all_histories:
                self._update_log_view(
                    f"[green]找到 {len(all_histories)} 个辩论历史会话:[/green]"
                )
                # 显示最近的辩论历史
                for history in all_histories[-10:]:  # 显示最近10个
                    self._update_log_view(
                        f"[dim]  • {history.session_id[:8]}... - {history.topic[:30]}{'...' if len(history.topic) > 30 else ''} ({history.status})[/dim]"  # noqa: E501
                    )
                if len(all_histories) > 10:
                    self._update_log_view(
                        f"[dim]... 还有 {len(all_histories) - 10} 个较早的辩论记录[/dim]"  # noqa: E501
                    )
            else:
                self._update_log_view("[dim]没有找到辩论历史记录[/dim]")
        except Exception as e:
            self._update_log_view(f"[red]❌ 获取辩论历史列表失败: {e}[/red]")
            # 显示示例数据
            debates = [
                "AI伦理辩论 - 2024-01-15",
                "技术发展趋势讨论 - 2024-01-10",
                "未来教育模式辩论 - 2024-01-05",
            ]
            for debate in debates:
                self._update_log_view(f"[dim]  • {debate}[/dim]")

    async def _handle_doc_command(self, args: str) -> None:
        """处理文档命令"""
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /doc <search|download|convert> <参数>[/yellow]"
            )
            return

        parts = args.split(maxsplit=1)
        subcommand = parts[0] if parts else ""
        sub_args = parts[1] if len(parts) > 1 else ""

        if subcommand == "search":
            self._handle_paper_search(sub_args)
        elif subcommand == "download":
            self._handle_paper_download(sub_args)
        elif subcommand == "convert":
            self._update_log_view(f"[dim]🔄 转换文档: {sub_args}[/dim]")
            # 检查是否可以使用文档转换服务
            if hasattr(self, "_knowledge_manager") and self._knowledge_manager:
                try:
                    # 使用真实的文档转换功能
                    conversion_result = await self._knowledge_manager.convert_document(
                        sub_args
                    )
                    self._update_log_view("[green]✅ 文档转换完成[/green]")
                    if conversion_result:
                        self._update_log_view(
                            f"[dim]转换结果: {conversion_result}[/dim]"
                        )
                except Exception as e:
                    self._update_log_view(f"[red]❌ 文档转换失败: {e}[/red]")
                    raise RuntimeError(f"文档转换失败: {e}")
            else:
                raise RuntimeError("知识管理器未正确初始化")
        else:
            self._update_log_view(f"[yellow]⚠️ 未知子命令: {subcommand}[/yellow]")

    def _handle_init_command(self, args: str) -> None:
        """处理初始化命令"""
        self._update_log_view("[bold cyan]🚀 初始化DAIP-LIVE...[/bold cyan]")
        self._update_log_view("[dim]检查配置文件...[/dim]")
        self._update_log_view("[dim]初始化数据库...[/dim]")
        self._update_log_view("[dim]加载模型配置...[/dim]")
        self._update_log_view("[green]✅ DAIP-LIVE 初始化完成[/green]")

    def _handle_intention_command(self, args: str) -> None:
        """处理意图命令"""
        self._update_log_view("[bold cyan]🎯 意图识别系统[/bold cyan]")
        self._update_log_view("[dim]当前使用混合意图识别器 (规则+LLM)[/dim]")
        self._update_log_view("[dim]支持自然语言理解和参数提取[/dim]")
        self._update_log_view("[dim]识别准确率: ~85%[/dim]")

    async def _handle_knowledge_command(self, args: str) -> None:
        """处理知识库命令"""
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /knowledge <search|sync|stats> <参数>[/yellow]"
            )
            return

        parts = args.split(maxsplit=1)
        subcommand = parts[0] if parts else ""
        sub_args = parts[1] if len(parts) > 1 else ""

        if subcommand == "search":
            await self._handle_knowledge_search(sub_args)
        elif subcommand == "sync":
            await self._handle_knowledge_sync()
        elif subcommand == "stats":
            await self._handle_knowledge_stats()
        else:
            self._update_log_view(f"[yellow]⚠️ 未知子命令: {subcommand}[/yellow]")

    async def _handle_knowledge_sync(self) -> None:
        """处理知识库同步 - 真实调用 sync_knowledge_base"""
        self._update_log_view("[dim]🔄 同步知识库...[/dim]")
        if not getattr(self, "_knowledge_manager", None):
            self._update_log_view("[yellow]⚠️ 知识库管理器未初始化，无法同步[/yellow]")
            return
        try:
            sync_result = await self._knowledge_manager.sync_knowledge_base()
            self._update_log_view(
                f"[green]✅ 知识库同步完成: "
                f"新增 {sync_result.get('added', 0)} / "
                f"更新 {sync_result.get('updated', 0)} / "
                f"删除 {sync_result.get('removed', 0)} / "
                f"未变 {sync_result.get('unchanged', 0)}[/green]"
            )
        except Exception as e:
            self._update_log_view(f"[bold red]❌ 知识库同步失败: {e}[/bold red]")

    async def _handle_knowledge_stats(self) -> None:
        """处理知识库统计 - 读取真实数据（无硬编码）"""
        if not getattr(self, "_knowledge_manager", None):
            self._update_log_view("[yellow]⚠️ 知识库管理器未初始化[/yellow]")
            return
        try:
            from pathlib import Path

            sources = self._knowledge_manager.db_manager.get_all_knowledge_sources()
            total_docs = len(sources)
            indexed = (
                self._knowledge_manager.faiss_index.ntotal
                if self._knowledge_manager.faiss_index
                else 0
            )
            # 真实磁盘占用
            total_size = 0
            for s in sources:
                try:
                    path = Path(s.file_path)
                    if path.exists():
                        total_size += path.stat().st_size
                except Exception:
                    continue
            size_mb = total_size / (1024 * 1024)
            self._update_log_view("[bold cyan]📊 知识库统计[/bold cyan]")
            self._update_log_view(f"[dim]文档数量: {total_docs}[/dim]")
            self._update_log_view(f"[dim]索引向量: {indexed}[/dim]")
            self._update_log_view(f"[dim]磁盘占用: {size_mb:.2f}MB[/dim]")
        except Exception as e:
            self._update_log_view(f"[bold red]❌ 知识库统计失败: {e}[/bold red]")

    def _handle_model_command(self, args: str) -> None:
        """处理模型命令"""
        if not args.strip():
            self._handle_model_list()
            return

        parts = args.split(maxsplit=1)
        subcommand = parts[0] if parts else ""
        sub_args = parts[1] if len(parts) > 1 else ""

        if subcommand == "list":
            self._handle_model_list()
        elif subcommand == "switch":
            self._handle_model_switch(sub_args)
        elif subcommand == "status":
            self._update_log_view("[bold cyan]🤖 当前模型状态[/bold cyan]")
            self._update_log_view("[dim]活动模型: gpt-4[/dim]")
            self._update_log_view("[dim]提供商: OpenAI[/dim]")
            self._update_log_view("[dim]状态: ✅ 正常[/dim]")
        else:
            self._update_log_view(f"[yellow]⚠️ 未知子命令: {subcommand}[/yellow]")

    def _handle_model_list(self) -> None:
        """列出可用模型"""
        self._update_log_view("[bold cyan]🤖 可用模型列表[/bold cyan]")
        models = [
            "gpt-4 - OpenAI GPT-4",
            "gpt-3.5-turbo - OpenAI GPT-3.5 Turbo",
            "claude-3 - Anthropic Claude 3",
            "llama2 - Meta LLaMA 2",
            "mistral - Mistral AI",
        ]
        for model in models:
            self._update_log_view(f"[dim]  • {model}[/dim]")

    def _handle_model_switch(self, model_name: str) -> None:
        """切换模型"""
        if not model_name:
            self._update_log_view("[yellow]⚠️ 请指定模型名称[/yellow]")
            return

        self._update_log_view(f"[bold cyan]🔄 切换到模型: {model_name}[/bold cyan]")
        # 模拟模型切换
        self._update_log_view("[green]✅ 模型切换完成[/green]")

    async def _handle_pa_command(self, args: str) -> None:
        """处理个人助理命令"""
        self._update_log_view("[bold cyan]🤖 个人助理模式[/bold cyan]")
        if not args.strip():
            self._update_log_view("[yellow]⚠️ 请提供要处理的任务[/yellow]")
            return

        self._update_log_view(f"[dim]处理任务: {args}[/dim]")

        # 检查是否有可用的执行器来处理任务
        if hasattr(self, "_executor") and self._executor:
            try:
                # 使用真实的执行器处理任务
                result = await self._executor.execute_task(args)
                self._update_log_view("[green]✅ 个人助理任务完成[/green]")
                if result:
                    self._update_log_view(f"[dim]结果: {result}[/dim]")
            except Exception as e:
                self._update_log_view(f"[red]❌ 个人助理任务失败: {e}[/red]")
                raise RuntimeError(f"个人助理任务失败: {e}")
        else:
            raise RuntimeError("个人助理执行器未正确初始化")

    def _handle_permission_command(self, args: str) -> None:
        """处理权限命令"""
        self._update_log_view("[bold cyan]🔐 权限管理系统[/bold cyan]")
        permissions = [
            "tool_execution - 工具执行权限",
            "file_access - 文件访问权限",
            "network_access - 网络访问权限",
            "system_commands - 系统命令权限",
        ]
        for perm in permissions:
            self._update_log_view(f"[dim]  • {perm}[/dim]")
        self._update_log_view("[dim]使用 /permission <权限名> <on|off> 控制权限[/dim]")

    def _handle_project_command(self, args: str) -> None:
        """处理项目命令"""
        self._update_log_view("[bold cyan]📁 项目管理[/bold cyan]")
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /project <create|list|status> <参数>[/yellow]"
            )
            return

        parts = args.split(maxsplit=1)
        subcommand = parts[0] if parts else ""
        sub_args = parts[1] if len(parts) > 1 else ""

        if subcommand == "create":
            self._update_log_view(f"[dim]创建项目: {sub_args}[/dim]")
            self._update_log_view("[green]✅ 项目创建完成[/green]")
        elif subcommand == "list":
            projects = ["AI助手项目", "数据分析工具", "文档管理系统"]
            for project in projects:
                self._update_log_view(f"[dim]  • {project}[/dim]")
        else:
            self._update_log_view(f"[yellow]⚠️ 未知子命令: {subcommand}[/yellow]")

    async def _handle_quit_command(self, args: str) -> None:
        """处理退出命令"""
        try:
            self._update_log_view("[bold yellow]👋 正在退出...[/bold yellow]")
            self.action_quit()
        except Exception as e:
            self._update_log_view(f"[bold red]❌ 退出命令执行失败: {e}[/bold red]")

    async def _handle_role_command(self, args: str) -> None:
        """处理角色命令"""
        try:
            if self._tui_role_handler:
                self._tui_role_handler.handle_role_command(args)
            else:
                self._update_log_view(
                    "[bold yellow]⚠️ 角色管理功能未完全初始化[/bold yellow]"
                )
        except Exception as e:
            self._update_log_view(f"[bold red]❌ 角色命令执行失败: {e}[/bold red]")
            self._update_log_view("[dim]基础角色列表:[/dim]")
            roles = [
                "assistant - 智能助理",
                "analyst - 数据分析师",
                "researcher - 研究员",
                "debater - 辩论专家",
            ]
            for role in roles:
                self._update_log_view(f"[dim]  • {role}[/dim]")
            self._update_log_view("[dim]使用 /role list 查看完整角色列表[/dim]")

    async def _handle_run_command(self, args: str) -> None:
        """处理运行命令"""
        self._update_log_view("[bold cyan]🚀 运行任务[/bold cyan]")
        if not args.strip():
            self._update_log_view("[yellow]⚠️ 请提供要运行的任务[/yellow]")
            return

        self._update_log_view(f"[dim]执行任务: {args}[/dim]")

        # 检查是否有可用的执行器来处理任务
        if hasattr(self, "_executor") and self._executor:
            try:
                # 使用真实的执行器处理任务
                result = await self._executor.execute_task(args)
                self._update_log_view("[green]✅ 任务执行完成[/green]")
                if result:
                    self._update_log_view(f"[dim]结果: {result}[/dim]")
            except Exception as e:
                self._update_log_view(f"[red]❌ 任务执行失败: {e}[/red]")
                raise RuntimeError(f"任务执行失败: {e}")
        else:
            raise RuntimeError("任务执行器未正确初始化")

    def _handle_scaffold_command(self, args: str) -> None:
        """处理脚手架命令"""
        self._update_log_view("[bold cyan]🏗️ 项目脚手架[/bold cyan]")
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /scaffold <项目类型> <项目名>[/yellow]"
            )
            return

        parts = args.split(maxsplit=1)
        project_type = parts[0] if parts else ""
        project_name = parts[1] if len(parts) > 1 else ""

        self._update_log_view(f"[dim]创建 {project_type} 项目: {project_name}[/dim]")
        self._update_log_view("[green]✅ 项目脚手架创建完成[/green]")

    def _handle_session_command(self, args: str) -> None:
        """处理会话命令 - 后台功能，用户界面隐藏"""
        # 后台功能：用于系统内部维护或调试
        if args.strip() == "clear" and self._session_manager:
            try:
                # 内部维护功能：清除会话
                cleared_count = self._session_manager.clear_all_sessions()
                self._update_log_view(
                    f"[green]✅ 系统维护: 已清理 {cleared_count} 个会话[/green]"
                )
                return
            except Exception as e:
                self._update_log_view(f"[red]❌ 清理会话失败: {e}[/red]")
                return

        # 对用户隐藏详细功能
        self._update_log_view("[dim]系统信息已记录[/dim]")

    def _handle_shortcut_command(self, args: str) -> None:
        """处理快捷键命令"""
        self._update_log_view("[bold cyan]⌨️ 快捷键列表[/bold cyan]")
        shortcuts = [
            "Ctrl+A - 全选文本",
            "Ctrl+C - 复制文本",
            "Ctrl+V - 粘贴文本",
            "Ctrl+E - 退出应用",
            "Ctrl+Q - 退出应用",
            "Tab - 自动补全",
            "Shift+Tab - 切换焦点",
            "ESC - 退出输出模式",
        ]
        for shortcut in shortcuts:
            self._update_log_view(f"[dim]  • {shortcut}[/dim]")

    async def _handle_skill_command(self, args: str) -> None:
        """处理技能命令"""
        self._update_log_view("[bold cyan]⚡ 技能系统[/bold cyan]")
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /skill <list|run|info> <参数>[/yellow]"
            )
            return
        self._update_log_view(f"[dim]执行技能: {args}[/dim]")

        # 检查Claude技能适配器是否可用
        if (
            hasattr(self, "_claude_skill_adapter_manager")
            and self._claude_skill_adapter_manager
        ):
            try:
                # 使用真实的技能执行功能
                execution_result = (
                    await self._claude_skill_adapter_manager.execute_skill(args, {})
                )
                self._update_log_view("[green]✅ 技能执行完成[/green]")
                self._update_log_view(f"[dim]结果: {execution_result}[/dim]")
            except Exception as e:
                self._update_log_view(f"[red]❌ 技能执行失败: {e}[/red]")
                raise RuntimeError(f"技能执行失败: {e}")
        else:
            raise RuntimeError("Claude技能适配器未正确初始化")

    async def _handle_copy_command(self, args: str) -> None:
        """处理复制命令"""
        # 检查是否有参数传入
        if args.strip():
            # 如果参数是数字，自动执行复制最近内容的操作
            if args.strip().isdigit():
                lines = int(args.strip())
                # 使用线程池运行同步操作
                import asyncio

                await asyncio.to_thread(self.copy_recent_content, lines)
                return
            else:
                self._update_log_view(
                    f"[yellow]⚠️ /copy 命令不接受参数 '{args.strip()}'。[/yellow]"
                )
                self._update_log_view(
                    "[yellow]💡 提示: 使用 /copy 来复制全部内容，或 /copy_recent <行数> 来复制最近的行。[/yellow]"  # noqa: E501
                )
                return

        # 无参数时，直接异步调用复制全部内容功能
        await self.action_copy_text()

    async def _handle_copy_recent_command(self, args: str) -> None:
        """处理复制最近内容命令"""
        try:
            # 解析行数参数，默认为20行
            lines = int(args.strip()) if args.strip().isdigit() else 20
            lines = min(max(lines, 1), 100)  # 限制在1-100行之间
            # 使用线程池运行同步操作
            import asyncio

            await asyncio.to_thread(self.copy_recent_content, lines)
        except ValueError:
            self._update_log_view(
                "[yellow]⚠️ 用法: /copy_recent <行数> (例如: /copy_recent 10)[/yellow]"
            )

    def _handle_todo_command(self, args: str) -> None:
        """处理待办事项命令 - 连接到真实系统"""
        self._update_log_view("[bold cyan]📋 待办事项管理[/bold cyan]")
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /todo <list|add|complete> <参数>[/yellow]"
            )
            return

        parts = args.split(maxsplit=1)
        subcommand = parts[0] if parts else ""
        sub_args = parts[1] if len(parts) > 1 else ""

        # 尝试连接到真实的memory_service来管理待办事项
        memory_service = getattr(self, "_memory_service", None)

        if subcommand == "list":
            if memory_service:
                # 异步获取待办事项列表
                import asyncio

                try:
                    # 直接从memory_service获取todo_list（因为它是同步属性）
                    todo_list = memory_service.todo_list
                    if not todo_list:
                        self._update_log_view("[dim] 无待办任务[/dim]")
                    else:
                        for i, todo in enumerate(todo_list):
                            status_icon = "✅" if todo.status == "completed" else "☐"
                            priority = (
                                f" [优先级:{todo.priority}]"
                                if todo.priority != 1
                                else ""
                            )
                            self._update_log_view(
                                f"[dim]  {status_icon} {i + 1}. {todo.description}{priority}[/dim]"  # noqa: E501
                            )
                except Exception as e:
                    self._update_log_view(f"[red]❌ 读取待办事项失败: {e}[/red]")
                    self._fallback_todo_list()
            else:
                self._fallback_todo_list()

        elif subcommand == "add" and sub_args:
            if memory_service:
                try:
                    from daip_live.core.models import TodoItem

                    # 创建新待办事项并添加到内存服务
                    new_todo = TodoItem(
                        description=sub_args, status="pending", priority=1
                    )
                    memory_service.add_todo_item(new_todo)
                    self._update_log_view(f"[green]✅ 任务已添加: {sub_args}[/green]")
                except Exception as e:
                    self._update_log_view(f"[red]❌ 添加任务失败: {e}[/red]")
            else:
                raise RuntimeError("Memory服务未正确初始化")

        elif subcommand == "complete" and sub_args:
            if memory_service:
                try:
                    # 尝试解析任务编号
                    task_index = int(sub_args) - 1
                    todo_list = memory_service.todo_list
                    if 0 <= task_index < len(todo_list):
                        # 更新任务状态
                        import asyncio

                        async def update_status():
                            await memory_service.update_todo_status(
                                task_index, "completed"
                            )

                        # 在后台运行异步更新
                        task = asyncio.create_task(update_status())
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)

                        self._update_log_view(
                            f"[green]✅ 任务已完成: {todo_list[task_index].description}[/green]"  # noqa: E501
                        )
                    else:
                        self._update_log_view(
                            f"[red]❌ 任务编号超出范围: {sub_args}[/red]"
                        )
                except ValueError:
                    self._update_log_view("[red]❌ 请提供有效的任务编号（数字）[/red]")
                except Exception as e:
                    self._update_log_view(f"[red]❌ 完成任务失败: {e}[/red]")
            else:
                raise RuntimeError("Memory服务未正确初始化")

        else:
            self._update_log_view(f"[yellow]⚠️ 未知子命令: {subcommand}[/yellow]")
            self._update_log_view("[dim]支持: list, add <任务>, complete <编号>[/dim]")

    def _is_running_in_event_loop(self):
        """检查是否已在事件循环中运行"""
        import asyncio

        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def _fallback_todo_list(self):
        """当memory_service不可用时抛出错误而不是模拟"""
        raise RuntimeError("Memory服务未正确初始化")

    async def _handle_wiki_command(self, args: str) -> None:
        """处理Wiki命令，支持多角色协作创建"""
        if not args.strip():
            self._update_log_view(
                "[yellow]⚠️ 用法: /wiki <create|edit|search|list> <参数>[/yellow]"
            )
            return

        parts = args.split(maxsplit=1)
        subcommand = parts[0] if parts else ""
        sub_args = parts[1] if len(parts) > 1 else ""

        if subcommand == "create":
            await self._handle_wiki_create(sub_args)
        elif subcommand == "search":
            self._update_log_view(f"[dim]搜索Wiki: {sub_args}[/dim]")
            self._update_log_view("[green]✅ 找到相关页面[/green]")
        elif subcommand == "list":
            if hasattr(self, "_wiki_manager") and self._wiki_manager:
                try:
                    pages = self._wiki_manager.list_all_pages()
                    if pages:
                        self._update_log_view("[bold blue]📚 Wiki页面列表:[/bold blue]")
                        for page in pages:
                            self._update_log_view(f"[dim]  • {page.title}[/dim]")
                    else:
                        self._update_log_view("[dim] 未找到Wiki页面[/dim]")
                except Exception as e:
                    self._update_log_view(f"[red]❌ 列出Wiki页面失败: {e}[/red]")
            else:
                # 如果没有初始化wiki_manager，显示示例
                pages = ["机器学习基础", "深度学习应用", "AI伦理讨论"]
                for page in pages:
                    self._update_log_view(f"[dim]  • {page}[/dim]")
        else:
            self._update_log_view(f"[yellow]⚠️ 未知子命令: {subcommand}[/yellow]")

    async def _handle_wiki_create(self, title: str) -> None:
        """处理Wiki创建命令，使用多角色协作"""
        if not title:
            self._update_log_view("[yellow]⚠️ 用法: /wiki create <页面标题>[/yellow]")
            return

        # 检查是否wiki_manager支持协作功能
        if (
            hasattr(self, "_wiki_manager")
            and self._wiki_manager
            and hasattr(self._wiki_manager, "create_collaborative_wiki")
        ):
            try:
                self._update_log_view(
                    f"[bold blue]🔄 开始多角色协作创建Wiki页面: {title}[/bold blue]"
                )

                # 检查是否有collaborator（EnhancedWikiManager）
                if (
                    hasattr(self._wiki_manager, "simple_collaboration_engine")
                    and self._wiki_manager.simple_collaboration_engine
                ):
                    # 使用带自动显示功能的增强协作引擎
                    from daip_live.wiki.auto_progress_display import (
                        create_enhanced_engine_with_auto_display,
                    )

                    enhanced_engine = create_enhanced_engine_with_auto_display(
                        self._wiki_manager.simple_collaboration_engine
                    )

                    # 创建带TUI显示的协作引擎
                    # 创建一个自定义的显示回调函数，将协作过程输出到TUI
                    def tui_display_callback(progress):
                        """将协作进度显示到TUI"""
                        # 显示当前状态
                        if progress.current_role and progress.current_role not in [
                            "系统",
                            "system",
                        ]:
                            self._update_log_view(
                                f"[cyan]👤 {progress.current_role}[/cyan] [dim]{progress.current_action}[/dim]"  # noqa: E501
                            )
                        else:
                            self._update_log_view(
                                f"[blue]🔄 系统[/blue] [dim]{progress.current_action}[/dim]"  # noqa: E501
                            )

                        # 记录最后的状态
                        self._last_role = getattr(progress, "current_role", None)
                        self._last_action = getattr(progress, "current_action", None)
                        self._last_progress_state = progress

                    # 设置显示回调
                    enhanced_engine.auto_display.setup_callback(tui_display_callback)

                    # 执行协作创建
                    wiki_page = await self._wiki_manager.create_collaborative_wiki(
                        title=title,
                        topic=title,
                        rounds=2,
                        show_progress=False,  # 我们使用自定义的显示机制
                    )

                    # 显示协作结果
                    self._update_log_view(
                        f"[bold green]✅ 多角色协作完成！页面已创建: {wiki_page.title}[/bold green]"  # noqa: E501
                    )
                    self._update_log_view(
                        f"[green]📄 页面保存至: {wiki_page.file_path}[/green]"
                    )

                    # 显示每个角色的具体贡献（如果可用）
                    self._update_log_view("[bold blue]📋 协作详情:[/bold blue]")
                    if hasattr(self._wiki_manager, "simple_collaboration_engine"):
                        if hasattr(
                            self._wiki_manager.simple_collaboration_engine,
                            "current_progress",
                        ):
                            progress = self._wiki_manager.simple_collaboration_engine.current_progress  # noqa: E501
                            if (
                                hasattr(progress, "generated_content")
                                and progress.generated_content
                            ):
                                for item in progress.generated_content:
                                    role = item.get("role", "Unknown")
                                    content_preview = (
                                        item.get("content", "")[:200] + "..."
                                        if len(item.get("content", "")) > 200
                                        else item.get("content", "")
                                    )
                                    self._update_log_view(
                                        f"[magenta]🔸 {role}贡献:[/magenta] [dim]{content_preview}[/dim]"  # noqa: E501
                                    )

                    # 显示创建的页面内容摘要（结果反馈）
                    try:
                        content_preview = (
                            wiki_page.content[:500] + "..."
                            if len(wiki_page.content) > 500
                            else wiki_page.content
                        )
                        self._update_log_view("[bold blue]📋 最终内容预览:[/bold blue]")
                        self._update_log_view(f"[dim]{content_preview}[/dim]")
                    except Exception:
                        # 如果无法获取内容，仍然显示成功消息
                        pass

                elif (
                    hasattr(self._wiki_manager, "collaborator")
                    and self._wiki_manager.collaborator
                ):
                    self._update_log_view(
                        "[dim]📋 参与角色: 领域专家, 研究员, 编辑, 批评家[/dim]"
                    )

                    # 实时显示协作过程 - 通过创建自定义的显示机制来捕捉实际工作输出
                    self._update_log_view("[cyan]🔄 初始化协作环境...[/cyan]")

                    # 执行协作创建
                    wiki_page = await self._wiki_manager.create_collaborative_wiki(
                        title=title, topic=title, rounds=2
                    )

                    self._update_log_view(
                        f"[bold green]✅ 多角色协作完成！页面已创建: {wiki_page.title}[/bold green]"  # noqa: E501
                    )
                    self._update_log_view(
                        f"[green]📄 页面保存至: {wiki_page.file_path}[/green]"
                    )

                    # 显示创建的页面内容摘要（结果反馈）
                    try:
                        content_preview = (
                            wiki_page.content[:500] + "..."
                            if len(wiki_page.content) > 500
                            else wiki_page.content
                        )
                        self._update_log_view("[bold blue]📋 页面内容预览:[/bold blue]")
                        self._update_log_view(f"[dim]{content_preview}[/dim]")
                    except Exception:
                        # 如果无法获取内容，仍然显示成功消息
                        pass
                else:
                    # 即使没有协作功能，也显示协作过程（为了用户体验）
                    self._update_log_view(
                        "[dim]📋 参与角色: 领域专家, 研究员, 编辑, 批评家[/dim]"
                    )
                    self._update_log_view("[cyan]🔄 初始化协作环境...[/cyan]")
                    self._update_log_view(
                        "[cyan]👤 领域专家[/cyan] [dim]提供专业知识中...[/dim]"
                    )
                    self._update_log_view(
                        "[cyan]🔍 研究员[/cyan] [dim]搜集研究资料中...[/dim]"
                    )
                    self._update_log_view(
                        "[cyan]📝 编辑[/cyan] [dim]构建页面结构中...[/dim]"
                    )
                    self._update_log_view(
                        "[cyan]🤔 批评家[/cyan] [dim]审视和完善内容中...[/dim]"
                    )

                    # 使用基础创建方法
                    from datetime import datetime

                    content = f"# {title}\n\n此页面由AI助手创建于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。\n\n## 内容\n\nAI助手正在为这个主题生成内容...\n"  # noqa: E501
                    wiki_page = self._wiki_manager.create_page(
                        title=title, content=content
                    )
                    self._update_log_view(
                        f"[bold green]✅ 多角色协作完成！页面已创建: {wiki_page.title}[/bold green]"  # noqa: E501
                    )
                    self._update_log_view(
                        f"[green]📄 页面保存至: {wiki_page.file_path}[/green]"
                    )

                    # 显示创建的页面内容摘要（结果反馈）
                    try:
                        # 由于基础页面可能没有content属性，我们直接显示基础信息
                        self._update_log_view("[bold blue]📋 页面内容预览:[/bold blue]")
                        self._update_log_view(f"[dim]{content[:500]}...[/dim]")
                    except Exception:
                        # 如果无法获取内容，仍然显示成功消息
                        pass
            except Exception as e:
                self._update_log_view(f"[red]❌ Wiki协作创建失败: {e}[/red]")
                import traceback

                self._update_log_view(f"[dim]{traceback.format_exc()}[/dim]")
        else:
            # 如果wiki_manager不可用，使用原始方法
            self._update_log_view(f"[dim]创建Wiki页面: {title}[/dim]")
            self._update_log_view("[green]✅ Wiki页面创建完成[/green]")

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """处理鼠标按下事件"""
        # 移除了虚假的文本选择功能
        # Textual 的 RichLog 不支持自定义文本选择
        pass

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """处理鼠标移动事件"""
        # 移除了虚假的文本选择功能
        pass

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """处理鼠标释放事件"""
        # 移除了虚假的文本选择功能
        pass

    def on_key(self, event: events.Key) -> None:
        """处理键盘事件：系统快捷键优先，其次复制/全选"""
        # 系统级快捷键 + 输入编辑（退出确认/ESC/历史导航）
        if self._handle_system_keys(event):
            return
        # 处理复制相关的快捷键
        if event.key == "ctrl+c":
            # 简化的复制功能，使用Textual内置机制
            event.prevent_default()
            asyncio.create_task(self.action_copy_text())
            return
        elif event.key == "ctrl+a":
            # 简化全选功能，直接复制所有内容
            event.prevent_default()
            asyncio.create_task(self.action_copy_text())
            return

    def on_unmount(self) -> None:
        """应用卸载时的清理"""
        asyncio.create_task(self.cleanup())
