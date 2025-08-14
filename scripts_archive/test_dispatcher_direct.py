#!/usr/bin/env python3
"""直接测试统一调度器

直接测试统一调度器的功能，不通过兼容层。
"""

import asyncio
import sys

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

async def test_dispatcher_direct():
    """直接测试统一调度器"""
    print("🧪 直接测试统一调度器...")

    try:
        from consensus_models import ConsensusInput, ConsensusRequest
        from simple_majority_algorithm import SimpleMajorityAlgorithm
        from unified_consensus_dispatcher import UnifiedConsensusDispatcher

        # 创建调度器
        dispatcher = UnifiedConsensusDispatcher()
        print("✅ 调度器创建成功")

        # 手动注册算法
        registry = dispatcher.registry
        simple_majority = SimpleMajorityAlgorithm()
        success = registry.register("simple_majority", simple_majority)
        print(f"   算法注册: {'成功' if success else '失败'}")

        # 检查注册结果
        algorithms = registry.get_algorithm_ids()
        print(f"   已注册算法: {algorithms}")

        # 创建测试请求
        inputs = [
            ConsensusInput(
                agent_id="test1",
                position="选项A",
                confidence=0.8,
                reasoning="测试理由1"
            ),
            ConsensusInput(
                agent_id="test2",
                position="选项A",
                confidence=0.9,
                reasoning="测试理由2"
            )
        ]

        request = ConsensusRequest(
            inputs=inputs,
            algorithm_preference="simple_majority"
        )

        print(f"   测试请求创建成功，输入数量: {len(inputs)}")

        # 执行共识计算
        response = await dispatcher.calculate_consensus(request)

        print(f"   共识计算结果: {'成功' if response.success else '失败'}")
        if response.success:
            print(f"   共识值: {response.result.consensus_value}")
            print(f"   置信度: {response.result.confidence:.3f}")
            print(f"   使用算法: {response.algorithm_used}")
        else:
            print(f"   错误信息: {response.error}")

        return response.success

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_algorithm_selector():
    """测试算法选择器"""
    print("\n🎯 测试算法选择器...")

    try:
        from algorithm_registry import AlgorithmRegistry
        from algorithm_selector import AlgorithmSelector, SelectionStrategy
        from consensus_models import ConsensusInput, ConsensusRequest
        from simple_majority_algorithm import SimpleMajorityAlgorithm

        # 创建注册表和选择器
        registry = AlgorithmRegistry()
        selector = AlgorithmSelector(registry, SelectionStrategy.BALANCED)

        # 注册算法
        simple_majority = SimpleMajorityAlgorithm()
        registry.register("simple_majority", simple_majority)

        print(f"   注册表中的算法: {registry.get_algorithm_ids()}")

        # 创建测试请求
        inputs = [
            ConsensusInput(
                agent_id="test1",
                position="test",
                confidence=0.8
            )
        ]

        request = ConsensusRequest(inputs=inputs)

        # 测试算法选择
        selection = selector.select_algorithm(request)

        print(f"   算法选择结果: {'成功' if selection else '失败'}")
        if selection:
            print(f"   选中算法: {selection.algorithm_id}")
            print(f"   选择置信度: {selection.confidence:.3f}")
            print(f"   选择理由: {selection.reasoning}")

        return selection is not None

    except Exception as e:
        print(f"❌ 算法选择器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始直接调度器测试")
    print("=" * 50)

    # 运行测试
    test1 = asyncio.run(test_dispatcher_direct())
    test2 = asyncio.run(test_algorithm_selector())

    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   直接调度器测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"   算法选择器测试: {'✅ 通过' if test2 else '❌ 失败'}")

    if all([test1, test2]):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 存在问题，需要进一步调试。")
