"""
自动进度显示组件
在TUI和非TUI环境下自动提供进度显示
"""

import sys
import time
from typing import Callable, Optional

from .simple_collaboration_engine import CollaborationProgress


class AutoProgressDisplay:
    """自动进度显示器，支持TUI和命令行环境"""

    def __init__(self):
        self.is_tui_environment = self._detect_tui_environment()
        self.display_callback = None
        self.progress_history = []
        self.start_time = None

    def _detect_tui_environment(self) -> bool:
        """检测是否在TUI环境中运行"""
        # 检查是否在支持ANSI转义序列的终端中
        try:
            # 如果有stderr且是TTY，可能是TUI环境
            if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
                # 进一步检查是否有环境变量表明在TUI中
                import os

                if os.getenv("TERM") and os.getenv("TERM") != "dumb":
                    return True
        except Exception:
            pass
        return False

    def setup_callback(self, callback: Optional[Callable] = None):
        """设置进度回调函数"""
        if callback:
            self.display_callback = callback
        elif self.is_tui_environment:
            self.display_callback = self._tui_display_callback
        else:
            self.display_callback = self._cli_display_callback

    def _tui_display_callback(self, progress: CollaborationProgress):
        """TUI环境下的显示回调"""
        # 在TUI环境中，通常会通过事件系统更新UI
        # 这里只是记录进度，实际UI更新由TUI框架处理
        self.progress_history.append(progress.to_dict())

    def _cli_display_callback(self, progress: CollaborationProgress):
        """命令行环境下的显示回调"""
        if not self.start_time:
            self.start_time = time.time()

        # 创建进度条
        percentage = progress.get_progress_percentage()
        bar_width = 40
        filled = int(bar_width * percentage / 100)
        "█" * filled + "░" * (bar_width - filled)

        # 计算耗时
        time.time() - self.start_time

        # 构建显示行 - 移除百分比显示
        if progress.current_role:
            pass
        else:
            pass

        # 输出到stderr，避免干扰正常输出

        # 如果完成，添加换行
        if progress.is_complete:
            pass

    def show_completion_summary(self, progress: CollaborationProgress):
        """显示完成摘要"""
        if progress.is_complete:
            progress.to_dict()["elapsed_seconds"] if hasattr(progress, "to_dict") else 0

            if progress.generated_content:
                list({item["role"] for item in progress.generated_content})

    def show_error_summary(self, progress: CollaborationProgress):
        """显示错误摘要"""
        if progress.errors:
            for i, error in enumerate(progress.errors[-3:], 1):  # 只显示最后3个错误
                pass


class EnhancedCollaborationEngine:
    """增强的协作引擎，自动包含进度显示"""

    def __init__(self, base_engine):
        self.base_engine = base_engine
        self.auto_display = AutoProgressDisplay()

    async def create_collaborative_wiki_with_auto_display(
        self,
        title: str,
        topic: str,
        roles: Optional[list] = None,
        rounds: int = 1,
        custom_display: Optional[Callable] = None,
    ):
        """创建协作维基页面，自动显示进度"""

        # 设置自动显示
        self.auto_display.setup_callback(custom_display)

        # 包装原有的进度回调
        original_callback = self.base_engine.progress_callback

        def wrapped_callback(progress: CollaborationProgress):
            # 调用原有回调
            if original_callback:
                original_callback(progress)

            # 调用自动显示
            if self.auto_display.display_callback:
                self.auto_display.display_callback(progress)

        # 临时设置新的回调
        self.base_engine.progress_callback = wrapped_callback

        try:
            # 执行协作创建
            page, content = await self.base_engine.create_collaborative_wiki(
                title, topic, roles, rounds
            )

            # 显示完成摘要
            if (
                hasattr(self.base_engine, "current_progress")
                and self.base_engine.current_progress
            ):
                self.auto_display.show_completion_summary(
                    self.base_engine.current_progress
                )
                self.auto_display.show_error_summary(self.base_engine.current_progress)

            return page, content

        finally:
            # 恢复原有回调
            self.base_engine.progress_callback = original_callback


def create_enhanced_engine_with_auto_display(simple_engine):
    """创建带有自动显示功能的增强协作引擎"""
    return EnhancedCollaborationEngine(simple_engine)
