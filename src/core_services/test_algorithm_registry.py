#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算法注册表测试

验证AlgorithmRegistry的所有功能，包括注册、发现、验证和健康检查。
"""

import asyncio
import pytest
from datetime import datetime
from typing import List, Dict, Any

from consensus_models import (
    ConsensusInput, ConsensusResult, AlgorithmMetadata, 
    ValidationResult, AlgorithmType
)
from consensus_algorithm_interface import (
    ConsensusAlgorithm, ConsensusContext, AlgorithmCapabilities
)
from algorithm_registry import AlgorithmRegistry, AlgorithmInfo, RegistryStats


class MockConsensusAlgorithm(ConsensusAlgorithm):
    """模拟共识算法用于测试"""
    
    def __init__(self, algorithm_id: str, should_fail: bool = False):
        super().__init__(algorithm_id, {})
        self.should_fail = should_fail
        self.calculate_called = False
        
    async def calculate(self, inputs: List[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
        """模拟共识计算"""
        self.calculate_called = True
        
        if self.should_fail:
            raise RuntimeError("Mock algorithm failure")
            
        # 简单的多数投票
        positions = [inp.position for inp in inputs]
        if isinstance(positions[0], str):
            from collections import Counter
            counter = Counter(positions)
            consensus_value = counter.most_common(1)[0][0]
        else:
            consensus_value = sum(positions) / len(positions)
            
        avg_confidence = sum(inp.confidence for inp in inputs) / len(inputs)
        
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=avg_confidence,
            participants=[inp.agent_id for inp in inputs],
            reasoning_trace={"method": "mock_majority"},
            metadata={"algorithm": self.algorithm_id}
        )
        
    def get_metadata(self) -> AlgorithmMetadata:
        """获取算法元数据"""
        return AlgorithmMetadata(
            name=f"Mock Algorithm {self.algorithm_id}",
            version="1.0.0",
            description="Mock algorithm for testing",
            algorithm_type=AlgorithmType.SIMPLE_MAJORITY,
            input_types=["str", "float"],
            output_types=["str", "float"],
            complexity="low",
            accuracy=0.8,
            performance="fast",
            requirements=[],
            configuration_schema={}
        )
        
    def get_capabilities(self) -> AlgorithmCapabilities:
        """获取算法能力"""
        return AlgorithmCapabilities(
            supported_input_types={"str", "float"},
            supported_output_types={"str", "float"},
            requires_reasoning=False,
            requires_evidence=False,
            supports_async=True,
            min_participants=1,
            max_participants=100
        )
        
    def validate_inputs(self, inputs: List[ConsensusInput]) -> ValidationResult:
        """验证输入"""
        if not inputs:
            return ValidationResult(is_valid=False, errors=["Empty inputs"])
        return ValidationResult(is_valid=True)
        
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        if self.should_fail:
            return {"status": "unhealthy", "reason": "Mock failure"}
        return {"status": "healthy"}


class TestAlgorithmRegistry:
    """测试算法注册表"""
    
    def setup_method(self):
        """测试前设置"""
        self.registry = AlgorithmRegistry(health_check_interval=1)  # 1秒间隔用于测试
        
    def teardown_method(self):
        """测试后清理"""
        self.registry.shutdown()
        
    def test_register_algorithm(self):
        """测试算法注册"""
        algorithm = MockConsensusAlgorithm("test_algo")
        
        # 注册算法
        success = self.registry.register("test_algo", algorithm)
        assert success is True
        
        # 验证算法已注册
        assert "test_algo" in self.registry
        assert len(self.registry) == 1
        
        # 获取算法
        retrieved_algorithm = self.registry.get_algorithm("test_algo")
        assert retrieved_algorithm is algorithm
        
    def test_register_duplicate_algorithm(self):
        """测试重复注册算法"""
        algorithm1 = MockConsensusAlgorithm("test_algo")
        algorithm2 = MockConsensusAlgorithm("test_algo")
        
        # 首次注册
        success1 = self.registry.register("test_algo", algorithm1)
        assert success1 is True
        
        # 重复注册（应该更新）
        success2 = self.registry.register("test_algo", algorithm2)
        assert success2 is True
        
        # 验证算法已更新
        retrieved_algorithm = self.registry.get_algorithm("test_algo")
        assert retrieved_algorithm is algorithm2
        
    def test_unregister_algorithm(self):
        """测试算法注销"""
        algorithm = MockConsensusAlgorithm("test_algo")
        
        # 注册算法
        self.registry.register("test_algo", algorithm)
        assert "test_algo" in self.registry
        
        # 注销算法
        success = self.registry.unregister("test_algo")
        assert success is True
        assert "test_algo" not in self.registry
        assert len(self.registry) == 0
        
        # 注销不存在的算法
        success = self.registry.unregister("nonexistent")
        assert success is False
        
    def test_list_algorithms(self):
        """测试列出算法"""
        # 注册多个算法
        algo1 = MockConsensusAlgorithm("algo1")
        algo2 = MockConsensusAlgorithm("algo2")
        
        self.registry.register("algo1", algo1)
        self.registry.register("algo2", algo2)
        
        # 列出所有算法
        algorithms = self.registry.list_algorithms()
        assert len(algorithms) == 2
        
        algorithm_ids = [info.algorithm_id for info in algorithms]
        assert "algo1" in algorithm_ids
        assert "algo2" in algorithm_ids
        
        # 获取算法ID列表
        ids = self.registry.get_algorithm_ids()
        assert set(ids) == {"algo1", "algo2"}
        
    def test_algorithm_validation(self):
        """测试算法验证"""
        # 有效算法
        valid_algorithm = MockConsensusAlgorithm("valid")
        result = self.registry.validate_algorithm(valid_algorithm)
        assert result.is_valid is True
        assert len(result.errors) == 0
        
        # 无效算法（缺少方法）
        class InvalidAlgorithm:
            pass
            
        invalid_algorithm = InvalidAlgorithm()
        result = self.registry.validate_algorithm(invalid_algorithm)
        assert result.is_valid is False
        assert len(result.errors) > 0
        
    def test_find_algorithms_by_capability(self):
        """测试根据能力查找算法"""
        # 创建不同能力的算法
        class SpecialAlgorithm(MockConsensusAlgorithm):
            def get_capabilities(self):
                return AlgorithmCapabilities(
                    supported_input_types={"str"},
                    supported_output_types={"str"},
                    requires_reasoning=True,
                    requires_evidence=True,
                    supports_async=True,
                    min_participants=2,
                    max_participants=10
                )
                
        normal_algo = MockConsensusAlgorithm("normal")
        special_algo = SpecialAlgorithm("special")
        
        self.registry.register("normal", normal_algo)
        self.registry.register("special", special_algo)
        
        # 查找支持字符串输入的算法
        str_algorithms = self.registry.find_algorithms_by_capability(
            input_types={"str"}
        )
        assert set(str_algorithms) == {"normal", "special"}
        
        # 查找需要推理的算法
        reasoning_algorithms = self.registry.find_algorithms_by_capability(
            requires_reasoning=True
        )
        assert reasoning_algorithms == ["special"]
        
        # 查找最小参与者数量为1的算法
        min_participant_algorithms = self.registry.find_algorithms_by_capability(
            min_participants=1
        )
        assert "normal" in min_participant_algorithms
        assert "special" not in min_participant_algorithms  # 需要至少2个参与者
        
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        healthy_algo = MockConsensusAlgorithm("healthy", should_fail=False)
        unhealthy_algo = MockConsensusAlgorithm("unhealthy", should_fail=True)
        
        self.registry.register("healthy", healthy_algo)
        self.registry.register("unhealthy", unhealthy_algo)
        
        # 检查单个算法健康状态
        healthy_result = await self.registry.check_algorithm_health("healthy")
        assert healthy_result is True
        
        unhealthy_result = await self.registry.check_algorithm_health("unhealthy")
        assert unhealthy_result is False
        
        # 检查所有算法健康状态
        all_health = await self.registry.check_all_algorithms_health()
        assert all_health["healthy"] is True
        assert all_health["unhealthy"] is False
        
        # 获取健康算法列表
        healthy_algorithms = self.registry.get_healthy_algorithms()
        assert "healthy" in healthy_algorithms
        assert "unhealthy" not in healthy_algorithms
        
    def test_registry_stats(self):
        """测试注册表统计"""
        # 初始状态
        stats = self.registry.get_registry_stats()
        assert stats.total_algorithms == 0
        
        # 注册算法
        algo1 = MockConsensusAlgorithm("algo1")
        algo2 = MockConsensusAlgorithm("algo2")
        
        self.registry.register("algo1", algo1)
        self.registry.register("algo2", algo2)
        
        # 模拟使用
        self.registry.get_algorithm("algo1")
        self.registry.get_algorithm("algo1")
        self.registry.get_algorithm("algo2")
        
        # 检查统计
        stats = self.registry.get_registry_stats()
        assert stats.total_algorithms == 2
        assert stats.total_usage_count == 3
        
    def test_event_listeners(self):
        """测试事件监听器"""
        events = []
        
        def event_listener(event_type: str, algorithm_id: str):
            events.append((event_type, algorithm_id))
            
        # 添加监听器
        self.registry.add_listener(event_listener)
        
        # 注册算法
        algorithm = MockConsensusAlgorithm("test_algo")
        self.registry.register("test_algo", algorithm)
        
        # 注销算法
        self.registry.unregister("test_algo")
        
        # 验证事件
        assert len(events) == 2
        assert events[0] == ("registered", "test_algo")
        assert events[1] == ("unregistered", "test_algo")
        
        # 移除监听器
        self.registry.remove_listener(event_listener)
        
        # 再次注册，应该没有新事件
        self.registry.register("test_algo2", algorithm)
        assert len(events) == 2  # 没有新事件
        
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """测试健康监控"""
        algorithm = MockConsensusAlgorithm("test_algo")
        self.registry.register("test_algo", algorithm)
        
        # 启动健康监控
        await self.registry.start_health_monitoring()
        
        # 等待一次健康检查
        await asyncio.sleep(1.5)
        
        # 检查健康状态已更新
        algorithm_info = self.registry.get_algorithm_info("test_algo")
        assert algorithm_info.last_health_check is not None
        assert algorithm_info.health_status == "healthy"
        
        # 停止健康监控
        await self.registry.stop_health_monitoring()
        
    def test_algorithm_info(self):
        """测试算法信息"""
        algorithm = MockConsensusAlgorithm("test_algo")
        config = {"param1": "value1", "param2": 42}
        
        # 注册带配置的算法
        success = self.registry.register("test_algo", algorithm, configuration=config)
        assert success is True
        
        # 获取算法信息
        info = self.registry.get_algorithm_info("test_algo")
        assert info is not None
        assert info.algorithm_id == "test_algo"
        assert info.algorithm is algorithm
        assert info.configuration == config
        assert info.usage_count == 0
        assert info.health_status == "unknown"
        
        # 使用算法后检查统计
        self.registry.get_algorithm("test_algo")
        info = self.registry.get_algorithm_info("test_algo")
        assert info.usage_count == 1
        assert info.last_used is not None


def run_basic_functionality_test():
    """运行基本功能测试"""
    print("🧪 开始AlgorithmRegistry基本功能测试...")
    
    registry = AlgorithmRegistry()
    
    try:
        # 测试算法注册
        algorithm = MockConsensusAlgorithm("test_algo")
        success = registry.register("test_algo", algorithm)
        if not success:
            print("❌ 算法注册失败")
            return False
        print("✅ 算法注册成功")
        
        # 测试算法获取
        retrieved = registry.get_algorithm("test_algo")
        if retrieved is not algorithm:
            print("❌ 算法获取失败")
            return False
        print("✅ 算法获取成功")
        
        # 测试算法列表
        algorithms = registry.list_algorithms()
        if len(algorithms) != 1:
            print("❌ 算法列表错误")
            return False
        print("✅ 算法列表正确")
        
        # 测试算法验证
        validation_result = registry.validate_algorithm(algorithm)
        if not validation_result.is_valid:
            print(f"❌ 算法验证失败: {validation_result.errors}")
            return False
        print("✅ 算法验证通过")
        
        # 测试能力查找
        matching = registry.find_algorithms_by_capability(input_types={"str"})
        if "test_algo" not in matching:
            print("❌ 能力查找失败")
            return False
        print("✅ 能力查找成功")
        
        # 测试统计信息
        stats = registry.get_registry_stats()
        if stats.total_algorithms != 1:
            print("❌ 统计信息错误")
            return False
        print("✅ 统计信息正确")
        
        print("🎉 所有基本功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False
        
    finally:
        registry.shutdown()


async def run_async_functionality_test():
    """运行异步功能测试"""
    print("🧪 开始AlgorithmRegistry异步功能测试...")
    
    registry = AlgorithmRegistry(health_check_interval=1)
    
    try:
        # 注册算法
        healthy_algo = MockConsensusAlgorithm("healthy", should_fail=False)
        unhealthy_algo = MockConsensusAlgorithm("unhealthy", should_fail=True)
        
        registry.register("healthy", healthy_algo)
        registry.register("unhealthy", unhealthy_algo)
        
        # 测试健康检查
        healthy_result = await registry.check_algorithm_health("healthy")
        if not healthy_result:
            print("❌ 健康算法检查失败")
            return False
        print("✅ 健康算法检查通过")
        
        unhealthy_result = await registry.check_algorithm_health("unhealthy")
        if unhealthy_result:
            print("❌ 不健康算法检查失败")
            return False
        print("✅ 不健康算法检查通过")
        
        # 测试批量健康检查
        all_health = await registry.check_all_algorithms_health()
        if not (all_health["healthy"] and not all_health["unhealthy"]):
            print("❌ 批量健康检查失败")
            return False
        print("✅ 批量健康检查通过")
        
        # 测试健康监控
        await registry.start_health_monitoring()
        await asyncio.sleep(1.5)  # 等待一次健康检查
        await registry.stop_health_monitoring()
        
        # 检查健康状态已更新
        healthy_info = registry.get_algorithm_info("healthy")
        if healthy_info.health_status != "healthy":
            print("❌ 健康监控状态更新失败")
            return False
        print("✅ 健康监控功能正常")
        
        print("🎉 所有异步功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 异步测试过程中出现异常: {str(e)}")
        return False
        
    finally:
        registry.shutdown()


if __name__ == "__main__":
    # 运行基本功能测试
    basic_success = run_basic_functionality_test()
    
    # 运行异步功能测试
    async_success = asyncio.run(run_async_functionality_test())
    
    if basic_success and async_success:
        print("\n📋 测试总结:")
        print("- ✅ 算法注册和注销功能正常")
        print("- ✅ 算法发现和查询功能正常")
        print("- ✅ 算法验证功能正常")
        print("- ✅ 健康检查功能正常")
        print("- ✅ 统计和监控功能正常")
        print("\n🚀 任务2实现完成，可以进行下一步开发!")
    else:
        print("\n❌ 部分测试失败，需要修复问题后再继续")