"""Institutional Primitives Implementation for Multi-Agent Collaboration

Implements the core institutional primitives that orchestrate multi-agent workflows.
Each primitive represents a fundamental operation in the collaboration system.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

# Import from multi-agent collaboration system
try:
    from .multi_agent_collaboration_system import (
        AgentMessage,
        AgentProfile,
        CollaborationSession,
        CollaborativeTask,
        ConsensusInput,
        ConsensusResult,
        InstitutionalPrimitive,
        WorkflowStep,
    )
except ImportError:
    # Define basic types if multi-agent system not available
    class InstitutionalPrimitive(str, Enum):
        INTERPRET_INTENT = "interpret_intent"
        FORM_TEAM = "form_team"
        EXECUTE_WORKFLOW = "execute_workflow"
        MULTI_AGENT_COLLABORATE = "multi_agent_collaborate"
        COMPUTE_CONSENSUS = "compute_consensus"
        GENERATE_REPORT = "generate_report"
        USER_INTERVENE = "user_intervene"
        DYNAMIC_WORKFLOW_ADJUST = "dynamic_workflow_adjust"
        MONITOR_PROCESS = "monitor_process"
    
    @dataclass
    class AgentMessage:
        message_id: str
        sender_id: str
        receiver_id: Union[str, list[str]]
        message_type: str
        content: Any
        context: dict[str, Any] = field(default_factory=dict)
        priority: int = 1
        requires_response: bool = False
        response_to: Optional[str] = None
        timestamp: datetime = field(default_factory=datetime.now)
        session_id: Optional[str] = None
    
    @dataclass
    class ConsensusInput:
        agent_id: str
        position: Union[str, float, dict[str, Any]]
        confidence: float
        reasoning: str
        evidence: list[str] = field(default_factory=list)
        weight: float = 1.0
        timestamp: datetime = field(default_factory=datetime.now)
    
    @dataclass
    class ConsensusResult:
        consensus_value: Any
        confidence: float
        participants: list[str]
        consensus_method: str
        reasoning_trace: list[str]
        conflict_resolution: Optional[str] = None
        metadata: dict[str, Any] = field(default_factory=dict)
        computation_time: float = 0.0

logger = logging.getLogger(__name__)

@dataclass
class PrimitiveContext:
    """Context for institutional primitive execution"""
    primitive_id: str
    primitive_type: InstitutionalPrimitive
    session_id: str
    execution_id: str
    inputs: dict[str, Any]
    assigned_agents: list[str]
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "pending"
    results: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class PrimitiveResult:
    """Result of institutional primitive execution"""
    success: bool
    outputs: dict[str, Any]
    execution_time: float
    messages_generated: list[AgentMessage] = field(default_factory=list)
    next_primitives: list[InstitutionalPrimitive] = field(default_factory=list)
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

class InstitutionalPrimitiveBase(ABC):
    """Base class for all institutional primitives"""
    
    def __init__(self, primitive_type: InstitutionalPrimitive):
        self.primitive_type = primitive_type
        self.logger = logging.getLogger(f"{__name__}.{primitive_type.value}")
    
    @abstractmethod
    async def execute(
        self,
        context: PrimitiveContext,
        services: dict[str, Any]
    ) -> PrimitiveResult:
        """Execute the institutional primitive"""
        pass
    
    @abstractmethod
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate primitive inputs"""
        pass
    
    @abstractmethod
    def get_required_capabilities(self) -> list[str]:
        """Get required agent capabilities for this primitive"""
        pass

