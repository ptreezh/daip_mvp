#!/usr/bin/env python3
"""统一共识调度器核心数据模型集成测试

验证所有组件的集成工作情况，确保满足任务要求。
"""

import sys
import traceback
<<<<<<< HEAD
from typing import List
=======
>>>>>>> feature/core-services-refactor

from consensus_algorithm_interface import AlgorithmCapabilities, ConsensusAlgorithm, ConsensusContext
from consensus_models import (
    AlgorithmMetadata,
    AlgorithmType,
    ConsensusInput,
    ConsensusRequest,
    ConsensusResponse,
    ConsensusResult,
    QualityRequirements,
    ValidationResult,
)
from consensus_validation import ConsensusDataSerializer, ConsensusDataValidator


class MockConsensusAlgorithm(ConsensusAlgorithm):
    """模拟共识算法用于测试"""
<<<<<<< HEAD

    def __init__(self):
        super().__init__("mock_algorithm", {"test_param": "test_value"})

    async def calculate(self, inputs: List[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
=======
    
    def __init__(self):
        super().__init__("mock_algorithm", {"test_param": "test_value"})
        
    async def calculate(self, inputs: list[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
>>>>>>> feature/core-services-refactor
        """模拟共识计算"""
        # 简单的多数投票逻辑
        positions = [inp.position for inp in inputs]
        if isinstance(positions[0], str):
            # 字符串类型，找最常见的
            from collections import Counter
            counter = Counter(positions)
            consensus_value = counter.most_common(1)[0][0]
        else:
            # 数值类型，计算平均值
            consensus_value = sum(positions) / len(positions)
<<<<<<< HEAD

        # 计算平均置信度
        avg_confidence = sum(inp.confidence for inp in inputs) / len(inputs)

=======
            
        # 计算平均置信度
        avg_confidence = sum(inp.confidence for inp in inputs) / len(inputs)
        
>>>>>>> feature/core-services-refactor
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=avg_confidence,
            participants=[inp.agent_id for inp in inputs],
            reasoning_trace={"method": "mock_majority_vote"},
            metadata={"algorithm": "mock", "input_count": len(inputs)}
        )
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    def get_metadata(self) -> AlgorithmMetadata:
        """获取算法元数据"""
        return AlgorithmMetadata(
            name="模拟共识算法",
            version="1.0.0",
            description="用于测试的模拟算法",
            algorithm_type=AlgorithmType.SIMPLE_MAJORITY,
            input_types=["str", "float", "int"],
            output_types=["str", "float"],
            complexity="low",
            accuracy=0.8,
            performance="fast",
            requirements=[],
            configuration_schema={"test_param": {"type": "string"}}
        )
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    def get_capabilities(self) -> AlgorithmCapabilities:
        """获取算法能力"""
        return AlgorithmCapabilities(
            supported_input_types={"str", "float", "int"},
            supported_output_types={"str", "float"},
            requires_reasoning=False,
            requires_evidence=False,
            supports_async=True,
            min_participants=1,
            max_participants=100
        )
<<<<<<< HEAD

    def validate_inputs(self, inputs: List[ConsensusInput]) -> ValidationResult:
=======
        
    def validate_inputs(self, inputs: list[ConsensusInput]) -> ValidationResult:
>>>>>>> feature/core-services-refactor
        """验证输入"""
        if not inputs:
            return ValidationResult(is_valid=False, errors=["输入列表为空"])
        return ValidationResult(is_valid=True)


def test_complete_workflow():
    """测试完整的工作流程"""
    print("🔄 测试完整工作流程...")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    try:
        # 1. 创建测试数据
        inputs = [
            ConsensusInput(
                agent_id="agent_001",
                position="支持提案A",
                confidence=0.8,
                reasoning="基于历史数据分析",
                evidence=["数据点1", "数据点2"]
            ),
            ConsensusInput(
<<<<<<< HEAD
                agent_id="agent_002",
=======
                agent_id="agent_002", 
>>>>>>> feature/core-services-refactor
                position="支持提案A",
                confidence=0.7,
                reasoning="符合业务需求",
                evidence=["需求文档"]
            ),
            ConsensusInput(
                agent_id="agent_003",
<<<<<<< HEAD
                position="反对提案A",
=======
                position="反对提案A", 
>>>>>>> feature/core-services-refactor
                confidence=0.6,
                reasoning="成本过高",
                evidence=["成本分析"]
            )
        ]
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 2. 创建共识请求
        request = ConsensusRequest(
            inputs=inputs,
            algorithm_preference="mock_algorithm",
            timeout=30.0,
            quality_requirements=QualityRequirements(min_confidence=0.6)
        )
<<<<<<< HEAD

        print("✅ 测试数据创建成功")

        # 3. 验证请求数据
        validator = ConsensusDataValidator()
        validation_result = validator.validate_consensus_request(request.dict())

        if not validation_result.is_valid:
            print(f"❌ 请求验证失败: {validation_result.errors}")
            return False

        print("✅ 请求数据验证通过")

=======
        
        print("✅ 测试数据创建成功")
        
        # 3. 验证请求数据
        validator = ConsensusDataValidator()
        validation_result = validator.validate_consensus_request(request.dict())
        
        if not validation_result.is_valid:
            print(f"❌ 请求验证失败: {validation_result.errors}")
            return False
            
        print("✅ 请求数据验证通过")
        
>>>>>>> feature/core-services-refactor
        # 4. 测试算法接口
        algorithm = MockConsensusAlgorithm()
        context = ConsensusContext(
            session_id="test_session",
            services={},
            configuration={}
        )
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 检查算法能力
        capabilities = algorithm.get_capabilities()
        if not capabilities.can_handle_request(request):
            print("❌ 算法无法处理请求")
            return False
<<<<<<< HEAD

        print("✅ 算法能力检查通过")

        # 5. 执行共识计算
        import asyncio
        result = asyncio.run(algorithm.calculate(inputs, context))

        if not result:
            print("❌ 共识计算失败")
            return False

        print(f"✅ 共识计算成功: {result.consensus_value} (置信度: {result.confidence:.2f})")

=======
            
        print("✅ 算法能力检查通过")
        
        # 5. 执行共识计算
        import asyncio
        result = asyncio.run(algorithm.calculate(inputs, context))
        
        if not result:
            print("❌ 共识计算失败")
            return False
            
        print(f"✅ 共识计算成功: {result.consensus_value} (置信度: {result.confidence:.2f})")
        
>>>>>>> feature/core-services-refactor
        # 6. 创建响应
        response = ConsensusResponse(
            success=True,
            result=result,
            algorithm_used="mock_algorithm",
            execution_time=1.5,
            fallback_used=False
        )
<<<<<<< HEAD

        print("✅ 响应创建成功")

=======
        
        print("✅ 响应创建成功")
        
>>>>>>> feature/core-services-refactor
        # 7. 测试序列化
        serializer = ConsensusDataSerializer()
        json_str = serializer.serialize_to_json(response)
        deserialized_response = serializer.deserialize_from_json(json_str, ConsensusResponse)
<<<<<<< HEAD

        if deserialized_response.success != response.success:
            print("❌ 序列化测试失败")
            return False

        print("✅ 序列化测试通过")

        return True

=======
        
        if deserialized_response.success != response.success:
            print("❌ 序列化测试失败")
            return False
            
        print("✅ 序列化测试通过")
        
        return True
        
>>>>>>> feature/core-services-refactor
    except Exception as e:
        print(f"❌ 工作流程测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_data_validation_edge_cases():
    """测试数据验证边界情况"""
    print("🧪 测试数据验证边界情况...")
<<<<<<< HEAD

    validator = ConsensusDataValidator()

=======
    
    validator = ConsensusDataValidator()
    
>>>>>>> feature/core-services-refactor
    # 测试空输入
    empty_request = {"inputs": []}
    result = validator.validate_consensus_request(empty_request)
    if result.is_valid:
        print("❌ 空输入验证应该失败")
        return False
    print("✅ 空输入验证正确失败")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    # 测试置信度边界
    invalid_confidence_input = {
        "agent_id": "test",
        "position": "test",
        "confidence": 1.5  # 超出范围
    }
    result = validator.validate_consensus_input(invalid_confidence_input)
    if result.is_valid:
        print("❌ 无效置信度验证应该失败")
        return False
    print("✅ 无效置信度验证正确失败")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    # 测试超时时间
    invalid_timeout_request = {
        "inputs": [{"agent_id": "test", "position": "test", "confidence": 0.5}],
        "timeout": -1  # 负数
    }
    result = validator.validate_consensus_request(invalid_timeout_request)
    if result.is_valid:
        print("❌ 无效超时时间验证应该失败")
        return False
    print("✅ 无效超时时间验证正确失败")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    return True


def test_legacy_format_conversion():
    """测试旧格式转换"""
    print("🔄 测试旧格式转换...")
<<<<<<< HEAD

    serializer = ConsensusDataSerializer()

=======
    
    serializer = ConsensusDataSerializer()
    
>>>>>>> feature/core-services-refactor
    # 测试DebateTurn格式转换
    debate_turn = {
        "role_id": "expert_001",
        "opinion": "我支持这个提案",
        "round": 1
    }
<<<<<<< HEAD

    try:
        converted = serializer.convert_legacy_format(debate_turn, "debate_turn")

        if converted["agent_id"] != "expert_001":
            print("❌ DebateTurn转换失败: agent_id不正确")
            return False

        if converted["position"] != "我支持这个提案":
            print("❌ DebateTurn转换失败: position不正确")
            return False

        print("✅ DebateTurn格式转换成功")

    except Exception as e:
        print(f"❌ DebateTurn转换失败: {str(e)}")
        return False

=======
    
    try:
        converted = serializer.convert_legacy_format(debate_turn, "debate_turn")
        
        if converted["agent_id"] != "expert_001":
            print("❌ DebateTurn转换失败: agent_id不正确")
            return False
            
        if converted["position"] != "我支持这个提案":
            print("❌ DebateTurn转换失败: position不正确")
            return False
            
        print("✅ DebateTurn格式转换成功")
        
    except Exception as e:
        print(f"❌ DebateTurn转换失败: {str(e)}")
        return False
    
>>>>>>> feature/core-services-refactor
    # 测试AdvancedConsensusInput格式转换
    advanced_input = {
        "agent_id": "agent_001",
        "position": "支持",
        "confidence": 0.9,
        "reasoning": "详细分析",
        "evidence": ["证据1"],
        "cognitive_profile": {"expertise": "high"}
    }
<<<<<<< HEAD

    try:
        converted = serializer.convert_legacy_format(advanced_input, "advanced_consensus_input")

        if converted["agent_id"] != "agent_001":
            print("❌ AdvancedConsensusInput转换失败: agent_id不正确")
            return False

        if converted["confidence"] != 0.9:
            print("❌ AdvancedConsensusInput转换失败: confidence不正确")
            return False

        print("✅ AdvancedConsensusInput格式转换成功")

    except Exception as e:
        print(f"❌ AdvancedConsensusInput转换失败: {str(e)}")
        return False

=======
    
    try:
        converted = serializer.convert_legacy_format(advanced_input, "advanced_consensus_input")
        
        if converted["agent_id"] != "agent_001":
            print("❌ AdvancedConsensusInput转换失败: agent_id不正确")
            return False
            
        if converted["confidence"] != 0.9:
            print("❌ AdvancedConsensusInput转换失败: confidence不正确")
            return False
            
        print("✅ AdvancedConsensusInput格式转换成功")
        
    except Exception as e:
        print(f"❌ AdvancedConsensusInput转换失败: {str(e)}")
        return False
    
>>>>>>> feature/core-services-refactor
    return True


def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始综合集成测试...\n")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    tests = [
        ("完整工作流程", test_complete_workflow),
        ("数据验证边界情况", test_data_validation_edge_cases),
        ("旧格式转换", test_legacy_format_conversion)
    ]
<<<<<<< HEAD

    passed = 0
    failed = 0

=======
    
    passed = 0
    failed = 0
    
>>>>>>> feature/core-services-refactor
    for test_name, test_func in tests:
        print(f"📋 运行测试: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} 通过\n")
                passed += 1
            else:
                print(f"❌ {test_name} 失败\n")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}\n")
            failed += 1
<<<<<<< HEAD

    print("=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")

=======
    
    print("=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
>>>>>>> feature/core-services-refactor
    if failed == 0:
        print("🎉 所有集成测试通过!")
        print("\n📋 任务1完成情况:")
        print("- ✅ 统一数据模型类 (ConsensusRequest, ConsensusResponse, ConsensusInput等)")
        print("- ✅ 抽象ConsensusAlgorithm基类接口")
        print("- ✅ 算法元数据和配置结构")
        print("- ✅ 数据验证和序列化逻辑")
        print("- ✅ 向后兼容性支持")
        print("\n🚀 任务1实现完成，满足所有需求!")
        return True
    else:
        print("❌ 部分测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
<<<<<<< HEAD
    sys.exit(0 if success else 1)
=======
    sys.exit(0 if success else 1)
>>>>>>> feature/core-services-refactor
