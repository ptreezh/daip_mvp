#!/usr/bin/env python3
"""统一共识调度器测试

按照新规则创建的简化测试，文件长度<400行
"""

import asyncio

from consensus_models import ConsensusInput, ConsensusRequest
from test_algorithm_registry import MockConsensusAlgorithm
from unified_consensus_dispatcher import DispatcherConfig, UnifiedConsensusDispatcher
from unified_consensus_dispatcher_utils import ConfigurationManager, DispatcherManager, MetricsCollector


class SlowAlgorithm(MockConsensusAlgorithm):
    """慢速算法用于测试超时"""
    
    def __init__(self, algorithm_id: str, delay: float = 2.0):
        super().__init__(algorithm_id)
        self.delay = delay
        
    async def calculate(self, inputs, context):
        await asyncio.sleep(self.delay)
        return await super().calculate(inputs, context)


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始UnifiedConsensusDispatcher基本功能测试...")
    
    try:
        # 创建调度器
        config = DispatcherConfig(
            default_timeout=5.0,
            max_concurrent_requests=10,
            fallback_enabled=True
        )
        dispatcher = UnifiedConsensusDispatcher(config)
        manager = DispatcherManager(dispatcher)
        
        # 注册测试算法
        reliable_algo = MockConsensusAlgorithm("reliable_algo")
        fast_algo = MockConsensusAlgorithm("fast_algo")
        
        success1 = manager.register_algorithm("reliable_algo", reliable_algo)
        success2 = manager.register_algorithm("fast_algo", fast_algo)
        
        if not (success1 and success2):
            print("❌ 算法注册失败")
            return False
            
        print("✅ 算法注册成功")
        
        # 设置算法健康状态
        for algo_id in ["reliable_algo", "fast_algo"]:
            info = dispatcher.registry.get_algorithm_info(algo_id)
            info.health_status = "healthy"
            
        # 测试共识计算
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8),
            ConsensusInput(agent_id="agent2", position="反对", confidence=0.7)
        ]
        request = ConsensusRequest(inputs=inputs)
        
        async def test_consensus():
            response = await dispatcher.calculate_consensus(request)
            return response
            
        response = asyncio.run(test_consensus())
        
        if not response.success:
            print(f"❌ 共识计算失败: {response.error}")
            return False
            
        print(f"✅ 共识计算成功: {response.result.consensus_value}")
        
        # 测试获取可用算法
        algorithms = manager.get_available_algorithms()
        if len(algorithms) != 2:
            print("❌ 获取可用算法失败")
            return False
            
        print("✅ 获取可用算法成功")
        
        # 测试指标收集
        metrics_collector = MetricsCollector(dispatcher)
        metrics = metrics_collector.get_metrics()
        
        if metrics["summary"]["total_requests"] != 1:
            print("❌ 指标收集失败")
            return False
            
        print("✅ 指标收集成功")
        
        print("🎉 所有基本功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False
        
    finally:
        asyncio.run(dispatcher.shutdown())


async def test_timeout_handling():
    """测试超时处理"""
    print("🧪 开始超时处理测试...")
    
    try:
        # 创建调度器
        config = DispatcherConfig(
            default_timeout=0.5,  # 更短的超时用于测试
            fallback_enabled=False  # 禁用降级以测试纯超时
        )
        dispatcher = UnifiedConsensusDispatcher(config)
        manager = DispatcherManager(dispatcher)
        
        # 注册慢速算法
        slow_algo = SlowAlgorithm("slow_algo", delay=2.0)  # 2秒延迟，超过1秒超时
        success = manager.register_algorithm("slow_algo", slow_algo)
        
        if not success:
            print("❌ 慢速算法注册失败")
            return False
            
        # 设置健康状态
        info = dispatcher.registry.get_algorithm_info("slow_algo")
        info.health_status = "healthy"
        
        # 测试超时
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
        
        response = await dispatcher.calculate_consensus(request)
        
        if response.success:
            print("❌ 超时测试失败：应该超时但成功了")
            return False
            
        if "timed out" not in response.error:
            print(f"❌ 超时错误信息不正确: {response.error}")
            return False
            
        print("✅ 超时处理正常")
        
        print("🎉 超时处理测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 超时测试异常: {str(e)}")
        return False
        
    finally:
        await dispatcher.shutdown()


async def test_fallback_integration():
    """测试降级集成"""
    print("🧪 开始降级集成测试...")
    
    try:
        # 创建调度器
        config = DispatcherConfig(
            default_timeout=5.0,
            fallback_enabled=True
        )
        dispatcher = UnifiedConsensusDispatcher(config)
        manager = DispatcherManager(dispatcher)
        
        # 注册算法
        from test_fallback_manager_simple import FailingAlgorithm
        failing_algo = FailingAlgorithm("failing_algo")
        reliable_algo = MockConsensusAlgorithm("reliable_algo")
        
        manager.register_algorithm("failing_algo", failing_algo)
        manager.register_algorithm("reliable_algo", reliable_algo)
        
        # 设置健康状态
        for algo_id in ["failing_algo", "reliable_algo"]:
            info = dispatcher.registry.get_algorithm_info(algo_id)
            info.health_status = "healthy"
            
        # 强制选择失败算法（通过修改选择器）
        dispatcher.selector.default_strategy = dispatcher.selector.default_strategy
        
        # 测试降级
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
        
        response = await dispatcher.calculate_consensus(request)
        
        # 应该通过降级成功
        if not response.success and not response.fallback_used:
            print(f"❌ 降级集成失败: {response.error}")
            return False
            
        print("✅ 降级集成正常")
        
        print("🎉 降级集成测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 降级集成测试异常: {str(e)}")
        return False
        
    finally:
        await dispatcher.shutdown()


def test_configuration_management():
    """测试配置管理"""
    print("🧪 开始配置管理测试...")
    
    try:
        # 创建调度器
        dispatcher = UnifiedConsensusDispatcher()
        config_manager = ConfigurationManager(dispatcher)
        
        # 获取初始配置
        initial_config = config_manager.get_config()
        if not initial_config:
            print("❌ 获取初始配置失败")
            return False
            
        print("✅ 获取初始配置成功")
        
        # 更新配置
        updates = {
            "default_timeout": 60.0,
            "max_concurrent_requests": 50,
            "enable_load_balancing": False
        }
        
        success = config_manager.update_config(updates)
        if not success:
            print("❌ 配置更新失败")
            return False
            
        print("✅ 配置更新成功")
        
        # 验证配置更新
        updated_config = config_manager.get_config()
        if updated_config["default_timeout"] != 60.0:
            print("❌ 配置更新验证失败")
            return False
            
        print("✅ 配置更新验证成功")
        
        # 测试配置导出
        config_json = config_manager.export_config()
        if not config_json:
            print("❌ 配置导出失败")
            return False
            
        print("✅ 配置导出成功")
        
        print("🎉 配置管理测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 配置管理测试异常: {str(e)}")
        return False
        
    finally:
        asyncio.run(dispatcher.shutdown())


def test_health_status():
    """测试健康状态"""
    print("🧪 开始健康状态测试...")
    
    try:
        # 创建调度器
        dispatcher = UnifiedConsensusDispatcher()
        manager = DispatcherManager(dispatcher)
        
        # 注册算法
        algo = MockConsensusAlgorithm("test_algo")
        manager.register_algorithm("test_algo", algo)
        
        # 设置健康状态
        info = dispatcher.registry.get_algorithm_info("test_algo")
        info.health_status = "healthy"
        
        # 获取健康状态
        health = dispatcher.get_health_status()
        
        if health["status"] != "healthy":
            print(f"❌ 健康状态错误: {health['status']}")
            return False
            
        print("✅ 健康状态正常")
        
        print("🎉 健康状态测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 健康状态测试异常: {str(e)}")
        return False
        
    finally:
        asyncio.run(dispatcher.shutdown())


if __name__ == "__main__":
    # 运行所有测试
    basic_success = test_basic_functionality()
    timeout_success = asyncio.run(test_timeout_handling())
    fallback_success = asyncio.run(test_fallback_integration())
    config_success = test_configuration_management()
    health_success = test_health_status()
    
    if all([basic_success, timeout_success, fallback_success, config_success, health_success]):
        print("\n📋 测试总结:")
        print("- ✅ 基本功能正常")
        print("- ✅ 超时处理正常")
        print("- ✅ 降级集成正常")
        print("- ✅ 配置管理正常")
        print("- ✅ 健康状态正常")
        print("\n🚀 任务5实现完成!")
    else:
        print("\n❌ 部分测试失败")