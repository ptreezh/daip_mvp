#!/usr/bin/env python3
"""
测试键绑定功能
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Label
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class KeyTestApp(App):
    """测试键绑定的简单应用"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1;
    }

    #main {
        column-span: 2;
        height: 100%;
        content-align: center middle;
    }

    #main Label {
        text-align: center;
    }

    #status {
        row-span: 1;
        height: 3;
        text-style: bold;
        background: $primary;
        content-align: center middle;
    }
    """

    BINDINGS = [
        Binding("ctrl+e", "quit", "退出应用", show=True, priority=True),
        Binding("ctrl+q", "quit", "退出应用", show=True, priority=True),
        Binding("escape", "quit", "退出应用", show=True, priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield Label("按键测试应用", id="main")
        yield Label("状态: 就绪", id="status")

    def action_quit(self) -> None:
        """退出应用"""
        self.bell()
        self.exit("用户请求退出")

if __name__ == "__main__":
    app = KeyTestApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n用户中断了应用")