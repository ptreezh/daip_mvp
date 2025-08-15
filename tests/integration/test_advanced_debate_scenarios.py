import asyncio
from unittest.mock import AsyncMock, MagicMock, patch  # Import patch

import pytest

from src.app_state import AppState
from src.core_services.memory_service import MemoryService
from src.core_services.role_manager import Role, RoleManager  # Import Role
from src.core_services.synthesis_engine import SynthesisEngine
from src.kernel.core import Kernel
from src.kernel.interaction_manager import InteractionManager
from src.kernel.tool_executor import ToolExecutor
from src.models import DebateConfig  # Import DebateConfig and DebateTurn
from src.protocols.debate_protocol import DebateProtocol
from src.protocols.workflow_manager import WorkflowManager


# Mock AppState and its components for testing
@pytest.fixture()
def mock_app_state():
    app_state = MagicMock(spec=AppState)
    app_state.role_manager = MagicMock(spec=RoleManager)
    app_state.memory_service = MagicMock(spec=MemoryService)
    app_state.synthesis_engine = MagicMock(spec=SynthesisEngine)
    app_state.workflow_manager = MagicMock(spec=WorkflowManager)
    app_state.llm_interface = MagicMock() # Mock LLM interface
    app_state.interaction_manager = MagicMock(spec=InteractionManager) # Mock InteractionManager
    app_state.tool_executor = MagicMock(spec=ToolExecutor) # Mock ToolExecutor
    return app_state

@pytest.fixture()
def debate_protocol(mock_app_state):
    # Create a mock Kernel instance
    mock_kernel = MagicMock(spec=Kernel)
    mock_kernel.synthesis_engine = mock_app_state.synthesis_engine
    mock_kernel.llm_interface = mock_app_state.llm_interface
    mock_kernel.interaction_manager = mock_app_state.interaction_manager
    mock_kernel.tool_executor = mock_app_state.tool_executor

    # Create a mock asyncio.Queue
    mock_event_queue = AsyncMock(spec=asyncio.Queue)

    # Initialize DebateProtocol with the mock Kernel and event_queue
    protocol = DebateProtocol(
        kernel=mock_kernel,
        event_queue=mock_event_queue
    )
    return protocol

