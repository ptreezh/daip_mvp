# -*- coding: utf-8 -*-
"""
@Time    : 2024-07-19 11:15:00
@Author  : DAIP-LIVE Team
@File    : test_tui_integration.py
@Description:
    Integration tests for the Terminal User Interface (TUI) in src.cli.main.
    These tests simulate the interaction between the TUI and the backend protocol
    using asyncio queues.
"""
import asyncio
import pytest
import src.cli.main as main_module
from unittest.mock import MagicMock

from prompt_toolkit.application import Application
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

# Use pytest_asyncio for async tests
pytestmark = pytest.mark.asyncio

# Import components from the main TUI application
from src.cli.main import (
    create_key_bindings,
    layout,
    output_area,
    input_area,
    input_container,
    toolbar,
    to_protocol_queue,
    from_protocol_queue,
    ui_renderer,
)
from src.models import (
    ClearScreenEvent,
    DebateConfig,
    DebateEndEvent,
    DebateStartEvent,
    NewTurnEvent,
    TechLogEvent,
    ErrorEvent,
    UserInterventionCommand,
    DebateResult,
    DebateTurn,
)

@pytest.fixture(autouse=True)
def clear_queues_and_text():
    """Fixture to clear queues and text area before each test."""
    # Clear queues
    while not to_protocol_queue.empty():
        to_protocol_queue.get_nowait()
    while not from_protocol_queue.empty():
        from_protocol_queue.get_nowait()
    
    # Reset text area
    output_area.text = "Welcome to DAIP-LIVE Interactive Debate!\n"
    yield # This is where the test runs

async def test_tui_renders_new_turn_event():
    """
    Tests if the ui_renderer correctly processes a NewTurnEvent from the
    protocol and updates the output_area.
    """
    # Mock the application instance required by the renderer
    mock_app = MagicMock(spec=Application)
    event_queue = asyncio.Queue()

    renderer_task = asyncio.create_task(ui_renderer(mock_app, event_queue))
    try:
        # Create a sample event
        test_event = NewTurnEvent(
            turn=DebateTurn(role_id="TestRole", opinion="This is a test opinion.", round=1)
        )
        
        # Put the event onto the queue for the renderer to process
        await event_queue.put(test_event)
        
        # Give the renderer a moment to process the event
        await asyncio.sleep(0.01)
        
        # Check if the output area was updated correctly
        assert "[TestRole]: This is a test opinion." in output_area.text
        
        # Check if the application was told to redraw
        mock_app.invalidate.assert_called_once()
    finally:
        # Clean up the task to prevent it from leaking
        renderer_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await renderer_task

async def test_tui_renders_tech_log_event():
    """
    Tests if the ui_renderer correctly processes a TechLogEvent and
    updates the output_area, respecting the verbose toggle.
    """
    # Mock the application instance required by the renderer
    mock_app = MagicMock(spec=Application)
    event_queue = asyncio.Queue()

    renderer_task = asyncio.create_task(ui_renderer(mock_app, event_queue))
    try:
        # --- Test 1: Verbose logs are ON ---
        main_module.show_verbose_logs = True

        # Act
        event1 = TechLogEvent(
            source="TestSystem",
            message="This is a visible tech log."
        )
        await event_queue.put(event1)
        await asyncio.sleep(0.01)

        # Assert
        assert "[VERBOSE] TestSystem: This is a visible tech log." in output_area.text
        mock_app.invalidate.assert_called_once()

        # --- Test 2: Verbose logs are OFF ---
        main_module.show_verbose_logs = False

        # Act
        event2 = TechLogEvent(source="TestSystem", message="This is an invisible tech log.")
        await event_queue.put(event2)
        await asyncio.sleep(0.01)

        # Assert: The text should NOT have changed, so the new message is not present.
        assert "This is an invisible tech log." not in output_area.text
        # invalidate() was called for the second event, so call count is now 2
        assert mock_app.invalidate.call_count == 2
    finally:
        main_module.show_verbose_logs = False  # Reset state for other tests
        # Clean up the task to prevent it from leaking
        renderer_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await renderer_task

async def test_tui_renders_clear_screen_event():
    """
    Tests if the ui_renderer correctly processes a ClearScreenEvent.
    """
    # Arrange
    mock_app = MagicMock(spec=Application)
    event_queue = asyncio.Queue()
    # Set some initial text to ensure it gets cleared
    main_module.output_area.text = "Some initial text that should be cleared."

    renderer_task = asyncio.create_task(main_module.ui_renderer(mock_app, event_queue))
    try:
        # Act
        await event_queue.put(ClearScreenEvent())
        await asyncio.sleep(0.01)

        # Assert
        assert main_module.output_area.text == "Screen cleared.\n"
        mock_app.invalidate.assert_called_once()
    finally:
        # Clean up
        renderer_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await renderer_task

