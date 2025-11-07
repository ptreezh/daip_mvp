"""Intent Recognition Service implementation."""

import asyncio
import logging
import re
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from .interfaces import (
    IIntentRecognitionService,
    IntentRecognitionResult,
    IDomainService
)

logger = logging.getLogger(__name__)


@dataclass
class IntentPattern:
    """Represents an intent pattern with associated information."""
    intent: str
    patterns: List[str]
    parameters: List[str]
    description: str = ""
    confidence_weight: float = 1.0


class IntentRecognitionStrategy(ABC):
    """Abstract base class for intent recognition strategies."""

    @abstractmethod
    async def recognize(
        self,
        input_text: str,
        patterns: List[IntentPattern],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[IntentRecognitionResult]:
        """
        Recognize intent using this strategy.

        Args:
            input_text: Input text to analyze
            patterns: List of intent patterns
            context: Optional context

        Returns:
            Intent recognition result or None
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass


class KeywordMatchingStrategy(IntentRecognitionStrategy):
    """Keyword-based intent recognition strategy."""

    def __init__(self, confidence_threshold: float = 0.3):
        """
        Initialize keyword matching strategy.

        Args:
            confidence_threshold: Minimum confidence threshold
        """
        self.confidence_threshold = confidence_threshold

    async def recognize(
        self,
        input_text: str,
        patterns: List[IntentPattern],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[IntentRecognitionResult]:
        """Recognize intent using keyword matching."""
        input_lower = input_text.lower()
        best_match = None
        best_confidence = 0.0

        for pattern in patterns:
            matches = 0
            total_keywords = 0
            parameters = {}

            for pattern_str in pattern.patterns:
                pattern_lower = pattern_str.lower()

                # Count keyword matches
                words = re.findall(r'\b\w+\b', pattern_lower)
                total_keywords += len(words)

                for word in words:
                    if word in input_lower:
                        matches += 1

                # Extract parameters using named groups
                param_matches = re.findall(pattern_str, input_text, re.IGNORECASE)
                if param_matches and pattern.parameters:
                    for i, param in enumerate(pattern.parameters):
                        if i < len(param_matches) and param_matches[i]:
                            if isinstance(param_matches[i], tuple):
                                # Handle multiple capture groups
                                for j, value in enumerate(param_matches[i]):
                                    if j < len(pattern.parameters):
                                        parameters[pattern.parameters[j]] = value
                            else:
                                parameters[param] = param_matches[i]

            if total_keywords > 0:
                confidence = (matches / total_keywords) * pattern.confidence_weight

                if confidence > best_confidence and confidence >= self.confidence_threshold:
                    best_confidence = confidence
                    best_match = pattern

        if best_match:
            return IntentRecognitionResult(
                intent=best_match.intent,
                confidence=best_confidence,
                parameters=parameters,
                reasoning=f"Keyword matching: {best_confidence:.2f} confidence",
                strategy_used=self.get_strategy_name()
            )

        return None

    def get_strategy_name(self) -> str:
        return "keyword_matching"


class RegexStrategy(IntentRecognitionStrategy):
    """Regex-based intent recognition strategy."""

    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize regex strategy.

        Args:
            confidence_threshold: Minimum confidence threshold
        """
        self.confidence_threshold = confidence_threshold

    async def recognize(
        self,
        input_text: str,
        patterns: List[IntentPattern],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[IntentRecognitionResult]:
        """Recognize intent using regex patterns."""
        best_match = None
        best_confidence = 0.0

        for pattern in patterns:
            for pattern_str in pattern.patterns:
                try:
                    match = re.search(pattern_str, input_text, re.IGNORECASE)
                    if match:
                        # Calculate confidence based on match quality
                        match_length = len(match.group(0))
                        total_length = len(input_text)
                        confidence = min(0.9, (match_length / total_length) * pattern.confidence_weight)

                        # Extract parameters
                        parameters = {}
                        if pattern.parameters:
                            groups = match.groups()
                            for i, param in enumerate(pattern.parameters):
                                if i < len(groups):
                                    parameters[param] = groups[i]

                        if confidence > best_confidence and confidence >= self.confidence_threshold:
                            best_confidence = confidence
                            best_match = pattern

                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{pattern_str}': {e}")

        if best_match:
            return IntentRecognitionResult(
                intent=best_match.intent,
                confidence=best_confidence,
                parameters=parameters,
                reasoning=f"Regex matching: {best_confidence:.2f} confidence",
                strategy_used=self.get_strategy_name()
            )

        return None

    def get_strategy_name(self) -> str:
        return "regex_matching"


class MLBasedStrategy(IntentRecognitionStrategy):
    """Mock ML-based intent recognition strategy (placeholder for future implementation)."""

    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize ML-based strategy.

        Args:
            confidence_threshold: Minimum confidence threshold
        """
        self.confidence_threshold = confidence_threshold

    async def recognize(
        self,
        input_text: str,
        patterns: List[IntentPattern],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[IntentRecognitionResult]:
        """
        Mock ML-based recognition.

        In a real implementation, this would use actual ML models.
        """
        # Simple heuristic based on text characteristics as placeholder
        text_lower = input_text.lower()

        # Determine intent based on keywords and patterns
        intent_scores = defaultdict(float)

        # Check for question patterns
        if any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            intent_scores['question'] += 0.8

        # Check for command patterns
        if any(word in text_lower for word in ['create', 'delete', 'update', 'list', 'show', 'run', 'execute']):
            intent_scores['command'] += 0.7

        # Check for file operations
        if any(word in text_lower for word in ['file', 'read', 'write', 'save', 'open']):
            intent_scores['file_operation'] += 0.8

        # Check for search patterns
        if any(word in text_lower for word in ['search', 'find', 'look for', 'get']):
            intent_scores['search'] += 0.7

        # Find best scoring intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            if best_intent[1] >= self.confidence_threshold:
                return IntentRecognitionResult(
                    intent=best_intent[0],
                    confidence=best_intent[1],
                    parameters={},
                    reasoning=f"ML-based classification: {best_intent[1]:.2f} confidence",
                    strategy_used=self.get_strategy_name()
                )

        return None

    def get_strategy_name(self) -> str:
        return "ml_based"


class IntentCache:
    """Simple cache for intent recognition results."""

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300.0):
        """
        Initialize intent cache.

        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time to live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[IntentRecognitionResult, float]] = {}

    def get(self, key: str) -> Optional[IntentRecognitionResult]:
        """Get cached result."""
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return result
            else:
                del self._cache[key]
        return None

    def put(self, key: str, result: IntentRecognitionResult) -> None:
        """Cache result."""
        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[key] = (result, time.time())

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()


class IntentRecognitionService(IIntentRecognitionService):
    """
    Intent Recognition Service implementation.

    This service uses multiple strategies to recognize user intents from input text,
    with confidence scoring and parameter extraction.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enable_caching: bool = True,
        cache_size: int = 1000,
        cache_ttl: float = 300.0
    ):
        """
        Initialize intent recognition service.

        Args:
            confidence_threshold: Minimum confidence threshold for acceptance
            enable_caching: Whether to enable result caching
            cache_size: Maximum cache size
            cache_ttl: Cache TTL in seconds
        """
        self.confidence_threshold = confidence_threshold
        self.enable_caching = enable_caching
        self._strategies: List[IntentRecognitionStrategy] = []
        self._patterns: List[IntentPattern] = []
        self._pattern_map: Dict[str, IntentPattern] = {}
        self._cache = IntentCache(cache_size, cache_ttl) if enable_caching else None
        self._running = False
        self._metrics = {
            "requests_processed": 0,
            "cache_hits": 0,
            "strategy_usage": defaultdict(int),
            "intent_counts": defaultdict(int),
            "avg_confidence": 0.0,
            "processing_time_total": 0.0
        }

        # Initialize default strategies
        self._initialize_default_strategies()
        self._initialize_default_patterns()

    def _initialize_default_strategies(self) -> None:
        """Initialize default recognition strategies."""
        self._strategies = [
            KeywordMatchingStrategy(confidence_threshold=0.3),
            RegexStrategy(confidence_threshold=0.5),
            MLBasedStrategy(confidence_threshold=0.6)
        ]

    def _initialize_default_patterns(self) -> None:
        """Initialize default intent patterns."""
        default_patterns = [
            IntentPattern(
                intent="file_read",
                patterns=[
                    r"read (?:file|document) (.+)",
                    r"open (?:file|document) (.+)",
                    r"show (?:file|document|content of) (.+)",
                    r"what'?s in (.+)",
                    r"display (.+)"
                ],
                parameters=["file_path"],
                description="Read a file or document"
            ),
            IntentPattern(
                intent="file_write",
                patterns=[
                    r"write (?:to )?(.+)",
                    r"save (?:to )?(.+)",
                    r"create (?:file|document) (.+)",
                    r"put (.+) in (.+)"
                ],
                parameters=["file_path", "content"],
                description="Write to a file or document"
            ),
            IntentPattern(
                intent="file_delete",
                patterns=[
                    r"delete (?:file|document) (.+)",
                    r"remove (?:file|document) (.+)",
                    r"get rid of (.+)"
                ],
                parameters=["file_path"],
                description="Delete a file or document"
            ),
            IntentPattern(
                intent="tool_execute",
                patterns=[
                    r"run (.+)",
                    r"execute (.+)",
                    r"use (.+)",
                    r"call (.+)"
                ],
                parameters=["tool_name"],
                description="Execute a tool or command"
            ),
            IntentPattern(
                intent="search",
                patterns=[
                    r"search (?:for )?(.+)",
                    r"find (.+)",
                    r"look for (.+)",
                    r"where is (.+)"
                ],
                parameters=["query"],
                description="Search for information"
            ),
            IntentPattern(
                intent="question",
                patterns=[
                    r"what (?:is|are) (.+)",
                    r"how (?:do|does|can|to) (.+)",
                    r"why (?:do|does|is) (.+)",
                    r"when (?:do|does|is) (.+)",
                    r"where (?:is|are) (.+)",
                    r"who (?:is|are) (.+)"
                ],
                parameters=["question"],
                description="Ask a question"
            ),
            IntentPattern(
                intent="help",
                patterns=[
                    r"help",
                    r"how do i (.+)",
                    r"show me how to (.+)",
                    r"what can you do"
                ],
                parameters=["topic"],
                description="Request help or assistance"
            ),
            IntentPattern(
                intent="list_files",
                patterns=[
                    r"list (?:files|directory|folder) (.+)",
                    r"show (?:files|directory|folder) (.+)",
                    r"what'?s in (.+)",
                    r"ls (.+)",
                    r"dir (.+)"
                ],
                parameters=["directory_path"],
                description="List files in a directory"
            )
        ]

        for pattern in default_patterns:
            self.add_custom_intent(
                pattern.intent,
                pattern.patterns,
                pattern.parameters
            )

    async def start(self) -> None:
        """Start the intent recognition service."""
        if self._running:
            return

        self._running = True
        logger.info("IntentRecognitionService started")

    async def stop(self) -> None:
        """Stop the intent recognition service."""
        if not self._running:
            return

        self._running = False
        if self._cache:
            self._cache.clear()
        logger.info("IntentRecognitionService stopped")

    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return self._running and len(self._strategies) > 0

    async def recognize_intent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentRecognitionResult:
        """
        Recognize the intent from input text.

        Args:
            input_text: The input text to analyze
            context: Optional context information

        Returns:
            Intent recognition result with confidence and parameters
        """
        if not self._running:
            raise RuntimeError("IntentRecognitionService is not running")

        start_time = time.time()
        self._metrics["requests_processed"] += 1

        # Check cache first
        cache_key = f"{input_text}:{hash(str(context))}"
        if self._cache:
            cached_result = self._cache.get(cache_key)
            if cached_result:
                self._metrics["cache_hits"] += 1
                self._metrics["processing_time_total"] += time.time() - start_time
                return cached_result

        best_result = None
        best_confidence = 0.0

        # Try each strategy
        for strategy in self._strategies:
            try:
                result = await strategy.recognize(input_text, self._patterns, context)
                if result and result.confidence > best_confidence:
                    best_result = result
                    best_confidence = result.confidence
                    self._metrics["strategy_usage"][strategy.get_strategy_name()] += 1
            except Exception as e:
                logger.error(f"Strategy {strategy.get_strategy_name()} failed: {e}")

        # Ensure minimum confidence threshold
        if best_result and best_result.confidence < self.confidence_threshold:
            logger.debug(f"Intent confidence {best_result.confidence:.2f} below threshold {self.confidence_threshold}")
            best_result = None

        # Fall back to unknown intent if no match
        if not best_result:
            best_result = IntentRecognitionResult(
                intent="unknown",
                confidence=0.0,
                parameters={},
                reasoning="No intent pattern matched",
                strategy_used="fallback"
            )

        # Update metrics
        self._metrics["intent_counts"][best_result.intent] += 1
        total_time = time.time() - start_time
        self._metrics["processing_time_total"] += total_time
        self._metrics["avg_confidence"] = (
            (self._metrics["avg_confidence"] * (self._metrics["requests_processed"] - 1) + best_result.confidence) /
            self._metrics["requests_processed"]
        )

        # Cache result
        if self._cache:
            self._cache.put(cache_key, best_result)

        logger.debug(f"Recognized intent '{best_result.intent}' with confidence {best_result.confidence:.2f}")
        return best_result

    async def batch_recognize_intents(
        self,
        inputs: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[IntentRecognitionResult]:
        """
        Recognize intents for multiple inputs.

        Args:
            inputs: List of input texts
            context: Optional context information

        Returns:
            List of intent recognition results
        """
        if not self._running:
            raise RuntimeError("IntentRecognitionService is not running")

        # Process in parallel for better performance
        tasks = [
            self.recognize_intent(input_text, context)
            for input_text in inputs
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing input {i}: {result}")
                processed_results.append(IntentRecognitionResult(
                    intent="error",
                    confidence=0.0,
                    parameters={"error": str(result)},
                    reasoning="Processing error occurred"
                ))
            else:
                processed_results.append(result)

        return processed_results

    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents."""
        return list(self._pattern_map.keys())

    def add_custom_intent(
        self,
        intent: str,
        patterns: List[str],
        parameters: Optional[List[str]] = None
    ) -> None:
        """
        Add a custom intent pattern.

        Args:
            intent: Intent name
            patterns: Pattern strings that match this intent
            parameters: List of parameter names to extract
        """
        pattern = IntentPattern(
            intent=intent,
            patterns=patterns,
            parameters=parameters or []
        )

        self._patterns.append(pattern)
        self._pattern_map[intent] = pattern

        # Clear cache to ensure new patterns are used
        if self._cache:
            self._cache.clear()

        logger.info(f"Added custom intent '{intent}' with {len(patterns)} patterns")

    def remove_intent(self, intent: str) -> bool:
        """
        Remove an intent pattern.

        Args:
            intent: Intent name to remove

        Returns:
            True if intent was removed, False if not found
        """
        if intent not in self._pattern_map:
            return False

        pattern = self._pattern_map[intent]
        self._patterns.remove(pattern)
        del self._pattern_map[intent]

        # Clear cache
        if self._cache:
            self._cache.clear()

        logger.info(f"Removed intent '{intent}'")
        return True

    def add_strategy(self, strategy: IntentRecognitionStrategy) -> None:
        """Add a custom recognition strategy."""
        self._strategies.append(strategy)
        logger.info(f"Added recognition strategy '{strategy.get_strategy_name()}'")

    def remove_strategy(self, strategy_name: str) -> bool:
        """Remove a recognition strategy by name."""
        for i, strategy in enumerate(self._strategies):
            if strategy.get_strategy_name() == strategy_name:
                self._strategies.pop(i)
                logger.info(f"Removed recognition strategy '{strategy_name}'")
                return True
        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            **self._metrics,
            "cache_hit_rate": (
                self._metrics["cache_hits"] / self._metrics["requests_processed"]
                if self._metrics["requests_processed"] > 0 else 0.0
            ),
            "avg_processing_time_ms": (
                (self._metrics["processing_time_total"] / self._metrics["requests_processed"]) * 1000
                if self._metrics["requests_processed"] > 0 else 0.0
            ),
            "supported_intents": len(self._pattern_map),
            "active_strategies": len(self._strategies),
            "cache_enabled": self.enable_caching
        }