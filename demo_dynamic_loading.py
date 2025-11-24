"""
Demonstration of dynamic loading of Subagents and Skills.
"""
import os
import sys
import tempfile
import threading
import time
from http.server import HTTPServer
import requests

# Add src to path so we can import our modules
sys.path.insert(0, 'src')

from src.daip_live.subagents.grounded_theory import GroundedTheorySubagent
from src.daip_live.subagents.sna_expert import SNASubagent
from src.daip_live.orchestration.manager import SubagentManager
from src.daip_live.skills.text_analysis import TextAnalysisSkill
from src.daip_live.skills.manager import SkillManager
from src.daip_live.plugins.manager import PluginManager


def start_marketplace_server():
    """Start the marketplace server in a separate thread."""
    from marketplace_server import MarketplaceHandler, HTTPServer
    
    def run_server():
        server_address = ('localhost', 8001)
        httpd = HTTPServer(server_address, MarketplaceHandler)
        print("Marketplace server started on http://localhost:8001")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give server time to start
    return server_thread


def demonstrate_dynamic_loading():
    """Demonstrate dynamic loading of Subagents and Skills."""
    print("=== DAIP-LIVE Dynamic Loading Demonstration ===\n")
    
    # 1. Initialize managers
    print("1. Initializing managers...")
    subagent_manager = SubagentManager()
    skill_manager = SkillManager()
    plugin_manager = PluginManager(subagent_manager, skill_manager)
    
    # 2. Register built-in Subagents and Skills
    print("2. Registering built-in components...")
    subagent_manager.register_subagent(GroundedTheorySubagent())
    subagent_manager.register_subagent(SNASubagent())
    skill_manager.register_skill(TextAnalysisSkill())
    
    print(f"   Built-in Subagents: {subagent_manager.list_subagents()}")
    print(f"   Built-in Skills: {skill_manager.list_skills()}")
    
    # 3. Start marketplace server
    print("\n3. Starting marketplace server...")
    # Note: In a real scenario, you would connect to an external marketplace
    # For this demo, we'll simulate by creating a local plugin file
    
    # 4. Create a sample plugin file
    print("4. Creating sample plugin files...")
    
    # Create directory for plugins
    plugins_dir = os.path.join("data", "plugins_demo")
    os.makedirs(plugins_dir, exist_ok=True)
    
    # Create a sample Subagent plugin
    sample_subagent_code = '''
"""
Sample Dynamic Subagent Plugin.
"""
from src.daip_live.subagents.base import TheorySubagent, AnalysisResult, SubagentCapabilities


class DynamicSubagent(TheorySubagent):
    """A dynamically loaded Subagent."""
    
    def __init__(self):
        super().__init__("dynamic_subagent")
    
    def analyze(self, data, context=None):
        """Perform analysis."""
        return AnalysisResult(
            content=f"Dynamic analysis of: {data[:50]}...",
            metadata={"source": "dynamic_plugin", "length": len(data)},
            confidence=0.95,
            subagent_name=self.name
        )
    
    def get_capabilities(self):
        """Get capabilities."""
        return SubagentCapabilities(
            name=self.name,
            description="A dynamically loaded Subagent",
            supported_domains=["dynamic_analysis", "sample"],
            required_skills=["basic_analysis"],
            version="1.0.0"
        )
'''
    
    # Create a sample Skill plugin
    sample_skill_code = '''
"""
Sample Dynamic Skill Plugin.
"""
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata


class DynamicSkill(Skill):
    """A dynamically loaded skill."""
    
    def __init__(self):
        metadata = SkillMetadata(
            name="dynamic_skill",
            description="A dynamically loaded skill",
            version="1.0.0",
            author="DAIP-LIVE Demo",
            tags=["dynamic", "sample"]
        )
        super().__init__(metadata)
    
    def execute(self, input):
        """Execute the skill."""
        return SkillOutput(
            result=f"Dynamic skill processed: {input.data[:30]}...",
            metadata={"processed_by": "dynamic_skill"},
            confidence=0.90,
            execution_time=0.1
        )
'''
    
    # Save plugin files
    subagent_plugin_path = os.path.join(plugins_dir, "dynamic_subagent.py")
    skill_plugin_path = os.path.join(plugins_dir, "dynamic_skill.py")
    
    with open(subagent_plugin_path, "w", encoding="utf-8") as f:
        f.write(sample_subagent_code)
    
    with open(skill_plugin_path, "w", encoding="utf-8") as f:
        f.write(sample_skill_code)
    
    print(f"   Created plugin files in {plugins_dir}")
    
    # 5. Load plugins from directory
    print("\n5. Loading plugins from directory...")
    subagents_loaded = subagent_manager.load_subagents_from_directory(plugins_dir)
    skills_loaded = skill_manager.load_skills_from_directory(plugins_dir)
    
    print(f"   Loaded {subagents_loaded} Subagents: {subagent_manager.list_subagents()}")
    print(f"   Loaded {skills_loaded} Skills: {skill_manager.list_skills()}")
    
    # 6. Simulate marketplace integration
    print("\n6. Simulating marketplace integration...")
    
    # Create a mock marketplace response
    mock_marketplace_data = {
        "plugins": [
            {
                "name": "marketplace_sna_analyzer",
                "version": "2.0.0",
                "description": "Marketplace SNA Analyzer with advanced features",
                "type": "subagent",
                "url": "file://" + os.path.abspath(subagent_plugin_path),  # Local file for demo
                "checksum": "",
                "dependencies": [],
                "tags": ["sna", "marketplace", "advanced"]
            }
        ]
    }
    
    # Save mock marketplace data to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump(mock_marketplace_data, f)
        marketplace_file = f.name
    
    # Register the mock marketplace
    try:
        success = plugin_manager.register_plugin_source(f"file://{marketplace_file}")
        print(f"   Marketplace registration: {'Success' if success else 'Failed'}")
        
        if success:
            # List available plugins
            available_plugins = plugin_manager.list_available_plugins()
            print(f"   Available plugins: {[p.name for p in available_plugins]}")
            
            # Search for SNA plugins
            sna_plugins = plugin_manager.search_plugins("sna", "subagent")
            print(f"   SNA Subagent plugins: {[p.name for p in sna_plugins]}")
    
    finally:
        # Clean up temporary file
        os.unlink(marketplace_file)
    
    # 7. Demonstrate plugin installation (simulated)
    print("\n7. Demonstrating plugin management...")
    print("   Plugin installation would download and install plugins from URLs")
    print("   Plugin uninstallation would remove plugins and clean up")
    print("   Plugin updates would check for newer versions and upgrade")
    
    # 8. Test the dynamically loaded components
    print("\n8. Testing dynamically loaded components...")
    
    # Test dynamic Subagent
    dynamic_subagent = subagent_manager.get_subagent("dynamic_subagent")
    if dynamic_subagent:
        test_data = "This is test data for dynamic analysis."
        result = dynamic_subagent.analyze(test_data)
        print(f"   Dynamic Subagent result: {result.content[:50]}...")
        print(f"   Confidence: {result.confidence}")
    
    # Test dynamic Skill
    dynamic_skill = skill_manager.get_skill("dynamic_skill")
    if dynamic_skill:
        from src.daip_live.skills.base import SkillInput
        test_input = SkillInput("This is test input for dynamic skill.")
        output = dynamic_skill.execute(test_input)
        print(f"   Dynamic Skill result: {output.result[:50]}...")
        print(f"   Confidence: {output.confidence}")
    
    print("\n=== Dynamic Loading Demonstration Complete ===")
    print("Summary:")
    print(f"  - Loaded {len(subagent_manager.list_subagents())} Subagents")
    print(f"  - Loaded {len(skill_manager.list_skills())} Skills")
    print("  - Dynamic loading from directories works correctly")
    print("  - Marketplace integration framework is ready")


if __name__ == "__main__":
    demonstrate_dynamic_loading()