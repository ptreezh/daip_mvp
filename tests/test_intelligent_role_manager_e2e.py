"""End-to-end tests for the intelligent role management system"""

import asyncio
import pytest
import tempfile
import os
from pathlib import Path

from src.daip_live.p4_role_manager_tools.intelligent_role_manager import IntelligentRoleManager
from src.daip_live.p4_role_manager_tools.role_model_config import EnhancedRole, RoleModelConfig
from src.daip_live.model_provider.provider import LiteLLMProvider
from src.daip_live.core.models import ProviderConfig


class TestIntelligentRoleManagerE2E:
    """End-to-end tests for the IntelligentRoleManager class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for test roles
        self.temp_dir = tempfile.mkdtemp()
        self.roles_path = Path(self.temp_dir) / "test_roles"
        self.roles_path.mkdir(exist_ok=True)
        
        # Create a mock model provider for testing
        self.mock_config = ProviderConfig(model="mock-model")
        self.model_provider = LiteLLMProvider(config=self.mock_config)
        
        self.role_manager = IntelligentRoleManager(
            roles_dir=self.roles_path,
            model_provider=self.model_provider
        )

    def test_end_to_end_role_creation_and_persistence(self):
        """Test complete workflow: topic analysis → role creation → saving → loading"""
        topic = "The impact of AI on healthcare"
        
        # 1. Create a role for the topic
        created_role = self.role_manager.create_role_from_topic(topic, role_position="supporting")
        
        # 2. Verify the role was created with appropriate attributes
        assert created_role.name is not None
        assert len(created_role.name) > 0  # Ensure name exists
        assert "healthcare" in created_role.persona.lower()  # Check persona contains topic
        assert len(created_role.model_configs) > 0
        
        # 3. Save the role to file
        save_success = self.role_manager.save_role_to_file(created_role)
        assert save_success is True
        
        # 4. Verify the file was created
        role_file_path = self.roles_path / f"{created_role.name}.yaml"
        assert role_file_path.exists() is True
        
        # 5. Load the role from file
        loaded_role = self.role_manager.load_role_from_file(created_role.name)
        assert loaded_role is not None
        assert loaded_role.name == created_role.name
        assert loaded_role.persona == created_role.persona
        assert len(loaded_role.model_configs) == len(created_role.model_configs)

    def test_auto_select_roles_for_topic(self):
        """Test automatic role selection for a topic"""
        # Create some test roles
        test_roles = [
            EnhancedRole(
                name="TechExpert",
                persona="An expert in technology and AI systems.",
                tools=[],
                model_configs=[RoleModelConfig(
                    model_name="gpt-4",
                    provider="openai",
                    is_primary=True
                )]
            ),
            EnhancedRole(
                name="Ethicist",
                persona="A specialist in ethical considerations and moral philosophy.",
                tools=[],
                model_configs=[RoleModelConfig(
                    model_name="gpt-4",
                    provider="openai",
                    is_primary=True
                )]
            ),
            EnhancedRole(
                name="HealthcareSpecialist",
                persona="A healthcare professional with knowledge of medical systems.",
                tools=[],
                model_configs=[RoleModelConfig(
                    model_name="gpt-4",
                    provider="openai",
                    is_primary=True
                )]
            )
        ]
        
        topic = "AI in medical diagnosis"
        
        # Use auto-select functionality
        selected_roles = self.role_manager.auto_select_roles(topic, test_roles, num_roles=2)
        
        # Verify that we got 2 roles
        assert len(selected_roles) == 2
        assert all(isinstance(role, EnhancedRole) for role in selected_roles)
        
        # At least one role should be relevant to healthcare
        relevant_roles = [role for role in selected_roles 
                         if "healthcare" in role.name.lower() or "healthcare" in role.persona.lower()]
        assert len(relevant_roles) >= 1

    def test_create_and_save_role_for_topic(self):
        """Test the complete create-and-save workflow"""
        topic = "Ethical implications of autonomous vehicles"
        
        # Create and save role in one call
        created_role = asyncio.run(
            self.role_manager.create_and_save_role_for_topic(topic, position="opposing")
        )
        
        assert created_role is not None
        assert "autonomous" in created_role.name.lower() or "challenger" in created_role.name.lower()
        
        # Verify the file was created
        role_file_path = self.roles_path / f"{created_role.name}.yaml"
        assert role_file_path.exists() is True
        
        # Load and verify the saved role
        loaded_role = self.role_manager.load_role_from_file(created_role.name)
        assert loaded_role is not None
        assert loaded_role.name == created_role.name

    def test_topic_analysis_and_suggestion(self):
        """Test topic analysis and role suggestion functionality"""
        topic = "Environmental impact of renewable energy"
        
        # Analyze the topic
        analysis = self.role_manager.analyze_topic(topic)
        
        assert analysis['topic'] == topic
        assert 'environment' in analysis['domains'] or 'technology' in analysis['domains']
        assert len(analysis['keywords']) > 0
        assert analysis['complexity_score'] >= 0.0
        
        # Create test roles
        test_roles = [
            EnhancedRole(
                name="EnvironmentalScientist",
                persona="An expert in environmental science and sustainability.",
                tools=[],
                model_configs=[RoleModelConfig(
                    model_name="gpt-4",
                    provider="openai",
                    is_primary=True
                )]
            ),
            EnhancedRole(
                name="Economist",
                persona="An expert in economic impacts and market forces.",
                tools=[],
                model_configs=[RoleModelConfig(
                    model_name="gpt-4",
                    provider="openai",
                    is_primary=True
                )]
            )
        ]
        
        # Suggest roles for the topic
        suggested_roles = self.role_manager.suggest_roles_for_topic(topic, test_roles, num_suggestions=2)
        
        assert len(suggested_roles) <= 2
        assert all(isinstance(role, EnhancedRole) for role in suggested_roles)

    def test_model_update_functionality(self):
        """Test the model update functionality"""
        # Create a role with a model that doesn't exist
        original_role = EnhancedRole(
            name="TestRole",
            persona="A test role with a potentially unavailable model.",
            tools=[],
            model_configs=[RoleModelConfig(
                model_name="nonexistent/model:v1",
                provider="openai",
                is_primary=True
            )]
        )
        
        # Update the role models
        updated_role = asyncio.run(self.role_manager.update_role_models(original_role))
        
        # The updated role should have at least one model configuration
        assert len(updated_role.model_configs) > 0
        
        # If available models exist, the model name should be different
        available_models = asyncio.run(self.role_manager.check_model_availability())
        if available_models:
            assert updated_role.model_configs[0].model_name != "nonexistent/model:v1"


class TestModelAvailability:
    """Tests for model availability checking functionality"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.roles_path = Path(self.temp_dir) / "test_roles"
        self.roles_path.mkdir(exist_ok=True)
        
        self.role_manager = IntelligentRoleManager(roles_dir=self.roles_path)

    def test_model_availability_check(self):
        """Test checking model availability"""
        # This test will work if Ollama is installed
        available_models = asyncio.run(self.role_manager.check_model_availability())
        
        # The result should be a list
        assert isinstance(available_models, list)
        
        # If Ollama is available, we should have some models
        # (this might be empty if Ollama is not installed, which is OK)


def run_e2e_tests():
    """Run all end-to-end tests"""
    test_instance = TestIntelligentRoleManagerE2E()
    test_instance.setup_method()
    
    print("Running end-to-end tests for IntelligentRoleManager...")
    
    # Run each test
    test_instance.test_end_to_end_role_creation_and_persistence()
    print("✓ test_end_to_end_role_creation_and_persistence passed")
    
    test_instance.test_auto_select_roles_for_topic()
    print("✓ test_auto_select_roles_for_topic passed")
    
    test_instance.test_create_and_save_role_for_topic()
    print("✓ test_create_and_save_role_for_topic passed")
    
    test_instance.test_topic_analysis_and_suggestion()
    print("✓ test_topic_analysis_and_suggestion passed")
    
    test_instance.test_model_update_functionality()
    print("✓ test_model_update_functionality passed")
    
    print("All end-to-end tests passed!")


if __name__ == "__main__":
    run_e2e_tests()