"""
TDD Tests for Role-Model Configuration System

Test-Driven Development approach for implementing role-model configuration support.
Following SOLID, KISS, and YAGNI principles.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import local model configuration
from daip_live.core.config import get_safe_test_model, is_local_model

from daip_live.p4_role_manager_tools.role_model_config import (
    EnhancedRole, 
    RoleModelConfig, 
    RoleModelMapping
)
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.core.models import Role


class TestRoleModelConfig:
    """Test basic role model configuration functionality."""
    
    def test_role_model_config_creation(self):
        """Test creating a basic model configuration."""
        config = RoleModelConfig(
            model_name=get_safe_test_model(),
            provider="local",
            max_tokens=4000,
            temperature=0.7
        )

        assert config.model_name == "test-model"
        assert config.provider == "local"
        assert config.max_tokens == 4000
        assert config.temperature == 0.7
        assert config.is_primary == True  # Default value
    
    def test_role_model_config_validation(self):
        """Test model configuration validation."""
        # Valid configuration
        config = RoleModelConfig(
            model_name=get_safe_test_model(),
            provider="local",
            max_tokens=4000,
            temperature=0.7
        )
        assert config.temperature == 0.7
        
        # Test temperature bounds (should be 0.0-1.0)
        with pytest.raises(ValueError):
            RoleModelConfig(
                model_name=get_safe_test_model(),
                provider="local",
                temperature=1.5  # Invalid temperature
            )
    
    def test_enhanced_role_creation(self):
        """Test creating enhanced role with model configurations."""
        model_config = RoleModelConfig(
            model_name=get_safe_test_model(),
            provider="local",
            max_tokens=4000,
            temperature=0.7,
            is_primary=True
        )

        role = EnhancedRole(
            name="test_role",
            persona="Test persona",
            tools=["search", "analyze"],
            model_configs=[model_config]
        )

        assert role.name == "test_role"
        assert len(role.model_configs) == 1
        assert role.get_primary_model_config().model_name == "test-model"
    
    def test_enhanced_role_primary_model_selection(self):
        """Test primary model selection logic."""
        configs = [
            RoleModelConfig(model_name="mock-llm", provider="local", is_primary=False),
            RoleModelConfig(model_name=get_safe_test_model(), provider="local", is_primary=True),
            RoleModelConfig(model_name="claude-3", provider="anthropic", is_primary=False)
        ]

        role = EnhancedRole(
            name="test_role",
            persona="Test persona",
            tools=["search"],
            model_configs=configs
        )

        primary = role.get_primary_model_config()
        assert primary.model_name == "test-model"
        assert primary.is_primary == True
    
    def test_enhanced_role_fallback_to_first_model(self):
        """Test fallback to first model when no primary is specified."""
        configs = [
            RoleModelConfig(model_name="mock-llm", provider="local", is_primary=False),
            RoleModelConfig(model_name=get_safe_test_model(), provider="local", is_primary=False)
        ]

        role = EnhancedRole(
            name="test_role",
            persona="Test persona",
            tools=["search"],
            model_configs=configs
        )

        primary = role.get_primary_model_config()
        assert primary.model_name == "mock-llm"  # First model as fallback
    
    def test_enhanced_role_debate_model_config(self):
        """Test debate-specific model configuration."""
        debate_config = RoleModelConfig(
            model_name=get_safe_test_model(),
            provider="local",
            max_tokens=3000,
            temperature=0.5,
            is_primary=True
        )

        role = EnhancedRole(
            name="test_role",
            persona="Test persona",
            tools=["search"],
            debate_model_config=debate_config
        )

        debate_model = role.get_debate_model_config()
        assert debate_model.model_name == "test-model"
        assert debate_model.max_tokens == 3000
    
    def test_role_model_mapping_creation(self):
        """Test role to model mapping creation."""
        role = EnhancedRole(
            name="test_role",
            persona="Test persona",
            tools=["search"]
        )

        mapping = RoleModelMapping.from_role(role)
        assert mapping.role_name == "test_role"
        assert mapping.role_model_config.model_name == "gpt-3.5-turbo"  # Default from EnhancedRole
        assert mapping.priority == 1


class TestRoleModelManager:
    """Test role model manager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = RoleModelManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manager_initialization(self):
        """Test manager initialization with empty directory."""
        assert len(self.manager._roles) == 0
    
    def test_load_basic_role_config(self):
        """Test loading basic role configuration."""
        config_content = """
persona: "Test persona"
tools: ["search", "analyze"]
model_configs:
  - model_name: "gpt-4"
    provider: "openai"
    max_tokens: 4000
    temperature: 0.7
    is_primary: true
"""
        
        config_file = os.path.join(self.temp_dir, "test_role.yaml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Reload manager
        self.manager = RoleModelManager(self.temp_dir)
        
        role = self.manager.get_role_by_name("test_role")
        assert role is not None
        assert role.name == "test_role"
        assert len(role.model_configs) == 1
        assert role.model_configs[0].model_name == "gpt-4"
    
    def test_load_role_without_model_configs(self):
        """Test loading role without model configurations (backward compatibility)."""
        config_content = """
persona: "Test persona"
tools: ["search", "analyze"]
"""
        
        config_file = os.path.join(self.temp_dir, "legacy_role.yaml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Reload manager
        self.manager = RoleModelManager(self.temp_dir)
        
        role = self.manager.get_role_by_name("legacy_role")
        assert role is not None
        assert role.name == "legacy_role"
        assert len(role.model_configs) == 1  # Default config should be created
        assert role.model_configs[0].model_name == "gpt-3.5-turbo"
    
    def test_get_role_model_mapping(self):
        """Test getting role model mapping."""
        config_content = """
persona: "Test persona"
tools: ["search"]
model_configs:
  - model_name: "gpt-4"
    provider: "openai"
    max_tokens: 4000
    temperature: 0.7
    is_primary: true
"""
        
        config_file = os.path.join(self.temp_dir, "test_role.yaml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        self.manager = RoleModelManager(self.temp_dir)
        mapping = self.manager.get_role_model_mapping("test_role")
        
        assert mapping is not None
        assert mapping.role_name == "test_role"
        assert mapping.role_model_config.model_name == "gpt-4"
    
    def test_get_debate_model_mappings(self):
        """Test getting multiple debate model mappings."""
        # Create two role configurations
        for role_name in ["role1", "role2"]:
            config_content = f"""
persona: "Test persona {role_name}"
tools: ["search"]
model_configs:
  - model_name: "gpt-4"
    provider: "openai"
    max_tokens: 4000
    temperature: 0.7
    is_primary: true
"""
            config_file = os.path.join(self.temp_dir, f"{role_name}.yaml")
            with open(config_file, 'w') as f:
                f.write(config_content)
        
        self.manager = RoleModelManager(self.temp_dir)
        mappings = self.manager.get_debate_model_mappings(["role1", "role2"])
        
        assert len(mappings) == 2
        assert mappings[0].role_name in ["role1", "role2"]
        assert mappings[1].role_name in ["role1", "role2"]
    
    def test_list_available_models(self):
        """Test listing all available models."""
        config_content = """
persona: "Test persona"
tools: ["search"]
model_configs:
  - model_name: "gpt-4"
    provider: "openai"
    is_primary: true
  - model_name: "claude-3"
    provider: "anthropic"
    is_primary: false
"""
        
        config_file = os.path.join(self.temp_dir, "test_role.yaml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        self.manager = RoleModelManager(self.temp_dir)
        models = self.manager.list_available_models()
        
        assert "gpt-4" in models
        assert "claude-3" in models
        assert len(models) == 2


class TestEnhancedDebateManager:
    """Test enhanced debate manager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock services
        self.session_manager = Mock()
        self.role_manager = Mock()
        self.role_model_manager = RoleModelManager(self.temp_dir)
        self.model_provider = Mock()
        
        # Create test role configuration
        config_content = """
persona: "Test persona"
tools: ["search"]
model_configs:
  - model_name: "test-model"
    provider: "local"
    max_tokens: 4000
    temperature: 0.7
    is_primary: true
"""
        
        config_file = os.path.join(self.temp_dir, "test_role.yaml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        self.role_model_manager = RoleModelManager(self.temp_dir)
        
        # Create debate manager
        self.debate_manager = EnhancedDebateManager(
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            role_model_manager=self.role_model_manager,
            model_provider=self.model_provider
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_debate_manager_initialization(self):
        """Test debate manager initialization."""
        assert self.debate_manager.session_manager is not None
        assert self.debate_manager.role_model_manager is not None
        assert len(self.debate_manager.model_cache) == 0
    
    @pytest.mark.asyncio
    async def test_get_debate_model_summary(self):
        """Test getting debate model summary."""
        summary = self.debate_manager.get_debate_model_summary(["test_role"])
        
        assert "topic_roles" in summary
        assert "model_assignments" in summary
        assert "model_stats" in summary
        assert "test_role" in summary["topic_roles"]
    
    @pytest.mark.asyncio
    async def test_model_provider_caching(self):
        """Test model provider caching mechanism."""
        # Get model provider for same config twice
        role = self.role_model_manager.get_role_by_name("test_role")
        mapping = self.role_model_manager.get_role_model_mapping("test_role")

        provider1 = self.debate_manager._get_model_provider_for_config(mapping.role_model_config)
        provider2 = self.debate_manager._get_model_provider_for_config(mapping.role_model_config)

        # Should return the same cached instance
        assert provider1 is provider2
        assert len(self.debate_manager.model_cache) == 1


class TestIntegration:
    """Integration tests for role-model configuration system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample role configurations
        sample_configs = {
            "researcher": """
persona: "Research specialist"
tools: ["search", "analyze"]
model_configs:
  - model_name: "test-model"
    provider: "local"
    max_tokens: 4000
    temperature: 0.3
    is_primary: true
debate_model_config:
  model_name: "test-model"
  provider: "local"
  max_tokens: 3000
  temperature: 0.4
  is_primary: true
""",
            "analyst": """
persona: "Data analyst"
tools: ["analyze", "visualize"]
model_configs:
  - model_name: "mock-llm"
    provider: "local"
    max_tokens: 4000
    temperature: 0.2
    is_primary: true
"""
        }
        
        for role_name, config in sample_configs.items():
            config_file = os.path.join(self.temp_dir, f"{role_name}.yaml")
            with open(config_file, 'w') as f:
                f.write(config)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_role_loading(self):
        """Test end-to-end role loading with model configurations."""
        manager = RoleModelManager(self.temp_dir)
        
        # Test loading both roles
        researcher = manager.get_role_by_name("researcher")
        analyst = manager.get_role_by_name("analyst")
        
        assert researcher is not None
        assert analyst is not None
        
        # Test researcher configuration
        assert researcher.get_primary_model_config().model_name == "test-model"
        assert researcher.get_debate_model_config().model_name == "test-model"
        assert researcher.get_debate_model_config().max_tokens == 3000

        # Test analyst configuration
        assert analyst.get_primary_model_config().model_name == "mock-llm"
        assert analyst.get_primary_model_config().temperature == 0.2
    
    def test_debate_model_mappings(self):
        """Test debate model mappings for multiple roles."""
        manager = RoleModelManager(self.temp_dir)
        mappings = manager.get_debate_model_mappings(["researcher", "analyst"])
        
        assert len(mappings) == 2
        
        # Find researcher and analyst mappings
        researcher_mapping = next(m for m in mappings if m.role_name == "researcher")
        analyst_mapping = next(m for m in mappings if m.role_name == "analyst")
        
        # Verify correct model assignments
        assert researcher_mapping.role_model_config.model_name == "test-model"
        assert researcher_mapping.role_model_config.max_tokens == 3000  # Debate config
        assert analyst_mapping.role_model_config.model_name == "mock-llm"
        assert analyst_mapping.role_model_config.temperature == 0.2
    
    def test_model_listing(self):
        """Test listing all available models."""
        manager = RoleModelManager(self.temp_dir)
        models = manager.list_available_models()

        assert "test-model" in models
        assert "mock-llm" in models
        assert len(models) == 2


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_yaml_config(self):
        """Test handling invalid YAML configuration."""
        # Create invalid YAML file
        config_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        manager = RoleModelManager(self.temp_dir)
        
        # Should not crash, should just skip invalid file
        assert len(manager._roles) == 0
    
    def test_invalid_model_config(self):
        """Test handling invalid model configuration."""
        config_content = """
persona: "Test persona"
tools: ["search"]
model_configs:
  - model_name: "gpt-4"
    provider: "openai"
    temperature: 1.5  # Invalid temperature
    is_primary: true
"""
        
        config_file = os.path.join(self.temp_dir, "invalid_model.yaml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        manager = RoleModelManager(self.temp_dir)
        
        # 源码权威: 无效配置的角色文件被整体跳过（role_model_manager.py:61），
        # 无回退默认机制；get_role_by_name 返回 None 即优雅处理
        role = manager.get_role_by_name("invalid_model")
        assert role is None
    
    def test_nonexistent_role(self):
        """Test handling requests for nonexistent roles."""
        manager = RoleModelManager(self.temp_dir)
        
        role = manager.get_role_by_name("nonexistent")
        assert role is None
        
        mapping = manager.get_role_model_mapping("nonexistent")
        assert mapping is None
    
    def test_empty_roles_directory(self):
        """Test handling empty roles directory."""
        manager = RoleModelManager(self.temp_dir)
        
        assert len(manager._roles) == 0
        assert len(manager.list_available_models()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])