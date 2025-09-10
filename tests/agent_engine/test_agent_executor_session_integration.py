import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from src.daip_live.agent_engine.executor import AgentExecutor
from src.daip_live.core.models import AgentState, Session
from src.daip_live.memory.service import MemoryService
from src.daip_live.memory.session_manager import SessionManager


class TestAgentExecutorSessionIntegration(unittest.TestCase):

    def setUp(self):
        self.mock_session_manager = MagicMock(spec=SessionManager)
        self.mock_memory_service = MagicMock(spec=MemoryService)
        self.mock_model_provider = MagicMock()
        self.mock_tool_manager = MagicMock()
        self.mock_knowledge_manager = MagicMock()
        self.user_input_queue = asyncio.Queue()

        self.agent_executor = AgentExecutor(
            session_manager=self.mock_session_manager,
            memory_service=self.mock_memory_service,
            model_provider=self.mock_model_provider,
            tool_manager=self.mock_tool_manager,
            knowledge_manager=self.mock_knowledge_manager,
            user_input_queue=self.user_input_queue
        )

    def test_session_creation_and_saving_on_simple_run(self):
        """Verify a session is created, populated, and saved during a simple run that just responds."""
        async def run_test():
            # Arrange
            goal = "A simple goal"
            final_llm_response = "Confidence: 1.0\nFinal Answer: All done."
            prompt = "Generated Prompt"

            self.mock_memory_service.construct_prompt.return_value = prompt
            self.mock_model_provider.generate = AsyncMock(return_value=final_llm_response)

            mock_session = Session(goal=goal, session_type="workflow", participant_ids=["agent", "system"])
            self.mock_session_manager.create_session.return_value = mock_session

            # Act
            async for _ in self.agent_executor.run(goal):
                pass

            # Assert
            self.mock_memory_service.construct_prompt.assert_called_once()
            self.mock_session_manager.create_session.assert_called_once_with(
                goal=goal, session_type="workflow", participant_ids=["agent", "system"]
            )
            self.mock_session_manager.save_session.assert_called_once()
            saved_session_arg = self.mock_session_manager.save_session.call_args[0][0]

            self.assertIsInstance(saved_session_arg, Session)
            self.assertEqual(saved_session_arg.status, AgentState.COMPLETED)
            self.assertEqual(saved_session_arg.summary, "Final Answer: All done.")
            self.assertEqual(len(saved_session_arg.history), 1)
            self.assertEqual(saved_session_arg.history[0].participant_id, "agent")
            self.assertEqual(saved_session_arg.history[0].content, final_llm_response)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
