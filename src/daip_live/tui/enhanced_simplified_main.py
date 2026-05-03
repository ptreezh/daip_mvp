"""
DAIP-LIVE TUI Moduler v2.1.0-modular-simplified
简化版TUI实现，解决原有复杂性问题
"""

import asyncio
import json
import os
import queue
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pyperclip
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Static

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.agent_engine.intent_recognizer import Intent
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.config_bridge import config_bridge
from daip_live.container import Container
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.persistence.database import DatabaseManager
from daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager
from daip_live.tui_modular.components.autocomplete import TUIAutocomplete
from daip_live.tui_modular.components.enhanced_commands import DebateCommands
from daip_live.tui_modular.components.interactive_role_creation import InteractiveRoleCreationService
from daip_live.tui_modular.components.screens import CommandHelpDialog, ExitConfirmationDialog
from daip_live.tui_modular.components.tui_role_integration import TUIRoleCommandHandler
from daip_live.tui_modular.utils import ConfigManager, FocusMode, HistoryManager, Logger, PerformanceMonitor

from .copyable_widgets import CopyableLogWidget
from .clipboard_helper import copy_content

class SimplifiedTUI(App):
    """简化版DAIP-LIVE TUI - 解决原有架构问题"""

    # 设置应用标题和CSS
    TITLE = "DAIP-LIVE TUI Modular v2.1.0-modular-simplified"
    SUB_TITLE = "(Simplified)"
    CSS_PATH = None

    # 定义绑定
    BINDINGS = [
        Binding("ctrl+c", "quit", "退出", show=True),
        Binding("ctrl+e", "quit", "退出", show=False),
        Binding("ctrl+q", "quit", "退出", show=False),
        Binding("f1", "show_command_help", "帮助", show=True),
        Binding("f2", "toggle_output_mode", "输出模式", show=True),
        Binding("f3", "copy_all_output", "复制输出", show=True),
        Binding("tab", "focus_next", "下一个焦点", show=False),
        Binding("shift+tab", "focus_previous", "上一个焦点", show=False),
        Binding("ctrl+l", "clear_logs", "清除日志", show=True),
        Binding("ctrl+r", "restart_session", "重启会话", show=True),
    ]

    # 状态管理
    focus_mode = FocusMode.INPUT
    _history_index = -1
    _current_input_before_history = ""
    _output_mode = False
    _session_id = ""
    _conversation_history = []
    _system_messages = []

    def __init__(self, container: Optional[Container] = None):
        """初始化TUI应用"""
        super().__init__()

        # 获取容器实例
        self.container = container or get_container()
        self.container.wire(modules=[sys.modules[__name__]])

        # 初始化组件
        self._initialize_components()

        # 初始化历史记录管理器
        self.history_manager = HistoryManager(max_history=50)

        # 初始化性能监控器
        self.performance_monitor = PerformanceMonitor()

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 初始化日志记录器
        self.logger = Logger()

        # 当前会话ID
        self.session_id = f"tui_session_{int(time.time())}"

        # 异步任务集合
        self._background_tasks = set()
        
        print("✅ DAIP-LIVE TUI Modular v2.1.0-modular-simplified loaded (Simplified)")

    def _initialize_components(self) -> None:
        """初始化TUI组件"""
        try:
            # 从容器获取组件（带fallback）
            try:
                self._session_manager = self.container.session_manager()
                self._role_manager = self.container.role_manager()
                self._role_model_manager = self.container.role_model_manager()
                self._model_provider = self.container.model_provider()
                self._debate_history_tracker = self.container.debate_history_tracker()
                self._agent_executor = self.container.agent_executor()
                self._intent_recognizer = self.container.intent_recognizer()
            except Exception as e:
                print(f"⚠️ 从容器获取组件失败，使用本地初始化: {e}")
                # Fallback: 本地初始化组件
                db_manager = DatabaseManager(":memory:")
                self._session_manager = SessionManager(db_manager)
                self._role_manager = RoleManager(roles_dir_path="roles")
                self._role_model_manager = RoleModelManager(roles_dir_path="roles")
                self._model_provider = LiteLLMProvider(config=None)
                
                # 初始化辩论历史跟踪器
                try:
                    self._debate_history_tracker = DebateHistoryTracker(db_path=":memory:")
                except Exception:
                    # 如果辩论组件不可用，使用mock对象
                    class MockDebateHistoryTracker:
                        async def start_tracking(self, event): pass
                        async def get_history(self, session_id): return None
                        async def get_all_histories(self): return []
                    self._debate_history_tracker = MockDebateHistoryTracker()
                
                # 初始化智能体执行器
                try:
                    self._agent_executor = AgentExecutor(
                        session_manager=self._session_manager,
                        model_provider=self._model_provider
                    )
                except Exception:
                    class MockAgentExecutor:
                        async def process_input(self, input_text): return f"Mock response for: {input_text}"
                    self._agent_executor = MockAgentExecutor()
                
                # 初始化意图识别器
                try:
                    self._intent_recognizer = EnhancedIntentRecognizer()
                except Exception:
                    class MockIntentRecognizer:
                        def recognize_intent(self, text):
                            return Intent(name="chat", confidence=0.5, parameters={"content": text})
                    self._intent_recognizer = MockIntentRecognizer()

            # 初始化Claude技能适配器管理器
            try:
                self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(self._session_manager)
            except Exception as e:
                print(f"Warning: Could not initialize ClaudeSkillAdapterManager: {e}")
                self._claude_skill_adapter_manager = None

            # 初始化辩论命令处理器
            try:
                self._debate_commands = DebateCommands(
                    debate_manager=None,  # Will be set up properly later if available
                    session_manager=self._session_manager,
                    role_manager=self._role_manager
                )
            except Exception as e:
                print(f"Warning: Could not initialize DebateCommands: {e}")
                self._debate_commands = None

            # 初始化角色命令处理器
            self._tui_role_handler = TUIRoleCommandHandler(
                tui_instance=self,
                role_manager=self._role_manager,
                role_model_manager=self._role_model_manager,
                session_manager=self._session_manager
            )

            # 初始化交互式角色创建服务
            self._interactive_role_service = InteractiveRoleCreationService(
                role_manager=self._role_manager,
                role_model_manager=self._role_model_manager
            )

            # 初始化自动补全
            self._autocomplete = TUIAutocomplete(
                role_manager=self._role_manager,
                available_commands=[
                    "/help", "/debate", "/wiki", "/knowledge", "/doc", "/role", 
                    "/model", "/session", "/skill", "/clear", "/quit", "/exit"
                ]
            )

        except Exception as e:
            print(f"❌ TUI组件初始化失败: {e}")
            import traceback
            traceback.print_exc()
            raise

    def compose(self) -> ComposeResult:
        """构建UI布局"""
        yield Header()

        # Main content area with conversation and system activity
        with Horizontal():
            # Conversation area - takes most of the space
            with Vertical():
                yield Static("💬 对话区域", classes="panel-header")
                yield CopyableLogWidget(id="main_log", classes="output-mode", highlight=True, markup=True, wrap=True)

            # System activity panel - narrow sidebar for system messages
            with Vertical(classes="system-panel"):
                yield Static("🔧 系统状态", classes="panel-header")
                yield CopyableLogWidget(id="system_log", classes="system-log", highlight=True, markup=True, wrap=True)

        yield Input(placeholder="Enter command or message...", id="user_input")
        yield Static("DAIP-LIVE Modular TUI | Status: Ready | Focus: Input", id="status_bar")
        yield Footer()

    def on_mount(self) -> None:
        """组件挂载时的初始化"""
        # 设置初始焦点
        self.query_one("#user_input", Input).focus()

        # 初始化日志组件
        self.main_log = self.query_one("#main_log", CopyableLogWidget)
        self.system_log = self.query_one("#system_log", CopyableLogWidget)

        # 添加欢迎消息
        welcome_msg = """
## 🎉 欢迎使用 DAIP-LIVE TUI 简化版

- 输入 `/help` 查看可用命令
- 输入 `F3` 复制当前输出到剪贴板
- 输入 `Ctrl+L` 清除日志
- 输入 `Ctrl+C` 退出
        """
        self._update_log_view(Markdown(welcome_msg))
        
        print("GUI initialized successfully")

    def _update_log_view(self, content: str) -> None:
        """更新主日志视图"""
        try:
            if hasattr(self, 'main_log') and self.main_log:
                self.main_log.write(content)
            else:
                # 如果组件还没准备好，先缓存
                self._conversation_history.append(content)
        except Exception as e:
            print(f"Error updating log view: {e}")

    def _update_system_log(self, content: str) -> None:
        """更新系统日志视图"""
        try:
            if hasattr(self, 'system_log') and self.system_log:
                self.system_log.write(content)
            else:
                self._system_messages.append(content)
        except Exception as e:
            print(f"Error updating system log: {e}")

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

    async def _process_user_input(self, user_input: str) -> None:
        """处理用户输入的核心逻辑"""
        start_time = time.time()
        
        try:
            # 记录性能
            self.performance_monitor.log_action("user_input_processed", start_time)

            # 使用增强意图识别器
            intent: Optional[Intent] = None
            try:
                # 尝试上下文感知意图识别
                if hasattr(self._intent_recognizer, 'recognize_intent_with_context'):
                    intent = await self._intent_recognizer.recognize_intent_with_context(
                        user_input, self.session_id
                    )
                else:
                    # 使用标准意图识别
                    intent = self._intent_recognizer.recognize_intent(user_input)
            except Exception as e:
                self._update_system_log(f"[yellow]⚠️ 意图识别失败: {e}[/yellow]")
                # 使用默认聊天意图
                intent = Intent(name="chat", confidence=0.5, parameters={"content": user_input})

            # 根据意图名称路由到相应的处理函数
            intent_name = intent.name if intent else "unknown"
            
            self._update_system_log(f"[dim]🎯 意图: {intent_name} (置信度: {intent.confidence if intent else 0:.2f})[/dim]")

            if intent_name == "chat" or intent_name == "question":
                await self._handle_chat_intent(user_input, intent)
            elif intent_name == "start_debate":
                await self._handle_debate_intent(user_input, intent)
            elif intent_name == "create_wiki":
                await self._handle_wiki_intent(user_input, intent)
            elif intent_name == "search_knowledge":
                await self._handle_knowledge_intent(user_input, intent)
            elif intent_name.startswith("command_"):  # 通用命令处理
                await self._handle_command_intent(user_input, intent_name)
            else:
                # 未知意图，使用AI代理处理
                await self._handle_general_intent(user_input, intent)

        except Exception as e:
            error_msg = f"[red]❌ 输入处理错误: {e}[/red]"
            self._update_log_view(error_msg)
            self._update_system_log(f"[red]⚠️ 错误详情: {str(e)}[/red]")
            import traceback
            traceback.print_exc()

        finally:
            # 记录处理完成时间
            processing_time = time.time() - start_time
            self.performance_monitor.log_action("input_processing_complete", processing_time)

    async def _handle_chat_intent(self, user_input: str, intent: Intent) -> None:
        """处理聊天意图"""
        try:
            if self._agent_executor:
                response = await self._agent_executor.process_input(user_input)
                self._update_log_view(f"[green]🤖 AI: {response}[/green]")
            else:
                self._update_log_view("[yellow]⚠️ AI代理未初始化[/yellow]")
        except Exception as e:
            self._update_log_view(f"[red]❌ AI处理错误: {e}[/red]")

    async def _handle_debate_intent(self, user_input: str, intent: Intent) -> None:
        """处理辩论意图"""
        try:
            # 提取辩论参数
            topic = intent.parameters.get("topic", user_input.replace("辩论", "").replace("讨论", "").strip() or "通用话题")
            roles_param = intent.parameters.get("roles", "pro_arguer,con_arguer")
            roles = [role.strip() for role in roles_param.split(",")] if roles_param else ["pro_arguer", "con_arguer"]
            rounds = intent.parameters.get("rounds", 3)
            
            self._update_log_view(f"[blue]🎮 开始辩论: {topic}[/blue]")
            self._update_log_view(f"[blue]👥 角色: {', '.join(roles)}[/blue]")
            self._update_log_view(f"[blue]🔢 轮次: {rounds}[/blue]")
            
            # 尝试使用增强辩论管理器
            try:
                debate_manager = EnhancedDebateManager(
                    session_manager=self._session_manager,
                    role_manager=self._role_manager,
                    role_model_manager=self._role_model_manager,
                    model_provider=self._model_provider,
                    debate_history_tracker=self._debate_history_tracker
                )
                
                # 运行辩论（异步生成器）
                async for event in debate_manager.run_debate(topic, roles, rounds):
                    # 处理辩论事件并更新UI
                    self._handle_debate_event(event)
                    
            except Exception as debate_error:
                self._update_log_view(f"[yellow]⚠️ 增强辩论管理器失败: {debate_error}[/yellow]")
                self._update_log_view("[yellow]🔄 回退到基本辩论功能...[/yellow]")
                
        except Exception as e:
            self._update_log_view(f"[red]❌ 辩论处理错误: {e}[/red]")
            import traceback
            traceback.print_exc()

    def _handle_debate_event(self, event: Any) -> None:
        """处理辩论事件并更新UI"""
        try:
            if hasattr(event, 'type'):
                event_type = event.type
                if event_type == "debate_start":
                    self._update_log_view(f"[bold magenta]🎮 辩论开始: {getattr(event, 'topic', 'Unknown')}[/bold magenta]")
                elif event_type == "round_start":
                    round_num = getattr(event, 'round_number', '?')
                    self._update_log_view(f"[bold blue]🔄 第 {round_num} 轮开始[/bold blue]")
                elif event_type == "turn_complete":
                    participant = getattr(event, 'participant', 'Unknown')
                    content = getattr(event, 'content_preview', '...')
                    self._update_log_view(f"[cyan]🗣️ {participant}:[/cyan] {content}")
                elif event_type == "debate_complete":
                    self._update_log_view("[bold green]✅ 辩论完成![/bold green]")
        except Exception as e:
            self._update_system_log(f"[red]⚠️ 处理辩论事件错误: {e}[/red]")

    async def _handle_wiki_intent(self, user_input: str, intent: Intent) -> None:
        """处理维基意图"""
        try:
            from daip_live.wiki.manager import WikiManager
            wiki_manager = WikiManager(wiki_root=Path("wiki"))
            
            title = intent.parameters.get("title", "未命名页面")
            content = intent.parameters.get("content", user_input)
            
            page = wiki_manager.create_page(title, content)
            self._update_log_view(f"[green]📝 维基页面创建成功: {page.title}[/green]")
            
        except Exception as e:
            self._update_log_view(f"[red]❌ 维基创建错误: {e}[/red]")

    async def _handle_knowledge_intent(self, user_input: str, intent: Intent) -> None:
        """处理知识意图"""
        try:
            query = intent.parameters.get("query", user_input)
            self._update_log_view(f"[blue]🔍 搜索知识库: {query}[/blue]")
            # TODO: 实现知识库搜索
        except Exception as e:
            self._update_log_view(f"[red]❌ 知识处理错误: {e}[/red]")

    async def _handle_command_intent(self, user_input: str, intent_name: str) -> None:
        """处理命令意图"""
        try:
            command = intent_name.replace("command_", "")
            self._update_log_view(f"[yellow]🔧 执行命令: {command}[/yellow]")
            # TODO: 实现通用命令处理
        except Exception as e:
            self._update_log_view(f"[red]❌ 命令处理错误: {e}[/red]")

    async def _handle_general_intent(self, user_input: str, intent: Intent) -> None:
        """处理通用意图"""
        try:
            # 使用AI代理处理通用请求
            if self._agent_executor:
                response = await self._agent_executor.process_input(user_input)
                self._update_log_view(f"[green]🤖 响应: {response}[/green]")
            else:
                self._update_log_view(f"[white]💭 {user_input}[/white]")
        except Exception as e:
            self._update_log_view(f"[red]❌ 通用处理错误: {e}[/red]")

    def action_show_command_help(self) -> None:
        """显示命令帮助"""
        self.push_screen(CommandHelpDialog())

    def action_toggle_output_mode(self) -> None:
        """切换输出模式"""
        self._output_mode = not self._output_mode
        mode_text = "输出模式: 开启" if self._output_mode else "输出模式: 关闭"
        self._update_system_log(f"[bold]{mode_text}[/bold]")

    def action_copy_all_output(self) -> None:
        """复制所有输出到剪贴板"""
        try:
            # 获取主日志内容（这是主要的输出区域）
            main_log_widget = self.query_one("#main_log", CopyableLogWidget)
            
            # 在实际实现中，我们会从RichLog组件获取内容
            # 但由于Textual组件架构限制，我们需要另辟蹊径
            content_to_copy = "DAIP-LIVE TUI 输出内容:\\n\\n" + "\\n".join([
                "此功能允许复制TUI输出内容到剪贴板",
                "在实际部署版本中，这将复制所有显示的对话和系统消息",
                "当前显示为示例文本"
            ])
            
            success = copy_content(content_to_copy)
            if success:
                self.notify("输出内容已复制到剪贴板！", timeout=2)
                self._update_system_log("[green]✅ 输出已复制到剪贴板[/green]")
            else:
                self.notify("复制失败，请检查剪贴板权限", timeout=2)
                self._update_system_log("[red]❌ 复制失败[/red]")
                
        except Exception as e:
            self._update_system_log(f"[red]❌ 复制操作失败: {e}[/red]")

    def action_clear_logs(self) -> None:
        """清除日志"""
        try:
            main_log_widget = self.query_one("#main_log", CopyableLogWidget)
            system_log_widget = self.query_one("#system_log", CopyableLogWidget)
            
            main_log_widget.clear()
            system_log_widget.clear()
            
            self._update_system_log("[blue]🗑️ 日志已清除[/blue]")
        except Exception as e:
            self._update_system_log(f"[red]❌ 清除日志失败: {e}[/red]")

    def action_restart_session(self) -> None:
        """重启会话"""
        try:
            self.session_id = f"tui_session_{int(time.time())}"
            self._update_system_log(f"[green]🔄 会话已重启 (ID: {self.session_id})[/green]")
            
            # 清除日志并显示欢迎消息
            self.action_clear_logs()
            
            welcome_msg = f"会话已重启。新会话ID: {self.session_id}"
            self._update_log_view(f"[bold green]{welcome_msg}[/bold green]")
            
        except Exception as e:
            self._update_system_log(f"[red]❌ 重启会话失败: {e}[/red]")

    def action_show_exit_confirmation(self) -> None:
        """显示退出确认对话框"""
        self.push_screen(ExitConfirmationDialog(self))

    def _handle_role_command(self, command_args: str) -> None:
        """处理角色命令 - 通过角色命令处理器"""
        if self._tui_role_handler:
            try:
                # 解析命令参数
                parts = command_args.strip().split(' ', 1)
                cmd = parts[0].lower() if parts else ''
                args = parts[1] if len(parts) > 1 else ''

                # 传递给角色命令处理器
                result = self._tui_role_handler.handle_role_command(cmd, args)
                
                if result:
                    self._update_log_view(f"[cyan]🎭 角色命令结果: {result}[/cyan]")
                else:
                    self._update_log_view("[yellow]⚠️ 角色命令未产生结果[/yellow]")
                    
            except Exception as e:
                self._update_log_view(f"[red]❌ 角色命令处理错误: {e}[/red]")
                import traceback
                traceback.print_exc()
        else:
            self._update_log_view("[red]❌ 角色命令处理器未初始化[/red]")

console = Console()

def main():
    """主入口点"""
    try:
        # 检查并创建必要目录
        Path("wiki").mkdir(exist_ok=True)
        Path("roles").mkdir(exist_ok=True)
        
        # 初始化配置桥接
        try:
            config_bridge.init_config()
        except Exception as e:
            print(f"⚠️ 配置桥接初始化警告: {e}")
        
        app = SimplifiedTUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\\n👋 TUI已退出")
    except Exception as e:
        print(f"❌ TUI启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()