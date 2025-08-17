# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 07:30:00
@Author  : DAIP-LIVE Team
@File    : consensus_customization.py
@Description:
    Custom consensus mechanism registration and management system.
    Implements requirement 7.5 - custom consensus mechanism registration.
"""
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from datetime import datetime
from enum import Enum
import statistics
import math

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConsensusType(str, Enum):
    """Types of consensus mechanisms."""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    EVIDENCE_BASED = "evidence_based"
    BAYESIAN = "bayesian"
    FUZZY_LOGIC = "fuzzy_logic"
    DELPHI_METHOD = "delphi_method"
    CUSTOM = "custom"


class VotingStrategy(str, Enum):
    """Voting strategies for consensus."""
    SIMPLE_MAJORITY = "simple_majority"
    SUPERMAJORITY = "supermajority"
    UNANIMOUS = "unanimous"
    PLURALITY = "plurality"
    RANKED_CHOICE = "ranked_choice"
    APPROVAL = "approval"


class EvidenceWeightingStrategy(str, Enum):
    """Strategies for weighting evidence."""
    EQUAL_WEIGHT = "equal_weight"
    SOURCE_RELIABILITY = "source_reliability"
    RECENCY_WEIGHTED = "recency_weighted"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    EXPERTISE_WEIGHTED = "expertise_weighted"
    COMBINED_FACTORS = "combined_factors"


class ConflictResolutionStrategy(str, Enum):
    """Strategies for resolving conflicts."""
    HIGHEST_CONFIDENCE = "highest_confidence"
    MOST_EVIDENCE = "most_evidence"
    EXPERT_OVERRIDE = "expert_override"
    WEIGHTED_AVERAGE = "weighted_average"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    HUMAN_INTERVENTION = "human_intervention"


class ConsensusInput(BaseModel):
    """Input for consensus calculation."""
    participant_id: str
    vote: Any  # Can be boolean, numeric, categorical, or complex object
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning: str = ""
    weight: float = Field(ge=0.0, default=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConsensusResult(BaseModel):
    """Result of consensus calculation."""
    consensus_value: Any
    confidence: float = Field(ge=0.0, le=1.0)
    agreement_level: float = Field(ge=0.0, le=1.0)
    participant_count: int
    supporting_participants: List[str] = Field(default_factory=list)
    dissenting_participants: List[str] = Field(default_factory=list)
    evidence_summary: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class ConsensusConfiguration(BaseModel):
    """Configuration for a consensus mechanism."""
    mechanism_id: str
    name: str
    description: str
    consensus_type: ConsensusType
    
    # Voting parameters
    voting_strategy: VotingStrategy = VotingStrategy.SIMPLE_MAJORITY
    minimum_participants: int = Field(ge=1, default=2)
    required_agreement: float = Field(ge=0.0, le=1.0, default=0.5)
    confidence_threshold: float = Field(ge=0.0, le=1.0, default=0.6)
    
    # Evidence weighting
    evidence_weighting: EvidenceWeightingStrategy = EvidenceWeightingStrategy.EQUAL_WEIGHT
    evidence_threshold: float = Field(ge=0.0, default=0.0)
    
    # Conflict resolution
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.HIGHEST_CONFIDENCE
    max_iterations: int = Field(ge=1, default=3)
    
    # Custom parameters
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class ConsensusAlgorithm(ABC):
    """
    Abstract base class for consensus algorithms.
    
    Custom consensus mechanisms must implement this interface.
    """
    
    def __init__(self, config: ConsensusConfiguration):
        """
        Initialize the consensus algorithm.
        
        Args:
            config: Configuration for the consensus mechanism
        """
        self.config = config
    
    @abstractmethod
    async def calculate_consensus(self, inputs: List[ConsensusInput]) -> ConsensusResult:
        """
        Calculate consensus from participant inputs.
        
        Args:
            inputs: List of participant inputs
            
        Returns:
            Consensus result
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, inputs: List[ConsensusInput]) -> List[str]:
        """
        Validate consensus inputs.
        
        Args:
            inputs: List of participant inputs
            
        Returns:
            List of validation errors
        """
        pass
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about this algorithm."""
        return {
            "mechanism_id": self.config.mechanism_id,
            "name": self.config.name,
            "type": self.config.consensus_type.value,
            "description": self.config.description,
            "parameters": self.config.dict()
        }


class MajorityVoteAlgorithm(ConsensusAlgorithm):
    """Simple majority voting algorithm."""
    
    async def calculate_consensus(self, inputs: List[ConsensusInput]) -> ConsensusResult:
        """Calculate majority vote consensus."""
        if not inputs:
            return ConsensusResult(
                consensus_value=None,
                confidence=0.0,
                agreement_level=0.0,
                participant_count=0,
                reasoning="No inputs provided"
            )
        
        # Count votes
        vote_counts = {}
        total_confidence = 0.0
        participants = []
        
        for input_item in inputs:
            vote = str(input_item.vote)  # Convert to string for counting
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
            total_confidence += input_item.confidence
            participants.append(input_item.participant_id)
        
        # Find majority
        total_votes = len(inputs)
        majority_vote = max(vote_counts.items(), key=lambda x: x[1])
        majority_count = majority_vote[1]
        consensus_value = majority_vote[0]
        
        # Calculate agreement level
        agreement_level = majority_count / total_votes
        
        # Calculate confidence
        avg_confidence = total_confidence / total_votes
        confidence = avg_confidence * agreement_level
        
        # Determine supporting and dissenting participants
        supporting = []
        dissenting = []
        
        for input_item in inputs:
            if str(input_item.vote) == consensus_value:
                supporting.append(input_item.participant_id)
            else:
                dissenting.append(input_item.participant_id)
        
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=confidence,
            agreement_level=agreement_level,
            participant_count=total_votes,
            supporting_participants=supporting,
            dissenting_participants=dissenting,
            reasoning=f"Majority vote: {majority_count}/{total_votes} participants agreed on '{consensus_value}'"
        )
    
    def validate_inputs(self, inputs: List[ConsensusInput]) -> List[str]:
        """Validate inputs for majority voting."""
        errors = []
        
        if len(inputs) < self.config.minimum_participants:
            errors.append(f"Minimum {self.config.minimum_participants} participants required")
        
        for i, input_item in enumerate(inputs):
            if input_item.confidence < 0.0 or input_item.confidence > 1.0:
                errors.append(f"Input {i}: confidence must be between 0.0 and 1.0")
        
        return errors


class WeightedVoteAlgorithm(ConsensusAlgorithm):
    """Weighted voting algorithm based on participant weights."""
    
    async def calculate_consensus(self, inputs: List[ConsensusInput]) -> ConsensusResult:
        """Calculate weighted vote consensus."""
        if not inputs:
            return ConsensusResult(
                consensus_value=None,
                confidence=0.0,
                agreement_level=0.0,
                participant_count=0,
                reasoning="No inputs provided"
            )
        
        # Calculate weighted votes
        weighted_votes = {}
        total_weight = 0.0
        weighted_confidence = 0.0
        participants = []
        
        for input_item in inputs:
            vote = str(input_item.vote)
            weight = input_item.weight
            
            weighted_votes[vote] = weighted_votes.get(vote, 0.0) + weight
            total_weight += weight
            weighted_confidence += input_item.confidence * weight
            participants.append(input_item.participant_id)
        
        # Find weighted majority
        majority_vote = max(weighted_votes.items(), key=lambda x: x[1])
        majority_weight = majority_vote[1]
        consensus_value = majority_vote[0]
        
        # Calculate agreement level (weighted)
        agreement_level = majority_weight / total_weight if total_weight > 0 else 0.0
        
        # Calculate confidence (weighted average)
        base_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0
        # Boost confidence based on agreement level and weight distribution
        confidence = base_confidence * (0.5 + agreement_level * 0.5)
        
        # Determine supporting and dissenting participants
        supporting = []
        dissenting = []
        
        for input_item in inputs:
            if str(input_item.vote) == consensus_value:
                supporting.append(input_item.participant_id)
            else:
                dissenting.append(input_item.participant_id)
        
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=confidence,
            agreement_level=agreement_level,
            participant_count=len(inputs),
            supporting_participants=supporting,
            dissenting_participants=dissenting,
            reasoning=f"Weighted vote: {majority_weight:.2f}/{total_weight:.2f} weight for '{consensus_value}'"
        )
    
    def validate_inputs(self, inputs: List[ConsensusInput]) -> List[str]:
        """Validate inputs for weighted voting."""
        errors = []
        
        if len(inputs) < self.config.minimum_participants:
            errors.append(f"Minimum {self.config.minimum_participants} participants required")
        
        total_weight = sum(input_item.weight for input_item in inputs)
        if total_weight <= 0:
            errors.append("Total weight must be greater than 0")
        
        for i, input_item in enumerate(inputs):
            if input_item.weight < 0:
                errors.append(f"Input {i}: weight must be non-negative")
            if input_item.confidence < 0.0 or input_item.confidence > 1.0:
                errors.append(f"Input {i}: confidence must be between 0.0 and 1.0")
        
        return errors


class EvidenceBasedAlgorithm(ConsensusAlgorithm):
    """Evidence-based consensus algorithm."""
    
    async def calculate_consensus(self, inputs: List[ConsensusInput]) -> ConsensusResult:
        """Calculate evidence-based consensus."""
        if not inputs:
            return ConsensusResult(
                consensus_value=None,
                confidence=0.0,
                agreement_level=0.0,
                participant_count=0,
                reasoning="No inputs provided"
            )
        
        # Analyze evidence for each vote option
        vote_evidence = {}
        participants = []
        
        for input_item in inputs:
            vote = str(input_item.vote)
            participants.append(input_item.participant_id)
            
            if vote not in vote_evidence:
                vote_evidence[vote] = {
                    "evidence_count": 0,
                    "evidence_quality": 0.0,
                    "confidence_sum": 0.0,
                    "participants": [],
                    "evidence_items": []
                }
            
            evidence_data = vote_evidence[vote]
            evidence_data["participants"].append(input_item.participant_id)
            evidence_data["confidence_sum"] += input_item.confidence
            
            # Analyze evidence
            for evidence in input_item.evidence:
                evidence_data["evidence_count"] += 1
                evidence_data["evidence_items"].append(evidence)
                
                # Simple evidence quality scoring
                quality = evidence.get("credibility", 0.5)
                if "source" in evidence:
                    quality += 0.2
                if "timestamp" in evidence:
                    quality += 0.1
                
                evidence_data["evidence_quality"] += min(quality, 1.0)
        
        # Calculate evidence scores for each vote
        evidence_scores = {}
        for vote, data in vote_evidence.items():
            participant_count = len(data["participants"])
            avg_confidence = data["confidence_sum"] / participant_count if participant_count > 0 else 0.0
            avg_evidence_quality = data["evidence_quality"] / max(data["evidence_count"], 1)
            
            # Combined evidence score
            evidence_scores[vote] = {
                "score": avg_confidence * 0.4 + avg_evidence_quality * 0.4 + (data["evidence_count"] / 10.0) * 0.2,
                "participant_count": participant_count,
                "evidence_count": data["evidence_count"],
                "avg_confidence": avg_confidence,
                "avg_quality": avg_evidence_quality
            }
        
        # Find consensus based on evidence
        best_vote = max(evidence_scores.items(), key=lambda x: x[1]["score"])
        consensus_value = best_vote[0]
        best_score = best_vote[1]
        
        # Calculate agreement level and confidence
        total_participants = len(inputs)
        agreement_level = best_score["participant_count"] / total_participants
        confidence = best_score["score"]
        
        # Determine supporting and dissenting participants
        supporting = vote_evidence[consensus_value]["participants"]
        dissenting = [p for p in participants if p not in supporting]
        
        # Create evidence summary
        evidence_summary = {
            "total_evidence_items": sum(data["evidence_count"] for data in vote_evidence.values()),
            "consensus_evidence_count": vote_evidence[consensus_value]["evidence_count"],
            "consensus_avg_quality": best_score["avg_quality"],
            "vote_breakdown": evidence_scores
        }
        
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=confidence,
            agreement_level=agreement_level,
            participant_count=total_participants,
            supporting_participants=supporting,
            dissenting_participants=dissenting,
            evidence_summary=evidence_summary,
            reasoning=f"Evidence-based consensus: '{consensus_value}' with score {best_score['score']:.3f} "
                     f"({best_score['evidence_count']} evidence items, {best_score['participant_count']} participants)"
        )
    
    def validate_inputs(self, inputs: List[ConsensusInput]) -> List[str]:
        """Validate inputs for evidence-based consensus."""
        errors = []
        
        if len(inputs) < self.config.minimum_participants:
            errors.append(f"Minimum {self.config.minimum_participants} participants required")
        
        total_evidence = sum(len(input_item.evidence) for input_item in inputs)
        if total_evidence < self.config.evidence_threshold:
            errors.append(f"Minimum {self.config.evidence_threshold} evidence items required")
        
        return errors


class BayesianConsensusAlgorithm(ConsensusAlgorithm):
    """Bayesian consensus algorithm using prior beliefs and evidence."""
    
    async def calculate_consensus(self, inputs: List[ConsensusInput]) -> ConsensusResult:
        """Calculate Bayesian consensus."""
        if not inputs:
            return ConsensusResult(
                consensus_value=None,
                confidence=0.0,
                agreement_level=0.0,
                participant_count=0,
                reasoning="No inputs provided"
            )
        
        # For binary decisions (True/False), use Bayesian updating
        true_votes = []
        false_votes = []
        
        for input_item in inputs:
            vote_value = input_item.vote
            if isinstance(vote_value, bool):
                if vote_value:
                    true_votes.append(input_item)
                else:
                    false_votes.append(input_item)
            elif isinstance(vote_value, str):
                if vote_value.lower() in ['true', 'yes', '1', 'positive']:
                    true_votes.append(input_item)
                else:
                    false_votes.append(input_item)
        
        # Prior probability (uniform prior)
        prior_true = 0.5
        prior_false = 0.5
        
        # Calculate likelihood based on confidence
        likelihood_true = 1.0
        likelihood_false = 1.0
        
        for vote in true_votes:
            likelihood_true *= vote.confidence
            likelihood_false *= (1.0 - vote.confidence)
        
        for vote in false_votes:
            likelihood_false *= vote.confidence
            likelihood_true *= (1.0 - vote.confidence)
        
        # Calculate posterior probabilities
        evidence = likelihood_true * prior_true + likelihood_false * prior_false
        
        if evidence > 0:
            posterior_true = (likelihood_true * prior_true) / evidence
            posterior_false = (likelihood_false * prior_false) / evidence
        else:
            posterior_true = 0.5
            posterior_false = 0.5
        
        # Determine consensus
        if posterior_true > posterior_false:
            consensus_value = True
            confidence = posterior_true
            supporting = [v.participant_id for v in true_votes]
            dissenting = [v.participant_id for v in false_votes]
        else:
            consensus_value = False
            confidence = posterior_false
            supporting = [v.participant_id for v in false_votes]
            dissenting = [v.participant_id for v in true_votes]
        
        agreement_level = len(supporting) / len(inputs)
        
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=confidence,
            agreement_level=agreement_level,
            participant_count=len(inputs),
            supporting_participants=supporting,
            dissenting_participants=dissenting,
            reasoning=f"Bayesian consensus: P(True)={posterior_true:.3f}, P(False)={posterior_false:.3f}",
            metadata={
                "posterior_true": posterior_true,
                "posterior_false": posterior_false,
                "likelihood_true": likelihood_true,
                "likelihood_false": likelihood_false
            }
        )
    
    def validate_inputs(self, inputs: List[ConsensusInput]) -> List[str]:
        """Validate inputs for Bayesian consensus."""
        errors = []
        
        if len(inputs) < self.config.minimum_participants:
            errors.append(f"Minimum {self.config.minimum_participants} participants required")
        
        for i, input_item in enumerate(inputs):
            if input_item.confidence < 0.0 or input_item.confidence > 1.0:
                errors.append(f"Input {i}: confidence must be between 0.0 and 1.0")
        
        return errors


class ConsensusRegistry:
    """
    Registry for consensus algorithms and configurations.
    
    This class manages the registration and instantiation of
    custom consensus mechanisms.
    """
    
    def __init__(self):
        """Initialize the consensus registry."""
        self.algorithms: Dict[str, type] = {}
        self.configurations: Dict[str, ConsensusConfiguration] = {}
        
        # Register built-in algorithms
        self._register_builtin_algorithms()
        
        logger.info("ConsensusRegistry initialized")
    
    def _register_builtin_algorithms(self) -> None:
        """Register built-in consensus algorithms."""
        self.algorithms["majority_vote"] = MajorityVoteAlgorithm
        self.algorithms["weighted_vote"] = WeightedVoteAlgorithm
        self.algorithms["evidence_based"] = EvidenceBasedAlgorithm
        self.algorithms["bayesian"] = BayesianConsensusAlgorithm
        
        logger.info("Registered built-in consensus algorithms")
    
    def register_algorithm(self, algorithm_id: str, algorithm_class: type) -> bool:
        """
        Register a custom consensus algorithm.
        
        Args:
            algorithm_id: Unique identifier for the algorithm
            algorithm_class: Algorithm class implementing ConsensusAlgorithm
            
        Returns:
            True if registration was successful
        """
        if not issubclass(algorithm_class, ConsensusAlgorithm):
            logger.error(f"Algorithm class must inherit from ConsensusAlgorithm")
            return False
        
        if algorithm_id in self.algorithms:
            logger.warning(f"Algorithm '{algorithm_id}' already registered. Overwriting.")
        
        self.algorithms[algorithm_id] = algorithm_class
        logger.info(f"Registered consensus algorithm: {algorithm_id}")
        return True
    
    def register_configuration(self, config: ConsensusConfiguration) -> bool:
        """
        Register a consensus configuration.
        
        Args:
            config: Consensus configuration to register
            
        Returns:
            True if registration was successful
        """
        if config.mechanism_id in self.configurations:
            logger.warning(f"Configuration '{config.mechanism_id}' already exists. Overwriting.")
        
        self.configurations[config.mechanism_id] = config
        logger.info(f"Registered consensus configuration: {config.mechanism_id}")
        return True
    
    def create_consensus_instance(self, mechanism_id: str) -> Optional[ConsensusAlgorithm]:
        """
        Create an instance of a consensus algorithm.
        
        Args:
            mechanism_id: ID of the consensus mechanism configuration
            
        Returns:
            Consensus algorithm instance, or None if creation failed
        """
        if mechanism_id not in self.configurations:
            logger.error(f"Configuration '{mechanism_id}' not found")
            return None
        
        config = self.configurations[mechanism_id]
        algorithm_type = config.consensus_type.value
        
        if algorithm_type not in self.algorithms:
            logger.error(f"Algorithm type '{algorithm_type}' not registered")
            return None
        
        try:
            algorithm_class = self.algorithms[algorithm_type]
            instance = algorithm_class(config)
            return instance
        except Exception as e:
            logger.error(f"Error creating consensus instance: {e}")
            return None
    
    def list_algorithms(self) -> List[str]:
        """List all registered algorithm types."""
        return list(self.algorithms.keys())
    
    def list_configurations(self) -> List[ConsensusConfiguration]:
        """List all registered configurations."""
        return list(self.configurations.values())
    
    def get_configuration(self, mechanism_id: str) -> Optional[ConsensusConfiguration]:
        """Get a configuration by ID."""
        return self.configurations.get(mechanism_id)


class ConsensusManager:
    """
    High-level manager for consensus mechanisms.
    
    This class provides a convenient interface for managing and executing
    consensus algorithms with custom configurations.
    """
    
    def __init__(self):
        """Initialize the consensus manager."""
        self.registry = ConsensusRegistry()
        self.active_sessions: Dict[str, ConsensusAlgorithm] = {}
        
        # Create default configurations
        self._create_default_configurations()
        
        logger.info("ConsensusManager initialized")
    
    def _create_default_configurations(self) -> None:
        """Create default consensus configurations."""
        # Simple majority vote
        majority_config = ConsensusConfiguration(
            mechanism_id="simple_majority",
            name="Simple Majority Vote",
            description="Basic majority voting mechanism",
            consensus_type=ConsensusType.MAJORITY_VOTE,
            voting_strategy=VotingStrategy.SIMPLE_MAJORITY,
            minimum_participants=2,
            required_agreement=0.5
        )
        
        # Weighted expert vote
        weighted_config = ConsensusConfiguration(
            mechanism_id="weighted_expert",
            name="Weighted Expert Vote",
            description="Weighted voting based on expertise",
            consensus_type=ConsensusType.WEIGHTED_VOTE,
            voting_strategy=VotingStrategy.SIMPLE_MAJORITY,
            minimum_participants=2,
            required_agreement=0.6,
            evidence_weighting=EvidenceWeightingStrategy.EXPERTISE_WEIGHTED
        )
        
        # Evidence-based consensus
        evidence_config = ConsensusConfiguration(
            mechanism_id="evidence_based",
            name="Evidence-Based Consensus",
            description="Consensus based on evidence quality and quantity",
            consensus_type=ConsensusType.EVIDENCE_BASED,
            minimum_participants=2,
            evidence_threshold=1.0,
            confidence_threshold=0.7
        )
        
        # Bayesian consensus
        bayesian_config = ConsensusConfiguration(
            mechanism_id="bayesian_consensus",
            name="Bayesian Consensus",
            description="Bayesian updating for binary decisions",
            consensus_type=ConsensusType.BAYESIAN,
            minimum_participants=2,
            confidence_threshold=0.8
        )
        
        # Register configurations
        self.registry.register_configuration(majority_config)
        self.registry.register_configuration(weighted_config)
        self.registry.register_configuration(evidence_config)
        self.registry.register_configuration(bayesian_config)
        
        logger.info("Created default consensus configurations")
    
    def register_custom_algorithm(self, algorithm_id: str, algorithm_class: type) -> bool:
        """Register a custom consensus algorithm."""
        return self.registry.register_algorithm(algorithm_id, algorithm_class)
    
    def create_custom_configuration(
        self,
        mechanism_id: str,
        name: str,
        consensus_type: ConsensusType,
        **kwargs
    ) -> ConsensusConfiguration:
        """
        Create a custom consensus configuration.
        
        Args:
            mechanism_id: Unique ID for the mechanism
            name: Human-readable name
            consensus_type: Type of consensus mechanism
            **kwargs: Additional configuration parameters
            
        Returns:
            Created configuration
        """
        config = ConsensusConfiguration(
            mechanism_id=mechanism_id,
            name=name,
            description=kwargs.get("description", f"Custom {consensus_type.value} mechanism"),
            consensus_type=consensus_type,
            **{k: v for k, v in kwargs.items() if k != "description"}
        )
        
        self.registry.register_configuration(config)
        return config
    
    async def calculate_consensus(
        self,
        mechanism_id: str,
        inputs: List[ConsensusInput],
        session_id: str = None
    ) -> Optional[ConsensusResult]:
        """
        Calculate consensus using a specific mechanism.
        
        Args:
            mechanism_id: ID of the consensus mechanism to use
            inputs: List of participant inputs
            session_id: Optional session ID for tracking
            
        Returns:
            Consensus result, or None if calculation failed
        """
        try:
            # Get or create algorithm instance
            if session_id and session_id in self.active_sessions:
                algorithm = self.active_sessions[session_id]
            else:
                algorithm = self.registry.create_consensus_instance(mechanism_id)
                if not algorithm:
                    return None
                
                if session_id:
                    self.active_sessions[session_id] = algorithm
            
            # Validate inputs
            validation_errors = algorithm.validate_inputs(inputs)
            if validation_errors:
                logger.error(f"Input validation failed: {validation_errors}")
                return ConsensusResult(
                    consensus_value=None,
                    confidence=0.0,
                    agreement_level=0.0,
                    participant_count=len(inputs),
                    reasoning=f"Validation failed: {'; '.join(validation_errors)}"
                )
            
            # Calculate consensus
            result = await algorithm.calculate_consensus(inputs)
            
            logger.info(f"Calculated consensus using '{mechanism_id}': {result.consensus_value} "
                       f"(confidence: {result.confidence:.3f}, agreement: {result.agreement_level:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating consensus: {e}")
            return None
    
    def end_session(self, session_id: str) -> bool:
        """End a consensus session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Ended consensus session: {session_id}")
            return True
        return False
    
    def get_available_mechanisms(self) -> List[Dict[str, Any]]:
        """Get information about available consensus mechanisms."""
        mechanisms = []
        
        for config in self.registry.list_configurations():
            mechanisms.append({
                "mechanism_id": config.mechanism_id,
                "name": config.name,
                "description": config.description,
                "type": config.consensus_type.value,
                "voting_strategy": config.voting_strategy.value,
                "minimum_participants": config.minimum_participants,
                "required_agreement": config.required_agreement
            })
        
        return mechanisms
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information."""
        return {
            "registered_algorithms": len(self.registry.algorithms),
            "registered_configurations": len(self.registry.configurations),
            "active_sessions": len(self.active_sessions),
            "algorithm_types": self.registry.list_algorithms(),
            "configuration_ids": [c.mechanism_id for c in self.registry.list_configurations()],
            "session_ids": list(self.active_sessions.keys())
        }