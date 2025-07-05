import unittest
from unittest.mock import MagicMock, patch

from src.kernel.llm_interface import (
    LLMConfig,
    LLMFactory,
    OllamaInterface,
    OpenAIInterface,
)


class TestLLMFactory(unittest.TestCase):
    def test_create_openai_interface(self):
        """Tests that the factory correctly creates an OpenAIInterface."""
        config = LLMConfig(provider="openai", model="gpt-4")
        interface = LLMFactory.create(config)
        self.assertIsInstance(interface, OpenAIInterface)

    def test_create_ollama_interface(self):
        """Tests that the factory correctly creates an OllamaInterface."""
        config = LLMConfig(provider="ollama", model="llama3")
        interface = LLMFactory.create(config)
        self.assertIsInstance(interface, OllamaInterface)

    def test_create_unsupported_provider_raises_error(self):
        """Tests that the factory raises a ValueError for an unknown provider."""
        config = LLMConfig(provider="unsupported_provider", model="test")
        with self.assertRaises(ValueError):
            LLMFactory.create(config)


class TestOpenAIInterface(unittest.TestCase):
    def setUp(self):
        self.config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key="test_key",
            temperature=0.5,
            max_tokens=100,
        )

    @patch("src.kernel.llm_interface.OpenAI")
    def test_generate(self, mock_openai_class):
        """Tests the non-streaming generate method for OpenAI."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock the response from the API
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Hello, world!"
        mock_client.chat.completions.create.return_value = mock_completion

        interface = OpenAIInterface(self.config)
        response = interface.generate("Say hi")

        self.assertEqual(response, "Hello, world!")
        mock_client.chat.completions.create.assert_called_once_with(
            model=self.config.model,
            messages=[{"role": "user", "content": "Say hi"}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=False,
        )

    @patch("src.kernel.llm_interface.OpenAI")
    def test_generate_stream(self, mock_openai_class):
        """Tests the streaming generate_stream method for OpenAI."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock the streaming response
        mock_chunk1 = MagicMock()
        mock_chunk1.choices[0].delta.content = "Hello,"
        mock_chunk2 = MagicMock()
        mock_chunk2.choices[0].delta.content = " world!"
        mock_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2]

        interface = OpenAIInterface(self.config)
        stream = interface.generate_stream("Say hi")
        response_parts = list(stream)

        self.assertEqual(response_parts, ["Hello,", " world!"])
        mock_client.chat.completions.create.assert_called_once_with(
            model=self.config.model,
            messages=[{"role": "user", "content": "Say hi"}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
        )


class TestOllamaInterface(unittest.TestCase):
    def setUp(self):
        self.config = LLMConfig(
            provider="ollama", model="llama3", base_url="http://localhost:11434"
        )

    @patch("src.kernel.llm_interface.ollama.Client")
    def test_generate(self, mock_ollama_client_class):
        """Tests the non-streaming generate method for Ollama."""
        mock_client = MagicMock()
        mock_ollama_client_class.return_value = mock_client
        mock_client.chat.return_value = {"message": {"content": "Ollama says hi"}}

        interface = OllamaInterface(self.config)
        response = interface.generate("Say hi")

        self.assertEqual(response, "Ollama says hi")
        mock_client.chat.assert_called_once()
        call_args = mock_client.chat.call_args
        self.assertEqual(call_args.kwargs["model"], self.config.model)
        self.assertFalse(call_args.kwargs["stream"])

    @patch("src.kernel.llm_interface.ollama.Client")
    def test_generate_stream(self, mock_ollama_client_class):
        """Tests the streaming generate_stream method for Ollama."""
        mock_client = MagicMock()
        mock_ollama_client_class.return_value = mock_client

        # Mock the streaming response
        mock_client.chat.return_value = [
            {"message": {"content": "Ollama"}},
            {"message": {"content": " says"}},
            {"message": {"content": " hi"}},
        ]

        interface = OllamaInterface(self.config)
        stream = interface.generate_stream("Say hi")
        response_parts = list(stream)

        self.assertEqual(response_parts, ["Ollama", " says", " hi"])
        mock_client.chat.assert_called_once()
        call_args = mock_client.chat.call_args
        self.assertTrue(call_args.kwargs["stream"])


if __name__ == "__main__":
    unittest.main()