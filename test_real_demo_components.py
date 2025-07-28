"""
真实演示系统组件测试

测试已实现的真实演示系统组件的基本功能。
"""

import asyncio
import json
import logging
import os
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_role_manager():
    """测试角色管理器"""
    print("\n" + "="*50)
    print("测试 RealRoleManager")
    print("="*50)
    
    try:
        from src.real_demo_system.real_role_manager import RealRoleManager
        
        # 创建角色管理器
        role_manager = RealRoleManager()
        
        # 获取所有角色
        print(f"\n1. 加载的角色数量: {len(role_manager.get_all_roles())}")
        
        # 显示前5个角色
        all_roles = role_manager.get_all_roles()
        print("\n2. 前5个角色:")
        for i, (role_id, role_data) in enumerate(list(all_roles.items())[:5]):
            print(f"  {i+1}. {role_id}: {role_data.get('name', 'Unknown')}")
        
        # 验证摘要
        print("\n3. 验证摘要:")
        validation_summary = role_manager.get_validation_summary()
        print(json.dumps(validation_summary, indent=2, ensure_ascii=False))
        
        # 测试角色搜索
        print("\n4. 搜索测试 (搜索'AI'相关角色):")
        ai_roles = role_manager.search_roles("AI")
        print(f"找到 {len(ai_roles)} 个AI相关角色")
        
        # 测试角色真实性验证
        if all_roles:
            first_role_id = list(all_roles.keys())[0]
            print(f"\n5. 角色真实性验证 (角色: {first_role_id}):")
            verification = role_manager.verify_role_authenticity(first_role_id)
            print(f"验证通过: {verification['verified']}")
            print(f"文件哈希匹配: {verification['hash_matches']}")
            print(f"验证状态: {verification['validation_status']}")
            print(f"置信度分数: {verification['confidence_score']}")
        
        print("\n✅ RealRoleManager 测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ RealRoleManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_integrator():
    """测试LLM集成器"""
    print("\n" + "="*50)
    print("测试 RealLLMIntegrator")
    print("="*50)
    
    try:
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        
        # 创建LLM集成器
        llm_integrator = RealLLMIntegrator()
        
        # 健康检查
        print("\n1. 健康检查:")
        health_status = await llm_integrator.health_check()
        print(f"整体状态: {health_status['overall_status']}")
        
        for provider, status in health_status['providers'].items():
            print(f"  {provider}: {status['status']} (可用: {status['available']})")
        
        # 获取性能指标
        print("\n2. 性能指标:")
        metrics = llm_integrator.get_performance_metrics()
        print(f"总调用数: {metrics['total_calls']}")
        print(f"成功调用数: {metrics['successful_calls']}")
        print(f"成功率: {metrics['success_rate']:.2%}")
        
        # 获取实时状态
        print("\n3. 实时状态:")
        status = llm_integrator.get_real_time_status()
        print(f"是否活跃: {status['is_active']}")
        print(f"最后调用时间: {status['last_call_time']}")
        print(f"今日总调用数: {status['total_calls_today']}")
        
        print("\n✅ RealLLMIntegrator 测试通过")
        return llm_integrator
        
    except Exception as e:
        print(f"\n❌ RealLLMIntegrator 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_call_verification():
    """测试调用验证系统"""
    print("\n" + "="*50)
    print("测试 CallVerificationSystem")
    print("="*50)
    
    try:
        from src.real_demo_system.call_verification import CallVerificationSystem
        
        # 创建验证系统
        verification_system = CallVerificationSystem()
        
        # 获取验证摘要
        print("\n1. 验证摘要:")
        summary = verification_system.get_verification_summary()
        print(f"总验证数: {summary['total_verifications']}")
        print(f"审计条目数: {summary['audit_stats']['total_entries']}")
        if 'audit_stats' in summary and 'hash_chain_length' in summary['audit_stats']:
            print(f"哈希链长度: {summary['audit_stats']['hash_chain_length']}")
        else:
            print("哈希链长度: 0 (无数据)")
        
        # 验证系统完整性
        print("\n2. 系统完整性验证:")
        integrity = verification_system.validate_system_integrity()
        print(f"整体有效: {integrity['overall_valid']}")
        print(f"哈希链有效: {integrity['hash_chain_valid']}")
        print(f"审计日志一致: {integrity['audit_log_consistent']}")
        
        print("\n✅ CallVerificationSystem 测试通过")
        return verification_system
        
    except Exception as e:
        print(f"\n❌ CallVerificationSystem 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_transparency_monitor(llm_integrator):
    """测试透明度监控"""
    print("\n" + "="*50)
    print("测试 TransparencyMonitor")
    print("="*50)
    
    if not llm_integrator:
        print("❌ 跳过透明度监控测试 (LLM集成器不可用)")
        return None
    
    try:
        from src.real_demo_system.transparency_monitor import TransparencyMonitor
        
        # 创建透明度监控器
        monitor = TransparencyMonitor(llm_integrator)
        
        # 等待一下让监控器启动
        await asyncio.sleep(1)
        
        # 获取实时状态
        print("\n1. 实时状态:")
        status = monitor.get_real_time_status()
        print(f"活跃调用数: {status['active_calls']}")
        print(f"最近事件数: {status['recent_events_count']}")
        
        # 获取审计摘要
        print("\n2. 审计摘要:")
        audit_summary = monitor.get_audit_summary()
        print(f"监控的调用总数: {audit_summary['total_monitored_calls']}")
        print(f"记录的事件总数: {audit_summary['total_events_recorded']}")
        print(f"监控覆盖率: {audit_summary['monitoring_coverage']['coverage_percentage']:.1f}%")
        
        # 停止监控
        monitor.stop_monitoring()
        
        print("\n✅ TransparencyMonitor 测试通过")
        return monitor
        
    except Exception as e:
        print(f"\n❌ TransparencyMonitor 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主测试函数"""
    print("开始测试真实演示系统组件...")
    print(f"测试时间: {datetime.now().isoformat()}")
    
    # 检查roles目录是否存在
    if not os.path.exists("roles"):
        print("❌ roles目录不存在，某些测试可能失败")
    else:
        print(f"✅ roles目录存在，包含 {len(os.listdir('roles'))} 个文件")
    
    test_results = {}
    
    try:
        # 测试角色管理器
        test_results['role_manager'] = test_role_manager()
        
        # 测试LLM集成器
        llm_integrator = await test_llm_integrator()
        test_results['llm_integrator'] = llm_integrator is not None
        
        # 测试调用验证系统
        verification_system = test_call_verification()
        test_results['verification_system'] = verification_system is not None
        
        # 测试透明度监控
        monitor = await test_transparency_monitor(llm_integrator)
        test_results['transparency_monitor'] = monitor is not None
        
        print("\n" + "="*50)
        print("测试结果摘要")
        print("="*50)
        
        for component, success in test_results.items():
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{component}: {status}")
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        print(f"\n总测试数: {total_tests}")
        print(f"通过测试数: {passed_tests}")
        print(f"成功率: {passed_tests/total_tests:.1%}")
        
        if passed_tests == total_tests:
            print("\n🎉 所有组件测试通过！真实演示系统基础组件运行正常。")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} 个组件测试失败，请检查相关配置。")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())