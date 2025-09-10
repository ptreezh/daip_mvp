"""
DAIP-LIVE 回归测试基准
用于确保修复过程中系统功能不受影响
"""
import os
import tempfile
from unittest.mock import Mock, patch

import pytest


# 核心组件导入测试
def test_core_imports():
    """测试所有核心组件能够正常导入"""
    try:
        from daip_live.core.exceptions import DAIPError
        from daip_live.core.interfaces import IKnowledgeManager, IModelProvider, ITool
        from daip_live.core.models import AgentState, Role, Session
        assert True, "Core imports successful"
    except ImportError as e:
        pytest.fail(f"Core import failed: {e}")

def test_config_management():
    """测试配置管理功能"""
    from daip_live.config import config_manager

    # 测试配置加载
    try:
        config = config_manager.get_config()
        assert hasattr(config, 'database')
        assert hasattr(config, 'llm_provider')
        assert hasattr(config, 'knowledge_base')
        assert config.database.path is not None
    except Exception as e:
        pytest.fail(f"Config management failed: {e}")

def test_database_manager_creation():
    """测试数据库管理器创建"""
    from daip_live.persistence.database import DatabaseManager

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        try:
            db_manager = DatabaseManager(tmp.name)
            assert db_manager is not None
        except Exception as e:
            pytest.fail(f"Database manager creation failed: {e}")
        finally:
            os.unlink(tmp.name)

def test_session_manager_basic():
    """测试会话管理器基本功能"""
    from daip_live.core.models import Session
    from daip_live.memory.session_manager import SessionManager

    try:
        session_manager = SessionManager()
        # 测试创建会话
        session = Session(
            session_type="chat",
            goal="test goal",
            participant_ids=["user_human"]
        )
        assert session.session_id is not None
        assert session.goal == "test goal"
    except Exception as e:
        pytest.fail(f"Session manager basic test failed: {e}")

def test_role_manager_basic():
    """测试角色管理器基本功能"""
    from daip_live.p4_role_manager_tools.role_manager import RoleManager

    try:
        role_manager = RoleManager()
        # 测试角色加载（应该能处理空角色目录）
        roles = role_manager._roles
        assert isinstance(roles, dict)
    except Exception as e:
        pytest.fail(f"Role manager basic test failed: {e}")

def test_tool_manager_basic():
    """测试工具管理器基本功能"""
    from daip_live.p4_role_manager_tools.tool_manager import ToolManager

    try:
        tool_manager = ToolManager()
        # 测试工具管理器创建成功
        assert tool_manager is not None
        # 测试工具注册表存在
        assert hasattr(tool_manager, '_tools')
    except Exception as e:
        pytest.fail(f"Tool manager basic test failed: {e}")

def test_knowledge_manager_creation():
    """测试知识管理器创建"""
    from daip_live.core.models import ProviderConfig
    from daip_live.knowledge.manager import KnowledgeManager
    from daip_live.model_provider.provider import LiteLLMProvider
    from daip_live.persistence.database import DatabaseManager

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        try:
            db_manager = DatabaseManager(tmp.name)
            provider_config = ProviderConfig(model="test-model")
            model_provider = LiteLLMProvider(provider_config)

            # 创建临时知识目录
            with tempfile.TemporaryDirectory() as temp_dir:
                config = {"knowledge_dir": temp_dir}
                knowledge_manager = KnowledgeManager(
                    db_manager=db_manager,
                    model_provider=model_provider,
                    config=config
                )
                assert knowledge_manager is not None
        except Exception as e:
            pytest.fail(f"Knowledge manager creation failed: {e}")
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

@patch('litellm.completion')
def test_model_provider_basic(mock_completion):
    """测试模型提供商基本功能"""
    from daip_live.core.models import ProviderConfig
    from daip_live.model_provider.provider import LiteLLMProvider

    # Mock LiteLLM响应
    mock_completion.return_value = Mock(
        choices=[Mock(message=Mock(content="test response"))]
    )

    try:
        config = ProviderConfig(model="test-model")
        provider = LiteLLMProvider(config)

        # 测试基本生成功能
        response = provider.generate("test prompt")
        assert response is not None
    except Exception as e:
        pytest.fail(f"Model provider basic test failed: {e}")

