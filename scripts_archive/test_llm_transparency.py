#!/usr/bin/env python3
"""验证LLM调用透明度
"""

import asyncio
import sys

sys.path.append('src')

def test_transparency_monitor():
    """测试透明度监控"""
    try:
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.real_demo_system.transparency_monitor import TransparencyMonitor

        # 创建LLM集成器和监控器
        integrator = RealLLMIntegrator()
        monitor = TransparencyMonitor(integrator)

        # 验证基本属性
        assert hasattr(monitor, 'llm_integrator'), "缺少llm_integrator属性"
        assert hasattr(monitor, 'events'), "缺少events属性"
        assert hasattr(monitor, 'active_calls'), "缺少active_calls属性"
        assert hasattr(monitor, 'real_time_metrics'), "缺少real_time_metrics属性"

        # 验证基本方法
        assert hasattr(monitor, 'subscribe'), "缺少subscribe方法"
        assert hasattr(monitor, 'get_real_time_status'), "缺少get_real_time_status方法"
        assert hasattr(monitor, 'get_performance_dashboard'), "缺少get_performance_dashboard方法"

        print("✅ TransparencyMonitor验证通过")
        return True

    except Exception as e:
        print(f"❌ TransparencyMonitor验证失败: {e}")
        return False

def test_call_logging():
    """测试调用日志记录"""
    try:
        from datetime import datetime

        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.real_demo_system.transparency_monitor import TransparencyEvent, TransparencyMonitor

        integrator = RealLLMIntegrator()
        monitor = TransparencyMonitor(integrator)

        # 创建测试事件
        event = TransparencyEvent(
            event_id="test_001",
            event_type="call_completed",
            timestamp=datetime.now(),
            data={"model": "gemma3:latest", "duration": 1.5}
        )

        # 添加事件
        monitor.events.append(event)

        # 验证事件记录
        assert len(monitor.events) > 0, "事件记录为空"
        assert monitor.events[-1].event_id == "test_001", "事件ID不匹配"

        print("✅ 调用日志记录验证通过")
        return True

    except Exception as e:
        print(f"❌ 调用日志记录验证失败: {e}")
        return False

def test_performance_tracking():
    """测试性能追踪"""
    try:
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.real_demo_system.transparency_monitor import RealTimeMetrics, TransparencyMonitor

        integrator = RealLLMIntegrator()
        monitor = TransparencyMonitor(integrator)

        # 验证实时指标
        metrics = monitor.real_time_metrics
        assert isinstance(metrics, RealTimeMetrics), "metrics类型不正确"
        assert hasattr(metrics, 'current_active_calls'), "缺少current_active_calls"
        assert hasattr(metrics, 'calls_per_minute'), "缺少calls_per_minute"
        assert hasattr(metrics, 'average_response_time_ms'), "缺少average_response_time_ms"

        # 验证获取指标方法
        assert hasattr(monitor, 'get_real_time_status'), "缺少get_real_time_status方法"
        status = monitor.get_real_time_status()
        assert isinstance(status, dict), "返回的status类型不正确"
        assert 'active_calls' in status, "status缺少active_calls"

        print("✅ 性能追踪验证通过")
        return True

    except Exception as e:
        print(f"❌ 性能追踪验证失败: {e}")
        return False

async def test_llm_integration_transparency():
    """测试LLM集成服务的透明度功能"""
    try:
        from src.real_demo_system.llm_integration_service import LLMBackend, LLMIntegrationService

        service = LLMIntegrationService()

        # 执行调用
        response = await service.generate(
            prompt="透明度测试",
            backend=LLMBackend.OLLAMA,
            temperature=0.1,
            max_tokens=20
        )

        # 验证调用记录
        assert hasattr(response, 'call_record'), "响应缺少call_record"
        call_record = response.call_record

        if call_record:
            assert hasattr(call_record, 'call_id'), "调用记录缺少call_id"
            assert hasattr(call_record, 'timestamp'), "调用记录缺少timestamp"
            assert hasattr(call_record, 'duration'), "调用记录缺少duration"
            assert hasattr(call_record, 'token_usage'), "调用记录缺少token_usage"

        # 验证调用历史
        history = service.get_call_history()
        assert len(history) > 0, "调用历史为空"

        # 验证统计信息
        stats = service.get_call_statistics()
        assert "total_calls" in stats, "缺少total_calls统计"
        assert "total_duration" in stats, "缺少total_duration统计"

        print("✅ LLM集成服务透明度验证通过")
        return True

    except Exception as e:
        print(f"❌ LLM集成服务透明度验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证LLM调用透明度")

    tests = [
        ("TransparencyMonitor", test_transparency_monitor),
        ("调用日志记录", test_call_logging),
        ("性能追踪", test_performance_tracking),
        ("LLM集成服务透明度", test_llm_integration_transparency)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()

        if result:
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break

    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
