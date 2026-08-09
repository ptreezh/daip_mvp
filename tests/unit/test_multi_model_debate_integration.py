"""多模型辩论集成单元测试 - 对齐真实 EnhancedDebateManager 事件流与 TUI 显示"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from daip_live.core.models import (
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
    DebateTurnStartEvent,
)
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.tui.simplified_main import SimplifiedTUI


def _build_debate_manager():
    """构造真实 EnhancedDebateManager（legacy 路径），外部模型调用全部 mock"""
    session = Mock()
    session.session_id = "session-1"
    session.history = []
    session.summary = ""

    mock_session_manager = Mock()
    mock_session_manager.create_session.return_value = session

    role = Mock()
    role.persona = "测试角色"

    mapping_a = Mock()
    mapping_a.role_name = "proponent"
    mapping_a.priority = 1
    mapping_a.model_config = Mock(
        model_name="gpt-4",
        temperature=0.7,
        max_tokens=512,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    mapping_b = Mock()
    mapping_b.role_name = "opponent"
    mapping_b.priority = 2
    mapping_b.model_config = Mock(
        model_name="claude-3",
        temperature=0.7,
        max_tokens=512,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    mock_role_model_manager = Mock()
    mock_role_model_manager.get_debate_model_mappings.return_value = [
        mapping_a,
        mapping_b,
    ]

    mock_role_manager = Mock()
    mock_role_manager.get_role_by_name.return_value = role

    manager = EnhancedDebateManager(
        session_manager=mock_session_manager,
        role_manager=mock_role_manager,
        role_model_manager=mock_role_model_manager,
        model_provider=Mock(),
        use_optimized_architecture=False,
    )
    manager._generate_response_with_model = AsyncMock(
        return_value=("Test response", {"total_tokens": 10})
    )
    manager._generate_summary_with_model = AsyncMock(
        return_value=("Summary text", None)
    )
    return manager, mock_session_manager, session


async def _collect(manager, topic, roles, rounds):
    return [
        event
        async for event in manager.run_debate(
            topic=topic, roles_names=roles, num_rounds=rounds
        )
    ]


@pytest.mark.asyncio
async def test_run_debate_produces_complete_event_sequence():
    """真实 run_debate 产生完整事件序列"""
    manager, _, _ = _build_debate_manager()
    events = await _collect(
        manager, "Should AI be regulated?", ["proponent", "opponent"], 2
    )

    assert isinstance(events[0], DebateStartEvent)
    assert events[0].topic == "Should AI be regulated?"
    assert events[0].roles == ["proponent", "opponent"]
    assert events[0].rounds == 2

    round_starts = [e for e in events if isinstance(e, DebateRoundStartEvent)]
    assert len(round_starts) == 2
    assert [e.round_number for e in round_starts] == [1, 2]

    turn_starts = [e for e in events if isinstance(e, DebateTurnStartEvent)]
    assert len(turn_starts) == 4  # 2 rounds x 2 roles
    assert {e.participant for e in turn_starts} == {"proponent", "opponent"}

    turn_completes = [e for e in events if isinstance(e, DebateTurnCompleteEvent)]
    assert len(turn_completes) == 4
    assert all(e.content_preview == "Test response" for e in turn_completes)

    assert isinstance(events[-1], DebateCompleteEvent)
    assert events[-1].summary == "Summary text"


@pytest.mark.asyncio
async def test_run_debate_creates_and_saves_session():
    """run_debate 创建并保存传统会话"""
    manager, mock_session_manager, session = _build_debate_manager()
    await _collect(manager, "topic", ["proponent", "opponent"], 1)

    mock_session_manager.create_session.assert_called_once_with(
        goal="topic", session_type="debate", participant_ids=["proponent", "opponent"]
    )
    mock_session_manager.save_session.assert_called_once_with(session)
    assert session.summary == "Summary text"


@pytest.fixture
def tui_app():
    container = Mock()
    container.config_manager.get.return_value = 100
    with patch("daip_live.container.Container", return_value=container):
        return SimplifiedTUI()


async def _async_events(*events):
    for event in events:
        yield event


@pytest.mark.asyncio
async def test_tui_start_debate_displays_events(tui_app):
    """TUI 启动辩论: 实时显示事件格式化行"""
    fake_manager = Mock()
    fake_manager.run_debate = Mock(
        return_value=_async_events(
            DebateStartEvent(
                topic="Should AI be regulated?",
                roles=["proponent", "opponent"],
                rounds=2,
                session_id="s1",
            ),
            DebateRoundStartEvent(round_number=1, total_rounds=2, session_id="s1"),
            DebateTurnStartEvent(
                participant="proponent", round_number=1, session_id="s1"
            ),
            DebateTurnCompleteEvent(
                participant="proponent",
                round_number=1,
                content_preview="Test response",
                session_id="s1",
            ),
            DebateCompleteEvent(session_id="s1", summary="Summary text"),
        )
    )
    tui_app._debate_manager = fake_manager

    await tui_app._start_debate(
        topic="Should AI be regulated?", roles="proponent, opponent", rounds="2"
    )

    logs = "".join(tui_app._log_text_buffer)
    assert "🏛️ 辩论开始: Should AI be regulated?" in logs
    assert "🗣️ proponent (R1):" in logs
    assert "Test response" in logs
    assert "🏁 辩论完成！总结: Summary text" in logs
    assert "✅ 辩论完成" in logs


@pytest.mark.asyncio
async def test_tui_start_debate_without_manager_shows_error(tui_app):
    """无辩论管理器时显示错误"""
    tui_app._debate_manager = None
    await tui_app._start_debate(topic="t", roles="proponent", rounds="1")
    logs = "".join(tui_app._log_text_buffer)
    assert "❌ 辩论管理器未初始化" in logs
