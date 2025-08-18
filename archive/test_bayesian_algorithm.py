#!/usr/bin/env python3
"""贝叶斯共识算法测试

测试BayesianAlgorithm的各种功能，包括数值和分类贝叶斯更新。
"""

import asyncio
import sys

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

async def test_bayesian_algorithm():
    """测试贝叶斯共识算法"""
    print("🧪 测试贝叶斯共识算法...")
    
    try:
        from bayesian_algorithm import BayesianAlgorithm
        
        # 创建算法实例
        algorithm = BayesianAlgorithm()
        print("✅ 算法实例创建成功")
        
        # 测试元数据
        metadata = algorithm.get_metadata()
        print(f"✅ 算法元数据: {metadata.name} v{metadata.version}")
        print(f"   复杂度: {metadata.complexity}, 准确性: {metadata.accuracy}")
        
        # 测试能力描述
        capabilities = algorithm.get_capabilities()
        print(f"✅ 算法能力: 最少{capabilities.min_participants}个参与者")
        
        # 测试数值贝叶斯共识
        await test_numerical_bayesian_consensus(algorithm)
        
        # 测试分类贝叶斯共识
        await test_categorical_bayesian_consensus(algorithm)
        
        # 测试先验强度影响
        await test_prior_strength_effect()
        
        # 测试收敛信息
        await test_convergence_info(algorithm)
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_numerical_bayesian_consensus(algorithm):
    """测试数值贝叶斯共识"""
    print("\n🔢 测试数值贝叶斯共识...")
    
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    
    # 创建数值输入（不同置信度作为精度权重）
    inputs = [
        ConsensusInput(
            agent_id="precise_sensor", 
            position=7.8, 
            confidence=0.9,  # 高精度
            reasoning="高精度传感器测量"
        ),
        ConsensusInput(
            agent_id="medium_sensor", 
            position=8.1, 
            confidence=0.7,  # 中等精度
            reasoning="中等精度传感器测量"
        ),
        ConsensusInput(
            agent_id="rough_estimate", 
            position=7.5, 
            confidence=0.4,  # 低精度
            reasoning="粗略估计"
        ),
        ConsensusInput(
            agent_id="expert_judgment", 
            position=7.9, 
            confidence=0.8,  # 高精度
            reasoning="专家判断"
        )
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    print(f"   共识结果: {result.consensus_value:.3f}")
    print(f"   置信度: {result.confidence:.3f}")
    print(f"   共识类型: {result.metadata.get('consensus_type', 'unknown')}")
    
    # 结果应该偏向高置信度的输入
    assert 7.5 <= result.consensus_value <= 8.1, "数值共识结果超出合理范围"
    assert result.metadata.get("precision_weighted", False), "应该使用精度加权"
    print("✅ 数值贝叶斯共识测试通过")

async def test_categorical_bayesian_consensus(algorithm):
    """测试分类贝叶斯共识"""
    print("\n📊 测试分类贝叶斯共识...")
    
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    
    # 创建分类输入（置信度作为证据强度）
    inputs = [
        ConsensusInput(
            agent_id="strong_evidence", 
            position="选项A", 
            confidence=0.9,
            reasoning="强有力的证据支持"
        ),
        ConsensusInput(
            agent_id="moderate_evidence", 
            position="选项A", 
            confidence=0.7,
            reasoning="中等证据支持"
        ),
        ConsensusInput(
            agent_id="weak_counter", 
            position="选项B", 
            confidence=0.3,
            reasoning="微弱的反对证据"
        ),
        ConsensusInput(
            agent_id="uncertain", 
            position="选项C", 
            confidence=0.2,
            reasoning="不确定的观点"
        )
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    print(f"   共识结果: {result.consensus_value}")
    print(f"   置信度: {result.confidence:.3f}")
    print(f"   共识类型: {result.metadata.get('consensus_type', 'unknown')}")
    
    # 强证据的选项A应该获胜
    assert result.consensus_value == "选项A", "分类贝叶斯共识结果错误"
    assert result.metadata.get("evidence_aggregated", False), "应该聚合证据"
    print("✅ 分类贝叶斯共识测试通过")

async def test_prior_strength_effect():
    """测试先验强度的影响"""
    print("\n🎯 测试先验强度影响...")
    
    from bayesian_algorithm import BayesianAlgorithm
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    
    # 创建测试输入
    inputs = [
        ConsensusInput(agent_id="agent1", position=8.0, confidence=0.6),
        ConsensusInput(agent_id="agent2", position=9.0, confidence=0.6)
    ]
    
    # 测试不同先验强度
    weak_prior = BayesianAlgorithm({"prior_strength": 0.1})
    strong_prior = BayesianAlgorithm({"prior_strength": 5.0})
    
    context = ConsensusContext()
    
    weak_result = await weak_prior.calculate(inputs, context)
    strong_result = await strong_prior.calculate(inputs, context)
    
    print(f"   弱先验结果: {weak_result.consensus_value:.3f}, 置信度: {weak_result.confidence:.3f}")
    print(f"   强先验结果: {strong_result.consensus_value:.3f}, 置信度: {strong_result.confidence:.3f}")
    
    # 强先验应该产生更保守的结果
    assert weak_result.confidence > strong_result.confidence, "弱先验应该产生更高置信度"
    print("✅ 先验强度影响测试通过")

async def test_convergence_info(algorithm):
    """测试收敛信息"""
    print("\n📈 测试收敛信息...")
    
    from consensus_models import ConsensusInput
    
    # 创建高置信度输入
    high_confidence_inputs = [
        ConsensusInput(agent_id="expert1", position=7.5, confidence=0.9),
        ConsensusInput(agent_id="expert2", position=7.8, confidence=0.8),
        ConsensusInput(agent_id="expert3", position=7.6, confidence=0.85)
    ]
    
    # 创建低置信度输入
    low_confidence_inputs = [
        ConsensusInput(agent_id="novice1", position=6.0, confidence=0.3),
        ConsensusInput(agent_id="novice2", position=9.0, confidence=0.2)
    ]
    
    high_conv_info = algorithm.get_convergence_info(high_confidence_inputs)
    low_conv_info = algorithm.get_convergence_info(low_confidence_inputs)
    
    print(f"   高置信度收敛: {high_conv_info['convergence_possible']}")
    print(f"   有效样本大小: {high_conv_info['effective_sample_size']:.2f}")
    print(f"   低置信度收敛: {low_conv_info['convergence_possible']}")
    
    assert high_conv_info["convergence_possible"], "高置信度输入应该能收敛"
    assert high_conv_info["effective_sample_size"] > low_conv_info["effective_sample_size"], "高置信度应该有更大的有效样本"
    print("✅ 收敛信息测试通过")

async def test_edge_cases():
    """测试边界情况"""
    print("\n⚠️ 测试边界情况...")
    
    from bayesian_algorithm import BayesianAlgorithm
    from consensus_algorithm_interface import ConsensusContext
    from consensus_models import ConsensusInput
    
    algorithm = BayesianAlgorithm()
    
    # 测试单个输入
    single_input = [ConsensusInput(agent_id="alone", position=5.0, confidence=0.8)]
    context = ConsensusContext()
    
    result = await algorithm.calculate(single_input, context)
    assert result.consensus_value == 5.0, "单输入应该返回原值"
    print("✅ 单输入测试通过")
    
    # 测试相同值输入
    same_value_inputs = [
        ConsensusInput(agent_id="agent1", position=7.0, confidence=0.8),
        ConsensusInput(agent_id="agent2", position=7.0, confidence=0.6),
        ConsensusInput(agent_id="agent3", position=7.0, confidence=0.9)
    ]
    
    validation = algorithm.validate_inputs(same_value_inputs)
    # 应该有警告但仍然有效
    assert validation.is_valid, "相同值输入应该有效"
    print("✅ 相同值输入测试通过")
    
    # 测试低置信度输入
    low_confidence_inputs = [
        ConsensusInput(agent_id="uncertain1", position="A", confidence=0.1),
        ConsensusInput(agent_id="uncertain2", position="B", confidence=0.2)
    ]
    
    validation = algorithm.validate_inputs(low_confidence_inputs)
    assert len(validation.warnings) > 0, "低置信度应该产生警告"
    print("✅ 低置信度警告测试通过")
    
    # 测试配置验证
    bad_config = {"prior_strength": -1.0}
    validation = algorithm.validate_configuration(bad_config)
    assert not validation.is_valid, "负先验强度应该验证失败"
    print("✅ 配置验证测试通过")

async def test_health_and_performance():
    """测试健康状态和性能"""
    print("\n🏥 测试健康状态和性能...")
    
    from bayesian_algorithm import BayesianAlgorithm
    from consensus_models import ConsensusInput, ConsensusRequest
    
    algorithm = BayesianAlgorithm()
    
    # 测试健康状态
    health = algorithm.get_health_status()
    assert health["status"] == "healthy", "健康状态应该正常"
    assert health["bayesian_properties"]["probabilistic_output"], "应该支持概率输出"
    print("✅ 健康状态检查通过")
    
    # 测试执行时间估算
    request = ConsensusRequest(
        inputs=[
            ConsensusInput(agent_id="test1", position=1.0, confidence=0.8),
            ConsensusInput(agent_id="test2", position=2.0, confidence=0.7),
            ConsensusInput(agent_id="test3", position=1.5, confidence=0.9)
        ]
    )
    
    estimated_time = algorithm.estimate_execution_time(request)
    assert estimated_time > 0, "执行时间估算应该大于0"
    print(f"✅ 执行时间估算: {estimated_time:.3f}秒")

if __name__ == "__main__":
    asyncio.run(test_bayesian_algorithm())
    asyncio.run(test_edge_cases())
    asyncio.run(test_health_and_performance())