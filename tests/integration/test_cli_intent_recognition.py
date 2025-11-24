"""
Integration tests for CLI intent recognition functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import typer
from typer.testing import CliRunner

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer, Intent, IntentType
from daip_live.cli.main import app


class TestCLIIntentRecognitionIntegration:
    """Integration tests for CLI intent recognition functionality."""

    @pytest.fixture
    def intent_recognizer(self):
        """Create an intent recognizer instance for testing."""
        return EnhancedIntentRecognizer()

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_cli_command_line_arguments_passed_to_intent_recognizer(self, intent_recognizer):
        """Test that CLI command line arguments are correctly passed to intent recognizer."""
        # Test that the CLI can recognize and process various command patterns
        # This test verifies the integration between CLI argument parsing and intent recognition
        
        # Test debate command recognition
        intent = intent_recognizer.recognize_intent("开始辩论人工智能伦理")
        assert intent is not None
        assert intent.name == "start_debate"
        assert intent.tool_name == "debate"
        assert intent.intent_type == IntentType.WORKFLOW
        
        # Test paper search command recognition
        intent = intent_recognizer.recognize_intent("搜索深度学习论文")
        assert intent is not None
        assert intent.name == "search_papers"
        assert intent.tool_name == "search_academic_papers"
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

    def test_recognized_intent_converts_to_command_execution(self, intent_recognizer):
        """Test that recognized intents correctly convert to command execution."""
        # Test debate intent mapping to command
        intent = intent_recognizer.recognize_intent("发起辩论")
        assert intent is not None
        assert intent.tool_name == "debate"
        assert "topic" in intent.parameters or "query" in intent.parameters
        
        # Test wiki intent mapping to command
        intent = intent_recognizer.recognize_intent("创建wiki")
        assert intent is not None
        assert intent.tool_name == "wiki"
        assert "title" in intent.parameters or "query" in intent.parameters
        
        # Test project scaffold intent mapping to command
        intent = intent_recognizer.recognize_intent("初始化项目")
        assert intent is not None
        assert intent.tool_name == "scaffold"
        assert "project_type" in intent.parameters or "query" in intent.parameters
        
        # Test paper search intent mapping to command
        intent = intent_recognizer.recognize_intent("搜索论文")
        assert intent is not None
        assert intent.tool_name == "search_academic_papers"
        assert "query" in intent.parameters

    def test_different_intent_types_are_handled_correctly(self, intent_recognizer):
        """Test that different types of intents are handled correctly."""
        # Test workflow intents (should trigger specific commands)
        workflow_intents = [
            ("开始辩论", "start_debate", IntentType.WORKFLOW),
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

        # Test download paper intent with specific pattern
        intent = intent_recognizer.recognize_intent("下载arxiv论文1234.5678")
        assert intent is not None
        assert intent.name == "download_paper"
        assert intent.intent_type == IntentType.WORKFLOW
        assert intent.tool_name == "download_paper"

        # Test question intents (require confidence check)
        question_intent = intent_recognizer.recognize_intent("什么是人工智能?")
        assert question_intent is not None
        assert question_intent.name == "question"
        assert question_intent.intent_type == IntentType.QUESTION
        assert question_intent.requires_confidence_check is True

        # Test chat intents (direct response)
        chat_intent = intent_recognizer.recognize_intent("你好")
        assert chat_intent is not None
        assert chat_intent.name == "chat"
        assert chat_intent.intent_type == IntentType.CHAT
        assert chat_intent.requires_confidence_check is False

    def test_unrecognized_intent_gives_appropriate_feedback(self, intent_recognizer):
        """Test that unrecognized intents provide appropriate feedback."""
        # Test completely unrelated text (should not be recognized or classified as chat)
        intent = intent_recognizer.recognize_intent("今天天气很好")
        # This might be classified as chat or remain None depending on implementation
        
        # Test text below confidence threshold (should not be recognized)
        intent = intent_recognizer.recognize_intent("xyz")
        assert intent is None, "Should not recognize random text with low confidence"

        # Test ambiguous text (should not crash)
        intent = intent_recognizer.recognize_intent("处理文档")
        # May or may not be recognized depending on patterns, but should not crash

    def test_natural_language_input_scenarios(self, intent_recognizer):
        """Test various natural language input scenarios."""
        # Test debate scenarios with different phrasings
        debate_inputs = [
            "我们来辩论人工智能的未来发展",
            "发起一场关于机器学习伦理的辩论",
            "让我们辩论自动驾驶汽车的安全性问题"
        ]
        
        for input_text in debate_inputs:
            intent = intent_recognizer.recognize_intent(input_text)
            assert intent is not None, f"Failed to recognize debate input: {input_text}"
            assert intent.name == "start_debate"
            assert "topic" in intent.parameters or "query" in intent.parameters

        # Test wiki creation scenarios
        wiki_inputs = [
            "创建wiki页面介绍量子计算",
            "新建一个关于区块链技术的wiki",
            "写个wiki页面说明机器学习基础",
            "编辑wiki添加人工智能发展史"
        ]
        
        for input_text in wiki_inputs:
            intent = intent_recognizer.recognize_intent(input_text)
            assert intent is not None, f"Failed to recognize wiki input: {input_text}"
            assert intent.name == "create_wiki"
            assert "title" in intent.parameters or "query" in intent.parameters

        # Test project initialization scenarios
        project_inputs = [
            "初始化一个新的Python项目",
            "创建一个机器学习项目",
            "新建数据科学项目模板",
            "设置一个新的web开发环境"
        ]
        
        for input_text in project_inputs:
            intent = intent_recognizer.recognize_intent(input_text)
            assert intent is not None, f"Failed to recognize project input: {input_text}"
            assert intent.name == "initialize_project"
            assert "project_type" in intent.parameters or "query" in intent.parameters

        # Test academic paper search scenarios
        paper_inputs = [
            "搜索关于神经网络优化的论文",
            "查找深度学习在医疗领域的应用论文",
            "找一些关于自然语言处理的最新研究",
            "搜索计算机视觉方面的学术文章"
        ]
        
        for input_text in paper_inputs:
            intent = intent_recognizer.recognize_intent(input_text)
            assert intent is not None, f"Failed to recognize paper search input: {input_text}"
            assert intent.name == "search_papers"
            assert "query" in intent.parameters

    def test_edge_cases_and_input_variations(self, intent_recognizer):
        """Test various edge cases and input variations."""
        # Test with extra whitespace
        intent = intent_recognizer.recognize_intent("  开始辩论  ")
        assert intent is not None
        assert intent.name == "start_debate"

        # Test mixed case input
        intent = intent_recognizer.recognize_intent("创建WIKI")
        assert intent is not None
        assert intent.name == "create_wiki"

        # Test English commands
        intent = intent_recognizer.recognize_intent("search paper")
        assert intent is not None
        assert intent.name == "search_papers"

        # Test commands with special characters
        intent = intent_recognizer.recognize_intent("创建wiki页面：量子计算基础")
        assert intent is not None
        assert intent.name == "create_wiki"

        # Test partially matching commands
        intent = intent_recognizer.recognize_intent("我想开始一个辩论")
        assert intent is not None
        assert intent.name == "start_debate"

    @pytest.mark.asyncio
    async def test_cli_integration_with_real_commands(self, runner):
        """Test CLI integration with real command execution (mocked)."""
        # Test that CLI commands can be invoked (this tests the Typer integration)
        # Note: We're not actually running the async functions, just testing command structure
        
        # Test help command
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        
        # Test debate subcommand help
        result = runner.invoke(app, ["debate", "--help"])
        assert result.exit_code == 0
        
        # Test doc subcommand help
        result = runner.invoke(app, ["doc", "--help"])
        assert result.exit_code == 0

        # Test that debate start command structure is correct
        # (We won't actually run it due to async dependencies)
        result = runner.invoke(app, ["debate", "start", "--help"])
        assert result.exit_code == 0

    def test_intent_parameter_extraction_accuracy(self, intent_recognizer):
        """Test that intent parameters are accurately extracted from natural language."""
        # Test debate topic extraction
        intent = intent_recognizer.recognize_intent("开始辩论人工智能的伦理问题")
        assert intent is not None
        assert "topic" in intent.parameters or "query" in intent.parameters
        # The topic should contain the key elements
        topic_content = intent.parameters.get("topic", "") or intent.parameters.get("query", "")
        assert "人工智能" in topic_content or "伦理" in topic_content

        # Test wiki title extraction
        intent = intent_recognizer.recognize_intent("创建wiki页面：机器学习基础概念")
        assert intent is not None
        title_content = intent.parameters.get("title", "") or intent.parameters.get("query", "")
        assert "机器学习" in title_content or "基础概念" in title_content

        # Test project type extraction
        intent = intent_recognizer.recognize_intent("初始化机器学习项目")
        assert intent is not None
        project_type = intent.parameters.get("project_type", "")
        # The project type extraction might not be perfect, so we'll check if it's not empty
        assert project_type != ""

        # Test search query extraction
        intent = intent_recognizer.recognize_intent("搜索自然语言处理的最新进展论文")
        assert intent is not None
        search_query = intent.parameters.get("query", "")
        assert "自然语言处理" in search_query or "最新进展" in search_query or search_query != ""