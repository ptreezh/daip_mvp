from unittest import TestCase, main

from src.core_services.synthesis_engine import SynthesisEngine


class TestSynthesisEngine(TestCase):
    def setUp(self):
        """Set up a new SynthesisEngine instance for each test."""
        self.engine = SynthesisEngine()

    def test_synthesize_opinions_with_multiple_opinions(self):
        """
        Tests that the engine correctly processes a list of opinions
        and returns the expected mock synthesis string.
        """
        opinions = ["The market will go up.", "The market will go down."]
        topic = "Market Outlook"
        result = self.engine.synthesize_opinions(opinions, topic)
        self.assertIn("mock synthesis of 2 opinions", result)
        self.assertIn("on the given topic", result)

    def test_synthesize_opinions_with_no_opinions(self):
        """
        Tests that the engine returns the correct message when an
        empty list of opinions is provided.
        """
        result = self.engine.synthesize_opinions([], "Any Topic")
        self.assertEqual(result, "No opinions were provided to synthesize.")

    def test_build_synthesis_prompt_structure(self):
        """
        Tests the internal prompt building logic to ensure it constructs
        a well-formed prompt for the (future) LLM.
        """
        opinions = ["First point of view.", "A contrasting second point."]
        topic = "Test Topic"
        # Accessing a private method for unit testing is acceptable here
        # to isolate the logic of prompt construction.
        prompt = self.engine._build_synthesis_prompt(opinions, topic)

        self.assertIn(f"on the topic of '{topic}'", prompt)
        self.assertIn('Opinion 1:\n"""\nFirst point of view.\n"""', prompt)
        self.assertIn('Opinion 2:\n"""\nA contrasting second point.\n"""', prompt)
        self.assertTrue(prompt.startswith("You are an expert synthesizer."))


if __name__ == "__main__":
    main()