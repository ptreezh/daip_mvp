#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单多数投票算法测试

测试SimpleMajorityAlgorithm的各种功能和边界情况。
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

async def test_simple_majority_algorithm():
    """测试简单多数投票算法"""
    print("🧪 测试简单多数投票算法...")
    
    try:
        from simple_majority_algorithm import SimpleMajorityAlgorithm
        from consensus_algorithm_interface import ConsensusContext
        from consensus_models import ConsensusInput, ConsensusRequest
        
        # 创建算法实例
        algorithm = SimpleMajorityAlgorithm()
        print("✅ 算法实例创建成功")
        
        # 测试元数据
        metadata = algorithm.get_metadata()
        print(f"✅ 算法元数据: {metadata.name} v{metadata.version}")
        
        # 测试能力描述
        capabilities = algorithm.get_capabilities()
        print(f"✅ 算法能力: 支持{len(capabilities.supported_input_types)}种输入类型")
        
        # 测试分类共识
        await test_categorical_consensus(algorithm)
        
        # 测试数值共识
        await test_numerical_consensus(algorithm)
        
        # 测试复杂类型共识
        await test_complex_consensus(algorithm)
        
        # 测试边界情况
        await test_edge_cases(algorithm)
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_categorical_consensus(algorithm):
    """测试分类共识"""
    print("\n📊 测试分类共识...")
    
    from consensus_models import ConsensusInput
    from consensus_algorithm_interface import ConsensusContext
    
    # 创建测试输入
    inputs = [
        ConsensusInput(agent_id="agent1", position="选项A", confidence=0.8),
        ConsensusInput(agent_id="agent2", position="选项A", confidence=0.9),
        ConsensusInput(agent_id="agent3", position="选项B", confidence=0.7),
        ConsensusInput(agent_id="agent4", position="选项A", confidence=0.6)
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    print(f"   共识结果: {result.consensus_value}")
    print(f"   置信度: {result.confidence:.3f}")
    print(f"   参与者: {len(result.participants)}")
    
    assert result.consensus_value == "选项A", "分类共识结果错误"
    assert result.confidence > 0.5, "置信度过低"
    print("✅ 分类共识测试通过")

async def test_numerical_consensus(algorithm):
    """测试数值共识"""
    print("\n🔢 测试数值共识...")
    
    from consensus_models import ConsensusInput
    from consensus_algorithm_interface import ConsensusContext
    
    # 创建测试输入
    inputs = [
        ConsensusInput(agent_id="agent1", position=8.5, confidence=0.8),
        ConsensusInput(agent_id="agent2", position=7.2, confidence=0.9),
        ConsensusInput(agent_id="agent3", position=8.0, confidence=0.7),
        ConsensusInput(agent_id="agent4", position=7.8, confidence=0.6)
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    print(f"   共识结果: {result.consensus_value:.2f}")
    print(f"   置信度: {result.confidence:.3f}")
    
    expected_mean = (8.5 + 7.2 + 8.0 + 7.8) / 4
    assert abs(result.consensus_value - expected_mean) < 0.01, "数值共识结果错误"
    print("✅ 数值共识测试通过")

async def test_complex_consensus(algorithm):
    """测试复杂类型共识"""
    print("\n🔧 测试复杂类型共识...")
    
    from consensus_models import ConsensusInput
    from consensus_algorithm_interface import ConsensusContext
    
    # 创建测试输入
    inputs = [
        ConsensusInput(agent_id="agent1", position={"choice": "A", "score": 8}, confidence=0.8),
        ConsensusInput(agent_id="agent2", position={"choice": "A", "score": 8}, confidence=0.9),
        ConsensusInput(agent_id="agent3", position={"choice": "B", "score": 7}, confidence=0.7)
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    print(f"   共识结果: {result.consensus_value}")
    print(f"   置信度: {result.confidence:.3f}")
    
    # 复杂类型应该选择出现次数最多的
    assert result.consensus_value == {"choice": "A", "score": 8}, "复杂类型共识结果错误"
    print("✅ 复杂类型共识测试通过")

async def test_edge_cases(algorithm):
    """测试边界情况"""
    print("\n⚠️ 测试边界情况...")
    
    from consensus_models import ConsensusInput
    from consensus_algorithm_interface import ConsensusContext
    
    # 测试单个输入
    single_input = [ConsensusInput(agent_id="agent1", position="唯一选项", confidence=0.8)]
    context = ConsensusContext()
    result = await algorithm.calculate(single_input, context)
    assert result.consensus_value == "唯一选项", "单输入测试失败"
    print("✅ 单输入测试通过")
    
    # 测试平票情况
    tie_inputs = [
        ConsensusInput(agent_id="agent1", position="选项A", confidence=0.8),
        ConsensusInput(agent_id="agent2", position="选项B", confidence=0.8)
    ]
    result = await algorithm.calculate(tie_inputs, context)
    assert result.consensus_value in ["选项A", "选项B"], "平票处理失败"
    print("✅ 平票处理测试通过")
    
    # 测试输入验证
    validation = algorithm.validate_inputs([])
    assert not validation.is_valid, "空输入验证失败"
    print("✅ 输入验证测试通过")

async def test_configuration():
    """测试配置功能"""
    print("\n⚙️ 测试配置功能...")
    
    from simple_majority_algorithm import SimpleMajorityAlgorithm
    
    # 测试自定义配置
    config = {
        "tie_breaking_method": "highest_confidence",
        "min_confidence_threshold": 0.5,
        "numerical_aggregation": "median"
    }
    
    algorithm = SimpleMajorityAlgorithm(config)
    
    # 验证配置
    validation = algorithm.validate_configuration(config)
    assert validation.is_valid, f"配置验证失败: {validation.errors}"
    print("✅ 配置验证通过")
    
    # 测试配置效果
    from consensus_models import ConsensusInput
    from consensus_algorithm_interface import ConsensusContext
    
    inputs = [
        ConsensusInput(agent_id="agent1", position="选项A", confidence=0.9),
        ConsensusInput(agent_id="agent2", position="选项B", confidence=0.6)
    ]
    
    context = ConsensusContext()
    result = await algorithm.calculate(inputs, context)
    
    # 应该选择置信度更高的选项A
    assert result.consensus_value == "选项A", "高置信度平票处理失败"
    print("✅ 配置效果测试通过")

if __name__ == "__main__":
    asyncio.run(test_simple_majority_algorithm())
    asyncio.run(test_configuration())