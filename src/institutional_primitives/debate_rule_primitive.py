"""
Debate Rule Primitive Implementation.

This module implements the debate rule institutional primitive for validating
and enforcing debate rules within the DAIP-LIVE system.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import time

from pydantic import BaseModel, Field, field_validator

from src.institutional_primitives.base import InstitutionalPrimitive, ExecutionContext

logger = logging.getLogger(__name__)


class DebateRuleType(str, Enum):
    """Types of debate rules that can be enforced."""
    FORMAT_VALIDATION = "format_validation"
    PARTICIPANT_VALIDATION = "participant_validation"
    EVIDENCE_VALIDATION = "evidence_validation"
    CONSENSUS_VALIDATION = "consensus_validation"
    TIMING_VALIDATION = "timing_validation"
    CONTENT_VALIDATION = "content_validation"
    CUSTOM = "custom"


class DebateFormat(str, Enum):
    """Supported debate formats."""
    TRADITIONAL = "traditional"
    OXFORD = "oxford"
    PARLIAMENTARY = "parliamentary"
    FISHBOWL = "fishbowl"
    SOCRATIC = "socratic"
    CONSENSUS_BUILDING = "consensus_building"
    CUSTOM = "custom"


class ParticipantRole(str, Enum):
    """Participant roles in debates."""
    PROPONENT = "proponent"
    OPPONENT = "opponent"
    MODERATOR = "moderator"
    OBSERVER = "observer"
    EXPERT = "expert"
    JUDGE = "judge"


class DebatePhase(str, Enum):
    """Debate phases."""
    PREPARATION = "preparation"
    OPENING_STATEMENTS = "opening_statements"
    MAIN_ARGUMENTS = "main_arguments"
    CROSS_EXAMINATION = "cross_examination"
    REBUTTAL = "rebuttal"
    CLOSING_STATEMENTS = "closing_statements"
    CONSENSUS_BUILDING = "consensus_building"
    EVALUATION = "evaluation"
    COMPLETED = "completed"


class DebateRuleConfiguration(BaseModel):
    """Configuration for debate rule primitive."""
    
    rule_id: str
    name: str
    description: str
    rule_type: DebateRuleType = DebateRuleType.FORMAT_VALIDATION
    
    # Debate format settings
    debate_format: DebateFormat = DebateFormat.TRADITIONAL
    allowed_formats: List[DebateFormat] = Field(default_factory=list)
    
    # Participant settings
    min_participants: int = Field(ge=1, default=2)
    max_participants: int = Field(ge=1, default=10)
    required_roles: List[ParticipantRole] = Field(default_factory=list)
    balanced_sides_required: bool = True
    
    # Round and timing settings
    max_rounds: int = Field(ge=1, default=3)
    round_duration_minutes: Optional[int] = Field(ge=1, default=None)
    total_duration_minutes: Optional[int] = Field(ge=1, default=None)
    
    # Consensus settings
    consensus_threshold: float = Field(ge=0.0, le=1.0, default=0.5)
    consensus_required: bool = False
    
    # Evidence requirements
    evidence_required: bool = False
    min_evidence_per_contribution: int = Field(ge=0, default=0)
    evidence_sources_required: bool = False
    
    # Content validation
    max_contribution_length: Optional[int] = Field(ge=1, default=None)
    prohibited_content: List[str] = Field(default_factory=list)
    required_content_elements: List[str] = Field(default_factory=list)
    
    # Enforcement settings
    strict_mode: bool = False
    auto_correct: bool = False
    violation_threshold: int = Field(ge=1, default=3)
    
    # Custom parameters
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @field_validator('consensus_threshold')
    @classmethod
    def validate_consensus_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Consensus threshold must be between 0.0 and 1.0')
        return v
    
    @field_validator('max_participants')
    @classmethod
    def validate_max_participants(cls, v, values):
        if 'min_participants' in values.data and v < values.data['min_participants']:
            raise ValueError('Max participants must be >= min participants')
        return v
    
    @field_validator('max_rounds')
    @classmethod
    def validate_max_rounds(cls, v):
        if v < 1:
            raise ValueError('Max rounds must be at least 1')
        return v


class RuleViolation(BaseModel):
    """Represents a rule violation."""
    
    violation_id: str
    rule_type: str
    violation_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    affected_participants: List[str] = Field(default_factory=list)
    suggested_fix: Optional[str] = None
    auto_correctable: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EnforcementAction(BaseModel):
    """Represents an enforcement action for rule violations."""
    
    action_id: str
    action_type: str  # "warning", "correction", "pause", "terminate", "notification"
    target: str  # "participant", "debate", "moderator", "system"
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    is_automatic: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)


class ValidationResult(BaseModel):
    """Result of rule validation."""
    
    is_valid: bool
    score: float = Field(ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)
    validation_time: datetime = Field(default_factory=datetime.now)
    validator_id: str


class DebateRulePrimitive(InstitutionalPrimitive):
    """
    Debate Rule Primitive for validating and enforcing debate rules.
    
    This primitive provides comprehensive rule validation and enforcement
    for debates, including format validation, participant management,
    evidence requirements, and consensus validation.
    """
    
    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
        """Initialize the debate rule primitive."""
        super().__init__(primitive_id, config)
        
        # Parse configuration
        if config:
            self.rule_config = DebateRuleConfiguration(**config)
        else:
            self.rule_config = DebateRuleConfiguration(
                rule_id="default_rule",
                name="Default Debate Rule",
                description="Default debate rule configuration"
            )
        
        logger.info(f"Initialized DebateRulePrimitive: {primitive_id}")
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for expected inputs."""
        return {
            "type": "object",
            "properties": {
                "debate_session": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "topic": {"type": "string"},
                        "format": {"type": "string"},
                        "max_rounds": {"type": "integer", "minimum": 1},
                        "current_round": {"type": "integer", "minimum": 1},
                        "start_time": {"type": "string", "format": "date-time"},
                        "participants": {"type": "array"}
                    },
                    "required": ["session_id", "topic", "format"]
                },
                "participants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "participant_id": {"type": "string"},
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "side": {"type": "string"}
                        },
                        "required": ["participant_id", "name", "role"]
                    }
                },
                "rule_context": {
                    "type": "object",
                    "properties": {
                        "phase": {"type": "string"},
                        "round_number": {"type": "integer", "minimum": 1},
                        "current_contribution": {"type": "object"},
                        "consensus_data": {"type": "object"}
                    }
                }
            },
            "required": ["debate_session", "participants"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for produced outputs."""
        return {
            "type": "object",
            "properties": {
                "validation_result": {
                    "type": "object",
                    "properties": {
                        "is_valid": {"type": "boolean"},
                        "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "details": {"type": "object"},
                        "validation_time": {"type": "string", "format": "date-time"}
                    },
                    "required": ["is_valid", "score"]
                },
                "rule_violations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "violation_id": {"type": "string"},
                            "rule_type": {"type": "string"},
                            "violation_type": {"type": "string"},
                            "severity": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["violation_id", "rule_type", "violation_type", "description"]
                    }
                },
                "enforcement_actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action_id": {"type": "string"},
                            "action_type": {"type": "string"},
                            "target": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["action_id", "action_type", "target", "description"]
                    }
                },
                "rule_execution_summary": {
                    "type": "object",
                    "properties": {
                        "rules_checked": {"type": "integer", "minimum": 0},
                        "violations_found": {"type": "integer", "minimum": 0},
                        "execution_time": {"type": "number", "minimum": 0.0},
                        "execution_id": {"type": "string"}
                    }
                }
            },
            "required": ["validation_result", "rule_violations", "enforcement_actions", "rule_execution_summary"]
        }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate that the inputs match the expected schema."""
        try:
            # Check required fields
            required_fields = ["debate_session", "participants"]
            for field in required_fields:
                if field not in inputs:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate debate session
            debate_session = inputs["debate_session"]
            if not isinstance(debate_session, dict):
                logger.error("debate_session must be a dictionary")
                return False
            
            session_required = ["session_id", "topic", "format"]
            for field in session_required:
                if field not in debate_session:
                    logger.error(f"Missing required debate_session field: {field}")
                    return False
            
            # Validate participants
            participants = inputs["participants"]
            if not isinstance(participants, list):
                logger.error("participants must be a list")
                return False
            
            for participant in participants:
                if not isinstance(participant, dict):
                    logger.error("Each participant must be a dictionary")
                    return False
                
                participant_required = ["participant_id", "name", "role"]
                for field in participant_required:
                    if field not in participant:
                        logger.error(f"Missing required participant field: {field}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return False
    
    def validate_outputs(self, outputs: Dict[str, Any]) -> bool:
        """Validate that the outputs match the expected schema."""
        try:
            # Check required fields
            required_fields = ["validation_result", "rule_violations", "enforcement_actions", "rule_execution_summary"]
            for field in required_fields:
                if field not in outputs:
                    logger.error(f"Missing required output field: {field}")
                    return False
            
            # Validate validation_result
            validation_result = outputs["validation_result"]
            if not isinstance(validation_result, dict):
                logger.error("validation_result must be a dictionary")
                return False
            
            if "is_valid" not in validation_result or "score" not in validation_result:
                logger.error("validation_result missing required fields")
                return False
            
            # Validate rule_violations and enforcement_actions are lists
            if not isinstance(outputs["rule_violations"], list):
                logger.error("rule_violations must be a list")
                return False
            
            if not isinstance(outputs["enforcement_actions"], list):
                logger.error("enforcement_actions must be a list")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Output validation error: {e}")
            return False
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute the debate rule primitive."""
        start_time = time.time()
        
        try:
            logger.info(f"Executing DebateRulePrimitive: {self.primitive_id}")
            
            # Validate inputs
            if not self.validate_inputs(inputs):
                return self._create_error_result("Invalid inputs", start_time)
            
            # Extract data
            debate_session = inputs["debate_session"]
            participants = inputs["participants"]
            rule_context = inputs.get("rule_context", {})
            
            # Initialize results
            violations = []
            actions = []
            validation_details = {}
            
            # Execute rule validation based on rule type
            if self.rule_config.rule_type == DebateRuleType.FORMAT_VALIDATION:
                violations.extend(self._validate_format(debate_session))
            elif self.rule_config.rule_type == DebateRuleType.PARTICIPANT_VALIDATION:
                violations.extend(self._validate_participants(participants))
            elif self.rule_config.rule_type == DebateRuleType.EVIDENCE_VALIDATION:
                violations.extend(self._validate_evidence(rule_context))
            elif self.rule_config.rule_type == DebateRuleType.CONSENSUS_VALIDATION:
                violations.extend(self._validate_consensus(rule_context))
            elif self.rule_config.rule_type == DebateRuleType.TIMING_VALIDATION:
                violations.extend(self._validate_timing(debate_session, rule_context))
            elif self.rule_config.rule_type == DebateRuleType.CONTENT_VALIDATION:
                violations.extend(self._validate_content(rule_context))
            else:
                # Default: validate all rules
                violations.extend(self._validate_all_rules(debate_session, participants, rule_context))
            
            # Generate enforcement actions
            if violations:
                actions = self._generate_enforcement_actions(violations)
            
            # Calculate validation score
            max_possible_violations = 10  # Arbitrary baseline
            violation_penalty = len(violations) / max_possible_violations
            validation_score = max(0.0, 1.0 - violation_penalty)
            
            # Create validation result
            validation_result = ValidationResult(
                is_valid=len(violations) == 0,
                score=validation_score,
                details=validation_details,
                validator_id=self.primitive_id
            )
            
            # Create execution summary
            execution_time = time.time() - start_time
            execution_summary = {
                "rules_checked": len([self.rule_config.rule_type]),
                "violations_found": len(violations),
                "execution_time": execution_time,
                "execution_id": context.execution_id,
                "primitive_id": self.primitive_id,
                "rule_type": self.rule_config.rule_type.value
            }
            
            logger.info(f"DebateRulePrimitive execution completed: {len(violations)} violations found")
            
            return {
                "validation_result": validation_result.model_dump(),
                "rule_violations": [v.model_dump() for v in violations],
                "enforcement_actions": [a.model_dump() for a in actions],
                "rule_execution_summary": execution_summary
            }
            
        except Exception as e:
            logger.error(f"Error executing DebateRulePrimitive: {e}")
            return self._create_error_result(f"Execution error: {str(e)}", start_time)
    
    def _validate_format(self, debate_session: Dict[str, Any]) -> List[RuleViolation]:
        """Validate debate format rules."""
        violations = []
        
        # Check format compatibility
        session_format = debate_session.get("format")
        if session_format:
            try:
                format_enum = DebateFormat(session_format)
                if (self.rule_config.allowed_formats and 
                    format_enum not in self.rule_config.allowed_formats and
                    format_enum != self.rule_config.debate_format):
                    violations.append(RuleViolation(
                        violation_id=f"format_{session_format}",
                        rule_type="format_validation",
                        violation_type="invalid_format",
                        severity="medium",
                        description=f"Debate format '{session_format}' is not allowed",
                        suggested_fix=f"Use one of the allowed formats: {[f.value for f in self.rule_config.allowed_formats]}"
                    ))
            except ValueError:
                violations.append(RuleViolation(
                    violation_id="format_unknown",
                    rule_type="format_validation", 
                    violation_type="unknown_format",
                    severity="high",
                    description=f"Unknown debate format: {session_format}",
                    suggested_fix=f"Use a valid format: {[f.value for f in DebateFormat]}"
                ))
        
        # Check round limits
        max_rounds = debate_session.get("max_rounds")
        current_round = debate_session.get("current_round", 1)
        
        if max_rounds and max_rounds > self.rule_config.max_rounds:
            violations.append(RuleViolation(
                violation_id="round_limit_exceeded",
                rule_type="format_validation",
                violation_type="round_limit",
                severity="medium",
                description=f"Max rounds ({max_rounds}) exceeds configured limit ({self.rule_config.max_rounds})",
                suggested_fix=f"Reduce max rounds to {self.rule_config.max_rounds}"
            ))
        
        if current_round > self.rule_config.max_rounds:
            violations.append(RuleViolation(
                violation_id="current_round_exceeded",
                rule_type="format_validation",
                violation_type="round_limit",
                severity="high",
                description=f"Current round ({current_round}) exceeds maximum allowed rounds ({self.rule_config.max_rounds})",
                suggested_fix="End debate or increase max rounds"
            ))
        
        return violations
    
    def _validate_participants(self, participants: List[Dict[str, Any]]) -> List[RuleViolation]:
        """Validate participant rules."""
        violations = []
        
        # Check participant count
        participant_count = len(participants)
        
        if participant_count < self.rule_config.min_participants:
            violations.append(RuleViolation(
                violation_id="insufficient_participants",
                rule_type="participant_validation",
                violation_type="participant_limit",
                severity="high",
                description=f"Insufficient participants: {participant_count} < {self.rule_config.min_participants}",
                suggested_fix=f"Add at least {self.rule_config.min_participants - participant_count} more participants"
            ))
        
        if participant_count > self.rule_config.max_participants:
            violations.append(RuleViolation(
                violation_id="excessive_participants",
                rule_type="participant_validation",
                violation_type="participant_limit",
                severity="medium",
                description=f"Too many participants: {participant_count} > {self.rule_config.max_participants}",
                suggested_fix=f"Remove {participant_count - self.rule_config.max_participants} participants"
            ))
        
        # Check required roles
        if self.rule_config.required_roles:
            present_roles = {p.get("role", "").lower() for p in participants}
            missing_roles = []
            
            for required_role in self.rule_config.required_roles:
                if required_role.value not in present_roles:
                    missing_roles.append(required_role.value)
            
            if missing_roles:
                violations.append(RuleViolation(
                    violation_id="missing_roles",
                    rule_type="participant_validation",
                    violation_type="missing_role",
                    severity="high",
                    description=f"Missing required roles: {missing_roles}",
                    suggested_fix=f"Add participants with roles: {missing_roles}"
                ))
        
        # Check balanced sides (if required)
        if self.rule_config.balanced_sides_required:
            sides = {}
            for participant in participants:
                side = participant.get("side", "unknown")
                sides[side] = sides.get(side, 0) + 1
            
            if len(sides) < 2:
                violations.append(RuleViolation(
                    violation_id="unbalanced_sides",
                    rule_type="participant_validation",
                    violation_type="balance",
                    severity="medium",
                    description="Debate lacks balanced sides",
                    suggested_fix="Add participants to different sides"
                ))
        
        return violations
    
    def _validate_evidence(self, rule_context: Dict[str, Any]) -> List[RuleViolation]:
        """Validate evidence rules."""
        violations = []
        
        current_contribution = rule_context.get("current_contribution", {})
        
        if self.rule_config.evidence_required:
            evidence = current_contribution.get("evidence", [])
            evidence_count = len(evidence)
            
            if evidence_count < self.rule_config.min_evidence_per_contribution:
                violations.append(RuleViolation(
                    violation_id="insufficient_evidence",
                    rule_type="evidence_validation",
                    violation_type="evidence_required",
                    severity="medium",
                    description=f"Insufficient evidence: {evidence_count} < {self.rule_config.min_evidence_per_contribution}",
                    suggested_fix=f"Add at least {self.rule_config.min_evidence_per_contribution - evidence_count} evidence items"
                ))
            
            # Check evidence sources if required
            if self.rule_config.evidence_sources_required:
                missing_sources = 0
                for evidence_item in evidence:
                    if not evidence_item.get("source"):
                        missing_sources += 1
                
                if missing_sources > 0:
                    violations.append(RuleViolation(
                        violation_id="missing_evidence_sources",
                        rule_type="evidence_validation",
                        violation_type="evidence_source",
                        severity="low",
                        description=f"Missing sources for {missing_sources} evidence items",
                        suggested_fix="Add sources to all evidence items"
                    ))
        
        return violations
    
    def _validate_consensus(self, rule_context: Dict[str, Any]) -> List[RuleViolation]:
        """Validate consensus rules."""
        violations = []
        
        consensus_data = rule_context.get("consensus_data", {})
        
        if self.rule_config.consensus_required:
            agreement_level = consensus_data.get("agreement_level", 0.0)
            
            if agreement_level < self.rule_config.consensus_threshold:
                violations.append(RuleViolation(
                    violation_id="low_consensus",
                    rule_type="consensus_validation",
                    violation_type="consensus_threshold",
                    severity="medium",
                    description=f"Consensus level ({agreement_level}) below threshold ({self.rule_config.consensus_threshold})",
                    suggested_fix="Continue discussion to build consensus"
                ))
        
        return violations
    
    def _validate_timing(self, debate_session: Dict[str, Any], rule_context: Dict[str, Any]) -> List[RuleViolation]:
        """Validate timing rules."""
        violations = []
        
        # Check round duration
        if self.rule_config.round_duration_minutes:
            # This would require timing data from the debate session
            # For now, we'll check if the round has exceeded theoretical limits
            current_round = rule_context.get("round_number", 1)
            if current_round > self.rule_config.max_rounds:
                violations.append(RuleViolation(
                    violation_id="round_duration_exceeded",
                    rule_type="timing_validation",
                    violation_type="duration",
                    severity="medium",
                    description=f"Round {current_round} exceeds maximum allowed rounds",
                    suggested_fix="End debate or extend round limits"
                ))
        
        # Check total duration
        if self.rule_config.total_duration_minutes:
            # This would require start time from debate session
            pass
        
        return violations
    
    def _validate_content(self, rule_context: Dict[str, Any]) -> List[RuleViolation]:
        """Validate content rules."""
        violations = []
        
        current_contribution = rule_context.get("current_contribution", {})
        content = current_contribution.get("content", "")
        
        # Check content length
        if self.rule_config.max_contribution_length:
            content_length = len(content)
            if content_length > self.rule_config.max_contribution_length:
                violations.append(RuleViolation(
                    violation_id="content_too_long",
                    rule_type="content_validation",
                    violation_type="length",
                    severity="low",
                    description=f"Content length ({content_length}) exceeds maximum ({self.rule_config.max_contribution_length})",
                    suggested_fix="Shorten contribution"
                ))
        
        # Check prohibited content
        for prohibited in self.rule_config.prohibited_content:
            if prohibited.lower() in content.lower():
                violations.append(RuleViolation(
                    violation_id="prohibited_content",
                    rule_type="content_validation",
                    violation_type="prohibited",
                    severity="high",
                    description=f"Content contains prohibited term: {prohibited}",
                    suggested_fix="Remove prohibited content"
                ))
        
        # Check required content elements
        for required in self.rule_config.required_content_elements:
            if required.lower() not in content.lower():
                violations.append(RuleViolation(
                    violation_id="missing_required_content",
                    rule_type="content_validation",
                    violation_type="required",
                    severity="medium",
                    description=f"Content missing required element: {required}",
                    suggested_fix=f"Add {required} to contribution"
                ))
        
        return violations
    
    def _validate_all_rules(self, debate_session: Dict[str, Any], participants: List[Dict[str, Any]], rule_context: Dict[str, Any]) -> List[RuleViolation]:
        """Validate all rule types."""
        violations = []
        
        violations.extend(self._validate_format(debate_session))
        violations.extend(self._validate_participants(participants))
        violations.extend(self._validate_evidence(rule_context))
        violations.extend(self._validate_consensus(rule_context))
        violations.extend(self._validate_timing(debate_session, rule_context))
        violations.extend(self._validate_content(rule_context))
        
        return violations
    
    def _generate_enforcement_actions(self, violations: List[RuleViolation]) -> List[EnforcementAction]:
        """Generate enforcement actions for violations."""
        actions = []
        
        # Group violations by severity
        critical_violations = [v for v in violations if v.severity == "critical"]
        high_violations = [v for v in violations if v.severity == "high"]
        medium_violations = [v for v in violations if v.severity == "medium"]
        low_violations = [v for v in violations if v.severity == "low"]
        
        # Generate actions based on violation count and severity
        if critical_violations:
            actions.append(EnforcementAction(
                action_id="terminate_debate",
                action_type="terminate",
                target="debate",
                description="Terminate debate due to critical violations",
                parameters={"violations": [v.violation_id for v in critical_violations]}
            ))
        
        if high_violations and len(high_violations) >= self.rule_config.violation_threshold:
            actions.append(EnforcementAction(
                action_id="pause_debate",
                action_type="pause",
                target="debate",
                description="Pause debate due to multiple high-severity violations",
                parameters={"violations": [v.violation_id for v in high_violations]}
            ))
        
        if medium_violations:
            actions.append(EnforcementAction(
                action_id="issue_warning",
                action_type="warning",
                target="participants",
                description="Warning issued for medium-severity violations",
                parameters={"violations": [v.violation_id for v in medium_violations]}
            ))
        
        # Auto-correction actions
        if self.rule_config.auto_correct:
            auto_correctable = [v for v in violations if v.auto_correctable]
            for violation in auto_correctable:
                actions.append(EnforcementAction(
                    action_id=f"auto_correct_{violation.violation_id}",
                    action_type="correction",
                    target=violation.affected_participants[0] if violation.affected_participants else "system",
                    description=f"Auto-correct {violation.violation_type}",
                    parameters={"violation_id": violation.violation_id, "fix": violation.suggested_fix}
                ))
        
        return actions
    
    def _create_error_result(self, error_message: str, start_time: float) -> Dict[str, Any]:
        """Create an error result."""
        execution_time = time.time() - start_time
        
        return {
            "validation_result": {
                "is_valid": False,
                "score": 0.0,
                "details": {"error": error_message},
                "validation_time": datetime.now().isoformat(),
                "validator_id": self.primitive_id
            },
            "rule_violations": [
                {
                    "violation_id": "execution_error",
                    "rule_type": "system",
                    "violation_type": "error",
                    "severity": "critical",
                    "description": error_message,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "enforcement_actions": [],
            "rule_execution_summary": {
                "rules_checked": 0,
                "violations_found": 1,
                "execution_time": execution_time,
                "error": error_message
            }
        }