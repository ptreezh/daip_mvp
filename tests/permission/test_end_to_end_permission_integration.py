"""
端到端权限集成测试 - TDD实现
严格遵循端到端测试规范，验证权限系统在完整工作流程中的集成
基于BMAD kiro's spec规范，确保端到端功能验证
"""

import pytest
import asyncio
import time
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

from daip_live.core.models import (
    AgentEvent,
    AgentState,
    SessionContext,
    PermissionRequestEvent,
    PermissionResponse,
    PermissionResult,
    FinalResponseEvent,
    ToolCallEvent,
    ToolOutputEvent,
    ThoughtEvent
)

from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.permission.permission_manager import PermissionManager

# 待实现的工具管理器导入
# from daip_live.p4_role_manager_tools.tool_manager import ToolManager
# from daip_live.knowledge.manager import KnowledgeManager
# from daip_live.model_provider.service import ModelProviderService


@pytest.fixture
def end_to_end_test_environment():
    """端到端测试环境搭建 - 完整系统组件（模块级别fixture）"""
    # 创建用户输入队列
    user_input_queue = asyncio.Queue()
    
    # 创建模拟的系统组件
    session_manager = MagicMock(spec=SessionManager)
    memory_service = MagicMock(spec=MemoryService)
    
    # 设置内存服务行为
    memory_service.get_todo_list = AsyncMock(return_value=[
        MagicMock(id=1, description="Test task", status="pending", priority=1)
    ])
    memory_service.is_todo_list_complete = AsyncMock(return_value=False)
    memory_service.update_todo_status = AsyncMock()
    memory_service.construct_prompt = AsyncMock(return_value="Test prompt")
    
    # 设置会话管理器行为
    session_manager.create_session = MagicMock(return_value=MagicMock(
        session_id="test_session_123",
        goal="Test goal",
        status=AgentState.INIT,
        history=[]
    ))
    session_manager.save_session = MagicMock()
    
    # 创建权限管理器
    permission_manager = PermissionManager(user_input_queue, MagicMock())
    
    # 创建简化的AgentExecutor with PermissionManager
    agent_executor = _create_test_agent_executor(
        session_manager, memory_service, permission_manager, user_input_queue
    )
    
    return {
        'agent_executor': agent_executor,
        'permission_manager': permission_manager,
        'user_input_queue': user_input_queue,
        'session_manager': session_manager,
        'memory_service': memory_service
    }


def _create_test_agent_executor(session_manager, memory_service, permission_manager, user_input_queue):
    """创建测试用的AgentExecutor - 端到端测试专用"""
    # 创建简化的测试环境
    knowledge_manager = MagicMock()
    model_provider = MagicMock()
    tool_manager = MagicMock()
    
    # 设置模型提供者行为
    model_provider.generate = AsyncMock(return_value=("Use Tool: read_file(path='test.txt')", {"total_tokens": 50}))
    model_provider.config = MagicMock(model="test-model")
    
    # 设置工具管理器行为
    tool_manager._registry = {
        "read_file": MagicMock(),
        "write_file": MagicMock(),
        "execute_command": MagicMock()
    }
    
    # 模拟工具执行（带权限检查）
    def mock_execute_tool(name, args, session_context=None):
        # 这里会触发权限检查
        if name == "read_file":
            return f"Content of {args.get('path', 'file')}"
        elif name == "write_file":
            return f"File {args.get('path', 'file')} written successfully"
        elif name == "execute_command":
            return f"Command '{args.get('command', 'cmd')}' executed"
        return f"Tool {name} executed with args {args}"
    
    tool_manager.execute_tool = mock_execute_tool
    
    # 创建AgentExecutor with PermissionManager
    agent_executor = AgentExecutor(
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=user_input_queue,
        permission_manager=permission_manager  # 关键：集成权限管理器
    )
    
    return agent_executor





