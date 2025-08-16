#!/usr/bin/env python3
"""统一共识调度器简化测试

专注于核心功能的简化测试
"""

import asyncio

from consensus_models import ConsensusInput, ConsensusRequest
from test_algorithm_registry import MockConsensusAlgorithm
from unified_consensus_dispatcher import DispatcherConfig, UnifiedConsensusDispatcher
from unified_consensus_dispatcher_utils import DispatcherManager, MetricsCollector


def test_core_functionality():
    """测试核心功能"""
    print("🧪 开始核心功能测试...")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    try:
        # 创建调度器
        dispatcher = UnifiedConsensusDispatcher()
        manager = DispatcherManager(dispatcher)
        metrics_collector = MetricsCollector(dispatcher)
<<<<<<< HEAD

        # 注册算法
        algo1 = MockConsensusAlgorithm("algo1")
        algo2 = MockConsensusAlgorithm("algo2")

        success1 = manager.register_algorithm("algo1", algo1)
        success2 = manager.register_algorithm("algo2", algo2)

        if not (success1 and success2):
            print("❌ 算法注册失败")
            return False

        print("✅ 算法注册成功")

=======
        
        # 注册算法
        algo1 = MockConsensusAlgorithm("algo1")
        algo2 = MockConsensusAlgorithm("algo2")
        
        success1 = manager.register_algorithm("algo1", algo1)
        success2 = manager.register_algorithm("algo2", algo2)
        
        if not (success1 and success2):
            print("❌ 算法注册失败")
            return False
            
        print("✅ 算法注册成功")
        
>>>>>>> feature/core-services-refactor
        # 设置健康状态
        for algo_id in ["algo1", "algo2"]:
            info = dispatcher.registry.get_algorithm_info(algo_id)
            info.health_status = "healthy"
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 测试共识计算
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8),
            ConsensusInput(agent_id="agent2", position="反对", confidence=0.7)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        async def run_consensus():
            return await dispatcher.calculate_consensus(request)

        response = asyncio.run(run_consensus())

        if not response.success:
            print(f"❌ 共识计算失败: {response.error}")
            return False

        print(f"✅ 共识计算成功: {response.result.consensus_value}")

=======
        
        async def run_consensus():
            return await dispatcher.calculate_consensus(request)
            
        response = asyncio.run(run_consensus())
        
        if not response.success:
            print(f"❌ 共识计算失败: {response.error}")
            return False
            
        print(f"✅ 共识计算成功: {response.result.consensus_value}")
        
>>>>>>> feature/core-services-refactor
        # 测试指标
        metrics = metrics_collector.get_metrics()
        if metrics["summary"]["total_requests"] != 1:
            print("❌ 指标统计错误")
            return False
<<<<<<< HEAD

        print("✅ 指标统计正确")

=======
            
        print("✅ 指标统计正确")
        
>>>>>>> feature/core-services-refactor
        # 测试健康状态
        health = dispatcher.get_health_status()
        if health["status"] != "healthy":
            print(f"❌ 健康状态错误: {health['status']}")
            return False
<<<<<<< HEAD

        print("✅ 健康状态正常")

=======
            
        print("✅ 健康状态正常")
        
>>>>>>> feature/core-services-refactor
        # 测试获取算法列表
        algorithms = manager.get_available_algorithms()
        if len(algorithms) != 2:
            print("❌ 算法列表错误")
            return False
<<<<<<< HEAD

        print("✅ 算法列表正确")

        print("🎉 所有核心功能测试通过!")
        return True

    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