def test_agent_executor_creation():
    """测试智能体执行器创建"""
    import asyncio

    from daip_live.agent_engine.executor import AgentExecutor
    from daip_live.core.models import ProviderConfig
    from daip_live.knowledge.manager import KnowledgeManager
    from daip_live.memory.service import MemoryService
    from daip_live.memory.session_manager import SessionManager
    from daip_live.model_provider.provider import LiteLLMProvider
    from daip_live.p4_role_manager_tools.tool_manager import ToolManager
    from daip_live.persistence.database import DatabaseManager

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        try:
            # 创建所需组件
            session_manager = SessionManager()

            db_manager = DatabaseManager(tmp.name)
            provider_config = ProviderConfig(model="test-model")
            model_provider = LiteLLMProvider(provider_config)
            memory_service = MemoryService(model_provider)

            with tempfile.TemporaryDirectory() as temp_dir:
                config = {"knowledge_dir": temp_dir}
                knowledge_manager = KnowledgeManager(
                    db_manager=db_manager,
                    model_provider=model_provider,
                    config=config
                )

            tool_manager = ToolManager()
            user_input_queue = asyncio.Queue()

            # 创建智能体执行器
            executor = AgentExecutor(
                session_manager=session_manager,
                memory_service=memory_service,
                knowledge_manager=knowledge_manager,
                model_provider=model_provider,
                tool_manager=tool_manager,
                user_input_queue=user_input_queue
            )
            assert executor is not None
        except Exception as e:
            pytest.fail(f"Agent executor creation failed: {e}")
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

def test_cli_module_import():
    """测试CLI模块导入（不执行CLI命令）"""
    try:
        from daip_live.cli import app
        assert app is not None
        # 测试CLI应用对象创建成功
        assert hasattr(app, 'commands')
    except Exception as e:
        pytest.fail(f"CLI module import failed: {e}")

def test_tui_module_import():
    """测试TUI模块导入"""
    try:
        from daip_live.tui import DAIP_TUI
        assert DAIP_TUI is not None
    except Exception as e:
        pytest.fail(f"TUI module import failed: {e}")

class TestSystemIntegration:
    """系统集成测试类"""

    def test_full_component_integration(self):
        """测试完整组件集成（模拟CLI run命令的组件初始化）"""

        from daip_live.config import config_manager
        from daip_live.core.models import ProviderConfig
        from daip_live.knowledge.manager import KnowledgeManager
        from daip_live.memory.service import MemoryService
        from daip_live.memory.session_manager import SessionManager
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.p4_role_manager_tools.role_manager import RoleManager
        from daip_live.p4_role_manager_tools.tool_manager import ToolManager
        from daip_live.p8_debate_system.manager import DebateManager
        from daip_live.persistence.database import DatabaseManager

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            try:
                # 模拟完整的组件初始化流程
                cfg = config_manager.get_config()

                # 使用临时数据库
                db_manager = DatabaseManager(tmp.name)

                # 创建嵌入模型提供商
                embed_provider_config = ProviderConfig(model=cfg.llm_provider.embedding_model)
                embed_provider = LiteLLMProvider(embed_provider_config)

                # 创建知识管理器
                with tempfile.TemporaryDirectory() as temp_dir:
                    knowledge_config = {"knowledge_dir": temp_dir}
                    knowledge_manager = KnowledgeManager(
                        db_manager=db_manager,
                        model_provider=embed_provider,
                        config=knowledge_config
                    )

                # 创建主模型提供商
                model_provider = LiteLLMProvider(config=cfg.llm_provider)

                # 创建其他组件
                tool_manager = ToolManager()
                session_manager = SessionManager()
                memory_service = MemoryService(model_provider)
                role_manager = RoleManager()

                # 创建辩论管理器
                debate_manager = DebateManager(
                    session_manager=session_manager,
                    role_manager=role_manager,
                    model_provider=model_provider
                )

                # 验证所有组件都创建成功
                assert db_manager is not None
                assert knowledge_manager is not None
                assert model_provider is not None
                assert tool_manager is not None
                assert session_manager is not None
                assert memory_service is not None
                assert role_manager is not None
                assert debate_manager is not None

            except Exception as e:
                pytest.fail(f"Full component integration failed: {e}")
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
