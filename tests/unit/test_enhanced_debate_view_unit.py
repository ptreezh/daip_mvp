"""
Unit Tests for EnhancedDebateView model
"""
import pytest
from daip_live.tui_v1.models.debate_view import EnhancedDebateView, DebateParticipantView, DebateTurnView


class TestEnhancedDebateViewUnit:
    """Unit tests for EnhancedDebateView model."""
    
    def test_enhanced_debate_view_creation(self):
        """Test EnhancedDebateView model creation with required fields."""
        participant = DebateParticipantView(name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0)
        
        view = EnhancedDebateView(
            session_id="test_session_123",
            topic="Sample Debate Topic",
            participants=[participant],
            total_rounds=3
        )
        
        assert view.session_id == "test_session_123"
        assert view.topic == "Sample Debate Topic"
        assert view.total_rounds == 3
        assert len(view.participants) == 1
        assert view.status == "active"
        assert view.current_round == 1
        assert view.color_scheme is not None
        assert "background" in view.color_scheme
    
    def test_enhanced_debate_view_default_values(self):
        """Test EnhancedDebateView model with default values."""
        view = EnhancedDebateView(
            session_id="default_session",
            topic="Default Test",
            participants=[]
        )
        
        assert view.session_id == "default_session"
        assert view.topic == "Default Test"
        assert view.participants == []
        assert view.current_turn is None
        assert view.status == "active"
        assert view.color_scheme is not None
    
    def test_enhanced_debate_view_color_assignment(self):
        """Test that participant colors are properly assigned."""
        participants = [
            DebateParticipantView(name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0),
            DebateParticipantView(name="Con_Arguer", color="#FFB6C1", symbol="👤", turn_order=1)
        ]
        
        view = EnhancedDebateView(
            session_id="color_test",
            topic="Color Assignment Test",
            participants=participants
        )
        
        # Check that default participant colors are assigned
        color_scheme = view.color_scheme
        assert "participant_colors" in color_scheme
        participant_names = [p.name for p in participants]
        assigned_colors = color_scheme["participant_colors"]
        
        for name in participant_names:
            assert name in assigned_colors
            assert assigned_colors[name].startswith("#")  # Should be a hex color
    
    def test_debate_participant_view_creation(self):
        """Test DebateParticipantView model creation."""
        participant = DebateParticipantView(
            name="Test_Pro", 
            color="#FF0000", 
            symbol="🔵",
            turn_order=1
        )
        
        assert participant.name == "Test_Pro"
        assert participant.color == "#FF0000"
        assert participant.symbol == "🔵"
        assert participant.turn_order == 1
    
    def test_debate_turn_view_creation(self):
        """Test DebateTurnView model creation."""
        from datetime import datetime
        turn = DebateTurnView(
            participant_name="Con_Arguer",
            content="My counter argument",
            round_number=2,
            turn_in_round=1
        )
        
        assert turn.participant_name == "Con_Arguer"
        assert turn.content == "My counter argument"
        assert turn.round_number == 2
        assert turn.turn_in_round == 1
        assert turn.timestamp is not None  # Should be set to current time
        assert turn.color == "#FFFFFF"  # Default color
    
    def test_debate_turn_view_custom_color(self):
        """Test DebateTurnView with custom color."""
        turn = DebateTurnView(
            participant_name="Pro_Arguer",
            content="Test argument",
            round_number=1,
            turn_in_round=1,
            color="#00FF00"
        )
        
        assert turn.color == "#00FF00"
    
    def test_debate_participant_view_defaults(self):
        """Test DebateParticipantView with default values."""
        participant = DebateParticipantView(name="Default_Test")
        
        assert participant.name == "Default_Test"
        assert participant.color == "#87CEEB"  # Default color
        assert participant.symbol == "👤"  # Default symbol
        assert participant.turn_order == 0  # Default order


if __name__ == "__main__":
    pytest.main([__file__])