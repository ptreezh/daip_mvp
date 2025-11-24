"""
Unit tests for the Subagent manager.
"""
import pytest
from unittest.mock import Mock, patch
from src.daip_live.subagents.base import TheorySubagent, AnalysisResult, SubagentCapabilities
from src.daip_live.orchestration.manager import SubagentManager


class TestSubagentManager:
    """Test cases for the SubagentManager class."""
    
    @pytest.fixture
    def subagent_manager(self):
        """Create a SubagentManager instance for testing."""
        return SubagentManager()
    
    @pytest.fixture
    def mock_subagent(self):
        """Create a mock Subagent for testing."""
        class MockSubagent(TheorySubagent):
            def __init__(self):
                super().__init__("test_subagent")
                self.initialized = False
                self.cleaned_up = False
            
            def analyze(self, data, context=None):
                return AnalysisResult("test analysis", {})
            
            def get_capabilities(self):
                return SubagentCapabilities(
                    name="test_subagent",
                    description="test description",
                    supported_domains=["test_domain"],
                    required_skills=["test_skill"]
                )
            
            def initialize(self):
                self.initialized = True
                super().initialize()
            
            def cleanup(self):
                self.cleaned_up = True
                super().cleanup()
        
        return MockSubagent()
    
    def test_register_subagent(self, subagent_manager, mock_subagent):
        """Test registering a Subagent."""
        subagent_manager.register_subagent(mock_subagent)
        
        assert "test_subagent" in subagent_manager.list_subagents()
        assert subagent_manager.get_subagent("test_subagent") == mock_subagent
        assert mock_subagent.initialized == True
    
    def test_unregister_subagent(self, subagent_manager, mock_subagent):
        """Test unregistering a Subagent."""
        subagent_manager.register_subagent(mock_subagent)
        subagent_manager.unregister_subagent("test_subagent")
        
        assert "test_subagent" not in subagent_manager.list_subagents()
        assert subagent_manager.get_subagent("test_subagent") is None
        assert mock_subagent.cleaned_up == True
    
    def test_register_duplicate_subagent(self, subagent_manager, mock_subagent):
        """Test registering a duplicate Subagent."""
        subagent_manager.register_subagent(mock_subagent)
        
        # Trying to register the same Subagent again should raise an error
        with pytest.raises(ValueError):
            subagent_manager.register_subagent(mock_subagent)
    
    def test_get_nonexistent_subagent(self, subagent_manager):
        """Test getting a non-existent Subagent."""
        subagent = subagent_manager.get_subagent("nonexistent")
        assert subagent is None
    
    def test_list_subagents(self, subagent_manager, mock_subagent):
        """Test listing registered Subagents."""
        assert subagent_manager.list_subagents() == []
        
        subagent_manager.register_subagent(mock_subagent)
        assert subagent_manager.list_subagents() == ["test_subagent"]
    
    def test_get_capabilities(self, subagent_manager, mock_subagent):
        """Test getting Subagent capabilities."""
        subagent_manager.register_subagent(mock_subagent)
        
        capabilities = subagent_manager.get_capabilities("test_subagent")
        assert capabilities is not None
        assert capabilities.name == "test_subagent"
    
    def test_find_subagents_by_capability(self, subagent_manager):
        """Test finding Subagents by capability."""
        # Create mock Subagents with different capabilities
        class MockSubagent1(TheorySubagent):
            def __init__(self):
                super().__init__("subagent1")
            
            def analyze(self, data, context=None):
                return AnalysisResult("test", {})
            
            def get_capabilities(self):
                return SubagentCapabilities(
                    name="subagent1",
                    description="test",
                    supported_domains=["domain1", "common_domain"],
                    required_skills=[]
                )
        
        class MockSubagent2(TheorySubagent):
            def __init__(self):
                super().__init__("subagent2")
            
            def analyze(self, data, context=None):
                return AnalysisResult("test", {})
            
            def get_capabilities(self):
                return SubagentCapabilities(
                    name="subagent2",
                    description="test",
                    supported_domains=["domain2", "common_domain"],
                    required_skills=[]
                )
        
        subagent1 = MockSubagent1()
        subagent2 = MockSubagent2()
        
        subagent_manager.register_subagent(subagent1)
        subagent_manager.register_subagent(subagent2)
        
        # Test finding Subagents by specific domain
        domain1_subagents = subagent_manager.find_subagents_by_capability("domain1")
        assert domain1_subagents == ["subagent1"]
        
        # Test finding Subagents by common domain
        common_subagents = subagent_manager.find_subagents_by_capability("common_domain")
        assert set(common_subagents) == {"subagent1", "subagent2"}
        
        # Test finding Subagents by non-existent domain
        nonexistent_subagents = subagent_manager.find_subagents_by_capability("nonexistent")
        assert nonexistent_subagents == []
    
    def test_match_subagent_to_task(self, subagent_manager):
        """Test matching Subagents to tasks."""
        # Create mock Subagents with different capabilities
        class GroundedTheorySubagent(TheorySubagent):
            def __init__(self):
                super().__init__("grounded_theory")
            
            def analyze(self, data, context=None):
                return AnalysisResult("test", {})
            
            def get_capabilities(self):
                return SubagentCapabilities(
                    name="grounded_theory",
                    description="Grounded Theory expert",
                    supported_domains=["grounded_theory"],
                    required_skills=["coding", "theory_building"]
                )
        
        class SNASubagent(TheorySubagent):
            def __init__(self):
                super().__init__("sna_expert")
            
            def analyze(self, data, context=None):
                return AnalysisResult("test", {})
            
            def get_capabilities(self):
                return SubagentCapabilities(
                    name="sna_expert",
                    description="SNA expert",
                    supported_domains=["sna"],
                    required_skills=["network_analysis", "graph_theory"]
                )
        
        grounded_theory_subagent = GroundedTheorySubagent()
        sna_subagent = SNASubagent()
        
        subagent_manager.register_subagent(grounded_theory_subagent)
        subagent_manager.register_subagent(sna_subagent)
        
        # Test matching to grounded theory domain
        matched_subagent = subagent_manager.match_subagent_to_task("grounded_theory")
        assert matched_subagent == "grounded_theory"
        
        # Test matching to SNA domain
        matched_subagent = subagent_manager.match_subagent_to_task("sna")
        assert matched_subagent == "sna_expert"
        
        # Test matching with required skills
        matched_subagent = subagent_manager.match_subagent_to_task(
            "grounded_theory", ["coding"])
        assert matched_subagent == "grounded_theory"
        
        # Test matching to non-existent domain
        matched_subagent = subagent_manager.match_subagent_to_task("nonexistent")
        assert matched_subagent is None