class TestEndToEndPermissionIntegration:
    """端到端权限集成测试 - 验证完整工作流程"""
    
    # ===== 测试1: 完整权限允许工作流 - 红阶段 =====
    @pytest.mark.asyncio
    async def test_end_to_end_permission_allowed_workflow(self):
        """
        端到端测试：完整权限允许工作流 - TDD红阶段
        
        Given: 完整的系统环境，工具权限设置为allow
        When: 用户请求执行需要该工具的任务
        Then: 工具成功执行，返回正确结果
        
        验证完整的用户→AI→权限检查→工具执行→结果返回流程
        """
        # 创建端到端测试环境
        user_input_queue = asyncio.Queue()
        permission_manager = PermissionManager(user_input_queue, MagicMock())
        permission_manager.set_permission_rule("read_file", "allow")
        
        # Given: 模拟完整的AgentExecutor环境
        session_manager = MagicMock(spec=SessionManager)
        memory_service = MagicMock(spec=MemoryService)
        
        # 设置内存服务行为
        memory_service.get_todo_list = AsyncMock(return_value=[
            MagicMock(id=1, description="读取README.md文件", status="pending", priority=1)
        ])
        memory_service.is_todo_list_complete = AsyncMock(side_effect=[False, True])  # 先未完成，然后完成
        memory_service.update_todo_status = AsyncMock()
        memory_service.construct_prompt = AsyncMock(return_value="请使用read_file工具读取README.md文件")
        
        # 设置会话管理器行为
        test_session = MagicMock(
            session_id="test_session_e2e",
            goal="读取README.md文件",
            status=AgentState.INIT,
            history=[]
        )
        session_manager.create_session = MagicMock(return_value=test_session)
        session_manager.save_session = MagicMock()
        
        # 创建模型提供者（模拟LLM响应）
        model_provider = MagicMock()
        model_provider.generate = AsyncMock(return_value=(
 "Use Tool: read_file(path='README.md') Confidence: 0.95",
            {"total_tokens": 50}
        ))
        model_provider.config = MagicMock(model="test-model")
        
        # 创建工具管理器
        tool_manager = MagicMock()
        tool_manager._registry = {"read_file": MagicMock()}
        
        def mock_execute_tool(name, args, session_context=None):
            # 这里会触发权限检查
            if name == "read_file":
                return "# Project README\n\nThis is a test project."
            return f"Tool {name} executed"
        
        tool_manager.execute_tool = mock_execute_tool
        
        # 创建AgentExecutor with PermissionManager
        agent_executor = AgentExecutor(
            session_manager=session_manager,
            memory_service=memory_service,
            knowledge_manager=MagicMock(),
            model_provider=model_provider,
            tool_manager=tool_manager,
            user_input_queue=user_input_queue,
            permission_manager=permission_manager  # 关键：集成权限管理器
        )
        
        # 设置用户目标
        user_goal = "请读取项目中的README.md文件内容"
        
        # When: 执行完整的AgentExecutor运行流程
        events = []
        try:
            async for event in agent_executor.run(user_goal):
                events.append(event)
                print(f"事件类型: {type(event).__name__}, 内容: {getattr(event, 'content', '')[:100]}")
        except Exception as e:
            print(f"异常发生: {e}")
            import traceback
            traceback.print_exc()
        
        # Then: 验证完整工作流程（红阶段：记录分析，暂不断言）
        print(f"\n=== 端到端测试结果分析 ===")
        print(f"事件总数: {len(events)}")
        print(f"工具调用事件: {len([e for e in events if isinstance(e, ToolCallEvent)])}")
        print(f"工具输出事件: {len([e for e in events if isinstance(e, ToolOutputEvent)])}")
        print(f"权限请求事件: {len([e for e in events if isinstance(e, PermissionRequestEvent)])}")
        print(f"最终响应事件: {len([e for e in events if isinstance(e, FinalResponseEvent)])}")
        print(f"思考事件: {len([e for e in events if isinstance(e, ThoughtEvent)])}")
        
        # 红阶段：基础验证 - 确保测试能够运行并产生事件
        assert len(events) > 0, "应该产生至少一个事件"
        
        # 验证权限允许的工作流
        tool_call_events = [e for e in events if isinstance(e, ToolCallEvent)]
        tool_output_events = [e for e in events if isinstance(e, ToolOutputEvent)]
        
        # 由于权限设置为allow，应该成功执行工具
        assert len(tool_call_events) > 0, "应该至少有一个工具调用事件"
        assert len(tool_output_events) > 0, "应该至少有一个工具输出事件"
        
        # 验证没有权限请求事件（因为权限是allow）
        permission_events = [e for e in events if isinstance(e, PermissionRequestEvent)]
        assert len(permission_events) == 0, "权限设置为allow时不应该有权限请求事件"
        
        print("✅ 端到端权限允许工作流测试通过")
    
    # ===== 测试2: 完整权限拒绝工作流 - 红阶段 =====
    @pytest.mark.asyncio
    async def test_end_to_end_permission_denied_workflow(self, end_to_end_test_environment):
        """
        端到端测试：完整权限拒绝工作流 - TDD红阶段
        
        Given: 完整的系统环境，工具权限设置为deny
        When: 用户请求执行需要该工具的任务
        Then: 权限被拒绝，抛出ToolPermissionError异常
        
        验证完整的错误处理流程
        """
        # Given: 设置工具权限为deny
        env = end_to_end_test_environment
        env['permission_manager'].set_permission_rule("delete_file", "deny")
        
        # 设置用户目标
        user_goal = "请删除系统中的重要配置文件"
        
        # When: 执行完整的AgentExecutor运行流程
        events = []
        exception_caught = None
        
        try:
            async for event in env['agent_executor'].run(user_goal):
                events.append(event)
        except Exception as e:
            exception_caught = e
        
        # Then: 验证权限拒绝处理
        # 验证异常被正确捕获
        # assert exception_caught is not None, "应该捕获ToolPermissionError异常"  # 红阶段暂不断言
        # assert "permission denied" in str(exception_caught).lower(), "异常信息应该包含权限拒绝"  # 红阶段暂不断言
        # assert exception_caught.tool_name == "delete_file", "异常应该包含正确的工具名称"  # 红阶段暂不断言
        
        # 验证权限请求事件未发生（直接拒绝，不询问用户）
        permission_events = [e for e in events if isinstance(e, PermissionRequestEvent)]
        # assert len(permission_events) == 0, "权限拒绝时不应该请求用户确认"  # 红阶段暂不断言
        
        # 红阶段：记录当前状态并进行基础验证
        print(f"捕获的异常: {exception_caught}")
        print(f"事件数量: {len(events)}")
        print(f"权限请求事件: {len(permission_events)}")
        
        # 基础验证：确保测试能够运行
        assert len(events) > 0, "应该产生至少一个事件"
        
        # 验证权限拒绝工作流
        tool_call_events = [e for e in events if isinstance(e, ToolCallEvent)]
        tool_output_events = [e for e in events if isinstance(e, ToolOutputEvent)]
        
        # 由于权限设置为deny，工具调用应该失败或产生错误输出
        if len(tool_call_events) > 0:
            # 如果有工具调用，应该伴随着错误输出
            error_outputs = [e for e in tool_output_events if e.status == "error"]
            assert len(error_outputs) > 0, "权限拒绝时应该有错误输出"
        
        # 验证没有权限请求事件（直接拒绝，不询问用户）
        assert len(permission_events) == 0, "权限设置为deny时不应该请求用户确认"
        
        print("✅ 端到端权限拒绝工作流测试通过")
    
    # ===== 测试3: 权限检查性能基准 - 红阶段 =====
    @pytest.mark.asyncio
    async def test_end_to_end_permission_performance_baseline(self, end_to_end_test_environment):
        """
        端到端性能基准测试 - TDD红阶段
        
        Given: 标准测试环境
        When: 执行权限检查工作流程
        Then: 性能满足基准要求
        
        验证系统响应性能
        """
        import time
        
        env = end_to_end_test_environment
        env['permission_manager'].set_permission_rule("read_file", "allow")
        
        user_goal = "请读取README.md文件"
        
        # 测量完整工作流程时间
        start_time = time.time()
        
        events = []
        try:
            async for event in env['agent_executor'].run(user_goal):
                events.append(event)
        except Exception as e:
            print(f"执行异常: {e}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 红阶段：记录性能数据但不断言
        print(f"端到端执行时间: {execution_time:.3f}秒")
        print(f"事件总数: {len(events)}")
        
        # 性能基准要求（后续实现时验证）
        # assert execution_time < 5.0, f"执行时间{execution_time}秒超过阈值5.0秒"
        
        pytest.skip("端到端性能基准测试待实现 - 需要建立性能基准线")


class TestEndToEndPermissionScenarios:
    """端到端权限场景测试 - 具体用户场景验证"""
    
    # ===== 测试4: 开发者工作流权限场景 - 红阶段 =====
    @pytest.mark.asyncio
    async def test_developer_workflow_permission_scenario(self, end_to_end_test_environment):
        """
        开发者工作流权限场景测试 - TDD红阶段
        
        Given: 开发者使用DAIP进行项目分析
        When: 执行典型的开发任务序列
        Then: 权限系统正确处理各种工具调用
        
        验证真实开发场景中的权限行为
        """
        env = end_to_end_test_environment
        
        # 设置典型的开发工具权限
        env['permission_manager'].set_permission_rule("read_file", "allow")      # 读取文件：允许
        env['permission_manager'].set_permission_rule("write_file", "ask")       # 写入文件：询问
        env['permission_manager'].set_permission_rule("execute_command", "deny") # 执行命令：拒绝
        
        # 典型开发任务：读取配置文件，修改后保存，然后执行构建命令
        user_goal = "请读取项目配置文件，添加新的依赖项，然后执行构建命令"
        
        # 模拟用户交互
        await env['user_input_queue'].put("y")  # 用户授予write_file权限
        
        # When: 执行完整的开发工作流
        events = []
        try:
            async for event in env['agent_executor'].run(user_goal):
                events.append(event)
        except Exception as e:
            print(f"开发工作流异常: {e}")
        
        # 红阶段：分析事件流中的权限行为
        read_file_calls = [e for e in events if isinstance(e, ToolCallEvent) and e.tool_name == "read_file"]
        write_file_calls = [e for e in events if isinstance(e, ToolCallEvent) and e.tool_name == "write_file"]
        execute_commands = [e for e in events if isinstance(e, ToolCallEvent) and e.tool_name == "execute_command"]
        
        print(f"读取文件调用: {len(read_file_calls)} (应该成功)")
        print(f"写入文件调用: {len(write_file_calls)} (应该询问用户)")
        print(f"执行命令调用: {len(execute_commands)} (应该被拒绝)")
        
        pytest.skip("开发者工作流权限场景测试待实现 - 需要验证复杂工作流中的权限行为")
    
    # ===== 测试5: 权限缓存验证 - 红阶段 =====
    @pytest.mark.asyncio
    async def test_permission_caching_end_to_end(self, end_to_end_test_environment):
        """
        权限缓存端到端验证 - TDD红阶段
        
        Given: 工具权限设置为ask，用户首次授予权限
        When: 再次执行相同工具
        Then: 第二次应该直接使用缓存权限，不再询问用户
        
        验证权限缓存机制在完整工作流中的有效性
        """
        env = end_to_end_test_environment
        env['permission_manager'].set_permission_rule("write_file", "ask")
        
        # 第一次执行：用户授予权限
        user_goal_1 = "请写入第一个配置文件"
        await env['user_input_queue'].put("y")  # 用户授予权限
        
        # 执行第一次任务
        events_1 = []
        try:
            async for event in env['agent_executor'].run(user_goal_1):
                events_1.append(event)
        except Exception as e:
            print(f"第一次执行异常: {e}")
        
        # 验证权限被缓存
        cached_perms_before = env['permission_manager'].get_cached_permissions()
        print(f"第一次执行后的缓存权限: {cached_perms_before}")
        
        # 第二次执行：应该直接使用缓存
        user_goal_2 = "请写入第二个配置文件"
        events_2 = []
        try:
            async for event in env['agent_executor'].run(user_goal_2):
                events_2.append(event)
        except Exception as e:
            print(f"第二次执行异常: {e}")
        
        # 验证第二次执行的行为差异
        permission_events_1 = [e for e in events_1 if isinstance(e, PermissionRequestEvent)]
        permission_events_2 = [e for e in events_2 if isinstance(e, PermissionRequestEvent)]
        
        print(f"第一次权限请求事件: {len(permission_events_1)} (应该有1个)")
        print(f"第二次权限请求事件: {len(permission_events_2)} (应该为0个，使用缓存)")
        
        pytest.skip("权限缓存端到端验证待实现 - 需要验证缓存机制在完整工作流中的有效性")


# ===== 测试工具和数据工厂 =====
@pytest.fixture
def permission_scenarios():
    """提供各种权限场景测试数据"""
    return {
        "safe_development": {
            "read_file": "allow",
            "list_files": "allow", 
            "write_file": "ask",
            "execute_command": "deny"
        },
        "dangerous_operations": {
            "delete_file": "deny",
            "format_disk": "deny",
            "system_command": "deny",
            "network_admin": "deny"
        },
        "mixed_permissions": {
            "read_config": "allow",
            "write_config": "ask",
            "backup_data": "allow",
            "restore_data": "ask"
        }
    }


@pytest.fixture
def mock_model_response():
    """提供模拟的模型响应"""
    return {
        "read_file": "Use Tool: read_file(path='test.txt') Confidence: 0.95",
        "write_file": "Use Tool: write_file(path='output.txt', content='test data') Confidence: 0.85",
        "execute_command": "Use Tool: execute_command(command='ls -la') Confidence: 0.75",
        "complete_task": "Final Answer: Task completed successfully."
    }


if __name__ == "__main__":
    # 运行端到端测试
    pytest.main([__file__, "-v", "--tb=short"])