"""TUI屏幕和对话框组件模块"""

from typing import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, ListItem, ListView, Static


class CommandHelpDialog(Screen):
    """命令帮助对话框"""

    BINDINGS = [Binding("escape", "dismiss", "关闭")]

    def __init__(self, help_text: str):
        super().__init__()
        self.help_text = help_text

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📚 命令帮助", id="title")
            yield Static(self.help_text, id="help_content")
            yield Button("关闭", id="close_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_button":
            self.dismiss()


class SessionSelectionDialog(Screen):
    """会话选择对话框"""

    BINDINGS = [Binding("escape", "dismiss", "关闭")]

    def __init__(self, sessions, on_select):
        super().__init__()
        self.sessions = sessions
        self.on_select = on_select

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("选择会话", id="title")
            yield ListView(id="session_list")
            yield Button("取消", id="cancel_button")

        # 填充会话列表
        list_view = self.query_one("#session_list", ListView)
        for session in self.sessions:
            item = ListItem(Label(f"{session.session_id} - {session.goal[:50]}"))
            list_view.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item_index < len(self.sessions):
            session = self.sessions[event.item_index]
            self.on_select(session)
            self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_button":
            self.dismiss()


class RoleSelectionDialog(Screen):
    """角色选择对话框"""

    BINDINGS = [Binding("escape", "dismiss", "关闭")]

    def __init__(self, roles, on_select):
        super().__init__()
        self.roles = roles
        self.on_select = on_select

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("选择AI角色", id="title")
            yield ListView(id="role_list")
            yield Button("取消", id="cancel_button")

        # 填充角色列表
        list_view = self.query_one("#role_list", ListView)
        for role in self.roles:
            item = ListItem(Label(f"{role.name} - {role.description[:50]}"))
            list_view.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item_index < len(self.roles):
            role = self.roles[event.item_index]
            self.on_select(role)
            self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_button":
            self.dismiss()


class ConfirmationDialog(Screen):
    """确认对话框"""

    BINDINGS = [Binding("escape", "dismiss", "取消")]

    def __init__(self, title: str, message: str, on_confirm=None, on_cancel=None):
        super().__init__()
        self.title = title
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.title, id="title")
            yield Static(self.message, id="message")
            with Horizontal(id="button_container"):
                yield Button("确认", id="confirm_button", variant="primary")
                yield Button("取消", id="cancel_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_button":
            if self.on_confirm:
                self.on_confirm()
            self.dismiss(True)
        elif event.button.id == "cancel_button":
            if self.on_cancel:
                self.on_cancel()
            self.dismiss(False)

    def on_key(self, event) -> None:
        if event.key == "escape":
            if self.on_cancel:
                self.on_cancel()
            self.dismiss(False)


class LoadingDialog(Screen):
    """加载对话框"""

    BINDINGS = [Binding("escape", "dismiss", "取消")]

    def __init__(self, title: str, message: str = ""):
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.title, id="title")
            if self.message:
                yield Static(self.message, id="message")
            yield Static("思考中...", id="loading_text")


