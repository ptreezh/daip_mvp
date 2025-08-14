#!/usr/bin/env python3
"""实时状态监控测试

测试任务3.1.2的实时状态监控功能
验证透明度监控组件的实时更新能力
"""

import asyncio
import logging
import sys
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_transparency_monitor_realtime():
    """测试透明度监控的实时功能"""
    print("\n" + "="*60)
    print("🧪 测试透明度监控实时功能")
    print("="*60)

    try:
        from components.transparency_monitor import TransparencyMonitor
        from services.websocket_manager import realtime_manager, websocket_manager

        # 创建透明度监控器
        monitor = TransparencyMonitor(
            websocket_manager=websocket_manager,
            realtime_manager=realtime_manager
        )

        # 验证基本属性
        assert hasattr(monitor, 'monitoring_active'), "缺少monitoring_active属性"
        assert hasattr(monitor, 'start_monitoring'), "缺少start_monitoring方法"
        assert hasattr(monitor, 'stop_monitoring'), "缺少stop_monitoring方法"
        assert hasattr(monitor, 'system_status'), "缺少system_status属性"
        assert hasattr(monitor, 'system_metrics'), "缺少system_metrics属性"

        print("✅ 透明度监控器基本功能验证通过")

        # 启动监控
        await monitor.start_monitoring()
        assert monitor.monitoring_active == True, "监控未正确启动"
        print("✅ 实时监控启动成功")

        # 等待一段时间让监控循环运行
        await asyncio.sleep(3)

        # 停止监控
        await monitor.stop_monitoring()
        assert monitor.monitoring_active == False, "监控未正确停止"
        print("✅ 实时监控停止成功")

        return True

    except Exception as e:
        print(f"❌ 透明度监控实时功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_status_updates():
    """测试代理状态实时更新"""
    print("\n" + "="*60)
    print("🤖 测试代理状态实时更新")
    print("="*60)

    try:
        from components.transparency_monitor import TransparencyMonitor
        from services.websocket_manager import realtime_manager, websocket_manager

        monitor = TransparencyMonitor(
            websocket_manager=websocket_manager,
            realtime_manager=realtime_manager
        )

        # 记录初始代理数量
        initial_agent_count = len(monitor.active_agents)
        print(f"初始代理数量: {initial_agent_count}")

        # 模拟代理状态更新
        test_agent_data = {
            "agent_id": "test_agent_001",
            "name": "测试代理",
            "status": "processing",
            "framework": "测试框架",
            "confidence": 0.95,
            "current_task": "执行测试任务"
        }

        await monitor.update_agent_status(test_agent_data)

        # 验证代理已添加
        updated_agent_count = len(monitor.active_agents)
        assert updated_agent_count == initial_agent_count + 1, f"代理数量未正确更新: {updated_agent_count} vs {initial_agent_count + 1}"

        # 验证代理信息
        test_agent = None
        for agent in monitor.active_agents:
            if agent["id"] == "test_agent_001":
                test_agent = agent
                break

        assert test_agent is not None, "测试代理未找到"
        assert test_agent["name"] == "测试代理", "代理名称不正确"
        assert test_agent["status"] == "processing", "代理状态不正确"
        assert test_agent["confidence"] == 0.95, "代理置信度不正确"

        print("✅ 代理状态更新测试通过")

        # 测试代理状态变更
        update_data = {
            "agent_id": "test_agent_001",
            "status": "completed",
            "current_task": "任务已完成"
        }

        await monitor.update_agent_status(update_data)

        # 验证状态已更新
        for agent in monitor.active_agents:
            if agent["id"] == "test_agent_001":
                assert agent["status"] == "completed", "代理状态未正确更新"
                assert agent["current_task"] == "任务已完成", "代理任务未正确更新"
                break

        print("✅ 代理状态变更测试通过")
        return True

    except Exception as e:
        print(f"❌ 代理状态更新测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_system_status_updates():
    """测试系统状态实时更新"""
    print("\n" + "="*60)
    print("🏥 测试系统状态实时更新")
    print("="*60)

    try:
        from components.transparency_monitor import TransparencyMonitor
        from services.websocket_manager import realtime_manager, websocket_manager

        monitor = TransparencyMonitor(
            websocket_manager=websocket_manager,
            realtime_manager=realtime_manager
        )

        # 测试后端连接状态更新
        backend_status_data = {
            "type": "backend_connection",
            "data": {"connected": False}
        }

        await monitor.update_system_status(backend_status_data)
        assert monitor.system_status["backend_connected"] == False, "后端连接状态未正确更新"
        print("✅ 后端连接状态更新测试通过")

        # 测试LLM服务状态更新
        llm_status_data = {
            "type": "llm_service",
            "data": {
                "service": "test_llm",
                "status": "degraded",
                "response_time": 5.2
            }
        }

        await monitor.update_system_status(llm_status_data)
        assert "test_llm" in monitor.system_status["llm_services"], "LLM服务未添加"
        assert monitor.system_status["llm_services"]["test_llm"]["status"] == "degraded", "LLM服务状态不正确"
        assert monitor.system_status["llm_services"]["test_llm"]["response_time"] == 5.2, "LLM服务响应时间不正确"
        print("✅ LLM服务状态更新测试通过")

        # 测试角色库状态更新
        role_library_data = {
            "type": "role_library",
            "data": {"status": "loading"}
        }

        await monitor.update_system_status(role_library_data)
        assert monitor.system_status["role_library_status"] == "loading", "角色库状态未正确更新"
        print("✅ 角色库状态更新测试通过")

        return True

    except Exception as e:
        print(f"❌ 系统状态更新测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_status_updates():
    """测试工作流状态实时更新"""
    print("\n" + "="*60)
    print("🔄 测试工作流状态实时更新")
    print("="*60)

    try:
        from components.transparency_monitor import TransparencyMonitor
        from services.websocket_manager import realtime_manager, websocket_manager

        monitor = TransparencyMonitor(
            websocket_manager=websocket_manager,
            realtime_manager=realtime_manager
        )

        initial_workflow_count = len(monitor.workflow_executions)

        # 测试工作流开始
        workflow_start_data = {
            "workflow_id": "test_workflow_001",
            "type": "critical_review",
            "status": "started",
            "progress": 0,
            "workflows": ["批判性审查"],
            "roles": ["专家A", "专家B"],
            "steps": []
        }

        await monitor.update_workflow_status(workflow_start_data)

        # 验证工作流已添加
        updated_workflow_count = len(monitor.workflow_executions)
        assert updated_workflow_count == initial_workflow_count + 1, "工作流未正确添加"

        # 验证工作流信息
        test_workflow = None
        for workflow in monitor.workflow_executions:
            if workflow["id"] == "test_workflow_001":
                test_workflow = workflow
                break

        assert test_workflow is not None, "测试工作流未找到"
        assert test_workflow["type"] == "critical_review", "工作流类型不正确"
        assert test_workflow["status"] == "started", "工作流状态不正确"
        assert test_workflow["progress"] == 0, "工作流进度不正确"

        print("✅ 工作流开始测试通过")

        # 测试工作流进度更新
        workflow_progress_data = {
            "workflow_id": "test_workflow_001",
            "status": "running",
            "progress": 50
        }

        await monitor.update_workflow_status(workflow_progress_data)

        # 验证进度已更新
        for workflow in monitor.workflow_executions:
            if workflow["id"] == "test_workflow_001":
                assert workflow["status"] == "running", "工作流状态未正确更新"
                assert workflow["progress"] == 50, "工作流进度未正确更新"
                break

        print("✅ 工作流进度更新测试通过")

        # 测试工作流完成
        workflow_complete_data = {
            "workflow_id": "test_workflow_001",
            "status": "completed",
            "progress": 100,
            "result": {"success": True, "insights": ["洞察1", "洞察2"]}
        }

        await monitor.update_workflow_status(workflow_complete_data)

        # 验证工作流已完成
        for workflow in monitor.workflow_executions:
            if workflow["id"] == "test_workflow_001":
                assert workflow["status"] == "completed", "工作流状态未正确更新为完成"
                assert workflow["progress"] == 100, "工作流进度未正确更新为100%"
                assert "end_time" in workflow, "工作流完成时间未设置"
                assert "result" in workflow, "工作流结果未设置"
                break

        print("✅ 工作流完成测试通过")
        return True

    except Exception as e:
        print(f"❌ 工作流状态更新测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_performance_metrics():
    """测试性能指标计算"""
    print("\n" + "="*60)
    print("⚡ 测试性能指标计算")
    print("="*60)

    try:
        from components.transparency_monitor import TransparencyMonitor
        from services.websocket_manager import realtime_manager, websocket_manager

        monitor = TransparencyMonitor(
            websocket_manager=websocket_manager,
            realtime_manager=realtime_manager
        )

        # 添加一些测试LLM调用数据
        test_calls = [
            {
                "id": "call_1",
                "model": "test_model",
                "response_time": 1.5,
                "success": True,
                "timestamp": datetime.now(),
                "provider": "test"
            },
            {
                "id": "call_2",
                "model": "test_model",
                "response_time": 2.0,
                "success": True,
                "timestamp": datetime.now(),
                "provider": "test"
            },
            {
                "id": "call_3",
                "model": "test_model",
                "response_time": 1.8,
                "success": False,
                "timestamp": datetime.now(),
                "provider": "test"
            }
        ]

        monitor.llm_calls.extend(test_calls)

        # 更新系统指标
        await monitor._update_system_metrics()

        # 验证性能指标
        metrics = monitor.system_metrics["performance_metrics"]

        assert "avg_response_time" in metrics, "缺少平均响应时间指标"
        assert "success_rate" in metrics, "缺少成功率指标"
        assert "throughput" in metrics, "缺少吞吐量指标"

        # 验证计算结果
        expected_avg_response_time = (1.5 + 2.0 + 1.8) / 3
        print(f"期望平均响应时间: {expected_avg_response_time}")
        print(f"实际平均响应时间: {metrics['avg_response_time']}")
        print(f"差值: {abs(metrics['avg_response_time'] - expected_avg_response_time)}")

        # 由于初始化数据的影响，我们需要考虑所有调用
        all_response_times = [call["response_time"] for call in monitor.llm_calls]
        actual_expected = sum(all_response_times) / len(all_response_times)
        print(f"基于所有调用的期望值: {actual_expected}")

        assert abs(metrics["avg_response_time"] - actual_expected) < 0.01, f"平均响应时间计算不正确: 期望{actual_expected}, 实际{metrics['avg_response_time']}"

        # 计算基于所有调用的成功率
        all_success_count = sum(1 for call in monitor.llm_calls if call["success"])
        actual_expected_success_rate = (all_success_count / len(monitor.llm_calls)) * 100
        print(f"期望成功率: {actual_expected_success_rate}")
        print(f"实际成功率: {metrics['success_rate']}")

        assert abs(metrics["success_rate"] - actual_expected_success_rate) < 0.1, f"成功率计算不正确: 期望{actual_expected_success_rate}, 实际{metrics['success_rate']}"

        print("✅ 性能指标计算测试通过")
        return True

    except Exception as e:
        print(f"❌ 性能指标计算测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_websocket_integration():
    """测试WebSocket集成"""
    print("\n" + "="*60)
    print("🔌 测试WebSocket集成")
    print("="*60)

    try:
        from components.transparency_monitor import TransparencyMonitor
        from services.websocket_manager import realtime_manager, websocket_manager

        # 连接WebSocket
        connection_result = await websocket_manager.connect()
        assert connection_result == True, "WebSocket连接失败"
        print("✅ WebSocket连接成功")

        # 创建监控器
        monitor = TransparencyMonitor(
            websocket_manager=websocket_manager,
            realtime_manager=realtime_manager
        )

        # 验证回调已注册
        assert "agent_status" in realtime_manager.component_callbacks, "代理状态回调未注册"
        assert "workflow" in realtime_manager.component_callbacks, "工作流回调未注册"
        assert "system_status" in realtime_manager.component_callbacks, "系统状态回调未注册"

        print("✅ WebSocket回调注册成功")

        # 断开连接
        await websocket_manager.disconnect()
        print("✅ WebSocket断开成功")

        return True

    except Exception as e:
        print(f"❌ WebSocket集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始实时状态监控测试套件")
    print("="*80)

    tests = [
        ("透明度监控实时功能", test_transparency_monitor_realtime),
        ("代理状态实时更新", test_agent_status_updates),
        ("系统状态实时更新", test_system_status_updates),
        ("工作流状态实时更新", test_workflow_status_updates),
        ("性能指标计算", test_performance_metrics),
        ("WebSocket集成", test_websocket_integration)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 {test_name} 执行失败: {e}")
            results.append((test_name, False))

    # 输出测试结果
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {(passed/len(results)*100):.1f}%")

    if failed == 0:
        print("\n🎉 所有测试通过！任务3.1.2实时状态监控功能实现成功！")
        return True
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，需要修复")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试执行出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
