"""
End-to-End Tests for Enhanced Debate Features
"""

import asyncio
import os
import tempfile

import pytest

from daip_live.config import ConfigManager
from daip_live.container import Container
from daip_live.core.models import (
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
    DebateTurnStartEvent,
)
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.tui_v1.models.debate_view import (
    DebateParticipantView,
    EnhancedDebateView,
)


class TestEnhancedDebateEndToEnd:
    """End-to-end tests for enhanced debate features."""

    def test_complete_debate_workflow_end_to_end(self):
        """Test complete debate workflow from start to finish."""
        tracker = DebateHistoryTracker(
            db_path=os.path.join(tempfile.mkdtemp(), "debate_history.db")
        )

        # 1. Start debate
        start_event = DebateStartEvent(
            topic="Complete Workflow E2E Test",
            roles=["Pro_Arguer", "Con_Arguer", "Moderator"],
            rounds=3,
            session_id="e2e_complete_001",
        )

        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.session_id == "e2e_complete_001"
        assert history.topic == "Complete Workflow E2E Test"
        assert len(history.participants) == 3
        assert history.total_rounds == 3
        assert history.status == "active"

        # 2. Simulate full debate execution with all rounds and turns
        debate_events = [
            # Round 1
            DebateRoundStartEvent(
                round_number=1, total_rounds=3, session_id="e2e_complete_001"
            ),
            DebateTurnStartEvent(
                participant="Pro_Arguer", round_number=1, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Pro_Arguer",
                round_number=1,
                content_preview="Pro argument round 1",
                session_id="e2e_complete_001",
            ),
            DebateTurnStartEvent(
                participant="Con_Arguer", round_number=1, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Con_Arguer",
                round_number=1,
                content_preview="Con argument round 1",
                session_id="e2e_complete_001",
            ),
            DebateTurnStartEvent(
                participant="Moderator", round_number=1, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Moderator",
                round_number=1,
                content_preview="Moderator summary round 1",
                session_id="e2e_complete_001",
            ),
            # Round 2
            DebateRoundStartEvent(
                round_number=2, total_rounds=3, session_id="e2e_complete_001"
            ),
            DebateTurnStartEvent(
                participant="Con_Arguer", round_number=2, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Con_Arguer",
                round_number=2,
                content_preview="Con argument round 2",
                session_id="e2e_complete_001",
            ),
            DebateTurnStartEvent(
                participant="Pro_Arguer", round_number=2, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Pro_Arguer",
                round_number=2,
                content_preview="Pro argument round 2",
                session_id="e2e_complete_001",
            ),
            DebateTurnStartEvent(
                participant="Moderator", round_number=2, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Moderator",
                round_number=2,
                content_preview="Moderator summary round 2",
                session_id="e2e_complete_001",
            ),
            # Round 3
            DebateRoundStartEvent(
                round_number=3, total_rounds=3, session_id="e2e_complete_001"
            ),
            DebateTurnStartEvent(
                participant="Moderator", round_number=3, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Moderator",
                round_number=3,
                content_preview="Moderator final summary",
                session_id="e2e_complete_001",
            ),
            DebateTurnStartEvent(
                participant="Pro_Arguer", round_number=3, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Pro_Arguer",
                round_number=3,
                content_preview="Pro final argument",
                session_id="e2e_complete_001",
            ),
            DebateTurnStartEvent(
                participant="Con_Arguer", round_number=3, session_id="e2e_complete_001"
            ),
            DebateTurnCompleteEvent(
                participant="Con_Arguer",
                round_number=3,
                content_preview="Con final argument",
                session_id="e2e_complete_001",
            ),
        ]

        # Process all turn complete events through the tracker
        turn_events = [
            event
            for event in debate_events
            if isinstance(event, DebateTurnCompleteEvent)
        ]
        for turn_event in turn_events:
            asyncio.run(tracker.add_turn(turn_event))

        # 3. Complete the debate
        complete_event = DebateCompleteEvent(
            session_id="e2e_complete_001",
            summary="Complete workflow E2E test debate concluded with thorough discussion",  # noqa: E501
        )
        final_history = asyncio.run(tracker.complete_debate(complete_event))

        # 4. Verify complete workflow
        assert final_history.status == "completed"
        assert len(final_history.turns) == 9  # 3 rounds * 3 participants
        assert final_history.current_round == 3
        assert final_history.total_rounds == 3
        assert final_history.end_time is not None

        # Verify content preservation
        contents = [turn.content for turn in final_history.turns]
        assert "Pro argument round 1" in contents
        assert "Con argument round 1" in contents
        assert "Moderator summary round 1" in contents
        assert "Con argument round 2" in contents
        assert "Pro argument round 2" in contents
        assert "Pro final argument" in contents
        assert "Con final argument" in contents

    def test_container_integration_end_to_end(self):
        """Test complete container integration for enhanced debate features."""

        # Create a temporary config file for testing
        db_path = os.path.join(tempfile.mkdtemp(), "debate.db")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(f"""
database:
  path: '{db_path}'
llm_provider:
  default_model: "mock-model"
  embedding_model: "mock-embedding"
knowledge_base:
  directory: "./test_knowledge"
role_manager:
  roles_dir: "./test_roles"
wiki:
  pages_directory: "./test_wiki"
""")
            config_path = f.name

        try:
            # 1. Initialize container with config
            container = Container()
            container.config_manager.override(ConfigManager(config_path=config_path))

            # 2. Get all required services
            debate_history_tracker = container.debate_history_tracker()
            enhanced_debate_manager = container.enhanced_debate_manager()
            session_manager = container.session_manager()
            role_manager = container.role_manager()

            # 3. Verify all services are available
            assert debate_history_tracker is not None
            assert enhanced_debate_manager is not None
            assert session_manager is not None
            assert role_manager is not None

            # 4. Create a debate through the system
            start_event = DebateStartEvent(
                topic="Container Integration E2E Test",
                roles=["Test_Pro", "Test_Con"],
                rounds=2,
                session_id="container_e2e_002",
            )

            history = asyncio.run(debate_history_tracker.start_tracking(start_event))
            assert history.session_id == "container_e2e_002"
            assert len(history.participants) == 2

            # 5. Add debate content
            turn1 = DebateTurnCompleteEvent(
                participant="Test_Pro",
                round_number=1,
                content_preview="Pro argument in container system",
                session_id="container_e2e_002",
            )
            asyncio.run(debate_history_tracker.add_turn(turn1))

            turn2 = DebateTurnCompleteEvent(
                participant="Test_Con",
                round_number=1,
                content_preview="Con argument in container system",
                session_id="container_e2e_002",
            )
            updated_history = asyncio.run(debate_history_tracker.add_turn(turn2))

            # 6. Verify through the system
            assert len(updated_history.turns) == 2
            assert (
                updated_history.turns[0].content == "Pro argument in container system"
            )
            assert (
                updated_history.turns[1].content == "Con argument in container system"
            )

            # 7. Complete the debate
            complete_event = DebateCompleteEvent(
                session_id="container_e2e_002",
                summary="Container integration test completed successfully",
            )
            final_history = asyncio.run(
                debate_history_tracker.complete_debate(complete_event)
            )

            assert final_history.status == "completed"

        finally:
            # Clean up temp file
            os.unlink(config_path)

    def test_cli_tui_integration_e2e(self):
        """Test CLI and TUI integration through end-to-end scenario."""

        # This test simulates the integration between CLI commands, TUI display,
        # and the underlying debate management system

        tracker = DebateHistoryTracker(
            db_path=os.path.join(tempfile.mkdtemp(), "debate_history.db")
        )

        # Simulate a debate as it would occur through the system
        session_id = "cli_tui_e2e_003"

        # 1. Debate starts (as would happen from CLI command)
        start_event = DebateStartEvent(
            topic="CLI-TUI Integration Test",
            roles=["Advocate", "Skeptic"],
            rounds=2,
            session_id=session_id,
        )

        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.topic == "CLI-TUI Integration Test"

        # 2. Simulate debate turns (as would happen during debate execution)
        round1_events = [
            DebateTurnCompleteEvent(
                participant="Advocate",
                round_number=1,
                content_preview="Advocate's position statement",
                session_id=session_id,
            ),
            DebateTurnCompleteEvent(
                participant="Skeptic",
                round_number=1,
                content_preview="Skeptic's counter-argument",
                session_id=session_id,
            ),
        ]

        for event in round1_events:
            asyncio.run(tracker.add_turn(event))

        round2_events = [
            DebateTurnCompleteEvent(
                participant="Skeptic",
                round_number=2,
                content_preview="Skeptic's second argument",
                session_id=session_id,
            ),
            DebateTurnCompleteEvent(
                participant="Advocate",
                round_number=2,
                content_preview="Advocate's rebuttal",
                session_id=session_id,
            ),
        ]

        for event in round2_events:
            asyncio.run(tracker.add_turn(event))

        # 3. Complete debate (as would happen at the end)
        complete_event = DebateCompleteEvent(
            session_id=session_id,
            summary="Integration test debate completed with balanced discussion",
        )
        final_history = asyncio.run(tracker.complete_debate(complete_event))

        # 4. Verify the history is complete and accurate (as would be retrieved by TUI)
        assert final_history.status == "completed"
        assert len(final_history.turns) == 4  # 2 rounds * 2 participants
        assert final_history.total_rounds == 2

        # Verify turn content preservation
        participant_turns = {}
        for turn in final_history.turns:
            if turn.participant_name not in participant_turns:
                participant_turns[turn.participant_name] = []
            participant_turns[turn.participant_name].append(turn.content)

        assert "Advocate" in participant_turns
        assert "Skeptic" in participant_turns
        assert len(participant_turns["Advocate"]) == 2  # 2 turns
        assert len(participant_turns["Skeptic"]) == 2  # 2 turns

        contents = [turn.content for turn in final_history.turns]
        assert "Advocate's position statement" in contents
        assert "Skeptic's counter-argument" in contents
        assert "Skeptic's second argument" in contents
        assert "Advocate's rebuttal" in contents

    def test_multi_model_debate_end_to_end(self):
        """Test multi-model debate functionality end-to-end."""
        tracker = DebateHistoryTracker(
            db_path=os.path.join(tempfile.mkdtemp(), "debate_history.db")
        )

        # Simulate a multi-model debate scenario
        session_id = "multi_model_e2e_004"

        # Start debate with roles that might use different models
        start_event = DebateStartEvent(
            topic="Multi-Model Debate Test",
            roles=["GPT_Expert", "Claude_Analyst", "Gemini_Researcher"],
            rounds=2,
            session_id=session_id,
        )

        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.session_id == session_id
        assert len(history.participants) == 3

        # Add turns from different "models" (participants with different characteristics)  # noqa: E501
        model_turns = [
            # Round 1
            DebateTurnCompleteEvent(
                participant="GPT_Expert",
                round_number=1,
                content_preview="Expert analysis from GPT model",
                session_id=session_id,
            ),
            DebateTurnCompleteEvent(
                participant="Claude_Analyst",
                round_number=1,
                content_preview="Thoughtful analysis from Claude",
                session_id=session_id,
            ),
            DebateTurnCompleteEvent(
                participant="Gemini_Researcher",
                round_number=1,
                content_preview="Research-backed response from Gemini",
                session_id=session_id,
            ),
            # Round 2
            DebateTurnCompleteEvent(
                participant="Claude_Analyst",
                round_number=2,
                content_preview="Second analysis from Claude",
                session_id=session_id,
            ),
            DebateTurnCompleteEvent(
                participant="Gemini_Researcher",
                round_number=2,
                content_preview="Updated research from Gemini",
                session_id=session_id,
            ),
            DebateTurnCompleteEvent(
                participant="GPT_Expert",
                round_number=2,
                content_preview="Expert synthesis from GPT",
                session_id=session_id,
            ),
        ]

        for turn in model_turns:
            asyncio.run(tracker.add_turn(turn))

        # Complete the debate
        complete_event = DebateCompleteEvent(
            session_id=session_id,
            summary="Multi-model debate completed with diverse perspectives",
        )
        final_history = asyncio.run(tracker.complete_debate(complete_event))

        assert final_history.status == "completed"
        assert len(final_history.turns) == 6  # 2 rounds * 3 participants

        # Verify that each "model" participated appropriately
        model_participants = {turn.participant_name for turn in final_history.turns}
        assert model_participants == {
            "GPT_Expert",
            "Claude_Analyst",
            "Gemini_Researcher",
        }

        # Verify all turns have appropriate content
        for turn in final_history.turns:
            assert turn.content.startswith(
                (
                    "Expert",
                    "Thoughtful",
                    "Research",
                    "Second",
                    "Updated",
                    "Expert synthesis",
                )
            )

    def test_history_navigation_end_to_end(self):
        """Test complete history navigation workflow from creation to retrieval."""
        tracker = DebateHistoryTracker(
            db_path=os.path.join(tempfile.mkdtemp(), "debate_history.db")
        )

        # Create multiple debates to test navigation
        debates_data = [
            {
                "id": "nav_test_005a",
                "topic": "First Navigation Test",
                "roles": ["A", "B"],
                "rounds": 1,
                "turns": ["A1", "B1"],
            },
            {
                "id": "nav_test_005b",
                "topic": "Second Navigation Test",
                "roles": ["X", "Y", "Z"],
                "rounds": 2,
                "turns": ["X1", "Y1", "Z1", "Z2", "Y2", "X2"],
            },
            {
                "id": "nav_test_005c",
                "topic": "Third Navigation Test",
                "roles": ["P", "Q"],
                "rounds": 3,
                "turns": ["P1", "Q1", "Q2", "P2", "P3", "Q3"],
            },
        ]

        # Create all debates
        for debate_data in debates_data:
            start_event = DebateStartEvent(
                topic=debate_data["topic"],
                roles=debate_data["roles"],
                rounds=debate_data["rounds"],
                session_id=debate_data["id"],
            )
            asyncio.run(tracker.start_tracking(start_event))

            # Add turns for each debate
            for i, turn_content in enumerate(debate_data["turns"]):
                turn_event = DebateTurnCompleteEvent(
                    participant=debate_data["roles"][i % len(debate_data["roles"])],
                    round_number=(i % debate_data["rounds"]) + 1,
                    content_preview=turn_content,
                    session_id=debate_data["id"],
                )
                asyncio.run(tracker.add_turn(turn_event))

            # Complete each debate
            complete_event = DebateCompleteEvent(
                session_id=debate_data["id"],
                summary=f"Debate {debate_data['id']} completed",
            )
            asyncio.run(tracker.complete_debate(complete_event))

        # Test retrieving specific histories
        for debate_data in debates_data:
            retrieved_history = asyncio.run(tracker.get_history(debate_data["id"]))
            assert retrieved_history is not None
            assert retrieved_history.session_id == debate_data["id"]
            assert retrieved_history.topic == debate_data["topic"]
            assert len(retrieved_history.turns) == len(debate_data["turns"])
            assert retrieved_history.status == "completed"

        # Test retrieving all histories
        all_histories = asyncio.run(tracker.get_all_histories())
        assert len(all_histories) == 3

        retrieved_ids = {h.session_id for h in all_histories}
        expected_ids = {debate_data["id"] for debate_data in debates_data}
        assert retrieved_ids == expected_ids

        # Test that all turns are preserved correctly
        for history in all_histories:
            if history.session_id == "nav_test_005a":
                assert len(history.turns) == 2
                contents = [t.content for t in history.turns]
                assert "A1" in contents and "B1" in contents
            elif history.session_id == "nav_test_005b":
                assert len(history.turns) == 6
            elif history.session_id == "nav_test_005c":
                assert len(history.turns) == 6

    def test_enhanced_visualization_end_to_end(self):
        """Test end-to-end enhanced visualization workflow."""

        # Create an enhanced debate view with visualization features
        participants = [
            DebateParticipantView(
                name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0
            ),
            DebateParticipantView(
                name="Con_Arguer", color="#FFB6C1", symbol="👤", turn_order=1
            ),
            DebateParticipantView(
                name="Expert_Analyst", color="#98FB98", symbol="👤", turn_order=2
            ),
        ]

        enhanced_view = EnhancedDebateView(
            session_id="viz_e2e_006",
            topic="Enhanced Visualization E2E Test",
            participants=participants,
            current_round=1,
            total_rounds=3,
        )

        # Add debate turns to the view
        from daip_live.tui_v1.models.debate_view import DebateTurnView

        enhanced_view.history.extend(
            [
                DebateTurnView(
                    participant_name="Pro_Arguer",
                    content="Pro visualization argument",
                    round_number=1,
                    turn_in_round=1,
                    color="#87CEEB",
                ),
                DebateTurnView(
                    participant_name="Con_Arguer",
                    content="Con visualization argument",
                    round_number=1,
                    turn_in_round=2,
                    color="#FFB6C1",
                ),
                DebateTurnView(
                    participant_name="Expert_Analyst",
                    content="Expert visualization analysis",
                    round_number=1,
                    turn_in_round=3,
                    color="#98FB98",
                ),
                DebateTurnView(
                    participant_name="Pro_Arguer",
                    content="Pro second round argument",
                    round_number=2,
                    turn_in_round=1,
                    color="#87CEEB",
                ),
                DebateTurnView(
                    participant_name="Con_Arguer",
                    content="Con second round argument",
                    round_number=2,
                    turn_in_round=2,
                    color="#FFB6C1",
                ),
            ]
        )

        # Verify enhanced visualization features
        assert enhanced_view.session_id == "viz_e2e_006"
        assert enhanced_view.topic == "Enhanced Visualization E2E Test"
        assert len(enhanced_view.participants) == 3
        assert len(enhanced_view.history) == 5
        assert enhanced_view.current_round == 1  # Default from constructor
        assert enhanced_view.total_rounds == 3

        # Verify color assignments
        assert enhanced_view.color_scheme is not None
        participant_colors = enhanced_view.color_scheme["participant_colors"]
        assert "Pro_Arguer" in participant_colors
        assert "Con_Arguer" in participant_colors
        assert "Expert_Analyst" in participant_colors

        # Verify history has appropriate styling
        for turn in enhanced_view.history:
            assert turn.participant_name in [
                "Pro_Arguer",
                "Con_Arguer",
                "Expert_Analyst",
            ]
            assert turn.round_number in [1, 2]
            assert turn.color.startswith("#")  # Should be a color value

    def test_error_recovery_end_to_end(self):
        """Test end-to-end error recovery scenarios."""
        tracker = DebateHistoryTracker(
            db_path=os.path.join(tempfile.mkdtemp(), "debate_history.db")
        )

        # Test graceful handling of incomplete debates
        session_id = "error_recovery_007"

        # Start a debate
        start_event = DebateStartEvent(
            topic="Error Recovery Test",
            roles=["Participant_A", "Participant_B"],
            rounds=3,
            session_id=session_id,
        )
        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.session_id == session_id

        # Add some turns but don't complete the debate
        turn1 = DebateTurnCompleteEvent(
            participant="Participant_A",
            round_number=1,
            content_preview="First argument before error",
            session_id=session_id,
        )
        asyncio.run(tracker.add_turn(turn1))

        turn2 = DebateTurnCompleteEvent(
            participant="Participant_B",
            round_number=1,
            content_preview="Response before error",
            session_id=session_id,
        )
        updated_history = asyncio.run(tracker.add_turn(turn2))

        # Verify the incomplete state is preserved
        assert len(updated_history.turns) == 2
        assert updated_history.status == "active"  # Not completed
        assert updated_history.current_round == 1

        # Retrieve the incomplete debate later
        retrieved_history = asyncio.run(tracker.get_history(session_id))
        assert retrieved_history is not None
        assert retrieved_history.status == "active"
        assert len(retrieved_history.turns) == 2

        # Complete the debate after the "error" scenario
        remaining_turns = [
            DebateTurnCompleteEvent(
                participant="Participant_A",
                round_number=2,
                content_preview="Second round argument",
                session_id=session_id,
            ),
            DebateTurnCompleteEvent(
                participant="Participant_B",
                round_number=2,
                content_preview="Second round response",
                session_id=session_id,
            ),
        ]

        for turn in remaining_turns:
            asyncio.run(tracker.add_turn(turn))

        complete_event = DebateCompleteEvent(
            session_id=session_id,
            summary="Error recovery test completed successfully after partial state",
        )
        final_history = asyncio.run(tracker.complete_debate(complete_event))

        assert final_history.status == "completed"
        assert len(final_history.turns) == 4  # 2 original + 2 added later
        assert final_history.end_time is not None


if __name__ == "__main__":
    pytest.main([__file__])
