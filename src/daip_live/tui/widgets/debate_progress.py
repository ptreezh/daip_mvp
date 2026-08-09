"""辩论进度小部件 - 显示实时辩论进度"""

import time
from typing import Any

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, ProgressBar, Static


class DebateProgressWidget(Widget):
    """辩论进度显示小部件"""

    DEFAULT_CSS = """
    DebateProgressWidget {
        height: auto;
    }

    .progress-container {
        width: 100%;
        height: 3;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }

    .progress-header {
        text-align: center;
        color: $text;
        padding: 0 1;
    }

    .progress-bar {
        width: 100%;
        height: 1;
    }

    .participant-status {
        height: 1;
        padding: 0 1;
    }

    .thinking-indicator {
        color: $accent;
    }
    """

    def __init__(self):
        super().__init__()
        self.debate_state = {
            "current_round": 0,
            "total_rounds": 0,
            "participants": [],
            "participant_status": {},
            "debate_running": False,
            "current_participant": None,
            "start_time": None,
        }

    def compose(self):
        """构建小部件布局"""
        # 创建UI组件
        yield Static("🎯 辩论进度", classes="progress-header", id="header")

        progress_container = Vertical(classes="progress-container")
        progress_container.mount(
            Label("准备中...", classes="progress-header", id="progress-label")
        )
        progress_container.mount(
            ProgressBar(show_eta=False, show_percentage=True, id="progress-bar")
        )
        yield progress_container

        status_container = Vertical(classes="participant-status")
        status_container.mount(Static("", id="participants-status"))
        yield status_container

    def update_debate_state(self, state: dict[str, Any]) -> None:
        """更新辩论状态"""
        self.debate_state.update(state)
        self._refresh_display()

    def update_round(self, round_number: int, total_rounds: int) -> None:
        """更新轮次进度"""
        self.debate_state["current_round"] = round_number
        self.debate_state["total_rounds"] = total_rounds
        self._refresh_display()

    def set_participants(self, participants: list) -> None:
        """设置参与者"""
        self.debate_state["participants"] = participants
        self._refresh_display()

    def update_participant_status(
        self, participant: str, status: str, color: str = "yellow"
    ) -> None:
        """更新参与者状态"""
        self.debate_state["participant_status"][participant] = {
            "status": status,
            "color": color,
        }
        self._refresh_display()

    def start_debate(self, total_rounds: int, participants: list) -> None:
        """开始辩论"""
        self.debate_state["debate_running"] = True
        self.debate_state["start_time"] = time.time()
        self.debate_state["total_rounds"] = total_rounds
        self.debate_state["participants"] = participants
        self.debate_state["current_round"] = 0

        # 初始化参与者状态
        for participant in participants:
            self.debate_state["participant_status"][participant] = {
                "status": "waiting",
                "color": "blue",
            }

        self._refresh_display()

    def update_thinking(self, participant: str, is_thinking: bool) -> None:
        """更新思考状态"""
        color = "green" if is_thinking else "blue"
        self.update_participant_status(participant, "思考中...", color)

    def complete_turn(self, participant: str) -> None:
        """完成回合"""
        self.update_participant_status(participant, "已完成", "green")

    def next_round(self, round_number: int) -> None:
        """进入下一轮"""
        self.debate_state["current_round"] = round_number

        # 重置所有参与者状态为等待
        for participant in self.debate_state["participants"]:
            self.update_participant_status(participant, "等待中...", "blue")

        self._refresh_display()

    def finish_debate(self) -> None:
        """完成辩论"""
        self.debate_state["debate_running"] = False

        # 更新所有参与者为完成状态
        for participant in self.debate_state["participants"]:
            self.update_participant_status(participant, "已完成", "green")

        self._refresh_display()

    def _refresh_display(self) -> None:
        """刷新显示"""
        # 获取子部件
        progress_label = self.query_one("#progress-label", Label)
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        participants_status = self.query_one("#participants-status", Static)

        if not self.debate_state["debate_running"]:
            # 清除内容
            progress_label.update("辩论未开始")
            progress_bar.progress(0)
            participants_status.update("")
            return

        # 更新进度条
        progress_percentage = 0
        if self.debate_state["total_rounds"] > 0:
            progress_percentage = (
                self.debate_state["current_round"] / self.debate_state["total_rounds"]
            ) * 100
        else:
            progress_percentage = 0

        progress_bar.progress(progress_percentage)

        # 更新进度标签
        current_round = self.debate_state["current_round"]
        total_rounds = self.debate_state["total_rounds"]

        if self.debate_state["debate_running"]:
            if current_round > 0:
                progress_label.update(f"第 {current_round} 轮 (共 {total_rounds} 轮)")
            else:
                progress_label.update("准备开始辩论...")

        # 更新参与者状态显示
        status_text = []
        for participant in self.debate_state["participants"]:
            status_info = self.debate_state["participant_status"].get(participant, {})
            if status_info:
                color_tag = f"[{status_info['color']}]{participant}[/]"
                status_text.append(f"{color_tag}: {status_info['status']}")

        participants_status.update(
            "\\n".join(status_text) if status_text else "等待参与者..."
        )

        # 更新思考指示器
        current_participant = self.debate_state.get("current_participant")
        if (
            current_participant
            and current_participant in self.debate_state["participant_status"]
        ):
            participant_status = self.debate_state["participant_status"][
                current_participant
            ]
            if participant_status.get("status") == "思考中...":
                # 显示思考动画
                thinking_chars = "⠋⠙⠹⠸⠼⠦⠧⠮⠥"
                thinking_text = ""
                for i, char in enumerate(thinking_chars):
                    if i % 4 == 0:
                        thinking_text += f"[green]{char}[/green]"
                    else:
                        thinking_text += f"[dim]{char}[/dim]"

                status_text.append(
                    f"[green]💭 {current_participant} 思考中...{thinking_text}[/green]"
                )

        if status_text:
            full_status = "\\n".join(status_text)
            participants_status.update(full_status)
