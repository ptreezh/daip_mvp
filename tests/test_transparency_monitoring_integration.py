#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V0.2.2 - 透明度监控系统集成测试

测试增强透明度监控系统的集成功能
"""

import asyncio
import pytest
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# 设置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestTransparencyMonitoringIntegration:
    """透明度监控系统集成测试"""
    
    @pytest.fixture
    async def mock_personal_assistant(self):
        """模拟PersonalAssistant服务"""
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService, WorkflowType, IntentResult, TeamProposal
        
        mock_assistant = Mock(spec=PersonalAssistantService)
        
        # 模拟意图分析
        mock_assistant.analyze_intent = AsyncMock(return_value=IntentResult(
            workflowType=WorkflowType.CRITICAL_REVIEW,
            confidence=0.85,
            reasoning="测试意图分析",
            topic="测试主题"
        ))
        
        # 模拟团队组建
        mock_assistant.assemble_team = AsyncMock(return_value=TeamProposal(
            agents=["测试专家1", "测试专家2"],
            diversity_score=0.75,
            rationale="测试团队组建",
            confirmation_message="测试确认消息"
        ))
        
        # 模拟消息处理
        mock_assistant.process_message = AsyncMock(return_value="测试响应消息")
        
        # 模拟命令执行
        mock_assistant.execute_command = AsyncMock(return_value="测试命令结果")
        
        return mock_assistant
    
    @pytest.fixture
    async def mock_backend_service(self):
        """模拟后端服务"""
        from personal_intelligence_hub.services.backend_integration import BackendIntegrationService, ServiceHealthStatus, ServiceStatus
        
        mock_backend = Mock(spec=BackendIntegrationService)
        
        # 模拟健康检查
        mock_backend.check_backend_health = AsyncMock(return_value={
            "backend": ServiceHealthStatus(
                service_name="Test Backend",
                status=ServiceStatus.HEALTHY,
                response_time=0.5,
                last_check=datetime.now(),
                details="Test backend healthy"
            )
        })
        
        return mock_backend
    
    @pytest.fixture
    async def transparency_monitor(self):
        """创建透明度监控器"""
        from frontend.components.transparency_monitor import TransparencyMonitor
        
        monitor = TransparencyMonitor()
        await monitor.start_monitoring()
        
        yield monitor
        
        await monitor.stop_monitoring()
    
    @pytest.fixture
    async def monitoring_integration(self, mock_personal_assistant):
        """创建监控集成服务"""
        from personal_intelligence_hub.services.monitoring_integration import MonitoringIntegrationService
        
        integration = MonitoringIntegrationService()
        await integration.initialize(mock_personal_assistant)
        
        yield integration
        
        await integration.shutdown()
    
    async def test_enhanced_transparency_integration_initialization(self, transparency_monitor):
        """测试增强透明度集成初始化"""
        from frontend.services.enhanced_transparency_integration import EnhancedTransparencyIntegration, MonitoringLevel
        
        # 创建集成器
        integration = EnhancedTransparencyIntegration(transparency_monitor, MonitoringLevel.DETAILED)
        
        # 模拟后端服务
        with patch('frontend.services.enhanced_transparency_integration.get_backend_service') as mock_get_backend:
            mock_backend = AsyncMock()
            mock_get_backend.return_value = mock_backend
            
            # 初始化
            await integration.initialize()
            
            # 验证初始化状态
            assert integration.is_monitoring == True
            assert integration.monitoring_level == MonitoringLevel.DETAILED
            assert integration.backend_service is not None
            
            # 清理
            await integration.stop_monitoring()
    
    async def test_llm_call_monitoring(self, transparency_monitor):
        """测试LLM调用监控"""
        from frontend.services.enhanced_transparency_integration import EnhancedTransparencyIntegration, MonitoringLevel
        
        integration = EnhancedTransparencyIntegration(transparency_monitor, MonitoringLevel.DETAILED)
        
        with patch('frontend.services.enhanced_transparency_integration.get_backend_service') as mock_get_backend:
            mock_backend = AsyncMock()
            mock_get_backend.return_value = mock_backend
            
            await integration.initialize()
            
            # 测试LLM调用记录
            call_data = {
                "call_id": "test_call_1",
                "model": "test-model",
                "provider": "test-provider",
                "input_tokens": 100,
                "output_tokens": 200,
                "response_time": 1.5,
                "cost": 0.01,
                "success": True
            }
            
            await integration.log_llm_call(call_data)
            
            # 验证调用被记录
            assert len(integration.llm_call_cache) == 1
            cached_call = integration.llm_call_cache[0]
            assert cached_call.model == "test-model"
            assert cached_call.response_time == 1.5
            assert cached_call.success == True
            
            await integration.stop_monitoring()
    
    async def test_workflow_monitoring(self, transparency_monitor):
        """测试工作流监控"""
        from frontend.services.enhanced_transparency_integration import EnhancedTransparencyIntegration, MonitoringLevel
        
        integration = EnhancedTransparencyIntegration(transparency_monitor, MonitoringLevel.DETAILED)
        
        with patch('frontend.services.enhanced_transparency_integration.get_backend_service') as mock_get_backend:
            mock_backend = AsyncMock()
            mock_get_backend.return_value = mock_backend
            
            await integration.initialize()
            
            # 测试工作流开始记录
            workflow_data = {
                "workflow_id": "test_workflow_1",
                "workflow_type": "critical_review",
                "participants": ["专家1", "专家2"]
            }
            
            await integration.log_workflow_start(workflow_data)
            
            # 验证工作流被记录
            assert "test_workflow_1" in integration.workflow_cache
            workflow_metrics = integration.workflow_cache["test_workflow_1"]
            assert workflow_metrics.workflow_type == "critical_review"
            assert workflow_metrics.status == "started"
            assert len(workflow_metrics.participants) == 2
            
            await integration.stop_monitoring()
    
    async def test_personal_assistant_monitoring_wrapper(self, mock_personal_assistant):
        """测试PersonalAssistant监控包装器"""
        from personal_intelligence_hub.services.monitoring_integration import PersonalAssistantMonitoringWrapper
        
        wrapper = PersonalAssistantMonitoringWrapper(mock_personal_assistant)
        
        # 添加监控回调
        events_received = []
        
        async def test_callback(event):
            events_received.append(event)
        
        wrapper.add_monitoring_callback(test_callback)
        
        # 测试意图分析监控
        result = await wrapper.analyze_intent("测试输入", {"session_id": "test_session"})
        
        # 验证结果
        assert result.topic == "测试主题"
        assert wrapper.stats["intent_analyses"] == 1
        
        # 验证事件
        assert len(events_received) >= 2  # 开始和完成事件
        start_event = events_received[0]
        assert start_event.event_type == "intent_analysis_start"
        assert start_event.session_id == "test_session"
        
        complete_event = events_received[1]
        assert complete_event.event_type == "intent_analysis_complete"
        assert complete_event.data["workflow_type"] == "critical_review"
    
    async def test_monitoring_integration_service(self, mock_personal_assistant):
        """测试监控集成服务"""
        from personal_intelligence_hub.services.monitoring_integration import MonitoringIntegrationService
        
        service = MonitoringIntegrationService()
        
        with patch('personal_intelligence_hub.services.monitoring_integration.get_backend_service') as mock_get_backend:
            mock_backend = AsyncMock()
            mock_get_backend.return_value = mock_backend
            
            await service.initialize(mock_personal_assistant)
            
            # 验证初始化状态
            assert service.monitoring_active == True
            assert service.personal_assistant_wrapper is not None
            
            # 测试透明度数据获取
            transparency_data = await service.get_transparency_data()
            
            assert "timestamp" in transparency_data
            assert "monitoring_active" in transparency_data
            assert "personal_assistant_stats" in transparency_data
            assert transparency_data["monitoring_active"] == True
            
            await service.shutdown()
    
    async def test_enhanced_monitoring_dashboard_initialization(self):
        """测试增强监控仪表板初始化"""
        from frontend.components.enhanced_monitoring_dashboard import EnhancedMonitoringDashboard, MonitoringLevel
        
        dashboard = EnhancedMonitoringDashboard(MonitoringLevel.DETAILED)
        
        # 模拟依赖
        with patch('frontend.components.enhanced_monitoring_dashboard.get_enhanced_transparency_integration') as mock_get_integration:
            mock_integration = AsyncMock()
            mock_integration.get_monitoring_statistics.return_value = {
                "is_monitoring": True,
                "monitoring_level": "detailed",
                "llm_calls_cached": 5,
                "active_workflows": 2,
                "total_workflows": 3
            }
            mock_get_integration.return_value = mock_integration
            
            await dashboard.initialize()
            
            # 验证初始化状态
            assert dashboard.is_initialized == True
            assert dashboard.integration_service is not None
            
            # 测试数据更新
            await dashboard._update_dashboard_data()
            
            dashboard_data = dashboard.dashboard_data
            assert "monitoring_stats" in dashboard_data
            assert "system_overview" in dashboard_data
            
            await dashboard.stop_auto_refresh()
    
    async def test_websocket_integration(self, transparency_monitor):
        """测试WebSocket集成"""
        from frontend.services.enhanced_transparency_integration import EnhancedTransparencyIntegration, MonitoringLevel
        from frontend.services.websocket_manager import WebSocketMessage, MessageType
        
        integration = EnhancedTransparencyIntegration(transparency_monitor, MonitoringLevel.DETAILED)
        
        with patch('frontend.services.enhanced_transparency_integration.get_backend_service') as mock_get_backend:
            mock_backend = AsyncMock()
            mock_get_backend.return_value = mock_backend
            
            await integration.initialize()
            
            # 模拟WebSocket消息
            llm_message = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                payload={
                    "type": "llm_call",
                    "call_id": "ws_test_call",
                    "model": "gpt-4",
                    "provider": "openai",
                    "input_tokens": 150,
                    "output_tokens": 300,
                    "response_time": 2.1,
                    "cost": 0.02,
                    "success": True
                }
            )
            
            # 处理消息
            await integration._handle_llm_call_update(llm_message)
            
            # 验证消息被处理
            assert len(integration.llm_call_cache) == 1
            cached_call = integration.llm_call_cache[0]
            assert cached_call.call_id == "ws_test_call"
            assert cached_call.model == "gpt-4"
            
            await integration.stop_monitoring()
    
    async def test_performance_metrics_calculation(self, transparency_monitor):
        """测试性能指标计算"""
        from frontend.services.enhanced_transparency_integration import EnhancedTransparencyIntegration, MonitoringLevel, LLMCallMetrics
        
        integration = EnhancedTransparencyIntegration(transparency_monitor, MonitoringLevel.DETAILED)
        
        # 添加测试数据
        test_calls = [
            LLMCallMetrics("call1", "model1", "provider1", 100, 200, 1.0, 0.01, True),
            LLMCallMetrics("call2", "model2", "provider2", 150, 250, 2.0, 0.02, True),
            LLMCallMetrics("call3", "model3", "provider3", 120, 180, 1.5, 0.015, False)  # 失败调用
        ]
        
        integration.llm_call_cache = test_calls
        
        # 计算性能指标
        metrics = await integration._calculate_performance_metrics()
        
        # 验证指标
        assert "avg_response_time" in metrics
        assert "success_rate" in metrics
        assert "throughput" in metrics
        
        # 验证平均响应时间
        expected_avg = (1.0 + 2.0 + 1.5) / 3
        assert abs(metrics["avg_response_time"] - expected_avg) < 0.01
        
        # 验证成功率
        expected_success_rate = (2 / 3) * 100  # 2个成功，1个失败
        assert abs(metrics["success_rate"] - expected_success_rate) < 0.01
    
    async def test_error_handling(self, mock_personal_assistant):
        """测试错误处理"""
        from personal_intelligence_hub.services.monitoring_integration import PersonalAssistantMonitoringWrapper
        
        # 设置模拟异常
        mock_personal_assistant.analyze_intent.side_effect = Exception("测试异常")
        
        wrapper = PersonalAssistantMonitoringWrapper(mock_personal_assistant)
        
        # 添加监控回调
        error_events = []
        
        async def error_callback(event):
            if event.event_type.endswith("_error"):
                error_events.append(event)
        
        wrapper.add_monitoring_callback(error_callback)
        
        # 测试异常处理
        with pytest.raises(Exception, match="测试异常"):
            await wrapper.analyze_intent("测试输入")
        
        # 验证错误统计
        assert wrapper.stats["error_count"] == 1
        
        # 验证错误事件
        assert len(error_events) == 1
        error_event = error_events[0]
        assert error_event.event_type == "intent_analysis_error"
        assert "测试异常" in error_event.data["error"]
    
    async def test_cache_cleanup(self, transparency_monitor):
        """测试缓存清理"""
        from frontend.services.enhanced_transparency_integration import EnhancedTransparencyIntegration, MonitoringLevel, LLMCallMetrics
        
        integration = EnhancedTransparencyIntegration(transparency_monitor, MonitoringLevel.DETAILED)
        integration.cache_size = 5  # 设置小的缓存大小
        
        # 添加超过缓存大小的数据
        for i in range(10):
            call = LLMCallMetrics(f"call{i}", "model", "provider", 100, 200, 1.0, 0.01, True)
            integration.llm_call_cache.append(call)
        
        # 执行清理
        await integration._cleanup_llm_cache()
        
        # 验证缓存大小
        assert len(integration.llm_call_cache) == integration.cache_size
        
        # 验证保留的是最新的记录
        assert integration.llm_call_cache[0].call_id == "call5"
        assert integration.llm_call_cache[-1].call_id == "call9"


class TestIntegrationScenarios:
    """集成场景测试"""
    
    async def test_end_to_end_monitoring_flow(self):
        """测试端到端监控流程"""
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        from personal_intelligence_hub.services.monitoring_integration import initialize_monitoring_integration
        from frontend.components.enhanced_monitoring_dashboard import get_enhanced_monitoring_dashboard, MonitoringLevel
        
        # 创建PersonalAssistant服务
        personal_assistant = PersonalAssistantService()
        
        # 模拟后端服务
        with patch('personal_intelligence_hub.services.backend_integration.get_backend_service') as mock_get_backend:
            mock_backend = AsyncMock()
            mock_backend.check_backend_health.return_value = {}
            mock_get_backend.return_value = mock_backend
            
            # 初始化监控集成
            monitoring_service = await initialize_monitoring_integration(personal_assistant)
            
            # 获取监控仪表板
            with patch('frontend.components.enhanced_monitoring_dashboard.get_enhanced_transparency_integration') as mock_get_integration:
                mock_integration = AsyncMock()
                mock_integration.get_monitoring_statistics.return_value = {
                    "is_monitoring": True,
                    "monitoring_level": "detailed"
                }
                mock_get_integration.return_value = mock_integration
                
                dashboard = await get_enhanced_monitoring_dashboard(MonitoringLevel.DETAILED)
                
                # 验证集成状态
                assert monitoring_service.monitoring_active == True
                assert dashboard.is_initialized == True
                
                # 清理
                await dashboard.stop_auto_refresh()
                await monitoring_service.shutdown()
    
    async def test_real_time_monitoring_updates(self):
        """测试实时监控更新"""
        from frontend.components.transparency_monitor import TransparencyMonitor
        from frontend.services.enhanced_transparency_integration import EnhancedTransparencyIntegration, MonitoringLevel
        
        # 创建监控组件
        monitor = TransparencyMonitor()
        integration = EnhancedTransparencyIntegration(monitor, MonitoringLevel.COMPREHENSIVE)
        
        # 模拟实时更新
        with patch('frontend.services.enhanced_transparency_integration.get_backend_service') as mock_get_backend:
            mock_backend = AsyncMock()
            mock_get_backend.return_value = mock_backend
            
            await integration.initialize()
            
            # 模拟多个并发事件
            tasks = []
            for i in range(5):
                call_data = {
                    "call_id": f"concurrent_call_{i}",
                    "model": f"model_{i}",
                    "provider": "test",
                    "input_tokens": 100 + i * 10,
                    "output_tokens": 200 + i * 20,
                    "response_time": 1.0 + i * 0.1,
                    "cost": 0.01 + i * 0.001,
                    "success": True
                }
                tasks.append(integration.log_llm_call(call_data))
            
            # 并发执行
            await asyncio.gather(*tasks)
            
            # 验证所有调用都被记录
            assert len(integration.llm_call_cache) == 5
            
            # 验证性能指标计算
            metrics = await integration._calculate_performance_metrics()
            assert metrics["avg_response_time"] > 0
            assert metrics["success_rate"] == 100.0
            
            await integration.stop_monitoring()


if __name__ == "__main__":
    # 运行测试
    async def run_tests():
        """运行所有测试"""
        logger.info("开始透明度监控系统集成测试")
        
        try:
            # 基础功能测试
            test_class = TestTransparencyMonitoringIntegration()
            
            # 创建模拟对象
            mock_assistant = await test_class.mock_personal_assistant()
            mock_backend = await test_class.mock_backend_service()
            
            # 运行基础测试
            logger.info("测试增强透明度集成初始化...")
            transparency_monitor = await test_class.transparency_monitor()
            await test_class.test_enhanced_transparency_integration_initialization(transparency_monitor)
            logger.info("✅ 增强透明度集成初始化测试通过")
            
            logger.info("测试LLM调用监控...")
            await test_class.test_llm_call_monitoring(transparency_monitor)
            logger.info("✅ LLM调用监控测试通过")
            
            logger.info("测试工作流监控...")
            await test_class.test_workflow_monitoring(transparency_monitor)
            logger.info("✅ 工作流监控测试通过")
            
            logger.info("测试PersonalAssistant监控包装器...")
            await test_class.test_personal_assistant_monitoring_wrapper(mock_assistant)
            logger.info("✅ PersonalAssistant监控包装器测试通过")
            
            logger.info("测试性能指标计算...")
            await test_class.test_performance_metrics_calculation(transparency_monitor)
            logger.info("✅ 性能指标计算测试通过")
            
            # 集成场景测试
            logger.info("测试端到端监控流程...")
            integration_test = TestIntegrationScenarios()
            await integration_test.test_end_to_end_monitoring_flow()
            logger.info("✅ 端到端监控流程测试通过")
            
            logger.info("🎉 所有透明度监控系统集成测试通过！")
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            raise
    
    # 运行测试
    asyncio.run(run_tests())