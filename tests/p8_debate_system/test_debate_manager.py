import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, call

from src.daip_live.p8_debate_system.manager import DebateManager
from src.daip_live.core.models import Session, Role, DialogueTurn, AgentState
from src.daip_live.memory.session_manager import SessionManager
from src.daip_live.p4_role_manager_tools.role_manager import RoleManager
from src.daip_live.model_provider.provider import LiteLLMProvider


class TestDebateManager(unittest.TestCase):

    def setUp(self):
        self.mock_session_manager = MagicMock(spec=SessionManager)
        self.mock_role_manager = MagicMock(spec=RoleManager)
        self.mock_model_provider = MagicMock(spec=LiteLLMProvider)

        self.debate_manager = DebateManager(
            session_manager=self.mock_session_manager,
            role_manager=self.mock_role_manager,
            model_provider=self.mock_model_provider
        )

    def test_debate_lifecycle(self):
        """Test the full lifecycle of a debate."""
        async def run_test():
            # Arrange
            topic = "Should AI be regulated?"
            roles = ["pro_arguer", "con_arguer"]
            num_rounds = 2

            # Mock roles
            pro_role = Role(name="pro_arguer", persona="Pro AI", tools=[])
            con_role = Role(name="con_arguer", persona="Con AI", tools=[])
            self.mock_role_manager.get_role_by_name.side_effect = [pro_role, con_role]

            # Mock session creation
            mock_session = Session(goal=topic, session_type="debate", participant_ids=roles)
            self.mock_session_manager.create_session.return_value = mock_session

            # Mock model provider responses
            self.mock_model_provider.generate = AsyncMock(side_effect=[
                "Pro argument 1", "Con argument 1",
                "Pro argument 2", "Con argument 2",
                "Final summary of the debate."
            ])

            # Act
            final_session = await self.debate_manager.run_debate(
                topic=topic, 
                roles_names=roles, 
                num_rounds=num_rounds
            )

            # Assert
            self.mock_session_manager.create_session.assert_called_once_with(
                goal=topic, session_type="debate", participant_ids=roles
            )
            self.mock_role_manager.get_role_by_name.assert_has_calls([
                call("pro_arguer"), call("con_arguer")
            ])
            self.assertEqual(self.mock_model_provider.generate.call_count, 5)
            self.assertEqual(final_session.status, AgentState.COMPLETED)
            self.assertEqual(len(final_session.history), 4)
            self.assertEqual(final_session.history[0].content, "Pro argument 1")
            self.assertEqual(final_session.history[3].content, "Con argument 2")
            self.assertEqual(final_session.summary, "Final summary of the debate.")
            self.mock_session_manager.save_session.assert_called_once_with(final_session)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
