# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 18:00:00
@Author  : DAIP-LIVE Team
@File    : progress_monitor.py
@Description:
    Progress monitoring for workflow execution.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProgressStep(BaseModel):
    """Model for a progress step."""
    step_id: str
    name: str
    description: str
    progress: float  # 0.0 to 1.0
    status: str  # "pending", "running", "completed", "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class WorkflowProgress(BaseModel):
    """Model for overall workflow progress."""
    execution_id: str
    workflow_name: str
    overall_progress: float  # 0.0 to 1.0
    current_step: str
    steps: List[ProgressStep] = []
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class ProgressMonitor:
    """Monitor and track workflow execution progress."""
    
    def __init__(self):
        """Initialize the progress monitor."""
        self.active_workflows: Dict[str, WorkflowProgress] = {}
        self.progress_callbacks: Dict[str, List[Callable]] = {}
    
    def start_workflow(
        self,
        execution_id: str,
        workflow_name: str,
        steps: List[Dict[str, str]]
    ) -> WorkflowProgress:
        """Start monitoring a workflow."""
        # Create progress steps
        progress_steps = []
        for i, step_info in enumerate(steps):
            progress_step = ProgressStep(
                step_id=f"step_{i}",
                name=step_info.get("name", f"Step {i+1}"),
                description=step_info.get("description", ""),
                progress=0.0,
                status="pending"
            )
            progress_steps.append(progress_step)
        
        # Create workflow progress
        workflow_progress = WorkflowProgress(
            execution_id=execution_id,
            workflow_name=workflow_name,
            overall_progress=0.0,
            current_step=progress_steps[0].name if progress_steps else "Starting",
            steps=progress_steps,
            started_at=datetime.now()
        )
        
        self.active_workflows[execution_id] = workflow_progress
        return workflow_progress
    
    def update_step_progress(
        self,
        execution_id: str,
        step_id: str,
        progress: float,
        status: str = "running",
        error: Optional[str] = None
    ) -> None:
        """Update progress for a specific step."""
        if execution_id not in self.active_workflows:
            logger.warning(f"Workflow {execution_id} not found for progress update")
            return
        
        workflow = self.active_workflows[execution_id]
        
        # Find and update the step
        for step in workflow.steps:
            if step.step_id == step_id:
                step.progress = progress
                step.status = status
                
                if status == "running" and step.started_at is None:
                    step.started_at = datetime.now()
                elif status in ["completed", "failed"]:
                    step.completed_at = datetime.now()
                
                if error:
                    step.error = error
                
                break
        
        # Update overall progress
        self._update_overall_progress(execution_id)
        
        # Notify callbacks
        self._notify_callbacks(execution_id, workflow)
    
    def complete_step(
        self,
        execution_id: str,
        step_id: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Mark a step as completed."""
        self.update_step_progress(execution_id, step_id, 1.0, "completed")
        
        if metadata and execution_id in self.active_workflows:
            workflow = self.active_workflows[execution_id]
            for step in workflow.steps:
                if step.step_id == step_id:
                    step.metadata.update(metadata)
                    break
    
    def fail_step(
        self,
        execution_id: str,
        step_id: str,
        error: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Mark a step as failed."""
        self.update_step_progress(execution_id, step_id, 0.0, "failed", error)
        
        if metadata and execution_id in self.active_workflows:
            workflow = self.active_workflows[execution_id]
            for step in workflow.steps:
                if step.step_id == step_id:
                    step.metadata.update(metadata)
                    break
    
    def get_workflow_progress(self, execution_id: str) -> Optional[WorkflowProgress]:
        """Get current progress for a workflow."""
        return self.active_workflows.get(execution_id)
    
    def complete_workflow(self, execution_id: str, metadata: Dict[str, Any] = None) -> None:
        """Mark a workflow as completed."""
        if execution_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows[execution_id]
        workflow.overall_progress = 1.0
        workflow.current_step = "Completed"
        
        if metadata:
            workflow.metadata.update(metadata)
        
        # Mark all remaining steps as completed
        for step in workflow.steps:
            if step.status == "pending":
                step.status = "completed"
                step.progress = 1.0
                step.completed_at = datetime.now()
        
        # Notify callbacks
        self._notify_callbacks(execution_id, workflow)
    
    def fail_workflow(self, execution_id: str, error: str, metadata: Dict[str, Any] = None) -> None:
        """Mark a workflow as failed."""
        if execution_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows[execution_id]
        workflow.current_step = f"Failed: {error}"
        
        if metadata:
            workflow.metadata.update(metadata)
        
        # Notify callbacks
        self._notify_callbacks(execution_id, workflow)
    
    def add_progress_callback(
        self,
        execution_id: str,
        callback: Callable[[WorkflowProgress], None]
    ) -> None:
        """Add a callback for progress updates."""
        if execution_id not in self.progress_callbacks:
            self.progress_callbacks[execution_id] = []
        
        self.progress_callbacks[execution_id].append(callback)
    
    def remove_progress_callback(
        self,
        execution_id: str,
        callback: Callable[[WorkflowProgress], None]
    ) -> None:
        """Remove a progress callback."""
        if execution_id in self.progress_callbacks:
            try:
                self.progress_callbacks[execution_id].remove(callback)
            except ValueError:
                pass
    
    def cleanup_workflow(self, execution_id: str) -> None:
        """Clean up workflow tracking data."""
        self.active_workflows.pop(execution_id, None)
        self.progress_callbacks.pop(execution_id, None)
    
    def _update_overall_progress(self, execution_id: str) -> None:
        """Update overall workflow progress based on step progress."""
        if execution_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows[execution_id]
        
        if not workflow.steps:
            return
        
        # Calculate overall progress as average of step progress
        total_progress = sum(step.progress for step in workflow.steps)
        workflow.overall_progress = total_progress / len(workflow.steps)
        
        # Update current step
        current_step = None
        for step in workflow.steps:
            if step.status == "running":
                current_step = step.name
                break
            elif step.status == "pending":
                current_step = f"Next: {step.name}"
                break
        
        if current_step:
            workflow.current_step = current_step
        elif all(step.status == "completed" for step in workflow.steps):
            workflow.current_step = "Completed"
        elif any(step.status == "failed" for step in workflow.steps):
            failed_step = next(step for step in workflow.steps if step.status == "failed")
            workflow.current_step = f"Failed at: {failed_step.name}"
    
    def _notify_callbacks(self, execution_id: str, workflow: WorkflowProgress) -> None:
        """Notify all registered callbacks about progress updates."""
        if execution_id in self.progress_callbacks:
            for callback in self.progress_callbacks[execution_id]:
                try:
                    callback(workflow)
                except Exception as e:
                    logger.error(f"Progress callback failed: {e}")
    
    def get_active_workflows(self) -> List[WorkflowProgress]:
        """Get all currently active workflows."""
        return list(self.active_workflows.values())
    
    def get_workflow_summary(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of workflow progress."""
        workflow = self.get_workflow_progress(execution_id)
        if not workflow:
            return None
        
        completed_steps = sum(1 for step in workflow.steps if step.status == "completed")
        failed_steps = sum(1 for step in workflow.steps if step.status == "failed")
        running_steps = sum(1 for step in workflow.steps if step.status == "running")
        
        return {
            "execution_id": execution_id,
            "workflow_name": workflow.workflow_name,
            "overall_progress": workflow.overall_progress,
            "current_step": workflow.current_step,
            "total_steps": len(workflow.steps),
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "running_steps": running_steps,
            "started_at": workflow.started_at,
            "estimated_completion": workflow.estimated_completion
        }