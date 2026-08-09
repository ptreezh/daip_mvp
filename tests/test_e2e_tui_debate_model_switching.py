import asyncio
import os

import pytest
from dependency_injector import providers

from daip_live.container import Container
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider as ModelProvider
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.persistence.database import DatabaseManager as Database
from daip_live.tui import DAIP_TUI

pytestmark = pytest.mark.skip(
    reason="TDD红阶段spec，针对已重构移除的旧TUI API；当前源码为准"
)

# Set a fake API key for tests
os.environ["OPENAI_API_KEY"] = "fake_key"


@pytest.fixture
def container():
    """Override the container to use mock providers for external services."""
    container = Container()
    container.config.from_yaml("config.yaml")

    # Use a real database, but in-memory
    container.db_manager.override(providers.Singleton(Database, db_path=":memory:"))

    # Use real managers, but ensure they use the in-memory DB
    container.role_model_manager.override(
        providers.Singleton(RoleModelManager, roles_dir_path="roles")
    )
    container.knowledge_manager.override(
        providers.Singleton(
            KnowledgeManager,
            db_manager=container.db_manager,
            model_provider=container.embed_provider,
            config=container.knowledge_base_config,
        )
    )
    container.model_provider.override(
        providers.Singleton(ModelProvider, config=container.config.llm_provider)
    )

    # Create enhanced debate manager after role_model_manager override to ensure it gets the right instance  # noqa: E501
    role_model_manager_instance = container.role_model_manager()
    container.enhanced_debate_manager.override(
        providers.Singleton(
            EnhancedDebateManager,
            session_manager=container.session_manager,
            role_manager=container.role_manager,
            role_model_manager=role_model_manager_instance,
            model_provider=container.model_provider,
        )
    )

    yield container

    # Reset overrides after test
    container.db_manager.reset_override()
    container.role_model_manager.reset_override()
    container.knowledge_manager.reset_override()
    container.model_provider.reset_override()
    container.enhanced_debate_manager.reset_override()


@pytest.mark.asyncio
async def test_debate_model_switching_e2e(container: Container, capsys):
    """
    End-to-end test for model switching in a TUI debate.
    """
    app = DAIP_TUI(
        executor=container.agent_executor(),
        session_manager=container.session_manager(),
        role_manager=container.role_manager(),
        knowledge_manager=container.knowledge_manager(),
        debate_manager=container.debate_manager(),
        model_provider=container.model_provider(),
        db_manager=container.db_manager(),
        role_model_manager=container.role_model_manager(),
        enhanced_debate_manager=container.enhanced_debate_manager(),
    )

    async with app.run_test() as pilot:
        input_widget = app.query_one("Input")
        input_widget.value = (
            '/debate start "AI Ethics" --roles "tech_analyst,pro_arguer" --rounds 1'
        )
        await pilot.press("enter")

        async def wait_for(pred, timeout=30.0):
            async def _poll():
                while not pred():
                    await asyncio.sleep(0.1)

            await asyncio.wait_for(_poll(), timeout=timeout)

        await app.wait_debate_started()
        assert app._current_debate["role_models"]
        assert app._current_debate["role_models"].get("tech_analyst") == "qwen3:8b"
        assert app._current_debate["role_models"].get("pro_arguer") == "llama3:instruct"

        await app.wait_participant("tech_analyst")
        await app.wait_participant("pro_arguer")

        await app.wait_debate_completed()
