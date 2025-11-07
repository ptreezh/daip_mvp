import ast
import asyncio
import re
import time
from collections.abc import AsyncGenerator
from typing import Any, Dict, Optional, Tuple, List

from daip_live.core.exceptions import ToolError
from daip_live.core.models import (
    AgentEvent,
    AgentState,
    AgentStatus,
    DialogueTurn,
    FinalResponseEvent,
    ModelMetricsEvent,
    Session,
    SessionContext,
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
    TokenUsageEvent,
    TodoItem,
    PermissionRequestEvent,
)
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.workflow.parser import WorkflowDefinition, WorkflowParser


class AgentExecutor:
    TOOL_CALL_PATTERN = re.compile(r"Use Tool:\s*(\w+)\s*\((.*)\)")
    CONFIDENCE_PATTERN = re.compile(r"Confidence: (\d\.\d+)")
    FINAL_ANSWER_PATTERN = re.compile(r"Final Answer:\s*", re.IGNORECASE)

    def __init__(
        self,
        session_manager: SessionManager,
        memory_service: MemoryService,
        knowledge_manager: Any,
        model_provider: Any,
        tool_manager: Any,
        user_input_queue: asyncio.Queue,
        max_reflections: int = 3,
    ):
        self.session_manager = session_manager
        self.memory_service = memory_service
        self.knowledge_manager = knowledge_manager
        self.model_provider = model_provider
        self.tool_manager = tool_manager
        self.user_input_queue = user_input_queue
        self.max_reflections = max_reflections

        self.state: AgentState = AgentState.IDLE
        self.session: Optional[Session] = None
        self.llm_response: str = ""
        self.last_tool_result: Optional[str] = None
        self.last_final_response: Optional[FinalResponseEvent] = None
        self.reflection_count: int = 0
        self.session_context = SessionContext()
        self.tokens_used: int = 0
        self.tokens_total: int = 8192 # Default, should be updated based on model
        
        # 工作流相关属性
        self.workflow_definition: Optional[WorkflowDefinition] = None
        self.current_element_id: Optional[str] = None
        self.element_outputs: Dict[str, Any] = {}  # 存储各元素的输出结果
        self.loop_counters: Dict[str, int] = {}  # 存储循环计数器
        self.execution_history: List[Dict[str, Any]] = []  # 执行历史记录

    def get_status(self) -> AgentStatus:
        """Returns a snapshot of the agent's current state."""
        return AgentStatus(
            state=self.state.value,
            model_name=getattr(self.model_provider.config, 'model', 'unknown'),
            tokens_used=self.tokens_used,
            tokens_total=self.tokens_total,
        )

    async def run(self, goal: str, workflow_definition: Optional[WorkflowDefinition] = None) -> AsyncGenerator[AgentEvent, None]:
        """Main execution loop, driven by a Todo list and delegating steps to _execute_step."""
        self.session = self.session_manager.create_session(
            goal=goal, session_type="workflow", participant_ids=["agent", "system", "user"]
        )
        self._change_state(AgentState.RUNNING)
        self.session.status = self.state
        
        # 设置工作流定义
        self.workflow_definition = workflow_definition

        todo_list = await self.memory_service.get_todo_list()
        current_task_index = 0
        self.last_final_response = None

        try:
            # 如果有工作流定义，按工作流执行
            if self.workflow_definition:
                async for event in self._execute_workflow():
                    yield event
            else:
                # 否则按原有的Todo列表执行
                while not await self.memory_service.is_todo_list_complete():
                    # --- Outer loop: Get next task and delegate execution ---
                    current_task = todo_list[current_task_index]

                    # Reset context for the new step
                    self.llm_response = ""
                    self.last_tool_result = None
                    self._change_state(AgentState.THINKING)

                    # Delegate the entire step execution to the helper method
                    async for event in self._execute_step(current_task):
                        yield event

                    if self.state == AgentState.FAILED:
                        break # Exit outer loop on failure

                    await self.memory_service.update_todo_status(current_task_index)
                    current_task_index += 1

            if self.state != AgentState.FAILED:
                self._change_state(AgentState.COMPLETED)
                if not self.last_final_response:
                     yield FinalResponseEvent(content="Plan completed successfully.")

        finally:
            if self.session:
                self.session.status = self.state
                self.session_manager.save_session(self.session)
                yield ThoughtEvent(content=f"Session {self.session.session_id} saved with status {self.state.name}.")

    async def chat_run(self, initial_goal: str) -> AsyncGenerator[AgentEvent, None]:
        """Runs the agent in an interactive chat mode."""
        self.session = self.session_manager.create_session(
            goal=initial_goal, session_type="chat", participant_ids=["agent", "user"]
        )
        self._change_state(AgentState.RUNNING)
        self.session.status = self.state
        yield ThoughtEvent(content=f"Session {self.session.session_id} started for goal: {initial_goal}")

        # Process the initial goal
        async for event in self._process_chat_turn(initial_goal):
            yield event

        try:
            while True:
                # Wait for user input from the TUI
                user_input = await self.user_input_queue.get()
                if user_input is None:  # Add a way to gracefully exit the loop
                    break

                self.session.history.append(DialogueTurn(participant_id="user", content=user_input))

                async for event in self._process_chat_turn(user_input):
                    yield event

                self.user_input_queue.task_done()

        finally:
            self._change_state(AgentState.COMPLETED)
            if self.session:
                self.session.status = self.state
                self.session_manager.save_session(self.session)
                yield ThoughtEvent(content=f"Session {self.session.session_id} saved with status {self.state.name}.")

    async def _process_chat_turn(self, turn_description: str) -> AsyncGenerator[AgentEvent, None]:
        """Helper to process a single turn in a chat, avoiding code duplication."""
        # Reset context for the new turn
        self.llm_response = ""
        self.last_tool_result = None
        self.reflection_count = 0
        self._change_state(AgentState.THINKING)

        # Execute the user input as the new task
        current_task = TodoItem(id=0, description=turn_description, status="pending", priority=1)
        async for event in self._execute_step(current_task):
            yield event

    async def _execute_workflow(self) -> AsyncGenerator[AgentEvent, None]:
        """执行工作流"""
        if not self.workflow_definition or not self.workflow_definition.elements:
            yield ThoughtEvent(content="Invalid workflow definition")
            self._change_state(AgentState.FAILED)
            return
            
        self.current_element_id = self.workflow_definition.start_element
        self._change_state(AgentState.THINKING)
        
        # 如果启用了持久化，尝试恢复执行状态
        if self.workflow_definition.persistence:
            async for event in self._recover_workflow_state():
                yield event
        
        # 记录工作流开始日志
        if self.workflow_definition.logging:
            yield ThoughtEvent(content=f"Starting workflow: {self.workflow_definition.name} v{self.workflow_definition.version}")
        
        while self.current_element_id and self.state != AgentState.FAILED:
            element = self.workflow_definition.elements.get(self.current_element_id)
            if not element:
                yield ThoughtEvent(content=f"Element {self.current_element_id} not found")
                self._change_state(AgentState.FAILED)
                break
                
            # 记录元素执行日志
            if element.logging:
                yield ThoughtEvent(content=f"Executing element: {element.name} ({element.type.value})")
            
            # 记录执行历史
            execution_record = {
                "element_id": self.current_element_id,
                "element_name": element.name,
                "start_time": time.time(),
                "status": "running"
            }
            self.execution_history.append(execution_record)
            
            # 根据元素类型执行相应逻辑
            # 首先执行元素并收集所有事件
            async for event in self._execute_workflow_element_events(element):
                yield event
            
            # 然后获取下一个元素ID
            next_element_id = self._get_next_element_id(element)
            
            # 更新执行历史状态
            execution_record.update({
                "end_time": time.time(),
                "status": "completed" if self.state != AgentState.FAILED else "failed",
                "output": self.element_outputs.get(self.current_element_id)
            })
            
            # 如果启用了持久化，保存执行状态
            if self.workflow_definition.persistence:
                async for event in self._persist_workflow_state():
                    yield event
            
            if self.state == AgentState.FAILED:
                break
                
            self.current_element_id = next_element_id

    async def _recover_workflow_state(self) -> AsyncGenerator[AgentEvent, None]:
        """恢复工作流执行状态"""
        # 这里应该从持久化存储中恢复工作流状态
        # 简化处理，仅添加提示信息
        yield ThoughtEvent(content="Recovering workflow state from persistence")

    async def _persist_workflow_state(self) -> AsyncGenerator[AgentEvent, None]:
        """持久化工作流执行状态"""
        # 这里应该将工作流状态保存到持久化存储中
        # 简化处理，仅添加提示信息
        yield ThoughtEvent(content="Persisting workflow state")

    async def _execute_workflow_element_events(self, element: Any) -> AsyncGenerator[AgentEvent, None]:
        """执行工作流元素并产生事件"""
        from daip_live.workflow.parser import WorkflowElementType, TaskElement, ConditionElement, LoopElement, SubWorkflowElement
        
        if element.type == WorkflowElementType.TASK:
            async for event in self._execute_task_element_events(element):
                yield event
        elif element.type == WorkflowElementType.CONDITION:
            async for event in self._execute_condition_element_events(element):
                yield event
        elif element.type == WorkflowElementType.LOOP:
            async for event in self._execute_loop_element_events(element):
                yield event
        elif element.type == WorkflowElementType.SUBWORKFLOW:
            async for event in self._execute_subworkflow_element_events(element):
                yield event
        else:
            # 默认作为任务元素处理
            async for event in self._execute_task_element_events(element):
                yield event

    def _get_next_element_id(self, element: Any) -> Optional[str]:
        """获取下一个元素ID"""
        from daip_live.workflow.parser import WorkflowElementType, TaskElement, ConditionElement, LoopElement, SubWorkflowElement
        
        if element.type == WorkflowElementType.TASK:
            return self._get_task_next_element_id(element)
        elif element.type == WorkflowElementType.CONDITION:
            return self._get_condition_next_element_id(element)
        elif element.type == WorkflowElementType.LOOP:
            return self._get_loop_next_element_id(element)
        elif element.type == WorkflowElementType.SUBWORKFLOW:
            return self._get_subworkflow_next_element_id(element)
        else:
            # 默认作为任务元素处理
            return self._get_task_next_element_id(element)

    async def _execute_task_element_events(self, element: Any) -> AsyncGenerator[AgentEvent, None]:
        """执行任务元素并产生事件"""
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
            
        # 创建临时Todo项
        # 将字符串ID转换为整数ID
        try:
            todo_id = int(element.id) if element.id.isdigit() else hash(element.id) % (10 ** 8)
        except:
            todo_id = hash(element.id) % (10 ** 8)
        
        temp_task = TodoItem(
            id=todo_id,
            description=task_description,
            status="pending",
            priority=1
        )
        
        # 执行任务
        async for event in self._execute_step(temp_task):
            yield event
            
        # 存储任务输出
        if self.last_final_response:
            self.element_outputs[element.id] = self.last_final_response.content

    def _get_task_next_element_id(self, element: Any) -> Optional[str]:
        """获取任务元素的下一个元素ID"""
        if element.next_elements:
            return element.next_elements[0]
        return None

    async def _execute_condition_element_events(self, element: Any) -> AsyncGenerator[AgentEvent, None]:
        """执行条件元素并产生事件"""
        # 条件元素暂时不产生特殊事件
        pass

    def _get_condition_next_element_id(self, element: Any) -> Optional[str]:
        """获取条件元素的下一个元素ID"""
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

    async def _execute_loop_element_events(self, element: Any) -> AsyncGenerator[AgentEvent, None]:
        """执行循环元素并产生事件"""
        # 循环元素暂时不产生特殊事件
        pass

    def _get_loop_next_element_id(self, element: Any) -> Optional[str]:
        """获取循环元素的下一个元素ID"""
        # 初始化循环计数器
        if element.id not in self.loop_counters:
            self.loop_counters[element.id] = 0
            
        # 检查循环条件
        # 简化处理，实际应根据输入数据计算循环条件
        if self.loop_counters[element.id] < element.max_iterations:
            self.loop_counters[element.id] += 1
            # 返回循环体的第一个元素
            if element.next_elements:
                return element.next_elements[0]
            return None
        
        # 循环结束，返回循环后的元素
        # 这里需要根据具体实现确定返回哪个元素
        return None

    async def _execute_subworkflow_element_events(self, element: Any) -> AsyncGenerator[AgentEvent, None]:
        """执行子工作流元素并产生事件"""
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

    def _get_subworkflow_next_element_id(self, element: Any) -> Optional[str]:
        """获取子工作流元素的下一个元素ID"""
        if element.next_elements:
            return element.next_elements[0]
        return None

    async def _execute_step(self, current_task: TodoItem) -> AsyncGenerator[AgentEvent, None]:
        """Executes a single step from the Todo list using a state machine."""
        step_completed = False
        max_iterations = 20  # Prevent infinite loops - increased for complex workflows
        iteration_count = 0
        failed_tool_calls = set()  # Track failed tool calls to avoid repetition

        while not step_completed and iteration_count < max_iterations:
            # 1. OBSERVE & STEER
            try:
                user_command = self.user_input_queue.get_nowait()
                yield ThoughtEvent(content=f"Received steering command: {user_command}")
                self.session.history.append(DialogueTurn(participant_id="user", content=user_command))
                self.last_tool_result = f"User steering command: {user_command}"
                self.user_input_queue.task_done()
                self._change_state(AgentState.THINKING) # Force re-thinking
            except asyncio.QueueEmpty:
                pass # No user command

            iteration_count += 1
            if iteration_count >= max_iterations:
                yield ThoughtEvent(content=f"Maximum iterations ({max_iterations}) reached for this step. Forcing completion.")
                self.last_final_response = FinalResponseEvent(content="Step completed due to iteration limit.")
                yield self.last_final_response
                step_completed = True
                break

            # 2. ACT based on current state
            if self.state == AgentState.THINKING:
                yield ThoughtEvent(content=f"Thinking about task: {current_task.description}")
                prompt = await self.memory_service.construct_prompt(
                    current_task.description, self.last_tool_result, self.llm_response, self.session
                )
                start_time = time.time()
                self.llm_response, usage = await self.model_provider.generate(prompt)
                latency = time.time() - start_time
                
                # Send token usage event
                if usage and isinstance(usage, dict):
                    yield TokenUsageEvent(usage_info=usage)
                    if "total_tokens" in usage:
                        self.tokens_used += usage["total_tokens"]
                
                # Send model metrics event
                request_count = getattr(self, '_request_count', 0) + 1
                self._request_count = request_count
                yield ModelMetricsEvent(latency=latency, request_count=request_count)
                self.session.history.append(DialogueTurn(participant_id="agent", content=self.llm_response))
                self._change_state(AgentState.EVALUATING)

            elif self.state == AgentState.EVALUATING:
                confidence_match = self.CONFIDENCE_PATTERN.search(self.llm_response)
                confidence = float(confidence_match.group(1)) if confidence_match else 1.0

                if confidence < 0.85 and self.reflection_count < self.max_reflections:
                    self.reflection_count += 1
                    yield ThoughtEvent(content=f"Confidence is low ({confidence}). Reflecting... ({self.reflection_count}/{self.max_reflections})")
                    self.last_tool_result = f"Self-reflection: The previous response had low confidence ({confidence}). I need to reconsider my approach to be more certain."
                    self._change_state(AgentState.THINKING)
                else:
                    tool_call = self._parse_tool_call(self.llm_response)
                    if tool_call:
                        name, args = tool_call
                        # Create a unique key for this tool call to detect repetitions
                        tool_call_key = f"{name}:{sorted(args.items()) if args else ''}"
                        
                        if tool_call_key in failed_tool_calls:
                            yield ThoughtEvent(content=f"Tool '{name}' with these arguments already failed. Skipping to avoid repetition.")
                            self._change_state(AgentState.RESPONDING)
                        else:
                            has_tool = hasattr(self.tool_manager, "_registry") and name in getattr(self.tool_manager, "_registry", {})
                            if not has_tool:
                                yield ThoughtEvent(content=f"Tool '{name}' not available. Ignored.")
                                failed_tool_calls.add(tool_call_key)  # Mark as failed to avoid retry
                                self._change_state(AgentState.RESPONDING)
                            else:
                                self._change_state(AgentState.EXECUTING_TOOL)
                    else:
                        self._change_state(AgentState.RESPONDING)

            elif self.state == AgentState.EXECUTING_TOOL:
                tool_name, tool_args = self._parse_tool_call(self.llm_response)
                yield ToolCallEvent(tool_name=tool_name, args=tool_args)
                try:
                    self.last_tool_result = self.tool_manager.execute_tool(
                        tool_name, tool_args, session_context=self.session_context
                    )
                    yield ToolOutputEvent(tool_name=tool_name, status="success", output=self.last_tool_result)
                    self._change_state(AgentState.THINKING)
                except Exception as e:
                    from daip_live.p4_role_manager_tools.tool_manager import ToolPermissionRequest
                    # Create tool call key for tracking failed attempts
                    tool_call_key = f"{tool_name}:{sorted(tool_args.items()) if tool_args else ''}"
                    
                    if isinstance(e, ToolPermissionRequest):
                        yield PermissionRequestEvent(tool_name=tool_name, args=tool_args)
                        # Treat permission denial as a tool error and skip to response
                        self.last_tool_result = f"Permission denied for tool '{tool_name}'. Continuing without tool execution."
                        yield ToolOutputEvent(tool_name=tool_name, status="error", output=self.last_tool_result)
                        failed_tool_calls.add(tool_call_key)  # Mark this tool call as failed to avoid retry
                        self._change_state(AgentState.RESPONDING)  # Skip to responding instead of re-thinking
                    else:
                        self.last_tool_result = f"Error: {e}"
                        yield ToolOutputEvent(tool_name=tool_name, status="error", output=self.last_tool_result)
                        failed_tool_calls.add(tool_call_key)  # Mark as failed to avoid retry
                        self._change_state(AgentState.FAILED)
                        step_completed = True

            elif self.state == AgentState.RESPONDING:
                final_answer = self.CONFIDENCE_PATTERN.sub("", self.llm_response).strip()
                final_answer = self.TOOL_CALL_PATTERN.sub("", final_answer).strip()
                final_answer = self.FINAL_ANSWER_PATTERN.sub("", final_answer).strip()
                self.last_final_response = FinalResponseEvent(content=final_answer)
                yield self.last_final_response
                step_completed = True  # This step is done

    def _change_state(self, new_state: AgentState):
        self.state = new_state

    def _parse_tool_call(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        match = self.TOOL_CALL_PATTERN.search(text)
        if not match: return None
        tool_name, args_str = match.groups()
        try:
            # A slightly more robust arg parser
            args = dict(re.findall(r'(\w+)=([^,)]+)', args_str))
            for key, value in args.items():
                try:
                    args[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    args[key] = value # Keep as string if it's not a literal
            return tool_name, args
        except Exception: return None