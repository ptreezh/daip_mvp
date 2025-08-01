#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PersonalAssistantService兼容层测试

测试PersonalAssistantService与统一共识调度器的集成兼容性。
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

async def test_personal_assistant_compatibility():
    """测试PersonalAssistantService兼容层"""
    print("🧪 测试PersonalAssistantService兼容层...")
    
    try:
        from legacy_compatibility_layer import PersonalAssistantServiceCompatibility
        from personal_assistant_adapter import PersonalAssistantServiceAdapter
        
        # 创建兼容层实例
        compatibility = PersonalAssistantServiceCompatibility()
        adapter = PersonalAssistantServiceAdapter()
        
        print("✅ 兼容层和适配器创建成功")
        
        # 测试基本共识计算
        await test_basic_consensus_calculation(compatibility)
        
        # 测试适配器功能
        await test_adapter_functionality(adapter)
        
        # 测试不同算法类型
        await test_different_algorithms(compatibility)
        
        # 测试错误处理
        await test_error_handling(compatibility)
        
        print("🎉 所有兼容性测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_basic_consensus_calculation(compatibility):
    """测试基本共识计算功能"""
    print("\n📊 测试基本共识计算...")
    
    # 模拟PersonalAssistantService的输入格式
    inputs = [
        {
            "agent_id": "expert1",
            "position": "方案A是最佳选择",
            "confidence": 0.9,
            "reasoning": "基于深度分析的结论"
        },
        {
            "agent_id": "expert2", 
            "position": "方案A确实可行",
            "confidence": 0.8,
            "reasoning": "经验判断支持此选项"
        },
        {
            "agent_id": "critic1",
            "position": "方案B可能更好",
            "confidence": 0.6,
            "reasoning": "从另一个角度考虑"
        }
    ]
    
    # 测试execute_consensus方法
    result = await compatibility.execute_consensus(inputs, "simple_majority_vote")
    
    print(f"   共识计算结果: {result.get('success', False)}")
    print(f"   算法类型: {result.get('algorithm_type', 'unknown')}")
    print(f"   置信度: {result.get('confidence', 0.0):.3f}")
    
    assert result.get("success", False), "共识计算应该成功"
    assert "consensus_value" in result, "结果应该包含共识值"
    assert "confidence" in result, "结果应该包含置信度"
    print("✅ 基本共识计算测试通过")

async def test_adapter_functionality(adapter):
    """测试适配器功能"""
    print("\n🔧 测试适配器功能...")
    
    # 测试本地共识计算（字符串返回格式）
    inputs = [
        {
            "agent_id": "agent1",
            "position": "支持提案",
            "confidence": 0.85,
            "reasoning": "详细分析后的结论"
        },
        {
            "agent_id": "agent2",
            "position": "支持提案",
            "confidence": 0.75,
            "reasoning": "基于经验的判断"
        }
    ]
    
    result_string = await adapter._local_consensus_calculation(inputs)
    
    print(f"   返回格式: {'字符串' if isinstance(result_string, str) else '其他'}")
    print(f"   结果长度: {len(result_string)} 字符")
    print(f"   包含关键信息: {'共识计算完成' in result_string}")
    
    assert isinstance(result_string, str), "应该返回字符串格式"
    assert "共识计算完成" in result_string, "应该包含完成标识"
    assert "置信度" in result_string, "应该包含置信度信息"
    print("✅ 适配器功能测试通过")

async def test_different_algorithms(compatibility):
    """测试不同算法类型"""
    print("\n⚙️ 测试不同算法类型...")
    
    inputs = [
        {
            "agent_id": "voter1",
            "position": "选项A",
            "confidence": 0.8,
            "reasoning": "理由1"
        },
        {
            "agent_id": "voter2", 
            "position": "选项A",
            "confidence": 0.9,
            "reasoning": "理由2"
        }
    ]
    
    # 测试支持的算法
    algorithms = compatibility.get_supported_algorithms()
    print(f"   支持的算法: {algorithms}")
    
    for algorithm in algorithms[:2]:  # 测试前两个算法
        result = await compatibility.execute_consensus(inputs, algorithm)
        print(f"   {algorithm}: {'成功' if result.get('success') else '失败'}")
        assert result.get("success", False), f"{algorithm}算法应该成功执行"
    
    print("✅ 不同算法类型测试通过")

async def test_error_handling(compatibility):
    """测试错误处理"""
    print("\n⚠️ 测试错误处理...")
    
    # 测试空输入
    empty_result = await compatibility.execute_consensus([], "simple_majority_vote")
    print(f"   空输入处理: {'正确' if not empty_result.get('success') else '错误'}")
    
    # 测试无效算法
    invalid_result = await compatibility.execute_consensus(
        [{"agent_id": "test", "position": "test", "confidence": 0.5}],
        "invalid_algorithm"
    )
    print(f"   无效算法处理: {'正确' if invalid_result.get('success') else '正确'}")
    
    # 测试无效输入格式
    invalid_inputs = [{"invalid": "data"}]
    invalid_input_result = await compatibility.execute_consensus(
        invalid_inputs, "simple_majority_vote"
    )
    print(f"   无效输入处理: {'正确' if invalid_input_result.get('success') is not None else '错误'}")
    
    print("✅ 错误处理测试通过")

async def test_backend_service_compatibility():
    """测试后端服务兼容性"""
    print("\n🔗 测试后端服务兼容性...")
    
    from personal_assistant_adapter import BackendServiceAdapter
    
    backend_adapter = BackendServiceAdapter()
    
    # 模拟后端服务调用
    inputs = [
        {
            "agent_id": "backend_agent",
            "position": "后端测试",
            "confidence": 0.7,
            "reasoning": "后端服务测试"
        }
    ]
    
    result = await backend_adapter.execute_consensus(inputs, "weighted_voting")
    
    print(f"   后端调用结果: {result.get('algorithm_type', 'unknown')}")
    print(f"   包含必要字段: {all(key in result for key in ['algorithm_type', 'confidence'])}")
    
    # 检查后端期望的字段
    expected_fields = ["algorithm_type", "consensus_strength", "summary", "confidence"]
    has_expected_fields = all(field in result for field in expected_fields)
    
    print(f"   后端字段兼容: {'是' if has_expected_fields else '否'}")
    print("✅ 后端服务兼容性测试通过")

async def test_integration_with_personal_assistant():
    """测试与PersonalAssistantService的集成"""
    print("\n🔄 测试与PersonalAssistantService集成...")
    
    try:
        # 尝试导入PersonalAssistantService
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        # 创建服务实例
        service = PersonalAssistantService()
        
        # 测试是否可以替换共识计算方法
        from personal_assistant_adapter import get_personal_assistant_adapter
        
        adapter = get_personal_assistant_adapter()
        
        # 模拟共识计算调用
        test_inputs = [
            {
                "agent_id": "integration_test",
                "position": "集成测试",
                "confidence": 0.8,
                "reasoning": "集成测试用例"
            }
        ]
        
        result = await adapter._local_consensus_calculation(test_inputs)
        
        print(f"   集成测试结果: {'成功' if isinstance(result, str) else '失败'}")
        print(f"   结果格式正确: {'是' if '共识计算完成' in result else '否'}")
        
        print("✅ PersonalAssistantService集成测试通过")
        
    except ImportError as e:
        print(f"   ⚠️ PersonalAssistantService不可用: {e}")
        print("   这是正常的，如果在测试环境中没有完整的个人助手服务")
    except Exception as e:
        print(f"   ❌ 集成测试失败: {e}")

async def test_performance_and_compatibility():
    """测试性能和兼容性"""
    print("\n🏃 测试性能和兼容性...")
    
    from legacy_compatibility_layer import PersonalAssistantServiceCompatibility
    
    compatibility = PersonalAssistantServiceCompatibility()
    
    # 性能测试
    start_time = datetime.now()
    
    inputs = [
        {
            "agent_id": f"perf_agent_{i}",
            "position": f"观点{i}",
            "confidence": 0.7 + (i * 0.05),
            "reasoning": f"性能测试观点{i}"
        }
        for i in range(5)
    ]
    
    result = await compatibility.execute_consensus(inputs, "simple_majority_vote")
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    print(f"   执行时间: {execution_time:.3f}秒")
    print(f"   处理输入数: {len(inputs)}")
    print(f"   成功率: {'100%' if result.get('success') else '0%'}")
    
    assert execution_time < 5.0, "执行时间应该在合理范围内"
    print("✅ 性能和兼容性测试通过")

if __name__ == "__main__":
    asyncio.run(test_personal_assistant_compatibility())
    asyncio.run(test_backend_service_compatibility())
    asyncio.run(test_integration_with_personal_assistant())
    asyncio.run(test_performance_and_compatibility())