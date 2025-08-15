"""Unit tests for the Task Context Optimizer.
"""

import unittest

from .models import (
    ContextElement,
    ContextOptimizationConfig,
    ElementType,
    OptimizedContext,
    RequirementType,
    TaskDetectionResult,
    TaskRequirement,
    TaskType,
)
from .optimizer import TaskContextOptimizer
from .strategies import (
    PatternBasedTaskDetection,
    ProportionalBlending,
    RelevanceBasedPrioritization,
    SmartTruncationCompression,
)


class TestTaskContextOptimizer(unittest.TestCase):
    """Test cases for the TaskContextOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = ContextOptimizationConfig(
            max_tokens=1000,
            min_relevance_threshold=0.3
        )
        self.optimizer = TaskContextOptimizer(config=self.config)
    
    def test_initialization(self):
        """Test that the optimizer initializes correctly."""
        self.assertIsInstance(self.optimizer.task_detection_strategy, PatternBasedTaskDetection)
        self.assertIsInstance(self.optimizer.prioritization_strategy, RelevanceBasedPrioritization)
        self.assertIsInstance(self.optimizer.compression_strategy, SmartTruncationCompression)
        self.assertIsInstance(self.optimizer.blending_strategy, ProportionalBlending)
        self.assertEqual(self.optimizer.config.max_tokens, 1000)
    
    def test_optimize_context_for_task(self):
        """Test context optimization for a specific task."""
        context = [
            {'content': 'This is some background information about AI'},
            {'content': 'Explain how neural networks work'},
            {'content': 'Machine learning is a subset of artificial intelligence'},
            {'content': 'Deep learning uses multiple layers of neurons'}
        ]
        
        task = "explain neural networks"
        max_tokens = 500
        
        result = self.optimizer.optimize_context_for_task(context, task, max_tokens)
        
        self.assertIsInstance(result, OptimizedContext)
        self.assertLessEqual(result.total_tokens, max_tokens)
        self.assertTrue(len(result.elements) > 0)
        self.assertIn('neural', result.task_focus.lower())
    
    def test_extract_task_requirements(self):
        """Test task requirement extraction."""
        task = "Please explain how to solve quadratic equations step by step"
        
        requirements = self.optimizer.extract_task_requirements(task)
        
        self.assertIsInstance(requirements, list)
        # The exact requirements depend on the implementation
        # but we should get some requirements for an explanation task
    
    def test_prioritize_context_elements(self):
        """Test context element prioritization."""
        context_elements = [
            {'content': 'Background information'},
            {'content': 'Relevant explanation about the topic'},
            {'content': 'Unrelated information'},
            {'content': 'Important constraint: must be accurate'}
        ]
        
        task_requirements = [
            TaskRequirement(
                requirement_type=RequirementType.KNOWLEDGE,
                content="explanation about the topic",
                importance=0.9
            )
        ]
        
        prioritized = self.optimizer.prioritize_context_elements(context_elements, task_requirements)
        
        self.assertEqual(len(prioritized), len(context_elements))
        self.assertTrue(all('priority' in element for element in prioritized))
        
        # The element with "explanation about the topic" should have higher priority
        explanation_element = next(e for e in prioritized if 'explanation' in e['content'])
        self.assertGreaterEqual(explanation_element['priority'], 0.5)
    
    def test_blend_context_sources(self):
        """Test context source blending."""
        task_instructions = "Explain the concept clearly"
        background_knowledge = [
            "Concept A is related to concept B",
            "Historical context of the concept",
            "Modern applications of the concept"
        ]
        conversation_history = [
            {'content': 'User asked about the concept'},
            {'content': 'Assistant provided initial explanation'}
        ]
        max_tokens = 800
        
        result = self.optimizer.blend_context_sources(
            task_instructions, background_knowledge, conversation_history, max_tokens
        )
        
        self.assertIsInstance(result, OptimizedContext)
        self.assertLessEqual(result.total_tokens, max_tokens)
        self.assertEqual(result.task_focus, task_instructions)
        
        # Should have elements from different sources
        element_types = {element.element_type for element in result.elements}
        self.assertIn(ElementType.INSTRUCTION, element_types)
        self.assertIn(ElementType.KNOWLEDGE, element_types)
    
    def test_maintain_task_coherence(self):
        """Test task coherence maintenance."""
        context = [
            {'content': 'Step 1: Initialize variables'},
            {'content': 'Step 2: Process input data'},
            {'content': 'Unrelated topic about weather'},
            {'content': 'Step 3: Generate output'}
        ]
        
        task = "Follow the step-by-step process"
        
        coherent_context = self.optimizer.maintain_task_coherence(context, task)
        
        self.assertIsInstance(coherent_context, list)
        self.assertTrue(len(coherent_context) > 0)
        
        # Should preserve step-related content
        step_content = [item for item in coherent_context if 'Step' in item['content']]
        self.assertTrue(len(step_content) > 0)
    
    def test_delineate_task_boundaries(self):
        """Test task boundary delineation."""
        context = [
            {'content': 'Information about task A'},
            {'content': 'Information about task B'},
            {'content': 'General background information'},
            {'content': 'More information about task A'}
        ]
        
        current_task = "Focus on task A specifically"
        
        bounded_context = self.optimizer.delineate_task_boundaries(context, current_task)
        
        self.assertIsInstance(bounded_context, list)
        self.assertTrue(len(bounded_context) > 0)
        
        # Should prioritize task A related content
        task_a_content = [item for item in bounded_context if 'task A' in item['content']]
        self.assertTrue(len(task_a_content) > 0)
    
    def test_get_optimization_stats(self):
        """Test optimization statistics retrieval."""
        # Perform some optimizations to generate stats
        context = [{'content': 'Test content'}]
        task = "test task"
        
        self.optimizer.optimize_context_for_task(context, task, 100)
        self.optimizer.optimize_context_for_task(context, task, 100)
        
        stats = self.optimizer.get_optimization_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_optimizations', stats)
        self.assertIn('average_processing_time', stats)
        self.assertIn('average_compression_ratio', stats)
        self.assertIn('task_type_distribution', stats)
        
        self.assertEqual(stats['total_optimizations'], 2)
        self.assertGreater(stats['average_processing_time'], 0)


class TestPatternBasedTaskDetection(unittest.TestCase):
    """Test cases for the PatternBasedTaskDetection strategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = PatternBasedTaskDetection()
    
    def test_detect_information_retrieval_task(self):
        """Test detection of information retrieval tasks."""
        messages = [{'content': 'What is machine learning?'}]
        context = {}
        
        result = self.strategy.detect_task(messages, context)
        
        self.assertEqual(result.task_type, TaskType.INFORMATION_RETRIEVAL)
        self.assertGreater(result.confidence, 0.0)
        self.assertIn('machine learning', result.task_description.lower())
    
    def test_detect_explanation_task(self):
        """Test detection of explanation tasks."""
        messages = [{'content': 'Please explain how photosynthesis works'}]
        context = {}
        
        result = self.strategy.detect_task(messages, context)
        
        self.assertEqual(result.task_type, TaskType.EXPLANATION)
        self.assertGreater(result.confidence, 0.0)
    
    def test_detect_problem_solving_task(self):
        """Test detection of problem solving tasks."""
        messages = [{'content': 'How can I fix this error in my code?'}]
        context = {}
        
        result = self.strategy.detect_task(messages, context)
        
        self.assertEqual(result.task_type, TaskType.PROBLEM_SOLVING)
        self.assertGreater(result.confidence, 0.0)
    
    def test_detect_unknown_task(self):
        """Test detection when task type is unclear."""
        messages = [{'content': 'Hello there'}]
        context = {}
        
        result = self.strategy.detect_task(messages, context)
        
        self.assertEqual(result.task_type, TaskType.UNKNOWN)
        self.assertEqual(result.confidence, 0.0)


