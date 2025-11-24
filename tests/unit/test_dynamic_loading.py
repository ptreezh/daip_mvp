"""
Unit tests for dynamic loading functionality.
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
import shutil

# Add src to path
sys.path.insert(0, 'src')

from src.daip_live.orchestration.manager import SubagentManager
from src.daip_live.skills.manager import SkillManager
from src.daip_live.plugins.manager import PluginManager, PluginInfo
from src.daip_live.subagents.base import TheorySubagent, AnalysisResult, SubagentCapabilities
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata


class TestDynamicLoading(unittest.TestCase):
    """Test cases for dynamic loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = os.path.join(os.path.dirname(__file__), "temp_test_plugins")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test plugin files
        self.sample_subagent_code = '''
"""
Sample Test Subagent.
"""
from src.daip_live.subagents.base import TheorySubagent, AnalysisResult, SubagentCapabilities


class TestSubagent(TheorySubagent):
    """A test Subagent."""
    
    def __init__(self):
        super().__init__("test_subagent")
    
    def analyze(self, data, context=None):
        """Perform analysis."""
        return AnalysisResult(
            content=f"Test analysis of: {data}",
            metadata={"source": "test_plugin"},
            confidence=0.9,
            subagent_name=self.name
        )
    
    def get_capabilities(self):
        """Get capabilities."""
        return SubagentCapabilities(
            name=self.name,
            description="A test Subagent",
            supported_domains=["test"],
            required_skills=["basic_analysis"],
            version="1.0.0"
        )
'''
        
        self.sample_skill_code = '''
"""
Sample Test Skill.
"""
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata


class TestSkill(Skill):
    """A test skill."""
    
    def __init__(self):
        metadata = SkillMetadata(
            name="test_skill",
            description="A test skill",
            version="1.0.0",
            author="Test",
            tags=["test"]
        )
        super().__init__(metadata)
    
    def execute(self, input):
        """Execute the skill."""
        return SkillOutput(
            result=f"Test skill processed: {input.data}",
            metadata={"processed_by": "test_skill"},
            confidence=0.85,
            execution_time=0.05
        )
'''
        
        # Save test plugin files
        self.subagent_file = os.path.join(self.test_dir, "test_subagent.py")
        self.skill_file = os.path.join(self.test_dir, "test_skill.py")
        
        with open(self.subagent_file, "w", encoding="utf-8") as f:
            f.write(self.sample_subagent_code)
        
        with open(self.skill_file, "w", encoding="utf-8") as f:
            f.write(self.sample_skill_code)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_subagent_manager_loads_from_directory(self):
        """Test that SubagentManager can load Subagents from a directory."""
        manager = SubagentManager()
        
        # Initially no Subagents
        self.assertEqual(len(manager.list_subagents()), 0)
        
        # Load Subagents from directory
        loaded_count = manager.load_subagents_from_directory(self.test_dir)
        
        # Should have loaded one Subagent
        self.assertEqual(loaded_count, 1)
        self.assertIn("test_subagent", manager.list_subagents())
        
        # Test that the loaded Subagent works
        subagent = manager.get_subagent("test_subagent")
        self.assertIsNotNone(subagent)
        
        result = subagent.analyze("test data")
        self.assertIn("Test analysis of: test data", result.content)
    
    def test_skill_manager_loads_from_directory(self):
        """Test that SkillManager can load skills from a directory."""
        manager = SkillManager()
        
        # Initially no skills
        self.assertEqual(len(manager.list_skills()), 0)
        
        # Load skills from directory
        loaded_count = manager.load_skills_from_directory(self.test_dir)
        
        # Should have loaded one skill
        self.assertEqual(loaded_count, 1)
        self.assertIn("test_skill", manager.list_skills())
        
        # Test that the loaded skill works
        skill = manager.get_skill("test_skill")
        self.assertIsNotNone(skill)
        
        input_data = SkillInput("test input")
        output = skill.execute(input_data)
        self.assertIn("Test skill processed: test input", output.result)
    
    def test_subagent_manager_handles_nonexistent_directory(self):
        """Test that SubagentManager handles nonexistent directories gracefully."""
        manager = SubagentManager()
        
        # Try to load from nonexistent directory
        loaded_count = manager.load_subagents_from_directory("nonexistent_directory")
        
        # Should return 0 without raising exception
        self.assertEqual(loaded_count, 0)
    
    def test_skill_manager_handles_nonexistent_directory(self):
        """Test that SkillManager handles nonexistent directories gracefully."""
        manager = SkillManager()
        
        # Try to load from nonexistent directory
        loaded_count = manager.load_skills_from_directory("nonexistent_directory")
        
        # Should return 0 without raising exception
        self.assertEqual(loaded_count, 0)
    
    def test_plugin_manager_registration(self):
        """Test PluginManager registration functionality."""
        subagent_manager = Mock()
        skill_manager = Mock()
        plugin_manager = PluginManager(subagent_manager, skill_manager)
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "plugins": [
                {
                    "name": "test_plugin",
                    "version": "1.0.0",
                    "description": "Test plugin",
                    "type": "subagent",
                    "url": "http://example.com/plugin.py",
                    "checksum": "abc123",
                    "dependencies": [],
                    "tags": ["test"]
                }
            ]
        }
        
        with patch('requests.get', return_value=mock_response):
            success = plugin_manager.register_plugin_source("http://example.com/plugins.json")
            
            # Should succeed
            self.assertTrue(success)
            
            # Should have one plugin available
            available_plugins = plugin_manager.list_available_plugins()
            self.assertEqual(len(available_plugins), 1)
            self.assertEqual(available_plugins[0].name, "test_plugin")
    
    def test_plugin_manager_search(self):
        """Test PluginManager search functionality."""
        subagent_manager = Mock()
        skill_manager = Mock()
        plugin_manager = PluginManager(subagent_manager, skill_manager)
        
        # Add some test plugins
        plugin1 = PluginInfo(
            name="sna_analyzer",
            version="1.0.0",
            description="Social Network Analysis tool",
            type="subagent",
            url="http://example.com/sna.py",
            tags=["sna", "network"]
        )
        
        plugin2 = PluginInfo(
            name="nlp_processor",
            version="1.0.0",
            description="Natural Language Processing tool",
            type="skill",
            url="http://example.com/nlp.py",
            tags=["nlp", "text"]
        )
        
        plugin_manager._plugins["sna_analyzer"] = plugin1
        plugin_manager._plugins["nlp_processor"] = plugin2
        
        # Search for SNA plugins
        sna_plugins = plugin_manager.search_plugins("sna")
        self.assertEqual(len(sna_plugins), 1)
        self.assertEqual(sna_plugins[0].name, "sna_analyzer")
        
        # Search for NLP plugins
        nlp_plugins = plugin_manager.search_plugins("nlp")
        self.assertEqual(len(nlp_plugins), 1)
        self.assertEqual(nlp_plugins[0].name, "nlp_processor")
        
        # Search by type
        subagent_plugins = plugin_manager.search_plugins("", "subagent")
        self.assertEqual(len(subagent_plugins), 1)
        self.assertEqual(subagent_plugins[0].name, "sna_analyzer")
    
    def test_plugin_manager_installation(self):
        """Test PluginManager installation functionality."""
        subagent_manager = SubagentManager()
        skill_manager = SkillManager()
        plugin_manager = PluginManager(subagent_manager, skill_manager)
        
        # Add a test plugin
        plugin = PluginInfo(
            name="test_subagent_plugin",
            version="1.0.0",
            description="Test Subagent plugin",
            type="subagent",
            url=f"file://{self.subagent_file}",  # Local file for testing
            tags=["test"]
        )
        plugin_manager._plugins["test_subagent_plugin"] = plugin
        
        # Mock the download method to use local file
        with patch.object(subagent_manager, 'download_and_install_subagent', return_value=True):
            success = plugin_manager.install_plugin("test_subagent_plugin")
            
            # Should succeed
            self.assertTrue(success)
            
            # Should be marked as installed
            self.assertTrue(plugin_manager.is_plugin_installed("test_subagent_plugin"))


if __name__ == '__main__':
    unittest.main()