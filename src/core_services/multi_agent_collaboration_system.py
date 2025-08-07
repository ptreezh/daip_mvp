# -*- coding: utf-8 -*-
"""
Multi-Agent Collaboration System for Personal Intelligence Hub

Technical Specifications and Architecture Design

This document provides detailed technical specifications for implementing 
the multi-agent collaboration system that supports both Secretariat automation 
and Forum debate functionality.
"""

from typing import Any, Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import asyncio
from abc import ABC, abstractmethod

# ============================================================================
# Core Data Models
# ============================================================================

class AgentType(str, Enum):
    """Agent type enumeration"""
    SECRETARIAT = "secretariat"
    FORUM_EXPERT = "forum_expert"
    COORDINATOR = "coordinator"
    MODERATOR = "moderator"
    SYNTHESIZER = "synthesizer"
    FACILITATOR = "facilitator"

class AgentSpecialization(str, Enum):
    """Agent specialization areas"""
    # Secretariat specializations
    TASK_MANAGER = "task_manager"
    SCHEDULER = "scheduler"
    NOTE_TAKER = "note_taker"
    FOLLOW_UP = "follow_up"
    
    # Forum expert specializations
    TECHNICAL = "technical"
    BUSINESS = "business"
    RESEARCH = "research"
    STRATEGY = "strategy"
    DESIGN = "design"
    MARKETING = "marketing"
    LEGAL = "legal"
    FINANCIAL = "financial"
    
    # Coordinator specializations
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"
    CONSENSUS_BUILDER = "consensus_builder"
    CONFLICT_RESOLVER = "conflict_resolver"

class CollaborationMode(str, Enum):
    """Collaboration modes"""
    SECRETARIAT_AUTOMATION = "secretariat_automation"
    FORUM_DEBATE = "forum_debate"
    HYBRID_COLLABORATION = "hybrid_collaboration"
    AD_HOC_DISCUSSION = "ad_hoc_discussion"

class ConsensusMethod(str, Enum):
    """Consensus computation methods"""
    SIMPLE_MAJORITY = "simple_majority"
    WEIGHTED_VOTING = "weighted_voting"
    BAYESIAN_CONSENSUS = "bayesian_consensus"
    COGNITIVE_DIVERSITY = "cognitive_diversity"
    DELPHI_METHOD = "delphi_method"
    NOMINAL_GROUP = "nominal_group"

class InstitutionalPrimitive(str, Enum):
    """Institutional primitive types"""
    INTERPRET_INTENT = "interpret_intent"
    FORM_TEAM = "form_team"
    EXECUTE_WORKFLOW = "execute_workflow"
    MULTI_AGENT_COLLABORATE = "multi_agent_collaborate"
    USER_INTERVENE = "user_intervene"
    DYNAMIC_WORKFLOW_ADJUST = "dynamic_workflow_adjust"
    COMPUTE_CONSENSUS = "compute_consensus"
    GENERATE_REPORT = "generate_report"
    MONITOR_PROCESS = "monitor_process"

@dataclass
class AgentProfile:
    """Agent profile and capabilities"""
    agent_id: str
    name: str
    agent_type: AgentType
    specializations: List[AgentSpecialization]
    expertise_domains: List[str]
    communication_style: str
    personality_traits: Dict[str, float]
    capabilities: List[str]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    availability: bool = True
    max_concurrent_tasks: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)

@dataclass
class AgentCapability:
    """Agent capability definition"""
    capability_id: str
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    complexity_score: float
    required_expertise: List[str]
    performance_threshold: float
    resource_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationSession:
    """Collaboration session context"""
    session_id: str
    session_name: str
    collaboration_mode: CollaborationMode
    initiator_id: str
    participants: List[str]
    topic: str
    objectives: List[str]
    institutional_primitives: List[InstitutionalPrimitive]
    consensus_method: ConsensusMethod
    constraints: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentMessage:
    """Message exchanged between agents"""
    message_id: str
    sender_id: str
    receiver_id: Union[str, List[str]]  # Single agent or broadcast
    message_type: str
    content: Any
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-5, 5 being highest
    requires_response: bool = False
    response_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None

