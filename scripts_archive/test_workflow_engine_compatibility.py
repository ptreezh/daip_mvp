#!/usr/bin/env python3
"""WorkflowEngine兼容层测试

测试WorkflowEngine与统一共识调度器的集成兼容性。
"""

import asyncio
import sys

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

async def test_workflow_engine_compatibility():
    """测试WorkflowEngine兼容层"""
    print("🧪 测试WorkflowEngine兼容层...")

    try:
        from legacy_compatibility_layer import get_workflow_engine_compatibility

        # 创建兼容层实例
        workflow_engine = get_workflow_engine_compatibility()
        print("✅ WorkflowEngine兼容层创建成功")

        # 测试聚合证据格式处理
        await test_aggregated_evidence_format(workflow_engine)

        # 测试直接输入格式处理
        await test_direct_input_format(workflow_engine)

        # 测试工作流节点输出格式
        await test_workflow_output_format(workflow_engine)

        # 测试错误处理
        await test_workflow_error_handling(workflow_engine)

        print("🎉 所有WorkflowEngine兼容性测试通过！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_aggregated_evidence_format(workflow_engine):
    """测试聚合证据格式处理"""
    print("\n📊 测试聚合证据格式...")

    # 模拟ConsensusNode期望的聚合证据格式
    inputs = {
        "aggregated_evidence": {
            "fact_001": {
                "fact_content": "新系统性能满足要求",
                "supporting_count": 3,
                "challenging_count": 1,
                "neutral_count": 1,
                "supporting_score": 2.4,
                "challenging_score": 0.6,
                "neutral_score": 0.5,
                "evidence_summary": "性能测试结果积极; 负载测试通过; 存在内存使用问题"
            },
            "fact_002": {
                "fact_content": "用户界面设计合理",
                "supporting_count": 4,
                "challenging_count": 0,
                "neutral_count": 1,
                "supporting_score": 3.2,
                "challenging_score": 0.0,
                "neutral_score": 0.3,
                "evidence_summary": "用户反馈积极; 界面直观易用; 需要小幅调整"
            }
        }
    }

    # 创建模拟的执行上下文
    class MockExecutionContext:
        def __init__(self):
            self.services = {}
            self.config = {}

    execution_context = MockExecutionContext()

    # 执行共识节点
    result = await workflow_engine.execute_consensus_node(inputs, execution_context)

    print(f"   执行结果: {'成功' if result.get('success') else '失败'}")
    print(f"   处理的事实数: {len(result.get('credibility_scores', {}))}")
    print(f"   可信度分数: {result.get('credibility_scores', {})}")

    # 验证输出格式
    assert result.get("success", False), "聚合证据处理应该成功"
    assert "credibility_scores" in result, "应该包含可信度分数"
    assert "consensus_results" in result, "应该包含共识结果"
    assert "facts_needing_revision" in result, "应该包含需要修订的事实"

    # 验证事实处理
    credibility_scores = result.get("credibility_scores", {})
    assert len(credibility_scores) == 2, "应该处理2个事实"
    assert "fact_001" in credibility_scores, "应该包含fact_001"
    assert "fact_002" in credibility_scores, "应该包含fact_002"

    print("✅ 聚合证据格式测试通过")

async def test_direct_input_format(workflow_engine):
    """测试直接输入格式处理"""
    print("\n🔧 测试直接输入格式...")

    # 模拟直接输入格式
    inputs = {
        "input1": {
            "agent_id": "reviewer1",
            "position": "方案可行",
            "confidence": 0.8,
            "reasoning": "基于技术分析的结论",
            "metadata": {"domain": "technical"}
        },
        "input2": {
            "agent_id": "reviewer2",
            "position": "方案可行",
            "confidence": 0.9,
            "reasoning": "经验判断支持",
            "metadata": {"domain": "business"}
        },
        "input3": {
            "agent_id": "reviewer3",
            "position": "需要改进",
            "confidence": 0.6,
            "reasoning": "存在一些风险",
            "metadata": {"domain": "risk"}
        }
    }

    class MockExecutionContext:
        def __init__(self):
            self.services = {}
            self.config = {}

    execution_context = MockExecutionContext()

    # 执行共识节点
    result = await workflow_engine.execute_consensus_node(inputs, execution_context)

    print(f"   执行结果: {'成功' if result.get('success') else '失败'}")
    print(f"   处理的输入数: {len(result.get('credibility_scores', {}))}")

    # 验证结果
    assert result.get("success", False), "直接输入处理应该成功"
    assert len(result.get("credibility_scores", {})) > 0, "应该有可信度分数"

    print("✅ 直接输入格式测试通过")

async def test_workflow_output_format(workflow_engine):
    """测试工作流节点输出格式"""
    print("\n📋 测试工作流输出格式...")

    # 使用聚合证据格式进行测试
    inputs = {
        "aggregated_evidence": {
            "test_fact": {
                "fact_content": "测试事实内容",
                "supporting_count": 2,
                "challenging_count": 1,
                "neutral_count": 0,
                "supporting_score": 1.6,
                "challenging_score": 0.4,
                "neutral_score": 0.0,
                "evidence_summary": "测试证据摘要"
            }
        }
    }

    class MockExecutionContext:
        def __init__(self):
            self.services = {}
            self.config = {}

    execution_context = MockExecutionContext()

    # 执行共识节点
    result = await workflow_engine.execute_consensus_node(inputs, execution_context)

    print(f"   执行成功: {result.get('success', False)}")

    if result.get("success", False):
        # 检查输出格式是否符合ConsensusNode期望
        required_fields = ["credibility_scores", "consensus_results", "facts_needing_revision"]
        for field in required_fields:
            assert field in result, f"输出应该包含{field}字段"
            print(f"   ✅ 包含{field}字段")

        # 检查consensus_results的详细格式
        consensus_results = result.get("consensus_results", {})
        if consensus_results:
            first_result = list(consensus_results.values())[0]
            expected_result_fields = [
                "fact_id", "fact_content", "credibility_score",
                "consensus_method", "needs_revision", "evidence_summary"
            ]

            for field in expected_result_fields:
                assert field in first_result, f"共识结果应该包含{field}字段"
                print(f"   ✅ 共识结果包含{field}字段")

        # 检查可信度阈值逻辑
        credibility_scores = result.get("credibility_scores", {})
        facts_needing_revision = result.get("facts_needing_revision", [])

        print(f"   可信度分数: {credibility_scores}")
        print(f"   需要修订的事实: {facts_needing_revision}")

        # 验证逻辑一致性
        for fact_id, score in credibility_scores.items():
            if score < 0.6:  # 默认阈值
                assert fact_id in facts_needing_revision, f"低可信度事实{fact_id}应该在修订列表中"

    print("✅ 工作流输出格式测试通过")

async def test_workflow_error_handling(workflow_engine):
    """测试工作流错误处理"""
    print("\n⚠️ 测试工作流错误处理...")

    class MockExecutionContext:
        def __init__(self):
            self.services = {}
            self.config = {}

    execution_context = MockExecutionContext()

    # 测试空输入
    empty_result = await workflow_engine.execute_consensus_node({}, execution_context)
    print(f"   空输入处理: {'正确' if not empty_result.get('success') else '错误'}")
    assert not empty_result.get("success", True), "空输入应该处理失败"

    # 测试无效输入格式
    invalid_inputs = {
        "invalid_key": "invalid_value"
    }

    invalid_result = await workflow_engine.execute_consensus_node(invalid_inputs, execution_context)
    print(f"   无效输入处理: {'正确' if not invalid_result.get('success') else '错误'}")

    # 验证错误输出格式
    assert "success" in empty_result, "错误结果应该包含success字段"
    assert "error" in empty_result, "错误结果应该包含error字段"
    assert "credibility_scores" in empty_result, "错误结果应该包含空的credibility_scores"
    assert "consensus_results" in empty_result, "错误结果应该包含空的consensus_results"
    assert "facts_needing_revision" in empty_result, "错误结果应该包含空的facts_needing_revision"

    print("✅ 工作流错误处理测试通过")

async def test_evidence_confidence_calculation():
    """测试证据置信度计算"""
    print("\n🧮 测试证据置信度计算...")

    from legacy_compatibility_layer import WorkflowEngineCompatibility

    workflow_engine = WorkflowEngineCompatibility()

    # 测试不同的证据组合
    test_cases = [
        {
            "name": "强支持证据",
            "evidence": {
                "supporting_score": 3.0,
                "challenging_score": 0.5,
                "neutral_score": 0.5
            },
            "expected_range": (0.7, 1.0)
        },
        {
            "name": "强质疑证据",
            "evidence": {
                "supporting_score": 0.5,
                "challenging_score": 3.0,
                "neutral_score": 0.5
            },
            "expected_range": (0.0, 0.3)
        },
        {
            "name": "平衡证据",
            "evidence": {
                "supporting_score": 1.5,
                "challenging_score": 1.5,
                "neutral_score": 1.0
            },
            "expected_range": (0.4, 0.6)
        },
        {
            "name": "无证据",
            "evidence": {
                "supporting_score": 0.0,
                "challenging_score": 0.0,
                "neutral_score": 0.0
            },
            "expected_range": (0.5, 0.5)
        }
    ]

    for test_case in test_cases:
        confidence = workflow_engine._calculate_evidence_confidence(test_case["evidence"])
        min_expected, max_expected = test_case["expected_range"]

        print(f"   {test_case['name']}: {confidence:.3f} (期望: {min_expected}-{max_expected})")

        assert min_expected <= confidence <= max_expected, \
            f"{test_case['name']}的置信度{confidence}不在期望范围{test_case['expected_range']}内"

    print("✅ 证据置信度计算测试通过")

if __name__ == "__main__":
    asyncio.run(test_workflow_engine_compatibility())
    asyncio.run(test_evidence_confidence_calculation())
