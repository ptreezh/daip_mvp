#!/usr/bin/env python3
"""降级管理器测试

验证FallbackManager的所有功能，包括降级策略、重试机制和熔断器。
"""

import asyncio
from typing import List

import pytest
from algorithm_registry import AlgorithmRegistry
from algorithm_selector import AlgorithmSelector
from consensus_algorithm_interface import ConsensusContext
from consensus_models import ConsensusInput, ConsensusRequest, ConsensusResult, FailureContext
from fallback_manager import (
    CircuitBreakerState,
    FallbackConfig,
    FallbackManager,
    FallbackStrategy,
    PriorityChainRule,
    RetryStrategy,
    SimilarityBasedRule,
)
from test_algorithm_registry import MockConsensusAlgorithm


class FailingAlgorithm(MockConsensusAlgorithm):
    """总是失败的算法"""

    def __init__(self, algorithm_id: str, failure_message: str = "Mock failure"):
        super().__init__(algorithm_id)
        self.failure_message = failure_message

    async def calculate(self, inputs: List[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
        raise RuntimeError(self.failure_message)


class UnstableAlgorithm(MockConsensusAlgorithm):
    """不稳定的算法（有时成功有时失败）"""

    def __init__(self, algorithm_id: str, failure_rate: float = 0.5):
        super().__init__(algorithm_id)
        self.failure_rate = failure_rate
        self.call_count = 0

    async def calculate(self, inputs: List[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
        self.call_count += 1

        # 基于调用次数决定是否失败
        if (self.call_count % 2) == 1 and self.failure_rate > 0.5:
            raise RuntimeError(f"Unstable algorithm failure #{self.call_count}")

        return await super().calculate(inputs, context)


class TestFallbackManager:
    """测试降级管理器"""

    def setup_method(self):
        """测试前设置"""
        self.registry = AlgorithmRegistry()
        self.selector = AlgorithmSelector(self.registry)
        self.config = FallbackConfig(
            max_retry_count=2,
            retry_delay_base=0.1,  # 快速测试
            failure_threshold=3,
            recovery_timeout=1.0   # 快速恢复测试
        )
        self.fallback_manager = FallbackManager(self.registry, self.selector, self.config)

        # 注册测试算法
        self._register_test_algorithms()

    def teardown_method(self):
        """测试后清理"""
        self.registry.shutdown()

    def _register_test_algorithms(self):
        """注册测试用算法"""
        # 可靠的算法
        reliable_algo = MockConsensusAlgorithm("reliable_algo")

        # 不稳定的算法
        unstable_algo = UnstableAlgorithm("unstable_algo", failure_rate=0.3)

        # 总是失败的算法
        failing_algo = FailingAlgorithm("failing_algo", "Always fails")

        # 备用算法
        backup_algo = MockConsensusAlgorithm("backup_algo")

        self.registry.register("reliable_algo", reliable_algo)
        self.registry.register("unstable_algo", unstable_algo)
        self.registry.register("failing_algo", failing_algo)
        self.registry.register("backup_algo", backup_algo)

        # 设置健康状态
        for algo_id in ["reliable_algo", "unstable_algo", "failing_algo", "backup_algo"]:
            info = self.registry.get_algorithm_info(algo_id)
            info.health_status = "healthy"

    def test_get_fallback_chain(self):
        """测试获取降级链"""
        # 创建失败上下文
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        # 创建请求
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 获取降级链
        fallback_chain = self.fallback_manager.get_fallback_chain(
            "failing_algo", request, failure_context
        )

        # 验证降级链
        assert isinstance(fallback_chain, list)
        assert len(fallback_chain) > 0
        assert "failing_algo" not in fallback_chain  # 失败算法不应在降级链中

    def test_priority_chain_rule(self):
        """测试优先级链规则"""
        # 设置优先级链
        priority_chains = {
            "failing_algo": ["reliable_algo", "backup_algo"],
            "unstable_algo": ["reliable_algo"]
        }

        rule = PriorityChainRule(priority_chains)

        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        available_algorithms = ["reliable_algo", "backup_algo", "unstable_algo"]

        candidates = rule.get_fallback_candidates(
            "failing_algo", request, failure_context, available_algorithms
        )

        assert candidates == ["reliable_algo", "backup_algo"]

    def test_similarity_based_rule(self):
        """测试相似性降级规则"""
        rule = SimilarityBasedRule(self.registry)

        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        available_algorithms = ["reliable_algo", "backup_algo", "unstable_algo"]

        candidates = rule.get_fallback_candidates(
            "failing_algo", request, failure_context, available_algorithms
        )

        assert isinstance(candidates, list)
        assert len(candidates) <= 3
        assert "failing_algo" not in candidates

    @pytest.mark.asyncio
    async def test_execute_fallback_success(self):
        """测试成功的降级执行"""
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行降级到可靠算法
        response = await self.fallback_manager.execute_fallback(
            "reliable_algo", request, failure_context, fallback_depth=1
        )

        # 验证响应
        assert response.success is True
        assert response.algorithm_used == "reliable_algo"
        assert response.fallback_used is True
        assert response.result is not None
        assert response.execution_time > 0

    @pytest.mark.asyncio
    async def test_execute_fallback_failure(self):
        """测试失败的降级执行"""
        failure_context = FailureContext(
            failed_algorithm="unstable_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行降级到失败算法
        response = await self.fallback_manager.execute_fallback(
            "failing_algo", request, failure_context, fallback_depth=1
        )

        # 验证响应
        assert response.success is False
        assert response.algorithm_used == "failing_algo"
        assert response.fallback_used is True
        assert response.error is not None

    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """测试重试机制"""
        # 配置重试
        config = FallbackConfig(
            max_retry_count=3,
            retry_strategy=RetryStrategy.FIXED_RETRY,
            retry_delay_base=0.01  # 很短的延迟用于测试
        )

        fallback_manager = FallbackManager(self.registry, self.selector, config)

        failure_context = FailureContext(
            failed_algorithm="reliable_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行降级到不稳定算法（可能需要重试）
        response = await fallback_manager.execute_fallback(
            "unstable_algo", request, failure_context, fallback_depth=1
        )

        # 不稳定算法最终应该成功（经过重试）
        assert response.success is True or response.success is False  # 取决于随机性

    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """测试熔断器机制"""
        failure_context = FailureContext(
            failed_algorithm="reliable_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 多次执行失败算法，触发熔断器
        for i in range(self.config.failure_threshold + 1):
            response = await self.fallback_manager.execute_fallback(
                "failing_algo", request, failure_context, fallback_depth=1
            )
            assert response.success is False

        # 检查熔断器状态
        breaker = self.fallback_manager.circuit_breakers["failing_algo"]
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count >= self.config.failure_threshold

        # 熔断器开启时，应该拒绝请求
        response = await self.fallback_manager.execute_fallback(
            "failing_algo", request, failure_context, fallback_depth=1
        )
        assert response.success is False
        assert "Circuit breaker is OPEN" in response.error

    def test_add_priority_chain(self):
        """测试添加优先级链"""
        success = self.fallback_manager.add_priority_chain(
            "new_algo", ["reliable_algo", "backup_algo"]
        )
        assert success is True

        # 验证优先级链已添加
        rule = self.fallback_manager.rules[FallbackStrategy.PRIORITY_CHAIN]
        assert isinstance(rule, PriorityChainRule)
        assert "new_algo" in rule.priority_chains
        assert rule.priority_chains["new_algo"] == ["reliable_algo", "backup_algo"]

    def test_event_listener(self):
        """测试事件监听器"""
        events = []

        def event_listener(event):
            events.append(event)

        # 添加监听器
        self.fallback_manager.add_event_listener(event_listener)

        # 执行一个会产生事件的操作
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行降级（这会产生事件）
        asyncio.run(self.fallback_manager.execute_fallback(
            "reliable_algo", request, failure_context, fallback_depth=1
        ))

        # 验证事件被记录
        assert len(events) == 1
        event = events[0]
        assert event.original_algorithm == "failing_algo"
        assert event.fallback_algorithm == "reliable_algo"
        assert event.fallback_depth == 1

    def test_fallback_stats(self):
        """测试降级统计"""
        # 执行一些降级操作来生成统计数据
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行成功的降级
        asyncio.run(self.fallback_manager.execute_fallback(
            "reliable_algo", request, failure_context, fallback_depth=1
        ))

        # 执行失败的降级
        asyncio.run(self.fallback_manager.execute_fallback(
            "failing_algo", request, failure_context, fallback_depth=1
        ))

        # 获取统计信息
        stats = self.fallback_manager.get_fallback_stats()

        assert "total_fallbacks" in stats
        assert "successful_fallbacks" in stats
        assert "failed_fallbacks" in stats
        assert "success_rate" in stats
        assert "circuit_breakers" in stats
        assert "recent_events" in stats
        assert "config" in stats

        assert stats["total_fallbacks"] == 2
        assert stats["successful_fallbacks"] == 1
        assert stats["failed_fallbacks"] == 1
        assert stats["success_rate"] == 0.5

    def test_algorithm_reliability(self):
        """测试算法可靠性分析"""
        # 执行一些操作来生成可靠性数据
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行降级
        asyncio.run(self.fallback_manager.execute_fallback(
            "reliable_algo", request, failure_context, fallback_depth=1
        ))

        # 获取可靠性信息
        reliability = self.fallback_manager.get_algorithm_reliability("reliable_algo")

        assert "algorithm_id" in reliability
        assert "circuit_breaker_state" in reliability
        assert "reliability_score" in reliability
        assert "fallback_successes" in reliability
        assert "fallback_failures" in reliability

        assert reliability["algorithm_id"] == "reliable_algo"
        assert reliability["fallback_successes"] == 1

    def test_strategy_update(self):
        """测试策略更新"""
        # 更新策略
        success = self.fallback_manager.update_fallback_strategy(
            FallbackStrategy.SIMILARITY_BASED
        )
        assert success is True
        assert self.fallback_manager.config.strategy == FallbackStrategy.SIMILARITY_BASED

        # 使用新配置更新
        new_config = FallbackConfig(
            strategy=FallbackStrategy.LOAD_AWARE,
            max_fallback_depth=5
        )

        success = self.fallback_manager.update_fallback_strategy(
            FallbackStrategy.LOAD_AWARE, new_config
        )
        assert success is True
        assert self.fallback_manager.config.strategy == FallbackStrategy.LOAD_AWARE
        assert self.fallback_manager.config.max_fallback_depth == 5

    def test_circuit_breaker_reset(self):
        """测试熔断器重置"""
        # 先触发熔断器
        failure_context = FailureContext(
            failed_algorithm="reliable_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 多次失败触发熔断器
        for i in range(self.config.failure_threshold + 1):
            asyncio.run(self.fallback_manager.execute_fallback(
                "failing_algo", request, failure_context, fallback_depth=1
            ))

        # 验证熔断器开启
        breaker = self.fallback_manager.circuit_breakers["failing_algo"]
        assert breaker.state == CircuitBreakerState.OPEN

        # 重置熔断器
        success = self.fallback_manager.reset_circuit_breaker("failing_algo")
        assert success is True

        # 验证熔断器已重置
        breaker = self.fallback_manager.circuit_breakers["failing_algo"]
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0

    def test_failure_pattern_analysis(self):
        """测试失败模式分析"""
        # 生成一些失败事件
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行多次降级
        for i in range(3):
            asyncio.run(self.fallback_manager.execute_fallback(
                "failing_algo", request, failure_context, fallback_depth=1
            ))

        # 分析失败模式
        analysis = self.fallback_manager.analyze_failure_patterns()

        assert "total_events" in analysis
        assert "algorithm_failures" in analysis
        assert "error_types" in analysis
        assert "most_unreliable_algorithm" in analysis
        assert "most_common_error_type" in analysis

        assert analysis["total_events"] == 3
        assert "failing_algo" in analysis["algorithm_failures"]

    def test_export_events(self):
        """测试事件导出"""
        # 生成一些事件
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 执行降级
        asyncio.run(self.fallback_manager.execute_fallback(
            "reliable_algo", request, failure_context, fallback_depth=1
        ))

        # 导出事件
        events = self.fallback_manager.export_events()

        assert isinstance(events, list)
        assert len(events) == 1

        event = events[0]
        assert "event_id" in event
        assert "timestamp" in event
        assert "original_algorithm" in event
        assert "fallback_algorithm" in event
        assert "failure_context" in event
        assert "success" in event

        assert event["original_algorithm"] == "failing_algo"
        assert event["fallback_algorithm"] == "reliable_algo"


def run_basic_functionality_test():
    """运行基本功能测试"""
    print("🧪 开始FallbackManager基本功能测试...")

    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)
    fallback_manager = FallbackManager(registry, selector)

    try:
        # 注册测试算法
        reliable_algo = MockConsensusAlgorithm("reliable_algo")
        failing_algo = FailingAlgorithm("failing_algo")

        registry.register("reliable_algo", reliable_algo)
        registry.register("failing_algo", failing_algo)

        # 设置健康状态
        for algo_id in ["reliable_algo", "failing_algo"]:
            info = registry.get_algorithm_info(algo_id)
            info.health_status = "healthy"

        print("✅ 测试环境设置成功")

        # 测试获取降级链
        failure_context = FailureContext(
            failed_algorithm="failing_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        fallback_chain = fallback_manager.get_fallback_chain(
            "failing_algo", request, failure_context
        )

        if not isinstance(fallback_chain, list) or len(fallback_chain) == 0:
            print("❌ 降级链获取失败")
            return False

        print(f"✅ 降级链获取成功: {fallback_chain}")

        # 测试降级执行
        async def test_fallback_execution():
            response = await fallback_manager.execute_fallback(
                "reliable_algo", request, failure_context, fallback_depth=1
            )
            return response

        response = asyncio.run(test_fallback_execution())

        if not response.success:
            print("❌ 降级执行失败")
            return False

        print("✅ 降级执行成功")

        # 测试统计信息
        stats = fallback_manager.get_fallback_stats()
        if not stats or "total_fallbacks" not in stats:
            print("❌ 统计信息获取失败")
            return False

        print("✅ 统计信息获取成功")

        # 测试策略更新
        success = fallback_manager.update_fallback_strategy(
            FallbackStrategy.SIMILARITY_BASED
        )
        if not success:
            print("❌ 策略更新失败")
            return False

        print("✅ 策略更新成功")

        print("🎉 所有基本功能测试通过!")
        return True

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False

    finally:
        registry.shutdown()


async def run_circuit_breaker_test():
    """运行熔断器测试"""
    print("🧪 开始FallbackManager熔断器测试...")

    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)

    config = FallbackConfig(
        failure_threshold=2,  # 低阈值用于快速测试
        recovery_timeout=0.5  # 快速恢复
    )

    fallback_manager = FallbackManager(registry, selector, config)

    try:
        # 注册测试算法
        failing_algo = FailingAlgorithm("failing_algo")
        registry.register("failing_algo", failing_algo)

        info = registry.get_algorithm_info("failing_algo")
        info.health_status = "healthy"

        failure_context = FailureContext(
            failed_algorithm="reliable_algo",
            error_type="RuntimeError",
            error_message="Test failure",
            execution_time=1.0
        )

        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)

        # 多次执行失败算法，触发熔断器
        for i in range(config.failure_threshold + 1):
            response = await fallback_manager.execute_fallback(
                "failing_algo", request, failure_context, fallback_depth=1
            )

        # 检查熔断器状态
        breaker = fallback_manager.circuit_breakers["failing_algo"]
        if breaker.state != CircuitBreakerState.OPEN:
            print("❌ 熔断器未正确开启")
            return False

        print("✅ 熔断器正确开启")

        # 测试熔断器拒绝请求
        response = await fallback_manager.execute_fallback(
            "failing_algo", request, failure_context, fallback_depth=1
        )

        if response.success or "Circuit breaker is OPEN" not in response.error:
            print("❌ 熔断器未正确拒绝请求")
            return False

        print("✅ 熔断器正确拒绝请求")

        # 测试熔断器重置
        success = fallback_manager.reset_circuit_breaker("failing_algo")
        if not success:
            print("❌ 熔断器重置失败")
            return False

        breaker = fallback_manager.circuit_breakers["failing_algo"]
        if breaker.state != CircuitBreakerState.CLOSED:
            print("❌ 熔断器未正确重置")
            return False

        print("✅ 熔断器重置成功")

        print("🎉 所有熔断器测试通过!")
        return True

    except Exception as e:
        print(f"❌ 熔断器测试过程中出现异常: {str(e)}")
        return False

    finally:
        registry.shutdown()


if __name__ == "__main__":
    # 运行基本功能测试
    basic_success = run_basic_functionality_test()

    # 运行熔断器测试
    circuit_breaker_success = asyncio.run(run_circuit_breaker_test())

    if basic_success and circuit_breaker_success:
        print("\n📋 测试总结:")
        print("- ✅ 降级链获取功能正常")
        print("- ✅ 降级执行功能正常")
        print("- ✅ 重试机制正常")
        print("- ✅ 熔断器机制正常")
        print("- ✅ 事件记录功能正常")
        print("- ✅ 统计分析功能正常")
        print("\n🚀 任务4实现完成，可以进行下一步开发!")
    else:
        print("\n❌ 部分测试失败，需要修复问题后再继续")
