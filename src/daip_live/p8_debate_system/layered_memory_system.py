"""
分层记忆系统
实现共享事实历史、角色独立记忆、轮次摘要和立场演化追踪
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import re


@dataclass
class LayeredMemorySystem:
    """分层记忆系统"""

    # 共享事实历史 - 所有角色共享的事实性信息
    shared_factual_history: List[Dict[str, Any]] = field(default_factory=list)

    # 角色个人记忆 - 每个角色独立的记忆
    role_personal_memories: Dict[str, Dict[str, List[Dict[str, Any]]]] = field(default_factory=dict)

    # 轮次摘要 - 每轮辩论的摘要
    round_summaries: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    # 立场演化追踪 - 每个角色立场的演化过程
    stance_evolution: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def add_shared_fact(self, round_num: int, fact: str, source: str, confidence: float):
        """添加共享事实"""
        self.shared_factual_history.append({
            "round": round_num,
            "fact": fact,
            "source": source,
            "confidence": confidence,
            "timestamp": self._get_timestamp()
        })

    def update_role_memory(self, role_name: str, content: str, round_num: int, memory_type: str):
        """更新角色记忆"""
        if role_name not in self.role_personal_memories:
            self.role_personal_memories[role_name] = {}

        if memory_type not in self.role_personal_memories[role_name]:
            self.role_personal_memories[role_name][memory_type] = []

        memory_entry = {
            "content": content,
            "round": round_num,
            "type": memory_type,
            "timestamp": self._get_timestamp()
        }

        self.role_personal_memories[role_name][memory_type].append(memory_entry)

    def add_round_summary(self, round_num: int, summary: str, key_points: List[str], consensus_level: float):
        """添加轮次摘要"""
        if round_num < 1:
            raise ValueError("Round number must be at least 1")

        self.round_summaries[round_num] = {
            "summary": summary,
            "key_points": key_points,
            "consensus_level": consensus_level,
            "timestamp": self._get_timestamp()
        }

    def track_stance_evolution(self, role_name: str, round_num: int, stance: str, confidence: float, reasoning: str):
        """追踪立场演化"""
        if role_name not in self.stance_evolution:
            self.stance_evolution[role_name] = []

        stance_entry = {
            "round": round_num,
            "stance": stance,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": self._get_timestamp()
        }

        self.stance_evolution[role_name].append(stance_entry)

    def get_role_context(self, role_name: str, current_round: int) -> str:
        """获取角色特定上下文"""
        context_parts = []

        # 共享事实历史
        context_parts.append("Shared Factual History:")
        relevant_facts = [f for f in self.shared_factual_history if f["round"] < current_round]
        if relevant_facts:
            for fact in relevant_facts[-5:]:  # 最近5个事实
                context_parts.append(f"  - {fact['fact']} (Round {fact['round']}, Confidence: {fact['confidence']})")
        else:
            context_parts.append("  None")

        # 角色个人记忆
        context_parts.append(f"\nPersonal Arguments:")
        if role_name in self.role_personal_memories:
            # 修复: update_role_memory 以 memory_type（如 "argument" 单数）为 key，
            # 此处需兼容单复数两种 key
            arguments = (self.role_personal_memories[role_name].get("arguments")
                         or self.role_personal_memories[role_name].get("argument", []))
            relevant_args = [arg for arg in arguments if arg["round"] < current_round]
            if relevant_args:
                for arg in relevant_args[-3:]:  # 最近3个论点
                    context_parts.append(f"  - {arg['content']} (Round {arg['round']})")
            else:
                context_parts.append("  None")
        else:
            context_parts.append("  No personal memory found")

        # 轮次摘要
        context_parts.append(f"\nRound Summaries:")
        relevant_rounds = [r for r in range(1, current_round) if r in self.round_summaries]
        if relevant_rounds:
            for round_num in relevant_rounds[-3:]:  # 最近3轮摘要
                summary = self.round_summaries[round_num]
                context_parts.append(f"  Round {round_num}: {summary['summary']}")
                context_parts.append(f"    Key Points: {', '.join(summary['key_points'])}")
        else:
            context_parts.append("  None")

        return "\n".join(context_parts)

    def get_compressed_context(self, role_name: str, current_round: int, max_rounds: int = 3) -> str:
        """获取压缩上下文（用于防止上下文过长）"""
        context_parts = []

        # 共享事实 - 只保留最近的
        recent_facts = [f for f in self.shared_factual_history if f["round"] >= current_round - max_rounds]
        if recent_facts:
            context_parts.append("Recent Shared Facts:")
            for fact in recent_facts[-3:]:
                context_parts.append(f"  - {fact['fact']}")

        # 角色论点 - 只保留最近的
        if role_name in self.role_personal_memories:
            arguments = (self.role_personal_memories[role_name].get("arguments")
                         or self.role_personal_memories[role_name].get("argument", []))
            recent_args = [arg for arg in arguments if arg["round"] >= current_round - max_rounds]
            if recent_args:
                context_parts.append("\nRecent Arguments:")
                for arg in recent_args[-2:]:
                    context_parts.append(f"  - {arg['content']}")

        # 轮次摘要 - 只保留最近的
        recent_rounds = [r for r in range(max(1, current_round - max_rounds + 1), current_round) if r in self.round_summaries]
        if recent_rounds:
            context_parts.append("\nRecent Round Summaries:")
            for round_num in recent_rounds:
                summary = self.round_summaries[round_num]
                context_parts.append(f"  Round {round_num}: {summary['summary']}")

        return "\n".join(context_parts) if context_parts else "No recent context available"

    def check_memory_consistency(self) -> List[str]:
        """检查记忆一致性，返回冲突列表"""
        conflicts = []

        # 检查事实一致性
        fact_groups = {}
        for fact in self.shared_factual_history:
            # 简单的关键词匹配来检测潜在冲突
            key_words = re.findall(r'\b\w+\b', fact['fact'].lower())
            key_words = [w for w in key_words if len(w) > 3]  # 过滤短词

            for word in key_words:
                if word not in fact_groups:
                    fact_groups[word] = []
                fact_groups[word].append(fact)

        # 查找潜在冲突
        for word, facts in fact_groups.items():
            if len(facts) > 1:
                # 检查是否表达相反观点
                for i, fact1 in enumerate(facts):
                    for fact2 in facts[i+1:]:
                        if self._are_contradictory(fact1['fact'], fact2['fact']):
                            conflicts.append(f"Contradictory facts about '{word}': '{fact1['fact']}' vs '{fact2['fact']}'")

        return conflicts

    def cleanup_old_memories(self, max_rounds_to_keep: int, current_round: int):
        """清理旧记忆以防止内存溢出"""
        cutoff_round = current_round - max_rounds_to_keep + 1
        # 只保留大于等于cutoff_round的记录

        # 清理共享事实
        self.shared_factual_history = [f for f in self.shared_factual_history if f["round"] >= cutoff_round]

        # 清理角色记忆
        for role_name in self.role_personal_memories:
            for memory_type in self.role_personal_memories[role_name]:
                self.role_personal_memories[role_name][memory_type] = [
                    m for m in self.role_personal_memories[role_name][memory_type]
                    if m["round"] >= cutoff_round
                ]

        # 清理立场演化
        for role_name in self.stance_evolution:
            self.stance_evolution[role_name] = [
                s for s in self.stance_evolution[role_name]
                if s["round"] >= cutoff_round
            ]

    def analyze_stance_consistency(self, role_name: str) -> Dict[str, Any]:
        """分析角色立场一致性"""
        if role_name not in self.stance_evolution:
            return {"overall_consistency": 0.0, "confidence_trend": "unknown", "stance_shifts": []}

        stances = self.stance_evolution[role_name]
        if len(stances) < 2:
            return {"overall_consistency": 1.0, "confidence_trend": "stable", "stance_shifts": []}

        # 计算置信度趋势
        confidences = [s["confidence"] for s in stances]
        if confidences[-1] > confidences[0]:
            confidence_trend = "increasing"
        elif confidences[-1] < confidences[0]:
            confidence_trend = "decreasing"
        else:
            confidence_trend = "stable"

        # 检测立场转变
        stance_shifts = []
        for i in range(1, len(stances)):
            if self._are_stances_different(stances[i-1]["stance"], stances[i]["stance"]):
                stance_shifts.append({
                    "from_round": stances[i-1]["round"],
                    "to_round": stances[i]["round"],
                    "from_stance": stances[i-1]["stance"],
                    "to_stance": stances[i]["stance"]
                })

        # 计算总体一致性（基于立场转变次数）
        shift_penalty = len(stance_shifts) * 0.15
        overall_consistency = max(0.0, 1.0 - shift_penalty)

        return {
            "overall_consistency": overall_consistency,
            "confidence_trend": confidence_trend,
            "stance_shifts": stance_shifts,
            "current_confidence": confidences[-1],
            "confidence_progression": confidences
        }

    def get_debate_progression_summary(self) -> Dict[str, Any]:
        """获取辩论进程摘要"""
        if not self.round_summaries:
            return {"rounds": [], "consensus_trend": "unknown", "topic_evolution": []}

        rounds = sorted(self.round_summaries.keys())
        consensus_levels = [self.round_summaries[r]["consensus_level"] for r in rounds]

        # 共识趋势
        if len(consensus_levels) > 1:
            if consensus_levels[-1] > consensus_levels[0]:
                consensus_trend = "improving"
            elif consensus_levels[-1] < consensus_levels[0]:
                consensus_trend = "declining"
            else:
                consensus_trend = "stable"
        else:
            consensus_trend = "stable"

        # 话题演化
        all_topics = []
        for round_num in rounds:
            all_topics.extend(self.round_summaries[round_num]["key_points"])

        return {
            "rounds": [self.round_summaries[r] for r in rounds],
            "consensus_trend": consensus_trend,
            "topic_evolution": all_topics,
            "total_rounds": len(rounds),
            "average_consensus": sum(consensus_levels) / len(consensus_levels)
        }

    def export_memory(self) -> Dict[str, Any]:
        """导出记忆数据"""
        return {
            "shared_factual_history": self.shared_factual_history,
            "role_personal_memories": self.role_personal_memories,
            "round_summaries": self.round_summaries,
            "stance_evolution": self.stance_evolution,
            "export_timestamp": self._get_timestamp()
        }

    def import_memory(self, memory_data: Dict[str, Any]):
        """导入记忆数据"""
        self.shared_factual_history = memory_data.get("shared_factual_history", [])
        self.role_personal_memories = memory_data.get("role_personal_memories", {})
        self.round_summaries = memory_data.get("round_summaries", {})
        self.stance_evolution = memory_data.get("stance_evolution", {})

    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        return {
            "total_shared_facts": len(self.shared_factual_history),
            "total_roles": len(self.role_personal_memories),
            "total_round_summaries": len(self.round_summaries),
            "total_stance_entries": sum(len(stances) for stances in self.stance_evolution.values()),
            "memory_size_estimate": len(json.dumps(self.export_memory()))
        }

    def clear_all_memories(self):
        """清除所有记忆"""
        self.shared_factual_history.clear()
        self.role_personal_memories.clear()
        self.round_summaries.clear()
        self.stance_evolution.clear()

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        return datetime.now().isoformat()

    def _are_contradictory(self, fact1: str, fact2: str) -> bool:
        """检查两个事实是否矛盾（简单实现）"""
        # 简单的矛盾检测逻辑
        contradictory_pairs = [
            (r"is safe", r"is not safe"),
            (r"is beneficial", r"is harmful"),
            (r"will improve", r"will worsen"),
            (r"supports", r"opposes"),
            (r"increases", r"decreases")
        ]

        fact1_lower = fact1.lower()
        fact2_lower = fact2.lower()

        for pattern1, pattern2 in contradictory_pairs:
            if (re.search(pattern1, fact1_lower) and re.search(pattern2, fact2_lower)) or \
               (re.search(pattern2, fact1_lower) and re.search(pattern1, fact2_lower)):
                return True

        return False

    def _are_stances_different(self, stance1: str, stance2: str) -> bool:
        """检查两个立场是否不同（简单实现）"""
        # 更精确的立场变化检测
        stance1_lower = stance1.lower()
        stance2_lower = stance2.lower()

        # 检查关键词强度变化
        intensity_words = {
            "beneficial": ["very beneficial", "essential"],
            "good": ["very good", "excellent"],
            "important": ["very important", "critical"],
            "helpful": ["very helpful", "essential"]
        }

        for base, intensifiers in intensity_words.items():
            if base in stance1_lower and any(i in stance2_lower for i in intensifiers):
                return True
            if base in stance2_lower and any(i in stance1_lower for i in intensifiers):
                return True

        # 检查是否表达完全不同的观点
        stance1_words = set(re.findall(r'\b\w+\b', stance1.lower()))
        stance2_words = set(re.findall(r'\b\w+\b', stance2.lower()))

        intersection = stance1_words.intersection(stance2_words)
        union = stance1_words.union(stance2_words)

        if not union:
            return False

        similarity = len(intersection) / len(union)
        return similarity < 0.6

    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_memory_statistics()
        return f"LayeredMemorySystem(facts={stats['total_shared_facts']}, roles={stats['total_roles']}, rounds={stats['total_round_summaries']})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"LayeredMemorySystem("
                f"shared_facts={len(self.shared_factual_history)}, "
                f"roles={list(self.role_personal_memories.keys())}, "
                f"round_summaries={list(self.round_summaries.keys())}, "
                f"stance_evolution={list(self.stance_evolution.keys())})")