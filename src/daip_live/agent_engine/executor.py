import asyncio
import logging
import re
from collections.abc import AsyncGenerator
from typing import Any, Optional

from daip_live.agent_engine.chat_executor import ChatExecutor

# 导入新创建的专门类
from daip_live.agent_engine.session_manager import SessionManager
from daip_live.agent_engine.state_manager import StateManager
from daip_live.agent_engine.step_executor import StepExecutor
from daip_live.agent_engine.workflow_executor import WorkflowExecutor
from daip_live.core.models import (
    AgentEvent,
    AgentState,
    AgentStatus,
    FinalResponseEvent,
    Session,
    SessionContext,
    ThoughtEvent,
    TodoItem,
)
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager as BaseSessionManager
from daip_live.permission.permission_manager import (
    PermissionManager,  # 新增权限管理器导入
)

# 导入任务分解引擎
from daip_live.workflow.parser import WorkflowDefinition

logger = logging.getLogger(__name__)


class AgentExecutor:
    def __init__(
        self,
        session_manager: BaseSessionManager,
        memory_service: MemoryService,
        knowledge_manager: Any,
        model_provider: Any,
        tool_manager: Any,
        user_input_queue: asyncio.Queue,
        permission_manager: Optional[PermissionManager] = None,  # 新增权限管理器参数
        max_reflections: int = 3,
    ):
        # 使用专门的管理器类
        self.session_manager = SessionManager(session_manager)
        self.state_manager = StateManager(model_provider)
        self.step_executor = StepExecutor(
            state_manager=self.state_manager,  # Pass the state manager
            memory_service=memory_service,
            model_provider=model_provider,
            tool_manager=tool_manager,
            user_input_queue=user_input_queue,
            permission_manager=permission_manager,
            max_reflections=max_reflections,
        )
        self.workflow_executor = WorkflowExecutor()
        self.chat_executor = ChatExecutor(
            session_manager, memory_service, user_input_queue
        )

        # 保持原有属性以确保兼容性
        self.memory_service = memory_service
        self.knowledge_manager = knowledge_manager
        self.model_provider = model_provider
        self.tool_manager = tool_manager
        self.user_input_queue = user_input_queue
        self.permission_manager = permission_manager
        self.max_reflections = max_reflections

        # 保持会话引用以确保兼容性
        self.session: Optional[Session] = None

        # 保持工作流相关属性以确保兼容性
        self.workflow_definition: Optional[WorkflowDefinition] = None

        logger.info("AgentExecutor initialized with refactored design")

    def get_status(self) -> AgentStatus:
        """Returns a snapshot of the agent's current state."""
        return self.state_manager.get_status()

    async def run(
        self, goal: str, workflow_definition: Optional[WorkflowDefinition] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        """Main execution loop, driven by a Todo list and delegating steps to _execute_step."""  # noqa: E501
        self.session = self.session_manager.create_session(
            goal=goal,
            session_type="workflow",
            participant_ids=["agent", "system", "user"],
        )
        self.state_manager.change_state(AgentState.RUNNING)
        self.session_manager.update_session_status(
            self.session, self.state_manager.state
        )

        # 设置工作流定义
        self.workflow_definition = workflow_definition

        # 首先检测是否是复杂任务，需要任务分解
        # 导入任务分解处理器
        from daip_live.task_decomposition.automatic_task_decomposition_engine import (
            AutoTaskDecompositionEngine,
        )

        # 检查模型提供者是否可用
        if self.model_provider:
            task_decomposition_engine = AutoTaskDecompositionEngine(self.model_provider)
            should_decompose = (
                await task_decomposition_engine.should_process_with_task_decomposition(
                    goal
                )
            )

            if should_decompose:
                # 使用任务分解处理复杂请求

                # 生成任务清单并执行
                async for (
                    event
                ) in task_decomposition_engine.process_with_task_decomposition(goal):
                    yield event
            else:
                # 不需要任务分解，按原有的Todo列表执行
                todo_list = await self.memory_service.get_todo_list()
                current_task_index = 0
                self.step_executor.last_final_response = None

                try:
                    workflow_failed = False

                    # 如果有工作流定义，按工作流执行
                    if self.workflow_definition:
                        async for event in self.workflow_executor.execute_workflow(
                            self.workflow_definition
                        ):
                            yield event
                            # 检查是否有工作流失败的特殊事件
                            if isinstance(
                                event, ThoughtEvent
                            ) and event.content.startswith(
                                "WORKFLOW_EXECUTION_FAILED:"
                            ):
                                workflow_failed = True
                                self.state_manager.change_state(AgentState.FAILED)
                                break
                    else:
                        # 否则按原有的Todo列表执行
                        while (
                            current_task_index < len(todo_list)
                            and not await self.memory_service.is_todo_list_complete()
                        ):
                            # --- Outer loop: Get next task and delegate execution ---
                            current_task = todo_list[current_task_index]

                            # Reset context for the new step
                            self.step_executor.llm_response = ""
                            self.step_executor.last_tool_result = None
                            self.state_manager.change_state(AgentState.THINKING)

                            # Delegate the entire step execution to the helper method
                            async for event in self.step_executor.execute_step(
                                current_task, self.session
                            ):
                                yield event

                            if self.state_manager.state == AgentState.FAILED:
                                workflow_failed = True
                                break  # Exit outer loop on failure

                            await self.memory_service.update_todo_status(
                                current_task_index
                            )
                            current_task_index += 1

                    if (
                        not workflow_failed
                        and self.state_manager.state != AgentState.FAILED
                    ):
                        self.state_manager.change_state(AgentState.COMPLETED)
                        if not self.step_executor.last_final_response:
                            yield FinalResponseEvent(
                                content="Plan completed successfully."
                            )

                finally:
                    if self.session:
                        if self.step_executor.last_final_response:
                            final_answer_pattern = re.compile(
                                r"Final Answer:\s*", re.IGNORECASE
                            )
                            summary_content = final_answer_pattern.sub(
                                "", self.step_executor.last_final_response.content
                            ).strip()
                            self.session.summary = summary_content
                        self.session_manager.update_session_status(
                            self.session, self.state_manager.state
                        )
                        self.session_manager.save_session(self.session)
                        session_event = await self.session_manager.create_session_event(
                            self.session.session_id, self.state_manager.state
                        )
                        yield session_event
        else:
            # 如果没有模型提供者，按原有的Todo列表执行
            todo_list = await self.memory_service.get_todo_list()
            current_task_index = 0
            self.step_executor.last_final_response = None

            try:
                workflow_failed = False

                # 如果有工作流定义，按工作流执行
                if self.workflow_definition:
                    async for event in self.workflow_executor.execute_workflow(
                        self.workflow_definition
                    ):
                        yield event
                        # 检查是否有工作流失败的特殊事件
                        if isinstance(event, ThoughtEvent) and event.content.startswith(
                            "WORKFLOW_EXECUTION_FAILED:"
                        ):
                            workflow_failed = True
                            self.state_manager.change_state(AgentState.FAILED)
                            break
                else:
                    # 否则按原有的Todo列表执行
                    while (
                        current_task_index < len(todo_list)
                        and not await self.memory_service.is_todo_list_complete()
                    ):
                        # --- Outer loop: Get next task and delegate execution ---
                        current_task = todo_list[current_task_index]

                        # Reset context for the new step
                        self.step_executor.llm_response = ""
                        self.step_executor.last_tool_result = None
                        self.state_manager.change_state(AgentState.THINKING)

                        # Delegate the entire step execution to the helper method
                        async for event in self.step_executor.execute_step(
                            current_task, self.session
                        ):
                            yield event

                        if self.state_manager.state == AgentState.FAILED:
                            workflow_failed = True
                            break  # Exit outer loop on failure

                        await self.memory_service.update_todo_status(current_task_index)
                        current_task_index += 1

                if (
                    not workflow_failed
                    and self.state_manager.state != AgentState.FAILED
                ):
                    self.state_manager.change_state(AgentState.COMPLETED)
                    if not self.step_executor.last_final_response:
                        yield FinalResponseEvent(content="Plan completed successfully.")

            finally:
                if self.session:
                    if self.step_executor.last_final_response:
                        final_answer_pattern = re.compile(
                            r"Final Answer:\s*", re.IGNORECASE
                        )
                        summary_content = final_answer_pattern.sub(
                            "", self.step_executor.last_final_response.content
                        ).strip()
                        self.session.summary = summary_content
                    self.session_manager.update_session_status(
                        self.session, self.state_manager.state
                    )
                    self.session_manager.save_session(self.session)
                    session_event = await self.session_manager.create_session_event(
                        self.session.session_id, self.state_manager.state
                    )
                    yield session_event

    async def chat_run(self, initial_goal: str) -> AsyncGenerator[AgentEvent, None]:
        """Runs the agent in an interactive chat mode."""
        # 检测初始目标是否需要任务分解
        from daip_live.task_decomposition.automatic_task_decomposition_engine import (
            AutoTaskDecompositionEngine,
        )

        # 检查模型提供者是否可用
        if self.model_provider:
            task_decomposition_engine = AutoTaskDecompositionEngine(self.model_provider)
            should_decompose = (
                await task_decomposition_engine.should_process_with_task_decomposition(
                    initial_goal
                )
            )

            if should_decompose:
                # 使用任务分解处理复杂初始目标

                # 生成任务清单并执行
                async for (
                    event
                ) in task_decomposition_engine.process_with_task_decomposition(
                    initial_goal
                ):
                    yield event
            else:
                # 不需要任务分解，使用常规聊天执行器
                async for event in self.chat_executor.chat_run(
                    initial_goal, self.step_executor
                ):
                    yield event
        else:
            # 如果没有模型提供者，直接使用常规聊天执行器
            async for event in self.chat_executor.chat_run(
                initial_goal, self.step_executor
            ):
                yield event

    def _change_state(self, new_state: AgentState):
        self.state_manager.change_state(new_state)

    @property
    def state(self):
        """获取当前状态以保持向后兼容性"""
        return self.state_manager.state

    # 保持原有方法以确保向后兼容性
    async def _process_chat_turn(
        self, turn_description: str
    ) -> AsyncGenerator[AgentEvent, None]:
        """Helper to process a single turn in a chat, avoiding code duplication."""
        # Reset context for the new turn
        self.step_executor.llm_response = ""
        self.step_executor.last_tool_result = None
        self.step_executor.reflection_count = 0
        self.state_manager.change_state(AgentState.THINKING)

        # Execute the user input as the new task
        current_task = TodoItem(
            id=0, description=turn_description, status="pending", priority=1
        )
        async for event in self.step_executor.execute_step(current_task):
            yield event

    async def _execute_workflow(self) -> AsyncGenerator[AgentEvent, None]:
        """执行工作流"""
        if self.workflow_definition:
            async for event in self.workflow_executor.execute_workflow(
                self.workflow_definition
            ):
                yield event

    async def _recover_workflow_state(self) -> AsyncGenerator[AgentEvent, None]:
        """恢复工作流执行状态"""
        if self.workflow_executor:
            async for event in self.workflow_executor._recover_workflow_state():
                yield event

    async def _persist_workflow_state(self) -> AsyncGenerator[AgentEvent, None]:
        """持久化工作流执行状态"""
        if self.workflow_executor:
            async for event in self.workflow_executor._persist_workflow_state():
                yield event

    async def _execute_workflow_element_events(
        self, element: Any
    ) -> AsyncGenerator[AgentEvent, None]:
        """执行工作流元素并产生事件"""
        # 这个方法现在在WorkflowExecutor中实现
        async for event in self.workflow_executor._execute_workflow_element_events(
            element, {}, {}
        ):
            yield event

    def _get_next_element_id(self, element: Any) -> Optional[str]:
        """获取下一个元素ID"""
        # 这个方法现在在WorkflowExecutor中实现
        return self.workflow_executor._get_next_element_id(element, {})

    async def _execute_task_element_events(
        self, element: Any
    ) -> AsyncGenerator[AgentEvent, None]:
        """执行任务元素并产生事件"""
        # 这个方法现在在WorkflowExecutor中实现
        async for event in self.workflow_executor._execute_task_element_events(
            element, {}
        ):
            yield event

    def _get_task_next_element_id(self, element: Any) -> Optional[str]:
        """获取任务元素的下一个元素ID"""
        # 这个方法现在在WorkflowExecutor中实现
        return self.workflow_executor._get_task_next_element_id(element)

    async def _execute_condition_element_events(
        self, element: Any
    ) -> AsyncGenerator[AgentEvent, None]:
        """执行条件元素并产生事件"""
        # 这个方法现在在WorkflowExecutor中实现
        async for event in self.workflow_executor._execute_condition_element_events(
            element
        ):
            yield event

    def _get_condition_next_element_id(self, element: Any) -> Optional[str]:
        """获取条件元素的下一个元素ID"""
        # 这个方法现在在WorkflowExecutor中实现
        return self.workflow_executor._get_condition_next_element_id(element)

    async def _execute_loop_element_events(
        self, element: Any
    ) -> AsyncGenerator[AgentEvent, None]:
        """执行循环元素并产生事件"""
        # 这个方法现在在WorkflowExecutor中实现
        async for event in self.workflow_executor._execute_loop_element_events(
            element, {}
        ):
            yield event

    def _get_loop_next_element_id(self, element: Any) -> Optional[str]:
        """获取循环元素的下一个元素ID"""
        # 这个方法现在在WorkflowExecutor中实现
        return self.workflow_executor._get_loop_next_element_id(element, {})

    async def _execute_subworkflow_element_events(
        self, element: Any
    ) -> AsyncGenerator[AgentEvent, None]:
        """执行子工作流元素并产生事件"""
        # 这个方法现在在WorkflowExecutor中实现
        async for event in self.workflow_executor._execute_subworkflow_element_events(
            element
        ):
            yield event

    def _get_subworkflow_next_element_id(self, element: Any) -> Optional[str]:
        """获取子工作流元素的下一个元素ID"""
        # 这个方法现在在WorkflowExecutor中实现
        return self.workflow_executor._get_subworkflow_next_element_id(element)

    async def _execute_step(
        self, current_task: TodoItem
    ) -> AsyncGenerator[AgentEvent, None]:
        """Executes a single step from the Todo list using a state machine."""
        async for event in self.step_executor.execute_step(current_task):
            yield event

    async def _execute_tool_with_permission_check(
        self, tool_name: str, args: dict[str, Any], session_context: SessionContext
    ) -> Any:
        """
        带权限检查的工具执行 - 核心权限集成函数
        """
        # 这个方法现在在StepExecutor中实现
        return await self.step_executor._execute_tool_with_permission_check(
            tool_name, args, session_context
        )

    def _assess_tool_risk(self, tool_name: str, args: dict[str, Any]) -> str:
        """
        评估工具风险等级 - 基于KISS原则的简化实现
        """
        # 这个方法现在在StepExecutor中实现
        return self.step_executor._assess_tool_risk(tool_name, args)

    def _parse_tool_call(self, text: str) -> Optional[tuple[str, dict[str, Any]]]:
        """
        解析工具调用
        """
        # 这个方法现在在StepExecutor中实现
        return self.step_executor._parse_tool_call(text)
