"""Security Gate for risk classification.

This module implements the security gate that classifies tasks by risk level
before they can be delegated to cloud providers.
"""

import re
from enum import Enum
from typing import Optional


class RiskLevel(Enum):
    """Risk classification for delegation decisions."""
    LOW = "LOW"         # Can be delegated to cloud
    MEDIUM = "MEDIUM"   # Auto-sanitize, local execution
    HIGH = "HIGH"       # Human confirmation required


class SecurityGate:
    """Security gate for risk-based task classification."""

    # Patterns that indicate HIGH risk
    HIGH_RISK_PATTERNS = [
        r"password",
        r"api[_-]?key",
        r"secret",
        r"token",
        r"private[_-]?key",
        r"credentials",
    ]

    # Patterns that indicate MEDIUM risk
    MEDIUM_RISK_PATTERNS = [
        r"file:///.*",           # Local file paths
        r"~[/\\].*",             # Home directory paths
        r"[A-Z]:[/\\].*",         # Windows drive paths
    ]

    @classmethod
    def classify_risk(cls, prompt: str, context: Optional[dict] = None) -> RiskLevel:
        """Classify the risk level of a task.

        Args:
            prompt: The user prompt to analyze
            context: Additional context (tool calls, file access, etc.)

        Returns:
            RiskLevel: LOW, MEDIUM, or HIGH
        """
        prompt_lower = prompt.lower()

        # Check for HIGH risk patterns
        for pattern in cls.HIGH_RISK_PATTERNS:
            if re.search(pattern, prompt_lower):
                return RiskLevel.HIGH

        # Check for MEDIUM risk patterns
        for pattern in cls.MEDIUM_RISK_PATTERNS:
            if re.search(pattern, prompt):
                return RiskLevel.MEDIUM

        # Check context for tool calls (always MEDIUM or HIGH)
        if context and context.get("has_tool_calls"):
            if any(key in prompt_lower for key in ["file", "read", "write", "delete"]):
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM

        # Default to LOW
        return RiskLevel.LOW

    @classmethod
    def can_delegate(cls, risk_level: RiskLevel) -> bool:
        """Check if a task can be delegated to cloud providers.

        Args:
            risk_level: The classified risk level

        Returns:
            bool: True if delegation is allowed
        """
        return risk_level == RiskLevel.LOW


class SecurityRule:
    """Security rule configuration."""

    def __init__(
        self,
        pattern: str,
        risk_level: RiskLevel,
        description: str = ""
    ):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.risk_level = risk_level
        self.description = description


class SecurityRulesConfig:
    """Configuration for security rules."""

    DEFAULT_RULES = [
        SecurityRule(
            pattern=r"password|api[_-]?key|secret",
            risk_level=RiskLevel.HIGH,
            description="Credentials and secrets"
        ),
        SecurityRule(
            pattern=r"file:///.*|~[/\\].*|[A-Z]:[/\\].*",
            risk_level=RiskLevel.MEDIUM,
            description="Local file paths"
        ),
    ]
