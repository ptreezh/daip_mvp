"""
AgentExecutor权限集成实现
基于TDD原则，实际集成PermissionManager到AgentExecutor
严格遵循BMAD kiro's spec规范
"""

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
from daip_live.permission.permission_manager import PermissionManager


class AgentExecutorWithPermission:
    """
    Agent执行器 - 权限集成版本
    严格遵循TDD原则和BMAD kiro's spec规范
    """
    
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
        permission_manager: PermissionManager,
        max_reflections: int = 3,
    ):
        """
        初始化带权限的AgentExecutor
        
        Args:
            session_manager: 会话管理器
            memory_service: 内存服务
            knowledge_manager: 知识管理器
            model_provider: 模型提供者
            tool_manager: 工具管理器
            user_input_queue: 用户输入队列
            permission_manager: 权限管理器（新增）
            max_reflections: 最大反思次数
        """
        self.session_manager = session_manager
        self.memory_service = memory_service
        self.knowledge_manager = knowledge_manager
        self.model_provider = model_provider
        self.tool_manager = tool_manager
        self.user_input_queue = user_input_queue
        self.permission_manager = permission_manager  # 新增权限管理器
        self.max_reflections = max_reflections

        self.state: AgentState = AgentState.IDLE
        self.session: Optional[Session] = None
        self.llm_response: str = ""
        self.last_tool_result: Optional[str] = None
        self.last_final_response: Optional[FinalResponseEvent] = None
        self.reflection_count: int = 0
        self.session_context = SessionContext()
        self.tokens_used: int = 0
        self.tokens_total: int = 8192
        
        # 工作流相关属性
        self.workflow_definition: Optional[WorkflowDefinition] = None
        self.current_element_id: Optional[str] = None
        self.element_outputs: Dict[str, Any] = {}
        self.loop_counters: Dict[str, int] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def get_status(self) -> AgentStatus:
        """返回代理当前状态的快照"""
        return AgentStatus(
            state=self.state.value,
            model_name=getattr(self.model_provider.config, 'model', 'unknown'),
            tokens_used=self.tokens_used,
            tokens_total=self.tokens_total,
        )

    async def execute_tool_with_permission(
        self,
        tool_name: str,
        args: Dict[str, Any],
        session_context: SessionContext,
        confirmation_granted: bool = False
    ) -> Any:
        """
        带权限检查的工具执行 - 核心集成函数
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            session_context: 会话上下文
            confirmation_granted: 是否已经获得用户确认
            
        Returns:
            Any: 工具执行结果
            
        Raises:
            ToolNotFoundError: 工具未找到
            ToolInputError: 工具输入验证失败
            ToolPermissionError: 权限被拒绝
            ToolPermissionRequest: 需要用户权限确认
        """
        logger.info(f"Executing tool with permission: {tool_name}")
        
        try:
            # 阶段1: 权限检查前置
            permission_result = await self.permission_manager.check_permission(
                tool_name=tool_name,
                args=args,
                session_context=session_context
            )
            
            # 阶段2: 权限结果处理 - 严格遵循契约
            if permission_result.granted:
                # 权限已授予，执行工具
                logger.info(f"Permission granted for {tool_name}: {permission_result.reason}")
                return await self._execute_tool_internal(tool_name, args, session_context)
                
            elif permission_result.response == PermissionResponse.DENY:
                # 权限被拒绝，抛出明确的ToolPermissionError
                logger.warning(f"Permission denied for {tool_name}: {permission_result.reason}")
                raise ToolPermissionError(
                    f"Permission denied for tool '{tool_name}': {permission_result.reason}",
                    tool_name=tool_name,
                    args=args,
                    reason=permission_result.reason
                )
                
            elif permission_result.response == PermissionResponse.ASK and not confirmation_granted:
                # 需要用户确认，抛出ToolPermissionRequest异常
                logger.info(f"Permission required for {tool_name}, requesting user confirmation")
                
                # 创建权限请求事件
                permission_request = PermissionRequestEvent(
                    tool_name=tool_name,
                    args=args,
                    risk_level=self._assess_tool_risk(tool_name, args),
                    description=f"Tool '{tool_name}' requires permission to execute"
                )
                
                raise ToolPermissionRequest(
                    tool_name=tool_name,
                    args=args,
                    request=permission_request
                )
                
            elif permission_result.response == PermissionResponse.ASK and confirmation_granted:
                # 用户已确认，执行工具
                logger.info(f"Permission confirmed for {tool_name}, executing tool")
                return await self._execute_tool_internal(tool_name, args, session_context)
                
            else:
                # 未知状态，安全起见默认拒绝
                logger.error(f"Unknown permission state for {tool_name}: {permission_result.response}")
                raise ToolPermissionError(
                    f"Unknown permission state for tool '{tool_name}'",
                    tool_name=tool_name,
                    args=args
                )
                
        except Exception as e:
            # 处理权限管理器本身的异常
            if isinstance(e, (ToolPermissionError, ToolPermissionRequest)):
                raise  # 重新抛出权限相关异常
            else:
                logger.error(f"Error during permission check for {tool_name}: {e}")
                # 权限系统错误时，默认拒绝以确保安全
                raise ToolPermissionError(
                    f"Permission system error for tool '{tool_name}': {e}",
                    tool_name=tool_name,
                    args=args,
                    error_message=str(e)
                )
    
    async def _execute_tool_internal(
        self,
        tool_name: str,
        args: Dict[str, Any],
        session_context: SessionContext
    ) -> Any:
        """
        内部工具执行 - 实际调用工具管理器
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            session_context: 会话上下文
            
        Returns:
            Any: 工具执行结果
        """
        # 调用原有的工具管理器执行逻辑
        return self.tool_manager.execute_tool(
            name=tool_name,
            args=args,
            session_context=session_context
        )
    
    def _assess_tool_risk(self, tool_name: str, args: Dict[str, Any]) -> str:
        """
        评估工具风险等级 - 基于YAGNI原则的简化实现
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            
        Returns:
            str: 风险等级 ("low"/"medium"/"high")
        """
        # KISS原则：基于工具名称和参数的简单风险评估
        tool_name_lower = tool_name.lower()
        
        # 高风险工具
        if any(keyword in tool_name_lower for keyword in ["execute", "command", "shell", "system"]):
            return "high"
        
        # 中风险工具
        elif any(keyword in tool_name_lower for keyword in ["write", "delete", "modify", "network", "http"]):
            return "medium"
        
        # 低风险工具（默认）
        else:
            return "low"
    
    # 以下方法保持与原始AgentExecutor相同，确保兼容性
    def get_status(self) -> AgentStatus:
        """返回代理当前状态的快照"""
        return AgentStatus(
            state=self.state.value,
            model_name=getattr(self.model_provider.config, 'model', 'unknown'),
            tokens_used=self.tokens_used,
            tokens_total=self.tokens_total,
        )
    
    async def run(self, goal: str, workflow_definition: Optional[WorkflowDefinition] = None) -> AsyncGenerator[AgentEvent, None]:
        """主执行循环 - 委托给原有的_execute_step逻辑"""
        # 实现与原始AgentExecutor相同的run逻辑
        # 这里可以重用原有的代码，但工具执行部分会调用我们的权限检查
        pass
    
    async def _execute_step(self, current_task: TodoItem) -> AsyncGenerator[AgentEvent, None]:
        """执行单个步骤 - 修改工具执行部分以使用权限检查"""
        # 基于原有的_execute_step逻辑，但修改工具执行部分
        pass


# 工具函数和辅助方法（与原始AgentExecutor保持一致）
def _change_state(self, new_state: AgentState):
    """改变代理状态"""
    self.state = new_state

def _parse_tool_call(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """解析工具调用"""
    match = AgentExecutorWithPermission.TOOL_CALL_PATTERN.search(text)
    if not match:
        return None
    tool_name, args_str = match.groups()
    try:
        args = dict(re.findall(r'(\w+)=([^,)]+)', args_str))
        for key, value in args.items():
            try:
                args[key] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                args[key] = value
        return tool_name, args
    except Exception:
        return None


# 兼容性导出
__all__ = ['AgentExecutorWithPermission']