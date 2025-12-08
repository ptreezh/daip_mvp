"""Enhanced TUI implementation with optimized layout and focus management."""

import os
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Footer,
    Header,
    Input,
    RichLog,
    Static,
)
from textual.css.query import NoMatches


from daip_live.agent_engine.executor import AgentExecutor
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.persistence.database import DatabaseManager


class FocusMode(Enum):
    """焦点模式枚举"""
    INPUT = "input"      # 输入区焦点
    OUTPUT = "output"    # 输出区焦点


class EnhancedDAIP_TUI(App):
    """增强版TUI实现，优化了界面布局和焦点管理"""

    BINDINGS = [
        Binding("ctrl+tab", "toggle_focus", "切换焦点"),
        Binding("ctrl+a", "select_all", "全选", show=False),
        Binding("ctrl+c", "copy_text", "复制", show=False),
        Binding("ctrl+e", "_handle_ctrl_e_exit", "退出应用", show=False),
        Binding("escape", "exit_output_mode", "退出输出模式", show=False),
    ]

    def __init__(
        self,
        executor: AgentExecutor = None,
        session_manager: SessionManager = None,
        role_manager: RoleManager = None,
        knowledge_manager: KnowledgeManager = None,
        debate_manager: DebateManager = None,
        model_provider: LiteLLMProvider = None,
        db_manager: DatabaseManager = None,
        config_manager: Any = None,
        role_model_manager: RoleModelManager = None,
        enhanced_debate_manager: EnhancedDebateManager = None,
        goal: Optional[str] = None,
    ):
        super().__init__()
        
        # 初始化依赖项
        self._executor = executor
        self._session_manager = session_manager
        self._role_manager = role_manager
        self._knowledge_manager = knowledge_manager
        self._debate_manager = debate_manager
        self._model_provider = model_provider
        self._role_model_manager = role_model_manager or RoleModelManager()
        self._enhanced_debate_manager = enhanced_debate_manager or EnhancedDebateManager(
            self._session_manager, self._role_manager, self._role_model_manager, self._model_provider
        ) if self._session_manager and self._role_manager and self._model_provider else None
        self._db_manager = db_manager
        self._config_manager = config_manager
        
        # 初始化属性
        self._goal = goal
        self._log_text_buffer: List[str] = []
        self._current_session_id: Optional[str] = None
        self._session_stack: List[str] = []
        self._model_name = "llama3:8b"
        self._token_usage = (0, 8192)
        
        # 状态跟踪变量
        self._real_token_usage = (0, 8192)
        
        self._current_debate = {
            'session_id': None,
            'topic': None,
            'current_round': 0,
            'total_rounds': 0,
            'current_participant': None,
            'is_active': False,
            'role_models': {}
        }

        self._current_model = "default"
        
        self._system_activity = {
            'events_processed': 0,
            'tools_executed': 0,
            'errors_encountered': 0,
            'session_start_time': None,
            'last_activity_time': None
        }
        
        # 焦点管理
        self.focus_mode = FocusMode.INPUT

    def compose(self) -> ComposeResult:
        """优化的界面布局"""
        # 头部
        yield Header()
        
        # 主内容区域 - 使用垂直布局
        with Vertical(id="main_content"):
            # 输出区域 - 使用RichLog支持语法高亮
            yield RichLog(
                id="main_log", 
                classes="output-mode", 
                highlight=True, 
                markup=True, 
                wrap=True,
                auto_scroll=True
            )
            
            # 状态信息区域
            with Horizontal(id="status_container"):
                yield Static(
                    "Model: llama3:8b | Tokens: 0/8192 (0%) | Status: Idle | Focus: Input", 
                    id="status_bar"
                )
        
        # 输入区域
        yield Input(placeholder="Enter command or message...", id="user_input")
        
        # 底部
        yield Footer()

    def action_toggle_focus(self) -> None:
        """切换输入/输出焦点"""
        if self.focus_mode == FocusMode.INPUT:
            self.focus_mode = FocusMode.OUTPUT
            self.query_one("#main_log").focus()
        else:
            self.focus_mode = FocusMode.INPUT
            self.query_one("#user_input").focus()

    def action_exit_output_mode(self) -> None:
        """退出输出模式"""
        if self.focus_mode == FocusMode.OUTPUT:
            self.focus_mode = FocusMode.INPUT
            self.query_one("#user_input").focus()

    def action_select_all(self) -> None:
        """全选输出区域文本"""
        if self.focus_mode == FocusMode.OUTPUT:
            # RichLog不支持程序化选择，这里作为占位符
            pass

    def action_copy_text(self) -> None:
        """复制输出区域所有文本到剪贴板"""
        if self.focus_mode == FocusMode.OUTPUT:
            all_text = "\n".join(self._log_text_buffer)
            try:
                import pyperclip
                pyperclip.copy(all_text)
            except:
                pass

    def on_ready(self) -> None:
        """应用就绪时的回调"""
        # 设置初始焦点到输入框
        self.query_one("#user_input").focus()


# 为了向后兼容，保留原有的DAIP_TUI类名
DAIP_TUI = EnhancedDAIP_TUI