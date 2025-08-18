#!/usr/bin/env python3
"""工作流共识算法测试

测试WorkflowConsensusAlgorithm的各种功能，包括与工作流引擎的兼容性。
"""

import asyncio
import sys

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

async def test_workflow_consensus_algorithm():
    """测试工作流共识算法"""
    print("🧪 测试工作流共识算法...")
    
    try:
        from workflow_consensus_algorithm import WorkflowConsensusAlgorithm
        
        # 创建算法实例
        algorithm = WorkflowConsensusAlgorithm()
        print("✅ 算法实例创建成功")
        
        # 测试元数据
        metadata = algorithm.get_metadata()
        print(f"✅ 算法元数据: {metadata.name} v{metadata.version}")
        print(f"   复杂度: {metadata.complexity}, 准确性: {metadata.accuracy}")
        
        # 测试能力描述
        capabilities = algorithm.get_capabilities()
        print(f"✅ 算法能力: 最少{capabilities.min_participants}个参与者")
        
        # 测试简单共识
        await test_simple_consensus(algorithm)
        
        # 测试事实-证据格式
        await test_fact_evidence_format(algorithm)
        
        # 测试不同共识方法
        await test_different_consensus_methods()
        
        # 测试工作流兼容性
        await test_workflow_compatibility(algorithm)
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_simple_consensus(algorithm):
    """测试简单共识功能"""
    print("\n📊 测试简单共识...")
    
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    
    # 创建简单共识输入
    inputs = [
        ConsensusInput(
            agent_id="reviewer1", 
            position="方案A", 
            confidence=0.8,
            reasoning="方案A具有更好的可行性"
        ),
        ConsensusInput(
            agent_id="reviewer2", 
            position="方案A", 
            confidence=0.9,
            reasoning="技术实现相对简单"
        ),
        ConsensusInput(
            agent_id="reviewer3", 
            position="方案B", 
            confidence=0.6,
            reasoning="方案B创新性更强"
        )
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    print(f"   共识结果: {result.consensus_value}")
    print(f"   置信度: {result.confidence:.3f}")
    print(f"   工作流兼容: {result.metadata.get('workflow_compatible', False)}")
    
    # 应该选择支持度更高的方案A
    assert "方案A" in str(result.consensus_value), "简单共识结果错误"
    assert result.metadata.get("workflow_compatible", False), "应该与工作流兼容"
    print("✅ 简单共识测试通过")

async def test_fact_evidence_format(algorithm):
    """测试事实-证据格式"""
    print("\n🔍 测试事实-证据格式...")
    
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    
    # 创建事实-证据格式输入
    inputs = [
        ConsensusInput(
            agent_id="expert1",
            position="支持证据1",
            confidence=0.9,
            reasoning="强有力的实验数据支持",
            metadata={
                "fact_id": "fact_001",
                "fact_content": "新药物具有显著疗效",
                "evidence_type": "supporting"
            }
        ),
        ConsensusInput(
            agent_id="expert2",
            position="支持证据2",
            confidence=0.8,
            reasoning="临床试验结果积极",
            metadata={
                "fact_id": "fact_001",
                "fact_content": "新药物具有显著疗效",
                "evidence_type": "supporting"
            }
        ),
        ConsensusInput(
            agent_id="critic1",
            position="质疑证据1",
            confidence=0.7,
            reasoning="样本量可能不足",
            metadata={
                "fact_id": "fact_001",
                "fact_content": "新药物具有显著疗效",
                "evidence_type": "challenging"
            }
        ),
        ConsensusInput(
            agent_id="neutral1",
            position="中性观察",
            confidence=0.5,
            reasoning="需要更多长期数据",
            metadata={
                "fact_id": "fact_001",
                "fact_content": "新药物具有显著疗效",
                "evidence_type": "neutral"
            }
        )
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    print(f"   事实可信度: {result.confidence:.3f}")
    print(f"   证据聚合: {result.metadata.get('evidence_aggregated', False)}")
    print(f"   可信度分数: {result.metadata.get('credibility_scores', {})}")
    
    # 支持证据较多，可信度应该较高
    assert result.confidence > 0.6, "事实可信度应该较高"
    assert result.metadata.get("evidence_aggregated", False), "应该聚合证据"
    print("✅ 事实-证据格式测试通过")

async def test_different_consensus_methods():
    """测试不同的共识方法"""
    print("\n⚙️ 测试不同共识方法...")
    
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    from workflow_consensus_algorithm import WorkflowConsensusAlgorithm
    
    # 创建测试输入
    inputs = [
        ConsensusInput(
            agent_id="voter1",
            position="选项A",
            confidence=0.8,
            reasoning="理由1"
        ),
        ConsensusInput(
            agent_id="voter2",
            position="选项A",
            confidence=0.9,
            reasoning="理由2"
        ),
        ConsensusInput(
            agent_id="voter3",
            position="选项B",
            confidence=0.7,
            reasoning="理由3"
        )
    ]
    
    # 测试加权平均方法
    weighted_algorithm = WorkflowConsensusAlgorithm({
        "consensus_method": "weighted_average",
        "credibility_threshold": 0.6
    })
    
    context = ConsensusContext()
    weighted_result = await weighted_algorithm.calculate(inputs, context)
    
    print(f"   加权平均结果: {weighted_result.confidence:.3f}")
    
    # 测试多数投票方法
    majority_algorithm = WorkflowConsensusAlgorithm({
        "consensus_method": "majority_vote",
        "credibility_threshold": 0.6
    })
    
    majority_result = await majority_algorithm.calculate(inputs, context)
    
    print(f"   多数投票结果: {majority_result.confidence:.3f}")
    
    # 两种方法都应该产生有效结果
    assert 0.0 <= weighted_result.confidence <= 1.0, "加权平均结果无效"
    assert 0.0 <= majority_result.confidence <= 1.0, "多数投票结果无效"
    print("✅ 不同共识方法测试通过")

async def test_workflow_compatibility(algorithm):
    """测试工作流兼容性"""
    print("\n🔄 测试工作流兼容性...")
    
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    
    # 模拟聚合证据格式（工作流中的典型格式）
    aggregated_evidence_input = ConsensusInput(
        agent_id="workflow_system",
        position={
            "aggregated_evidence": {
                "fact_001": {
                    "fact_content": "系统性能满足要求",
                    "supporting_count": 3,
                    "challenging_count": 1,
                    "neutral_count": 1,
                    "supporting_score": 2.4,
                    "challenging_score": 0.6,
                    "neutral_score": 0.5,
                    "evidence_summary": "性能测试结果积极; 负载测试通过; 存在内存使用问题"
                }
            }
        },
        confidence=1.0,
        reasoning="来自工作流的聚合证据"
    )
    
    context = ConsensusContext()
    result = await algorithm.calculate([aggregated_evidence_input], context)
    
    print(f"   工作流结果: {result.confidence:.3f}")
    print(f"   处理的事实数: {result.metadata.get('facts_processed', 0)}")
    
    # 应该正确处理聚合证据格式
    assert result.metadata.get("facts_processed", 0) > 0, "应该处理事实"
    assert result.confidence > 0.5, "支持证据较多，可信度应该较高"
    print("✅ 工作流兼容性测试通过")

async def test_edge_cases():
    """测试边界情况"""
    print("\n⚠️ 测试边界情况...")
    
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    from workflow_consensus_algorithm import WorkflowConsensusAlgorithm
    
    algorithm = WorkflowConsensusAlgorithm()
    
    # 测试单个输入
    single_input = [ConsensusInput(
        agent_id="single",
        position="唯一观点",
        confidence=0.8,
        reasoning="只有一个观点"
    )]
    
    context = ConsensusContext()
    result = await algorithm.calculate(single_input, context)
    assert result.confidence > 0, "单输入应该产生有效结果"
    print("✅ 单输入测试通过")
    
    # 测试配置验证
    bad_config = {"consensus_method": "invalid_method"}
    validation = algorithm.validate_configuration(bad_config)
    assert not validation.is_valid, "无效配置应该验证失败"
    print("✅ 配置验证测试通过")
    
    # 测试输入验证 - 创建有效输入但通过validate_inputs检查无效置信度
    valid_inputs = [ConsensusInput(
        agent_id="test",
        position="test",
        confidence=0.8
    )]
    
    # 手动修改置信度来测试验证
    valid_inputs[0].confidence = 1.5  # 直接修改以测试验证逻辑
    
    validation = algorithm.validate_inputs(valid_inputs)
    assert not validation.is_valid, "无效输入应该验证失败"
    print("✅ 输入验证测试通过")

async def test_performance_and_health():
    """测试性能和健康状态"""
    print("\n🏥 测试性能和健康状态...")
    
    from consensus_models import ConsensusInput, ConsensusRequest
    from workflow_consensus_algorithm import WorkflowConsensusAlgorithm
    
    algorithm = WorkflowConsensusAlgorithm()
    
    # 测试健康状态
    health = algorithm.get_health_status()
    assert health["status"] == "healthy", "健康状态应该正常"
    assert health["workflow_compatible"], "应该与工作流兼容"
    print("✅ 健康状态检查通过")
    
    # 测试执行时间估算
    request = ConsensusRequest(
        inputs=[
            ConsensusInput(agent_id="test1", position="A", confidence=0.8),
            ConsensusInput(agent_id="test2", position="B", confidence=0.7),
            ConsensusInput(agent_id="test3", position="A", confidence=0.9)
        ]
    )
    
    estimated_time = algorithm.estimate_execution_time(request)
    assert estimated_time > 0, "执行时间估算应该大于0"
    print(f"✅ 执行时间估算: {estimated_time:.3f}秒")
    
    # 测试不同方法的时间差异
    synthesis_algorithm = WorkflowConsensusAlgorithm({
        "consensus_method": "synthesis"
    })
    
    synthesis_time = synthesis_algorithm.estimate_execution_time(request)
    assert synthesis_time > estimated_time, "综合分析方法应该需要更多时间"
    print(f"✅ 综合分析时间估算: {synthesis_time:.3f}秒")

if __name__ == "__main__":
    asyncio.run(test_workflow_consensus_algorithm())
    asyncio.run(test_edge_cases())
    asyncio.run(test_performance_and_health())