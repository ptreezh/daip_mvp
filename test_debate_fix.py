import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Import the necessary modules
    from src.daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
    from src.daip_live.memory.session_manager import SessionManager
    from src.daip_live.p4_role_manager_tools.role_manager import RoleManager
    from src.daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
    from src.daip_live.model_provider.provider import LiteLLMProvider
    from src.daip_live.core.models import ProviderConfig
    
    print("All imports successful")
    
    # Create mock objects for testing
    session_manager = SessionManager()
    role_manager = RoleManager("roles")
    role_model_manager = RoleModelManager("roles")
    
    # Create a mock provider config
    provider_config = ProviderConfig(
        model="ollama/llama3",
        embedding_model="mock-embedding"
    )
    model_provider = LiteLLMProvider(provider_config)
    
    # Create the enhanced debate manager
    debate_manager = EnhancedDebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        role_model_manager=role_model_manager,
        model_provider=model_provider
    )
    
    print("EnhancedDebateManager created successfully")
    
    # Test getting role model mappings
    try:
        role_mappings = role_model_manager.get_debate_model_mappings(["pro_arguer", "con_arguer", "test_role"])
        print(f"Role mappings retrieved: {len(role_mappings)} mappings found")
        
        # Print details of each mapping
        for mapping in role_mappings:
            print(f"  - {mapping.role_name}: {mapping.role_model_config.model_name}")
            
        print("Test completed successfully - no AttributeError encountered")
        
        # Test the specific fix for system_prompt attribute
        print("\nTesting system_prompt attribute handling...")
        test_role = role_manager.get_role_by_name("test_role")
        if test_role:
            # Check if the role has system_prompt attribute
            if hasattr(test_role, 'system_prompt'):
                print(f"  - test_role has system_prompt: {test_role.system_prompt}")
            else:
                print("  - test_role does not have system_prompt attribute (expected for base Role)")
                
            # Test the getattr approach used in the fix
            system_prompt = getattr(test_role, 'system_prompt', '')
            print(f"  - getattr result for system_prompt: '{system_prompt}'")
        else:
            print("  - test_role not found")
            
    except Exception as e:
        print(f"Error during role mapping test: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"Error during initialization: {e}")
    import traceback
    traceback.print_exc()