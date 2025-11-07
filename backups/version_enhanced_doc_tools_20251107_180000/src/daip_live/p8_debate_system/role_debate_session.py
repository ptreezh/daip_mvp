"""
角色独立辩论会话
实现每个角色的独立会话管理，包括个人历史、立场记忆和论点追踪
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig


@dataclass
class RoleDebateSession:
    """角色独立辩论会话"""

    role_name: str
    role_persona: str
    model_config: RoleModelConfig
    system_prompt: str = ""

    # 角色个人历史记录
    personal_history: List[Dict[str, Any]] = field(default_factory=list)

    # 立场记忆系统
    stance_memory: Dict[str, Any] = field(default_factory=dict)

    # 论点追踪系统
    argument_tracker: Dict[int, Dict[str, Dict[str, Any]]] = field(default_factory=dict)

    # 轮次记忆系统
    round_memories: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    def add_personal_history(self, round_num: int, content: str, opponent_summary: str):
        """添加个人历史记录"""
        self.personal_history.append({
            "round": round_num,
            "content": content,
            "opponent_summary": opponent_summary,
            "timestamp": self._get_timestamp()
        })

    def update_stance_memory(self, key: str, value: Any):
        """更新立场记忆"""
        self.stance_memory[key] = value

    def track_argument(self, round_num: int, argument_type: str, content: str, strength: float = 0.5):
        """追踪论点"""
        if round_num not in self.argument_tracker:
            self.argument_tracker[round_num] = {}

        self.argument_tracker[round_num][argument_type] = {
            "content": content,
            "strength": strength,
            "timestamp": self._get_timestamp()
        }

    def add_round_memory(self, round_num: int, summary: str, key_points: List[str], opponent_arguments: List[str]):
        """添加轮次记忆"""
        self.round_memories[round_num] = {
            "summary": summary,
            "key_points": key_points,
            "opponent_arguments": opponent_arguments,
            "timestamp": self._get_timestamp()
        }

    def get_context_summary(self, current_round: int) -> str:
        """获取角色上下文摘要"""
        if current_round < 1:
            raise ValueError("Current round must be at least 1")

        context_parts = []

        # 基本信息
        context_parts.append(f"Role: {self.role_persona}")
        context_parts.append(f"Assigned Model: {self.model_config.model_name}")

        # 核心立场
        core_stance = self.stance_memory.get("core_stance", "Developing...")
        context_parts.append(f"Core Stance: {core_stance}")

        # 历史论点
        if self.personal_history:
            context_parts.append("Previous Arguments:")
            for hist in self.personal_history:
                context_parts.append(f"  Round {hist['round']}: {hist['content']}")
        else:
            context_parts.append("No previous arguments")

        # 轮次摘要
        for round_num in range(1, current_round):
            if round_num in self.round_memories:
                memory = self.round_memories[round_num]
                context_parts.append(f"Round {round_num} Summary:")
                context_parts.append(f"  Summary: {memory['summary']}")
                context_parts.append(f"  Key Points: {', '.join(memory['key_points'])}")

        return "\n".join(context_parts)

    def build_context_aware_prompt(self, topic: str, current_round: int) -> str:
        """构建上下文感知的提示词"""
        prompt = f"""Debate Topic: {topic}
Current Round: {current_round}

Your Role: {self.role_persona}
Your Assigned Model: {self.model_config.model_name}"""

        if self.system_prompt:
            prompt += f"\nSystem Prompt: {self.system_prompt}"

        # 添加历史论点
        if self.personal_history:
            prompt += "\n\nYour Previous Arguments:"
            for hist in self.personal_history:
                prompt += f"\nRound {hist['round']}: {hist['content']}"

        # 添加核心立场
        core_stance = self.stance_memory.get("core_stance", "Developing...")
        prompt += f"\n\nYour Core Stance: {core_stance}"

        # 添加对手论点摘要
        if self.personal_history:
            opponent_summaries = []
            for hist in self.personal_history:
                if hist.get("opponent_summary"):
                    opponent_summaries.append(f"Round {hist['round']}: {hist['opponent_summary']}")

            if opponent_summaries:
                prompt += "\n\nOpponent Arguments Summary:\n" + "\n".join(opponent_summaries)

        prompt += "\n\nWhat is your argument for this round? Please maintain your role consistency."

        return prompt

    def get_recent_arguments(self, last_n_rounds: int = 2) -> List[Dict[str, Any]]:
        """获取最近几轮的论点"""
        return self.personal_history[-last_n_rounds:]

    def get_stance_evolution(self) -> Dict[str, Any]:
        """获取立场演化"""
        evolution = {}
        for key, value in self.stance_memory.items():
            if key != "core_stance":
                evolution[key] = value
        return evolution

    def get_argument_strength_analysis(self) -> Dict[str, float]:
        """获取论点强度分析"""
        strength_analysis = {}
        for round_num, arguments in self.argument_tracker.items():
            for arg_type, arg_data in arguments.items():
                key = f"round_{round_num}_{arg_type}"
                strength_analysis[key] = arg_data.get("strength", 0.5)
        return strength_analysis

    def clear_history(self, preserve_stance: bool = True):
        """清除历史记录"""
        self.personal_history.clear()
        self.argument_tracker.clear()
        self.round_memories.clear()

        if not preserve_stance:
            self.stance_memory.clear()

    def merge_with_session(self, other_session: 'RoleDebateSession') -> bool:
        """与另一个会话合并（用于角色切换后的状态恢复）"""
        if self.role_name != other_session.role_name:
            return False

        # 合并个人历史
        self.personal_history.extend(other_session.personal_history)

        # 合并立场记忆（后者覆盖前者）
        self.stance_memory.update(other_session.stance_memory)

        # 合并论点追踪
        for round_num, arguments in other_session.argument_tracker.items():
            if round_num not in self.argument_tracker:
                self.argument_tracker[round_num] = {}
            self.argument_tracker[round_num].update(arguments)

        # 合并轮次记忆
        self.round_memories.update(other_session.round_memories)

        return True

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "role_name": self.role_name,
            "role_persona": self.role_persona,
            "model_config": self.model_config.model_name,
            "system_prompt": self.system_prompt,
            "personal_history": self.personal_history,
            "stance_memory": self.stance_memory,
            "argument_tracker": self.argument_tracker,
            "round_memories": self.round_memories
        }

    def __str__(self) -> str:
        """字符串表示"""
        return f"RoleDebateSession(role={self.role_name}, model={self.model_config.model_name}, history_entries={len(self.personal_history)})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"RoleDebateSession(role_name='{self.role_name}', "
                f"role_persona='{self.role_persona[:50]}...', "
                f"model_config={self.model_config.model_name}, "
                f"history_count={len(self.personal_history)}, "
                f"stance_keys={list(self.stance_memory.keys())})")