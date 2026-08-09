# ruff: noqa: E501
"""
真实模型端到端集成测试 - 使用本地Ollama模型进行完整功能测试
"""

import asyncio
import os
import tempfile
import time

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.config import ConfigManager
from daip_live.core.models import ProviderConfig
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI


class RealModelIntegrationTester:
    """真实模型集成测试器 - 使用本地Ollama模型"""

    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.setup_real_components()

    def setup_real_components(self):
        """设置真实的组件 - 不使用任何mock"""

        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp(prefix="daip_test_")
        self.temp_db_path = os.path.join(self.temp_dir, "test.db")
        self.temp_docs_dir = os.path.join(self.temp_dir, "docs")
        self.temp_roles_dir = os.path.join(self.temp_dir, "roles")

        os.makedirs(self.temp_docs_dir, exist_ok=True)
        os.makedirs(self.temp_roles_dir, exist_ok=True)

        # 创建测试文档
        self.create_test_documents()

        # 创建测试角色
        self.create_test_roles()

        # 配置真实的LLM提供者 - 使用本地Ollama模型
        self.llm_config = ProviderConfig(
            model="ollama/llama3:latest",  # 使用本地llama3模型
            api_key="",  # Ollama不需要API key
            base_url="http://localhost:11434",  # 本地Ollama服务
        )

        self.embedding_config = ProviderConfig(
            model="ollama/nomic-embed-text:latest",  # 使用本地嵌入模型
            api_key="",
            base_url="http://localhost:11434",
        )

    def create_test_documents(self):
        """创建测试文档"""
        docs = {
            "project_overview.md": """
# DAIP-LIVE 项目概述

DAIP-LIVE是一个动态AI驱动的项目执行系统，支持：
- 多智能体协作
- 知识库管理
- 项目脚手架生成
- 实时TUI交互

## 核心功能
- AI智能体编排
- 多智能体辩论
- 知识检索和管理
- 会话历史管理
""",
            "installation.md": """
# 安装指南

## 环境要求
- Python 3.9+
- Poetry 包管理器
- Ollama (可选，用于本地模型)

## 安装步骤
1. 克隆仓库
2. 安装依赖: `poetry install`
3. 配置模型
4. 启动应用: `poetry run daip`
""",
            "api_reference.md": """
# API 参考

## CLI 命令
- `daip run` - 启动TUI
- `daip pa` - 个人助手
- `daip debate` - 多智能体辩论
- `daip sync` - 同步知识库

## TUI 指令
- `/help` - 显示帮助
- `/role list` - 列出角色
- `/session list` - 列出会话
""",
        }

        for filename, content in docs.items():
            with open(
                os.path.join(self.temp_docs_dir, filename), "w", encoding="utf-8"
            ) as f:
                f.write(content)

    def create_test_roles(self):
        """创建测试角色"""
        roles = {
            "developer.yaml": """
name: developer
persona: 你是一个经验丰富的Python开发者，擅长系统架构设计和代码实现。你总是提供清晰、实用的技术建议。  # noqa: E501
tools:
  - search_knowledge
  - write_code
  - review_code
""",
            "analyst.yaml": """
name: analyst
persona: 你是一个数据分析师，擅长从复杂信息中提取关键洞察。你善于提出深入的问题并提供数据驱动的建议。  # noqa: E501
tools:
  - search_knowledge
  - analyze_data
""",
            "tester.yaml": """
name: tester
persona: 你是一个质量保证专家，专注于测试策略和质量控制。你总是从用户角度思考问题。
tools:
  - search_knowledge
  - run_tests
  - validate_quality
""",
        }

        for filename, content in roles.items():
            with open(
                os.path.join(self.temp_roles_dir, filename), "w", encoding="utf-8"
            ) as f:
                f.write(content)

    async def setup_real_managers(self):
        """设置真实的管理器组件"""

        # 数据库管理器
        self.db_manager = DatabaseManager(self.temp_db_path)

        # 模型提供者
        self.llm_provider = LiteLLMProvider(self.llm_config)
        self.embedding_provider = LiteLLMProvider(self.embedding_config)

        # 会话管理器
        self.session_manager = SessionManager()

        # 内存服务
        self.memory_service = MemoryService(self.llm_provider)

        # 知识管理器
        self.knowledge_manager = KnowledgeManager(
            db_manager=self.db_manager,
            model_provider=self.embedding_provider,
            config={"directory": self.temp_docs_dir},
        )

        # 角色管理器
        self.role_manager = RoleManager()
        # 设置角色目录
        self.role_manager.roles_dir = self.temp_roles_dir

        # 工具管理器
        self.tool_manager = ToolManager()

        # 辩论管理器
        self.debate_manager = DebateManager(
            session_manager=self.session_manager,
            model_provider=self.llm_provider,
            role_manager=self.role_manager,
        )

        # 智能体执行器
        self.agent_executor = AgentExecutor(
            session_manager=self.session_manager,
            memory_service=self.memory_service,
            knowledge_manager=self.knowledge_manager,
            model_provider=self.llm_provider,
            tool_manager=self.tool_manager,
            user_input_queue=asyncio.Queue(),
        )

        # 配置管理器
        self.config_manager = ConfigManager()

    async def test_ollama_connectivity(self):
        """测试Ollama连接"""

        try:
            # 测试主模型
            start_time = time.time()
            response, usage = await self.llm_provider.generate(
                "Hello, this is a test. Please respond briefly."
            )
            llm_time = time.time() - start_time

            llm_success = isinstance(response, str) and len(response) > 0

            # 测试嵌入模型
            start_time = time.time()
            embedding = await self.embedding_provider.embed(
                "This is a test sentence for embedding."
            )
            embed_time = time.time() - start_time

            embed_success = isinstance(embedding, list) and len(embedding) > 0

            success = llm_success and embed_success

            self.test_results.append(
                {
                    "test": "Ollama连接测试",
                    "success": success,
                    "details": f"LLM响应: {llm_success} ({llm_time:.2f}s), 嵌入: {embed_success} ({embed_time:.2f}s)",  # noqa: E501
                }
            )

            if success:
                pass

            return success

        except Exception as e:
            self.test_results.append(
                {
                    "test": "Ollama连接测试",
                    "success": False,
                    "details": f"连接错误: {str(e)}",
                }
            )
            return False

    async def test_knowledge_base_real(self):
        """测试真实知识库功能"""

        try:
            # 同步知识库
            sync_result = await self.knowledge_manager.sync_knowledge_base()
            sync_success = (
                isinstance(sync_result, dict) and sync_result.get("added", 0) > 0
            )

            # 搜索测试
            search_results = await self.knowledge_manager.search(
                "DAIP-LIVE项目", top_k=3
            )
            search_success = (
                isinstance(search_results, list) and len(search_results) > 0
            )

            success = sync_success and search_success

            self.test_results.append(
                {
                    "test": "真实知识库功能",
                    "success": success,
                    "details": f"同步: {sync_result}, 搜索结果: {len(search_results) if search_results else 0}个",  # noqa: E501
                }
            )

            if success:
                for i, result in enumerate(search_results[:2]):
                    pass

            return success

        except Exception as e:
            self.test_results.append(
                {
                    "test": "真实知识库功能",
                    "success": False,
                    "details": f"错误: {str(e)}",
                }
            )
            return False

    async def test_role_management_real(self):
        """测试真实角色管理"""

        try:
            # 加载角色
            roles = self.role_manager.list_roles()
            list_success = len(roles) > 0

            # 获取特定角色
            if roles:
                role = self.role_manager.get_role_by_name(roles[0].name)
                get_success = role is not None
            else:
                get_success = False

            success = list_success and get_success

            self.test_results.append(
                {
                    "test": "真实角色管理",
                    "success": success,
                    "details": f"加载角色: {len(roles)}个, 角色获取: {get_success}",
                }
            )

            if success:
                for role in roles:
                    pass

            return success

        except Exception as e:
            self.test_results.append(
                {"test": "真实角色管理", "success": False, "details": f"错误: {str(e)}"}
            )
            return False

    async def test_session_management_real(self):
        """测试真实会话管理"""

        try:
            # 创建会话
            session = self.session_manager.create_session(
                goal="测试真实会话功能",
                session_type="chat",
                participant_ids=["user", "assistant"],
            )

            # 添加对话轮次
            self.session_manager.add_dialogue_turn(
                session.session_id, "user", "这是一个测试消息"
            )

            # 检索会话
            retrieved_session = self.session_manager.get_session(session.session_id)

            # 列出会话
            sessions = self.session_manager.list_sessions()

            success = (
                retrieved_session is not None
                and len(retrieved_session.history) > 0
                and len(sessions) > 0
            )

            self.test_results.append(
                {
                    "test": "真实会话管理",
                    "success": success,
                    "details": f"会话创建: ✓, 对话轮次: {len(retrieved_session.history) if retrieved_session else 0}, 会话列表: {len(sessions)}",  # noqa: E501
                }
            )

            if success:
                pass

            return success

        except Exception as e:
            self.test_results.append(
                {"test": "真实会话管理", "success": False, "details": f"错误: {str(e)}"}
            )
            return False

    async def test_agent_executor_real(self):
        """测试真实智能体执行器"""

        try:
            # 创建简单的测试任务
            goal = "请简单介绍一下DAIP-LIVE项目"

            # 收集事件
            events = []
            event_count = 0
            max_events = 10  # 限制事件数量避免无限循环

            async for event in self.agent_executor.run(goal):
                events.append(event)
                event_count += 1

                if hasattr(event, "content"):
                    (
                        event.content[:100] + "..."
                        if len(event.content) > 100
                        else event.content
                    )

                # 限制事件数量
                if event_count >= max_events:
                    break

            success = len(events) > 0

            self.test_results.append(
                {
                    "test": "真实智能体执行器",
                    "success": success,
                    "details": f"生成事件: {len(events)}个, 执行状态: {'成功' if success else '失败'}",  # noqa: E501
                }
            )

            if success:
                pass

            return success

        except Exception as e:
            self.test_results.append(
                {
                    "test": "真实智能体执行器",
                    "success": False,
                    "details": f"错误: {str(e)}",
                }
            )
            return False

    async def test_debate_system_real(self):
        """测试真实辩论系统"""

        try:
            # 检查是否有足够的角色
            roles = self.role_manager.list_roles()
            if len(roles) < 2:
                return True

            # 选择两个角色进行辩论
            role_names = [roles[0].name, roles[1].name]
            topic = "Python和JavaScript哪个更适合初学者学习编程？"

            # 运行辩论（限制轮数）
            debate_session = await self.debate_manager.run_debate(
                topic=topic,
                role_names=role_names,
                rounds=1,  # 只进行1轮避免耗时过长
            )

            success = debate_session is not None and len(debate_session.history) > 0

            self.test_results.append(
                {
                    "test": "真实辩论系统",
                    "success": success,
                    "details": f"辩论轮次: {len(debate_session.history) if debate_session else 0}, 参与角色: {len(role_names)}",  # noqa: E501
                }
            )

            if success:
                pass

            return success

        except Exception as e:
            self.test_results.append(
                {"test": "真实辩论系统", "success": False, "details": f"错误: {str(e)}"}
            )
            return False

    async def test_tui_integration_real(self):
        """测试真实TUI集成"""

        try:
            # 创建TUI实例
            tui = DAIP_TUI(
                executor=self.agent_executor,
                goal=None,
                session_manager=self.session_manager,
                role_manager=self.role_manager,
                knowledge_manager=self.knowledge_manager,
                debate_manager=self.debate_manager,
                model_provider=self.llm_provider,
                db_manager=self.db_manager,
                config_manager=self.config_manager,
            )

            # 测试指令发现
            commands = [cmd for cmd, _ in tui._available_commands]
            command_success = len(commands) > 5

            # 测试自动补全
            suggestions = tui._get_autocomplete_suggestions("/r")
            autocomplete_success = len(suggestions) > 0

            # 模拟指令执行（不涉及UI组件）
            tui._update_log_view = lambda x: None  # 模拟日志更新

            try:
                await tui._handle_shortcut_command("/help")
                command_exec_success = True
            except Exception:
                command_exec_success = False

            success = command_success and autocomplete_success and command_exec_success

            self.test_results.append(
                {
                    "test": "真实TUI集成",
                    "success": success,
                    "details": f"指令: {len(commands)}个, 补全: {len(suggestions)}个建议, 执行: {'成功' if command_exec_success else '失败'}",  # noqa: E501
                }
            )

            if success:
                pass

            return success

        except Exception as e:
            self.test_results.append(
                {"test": "真实TUI集成", "success": False, "details": f"错误: {str(e)}"}
            )
            return False

    async def run_comprehensive_real_test(self):
        """运行全面的真实模型测试"""

        # 初始化真实组件
        await self.setup_real_managers()

        # 测试函数列表
        test_functions = [
            ("Ollama模型连接", self.test_ollama_connectivity),
            ("知识库功能", self.test_knowledge_base_real),
            ("角色管理", self.test_role_management_real),
            ("会话管理", self.test_session_management_real),
            ("智能体执行器", self.test_agent_executor_real),
            ("辩论系统", self.test_debate_system_real),
            ("TUI集成", self.test_tui_integration_real),
        ]

        total_tests = len(test_functions)
        passed_tests = 0

        for test_name, test_func in test_functions:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
                else:
                    pass
            except Exception as e:
                self.test_results.append(
                    {
                        "test": test_name,
                        "success": False,
                        "details": f"测试异常: {str(e)}",
                    }
                )

        for result in self.test_results:
            "✅" if result["success"] else "❌"

        # 评估结果
        if passed_tests == total_tests:
            assessment = "完全可用"
        elif passed_tests >= total_tests * 0.8:
            assessment = "基本可用"
        elif passed_tests >= total_tests * 0.6:
            assessment = "需要调整"
        else:
            assessment = "需要修复"

        # 清理资源
        self.cleanup()

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "assessment": assessment,
            "temp_dir": self.temp_dir,
        }

    def cleanup(self):
        """清理测试资源"""
        try:
            import shutil

            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass


async def main():
    """主测试函数"""

    tester = RealModelIntegrationTester()
    result = await tester.run_comprehensive_real_test()

    return result


if __name__ == "__main__":
    result = asyncio.run(main())