@dataclass
class ConsensusInput:
    """Input for consensus computation"""
    agent_id: str
    position: Union[str, float, Dict[str, Any]]
    confidence: float
    reasoning: str
    evidence: List[str] = field(default_factory=list)
    weight: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ConsensusResult:
    """Result of consensus computation"""
    consensus_value: Any
    confidence: float
    participants: List[str]
    consensus_method: ConsensusMethod
    reasoning_trace: List[str]
    conflict_resolution: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    computation_time: float = 0.0

@dataclass
class WorkflowStep:
    """Single step in a collaborative workflow"""
    step_id: str
    primitive_type: InstitutionalPrimitive
    assigned_agents: List[str]
    inputs: Dict[str, Any]
    expected_outputs: List[str]
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: float = 300.0
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class CollaborativeTask:
    """Task that requires multi-agent collaboration"""
    task_id: str
    title: str
    description: str
    session_id: str
    workflow_steps: List[WorkflowStep]
    priority: int
    estimated_duration: float
    assigned_team: List[str]
    progress: float = 0.0
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None

# ============================================================================
# Core AI Capabilities
# ============================================================================

class IntentInterpreter:
    """Interprets user intent and routes to appropriate workflows"""
    
    def __init__(self):
        self.intent_patterns = {
            "secretariat_automation": [
                "schedule", "meeting", "task", "follow up", "notes", "agenda"
            ],
            "forum_debate": [
                "debate", "discuss", "analyze", "evaluate", "perspectives", "opinion"
            ],
            "expert_consultation": [
                "expert", "advice", "recommendation", "specialist", "consult"
            ]
        }
    
    async def interpret_intent(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Interpret user intent and determine collaboration mode
        
        Returns:
            Dict containing:
            - intent_type: Primary intent
            - collaboration_mode: Recommended mode
            - required_agents: List of needed agent types
            - confidence: Intent confidence score
            - clarifying_questions: Questions for ambiguous intents
        """
        # Implementation would use NLP and pattern matching
        pass

class TeamFormationEngine:
    """Dynamically forms expert teams based on task requirements"""
    
    def __init__(self, agent_registry):
        self.agent_registry = agent_registry
        self.formation_strategies = {
            "expertise_matching": self._match_by_expertise,
            "performance_based": self._match_by_performance,
            "diversity_optimized": self._match_by_diversity,
            "load_balanced": self._match_by_load
        }
    
    async def form_team(
        self,
        task_requirements: Dict[str, Any],
        collaboration_mode: CollaborationMode,
        constraints: Dict[str, Any] = None
    ) -> List[str]:
        """
        Form optimal team for given requirements
        
        Args:
            task_requirements: Task specifications and needs
            collaboration_mode: Mode of collaboration
            constraints: Team formation constraints
            
        Returns:
            List of agent IDs for the optimal team
        """
        # Implementation would use optimization algorithms
        pass
    
    def _match_by_expertise(self, requirements: Dict[str, Any]) -> List[str]:
        """Match agents based on expertise requirements"""
        pass
    
    def _match_by_performance(self, requirements: Dict[str, Any]) -> List[str]:
        """Match agents based on historical performance"""
        pass
    
    def _match_by_diversity(self, requirements: Dict[str, Any]) -> List[str]:
        """Match agents to maximize cognitive diversity"""
        pass
    
    def _match_by_load(self, requirements: Dict[str, Any]) -> List[str]:
        """Match agents based on current workload"""
        pass

class WorkflowOrchestrator:
    """Orchestrates complex multi-agent workflows"""
    
    def __init__(self):
        self.workflow_templates = self._load_workflow_templates()
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Load workflow templates"""
        return {
            "secretariat_meeting": {
                "steps": [
                    {"step_id": "schedule", "type": "task", "description": "Schedule meeting"},
                    {"step_id": "invite", "type": "task", "description": "Send invitations"},
                    {"step_id": "prepare_agenda", "type": "task", "description": "Prepare agenda"}
                ]
            },
            "forum_debate": {
                "steps": [
                    {"step_id": "opening", "type": "task", "description": "Opening statements"},
                    {"step_id": "debate", "type": "task", "description": "Structured debate"},
                    {"step_id": "consensus", "type": "decision", "description": "Reach consensus"}
                ]
            }
        }
    
    async def execute_workflow(
        self,
        workflow_definition: Dict[str, Any],
        session_context: CollaborationSession
    ) -> Dict[str, Any]:
        """
        Execute a collaborative workflow
        
        Args:
            workflow_definition: Workflow specification
            session_context: Collaboration session context
            
        Returns:
            Workflow execution results
        """
        workflow_id = str(uuid.uuid4())
        
        # Initialize workflow execution
        execution_context = {
            "workflow_id": workflow_id,
            "session_id": session_context.session_id,
            "steps": workflow_definition["steps"],
            "current_step": 0,
            "status": "running",
            "results": {},
            "start_time": datetime.now()
        }
        
        self.active_workflows[workflow_id] = execution_context
        
        try:
            # Execute workflow steps
            results = await self._execute_workflow_steps(
                execution_context, 
                session_context
            )
            
            execution_context["status"] = "completed"
            execution_context["results"] = results
            execution_context["end_time"] = datetime.now()
            
            return results
            
        except Exception as e:
            execution_context["status"] = "failed"
            execution_context["error"] = str(e)
            raise
    
    async def _execute_workflow_steps(
        self,
        execution_context: Dict[str, Any],
        session_context: CollaborationSession
    ) -> Dict[str, Any]:
        """Execute individual workflow steps"""
        results = {}
        
        for i, step in enumerate(execution_context["steps"]):
            execution_context["current_step"] = i
            
            # Execute institutional primitive
            step_result = await self._execute_primitive(
                step,
                session_context,
                execution_context
            )
            
            results[step["step_id"]] = step_result
            
            # Check for workflow adjustment needs
            if await self._needs_workflow_adjustment(step_result, execution_context):
                await self._adjust_workflow(execution_context, step_result)
        
        return results
    
    async def _execute_primitive(
        self,
        step: Dict[str, Any],
        session_context: CollaborationSession,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single institutional primitive"""
        primitive_type = step["primitive_type"]
        
        if primitive_type == InstitutionalPrimitive.INTERPRET_INTENT:
            return await self._interpret_intent_primitive(step, session_context)
        elif primitive_type == InstitutionalPrimitive.FORM_TEAM:
            return await self._form_team_primitive(step, session_context)
        elif primitive_type == InstitutionalPrimitive.EXECUTE_WORKFLOW:
            return await self._execute_workflow_primitive(step, session_context)
        elif primitive_type == InstitutionalPrimitive.MULTI_AGENT_COLLABORATE:
            return await self._multi_agent_collaborate_primitive(step, session_context)
        elif primitive_type == InstitutionalPrimitive.COMPUTE_CONSENSUS:
            return await self._compute_consensus_primitive(step, session_context)
        elif primitive_type == InstitutionalPrimitive.GENERATE_REPORT:
            return await self._generate_report_primitive(step, session_context)
        else:
            raise ValueError(f"Unknown primitive type: {primitive_type}")

class ConsensusEngine:
    """Computes consensus from multiple agent opinions"""
    
    def __init__(self):
        self.consensus_algorithms = {
            ConsensusMethod.SIMPLE_MAJORITY: SimpleMajorityAlgorithm(),
            ConsensusMethod.WEIGHTED_VOTING: WeightedVotingAlgorithm(),
            ConsensusMethod.BAYESIAN_CONSENSUS: BayesianConsensusAlgorithm(),
            ConsensusMethod.COGNITIVE_DIVERSITY: CognitiveDiversityAlgorithm(),
            ConsensusMethod.DELPHI_METHOD: DelphiMethodAlgorithm(),
            ConsensusMethod.NOMINAL_GROUP: NominalGroupAlgorithm()
        }
    
    async def compute_consensus(
        self,
        inputs: List[ConsensusInput],
        method: ConsensusMethod,
        context: Dict[str, Any] = None
    ) -> ConsensusResult:
        """
        Compute consensus from multiple agent inputs
        
        Args:
            inputs: List of agent opinions/positions
            method: Consensus computation method
            context: Additional context for consensus computation
            
        Returns:
            Consensus computation result
        """
        algorithm = self.consensus_algorithms[method]
        
        start_time = datetime.now()
        result = await algorithm.compute(inputs, context)
        computation_time = (datetime.now() - start_time).total_seconds()
        
        return ConsensusResult(
            consensus_value=result["consensus_value"],
            confidence=result["confidence"],
            participants=[inp.agent_id for inp in inputs],
            consensus_method=method,
            reasoning_trace=result["reasoning_trace"],
            conflict_resolution=result.get("conflict_resolution"),
            metadata=result.get("metadata", {}),
            computation_time=computation_time
        )

# ============================================================================
# Consensus Algorithm Implementations
# ============================================================================

class ConsensusAlgorithm(ABC):
    """Base class for consensus algorithms"""
    
    @abstractmethod
    async def compute(
        self, 
        inputs: List[ConsensusInput], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute consensus from inputs"""
        pass

class SimpleMajorityAlgorithm(ConsensusAlgorithm):
    """Simple majority voting consensus"""
    
    async def compute(
        self, 
        inputs: List[ConsensusInput], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implementation for simple majority voting
        pass

class WeightedVotingAlgorithm(ConsensusAlgorithm):
    """Weighted voting based on expertise and confidence"""
    
    async def compute(
        self, 
        inputs: List[ConsensusInput], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implementation for weighted voting
        pass

class BayesianConsensusAlgorithm(ConsensusAlgorithm):
    """Bayesian consensus computation"""
    
    async def compute(
        self, 
        inputs: List[ConsensusInput], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implementation for Bayesian consensus
        pass

class CognitiveDiversityAlgorithm(ConsensusAlgorithm):
    """Cognitive diversity preserving consensus"""
    
    async def compute(
        self, 
        inputs: List[ConsensusInput], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implementation for cognitive diversity consensus
        pass

class DelphiMethodAlgorithm(ConsensusAlgorithm):
    """Delphi method consensus"""
    
    async def compute(
        self, 
        inputs: List[ConsensusInput], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implementation for Delphi method
        pass

class NominalGroupAlgorithm(ConsensusAlgorithm):
    """Nominal group technique consensus"""
    
    async def compute(
        self, 
        inputs: List[ConsensusInput], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implementation for nominal group technique
        pass

# ============================================================================
# Multi-Agent Communication System
# ============================================================================

class AgentCommunicationBus:
    """Handles communication between agents"""
    
    def __init__(self):
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.message_handlers: Dict[str, callable] = {}
        self.broadcast_subscriptions: Dict[str, Set[str]] = {}
    
    async def send_message(
        self,
        message: AgentMessage,
        session_id: Optional[str] = None
    ) -> None:
        """Send message from one agent to another"""
        if isinstance(message.receiver_id, str):
            # Direct message
            if message.receiver_id in self.message_queues:
                await self.message_queues[message.receiver_id].put(message)
        else:
            # Broadcast message
            for receiver_id in message.receiver_id:
                if receiver_id in self.message_queues:
                    await self.message_queues[receiver_id].put(message)
    
    async def register_agent(
        self,
        agent_id: str,
        message_handler: callable
    ) -> None:
        """Register an agent with the communication bus"""
        self.message_queues[agent_id] = asyncio.Queue()
        self.message_handlers[agent_id] = message_handler
    
    async def start_message_processing(self, agent_id: str) -> None:
        """Start processing messages for an agent"""
        while True:
            try:
                message = await self.message_queues[agent_id].get()
                await self.message_handlers[agent_id](message)
            except Exception as e:
                print(f"Error processing message for agent {agent_id}: {e}")

# ============================================================================
# Integration with Existing DAIP Services
# ============================================================================

class MultiAgentService:
    """Main service orchestrating multi-agent collaboration"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        self.agent_registry = AgentRegistry()
        self.intent_interpreter = IntentInterpreter()
        self.team_formation_engine = TeamFormationEngine(self.agent_registry)
        self.workflow_orchestrator = WorkflowOrchestrator()
        self.consensus_engine = ConsensusEngine()
        self.communication_bus = AgentCommunicationBus()
        
        # Initialize agents
        self._initialize_agents()
        
        # Integration with existing services
        self.memory_service = getattr(app_state, 'memory_service', None)
        self.role_manager = getattr(app_state, '_role_manager', None)
        self.synthesis_engine = getattr(app_state, '_synthesis_engine', None)
    
    def _initialize_agents(self):
        """Initialize core agents"""
        # Secretariat agents
        self.agent_registry.register_agent(AgentProfile(
            agent_id="secretariat_coordinator",
            name="Secretariat Coordinator",
            agent_type=AgentType.COORDINATOR,
            specializations=[AgentSpecialization.WORKFLOW_ORCHESTRATOR],
            expertise_domains=["meeting_management", "task_coordination"],
            communication_style="structured and efficient",
            personality_traits={"organized": 0.9, "efficient": 0.8},
            capabilities=["workflow_management", "task_assignment", "progress_tracking"]
        ))
        
        # Forum moderator
        self.agent_registry.register_agent(AgentProfile(
            agent_id="forum_moderator",
            name="Forum Moderator",
            agent_type=AgentType.MODERATOR,
            specializations=[AgentSpecialization.CONSENSUS_BUILDER, AgentSpecialization.CONFLICT_RESOLVER],
            expertise_domains=["debate_moderation", "consensus_building"],
            communication_style="balanced and inclusive",
            personality_traits={"diplomatic": 0.9, "analytical": 0.7},
            capabilities=["debate_moderation", "consensus_facilitation", "conflict_resolution"]
        ))
    
    async def handle_user_request(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Handle user request and initiate appropriate collaboration
        
        Args:
            user_input: User's request
            user_id: User identifier
            context: Additional context
            
        Returns:
            Collaboration session and initial response
        """
        try:
            # Interpret user intent
            intent_result = await self.intent_interpreter.interpret_intent(
                user_input, 
                context or {}
            )
            
            # Create collaboration session
            session = CollaborationSession(
                session_id=str(uuid.uuid4()),
                session_name=f"Session {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                collaboration_mode=intent_result.get("collaboration_mode", "general"),
                initiator_id=user_id,
                participants=[user_id],
                topic=user_input,
                objectives=intent_result.get("objectives", []),
                institutional_primitives=self._determine_primitives(intent_result),
                consensus_method=self._determine_consensus_method(intent_result)
            )
            
            # Form team
            team_agents = await self.team_formation_engine.form_team(
                task_requirements=intent_result,
                collaboration_mode=session.collaboration_mode
            )
            session.participants.extend(team_agents)
            
            # Execute workflow
            workflow_definition = self._create_workflow_definition(intent_result, session)
            results = await self.workflow_orchestrator.execute_workflow(
                workflow_definition,
                session
            )
            
            return {
                "session": session,
                "results": results,
                "team_agents": team_agents,
                "intent_analysis": intent_result
            }
        except Exception as e:
            # Return a simple response if something goes wrong
            return {
                "session": None,
                "results": {"error": str(e)},
                "team_agents": [],
                "intent_analysis": {"primary_intent": "general", "confidence": 0.5}
            }
    
    def _determine_primitives(self, intent_result: Dict[str, Any]) -> List[InstitutionalPrimitive]:
        """Determine required institutional primitives based on intent"""
        primitives = [
            InstitutionalPrimitive.INTERPRET_INTENT,
            InstitutionalPrimitive.FORM_TEAM,
            InstitutionalPrimitive.EXECUTE_WORKFLOW
        ]
        
        if intent_result["collaboration_mode"] == CollaborationMode.FORUM_DEBATE:
            primitives.extend([
                InstitutionalPrimitive.MULTI_AGENT_COLLABORATE,
                InstitutionalPrimitive.COMPUTE_CONSENSUS
            ])
        
        if intent_result.get("requires_report", False):
            primitives.append(InstitutionalPrimitive.GENERATE_REPORT)
        
        return primitives
    
    def _determine_consensus_method(self, intent_result: Dict[str, Any]) -> ConsensusMethod:
        """Determine appropriate consensus method"""
        if intent_result["collaboration_mode"] == CollaborationMode.FORUM_DEBATE:
            return ConsensusMethod.COGNITIVE_DIVERSITY
        else:
            return ConsensusMethod.SIMPLE_MAJORITY
    
    def _create_workflow_definition(
        self, 
        intent_result: Dict[str, Any], 
        session: CollaborationSession
    ) -> Dict[str, Any]:
        """Create workflow definition based on intent and session"""
        # Implementation would create appropriate workflow steps
        pass

class AgentRegistry:
    """Registry for managing agent profiles and capabilities"""
    
    def __init__(self):
        self.agents: Dict[str, AgentProfile] = {}
        self.capabilities: Dict[str, AgentCapability] = {}
    
    def register_agent(self, agent_profile: AgentProfile) -> None:
        """Register an agent profile"""
        self.agents[agent_profile.agent_id] = agent_profile
    
    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Get agent profile by ID"""
        return self.agents.get(agent_id)
    
    def find_agents_by_capability(self, capability: str) -> List[AgentProfile]:
        """Find agents with specific capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]
    
    def find_agents_by_specialization(
        self, 
        specialization: AgentSpecialization
    ) -> List[AgentProfile]:
        """Find agents with specific specialization"""
        return [
            agent for agent in self.agents.values()
            if specialization in agent.specializations
        ]

# ============================================================================
# WebSocket Integration for Real-time Updates
# ============================================================================

class CollaborationWebSocketManager:
    """Manages WebSocket connections for real-time collaboration updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[Any]] = {}  # session_id -> connections
        self.connection_managers: Dict[str, Any] = {}  # connection_id -> manager
    
    async def connect(
        self, 
        websocket: Any, 
        session_id: str, 
        user_id: str
    ) -> None:
        """Accept a new WebSocket connection"""
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        self.connection_managers[id(websocket)] = {
            "session_id": session_id,
            "user_id": user_id,
            "websocket": websocket
        }
    
    async def disconnect(self, websocket: Any) -> None:
        """Handle WebSocket disconnection"""
        if id(websocket) in self.connection_managers:
            session_id = self.connection_managers[id(websocket)]["session_id"]
            if session_id in self.active_connections:
                self.active_connections[session_id].discard(websocket)
            del self.connection_managers[id(websocket)]
    
    async def broadcast_to_session(
        self, 
        session_id: str, 
        message: Dict[str, Any]
    ) -> None:
        """Broadcast message to all connections in a session"""
        if session_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[session_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected:
                await self.disconnect(websocket)
    
    async def send_message_to_user(
        self, 
        session_id: str, 
        user_id: str, 
        message: Dict[str, Any]
    ) -> None:
        """Send message to specific user in session"""
        if session_id in self.active_connections:
            for websocket in self.active_connections[session_id]:
                connection_info = self.connection_managers.get(id(websocket))
                if connection_info and connection_info["user_id"] == user_id:
                    try:
                        await websocket.send_json(message)
                    except:
                        await self.disconnect(websocket)

# ============================================================================
# Performance Monitoring and Analytics
# ============================================================================

class CollaborationAnalytics:
    """Analytics and monitoring for collaboration sessions"""
    
    def __init__(self):
        self.session_metrics: Dict[str, Dict[str, Any]] = {}
        self.agent_performance: Dict[str, Dict[str, Any]] = {}
    
    def record_session_start(self, session: CollaborationSession) -> None:
        """Record session start metrics"""
        self.session_metrics[session.session_id] = {
            "start_time": session.created_at,
            "participants": len(session.participants),
            "collaboration_mode": session.collaboration_mode,
            "objectives": session.objectives,
            "events": []
        }
    
    def record_agent_contribution(
        self, 
        session_id: str, 
        agent_id: str, 
        contribution: Dict[str, Any]
    ) -> None:
        """Record agent contribution to session"""
        if session_id in self.session_metrics:
            self.session_metrics[session_id]["events"].append({
                "type": "agent_contribution",
                "agent_id": agent_id,
                "contribution": contribution,
                "timestamp": datetime.now()
            })
    
    def record_consensus_computation(
        self, 
        session_id: str, 
        consensus_result: ConsensusResult
    ) -> None:
        """Record consensus computation metrics"""
        if session_id in self.session_metrics:
            self.session_metrics[session_id]["events"].append({
                "type": "consensus_computation",
                "method": consensus_result.consensus_method,
                "confidence": consensus_result.confidence,
                "computation_time": consensus_result.computation_time,
                "participants": len(consensus_result.participants),
                "timestamp": datetime.now()
            })
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get session performance summary"""
        if session_id not in self.session_metrics:
            return {}
        
        metrics = self.session_metrics[session_id]
        duration = datetime.now() - metrics["start_time"]
        
        agent_contributions = [
            event for event in metrics["events"]
            if event["type"] == "agent_contribution"
        ]
        
        consensus_computations = [
            event for event in metrics["events"]
            if event["type"] == "consensus_computation"
        ]
        
        return {
            "session_id": session_id,
            "duration_seconds": duration.total_seconds(),
            "total_participants": metrics["participants"],
            "collaboration_mode": metrics["collaboration_mode"],
            "total_agent_contributions": len(agent_contributions),
            "total_consensus_computations": len(consensus_computations),
            "average_consensus_confidence": (
                sum(c["confidence"] for c in consensus_computations) / len(consensus_computations)
                if consensus_computations else 0
            ),
            "average_consensus_time": (
                sum(c["computation_time"] for c in consensus_computations) / len(consensus_computations)
                if consensus_computations else 0
            )
        }

# ============================================================================
# Example Usage and Integration Patterns
# ============================================================================

# Example integration with existing DAIP services
async def example_integration():
    """Example showing how to integrate with existing DAIP services"""
    
    # Initialize the multi-agent service
    from src.app_state import AppState
    app_state = AppState()
    multi_agent_service = MultiAgentService(app_state)
    
    # Handle a user request
    user_request = "I need to organize a debate about AI ethics with technical and business experts"
    user_id = "user_123"
    
    result = await multi_agent_service.handle_user_request(user_request, user_id)
    
    # The result contains:
    # - Collaboration session information
    # - Team formation results
    # - Initial workflow execution
    # - Intent analysis
    
    return result

# Example workflow definition
EXAMPLE_SECRETARIAT_WORKFLOW = {
    "workflow_id": "secretariat_meeting_preparation",
    "name": "Secretariat Meeting Preparation",
    "description": "Prepare and manage a meeting with secretariat automation",
    "steps": [
        {
            "step_id": "interpret_intent",
            "primitive_type": InstitutionalPrimitive.INTERPRET_INTENT,
            "assigned_agents": ["secretariat_coordinator"],
            "inputs": {"user_request": "Schedule a team meeting for next week"},
            "expected_outputs": ["meeting_objective", "required_participants"]
        },
        {
            "step_id": "form_team",
            "primitive_type": InstitutionalPrimitive.FORM_TEAM,
            "assigned_agents": ["secretariat_coordinator"],
            "inputs": {"task_type": "meeting_preparation"},
            "expected_outputs": ["team_members", "roles"]
        },
        {
            "step_id": "schedule_meeting",
            "primitive_type": InstitutionalPrimitive.EXECUTE_WORKFLOW,
            "assigned_agents": ["secretariat_scheduler"],
            "inputs": {"duration": 60, "participants": []},
            "expected_outputs": ["scheduled_time", "calendar_invites"]
        },
        {
            "step_id": "prepare_agenda",
            "primitive_type": InstitutionalPrimitive.EXECUTE_WORKFLOW,
            "assigned_agents": ["secretariat_note_taker"],
            "inputs": {"meeting_objective": "", "topics": []},
            "expected_outputs": ["meeting_agenda", "preparation_tasks"]
        }
    ]
}

EXAMPLE_FORUM_DEBATE_WORKFLOW = {
    "workflow_id": "forum_ethics_debate",
    "name": "AI Ethics Forum Debate",
    "description": "Conduct a structured debate on AI ethics",
    "steps": [
        {
            "step_id": "interpret_topic",
            "primitive_type": InstitutionalPrimitive.INTERPRET_INTENT,
            "assigned_agents": ["forum_moderator"],
            "inputs": {"debate_topic": "AI ethics in autonomous vehicles"},
            "expected_outputs": ["debate_scope", "key_questions"]
        },
        {
            "step_id": "form_expert_panel",
            "primitive_type": InstitutionalPrimitive.FORM_TEAM,
            "assigned_agents": ["forum_moderator"],
            "inputs": {"required_expertise": ["technical", "ethical", "business"]},
            "expected_outputs": ["expert_panel", "moderator"]
        },
        {
            "step_id": "opening_statements",
            "primitive_type": InstitutionalPrimitive.MULTI_AGENT_COLLABORATE,
            "assigned_agents": ["technical_expert", "ethics_expert", "business_expert"],
            "inputs": {"debate_topic": "", "time_limit": 300},
            "expected_outputs": ["opening_statements", "initial_positions"]
        },
        {
            "step_id": "structured_debate",
            "primitive_type": InstitutionalPrimitive.MULTI_AGENT_COLLABORATE,
            "assigned_agents": ["forum_moderator", "technical_expert", "ethics_expert", "business_expert"],
            "inputs": {"debate_structure": "pro_con", "rounds": 3},
            "expected_outputs": ["debate_transcript", "key_arguments"]
        },
        {
            "step_id": "consensus_building",
            "primitive_type": InstitutionalPrimitive.COMPUTE_CONSENSUS,
            "assigned_agents": ["forum_moderator"],
            "inputs": {"debate_positions": [], "consensus_method": "cognitive_diversity"},
            "expected_outputs": ["consensus_result", "remaining_disagreements"]
        },
        {
            "step_id": "generate_report",
            "primitive_type": InstitutionalPrimitive.GENERATE_REPORT,
            "assigned_agents": ["forum_synthesizer"],
            "inputs": {"debate_transcript": "", "consensus_result": ""},
            "expected_outputs": ["debate_report", "key_findings", "recommendations"]
        }
    ]
}

if __name__ == "__main__":
    # Example usage
    print("Multi-Agent Collaboration System Specifications")
    print("==============================================")
    print("This file contains the technical specifications for")
    print("implementing the multi-agent collaboration system.")
    print("\nKey Components:")
    print("- Agent profiles and capabilities")
    print("- Intent interpretation and workflow orchestration")
    print("- Team formation and consensus computation")
    print("- Real-time communication and WebSocket integration")
    print("- Performance monitoring and analytics")
    print("- Integration with existing DAIP services")