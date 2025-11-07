#!/usr/bin/env python3
"""
Test to check if TUI is actually running or just exiting immediately.
"""

import sys
import os
import subprocess
import time

def test_real_tui_launch():
    """Test actual TUI launch and monitor it."""
    print("Testing actual TUI launch...")
    
    try:
        # Launch TUI as a subprocess with a timeout
        print("Starting TUI process...")
        process = subprocess.Popen(
            [sys.executable, "-c", """
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from daip_live.cli import run
    from daip_live.container import Container
    from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
    from daip_live.tui import DAIP_TUI
    from daip_live.config import config_manager, create_config_yaml_if_not_exists
    
    print('Initializing TUI...')
    
    # Create and configure container
    container = Container()
    create_config_yaml_if_not_exists()
    container.config.from_yaml("config.yaml")
    
    # Get services from container
    agent_executor = container.agent_executor()
    session_manager = container.session_manager()
    role_manager = container.role_manager()
    knowledge_manager = container.knowledge_manager()
    debate_manager = container.debate_manager()
    model_provider = container.model_provider()
    db_manager = container.db_manager()
    role_model_manager = RoleModelManager()
    
    # Create TUI instance
    tui = DAIP_TUI(
        executor=agent_executor,
        goal="Test run",
        session_manager=session_manager,
        role_manager=role_manager,
        knowledge_manager=knowledge_manager,
        debate_manager=debate_manager,
        model_provider=model_provider,
        db_manager=db_manager,
        config_manager=config_manager,
        role_model_manager=role_model_manager
    )
    print('TUI initialized, starting run...')
    tui.run()
except Exception as e:
    print(f'Error in TUI: {e}')
    import traceback
    traceback.print_exc()
"""], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for a short time to see output
        time.sleep(3)
        
        # Check if process is still running
        return_code = process.poll()
        
        stdout, stderr = process.communicate(timeout=1)  # Get any output
        
        print(f"Return code: {return_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        
        if return_code is None:
            print("Process is still running (this is expected for TUI)")
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            return True
        else:
            print("Process terminated immediately")
            return False
            
    except Exception as e:
        print(f"Error testing TUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_tui_launch()
    if success:
        print("✅ TUI appears to be working correctly")
    else:
        print("❌ TUI might have issues")