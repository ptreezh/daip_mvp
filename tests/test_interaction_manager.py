import unittest
from unittest.mock import MagicMock, patch

# As the actual modules do not exist yet, we define placeholder classes
# that mimic the expected interface for type hinting and `spec`ing in mocks.
class LLMInterface:
    def generate(self, prompt: str, **kwargs) -> str:
        pass

class MemoryService:
    def get_history(self) -> list:
        pass
    def save_message(self, role: str, content: str):
        pass

class WikiService:
    def search(self, query: str) -> list:
        pass

class SynthesisEngine:
    def synthesize_opinions(self, opinions: list, topic: str) -> str:
        pass

# This is the class we are testing. We will import it from the actual path once it's created.
# For now, we assume its structure for the test.
from src.kernel.interaction_manager import InteractionManager


class TestInteractionManager(unittest.TestCase):

    def setUp(self):
        """Set up mock dependencies for each test."""
        self.mock_llm = MagicMock(spec=LLMInterface)
        self.mock_memory = MagicMock(spec=MemoryService)
        self.mock_wiki = MagicMock(spec=WikiService)
        self.mock_synthesis = MagicMock(spec=SynthesisEngine)

        self.interaction_manager = InteractionManager(
            llm_interface=self.mock_llm,
            memory_service=self.mock_memory,
            knowledge_base=self.mock_wiki,
            synthesis_engine=self.mock_synthesis,
        )
        # Set a low token limit for easier testing of summarization logic
        self.interaction_manager.TOKEN_LIMIT = 100

    def test_simple_request_no_rag_no_summarization(self):
        """
        Tests a basic flow where context is not long and no RAG results are found.
        """
        # Arrange
        user_input = "Hello, how are you?"
        role_prompt = "You are a helpful assistant."
        self.mock_memory.get_history.return_value = [{"role": "user", "content": "Previous message"}]
        self.mock_wiki.search.return_value = []
        self.mock_llm.generate.return_value = "I am fine, thank you!"

        # Act
        response = self.interaction_manager.process_user_request(user_input, role_prompt)

        # Assert
        self.assertEqual(response, "I am fine, thank you!")
        self.mock_wiki.search.assert_called_once_with(user_input)
        self.mock_memory.get_history.assert_called_once()
        self.mock_synthesis.synthesize_opinions.assert_not_called()
        self.mock_llm.generate.assert_called_once()
        
        # Check that the final prompt was constructed correctly
        final_prompt_arg = self.mock_llm.generate.call_args[0][0]
        self.assertIn(role_prompt, final_prompt_arg)
        self.assertIn("Previous message", final_prompt_arg)
        self.assertIn(user_input, final_prompt_arg)
        self.assertNotIn("Relevant Knowledge", final_prompt_arg) # No RAG

        # Verify history was saved
        self.assertEqual(self.mock_memory.save_message.call_count, 2)

    def test_request_with_rag_retrieval(self):
        """
        Tests that RAG context is correctly retrieved and included in the prompt.
        """
        # Arrange
        user_input = "Tell me about project X."
        rag_context = "Project X is a secret project."
        self.mock_wiki.search.return_value = [rag_context]
        self.mock_memory.get_history.return_value = []
        self.mock_llm.generate.return_value = "Okay, I will tell you about Project X."

        # Act
        self.interaction_manager.process_user_request(user_input, "You are an assistant.")

        # Assert
        self.mock_wiki.search.assert_called_once_with(user_input)
        final_prompt_arg = self.mock_llm.generate.call_args[0][0]
        self.assertIn("Relevant Knowledge", final_prompt_arg)
        self.assertIn(rag_context, final_prompt_arg)

    @patch('src.kernel.interaction_manager.InteractionManager._calculate_token_count')
    def test_request_with_context_summarization(self, mock_token_count):
        """
        Tests that long context triggers the synthesis engine to summarize history.
        """
        # Arrange
        user_input = "One more thing."
        long_history = [{"role": "user", "content": "A very long previous conversation..."}]
        summarized_history = "In summary, we talked about a long conversation."
        
        self.mock_memory.get_history.return_value = long_history
        self.mock_wiki.search.return_value = []
        self.mock_synthesis.synthesize_opinions.return_value = summarized_history
        mock_token_count.return_value = 200  # Exceeds the TOKEN_LIMIT of 100

        # Act
        self.interaction_manager.process_user_request(user_input, "You are an assistant.")

        # Assert
        self.mock_synthesis.synthesize_opinions.assert_called_once()
        final_prompt_arg = self.mock_llm.generate.call_args[0][0]
        self.assertIn("Summarized Context", final_prompt_arg)
        self.assertIn(summarized_history, final_prompt_arg)
        self.assertNotIn("A very long previous conversation...", final_prompt_arg)

    def test_process_request_handles_no_history(self):
        """
        Tests that the manager works correctly on the very first message.
        """
        # Arrange
        user_input = "This is the first message."
        self.mock_memory.get_history.return_value = []
        self.mock_wiki.search.return_value = []
        self.mock_llm.generate.return_value = "Welcome!"

        # Act & Assert
        response = self.interaction_manager.process_user_request(user_input, "Role prompt")
        self.assertEqual(response, "Welcome!")
        self.mock_llm.generate.assert_called_once()


if __name__ == '__main__':
    unittest.main()