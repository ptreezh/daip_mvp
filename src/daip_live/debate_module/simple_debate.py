#!/usr/bin/env python3
"""
简化辩论引擎
避免复杂的依赖和初始化问题
"""

import sys
import time

sys.path.insert(0, "src")

from daip_live.core.models import (
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
    DebateTurnStartEvent,
)
from daip_live.debate_module.core import DebateConfig


class SimpleDebateEngine:
    """简化辩论引擎"""

    def __init__(self):
        pass

    async def run_debate(self, topic: str, roles: list[str], rounds: int = 1):
        """运行简化辩论"""
        session_id = f"simple_debate_{int(time.time())}"
        time.time()

        # 产生开始事件
        yield DebateStartEvent(
            session_id=session_id, topic=topic, roles=roles, rounds=rounds
        )

        # 模拟辩论过程
        for round_num in range(1, rounds + 1):
            # 每轮开始事件
            yield DebateRoundStartEvent(
                round_number=round_num, total_rounds=rounds, session_id=session_id
            )

            for role in roles:
                # 每个参与者开始发言
                yield DebateTurnStartEvent(
                    participant=role, round_number=round_num, session_id=session_id
                )

                # 模拟发言
                content = f"这是 {role} 关于'{topic}'的第{round_num}轮观点"
                yield DebateTurnCompleteEvent(
                    participant=role,
                    round_number=round_num,
                    content_preview=content[:100],  # 只取前100个字符作为预览
                    session_id=session_id,
                )

        # 完成事件
        time.time()
        yield DebateCompleteEvent(
            session_id=session_id,
            summary=f"辩论 '{topic}' 完成，共进行了 {rounds} 轮",
        )

    def create_debate_config(
        self, topic: str, roles: list[str], **kwargs
    ) -> "DebateConfig":
        """创建辩论配置"""
        rounds = kwargs.get("rounds", 1)
        return DebateConfig(topic=topic, roles=roles, rounds=rounds)

    async def get_debate_summary(self, session_id: str) -> dict:
        """获取辩论摘要"""
        return {
            "session_id": session_id,
            "status": "completed",
            "message": "辩论已完成",
        }
