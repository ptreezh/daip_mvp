import unittest
from unittest.mock import MagicMock, patch
from src.core_services.context_quality_service import ContextQualityService, ReadabilityAnalyzer, CompletenessAnalyzer, CoherenceAnalyzer, SpecificityAnalyzer, ActionabilityAnalyzer

class TestContextQualityService(unittest.TestCase):
    def setUp(self):
        self.service = ContextQualityService()

    def test_evaluate_context_quality_basic(self):
        context = "This is a test context for quality evaluation."
        result = self.service.evaluate_context_quality(context)
        self.assertIsInstance(result, dict)
        self.assertIn("overall_score", result)
        self.assertIn("quality_level", result)

class TestReadabilityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ReadabilityAnalyzer()

    def test_analyze_basic(self):
        context = "This is a simple sentence. Another one here."
        score, analysis = self.analyzer.analyze(context, "general")
        self.assertIsInstance(score, float)
        self.assertIsInstance(analysis, dict)
        self.assertIn("issues", analysis)
        self.assertIn("suggestions", analysis)

class TestCompletenessAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CompletenessAnalyzer()

    def test_analyze_basic(self):
        context = "This is a complete context with background and objective. It has requirements."
        score, analysis = self.analyzer.analyze(context, "general")
        self.assertIsInstance(score, float)
        self.assertIsInstance(analysis, dict)

class TestCoherenceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CoherenceAnalyzer()

    def test_analyze_basic(self):
        context = "First, do this. Then, do that. Finally, finish it."
        score, analysis = self.analyzer.analyze(context, "general")
        self.assertIsInstance(score, float)
        self.assertIsInstance(analysis, dict)

class TestSpecificityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SpecificityAnalyzer()

    def test_analyze_basic(self):
        context = "The data shows 123 units were sold on 2025-08-27."
        score, analysis = self.analyzer.analyze(context, "general")
        self.assertIsInstance(score, float)
        self.assertIsInstance(analysis, dict)

class TestActionabilityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ActionabilityAnalyzer()

    def test_analyze_basic(self):
        context = "Please create a report by following these steps: 1. Collect data. 2. Analyze data. 3. Write report."
        score, analysis = self.analyzer.analyze(context, "general")
        self.assertIsInstance(score, float)
        self.assertIsInstance(analysis, dict)
