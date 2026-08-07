"""Tests for hybrid sanitization module (TDD - RED phase)."""

import pytest
from daip_live.hybrid.sanitization import sanitize_prompt, SanitizationResult


def test_sanitize_prompt_removes_api_keys():
    """Test that API keys are removed from prompts."""
    prompt = "Use my API key sk-1234567890 to call the service"
    result = sanitize_prompt(prompt)
    assert "sk-1234567890" not in result.sanitized
    assert result.redacted_count >= 1
    assert result.warnings


def test_sanitize_prompt_removes_passwords():
    """Test that passwords are removed from prompts."""
    prompt = "My password is SecretPass123 for the database"
    result = sanitize_prompt(prompt)
    assert "SecretPass123" not in result.sanitized
    assert result.redacted_count >= 1


def test_sanitize_prompt_removes_file_paths():
    """Test that file paths are removed from prompts."""
    prompt = "Read the file at C:\\Users\\Zhang\\secret.txt"
    result = sanitize_prompt(prompt)
    assert "C:\\Users\\Zhang\\secret.txt" not in result.sanitized
    assert result.redacted_count >= 1


def test_sanitize_prompt_preserves_safe_content():
    """Test that safe content is preserved."""
    prompt = "Write a function to sort an array"
    result = sanitize_prompt(prompt)
    assert "sort an array" in result.sanitized.lower()
    assert result.redacted_count == 0


def test_sanitize_result_contains_metadata():
    """Test that sanitization result contains metadata."""
    prompt = "API key: abc123, password: xyz789"
    result = sanitize_prompt(prompt)
    assert hasattr(result, 'sanitized')
    assert hasattr(result, 'redacted_count')
    assert hasattr(result, 'warnings')
    assert isinstance(result.redacted_count, int)
    assert isinstance(result.warnings, list)


def test_sanitize_prompt_multiple_secrets():
    """Test handling of multiple secrets in one prompt."""
    prompt = "Use API key sk-key1 and token tok-123 with password pass456"
    result = sanitize_prompt(prompt)
    assert "sk-key1" not in result.sanitized
    assert "tok-123" not in result.sanitized
    assert "pass456" not in result.sanitized
    assert result.redacted_count >= 3
