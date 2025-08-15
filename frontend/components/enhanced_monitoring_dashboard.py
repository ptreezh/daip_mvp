#!/usr/bin/env python3
"""增强监控仪表板

V0.2.2 - 透明度监控系统集成
提供统一的监控界面，集成TransparencyMonitor和EnhancedTransparencyIntegration
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from lona.html import H2, H3, HTML, Div, P, Span
from lona.html.widget import Widget

from frontend.components.transparency_monitor import TransparencyMonitor
from frontend.services.enhanced_transparency_integration import (
    MonitoringLevel,
    get_enhanced_transparency_integration,
)

logger = logging.getLogger(__name__)


class EnhancedMonitoringDashboard(Widget):
    """增强监控仪表板"""
    
    def __init__(self, monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED):
        super().__init__()
        
        self.monitoring_level = monitoring_level
        self.transparency_monitor = None
        self.integration_service = None
        
        # 仪表板状态
        self.is_initialized = False
        self.auto_refresh = True
        self.refresh_interval = 3  # 秒
        self.refresh_task = None
        
        # 显示配置
        self.show_llm_details = True
        self.show_workflow_details = True
        self.show_system_health = True
        self.show_performance_metrics = True
        
        # 数据缓存
        self.dashboard_data = {
            "last_update": datetime.now(),
            "monitoring_stats": {},
            "system_overview": {},
            "recent_activities": []
        }
        
        logger.info(f"Enhanced Monitoring Dashboard initialized with level: {monitoring_level.value}")
    
    async def initialize(self):
        """初始化仪表板"""
        try:
            if self.is_initialized:
                logger.warning("Dashboard already initialized")
                return
            
            # 创建透明度监控器
            self.transparency_monitor = TransparencyMonitor()
            
            # 获取增强集成服务
            self.integration_service = await get_enhanced_transparency_integration(
                self.transparency_monitor, 
                self.monitoring_level
            )
            
            # 设置回调
            self._setup_callbacks()
            
            # 启动自动刷新
            if self.auto_refresh:
                await self.start_auto_refresh()
            
            self.is_initialized = True
            logger.info("Enhanced Monitoring Dashboard initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize dashboard: {e}")
            raise
    
    def _setup_callbacks(self):
        """设置回调函数"""
        try:
            if self.integration_service:
                self.integration_service.on_llm_call_detected = self._on_llm_call_detected
                self.integration_service.on_workflow_status_change = self._on_workflow_status_change
                self.integration_service.on_system_health_change = self._on_system_health_change
            
            logger.info("Dashboard callbacks configured")
            
        except Exception as e:
            logger.error(f"Error setting up callbacks: {e}")
    
    async def start_auto_refresh(self):
        """启动自动刷新"""
        if self.refresh_task and not self.refresh_task.done():
            logger.warning("Auto refresh already running")
            return
        
        self.auto_refresh = True
        self.refresh_task = asyncio.create_task(self._auto_refresh_loop())
        logger.info("Auto refresh started")
    
    async def stop_auto_refresh(self):
        """停止自动刷新"""
        self.auto_refresh = False
        if self.refresh_task and not self.refresh_task.done():
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
        logger.info("Auto refresh stopped")
    
    async def _auto_refresh_loop(self):
        """自动刷新循环"""
        while self.auto_refresh:
            try:
                await self._update_dashboard_data()
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto refresh error: {e}")
                await asyncio.sleep(5)
    
    async def _update_dashboard_data(self):
        """更新仪表板数据"""
        try:
            if not self.integration_service:
                return
            
            # 获取监控统计
            monitoring_stats = self.integration_service.get_monitoring_statistics()
            
            # 更新缓存
            self.dashboard_data.update({
                "last_update": datetime.now(),
                "monitoring_stats": monitoring_stats,
                "system_overview": self._generate_system_overview(monitoring_stats),
                "recent_activities": self._get_recent_activities()
            })
            
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
    
    def _generate_system_overview(self, monitoring_stats: dict[str, Any]) -> dict[str, Any]:
        """生成系统概览"""
        try:
            return {
                "monitoring_status": "🟢 活跃" if monitoring_stats.get("is_monitoring", False) else "🔴 停止",
                "monitoring_level": monitoring_stats.get("monitoring_level", "unknown"),
                "llm_calls_today": monitoring_stats.get("llm_calls_cached", 0),
                "active_workflows": monitoring_stats.get("active_workflows", 0),
                "total_workflows": monitoring_stats.get("total_workflows", 0),
                "system_health": self._format_system_health(monitoring_stats.get("system_health")),
                "uptime": self._calculate_uptime()
            }
        except Exception as e:
            logger.error(f"Error generating system overview: {e}")
            return {}
    
    def _format_system_health(self, health_data: Optional[dict[str, Any]]) -> str:
        """格式化系统健康状态"""
        if not health_data:
            return "🟡 未知"
        
        try:
            backend_status = health_data.get("backend_status", "unknown")
            error_rate = health_data.get("error_rate", 0)
            
            if backend_status == "healthy" and error_rate < 5:
                return "🟢 健康"
            elif backend_status == "degraded" or error_rate < 15:
                return "🟡 降级"
            else:
                return "🔴 异常"
        except Exception:
            return "🟡 未知"
    
    def _calculate_uptime(self) -> str:
        """计算运行时间"""
        try:
            if self.transparency_monitor and hasattr(self.transparency_monitor, 'system_metrics'):
                uptime_start = self.transparency_monitor.system_metrics.get("uptime", datetime.now())
                uptime_delta = datetime.now() - uptime_start
                
                hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return "00:00:00"
        except Exception:
            return "00:00:00"
    
    def _get_recent_activities(self) -> list[dict[str, Any]]:
        """获取最近活动"""
        activities = []
        
        try:
            if self.transparency_monitor:
                # 获取最近的LLM调用
                for call in self.transparency_monitor.llm_calls[-5:]:
                    activities.append({
                        "type": "llm_call",
                        "timestamp": call.get("timestamp", datetime.now()),
                        "description": f"LLM调用: {call.get('model', 'unknown')} ({call.get('response_time', 0):.1f}s)",
                        "status": "success" if call.get("success", True) else "error"
                    })
                
                # 获取最近的工作流活动
                for workflow in self.transparency_monitor.workflow_executions[-3:]:
                    activities.append({
                        "type": "workflow",
                        "timestamp": workflow.get("start_time", datetime.now()),
                        "description": f"工作流: {workflow.get('type', 'unknown')} ({workflow.get('status', 'unknown')})",
                        "status": workflow.get("status", "unknown")
                    })
            
            # 按时间排序
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            return activities[:10]  # 返回最近10条
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            return []
    
    # 回调方法
    async def _on_llm_call_detected(self, llm_metrics):
        """LLM调用检测回调"""
        try:
            logger.debug(f"Dashboard detected LLM call: {llm_metrics.model}")
            # 这里可以添加实时通知逻辑
        except Exception as e:
            logger.error(f"Error in LLM call callback: {e}")
    
    async def _on_workflow_status_change(self, workflow_metrics):
        """工作流状态变更回调"""
        try:
            logger.debug(f"Dashboard detected workflow change: {workflow_metrics.workflow_id}")
            # 这里可以添加实时通知逻辑
        except Exception as e:
            logger.error(f"Error in workflow status callback: {e}")
    
    async def _on_system_health_change(self, health_metrics):
        """系统健康变更回调"""
        try:
            logger.debug("Dashboard detected system health change")
            # 这里可以添加健康状态告警逻辑
        except Exception as e:
            logger.error(f"Error in system health callback: {e}")
    
    def _render_dashboard_header(self) -> HTML:
        """渲染仪表板头部"""
        overview = self.dashboard_data.get("system_overview", {})
        last_update = self.dashboard_data.get("last_update", datetime.now())
        
        return Div(
            H2("🔍 增强监控仪表板", style="color: #2c3e50; margin-bottom: 10px;"),
            Div(
                Span(f"监控状态: {overview.get('monitoring_status', '🟡 未知')}", 
                     style="margin-right: 20px; font-weight: 500;"),
                Span(f"监控级别: {overview.get('monitoring_level', 'unknown').upper()}", 
                     style="margin-right: 20px; font-weight: 500;"),
                Span(f"运行时间: {overview.get('uptime', '00:00:00')}", 
                     style="margin-right: 20px; font-weight: 500;"),
                Span(f"最后更新: {last_update.strftime('%H:%M:%S')}", 
                     style="color: #7f8c8d; font-size: 0.9rem;"),
                style="margin-bottom: 15px; padding: 10px; background: #ecf0f1; border-radius: 6px;"
            ),
            style="margin-bottom: 20px;"
        )
    
    def _render_system_overview_cards(self) -> HTML:
        """渲染系统概览卡片"""
        overview = self.dashboard_data.get("system_overview", {})
        
        cards = [
            ("🏥 系统健康", overview.get("system_health", "🟡 未知"), "#e8f5e8"),
            ("📡 LLM调用", f"{overview.get('llm_calls_today', 0)} 次", "#fff3cd"),
            ("🔄 活跃工作流", f"{overview.get('active_workflows', 0)} 个", "#d1ecf1"),
            ("📊 总工作流", f"{overview.get('total_workflows', 0)} 个", "#f8d7da")
        ]
        
        card_elements = []
        for title, value, bg_color in cards:
            card_elements.append(
                Div(
                    P(title, style="font-weight: 600; margin: 0 0 5px 0; color: #2c3e50; font-size: 0.9rem;"),
                    P(value, style="font-size: 1.2rem; font-weight: 700; margin: 0; color: #34495e;"),
                    style=f"padding: 15px; background: {bg_color}; border-radius: 8px; text-align: center; min-width: 120px;"
                )
            )
        
        return Div(
            H3("📊 系统概览", style="color: #2c3e50; margin-bottom: 10px;"),
            Div(
                *card_elements,
                style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px;"
            )
        )
    
    def _render_recent_activities(self) -> HTML:
        """渲染最近活动"""
        activities = self.dashboard_data.get("recent_activities", [])
        
        if not activities:
            return Div(
                H3("📋 最近活动", style="color: #2c3e50; margin-bottom: 10px;"),
                P("暂无活动记录", style="color: #7f8c8d; font-style: italic; text-align: center; padding: 20px;")
            )
        
        activity_elements = []
        for activity in activities[:8]:  # 显示最近8条
            timestamp = activity.get("timestamp", datetime.now())
            description = activity.get("description", "未知活动")
            status = activity.get("status", "unknown")
            
            # 状态图标
            status_icon = {
                "success": "✅",
                "error": "❌", 
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
                "unknown": "❓"
            }.get(status, "❓")
            
            activity_elements.append(
                Div(
                    Div(
                        Span(status_icon, style="margin-right: 8px;"),
                        Span(description, style="font-weight: 500;"),
                        style="margin-bottom: 3px;"
                    ),
                    P(f"时间: {timestamp.strftime('%H:%M:%S')}", 
                      style="font-size: 0.8rem; color: #7f8c8d; margin: 0;"),
                    style="padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #3498db;"
                )
            )
        
        return Div(
            H3("📋 最近活动", style="color: #2c3e50; margin-bottom: 10px;"),
            Div(
                *activity_elements,
                style="max-height: 300px; overflow-y: auto;"
            )
        )
    
    def _render_monitoring_controls(self) -> HTML:
        """渲染监控控制面板"""
        monitoring_stats = self.dashboard_data.get("monitoring_stats", {})
        is_monitoring = monitoring_stats.get("is_monitoring", False)
        
        return Div(
            H3("🎛️ 监控控制", style="color: #2c3e50; margin-bottom: 10px;"),
            Div(
                Div(
                    P("监控状态", style="font-weight: 600; margin: 0 0 5px 0; color: #2c3e50;"),
                    P("🟢 运行中" if is_monitoring else "🔴 已停止", 
                      style="margin: 0; font-weight: 500;"),
                    style="padding: 10px; background: #e8f5e8 if is_monitoring else #f8d7da; border-radius: 6px;"
                ),
                Div(
                    P("自动刷新", style="font-weight: 600; margin: 0 0 5px 0; color: #2c3e50;"),
                    P(f"🔄 {self.refresh_interval}秒" if self.auto_refresh else "⏹️ 已停止", 
                      style="margin: 0; font-weight: 500;"),
                    style="padding: 10px; background: #fff3cd; border-radius: 6px;"
                ),
                Div(
                    P("缓存状态", style="font-weight: 600; margin: 0 0 5px 0; color: #2c3e50;"),
                    P(f"📦 {monitoring_stats.get('llm_calls_cached', 0)} 条记录", 
                      style="margin: 0; font-weight: 500;"),
                    style="padding: 10px; background: #d1ecf1; border-radius: 6px;"
                ),
                style="display: flex; gap: 15px; flex-wrap: wrap;"
            ),
            style="margin-bottom: 20px;"
        )
    
    def _render_detailed_transparency_monitor(self) -> HTML:
        """渲染详细透明度监控器"""
        if not self.transparency_monitor:
            return Div(
                P("透明度监控器未初始化", style="color: #e74c3c; text-align: center; padding: 20px;")
            )
        
        return Div(
            H3("🔍 详细监控信息", style="color: #2c3e50; margin-bottom: 10px;"),
            Div(
                self.transparency_monitor.render(),
                style="border: 1px solid #bdc3c7; border-radius: 8px; padding: 15px; background: white;"
            )
        )

    def render(self) -> HTML:
        """渲染仪表板"""
        if not self.is_initialized:
            return Div(
                H2("🔍 增强监控仪表板", style="color: #2c3e50;"),
                P("正在初始化监控系统...", style="color: #7f8c8d; text-align: center; padding: 40px;"),
                style="padding: 20px;"
            )
        
        return Div(
            # 仪表板头部
            self._render_dashboard_header(),
            
            # 系统概览卡片
            self._render_system_overview_cards(),
            
            # 监控控制面板
            self._render_monitoring_controls(),
            
            # 最近活动
            self._render_recent_activities(),
            
            # 详细透明度监控器（可选）
            self._render_detailed_transparency_monitor() if self.show_system_health else Div(),
            
            _class="enhanced-monitoring-dashboard",
            style="padding: 20px; background: #f8f9fa; min-height: 100vh;"
        )


# 全局仪表板实例
_enhanced_monitoring_dashboard: Optional[EnhancedMonitoringDashboard] = None


async def get_enhanced_monitoring_dashboard(
    monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED
) -> EnhancedMonitoringDashboard:
    """获取增强监控仪表板实例"""
    global _enhanced_monitoring_dashboard
    
    if _enhanced_monitoring_dashboard is None:
        _enhanced_monitoring_dashboard = EnhancedMonitoringDashboard(monitoring_level)
        await _enhanced_monitoring_dashboard.initialize()
    
    return _enhanced_monitoring_dashboard


async def cleanup_enhanced_monitoring_dashboard():
    """清理增强监控仪表板"""
    global _enhanced_monitoring_dashboard
    
    if _enhanced_monitoring_dashboard:
        await _enhanced_monitoring_dashboard.stop_auto_refresh()
        _enhanced_monitoring_dashboard = None