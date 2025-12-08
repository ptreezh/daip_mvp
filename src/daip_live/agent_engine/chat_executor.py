"""
ChatExecutor - 聊天执行器
专门负责聊天模式的执行
遵循KISS/YAGNI/SOLID原则
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, Optional, Dict

from daip_live.core.models import (
    AgentEvent,
    AgentState,
    DialogueTurn,
    FinalResponseEvent,
    ThoughtEvent,
    TodoItem,
)
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager as BaseSessionManager
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

logger = logging.getLogger(__name__)


class ChatExecutor:
    """
    聊天执行器 - 专门负责聊天模式执行功能
    遵循单一职责原则，只关注聊天执行相关功能
    """
    
    def __init__(
        self,
        session_manager: BaseSessionManager,
        memory_service: MemoryService,
        user_input_queue: asyncio.Queue,
    ):
        """
        初始化聊天执行器
        
        Args:
            session_manager: 会话管理器
            memory_service: 内存服务
            user_input_queue: 用户输入队列
        """
        self.session_manager = session_manager
        self.memory_service = memory_service
        self.user_input_queue = user_input_queue
        self.intent_recognizer = EnhancedIntentRecognizer()
        logger.info("ChatExecutor initialized")
    
    async def chat_run(self, initial_goal: str, step_executor: Any) -> AsyncGenerator[AgentEvent, None]:
        """
        运行聊天模式
        
        Args:
            initial_goal: 初始目标
            step_executor: 步骤执行器
            
        Yields:
            AgentEvent: 聊天事件
        """
        # 创建会话
        session = self.session_manager.create_session(
            goal=initial_goal, session_type="chat", participant_ids=["agent", "user"]
        )
        
        yield ThoughtEvent(content=f"Session {session.session_id} started for goal: {initial_goal}")
        
        # Process the initial goal
        async for event in self._process_chat_turn(initial_goal, step_executor, session):
            yield event
        
        try:
            while True:
                # Wait for user input from the TUI
                user_input = await self.user_input_queue.get()
                if user_input is None:  # Add a way to gracefully exit the loop
                    break
                
                session.history.append(DialogueTurn(participant_id="user", content=user_input))
                
                async for event in self._process_chat_turn(user_input, step_executor, session):
                    yield event
                
                self.user_input_queue.task_done()
        
        finally:
            # 保存会话
            session.status = AgentState.COMPLETED
            self.session_manager.save_session(session)
            yield ThoughtEvent(content=f"Session {session.session_id} saved with status {AgentState.COMPLETED.name}")
    
    async def _process_chat_turn(self, turn_description: str, step_executor: Any, session: Any) -> AsyncGenerator[AgentEvent, None]:
        """
        处理单个聊天回合

        Args:
            turn_description: 回合描述
            step_executor: 步骤执行器
            session: 会话

        Yields:
            AgentEvent: 处理事件
        """
        # 首先尝试识别用户意图
        intent = self.intent_recognizer.recognize_intent(turn_description)

        if intent and intent.confidence > 0.5:  # 设置置信度阈值
            # 如果识别到意图，显示意图信息
            yield ThoughtEvent(content=f"识别到意图: {intent.description} (置信度: {intent.confidence:.2f})")

            # 检查工具可用性并执行相应操作
            tool_executed_result = None
            async for result in self._try_execute_tool(intent, step_executor, session):
                if isinstance(result, bool):
                    tool_executed_result = result
                else:
                    yield result

            if tool_executed_result:
                return  # 工具已执行，不需要继续处理

        # 没有识别到意图或工具执行失败，按普通聊天处理
        current_task = TodoItem(id=0, description=turn_description, status="pending", priority=1)

        # 添加一个标志，确保至少有一个事件被发出
        events_generated = False

        async for event in step_executor.execute_step(current_task, session):
            yield event
            events_generated = True

        # 如果执行步骤后没有生成任何事件，发送一个基本响应以确保TUI收到反馈
        if not events_generated:
            yield ThoughtEvent(content="正在处理您的请求...")
            # 可能需要触发一次简单的响应
    
    async def _try_execute_tool(self, intent: Any, step_executor: Any, session: Any):
        """
        尝试执行识别到的工具
        
        Args:
            intent: 识别到的意图
            step_executor: 步骤执行器
            session: 会话
            
        Yields:
            AgentEvent: 工具执行事件
            bool: 是否成功执行了工具 (通过yield返回)
        """
        # 获取工具管理器
        tool_manager = getattr(step_executor, 'tool_manager', None)
        if not tool_manager:
            yield ThoughtEvent(content="工具管理器不可用")
            yield False
            return
        
        # 检查工具是否可用
        available_tools = getattr(tool_manager, '_registry', {})
        if intent.tool_name not in available_tools:
            yield ThoughtEvent(content=f"工具 '{intent.tool_name}' 不可用")
            yield False
            return
        
        # 获取工具函数
        tool_func = available_tools[intent.tool_name]
        
        # 检查工具参数模式
        input_schema = getattr(tool_func, 'input_schema', None)
        if not input_schema:
            yield ThoughtEvent(content=f"工具 '{intent.tool_name}' 缺少参数定义")
            yield False
            return
        
        # 准备工具参数
        try:
            tool_args = self._prepare_tool_args(intent, input_schema)
            yield ThoughtEvent(content=f"准备调用工具: {intent.tool_name}({', '.join(f'{k}={v}' for k, v in tool_args.items())})")
            
            # 执行工具
            result = tool_manager.execute_tool(
                intent.tool_name, 
                tool_args, 
                session_context=getattr(step_executor, 'session_context', None)
            )
            
            yield ThoughtEvent(content=f"工具执行结果: {result}")
            yield True
            
        except Exception as e:
            yield ThoughtEvent(content=f"工具执行失败: {e}")
            yield False
    
    def _prepare_tool_args(self, intent: Any, input_schema: Any) -> Dict[str, Any]:
        """
        准备工具参数，对齐用户意图与工具参数要求
        
        Args:
            intent: 用户意图
            input_schema: 工具输入模式
            
        Returns:
            Dict[str, Any]: 准备好的工具参数
        """
        tool_args = {}
        
        # 从意图参数中提取
        for param_name in input_schema.model_fields:
            if param_name in intent.parameters:
                tool_args[param_name] = intent.parameters[param_name]
        
        # 特殊处理某些工具的参数映射
        if intent.tool_name == "search_academic_papers":
            if "query" not in tool_args and "query" in intent.parameters:
                tool_args["query"] = intent.parameters["query"]
            elif "query" not in tool_args:
                # 从原始描述中提取查询
                tool_args["query"] = intent.parameters.get("query", "")
                
        elif intent.tool_name == "download_paper":
            if "paper_id" not in tool_args and "paper_id" in intent.parameters:
                tool_args["paper_id"] = intent.parameters["paper_id"]
                
        elif intent.tool_name == "debate":
            if "topic" not in tool_args and "topic" in intent.parameters:
                tool_args["topic"] = intent.parameters["topic"]
                
        elif intent.tool_name == "wiki":
            if "title" not in tool_args and "title" in intent.parameters:
                tool_args["title"] = intent.parameters["title"]
                
        return tool_args