"""
辩论事件类型定义
"""

from typing import Any


class DebateEvents:
    """辩论事件工具类"""

    @staticmethod
    def create_start_event(
        session_id: str, topic: str, roles: list[str], rounds: int
    ) -> dict[str, Any]:
        """创建辩论开始事件"""
        return {
            "type": "debate_start",
            "session_id": session_id,
            "topic": topic,
            "roles": roles,
            "rounds": rounds,
            "timestamp": 0,  # 简化时间戳
        }

    @staticmethod
    def create_turn_event(round: int, role: str, content: str) -> dict[str, Any]:
        """创建回合发言事件"""
        return {
            "type": "turn_complete",
            "round": round,
            "role": role,
            "content": content,
            "timestamp": 0,
        }

    @staticmethod
    def create_complete_event(
        session_id: str, conclusion: str, execution_time: float
    ) -> dict[str, Any]:
        """创建辩论完成事件"""
        return {
            "type": "debate_complete",
            "session_id": session_id,
            "conclusion": conclusion,
            "execution_time": execution_time,
            "timestamp": 0,
        }

    @staticmethod
    def create_error_event(session_id: str, error_message: str) -> dict[str, Any]:
        """创建错误事件"""
        return {
            "type": "error",
            "session_id": session_id,
            "error": error_message,
            "timestamp": 0,
        }
