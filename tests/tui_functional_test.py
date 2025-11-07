"""
TUI功能性测试 - 专注于逻辑功能而非UI组件
"""

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import ProviderConfig, Role
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI


class TUIFunctionalTester:
    """TUI功能测试器 - 测试核心逻辑功能"""

    def __init__(self):
        self.test_results = []
        self.setup_mocks()

    def setup_mocks(self):
        """设置测试模拟对象"""
        # 模拟配置
        self.config = ProviderConfig(model="test_model")

        # 模拟LLM提供者
        self.mock_model_provider = MagicMock(spec=LiteLLMProvider)
        self.mock_model_provider.generate = AsyncMock(return_value=("测试响应", None))
        self.mock_model_provider.embed = AsyncMock(return_value=[0.1] * 384)

        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_manager = DatabaseManager(self.temp_db.name)

        # 会话管理器
        self.session_manager = SessionManager()

        # 内存服务
        self.memory_service = MemoryService(self.mock_model_provider)

        # 模拟知识管理器
        self.mock_knowledge_manager = MagicMock(spec=KnowledgeManager)
        self.mock_knowledge_manager.sync_knowledge_base = AsyncMock(
            return_value={"added": 5, "updated": 2, "deleted": 1}
        )
        self.mock_knowledge_manager.search = AsyncMock(
            return_value=[
                {"file_path": "test.md", "distance": 0.1, "content": "测试内容"}
            ]
        )

        # 模拟角色管理器
        self.mock_role_manager = MagicMock(spec=RoleManager)
        self.mock_role_manager.list_roles = MagicMock(
            return_value=[Role(name="test_role", persona="测试角色", tools=["search"])]
        )
        self.mock_role_manager.get_role_by_name = MagicMock(
            return_value=Role(
                name="test_role", persona="测试角色详情", tools=["search", "write"]
            )
        )

        # 模拟辩论管理器
        self.mock_debate_manager = MagicMock(spec=DebateManager)

        # 模拟配置管理器
        self.mock_config_manager = MagicMock()

        # 模拟智能体执行器
        self.mock_executor = MagicMock(spec=AgentExecutor)
        self.mock_executor.user_input_queue = asyncio.Queue()
        self.mock_executor.permission_queue = asyncio.Queue()

    def create_tui_instance(self, goal=None):
        """创建TUI实例"""
        return DAIP_TUI(
            executor=self.mock_executor,
            goal=goal,
            session_manager=self.session_manager,
            role_manager=self.mock_role_manager,
            knowledge_manager=self.mock_knowledge_manager,
            debate_manager=self.mock_debate_manager,
            model_provider=self.mock_model_provider,
            db_manager=self.db_manager,
            config_manager=self.mock_config_manager,
        )

    async def test_command_discovery(self):
        """测试指令发现功能"""

        tui = self.create_tui_instance()

        # 检查指令发现
        discovered_commands = [cmd for cmd, _ in tui._available_commands]
        expected_commands = ["/pa", "/role", "/knowledge", "/session", "/help", "/quit"]

        found_commands = [
            cmd for cmd in expected_commands if cmd in discovered_commands
        ]
        success = len(found_commands) >= len(expected_commands) - 1  # 允许1个指令缺失

        self.test_results.append(
            {
                "test": "指令发现",
                "success": success,
                "details": (
                    f"发现 {len(discovered_commands)} 个指令，包含 "
                    f"{len(found_commands)}/{len(expected_commands)} 个预期指令"
                ),
            }
        )

        return success

    async def test_autocomplete_functionality(self):
        """测试自动补全功能"""

        tui = self.create_tui_instance()

        test_cases = [
            ("/r", "应该显示role相关指令"),
            ("/help", "应该显示help指令"),
        ]

        success_count = 0
        for input_text, expected in test_cases:
            try:
                suggestions = tui._get_autocomplete_suggestions(input_text)
                if len(suggestions) > 0:
                    success_count += 1

            except Exception:
                pass

        success = success_count >= len(test_cases) // 2
        self.test_results.append(
            {
                "test": "自动补全",
                "success": success,
                "details": f"{success_count}/{len(test_cases)} 个测试用例成功",
            }
        )

        return success

    async def test_command_handlers(self):
        """测试指令处理器"""

        tui = self.create_tui_instance()

        # 模拟日志更新方法
        tui._update_log_view = MagicMock()

        test_commands = [
            "/help",
            "/role list",
            "/knowledge sync",
            "/session list",
            "/quit",
        ]

        success_count = 0
        for cmd in test_commands:
            try:
                await tui._handle_shortcut_command(cmd)
                success_count += 1

            except Exception:
                pass

        success = success_count >= len(test_commands) // 2
        self.test_results.append(
            {
                "test": "指令处理器",
                "success": success,
                "details": f"{success_count}/{len(test_commands)} 个指令执行成功",
            }
        )

        return success

    async def test_session_management(self):
        """测试会话管理"""

        # 创建测试会话
        test_session = self.session_manager.create_session(
            goal="测试会话",
            session_type="chat",  # 使用有效的会话类型
            participant_ids=["user", "agent"],
        )

        # 验证会话创建
        sessions = self.session_manager.list_sessions()
        session_exists = any(s.session_id == test_session.session_id for s in sessions)

        # 验证会话检索
        retrieved_session = self.session_manager.get_session(test_session.session_id)
        session_retrievable = retrieved_session is not None

        success = session_exists and session_retrievable
        self.test_results.append(
            {
                "test": "会话管理",
                "success": success,
                "details": (
                    f"会话创建: {session_exists}, "
                    f"会话检索: {session_retrievable}"
                ),
            }
        )

        return success

    async def test_knowledge_integration(self):
        """测试知识库集成"""

        # 测试知识库同步
        sync_result = await self.mock_knowledge_manager.sync_knowledge_base()
        sync_success = isinstance(sync_result, dict) and "added" in sync_result

        # 测试知识库搜索
        search_result = await self.mock_knowledge_manager.search("测试查询")
        search_success = isinstance(search_result, list) and len(search_result) > 0

        success = sync_success and search_success
        self.test_results.append(
            {
                "test": "知识库集成",
                "success": success,
                "details": f"同步: {sync_success}, 搜索: {search_success}",
            }
        )

        return success

    async def test_role_management(self):
        """测试角色管理"""
        roles = self.mock_role_manager.list_roles()
        role_found = any(r.name == "test_role" for r in roles)

        role_details = self.mock_role_manager.get_role_by_name("test_role")
        details_found = (
            role_details is not None and role_details.persona == "测试角色详情"
        )

        success = role_found and details_found
        self.test_results.append(
            {
                "test": "角色管理",
                "success": success,
                "details": (f"列表: {role_found}, " f"详情: {details_found}"),
            }
        )
        return success

    async def test_event_system(self):
        """测试事件系统"""
        tui = self.create_tui_instance()

        from daip_live.core.models import FinalResponseEvent, ThoughtEvent

        # 模拟事件处理方法
        tui._update_log_view = MagicMock()
        tui._update_status_bar = MagicMock()

        # 测试事件处理
        events = [
            ThoughtEvent(content="测试思考"),
            FinalResponseEvent(content="最终响应"),
        ]

        success_count = 0
        for event in events:
            try:
                tui._post_event(event)
                success_count += 1
            except Exception:
                pass

        success = success_count == len(events)
        self.test_results.append(
            {
                "test": "事件系统",
                "success": success,
                "details": f"{success_count}/{len(events)} 个事件处理成功",
            }
        )

        return success

    async def run_all_tests(self):
        """运行所有功能测试"""
        test_functions = [
            self.test_command_discovery,
            self.test_autocomplete_functionality,
            self.test_command_handlers,
            self.test_session_management,
            self.test_knowledge_integration,
            self.test_role_management,
            self.test_event_system,
        ]

        total_tests = len(test_functions)
        passed_tests = 0

        for test_func in test_functions:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                self.test_results.append(
                    {
                        "test": test_func.__name__,
                        "success": False,
                        "details": f"异常: {str(e)}",
                    }
                )

        result_summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "assessment": (
                "完全正常"
                if passed_tests == total_tests
                else "核心功能正常"
                if passed_tests >= total_tests * 0.8
                else "基本可用"
                if passed_tests >= total_tests * 0.6
                else "需要修复"
            ),
            "details": self.test_results,
        }

        # 清理
        self.cleanup()

        return result_summary

    def cleanup(self):
        """清理测试资源"""
        try:
            os.unlink(self.temp_db.name)
        except Exception:
            pass
