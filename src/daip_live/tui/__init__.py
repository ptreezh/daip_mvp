"""TUI模块包 - 提供模块化的TUI组件"""

# 导入模块化TUI实现 - 避免循环导入
try:
    from .simplified_main import SimplifiedTUI as DAIP_TUI
except ImportError:
    # 如果无法导入simplified_main，尝试从tui_modular导入
    try:
        from ..tui_modular import DAIP_TUI
    except ImportError:
        # 如果都失败了，设为None
        DAIP_TUI = None

from .autocomplete import TUIAutocomplete
from .enhanced_commands import DebateCommands, SearchCommands
from .screens import (
    CommandHelpDialog,
    ConfirmationDialog,
    ErrorDialog,
    InputDialog,
    LoadingDialog,
    MultiSelectDialog,
    ProgressDialog,
    RoleSelectionDialog,
    SessionSelectionDialog,
    SuccessDialog,
)

# 移除了虚假的文本选择功能
# from .text_selection import TextSelectionManager, CopyPasteEnhancer
from .utils import (
    ConfigManager,
    FocusMode,
    HistoryManager,
    Logger,
    PerformanceMonitor,
    ThemeManager,
    TUIUtils,
)

# Container 延迟导出（真实定义在 daip_live.container）
# 恢复导出以兼容测试 mock 目标 `src.daip_live.tui.Container` 及外部引用
try:
    from ..container import Container
except ImportError:
    Container = None

__all__ = [
    # 主要TUI类（来自上级目录）
    "DAIP_TUI",
    # 依赖注入容器（真实定义在 daip_live.container）
    "Container",
    # 自动补全
    "TUIAutocomplete",
    # 命令处理
    "TUICommandHandler",
    "SearchCommands",
    "DebateCommands",
    # 屏幕和对话框
    "CommandHelpDialog",
    "SessionSelectionDialog",
    "RoleSelectionDialog",
    "ConfirmationDialog",
    "LoadingDialog",
    "ErrorDialog",
    "SuccessDialog",
    "InputDialog",
    "ProgressDialog",
    "MultiSelectDialog",
    # 移除了虚假的文本选择和复制粘贴增强功能
    # 'TextSelectionManager',
    # 'CopyPasteEnhancer',
    # 工具函数
    "FocusMode",
    "TUIUtils",
    "HistoryManager",
    "PerformanceMonitor",
    "ConfigManager",
    "ThemeManager",
    "Logger",
]