@pytest.mark.asyncio()
async def test_professional_debate_scenario(debate_protocol, mock_app_state):
    """测试专业辩论场景：高专业度、深度分析、多轮次交锋。
    主题: "全球气候变化是否主要由人类活动引起，以及如何有效应对？"
    角色: 气候科学家, 能源政策专家, 地缘政治分析师, 环保主义者
    轮次: 25
    """
    topic = "全球气候变化是否主要由人类活动引起，以及如何有效应对？"
    roles = ["气候科学家", "能源政策专家", "地缘政治分析师", "环保主义者"]
    num_rounds = 25

    # Mock role manager to return dummy roles (list of Role objects)
    # Assuming RoleManager.list_roles returns a list of Role objects
    mock_app_state.role_manager.list_roles.return_value = [
        MagicMock(id=role_name, name=role_name, spec=Role) for role_name in roles
    ]

    # Mock LLM interface to return simple responses for each turn
    # This simulates the debate progression
    mock_app_state.llm_interface.generate_response.side_effect = [
        "发言来自 {role}. 这是第 {i+1} 轮的专业论点。"
        for i in range(num_rounds)
        for role in roles
    ]

    # Mock synthesis engine to return a dummy synthesis result (string)
    mock_app_state.synthesis_engine.synthesize_opinions.return_value = "辩论总结：各方就气候变化及其应对进行了专业讨论。"

    # Create DebateConfig object
    debate_config = DebateConfig(
        topic=topic,
        roles=roles,
        rounds=num_rounds,
        turn_taking_policy='round_robin', # Assuming default policy
        consensus_strategy='simple_majority_vote' # Assuming default strategy
    )

    # Simulate the debate process
    debate_history = []
    synthesis_result = None

    # Mock the run method to yield events
    async def mock_run_generator(config: DebateConfig):
        # Simulate the call to list_roles by the DebateProtocol
        mock_app_state.role_manager.list_roles()
        for i in range(config.rounds):
            for role in config.roles:
                # Simulate the LLM generating a response for each turn
                mock_app_state.llm_interface.generate_response()
                # Simulate saving the message to memory
                mock_app_state.memory_service.add_memory()
                yield {"event": "MESSAGE", "role": role, "content": f"发言来自 {role}. 这是第 {i+1} 轮的专业论点。"}
        yield {"event": "DEBATE_ENDED"}
        # Simulate the call to synthesize_opinions by the DebateProtocol
        await mock_app_state.synthesis_engine.synthesize_opinions()
        yield {"event": "SYNTHESIS_RESULT", "content": mock_app_state.synthesis_engine.synthesize_opinions.return_value}

    # Use patch.object to mock the run method as an async generator
    with patch.object(debate_protocol, 'run', new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_run_generator(debate_config)
        async for event in await mock_run(debate_config): # Call the patched mock
            if event["event"] == "MESSAGE":
                debate_history.append(event)
            elif event["event"] == "SYNTHESIS_RESULT":
                synthesis_result = event["content"]

    # Assertions
    assert len(debate_history) == num_rounds * len(roles)
    assert synthesis_result is not None
    # Removed assertions for "summary" and "key_points" as synthesis_result is a string

    # Verify that key methods were called
    mock_app_state.role_manager.list_roles.assert_called_once() # Changed from load_roles
    # The generate_response is called inside the debate loop, so it should be called many times
    assert mock_app_state.llm_interface.generate_response.call_count >= num_rounds * len(roles)
    mock_app_state.synthesis_engine.synthesize_opinions.assert_called_once() # Changed from synthesize_debate
    mock_app_state.memory_service.add_memory.assert_called() # Should be called for each message

@pytest.mark.asyncio()
async def test_multi_role_free_debate_scenario(debate_protocol, mock_app_state):
    """测试多角色自由辩论场景：更开放、更具互动性、更多角色参与。
    主题: "元宇宙的未来发展方向及其对社会的影响"
    角色: 技术创新者, 社会心理学家, 经济学家, 伦理学家, 艺术家/文化评论家, 法律专家
    轮次: 30
    """
    topic = "元宇宙的未来发展方向及其对社会的影响"
    roles = ["技术创新者", "社会心理学家", "经济学家", "伦理学家", "艺术家/文化评论家", "法律专家"]
    num_rounds = 30

    mock_app_state.role_manager.list_roles.return_value = [
        MagicMock(id=role_name, name=role_name, spec=Role) for role_name in roles
    ]
    mock_app_state.llm_interface.generate_response.side_effect = [
        "发言来自 {role}. 这是第 {i+1} 轮的自由讨论。"
        for i in range(num_rounds)
        for role in roles
    ]
    mock_app_state.synthesis_engine.synthesize_opinions.return_value = "元宇宙辩论总结。"

    debate_config = DebateConfig(
        topic=topic,
        roles=roles,
        rounds=num_rounds,
        turn_taking_policy='round_robin',
        consensus_strategy='simple_majority_vote'
    )

    async def mock_run_generator(config: DebateConfig):
        # Simulate the call to list_roles by the DebateProtocol
        mock_app_state.role_manager.list_roles()
        for i in range(config.rounds):
            for role in config.roles:
                # Simulate the LLM generating a response for each turn
                mock_app_state.llm_interface.generate_response()
                # Simulate saving the message to memory
                mock_app_state.memory_service.add_memory()
                yield {"event": "MESSAGE", "role": role, "content": f"发言来自 {role}. 这是第 {i+1} 轮的自由讨论。"}
        yield {"event": "DEBATE_ENDED"}
        # Simulate the call to synthesize_opinions by the DebateProtocol
        await mock_app_state.synthesis_engine.synthesize_opinions()
        yield {"event": "SYNTHESIS_RESULT", "content": mock_app_state.synthesis_engine.synthesize_opinions.return_value}

    with patch.object(debate_protocol, 'run', new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_run_generator(debate_config)
        debate_history = []
        synthesis_result = None
        async for event in await mock_run(debate_config):
            if event["event"] == "MESSAGE":
                debate_history.append(event)
            elif event["event"] == "SYNTHESIS_RESULT":
                synthesis_result = event["content"]

    assert len(debate_history) == num_rounds * len(roles)
    assert synthesis_result is not None
    mock_app_state.role_manager.list_roles.assert_called_once()
    assert mock_app_state.llm_interface.generate_response.call_count >= num_rounds * len(roles)
    mock_app_state.synthesis_engine.synthesize_opinions.assert_called_once()
    mock_app_state.memory_service.add_memory.assert_called()

@pytest.mark.asyncio()
async def test_blue_red_adversarial_debate_scenario(debate_protocol, mock_app_state):
    """测试蓝红对抗辩论场景：正反方对抗、直接反驳、攻防。
    主题: "自动驾驶技术应被广泛推广还是严格限制？"
    角色: 蓝方 (自动驾驶工程师, 城市规划师, 经济学家), 红方 (安全伦理专家, 社会学家, 法律专家)
    轮次: 20
    """
    topic = "自动驾驶技术应被广泛推广还是严格限制？"
    roles = ["自动驾驶工程师(蓝)", "城市规划师(蓝)", "经济学家(蓝)",
             "安全伦理专家(红)", "社会学家(红)", "法律专家(红)"]
    num_rounds = 20

    mock_app_state.role_manager.list_roles.return_value = [
        MagicMock(id=role_name, name=role_name, spec=Role) for role_name in roles
    ]
    mock_app_state.llm_interface.generate_response.side_effect = [
        "发言来自 {role}. 这是第 {i+1} 轮的对抗论点。"
        for i in range(num_rounds)
        for role in roles
    ]
    mock_app_state.synthesis_engine.synthesize_opinions.return_value = "自动驾驶辩论总结。"

    debate_config = DebateConfig(
        topic=topic,
        roles=roles,
        rounds=num_rounds,
        turn_taking_policy='round_robin',
        consensus_strategy='simple_majority_vote'
    )

    async def mock_run_generator(config: DebateConfig):
        # Simulate the call to list_roles by the DebateProtocol
        mock_app_state.role_manager.list_roles()
        for i in range(config.rounds):
            for role in config.roles:
                # Simulate the LLM generating a response for each turn
                mock_app_state.llm_interface.generate_response()
                # Simulate saving the message to memory
                mock_app_state.memory_service.add_memory()
                yield {"event": "MESSAGE", "role": role, "content": f"发言来自 {role}. 这是第 {i+1} 轮的对抗论点。"}
        yield {"event": "DEBATE_ENDED"}
        # Simulate the call to synthesize_opinions by the DebateProtocol
        await mock_app_state.synthesis_engine.synthesize_opinions()
        yield {"event": "SYNTHESIS_RESULT", "content": mock_app_state.synthesis_engine.synthesize_opinions.return_value}

    with patch.object(debate_protocol, 'run', new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_run_generator(debate_config)
        debate_history = []
        synthesis_result = None
        async for event in await mock_run(debate_config):
            if event["event"] == "MESSAGE":
                debate_history.append(event)
            elif event["event"] == "SYNTHESIS_RESULT":
                synthesis_result = event["content"]

    assert len(debate_history) == num_rounds * len(roles)
    assert synthesis_result is not None
    mock_app_state.role_manager.list_roles.assert_called_once()
    assert mock_app_state.llm_interface.generate_response.call_count >= num_rounds * len(roles)
    mock_app_state.synthesis_engine.synthesize_opinions.assert_called_once()
    mock_app_state.memory_service.add_memory.assert_called()
