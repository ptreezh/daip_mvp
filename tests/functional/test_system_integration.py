"""
Quick system verification test to ensure all enhanced features work correctly.
"""

import asyncio
import os
import tempfile

from daip_live.container import Container
from daip_live.core.models import (
    DebateCompleteEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
)
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker


def test_all_enhanced_features():
    """Test all the enhanced features work together."""

    # Test 1: Create DebateHistoryTracker and verify it works
    tracker = DebateHistoryTracker()

    # Test 2: Start a sample debate
    start_event = DebateStartEvent(
        topic="Enhanced Features Test Debate",
        roles=["Pro_Enhanced", "Con_Enhanced", "Mod_Enhanced"],
        rounds=2,
        session_id="enhancement_test_001",
    )

    history = asyncio.run(tracker.start_tracking(start_event))
    assert history.session_id == "enhancement_test_001"
    assert len(history.participants) == 3

    # Test 3: Add turns to the debate
    turns = [
        DebateTurnCompleteEvent(
            participant="Pro_Enhanced",
            round_number=1,
            content_preview="Pro argument with enhanced features",
            session_id="enhancement_test_001",
        ),
        DebateTurnCompleteEvent(
            participant="Con_Enhanced",
            round_number=1,
            content_preview="Con argument with enhanced features",
            session_id="enhancement_test_001",
        ),
        DebateTurnCompleteEvent(
            participant="Mod_Enhanced",
            round_number=1,
            content_preview="Moderator summary",
            session_id="enhancement_test_001",
        ),
        DebateTurnCompleteEvent(
            participant="Con_Enhanced",
            round_number=2,
            content_preview="Con response in second round",
            session_id="enhancement_test_001",
        ),
        DebateTurnCompleteEvent(
            participant="Pro_Enhanced",
            round_number=2,
            content_preview="Pro response in second round",
            session_id="enhancement_test_001",
        ),
    ]

    for turn in turns:
        asyncio.run(tracker.add_turn(turn))

    # Test 4: Complete the debate
    complete_event = DebateCompleteEvent(
        session_id="enhancement_test_001",
        summary="Enhanced features test debate completed successfully",
    )
    final_history = asyncio.run(tracker.complete_debate(complete_event))

    assert final_history.status == "completed"
    assert len(final_history.turns) == 5

    # Test 5: Retrieve the debate history
    retrieved_history = asyncio.run(tracker.get_history("enhancement_test_001"))
    assert retrieved_history is not None
    assert retrieved_history.session_id == "enhancement_test_001"
    assert len(retrieved_history.turns) == 5

    # Test 6: Get all histories
    all_histories = asyncio.run(tracker.get_all_histories())
    assert len(all_histories) >= 1

    # Test 7: Test with Container integration
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""
database:
  path: ":memory:"
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
        container = Container()
        # 源码权威: Container 无 config 属性，用 config_manager provider 覆盖
        from daip_live.config import ConfigManager

        container.config_manager.override(ConfigManager(config_path))

        debate_history_tracker = container.debate_history_tracker()
        assert debate_history_tracker is not None

        # Quick test with container-provided tracker
        container_session = "container_integration_test"
        start_event = DebateStartEvent(
            topic="Container Integration Test",
            roles=["Container_Test_Role"],
            rounds=1,
            session_id=container_session,
        )
        container_history = asyncio.run(
            debate_history_tracker.start_tracking(start_event)
        )
        assert container_history.session_id == container_session

        # Add turn and complete
        turn_event = DebateTurnCompleteEvent(
            participant="Container_Test_Role",
            round_number=1,
            content_preview="Container integration content",
            session_id=container_session,
        )
        asyncio.run(debate_history_tracker.add_turn(turn_event))

        complete_event = DebateCompleteEvent(
            session_id=container_session, summary="Container integration test completed"
        )
        final_container_history = asyncio.run(
            debate_history_tracker.complete_debate(complete_event)
        )
        assert final_container_history.status == "completed"

    finally:
        os.unlink(config_path)

    # Test 8: Test EnhancedDebateView creation
    from daip_live.tui_v1.models.debate_view import (
        DebateParticipantView,
        EnhancedDebateView,
    )

    participants = [
        DebateParticipantView(
            name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0
        ),
        DebateParticipantView(
            name="Con_Arguer", color="#FFB6C1", symbol="👤", turn_order=1
        ),
    ]

    enhanced_view = EnhancedDebateView(
        session_id="enhanced_view_test",
        topic="Enhanced Visualization Test",
        participants=participants,
        total_rounds=2,
    )

    assert enhanced_view.session_id == "enhanced_view_test"
    assert len(enhanced_view.participants) == 2
    assert enhanced_view.total_rounds == 2

    return True


if __name__ == "__main__":
    success = test_all_enhanced_features()
    if success:
        pass
    else:
        pass
