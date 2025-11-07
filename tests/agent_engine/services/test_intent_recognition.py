"""Tests for IntentRecognitionService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from daip_live.agent_engine_v1.services.intent_recognition import (
    IntentRecognitionService,
    IntentRecognitionResult,
    KeywordMatchingStrategy,
    RegexStrategy,
    MLBasedStrategy,
    IntentPattern,
    IntentCache
)


class TestIntentRecognitionResult:
    """Test IntentRecognitionResult class."""

    def test_intent_recognition_result_creation(self):
        """Test creating intent recognition result."""
        result = IntentRecognitionResult(
            intent="file_read",
            confidence=0.85,
            parameters={"file_path": "/path/to/file.txt"},
            reasoning="Pattern matched perfectly",
            strategy_used="keyword_matching"
        )

        assert result.intent == "file_read"
        assert result.confidence == 0.85
        assert result.parameters == {"file_path": "/path/to/file.txt"}
        assert result.reasoning == "Pattern matched perfectly"
        assert result.strategy_used == "keyword_matching"
        assert result.timestamp > 0


class TestIntentPattern:
    """Test IntentPattern class."""

    def test_intent_pattern_creation(self):
        """Test creating intent pattern."""
        pattern = IntentPattern(
            intent="test_intent",
            patterns=["test pattern", "sample pattern"],
            parameters=["param1", "param2"],
            description="Test pattern for testing"
        )

        assert pattern.intent == "test_intent"
        assert pattern.patterns == ["test pattern", "sample pattern"]
        assert pattern.parameters == ["param1", "param2"]
        assert pattern.description == "Test pattern for testing"
        assert pattern.confidence_weight == 1.0


class TestIntentCache:
    """Test IntentCache functionality."""

    def test_cache_operations(self):
        """Test basic cache operations."""
        cache = IntentCache(max_size=2, ttl_seconds=1.0)

        # Test empty cache
        assert cache.get("key1") is None

        # Test put and get
        result = IntentRecognitionResult(
            intent="test",
            confidence=0.8
        )
        cache.put("key1", result)

        cached_result = cache.get("key1")
        assert cached_result is not None
        assert cached_result.intent == "test"
        assert cached_result.confidence == 0.8

        # Test cache hit
        assert cache.get("key1") is not None

        # Test cache size limit
        result2 = IntentRecognitionResult(intent="test2", confidence=0.7)
        result3 = IntentRecognitionResult(intent="test3", confidence=0.6)
        cache.put("key2", result2)
        cache.put("key3", result3)

        # Should have removed oldest entry (key1)
        assert cache.get("key1") is None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None

        # Test cache clear
        cache.clear()
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_cache_ttl(self):
        """Test cache TTL functionality."""
        import time

        cache = IntentCache(max_size=10, ttl_seconds=0.1)  # 100ms TTL

        result = IntentRecognitionResult(intent="test", confidence=0.8)
        cache.put("key1", result)

        # Should be available immediately
        assert cache.get("key1") is not None

        # Wait for TTL to expire
        time.sleep(0.15)

        # Should be expired
        assert cache.get("key1") is None


class TestKeywordMatchingStrategy:
    """Test keyword matching strategy."""

    @pytest.mark.asyncio
    async def test_keyword_matching_success(self):
        """Test successful keyword matching."""
        strategy = KeywordMatchingStrategy(confidence_threshold=0.3)

        patterns = [
            IntentPattern(
                intent="file_read",
                patterns=["read file", "open document"],
                parameters=["file_path"]
            )
        ]

        result = await strategy.recognize(
            "Please read the file named test.txt",
            patterns
        )

        assert result is not None
        assert result.intent == "file_read"
        assert result.confidence >= 0.3
        assert "test.txt" in result.parameters.get("file_path", "")

    @pytest.mark.asyncio
    async def test_keyword_matching_no_match(self):
        """Test keyword matching with no match."""
        strategy = KeywordMatchingStrategy(confidence_threshold=0.5)

        patterns = [
            IntentPattern(
                intent="file_read",
                patterns=["read file", "open document"],
                parameters=["file_path"]
            )
        ]

        result = await strategy.recognize(
            "Please search for information",
            patterns
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_keyword_matching_low_confidence(self):
        """Test keyword matching with low confidence."""
        strategy = KeywordMatchingStrategy(confidence_threshold=0.8)

        patterns = [
            IntentPattern(
                intent="file_read",
                patterns=["read file", "open document"],
                parameters=["file_path"]
            )
        ]

        result = await strategy.recognize(
            "Please file",  # Only one keyword match
            patterns
        )

        assert result is None  # Below threshold


class TestRegexStrategy:
    """Test regex matching strategy."""

    @pytest.mark.asyncio
    async def test_regex_matching_success(self):
        """Test successful regex matching."""
        strategy = RegexStrategy(confidence_threshold=0.5)

        patterns = [
            IntentPattern(
                intent="file_read",
                patterns=[r"read (?:file|document) (.+)", r"open (.+)"],
                parameters=["file_path"]
            )
        ]

        result = await strategy.recognize(
            "Read the file test.txt",
            patterns
        )

        assert result is not None
        assert result.intent == "file_read"
        assert result.confidence >= 0.5
        assert "test.txt" in result.parameters.get("file_path", "")

    @pytest.mark.asyncio
    async def test_regex_matching_invalid_pattern(self):
        """Test regex matching with invalid pattern."""
        strategy = RegexStrategy(confidence_threshold=0.5)

        patterns = [
            IntentPattern(
                intent="test",
                patterns=[r"[invalid regex("],  # This will cause regex error
                parameters=[]
            )
        ]

        # Should not crash, just skip invalid patterns
        result = await strategy.recognize("test input", patterns)
        assert result is None


class TestMLBasedStrategy:
    """Test ML-based strategy."""

    @pytest.mark.asyncio
    async def test_ml_based_question_recognition(self):
        """Test ML-based question recognition."""
        strategy = MLBasedStrategy(confidence_threshold=0.6)

        patterns = []  # ML strategy doesn't use predefined patterns

        result = await strategy.recognize(
            "What is the capital of France?",
            patterns
        )

        assert result is not None
        assert result.intent == "question"
        assert result.confidence >= 0.6

    @pytest.mark.asyncio
    async def test_ml_based_command_recognition(self):
        """Test ML-based command recognition."""
        strategy = MLBasedStrategy(confidence_threshold=0.6)

        patterns = []

        result = await strategy.recognize(
            "Create a new file",
            patterns
        )

        assert result is not None
        assert result.intent == "command"
        assert result.confidence >= 0.6

    @pytest.mark.asyncio
    async def test_ml_based_no_match(self):
        """Test ML-based strategy with no match."""
        strategy = MLBasedStrategy(confidence_threshold=0.9)  # High threshold

        patterns = []

        result = await strategy.recognize(
            "xyz123",  # No clear intent
            patterns
        )

        assert result is None  # Below high threshold


class TestIntentRecognitionService:
    """Test IntentRecognitionService."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service start/stop lifecycle."""
        service = IntentRecognitionService()

        assert not service.is_healthy()

        await service.start()
        assert service.is_healthy()

        await service.stop()
        assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_recognize_intent(self):
        """Test intent recognition."""
        service = IntentRecognitionService()
        await service.start()

        try:
            result = await service.recognize_intent("Please read the file test.txt")
            assert result is not None
            assert result.confidence > 0.0
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_recognize_intent_with_context(self):
        """Test intent recognition with context."""
        service = IntentRecognitionService()
        await service.start()

        try:
            context = {"user_preference": "files"}
            result = await service.recognize_intent(
                "Show me the file",
                context=context
            )
            assert result is not None
        finally:
            await service.stop()

    @pytest.asyncio
    async def test_batch_recognize_intents(self):
        """Test batch intent recognition."""
        service = IntentRecognitionService()
        await service.start()

        try:
            inputs = [
                "Read file test.txt",
                "Create new document",
                "What is Python?"
            ]
            results = await service.batch_recognize_intents(inputs)

            assert len(results) == 3
            for result in results:
                assert result is not None
                assert result.confidence >= 0.0
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_add_custom_intent(self):
        """Test adding custom intent patterns."""
        service = IntentRecognitionService()
        await service.start()

        try:
            # Add custom intent
            service.add_custom_intent(
                "custom_action",
                ["perform custom action on (.+)", "execute (.+)"],
                ["target"]
            )

            result = await service.recognize_intent("Perform custom action on test.txt")
            assert result is not None
            assert result.intent == "custom_action"
            assert "test.txt" in result.parameters.get("target", "")

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_get_supported_intents(self):
        """Test getting supported intents."""
        service = IntentRecognitionService()
        await service.start()

        try:
            intents = service.get_supported_intents()
            assert isinstance(intents, list)
            assert len(intents) > 0
            assert "file_read" in intents
            assert "file_write" in intents
            assert "help" in intents
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_remove_intent(self):
        """Test removing intent patterns."""
        service = IntentRecognitionService()
        await service.start()

        try:
            # Add custom intent
            service.add_custom_intent("test_intent", ["test pattern"], [])

            # Verify it exists
            intents = service.get_supported_intents()
            assert "test_intent" in intents

            # Remove intent
            removed = service.remove_intent("test_intent")
            assert removed is True

            # Verify it's gone
            intents = service.get_supported_intents()
            assert "test_intent" not in intents

            # Try removing non-existent intent
            removed = service.remove_intent("non_existent")
            assert removed is False

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_service_metrics(self):
        """Test service metrics collection."""
        service = IntentRecognitionService()
        await service.start()

        try:
            # Perform some operations
            await service.recognize_intent("test input")
            await service.batch_recognize_intents(["test1", "test2"])

            # Get metrics
            metrics = service.get_metrics()
            assert metrics["requests_processed"] == 3
            assert metrics["cache_hit_rate"] >= 0.0
            assert metrics["supported_intents"] > 0
            assert metrics["active_strategies"] == 3
            assert "cache_enabled" in metrics

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_caching_enabled(self):
        """Test that caching is enabled by default."""
        service = IntentRecognitionService()
        await service.start()

        try:
            # First request
            result1 = await service.recognize_intent("test input")
            assert result1 is not None

            # Second request (should use cache)
            result2 = await service.recognize_intent("test input")
            assert result2 is not None

            # Check cache metrics
            metrics = service.get_metrics()
            assert metrics["cache_hit_rate"] > 0

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_caching_disabled(self):
        """Test service with caching disabled."""
        service = IntentRecognitionService(enable_caching=False)
        await service.start()

        try:
            # First request
            result1 = await service.recognize_intent("test input")
            assert result1 is not None

            # Second request (no cache)
            result2 = await service.recognize_intent("test input")
            assert result2 is not None

            # Check cache metrics
            metrics = service.get_metrics()
            assert metrics["cache_enabled"] is False
            assert metrics["cache_hit_rate"] == 0.0

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_add_custom_strategy(self):
        """Test adding custom recognition strategy."""
        service = IntentRecognitionService()
        await service.start()

        try:
            # Add custom strategy
            custom_strategy = MagicMock()
            custom_strategy.get_strategy_name.return_value = "custom"
            custom_strategy.recognize = AsyncMock(
                return_value=IntentRecognitionResult(
                    intent="custom",
                    confidence=0.9,
                    strategy_used="custom"
                )
            )

            service.add_strategy(custom_strategy)

            # Verify strategy was added
            assert len(service._strategies) == 4  # 3 default + 1 custom

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_remove_strategy(self):
        """Test removing recognition strategy."""
        service = IntentRecognitionService()
        await service.start()

        try:
            # Remove default strategy (should fail)
            removed = service.remove_strategy("keyword_matching")
            assert removed is False

            # Add custom strategy and remove it
            custom_strategy = MagicMock()
            custom_strategy.get_strategy_name.return_value = "custom"
            service.add_strategy(custom_strategy)

            removed = service.remove_strategy("custom")
            assert removed is True

            # Verify it was removed
            assert len(service._strategies) == 3  # Back to 3 default

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self):
        """Test error handling when service is not running."""
        service = IntentRecognitionService()

        # Should raise error when not running
        with pytest.raises(RuntimeError, match="not running"):
            await service.recognize_intent("test")

        with pytest.raises(RuntimeError, match="not running"):
            await service.batch_recognize_intents(["test"])

    @pytest.mark.asyncio
    async def test_unknown_intent_fallback(self):
        """Test fallback to unknown intent."""
        service = IntentRecognitionService(confidence_threshold=0.99)  # Very high threshold
        await service.start()

        try:
            result = await service.recognize_intent("xyz123abc")  # Unrecognizable
            assert result is not None
            assert result.intent == "unknown"
            assert result.confidence == 0.0
            assert result.strategy_used == "fallback"

        finally:
            await service.stop()