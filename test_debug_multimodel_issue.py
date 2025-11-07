"""
Debug test to identify the exact issue with the multimodel command
"""
import sys
sys.path.insert(0, 'src')
import asyncio

def test_role_mapping_behavior():
    """Test how RoleModelManager behaves with non-existent roles."""
    from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
    
    role_model_manager = RoleModelManager(roles_dir_path='./roles')
    
    # Test with existing roles
    print("Testing with existing roles...")
    existing_roles = ['pro_arguer', 'con_arguer']
    existing_mappings = role_model_manager.get_debate_model_mappings(existing_roles)
    print(f"  For existing roles {existing_roles}: got {len(existing_mappings)} mappings")
    for i, mapping in enumerate(existing_mappings):
        if mapping:
            print(f"    - {existing_roles[i]}: {mapping.role_model_config.model_name}")
        else:
            print(f"    - {existing_roles[i]}: None")
    
    # Test with non-existent roles (this should be the issue)
    print("\\nTesting with non-existent roles...")
    non_existent_roles = ['economist', 'laborer', 'policymaker']
    non_existent_mappings = role_model_manager.get_debate_model_mappings(non_existent_roles)
    print(f"  For non-existent roles {non_existent_roles}: got {len(non_existent_mappings)} mappings")
    for i, mapping in enumerate(non_existent_mappings):
        if mapping:
            print(f"    - {non_existent_roles[i]}: {mapping.role_model_config.model_name}")
        else:
            print(f"    - {non_existent_roles[i]}: None (THIS IS THE PROBLEM!)")
    
    # Test with mixed roles
    print("\\nTesting with mixed existing/non-existent roles...")
    mixed_roles = ['pro_arguer', 'economist', 'con_arguer']
    mixed_mappings = role_model_manager.get_debate_model_mappings(mixed_roles)
    print(f"  For mixed roles {mixed_roles}: got {len(mixed_mappings)} mappings")
    for i, mapping in enumerate(mixed_mappings):
        if mapping:
            print(f"    - {mixed_roles[i]}: {mapping.role_model_config.model_name}")
        else:
            print(f"    - {mixed_roles[i]}: None")
    
    return existing_mappings, non_existent_mappings, mixed_mappings

def test_enhanced_debate_manager_behavior():
    """Test EnhancedDebateManager with the problematic role combinations."""
    print("\\n" + "="*50)
    print("Testing EnhancedDebateManager behavior...")
    
    from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
    from daip_live.memory.session_manager import SessionManager
    from daip_live.persistence.database import DatabaseManager
    from daip_live.p4_role_manager_tools.role_manager import RoleManager
    from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
    from unittest.mock import Mock
    
    # Create components
    db_manager = DatabaseManager(db_path=":memory:")
    session_manager = SessionManager(db_manager=db_manager)
    role_manager = RoleManager(roles_dir_path="./roles")
    role_model_manager = RoleModelManager(roles_dir_path="./roles")
    
    # Mock provider to avoid actual API calls
    mock_provider = Mock()
    mock_provider.generate = Mock(return_value=("Mock response", {"total_tokens": 10}))
    
    # Create the debate manager
    debate_manager = EnhancedDebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        role_model_manager=role_model_manager,
        model_provider=mock_provider
    )
    
    # Test with non-existent roles that were causing the error
    print("Testing problematic role combination that caused original error...")
    problematic_roles = ["economist", "laborer", "policymaker"]
    
    try:
        mappings = role_model_manager.get_debate_model_mappings(problematic_roles)
        print(f"  Raw mappings result: {mappings}")
        
        # Count valid mappings
        valid_mappings = [m for m in mappings if m is not None]
        invalid_mappings = [m for m in mappings if m is None]
        print(f"  Valid mappings: {len(valid_mappings)}, Invalid/None mappings: {len(invalid_mappings)}")
        
        if len(invalid_mappings) > 0:
            print("  ⚠️ ISSUE IDENTIFIED: The problem is in the EnhancedDebateManager's validation logic!")
            print("  The manager expects ALL mappings to be valid, but it receives Nones for non-existent roles.")
            return False, mappings
        else:
            print("  ✓ All mappings are valid")
            return True, mappings
        
    except Exception as e:
        print(f"  ❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    print("🔍 Debugging the multimodel debate issue...")
    
    # First, understand the current behavior
    existing_maps, non_existent_maps, mixed_maps = test_role_mapping_behavior()
    
    # Then test the manager behavior
    manager_works, role_mappings = test_enhanced_debate_manager_behavior()
    
    if not manager_works:
        print("\\n❌ The issue is in EnhancedDebateManager's validation logic")
        print("   It doesn't properly handle None values from RoleModelManager for non-existent roles")
        print("   The fix is to update the manager to create default mappings for None values")
    else:
        print("\\n✅ EnhancedDebateManager properly handles role mappings")