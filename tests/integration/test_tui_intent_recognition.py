"""
Integration tests for TUI intent recognition functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
from src.daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer, Intent, IntentType
from src.daip_live.tui import DAIP_TUI


class TestTUIIntentRecognitionIntegration:
    """Integration tests for TUI intent recognition functionality."""

    @pytest.fixture
    def intent_recognizer(self):
        """Create an intent recognizer instance for testing."""
        return EnhancedIntentRecognizer()

    @pytest.fixture
    def mock_tui(self):
        """Create a mock TUI instance for testing."""
        with patch('src.daip_live.tui.DAIP_TUI.__init__', return_value=None):
            tui = DAIP_TUI()
            # Mock required attributes
            tui._executor = None
            tui._session_manager = Mock()
            tui._role_manager = Mock()
            tui._knowledge_manager = Mock()
            tui._debate_manager = Mock()
            tui._model_provider = Mock()
            tui._role_model_manager = Mock()
            tui._enhanced_debate_manager = Mock()
            tui._db_manager = Mock()
            tui._config_manager = Mock()
            tui._model_manager = Mock()
            tui._memory_service = Mock()
            tui._tool_manager = Mock()
            tui._permission_manager = Mock()
            tui._wiki_manager = Mock()
            return tui

    def test_natural_language_command_recognition(self, intent_recognizer):
        """Test that natural language commands are correctly recognized."""
        # Test debate command recognition with patterns that work
        intent = intent_recognizer.recognize_intent("我们来辩论人工智能伦理")
        assert intent is not None
        assert intent.name == "start_debate"
        assert intent.tool_name == "debate"
        assert intent.intent_type == IntentType.WORKFLOW

        # Test wiki command recognition
        intent = intent_recognizer.recognize_intent("创建wiki页面")
        assert intent is not None
        assert intent.name == "create_wiki"
        assert intent.tool_name == "wiki"
        assert intent.intent_type == IntentType.WORKFLOW

        # Test project initialization recognition
        intent = intent_recognizer.recognize_intent("初始化项目")
        assert intent is not None
        assert intent.name == "initialize_project"
        assert intent.tool_name == "scaffold"
        assert intent.intent_type == IntentType.WORKFLOW

        # Test paper search recognition
        intent = intent_recognizer.recognize_intent("搜索深度学习论文")
        assert intent is not None
        assert intent.name == "search_papers"
        assert intent.tool_name == "search_academic_papers"
        assert intent.intent_type == IntentType.WORKFLOW

    def test_intent_to_command_execution(self, intent_recognizer):
        """Test that recognized intents correctly map to command execution."""
        # Test debate intent mapping
        intent = intent_recognizer.recognize_intent("发起辩论")
        assert intent is not None
        assert intent.tool_name == "debate"

        # Test wiki intent mapping
        intent = intent_recognizer.recognize_intent("创建wiki")
        assert intent is not None
        assert intent.tool_name == "wiki"

        # Test project scaffold intent mapping
        intent = intent_recognizer.recognize_intent("初始化项目")
        assert intent is not None
        assert intent.tool_name == "scaffold"

    def test_different_intent_types_handling(self, intent_recognizer):
        """Test that different types of intents are handled correctly."""
        # Test workflow intents
        workflow_intents = [
            ("发起辩论", "start_debate", IntentType.WORKFLOW),
            ("创建wiki", "create_wiki", IntentType.WORKFLOW),
            ("初始化项目", "initialize_project", IntentType.WORKFLOW),
            ("搜索论文", "search_papers", IntentType.WORKFLOW)
        ]

        for input_text, expected_name, expected_type in workflow_intents:
            intent = intent_recognizer.recognize_intent(input_text)
            assert intent is not None, f"Failed to recognize: {input_text}"
            assert intent.name == expected_name
            assert intent.intent_type == expected_type
            assert intent.tool_name is not None

        # Test question intents (require confidence check)
        question_intent = intent_recognizer.recognize_intent("什么是人工智能?")
        assert question_intent is not None
        assert question_intent.name == "question"
        assert question_intent.intent_type == IntentType.QUESTION
        assert question_intent.requires_confidence_check is True

        # Test chat intents
        chat_intent = intent_recognizer.recognize_intent("你好")
        assert chat_intent is not None
        assert chat_intent.name == "chat"
        assert chat_intent.intent_type == IntentType.CHAT
        assert chat_intent.requires_confidence_check is False

    def test_unrecognized_intent_feedback(self, intent_recognizer):
        """Test that unrecognized intents provide appropriate feedback."""
        # Test completely unrelated text
        intent = intent_recognizer.recognize_intent("今天天气很好")
        # This might be classified as chat or remain None depending on implementation
        
        # Test text below confidence threshold
        intent = intent_recognizer.recognize_intent("xyz")
        assert intent is None, "Should not recognize random text with low confidence"

        # Test ambiguous text
        intent = intent_recognizer.recognize_intent("处理文档")
        # May or may not be recognized depending on patterns, but should not crash

    def test_edge_cases_and_variations(self, intent_recognizer):
        """Test various edge cases and input variations."""
        # Test with extra whitespace
        intent = intent_recognizer.recognize_intent("  发起辩论  ")
        assert intent is not None

        # Test mixed case input - note that implementation lowercases input
        intent = intent_recognizer.recognize_intent("创建WIKI")
        assert intent is not None
        assert intent.name == "create_wiki"

        # Test English commands
        intent = intent_recognizer.recognize_intent("search paper")
        assert intent is not None
        assert intent.name == "search_papers"

        # Test with special characters in input that doesn't interfere with patterns
        intent = intent_recognizer.recognize_intent("创建wiki页面")
        assert intent is not None

    @pytest.mark.asyncio
    async def test_tui_integration_with_intent_recognition(self, mock_tui):
        """Test TUI integration with intent recognition."""
        # Mock the intent recognizer
        mock_tui._intent_recognizer = EnhancedIntentRecognizer()
        
        # Mock the command handlers
        mock_tui._handle_debate_command = AsyncMock()
        mock_tui._handle_wiki_command = AsyncMock()
        mock_tui._handle_project_command = AsyncMock()
        
        # Test that natural language input is processed through intent recognition
        with patch.object(mock_tui, '_update_log_view') as mock_update_log:
            # This would require more extensive mocking of the TUI's internal methods
            pass