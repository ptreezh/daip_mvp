"""真实演示系统测试脚本

测试已实现的真实演示系统组件，验证LLM集成器、角色管理器和透明度监控的功能。
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from real_demo_system.call_verification import CallVerificationSystem
from real_demo_system.real_llm_integrator import RealLLMIntegrator
from real_demo_system.real_role_manager import RealRoleManager
from real_demo_system.transparency_monitor import TransparencyMonitor

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_llm_integrator():
    """测试LLM集成器"""
    print("\n" + "="*50)
    print("测试 RealLLMIntegrator")
    print("="*50)

    # 创建LLM集成器
    llm_integrator = RealLLMIntegrator()

    # 健康检查
    print("\n1. 健康检查:")
    health_status = await llm_integrator.health_check()
    print(json.dumps(health_status, indent=2, ensure_ascii=False))

    # 测试LLM调用（使用Ollama，如果可用）
    print("\n2. 测试LLM调用:")
    try:
        record = await llm_integrator.call_llm(
            prompt="请简单介绍一下人工智能的发展历史。",
            provider="ollama",
            model="llama3:instruct",
            temperature=0.7,
            metadata={"test": "demo_system_test"}
        )

        print(f"调用成功: {record.success}")
        print(f"调用ID: {record.call_id}")
        print(f"响应时间: {record.duration_ms}ms")
        print(f"输入Token: {record.input_tokens}")
        print(f"输出Token: {record.output_tokens}")
        print(f"响应长度: {len(record.response)}")
        if record.response:
            print(f"响应预览: {record.response[:200]}...")

    except Exception as e:
        print(f"LLM调用失败: {e}")

    # 获取性能指标
    print("\n3. 性能指标:")
    metrics = llm_integrator.get_performance_metrics()
    print(json.dumps(metrics, indent=2, ensure_ascii=False))

    # 获取实时状态
    print("\n4. 实时状态:")
    status = llm_integrator.get_real_time_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))

    return llm_integrator


def test_role_manager():
    """测试角色管理器"""
    print("\n" + "="*50)
    print("测试 RealRoleManager")
    print("="*50)

    # 创建角色管理器
    role_manager = RealRoleManager()

    # 获取所有角色
    print("\n1. 加载的角色数量:")
    all_roles = role_manager.get_all_roles()
    print(f"总共加载了 {len(all_roles)} 个角色")

    # 显示前5个角色
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
    print(f"找到 {len(ai_roles)} 个AI相关角色:")
    for role_id, role_data in list(ai_roles.items())[:3]:
        print(f"  - {role_id}: {role_data.get('name', 'Unknown')}")

    # 测试角色真实性验证
    if all_roles:
        first_role_id = list(all_roles.keys())[0]
        print(f"\n5. 角色真实性验证 (角色: {first_role_id}):")
        verification = role_manager.verify_role_authenticity(first_role_id)
        print(json.dumps(verification, indent=2, ensure_ascii=False))

    # 测试认知差异分析
    if len(all_roles) >= 2:
        role_ids = list(all_roles.keys())[:2]
        print(f"\n6. 认知差异分析 ({role_ids[0]} vs {role_ids[1]}):")
        differences = role_manager.analyze_cognitive_differences(role_ids[0], role_ids[1])
        for diff in differences:
            print(f"  - {diff.dimension}: 差异分数 {diff.difference_score:.2f} - {diff.description}")

    return role_manager


async def test_transparency_monitor(llm_integrator):
    """测试透明度监控"""
    print("\n" + "="*50)
    print("测试 TransparencyMonitor")
    print("="*50)

    # 创建透明度监控器
    monitor = TransparencyMonitor(llm_integrator)

    # 等待一下让监控器启动
    await asyncio.sleep(1)

    # 获取实时状态
    print("\n1. 实时状态:")
    status = monitor.get_real_time_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))

    # 如果有调用记录，生成透明度报告
    if llm_integrator.call_records:
        call_id = llm_integrator.call_records[0].call_id
        print(f"\n2. 透明度报告 (调用ID: {call_id}):")
        report = monitor.get_call_transparency_report(call_id)
        print(json.dumps(report, indent=2, ensure_ascii=False))

        # 生成透明度证书
        print("\n3. 透明度证书:")
        certificate = await monitor.generate_transparency_certificate(call_id)
        print(json.dumps(certificate, indent=2, ensure_ascii=False))

    # 获取审计摘要
    print("\n4. 审计摘要:")
    audit_summary = monitor.get_audit_summary()
    print(json.dumps(audit_summary, indent=2, ensure_ascii=False))

    # 停止监控
    monitor.stop_monitoring()

    return monitor


def test_call_verification(llm_integrator):
    """测试调用验证系统"""
    print("\n" + "="*50)
    print("测试 CallVerificationSystem")
    print("="*50)

    # 创建验证系统
    verification_system = CallVerificationSystem()

    # 如果有调用记录，进行验证
    if llm_integrator.call_records:
        record = llm_integrator.call_records[0]

        print(f"\n1. 验证调用完整性 (调用ID: {record.call_id}):")
        verification_result = verification_system.verify_call_integrity(record)
        print(json.dumps(verification_result.to_dict(), indent=2, ensure_ascii=False))

        print("\n2. 生成调用签名:")
        signature = verification_system.generate_call_signature(record)
        print(f"签名: {signature}")

        print("\n3. 审计轨迹:")
        audit_trail = verification_system.generate_audit_trail(record.call_id)
        print(json.dumps(audit_trail, indent=2, ensure_ascii=False))

    # 获取验证摘要
    print("\n4. 验证摘要:")
    summary = verification_system.get_validation_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    return verification_system


async def main():
    """主测试函数"""
    print("开始测试真实演示系统组件...")
    print(f"测试时间: {datetime.now().isoformat()}")

    try:
        # 测试LLM集成器
        llm_integrator = await test_llm_integrator()

        # 测试角色管理器
        role_manager = test_role_manager()

        # 测试透明度监控
        monitor = await test_transparency_monitor(llm_integrator)

        # 测试调用验证
        verification_system = test_call_verification(llm_integrator)

        print("\n" + "="*50)
        print("所有测试完成!")
        print("="*50)

        # 生成测试报告
        test_report = {
            "test_timestamp": datetime.now().isoformat(),
            "components_tested": [
                "RealLLMIntegrator",
                "RealRoleManager",
                "TransparencyMonitor",
                "CallVerificationSystem"
            ],
            "llm_integrator_stats": llm_integrator.get_performance_metrics(),
            "role_manager_stats": role_manager.get_validation_summary(),
            "test_status": "completed"
        }

        print("\n测试报告:")
        print(json.dumps(test_report, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
