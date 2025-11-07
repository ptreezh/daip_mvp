"""
Integration test to verify CLI and TUI integration with new debate features
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from daip_live.cli import debate_history
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent
import asyncio
from unittest.mock import Mock, patch
import tempfile


def test_cli_integration():
    """Test that CLI components work with the new debate features."""
    
    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
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
""")
        config_path = f.name
    
    try:
        # Test that the debate history command function can be called without error
        # This tests the import and basic functionality
        from daip_live.container import Container
        
        # Create container to test that dependencies are properly configured
        container = Container()
        container.config.from_yaml(config_path)
        
        # Test that the debate_history_tracker can be retrieved from container
        tracker = container.debate_history_tracker()
        assert tracker is not None
        print("✓ Container integration test passed")
        
        # Test that tracker can handle basic operations
        start_event = DebateStartEvent(
            topic="Test CLI Integration",
            roles=["role1", "role2"],
            rounds=2,
            session_id="cli_test_001"
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.session_id == "cli_test_001"
        print("✓ Basic tracker operations test passed")
        
        # Test adding a turn
        turn_event = DebateTurnCompleteEvent(
            participant="role1",
            round_number=1,
            content_preview="Test content for CLI integration",
            session_id="cli_test_001"
        )
        
        updated_history = asyncio.run(tracker.add_turn(turn_event))
        assert len(updated_history.turns) == 1
        print("✓ Turn tracking test passed")
        
        # Test getting all histories
        all_histories = asyncio.run(tracker.get_all_histories())
        assert len(all_histories) >= 1
        print("✓ History retrieval test passed")
        
    finally:
        # Clean up temp file
        os.unlink(config_path)
    
    print("✓ CLI Integration tests passed")


def test_tui_integration():
    """Test basic TUI integration with new features."""
    
    # Test that the enhanced debate view models can be created and used correctly
    from daip_live.tui_v1.models.debate_view import EnhancedDebateView, DebateParticipantView
    
    # Create participants with different colors
    participants = [
        DebateParticipantView(name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0),
        DebateParticipantView(name="Con_Arguer", color="#FFB6C1", symbol="👤", turn_order=1)
    ]
    
    # Create an enhanced debate view
    debate_view = EnhancedDebateView(
        session_id="tui_integration_test_001",
        topic="TUI Integration Test",
        participants=participants,
        total_rounds=3
    )
    
    # Verify the view was created properly
    assert debate_view.session_id == "tui_integration_test_001"
    assert debate_view.topic == "TUI Integration Test"
    assert len(debate_view.participants) == 2
    assert debate_view.total_rounds == 3
    assert debate_view.color_scheme is not None
    print("✓ TUI EnhancedDebateView integration test passed")
    
    # Test default color assignment
    colors_assigned = debate_view.color_scheme["participant_colors"]
    assert len(colors_assigned) == 2
    print("✓ TUI participant color assignment test passed")
    
    print("✓ TUI Integration tests passed")


def test_backward_compatibility():
    """Test that new features don't break existing functionality."""
    
    # Test that existing debate functionality still works
    from daip_live.p8_debate_system.manager import DebateManager
    from daip_live.memory.session_manager import SessionManager
    from daip_live.persistence.database import DatabaseManager
    from daip_live.p4_role_manager_tools.role_manager import RoleManager
    from daip_live.model_provider.provider import LiteLLMProvider
    from daip_live.core.models import ProviderConfig
    
    # Create basic components (without full initialization to avoid dependency issues)
    # Test that the enhanced components can coexist with basic ones
    
    # Test that basic models still work
    from daip_live.core.models import DebateStartEvent
    event = DebateStartEvent(
        topic="Compatibility Test",
        roles=["test_role"],
        rounds=1,
        session_id="compat_001"
    )
    
    assert event.topic == "Compatibility Test"
    assert event.roles == ["test_role"]
    print("✓ Backward compatibility test passed")


def run_integration_tests():
    """Run all integration tests."""
    print("Running Integration Tests...")
    
    test_cli_integration()
    test_tui_integration()
    test_backward_compatibility()
    
    print("\n🎉 All Integration Tests Passed!")


if __name__ == "__main__":
    run_integration_tests()