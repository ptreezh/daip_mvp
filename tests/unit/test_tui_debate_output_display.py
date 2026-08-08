"""
Unit tests for TUI debate output display functionality.

Aligned with the current SimplifiedTUI implementation:
- Event display happens inline in _start_debate's `async for event in debate_events` loop
- run_debate is invoked synchronously and returns an async iterable of events
- Formatting is Chinese text: 🏛️ 辩论开始 / 🗣️ participant (Rn) / 🏁 辩论完成
"""
import pytest
from unittest.mock import Mock, patch
from src.daip_live.tui import DAIP_TUI
from daip_live.core.models import (
    DebateStartEvent, DebateRoundStartEvent, DebateTurnStartEvent,
    DebateTurnCompleteEvent, DebateCompleteEvent
)


async def _async_events(*events):
    """Yield events one at a time, mimicking the real run_debate async iterable."""
    for event in events:
        yield event


def _mock_debate_manager(tui_app, events):
    """Replace the debate manager with one that yields the given events."""
    manager = Mock()
    manager.run_debate.return_value = _async_events(*events)
    tui_app._debate_manager = manager
    return manager


class TestTUIDebateOutputDisplay:
    """Test cases for TUI debate output display functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch('daip_live.container.Container'):
            app = DAIP_TUI()
            return app

    @pytest.mark.asyncio
    async def test_debate_start_event_displays_output(self, tui_app):
        """Test that DebateStartEvent displays output in TUI."""
        # Setup
        event = DebateStartEvent(
            topic="Should AI be regulated?",
            roles=["proponent", "opponent"],
            rounds=3,
            session_id="test_session"
        )
        _mock_debate_manager(tui_app, [event])

        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            await tui_app._start_debate("Should AI be regulated?", "proponent,opponent", 3)

            # Assert that output was displayed
            mock_update_log.assert_called()
            # Check that the call contains debate start information
            call_args = [str(call) for call in mock_update_log.call_args_list]
            assert any("🏛️ 辩论开始" in call and "Should AI be regulated?" in call for call in call_args)

    @pytest.mark.asyncio
    async def test_debate_round_start_event_displays_output(self, tui_app):
        """Test that DebateRoundStartEvent displays output in TUI."""
        # Setup
        event = DebateRoundStartEvent(
            round_number=1,
            total_rounds=3,
            session_id="test_session"
        )
        _mock_debate_manager(tui_app, [event])

        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            await tui_app._start_debate("Topic", "proponent", 1)

            # Assert that output was displayed
            mock_update_log.assert_called()
            # RoundStartEvent has no participant/content, so it falls through to the generic branch
            call_args = [str(call) for call in mock_update_log.call_args_list]
            assert any("📋 事件: DebateRoundStartEvent" in call for call in call_args)

    @pytest.mark.asyncio
    async def test_debate_turn_start_event_displays_output(self, tui_app):
        """Test that DebateTurnStartEvent displays output in TUI."""
        # Setup
        event = DebateTurnStartEvent(
            participant="proponent",
            round_number=1,
            session_id="test_session"
        )
        _mock_debate_manager(tui_app, [event])

        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            await tui_app._start_debate("Topic", "proponent", 1)

            # Assert that output was displayed
            mock_update_log.assert_called()
            # TurnStartEvent only has participant, so it shows the "preparing" line
            call_args = [str(call) for call in mock_update_log.call_args_list]
            assert any("👤 proponent: 正在准备回复..." in call for call in call_args)

    @pytest.mark.asyncio
    async def test_debate_turn_complete_event_displays_output(self, tui_app):
        """Test that DebateTurnCompleteEvent displays output in TUI."""
        # Setup
        event = DebateTurnCompleteEvent(
            participant="proponent",
            round_number=1,
            content_preview="AI regulation is necessary for safety",
            session_id="test_session"
        )
        _mock_debate_manager(tui_app, [event])

        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            await tui_app._start_debate("Topic", "proponent", 1)

            # Assert that output was displayed
            mock_update_log.assert_called()
            # TurnCompleteEvent gets the formatted speech line with round number
            call_args = [str(call) for call in mock_update_log.call_args_list]
            assert any("🗣️ proponent (R1)" in call and "AI regulation is necessary for safety" in call for call in call_args)

    @pytest.mark.asyncio
    async def test_debate_complete_event_displays_output(self, tui_app):
        """Test that DebateCompleteEvent displays output in TUI."""
        # Setup
        event = DebateCompleteEvent(
            session_id="test_session",
            summary="The debate concluded with agreement on the need for balanced AI regulation."
        )
        _mock_debate_manager(tui_app, [event])

        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            await tui_app._start_debate("Topic", "proponent", 1)

            # Assert that output was displayed
            mock_update_log.assert_called()
            call_args = [str(call) for call in mock_update_log.call_args_list]
            assert any("🏁 辩论完成" in call and "balanced AI regulation" in call for call in call_args)

    @pytest.mark.asyncio
    async def test_all_debate_events_display_output_in_sequence(self, tui_app):
        """Test that all debate events display output in correct sequence."""
        # Setup events in sequence
        events = [
            DebateStartEvent(
                topic="Should AI be regulated?",
                roles=["proponent", "opponent"],
                rounds=1,
                session_id="test_session"
            ),
            DebateRoundStartEvent(
                round_number=1,
                total_rounds=1,
                session_id="test_session"
            ),
            DebateTurnStartEvent(
                participant="proponent",
                round_number=1,
                session_id="test_session"
            ),
            DebateTurnCompleteEvent(
                participant="proponent",
                round_number=1,
                content_preview="AI regulation is necessary for safety",
                session_id="test_session"
            ),
            DebateCompleteEvent(
                session_id="test_session",
                summary="The debate concluded with agreement on the need for balanced AI regulation."
            )
        ]
        _mock_debate_manager(tui_app, events)

        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute the whole event stream
            await tui_app._start_debate("Should AI be regulated?", "proponent,opponent", 1)

            # Assert that output was displayed for each event
            assert mock_update_log.call_count >= 5

            # Check that all types of information were displayed
            all_calls = " ".join(str(call) for call in mock_update_log.call_args_list)
            assert "🏛️ 辩论开始" in all_calls
            assert "📋 事件: DebateRoundStartEvent" in all_calls
            assert "👤 proponent: 正在准备回复..." in all_calls
            assert "🗣️ proponent (R1)" in all_calls
            assert "AI regulation is necessary for safety" in all_calls
            assert "🏁 辩论完成" in all_calls
            assert "balanced AI regulation" in all_calls
