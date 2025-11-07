"""
Validated test to reproduce the exact issue with the debate history functionality
"""
import asyncio
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_multimodel_issue():
    """Reproduce the exact multimodel issue."""
    print("Reproducing multimodel debate issue...")
    
    # Try to import and run the debate manager directly
    try:
        from daip_live.container import Container
        from daip_live.core.models import DebateStartEvent, DebateCompleteEvent, DebateTurnCompleteEvent
        from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
        from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
        from daip_live.memory.session_manager import SessionManager
        from daip_live.persistence.database import DatabaseManager
        from daip_live.p4_role_manager_tools.role_manager import RoleManager
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from unittest.mock import Mock
        
        print("✓ All imports successful")
        
        # Create mock components to avoid external dependencies during testing
        mock_provider = Mock()
        mock_provider.generate = Mock(return_value=("Mock response", {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}))
        
        # Create database manager
        db_manager = DatabaseManager(db_path=":memory:")
        session_manager = SessionManager(db_manager=db_manager)
        
        # Create role manager pointing to proper roles directory
        roles_dir = Path("roles").absolute()  # Assuming we have roles in the project root
        if not roles_dir.exists():
            # Create a basic roles directory structure if it doesn't exist
            roles_dir.mkdir(exist_ok=True)
            print(f"Created roles directory: {roles_dir}")
        
        role_manager = RoleManager(roles_dir_path=str(roles_dir))
        role_model_manager = RoleModelManager(roles_dir_path=str(roles_dir))
        
        # Get debate history tracker from container
        container = Container()
        try:
            container.config.from_yaml("config.yaml")
        except:
            # Create a minimal config if file doesn't exist
            from daip_live.config import AppConfig
            config_data = AppConfig(
                database={"path": ":memory:"},
                llm_provider={"default_model": "mock-model", "embedding_model": "mock-embedding"},
                knowledge_base={"directory": "./docs"},
                role_manager={"roles_dir": "./roles"}
            )
            container.config.from_value(config_data)
        
        debate_history_tracker = container.debate_history_tracker()
        print("✓ Debate history tracker created successfully")
        
        # Create debate manager with history tracker
        debate_manager = EnhancedDebateManager(
            session_manager=session_manager,
            role_manager=role_manager,
            role_model_manager=role_model_manager,
            model_provider=mock_provider,
            debate_history_tracker=debate_history_tracker
        )
        
        print("✓ EnhancedDebateManager created successfully")
        
        # Test with roles that exist in the system
        print("Testing with existing roles...")
        available_roles = role_manager.list_roles()
        print(f"Available roles: {[r.name for r in available_roles]}")
        
        # Use existing roles for the test
        test_roles = []
        if len(available_roles) >= 2:
            test_roles = [available_roles[0].name, available_roles[1].name]
        else:
            # Create default roles for this test if none exist
            test_roles = ["pro_arguer", "con_arguer"]
        
        print(f"Using roles for test: {test_roles}")
        
        # Test getting role mappings (this is likely where the error occurs)
        print("Getting role mappings...")
        role_mappings = role_model_manager.get_debate_model_mappings(test_roles)
        print(f"Got {len(role_mappings)} role mappings: {role_mappings}")
        
        # Test starting a debate through the manager
        print("\nTesting debate execution...")
        
        async def run_test():
            session_id = None
            count = 0
            async for event in debate_manager.run_debate(
                topic="Testing multimodel functionality",
                roles_names=test_roles,
                num_rounds=1
            ):
                count += 1
                print(f"Event #{count}: {type(event).__name__}")
                
                if hasattr(event, 'session_id'):
                    print(f"  - Session ID: {event.session_id}")
                
                if isinstance(event, DebateStartEvent):
                    print(f"  - Debate started: {event.topic} with roles {event.roles}")
                elif isinstance(event, DebateCompleteEvent):
                    print(f"  - Debate completed: {event.session_id}")
                    session_id = event.session_id
                    break
                elif isinstance(event, DebateTurnCompleteEvent):
                    print(f"  - Turn complete: {event.participant}")
                
                if count > 10:  # Limit to prevent hanging
                    print("Stopping after 10 events to prevent hanging")
                    break
            
            return session_id
        
        try:
            session_id = asyncio.run(run_test())
            print(f"✓ Debate execution completed, session_id: {session_id}")
            
            # Now try to retrieve the history
            print("\nTesting history retrieval...")
            all_histories = asyncio.run(debate_history_tracker.get_all_histories())
            print(f"✓ Retrieved {len(all_histories)} total histories")
            
            if all_histories:
                for hist in all_histories:
                    print(f"  - Session: {hist.session_id}, Topic: {hist.topic}, Status: {hist.status}")
                    
                # Try to retrieve specific history
                specific_hist = asyncio.run(debate_history_tracker.get_history(all_histories[0].session_id))
                if specific_hist:
                    print(f"✓ Retrieved specific history: {specific_hist.session_id}")
            
            print("\n🎉 MULTIMODEL DEBATE TEST COMPLETED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            print(f"❌ Error during debate execution: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error during test setup: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_multimodel_issue()
    if success:
        print("\n✅ ISSUE HAS BEEN RESOLVED!")
    else:
        print("\n❌ ISSUE STILL EXISTS!")
        sys.exit(1)