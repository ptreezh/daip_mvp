#!/usr/bin/env python3
"""V0.2.2 - 透明度监控系统集成演示

演示增强透明度监控系统的完整功能
"""

import asyncio
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_transparency_monitoring_integration():
    """演示透明度监控系统集成"""
    logger.info("🚀 开始V0.2.2透明度监控系统集成演示")
    
    try:
        # 1. 初始化PersonalAssistant服务
        logger.info("📋 步骤1: 初始化PersonalAssistant服务")
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        personal_assistant = PersonalAssistantService()
        logger.info("✅ PersonalAssistant服务初始化完成")
        
        # 2. 初始化监控集成
        logger.info("📋 步骤2: 初始化监控集成服务")
        from personal_intelligence_hub.services.monitoring_integration import initialize_monitoring_integration
        
        monitoring_service = await initialize_monitoring_integration(personal_assistant)
        wrapped_assistant = monitoring_service.get_wrapped_personal_assistant()
        logger.info("✅ 监控集成服务初始化完成")
        
        # 3. 创建透明度监控器
        logger.info("📋 步骤3: 创建透明度监控器")
        from frontend.components.transparency_monitor import TransparencyMonitor
        
        transparency_monitor = TransparencyMonitor()
        await transparency_monitor.start_monitoring()
        logger.info("✅ 透明度监控器启动完成")
        
        # 4. 创建增强透明度集成
        logger.info("📋 步骤4: 创建增强透明度集成")
        from frontend.services.enhanced_transparency_integration import (
            MonitoringLevel,
            get_enhanced_transparency_integration,
        )
        
        enhanced_integration = await get_enhanced_transparency_integration(
            transparency_monitor, MonitoringLevel.DETAILED
        )
        logger.info("✅ 增强透明度集成创建完成")
        
        # 5. 演示监控功能
        logger.info("📋 步骤5: 演示监控功能")
        
        # 演示意图分析监控
        logger.info("🔍 演示意图分析监控...")
        intent_result = await wrapped_assistant.analyze_intent(
            "请分析人工智能在教育领域的应用前景",
            {"session_id": "demo_session_1"}
        )
        logger.info(f"意图分析结果: {intent_result.workflowType.value} (置信度: {intent_result.confidence})")
        
        # 演示团队组建监控
        logger.info("👥 演示团队组建监控...")
        team_result = await wrapped_assistant.assemble_team(
            "人工智能教育应用", intent_result.workflowType
        )
        logger.info(f"团队组建结果: {len(team_result.agents)}个专家 (多样性: {team_result.diversity_score})")
        
        # 演示LLM调用监控
        logger.info("🤖 演示LLM调用监控...")
        await enhanced_integration.log_llm_call({
            "call_id": "demo_llm_call_1",
            "model": "gpt-4",
            "provider": "openai",
            "input_tokens": 150,
            "output_tokens": 300,
            "response_time": 2.1,
            "cost": 0.021,
            "success": True
        })
        logger.info("LLM调用已记录到监控系统")
        
        # 演示工作流监控
        logger.info("🔄 演示工作流监控...")
        await enhanced_integration.log_workflow_start({
            "workflow_id": "demo_workflow_1",
            "workflow_type": "critical_review",
            "participants": team_result.agents
        })
        logger.info("工作流开始已记录到监控系统")
        
        # 6. 获取监控统计
        logger.info("📋 步骤6: 获取监控统计")
        
        # PersonalAssistant统计
        pa_stats = wrapped_assistant.get_monitoring_statistics()
        logger.info(f"PersonalAssistant统计: {pa_stats['total_operations']}次操作, "
                   f"平均响应时间: {pa_stats['average_response_time']:.2f}s")
        
        # 集成服务统计
        integration_stats = enhanced_integration.get_monitoring_statistics()
        logger.info(f"集成服务统计: 监控级别: {integration_stats['monitoring_level']}, "
                   f"缓存调用: {integration_stats['llm_calls_cached']}条")
        
        # 透明度数据
        transparency_data = await monitoring_service.get_transparency_data()
        logger.info(f"透明度数据: 监控活跃: {transparency_data['monitoring_active']}, "
                   f"最近事件: {len(transparency_data['recent_events'])}条")
        
        # 7. 演示实时监控更新
        logger.info("📋 步骤7: 演示实时监控更新")
        
        # 模拟多个并发操作
        tasks = []
        for i in range(3):
            task = wrapped_assistant.process_message(
                f"测试消息 {i+1}: 请解释机器学习的基本概念",
                f"demo_session_{i+1}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        logger.info(f"并发处理完成: {len(results)}个响应")
        
        # 8. 显示最终统计
        logger.info("📋 步骤8: 显示最终统计")
        
        final_pa_stats = wrapped_assistant.get_monitoring_statistics()
        final_integration_stats = enhanced_integration.get_monitoring_statistics()
        
        logger.info("📊 最终统计报告:")
        logger.info(f"  - 总操作数: {final_pa_stats['total_operations']}")
        logger.info(f"  - 意图分析: {final_pa_stats['operations_breakdown']['intent_analyses']}次")
        logger.info(f"  - 团队组建: {final_pa_stats['operations_breakdown']['team_assemblies']}次")
        logger.info(f"  - 消息处理: {final_pa_stats['operations_breakdown']['message_processes']}次")
        logger.info(f"  - 平均响应时间: {final_pa_stats['average_response_time']:.2f}秒")
        logger.info(f"  - 错误率: {final_pa_stats['error_rate']:.1f}%")
        logger.info(f"  - 活跃会话: {final_pa_stats['active_sessions']}个")
        logger.info(f"  - LLM调用缓存: {final_integration_stats['llm_calls_cached']}条")
        logger.info(f"  - 活跃工作流: {final_integration_stats['active_workflows']}个")
        
        # 9. 清理资源
        logger.info("📋 步骤9: 清理资源")
        await transparency_monitor.stop_monitoring()
        await enhanced_integration.stop_monitoring()
        await monitoring_service.shutdown()
        logger.info("✅ 资源清理完成")
        
        logger.info("🎉 V0.2.2透明度监控系统集成演示完成！")
        
    except Exception as e:
        logger.error(f"❌ 演示过程中发生错误: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(demo_transparency_monitoring_integration())