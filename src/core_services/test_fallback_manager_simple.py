#!/usr/bin/env python3
"""降级管理器简化测试

按照新规则创建的简化测试，文件长度<400行
"""

import asyncio

from algorithm_registry import AlgorithmRegistry
from algorithm_selector import AlgorithmSelector
from consensus_models import ConsensusInput, ConsensusRequest, FailureContext
from fallback_manager_core import CircuitBreakerState, FallbackConfig, FallbackManager
from fallback_manager_utils import FallbackManagerUtils
from test_algorithm_registry import MockConsensusAlgorithm


class FailingAlgorithm(MockConsensusAlgorithm):
    """总是失败的算法"""

    def __init__(self, algorithm_id: str, failure_message: str = "Mock failure"):
        super().__init__(algorithm_id)
        self.failure_message = failure_message

    async def calculate(self, inputs, context):
        raise RuntimeError(self.failure_message)


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始FallbackManager基本功能测试...")

    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)
    fallback_manager = FallbackManager(registry, selector)
    utils = FallbackManagerUtils(fallback_manager)

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
        stats = utils.get_fallback_stats()
        if not stats or "total_fallbacks" not in stats:
            print("❌ 统计信息获取失败")
            return False

        print("✅ 统计信息获取成功")

        print("🎉 所有基本功能测试通过!")
        return True

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False

    finally:
        registry.shutdown()


async def test_circuit_breaker():
    """测试熔断器功能"""
    print("🧪 开始熔断器测试...")

    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)

    config = FallbackConfig(
        failure_threshold=2,
        recovery_timeout=0.5
    )

    fallback_manager = FallbackManager(registry, selector, config)
    utils = FallbackManagerUtils(fallback_manager)

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
        success = utils.reset_circuit_breaker("failing_algo")
        if not success:
            print("❌ 熔断器重置失败")
            return False

        breaker = fallback_manager.circuit_breakers["failing_algo"]
        if breaker.state != CircuitBreakerState.CLOSED:
            print("❌ 熔断器未正确重置")
            return False

        print("✅ 熔断器重置成功")

        print("🎉 熔断器测试通过!")
        return True

    except Exception as e:
        print(f"❌ 熔断器测试异常: {str(e)}")
        return False

    finally:
        registry.shutdown()


def test_event_handling():
    """测试事件处理"""
    print("🧪 开始事件处理测试...")

    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)
    fallback_manager = FallbackManager(registry, selector)
    utils = FallbackManagerUtils(fallback_manager)

    events = []

    def event_listener(event):
        events.append(event)

    try:
        # 添加事件监听器
        utils.add_event_listener(event_listener)

        # 注册算法
        reliable_algo = MockConsensusAlgorithm("reliable_algo")
        registry.register("reliable_algo", reliable_algo)

        info = registry.get_algorithm_info("reliable_algo")
        info.health_status = "healthy"

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
        asyncio.run(fallback_manager.execute_fallback(
            "reliable_algo", request, failure_context, fallback_depth=1
        ))

        # 验证事件
        if len(events) != 1:
            print("❌ 事件记录失败")
            return False

        event = events[0]
        if (event.original_algorithm != "failing_algo" or
            event.fallback_algorithm != "reliable_algo"):
            print("❌ 事件内容错误")
            return False

        print("✅ 事件处理正常")

        # 测试事件导出
        exported = utils.export_events()
        if len(exported) != 1:
            print("❌ 事件导出失败")
            return False

        print("✅ 事件导出正常")

        print("🎉 事件处理测试通过!")
        return True

    except Exception as e:
        print(f"❌ 事件处理测试异常: {str(e)}")
        return False

    finally:
        registry.shutdown()


if __name__ == "__main__":
    # 运行所有测试
    basic_success = test_basic_functionality()
    circuit_breaker_success = asyncio.run(test_circuit_breaker())
    event_success = test_event_handling()

    if basic_success and circuit_breaker_success and event_success:
        print("\n📋 测试总结:")
        print("- ✅ 基本功能正常")
        print("- ✅ 熔断器机制正常")
        print("- ✅ 事件处理正常")
        print("\n🚀 任务4实现完成!")
    else:
        print("\n❌ 部分测试失败")
