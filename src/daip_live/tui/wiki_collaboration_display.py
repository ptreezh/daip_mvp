"""
TUI Wiki协作过程展示组件
在终端界面中实时展示协作创建的进度和结果
"""

from textual.containers import Vertical
from textual.progress import ProgressBar
from textual.reactive import reactive
from textual.widget import Widget

from daip_live.wiki.simple_collaboration_engine import CollaborationProgress


class WikiCollaborationDisplay(Widget):
    """Wiki协作过程展示组件"""

    current_progress: reactive[CollaborationProgress] = reactive(None)

    def __init__(self):
        super().__init__()
        self.current_progress = None

    def compose(self):
        """构建UI组件"""
        with Vertical():
            # 标题
            yield Static("🚀 Wiki协作创建", classes="collaboration-title")

            # 进度条
            self.progress_bar = ProgressBar(total=100, show_eta=True)
            yield self.progress_bar

            # 当前状态
            self.status_text = Static("准备中...", classes="status-text")
            yield self.status_text

            # 当前角色
            self.role_text = Static("", classes="role-text")
            yield self.role_text

            # 生成的内容展示
            with Vertical(id="content-display"):
                yield Static("📝 生成的内容:", classes="content-title")
                self.content_container = Vertical(id="generated-content")
                yield self.content_container

            # 错误信息（默认隐藏）
            self.error_container = Vertical(id="error-container", classes="hidden")
            yield self.error_container

    def update_progress(self, progress: CollaborationProgress):
        """更新进度显示"""
        self.current_progress = progress
        self.call_after_refresh(self._refresh_display)

    def _refresh_display(self):
        """刷新显示内容"""
        if not self.current_progress:
            return

        progress = self.current_progress

        # 更新进度条
        self.progress_bar.progress = progress.get_progress_percentage()

        # 更新状态文本
        self.status_text.update(f"🔄 {progress.current_action}")

        # 更新角色文本
        if progress.current_role:
            self.role_text.update(f"👤 当前角色: {progress.current_role}")
        else:
            self.role_text.update("")

        # 更新生成的内容
        self._update_content_display()

        # 更新错误信息
        self._update_error_display()

        # 如果完成，显示完成状态
        if progress.is_complete:
            self.status_text.update("✅ 协作完成！")
            self.progress_bar.progress = 100

    def _update_content_display(self):
        """更新生成的内容显示"""
        # 清空现有内容
        self.content_container.remove_children()

        if not self.current_progress or not self.current_progress.generated_content:
            return

        # 显示最新的内容
        for i, content_item in enumerate(
            self.current_progress.generated_content[-5:]
        ):  # 只显示最新5条
            role = content_item.get("role", "Unknown")
            content = content_item.get("content", "")
            content_item.get("timestamp", "")

            # 创建内容项
            content_widget = Static(
                f"📌 {role}:\n{content[:100]}...", classes="content-item"
            )
            self.content_container.mount(content_widget)

    def _update_error_display(self):
        """更新错误信息显示"""
        # 清空现有错误
        self.error_container.remove_children()

        if not self.current_progress or not self.current_progress.errors:
            self.error_container.add_class("hidden")
            return

        self.error_container.remove_class("hidden")

        # 添加错误标题
        error_title = Static("⚠️ 错误信息:", classes="error-title")
        self.error_container.mount(error_title)

        # 显示错误
        for error_item in self.current_progress.errors[-3:]:  # 只显示最新3个错误
            error_text = error_item.get("error", "")
            error_item.get("timestamp", "")

            error_widget = Static(f"❌ {error_text}", classes="error-item")
            self.error_container.mount(error_widget)

    def reset(self):
        """重置显示状态"""
        self.current_progress = None
        self.progress_bar.progress = 0
        self.status_text.update("准备中...")
        self.role_text.update("")
        self.content_container.remove_children()
        self.error_container.remove_children()
        self.error_container.add_class("hidden")


class CollaborationEventHandler:
    """协作事件处理器"""

    def __init__(self, display_widget: WikiCollaborationDisplay):
        self.display_widget = display_widget
        self.is_active = False

    def handle_progress_update(self, progress: CollaborationProgress):
        """处理进度更新"""
        if self.is_active:
            self.display_widget.update_progress(progress)

    def start_collaboration(self):
        """开始协作监听"""
        self.is_active = True
        self.display_widget.reset()

    def stop_collaboration(self):
        """停止协作监听"""
        self.is_active = False


# 为Textual添加必要的导入
try:
    from textual.widgets import Static
except ImportError:
    # 如果Textual不可用，创建一个简单的替代品
    class Static:
        def __init__(self, text="", classes=None):
            self.text = text
            self.classes = classes or []

        def update(self, text):
            self.text = text

        def mount(self, parent):
            pass

        def remove_children(self):
            pass

        def add_class(self, class_name):
            if class_name not in self.classes:
                self.classes.append(class_name)

        def remove_class(self, class_name):
            if class_name in self.classes:
                self.classes.remove(class_name)

    class Widget:
        def __init__(self):
            pass

        def compose(self):
            return []

        def call_after_refresh(self, func):
            func()

    class ProgressBar(Widget):
        def __init__(self, total=100, show_eta=False):
            super().__init__()
            self.total = total
            self.progress = 0

        def update_progress(self, value):
            self.progress = min(max(value, 0), self.total)

    class Vertical(list):
        def __init__(self, id=None, classes=None):
            super().__init__()
            self.id = id
            self.classes = classes or []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
