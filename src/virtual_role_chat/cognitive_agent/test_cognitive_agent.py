"""Unit tests for the CognitiveAgent class and its components.
"""

import unittest
from unittest.mock import patch

from .agent import CognitiveAgent, CognitiveProfile
from .belief import BeliefSystem
from .epistemology import Epistemology
from .memory import AgentMemory
from .metacognition import MetaCognition
from .reasoning import ReasoningFramework


class TestCognitiveAgent(unittest.TestCase):
    """Test cases for the CognitiveAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.profile = CognitiveProfile(
            reasoning_style="analytical",
            belief_structure="hierarchical",
            epistemological_approach="empirical",
            metacognitive_level=3,
            cognitive_biases=["confirmation", "anchoring"],
            values={"truth": 0.9, "utility": 0.8, "autonomy": 0.7},
            domain_expertise={"science": 0.9, "philosophy": 0.7, "technology": 0.8}
        )
        
        self.agent = CognitiveAgent(
            agent_id="test_agent",
            name="Test Agent",
            profile=self.profile
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.agent.agent_id, "test_agent")
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.profile, self.profile)
        
        # Check that core components are initialized
        self.assertIsInstance(self.agent.reasoning_framework, ReasoningFramework)
        self.assertIsInstance(self.agent.belief_system, BeliefSystem)
        self.assertIsInstance(self.agent.epistemology, Epistemology)
        self.assertIsInstance(self.agent.meta_cognition, MetaCognition)
        self.assertIsInstance(self.agent.memory, AgentMemory)
    
    def test_get_cognitive_state(self):
        """Test getting the cognitive state."""
        state = self.agent.get_cognitive_state()
        
        self.assertEqual(state["agent_id"], "test_agent")
        self.assertEqual(state["name"], "Test Agent")
        self.assertEqual(state["profile"], self.profile.dict())
        
        # Check that state includes component states
        self.assertIn("reasoning_state", state)
        self.assertIn("belief_state", state)
        self.assertIn("epistemology_state", state)
        self.assertIn("metacognition_state", state)
        self.assertIn("memory_stats", state)
    
    @patch.object(MetaCognition, 'identify_task')
    @patch.object(AgentMemory, 'retrieve_relevant')
    @patch.object(ReasoningFramework, 'apply')
    @patch.object(BeliefSystem, 'filter')
    @patch.object(MetaCognition, 'ensure_independence')
    @patch.object(AgentMemory, 'update')
    async def test_process_input(self, mock_update, mock_ensure_independence, 
                               mock_filter, mock_apply, mock_retrieve_relevant, 
                               mock_identify_task):
        """Test the process_input method."""
        # Set up mock returns
        mock_identify_task.return_value = {"type": "test_task"}
        mock_retrieve_relevant.return_value = {"semantic": [{"content": "test knowledge"}]}
        mock_apply.return_value = {"conclusions": [{"content": "test conclusion"}]}
        mock_filter.return_value = {"conclusions": [{"content": "filtered conclusion"}]}
        mock_ensure_independence.return_value = {"conclusions": [{"content": "independent conclusion"}]}
        
        # Call process_input
        input_data = {"query": "test query"}
        context = {"session_id": "test_session"}
        result = await self.agent.process_input(input_data, context)
        
        # Check that each component method was called
        mock_identify_task.assert_called_once_with(input_data, context)
        mock_retrieve_relevant.assert_called_once()
        mock_apply.assert_called_once()
        mock_filter.assert_called_once()
        mock_ensure_independence.assert_called_once()
        mock_update.assert_called_once()
        
        # Check the result
        self.assertEqual(result, {"conclusions": [{"content": "independent conclusion"}]})


class TestReasoningFramework(unittest.TestCase):
    """Test cases for the ReasoningFramework class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.framework = ReasoningFramework(
            framework_type="analytical",
            agent_id="test_agent",
            domain_expertise={"science": 0.9, "philosophy": 0.7},
            cognitive_biases=["confirmation", "anchoring"]
        )
    
    def test_initialization(self):
        """Test that the framework initializes correctly."""
        self.assertEqual(self.framework.framework_type, "analytical")
        self.assertEqual(self.framework.agent_id, "test_agent")
        self.assertEqual(self.framework.domain_expertise, {"science": 0.9, "philosophy": 0.7})
        self.assertEqual(self.framework.cognitive_bias_ids, {"confirmation", "anchoring"})
        
        # Check that components are initialized
        self.assertIn("deduction", self.framework.inference_rules)
        self.assertIn("induction", self.framework.inference_rules)
        self.assertIn("elimination", self.framework.heuristics)
        self.assertIn("confirmation", self.framework.biases)
        self.assertIn("anchoring", self.framework.biases)
    
    async def test_apply(self):
        """Test applying the reasoning framework."""
        task = {"type": "problem_solving", "domain": "science"}
        relevant_knowledge = {"concepts": ["gravity", "motion"]}
        domain_knowledge = {"physics": {"principles": ["Newton's laws"]}}
        
        result = await self.framework.apply(task, relevant_knowledge, domain_knowledge)
        
        self.assertIn("conclusions", result)
        self.assertIn("reasoning_trace", result)
        self.assertEqual(result["reasoning_trace"]["framework_type"], "analytical")