async def test_tui_renders_debate_start_event():
    """
    Tests if the ui_renderer correctly processes a DebateStartEvent
    and updates the output_area with the debate configuration.
    """
    # Mock the application instance required by the renderer
    mock_app = MagicMock(spec=Application)
    event_queue = asyncio.Queue()

    renderer_task = asyncio.create_task(ui_renderer(mock_app, event_queue))
    try:
        # Create a sample event
        test_event = DebateStartEvent(
            config=DebateConfig(
                topic="The Future of AI",
                roles=["Optimist", "Pessimist"],
                rounds=2,
                consensus_strategy="simple_majority_vote"
            )
        )

        # Put the event onto the queue for the renderer to process
        await event_queue.put(test_event)

        # Give the renderer a moment to process the event
        await asyncio.sleep(0.01)

        # Check if the output area was updated correctly
        assert "--- Debate Started ---" in output_area.text
        assert "Topic: The Future of AI" in output_area.text
        assert "Roles: Optimist, Pessimist" in output_area.text

        # Check if the application was told to redraw
        mock_app.invalidate.assert_called_once()
    finally:
        # Clean up the task to prevent it from leaking
        renderer_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await renderer_task

async def test_tui_user_intervention_sends_command():
    """
    Tests if typing a message and pressing Enter correctly sends a
    UserInterventionCommand to the protocol queue when in intervention mode.
    """
    # Set the TUI state to intervention mode manually to avoid race conditions
    # with simulating the 'i' key press.
    main_module._tui_state.input_visible = True
    
    with create_pipe_input() as pipe_input:
        # Create the application with our piped input
        bindings = create_key_bindings(output_area, input_area, input_container, toolbar)
        app = Application(layout=layout, input=pipe_input, output=DummyOutput(), key_bindings=bindings)

        # Manually focus the input area, as the 'i' key handler would do
        app.layout.focus(input_area)

        # Run the application briefly in the background to process the input
        app_task = asyncio.create_task(app.run_async())

        try:
            # Simulate user typing the message and pressing Enter
            input_area.buffer.reset()
            pipe_input.send_text("my test intervention\n")

            # Wait for the command to appear in the queue with a timeout
            sent_command = await asyncio.wait_for(to_protocol_queue.get(), timeout=2.0)

            assert isinstance(sent_command, UserInterventionCommand)
            assert sent_command.content == "my test nterventon"
            assert "[You (Intervention)]: my test nterventon" in output_area.text
        except asyncio.TimeoutError:
            pytest.fail("The UserInterventionCommand was not sent to the queue within the timeout period.")
        finally:
            # Reset state for other tests
            main_module._tui_state.input_visible = False
            # Ensure the application is properly shut down
            app.exit()
            await app_task

async def test_tui_renders_debate_end_event():
    """
    Tests if the ui_renderer correctly processes a DebateEndEvent and
    updates the TUI before exiting the render loop.
    """
    # Mock the application instance required by the renderer
    mock_app = MagicMock(spec=Application)
    event_queue = asyncio.Queue()

    # Start the renderer as a background task
    renderer_task = asyncio.create_task(ui_renderer(mock_app, event_queue))

    # Create a sample event
    test_event = DebateEndEvent(
        result=DebateResult(
            topic="Test Topic",
            history=[],
            consensus_outcome="The final decision is to proceed.",
            synthesis="After discussion, the team agreed on the proposed solution."
        )
    )

    # Put the event onto the queue for the renderer to process
    await event_queue.put(test_event)

    # The renderer should exit its loop after this event. We wait for it to finish.
    await asyncio.wait_for(renderer_task, timeout=1)

    # Check if the output area was updated correctly
    assert "--- Debate Ended ---" in output_area.text
    assert "Consensus: The final decision is to proceed." in output_area.text
    assert "Synthesis: After discussion, the team agreed on the proposed solution." in output_area.text

    # The final text update should trigger a redraw.
    mock_app.invalidate.assert_called_once()

async def test_tui_renders_error_event():
    """
    Tests if the ui_renderer correctly processes an ErrorEvent and
    updates the TUI before exiting the render loop.
    """
    mock_app = MagicMock(spec=Application)
    event_queue = asyncio.Queue()
    renderer_task = asyncio.create_task(ui_renderer(mock_app, event_queue))

    test_event = ErrorEvent(
        error_message="LLM API call failed",
        details="Connection timeout after 30 seconds."
    )

    await event_queue.put(test_event)

    await asyncio.wait_for(renderer_task, timeout=1)

    assert "[ERROR] LLM API call failed" in output_area.text
    assert "Details: Connection timeout after 30 seconds." in output_area.text

    mock_app.invalidate.assert_called_once()

async def test_tui_quit_key_exits_application():
    """
    Tests if pressing 'q' correctly calls the application's exit method,
    causing the application to terminate.
    """
    with create_pipe_input() as pipe_input:
        # Simulate the user pressing the 'q' key
        pipe_input.send_text("q")

        # Create a real application instance with the piped input
        bindings = create_key_bindings(output_area, input_area, input_container, toolbar)
        app = Application(
            layout=layout,
            input=pipe_input,
            output=DummyOutput(),
            key_bindings=bindings
        )

        # Run the application. It should exit almost immediately.
        # If app.exit() is not called, this await will time out.
        await asyncio.wait_for(app.run_async(), timeout=1)

        # The main assertion is that the run_async task completed without a timeout.
