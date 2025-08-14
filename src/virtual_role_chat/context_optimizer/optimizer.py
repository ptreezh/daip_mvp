"""Main TaskContextOptimizer implementation.

This module implements the core TaskContextOptimizer class that provides
task-focused context optimization integrated at the lowest level of LLM interactions.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from .models import (
    ContextAnalysisResult,
    ContextElement,
    ContextOptimizationConfig,
    ElementType,
    OptimizedContext,
    TaskDetectionResult,
    TaskRequirement,
    TaskType,
)
from .strategies import (
    ContextBlendingStrategy,
    ContextCompressionStrategy,
    ContextPrioritizationStrategy,
    PatternBasedTaskDetection,
    ProportionalBlending,
    RelevanceBasedPrioritization,
    SmartTruncationCompression,
    TaskDetectionStrategy,
)


class TaskContextOptimizer:
    """Core task context optimizer that provides automatic context optimization
    for all LLM interactions.
    
    This optimizer is designed to be integrated at the lowest level of LLM
    interfaces, automatically detecting tasks and optimizing context preparation
    without requiring explicit optimization requests from higher-level components.
    """

    def __init__(
        self,
        config: Optional[ContextOptimizationConfig] = None,
        task_detection_strategy: Optional[TaskDetectionStrategy] = None,
        prioritization_strategy: Optional[ContextPrioritizationStrategy] = None,
        compression_strategy: Optional[ContextCompressionStrategy] = None,
        blending_strategy: Optional[ContextBlendingStrategy] = None
    ):
        """Initialize the task context optimizer.
        
        Args:
            config: Optimization configuration
            task_detection_strategy: Strategy for task detection
            prioritization_strategy: Strategy for context prioritization
            compression_strategy: Strategy for context compression
            blending_strategy: Strategy for context blending

        """
        self.config = config or ContextOptimizationConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize strategies
        self.task_detection_strategy = task_detection_strategy or PatternBasedTaskDetection()
        self.prioritization_strategy = prioritization_strategy or RelevanceBasedPrioritization()
        self.compression_strategy = compression_strategy or SmartTruncationCompression()
        self.blending_strategy = blending_strategy or ProportionalBlending()

        # Performance tracking
        self.optimization_stats = {
            'total_optimizations': 0,
            'total_processing_time': 0.0,
            'average_compression_ratio': 0.0,
            'task_type_distribution': {}
        }

        self.logger.info("TaskContextOptimizer initialized")

    def optimize_context_for_task(
        self,
        context: List[Dict[str, Any]],
        task: str,
        max_tokens: int
    ) -> OptimizedContext:
        """Optimize context for a specific task.
        
        Args:
            context: List of context messages/elements
            task: Task description or query
            max_tokens: Maximum token count for optimized context
            
        Returns:
            Optimized context

        """
        start_time = time.time()

        try:
            # Convert context to messages format for task detection
            messages = self._convert_context_to_messages(context)

            # Detect task type and requirements
            task_result = self.task_detection_strategy.detect_task(
                messages, {'task_description': task}
            )

            # Convert context to context elements
            context_elements = self._convert_to_context_elements(context, task_result)

            # Analyze context before optimization
            analysis = self._analyze_context(context_elements)

            # Prioritize context elements
            prioritized_elements = self.prioritization_strategy.prioritize_elements(
                context_elements, task_result, self.config
            )

            # Compress context if needed
            compressed_elements = self.compression_strategy.compress_context(
                prioritized_elements, max_tokens, self.config
            )

            # Create optimized context
            optimized_context = self._create_optimized_context(
                compressed_elements, task_result, analysis, start_time
            )

            # Update statistics
            self._update_stats(task_result, optimized_context, time.time() - start_time)

            self.logger.info(f"Context optimized for {task_result.task_type.value} task: "
                           f"{len(context_elements)} -> {len(compressed_elements)} elements, "
                           f"{analysis.total_tokens} -> {optimized_context.total_tokens} tokens")

            return optimized_context

        except Exception as e:
            self.logger.error(f"Error optimizing context: {e}")
            # Return a basic optimized context as fallback
            return self._create_fallback_context(context, task, max_tokens)

    def extract_task_requirements(self, task: str) -> List[TaskRequirement]:
        """Extract task requirements from a task description.
        
        Args:
            task: Task description
            
        Returns:
            List of extracted task requirements

        """
        # Convert task to messages format
        messages = [{'content': task}]

        # Detect task and extract requirements
        task_result = self.task_detection_strategy.detect_task(messages, {})

        return task_result.requirements

    def prioritize_context_elements(
        self,
        context_elements: List[Dict[str, Any]],
        task_requirements: List[TaskRequirement]
    ) -> List[Dict[str, Any]]:
        """Prioritize context elements based on task requirements.
        
        Args:
            context_elements: List of context elements
            task_requirements: List of task requirements
            
        Returns:
            Prioritized list of context elements

        """
        # Convert to ContextElement objects
        elements = []
        for i, element in enumerate(context_elements):
            elements.append(ContextElement(
                id=f"element_{i}",
                content=str(element.get('content', element)),
                element_type=ElementType.KNOWLEDGE,  # Default type
                relevance_score=0.5,
                importance=0.5,
                token_count=len(str(element).split()),
                source="context"
            ))

        # Create a mock task result
        task_result = TaskDetectionResult(
            task_type=TaskType.UNKNOWN,
            confidence=0.5,
            task_description="Unknown task",
            requirements=task_requirements
        )

        # Prioritize elements
        prioritized_elements = self.prioritization_strategy.prioritize_elements(
            elements, task_result, self.config
        )

        # Convert back to dictionary format
        return [{'content': element.content, 'priority': element.get_priority_score()}
                for element in prioritized_elements]

    def blend_context_sources(
        self,
        task_instructions: str,
        background_knowledge: List[str],
        conversation_history: List[Dict[str, Any]],
        max_tokens: int
    ) -> OptimizedContext:
        """Blend multiple context sources into an optimized context.
        
        Args:
            task_instructions: Task-specific instructions
            background_knowledge: Background knowledge items
            conversation_history: Conversation history
            max_tokens: Maximum token count
            
        Returns:
            Optimized context

        """
        return self.blending_strategy.blend_context_sources(
            task_instructions, background_knowledge, conversation_history, max_tokens, self.config
        )

    def maintain_task_coherence(
        self,
        context: List[Dict[str, Any]],
        task: str
    ) -> List[Dict[str, Any]]:
        """Maintain task coherence by preserving causal relationships and dependencies.
        
        Args:
            context: List of context elements
            task: Task description
            
        Returns:
            Context with maintained coherence

        """
        # This is a simplified implementation
        # In a real system, this would analyze dependencies and causal relationships

        # For now, just ensure the most relevant elements are preserved
        optimized = self.optimize_context_for_task(context, task, self.config.max_tokens)

        return [{'content': element.content} for element in optimized.elements]

    def delineate_task_boundaries(
        self,
        context: List[Dict[str, Any]],
        current_task: str
    ) -> List[Dict[str, Any]]:
        """Delineate task boundaries and prioritize the current active task.
        
        Args:
            context: List of context elements
            current_task: Current active task
            
        Returns:
            Context with delineated task boundaries

        """
        # Detect the current task
        messages = [{'content': current_task}]
        task_result = self.task_detection_strategy.detect_task(messages, {})

        # Filter context elements that are relevant to the current task
        relevant_context = []
        for element in context:
            element_content = str(element.get('content', element))

            # Simple relevance check based on keyword overlap
            task_keywords = set(current_task.lower().split())
            element_keywords = set(element_content.lower().split())

            overlap = len(task_keywords.intersection(element_keywords))
            if overlap > 0 or len(relevant_context) < 5:  # Keep at least 5 elements
                relevant_context.append(element)

        return relevant_context

    def _convert_context_to_messages(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert context to messages format for task detection.
        
        Args:
            context: Context to convert
            
        Returns:
            Messages format

        """
        messages = []
        for item in context:
            if isinstance(item, dict):
                if 'content' in item:
                    messages.append({'content': item['content']})
                else:
                    messages.append({'content': str(item)})
            else:
                messages.append({'content': str(item)})

        return messages

    def _convert_to_context_elements(
        self,
        context: List[Dict[str, Any]],
        task_result: TaskDetectionResult
    ) -> List[ContextElement]:
        """Convert context to ContextElement objects.
        
        Args:
            context: Context to convert
            task_result: Task detection result for relevance scoring
            
        Returns:
            List of ContextElement objects

        """
        elements = []

        for i, item in enumerate(context):
            content = str(item.get('content', item)) if isinstance(item, dict) else str(item)

            # Determine element type
            element_type = self._determine_element_type(item, content)

            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(content, task_result)

            elements.append(ContextElement(
                id=f"context_element_{i}",
                content=content,
                element_type=element_type,
                relevance_score=relevance_score,
                importance=0.5,  # Default importance
                token_count=len(content.split()),  # Simple token estimation
                source="context_input"
            ))

        return elements

    def _determine_element_type(self, item: Any, content: str) -> ElementType:
        """Determine the type of a context element.
        
        Args:
            item: Original context item
            content: Content string
            
        Returns:
            Element type

        """
        if isinstance(item, dict):
            if 'type' in item:
                type_mapping = {
                    'instruction': ElementType.INSTRUCTION,
                    'knowledge': ElementType.KNOWLEDGE,
                    'conversation': ElementType.CONVERSATION,
                    'example': ElementType.EXAMPLE,
                    'constraint': ElementType.CONSTRAINT,
                    'background': ElementType.BACKGROUND
                }
                return type_mapping.get(item['type'], ElementType.KNOWLEDGE)

        # Heuristic type detection based on content
        content_lower = content.lower()

        if any(word in content_lower for word in ['must', 'should', 'required', 'constraint']):
            return ElementType.CONSTRAINT
        elif any(word in content_lower for word in ['example', 'for instance', 'such as']):
            return ElementType.EXAMPLE
        elif any(word in content_lower for word in ['user:', 'assistant:', 'human:', 'ai:']):
            return ElementType.CONVERSATION
        elif any(word in content_lower for word in ['instruction', 'task', 'please', 'do']):
            return ElementType.INSTRUCTION
        else:
            return ElementType.KNOWLEDGE

    def _calculate_relevance_score(self, content: str, task_result: TaskDetectionResult) -> float:
        """Calculate relevance score for content based on task.
        
        Args:
            content: Content to score
            task_result: Task detection result
            
        Returns:
            Relevance score (0.0-1.0)

        """
        # Simple keyword-based relevance scoring
        content_words = set(content.lower().split())
        task_words = set(task_result.task_description.lower().split())

        if not task_words:
            return 0.5  # Default relevance

        overlap = len(content_words.intersection(task_words))
        if overlap == 0:
            return 0.3  # Minimum relevance for non-matching content

        # Boost relevance for content that matches task keywords
        relevance = 0.5 + (overlap / len(task_words)) * 0.5

        return min(relevance, 1.0)

    def _analyze_context(self, elements: List[ContextElement]) -> ContextAnalysisResult:
        """Analyze context before optimization.
        
        Args:
            elements: Context elements to analyze
            
        Returns:
            Context analysis result

        """
        if not elements:
            return ContextAnalysisResult(
                total_elements=0,
                total_tokens=0,
                element_type_distribution={},
                average_relevance=0.0,
                average_importance=0.0,
                complexity_score=0.0,
                coherence_score=0.0,
                redundancy_score=0.0
            )

        # Calculate basic statistics
        total_elements = len(elements)
        total_tokens = sum(element.token_count for element in elements)

        # Element type distribution
        type_distribution = {}
        for element in elements:
            element_type = element.element_type
            type_distribution[element_type] = type_distribution.get(element_type, 0) + 1

        # Average scores
        average_relevance = sum(element.relevance_score for element in elements) / total_elements
        average_importance = sum(element.importance for element in elements) / total_elements

        # Complexity score (based on variety of element types and total tokens)
        complexity_score = min((len(type_distribution) / 7) + (total_tokens / 10000), 1.0)

        return ContextAnalysisResult(
            total_elements=total_elements,
            total_tokens=total_tokens,
            element_type_distribution=type_distribution,
            average_relevance=average_relevance,
            average_importance=average_importance,
            complexity_score=complexity_score,
            coherence_score=0.8,  # Placeholder
            redundancy_score=0.2   # Placeholder
        )

    def _create_optimized_context(
        self,
        elements: List[ContextElement],
        task_result: TaskDetectionResult,
        analysis: ContextAnalysisResult,
        start_time: float
    ) -> OptimizedContext:
        """Create the final optimized context.
        
        Args:
            elements: Optimized context elements
            task_result: Task detection result
            analysis: Context analysis result
            start_time: Processing start time
            
        Returns:
            Optimized context

        """
        total_tokens = sum(element.token_count for element in elements)
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Calculate compression ratio
        compression_ratio = total_tokens / analysis.total_tokens if analysis.total_tokens > 0 else 1.0

        # Calculate completeness score (how much of the original context is preserved)
        completeness_score = len(elements) / analysis.total_elements if analysis.total_elements > 0 else 1.0

        return OptimizedContext(
            elements=elements,
            total_tokens=total_tokens,
            task_focus=task_result.task_description,
            optimization_metrics={
                'original_elements': analysis.total_elements,
                'original_tokens': analysis.total_tokens,
                'compression_ratio': compression_ratio,
                'completeness_score': completeness_score,
                'task_confidence': task_result.confidence,
                'processing_time_ms': processing_time
            },
            compression_ratio=compression_ratio,
            coherence_score=0.8,  # Placeholder
            completeness_score=completeness_score,
            optimization_strategy=f"{self.task_detection_strategy.__class__.__name__}+"
                                f"{self.prioritization_strategy.__class__.__name__}+"
                                f"{self.compression_strategy.__class__.__name__}",
            processing_time_ms=processing_time
        )

    def _create_fallback_context(
        self,
        context: List[Dict[str, Any]],
        task: str,
        max_tokens: int
    ) -> OptimizedContext:
        """Create a fallback optimized context when optimization fails.
        
        Args:
            context: Original context
            task: Task description
            max_tokens: Maximum token count
            
        Returns:
            Fallback optimized context

        """
        # Simple fallback: just take the first few elements
        elements = []
        current_tokens = 0

        for i, item in enumerate(context):
            content = str(item.get('content', item)) if isinstance(item, dict) else str(item)
            token_count = len(content.split())

            if current_tokens + token_count <= max_tokens:
                elements.append(ContextElement(
                    id=f"fallback_element_{i}",
                    content=content,
                    element_type=ElementType.KNOWLEDGE,
                    relevance_score=0.5,
                    importance=0.5,
                    token_count=token_count,
                    source="fallback"
                ))
                current_tokens += token_count
            else:
                break

        return OptimizedContext(
            elements=elements,
            total_tokens=current_tokens,
            task_focus=task,
            optimization_strategy="fallback"
        )

    def _update_stats(
        self,
        task_result: TaskDetectionResult,
        optimized_context: OptimizedContext,
        processing_time: float
    ) -> None:
        """Update optimization statistics.
        
        Args:
            task_result: Task detection result
            optimized_context: Optimized context
            processing_time: Processing time in seconds

        """
        self.optimization_stats['total_optimizations'] += 1
        self.optimization_stats['total_processing_time'] += max(processing_time, 0.001)  # Ensure non-zero

        # Update average compression ratio
        current_avg = self.optimization_stats['average_compression_ratio']
        total_opts = self.optimization_stats['total_optimizations']
        new_avg = ((current_avg * (total_opts - 1)) + optimized_context.compression_ratio) / total_opts
        self.optimization_stats['average_compression_ratio'] = new_avg

        # Update task type distribution
        task_type = task_result.task_type.value
        if task_type not in self.optimization_stats['task_type_distribution']:
            self.optimization_stats['task_type_distribution'][task_type] = 0
        self.optimization_stats['task_type_distribution'][task_type] += 1

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics.
        
        Returns:
            Dictionary containing optimization statistics

        """
        stats = self.optimization_stats.copy()

        if stats['total_optimizations'] > 0:
            stats['average_processing_time'] = stats['total_processing_time'] / stats['total_optimizations']
        else:
            stats['average_processing_time'] = 0.0

        return stats
