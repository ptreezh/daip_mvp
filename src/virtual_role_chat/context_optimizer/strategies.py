"""Optimization strategies for the Task Context Optimizer.

This module implements various strategies for task detection, context prioritization,
compression, and blending to optimize context preparation for LLM interactions.
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .models import (
    ContextElement,
    ContextOptimizationConfig,
    ElementType,
    OptimizedContext,
    TaskDetectionResult,
    TaskType,
)


class TaskDetectionStrategy(ABC):
    """Abstract base class for task detection strategies.
    """

    @abstractmethod
    def detect_task(self, messages: List[Dict[str, Any]], context: Dict[str, Any]) -> TaskDetectionResult:
        """Detect the task type and requirements from messages and context.
        
        Args:
            messages: List of conversation messages
            context: Additional context information
            
        Returns:
            Task detection result

        """
        pass


class PatternBasedTaskDetection(TaskDetectionStrategy):
    """Task detection strategy based on pattern matching.
    """

    def __init__(self):
        """Initialize the pattern-based task detection strategy."""
        self.logger = logging.getLogger(__name__)
        self.task_patterns = self._initialize_task_patterns()

    def _initialize_task_patterns(self) -> Dict[TaskType, List[str]]:
        """Initialize task detection patterns.
        
        Returns:
            Dictionary mapping task types to detection patterns

        """
        return {
            TaskType.INFORMATION_RETRIEVAL: [
                r'\b(what is|who is|when did|where is|how many|tell me about|find|search|lookup)\b',
                r'\b(information about|details on|facts about|data on)\b',
                r'\?(.*)(definition|meaning)\b'
            ],
            TaskType.EXPLANATION: [
                r'\b(explain|describe|how does|why does|what causes|help me understand)\b',
                r'\b(walk me through|break down|clarify|elaborate)\b',
                r'\b(how to|step by step|process of)\b',
                r'\b(neural networks|machine learning|deep learning)\b'
            ],
            TaskType.PROBLEM_SOLVING: [
                r'\b(solve|fix|troubleshoot|resolve|debug|repair)\b',
                r'\b(problem with|issue with|error|bug|not working)\b',
                r'\b(how can I|what should I do|need help with)\b'
            ],
            TaskType.DECISION_SUPPORT: [
                r'\b(should I|which is better|help me decide|recommend|suggest)\b',
                r'\b(pros and cons|compare|evaluate|choose between)\b',
                r'\b(best option|what would you|advice|guidance)\b'
            ],
            TaskType.CREATIVE_IDEATION: [
                r'\b(brainstorm|generate ideas|creative|innovative|think of)\b',
                r'\b(come up with|invent|design|create|imagine)\b',
                r'\b(alternatives|possibilities|options|variations)\b'
            ]
        }

    def detect_task(self, messages: List[Dict[str, Any]], context: Dict[str, Any]) -> TaskDetectionResult:
        """Detect task type using pattern matching.
        
        Args:
            messages: List of conversation messages
            context: Additional context information
            
        Returns:
            Task detection result

        """
        # Extract text from messages
        text_content = self._extract_text_content(messages)

        # Score each task type
        task_scores = {}
        for task_type, patterns in self.task_patterns.items():
            score = self._calculate_pattern_score(text_content, patterns)
            if score > 0:
                task_scores[task_type] = score

        # Determine best match
        if not task_scores:
            return TaskDetectionResult(
                task_type=TaskType.UNKNOWN,
                confidence=0.0,
                task_description="Unable to determine task type"
            )

        best_task_type = max(task_scores.items(), key=lambda x: x[1])
        task_type, confidence = best_task_type

        return TaskDetectionResult(
            task_type=task_type,
            confidence=min(confidence, 1.0),
            task_description=text_content[:100] if text_content else f"{task_type.value} task detected"
        )

    def _extract_text_content(self, messages: List[Dict[str, Any]]) -> str:
        """Extract text content from messages."""
        text_parts = []
        for message in messages:
            if isinstance(message, dict):
                if 'content' in message:
                    text_parts.append(str(message['content']))
                elif 'message' in message:
                    text_parts.append(str(message['message']))
            elif isinstance(message, str):
                text_parts.append(message)

        return ' '.join(text_parts).lower()

    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """Calculate pattern matching score for a task type."""
        total_matches = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            total_matches += matches

        text_length = len(text.split())
        if text_length == 0:
            return 0.0

        score = min(total_matches / max(text_length * 0.1, 1), 1.0)
        return score


class ContextPrioritizationStrategy(ABC):
    """Abstract base class for context prioritization strategies.
    """

    @abstractmethod
    def prioritize_elements(
        self,
        elements: List[ContextElement],
        task_result: TaskDetectionResult,
        config: ContextOptimizationConfig
    ) -> List[ContextElement]:
        """Prioritize context elements based on task requirements.
        
        Args:
            elements: List of context elements to prioritize
            task_result: Task detection result
            config: Optimization configuration
            
        Returns:
            Prioritized list of context elements

        """
        pass


class RelevanceBasedPrioritization(ContextPrioritizationStrategy):
    """Context prioritization strategy based on relevance scoring.
    """

    def __init__(self):
        """Initialize the relevance-based prioritization strategy."""
        self.logger = logging.getLogger(__name__)

    def prioritize_elements(
        self,
        elements: List[ContextElement],
        task_result: TaskDetectionResult,
        config: ContextOptimizationConfig
    ) -> List[ContextElement]:
        """Prioritize elements based on relevance to the task.
        
        Args:
            elements: List of context elements to prioritize
            task_result: Task detection result
            config: Optimization configuration
            
        Returns:
            Prioritized list of context elements

        """
        # Calculate enhanced relevance scores
        for element in elements:
            element.relevance_score = self._calculate_enhanced_relevance(
                element, task_result, config
            )

        # Sort by priority score
        prioritized = sorted(elements, key=lambda e: e.get_priority_score(), reverse=True)

        return prioritized

    def _calculate_enhanced_relevance(
        self,
        element: ContextElement,
        task_result: TaskDetectionResult,
        config: ContextOptimizationConfig
    ) -> float:
        """Calculate enhanced relevance score considering task context.
        
        Args:
            element: Context element to score
            task_result: Task detection result
            config: Optimization configuration
            
        Returns:
            Enhanced relevance score (0.0-1.0)

        """
        base_relevance = element.relevance_score

        # Task type specific adjustments
        task_weights = config.task_specific_weights.get(task_result.task_type, {})
        type_adjustment = task_weights.get(element.element_type.value, 1.0)

        # Domain relevance adjustment
        domain_adjustment = 1.0
        if task_result.domain and element.metadata.get('domain'):
            if task_result.domain == element.metadata['domain']:
                domain_adjustment = 1.2

        # Combine adjustments
        enhanced_relevance = base_relevance * type_adjustment * domain_adjustment

        return min(enhanced_relevance, 1.0)


class ContextCompressionStrategy(ABC):
    """Abstract base class for context compression strategies.
    """

    @abstractmethod
    def compress_context(
        self,
        elements: List[ContextElement],
        target_tokens: int,
        config: ContextOptimizationConfig
    ) -> List[ContextElement]:
        """Compress context to fit within token limits.
        
        Args:
            elements: List of context elements to compress
            target_tokens: Target token count
            config: Optimization configuration
            
        Returns:
            Compressed list of context elements

        """
        pass


class SmartTruncationCompression(ContextCompressionStrategy):
    """Context compression strategy using smart truncation.
    """

    def __init__(self):
        """Initialize the smart truncation compression strategy."""
        self.logger = logging.getLogger(__name__)

    def compress_context(
        self,
        elements: List[ContextElement],
        target_tokens: int,
        config: ContextOptimizationConfig
    ) -> List[ContextElement]:
        """Compress context using smart truncation strategies.
        
        Args:
            elements: List of context elements to compress
            target_tokens: Target token count
            config: Optimization configuration
            
        Returns:
            Compressed list of context elements

        """
        if not elements:
            return elements

        # Calculate current token count
        current_tokens = sum(element.token_count for element in elements)

        if current_tokens <= target_tokens:
            return elements

        # Remove low-relevance elements
        compressed_elements = self._remove_low_relevance_elements(
            elements, target_tokens, config
        )

        return compressed_elements

    def _remove_low_relevance_elements(
        self,
        elements: List[ContextElement],
        target_tokens: int,
        config: ContextOptimizationConfig
    ) -> List[ContextElement]:
        """Remove elements with low relevance scores.
        
        Args:
            elements: List of elements
            target_tokens: Target token count
            config: Optimization configuration
            
        Returns:
            Filtered list of elements

        """
        # Sort by priority score
        sorted_elements = sorted(elements, key=lambda e: e.get_priority_score(), reverse=True)

        # Keep elements until we reach the target
        kept_elements = []
        current_tokens = 0

        for element in sorted_elements:
            if current_tokens + element.token_count <= target_tokens:
                kept_elements.append(element)
                current_tokens += element.token_count
            elif element.relevance_score >= config.min_relevance_threshold:
                # Keep high-relevance elements even if they exceed the limit slightly
                kept_elements.append(element)
                break

        return kept_elements


class ContextBlendingStrategy(ABC):
    """Abstract base class for context blending strategies.
    """

    @abstractmethod
    def blend_context_sources(
        self,
        task_instructions: str,
        background_knowledge: List[str],
        conversation_history: List[Dict[str, Any]],
        max_tokens: int,
        config: ContextOptimizationConfig
    ) -> OptimizedContext:
        """Blend multiple context sources into an optimized context.
        
        Args:
            task_instructions: Task-specific instructions
            background_knowledge: Background knowledge items
            conversation_history: Conversation history
            max_tokens: Maximum token count
            config: Optimization configuration
            
        Returns:
            Optimized context

        """
        pass


class ProportionalBlending(ContextBlendingStrategy):
    """Context blending strategy that allocates tokens proportionally.
    """

    def __init__(self):
        """Initialize the proportional blending strategy."""
        self.logger = logging.getLogger(__name__)

    def blend_context_sources(
        self,
        task_instructions: str,
        background_knowledge: List[str],
        conversation_history: List[Dict[str, Any]],
        max_tokens: int,
        config: ContextOptimizationConfig
    ) -> OptimizedContext:
        """Blend context sources using proportional allocation.
        
        Args:
            task_instructions: Task-specific instructions
            background_knowledge: Background knowledge items
            conversation_history: Conversation history
            max_tokens: Maximum token count
            config: Optimization configuration
            
        Returns:
            Optimized context

        """
        # Define proportional allocation
        allocation = {
            'instructions': 0.3,  # 30% for instructions
            'knowledge': 0.4,     # 40% for background knowledge
            'conversation': 0.3   # 30% for conversation history
        }

        # Calculate token allocations
        instruction_tokens = int(max_tokens * allocation['instructions'])
        knowledge_tokens = int(max_tokens * allocation['knowledge'])
        conversation_tokens = int(max_tokens * allocation['conversation'])

        # Create context elements
        elements = []

        # Add task instructions
        if task_instructions:
            elements.append(ContextElement(
                id="task_instructions",
                content=task_instructions,
                element_type=ElementType.INSTRUCTION,
                relevance_score=1.0,
                importance=1.0,
                token_count=min(self._estimate_tokens(task_instructions), instruction_tokens),
                source="task_detection"
            ))

        # Add background knowledge
        for i, knowledge in enumerate(background_knowledge):
            if sum(e.token_count for e in elements if e.element_type == ElementType.KNOWLEDGE) < knowledge_tokens:
                remaining_tokens = knowledge_tokens - sum(e.token_count for e in elements if e.element_type == ElementType.KNOWLEDGE)
                token_count = min(self._estimate_tokens(knowledge), remaining_tokens)

                if token_count > 0:
                    elements.append(ContextElement(
                        id=f"knowledge_{i}",
                        content=knowledge,
                        element_type=ElementType.KNOWLEDGE,
                        relevance_score=0.8,
                        importance=0.7,
                        token_count=token_count,
                        source="background_knowledge"
                    ))

        # Calculate metrics
        total_tokens = sum(element.token_count for element in elements)
        compression_ratio = total_tokens / max_tokens if max_tokens > 0 else 1.0

        return OptimizedContext(
            elements=elements,
            total_tokens=total_tokens,
            task_focus=task_instructions,
            optimization_metrics={
                'compression_ratio': compression_ratio,
                'element_count': len(elements)
            },
            compression_ratio=compression_ratio,
            optimization_strategy="proportional_blending"
        )

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count

        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
