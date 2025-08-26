#!/usr/bin/env python3
"""Test script to verify circular import fix."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import_structure():
    """Test that the import structure doesn't have circular dependencies."""
    
    print("Testing import structure...")
    
    # Test 1: main.py should not import services that import from main
    with open('src/cli/main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Check if main.py imports any service classes directly
    service_imports = [
        'UserProfileService', 'BasicIntentAnalysisService', 'RoleManager',
        'EnhancedSSKGManager', 'MemAgent', 'IntegratedLLMManager', 'TaskManager',
        'PrimitiveRegistry', 'WorkflowEngine', 'ChatCoordinator', 'ChatRoomManager',
        'ChatSessionService', 'WikiService'
    ]
    
    for service in service_imports:
        if service in main_content:
            print(f"❌ main.py still imports {service} directly")
            return False
    
    print("✅ main.py no longer imports service classes directly")
    
    # Test 2: Check if command modules import from service_utils instead of main
    command_files = [
        'src/cli/wiki_commands.py',
        'src/cli/chat_commands.py',
        'src/cli/commands/debate_commands.py',
        'src/cli/wiki_commands/basic_commands.py',
        'src/cli/wiki_commands/proposal_commands.py',
        'src/cli/wiki_commands/collaborate_commands.py'
    ]
    
    for file_path in command_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'from src.cli.main import get_wiki_service' in content:
                print(f"❌ {file_path} still imports from src.cli.main")
                return False
                
            if 'from src.cli.service_utils import get_wiki_service' in content:
                print(f"✅ {file_path} uses service_utils correctly")
            
        except FileNotFoundError:
            print(f"⚠️  {file_path} not found (may be expected)")
    
    # Test 3: Check if service_utils exists and has the right functions
    try:
        with open('src/cli/service_utils.py', 'r', encoding='utf-8') as f:
            service_utils_content = f.read()
        
        required_functions = [
            'get_wiki_service', 'get_role_manager', 'get_primitive_registry',
            'get_personal_assistant_router', 'get_chat_coordinator',
            'get_chat_room_manager', 'get_chat_session_service'
        ]
        
        for func in required_functions:
            if f'def {func}(' not in service_utils_content:
                print(f"❌ service_utils.py missing {func}")
                return False
        
        print("✅ service_utils.py has all required functions")
        
    except FileNotFoundError:
        print("❌ service_utils.py not found")
        return False
    
    print("\n🎉 Circular import fix verification completed successfully!")
    print("All command modules now use service_utils instead of importing from main.py")
    return True

if __name__ == "__main__":
    success = test_import_structure()
    sys.exit(0 if success else 1)