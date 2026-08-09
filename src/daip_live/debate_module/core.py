"""
辩论核心功能
"""

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class DebateConfig:
    """辩论配置"""

    topic: str
    roles: list[str]
    rounds: int = 1
    max_turns_per_role: int = 10


@dataclass
class DebateResult:
    """辩论结果"""

    session_id: str
    topic: str
    turns: list[dict[str, Any]]
    conclusion: str
    role_performances: dict[str, str]
    execution_time: float


class DebateCore:
    """辩论核心功能"""

    def __init__(self, config: DebateConfig):
        self.config = config
        self.start_time = time.time()

    async def run_debate(self) -> DebateResult:
        """执行辩论"""
        session_id = f"debate_{int(time.time())}"

        # 产生事件流（简化版）
        events = []
        events.append(
            {
                "type": "start",
                "session_id": session_id,
                "topic": self.config.topic,
                "roles": self.config.roles,
                "rounds": self.config.rounds,
            }
        )

        # 模拟辩论过程
        for round_num in range(1, self.config.rounds + 1):
            for role in self.config.roles:
                turn = {
                    "type": "turn_start",
                    "round": round_num,
                    "role": role,
                    "timestamp": time.time(),
                }
                events.append(turn)

                # 模拟发言
                content = f"这是 {role} 在第 {round_num} 轮的发言"
                speech = {
                    "type": "turn_complete",
                    "round": round_num,
                    "role": role,
                    "content": content,
                    "timestamp": time.time(),
                }
                events.append(speech)

        # 完成事件
        end_time = time.time()
        result = DebateResult(
            session_id=session_id,
            topic=self.config.topic,
            turns=events,
            conclusion=f"辩论 '{self.config.topic}' 已完成，共进行了 {self.config.rounds} 轮",  # noqa: E501
            role_performances=dict.fromkeys(self.config.roles, "表现良好"),
            execution_time=end_time - self.start_time,
        )

        events.append(
            {
                "type": "complete",
                "session_id": session_id,
                "conclusion": result.conclusion,
                "execution_time": result.execution_time,
            }
        )

        return result

    async def stream_events(self, result: DebateResult):
        """流式输出辩论事件"""
        for event in result.turns:
            yield event

        yield {
            "type": "complete",
            "session_id": result.session_id,
            "conclusion": result.conclusion,
            "role_performances": result.role_performances,
        }