=======
            
        print("✅ 算法列表正确")
        
        print("🎉 所有核心功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        asyncio.run(dispatcher.shutdown())


async def test_concurrent_requests():
    """测试并发请求"""
    print("🧪 开始并发请求测试...")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    try:
        # 创建调度器
        config = DispatcherConfig(max_concurrent_requests=5)
        dispatcher = UnifiedConsensusDispatcher(config)
        manager = DispatcherManager(dispatcher)
<<<<<<< HEAD

        # 注册算法
        algo = MockConsensusAlgorithm("test_algo")
        manager.register_algorithm("test_algo", algo)

        # 设置健康状态
        info = dispatcher.registry.get_algorithm_info("test_algo")
        info.health_status = "healthy"

=======
        
        # 注册算法
        algo = MockConsensusAlgorithm("test_algo")
        manager.register_algorithm("test_algo", algo)
        
        # 设置健康状态
        info = dispatcher.registry.get_algorithm_info("test_algo")
        info.health_status = "healthy"
        
>>>>>>> feature/core-services-refactor
        # 创建多个并发请求
        async def make_request(request_id):
            inputs = [
                ConsensusInput(agent_id=f"agent_{request_id}", position="支持", confidence=0.8)
            ]
            request = ConsensusRequest(inputs=inputs)
            return await dispatcher.calculate_consensus(request)
<<<<<<< HEAD

        # 并发执行5个请求
        tasks = [make_request(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)

=======
            
        # 并发执行5个请求
        tasks = [make_request(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)
        
>>>>>>> feature/core-services-refactor
        # 验证所有请求都成功
        success_count = sum(1 for r in responses if r.success)
        if success_count != 5:
            print(f"❌ 并发请求失败: 只有{success_count}/5成功")
            return False
<<<<<<< HEAD

        print("✅ 并发请求处理正常")

=======
            
        print("✅ 并发请求处理正常")
        
>>>>>>> feature/core-services-refactor
        # 验证指标
        metrics_collector = MetricsCollector(dispatcher)
        metrics = metrics_collector.get_metrics()
        if metrics["summary"]["total_requests"] != 5:
            print("❌ 并发请求指标错误")
            return False
<<<<<<< HEAD

        print("✅ 并发请求指标正确")

        print("🎉 并发请求测试通过!")
        return True

    except Exception as e:
        print(f"❌ 并发测试异常: {str(e)}")
        return False

=======
            
        print("✅ 并发请求指标正确")
        
        print("🎉 并发请求测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 并发测试异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        await dispatcher.shutdown()


def test_algorithm_management():
    """测试算法管理"""
    print("🧪 开始算法管理测试...")
<<<<<<< HEAD

    try:
        dispatcher = UnifiedConsensusDispatcher()
        manager = DispatcherManager(dispatcher)

        # 注册算法
        algo = MockConsensusAlgorithm("test_algo")
        success = manager.register_algorithm("test_algo", algo)

        if not success:
            print("❌ 算法注册失败")
            return False

        print("✅ 算法注册成功")

=======
    
    try:
        dispatcher = UnifiedConsensusDispatcher()
        manager = DispatcherManager(dispatcher)
        
        # 注册算法
        algo = MockConsensusAlgorithm("test_algo")
        success = manager.register_algorithm("test_algo", algo)
        
        if not success:
            print("❌ 算法注册失败")
            return False
            
        print("✅ 算法注册成功")
        
>>>>>>> feature/core-services-refactor
        # 获取算法详情
        details = manager.get_algorithm_details("test_algo")
        if not details:
            print("❌ 获取算法详情失败")
            return False
<<<<<<< HEAD

        print("✅ 获取算法详情成功")

=======
            
        print("✅ 获取算法详情成功")
        
>>>>>>> feature/core-services-refactor
        # 注销算法
        success = manager.unregister_algorithm("test_algo")
        if not success:
            print("❌ 算法注销失败")
            return False
<<<<<<< HEAD

        print("✅ 算法注销成功")

=======
            
        print("✅ 算法注销成功")
        
>>>>>>> feature/core-services-refactor
        # 验证算法已注销
        algorithms = manager.get_available_algorithms()
        if len(algorithms) != 0:
            print("❌ 算法注销验证失败")
            return False
<<<<<<< HEAD

        print("✅ 算法注销验证成功")

        print("🎉 算法管理测试通过!")
        return True

    except Exception as e:
        print(f"❌ 算法管理测试异常: {str(e)}")
        return False

=======
            
        print("✅ 算法注销验证成功")
        
        print("🎉 算法管理测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 算法管理测试异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        asyncio.run(dispatcher.shutdown())


if __name__ == "__main__":
    # 运行简化测试
    core_success = test_core_functionality()
    concurrent_success = asyncio.run(test_concurrent_requests())
    management_success = test_algorithm_management()
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    if all([core_success, concurrent_success, management_success]):
        print("\n📋 测试总结:")
        print("- ✅ 核心功能正常")
        print("- ✅ 并发处理正常")
        print("- ✅ 算法管理正常")
        print("\n🚀 任务5实现完成!")
    else:
<<<<<<< HEAD
        print("\n❌ 部分测试失败")
=======
        print("\n❌ 部分测试失败")
>>>>>>> feature/core-services-refactor
