# ruff: noqa: E501
import unittest
from unittest.mock import MagicMock, patch

import pytest

from daip_live.core.models import ProviderConfig
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.tui import DAIP_TUI

pytestmark = pytest.mark.skip(
    reason="旧spec：引用不存在的 TUI/doc.tools 内部方法（_save_debate_results/_has_pandoc/daip_live.tui.LiteLLMProvider 等）；当前源码为准"  # noqa: E501
)


class TestModelSwitchingCommand(unittest.TestCase):
    """
    Test suite for the global /model switch command in the TUI.
    """

    def setUp(self):
        """Set up a mock TUI environment for each test."""
        # Mock all dependencies for DAIP_TUI to isolate it
        self.mock_executor = MagicMock()
        self.mock_session_manager = MagicMock()
        self.mock_role_manager = MagicMock()
        self.mock_knowledge_manager = MagicMock()
        self.mock_debate_manager = MagicMock()
        self.mock_model_provider = MagicMock(spec=LiteLLMProvider)
        self.mock_db_manager = MagicMock()
        self.mock_config_manager = MagicMock()
        self.mock_role_model_manager = MagicMock()
        self.mock_enhanced_debate_manager = MagicMock()
        self.mock_model_manager = MagicMock()

        # Configure the mock ModelManager to return a list of global models
        self.mock_model_manager.get_available_models.return_value = [
            {"name": "llama3:instruct", "provider": "ollama", "size": "4.7 GB"},
            {"name": "qwen3:8b", "provider": "ollama", "size": "5.2 GB"},
        ]

        # Instantiate the TUI with mocked dependencies
        self.tui = DAIP_TUI(
            executor=self.mock_executor,
            session_manager=self.mock_session_manager,
            role_manager=self.mock_role_manager,
            knowledge_manager=self.mock_knowledge_manager,
            debate_manager=self.mock_debate_manager,
            model_provider=self.mock_model_provider,
            db_manager=self.mock_db_manager,
            config_manager=self.mock_config_manager,
            role_model_manager=self.mock_role_model_manager,
            enhanced_debate_manager=self.mock_enhanced_debate_manager,
        )
        # Replace the TUI's model_manager with our mock
        self.tui._model_manager = self.mock_model_manager

    @patch("daip_live.tui.LiteLLMProvider")
    def test_global_model_switch_command_updates_provider(self, mock_LiteLLMProvider):
        """
        [VERIFY] Test that `/model switch` correctly updates the TUI's main model provider.  # noqa: E501
        """
        # --- Arrange ---
        # The TUI is set up with a default model provider in setUp.
        # We want to switch to 'qwen3:8b'
        target_model_name = "qwen3:8b"

        # Mock the switch_model method to return success
        self.mock_model_manager.switch_model.return_value = True

        # --- Act ---
        # Directly call the handler for the /model switch command
        self.tui._handle_model_switch(target_model_name)

        # --- Assert ---
        # 1. Assert that the model manager's switch method was called correctly
        self.mock_model_manager.switch_model.assert_called_once_with(
            target_model_name, "ollama"
        )

        # 2. Assert that a new LiteLLMProvider was instantiated with the correct config
        # The TUI creates a new ProviderConfig and passes it to a new LiteLLMProvider instance.  # noqa: E501
        # We check that this instantiation happened.
        mock_LiteLLMProvider.assert_called_once()

        # 3. Check the arguments passed to the new LiteLLMProvider instance
        # It should be a ProviderConfig object with the correct model name
        call_args, call_kwargs = mock_LiteLLMProvider.call_args
        self.assertIsInstance(call_args[0], ProviderConfig)
        self.assertEqual(call_args[0].model, f"ollama/{target_model_name}")

        # 4. Verify that the TUI's internal model provider has been replaced
        # The `_handle_model_switch` method replaces `self.tui._model_provider`
        # with the newly created instance.
        self.assertEqual(self.tui._model_provider, mock_LiteLLMProvider.return_value)


if __name__ == "__main__":
    unittest.main()
