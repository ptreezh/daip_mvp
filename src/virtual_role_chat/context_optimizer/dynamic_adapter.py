"""
Dynamic Context Adapter for real-time context optimization.

This module implements dynamic context adaptation capabilities that can
adjust context in real-time based on changing task requirements and
maintain task coherence throughout conversations.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from .models import (
    TaskType, TaskRequirement, ContextElement, TaskDetectionResult,
    OptimizedContext, ContextOptimizationConfig, ElementType
)
from .strategies import TaskDetectionStrategy, PatternBasedTaskDetection


class AdaptationTrigger(str, Enum):
    """Types of triggers that can cause context adaptation."""
    TASK_CHANGE = "task_change"
    CONTEXT_OVERFLOW = "context_overflow"
    RELEVANCE_DRIFT = "relevance_drift"
    TIME_DECAY = "time_decay"
    USER_FEEDBACK = "user_feedback"
    QUALITY_DEGRADATION = "quality_degradation"


class AdaptationAction(str, Enum):
    """Types of adaptation actions that can be taken."""
    REBALANCE_PRIORITIES = "rebalance_priorities"
    COMPRESS_CONTEXT = "compress_context"
    REFRESH_RELEVANCE = "refresh_relevance"
    REMOVE_STALE_CONTENT = "remove_stale_content"
    ADD_MISSING_CONTEXT = "add_missing_context"
    RESTRUCTURE_CONTEXT = "restructure_context"


class AdaptationEvent:
    """Represents a context adaptation event."""
    
    def __init__(
        self,
        trigger: AdaptationTrigger,
        action: AdaptationAction,
        timestamp: datetime,
        context_before: OptimizedContext,
        context_after: OptimizedContext,
        metadata: Dict[str, Any] = None
    ):
        self.trigger = trigger
        self.action = action
        self.timestamp = timestamp
        self.context_before = context_before
        self.context_after = context_after
        self.metadata = metadata or {}


class TaskBoundaryDetector:
    """Detects task boundaries and transitions in conversations."""
    
    def __init__(self, task_detection_strategy: Optional[TaskDetectionStrategy] = None):
        """
        Initialize the task boundary detector.
        
        Args:
            task_detection_strategy: Strategy for detecting tasks
        """
        self.task_detection_strategy = task_detection_strategy or PatternBasedTaskDetection()
        self.logger = logging.getLogger(__name__)
        self.task_history: List[Tuple[datetime, TaskDetectionResult]] = []
        self.current_task: Optional[TaskDetectionResult] = None
    
    def detect_task_transition(
        self,
        new_messages: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[TaskDetectionResult]]:
        """
        Detect if there's a task transition in the conversation.
        
        Args:
            new_messages: New messages to analyze
            context: Current context
            
        Returns:
            Tuple of (has_transition, new_task_result)
        """
        # Detect the current task from new messages
        new_task_result = self.task_detection_strategy.detect_task(new_messages, context)
        
        # Check if this represents a significant task change
        has_transition = self._is_significant_task_change(new_task_result)
        
        if has_transition:
            self.logger.info(f"Task transition detected: {self.current_task.task_type if self.current_task else 'None'} -> {new_task_result.task_type}")
            
            # Update task history
            if self.current_task:
                self.task_history.append((datetime.now(), self.current_task))
            
            self.current_task = new_task_result
        
        return has_transition, new_task_result if has_transition else None
    
    def _is_significant_task_change(self, new_task_result: TaskDetectionResult) -> bool:
        """
        Determine if a new task result represents a significant change.
        
        Args:
            new_task_result: New task detection result
            
        Returns:
            True if this is a significant task change
        """
        if not self.current_task:
            return True
        
        # Different task types indicate a transition
        if new_task_result.task_type != self.current_task.task_type:
            return True
        
        # High confidence in new task with different description
        if (new_task_result.confidence > 0.7 and 
            new_task_result.task_description != self.current_task.task_description):
            return True
        
        return False
    
    def get_task_context_window(self, window_size: int = 3) -> List[TaskDetectionResult]:
        """
        Get recent task context for understanding task flow.
        
        Args:
            window_size: Number of recent tasks to include
            
        Returns:
            List of recent task results
        """
        recent_tasks = []
        
        # Add current task if available
        if self.current_task:
            recent_tasks.append(self.current_task)
        
        # Add recent historical tasks
        for _, task_result in self.task_history[-window_size:]:
            recent_tasks.append(task_result)
        
        return recent_tasks


class CoherenceMonitor:
    """Monitors and maintains task coherence in context."""
    
    def __init__(self):
        """Initialize the coherence monitor."""
        self.logger = logging.getLogger(__name__)
        self.coherence_history: List[Tuple[datetime, float]] = []
    
    def assess_coherence(
        self,
        context: OptimizedContext,
        current_task: TaskDetectionResult
    ) -> float:
        """
        Assess the coherence of context with respect to the current task.
        
        Args:
            context: Current optimized context
            current_task: Current task
            
        Returns:
            Coherence score (0.0-1.0)
        """
        if not context.elements:
            return 0.0
        
        # Calculate task alignment score
        task_alignment = self._calculate_task_alignment(context, current_task)
        
        # Calculate internal consistency score
        internal_consistency = self._calculate_internal_consistency(context)
        
        # Calculate temporal coherence score
        temporal_coherence = self._calculate_temporal_coherence(context)
        
        # Weighted combination
        coherence_score = (
            task_alignment * 0.5 +
            internal_consistency * 0.3 +
            temporal_coherence * 0.2
        )
        
        # Record coherence history
        self.coherence_history.append((datetime.now(), coherence_score))
        
        # Keep only recent history
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.coherence_history = [
            (timestamp, score) for timestamp, score in self.coherence_history
            if timestamp > cutoff_time
        ]
        
        return coherence_score
    
    def _calculate_task_alignment(
        self,
        context: OptimizedContext,
        current_task: TaskDetectionResult
    ) -> float:
        """
        Calculate how well context aligns with the current task.
        
        Args:
            context: Current context
            current_task: Current task
            
        Returns:
            Task alignment score (0.0-1.0)
        """
        if not context.elements:
            return 0.0
        
        task_keywords = set(current_task.task_description.lower().split())
        
        alignment_scores = []
        for element in context.elements:
            element_keywords = set(element.content.lower().split())
            overlap = len(task_keywords.intersection(element_keywords))
            
            if task_keywords:
                alignment = overlap / len(task_keywords)
            else:
                alignment = 0.0
            
            # Weight by element relevance and importance
            weighted_alignment = alignment * element.relevance_score * element.importance
            alignment_scores.append(weighted_alignment)
        
        return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
    
    def _calculate_internal_consistency(self, context: OptimizedContext) -> float:
        """
        Calculate internal consistency of context elements.
        
        Args:
            context: Current context
            
        Returns:
            Internal consistency score (0.0-1.0)
        """
        if len(context.elements) < 2:
            return 1.0  # Single element is always consistent
        
        # Simple consistency check based on keyword overlap
        consistency_scores = []
        
        for i, element1 in enumerate(context.elements):
            for j, element2 in enumerate(context.elements[i+1:], i+1):
                words1 = set(element1.content.lower().split())
                words2 = set(element2.content.lower().split())
                
                if words1 and words2:
                    overlap = len(words1.intersection(words2))
                    union = len(words1.union(words2))
                    similarity = overlap / union if union > 0 else 0.0
                    consistency_scores.append(similarity)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
    
    def _calculate_temporal_coherence(self, context: OptimizedContext) -> float:
        """
        Calculate temporal coherence of context elements.
        
        Args:
            context: Current context
            
        Returns:
            Temporal coherence score (0.0-1.0)
        """
        # Simple temporal coherence based on timestamp distribution
        timestamps = [element.timestamp for element in context.elements if hasattr(element, 'timestamp')]
        
        if len(timestamps) < 2:
            return 1.0
        
        # Calculate time span
        timestamps.sort()
        time_span = (timestamps[-1] - timestamps[0]).total_seconds()
        
        # Prefer more recent and evenly distributed content
        if time_span < 3600:  # Within 1 hour
            return 0.9
        elif time_span < 86400:  # Within 1 day
            return 0.7
        else:
            return 0.5


class DynamicContextAdapter:
    """
    Main dynamic context adapter that provides real-time context optimization.
    
    This adapter monitors context quality, detects task transitions, and
    automatically adjusts context to maintain optimal performance.
    """
    
    def __init__(
        self,
        config: Optional[ContextOptimizationConfig] = None,
        task_boundary_detector: Optional[TaskBoundaryDetector] = None,
        coherence_monitor: Optional[CoherenceMonitor] = None
    ):
        """
        Initialize the dynamic context adapter.
        
        Args:
            config: Optimization configuration
            task_boundary_detector: Task boundary detector
            coherence_monitor: Coherence monitor
        """
        self.config = config or ContextOptimizationConfig()
        self.task_boundary_detector = task_boundary_detector or TaskBoundaryDetector()
        self.coherence_monitor = coherence_monitor or CoherenceMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Adaptation history
        self.adaptation_events: List[AdaptationEvent] = []
        
        # Monitoring thresholds
        self.coherence_threshold = 0.6
        self.relevance_threshold = 0.4
        self.staleness_threshold = timedelta(hours=2)
    
    def adapt_context_realtime(
        self,
        current_context: OptimizedContext,
        new_messages: List[Dict[str, Any]],
        conversation_context: Dict[str, Any]
    ) -> Tuple[OptimizedContext, List[AdaptationEvent]]:
        """
        Adapt context in real-time based on new messages and current state.
        
        Args:
            current_context: Current optimized context
            new_messages: New messages to process
            conversation_context: Conversation context
            
        Returns:
            Tuple of (adapted_context, adaptation_events)
        """
        adaptation_events = []
        adapted_context = current_context
        
        # Check for task transitions
        has_transition, new_task = self.task_boundary_detector.detect_task_transition(
            new_messages, conversation_context
        )
        
        if has_transition and new_task:
            # Adapt for task transition
            adapted_context, event = self._adapt_for_task_transition(
                adapted_context, new_task
            )
            adaptation_events.append(event)
        
        # Check coherence
        current_task = new_task or self.task_boundary_detector.current_task
        if current_task:
            coherence_score = self.coherence_monitor.assess_coherence(
                adapted_context, current_task
            )
            
            if coherence_score < self.coherence_threshold:
                # Adapt for low coherence
                adapted_context, event = self._adapt_for_low_coherence(
                    adapted_context, current_task, coherence_score
                )
                adaptation_events.append(event)
        
        # Check for context overflow
        if adapted_context.total_tokens > self.config.max_tokens:
            adapted_context, event = self._adapt_for_context_overflow(adapted_context)
            adaptation_events.append(event)
        
        # Check for stale content
        adapted_context, stale_events = self._remove_stale_content(adapted_context)
        adaptation_events.extend(stale_events)
        
        # Record adaptation events
        self.adaptation_events.extend(adaptation_events)
        
        return adapted_context, adaptation_events
    
    def _adapt_for_task_transition(
        self,
        context: OptimizedContext,
        new_task: TaskDetectionResult
    ) -> Tuple[OptimizedContext, AdaptationEvent]:
        """
        Adapt context for a task transition.
        
        Args:
            context: Current context
            new_task: New task detected
            
        Returns:
            Tuple of (adapted_context, adaptation_event)
        """
        self.logger.info(f"Adapting context for task transition to {new_task.task_type}")
        
        # Rebalance element priorities based on new task
        adapted_elements = []
        for element in context.elements:
            # Recalculate relevance for new task
            new_relevance = self._calculate_task_relevance(element, new_task)
            
            # Create updated element
            updated_element = ContextElement(
                id=element.id,
                content=element.content,
                element_type=element.element_type,
                relevance_score=new_relevance,
                importance=element.importance,
                token_count=element.token_count,
                source=element.source,
                timestamp=element.timestamp,
                dependencies=element.dependencies,
                metadata=element.metadata
            )
            adapted_elements.append(updated_element)
        
        # Sort by new priority scores
        adapted_elements.sort(key=lambda e: e.get_priority_score(), reverse=True)
        
        # Create adapted context
        adapted_context = OptimizedContext(
            elements=adapted_elements,
            total_tokens=context.total_tokens,
            task_focus=new_task.task_description,
            optimization_metrics=context.optimization_metrics,
            compression_ratio=context.compression_ratio,
            coherence_score=context.coherence_score,
            completeness_score=context.completeness_score,
            optimization_strategy=context.optimization_strategy + "+task_transition"
        )
        
        # Create adaptation event
        event = AdaptationEvent(
            trigger=AdaptationTrigger.TASK_CHANGE,
            action=AdaptationAction.REBALANCE_PRIORITIES,
            timestamp=datetime.now(),
            context_before=context,
            context_after=adapted_context,
            metadata={'new_task_type': new_task.task_type.value}
        )
        
        return adapted_context, event
    
    def _adapt_for_low_coherence(
        self,
        context: OptimizedContext,
        current_task: TaskDetectionResult,
        coherence_score: float
    ) -> Tuple[OptimizedContext, AdaptationEvent]:
        """
        Adapt context for low coherence.
        
        Args:
            context: Current context
            current_task: Current task
            coherence_score: Current coherence score
            
        Returns:
            Tuple of (adapted_context, adaptation_event)
        """
        self.logger.info(f"Adapting context for low coherence: {coherence_score:.2f}")
        
        # Remove low-relevance elements that hurt coherence
        filtered_elements = [
            element for element in context.elements
            if element.relevance_score >= self.relevance_threshold
        ]
        
        # Recalculate metrics
        total_tokens = sum(element.token_count for element in filtered_elements)
        
        adapted_context = OptimizedContext(
            elements=filtered_elements,
            total_tokens=total_tokens,
            task_focus=context.task_focus,
            optimization_metrics=context.optimization_metrics,
            compression_ratio=total_tokens / context.total_tokens if context.total_tokens > 0 else 1.0,
            coherence_score=coherence_score,
            completeness_score=len(filtered_elements) / len(context.elements) if context.elements else 1.0,
            optimization_strategy=context.optimization_strategy + "+coherence_fix"
        )
        
        event = AdaptationEvent(
            trigger=AdaptationTrigger.RELEVANCE_DRIFT,
            action=AdaptationAction.REMOVE_STALE_CONTENT,
            timestamp=datetime.now(),
            context_before=context,
            context_after=adapted_context,
            metadata={'coherence_score': coherence_score}
        )
        
        return adapted_context, event
    
    def _adapt_for_context_overflow(
        self,
        context: OptimizedContext
    ) -> Tuple[OptimizedContext, AdaptationEvent]:
        """
        Adapt context for token overflow.
        
        Args:
            context: Current context
            
        Returns:
            Tuple of (adapted_context, adaptation_event)
        """
        self.logger.info(f"Adapting context for overflow: {context.total_tokens} > {self.config.max_tokens}")
        
        # Sort elements by priority and keep top ones
        sorted_elements = sorted(context.elements, key=lambda e: e.get_priority_score(), reverse=True)
        
        compressed_elements = []
        current_tokens = 0
        
        for element in sorted_elements:
            if current_tokens + element.token_count <= self.config.max_tokens:
                compressed_elements.append(element)
                current_tokens += element.token_count
            else:
                break
        
        adapted_context = OptimizedContext(
            elements=compressed_elements,
            total_tokens=current_tokens,
            task_focus=context.task_focus,
            optimization_metrics=context.optimization_metrics,
            compression_ratio=current_tokens / context.total_tokens if context.total_tokens > 0 else 1.0,
            coherence_score=context.coherence_score,
            completeness_score=len(compressed_elements) / len(context.elements) if context.elements else 1.0,
            optimization_strategy=context.optimization_strategy + "+overflow_compression"
        )
        
        event = AdaptationEvent(
            trigger=AdaptationTrigger.CONTEXT_OVERFLOW,
            action=AdaptationAction.COMPRESS_CONTEXT,
            timestamp=datetime.now(),
            context_before=context,
            context_after=adapted_context,
            metadata={'tokens_removed': context.total_tokens - current_tokens}
        )
        
        return adapted_context, event
    
    def _remove_stale_content(
        self,
        context: OptimizedContext
    ) -> Tuple[OptimizedContext, List[AdaptationEvent]]:
        """
        Remove stale content from context.
        
        Args:
            context: Current context
            
        Returns:
            Tuple of (adapted_context, adaptation_events)
        """
        current_time = datetime.now()
        cutoff_time = current_time - self.staleness_threshold
        
        fresh_elements = []
        stale_elements = []
        
        for element in context.elements:
            if hasattr(element, 'timestamp') and element.timestamp < cutoff_time:
                stale_elements.append(element)
            else:
                fresh_elements.append(element)
        
        events = []
        if stale_elements:
            self.logger.info(f"Removing {len(stale_elements)} stale elements")
            
            total_tokens = sum(element.token_count for element in fresh_elements)
            
            adapted_context = OptimizedContext(
                elements=fresh_elements,
                total_tokens=total_tokens,
                task_focus=context.task_focus,
                optimization_metrics=context.optimization_metrics,
                compression_ratio=total_tokens / context.total_tokens if context.total_tokens > 0 else 1.0,
                coherence_score=context.coherence_score,
                completeness_score=len(fresh_elements) / len(context.elements) if context.elements else 1.0,
                optimization_strategy=context.optimization_strategy + "+stale_removal"
            )
            
            event = AdaptationEvent(
                trigger=AdaptationTrigger.TIME_DECAY,
                action=AdaptationAction.REMOVE_STALE_CONTENT,
                timestamp=current_time,
                context_before=context,
                context_after=adapted_context,
                metadata={'stale_elements_removed': len(stale_elements)}
            )
            
            events.append(event)
            return adapted_context, events
        
        return context, events
    
    def _calculate_task_relevance(
        self,
        element: ContextElement,
        task: TaskDetectionResult
    ) -> float:
        """
        Calculate relevance of an element to a specific task.
        
        Args:
            element: Context element
            task: Task to calculate relevance for
            
        Returns:
            Relevance score (0.0-1.0)
        """
        element_words = set(element.content.lower().split())
        task_words = set(task.task_description.lower().split())
        
        if not task_words:
            return 0.5
        
        overlap = len(element_words.intersection(task_words))
        relevance = overlap / len(task_words) if task_words else 0.0
        
        # Boost relevance for matching task type
        if task.task_type == TaskType.EXPLANATION and element.element_type == ElementType.KNOWLEDGE:
            relevance *= 1.2
        elif task.task_type == TaskType.PROBLEM_SOLVING and element.element_type == ElementType.INSTRUCTION:
            relevance *= 1.1
        
        return min(relevance, 1.0)
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about context adaptations.
        
        Returns:
            Dictionary containing adaptation statistics
        """
        if not self.adaptation_events:
            return {
                'total_adaptations': 0,
                'trigger_distribution': {},
                'action_distribution': {},
                'average_adaptation_interval': 0.0
            }
        
        # Count triggers and actions
        trigger_counts = {}
        action_counts = {}
        
        for event in self.adaptation_events:
            trigger = event.trigger.value
            action = event.action.value
            
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Calculate average interval
        if len(self.adaptation_events) > 1:
            timestamps = [event.timestamp for event in self.adaptation_events]
            timestamps.sort()
            intervals = [
                (timestamps[i] - timestamps[i-1]).total_seconds()
                for i in range(1, len(timestamps))
            ]
            average_interval = sum(intervals) / len(intervals)
        else:
            average_interval = 0.0
        
        return {
            'total_adaptations': len(self.adaptation_events),
            'trigger_distribution': trigger_counts,
            'action_distribution': action_counts,
            'average_adaptation_interval': average_interval
        }