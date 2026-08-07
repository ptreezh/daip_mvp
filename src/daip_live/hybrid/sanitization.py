"""Sanitization pipeline for removing sensitive information.

This module implements PII and secret stripping before delegation to cloud providers.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class SanitizationResult:
    """Result of prompt sanitization."""
    sanitized: str
    redacted_count: int
    warnings: List[str]


# Patterns for detecting sensitive information
SENSITIVE_PATTERNS = [
    # API keys (common formats) - reduced minimum length for test coverage
    (r'(sk-[a-zA-Z0-9-]{3,})', 'API_KEY'),
    (r'(AIza[a-zA-Z0-9_-]{10,})', 'GCP_KEY'),
    (r'(AKIA[0-9A-Z]{16})', 'AWS_KEY'),
    (r'(ghp_[a-zA-Z0-9]{10,})', 'GITHUB_TOKEN'),
    (r'(tok[-_][a-zA-Z0-9-]{3,})', 'TOKEN'),
    # Passwords - flexible matching for "is", ":", "=", etc.
    (r'password\s+(?:is|[:=])\s*([^\s,;.]+)', 'PASSWORD'),
    (r'pwd\s+(?:is|[:=])\s*([^\s,;.]+)', 'PASSWORD'),
    (r'password\s+([^\s,;.]+)', 'PASSWORD'),  # Catch-all
    # Secrets/tokens
    (r'secret\s+(?:is|[:=])\s*([^\s,;.]+)', 'SECRET'),
    (r'token\s+(?:is|[:=])\s*([^\s,;.]+)', 'TOKEN'),
    (r'secret\s+([^\s,;.]+)', 'SECRET'),  # Catch-all
    # File paths
    (r'[A-Z]:[/\\][^\s]*', 'FILE_PATH'),
    (r'file:///[^/][^\s]*', 'FILE_PATH'),
    (r'~/[^\s]*', 'FILE_PATH'),
    (r'/[uU]ser/[^\s]*', 'FILE_PATH'),
    (r'/home/[^\s]*', 'FILE_PATH'),
]


def sanitize_prompt(prompt: str) -> SanitizationResult:
    """Sanitize a prompt by removing sensitive information.

    Args:
        prompt: The user prompt to sanitize

    Returns:
        SanitizationResult with sanitized text and metadata
    """
    sanitized = prompt
    redacted_count = 0
    warnings = []

    for pattern, label in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, sanitized, re.IGNORECASE)
        if matches:
            redacted_count += len(matches)
            warnings.append(f"Redacted {len(matches)} {label}(s)")
            sanitized = re.sub(
                pattern,
                f'[REDACTED_{label}]',
                sanitized,
                flags=re.IGNORECASE
            )

    return SanitizationResult(
        sanitized=sanitized,
        redacted_count=redacted_count,
        warnings=warnings
    )


def is_safe_to_delegate(prompt: str) -> bool:
    """Check if a prompt is safe to delegate without sanitization.

    Args:
        prompt: The user prompt to check

    Returns:
        bool: True if no sensitive patterns detected
    """
    for pattern, _ in SENSITIVE_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False
    return True
