#!/usr/bin/env python3
"""
简化辩论引擎
避免复杂的依赖和初始化问题
"""

import asyncio
import time
import sys
sys.path.insert(0, 'src')

from debate_module.events import DebateEvents


class SimpleDebateEngine:
    """简化辩论引擎"""

    def __init__(self):
        pass

    async def run_debate(self, topic: str, roles: list[str], rounds: int = 1):
        """运行简化辩论"""
        session_id = f"simple_debate_{int(time.time())}"
        start_time = time.time()

        print(f"🎮 开始辩论: {topic}")
        print(f"👥 角色: {', '.join(roles)}")
        print(f"🔢 辩论轮次: {rounds}")

        # 产生开始事件
        yield DebateStartEvent(
            type="debate_start",
            session_id=session_id,
            topic=topic,
            roles=roles,
            rounds=rounds
        )

        # 模拟一轮辩论
        for i, role in enumerate(roles, 1):
            print(f"💬 {role} 第{i+1}轮发言:")

            yield DebateTurnStartEvent(
                type="turn_start",
                round=i+1,
                role=role
            )

            # 模拟发言
            content = f"这是 {role} 关于'{topic}'的第{i+1}轮观点"
            yield DebateTurnCompleteEvent(
                type="turn_complete",
                round=i+1,
                role=role,
                content=content
            )

        # 完成事件
        end_time = time.time()
        yield DebateCompleteEvent(
            type="debate_complete",
            session_id=session_id,
            topic=topic,
            turns=[],
            conclusion="简化辩论完成！",
            role_performances={},
            execution_time=end_time - start_time
        )

    def create_debate_config(self, topic: str, roles: list[str], **kwargs) -> 'DebateConfig':
        """创建辩论配置"""
        rounds = kwargs.get('rounds', 1)
        return DebateConfig(topic=topic, roles=roles, rounds=rounds)

    async def get_debate_summary(self, session_id: str) -> dict:
        """获取辩论摘要"""
        return {
            "session_id": session_id,
            "status": "completed",
            "message": "辩论已完成"
        }