class InterpretIntentPrimitive(InstitutionalPrimitiveBase):
    """Interprets user intent and determines collaboration requirements"""
    
    def __init__(self):
        super().__init__(InstitutionalPrimitive.INTERPRET_INTENT)
        self.intent_patterns = {
            "secretariat_automation": {
                "keywords": ["schedule", "meeting", "task", "follow up", "notes", "agenda", "minutes"],
                "weight": 0.8
            },
            "forum_debate": {
                "keywords": ["debate", "discuss", "analyze", "evaluate", "perspectives", "opinion", "argument"],
                "weight": 0.8
            },
            "expert_consultation": {
                "keywords": ["expert", "advice", "recommendation", "specialist", "consult", "guidance"],
                "weight": 0.7
            },
            "research_analysis": {
                "keywords": ["research", "analyze", "investigate", "study", "examine", "report"],
                "weight": 0.6
            }
        }
    
    async def execute(
        self,
        context: PrimitiveContext,
        services: dict[str, Any]
    ) -> PrimitiveResult:
        """Execute intent interpretation"""
        start_time = datetime.now()
        
        try:
            # Get input
            user_input = context.inputs.get("user_input", "")
            context_data = context.inputs.get("context", {})
            
            # Analyze intent
            intent_analysis = await self._analyze_intent(user_input, context_data, services)
            
            # Determine collaboration mode and requirements
            collaboration_requirements = await self._determine_requirements(intent_analysis, services)
            
            # Generate clarifying questions if needed
            clarifying_questions = await self._generate_questions(intent_analysis, services)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PrimitiveResult(
                success=True,
                outputs={
                    "intent_analysis": intent_analysis,
                    "collaboration_requirements": collaboration_requirements,
                    "clarifying_questions": clarifying_questions,
                    "confidence": intent_analysis.get("confidence", 0.0)
                },
                execution_time=execution_time,
                metadata={
                    "input_length": len(user_input),
                    "intent_categories": list(intent_analysis.get("categories", {}).keys()),
                    "complexity_score": intent_analysis.get("complexity_score", 0.0)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in InterpretIntentPrimitive: {e}")
            return PrimitiveResult(
                success=False,
                outputs={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs for intent interpretation"""
        return "user_input" in inputs and isinstance(inputs["user_input"], str)
    
    def get_required_capabilities(self) -> list[str]:
        """Get required capabilities"""
        return ["intent_analysis", "nlp_processing", "pattern_recognition"]
    
    async def _analyze_intent(
        self, 
        user_input: str, 
        context: dict[str, Any],
        services: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze user intent using NLP and pattern matching"""
        # Use existing intent analysis service if available
        if "intent_analysis_service" in services:
            intent_service = services["intent_analysis_service"]
            return await intent_service.analyze_intent(user_input, context)
        
        # Fallback to simple pattern matching
        input_lower = user_input.lower()
        categories = {}
        max_score = 0.0
        
        for category, config in self.intent_patterns.items():
            score = 0.0
            for keyword in config["keywords"]:
                if keyword in input_lower:
                    score += config["weight"] / len(config["keywords"])
            
            if score > 0:
                categories[category] = score
                max_score = max(max_score, score)
        
        # Determine complexity
        complexity_score = min(len(user_input.split()) / 50.0, 1.0)
        
        return {
            "primary_intent": max(categories.items(), key=lambda x: x[1])[0] if categories else "general",
            "categories": categories,
            "confidence": max_score,
            "complexity_score": complexity_score,
            "entities": self._extract_entities(user_input),
            "sentiment": self._analyze_sentiment(user_input)
        }
    
    def _extract_entities(self, text: str) -> list[dict[str, Any]]:
        """Extract entities from text (simplified)"""
        entities = []
        
        # Simple entity extraction patterns
        if "meeting" in text.lower():
            entities.append({"type": "event", "value": "meeting", "confidence": 0.8})
        
        if "AI" in text or "artificial intelligence" in text.lower():
            entities.append({"type": "topic", "value": "AI", "confidence": 0.9})
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ["good", "great", "excellent", "helpful", "effective"]
        negative_words = ["bad", "poor", "terrible", "difficult", "problem"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _determine_requirements(
        self, 
        intent_analysis: dict[str, Any],
        services: dict[str, Any]
    ) -> dict[str, Any]:
        """Determine collaboration requirements based on intent"""
        primary_intent = intent_analysis.get("primary_intent", "general")
        complexity = intent_analysis.get("complexity_score", 0.0)
        
        requirements = {
            "collaboration_mode": primary_intent,
            "required_agents": [],
            "estimated_duration": 300.0,  # 5 minutes default
            "required_primitives": [
                InstitutionalPrimitive.FORM_TEAM,
                InstitutionalPrimitive.EXECUTE_WORKFLOW
            ]
        }
        
        # Add intent-specific requirements
        if primary_intent == "forum_debate":
            requirements["required_agents"] = ["moderator", "technical_expert", "business_expert"]
            requirements["required_primitives"].extend([
                InstitutionalPrimitive.MULTI_AGENT_COLLABORATE,
                InstitutionalPrimitive.COMPUTE_CONSENSUS
            ])
        elif primary_intent == "secretariat_automation":
            requirements["required_agents"] = ["secretariat_coordinator", "scheduler"]
            requirements["estimated_duration"] = 600.0  # 10 minutes
        
        # Adjust for complexity
        if complexity > 0.7:
            requirements["required_primitives"].append(InstitutionalPrimitive.GENERATE_REPORT)
            requirements["estimated_duration"] *= 1.5
        
        return requirements
    
    async def _generate_questions(
        self, 
        intent_analysis: dict[str, Any],
        services: dict[str, Any]
    ) -> list[str]:
        """Generate clarifying questions for ambiguous intents"""
        confidence = intent_analysis.get("confidence", 0.0)
        questions = []
        
        if confidence < 0.6:
            questions.append("Could you please provide more details about what you'd like to accomplish?")
        
        if intent_analysis.get("complexity_score", 0.0) > 0.8:
            questions.append("What are the specific objectives or constraints for this task?")
        
        return questions

class FormTeamPrimitive(InstitutionalPrimitiveBase):
    """Forms optimal teams based on task requirements"""
    
    def __init__(self):
        super().__init__(InstitutionalPrimitive.FORM_TEAM)
    
    async def execute(
        self,
        context: PrimitiveContext,
        services: dict[str, Any]
    ) -> PrimitiveResult:
        """Execute team formation"""
        start_time = datetime.now()
        
        try:
            # Get requirements
            task_requirements = context.inputs.get("task_requirements", {})
            collaboration_mode = context.inputs.get("collaboration_mode", "general")
            constraints = context.inputs.get("constraints", {})
            
            # Form team
            team_formation = await self._form_team(
                task_requirements, 
                collaboration_mode, 
                constraints, 
                services
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PrimitiveResult(
                success=True,
                outputs={
                    "team_members": team_formation["members"],
                    "team_roles": team_formation["roles"],
                    "formation_strategy": team_formation["strategy"],
                    "confidence_score": team_formation["confidence_score"],
                    "alternative_teams": team_formation.get("alternative_teams", [])
                },
                execution_time=execution_time,
                metadata={
                    "requirements_complexity": task_requirements.get("complexity_score", 0.0),
                    "formation_time": execution_time,
                    "team_size": len(team_formation["members"])
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in FormTeamPrimitive: {e}")
            return PrimitiveResult(
                success=False,
                outputs={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs for team formation"""
        return "task_requirements" in inputs and "collaboration_mode" in inputs
    
    def get_required_capabilities(self) -> list[str]:
        """Get required capabilities"""
        return ["team_formation", "expertise_matching", "optimization"]
    
    async def _form_team(
        self,
        task_requirements: dict[str, Any],
        collaboration_mode: str,
        constraints: dict[str, Any],
        services: dict[str, Any]
    ) -> dict[str, Any]:
        """Form optimal team based on requirements"""
        # Use existing team formation service if available
        if "team_formation_engine" in services:
            engine = services["team_formation_engine"]
            return await engine.form_team(task_requirements, collaboration_mode, constraints)
        
        # Fallback to simple team formation
        agent_registry = services.get("agent_registry", {})
        
        # Determine required specializations
        required_specializations = self._determine_specializations(task_requirements, collaboration_mode)
        
        # Find matching agents
        team_members = []
        team_roles = {}
        
        for specialization in required_specializations:
            matching_agents = self._find_agents_by_specialization(
                specialization, agent_registry, constraints
            )
            
            if matching_agents:
                # Select best agent based on availability and performance
                selected_agent = self._select_best_agent(matching_agents, constraints)
                team_members.append(selected_agent)
                team_roles[selected_agent] = specialization
        
        return {
            "members": team_members,
            "roles": team_roles,
            "strategy": "expertise_matching",
            "confidence_score": len(team_members) / len(required_specializations) if required_specializations else 1.0,
            "alternative_teams": []  # Would generate alternatives in full implementation
        }
    
    def _determine_specializations(
        self, 
        task_requirements: dict[str, Any], 
        collaboration_mode: str
    ) -> list[str]:
        """Determine required specializations"""
        specializations = []
        
        if collaboration_mode == "forum_debate":
            specializations.extend(["moderator", "technical_expert", "business_expert"])
        elif collaboration_mode == "secretariat_automation":
            specializations.extend(["coordinator", "scheduler", "note_taker"])
        
        # Add task-specific specializations
        required_expertise = task_requirements.get("required_expertise", [])
        specializations.extend(required_expertise)
        
        return list(set(specializations))  # Remove duplicates
    
    def _find_agents_by_specialization(
        self, 
        specialization: str, 
        agent_registry: dict[str, Any],
        constraints: dict[str, Any]
    ) -> list[str]:
        """Find agents with specific specialization"""
        # Simplified implementation
        # In real implementation, would query agent registry
        return []
    
    def _select_best_agent(
        self, 
        candidate_agents: list[str], 
        constraints: dict[str, Any]
    ) -> str:
        """Select best agent from candidates"""
        # Simplified implementation
        # In real implementation, would use performance metrics and availability
        return candidate_agents[0] if candidate_agents else None

class ExecuteWorkflowPrimitive(InstitutionalPrimitiveBase):
    """Executes predefined workflows"""
    
    def __init__(self):
        super().__init__(InstitutionalPrimitive.EXECUTE_WORKFLOW)
        self.workflow_templates = self._load_workflow_templates()
    
    async def execute(
        self,
        context: PrimitiveContext,
        services: dict[str, Any]
    ) -> PrimitiveResult:
        """Execute workflow"""
        start_time = datetime.now()
        
        try:
            # Get workflow definition
            workflow_definition = context.inputs.get("workflow_definition", {})
            workflow_parameters = context.inputs.get("parameters", {})
            
            # Execute workflow
            workflow_result = await self._execute_workflow(
                workflow_definition, 
                workflow_parameters, 
                services
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PrimitiveResult(
                success=True,
                outputs={
                    "workflow_results": workflow_result["results"],
                    "execution_status": workflow_result["status"],
                    "completed_steps": workflow_result["completed_steps"],
                    "failed_steps": workflow_result.get("failed_steps", []),
                    "total_execution_time": workflow_result["total_time"]
                },
                execution_time=execution_time,
                metadata={
                    "workflow_type": workflow_definition.get("workflow_type", "unknown"),
                    "total_steps": len(workflow_definition.get("steps", [])),
                    "success_rate": len(workflow_result["completed_steps"]) / len(workflow_definition.get("steps", [])) if workflow_definition.get("steps") else 1.0
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in ExecuteWorkflowPrimitive: {e}")
            return PrimitiveResult(
                success=False,
                outputs={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs for workflow execution"""
        return "workflow_definition" in inputs and isinstance(inputs["workflow_definition"], dict)
    
    def get_required_capabilities(self) -> list[str]:
        """Get required capabilities"""
        return ["workflow_execution", "task_management", "process_orchestration"]
    
    async def _execute_workflow(
        self,
        workflow_definition: dict[str, Any],
        parameters: dict[str, Any],
        services: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute workflow steps"""
        # Use existing workflow orchestrator if available
        if "workflow_orchestrator" in services:
            orchestrator = services["workflow_orchestrator"]
            return await orchestrator.execute_workflow(workflow_definition, parameters)
        
        # Fallback to simple workflow execution
        steps = workflow_definition.get("steps", [])
        completed_steps = []
        failed_steps = []
        results = {}
        
        for step in steps:
            try:
                # Execute step
                step_result = await self._execute_step(step, parameters, services)
                
                completed_steps.append(step["step_id"])
                results[step["step_id"]] = step_result
                
            except Exception as e:
                failed_steps.append(step["step_id"])
                self.logger.error(f"Error executing step {step['step_id']}: {e}")
        
        return {
            "results": results,
            "status": "completed" if not failed_steps else "partial",
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "total_time": (datetime.now() - datetime.now()).total_seconds()  # Placeholder
        }
    
    async def _execute_step(
        self,
        step: dict[str, Any],
        parameters: dict[str, Any],
        services: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a single workflow step"""
        # Simplified step execution
        # In real implementation, would delegate to appropriate primitive
        step_type = step.get("type")
        
        if step_type == "task":
            return {"status": "completed", "result": "Task executed"}
        elif step_type == "decision":
            return {"status": "completed", "result": "Decision made"}
        else:
            return {"status": "completed", "result": "Step executed"}
    
    def _load_workflow_templates(self) -> dict[str, Any]:
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

class MultiAgentCollaboratePrimitive(InstitutionalPrimitiveBase):
    """Facilitates collaboration between multiple agents"""
    
    def __init__(self):
        super().__init__(InstitutionalPrimitive.MULTI_AGENT_COLLABORATE)
    
    async def execute(
        self,
        context: PrimitiveContext,
        services: dict[str, Any]
    ) -> PrimitiveResult:
        """Execute multi-agent collaboration"""
        start_time = datetime.now()
        
        try:
            # Get collaboration parameters
            participants = context.inputs.get("participants", [])
            collaboration_type = context.inputs.get("collaboration_type", "discussion")
            topic = context.inputs.get("topic", "")
            rules = context.inputs.get("rules", {})
            
            # Facilitate collaboration
            collaboration_result = await self._facilitate_collaboration(
                participants, 
                collaboration_type, 
                topic, 
                rules, 
                services
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PrimitiveResult(
                success=True,
                outputs={
                    "collaboration_transcript": collaboration_result["transcript"],
                    "key_insights": collaboration_result["key_insights"],
                    "agreements": collaboration_result["agreements"],
                    "disagreements": collaboration_result["disagreements"],
                    "participation_metrics": collaboration_result["participation_metrics"]
                },
                execution_time=execution_time,
                messages_generated=collaboration_result.get("messages", []),
                metadata={
                    "collaboration_type": collaboration_type,
                    "participant_count": len(participants),
                    "interaction_count": len(collaboration_result.get("transcript", []))
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in MultiAgentCollaboratePrimitive: {e}")
            return PrimitiveResult(
                success=False,
                outputs={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs for multi-agent collaboration"""
        return "participants" in inputs and "collaboration_type" in inputs and "topic" in inputs
    
    def get_required_capabilities(self) -> list[str]:
        """Get required capabilities"""
        return ["collaboration_facilitation", "communication_management", "conflict_resolution"]
    
    async def _facilitate_collaboration(
        self,
        participants: list[str],
        collaboration_type: str,
        topic: str,
        rules: dict[str, Any],
        services: dict[str, Any]
    ) -> dict[str, Any]:
        """Facilitate collaboration between agents"""
        # Get communication bus
        communication_bus = services.get("communication_bus")
        
        # Simulate collaboration process
        transcript = []
        messages = []
        
        # Opening statements
        for participant in participants:
            opening_message = AgentMessage(
                message_id=str(uuid.uuid4()),
                sender_id=participant,
                receiver_id=participants,  # Broadcast to all
                message_type="opening_statement",
                content=f"As {participant}, I believe {topic} requires careful consideration from multiple perspectives.",
                session_id=context.session_id if 'context' in locals() else None
            )
            messages.append(opening_message)
            transcript.append({
                "speaker": participant,
                "message": opening_message.content,
                "timestamp": datetime.now().isoformat(),
                "type": "opening_statement"
            })
        
        # Structured discussion
        if collaboration_type == "debate":
            debate_rounds = rules.get("rounds", 3)
            for round_num in range(debate_rounds):
                for participant in participants:
                    debate_message = AgentMessage(
                        message_id=str(uuid.uuid4()),
                        sender_id=participant,
                        receiver_id=participants,
                        message_type="debate_contribution",
                        content=f"In round {round_num + 1}, I'd like to add that {topic} presents both opportunities and challenges that we must address.",
                        session_id=context.session_id if 'context' in locals() else None
                    )
                    messages.append(debate_message)
                    transcript.append({
                        "speaker": participant,
                        "message": debate_message.content,
                        "timestamp": datetime.now().isoformat(),
                        "type": "debate_contribution",
                        "round": round_num + 1
                    })
        
        # Analyze collaboration results
        key_insights = self._extract_key_insights(transcript)
        agreements = self._identify_agreements(transcript)
        disagreements = self._identify_disagreements(transcript)
        participation_metrics = self._calculate_participation_metrics(transcript, participants)
        
        return {
            "transcript": transcript,
            "key_insights": key_insights,
            "agreements": agreements,
            "disagreements": disagreements,
            "participation_metrics": participation_metrics,
            "messages": messages
        }
    
    def _extract_key_insights(self, transcript: list[dict[str, Any]]) -> list[str]:
        """Extract key insights from collaboration transcript"""
        # Simplified insight extraction
        insights = []
        
        # Look for common themes
        common_words = {}
        for entry in transcript:
            words = entry["message"].lower().split()
            for word in words:
                if len(word) > 4:  # Focus on meaningful words
                    common_words[word] = common_words.get(word, 0) + 1
        
        # Extract most common themes
        sorted_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)
        for word, count in sorted_words[:5]:
            insights.append(f"Theme '{word}' appeared frequently in discussion")
        
        return insights
    
    def _identify_agreements(self, transcript: list[dict[str, Any]]) -> list[str]:
        """Identify points of agreement"""
        agreements = []
        
        # Look for agreement indicators
        agreement_keywords = ["agree", "support", "confirm", "endorse", "yes"]
        
        for entry in transcript:
            message_lower = entry["message"].lower()
            if any(keyword in message_lower for keyword in agreement_keywords):
                agreements.append(f"{entry['speaker']} expressed agreement")
        
        return agreements
    
    def _identify_disagreements(self, transcript: list[dict[str, Any]]) -> list[str]:
        """Identify points of disagreement"""
        disagreements = []
        
        # Look for disagreement indicators
        disagreement_keywords = ["disagree", "oppose", "however", "but", "alternative"]
        
        for entry in transcript:
            message_lower = entry["message"].lower()
            if any(keyword in message_lower for keyword in disagreement_keywords):
                disagreements.append(f"{entry['speaker']} raised concerns")
        
        return disagreements
    
    def _calculate_participation_metrics(
        self, 
        transcript: list[dict[str, Any]], 
        participants: list[str]
    ) -> dict[str, Any]:
        """Calculate participation metrics"""
        participant_contributions = {p: 0 for p in participants}
        
        for entry in transcript:
            speaker = entry["speaker"]
            if speaker in participant_contributions:
                participant_contributions[speaker] += 1
        
        total_contributions = sum(participant_contributions.values())
        
        return {
            "total_contributions": total_contributions,
            "participant_contributions": participant_contributions,
            "average_contributions": total_contributions / len(participants) if participants else 0,
            "participation_balance": max(participant_contributions.values()) - min(participant_contributions.values()) if participants else 0
        }

class ComputeConsensusPrimitive(InstitutionalPrimitiveBase):
    """Computes consensus from multiple agent inputs"""
    
    def __init__(self):
        super().__init__(InstitutionalPrimitive.COMPUTE_CONSENSUS)
    
    async def execute(
        self,
        context: PrimitiveContext,
        services: dict[str, Any]
    ) -> PrimitiveResult:
        """Execute consensus computation"""
        start_time = datetime.now()
        
        try:
            # Get consensus inputs
            agent_inputs = context.inputs.get("agent_inputs", [])
            consensus_method = context.inputs.get("consensus_method", "simple_majority")
            consensus_config = context.inputs.get("config", {})
            
            # Compute consensus
            consensus_result = await self._compute_consensus(
                agent_inputs, 
                consensus_method, 
                consensus_config, 
                services
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PrimitiveResult(
                success=True,
                outputs={
                    "consensus_value": consensus_result.consensus_value,
                    "consensus_confidence": consensus_result.confidence,
                    "participants": consensus_result.participants,
                    "reasoning_trace": consensus_result.reasoning_trace,
                    "conflict_resolution": consensus_result.conflict_resolution
                },
                execution_time=execution_time,
                metadata={
                    "consensus_method": consensus_method,
                    "input_count": len(agent_inputs),
                    "computation_time": consensus_result.computation_time
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in ComputeConsensusPrimitive: {e}")
            return PrimitiveResult(
                success=False,
                outputs={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs for consensus computation"""
        return "agent_inputs" in inputs and isinstance(inputs["agent_inputs"], list)
    
    def get_required_capabilities(self) -> list[str]:
        """Get required capabilities"""
        return ["consensus_computation", "opinion_synthesis", "conflict_resolution"]
    
    async def _compute_consensus(
        self,
        agent_inputs: list[dict[str, Any]],
        consensus_method: str,
        config: dict[str, Any],
        services: dict[str, Any]
    ) -> ConsensusResult:
        """Compute consensus from agent inputs"""
        # Convert inputs to ConsensusInput objects
        consensus_inputs = []
        for input_data in agent_inputs:
            consensus_input = ConsensusInput(
                agent_id=input_data["agent_id"],
                position=input_data["position"],
                confidence=input_data.get("confidence", 0.5),
                reasoning=input_data.get("reasoning", ""),
                evidence=input_data.get("evidence", []),
                weight=input_data.get("weight", 1.0)
            )
            consensus_inputs.append(consensus_input)
        
        # Use consensus engine if available
        if "consensus_engine" in services:
            engine = services["consensus_engine"]
            return await engine.compute_consensus(consensus_inputs, consensus_method, config)
        
        # Fallback to simple consensus computation
        return await self._simple_consensus_computation(consensus_inputs, consensus_method)
    
    async def _simple_consensus_computation(
        self,
        inputs: list[ConsensusInput],
        method: str
    ) -> ConsensusResult:
        """Simple consensus computation fallback"""
        start_time = datetime.now()
        
        if method == "simple_majority":
            # Count positions
            position_counts = {}
            for input_item in inputs:
                position = str(input_item.position)
                position_counts[position] = position_counts.get(position, 0) + 1
            
            # Find majority position
            majority_position = max(position_counts.items(), key=lambda x: x[1])
            consensus_value = majority_position[0]
            confidence = majority_position[1] / len(inputs)
            
        else:
            # Default to averaging for numeric positions
            numeric_positions = []
            for input_item in inputs:
                if isinstance(input_item.position, (int, float)):
                    numeric_positions.append(input_item.position)
            
            if numeric_positions:
                consensus_value = sum(numeric_positions) / len(numeric_positions)
                confidence = len(numeric_positions) / len(inputs)
            else:
                consensus_value = "No clear consensus"
                confidence = 0.0
        
        computation_time = (datetime.now() - start_time).total_seconds()
        
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=confidence,
            participants=[inp.agent_id for inp in inputs],
            consensus_method=method,
            reasoning_trace=["Simple consensus computation"],
            computation_time=computation_time
        )

class GenerateReportPrimitive(InstitutionalPrimitiveBase):
    """Generates comprehensive reports from collaboration results"""
    
    def __init__(self):
        super().__init__(InstitutionalPrimitive.GENERATE_REPORT)
    
    async def execute(
        self,
        context: PrimitiveContext,
        services: dict[str, Any]
    ) -> PrimitiveResult:
        """Execute report generation"""
        start_time = datetime.now()
        
        try:
            # Get report parameters
            collaboration_data = context.inputs.get("collaboration_data", {})
            report_type = context.inputs.get("report_type", "summary")
            template = context.inputs.get("template", "standard")
            
            # Generate report
            report_result = await self._generate_report(
                collaboration_data, 
                report_type, 
                template, 
                services
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PrimitiveResult(
                success=True,
                outputs={
                    "report_content": report_result["content"],
                    "report_metadata": report_result["metadata"],
                    "key_findings": report_result["key_findings"],
                    "recommendations": report_result["recommendations"],
                    "attachments": report_result.get("attachments", [])
                },
                execution_time=execution_time,
                metadata={
                    "report_type": report_type,
                    "template": template,
                    "content_length": len(report_result["content"]),
                    "generation_time": execution_time
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in GenerateReportPrimitive: {e}")
            return PrimitiveResult(
                success=False,
                outputs={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs for report generation"""
        return "collaboration_data" in inputs and "report_type" in inputs
    
    def get_required_capabilities(self) -> list[str]:
        """Get required capabilities"""
        return ["report_generation", "content_synthesis", "document_creation"]
    
    async def _generate_report(
        self,
        collaboration_data: dict[str, Any],
        report_type: str,
        template: str,
        services: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate comprehensive report"""
        # Extract key information from collaboration data
        session_info = collaboration_data.get("session", {})
        transcript = collaboration_data.get("transcript", [])
        consensus_results = collaboration_data.get("consensus_results", {})
        participant_metrics = collaboration_data.get("participation_metrics", {})
        
        # Generate report content
        report_content = self._generate_report_content(
            session_info, transcript, consensus_results, participant_metrics, report_type
        )
        
        # Extract key findings
        key_findings = self._extract_key_findings(transcript, consensus_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            session_info, consensus_results, key_findings
        )
        
        return {
            "content": report_content,
            "metadata": {
                "report_type": report_type,
                "template": template,
                "generated_at": datetime.now().isoformat(),
                "session_id": session_info.get("session_id", ""),
                "participant_count": len(session_info.get("participants", []))
            },
            "key_findings": key_findings,
            "recommendations": recommendations,
            "attachments": []  # Would include charts, graphs, etc.
        }
    
    def _generate_report_content(
        self,
        session_info: dict[str, Any],
        transcript: list[dict[str, Any]],
        consensus_results: dict[str, Any],
        participant_metrics: dict[str, Any],
        report_type: str
    ) -> str:
        """Generate the main report content"""
        session_title = session_info.get("session_name", "Collaboration Session")
        session_date = session_info.get("created_at", datetime.now().isoformat())
        
        content = f"""# {session_title} Report

**Generated:** {session_date}
**Report Type:** {report_type.title()}

## Executive Summary

This report summarizes the collaborative session that took place on {session_date}. 
The session involved {len(session_info.get('participants', []))} participants 
focusing on the topic: "{session_info.get('topic', 'General discussion')}".

## Session Overview

**Session ID:** {session_info.get('session_id', 'Unknown')}
**Collaboration Mode:** {session_info.get('collaboration_mode', 'Unknown')}
**Duration:** {session_info.get('duration', 'Unknown')}
**Participants:** {', '.join(session_info.get('participants', []))}

## Key Discussion Points

"""
        
        # Add transcript summary
        if transcript:
            content += "### Discussion Summary\n\n"
            for i, entry in enumerate(transcript[:10]):  # Limit to first 10 entries
                content += f"**{entry['speaker']}:** {entry['message'][:200]}...\n\n"
        
        # Add consensus results
        if consensus_results:
            content += "### Consensus Results\n\n"
            content += f"**Consensus Value:** {consensus_results.get('consensus_value', 'Not reached')}\n"
            content += f"**Confidence Level:** {consensus_results.get('confidence', 0):.2f}\n"
            content += f"**Consensus Method:** {consensus_results.get('consensus_method', 'Unknown')}\n\n"
        
        # Add participation metrics
        if participant_metrics:
            content += "### Participation Metrics\n\n"
            content += f"**Total Contributions:** {participant_metrics.get('total_contributions', 0)}\n"
            content += f"**Average Contributions per Participant:** {participant_metrics.get('average_contributions', 0):.1f}\n"
        
        return content
    
    def _extract_key_findings(
        self,
        transcript: list[dict[str, Any]],
        consensus_results: dict[str, Any]
    ) -> list[str]:
        """Extract key findings from collaboration data"""
        findings = []
        
        # Add consensus-based findings
        if consensus_results:
            confidence = consensus_results.get("confidence", 0)
            if confidence > 0.8:
                findings.append(f"Strong consensus achieved ({confidence:.1%} confidence)")
            elif confidence > 0.6:
                findings.append(f"Moderate consensus achieved ({confidence:.1%} confidence)")
            else:
                findings.append(f"Limited consensus ({confidence:.1%} confidence) - further discussion needed")
        
        # Add transcript-based findings
        if transcript:
            participant_count = len(set(entry["speaker"] for entry in transcript))
            findings.append(f"Active participation from {participant_count} different contributors")
        
        return findings
    
    def _generate_recommendations(
        self,
        session_info: dict[str, Any],
        consensus_results: dict[str, Any],
        key_findings: list[str]
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Generate recommendations based on consensus confidence
        confidence = consensus_results.get("confidence", 0)
        if confidence < 0.6:
            recommendations.append("Schedule follow-up session to address remaining disagreements")
        
        # Generate recommendations based on participation
        if session_info.get("collaboration_mode") == "forum_debate":
            recommendations.append("Consider expanding expert panel for more diverse perspectives")
        
        # Generate general recommendations
        recommendations.append("Document action items and assign responsibilities")
        recommendations.append("Schedule regular review sessions to track progress")
        
        return recommendations

class InstitutionalPrimitiveFactory:
    """Factory for creating institutional primitive instances"""
    
    def __init__(self):
        self.primitives = {
            InstitutionalPrimitive.INTERPRET_INTENT: InterpretIntentPrimitive(),
            InstitutionalPrimitive.FORM_TEAM: FormTeamPrimitive(),
            InstitutionalPrimitive.EXECUTE_WORKFLOW: ExecuteWorkflowPrimitive(),
            InstitutionalPrimitive.MULTI_AGENT_COLLABORATE: MultiAgentCollaboratePrimitive(),
            InstitutionalPrimitive.COMPUTE_CONSENSUS: ComputeConsensusPrimitive(),
            InstitutionalPrimitive.GENERATE_REPORT: GenerateReportPrimitive()
        }
    
    def get_primitive(self, primitive_type: InstitutionalPrimitive) -> InstitutionalPrimitiveBase:
        """Get primitive instance by type"""
        if primitive_type not in self.primitives:
            raise ValueError(f"Unknown primitive type: {primitive_type}")
        return self.primitives[primitive_type]
    
    def register_primitive(
        self, 
        primitive_type: InstitutionalPrimitive, 
        primitive_instance: InstitutionalPrimitiveBase
    ) -> None:
        """Register a new primitive"""
        self.primitives[primitive_type] = primitive_instance
    
    def list_primitives(self) -> list[InstitutionalPrimitive]:
        """List all available primitives"""
        return list(self.primitives.keys())

# Example usage
async def example_primitive_execution():
    """Example of how to execute institutional primitives"""
    # Initialize factory
    factory = InstitutionalPrimitiveFactory()
    
    # Create context for intent interpretation
    context = PrimitiveContext(
        primitive_id="intent_001",
        primitive_type=InstitutionalPrimitive.INTERPRET_INTENT,
        session_id="session_123",
        execution_id="exec_001",
        inputs={
            "user_input": "I need to organize a debate about AI ethics",
            "context": {"user_id": "user_123", "timestamp": datetime.now().isoformat()}
        },
        assigned_agents=["intent_analyzer"]
    )
    
    # Get services (mock for example)
    services = {
        "intent_analysis_service": None,  # Would be actual service
        "team_formation_engine": None,
        "workflow_orchestrator": None,
        "consensus_engine": None,
        "communication_bus": None
    }
    
    # Execute primitive
    primitive = factory.get_primitive(InstitutionalPrimitive.INTERPRET_INTENT)
    result = await primitive.execute(context, services)
    
    print(f"Primitive execution result: {result.success}")
    print(f"Outputs: {result.outputs}")
    
    return result

if __name__ == "__main__":
    print("Institutional Primitives Implementation")
    print("======================================")
    print("This module implements the core institutional primitives")
    print("for multi-agent collaboration in the DAIP system.")
    print("\nAvailable primitives:")
    factory = InstitutionalPrimitiveFactory()
    for primitive in factory.list_primitives():
        print(f"- {primitive.value}")