"""
增强的聊天执行器 - 支持PA助理记忆优化和置信度循环

专门负责聊天模式的执行，支持智能意图识别和工作流路由
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, Optional

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
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer, WorkflowType

logger = logging.getLogger(__name__)


class EnhancedChatExecutor:
    """
    增强的聊天执行器 - 支持PA助理记忆优化和置信度循环
    """
    
    def __init__(
        self,
        session_manager: BaseSessionManager,
        memory_service: MemoryService,
        user_input_queue: asyncio.Queue,
    ):
        """
        初始化增强聊天执行器
        
        Args:
            session_manager: 会话管理器
            memory_service: 内存服务
            user_input_queue: 用户输入队列
        """
        self.session_manager = session_manager
        self.memory_service = memory_service
        self.user_input_queue = user_input_queue
        self.intent_recognizer = EnhancedIntentRecognizer()
        self.confidence_threshold = 0.95  # 置信度阈值
        self.max_reflection_rounds = 3  # 最大反思轮数
        logger.info("EnhancedChatExecutor initialized")
    
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
        
        if intent:
            # 显示意图识别结果
            yield ThoughtEvent(content=f"识别到意图: {intent.description} (置信度: {intent.confidence:.2f})")
            
            # 根据工作流类型处理
            if intent.workflow_type == WorkflowType.QUESTION:
                # 问题需要置信度循环
                async for event in self._handle_question_with_confidence_loop(intent, step_executor, session):
                    yield event
                    
            elif intent.workflow_type == WorkflowType.CHAT:
                # 普通闲聊直接回答
                yield ThoughtEvent(content="普通闲聊模式，直接响应")
                current_task = TodoItem(id=0, description=turn_description, status="pending", priority=1)
                async for event in step_executor.execute_step(current_task, session):
                    yield event
                    
            elif intent.workflow_type in [
                WorkflowType.DEBATE, 
                WorkflowType.PAPER_SEARCH, 
                WorkflowType.PAPER_DOWNLOAD, 
                WorkflowType.WIKI_CREATE, 
                WorkflowType.CONTEXT_COMPRESS, 
                WorkflowType.PROJECT_SCAFFOLD
            ]:
                # 工作流类型，转换为相应命令
                modified_task = self._convert_intent_to_command(intent, turn_description)
                yield ThoughtEvent(content=f"转换为工作流命令: {modified_task}")
                current_task = TodoItem(id=0, description=modified_task, status="pending", priority=1)
                async for event in step_executor.execute_step(current_task, session):
                    yield event
        else:
            # 未识别到意图，按普通聊天处理
            yield ThoughtEvent(content="未识别到特定意图，按普通聊天处理")
            current_task = TodoItem(id=0, description=turn_description, status="pending", priority=1)
            async for event in step_executor.execute_step(current_task, session):
                yield event
    
    async def _handle_question_with_confidence_loop(
        self, 
        intent: Any, 
        step_executor: Any, 
        session: Any
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        处理需要置信度循环的问题
        
        Args:
            intent: 识别到的意图
            step_executor: 步骤执行器
            session: 会话
            
        Yields:
            AgentEvent: 处理事件
        """
        question = intent.parameters["question"]
        current_confidence = intent.confidence
        
        yield ThoughtEvent(content=f"问题识别，当前置信度: {current_confidence:.2f}，开始置信度循环...")
        
        for round_num in range(self.max_reflection_rounds):
            if current_confidence >= self.confidence_threshold:
                yield ThoughtEvent(content=f"置信度达到阈值 ({current_confidence:.2f} >= {self.confidence_threshold})，生成最终回答")
                
                # 构建高置信度提示词
                prompt = self._construct_confidence_prompt(question, session, round_num)
                
                # 执行推理
                response, confidence = await self._execute_reasoning_with_confidence(prompt)
                
                yield FinalResponseEvent(content=response)
                return
            else:
                yield ThoughtEvent(content=f"第{round_num + 1}轮反思，当前置信度: {current_confidence:.2f} < {self.confidence_threshold}")
                
                # 构建反思提示词
                prompt = self._construct_reflection_prompt(question, session, round_num)
                
                # 执行反思
                response, confidence = await self._execute_reasoning_with_confidence(prompt)
                
                yield ThoughtEvent(content=f"反思完成，新置信度: {confidence:.2f}")
                current_confidence = confidence
    
        # 如果达到最大轮数仍未达到阈值，使用当前最佳答案
        yield ThoughtEvent(content=f"达到最大反思轮数，使用当前最佳答案")
        prompt = self._construct_confidence_prompt(question, session, self.max_reflection_rounds)
        response, _ = await self._execute_reasoning_with_confidence(prompt)
        yield FinalResponseEvent(content=response)
    
    def _construct_confidence_prompt(self, question: str, session: Any, round_num: int) -> str:
        """构建置信度循环的提示词"""
        # 获取历史对话
        history_text = "\n".join(
            f"{turn.participant_id}: {turn.content}" 
            for turn in session.history[-5:]  # 最近5轮对话
        )
        
        # 获取长期记忆
        long_term_memory = self.memory_service.get_long_term_memory()
        
        prompt = f"""你是一个专业的AI助手，请基于以下信息回答问题：

问题：{question}

对话历史（最近5轮）：
{history_text}

长期记忆：
{long_term_memory}

请提供准确、详细的回答。回答要求：
1. 准确性优先于简洁性
2. 如果不确定，请明确说明
3. 提供相关的背景信息
4. 使用清晰的结构和格式

请以"Final Answer:"开头开始你的回答。

第{round_num + 1}次思考（置信度循环）：
"""
        
        return prompt
    
    def _construct_reflection_prompt(self, question: str, session: Any, round_num: int) -> str:
        """构建反思提示词"""
        # 获取之前的回答
        previous_responses = []
        for event in session.history[-3:]:
            if event.participant_id == "agent":
                previous_responses.append(event.content)
        
        previous_text = "\n".join([f"回答{i+1}: {resp}" for i, resp in enumerate(previous_responses)])
        
        return f"""请对之前的回答进行反思和改进：

原始问题：{question}

之前的回答：
{previous_text}

请分析：
1. 之前的回答是否准确完整？
2. 是否有遗漏的重要信息？
3. 表达是否清晰易懂？
4. 逻辑是否严谨？

请提供改进后的回答，格式要求：
- 以"Final Answer:"开头
- 更加准确和完整
- 保持专业的表达方式

第{round_num + 1}次反思：
"""
    
    async def _execute_reasoning_with_confidence(self, prompt: str) -> tuple[str, float]:
        """执行推理并返回置信度评估"""
        try:
            response = await self.memory_service.model_provider.generate(prompt)
            
            # 简单的置信度评估（基于回答的完整性和结构）
            confidence = self._calculate_confidence(response)
            
            return response, confidence
            
        except Exception as e:
            logger.error(f"推理执行错误: {e}")
            return f"抱歉，处理您的问题时出现错误：{e}", 0.5
    
    def _calculate_confidence(self, response: str) -> float:
        """计算回答的置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于回答长度
        if len(response) > 100:
            confidence += 0.2
        
        # 基于结构完整性
        if "Final Answer:" in response:
            confidence += 0.2
        
        # 基于包含关键信息指标
        if any(keyword in response for keyword in ["因为", "所以", "首先", "其次", "最后"]):
            confidence += 0.1
        
        # 基于专业性和准确性指标
        if any(keyword in response for keyword in ["根据", "基于", "分析", "研究表明", "数据显示"]):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _convert_intent_to_command(self, intent: Any, original_text: str) -> str:
        """将意图转换为相应的命令"""
        if intent.workflow_type == WorkflowType.DEBATE:
            topic = intent.parameters.get("topic", original_text)
            return f"/debate start {topic}"
        elif intent.workflow_type == WorkflowType.PAPER_SEARCH:
            query = intent.parameters.get("query", original_text)
            return f"/doc search {query}"
        elif intent.workflow_type == WorkflowType.PAPER_DOWNLOAD:
            paper_id = intent.parameters.get("paper_id")
            return f"/doc download {paper_id}"
        elif intent.workflow_type == WorkflowType.WIKI_CREATE:
            title = intent.parameters.get("title", original_text)
            return f"/wiki create {title}"
        elif intent.workflow_type == WorkflowType.CONTEXT_COMPRESS:
            return "/session clear"
        elif intent.workflow_type == WorkflowType.PROJECT_SCAFFOLD:
            description = intent.parameters.get("description", original_text)
            return f"/project scaffold {description}"
        else:
            return original_text
    
    def optimize_user_input(self, user_input: str) -> str:
        """PA助理功能：优化用户输入"""
        # 基本清理
        optimized = user_input.strip()
        
        # 修复常见的输入错误
        corrections = {
            "怎么": "如何",
            "怎么样": "如何",
            "为啥": "为什么",
            "啥是": "什么是",
            "咋办": "怎么办"
        }
        
        for old, new in corrections.items():
            optimized = optimized.replace(old, new)
        
        # 记录到长期记忆
        self._save_to_long_term_memory(f"用户输入优化: '{user_input}' -> '{optimized}'")
        
        return optimized
    
    def _save_to_long_term_memory(self, content: str) -> None:
        """保存到长期记忆"""
        try:
            current_memory = self.memory_service.get_long_term_memory()
            new_memory = f"{current_memory}\n{content}\n"
            
            # 写入文件
            with open(self.memory_service.long_term_memory_file, 'w', encoding='utf-8') as f:
                f.write(new_memory)
                
        except Exception as e:
            logger.error(f"保存长期记忆失败: {e}")
    
    def organize_knowledge(self, session: Any) -> None:
        """整理知识结构"""
        try:
            # 从对话历史中提取关键信息
            knowledge_points = []
            
            for turn in session.history:
                if turn.participant_id == "agent" and len(turn.content) > 50:
                    # 提取关键句子（简单实现）
                    sentences = turn.content.split('. ')
                    for sentence in sentences:
                        if any(keyword in sentence for keyword in ["因为", "所以", "重要", "关键", "注意"]):
                            knowledge_points.append(sentence.strip())
            
            # 整理并保存知识
            if knowledge_points:
                organized_knowledge = "\n".join([f"- {point}" for point in knowledge_points])
                
                # 添加到长期记忆
                self._save_to_long_term_memory(f"知识整理:\n{organized_knowledge}")
                
        except Exception as e:
            logger.error(f"知识整理失败: {e}")
