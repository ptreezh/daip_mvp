# -*- coding: utf-8 -*-
"""
@Time    : 2024-07-19 11:15:00
@Author  : DAIP-LIVE Team
@File    : test_tui_unit.py
@Description:
    Unit tests for the Terminal User Interface (TUI) components in src.cli.main.
    These tests focus on testing functions in isolation using mocks.
"""
import asyncio
import pytest
from unittest.mock import MagicMock, patch

from src.cli.main import create_key_bindings
from src.models import UserInterventionCommand, ClearScreenEvent
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import ConditionalContainer, Window, VSplit
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl


@pytest.fixture(autouse=True)
def clear_queues():
    """Fixture to clear queues before each test."""
    from src.cli.main import to_protocol_queue, from_protocol_queue
    while not to_protocol_queue.empty():
        to_protocol_queue.get_nowait()
    while not from_protocol_queue.empty():
        from_protocol_queue.get_nowait()
    yield


@pytest.fixture
def mock_tui_components():
    """A fixture that provides mocked TUI components."""
    input_area_mock = MagicMock(spec=TextArea)
    # The has_focus filter needs a real container. We make our mock return one
    # to satisfy the type checks within prompt_toolkit's `to_container`.
    input_area_mock.__pt_container__ = lambda: VSplit([])

    return {
        "output_area": MagicMock(spec=TextArea),
        "input_area": input_area_mock,
        "input_container": MagicMock(spec=ConditionalContainer),
        "toolbar": MagicMock(spec=Window),
    }


def _create_mock_event():
    """Helper to create a mock event object for key binding handlers."""
    mock_app = MagicMock()
    event = MagicMock()
    event.app = mock_app
    return event


def test_quit_handler(mock_tui_components):
    kb = create_key_bindings(**mock_tui_components)
    mock_event = _create_mock_event()
    handler = kb.get_bindings_for_keys(("q",))[0].handler
    handler(mock_event)
    mock_event.app.exit.assert_called_once()


@patch("src.cli.main.show_verbose_logs", False)
@patch("src.cli.main.output_area")
def test_toggle_verbose_handler(mock_global_output_area, mock_tui_components):
    # The 'v' binding is filtered by has_focus, so we patch it to be false.
    # This test specifically checks the handler's logic, not the filter.
    with patch("prompt_toolkit.filters.has_focus", return_value=Condition(lambda: False)):
        kb = create_key_bindings(**mock_tui_components)
        mock_event = _create_mock_event()
        # We need to find the correct handler. Since filters might exclude one,
        # we find the one for 'v'.
        handler = next(b.handler for b in kb.bindings if "v" in b.keys)
        handler(mock_event)
        # The handler uses the global output_area, so we assert on the patched one.
        mock_global_output_area.text.__iadd__.assert_called_with("\n[System] Verbose logs enabled.\n")
        mock_event.app.invalidate.assert_called_once()


@pytest.mark.asyncio
async def test_clear_screen_handler(mock_tui_components):
    from src.cli.main import from_protocol_queue
    kb = create_key_bindings(**mock_tui_components)
    mock_event = _create_mock_event()
    handler = kb.get_bindings_for_keys(("c-l",))[0].handler
    await handler(mock_event)
    event = await from_protocol_queue.get()
    assert isinstance(event, ClearScreenEvent)


@patch("src.cli.main._tui_state")
def test_intervene_handler(mock_tui_state, mock_tui_components):
    kb = create_key_bindings(**mock_tui_components)
    mock_event = _create_mock_event()
    handler = kb.get_bindings_for_keys(("i",))[0].handler
    handler(mock_event)
    assert mock_tui_state.input_visible is True
    # The content of the toolbar is a FormattedTextControl object
    mock_tui_components["toolbar"].content.text = "Enter your intervention and press Enter to submit."
    mock_event.app.layout.focus.assert_called_once_with(mock_tui_components["input_area"])


@pytest.mark.asyncio
@patch("src.cli.main.to_protocol_queue", new_callable=asyncio.Queue)
@patch("src.cli.main._tui_state")
async def test_submit_intervention_handler(mock_tui_state, mock_queue, mock_tui_components):
    mock_event = _create_mock_event()
    mock_event.app.current_buffer.text = "test intervention"
    mock_tui_components["input_area"].buffer = mock_event.app.current_buffer

    with patch("prompt_toolkit.filters.has_focus", return_value=Condition(lambda: True)):
        kb = create_key_bindings(**mock_tui_components)
        handler = next(b.handler for b in kb.bindings if "enter" in b.keys and b.filter is not None)
        await handler(mock_event)

    command = await mock_queue.get()
    assert isinstance(command, UserInterventionCommand)
    assert command.content == "test intervention"
    assert mock_tui_state.input_visible is False
    mock_event.app.current_buffer.reset.assert_called_once()
    mock_tui_components["output_area"].text.__iadd__.assert_called()


@patch("src.cli.main.pathlib.Path")
def test_save_transcript_success(MockPath, mock_tui_components):
    mock_path_instance = MockPath.return_value
    mock_file_obj = mock_path_instance.__truediv__.return_value
    
    # Configure the mock's text attribute to be a mock itself,
    # which can be read as a string and also have its methods asserted.
    mock_text = MagicMock()
    mock_text.__str__.return_value = "Topic: Test\nContent"
    mock_tui_components["output_area"].text = mock_text

    kb = create_key_bindings(**mock_tui_components)
    mock_event = _create_mock_event()
    handler = kb.get_bindings_for_keys(("c-s",))[0].handler
    handler(mock_event)

    mock_file_obj.write_text.assert_called_once_with("Topic: Test\nContent", encoding="utf-8")
    mock_text.__iadd__.assert_called_with(f"\n[System] Transcript saved to {mock_file_obj}\n")


@patch("src.cli.main.pathlib.Path")
def test_save_transcript_io_error(MockPath, mock_tui_components):
    mock_path_instance = MockPath.return_value
    mock_file_obj = mock_path_instance.__truediv__.return_value
    mock_file_obj.write_text.side_effect = IOError("Permission Denied")

    # Configure the mock's text attribute to be a mock itself.
    mock_text = MagicMock()
    mock_text.__str__.return_value = "Topic: Test\nContent"
    mock_tui_components["output_area"].text = mock_text

    kb = create_key_bindings(**mock_tui_components)
    mock_event = _create_mock_event()
    handler = kb.get_bindings_for_keys(("c-s",))[0].handler
    handler(mock_event)

    mock_text.__iadd__.assert_called_with("\n[System] Error saving transcript: Permission Denied\n")
