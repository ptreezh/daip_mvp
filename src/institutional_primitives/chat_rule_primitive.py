"""
Chat Rule Primitive Implementation.

This module implements the chat rule institutional primitive for validating
and enforcing chat rules within the DAIP-LIVE system.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field
from src.institutional_primitives.base import InstitutionalPrimitive, ExecutionContext

logger = logging.getLogger(__name__)


class ChatRuleType(str, Enum):
    """Types of chat rules that can be enforced."""
    CONTENT_FILTER = "content_filter"
    RATE_LIMIT = "rate_limit"
    PARTICIPANT_COUNT = "participant_count"
    CUSTOM = "custom"


class RuleViolation(BaseModel):
    """Represents a rule violation."""
    rule_id: str
    rule_type: ChatRuleType
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRuleConfiguration(BaseModel):
    """Configuration for the chat rule primitive."""
    rule_id: str
    name: str
    description: str
    rule_type: ChatRuleType = ChatRuleType.CONTENT_FILTER

    # Content filter settings
    prohibited_keywords: List[str] = Field(default_factory=list)
    max_message_length: Optional[int] = Field(default=None, ge=1)

    # Rate limit settings
    max_messages_per_minute: Optional[int] = Field(default=None, ge=1)

    # Participant count settings
    min_participants: int = Field(default=1, ge=1)
    max_participants: int = Field(default=100, ge=1)

    # Metadata
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)


class ChatRulePrimitive(InstitutionalPrimitive):
    """
    Chat Rule Primitive for validating and enforcing chat room rules.
    """

    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
        """Initialize the chat rule primitive."""
        super().__init__(primitive_id, config)
        if config:
            self.rule_config = ChatRuleConfiguration(**config)
        else:
            self.rule_config = ChatRuleConfiguration(
                rule_id="default_chat_rule",
                name="Default Chat Rule",
                description="Default chat rule configuration"
            )
        logger.info(f"Initialized ChatRulePrimitive: {primitive_id}")

    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for expected inputs."""
        return {
            "type": "object",
            "properties": {
                "chat_session": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "participants": {"type": "array", "items": {"type": "object"}},
                        "message_history": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["session_id", "participants"]
                },
                "message": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "author_id": {"type": "string"},
                        "content": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    },
                    "required": ["message_id", "author_id", "content"]
                }
            },
            "required": ["chat_session", "message"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for produced outputs."""
        return {
            "type": "object",
            "properties": {
                "is_valid": {"type": "boolean"},
                "violations": {"type": "array", "items": {"type": "object"}},
                "actions": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["is_valid", "violations"]
        }

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute the chat rule primitive."""
        violations = []

        # Execute rule validation based on rule type
        if self.rule_config.rule_type == ChatRuleType.CONTENT_FILTER:
            violations.extend(self._validate_content_filter(inputs))
        elif self.rule_config.rule_type == ChatRuleType.RATE_LIMIT:
            violations.extend(self._validate_rate_limit(inputs))
        elif self.rule_config.rule_type == ChatRuleType.PARTICIPANT_COUNT:
            violations.extend(self._validate_participant_count(inputs))

        is_valid = len(violations) == 0
        return {
            "is_valid": is_valid,
            "violations": [v.model_dump() for v in violations],
            "actions": []
        }

    def _validate_content_filter(self, inputs: Dict[str, Any]) -> List[RuleViolation]:
        """Validate content-based rules."""
        violations = []
        message_content = inputs.get("message", {}).get("content", "")

        # Max message length
        if self.rule_config.max_message_length and len(message_content) > self.rule_config.max_message_length:
            violation = RuleViolation(
                rule_id=self.rule_config.rule_id,
                rule_type=self.rule_config.rule_type,
                description=f"Message length {len(message_content)} exceeds max of {self.rule_config.max_message_length}"
            )
            violations.append(violation)

        # Prohibited keywords
        for keyword in self.rule_config.prohibited_keywords:
            if keyword.lower() in message_content.lower():
                violation = RuleViolation(
                    rule_id=self.rule_config.rule_id,
                    rule_type=self.rule_config.rule_type,
                    description=f"Message contains prohibited keyword: '{keyword}'"
                )
                violations.append(violation)
        
        return violations

    def _validate_rate_limit(self, inputs: Dict[str, Any]) -> List[RuleViolation]:
        """Validate rate limit rules."""
        violations = []
        if not self.rule_config.max_messages_per_minute:
            return violations

        message = inputs.get("message", {})
        author_id = message.get("author_id")
        timestamp = datetime.fromisoformat(message.get("timestamp"))
        
        history = inputs.get("chat_session", {}).get("message_history", [])
        
        recent_messages = 0
        one_minute_ago = timestamp - timedelta(minutes=1)

        for msg in history:
            if msg.get("author_id") == author_id:
                msg_ts = datetime.fromisoformat(msg.get("timestamp"))
                if msg_ts > one_minute_ago:
                    recent_messages += 1
        
        # Including the current message
        if (recent_messages + 1) > self.rule_config.max_messages_per_minute:
            violation = RuleViolation(
                rule_id=self.rule_config.rule_id,
                rule_type=self.rule_config.rule_type,
                description=f"Rate limit exceeded. User sent {recent_messages + 1} messages in the last minute (limit: {self.rule_config.max_messages_per_minute})."
            )
            violations.append(violation)

        return violations

    def _validate_participant_count(self, inputs: Dict[str, Any]) -> List[RuleViolation]:
        """Validate participant count rules."""
        violations = []
        participants = inputs.get("chat_session", {}).get("participants", [])
        count = len(participants)

        if count > self.rule_config.max_participants:
            violation = RuleViolation(
                rule_id=self.rule_config.rule_id,
                rule_type=self.rule_config.rule_type,
                description=f"Participant count exceeded. {count} participants, max is {self.rule_config.max_participants}."
            )
            violations.append(violation)
        
        if count < self.rule_config.min_participants:
            violation = RuleViolation(
                rule_id=self.rule_config.rule_id,
                rule_type=self.rule_config.rule_type,
                description=f"Insufficient participants. {count} participants, min is {self.rule_config.min_participants}."
            )
            violations.append(violation)

        return violations
