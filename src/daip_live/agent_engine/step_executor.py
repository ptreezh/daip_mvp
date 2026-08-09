"""
StepExecutor - 步骤执行器
专门负责执行单个步骤
遵循KISS/YAGNI/SOLID原则
"""

import ast
import asyncio
import logging
import re
import time
from collections.abc import AsyncGenerator
from typing import Any, Optional

from daip_live.core.models import (
    AgentEvent,
    AgentState,
    DialogueTurn,
    FinalResponseEvent,
    ModelMetricsEvent,
    PermissionRequestEvent,
    PermissionResponse,
    Session,
    SessionContext,
    ThoughtEvent,
    TodoItem,
    TokenUsageEvent,
    ToolCallEvent,
    ToolOutputEvent,
)
from daip_live.memory.service import MemoryService
from daip_live.p4_role_manager_tools.tool_manager import ToolPermissionRequest
from daip_live.permission.permission_manager import PermissionManager

logger = logging.getLogger(__name__)


from daip_live.agent_engine.state_manager import StateManager  # noqa: E402


class StepExecutor:
    """
    步骤执行器 - 专门负责执行单个步骤
    遵循单一职责原则，只关注步骤执行相关功能
    """

    TOOL_CALL_PATTERN = re.compile(r"Use Tool:\s*(\w+)\s*\((.*)\)")
    CONFIDENCE_PATTERN = re.compile(r"Confidence: (\d\.\d+)")
    FINAL_ANSWER_PATTERN = re.compile(r"Final Answer:\s*", re.IGNORECASE)

    def __init__(
        self,
        state_manager: StateManager,  # 新增
        memory_service: MemoryService,
        model_provider: Any,
        tool_manager: Any,
        user_input_queue: asyncio.Queue,
        permission_manager: Optional[PermissionManager] = None,
        max_reflections: int = 3,
    ):
        """
        初始化步骤执行器

        Args:
            state_manager: 状态管理器
            memory_service: 内存服务
            model_provider: 模型提供者
            tool_manager: 工具管理器
            user_input_queue: 用户输入队列
            permission_manager: 权限管理器
            max_reflections: 最大反思次数
        """
        self.state_manager = state_manager  # 新增
        self.memory_service = memory_service
        self.model_provider = model_provider
        self.tool_manager = tool_manager
        self.user_input_queue = user_input_queue
        self.permission_manager = permission_manager
        self.max_reflections = max_reflections

        self.llm_response: str = ""
        self.last_tool_result: Optional[str] = None
        self.last_final_response: Optional[FinalResponseEvent] = None
        self.reflection_count: int = 0
        self.session_context = SessionContext()
        # self.tokens_used: int = 0 # 移除
        self._request_count: int = 0

        logger.info("StepExecutor initialized")

    async def execute_step(
        self, current_task: TodoItem, session: "Session"
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        执行单个步骤

        Args:
            current_task: 当前任务

        Yields:
            AgentEvent: 执行事件
        """
        step_completed = False
        max_iterations = 20  # Prevent infinite loops - increased for complex workflows
        iteration_count = 0
        failed_tool_calls = set()  # Track failed tool calls to avoid repetition
        state = AgentState.THINKING

        while not step_completed and iteration_count < max_iterations:
            # 1. OBSERVE & STEER
            try:
                user_command = self.user_input_queue.get_nowait()
                yield ThoughtEvent(content=f"Received steering command: {user_command}")
                self.last_tool_result = f"User steering command: {user_command}"
                state = AgentState.THINKING  # Force re-thinking
            except asyncio.QueueEmpty:
                pass  # No user command

            iteration_count += 1
            if iteration_count >= max_iterations:
                yield ThoughtEvent(
                    content=f"Maximum iterations ({max_iterations}) reached for this step. Forcing completion."  # noqa: E501
                )
                self.last_final_response = FinalResponseEvent(
                    content="Step completed due to iteration limit."
                )
                yield self.last_final_response
                step_completed = True
                break

            # 2. ACT based on current state
            if state == AgentState.THINKING:
                yield ThoughtEvent(
                    content=f"Thinking about task: {current_task.description}"
                )
                prompt = await self.memory_service.construct_prompt(
                    current_task.description,
                    self.last_tool_result,
                    self.llm_response,
                    session,
                )
                start_time = time.time()
                async for chunk in self.model_provider.generate(
                    prompt, params={"max_tokens": 1024, "temperature": 0.7}
                ):
                    self.llm_response = chunk
                    break
                usage = None  # 真实模型不返回 usage（调用方有 None 保护）
                latency = time.time() - start_time

                # Send token usage event
                if usage and isinstance(usage, dict):
                    yield TokenUsageEvent(usage_info=usage)
                    if "total_tokens" in usage:
                        self.state_manager.update_tokens(usage["total_tokens"])

                # Append agent's response to history
                session.history.append(
                    DialogueTurn(participant_id="agent", content=self.llm_response)
                )

                # Send model metrics event
                self._request_count += 1
                yield ModelMetricsEvent(
                    latency=latency, request_count=self._request_count
                )
                state = AgentState.EVALUATING

            elif state == AgentState.EVALUATING:
                confidence_match = self.CONFIDENCE_PATTERN.search(self.llm_response)
                confidence = (
                    float(confidence_match.group(1)) if confidence_match else 1.0
                )

                if confidence < 0.85 and self.reflection_count < self.max_reflections:
                    self.reflection_count += 1
                    yield ThoughtEvent(
                        content=f"Confidence is low ({confidence}). Reflecting... ({self.reflection_count}/{self.max_reflections})"  # noqa: E501
                    )
                    self.last_tool_result = f"Self-reflection: The previous response had low confidence ({confidence}). I need to reconsider my approach to be more certain."  # noqa: E501
                    state = AgentState.THINKING
                else:
                    tool_call = self._parse_tool_call(self.llm_response)
                    if tool_call:
                        name, args = tool_call
                        # Create a unique key for this tool call to detect repetitions
                        tool_call_key = f"{name}:{sorted(args.items()) if args else ''}"

                        if tool_call_key in failed_tool_calls:
                            yield ThoughtEvent(
                                content=f"Tool '{name}' with these arguments already failed. Skipping to avoid repetition."  # noqa: E501
                            )
                            state = AgentState.RESPONDING
                        else:
                            has_tool = hasattr(
                                self.tool_manager, "_registry"
                            ) and name in getattr(self.tool_manager, "_registry", {})
                            if not has_tool:
                                yield ThoughtEvent(
                                    content=f"Tool '{name}' not available. Ignored."
                                )
                                failed_tool_calls.add(
                                    tool_call_key
                                )  # Mark as failed to avoid retry
                                state = AgentState.RESPONDING
                            else:
                                state = AgentState.EXECUTING_TOOL
                    else:
                        # For chat scenarios, ensure we always move to responding state to generate a response  # noqa: E501
                        state = AgentState.RESPONDING

            elif state == AgentState.EXECUTING_TOOL:
                tool_name, tool_args = self._parse_tool_call(self.llm_response)
                yield ToolCallEvent(tool_name=tool_name, args=tool_args)
                try:
                    # 权限集成：在工具执行前进行权限检查
                    if self.permission_manager:
                        tool_result = await self._execute_tool_with_permission_check(
                            tool_name, tool_args, self.session_context
                        )
                    else:
                        # 向后兼容：无权限管理器时直接执行（同步调用）
                        tool_result = self.tool_manager.execute_tool(
                            tool_name, tool_args, session_context=self.session_context
                        )
                    yield ToolOutputEvent(
                        tool_name=tool_name, status="success", output=tool_result
                    )
                    self.last_tool_result = tool_result
                    state = AgentState.THINKING
                except Exception as e:
                    # Create tool call key for tracking failed attempts
                    tool_call_key = (
                        f"{tool_name}:{sorted(tool_args.items()) if tool_args else ''}"
                    )

                    if isinstance(e, ToolPermissionRequest):
                        yield PermissionRequestEvent(
                            tool_name=tool_name, args=tool_args
                        )
                        # 权限请求现在由权限管理器处理，这里只处理异常情况
                        self.last_tool_result = f"Permission request for tool '{tool_name}' requires user interaction."  # noqa: E501
                        yield ToolOutputEvent(
                            tool_name=tool_name,
                            status="error",
                            output=self.last_tool_result,
                        )
                        failed_tool_calls.add(tool_call_key)
                        state = AgentState.RESPONDING
                    else:
                        self.last_tool_result = f"Error: {e}"
                        yield ToolOutputEvent(
                            tool_name=tool_name,
                            status="error",
                            output=self.last_tool_result,
                        )
                        failed_tool_calls.add(tool_call_key)
                        state = AgentState.FAILED
                        step_completed = True

            elif state == AgentState.RESPONDING:
                # Process the response to extract meaningful content
                final_answer = self.CONFIDENCE_PATTERN.sub(
                    "", self.llm_response
                ).strip()
                final_answer = self.TOOL_CALL_PATTERN.sub("", final_answer).strip()
                final_answer = self.FINAL_ANSWER_PATTERN.sub("", final_answer).strip()

                # Ensure we have some content to return, especially for chat scenarios
                if not final_answer or final_answer.isspace():
                    # If the processed answer is empty, use the original response
                    # This is particularly important for chat responses that may not follow strict format  # noqa: E501
                    final_answer = self.llm_response.strip()

                # Sanitize the final answer to remove any remaining patterns
                final_answer = final_answer.replace("Confidence: 1.0", "").strip()

                # Ensure we have meaningful content to return
                if final_answer and final_answer not in ["", " ", "\n"]:
                    self.last_final_response = FinalResponseEvent(content=final_answer)
                    yield self.last_final_response
                else:
                    # If all processing resulted in empty content, provide a default response  # noqa: E501
                    self.last_final_response = FinalResponseEvent(
                        content="处理完成，但未生成明确的响应内容。"
                    )
                    yield self.last_final_response

                step_completed = True  # This step is done

    async def _execute_tool_with_permission_check(
        self, tool_name: str, args: dict[str, Any], session_context: SessionContext
    ) -> Any:
        """
        带权限检查的工具执行 - 核心权限集成函数

        Args:
            tool_name: 工具名称
            args: 工具参数
            session_context: 会话上下文

        Returns:
            Any: 工具执行结果

        Raises:
            ToolPermissionError: 权限被拒绝
            ToolPermissionRequest: 需要用户权限确认
            ToolNotFoundError: 工具未找到
            ToolInputError: 工具输入验证失败
        """
        logger.info(f"Executing tool with permission check: {tool_name}")

        try:
            # 权限检查前置 - 严格遵循契约
            permission_result = await self.permission_manager.check_permission(
                tool_name=tool_name, args=args, session_context=session_context
            )

            # 权限结果处理 - 遵循BMAD规范
            if permission_result.granted:
                # 权限已授予，执行工具（同步调用）
                logger.info(
                    f"Permission granted for {tool_name}: {permission_result.reason}"
                )
                return self.tool_manager.execute_tool(
                    tool_name, args, session_context=session_context
                )

            elif permission_result.response == PermissionResponse.DENY:
                # 权限被拒绝，抛出明确的ToolPermissionError
                logger.warning(
                    f"Permission denied for {tool_name}: {permission_result.reason}"
                )
                from daip_live.p4_role_manager_tools.tool_manager import (
                    ToolPermissionError,
                )

                raise ToolPermissionError(
                    f"Permission denied for tool '{tool_name}': {permission_result.reason}",  # noqa: E501
                    tool_name=tool_name,
                    args=args,
                    reason=permission_result.reason,
                )

            elif permission_result.response == PermissionResponse.ASK:
                # 需要用户确认，抛出ToolPermissionRequest异常
                logger.info(
                    f"Permission required for {tool_name}, requesting user confirmation"
                )

                # 创建权限请求事件
                permission_request = PermissionRequestEvent(
                    tool_name=tool_name,
                    args=args,
                    risk_level=self._assess_tool_risk(tool_name, args),
                    description=f"Tool '{tool_name}' requires permission to execute",
                )

                from daip_live.p4_role_manager_tools.tool_manager import (
                    ToolPermissionRequest,
                )

                raise ToolPermissionRequest(
                    tool_name=tool_name, args=args, request=permission_request
                )

            else:
                # 未知状态，安全起见默认拒绝
                logger.error(
                    f"Unknown permission state for {tool_name}: {permission_result.response}"  # noqa: E501
                )
                from daip_live.p4_role_manager_tools.tool_manager import (
                    ToolPermissionError,
                )

                raise ToolPermissionError(
                    f"Unknown permission state for tool '{tool_name}'",
                    tool_name=tool_name,
                    args=args,
                )

        except Exception as e:
            # 处理权限管理器本身的异常
            if isinstance(e, (ToolPermissionError, ToolPermissionRequest)):
                raise  # 重新抛出权限相关异常
            else:
                logger.error(f"Error during permission check for {tool_name}: {e}")
                # 权限系统错误时，默认拒绝以确保安全
                from daip_live.p4_role_manager_tools.tool_manager import (
                    ToolPermissionError,
                )

                raise ToolPermissionError(
                    f"Permission system error for tool '{tool_name}': {e}",
                    tool_name=tool_name,
                    args=args,
                    error_message=str(e),
                )

    def _assess_tool_risk(self, tool_name: str, args: dict[str, Any]) -> str:
        """
        评估工具风险等级 - 基于KISS原则的简化实现

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            str: 风险等级 ("low"/"medium"/"high")
        """
        # KISS原则：基于工具名称的简单风险评估
        tool_name_lower = tool_name.lower()

        # 高风险工具
        if any(
            keyword in tool_name_lower
            for keyword in ["execute", "command", "shell", "system"]
        ):
            return "high"

        # 中风险工具
        elif any(
            keyword in tool_name_lower
            for keyword in ["write", "delete", "modify", "network", "http"]
        ):
            return "medium"

        # 低风险工具（默认）
        else:
            return "low"

    def _parse_tool_call(self, text: str) -> Optional[tuple[str, dict[str, Any]]]:
        """
        解析工具调用
        """
        match = self.TOOL_CALL_PATTERN.search(text)
        if not match:
            return None
        tool_name, args_str = match.groups()
        try:
            # A slightly more robust arg parser
            args = dict(re.findall(r"(\w+)=([^,)]+)", args_str))
            for key, value in args.items():
                try:
                    args[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    args[key] = value  # Keep as string if it's not a literal
            return tool_name, args
        except Exception:
            return None