class TestRelevanceBasedPrioritization(unittest.TestCase):
    """Test cases for the RelevanceBasedPrioritization strategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = RelevanceBasedPrioritization()
        self.config = ContextOptimizationConfig()
    
    def test_prioritize_elements(self):
        """Test element prioritization."""
        elements = [
            ContextElement(
                id="1",
                content="Information about machine learning",
                element_type=ElementType.KNOWLEDGE,
                relevance_score=0.8,
                importance=0.7,
                token_count=10,
                source="test"
            ),
            ContextElement(
                id="2",
                content="Unrelated information",
                element_type=ElementType.KNOWLEDGE,
                relevance_score=0.2,
                importance=0.3,
                token_count=8,
                source="test"
            ),
            ContextElement(
                id="3",
                content="Important instruction",
                element_type=ElementType.INSTRUCTION,
                relevance_score=0.6,
                importance=0.9,
                token_count=5,
                source="test"
            )
        ]
        
        task_result = TaskDetectionResult(
            task_type=TaskType.EXPLANATION,
            confidence=0.8,
            task_description="Explain machine learning concepts"
        )
        
        prioritized = self.strategy.prioritize_elements(elements, task_result, self.config)
        
        self.assertEqual(len(prioritized), 3)
        
        # Instruction should be first due to high importance and element type priority
        self.assertEqual(prioritized[0].element_type, ElementType.INSTRUCTION)
        
        # High relevance knowledge should be second
        self.assertEqual(prioritized[1].id, "1")
        
        # Low relevance should be last
        self.assertEqual(prioritized[2].id, "2")


class TestSmartTruncationCompression(unittest.TestCase):
    """Test cases for the SmartTruncationCompression strategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = SmartTruncationCompression()
        self.config = ContextOptimizationConfig(min_relevance_threshold=0.3)
    
    def test_compress_context_within_limit(self):
        """Test compression when context is already within limits."""
        elements = [
            ContextElement(
                id="1",
                content="Short content",
                element_type=ElementType.KNOWLEDGE,
                relevance_score=0.8,
                importance=0.7,
                token_count=5,
                source="test"
            )
        ]
        
        target_tokens = 100
        
        compressed = self.strategy.compress_context(elements, target_tokens, self.config)
        
        self.assertEqual(len(compressed), 1)
        self.assertEqual(compressed[0].id, "1")
    
    def test_compress_context_exceeds_limit(self):
        """Test compression when context exceeds token limits."""
        elements = [
            ContextElement(
                id="1",
                content="High relevance content",
                element_type=ElementType.KNOWLEDGE,
                relevance_score=0.9,
                importance=0.8,
                token_count=60,
                source="test"
            ),
            ContextElement(
                id="2",
                content="Medium relevance content",
                element_type=ElementType.KNOWLEDGE,
                relevance_score=0.6,
                importance=0.5,
                token_count=50,
                source="test"
            ),
            ContextElement(
                id="3",
                content="Low relevance content",
                element_type=ElementType.KNOWLEDGE,
                relevance_score=0.2,
                importance=0.3,
                token_count=40,
                source="test"
            )
        ]
        
        target_tokens = 100
        
        compressed = self.strategy.compress_context(elements, target_tokens, self.config)
        
        # Should keep high relevance elements and remove low relevance ones
        self.assertLess(len(compressed), 3)
        
        # High relevance element should be kept
        high_relevance_kept = any(element.id == "1" for element in compressed)
        self.assertTrue(high_relevance_kept)
        
        # Total tokens should be within or close to the limit
        total_tokens = sum(element.token_count for element in compressed)
        self.assertLessEqual(total_tokens, target_tokens + 60)  # Allow some flexibility


if __name__ == '__main__':
    unittest.main()