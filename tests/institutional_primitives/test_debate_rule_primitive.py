"""
Tests for debate rule primitive implementation.

This module contains comprehensive tests for the debate rule institutional primitive,
following the TDD RED-GREEN-REFACTOR approach.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from src.institutional_primitives.base import InstitutionalPrimitive, ExecutionContext
from src.institutional_primitives.debate_rule_primitive import (
    DebateRulePrimitive,
    DebateRuleConfiguration,
    DebateRuleType,
    DebateFormat,
    ParticipantRole,
    DebatePhase
)


class TestDebateRuleConfiguration:
    """Test debate rule configuration validation."""
    
    def test_debate_rule_configuration_valid(self):
        """Test valid debate rule configuration."""
        config = DebateRuleConfiguration(
            rule_id="test_rule",
            name="Test Debate Rule",
            description="Test debate rule configuration",
            rule_type=DebateRuleType.FORMAT_VALIDATION,
            debate_format=DebateFormat.TRADITIONAL,
            max_rounds=3,
            max_participants=6,
            consensus_threshold=0.7,
            evidence_required=True
        )
        
        assert config.rule_id == "test_rule"
        assert config.name == "Test Debate Rule"
        assert config.rule_type == DebateRuleType.FORMAT_VALIDATION
        assert config.debate_format == DebateFormat.TRADITIONAL
        assert config.max_rounds == 3
        assert config.max_participants == 6
        assert config.consensus_threshold == 0.7
        assert config.evidence_required is True
    
    def test_debate_rule_configuration_defaults(self):
        """Test debate rule configuration with default values."""
        config = DebateRuleConfiguration(
            rule_id="default_rule",
            name="Default Rule",
            description="Default configuration"
        )
        
        assert config.rule_id == "default_rule"
        assert config.debate_format == DebateFormat.TRADITIONAL
        assert config.max_rounds == 3
        assert config.max_participants == 10
        assert config.consensus_threshold == 0.5
        assert config.evidence_required is False
    
    def test_debate_rule_configuration_validation_errors(self):
        """Test debate rule configuration validation errors."""
        # Test invalid consensus threshold
        with pytest.raises(ValueError):
            DebateRuleConfiguration(
                rule_id="invalid_rule",
                name="Invalid Rule",
                description="Invalid configuration",
                consensus_threshold=1.5  # Invalid: > 1.0
            )
        
        # Test negative max rounds
        with pytest.raises(ValueError):
            DebateRuleConfiguration(
                rule_id="invalid_rule",
                name="Invalid Rule",
                description="Invalid configuration",
                max_rounds=-1
            )
        
        # Test negative max participants
        with pytest.raises(ValueError):
            DebateRuleConfiguration(
                rule_id="invalid_rule",
                name="Invalid Rule",
                description="Invalid configuration",
                max_participants=0
            )


class TestDebateRulePrimitive:
    """Test debate rule primitive functionality."""
    
    @pytest.fixture
    def execution_context(self):
        """Create a test execution context."""
        return ExecutionContext(
            execution_id="test_execution",
            workflow_id="test_workflow",
            node_id="test_node",
            services={
                "debate_engine": Mock(),
                "role_manager": Mock(),
                "consensus_service": Mock()
            }
        )
    
    @pytest.fixture
    def debate_config(self):
        """Create a test debate configuration."""
        return DebateRuleConfiguration(
            rule_id="test_debate_rule",
            name="Test Debate Rule",
            description="Test debate rule for validation",
            rule_type=DebateRuleType.FORMAT_VALIDATION,
            debate_format=DebateFormat.TRADITIONAL,
            max_rounds=3,
            max_participants=6,
            consensus_threshold=0.7,
            evidence_required=True
        )
    
    @pytest.fixture
    def debate_primitive(self, debate_config):
        """Create a test debate rule primitive."""
        return DebateRulePrimitive("test_primitive", debate_config.dict())
    
    def test_debate_rule_primitive_initialization(self, debate_primitive, debate_config):
        """Test debate rule primitive initialization."""
        assert debate_primitive.primitive_id == "test_primitive"
        assert debate_primitive.config["rule_id"] == "test_debate_rule"
        assert isinstance(debate_primitive.config, dict)
    
    def test_get_input_schema(self, debate_primitive):
        """Test input schema generation."""
        schema = debate_primitive.get_input_schema()
        
        assert isinstance(schema, dict)
        assert "type" in schema
        assert "properties" in schema
        assert "required" in schema
        
        # Check required properties
        required = schema["required"]
        assert "debate_session" in required
        assert "participants" in required
        
        # Check property definitions
        properties = schema["properties"]
        assert "debate_session" in properties
        assert "participants" in properties
        assert "rule_context" in properties
    
    def test_get_output_schema(self, debate_primitive):
        """Test output schema generation."""
        schema = debate_primitive.get_output_schema()
        
        assert isinstance(schema, dict)
        assert "type" in schema
        assert "properties" in schema
        
        # Check property definitions
        properties = schema["properties"]
        assert "validation_result" in properties
        assert "rule_violations" in properties
        assert "enforcement_actions" in properties
        assert "rule_execution_summary" in properties
    
    def test_validate_inputs_valid(self, debate_primitive):
        """Test input validation with valid inputs."""
        inputs = {
            "debate_session": {
                "session_id": "test_session",
                "topic": "Test topic",
                "format": "traditional",
                "max_rounds": 3,
                "current_round": 1
            },
            "participants": [
                {
                    "participant_id": "p1",
                    "name": "Participant 1",
                    "role": "proponent"
                },
                {
                    "participant_id": "p2", 
                    "name": "Participant 2",
                    "role": "opponent"
                }
            ],
            "rule_context": {
                "phase": "main_arguments",
                "round_number": 1
            }
        }
        
        result = debate_primitive.validate_inputs(inputs)
        assert result is True
    
    def test_validate_inputs_missing_required(self, debate_primitive):
        """Test input validation with missing required fields."""
        inputs = {
            "debate_session": {
                "session_id": "test_session"
            }
            # Missing required "participants" field
        }
        
        result = debate_primitive.validate_inputs(inputs)
        assert result is False
    
    def test_validate_outputs_valid(self, debate_primitive):
        """Test output validation with valid outputs."""
        outputs = {
            "validation_result": {
                "is_valid": True,
                "score": 0.95
            },
            "rule_violations": [],
            "enforcement_actions": [],
            "rule_execution_summary": {
                "rules_checked": 5,
                "violations_found": 0,
                "execution_time": 0.1
            }
        }
        
        result = debate_primitive.validate_outputs(outputs)
        assert result is True
    
    def test_validate_outputs_invalid(self, debate_primitive):
        """Test output validation with invalid outputs."""
        outputs = {
            # Missing required "validation_result" field
            "rule_violations": []
        }
        
        result = debate_primitive.validate_outputs(outputs)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_execute_format_validation(self, debate_primitive, execution_context):
        """Test execution with format validation rule type."""
        inputs = {
            "debate_session": {
                "session_id": "test_session",
                "topic": "AI Ethics Debate",
                "format": "traditional",
                "max_rounds": 3,
                "current_round": 1,
                "participants": []
            },
            "participants": [
                {
                    "participant_id": "p1",
                    "name": "AI Ethicist",
                    "role": "proponent"
                },
                {
                    "participant_id": "p2",
                    "name": "Tech Innovator", 
                    "role": "opponent"
                }
            ],
            "rule_context": {
                "phase": "opening_statements",
                "round_number": 1
            }
        }
        
        result = await debate_primitive.execute(inputs, execution_context)
        
        assert isinstance(result, dict)
        assert "validation_result" in result
        assert "rule_violations" in result
        assert "enforcement_actions" in result
        assert "rule_execution_summary" in result
        
        # Check validation result structure
        validation = result["validation_result"]
        assert "is_valid" in validation
        assert "score" in validation
        assert "details" in validation
        
        # Check execution summary
        summary = result["rule_execution_summary"]
        assert "rules_checked" in summary
        assert "violations_found" in summary
        assert "execution_time" in summary
    
    @pytest.mark.asyncio
    async def test_execute_participant_validation(self, debate_config, execution_context):
        """Test execution with participant validation rule type."""
        # Configure for participant validation
        debate_config.rule_type = DebateRuleType.PARTICIPANT_VALIDATION
        debate_config.max_participants = 4
        debate_config.balanced_sides_required = False
        
        primitive = DebateRulePrimitive("participant_primitive", debate_config.model_dump())
        
        inputs = {
            "debate_session": {
                "session_id": "test_session",
                "topic": "Test Debate",
                "format": "traditional",
                "max_rounds": 3,
                "current_round": 1
            },
            "participants": [
                {
                    "participant_id": "p1",
                    "name": "Participant 1",
                    "role": "proponent",
                    "side": "pro"
                },
                {
                    "participant_id": "p2",
                    "name": "Participant 2", 
                    "role": "opponent",
                    "side": "con"
                }
            ],
            "rule_context": {
                "phase": "preparation",
                "round_number": 1
            }
        }
        
        result = await primitive.execute(inputs, execution_context)
        
        assert result["validation_result"]["is_valid"] is True
        assert len(result["rule_violations"]) == 0
    
    @pytest.mark.asyncio
    async def test_execute_violation_detection(self, debate_config, execution_context):
        """Test execution with rule violations."""
        # Configure for validation of all rules (CUSTOM type validates all)
        debate_config.rule_type = DebateRuleType.CUSTOM
        debate_config.max_participants = 2
        debate_config.max_rounds = 2
        
        primitive = DebateRulePrimitive("strict_primitive", debate_config.model_dump())
        
        inputs = {
            "debate_session": {
                "session_id": "test_session",
                "topic": "Test Debate",
                "format": "traditional",
                "max_rounds": 5,  # Violation: exceeds configured max_rounds
                "current_round": 3  # Violation: exceeds configured max_rounds
            },
            "participants": [
                {
                    "participant_id": "p1",
                    "name": "Participant 1",
                    "role": "proponent",
                    "side": "pro"
                },
                {
                    "participant_id": "p2",
                    "name": "Participant 2",
                    "role": "opponent",
                    "side": "con"
                },
                {
                    "participant_id": "p3",  # Violation: exceeds max_participants
                    "name": "Participant 3",
                    "role": "expert",
                    "side": "expert"
                }
            ],
            "rule_context": {
                "phase": "main_arguments",
                "round_number": 3
            }
        }
        
        result = await primitive.execute(inputs, execution_context)
        
        assert result["validation_result"]["is_valid"] is False
        assert len(result["rule_violations"]) > 0
        assert len(result["enforcement_actions"]) > 0
        
        # Check specific violations
        violations = result["rule_violations"]
        violation_types = [v["violation_type"] for v in violations]
        assert "participant_limit" in violation_types
        assert "round_limit" in violation_types
    
    @pytest.mark.asyncio
    async def test_execute_evidence_validation(self, debate_config, execution_context):
        """Test execution with evidence validation rule type."""
        debate_config.rule_type = DebateRuleType.EVIDENCE_VALIDATION
        debate_config.evidence_required = True
        debate_config.min_evidence_per_contribution = 1
        
        primitive = DebateRulePrimitive("evidence_primitive", debate_config.model_dump())
        
        inputs = {
            "debate_session": {
                "session_id": "test_session",
                "topic": "Evidence-Based Debate",
                "format": "traditional",
                "max_rounds": 3,
                "current_round": 2
            },
            "participants": [
                {
                    "participant_id": "p1",
                    "name": "Researcher",
                    "role": "proponent"
                }
            ],
            "rule_context": {
                "phase": "main_arguments",
                "round_number": 2,
                "current_contribution": {
                    "content": "AI will revolutionize healthcare",
                    "evidence": []  # Missing required evidence
                }
            }
        }
        
        result = await primitive.execute(inputs, execution_context)
        
        # Should detect missing evidence violation
        assert len(result["rule_violations"]) > 0
        evidence_violations = [v for v in result["rule_violations"] if v["violation_type"] == "evidence_required"]
        assert len(evidence_violations) > 0
    
    @pytest.mark.asyncio
    async def test_execute_consensus_validation(self, debate_config, execution_context):
        """Test execution with consensus validation rule type."""
        debate_config.rule_type = DebateRuleType.CONSENSUS_VALIDATION
        debate_config.consensus_threshold = 0.8
        debate_config.consensus_required = True
        
        primitive = DebateRulePrimitive("consensus_primitive", debate_config.model_dump())
        
        inputs = {
            "debate_session": {
                "session_id": "test_session",
                "topic": "Consensus Debate",
                "format": "consensus_building",
                "max_rounds": 3,
                "current_round": 3
            },
            "participants": [
                {
                    "participant_id": "p1",
                    "name": "Participant 1",
                    "role": "proponent"
                },
                {
                    "participant_id": "p2",
                    "name": "Participant 2",
                    "role": "opponent"
                }
            ],
            "rule_context": {
                "phase": "consensus_building",
                "round_number": 3,
                "consensus_data": {
                    "agreement_level": 0.6  # Below threshold
                }
            }
        }
        
        result = await primitive.execute(inputs, execution_context)
        
        # Should detect low consensus violation
        assert len(result["rule_violations"]) > 0
        consensus_violations = [v for v in result["rule_violations"] if v["violation_type"] == "consensus_threshold"]
        assert len(consensus_violations) > 0
    
    def test_get_metadata(self, debate_primitive):
        """Test metadata generation."""
        metadata = debate_primitive.get_metadata()
        
        assert metadata["id"] == "test_primitive"
        assert metadata["type"] == "DebateRulePrimitive"
        assert "input_schema" in metadata
        assert "output_schema" in metadata
        assert "config" in metadata
    
    @pytest.mark.asyncio
    async def test_execute_error_handling(self, debate_primitive, execution_context):
        """Test error handling during execution."""
        # Invalid inputs that should cause errors
        inputs = {
            "debate_session": None,  # Invalid
            "participants": "invalid",  # Should be list
            "rule_context": {}
        }
        
        result = await debate_primitive.execute(inputs, execution_context)
        
        # Should handle errors gracefully
        assert result["validation_result"]["is_valid"] is False
        assert len(result["rule_violations"]) > 0
        assert "error" in result["rule_execution_summary"]


class TestDebateRulePrimitiveIntegration:
    """Integration tests for debate rule primitive."""
    
    @pytest.mark.asyncio
    async def test_workflow_integration(self):
        """Test integration with workflow system."""
        # This would test the primitive when used in actual workflows
        # For now, we'll test the basic integration points
        
        config = DebateRuleConfiguration(
            rule_id="workflow_rule",
            name="Workflow Integration Rule",
            description="Rule for workflow integration testing",
            rule_type=DebateRuleType.FORMAT_VALIDATION
        )
        
        primitive = DebateRulePrimitive("workflow_primitive", config.model_dump())
        
        context = ExecutionContext(
            execution_id="workflow_execution",
            workflow_id="debate_workflow",
            node_id="rule_validation_node"
        )
        
        inputs = {
            "debate_session": {
                "session_id": "workflow_session",
                "topic": "Workflow Test Debate",
                "format": "traditional"
            },
            "participants": [],
            "rule_context": {}
        }
        
        result = await primitive.execute(inputs, context)
        
        # Verify workflow integration
        assert "validation_result" in result
        assert "rule_execution_summary" in result
        assert result["rule_execution_summary"]["execution_id"] == context.execution_id
    
    @pytest.mark.asyncio 
    async def test_service_integration(self):
        """Test integration with DAIP-LIVE services."""
        config = DebateRuleConfiguration(
            rule_id="service_rule",
            name="Service Integration Rule",
            description="Rule for service integration testing"
        )
        
        primitive = DebateRulePrimitive("service_primitive", config.model_dump())
        
        # Mock services
        mock_debate_engine = Mock()
        mock_debate_engine.validate_debate_format = AsyncMock(return_value={"valid": True})
        
        context = ExecutionContext(
            execution_id="service_execution",
            workflow_id="service_workflow",
            node_id="service_node",
            services={
                "debate_engine": mock_debate_engine
            }
        )
        
        inputs = {
            "debate_session": {
                "session_id": "service_session",
                "topic": "Service Test Debate",
                "format": "traditional"
            },
            "participants": [],
            "rule_context": {}
        }
        
        result = await primitive.execute(inputs, context)
        
        # Verify service integration
        assert result["validation_result"]["is_valid"] is True
        # The service should have been called (in real implementation)