class TestBeliefSystem(unittest.TestCase):
    """Test cases for the BeliefSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.belief_system = BeliefSystem(
            structure_type="hierarchical",
            agent_id="test_agent",
            values={"truth": 0.9, "utility": 0.8, "autonomy": 0.7}
        )
    
    def test_initialization(self):
        """Test that the belief system initializes correctly."""
        self.assertEqual(self.belief_system.structure_type, "hierarchical")
        self.assertEqual(self.belief_system.agent_id, "test_agent")
        
        # Check that values are initialized
        self.assertIn("truth", self.belief_system.values)
        self.assertIn("utility", self.belief_system.values)
        self.assertIn("autonomy", self.belief_system.values)
        
        # Check that principles are initialized
        self.assertIn("seek_truth", self.belief_system.principles)
        self.assertIn("maximize_utility", self.belief_system.principles)
    
    async def test_filter(self):
        """Test filtering through the belief system."""
        reasoning_result = {
            "conclusions": [
                {"content": "The earth is round", "confidence": 0.9},
                {"content": "Climate change is real", "confidence": 0.8}
            ]
        }
        
        filtered_result = await self.belief_system.filter(reasoning_result)
        
        self.assertIn("conclusions", filtered_result)
        self.assertIn("belief_system_trace", filtered_result)
        self.assertEqual(filtered_result["belief_system_trace"]["structure_type"], "hierarchical")
        
        # Check that conclusions are marked as filtered
        for conclusion in filtered_result["conclusions"]:
            self.assertTrue(conclusion["belief_filtered"])


class TestEpistemology(unittest.TestCase):
    """Test cases for the Epistemology class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.epistemology = Epistemology(
            approach="empirical",
            agent_id="test_agent"
        )
    
    def test_initialization(self):
        """Test that the epistemology initializes correctly."""
        self.assertEqual(self.epistemology.approach, "empirical")
        self.assertEqual(self.epistemology.agent_id, "test_agent")
        
        # Check that standards are initialized
        self.assertIn("scientific", self.epistemology.evidence_standards)
        self.assertIn("statistical", self.epistemology.evidence_standards)
        self.assertIn("general", self.epistemology.evidence_standards)
        
        # Check that strategies are initialized
        self.assertIn("observation", self.epistemology.validation_strategies)
        self.assertIn("replication", self.epistemology.validation_strategies)
        self.assertIn("triangulation", self.epistemology.validation_strategies)
    
    async def test_validate_claim(self):
        """Test validating a claim."""
        claim = "The earth is round"
        domain = "science"
        evidence = [
            {"content": "Satellite images show a round earth", "source": "NASA", "credibility": 0.9},
            {"content": "Ships disappear hull-first over the horizon", "source": "observation", "credibility": 0.8}
        ]
        
        result = await self.epistemology.validate_claim(claim, domain, evidence)
        
        self.assertEqual(result["claim"], claim)
        self.assertIn("is_valid", result)
        self.assertIn("confidence", result)
        self.assertIn("reasoning", result)
        self.assertIn("standard_applied", result)
        self.assertIn("strategy_applied", result)
        self.assertIn("evidence_quality", result)


