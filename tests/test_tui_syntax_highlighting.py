import json
import os
import sys
import unittest
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from daip_live.tui import DAIP_TUI


class TestTUISyntaxHighlighting(unittest.TestCase):
    """Test cases for TUI syntax highlighting features."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the executor and other dependencies
        self.mock_executor = Mock()
        self.mock_session_manager = Mock()
        self.mock_role_manager = Mock()

        # Create TUI instance
        self.tui = DAIP_TUI(self.mock_executor, "test goal")

        # Replace the internal session manager and role manager with our mocks
        self.tui._session_manager = self.mock_session_manager
        self.tui._role_manager = self.mock_role_manager

    def test_highlight_code_and_json_with_valid_json(self):
        """Test syntax highlighting with valid JSON."""
        # Test JSON with various data types
        test_json = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False}
            ],
            "metadata": {
                "total": 2,
                "page": 1,
                "null_value": None
            }
        }

        json_string = json.dumps(test_json, ensure_ascii=False)
        highlighted = self.tui._highlight_code_and_json(json_string)

        # Verify that the function didn't crash and returned a string
        self.assertIsInstance(highlighted, str)

    def test_highlight_code_and_json_with_invalid_json(self):
        """Test syntax highlighting with invalid JSON (should return as is)."""
        # Test with plain text
        plain_text = "This is just plain text with no JSON structure"
        highlighted = self.tui._highlight_code_and_json(plain_text)

        # Should return the same text
        self.assertEqual(highlighted, plain_text)

    def test_highlight_code_and_json_with_empty_string(self):
        """Test syntax highlighting with empty string."""
        highlighted = self.tui._highlight_code_and_json("")

        # Should return empty string
        self.assertEqual(highlighted, "")

    def test_highlight_code_and_json_with_malformed_json(self):
        """Test syntax highlighting with malformed JSON."""
        malformed_json = '{"key": "value", "missing_quote: true}'
        highlighted = self.tui._highlight_code_and_json(malformed_json)

        # Should return the same text since it's not valid JSON
        self.assertEqual(highlighted, malformed_json)


if __name__ == '__main__':
    unittest.main()
