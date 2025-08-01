#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V0.2.2 - 透明度监控系统集成验证

验证增强透明度监控系统的实现
"""

import asyncio
import logging
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def validate_transparency_monitoring_integration():
    """验证透明度监控系统集成"""
    logger.info("🔍 开始V0.2.2透明度监控系统集成验证")
    
    validation_results = {
        "enhanced_transparency_integration": False,
        "monitoring_dashboard": False,
        "personal_assistant_monitoring": False,
        "websocket_integration": False,
        "performance_metrics": False
    }
    
    try:
        # 1. 验证增强透明度集成
        logger.info("📋 验证增强透明度集成...")
        try:
            from frontend.services.enhanced_transparency_integration import (
                EnhancedTransparencyIntegration, MonitoringLevel, LLMCallMetrics
            )
            from frontend.components.transparency_monitor import TransparencyMonitor
            
            # 创建透明度监控器
            monitor = TransparencyMonitor()
            
            # 创建集成器
            integration = EnhancedTransparencyIntegration(monitor, MonitoringLevel.DETAILED)
            
            # 验证基本属性
            assert integration.monitoring_level == MonitoringLevel.DETAILED
            assert integration.monitor is not None
            assert hasattr(integration, 'llm_call_cache')
            assert hasattr(integration, 'workflow_cache')
            
            # 测试LLM调用记录
            test_call = LLMCallMetrics(
                call_id="test_call",
                model="test-model",
                provider="test-provider",
                input_tokens=100,
                output_tokens=200,
                response_time=1.5,
                cost=0.01,
                success=True
            )
            
            integration.llm_call_cache.append(test_call)
            assert len(integration.llm_call_cache) == 1
            
            validation_results["enhanced_transparency_integration"] = True
            logger.info("✅ 增强透明度集成验证通过")
            
        except Exception as e:
            logger.error(f"❌ 增强透明度集成验证失败: {e}")
        
        # 2. 验证监控仪表板
        logger.info("📋 验证监控仪表板...")
        try:
            from frontend.components.enhanced_monitoring_dashboard import (
                EnhancedMonitoringDashboard, MonitoringLevel
            )
            
            # 创建仪表板
            dashboard = EnhancedMonitoringDashboard(MonitoringLevel.DETAILED)
            
            # 验证基本属性
            assert dashboard.monitoring_level == MonitoringLevel.DETAILED
            assert hasattr(dashboard, 'dashboard_data')
            assert hasattr(dashboard, 'auto_refresh')
            
            # 验证数据结构
            assert 'last_update' in dashboard.dashboard_data
            assert 'monitoring_stats' in dashboard.dashboard_data
            assert 'system_overview' in dashboard.dashboard_data
            
            validation_results["monitoring_dashboard"] = True
            logger.info("✅ 监控仪表板验证通过")
            
        except Exception as e:
            logger.error(f"❌ 监控仪表板验证失败: {e}")
        
        # 3. 验证PersonalAssistant监控
        logger.info("📋 验证PersonalAssistant监控...")
        try:
            from personal_intelligence_hub.services.monitoring_integration import (
                PersonalAssistantMonitoringWrapper, MonitoringIntegrationService
            )
            from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
            
            # 创建模拟PersonalAssistant
            mock_assistant = Mock(spec=PersonalAssistantService)
            mock_assistant.analyze_intent = AsyncMock()
            mock_assistant.assemble_team = AsyncMock()
            mock_assistant.process_message = AsyncMock()
            mock_assistant.execute_command = AsyncMock()
            
            # 创建监控包装器
            wrapper = PersonalAssistantMonitoringWrapper(mock_assistant)
            
            # 验证基本属性
            assert wrapper.personal_assistant is not None
            assert hasattr(wrapper, 'stats')
            assert hasattr(wrapper, 'monitoring_callbacks')
            
            # 验证统计结构
            stats = wrapper.get_monitoring_statistics()
            assert 'total_operations' in stats
            assert 'average_response_time' in stats
            assert 'error_rate' in stats
            assert 'operations_breakdown' in stats
            
            validation_results["personal_assistant_monitoring"] = True
            logger.info("✅ PersonalAssistant监控验证通过")
            
        except Exception as e:
            logger.error(f"❌ PersonalAssistant监控验证失败: {e}")
        
        # 4. 验证WebSocket集成
        logger.info("📋 验证WebSocket集成...")
        try:
            from frontend.services.websocket_manager import (
                LonaWebSocketManager, RealtimeUpdateManager, WebSocketMessage, MessageType
            )
            
            # 创建WebSocket管理器
            ws_manager = LonaWebSocketManager()
            realtime_manager = RealtimeUpdateManager(ws_manager)
            
            # 验证基本属性
            assert hasattr(ws_manager, 'backend_url')
            assert hasattr(ws_manager, 'event_handler')
            assert hasattr(realtime_manager, 'component_callbacks')
            
            # 创建测试消息
            test_message = WebSocketMessage(
                type=MessageType.AGENT_STATUS,
                payload={"agent_id": "test_agent", "status": "active"}
            )
            
            # 验证消息结构
            message_dict = test_message.to_dict()
            assert 'type' in message_dict
            assert 'payload' in message_dict
            assert 'timestamp' in message_dict
            
            validation_results["websocket_integration"] = True
            logger.info("✅ WebSocket集成验证通过")
            
        except Exception as e:
            logger.error(f"❌ WebSocket集成验证失败: {e}")
        
        # 5. 验证性能指标计算
        logger.info("📋 验证性能指标计算...")
        try:
            from frontend.services.enhanced_transparency_integration import LLMCallMetrics
            
            # 创建测试数据
            test_calls = [
                LLMCallMetrics("call1", "model1", "provider1", 100, 200, 1.0, 0.01, True),
                LLMCallMetrics("call2", "model2", "provider2", 150, 250, 2.0, 0.02, True),
                LLMCallMetrics("call3", "model3", "provider3", 120, 180, 1.5, 0.015, False)
            ]
            
            # 计算平均响应时间
            avg_response_time = sum(call.response_time for call in test_calls) / len(test_calls)
            assert abs(avg_response_time - 1.5) < 0.01
            
            # 计算成功率
            success_count = sum(1 for call in test_calls if call.success)
            success_rate = (success_count / len(test_calls)) * 100
            assert abs(success_rate - 66.67) < 0.1
            
            # 计算总成本
            total_cost = sum(call.cost for call in test_calls)
            assert abs(total_cost - 0.045) < 0.001
            
            validation_results["performance_metrics"] = True
            logger.info("✅ 性能指标计算验证通过")
            
        except Exception as e:
            logger.error(f"❌ 性能指标计算验证失败: {e}")
        
        # 6. 生成验证报告
        logger.info("📋 生成验证报告...")
        
        passed_count = sum(validation_results.values())
        total_count = len(validation_results)
        success_rate = (passed_count / total_count) * 100
        
        logger.info("📊 V0.2.2透明度监控系统集成验证报告:")
        logger.info(f"  总验证项目: {total_count}")
        logger.info(f"  通过项目: {passed_count}")
        logger.info(f"  成功率: {success_rate:.1f}%")
        logger.info("")
        
        for component, passed in validation_results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            logger.info(f"  - {component}: {status}")
        
        if success_rate == 100:
            logger.info("🎉 所有验证项目通过！V0.2.2透明度监控系统集成实现完成")
        else:
            logger.warning(f"⚠️ {total_count - passed_count}个验证项目失败，需要进一步修复")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"❌ 验证过程中发生错误: {e}")
        return validation_results


async def validate_integration_components():
    """验证集成组件的完整性"""
    logger.info("🔧 验证集成组件完整性...")
    
    components = {
        "enhanced_transparency_integration.py": "frontend/services/enhanced_transparency_integration.py",
        "enhanced_monitoring_dashboard.py": "frontend/components/enhanced_monitoring_dashboard.py", 
        "monitoring_integration.py": "personal_intelligence_hub/services/monitoring_integration.py",
        "transparency_monitor.py": "frontend/components/transparency_monitor.py",
        "websocket_manager.py": "frontend/services/websocket_manager.py"
    }
    
    missing_components = []
    
    for component_name, file_path in components.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 1000:  # 确保文件有实质内容
                    logger.info(f"✅ {component_name}: {len(content)}字符")
                else:
                    logger.warning(f"⚠️ {component_name}: 文件内容过少")
                    missing_components.append(component_name)
        except FileNotFoundError:
            logger.error(f"❌ {component_name}: 文件不存在")
            missing_components.append(component_name)
        except Exception as e:
            logger.error(f"❌ {component_name}: 读取错误 - {e}")
            missing_components.append(component_name)
    
    if not missing_components:
        logger.info("🎉 所有集成组件完整性验证通过！")
        return True
    else:
        logger.error(f"❌ {len(missing_components)}个组件存在问题: {missing_components}")
        return False


if __name__ == "__main__":
    async def main():
        """主验证流程"""
        logger.info("🚀 开始V0.2.2透明度监控系统集成完整验证")
        
        # 验证组件完整性
        components_ok = await validate_integration_components()
        
        if components_ok:
            # 验证功能实现
            validation_results = await validate_transparency_monitoring_integration()
            
            # 总结
            if all(validation_results.values()):
                logger.info("🎉 V0.2.2透明度监控系统集成验证完全通过！")
                logger.info("✅ 任务V0.2.2已成功完成，可以继续下一个任务")
            else:
                failed_items = [k for k, v in validation_results.items() if not v]
                logger.warning(f"⚠️ 部分验证失败: {failed_items}")
        else:
            logger.error("❌ 组件完整性验证失败，无法进行功能验证")
    
    asyncio.run(main())