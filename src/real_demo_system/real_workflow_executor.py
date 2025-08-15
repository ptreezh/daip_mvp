"""真实工作流执行器

集成真实的CriticalReviewWorkflow和MultiPerspectiveWorkflow，
实现工作流执行状态监控和透明度功能。
"""

import asyncio
import json
import logging
import os

# 导入现有的工作流
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.critical_review_workflow import CriticalReviewWorkflow
from workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowExecution:
    """工作流执行记录"""
    execution_id: str
    workflow_type: str
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    inputs: dict[str, Any]
    outputs: Optional[dict[str, Any]]
    error_message: Optional[str]
    metadata: dict[str, Any]
    
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        return data


@dataclass
class WorkflowMetrics:
    """工作流性能指标"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration_ms: float = 0.0
    success_rate: float = 0.0
    workflow_type_distribution: dict[str, int] = None
    
    def __post_init__(self):
        if self.workflow_type_distribution is None:
            self.workflow_type_distribution = {}
    
    def update(self, execution: WorkflowExecution):
        """更新指标"""
        self.total_executions += 1
        
        if execution.status == WorkflowStatus.COMPLETED:
            self.successful_executions += 1
        elif execution.status == WorkflowStatus.FAILED:
            self.failed_executions += 1
        
        if execution.duration_ms is not None:
            # 重新计算平均持续时间
            total_duration = self.average_duration_ms * (self.total_executions - 1) + execution.duration_ms
            self.average_duration_ms = total_duration / self.total_executions
        
        self.success_rate = self.successful_executions / self.total_executions if self.total_executions > 0 else 0.0
        
        # 更新工作流类型分布
        workflow_type = execution.workflow_type
        self.workflow_type_distribution[workflow_type] = self.workflow_type_distribution.get(workflow_type, 0) + 1


class RealWorkflowExecutor:
    """真实工作流执行器
    
    集成真实的CriticalReviewWorkflow和MultiPerspectiveWorkflow，
    提供工作流执行状态监控和透明度功能。
    """
    
    def __init__(self, llm_integrator=None, role_manager=None):
        """初始化工作流执行器
        
        Args:
            llm_integrator: LLM集成器实例
            role_manager: 角色管理器实例
        """
        self.llm_integrator = llm_integrator
        self.role_manager = role_manager
        
        # 执行记录和指标
        self.executions: dict[str, WorkflowExecution] = {}
        self.metrics = WorkflowMetrics()
        
        # 活跃执行
        self.active_executions: dict[str, dict[str, Any]] = {}
        
        # 事件订阅者
        self.subscribers: list[Callable] = []
        
        logger.info("RealWorkflowExecutor initialized")
    
    async def execute_critical_review(
        self,
        prompt: str,
        role_context: str = "",
        workflow_config: Optional[dict[str, Any]] = None,
        execution_id: Optional[str] = None
    ) -> dict[str, Any]:
        """执行批判性审查工作流
        
        Args:
            prompt: 输入提示
            role_context: 角色上下文
            workflow_config: 工作流配置
            execution_id: 执行ID
            
        Returns:
            工作流执行结果
        """
        execution_id = execution_id or f"critical_review_{int(time.time())}"
        
        # 创建执行记录
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_type="critical_review",
            status=WorkflowStatus.PENDING,
            start_time=datetime.now(),
            end_time=None,
            duration_ms=None,
            inputs={
                "prompt": prompt,
                "role_context": role_context,
                "workflow_config": workflow_config
            },
            outputs=None,
            error_message=None,
            metadata={}
        )
        
        self.executions[execution_id] = execution
        
        try:
            # 更新状态为运行中
            execution.status = WorkflowStatus.RUNNING
            self.active_executions[execution_id] = {
                "workflow_type": "critical_review",
                "start_time": execution.start_time,
                "current_step": "initializing"
            }
            
            await self._emit_event("workflow_started", {
                "execution_id": execution_id,
                "workflow_type": "critical_review",
                "inputs": execution.inputs
            })
            
            # 准备服务
            services = {}
            if self.llm_integrator:
                services["llm_integrator"] = self.llm_integrator
            if self.role_manager:
                services["role_manager"] = self.role_manager
            
            # 创建并执行工作流
            workflow = CriticalReviewWorkflow(execution_id, workflow_config)
            
            # 更新当前步骤
            self.active_executions[execution_id]["current_step"] = "executing"
            
            result = await workflow.execute(
                prompt=prompt,
                role_context=role_context,
                services=services,
                execution_id=execution_id
            )
            
            # 计算执行时间
            end_time = datetime.now()
            duration_ms = int((end_time - execution.start_time).total_seconds() * 1000)
            
            # 更新执行记录
            execution.end_time = end_time
            execution.duration_ms = duration_ms
            execution.outputs = result
            
            if result.get("success", False):
                execution.status = WorkflowStatus.COMPLETED
                await self._emit_event("workflow_completed", {
                    "execution_id": execution_id,
                    "duration_ms": duration_ms,
                    "result": result
                })
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = result.get("error", "Unknown error")
                await self._emit_event("workflow_failed", {
                    "execution_id": execution_id,
                    "error": execution.error_message,
                    "duration_ms": duration_ms
                })
            
            # 移除活跃执行
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            # 更新指标
            self.metrics.update(execution)
            
            return result
            
        except Exception as e:
            # 处理异常
            end_time = datetime.now()
            duration_ms = int((end_time - execution.start_time).total_seconds() * 1000)
            
            execution.end_time = end_time
            execution.duration_ms = duration_ms
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            self.metrics.update(execution)
            
            await self._emit_event("workflow_failed", {
                "execution_id": execution_id,
                "error": str(e),
                "duration_ms": duration_ms
            })
            
            logger.error(f"Critical review workflow failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_id": execution_id
            }
    
    async def execute_multi_perspective(
        self,
        topic: str,
        perspectives: Optional[list[str]] = None,
        workflow_config: Optional[dict[str, Any]] = None,
        execution_id: Optional[str] = None
    ) -> dict[str, Any]:
        """执行多视角综合工作流
        
        Args:
            topic: 分析主题
            perspectives: 视角列表
            workflow_config: 工作流配置
            execution_id: 执行ID
            
        Returns:
            工作流执行结果
        """
        execution_id = execution_id or f"multi_perspective_{int(time.time())}"
        
        # 创建执行记录
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_type="multi_perspective",
            status=WorkflowStatus.PENDING,
            start_time=datetime.now(),
            end_time=None,
            duration_ms=None,
            inputs={
                "topic": topic,
                "perspectives": perspectives,
                "workflow_config": workflow_config
            },
            outputs=None,
            error_message=None,
            metadata={}
        )
        
        self.executions[execution_id] = execution
        
        try:
            # 更新状态为运行中
            execution.status = WorkflowStatus.RUNNING
            self.active_executions[execution_id] = {
                "workflow_type": "multi_perspective",
                "start_time": execution.start_time,
                "current_step": "initializing"
            }
            
            await self._emit_event("workflow_started", {
                "execution_id": execution_id,
                "workflow_type": "multi_perspective",
                "inputs": execution.inputs
            })
            
            # 准备服务
            services = {}
            if self.llm_integrator:
                services["llm_integrator"] = self.llm_integrator
            if self.role_manager:
                services["role_manager"] = self.role_manager
            
            # 创建并执行工作流
            workflow = MultiPerspectiveSynthesisWorkflow(execution_id, workflow_config)
            
            # 更新当前步骤
            self.active_executions[execution_id]["current_step"] = "executing"
            
            result = await workflow.execute(
                topic=topic,
                perspectives=perspectives,
                services=services,
                execution_id=execution_id
            )
            
            # 计算执行时间
            end_time = datetime.now()
            duration_ms = int((end_time - execution.start_time).total_seconds() * 1000)
            
            # 更新执行记录
            execution.end_time = end_time
            execution.duration_ms = duration_ms
            execution.outputs = result
            
            if result.get("success", False):
                execution.status = WorkflowStatus.COMPLETED
                await self._emit_event("workflow_completed", {
                    "execution_id": execution_id,
                    "duration_ms": duration_ms,
                    "result": result
                })
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = result.get("error", "Unknown error")
                await self._emit_event("workflow_failed", {
                    "execution_id": execution_id,
                    "error": execution.error_message,
                    "duration_ms": duration_ms
                })
            
            # 移除活跃执行
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            # 更新指标
            self.metrics.update(execution)
            
            return result
            
        except Exception as e:
            # 处理异常
            end_time = datetime.now()
            duration_ms = int((end_time - execution.start_time).total_seconds() * 1000)
            
            execution.end_time = end_time
            execution.duration_ms = duration_ms
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            self.metrics.update(execution)
            
            await self._emit_event("workflow_failed", {
                "execution_id": execution_id,
                "error": str(e),
                "duration_ms": duration_ms
            })
            
            logger.error(f"Multi-perspective workflow failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_id": execution_id
            }
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """取消工作流执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            是否成功取消
        """
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        
        if execution.status not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
            return False
        
        # 更新状态
        execution.status = WorkflowStatus.CANCELLED
        execution.end_time = datetime.now()
        if execution.start_time:
            execution.duration_ms = int((execution.end_time - execution.start_time).total_seconds() * 1000)
        
        # 移除活跃执行
        if execution_id in self.active_executions:
            del self.active_executions[execution_id]
        
        # 更新指标
        self.metrics.update(execution)
        
        await self._emit_event("workflow_cancelled", {
            "execution_id": execution_id
        })
        
        logger.info(f"Workflow execution cancelled: {execution_id}")
        return True
    
    def get_execution_status(self, execution_id: str) -> Optional[dict[str, Any]]:
        """获取执行状态"""
        if execution_id not in self.executions:
            return None
        
        execution = self.executions[execution_id]
        status_info = execution.to_dict()
        
        # 添加活跃执行信息
        if execution_id in self.active_executions:
            status_info["active_info"] = self.active_executions[execution_id]
        
        return status_info
    
    def get_all_executions(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """获取所有执行记录"""
        executions = list(self.executions.values())
        executions.sort(key=lambda x: x.start_time, reverse=True)
        
        if limit:
            executions = executions[:limit]
        
        return [execution.to_dict() for execution in executions]
    
    def get_active_executions(self) -> dict[str, dict[str, Any]]:
        """获取活跃执行"""
        return self.active_executions.copy()
    
    def get_performance_metrics(self) -> dict[str, Any]:
        """获取性能指标"""
        return asdict(self.metrics)
    
    def get_execution_transparency_report(self, execution_id: str) -> dict[str, Any]:
        """获取执行透明度报告
        
        Args:
            execution_id: 执行ID
            
        Returns:
            透明度报告
        """
        if execution_id not in self.executions:
            return {"error": "Execution not found"}
        
        execution = self.executions[execution_id]
        
        # 分析执行详情
        transparency_score = self._calculate_execution_transparency_score(execution)
        
        return {
            "execution_id": execution_id,
            "execution_record": execution.to_dict(),
            "transparency_score": transparency_score,
            "verification_status": {
                "has_inputs": bool(execution.inputs),
                "has_outputs": bool(execution.outputs),
                "has_timing": execution.duration_ms is not None,
                "has_error_info": execution.error_message is not None if execution.status == WorkflowStatus.FAILED else True
            },
            "execution_proof": {
                "workflow_type": execution.workflow_type,
                "start_time": execution.start_time.isoformat(),
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "status": execution.status.value,
                "inputs_hash": self._calculate_inputs_hash(execution.inputs),
                "outputs_hash": self._calculate_outputs_hash(execution.outputs) if execution.outputs else None
            }
        }
    
    def _calculate_execution_transparency_score(self, execution: WorkflowExecution) -> float:
        """计算执行透明度分数"""
        score = 0.0
        
        # 基础信息完整性
        if execution.inputs:
            score += 25.0
        if execution.outputs:
            score += 25.0
        if execution.duration_ms is not None:
            score += 20.0
        if execution.start_time and execution.end_time:
            score += 15.0
        
        # 状态完整性
        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
            score += 15.0
        
        return min(score, 100.0)
    
    def _calculate_inputs_hash(self, inputs: dict[str, Any]) -> str:
        """计算输入哈希"""
        import hashlib
        inputs_str = json.dumps(inputs, sort_keys=True)
        return hashlib.sha256(inputs_str.encode()).hexdigest()
    
    def _calculate_outputs_hash(self, outputs: dict[str, Any]) -> str:
        """计算输出哈希"""
        import hashlib
        outputs_str = json.dumps(outputs, sort_keys=True)
        return hashlib.sha256(outputs_str.encode()).hexdigest()
    
    async def _emit_event(self, event_type: str, data: dict[str, Any]):
        """发送事件"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
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
        """订阅工作流事件"""
        self.subscribers.append(callback)
        logger.info(f"New workflow subscriber added, total: {len(self.subscribers)}")
    
    def unsubscribe(self, callback: Callable):
        """取消订阅"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            logger.info(f"Workflow subscriber removed, total: {len(self.subscribers)}")
    
    def get_workflow_statistics(self) -> dict[str, Any]:
        """获取工作流统计信息"""
        now = datetime.now()
        
        # 时间段统计
        today_executions = [
            exec for exec in self.executions.values()
            if exec.start_time.date() == now.date()
        ]
        
        last_hour_executions = [
            exec for exec in self.executions.values()
            if (now - exec.start_time).total_seconds() <= 3600
        ]
        
        return {
            "total_executions": len(self.executions),
            "active_executions": len(self.active_executions),
            "today_executions": len(today_executions),
            "last_hour_executions": len(last_hour_executions),
            "performance_metrics": self.get_performance_metrics(),
            "workflow_types": list(self.metrics.workflow_type_distribution.keys()),
            "average_duration_seconds": self.metrics.average_duration_ms / 1000 if self.metrics.average_duration_ms > 0 else 0
        }
    
    def export_execution_log(self) -> dict[str, Any]:
        """导出执行日志"""
        return {
            "export_timestamp": datetime.now().isoformat(),
            "total_executions": len(self.executions),
            "executions": self.get_all_executions(),
            "performance_metrics": self.get_performance_metrics(),
            "statistics": self.get_workflow_statistics()
        }