#!/usr/bin/env python3
"""调试算法注册问题
"""

import sys

sys.path.append('src')
sys.path.append('src/core_services')

def debug_algorithm_registration():
    print("🔍 调试算法注册...")
    
    try:
        # 导入所需模块
        from algorithm_registry import AlgorithmRegistry
        from simple_majority_algorithm import SimpleMajorityAlgorithm
        from unified_consensus_dispatcher import UnifiedConsensusDispatcher
        
        print("✅ 模块导入成功")
        
        # 创建注册表
        registry = AlgorithmRegistry()
        print("✅ 注册表创建成功")
        
        # 创建算法
        algorithm = SimpleMajorityAlgorithm()
        print("✅ 算法创建成功")
        
        # 注册算法
        success = registry.register("simple_majority", algorithm)
        print(f"✅ 算法注册: {'成功' if success else '失败'}")
        
        # 检查注册的算法
        algorithms = registry.list_algorithms()
        print(f"📊 已注册算法数量: {len(algorithms)}")
        for alg_id in algorithms:
            print(f"   - {alg_id}")
        
        # 创建调度器
        dispatcher = UnifiedConsensusDispatcher()
        print("✅ 调度器创建成功")
        
        # 手动注册算法到调度器
        dispatcher.registry.register("simple_majority", algorithm)
        
        # 检查调度器中的算法
        dispatcher_algorithms = dispatcher.registry.list_algorithms()
        print(f"📊 调度器中算法数量: {len(dispatcher_algorithms)}")
        
        # 测试算法选择
        from consensus_models import ConsensusInput, ConsensusRequest
        
        test_input = ConsensusInput(
            agent_id="test",
            position="test",
            confidence=0.8
        )
        
        test_request = ConsensusRequest(inputs=[test_input])
        
        # 尝试选择算法
        selection = dispatcher.selector.select_algorithm(test_request)
        print(f"🎯 算法选择结果: {selection.algorithm_id if selection else 'None'}")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_algorithm_registration()