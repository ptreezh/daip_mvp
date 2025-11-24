"""
Unit tests for the hierarchical architecture base classes.
"""
import pytest
from unittest.mock import Mock, patch
from src.daip_live.subagents.base import TheorySubagent, AnalysisResult, SubagentCapabilities
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata


class TestTheorySubagent:
    """Test cases for the TheorySubagent base class."""
    
    def test_abstract_methods_enforced(self):
        """Test that abstract methods must be implemented."""
        # This should raise TypeError because abstract methods aren't implemented
        with pytest.raises(TypeError):
            TheorySubagent("test_subagent")
    
    def test_subagent_initialization(self):
        """Test Subagent initialization."""
        # Create a concrete implementation for testing
        class ConcreteSubagent(TheorySubagent):
            def analyze(self, data, context=None):
                return AnalysisResult("test", {})
            
            def get_capabilities(self):
                return SubagentCapabilities("test", "test", [], [])
        
        subagent = ConcreteSubagent("test_subagent", {"config_key": "config_value"})
        assert subagent.name == "test_subagent"
        assert subagent.config == {"config_key": "config_value"}
        assert subagent.is_initialized == False
    
    def test_subagent_configuration(self):
        """Test Subagent configuration."""
        class ConcreteSubagent(TheorySubagent):
            def analyze(self, data, context=None):
                return AnalysisResult("test", {})
            
            def get_capabilities(self):
                return SubagentCapabilities("test", "test", [], [])
        
        subagent = ConcreteSubagent("test_subagent")
        subagent.configure({"new_key": "new_value"})
        assert subagent.config["new_key"] == "new_value"
    
    def test_subagent_lifecycle(self):
        """Test Subagent initialization and cleanup."""
        class ConcreteSubagent(TheorySubagent):
            def __init__(self, name, config=None):
                super().__init__(name, config)
                self.cleaned_up = False
            
            def analyze(self, data, context=None):
                return AnalysisResult("test", {})
            
            def get_capabilities(self):
                return SubagentCapabilities("test", "test", [], [])
            
            def cleanup(self):
                self.cleaned_up = True
                super().cleanup()
        
        subagent = ConcreteSubagent("test_subagent")
        subagent.initialize()
        assert subagent.is_initialized == True
        
        subagent.cleanup()
        assert subagent.cleaned_up == True


class TestAnalysisResult:
    """Test cases for AnalysisResult data class."""
    
    def test_analysis_result_creation(self):
        """Test AnalysisResult creation."""
        result = AnalysisResult(
            content="test content",
            metadata={"key": "value"},
            confidence=0.8,
            subagent_name="test_subagent"
        )
        
        assert result.content == "test content"
        assert result.metadata == {"key": "value"}
        assert result.confidence == 0.8
        assert result.subagent_name == "test_subagent"


class TestSubagentCapabilities:
    """Test cases for SubagentCapabilities data class."""
    
    def test_capabilities_creation(self):
        """Test SubagentCapabilities creation."""
        capabilities = SubagentCapabilities(
            name="test_subagent",
            description="test description",
            supported_domains=["domain1", "domain2"],
            required_skills=["skill1", "skill2"],
            version="1.0"
        )
        
        assert capabilities.name == "test_subagent"
        assert capabilities.description == "test description"
        assert capabilities.supported_domains == ["domain1", "domain2"]
        assert capabilities.required_skills == ["skill1", "skill2"]
        assert capabilities.version == "1.0"


class TestSkill:
    """Test cases for the Skill base class."""
    
    def test_abstract_methods_enforced(self):
        """Test that abstract methods must be implemented."""
        # This should raise TypeError because abstract methods aren't implemented
        with pytest.raises(TypeError):
            Skill(SkillMetadata("test", "test", "1.0", "test"))
    
    def test_skill_lifecycle(self):
        """Test Skill enable/disable functionality."""
        class ConcreteSkill(Skill):
            def execute(self, input):
                return SkillOutput("test", {})
        
        metadata = SkillMetadata("test_skill", "test description", "1.0", "test_author")
        skill = ConcreteSkill(metadata)
        
        assert skill.is_enabled == True
        
        skill.disable()
        assert skill.is_enabled == False
        
        skill.enable()
        assert skill.is_enabled == True


class TestSkillInput:
    """Test cases for SkillInput data class."""
    
    def test_skill_input_creation(self):
        """Test SkillInput creation."""
        input_data = SkillInput(
            data="test data",
            context={"context_key": "context_value"},
            metadata={"meta_key": "meta_value"}
        )
        
        assert input_data.data == "test data"
        assert input_data.context == {"context_key": "context_value"}
        assert input_data.metadata == {"meta_key": "meta_value"}


class TestSkillOutput:
    """Test cases for SkillOutput data class."""
    
    def test_skill_output_creation(self):
        """Test SkillOutput creation."""
        output = SkillOutput(
            result="test result",
            metadata={"meta_key": "meta_value"},
            confidence=0.9,
            execution_time=0.5
        )
        
        assert output.result == "test result"
        assert output.metadata == {"meta_key": "meta_value"}
        assert output.confidence == 0.9
        assert output.execution_time == 0.5


class TestSkillMetadata:
    """Test cases for SkillMetadata data class."""
    
    def test_skill_metadata_creation(self):
        """Test SkillMetadata creation."""
        metadata = SkillMetadata(
            name="test_skill",
            description="test description",
            version="1.0",
            author="test_author",
            tags=["tag1", "tag2"],
            dependencies=["dep1", "dep2"]
        )
        
        assert metadata.name == "test_skill"
        assert metadata.description == "test description"
        assert metadata.version == "1.0"
        assert metadata.author == "test_author"
        assert metadata.tags == ["tag1", "tag2"]
        assert metadata.dependencies == ["dep1", "dep2"]