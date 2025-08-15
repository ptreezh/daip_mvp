#!/usr/bin/env python3
"""算法注册测试

测试算法注册过程，找出为什么没有可用算法的问题。
"""

import sys

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

def test_algorithm_registration():
    """测试算法注册过程"""
    print("🧪 测试算法注册过程...")
    
    try:
        # 导入所需模块
        from algorithm_registry import AlgorithmRegistry
        from bayesian_algorithm import BayesianAlgorithm
        from simple_majority_algorithm import SimpleMajorityAlgorithm
        from weighted_voting_algorithm import WeightedVotingAlgorithm
        from workflow_consensus_algorithm import WorkflowConsensusAlgorithm
        
        print("✅ 所有算法模块导入成功")
        
        # 创建注册表
        registry = AlgorithmRegistry()
        print("✅ 算法注册表创建成功")
        
        # 创建算法实例
        simple_majority = SimpleMajorityAlgorithm()
        weighted_voting = WeightedVotingAlgorithm()
        bayesian = BayesianAlgorithm()
        workflow = WorkflowConsensusAlgorithm()
        
        print("✅ 所有算法实例创建成功")
        
        # 注册算法
        algorithms = [
            ("simple_majority", simple_majority),
            ("weighted_voting", weighted_voting),
            ("bayesian_consensus", bayesian),
            ("workflow_consensus", workflow)
        ]
        
        for alg_id, alg_instance in algorithms:
            try:
                success = registry.register(alg_id, alg_instance)
                print(f"   {alg_id}: {'成功' if success else '失败'}")
            except Exception as e:
                print(f"   {alg_id}: 失败 - {e}")
        
        # 检查注册结果
        registered_algorithms = registry.get_algorithm_ids()
        print("\n📊 注册结果:")
        print(f"   已注册算法数量: {len(registered_algorithms)}")
        
        for alg_id in registered_algorithms:
            print(f"   - {alg_id}")
        
        # 测试算法获取
        if registered_algorithms:
            test_alg_id = registered_algorithms[0]
            alg_instance = registry.get_algorithm(test_alg_id)
            print(f"\n✅ 成功获取算法: {test_alg_id}")
            print(f"   算法类型: {type(alg_instance).__name__}")
        
        return len(registered_algorithms) > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_dispatcher():
    """测试统一调度器"""
    print("\n🔧 测试统一调度器...")
    
    try:
        from unified_consensus_dispatcher import UnifiedConsensusDispatcher
        
        # 创建调度器
        dispatcher = UnifiedConsensusDispatcher()
        print("✅ 统一调度器创建成功")
        
        # 检查注册表
        registry = dispatcher.registry
        print(f"   注册表类型: {type(registry).__name__}")
        
        # 手动注册一个算法
        from simple_majority_algorithm import SimpleMajorityAlgorithm
        simple_majority = SimpleMajorityAlgorithm()
        
        success = registry.register("test_simple_majority", simple_majority)
        print(f"   手动注册结果: {'成功' if success else '失败'}")
        
        # 检查注册结果
        algorithms = registry.get_algorithm_ids()
        print(f"   调度器中的算法数量: {len(algorithms)}")
        
        return len(algorithms) > 0
        
    except Exception as e:
        print(f"❌ 调度器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compatibility_layer():
    """测试兼容层初始化"""
    print("\n🔗 测试兼容层初始化...")
    
    try:
        from legacy_compatibility_layer import PersonalAssistantServiceCompatibility
        
        # 创建兼容层（这会触发调度器初始化）
        compatibility = PersonalAssistantServiceCompatibility()
        print("✅ 兼容层创建成功")
        
        # 检查调度器中的算法
        dispatcher = compatibility.dispatcher
        algorithms = dispatcher.registry.get_algorithm_ids()
        print(f"   兼容层中的算法数量: {len(algorithms)}")
        
        for alg_id in algorithms:
            print(f"   - {alg_id}")
        
        return len(algorithms) > 0
        
    except Exception as e:
        print(f"❌ 兼容层测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始算法注册诊断测试")
    print("=" * 50)
    
    # 运行测试
    test1 = test_algorithm_registration()
    test2 = test_unified_dispatcher()
    test3 = test_compatibility_layer()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   算法注册测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"   统一调度器测试: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"   兼容层测试: {'✅ 通过' if test3 else '❌ 失败'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 所有测试通过！算法注册正常工作。")
    else:
        print("\n⚠️ 存在问题，需要进一步调试。")