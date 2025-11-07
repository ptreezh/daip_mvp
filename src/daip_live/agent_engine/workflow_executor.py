"""
WorkflowExecutor - 工作流执行器
专门负责工作流的执行
遵循KISS/YAGNI/SOLID原则
"""

import time
import logging
from collections.abc import AsyncGenerator
from typing import Any, Dict, Optional, List

from daip_live.core.models import (
    AgentEvent,
    AgentState,
    ThoughtEvent,
)
from daip_live.workflow.parser import WorkflowDefinition

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    """
    工作流执行器 - 专门负责工作流执行功能
    遵循单一职责原则，只关注工作流执行相关功能
    """
    
    def __init__(self):
        """
        初始化工作流执行器
        """
        logger.info("WorkflowExecutor initialized")
    
    async def execute_workflow(self, workflow_definition: WorkflowDefinition) -> AsyncGenerator[AgentEvent, None]:
        """
        执行工作流
        
        Args:
            workflow_definition: 工作流定义
            
        Yields:
            AgentEvent: 执行事件
        """
        if not workflow_definition or not workflow_definition.elements:
            yield ThoughtEvent(content="Invalid workflow definition")
            # 需要通过某种方式通知AgentExecutor工作流失败
            # 由于我们无法直接修改AgentExecutor的状态，这里通过特殊事件处理
            yield ThoughtEvent(content="WORKFLOW_EXECUTION_FAILED: Empty workflow definition")
            return
            
        current_element_id = workflow_definition.start_element
        state = AgentState.THINKING
        element_outputs: Dict[str, Any] = {}  # 存储各元素的输出结果
        loop_counters: Dict[str, int] = {}  # 存储循环计数器
        execution_history: List[Dict[str, Any]] = []  # 执行历史记录
        
        # 如果启用了持久化，尝试恢复执行状态
        if workflow_definition.persistence:
            async for event in self._recover_workflow_state():
                yield event
        
        # 记录工作流开始日志
        if workflow_definition.logging:
            yield ThoughtEvent(content=f"Starting workflow: {workflow_definition.name} v{workflow_definition.version}")
        
        while current_element_id and state != AgentState.FAILED:
            element = workflow_definition.elements.get(current_element_id)
            if not element:
                yield ThoughtEvent(content=f"Element {current_element_id} not found")
                yield ThoughtEvent(content=f"WORKFLOW_EXECUTION_FAILED: Element {current_element_id} not found")
                state = AgentState.FAILED
                break
                
            # 记录元素执行日志
            if element.logging:
                yield ThoughtEvent(content=f"Executing element: {element.name} ({element.type.value})")
            
            # 记录执行历史
            execution_record = {
                "element_id": current_element_id,
                "element_name": element.name,
                "start_time": time.time(),
                "status": "running"
            }
            execution_history.append(execution_record)
            
            # 根据元素类型执行相应逻辑
            # 首先执行元素并收集所有事件
            async for event in self._execute_workflow_element_events(element, element_outputs, loop_counters):
                yield event
            
            # 然后获取下一个元素ID
            next_element_id = self._get_next_element_id(element, loop_counters)
            
            # 更新执行历史状态
            execution_record.update({
                "end_time": time.time(),
                "status": "completed" if state != AgentState.FAILED else "failed",
                "output": element_outputs.get(current_element_id)
            })
            
            # 如果启用了持久化，保存执行状态
            if workflow_definition.persistence:
                async for event in self._persist_workflow_state():
                    yield event
            
            if state == AgentState.FAILED:
                break
                
            current_element_id = next_element_id
    
    async def _recover_workflow_state(self) -> AsyncGenerator[AgentEvent, None]:
        """
        恢复工作流执行状态
        
        Yields:
            AgentEvent: 恢复事件
        """
        # 这里应该从持久化存储中恢复工作流状态
        # 简化处理，仅添加提示信息
        yield ThoughtEvent(content="Recovering workflow state from persistence")
    
    async def _persist_workflow_state(self) -> AsyncGenerator[AgentEvent, None]:
        """
        持久化工作流执行状态
        
        Yields:
            AgentEvent: 持久化事件
        """
        # 这里应该将工作流状态保存到持久化存储中
        # 简化处理，仅添加提示信息
        yield ThoughtEvent(content="Persisting workflow state")
    
    async def _execute_workflow_element_events(self, element: Any, element_outputs: Dict[str, Any], loop_counters: Dict[str, int]) -> AsyncGenerator[AgentEvent, None]:
        """
        执行工作流元素并产生事件
        
        Args:
            element: 工作流元素
            element_outputs: 元素输出存储
            loop_counters: 循环计数器
            
        Yields:
            AgentEvent: 执行事件
        """
        from daip_live.workflow.parser import WorkflowElementType, TaskElement, ConditionElement, LoopElement, SubWorkflowElement
        
        if element.type == WorkflowElementType.TASK:
            async for event in self._execute_task_element_events(element, element_outputs):
                yield event
        elif element.type == WorkflowElementType.CONDITION:
            async for event in self._execute_condition_element_events(element):
                yield event
        elif element.type == WorkflowElementType.LOOP:
            async for event in self._execute_loop_element_events(element, loop_counters):
                yield event
        elif element.type == WorkflowElementType.SUBWORKFLOW:
            async for event in self._execute_subworkflow_element_events(element):
                yield event
        else:
            # 默认作为任务元素处理
            async for event in self._execute_task_element_events(element, element_outputs):
                yield event
    
    def _get_next_element_id(self, element: Any, loop_counters: Dict[str, int]) -> Optional[str]:
        """
        获取下一个元素ID
        
        Args:
            element: 当前元素
            loop_counters: 循环计数器
            
        Returns:
            Optional[str]: 下一个元素ID
        """
        from daip_live.workflow.parser import WorkflowElementType, TaskElement, ConditionElement, LoopElement, SubWorkflowElement
        
        if element.type == WorkflowElementType.TASK:
            return self._get_task_next_element_id(element)
        elif element.type == WorkflowElementType.CONDITION:
            return self._get_condition_next_element_id(element)
        elif element.type == WorkflowElementType.LOOP:
            return self._get_loop_next_element_id(element, loop_counters)
        elif element.type == WorkflowElementType.SUBWORKFLOW:
            return self._get_subworkflow_next_element_id(element)
        else:
            # 默认作为任务元素处理
            return self._get_task_next_element_id(element)
    
    async def _execute_task_element_events(self, element: Any, element_outputs: Dict[str, Any]) -> AsyncGenerator[AgentEvent, None]:
        """
        执行任务元素并产生事件
        
        Args:
            element: 任务元素
            element_outputs: 元素输出存储
            
        Yields:
            AgentEvent: 执行事件
        """
        # 检查权限
        if element.permissions:
            yield ThoughtEvent(content=f"Checking permissions: {element.permissions}")
            # 这里应该检查权限，简化处理仅记录日志
        
        # 处理数据输入
        task_description = element.name
        if element.description:
            task_description += f": {element.description}"
            
        # 添加数据输入信息到任务描述
        if element.data_inputs:
            task_description += f"\nData Inputs: {element.data_inputs}"
            
        # 处理角色指定
        if element.role:
            task_description += f"\nRole: {element.role}"
            
        # 处理超时设置
        if element.timeout:
            task_description += f"\nTimeout: {element.timeout}s"
            
        # 处理重试次数
        if element.retry_count > 0:
            task_description += f"\nRetry Count: {element.retry_count}"
            
        # 处理重试延迟
        if element.retry_delay > 0:
            task_description += f"\nRetry Delay: {element.retry_delay}s"
            
        # 处理并行执行
        if element.parallel:
            task_description += f"\nParallel Execution: Enabled"
            
        # 存储任务输出（简化处理）
        element_outputs[element.id] = f"Executed task: {task_description}"
        yield ThoughtEvent(content=f"Executed task element: {element.name}")
    
    async def _execute_condition_element_events(self, element: Any) -> AsyncGenerator[AgentEvent, None]:
        """
        执行条件元素并产生事件
        
        Args:
            element: 条件元素
            
        Yields:
            AgentEvent: 执行事件
        """
        # 条件元素暂时不产生特殊事件
        yield ThoughtEvent(content=f"Executed condition element: {element.name}")
    
    async def _execute_loop_element_events(self, element: Any, loop_counters: Dict[str, int]) -> AsyncGenerator[AgentEvent, None]:
        """
        执行循环元素并产生事件
        
        Args:
            element: 循环元素
            loop_counters: 循环计数器
            
        Yields:
            AgentEvent: 执行事件
        """
        # 初始化循环计数器
        if element.id not in loop_counters:
            loop_counters[element.id] = 0
        yield ThoughtEvent(content=f"Executed loop element: {element.name} (iteration {loop_counters[element.id]})")
    
    async def _execute_subworkflow_element_events(self, element: Any) -> AsyncGenerator[AgentEvent, None]:
        """
        执行子工作流元素并产生事件
        
        Args:
            element: 子工作流元素
            
        Yields:
            AgentEvent: 执行事件
        """
        # 检查权限
        if element.permissions:
            yield ThoughtEvent(content=f"Checking permissions: {element.permissions}")
            # 这里应该检查权限，简化处理仅记录日志
            
        # 这里需要加载和执行子工作流
        # 简化处理，直接返回下一个元素
        if element.logging:
            yield ThoughtEvent(content=f"Executing subworkflow: {element.workflow_ref}")
        
        # 如果有子工作流引用，尝试加载并执行
        if element.workflow_ref:
            # 这里应该加载子工作流定义并执行
            # 简化处理，仅添加提示信息
            if element.logging:
                yield ThoughtEvent(content=f"Subworkflow {element.workflow_ref} execution completed")
    
    def _get_task_next_element_id(self, element: Any) -> Optional[str]:
        """
        获取任务元素的下一个元素ID
        
        Args:
            element: 任务元素
            
        Returns:
            Optional[str]: 下一个元素ID
        """
        if element.next_elements:
            return element.next_elements[0]
        return None
    
    def _get_condition_next_element_id(self, element: Any) -> Optional[str]:
        """
        获取条件元素的下一个元素ID
        
        Args:
            element: 条件元素
            
        Returns:
            Optional[str]: 下一个元素ID
        """
        # 获取输入数据用于条件判断
        condition_result = "default"  # 简化处理，实际应根据输入数据计算条件
        
        # 根据条件结果选择分支
        if condition_result in element.branches:
            next_elements = element.branches[condition_result]
            if next_elements:
                return next_elements[0]
            return None
        elif element.branches:
            # 使用默认分支（第一个分支）
            next_elements = next(iter(element.branches.values()))
            if next_elements:
                return next_elements[0]
            return None
        if element.next_elements:
            return element.next_elements[0]
        return None
    
    def _get_loop_next_element_id(self, element: Any, loop_counters: Dict[str, int]) -> Optional[str]:
        """
        获取循环元素的下一个元素ID
        
        Args:
            element: 循环元素
            loop_counters: 循环计数器
            
        Returns:
            Optional[str]: 下一个元素ID
        """
        # 检查循环条件
        # 简化处理，实际应根据输入数据计算循环条件
        if loop_counters[element.id] < element.max_iterations:
            loop_counters[element.id] += 1
            # 返回循环体的第一个元素
            if element.next_elements:
                return element.next_elements[0]
            return None
        
        # 循环结束，返回循环后的元素
        # 这里需要根据具体实现确定返回哪个元素
        return None
    
    def _get_subworkflow_next_element_id(self, element: Any) -> Optional[str]:
        """
        获取子工作流元素的下一个元素ID
        
        Args:
            element: 子工作流元素
            
        Returns:
            Optional[str]: 下一个元素ID
        """
        if element.next_elements:
            return element.next_elements[0]
        return None