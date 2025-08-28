import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np

from src.core_services.context_optimization_engine import (
    ContextOptimizationEngine,
    ContextOptimizationRequest,
    OptimizedContext,
    ContextElement,
)

class TestContextOptimizationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ContextOptimizationEngine()
        
        # Mock internal components
        self.engine.history_analyzer = AsyncMock()
        self.engine.task_analyzer = AsyncMock()
        self.engine.context_aggregator = AsyncMock()
        self.engine.embedding_model = AsyncMock()

    def test_optimize_context_basic(self):
        async def run_test():
            # Mock return values for internal components
            self.engine.history_analyzer.analyze.return_value = {
                "patterns": {}, "preferences": {}, "success_indicators": {"task_completion_rate": 0.8},
                "key_topics": ["AI", "ML"], "total_conversations": 10
            }
            self.engine.task_analyzer.analyze.return_value = {
                "task_type": "analysis", "complexity": "medium", "keywords": ["data"],
                "analysis_confidence": 0.9
            }
            self.engine.context_aggregator.aggregate.return_value = [
                ContextElement(element_id="hist1", content="history content", element_type="history", relevance_score=0.8, confidence_score=0.9, source="mock", timestamp=datetime.now()),
                ContextElement(element_id="task1", content="task content", element_type="task", relevance_score=0.9, confidence_score=0.95, source="mock", timestamp=datetime.now()),
            ]
            self.engine.embedding_model.encode_multi_aspect.return_value = (
            np.array([0.1, 0.2, 0.3, 0.4]),
            np.array([0.5, 0.6, 0.7, 0.8]),
            np.array([0.9, 1.0, 1.1, 1.2]),
            np.array([1.3, 1.4, 1.5, 1.6]),
        )

            request = ContextOptimizationRequest(
                user_id="user1",
                current_query="optimize this query",
                conversation_history=[{"role": "user", "content": "hello"}],
                current_task="task_id_1",
                optimization_strategy="adaptive"
            )

            optimized_context = await self.engine.optimize_context(request)

            self.assertIsInstance(optimized_context, OptimizedContext)
            self.assertGreater(len(optimized_context.optimized_prompt), 0)
            self.assertGreater(len(optimized_context.context_elements), 0)
            self.assertGreater(optimized_context.confidence_score, 0.0)
            
            self.engine.history_analyzer.analyze.assert_called_once()
            self.engine.task_analyzer.analyze.assert_called_once()
            self.engine.context_aggregator.aggregate.assert_called_once()

        asyncio.run(run_test())

    def test_adaptive_optimization_strategy(self):
        async def run_test():
            request = ContextOptimizationRequest(
                user_id="user1",
                current_query="optimize this query",
                conversation_history=[],
                optimization_strategy="adaptive"
            )
            self.engine.embedding_model.encode_multi_aspect.return_value = (
                np.array([0.1, 0.2, 0.3, 0.4]),
                np.array([0.5, 0.6, 0.7, 0.8]),
                np.array([0.9, 1.0, 1.1, 1.2]),
                np.array([1.3, 1.4, 1.5, 1.6]),
            )
            context_elements = [
                ContextElement(element_id="hist1", content="history content", element_type="history", relevance_score=0.8, confidence_score=0.9, source="mock", timestamp=datetime.now()),
                ContextElement(element_id="task1", content="task content", element_type="task", relevance_score=0.9, confidence_score=0.95, source="mock", timestamp=datetime.now()),
            ]
            history_insights = {"total_conversations": 20, "success_indicators": {"task_completion_rate": 0.9}, "key_topics": ["topic1"]}
            task_insights = {"task_type": "analysis", "complexity": "medium"}

            optimized_context = await self.engine._adaptive_optimization_strategy(
                request, context_elements, history_insights, task_insights
            )

            self.assertIsInstance(optimized_context, OptimizedContext)
            self.assertGreater(len(optimized_context.optimized_prompt), 0)
            self.assertLessEqual(len(optimized_context.context_elements), 15) # Medium experience user
            self.assertIn("balanced", optimized_context.optimization_metrics["detail_level"])

        asyncio.run(run_test())

    def test_focused_optimization_strategy(self):
        async def run_test():
            request = ContextOptimizationRequest(
                user_id="user1",
                current_query="focus on this task",
                conversation_history=[],
                optimization_strategy="focused"
            )
            context_elements = [
                ContextElement(element_id="hist1", content="history content", element_type="history", relevance_score=0.8, confidence_score=0.9, source="mock", timestamp=datetime.now()),
                ContextElement(element_id="task1", content="task content", element_type="task", relevance_score=0.9, confidence_score=0.95, source="mock", timestamp=datetime.now()),
                ContextElement(element_id="know1", content="knowledge content", element_type="knowledge", relevance_score=0.7, confidence_score=0.8, source="mock", timestamp=datetime.now()),
                ContextElement(element_id="env1", content="environment content", element_type="environment", relevance_score=0.6, confidence_score=0.7, source="mock", timestamp=datetime.now()),
            ]
            history_insights = {}
            task_insights = {"task_type": "decision", "complexity": "high"}

            optimized_context = await self.engine._focused_optimization_strategy(
                request, context_elements, history_insights, task_insights
            )

            self.assertIsInstance(optimized_context, OptimizedContext)
            self.assertGreater(len(optimized_context.optimized_prompt), 0)
            self.assertLessEqual(len(optimized_context.context_elements), 8) # Focused strategy limit
            self.assertTrue(all(elem.element_type in ["task", "knowledge"] for elem in optimized_context.context_elements))

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