class TestMetaCognition(unittest.TestCase):
    """Test cases for the MetaCognition class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.meta_cognition = MetaCognition(
            level=3,
            agent_id="test_agent"
        )
    
    def test_initialization(self):
        """Test that the meta-cognition initializes correctly."""
        self.assertEqual(self.meta_cognition.level, 3)
        self.assertEqual(self.meta_cognition.agent_id, "test_agent")
        
        # Check that task templates are initialized
        self.assertIn("information_retrieval", self.meta_cognition.task_templates)
        self.assertIn("explanation", self.meta_cognition.task_templates)
        self.assertIn("problem_solving", self.meta_cognition.task_templates)
        self.assertIn("decision_support", self.meta_cognition.task_templates)
        
        # Check that cognitive strategies are initialized
        self.assertIn("task_decomposition", self.meta_cognition.cognitive_strategies)
        self.assertIn("knowledge_integration", self.meta_cognition.cognitive_strategies)
        self.assertIn("perspective_taking", self.meta_cognition.cognitive_strategies)
    
    async def test_identify_task(self):
        """Test identifying a task."""
        input_data = {"query": "explain how gravity works"}
        context = {"session_id": "test_session"}
        
        task = await self.meta_cognition.identify_task(input_data, context)
        
        self.assertIn("type", task)
        self.assertIn("name", task)
        self.assertIn("description", task)
        self.assertIn("confidence", task)
        self.assertIn("required_capabilities", task)
        self.assertIn("handling_strategy", task)
        self.assertIn("cognitive_strategies", task)
    
    async def test_ensure_independence(self):
        """Test ensuring cognitive independence."""
        result = {
            "conclusions": [
                {"content": "Gravity is a fundamental force", "confidence": 0.9}
            ]
        }
        context = {"session_id": "test_session"}
        
        independent_result = await self.meta_cognition.ensure_independence(result, context)
        
        self.assertIn("conclusions", independent_result)
        self.assertIn("meta_cognitive_trace", independent_result)
        self.assertEqual(independent_result["meta_cognitive_trace"]["independence_level"], 3)
        self.assertTrue(independent_result["independence_enhanced"])


class TestAgentMemory(unittest.TestCase):
    """Test cases for the AgentMemory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = AgentMemory(agent_id="test_agent")
    
    def test_initialization(self):
        """Test that the memory initializes correctly."""
        self.assertEqual(self.memory.agent_id, "test_agent")
        
        # Check that categories are initialized
        self.assertIn("episodic", self.memory.categories)
        self.assertIn("semantic", self.memory.categories)
        self.assertIn("procedural", self.memory.categories)
        self.assertIn("conversations", self.memory.categories)
        self.assertIn("domain_knowledge", self.memory.categories)
        self.assertIn("problem_solving", self.memory.categories)
    
    def test_store(self):
        """Test storing a memory."""
        memory_id = self.memory.store(
            key="gravity",
            content="Gravity is a fundamental force",
            memory_type="semantic",
            importance=0.8,
            source="physics_knowledge"
        )
        
        self.assertTrue(memory_id in self.memory.memories)
        self.assertEqual(self.memory.memories[memory_id].content, "Gravity is a fundamental force")
        self.assertEqual(self.memory.memories[memory_id].memory_type, "semantic")
        self.assertEqual(self.memory.memories[memory_id].importance, 0.8)
        self.assertEqual(self.memory.memories[memory_id].source, "physics_knowledge")
    
    async def test_retrieve(self):
        """Test retrieving a memory."""
        # Store a memory first
        memory_id = self.memory.store(
            key="gravity",
            content="Gravity is a fundamental force",
            memory_type="semantic"
        )
        
        # Retrieve it
        memory = await self.memory.retrieve(memory_id)
        
        self.assertEqual(memory.id, memory_id)
        self.assertEqual(memory.content, "Gravity is a fundamental force")
        self.assertEqual(memory.memory_type, "semantic")
        self.assertEqual(memory.access_count, 1)
    
    async def test_search(self):
        """Test searching for memories."""
        # Store some memories
        self.memory.store(
            key="gravity",
            content="Gravity is a fundamental force",
            memory_type="semantic"
        )
        self.memory.store(
            key="relativity",
            content="Gravity curves spacetime according to relativity",
            memory_type="semantic"
        )
        self.memory.store(
            key="apple",
            content="Newton was inspired by a falling apple",
            memory_type="episodic"
        )
        
        # Search for gravity-related memories
        results = await self.memory.search("gravity")
        
        self.assertEqual(len(results), 2)  # Should find both gravity and relativity memories
    
    async def test_retrieve_relevant(self):
        """Test retrieving relevant memories for a task."""
        # Store some memories
        self.memory.store(
            key="gravity",
            content="Gravity is a fundamental force",
            memory_type="semantic"
        )
        self.memory.store(
            key="relativity",
            content="Gravity curves spacetime according to relativity",
            memory_type="semantic"
        )
        self.memory.store(
            key="apple",
            content="Newton was inspired by a falling apple",
            memory_type="episodic"
        )
        
        # Retrieve relevant memories for a gravity-related task
        task = {"type": "explanation", "description": "explain gravity"}
        relevant = await self.memory.retrieve_relevant(task)
        
        self.assertIn("semantic", relevant)
        self.assertTrue(len(relevant["semantic"]) > 0)
    
    async def test_update(self):
        """Test updating memory based on task execution."""
        # Define task and result
        task = {"type": "explanation", "description": "explain gravity"}
        result = {
            "conclusions": [
                {"content": "Gravity is a force that attracts objects with mass", "confidence": 0.9},
                {"content": "The strength of gravity decreases with distance", "confidence": 0.8}
            ]
        }
        
        # Update memory
        await self.memory.update(task, result)
        
        # Check that memories were stored
        self.assertTrue(len(self.memory.memories) > 0)
        
        # Check that at least one episodic memory was stored
        episodic_memories = [m for m in self.memory.memories.values() if m.memory_type == "episodic"]
        self.assertTrue(len(episodic_memories) > 0)


if __name__ == '__main__':
    unittest.main()