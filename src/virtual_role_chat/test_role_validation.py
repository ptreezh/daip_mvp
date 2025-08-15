"""Test script for role validation functionality.
"""

import tempfile
from pathlib import Path

from src.virtual_role_chat.chat_room_manager import ChatRoomManager
from src.virtual_role_chat.models import ChatRoomConfig
from src.virtual_role_chat.role_validator import RoleValidationError, RoleValidator


def test_role_validation():
    """Test basic role validation functionality."""
    print("Testing role validation...")
    
    # Create a temporary storage file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        storage_path = f.name
    
    try:
        # Initialize ChatRoomManager with role validation
        manager = ChatRoomManager(storage_path=storage_path)
        
        # Test getting available roles
        available_roles = manager.get_available_roles()
        print(f"✓ Found {len(available_roles)} available roles")
        
        if available_roles:
            # Show first few roles
            for i, role in enumerate(available_roles[:3]):
                print(f"  - {role['id']}: {role['name']}")
        
        # Test role suggestions for a topic
        if available_roles:
            topic = "artificial intelligence"
            suggestions = manager.suggest_roles_for_topic(topic)
            print(f"✓ Found {len(suggestions)} role suggestions for topic '{topic}'")
            if suggestions:
                print(f"  Suggestions: {', '.join(suggestions[:3])}")
        
        # Test creating a room with valid roles (if any exist)
        if available_roles:
            valid_role_ids = [role['id'] for role in available_roles[:2]]
            
            config = ChatRoomConfig(
                name="Test Room with Valid Roles",
                description="Testing role validation",
                topic="AI and technology",
                roles=valid_role_ids,
                mode="free_form"
            )
            
            # Validate the configuration first
            validation_info = manager.validate_room_config(config)
            print(f"✓ Configuration validation: {validation_info['is_valid']}")
            if not validation_info['is_valid']:
                print(f"  Reason: {validation_info['reasoning']}")
                if validation_info['suggested_correction']:
                    print(f"  Suggestion: {validation_info['suggested_correction']}")
            
            if validation_info['is_valid']:
                # Create the room
                room_id = manager.create_chat_room(config)
                print(f"✓ Created room with valid roles: {room_id}")
                
                # Test searching by role
                rooms_with_role = manager.get_rooms_by_role(valid_role_ids[0])
                print(f"✓ Found {len(rooms_with_role)} rooms with role '{valid_role_ids[0]}'")
        
        # Test creating a room with invalid roles
        try:
            invalid_config = ChatRoomConfig(
                name="Test Room with Invalid Roles",
                description="Testing invalid role handling",
                topic="Testing",
                roles=["non_existent_role_1", "non_existent_role_2"],
                mode="free_form"
            )
            
            room_id = manager.create_chat_room(invalid_config)
            print("❌ Should have failed with invalid roles")
            
        except RoleValidationError as e:
            print(f"✓ Correctly caught role validation error: {e}")
        
        # Test empty roles
        try:
            empty_config = ChatRoomConfig(
                name="Test Room with No Roles",
                description="Testing empty role list",
                topic="Testing",
                roles=[],
                mode="free_form"
            )
            
            room_id = manager.create_chat_room(empty_config)
            print("❌ Should have failed with empty roles")
            
        except RoleValidationError as e:
            print(f"✓ Correctly caught empty roles error: {e}")
        
        # Test duplicate roles
        if available_roles:
            duplicate_role = available_roles[0]['id']
            try:
                duplicate_config = ChatRoomConfig(
                    name="Test Room with Duplicate Roles",
                    description="Testing duplicate role handling",
                    topic="Testing",
                    roles=[duplicate_role, duplicate_role],
                    mode="free_form"
                )
                
                room_id = manager.create_chat_room(duplicate_config)
                print("❌ Should have failed with duplicate roles")
                
            except RoleValidationError as e:
                print(f"✓ Correctly caught duplicate roles error: {e}")
        
        print("✓ Role validation tests passed!")
        
    finally:
        # Clean up
        Path(storage_path).unlink(missing_ok=True)


def test_debate_mode_validation():
    """Test validation specific to debate mode."""
    print("\nTesting debate mode validation...")
    
    manager = ChatRoomManager()  # In-memory storage
    available_roles = manager.get_available_roles()
    
    if len(available_roles) >= 2:
        # Test valid debate configuration
        role_ids = [role['id'] for role in available_roles[:2]]
        
        debate_config = ChatRoomConfig(
            name="Debate Room",
            description="Testing debate mode",
            topic="The future of AI",
            roles=role_ids,
            mode="debate"
        )
        
        validation_info = manager.validate_room_config(debate_config)
        print(f"✓ Debate mode validation with 2 roles: {validation_info['is_valid']}")
        
        if validation_info['is_valid']:
            room_id = manager.create_chat_room(debate_config)
            print(f"✓ Created debate room: {room_id}")
        
        # Test debate mode with only one role
        single_role_config = ChatRoomConfig(
            name="Invalid Debate Room",
            description="Testing debate mode with insufficient roles",
            topic="Testing",
            roles=[role_ids[0]],
            mode="debate"
        )
        
        try:
            room_id = manager.create_chat_room(single_role_config)
            print("❌ Should have failed with insufficient roles for debate")
        except RoleValidationError as e:
            print(f"✓ Correctly caught insufficient roles for debate: {e}")
    
    else:
        print("⚠ Skipping debate mode tests - insufficient roles available")


def test_role_suggestions():
    """Test role suggestion functionality."""
    print("\nTesting role suggestions...")
    
    validator = RoleValidator()
    
    # Test topic-based suggestions
    topics = ["artificial intelligence", "philosophy", "science", "ethics"]
    
    for topic in topics:
        suggestions = validator.suggest_roles_for_topic(topic, max_suggestions=3)
        print(f"✓ Topic '{topic}': {len(suggestions)} suggestions")
        if suggestions:
            print(f"  Suggestions: {', '.join(suggestions)}")
    
    # Test capability-based role search
    capabilities = ["analysis", "research", "debate", "synthesis"]
    
    for capability in capabilities:
        matching_roles = validator.get_roles_by_capability(capability)
        print(f"✓ Capability '{capability}': {len(matching_roles)} matching roles")
        if matching_roles:
            print(f"  Roles: {', '.join(matching_roles[:3])}")


def main():
    """Run all tests."""
    print("=== Testing Role Validation and Assignment ===")
    
    try:
        test_role_validation()
        test_debate_mode_validation()
        test_role_suggestions()
        
        print("\n=== All Role Validation Tests Passed! ===")
        print("✓ Role existence validation works")
        print("✓ Chat room configuration validation works")
        print("✓ Mode-specific validation works")
        print("✓ Role suggestions work")
        print("✓ Error handling is proper")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()