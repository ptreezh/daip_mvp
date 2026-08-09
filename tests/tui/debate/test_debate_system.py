"""
DAIP Debate System Tests for newP6 TUI

This test suite implements TDD approach for debate system functionality.
Tests are written first (RED), then implementation follows (GREEN), then refactoring.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from daip_live.tui_v1.debate.argument import Argument

# Import real implementations (will fail initially - RED phase)
from daip_live.tui_v1.debate.debate import Debate
from daip_live.tui_v1.debate.debate_manager import DebateManager
from daip_live.tui_v1.debate.participant import DebateParticipant
from daip_live.tui_v1.debate.round import DebateRound


class TestDebate:
    """Test core debate functionality"""

    def test_debate_creation(self):
        """Test debate creation"""
        # This will fail initially - driving need for Debate class
        debate = Debate(
            topic="Should AI development be regulated?",
            description="A debate on AI regulation policies",
        )

        assert debate is not None
        assert debate.topic == "Should AI development be regulated?"
        assert debate.description == "A debate on AI regulation policies"
        assert debate.status == "preparing"
        assert hasattr(debate, "created_at")
        assert debate.participants == []
        assert debate.rounds == []

    def test_debate_initialization(self):
        """Test debate initialization with metadata"""
        debate = Debate(
            topic="AI in healthcare",
            description="Benefits and risks of AI in medical applications",
            max_participants=4,
            max_rounds=3,
        )

        assert debate.max_participants == 4
        assert debate.max_rounds == 3
        assert debate.current_round == 0
        assert not debate.is_active

    def test_debate_add_participant(self):
        """Test adding participants to debate"""
        debate = Debate("Test topic", "Test description")
        participant = Mock(spec=DebateParticipant)
        participant.id = "participant1"
        participant.name = "Test Participant"

        debate.add_participant(participant)

        assert len(debate.participants) == 1
        assert participant in debate.participants

    def test_debate_remove_participant(self):
        """Test removing participants from debate"""
        debate = Debate("Test topic", "Test description")
        participant = Mock(spec=DebateParticipant)
        participant.id = "participant1"
        participant.name = "Test Participant"

        debate.add_participant(participant)
        assert len(debate.participants) == 1

        debate.remove_participant("participant1")
        assert len(debate.participants) == 0

    def test_debate_start(self):
        """Test starting a debate"""
        debate = Debate("Test topic", "Test description")
        participant1 = Mock(spec=DebateParticipant)
        participant2 = Mock(spec=DebateParticipant)
        participant1.id = "p1"
        participant1.name = "Participant 1"
        participant2.id = "p2"
        participant2.name = "Participant 2"

        debate.add_participant(participant1)
        debate.add_participant(participant2)

        success = debate.start()

        assert success
        assert debate.status == "active"
        assert debate.is_active
        assert debate.current_round == 1

    def test_debate_start_insufficient_participants(self):
        """Test starting debate with insufficient participants"""
        debate = Debate("Test topic", "Test description")
        participant = Mock(spec=DebateParticipant)
        participant.id = "p1"
        participant.name = "Single Participant"

        debate.add_participant(participant)

        success = debate.start()

        assert not success
        assert debate.status == "preparing"
        assert not debate.is_active

    def test_debate_end(self):
        """Test ending a debate"""
        debate = Debate("Test topic", "Test description")
        debate.start()  # Start first

        debate.end()

        assert debate.status == "completed"
        assert not debate.is_active
        assert debate.ended_at is not None

    def test_debate_get_summary(self):
        """Test getting debate summary"""
        debate = Debate("Test topic", "Test description")
        debate.start()
        debate.end()

        summary = debate.get_summary()

        assert "Test topic" in summary
        assert "Test description" in summary
        assert "completed" in summary


class TestDebateParticipant:
    """Test debate participant functionality"""

    def test_participant_creation(self):
        """Test participant creation"""
        from daip_live.tui_v1.debate.roles import RoleType

        # This will fail initially - driving need for DebateParticipant class
        participant = DebateParticipant(
            name="AI Expert", role=RoleType.PROPONENT, model="gpt-4"
        )

        assert participant is not None
        assert participant.name == "AI Expert"
        assert participant.role == RoleType.PROPONENT
        assert participant.model == "gpt-4"
        assert participant.arguments == []

    def test_participant_add_argument(self):
        """Test adding argument to participant"""
        from daip_live.tui_v1.debate.roles import RoleType

        participant = DebateParticipant("Expert", RoleType.PROPONENT, "gpt-4")
        argument = Argument(participant.id, "Test argument", "proponent")

        participant.add_argument(argument)

        assert len(participant.arguments) == 1
        assert argument in participant.arguments

    def test_participant_get_position(self):
        """Test getting participant position"""
        from daip_live.tui_v1.debate.roles import RoleType

        participant = DebateParticipant("Expert", RoleType.PROPONENT, "gpt-4")

        position = participant.get_position()

        assert "proponent" in position.lower()

    @pytest.mark.asyncio
    async def test_participant_generate_argument(self):
        """Test generating argument for participant"""
        from daip_live.tui_v1.debate.roles import RoleType

        participant = DebateParticipant("Expert", RoleType.PROPONENT, "gpt-4")
        participant.model_service = Mock()
        participant.model_service.generate_response = AsyncMock(
            return_value={
                "content": "AI should be regulated to ensure safety",
                "tokens": 150,
                "reasoning": "Based on ethical considerations",
            }
        )

        topic = "Should AI be regulated?"
        context = {"round": 1, "previous_arguments": []}

        argument = await participant.generate_argument(topic, context)

        assert argument is not None
        assert "AI should be regulated" in argument.content
        assert argument.participant_id == participant.id


class TestArgument:
    """Test argument functionality"""

    def test_argument_creation(self):
        """Test argument creation"""
        # This will fail initially - driving need for Argument class
        argument = Argument(
            participant_id="expert1",
            content="AI regulation is necessary for safety",
            position="proponent",
        )

        assert argument is not None
        assert argument.participant_id == "expert1"
        assert argument.content == "AI regulation is necessary for safety"
        assert argument.position == "proponent"
        assert hasattr(argument, "created_at")
        assert argument.score is None

    def test_argument_add_rebuttal(self):
        """Test adding rebuttal to argument"""
        argument = Argument("p1", "Original argument", "proponent")
        rebuttal = Mock(spec=Argument)
        rebuttal.id = "rebuttal1"

        argument.add_rebuttal(rebuttal)

        assert len(argument.rebuttals) == 1
        assert rebuttal in argument.rebuttals

    def test_argument_evaluate(self):
        """Test argument evaluation"""
        argument = Argument("p1", "Test argument", "proponent")
        argument.evaluate(8.5, "Well-reasoned and comprehensive")

        assert argument.score == 8.5
        assert argument.evaluation == "Well-reasoned and comprehensive"
        assert argument.evaluated_at is not None


class TestDebateRound:
    """Test debate round functionality"""

    def test_round_creation(self):
        """Test round creation"""
        # This will fail initially - driving need for DebateRound class
        round = DebateRound(
            round_number=1,
            topic="Should AI be regulated?",
            max_arguments_per_participant=2,
        )

        assert round is not None
        assert round.round_number == 1
        assert round.topic == "Should AI be regulated?"
        assert round.max_arguments_per_participant == 2
        assert round.arguments == []
        assert round.status == "active"

    def test_round_add_argument(self):
        """Test adding argument to round"""
        round = DebateRound(1, "Test topic", 2)
        argument = Mock(spec=Argument)
        argument.participant_id = "p1"
        argument.id = "arg1"

        success = round.add_argument(argument)

        assert success
        assert len(round.arguments) == 1
        assert argument in round.arguments

    def test_round_max_arguments_reached(self):
        """Test max arguments per participant limit"""
        round = DebateRound(1, "Test topic", 1)
        participant_id = "p1"

        argument1 = Mock(spec=Argument)
        argument1.participant_id = participant_id
        argument1.id = "arg1"
        argument2 = Mock(spec=Argument)
        argument2.participant_id = participant_id
        argument2.id = "arg2"

        round.add_argument(argument1)
        success = round.add_argument(argument2)

        assert not success
        assert len(round.arguments) == 1

    def test_round_complete(self):
        """Test completing a round"""
        round = DebateRound(1, "Test topic", 2)
        argument = Mock(spec=Argument)
        argument.participant_id = "p1"
        argument.id = "arg1"
        round.add_argument(argument)

        round.complete()

        assert round.status == "completed"
        assert round.completed_at is not None

    def test_round_get_summary(self):
        """Test getting round summary"""
        round = DebateRound(1, "Test topic", 2)
        argument = Argument("p1", "Test argument", "proponent")
        argument.id = "arg1"
        round.add_argument(argument)

        summary = round.get_summary()

        assert "Test topic" in summary
        assert "Arguments: 1" in summary
        assert "p1: 1 arguments" in summary
        assert "1" in summary  # round number


class TestDebateManager:
    """Test debate manager functionality"""

    def test_debate_manager_creation(self):
        """Test debate manager creation"""
        # This will fail initially - driving need for DebateManager class
        manager = DebateManager()

        assert manager is not None
        assert manager.debates == []
        assert hasattr(manager, "_debate_id_counter")

    def test_create_debate(self):
        """Test creating a new debate"""
        manager = DebateManager()

        debate = manager.create_debate(
            topic="Should AI be regulated?",
            description="Regulation debate",
            max_participants=4,
        )

        assert debate is not None
        assert debate.topic == "Should AI be regulated?"
        assert debate.id is not None
        assert len(manager.debates) == 1

    def test_get_debate(self):
        """Test retrieving debate by ID"""
        manager = DebateManager()
        debate = manager.create_debate("Test topic", "Test description")

        retrieved = manager.get_debate(debate.id)

        assert retrieved == debate

    def test_get_nonexistent_debate(self):
        """Test retrieving non-existent debate"""
        manager = DebateManager()

        result = manager.get_debate("nonexistent")

        assert result is None

    def test_list_debates(self):
        """Test listing all debates"""
        manager = DebateManager()
        manager.create_debate("Topic 1", "Description 1")
        manager.create_debate("Topic 2", "Description 2")

        debates = manager.list_debates()

        assert len(debates) == 2
        assert debates[0].topic == "Topic 1"
        assert debates[1].topic == "Topic 2"

    def test_delete_debate(self):
        """Test deleting a debate"""
        manager = DebateManager()
        debate = manager.create_debate("Test topic", "Test description")

        success = manager.delete_debate(debate.id)

        assert success
        assert len(manager.debates) == 0

    def test_delete_nonexistent_debate(self):
        """Test deleting non-existent debate"""
        manager = DebateManager()

        success = manager.delete_debate("nonexistent")

        assert not success

    @pytest.mark.asyncio
    async def test_start_debate(self):
        """Test starting a debate through manager"""
        manager = DebateManager()
        debate = manager.create_debate("Test topic", "Test description")

        # Add mock participants
        participant1 = Mock(spec=DebateParticipant)
        participant2 = Mock(spec=DebateParticipant)
        participant1.id = "p1"
        participant1.name = "Participant 1"
        participant2.id = "p2"
        participant2.name = "Participant 2"
        debate.add_participant(participant1)
        debate.add_participant(participant2)

        success = await manager.start_debate(debate.id)

        assert success
        assert debate.status == "active"

    @pytest.mark.asyncio
    async def test_execute_debate_round(self):
        """Test executing a debate round"""

        manager = DebateManager()
        debate = manager.create_debate("Test topic", "Test description")

        # Setup participants - need at least 2 for debate to start
        participant1 = Mock(spec=DebateParticipant)
        participant1.id = "p1"
        participant1.name = "Test Participant 1"
        participant1.role = Mock()
        participant1.role.value = "proponent"
        participant1.generate_argument = AsyncMock(return_value=Mock(spec=Argument))

        participant2 = Mock(spec=DebateParticipant)
        participant2.id = "p2"
        participant2.name = "Test Participant 2"
        participant2.role = Mock()
        participant2.role.value = "opponent"
        participant2.generate_argument = AsyncMock(return_value=Mock(spec=Argument))

        debate.add_participant(participant1)
        debate.add_participant(participant2)

        debate.start()

        round_result = await manager.execute_round(debate.id, 1)

        assert round_result is not None
        assert round_result.status == "completed"

    @pytest.mark.asyncio
    async def test_get_debate_statistics(self):
        """Test getting debate statistics"""
        manager = DebateManager()
        debate = manager.create_debate("Test topic", "Test description")
        debate.start()
        debate.end()

        stats = await manager.get_debate_statistics(debate.id)

        assert "total_arguments" in stats
        assert "actual_participants" in stats  # Use actual field name
        # duration_seconds is only included if debate was started and has valid timing
        assert stats["actual_participants"] == 0  # No actual participants in this test


class TestDebateRoles:
    """Test debate role configurations"""

    def test_role_creation(self):
        """Test creating debate roles"""
        # This will fail initially - driving need for role system
        from daip_live.tui_v1.debate.roles import DebateRole, RoleType

        proponent = DebateRole(
            name="Technology Optimist",
            role_type=RoleType.PROPONENT,
            description="Advocates for technological progress",
            model="gpt-4",
            system_prompt="You are a technology optimist...",
        )

        assert proponent is not None
        assert proponent.name == "Technology Optimist"
        assert proponent.role_type == RoleType.PROPONENT

    def test_role_configuration(self):
        """Test role configuration"""
        from daip_live.tui_v1.debate.roles import DebateRole, RoleType

        skeptic = DebateRole(
            name="AI Skeptic",
            role_type=RoleType.OPPONENT,
            description="Questions AI safety and ethics",
            model="claude-3",
            system_prompt="You are skeptical about AI development...",
        )

        config = skeptic.get_configuration()

        assert "AI Skeptic" in config["name"]
        assert "claude-3" in config["model"]
        assert "skeptical" in config["system_prompt"].lower()

    def test_role_validation(self):
        """Test role validation"""
        from daip_live.tui_v1.debate.roles import DebateRole, RoleType

        # Valid role
        valid_role = DebateRole(
            "Test", RoleType.PROPONENT, "Test", "gpt-4", "Test prompt"
        )
        assert valid_role.is_valid()

        # Invalid role (missing system prompt)
        invalid_role = DebateRole("Test", RoleType.PROPONENT, "Test", "gpt-4", "")
        assert not invalid_role.is_valid()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
