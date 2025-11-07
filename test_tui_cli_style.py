#!/usr/bin/env python3
"""
Test TUI startup similar to how CLI does it.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tui_like_cli():
    """Test TUI startup similar to CLI approach."""
    print("Testing TUI startup like CLI...")
    print("=" * 40)
    
    try:
        # Import required components
        from daip_live.container import Container
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.tui import DAIP_TUI
        from daip_live.config import config_manager, create_config_yaml_if_not_exists
        
        print("✅ Imports successful")
        
        # Create and configure container
        print("Creating container...")
        container = Container()
        create_config_yaml_if_not_exists()
        container.config.from_yaml("config.yaml")
        print("✅ Container created and configured")
        
        # Get services from container
        print("Getting services from container...")
        agent_executor = container.agent_executor()
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        knowledge_manager = container.knowledge_manager()
        debate_manager = container.debate_manager()
        model_provider = container.model_provider()
        db_manager = container.db_manager()
        role_model_manager = RoleModelManager()
        print("✅ Services retrieved")
        
        # Create TUI instance
        print("Creating TUI instance...")
        tui = DAIP_TUI(
            executor=agent_executor,
            goal="开始与人格AI对话",
            session_manager=session_manager,
            role_manager=role_manager,
            knowledge_manager=knowledge_manager,
            debate_manager=debate_manager,
            model_provider=model_provider,
            db_manager=db_manager,
            config_manager=config_manager,
            role_model_manager=role_model_manager
        )
        print("✅ TUI instance created")
        
        print("TUI is ready to run. If it exits immediately, there might be an exception.")
        print("=" * 40)
        
        # Try to run TUI
        print("Attempting to run TUI...")
        try:
            tui.run()
            print("✅ TUI run completed")
        except Exception as e:
            print(f"❌ TUI run failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tui_like_cli()
    if success:
        print("\n✅ TUI test completed successfully!")
    else:
        print("\n❌ TUI test failed!")
        sys.exit(1)