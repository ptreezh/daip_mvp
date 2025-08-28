# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 08:30:00
@Author  : DAIP-LIVE Team
@File    : test_role_consensus_customization.py
@Description:
    Integration tests for role and consensus customization functionality.
    Tests requirements 7.4, 7.5, 7.6, 7.7 for task 11.2.
"""
import pytest

from .role_customization import (
    RoleConfigurationManager, RoleConfiguration, ExpertiseProfile, RolePersonality, RolePromptTemplate,
    ExpertiseLevel, CognitiveStyle, InteractionMode
)
from .consensus_customization import (
    ConsensusManager, ConsensusInput
)
from .performance_optimization import (
    PerformanceOptimizationManager, PerformanceMetricType
)


class TestRoleCustomization:
    """Test role customization functionality (Requirement 7.4)."""
    
    @pytest.fixture
    def role_manager(self):
        """Create a role configuration manager for testing."""
        return RoleConfigurationManager()
    
    def test_role_template_creation(self, role_manager):
        """Test creation of custom role templates."""
        # Create custom expertise profile
        expertise = ExpertiseProfile(
            domain="quantum_computing",
            level=ExpertiseLevel.EXPERT,
            specializations=["quantum_algorithms", "quantum_error_correction"],
            years_experience=10,
            key_skills=["quantum_mechanics", "linear_algebra", "programming"]
        )
        
        # Create custom personality
        personality = RolePersonality(
            openness=0.9,
            conscientiousness=0.8,
            extraversion=0.4,
            agreeableness=0.6,
            neuroticism=0.2
        )
        
        # Create role configuration
        config = RoleConfiguration(
            role_id="quantum_expert_001",
            name="Quantum Computing Expert",
            description="Expert in quantum computing and quantum algorithms",
            expertise_profile=expertise,
            personality=personality,
            cognitive_style=CognitiveStyle.ANALYTICAL,
            interaction_mode=InteractionMode.ANALYTICAL,
            prompt_template=RolePromptTemplate(
                system_prompt="You are a quantum computing expert.",
                task_prompt_template="Apply quantum computing principles to: {task}",
                interaction_prompt_template="As a quantum expert, respond to: {message}",
                context_prompt_template="Given quantum context: {context}"
            ),
            confidence_threshold=0.8,
            communication_style="technical and precise"
        )
        
        # Register configuration
        success = role_manager.register_role_configuration(config)
        assert success is True
        
        # Retrieve and verify
        retrieved_config = role_manager.get_role_configuration("quantum_expert_001")
        assert retrieved_config is not None
        assert retrieved_config.name == "Quantum Computing Expert"
        assert retrieved_config.expertise_profile.domain == "quantum_computing"
    
    def test_role_template_instantiation(self, role_manager):
        """Test creating roles from templates."""
        # Create role from built-in template
        customizations = {
            "expertise_profile": ExpertiseProfile(
                domain="machine_learning",
                level=ExpertiseLevel.EXPERT,
                specializations=["deep_learning", "neural_networks"]
            ),
            "communication_style": "accessible and educational"
        }
        
        config = role_manager.create_role_from_template(
            "domain_expert",
            "ml_expert_001",
            customizations
        )
        
        assert config is not None
        assert config.role_id == "ml_expert_001"
        assert config.expertise_profile.domain == "machine_learning"
        assert config.communication_style == "accessible and educational"
    
    def test_dynamic_role_configuration(self, role_manager):
        """Test dynamic role configuration updates."""
        # Create initial configuration
        config = role_manager.create_role_from_template(
            "critical_reviewer",
            "reviewer_001"
        )
        
        assert config is not None
        initial_threshold = config.confidence_threshold
        
        # Update configuration
        updates = {
            "confidence_threshold": 0.9,
            "communication_style": "diplomatic but thorough",
            "max_response_length": 1500
        }
        
        success = role_manager.update_role_configuration("reviewer_001", updates)
        assert success is True
        
        # Verify updates
        updated_config = role_manager.get_role_configuration("reviewer_001")
        assert updated_config.confidence_threshold == 0.9
        assert updated_config.communication_style == "diplomatic but thorough"
        assert updated_config.max_response_length == 1500


class TestConsensusCustomization:
    """Test consensus customization functionality (Requirement 7.5)."""
    
    @pytest.fixture
    def consensus_manager(self):
        """Create a consensus manager for testing."""
        return ConsensusManager()
    
    @pytest.mark.asyncio
    async def test_majority_vote_consensus(self, consensus_manager):
        """Test majority voting consensus mechanism."""
        # Create consensus inputs
        inputs = [
            ConsensusInput(participant_id="participant_1", vote=True, confidence=0.8),
            ConsensusInput(participant_id="participant_2", vote=True, confidence=0.9),
            ConsensusInput(participant_id="participant_3", vote=False, confidence=0.7),
            ConsensusInput(participant_id="participant_4", vote=True, confidence=0.6)
        ]
        
        # Calculate consensus
        result = await consensus_manager.calculate_consensus("simple_majority", inputs)
        
        assert result is not None
        assert result.consensus_value == "True"  # Majority voted True
        assert result.participant_count == 4
        assert len(result.supporting_participants) == 3
        assert len(result.dissenting_participants) == 1
        assert result.agreement_level == 0.75  # 3/4 agreement
        assert result.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_weighted_vote_consensus(self, consensus_manager):
        """Test weighted voting consensus mechanism."""
        # Create weighted consensus inputs
        inputs = [
            ConsensusInput(participant_id="expert_1", vote="option_A", confidence=0.9, weight=3.0),
            ConsensusInput(participant_id="expert_2", vote="option_B", confidence=0.8, weight=2.0),
            ConsensusInput(participant_id="novice_1", vote="option_A", confidence=0.6, weight=1.0),
            ConsensusInput(participant_id="novice_2", vote="option_B", confidence=0.5, weight=1.0)
        ]
        
        # Calculate weighted consensus
        result = await consensus_manager.calculate_consensus("weighted_expert", inputs)
        
        assert result is not None
        assert result.consensus_value == "option_A"  # Higher weighted support
        assert result.participant_count == 4
        assert result.confidence > 0.4  # Adjusted for weighted algorithm


class TestPerformanceOptimization:
    """Test performance optimization functionality (Requirements 7.6, 7.7)."""
    
    @pytest.fixture
    def optimization_manager(self):
        """Create a performance optimization manager for testing."""
        return PerformanceOptimizationManager()
    
    def test_configuration_validation(self, optimization_manager):
        """Test configuration validation (Requirement 7.6)."""
        # Test valid configuration
        valid_config = {
            "name": "test_workflow",
            "version": "1.0.0",
            "type": "workflow",
            "parameters": {
                "confidence_threshold": 0.7,
                "max_iterations": 5
            },
            "resources": {
                "memory_limit": 2048,
                "cpu_limit": 2.0,
                "timeout": 300
            },
            "dependencies": {
                "services": ["llm_interface", "memory_service"]
            }
        }
        
        result = optimization_manager.validate_and_optimize_configuration(valid_config)
        
        assert "validation" in result
        assert "optimization_suggestions" in result
        assert result["validation"]["is_valid"] is True
        assert len(result["validation"]["errors"]) == 0
    
    def test_performance_profiling(self, optimization_manager):
        """Test performance profiling (Requirement 7.7)."""
        profiler = optimization_manager.profiler
        
        # Start profiling
        session_id = profiler.start_profiling("test_component", "primitive")
        assert session_id is not None
        assert session_id in profiler.active_profiles
        
        # Record metrics
        profiler.record_metric(session_id, PerformanceMetricType.EXECUTION_TIME, 2.5, "seconds")
        profiler.record_metric(session_id, PerformanceMetricType.MEMORY_USAGE, 512, "MB")
        profiler.record_metric(session_id, PerformanceMetricType.THROUGHPUT, 15, "ops/sec")
        
        # End profiling
        profile = profiler.end_profiling(session_id)
        
        assert profile is not None
        assert profile.component_id == "test_component"
        assert len(profile.metrics) == 3
        assert profile.end_time is not None


class TestIntegration:
    """Test integration between role and consensus customization."""
    
    @pytest.fixture
    def integrated_system(self):
        """Create an integrated system for testing."""
        return {
            "role_manager": RoleConfigurationManager(),
            "consensus_manager": ConsensusManager(),
            "optimization_manager": PerformanceOptimizationManager()
        }
    
    @pytest.mark.asyncio
    async def test_role_based_consensus(self, integrated_system):
        """Test consensus with role-based weighting."""
        role_manager = integrated_system["role_manager"]
        consensus_manager = integrated_system["consensus_manager"]
        
        # Create expert roles with different expertise levels
        expert_roles = [
            ("quantum_expert", ExpertiseLevel.EXPERT, 3.0),
            ("physics_expert", ExpertiseLevel.ADVANCED, 2.0),
            ("student", ExpertiseLevel.NOVICE, 1.0)
        ]
        
        # Create role configurations
        for role_id, level, weight in expert_roles:
            config = role_manager.create_role_from_template(
                "domain_expert",
                role_id,
                {
                    "expertise_profile": ExpertiseProfile(
                        domain="quantum_physics",
                        level=level
                    )
                }
            )
            assert config is not None
        
        # Create consensus inputs with role-based weights
        inputs = []
        for role_id, level, weight in expert_roles:
            inputs.append(ConsensusInput(
                participant_id=role_id,
                vote="quantum_supremacy_achieved",
                confidence=0.8 if level == ExpertiseLevel.EXPERT else 0.6,
                weight=weight
            ))
        
        # Add dissenting opinion from student
        inputs[-1].vote = "quantum_supremacy_not_achieved"
        inputs[-1].confidence = 0.4
        
        # Calculate weighted consensus
        result = await consensus_manager.calculate_consensus("weighted_expert", inputs)
        
        assert result is not None
        assert result.consensus_value == "quantum_supremacy_achieved"  # Expert opinion should dominate
        assert result.confidence > 0.5  # Adjusted for weighted algorithm


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])