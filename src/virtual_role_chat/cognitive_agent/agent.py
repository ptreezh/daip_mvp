"""
Core implementation of the CognitiveAgent class.

This module defines the CognitiveAgent class, which is the foundation of the
cognitive independence framework. Each agent maintains its own reasoning framework,
belief system, epistemology, and meta-cognitive capabilities.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .reasoning import ReasoningFramework
from .belief import BeliefSystem
from .epistemology import Epistemology
from .metacognition import MetaCognition
from .memory import AgentMemory


class CognitiveProfile(BaseModel):
    """
    Profile defining the cognitive characteristics of an agent.
    """
    reasoning_style: str = Field(
        description="The dominant reasoning style (e.g., 'analytical', 'intuitive', 'pragmatic')"
    )
    belief_structure: str = Field(
        description="The belief structure type (e.g., 'hierarchical', 'networked', 'bayesian')"
    )
    epistemological_approach: str = Field(
        description="The approach to knowledge (e.g., 'empirical', 'rationalist', 'constructivist')"
    )
    metacognitive_level: int = Field(
        description="The level of metacognitive capability (1-5)",
        ge=1, le=5
    )
    cognitive_biases: List[str] = Field(
        default_factory=list,
        description="List of cognitive biases that influence the agent's reasoning"
    )
    values: Dict[str, float] = Field(
        default_factory=dict,
        description="Dictionary of values and their importance (0.0-1.0)"
    )
    domain_expertise: Dict[str, float] = Field(
        default_factory=dict,
        description="Dictionary of domains and expertise levels (0.0-1.0)"
    )


class CognitiveAgent:
    """
    Core cognitive agent class that enables true cognitive independence.
    
    Each CognitiveAgent maintains its own reasoning framework, belief system,
    epistemology, and meta-cognitive capabilities, allowing it to function as
    an autonomous cognitive entity rather than a mere role-playing simulation.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        profile: CognitiveProfile,
        initial_knowledge: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a cognitive agent with its core components.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
            profile: Cognitive profile defining the agent's characteristics
            initial_knowledge: Initial knowledge base for the agent
        """
        self.agent_id = agent_id
        self.name = name
        self.profile = profile
        self.logger = logging.getLogger(f"cognitive_agent.{agent_id}")
        
        # Initialize core cognitive components
        self.reasoning_framework = self._initialize_reasoning_framework()
        self.belief_system = self._initialize_belief_system()
        self.epistemology = self._initialize_epistemology()
        self.meta_cognition = self._initialize_meta_cognition()
        self.memory = self._initialize_memory(initial_knowledge)
        
        self.logger.info(f"Cognitive agent '{name}' ({agent_id}) initialized")
    
    def _initialize_reasoning_framework(self) -> ReasoningFramework:
        """
        Initialize the reasoning framework based on the agent's profile.
        
        Returns:
            Initialized reasoning framework
        """
        self.logger.debug(f"Initializing reasoning framework with style: {self.profile.reasoning_style}")
        return ReasoningFramework(
            framework_type=self.profile.reasoning_style,
            agent_id=self.agent_id,
            domain_expertise=self.profile.domain_expertise,
            cognitive_biases=self.profile.cognitive_biases
        )
    
    def _initialize_belief_system(self) -> BeliefSystem:
        """
        Initialize the belief system based on the agent's profile.
        
        Returns:
            Initialized belief system
        """
        self.logger.debug(f"Initializing belief system with structure: {self.profile.belief_structure}")
        return BeliefSystem(
            structure_type=self.profile.belief_structure,
            agent_id=self.agent_id,
            values=self.profile.values
        )
    
    def _initialize_epistemology(self) -> Epistemology:
        """
        Initialize the epistemology based on the agent's profile.
        
        Returns:
            Initialized epistemology
        """
        self.logger.debug(f"Initializing epistemology with approach: {self.profile.epistemological_approach}")
        return Epistemology(
            approach=self.profile.epistemological_approach,
            agent_id=self.agent_id
        )
    
    def _initialize_meta_cognition(self) -> MetaCognition:
        """
        Initialize the meta-cognition based on the agent's profile.
        
        Returns:
            Initialized meta-cognition
        """
        self.logger.debug(f"Initializing meta-cognition with level: {self.profile.metacognitive_level}")
        return MetaCognition(
            level=self.profile.metacognitive_level,
            agent_id=self.agent_id
        )
    
    def _initialize_memory(self, initial_knowledge: Optional[Dict[str, Any]] = None) -> AgentMemory:
        """
        Initialize the agent memory with optional initial knowledge.
        
        Args:
            initial_knowledge: Initial knowledge to populate the memory with
            
        Returns:
            Initialized agent memory
        """
        self.logger.debug(f"Initializing agent memory")
        memory = AgentMemory(agent_id=self.agent_id)
        
        if initial_knowledge:
            self.logger.debug(f"Loading {len(initial_knowledge)} initial knowledge items")
            for key, value in initial_knowledge.items():
                memory.store(key, value, source="initialization")
        
        return memory
    
    async def process_input(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input through the cognitive pipeline.
        
        This method implements the core cognitive processing pipeline:
        1. Task identification through meta-cognition
        2. Knowledge retrieval from memory
        3. Reasoning based on the agent's framework
        4. Belief alignment
        5. Ensuring cognitive independence
        6. Memory update
        
        Args:
            input_data: Input data to process
            context: Context information for processing
            
        Returns:
            Processed output with the agent's independent perspective
        """
        self.logger.info(f"Processing input for agent '{self.name}'")
        
        # 1. Task identification
        task = await self.meta_cognition.identify_task(input_data, context)
        self.logger.debug(f"Identified task: {task}")
        
        # 2. Knowledge retrieval
        relevant_knowledge = await self.memory.retrieve_relevant(task)
        domain_knowledge = await self._retrieve_domain_knowledge(task)
        self.logger.debug(f"Retrieved {len(relevant_knowledge)} memory items and {len(domain_knowledge)} domain knowledge items")
        
        # 3. Apply reasoning framework
        reasoning_result = await self.reasoning_framework.apply(
            task, relevant_knowledge, domain_knowledge
        )
        self.logger.debug(f"Applied reasoning framework")
        
        # 4. Belief system filtering
        belief_aligned_result = await self.belief_system.filter(reasoning_result)
        self.logger.debug(f"Filtered through belief system")
        
        # 5. Ensure cognitive independence
        independent_perspective = await self.meta_cognition.ensure_independence(
            belief_aligned_result, context
        )
        self.logger.debug(f"Ensured cognitive independence")
        
        # 6. Update memory
        await self.memory.update(task, independent_perspective)
        self.logger.debug(f"Updated agent memory")
        
        return independent_perspective
    
    async def _retrieve_domain_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve domain-specific knowledge relevant to the task.
        
        Args:
            task: Task information
            
        Returns:
            Domain knowledge relevant to the task
        """
        # In a real implementation, this would query external knowledge sources
        # based on the agent's domain expertise
        return {}
    
    def get_cognitive_state(self) -> Dict[str, Any]:
        """
        Get the current cognitive state of the agent.
        
        Returns:
            Dictionary containing the agent's cognitive state
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "profile": self.profile.dict(),
            "reasoning_state": self.reasoning_framework.get_state(),
            "belief_state": self.belief_system.get_state(),
            "epistemology_state": self.epistemology.get_state(),
            "metacognition_state": self.meta_cognition.get_state(),
            "memory_stats": self.memory.get_stats()
        }
    
    def update_cognitive_state(self, state_updates: Dict[str, Any]) -> None:
        """
        Update the cognitive state of the agent.
        
        Args:
            state_updates: Dictionary containing state updates
        """
        if "profile" in state_updates:
            self.profile = CognitiveProfile(**state_updates["profile"])
            self.logger.info(f"Updated cognitive profile for agent '{self.name}'")
        
        if "reasoning_state" in state_updates:
            self.reasoning_framework.update_state(state_updates["reasoning_state"])
            self.logger.info(f"Updated reasoning state for agent '{self.name}'")
        
        if "belief_state" in state_updates:
            self.belief_system.update_state(state_updates["belief_state"])
            self.logger.info(f"Updated belief state for agent '{self.name}'")
        
        if "epistemology_state" in state_updates:
            self.epistemology.update_state(state_updates["epistemology_state"])
            self.logger.info(f"Updated epistemology state for agent '{self.name}'")
        
        if "metacognition_state" in state_updates:
            self.meta_cognition.update_state(state_updates["metacognition_state"])
            self.logger.info(f"Updated metacognition state for agent '{self.name}'")