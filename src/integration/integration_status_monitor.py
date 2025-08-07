#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 22:15:00
@Author  : DAIP-LIVE Team
@File    : integration_status_monitor.py
@Description:
    集成状态监控器 - 实时监控新服务集成状态和健康状况
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class ServiceHealthMetrics:
    """服务健康指标"""
    service_name: str
    availability_rate: float = 0.0  # 可用性百分比
    average_response_time: float = 0.0  # 平均响应时间(ms)
    error_count: int = 0  # 错误次数
    last_successful_check: Optional[datetime] = None
    last_error: Optional[str] = None
    check_count: int = 0
    success_count: int = 0

@dataclass 
class IntegrationMonitorConfig:
    """监控配置"""
    check_interval_seconds: int = 30  # 检查间隔
    health_check_timeout: float = 5.0  # 健康检查超时
    max_error_threshold: int = 5  # 最大错误阈值
    enable_logging: bool = True
    enable_metrics_persistence: bool = True
    metrics_file: str = "data/integration_metrics.json"

class IntegrationStatusMonitor:
    """
    集成状态监控器
    
    负责持续监控新服务的集成状态、健康状况和性能指标。
    """
    
    def __init__(self, app_state: Any, config: IntegrationMonitorConfig = None):
        self.app_state = app_state
        self.config = config or IntegrationMonitorConfig()
        
        # 监控状态
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # 健康指标
        self.service_metrics: Dict[str, ServiceHealthMetrics] = {}
        self.monitoring_start_time: Optional[datetime] = None
        
        # 初始化监控服务列表
        self._init_service_metrics()
        
        logger.info("IntegrationStatusMonitor 初始化完成")
    
    def _init_service_metrics(self):
        """初始化服务指标"""
        monitored_services = [
            "prompt_building_service",
            "autonomous_role_creation_system",
            "enhanced_memory_manager", 
            "interactive_experience_optimizer"
        ]
        
        for service_name in monitored_services:
            self.service_metrics[service_name] = ServiceHealthMetrics(
                service_name=service_name
            )
    
    async def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            logger.warning("监控已在运行")
            return
        
        self.is_monitoring = True
        self.monitoring_start_time = datetime.now()
        
        logger.info(f"开始监控服务状态，检查间隔: {self.config.check_interval_seconds}秒")
        
        # 启动监控任务
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("监控已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        try:
            while self.is_monitoring:
                await self._perform_health_checks()
                
                if self.config.enable_metrics_persistence:
                    await self._save_metrics()
                
                await asyncio.sleep(self.config.check_interval_seconds)
                
        except asyncio.CancelledError:
            logger.info("监控循环被取消")
        except Exception as e:
            logger.error(f"监控循环异常: {e}")
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        check_time = datetime.now()
        
        for service_name, metrics in self.service_metrics.items():
            await self._check_service_health(service_name, metrics, check_time)
    
    async def _check_service_health(
        self, 
        service_name: str, 
        metrics: ServiceHealthMetrics, 
        check_time: datetime
    ):
        """检查单个服务健康状态"""
        try:
            # 获取服务实例
            service = getattr(self.app_state, service_name, None)
            if service is None:
                self._record_service_error(metrics, "Service not available", check_time)
                return
            
            # 执行健康检查
            start_time = time.time()
            
            health_check_result = await asyncio.wait_for(
                self._call_service_health_check(service),
                timeout=self.config.health_check_timeout
            )
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 更新指标
            self._update_service_metrics(metrics, health_check_result, response_time, check_time)
            
        except asyncio.TimeoutError:
            self._record_service_error(metrics, "Health check timeout", check_time)
        except Exception as e:
            self._record_service_error(metrics, str(e), check_time)
    
    async def _call_service_health_check(self, service: Any) -> Dict[str, Any]:
        """调用服务健康检查方法"""
        # 尝试不同的健康检查方法
        if hasattr(service, 'get_service_status'):
            return await service.get_service_status()
        elif hasattr(service, 'get_system_status'):
            return await service.get_system_status()
        elif hasattr(service, 'health_check'):
            return await service.health_check()
        else:
            # 简单的存在性检查
            return {"status": "available", "message": "Service exists"}
    
    def _update_service_metrics(
        self,
        metrics: ServiceHealthMetrics,
        health_result: Dict[str, Any],
        response_time: float,
        check_time: datetime
    ):
        """更新服务指标"""
        metrics.check_count += 1
        
        # 检查健康状态
        is_healthy = health_result.get("status") in ["healthy", "available"]
        
        if is_healthy:
            metrics.success_count += 1
            metrics.last_successful_check = check_time
            
            # 更新响应时间（移动平均）
            if metrics.average_response_time == 0:
                metrics.average_response_time = response_time
            else:
                metrics.average_response_time = (
                    metrics.average_response_time * 0.8 + response_time * 0.2
                )
        else:
            self._record_service_error(
                metrics, 
                health_result.get("error", "Unknown health check failure"),
                check_time
            )
        
        # 计算可用性
        metrics.availability_rate = (
            metrics.success_count / metrics.check_count * 100
        ) if metrics.check_count > 0 else 0
    
    def _record_service_error(
        self,
        metrics: ServiceHealthMetrics,
        error_message: str,
        check_time: datetime
    ):
        """记录服务错误"""
        metrics.check_count += 1
        metrics.error_count += 1
        metrics.last_error = error_message
        
        # 重新计算可用性
        metrics.availability_rate = (
            metrics.success_count / metrics.check_count * 100
        ) if metrics.check_count > 0 else 0
        
        if self.config.enable_logging:
            logger.warning(f"服务 {metrics.service_name} 健康检查失败: {error_message}")
    
    async def _save_metrics(self):
        """保存指标到文件"""
        try:
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_duration": str(datetime.now() - self.monitoring_start_time) if self.monitoring_start_time else None,
                "services": {}
            }
            
            for service_name, metrics in self.service_metrics.items():
                metrics_data["services"][service_name] = {
                    "availability_rate": metrics.availability_rate,
                    "average_response_time": metrics.average_response_time,
                    "error_count": metrics.error_count,
                    "check_count": metrics.check_count,
                    "success_count": metrics.success_count,
                    "last_successful_check": metrics.last_successful_check.isoformat() if metrics.last_successful_check else None,
                    "last_error": metrics.last_error
                }
            
            # 确保目录存在
            metrics_file = Path(self.config.metrics_file)
            metrics_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存数据
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"保存指标失败: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前监控状态"""
        return {
            "is_monitoring": self.is_monitoring,
            "monitoring_duration": str(datetime.now() - self.monitoring_start_time) if self.monitoring_start_time else None,
            "check_interval": self.config.check_interval_seconds,
            "services": {
                name: {
                    "availability_rate": f"{metrics.availability_rate:.2f}%",
                    "average_response_time": f"{metrics.average_response_time:.2f}ms",
                    "error_count": metrics.error_count,
                    "total_checks": metrics.check_count,
                    "last_successful_check": metrics.last_successful_check.isoformat() if metrics.last_successful_check else None,
                    "last_error": metrics.last_error,
                    "health_status": self._get_service_health_status(metrics)
                }
                for name, metrics in self.service_metrics.items()
            }
        }
    
    def _get_service_health_status(self, metrics: ServiceHealthMetrics) -> str:
        """获取服务健康状态"""
        if metrics.check_count == 0:
            return "unknown"
        elif metrics.availability_rate >= 95:
            return "excellent"
        elif metrics.availability_rate >= 90:
            return "good" 
        elif metrics.availability_rate >= 70:
            return "degraded"
        else:
            return "poor"
    
    def get_service_alerts(self) -> List[Dict[str, Any]]:
        """获取服务告警"""
        alerts = []
        
        for service_name, metrics in self.service_metrics.items():
            # 可用性告警
            if metrics.availability_rate < 90 and metrics.check_count >= 3:
                alerts.append({
                    "service": service_name,
                    "type": "availability",
                    "severity": "high" if metrics.availability_rate < 70 else "medium",
                    "message": f"可用性低于阈值: {metrics.availability_rate:.2f}%",
                    "details": {
                        "availability_rate": metrics.availability_rate,
                        "error_count": metrics.error_count,
                        "total_checks": metrics.check_count
                    }
                })
            
            # 错误数量告警
            if metrics.error_count >= self.config.max_error_threshold:
                alerts.append({
                    "service": service_name,
                    "type": "errors",
                    "severity": "high",
                    "message": f"错误次数超过阈值: {metrics.error_count}",
                    "details": {
                        "error_count": metrics.error_count,
                        "last_error": metrics.last_error
                    }
                })
            
            # 响应时间告警
            if metrics.average_response_time > 1000:  # 超过1秒
                alerts.append({
                    "service": service_name,
                    "type": "performance",
                    "severity": "medium",
                    "message": f"平均响应时间过长: {metrics.average_response_time:.2f}ms",
                    "details": {
                        "average_response_time": metrics.average_response_time
                    }
                })
        
        return alerts
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """生成健康报告"""
        alerts = self.get_service_alerts()
        status = self.get_current_status()
        
        # 计算总体健康分数
        total_availability = sum(
            metrics.availability_rate for metrics in self.service_metrics.values()
        )
        average_availability = total_availability / len(self.service_metrics) if self.service_metrics else 0
        
        overall_health = "excellent"
        if average_availability < 70:
            overall_health = "poor"
        elif average_availability < 90:
            overall_health = "degraded"
        elif average_availability < 95:
            overall_health = "good"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.is_monitoring,
            "overall_health": overall_health,
            "average_availability": f"{average_availability:.2f}%",
            "total_alerts": len(alerts),
            "alerts": alerts,
            "service_details": status["services"],
            "recommendations": self._generate_recommendations(alerts)
        }
        
        return report
    
    def _generate_recommendations(self, alerts: List[Dict[str, Any]]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        availability_issues = [a for a in alerts if a["type"] == "availability"]
        error_issues = [a for a in alerts if a["type"] == "errors"]
        performance_issues = [a for a in alerts if a["type"] == "performance"]
        
        if availability_issues:
            recommendations.append("检查服务依赖和配置，确保服务正常启动")
        
        if error_issues:
            recommendations.append("查看错误日志，修复导致服务失败的问题")
            
        if performance_issues:
            recommendations.append("优化服务性能，考虑增加缓存或并行处理")
        
        if not alerts:
            recommendations.append("所有服务运行良好，继续保持当前配置")
        
        return recommendations

# 工厂函数
def create_integration_monitor(
    app_state: Any, 
    config: IntegrationMonitorConfig = None
) -> IntegrationStatusMonitor:
    """创建集成状态监控器"""
    return IntegrationStatusMonitor(app_state, config)