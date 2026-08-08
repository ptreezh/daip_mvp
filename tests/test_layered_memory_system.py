"""
LayeredMemorySystem测试用例
测试分层记忆系统功能
"""

import pytest
from unittest.mock import Mock
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig


class TestLayeredMemorySystem:
    """分层记忆系统测试"""

    def test_memory_system_initialization(self):
        """测试记忆系统初始化"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 验证初始化
        assert len(memory_system.shared_factual_history) == 0
        assert len(memory_system.role_personal_memories) == 0
        assert len(memory_system.round_summaries) == 0
        assert len(memory_system.stance_evolution) == 0

    def test_add_shared_factual_history(self):
        """测试添加共享事实历史"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加共享事实
        memory_system.add_shared_fact(
            round_num=1,
            fact="AI technology has advanced significantly in recent years",
            source="tech_analyst",
            confidence=0.9
        )

        # 验证添加
        assert len(memory_system.shared_factual_history) == 1
        assert memory_system.shared_factual_history[0]["fact"] == "AI technology has advanced significantly in recent years"
        assert memory_system.shared_factual_history[0]["source"] == "tech_analyst"
        assert memory_system.shared_factual_history[0]["confidence"] == 0.9

    def test_update_role_memory(self):
        """测试更新角色记忆"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 更新角色记忆
        memory_system.update_role_memory(
            role_name="tech_analyst",
            content="AI will transform healthcare diagnostics",
            round_num=1,
            memory_type="argument"
        )

        # 验证更新
        assert "tech_analyst" in memory_system.role_personal_memories
        assert len(memory_system.role_personal_memories["tech_analyst"]["argument"]) == 1
        assert memory_system.role_personal_memories["tech_analyst"]["argument"][0]["content"] == "AI will transform healthcare diagnostics"

    def test_add_round_summary(self):
        """测试添加轮次摘要"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加轮次摘要
        memory_system.add_round_summary(
            round_num=1,
            summary="The debate focused on AI's impact on healthcare",
            key_points=["Diagnostics improvement", "Patient outcomes", "Cost reduction"],
            consensus_level=0.7
        )

        # 验证添加
        assert 1 in memory_system.round_summaries
        assert memory_system.round_summaries[1]["summary"] == "The debate focused on AI's impact on healthcare"
        assert len(memory_system.round_summaries[1]["key_points"]) == 3
        assert "Diagnostics improvement" in memory_system.round_summaries[1]["key_points"]

    def test_track_stance_evolution(self):
        """测试立场演化追踪"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 追踪立场演化
        memory_system.track_stance_evolution(
            role_name="tech_analyst",
            round_num=1,
            stance="AI is beneficial for healthcare",
            confidence=0.8,
            reasoning="Improved diagnostics and treatment"
        )

        memory_system.track_stance_evolution(
            role_name="tech_analyst",
            round_num=2,
            stance="AI is essential for healthcare advancement",
            confidence=0.9,
            reasoning="Proven success in early applications"
        )

        # 验证追踪
        assert "tech_analyst" in memory_system.stance_evolution
        assert len(memory_system.stance_evolution["tech_analyst"]) == 2
        assert memory_system.stance_evolution["tech_analyst"][1]["confidence"] == 0.9
        assert memory_system.stance_evolution["tech_analyst"][1]["stance"] == "AI is essential for healthcare advancement"

    def test_get_role_context(self):
        """测试获取角色上下文"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加一些数据
        memory_system.add_shared_fact(1, "AI helps in medical imaging", "tech_analyst", 0.9)
        memory_system.update_role_memory("tech_analyst", "AI improves diagnostic accuracy", 1, "argument")
        memory_system.add_round_summary(1, "Discussed medical AI applications", ["Diagnostics", "Treatment"], 0.8)

        # 获取角色上下文
        context = memory_system.get_role_context("tech_analyst", current_round=2)

        # 验证上下文内容
        assert "Shared Factual History:" in context
        assert "AI helps in medical imaging" in context
        assert "Personal Arguments:" in context
        assert "AI improves diagnostic accuracy" in context
        assert "Round Summaries:" in context
        assert "Discussed medical AI applications" in context

    def test_get_compressed_context(self):
        """测试获取压缩上下文"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加多轮数据
        for i in range(5):
            memory_system.add_shared_fact(i+1, f"Fact {i+1}", "tech_analyst", 0.8)
            memory_system.update_role_memory("tech_analyst", f"Argument {i+1}", i+1, "argument")
            memory_system.add_round_summary(i+1, f"Round {i+1} summary", [f"Point {i+1}"], 0.7)

        # 获取压缩上下文（最近3轮）
        compressed = memory_system.get_compressed_context("tech_analyst", current_round=6, max_rounds=3)

        # 验证压缩
        # 标题行 "Recent Shared Facts:" 含子串 "Fact"，只统计事实条目行
        assert len([line for line in compressed.split('\n') if line.startswith("  - Fact")]) <= 3
        assert len([line for line in compressed.split('\n') if line.startswith("  - Argument")]) <= 3
        assert "Round 4" in compressed
        assert "Round 5" in compressed
        assert "Round 1" not in compressed

    def test_memory_consistency_check(self):
        """测试记忆一致性检查"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加可能冲突的事实（源码 _are_contradictory 检测显式否定对，layered_memory_system.py:316-322）
        memory_system.add_shared_fact(1, "AI is safe for medical use", "tech_analyst", 0.9)
        memory_system.add_shared_fact(2, "AI is not safe for medical use", "ethics_expert", 0.8)

        # 检查一致性
        conflicts = memory_system.check_memory_consistency()

        # 验证发现冲突
        assert len(conflicts) > 0
        assert any("medical use" in conflict for conflict in conflicts)

    def test_memory_cleanup(self):
        """测试记忆清理"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加大量数据
        for i in range(20):
            memory_system.add_shared_fact(i+1, f"Fact {i+1}", "tech_analyst", 0.8)
            memory_system.update_role_memory("tech_analyst", f"Argument {i+1}", i+1, "argument")

        # 执行清理（保留最近10轮）
        memory_system.cleanup_old_memories(max_rounds_to_keep=10, current_round=20)

        # 验证清理
        assert len(memory_system.shared_factual_history) <= 10
        assert len(memory_system.role_personal_memories["tech_analyst"]["argument"]) <= 10

    def test_cross_role_memory_sharing(self):
        """测试跨角色记忆共享"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 角色A添加共享事实
        memory_system.add_shared_fact(1, "AI can reduce medical errors", "tech_analyst", 0.9)

        # 角色B获取上下文
        context_b = memory_system.get_role_context("ethics_expert", current_round=2)

        # 验证共享
        assert "AI can reduce medical errors" in context_b

    def test_stance_consistency_analysis(self):
        """测试立场一致性分析"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加一致的立场演化
        memory_system.track_stance_evolution("tech_analyst", 1, "AI is beneficial", 0.7, "Helps people")
        memory_system.track_stance_evolution("tech_analyst", 2, "AI is very beneficial", 0.8, "Proven benefits")
        memory_system.track_stance_evolution("tech_analyst", 3, "AI is essential", 0.9, "Critical for progress")

        # 分析一致性
        consistency = memory_system.analyze_stance_consistency("tech_analyst")

        # 验证一致性分析
        assert consistency["overall_consistency"] >= 0.7
        assert consistency["confidence_trend"] == "increasing"
        assert len(consistency["stance_shifts"]) == 2

    def test_memory_export_import(self):
        """测试记忆导出导入"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 添加数据
        memory_system.add_shared_fact(1, "Test fact", "test_role", 0.8)
        memory_system.update_role_memory("test_role", "Test argument", 1, "argument")

        # 导出
        export_data = memory_system.export_memory()

        # 创建新系统并导入
        new_system = LayeredMemorySystem()
        new_system.import_memory(export_data)

        # 验证导入
        assert len(new_system.shared_factual_history) == 1
        assert "test_role" in new_system.role_personal_memories
        assert new_system.shared_factual_history[0]["fact"] == "Test fact"

    def test_debate_progression_tracking(self):
        """测试辩论进程追踪"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 模拟多轮辩论
        rounds_data = [
            {"summary": "Initial discussion", "key_topics": ["AI basics"], "consensus": 0.5},
            {"summary": "Deep dive into applications", "key_topics": ["Healthcare", "Education"], "consensus": 0.6},
            {"summary": "Ethical considerations", "key_topics": ["Privacy", "Bias"], "consensus": 0.7}
        ]

        for i, round_data in enumerate(rounds_data):
            memory_system.add_round_summary(
                round_num=i+1,
                summary=round_data["summary"],
                key_points=round_data["key_topics"],
                consensus_level=round_data["consensus"]
            )

        # 获取进程摘要
        progression = memory_system.get_debate_progression_summary()

        # 验证进程追踪
        assert len(progression["rounds"]) == 3
        assert progression["consensus_trend"] == "improving"
        assert progression["topic_evolution"] == ["AI basics", "Healthcare", "Education", "Privacy", "Bias"]

    def test_error_handling(self):
        """测试错误处理"""
        from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem

        memory_system = LayeredMemorySystem()

        # 测试无效角色名
        context = memory_system.get_role_context("nonexistent_role", current_round=1)
        assert "No personal memory found" in context

        # 测试空数据（源码输出 "Shared Factual History:" + 换行 + "  None"）
        empty_context = memory_system.get_role_context("any_role", current_round=1)
        assert "Shared Factual History:" in empty_context
        assert "None" in empty_context

        # 测试无效轮次
        with pytest.raises(ValueError):
            memory_system.add_round_summary(0, "Invalid round", [], 0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])