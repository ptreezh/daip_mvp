#!/usr/bin/env python3
"""
测试意图识别和工具调用逻辑
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from daip_live.agent_engine.chat_executor import ChatExecutor
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.core.models import TodoItem
from daip_live.memory.session_manager import SessionManager
from daip_live.memory.service import MemoryService
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.p4_role_manager_tools.tools import tool


# 创建测试工具
@tool
def search_academic_papers(query: str, max_results: int = 10) -> str:
    """搜索学术论文的测试工具"""
    return f"搜索 '{query}' 的论文，找到 {max_results} 个结果"


@tool  
def download_paper(paper_id: str) -> str:
    """下载论文的测试工具"""
    return f"正在下载论文 {paper_id}"


async def test_intent_recognition_and_tool_call():
    """测试意图识别和工具调用流程"""
    
    # 创建模拟对象
    mock_session_manager = Mock()
    mock_memory_service = Mock()
    mock_user_input_queue = asyncio.Queue()
    
    # 创建工具管理器并注册测试工具
    tool_manager = ToolManager()
    tool_manager.register_tool(search_academic_papers)
    tool_manager.register_tool(download_paper)
    
    # 创建聊天执行器
    chat_executor = ChatExecutor(
        session_manager=mock_session_manager,
        memory_service=mock_memory_service,
        user_input_queue=mock_user_input_queue
    )
    
    # 创建模拟的步骤执行器
    mock_step_executor = Mock()
    mock_step_executor.tool_manager = tool_manager
    mock_step_executor.session_context = Mock()
    
    # 模拟execute_step方法
    async def mock_execute_step(task, session):
        """模拟execute_step方法"""
        from daip_live.core.models import ThoughtEvent, FinalResponseEvent
        yield ThoughtEvent(content=f"执行任务: {task.description}")
        yield FinalResponseEvent(content=f"任务完成: {task.description}")
    
    mock_step_executor.execute_step = mock_execute_step
    
    # 创建模拟会话
    mock_session = Mock()
    mock_session.history = []
    
    print("=== 测试意图识别和工具调用 ===\n")
    
    # 测试用例1: 论文搜索意图
    print("1. 测试论文搜索意图")
    test_input_1 = "搜索关于机器学习的论文"
    
    events = []
    async for event in chat_executor._process_chat_turn(test_input_1, mock_step_executor, mock_session):
        events.append(event)
        print(f"  事件: {type(event).__name__} - {getattr(event, 'content', str(event))}")
    
    print()
    
    # 测试用例2: 论文下载意图
    print("2. 测试论文下载意图") 
    test_input_2 = "下载论文 2301.00001"
    
    events = []
    async for event in chat_executor._process_chat_turn(test_input_2, mock_step_executor, mock_session):
        events.append(event)
        print(f"  事件: {type(event).__name__} - {getattr(event, 'content', str(event))}")
    
    print()
    
    # 测试用例3: 普通聊天（无意图识别）
    print("3. 测试普通聊天")
    test_input_3 = "今天天气怎么样？"
    
    events = []
    async for event in chat_executor._process_chat_turn(test_input_3, mock_step_executor, mock_session):
        events.append(event)
        print(f"  事件: {type(event).__name__} - {getattr(event, 'content', str(event))}")


if __name__ == "__main__":
    asyncio.run(test_intent_recognition_and_tool_call())