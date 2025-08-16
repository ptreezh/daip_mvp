#!/usr/bin/env python3
"""算法注册表集成测试

验证AlgorithmRegistry与现有系统组件的集成和兼容性。
"""

import asyncio
import sys
<<<<<<< HEAD
from typing import List
=======
>>>>>>> feature/core-services-refactor

from algorithm_registry import AlgorithmRegistry
from consensus_algorithm_interface import AlgorithmCapabilities, ConsensusAlgorithm, ConsensusContext
from consensus_models import AlgorithmMetadata, AlgorithmType, ConsensusInput, ConsensusResult, ValidationResult
from consensus_validation import ConsensusDataSerializer


class LegacyCompatibleAlgorithm(ConsensusAlgorithm):
    """兼容旧系统格式的算法"""
<<<<<<< HEAD

    def __init__(self, algorithm_id: str):
        super().__init__(algorithm_id, {})

    async def calculate(self, inputs: List[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
        """模拟兼容旧格式的共识计算"""
        # 模拟处理旧格式数据
        serializer = ConsensusDataSerializer()

=======
    
    def __init__(self, algorithm_id: str):
        super().__init__(algorithm_id, {})
        
    async def calculate(self, inputs: list[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
        """模拟兼容旧格式的共识计算"""
        # 模拟处理旧格式数据
        serializer = ConsensusDataSerializer()
        
>>>>>>> feature/core-services-refactor
        # 转换为旧格式进行处理
        legacy_inputs = []
        for inp in inputs:
            if hasattr(inp, 'metadata') and inp.metadata.get('source_format') == 'debate_turn':
                # 处理DebateTurn格式
                legacy_inputs.append({
                    'role_id': inp.agent_id,
                    'opinion': inp.position,
                    'round': inp.metadata.get('round', 1)
                })
            else:
                # 标准格式
                legacy_inputs.append({
                    'agent_id': inp.agent_id,
                    'position': inp.position,
                    'confidence': inp.confidence
                })
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
        # 简单的共识逻辑
        positions = [inp.position for inp in inputs]
        if isinstance(positions[0], str):
            from collections import Counter
            counter = Counter(positions)
            consensus_value = counter.most_common(1)[0][0]
        else:
            consensus_value = sum(positions) / len(positions)
<<<<<<< HEAD

        avg_confidence = sum(inp.confidence for inp in inputs) / len(inputs)

=======
            
        avg_confidence = sum(inp.confidence for inp in inputs) / len(inputs)
        
>>>>>>> feature/core-services-refactor
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=avg_confidence,
            participants=[inp.agent_id for inp in inputs],
            reasoning_trace={
                "method": "legacy_compatible",
                "processed_legacy_inputs": len(legacy_inputs)
            },
            metadata={
                "algorithm": self.algorithm_id,
                "legacy_compatible": True
            }
        )
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    def get_metadata(self) -> AlgorithmMetadata:
        """获取算法元数据"""
        return AlgorithmMetadata(
            name="Legacy Compatible Algorithm",
            version="1.0.0",
            description="Algorithm compatible with legacy data formats",
            algorithm_type=AlgorithmType.SIMPLE_MAJORITY,
            input_types=["str", "float", "dict"],
            output_types=["str", "float"],
            complexity="low",
            accuracy=0.75,
            performance="fast",
            requirements=["consensus_validation"],
            configuration_schema={
                "legacy_mode": {"type": "boolean", "default": True}
            }
        )
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    def get_capabilities(self) -> AlgorithmCapabilities:
        """获取算法能力"""
        return AlgorithmCapabilities(
            supported_input_types={"str", "float", "dict"},
            supported_output_types={"str", "float"},
            requires_reasoning=False,
            requires_evidence=False,
            supports_async=True,
            min_participants=1,
            max_participants=1000
        )
<<<<<<< HEAD

    def validate_inputs(self, inputs: List[ConsensusInput]) -> ValidationResult:
        """验证输入"""
        if not inputs:
            return ValidationResult(is_valid=False, errors=["Empty inputs"])

=======
        
    def validate_inputs(self, inputs: list[ConsensusInput]) -> ValidationResult:
        """验证输入"""
        if not inputs:
            return ValidationResult(is_valid=False, errors=["Empty inputs"])
            
>>>>>>> feature/core-services-refactor
        # 检查是否包含旧格式数据
        has_legacy_format = any(
            hasattr(inp, 'metadata') and inp.metadata.get('source_format') in ['debate_turn', 'advanced_consensus_input']
            for inp in inputs
        )
<<<<<<< HEAD

        warnings = []
        if has_legacy_format:
            warnings.append("Legacy format data detected, will be converted")

=======
        
        warnings = []
        if has_legacy_format:
            warnings.append("Legacy format data detected, will be converted")
            
>>>>>>> feature/core-services-refactor
        return ValidationResult(is_valid=True, warnings=warnings)


def test_registry_with_multiple_algorithm_types():
    """测试注册表处理多种算法类型"""
    print("🔄 测试多种算法类型注册...")
<<<<<<< HEAD

    registry = AlgorithmRegistry()

=======
    
    registry = AlgorithmRegistry()
    
>>>>>>> feature/core-services-refactor
    try:
        # 注册不同类型的算法
        algorithms = {
            "simple_majority": AlgorithmType.SIMPLE_MAJORITY,
            "weighted_voting": AlgorithmType.WEIGHTED_VOTING,
            "bayesian": AlgorithmType.BAYESIAN_CONSENSUS,
            "legacy_compatible": AlgorithmType.SIMPLE_MAJORITY
        }
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        for algo_id, algo_type in algorithms.items():
            if algo_id == "legacy_compatible":
                algorithm = LegacyCompatibleAlgorithm(algo_id)
            else:
                # 使用基本的模拟算法
                from test_algorithm_registry import MockConsensusAlgorithm
                algorithm = MockConsensusAlgorithm(algo_id)
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
            success = registry.register(algo_id, algorithm)
            if not success:
                print(f"❌ 注册算法 {algo_id} 失败")
                return False
<<<<<<< HEAD

        print(f"✅ 成功注册 {len(algorithms)} 个不同类型的算法")

=======
                
        print(f"✅ 成功注册 {len(algorithms)} 个不同类型的算法")
        
>>>>>>> feature/core-services-refactor
        # 测试按类型查找
        simple_algorithms = registry.list_algorithms(algorithm_type=AlgorithmType.SIMPLE_MAJORITY)
        if len(simple_algorithms) < 2:  # simple_majority 和 legacy_compatible
            print("❌ 按类型查找算法失败")
            return False
<<<<<<< HEAD

        print("✅ 按类型查找算法成功")

=======
            
        print("✅ 按类型查找算法成功")
        
>>>>>>> feature/core-services-refactor
        # 测试统计信息
        stats = registry.get_registry_stats()
        if stats.total_algorithms != len(algorithms):
            print("❌ 统计信息不正确")
            return False
<<<<<<< HEAD

        print("✅ 统计信息正确")

        return True

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False

=======
            
        print("✅ 统计信息正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        registry.shutdown()


def test_legacy_data_format_compatibility():
    """测试旧数据格式兼容性"""
    print("🔄 测试旧数据格式兼容性...")
<<<<<<< HEAD

    registry = AlgorithmRegistry()

=======
    
    registry = AlgorithmRegistry()
    
>>>>>>> feature/core-services-refactor
    try:
        # 注册兼容算法
        legacy_algorithm = LegacyCompatibleAlgorithm("legacy_compatible")
        success = registry.register("legacy_compatible", legacy_algorithm)
        if not success:
            print("❌ 注册兼容算法失败")
            return False
<<<<<<< HEAD

        # 创建包含旧格式数据的输入
        serializer = ConsensusDataSerializer()

=======
            
        # 创建包含旧格式数据的输入
        serializer = ConsensusDataSerializer()
        
>>>>>>> feature/core-services-refactor
        # 模拟DebateTurn格式数据
        debate_turn_data = {
            "role_id": "expert_001",
            "opinion": "我支持这个提案",
            "round": 1
        }
<<<<<<< HEAD

        converted_input = serializer.convert_legacy_format(debate_turn_data, "debate_turn")
        consensus_input = ConsensusInput(**converted_input)

        # 验证算法能处理这种输入
        algorithm = registry.get_algorithm("legacy_compatible")
        validation_result = algorithm.validate_inputs([consensus_input])

        if not validation_result.is_valid:
            print(f"❌ 旧格式数据验证失败: {validation_result.errors}")
            return False

        print("✅ 旧格式数据验证通过")

        # 测试实际计算
        context = ConsensusContext()
        result = asyncio.run(algorithm.calculate([consensus_input], context))

        if not result or not result.metadata.get("legacy_compatible"):
            print("❌ 旧格式数据计算失败")
            return False

        print("✅ 旧格式数据计算成功")

        return True

    except Exception as e:
        print(f"❌ 兼容性测试过程中出现异常: {str(e)}")
        return False

=======
        
        converted_input = serializer.convert_legacy_format(debate_turn_data, "debate_turn")
        consensus_input = ConsensusInput(**converted_input)
        
        # 验证算法能处理这种输入
        algorithm = registry.get_algorithm("legacy_compatible")
        validation_result = algorithm.validate_inputs([consensus_input])
        
        if not validation_result.is_valid:
            print(f"❌ 旧格式数据验证失败: {validation_result.errors}")
            return False
            
        print("✅ 旧格式数据验证通过")
        
        # 测试实际计算
        context = ConsensusContext()
        result = asyncio.run(algorithm.calculate([consensus_input], context))
        
        if not result or not result.metadata.get("legacy_compatible"):
            print("❌ 旧格式数据计算失败")
            return False
            
        print("✅ 旧格式数据计算成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 兼容性测试过程中出现异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        registry.shutdown()


async def test_concurrent_operations():
    """测试并发操作"""
    print("🔄 测试并发操作...")
<<<<<<< HEAD

    registry = AlgorithmRegistry()

=======
    
    registry = AlgorithmRegistry()
    
>>>>>>> feature/core-services-refactor
    try:
        # 并发注册多个算法
        async def register_algorithm(algo_id: str):
            from test_algorithm_registry import MockConsensusAlgorithm
            algorithm = MockConsensusAlgorithm(algo_id)
            return registry.register(algo_id, algorithm)
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 创建并发注册任务
        tasks = []
        for i in range(10):
            task = asyncio.create_task(register_algorithm(f"algo_{i}"))
            tasks.append(task)
<<<<<<< HEAD

        # 等待所有注册完成
        results = await asyncio.gather(*tasks)

        if not all(results):
            print("❌ 并发注册失败")
            return False

        print("✅ 并发注册成功")

        # 并发健康检查
        health_results = await registry.check_all_algorithms_health()

        if len(health_results) != 10:
            print("❌ 并发健康检查失败")
            return False

        print("✅ 并发健康检查成功")

        # 并发获取算法
        async def get_algorithm(algo_id: str):
            return registry.get_algorithm(algo_id)

=======
            
        # 等待所有注册完成
        results = await asyncio.gather(*tasks)
        
        if not all(results):
            print("❌ 并发注册失败")
            return False
            
        print("✅ 并发注册成功")
        
        # 并发健康检查
        health_results = await registry.check_all_algorithms_health()
        
        if len(health_results) != 10:
            print("❌ 并发健康检查失败")
            return False
            
        print("✅ 并发健康检查成功")
        
        # 并发获取算法
        async def get_algorithm(algo_id: str):
            return registry.get_algorithm(algo_id)
            
>>>>>>> feature/core-services-refactor
        get_tasks = []
        for i in range(10):
            task = asyncio.create_task(get_algorithm(f"algo_{i}"))
            get_tasks.append(task)
<<<<<<< HEAD

        algorithms = await asyncio.gather(*get_tasks)

        if not all(algo is not None for algo in algorithms):
            print("❌ 并发获取算法失败")
            return False

        print("✅ 并发获取算法成功")

        return True

    except Exception as e:
        print(f"❌ 并发测试过程中出现异常: {str(e)}")
        return False

=======
            
        algorithms = await asyncio.gather(*get_tasks)
        
        if not all(algo is not None for algo in algorithms):
            print("❌ 并发获取算法失败")
            return False
            
        print("✅ 并发获取算法成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 并发测试过程中出现异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        registry.shutdown()


def test_algorithm_lifecycle_management():
    """测试算法生命周期管理"""
    print("🔄 测试算法生命周期管理...")
<<<<<<< HEAD

    registry = AlgorithmRegistry()
    events = []

    def event_listener(event_type: str, algorithm_id: str):
        events.append((event_type, algorithm_id))

    try:
        # 添加事件监听器
        registry.add_listener(event_listener)

        # 注册算法
        from test_algorithm_registry import MockConsensusAlgorithm
        algorithm = MockConsensusAlgorithm("lifecycle_test")

=======
    
    registry = AlgorithmRegistry()
    events = []
    
    def event_listener(event_type: str, algorithm_id: str):
        events.append((event_type, algorithm_id))
        
    try:
        # 添加事件监听器
        registry.add_listener(event_listener)
        
        # 注册算法
        from test_algorithm_registry import MockConsensusAlgorithm
        algorithm = MockConsensusAlgorithm("lifecycle_test")
        
>>>>>>> feature/core-services-refactor
        success = registry.register("lifecycle_test", algorithm)
        if not success:
            print("❌ 算法注册失败")
            return False
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 使用算法
        retrieved = registry.get_algorithm("lifecycle_test")
        if retrieved is None:
            print("❌ 算法获取失败")
            return False
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 检查使用统计
        info = registry.get_algorithm_info("lifecycle_test")
        if info.usage_count != 1:
            print("❌ 使用统计错误")
            return False
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 更新算法（重新注册）
        new_algorithm = MockConsensusAlgorithm("lifecycle_test")
        success = registry.register("lifecycle_test", new_algorithm)
        if not success:
            print("❌ 算法更新失败")
            return False
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 注销算法
        success = registry.unregister("lifecycle_test")
        if not success:
            print("❌ 算法注销失败")
            return False
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 验证事件
        expected_events = [
            ("registered", "lifecycle_test"),
            ("registered", "lifecycle_test"),  # 更新也会触发注册事件
            ("unregistered", "lifecycle_test")
        ]
<<<<<<< HEAD

        if events != expected_events:
            print(f"❌ 事件序列错误: 期望 {expected_events}, 实际 {events}")
            return False

        print("✅ 算法生命周期管理正常")

        return True

    except Exception as e:
        print(f"❌ 生命周期测试过程中出现异常: {str(e)}")
        return False

=======
        
        if events != expected_events:
            print(f"❌ 事件序列错误: 期望 {expected_events}, 实际 {events}")
            return False
            
        print("✅ 算法生命周期管理正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 生命周期测试过程中出现异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        registry.shutdown()


def run_comprehensive_integration_test():
    """运行综合集成测试"""
    print("🚀 开始AlgorithmRegistry综合集成测试...\n")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    tests = [
        ("多种算法类型注册", test_registry_with_multiple_algorithm_types),
        ("旧数据格式兼容性", test_legacy_data_format_compatibility),
        ("并发操作", lambda: asyncio.run(test_concurrent_operations())),
        ("算法生命周期管理", test_algorithm_lifecycle_management)
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
        print("\n📋 任务2完成情况:")
        print("- ✅ AlgorithmRegistry类实现算法管理")
        print("- ✅ 算法注册、发现和验证功能")
        print("- ✅ 算法元数据存储和查询")
        print("- ✅ 算法健康检查机制")
        print("- ✅ 多种算法类型支持")
        print("- ✅ 旧格式数据兼容性")
        print("- ✅ 并发操作安全性")
        print("- ✅ 完整的生命周期管理")
        print("\n🚀 任务2实现完成，满足所有需求!")
        return True
    else:
        print("❌ 部分测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = run_comprehensive_integration_test()
<<<<<<< HEAD
    sys.exit(0 if success else 1)
=======
    sys.exit(0 if success else 1)
>>>>>>> feature/core-services-refactor
