"""
Tests for chat rule primitive implementation.

This module contains comprehensive tests for the chat rule institutional primitive,
following the TDD RED-GREEN-REFACTOR approach.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from src.institutional_primitives.chat_rule_primitive import ChatRulePrimitive, ChatRuleConfiguration, ChatRuleType


class TestChatRuleConfiguration:
    """Test chat rule configuration validation."""

    def test_chat_rule_configuration_valid(self):
        """Test valid chat rule configuration."""
        config = ChatRuleConfiguration(
            rule_id="test_rule",
            name="Test Chat Rule",
            description="Test chat rule configuration",
            rule_type=ChatRuleType.CONTENT_FILTER,
            max_message_length=140
        )
        assert config.rule_id == "test_rule"
        assert config.rule_type == ChatRuleType.CONTENT_FILTER
        assert config.max_message_length == 140

    def test_chat_rule_configuration_defaults(self):
        """Test chat rule configuration with default values."""
        config = ChatRuleConfiguration(
            rule_id="default_rule",
            name="Default Rule",
            description="Default configuration"
        )
        assert config.rule_type == ChatRuleType.CONTENT_FILTER
        assert config.max_message_length is None
        assert config.max_participants == 100

    def test_chat_rule_configuration_invalid(self):
        """Test invalid chat rule configuration."""
        with pytest.raises(ValueError):
            ChatRuleConfiguration(
                rule_id="invalid", name="invalid", description="invalid",
                max_message_length=0
            )


class TestChatRulePrimitive:
    """Test chat rule primitive functionality."""

    def test_chat_rule_primitive_initialization(self):
        """
        Test the initialization of the primitive.
        """
        primitive = ChatRulePrimitive(primitive_id="test_chat_primitive", config={
            "rule_id": "test", "name": "test", "description": "test"
        })
        assert primitive.primitive_id == "test_chat_primitive"
        assert primitive.rule_config.name == "test"

    def test_get_input_schema(self, primitive):
        """Test input schema generation."""
        schema = primitive.get_input_schema()
        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "chat_session" in schema["properties"]
        assert "message" in schema["properties"]

    def test_get_output_schema(self, primitive):
        """Test output schema generation."""
        schema = primitive.get_output_schema()
        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "is_valid" in schema["properties"]
        assert "violations" in schema["properties"]

    @pytest.mark.asyncio
    async def test_execute_valid_message(self, primitive):
        """Test the execute method with a valid message."""
        context = Mock()
        context.execution_id = "test_exec"
        inputs = {
            "chat_session": {
                "session_id": "test_session",
                "participants": []
            },
            "message": {
                "message_id": "msg1",
                "author_id": "user1",
                "content": "This is a valid message.",
                "timestamp": datetime.now().isoformat()
            }
        }

        result = await primitive.execute(inputs, context)

        assert result["is_valid"] is True
        assert len(result["violations"]) == 0

    @pytest.mark.asyncio
    async def test_execute_message_too_long(self):
        """Test that a message exceeding the max length fails validation."""
        config = {
            "rule_id": "len_rule", "name": "len", "description": "len",
            "rule_type": ChatRuleType.CONTENT_FILTER,
            "max_message_length": 10
        }
        primitive = ChatRulePrimitive("len_primitive", config)
        context = Mock()
        context.execution_id = "test_exec_len"
        inputs = {
            "chat_session": {"session_id": "s1", "participants": []},
            "message": {
                "message_id": "m1", "author_id": "u1",
                "content": "This message is definitely too long.",
                "timestamp": datetime.now().isoformat()
            }
        }

        result = await primitive.execute(inputs, context)

        assert result["is_valid"] is False
        assert len(result["violations"]) == 1
        assert result["violations"][0]["rule_type"] == ChatRuleType.CONTENT_FILTER

    @pytest.mark.asyncio
    async def test_execute_prohibited_keyword(self):
        """Test that a message with a prohibited keyword fails validation."""
        config = {
            "rule_id": "kw_rule", "name": "kw", "description": "kw",
            "rule_type": ChatRuleType.CONTENT_FILTER,
            "prohibited_keywords": ["spam", "unethical"]
        }
        primitive = ChatRulePrimitive("kw_primitive", config)
        context = Mock()
        context.execution_id = "test_exec_kw"
        inputs = {
            "chat_session": {"session_id": "s1", "participants": []},
            "message": {
                "message_id": "m1", "author_id": "u1",
                "content": "This is considered spam content.",
                "timestamp": datetime.now().isoformat()
            }
        }

        result = await primitive.execute(inputs, context)

        assert result["is_valid"] is False
        assert len(result["violations"]) == 1
        assert "prohibited keyword" in result["violations"][0]["description"]

    @pytest.mark.asyncio
    async def test_execute_rate_limit_exceeded(self):
        """Test that sending messages too frequently fails validation."""
        config = {
            "rule_id": "rate_rule", "name": "rate", "description": "rate",
            "rule_type": ChatRuleType.RATE_LIMIT,
            "max_messages_per_minute": 2
        }
        primitive = ChatRulePrimitive("rate_primitive", config)
        context = Mock()
        context.execution_id = "test_exec_rate"

        now = datetime.now()
        message_history = [
            {"author_id": "u1", "timestamp": (now - timedelta(seconds=10)).isoformat()},
            {"author_id": "u1", "timestamp": (now - timedelta(seconds=20)).isoformat()},
        ]

        inputs = {
            "chat_session": {"session_id": "s1", "participants": [], "message_history": message_history},
            "message": {
                "message_id": "m3", "author_id": "u1",
                "content": "This message should be rate limited.",
                "timestamp": now.isoformat()
            }
        }

        result = await primitive.execute(inputs, context)

        assert result["is_valid"] is False
        assert len(result["violations"]) == 1
        assert "Rate limit exceeded" in result["violations"][0]["description"]

    @pytest.mark.asyncio
    async def test_execute_participant_count_exceeded(self):
        """Test that having too many participants fails validation."""
        config = {
            "rule_id": "pcount_rule", "name": "pcount", "description": "pcount",
            "rule_type": ChatRuleType.PARTICIPANT_COUNT,
            "max_participants": 2
        }
        primitive = ChatRulePrimitive("pcount_primitive", config)
        context = Mock()
        context.execution_id = "test_exec_pcount"

        participants = [
            {"id": "u1"}, {"id": "u2"}, {"id": "u3"}
        ]

        inputs = {
            "chat_session": {"session_id": "s1", "participants": participants},
            "message": {
                "message_id": "m1", "author_id": "u1",
                "content": "Hello everyone!",
                "timestamp": datetime.now().isoformat()
            }
        }

        result = await primitive.execute(inputs, context)

        assert result["is_valid"] is False
        assert len(result["violations"]) == 1
        assert "Participant count exceeded" in result["violations"][0]["description"]

    @pytest.fixture
    def primitive(self):
        """Create a test chat rule primitive."""
        config = {
            "rule_id": "test_rule",
            "name": "Test Rule",
            "description": "A test rule"
        }
        return ChatRulePrimitive("test_primitive", config)
