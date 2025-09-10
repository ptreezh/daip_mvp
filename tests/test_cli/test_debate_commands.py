import asyncio
import unittest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from src.daip_live.cli import app
from src.daip_live.core.models import Session, AgentState

runner = CliRunner()

class TestDebateCommands(unittest.TestCase):

    @patch("src.daip_live.cli.DebateManager")
    @patch("src.daip_live.cli.config_manager")
    def test_debate_start_command(self, mock_config_manager, mock_debate_manager):
        """Test the 'debate start' command."""
        # Arrange
        mock_cfg = MagicMock()
        mock_cfg.database.path = ":memory:"
        mock_cfg.llm_provider.default_model = "mock-model"
        mock_config_manager.get_config.return_value = mock_cfg

        mock_final_session = Session(
            session_id="debate_sess_1",
            goal="Test Topic",
            session_type="debate",
            status=AgentState.COMPLETED,
            participant_ids=["pro_arguer", "con_arguer"],
            summary="A great debate."
        )
        instance = mock_debate_manager.return_value
        instance.run_debate.return_value = mock_final_session

        # Act
        with patch("src.daip_live.cli.asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.side_effect = lambda coro: coro.send(None) if hasattr(coro, 'send') else coro
            result = runner.invoke(app, ["debate", "start", "Test Topic", "--roles", "pro_arguer,con_arguer", "--rounds", "1"])

        # Assert
        self.assertEqual(result.exit_code, 0)
        instance.run_debate.assert_called_once()
        self.assertIn("Debate finished.", result.stdout)
        self.assertIn("debate_sess_1", result.stdout)
        self.assertIn("A great debate.", result.stdout)

if __name__ == '__main__':
    unittest.main()