class ErrorDialog(Screen):
    """错误对话框"""

    BINDINGS = [Binding("escape", "dismiss", "关闭")]

    def __init__(self, title: str, error_message: str):
        super().__init__()
        self.title = title
        self.error_message = error_message

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(f"❌ {self.title}", id="title")
            yield Static(self.error_message, id="error_message")
            yield Button("关闭", id="close_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_button":
            self.dismiss()


class SuccessDialog(Screen):
    """成功对话框"""

    BINDINGS = [Binding("escape", "dismiss", "关闭")]

    def __init__(self, title: str, success_message: str):
        super().__init__()
        self.title = title
        self.success_message = success_message

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(f"✅ {self.title}", id="title")
            yield Static(self.success_message, id="success_message")
            yield Button("确定", id="ok_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok_button":
            self.dismiss()


class InputDialog(Screen):
    """输入对话框"""

    BINDINGS = [Binding("escape", "dismiss", "取消")]

    def __init__(self, title: str, prompt: str, default_text: str = "", on_submit=None):
        super().__init__()
        self.title = title
        self.prompt = prompt
        self.default_text = default_text
        self.on_submit = on_submit
        self.input_text = default_text

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.title, id="title")
            yield Static(self.prompt, id="prompt")
            # Note: 这里需要添加输入框，但为了简化暂时用静态文本代替
            yield Static(
                f"默认值: {self.default_text}" if self.default_text else "请输入值",
                id="input_display",
            )
            with Horizontal(id="button_container"):
                yield Button("确定", id="ok_button", variant="primary")
                yield Button("取消", id="cancel_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok_button":
            if self.on_submit:
                self.on_submit(self.input_text)
            self.dismiss(self.input_text)
        elif event.button.id == "cancel_button":
            self.dismiss(None)


class ProgressDialog(Screen):
    """进度对话框"""

    BINDINGS = [Binding("escape", "dismiss", "取消")]

    def __init__(self, title: str, steps: list[str]):
        super().__init__()
        self.title = title
        self.steps = steps
        self.current_step = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.title, id="title")
            yield Static("步骤 0/0", id="progress_text")
            for i, step in enumerate(self.steps):
                yield Static(
                    f"{'✓' if i < self.current_step else '○'} {step}", id=f"step_{i}"
                )

    def update_progress(self, current_step: int):
        """更新进度"""
        self.current_step = current_step
        progress_text = self.query_one("#progress_text", Static)
        progress_text.update(f"步骤 {current_step}/{len(self.steps)}")

        for i, step in enumerate(self.steps):
            step_widget = self.query_one(f"#step_{i}", Static)
            if i < current_step:
                step_widget.update(f"✓ {step}")
            elif i == current_step:
                step_widget.update(f"⟳ {step}")
            else:
                step_widget.update(f"○ {step}")


class MultiSelectDialog(Screen):
    """多选对话框"""

    BINDINGS = [Binding("escape", "dismiss", "取消")]

    def __init__(self, title: str, items: list[str], on_select=None):
        super().__init__()
        self.title = title
        self.items = items
        self.on_select = on_select
        self.selected_items = []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.title, id="title")
            yield ListView(id="items_list")
            with Horizontal(id="button_container"):
                yield Button("全选", id="select_all_button")
                yield Button("取消全选", id="deselect_all_button")
                yield Button("确定", id="ok_button", variant="primary")
                yield Button("取消", id="cancel_button")

        # 填充项目列表
        list_view = self.query_one("#items_list", ListView)
        for item in self.items:
            list_view.append(ListItem(Label(f"○ {item}")))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select_all_button":
            self._select_all()
        elif event.button.id == "deselect_all_button":
            self._deselect_all()
        elif event.button.id == "ok_button":
            if self.on_select:
                self.on_select(self.selected_items)
            self.dismiss(self.selected_items)
        elif event.button.id == "cancel_button":
            self.dismiss(None)

    def _select_all(self):
        """全选"""
        self.selected_items = self.items.copy()
        list_view = self.query_one("#items_list", ListView)
        for i, item in enumerate(self.items):
            if i < len(list_view.children):
                list_view.children[i].update(f"✓ {item}")

    def _deselect_all(self):
        """取消全选"""
        self.selected_items = []
        list_view = self.query_one("#items_list", ListView)
        for i, item in enumerate(self.items):
            if i < len(list_view.children):
                list_view.children[i].update(f"○ {item}")


class ExitConfirmationDialog(Screen):
    """退出确认对话框"""

    BINDINGS = [
        Binding("y", "confirm_exit", "确认退出", show=True),
        Binding("n", "cancel_exit", "取消退出", show=True),
        Binding("escape", "cancel_exit", "取消退出", show=False),
        Binding("enter", "confirm_exit", "确认退出", show=False),
    ]

    CSS = """
    #dialog_container {
        align: center middle;
        padding: 2;
        border: solid $primary;
        width: 60;
        background: $surface;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 1 0;
    }

    #message {
        text-align: center;
        margin: 1 0;
        color: $text;
    }

    #warning {
        text-align: center;
        margin: 1 0;
        color: $warning;
    }

    #button_container {
        align: center middle;
        height: auto;
        margin-top: 2;
    }

    #button_container Button {
        margin: 0 1;
    }
    """

    def __init__(self, on_confirm: Callable[[], None] = None):
        super().__init__()
        self.on_confirm = on_confirm

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog_container"):
            yield Label("👋 确认退出 DAIP-LIVE", id="title")
            yield Static("您确定要退出 DAIP-LIVE 吗？", id="message")
            yield Static("⚠️ 所有未保存的工作将会丢失", id="warning")

            with Horizontal(id="button_container"):
                yield Button("确认退出 (Y)", id="confirm_button", variant="error")
                yield Button("取消 (N)", id="cancel_button", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_button":
            self.action_confirm_exit()
        elif event.button.id == "cancel_button":
            self.action_cancel_exit()

    def action_confirm_exit(self) -> None:
        """确认退出"""
        if self.on_confirm:
            self.on_confirm()
        self.dismiss()

    def action_cancel_exit(self) -> None:
        """取消退出"""
        self.dismiss()
