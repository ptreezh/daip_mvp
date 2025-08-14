"""透明度监控系统

提供实时的LLM调用透明度监控，包括调用状态、参数、Token消耗、成本和响应时间的详细展示。
"""

import asyncio
import json
import logging
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from .real_llm_integrator import LLMCallRecord, RealLLMIntegrator

logger = logging.getLogger(__name__)


@dataclass
class TransparencyEvent:
    """透明度事件"""

    event_id: str
    event_type: str  # call_started, call_completed, call_failed, metrics_updated
    timestamp: datetime
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class RealTimeMetrics:
    """实时指标"""

    current_active_calls: int = 0
    calls_per_minute: float = 0.0
    average_response_time_ms: float = 0.0
    success_rate_last_hour: float = 0.0
    total_cost_today: float = 0.0
    total_tokens_today: int = 0
    provider_distribution: Dict[str, int] = None

    def __post_init__(self):
        if self.provider_distribution is None:
            self.provider_distribution = {}


class TransparencyMonitor:
    """透明度监控系统
    
    提供LLM调用的完整透明度监控，包括实时状态显示、性能指标跟踪、
    成本分析和调用验证功能。
    """

    def __init__(self, llm_integrator: RealLLMIntegrator):
        """初始化透明度监控器
        
        Args:
            llm_integrator: LLM集成器实例

        """
        self.llm_integrator = llm_integrator
        self.events: deque = deque(maxlen=1000)  # 保留最近1000个事件
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.subscribers: List[Callable] = []
        self.real_time_metrics = RealTimeMetrics()

        # 启动监控任务
        self._monitoring_task = None
        self._start_monitoring()

        logger.info("TransparencyMonitor initialized")

    def _start_monitoring(self):
        """启动监控任务"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                await self._update_real_time_metrics()
                await asyncio.sleep(1)  # 每秒更新一次
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # 错误时等待更长时间

    async def _update_real_time_metrics(self):
        """更新实时指标"""
        now = datetime.now()

        # 获取最近的调用记录
        recent_records = [
            record for record in self.llm_integrator.call_records
            if (now - record.timestamp).total_seconds() <= 3600  # 最近1小时
        ]

        # 计算指标
        self.real_time_metrics.current_active_calls = len(self.active_calls)

        # 每分钟调用数
        minute_ago = now - timedelta(minutes=1)
        calls_last_minute = [
            record for record in recent_records
            if record.timestamp >= minute_ago
        ]
        self.real_time_metrics.calls_per_minute = len(calls_last_minute)

        # 平均响应时间
        if recent_records:
            self.real_time_metrics.average_response_time_ms = sum(
                record.duration_ms for record in recent_records
            ) / len(recent_records)

        # 成功率
        if recent_records:
            successful = sum(1 for record in recent_records if record.success)
            self.real_time_metrics.success_rate_last_hour = successful / len(recent_records)

        # 今日成本和Token
        today = now.date()
        today_records = [
            record for record in self.llm_integrator.call_records
            if record.timestamp.date() == today
        ]

        self.real_time_metrics.total_cost_today = sum(
            record.cost_usd for record in today_records
        )
        self.real_time_metrics.total_tokens_today = sum(
            record.input_tokens + record.output_tokens for record in today_records
        )

        # 提供商分布
        provider_counts = defaultdict(int)
        for record in today_records:
            provider_counts[record.provider] += 1
        self.real_time_metrics.provider_distribution = dict(provider_counts)

        # 发送指标更新事件
        await self._emit_event("metrics_updated", {
            "metrics": asdict(self.real_time_metrics)
        })

    async def monitor_llm_call(
        self,
        call_id: str,
        provider: str,
        model: str,
        prompt: str,
        parameters: Dict[str, Any]
    ):
        """监控LLM调用开始
        
        Args:
            call_id: 调用ID
            provider: 提供商
            model: 模型名称
            prompt: 输入提示
            parameters: 调用参数

        """
        call_info = {
            "call_id": call_id,
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "parameters": parameters,
            "start_time": datetime.now(),
            "status": "active"
        }

        self.active_calls[call_id] = call_info

        await self._emit_event("call_started", {
            "call_id": call_id,
            "provider": provider,
            "model": model,
            "prompt_length": len(prompt),
            "parameters": parameters
        })

        logger.info(f"Monitoring LLM call started: {call_id}")

    async def record_llm_call_completion(self, record: LLMCallRecord):
        """记录LLM调用完成
        
        Args:
            record: 调用记录

        """
        # 移除活跃调用
        if record.call_id in self.active_calls:
            del self.active_calls[record.call_id]

        event_type = "call_completed" if record.success else "call_failed"

        await self._emit_event(event_type, {
            "call_id": record.call_id,
            "provider": record.provider,
            "model": record.model,
            "success": record.success,
            "duration_ms": record.duration_ms,
            "input_tokens": record.input_tokens,
            "output_tokens": record.output_tokens,
            "cost_usd": record.cost_usd,
            "error_message": record.error_message,
            "response_length": len(record.response) if record.response else 0
        })

        logger.info(f"LLM call completed: {record.call_id}, success: {record.success}")

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """发送事件"""
        event = TransparencyEvent(
            event_id=f"{datetime.now().timestamp()}_{event_type}",
            event_type=event_type,
            timestamp=datetime.now(),
            data=data
        )

        self.events.append(event)

        # 通知订阅者
        for subscriber in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")

    def subscribe(self, callback: Callable):
        """订阅透明度事件
        
        Args:
            callback: 回调函数

        """
        self.subscribers.append(callback)
        logger.info(f"New subscriber added, total: {len(self.subscribers)}")

    def unsubscribe(self, callback: Callable):
        """取消订阅"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            logger.info(f"Subscriber removed, total: {len(self.subscribers)}")

    def get_real_time_status(self) -> Dict[str, Any]:
        """获取实时状态"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_calls": len(self.active_calls),
            "active_call_details": [
                {
                    "call_id": call_id,
                    "provider": info["provider"],
                    "model": info["model"],
                    "duration_seconds": (datetime.now() - info["start_time"]).total_seconds(),
                    "status": info["status"]
                }
                for call_id, info in self.active_calls.items()
            ],
            "metrics": asdict(self.real_time_metrics),
            "recent_events_count": len(self.events)
        }

    def get_call_transparency_report(self, call_id: str) -> Dict[str, Any]:
        """获取特定调用的透明度报告
        
        Args:
            call_id: 调用ID
            
        Returns:
            透明度报告

        """
        # 查找调用记录
        record = next(
            (r for r in self.llm_integrator.call_records if r.call_id == call_id),
            None
        )

        if not record:
            return {"error": "Call record not found"}

        # 查找相关事件
        related_events = [
            event.to_dict() for event in self.events
            if event.data.get("call_id") == call_id
        ]

        # 验证调用真实性
        verification = self.llm_integrator.verify_call_authenticity(call_id)

        return {
            "call_record": record.to_dict(),
            "related_events": related_events,
            "verification": verification,
            "transparency_score": self._calculate_transparency_score(record, related_events),
            "audit_trail": {
                "call_signature": record.get_signature(),
                "event_count": len(related_events),
                "monitoring_complete": len(related_events) >= 2  # 至少有开始和结束事件
            }
        }

    def _calculate_transparency_score(
        self, record: LLMCallRecord, events: List[Dict[str, Any]]
    ) -> float:
        """计算透明度分数"""
        score = 0.0

        # 基础分数：有完整记录
        if record:
            score += 40.0

        # 事件完整性
        event_types = {event["event_type"] for event in events}
        if "call_started" in event_types:
            score += 20.0
        if "call_completed" in event_types or "call_failed" in event_types:
            score += 20.0

        # 数据完整性
        if record and record.input_tokens > 0:
            score += 10.0
        if record and record.duration_ms > 0:
            score += 10.0

        return min(score, 100.0)

    def get_performance_dashboard(self) -> Dict[str, Any]:
        """获取性能仪表板数据"""
        now = datetime.now()

        # 时间段分析
        time_periods = {
            "last_hour": now - timedelta(hours=1),
            "last_day": now - timedelta(days=1),
            "last_week": now - timedelta(weeks=1)
        }

        dashboard_data = {
            "current_status": self.get_real_time_status(),
            "time_series_data": {},
            "provider_analysis": {},
            "cost_analysis": {},
            "performance_trends": {}
        }

        for period_name, start_time in time_periods.items():
            period_records = [
                record for record in self.llm_integrator.call_records
                if record.timestamp >= start_time
            ]

            if period_records:
                dashboard_data["time_series_data"][period_name] = {
                    "total_calls": len(period_records),
                    "successful_calls": sum(1 for r in period_records if r.success),
                    "total_cost": sum(r.cost_usd for r in period_records),
                    "total_tokens": sum(r.input_tokens + r.output_tokens for r in period_records),
                    "average_response_time": sum(r.duration_ms for r in period_records) / len(period_records)
                }

        return dashboard_data

    def get_audit_summary(self) -> Dict[str, Any]:
        """获取审计摘要"""
        total_records = len(self.llm_integrator.call_records)

        return {
            "audit_timestamp": datetime.now().isoformat(),
            "total_monitored_calls": total_records,
            "total_events_recorded": len(self.events),
            "monitoring_coverage": {
                "calls_with_start_events": len([
                    e for e in self.events if e.event_type == "call_started"
                ]),
                "calls_with_completion_events": len([
                    e for e in self.events if e.event_type in ["call_completed", "call_failed"]
                ]),
                "coverage_percentage": min(
                    len([e for e in self.events if e.event_type == "call_started"]) / max(total_records, 1) * 100,
                    100.0
                )
            },
            "verification_status": {
                "verifiable_calls": sum(
                    1 for record in self.llm_integrator.call_records
                    if record.get_signature()
                ),
                "verification_rate": sum(
                    1 for record in self.llm_integrator.call_records
                    if record.get_signature()
                ) / max(total_records, 1) * 100
            },
            "transparency_metrics": asdict(self.real_time_metrics)
        }

    async def generate_transparency_certificate(self, call_id: str) -> Dict[str, Any]:
        """生成透明度证书
        
        Args:
            call_id: 调用ID
            
        Returns:
            透明度证书

        """
        report = self.get_call_transparency_report(call_id)

        if "error" in report:
            return report

        certificate = {
            "certificate_id": f"TRANS_{call_id}_{int(datetime.now().timestamp())}",
            "call_id": call_id,
            "issued_at": datetime.now().isoformat(),
            "transparency_score": report["transparency_score"],
            "verification_status": report["verification"]["verified"],
            "audit_trail": report["audit_trail"],
            "certificate_hash": "",  # 将在下面计算
            "issuer": "DAIP-LIVE Real Demo System",
            "validity": "This certificate verifies the transparency and authenticity of the LLM call"
        }

        # 计算证书哈希
        cert_content = json.dumps(certificate, sort_keys=True)
        import hashlib
        certificate["certificate_hash"] = hashlib.sha256(cert_content.encode()).hexdigest()

        return certificate

    def stop_monitoring(self):
        """停止监控"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
        logger.info("TransparencyMonitor stopped")

    def __del__(self):
        """析构函数"""
        self.stop_monitoring()
