"""Test script for ChatRoomManager implementation.
"""

import tempfile
from pathlib import Path

from src.virtual_role_chat.chat_room_manager import ChatRoomManager
from src.virtual_role_chat.models import ChatRoomConfig


def test_basic_crud_operations():
    """Test basic CRUD operations of ChatRoomManager."""
    print("Testing basic CRUD operations...")

    # Create a temporary storage file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        storage_path = f.name

    try:
        # Initialize ChatRoomManager
        manager = ChatRoomManager(storage_path=storage_path)

        # Test creating a chat room
        config = ChatRoomConfig(
            name="AI Ethics Discussion",
            description="A room for discussing AI ethics",
            topic="The future of AI and its ethical implications",
            roles=["philosopher", "scientist", "ethicist", "policy_maker"],
            mode="structured",
            interaction_rules={
                "max_response_length": 1000,
                "require_citations": True,
                "moderation_level": "moderate"
            }
        )

        room_id = manager.create_chat_room(config)
        print(f"✓ Created chat room: {room_id}")

        # Test getting the chat room
        room = manager.get_chat_room(room_id)
        print(f"✓ Retrieved chat room: {room.config.name}")
        assert room.config.name == config.name
        assert room.config.topic == config.topic
        assert len(room.config.roles) == 4

        # Test updating the chat room
        updated_config = ChatRoomConfig(
            name="AI Ethics Discussion - Updated",
            description="An updated room for discussing AI ethics",
            topic="The future of AI and its ethical implications - Updated",
            roles=["philosopher", "scientist", "ethicist"],  # Removed policy_maker
            mode="free_form",  # Changed mode
            interaction_rules={
                "max_response_length": 800,  # Changed limit
                "require_citations": False,  # Changed requirement
                "moderation_level": "light"  # Changed level
            }
        )

        success = manager.update_chat_room(room_id, updated_config)
        print(f"✓ Updated chat room: {success}")
        assert success is True

        # Verify the update
        updated_room = manager.get_chat_room(room_id)
        assert updated_room.config.name == updated_config.name
        assert updated_room.config.mode == "free_form"
        assert len(updated_room.config.roles) == 3

        # Test listing chat rooms
        rooms = manager.list_chat_rooms()
        print(f"✓ Listed {len(rooms)} chat rooms")
        assert len(rooms) == 1
        assert rooms[0].name == updated_config.name

        # Test archiving a chat room
        success = manager.archive_chat_room(room_id)
        print(f"✓ Archived chat room: {success}")
        assert success is True

        archived_room = manager.get_chat_room(room_id)
        assert archived_room.status == "archived"

        # Test activating a chat room
        success = manager.activate_chat_room(room_id)
        print(f"✓ Activated chat room: {success}")
        assert success is True

        active_room = manager.get_chat_room(room_id)
        assert active_room.status == "active"

        # Test deleting the chat room
        success = manager.delete_chat_room(room_id)
        print(f"✓ Deleted chat room: {success}")
        assert success is True

        # Verify deletion
        rooms = manager.list_chat_rooms()
        assert len(rooms) == 0

        print("✓ All basic CRUD operations passed!")

    finally:
        # Clean up
        Path(storage_path).unlink(missing_ok=True)


def test_multiple_rooms():
    """Test managing multiple chat rooms."""
    print("\nTesting multiple chat rooms...")

    manager = ChatRoomManager()  # In-memory storage

    # Create multiple rooms
    room_configs = [
        ChatRoomConfig(
            name="Philosophy Debate",
            topic="The nature of consciousness",
            roles=["philosopher", "neuroscientist"],
            mode="debate"
        ),
        ChatRoomConfig(
            name="Tech Innovation",
            topic="Future of technology",
            roles=["engineer", "futurist", "entrepreneur"],
            mode="free_form"
        ),
        ChatRoomConfig(
            name="Climate Discussion",
            topic="Climate change solutions",
            roles=["scientist", "policy_maker", "activist"],
            mode="structured"
        )
    ]

    room_ids = []
    for config in room_configs:
        room_id = manager.create_chat_room(config)
        room_ids.append(room_id)
        print(f"✓ Created room: {config.name}")

    # Test listing all rooms
    rooms = manager.list_chat_rooms()
    assert len(rooms) == 3
    print(f"✓ Listed {len(rooms)} rooms")

    # Test getting active rooms
    active_rooms = manager.get_active_rooms()
    assert len(active_rooms) == 3
    print(f"✓ Found {len(active_rooms)} active rooms")

    # Archive one room
    manager.archive_chat_room(room_ids[0])

    # Test getting active and archived rooms
    active_rooms = manager.get_active_rooms()
    archived_rooms = manager.get_archived_rooms()
    assert len(active_rooms) == 2
    assert len(archived_rooms) == 1
    print(f"✓ Active rooms: {len(active_rooms)}, Archived rooms: {len(archived_rooms)}")

    # Test room count
    total_count = manager.get_room_count()
    assert total_count == 3
    print(f"✓ Total room count: {total_count}")

    print("✓ Multiple rooms test passed!")


def test_error_handling():
    """Test error handling."""
    print("\nTesting error handling...")

    manager = ChatRoomManager()

    # Test getting non-existent room
    try:
        manager.get_chat_room("non_existent_room")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly raised error for non-existent room: {e}")

    # Test updating non-existent room
    try:
        config = ChatRoomConfig(name="Test", topic="Test", roles=["test"])
        manager.update_chat_room("non_existent_room", config)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly raised error for updating non-existent room: {e}")

    # Test deleting non-existent room
    try:
        manager.delete_chat_room("non_existent_room")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly raised error for deleting non-existent room: {e}")

    print("✓ Error handling test passed!")


def test_persistence():
    """Test data persistence."""
    print("\nTesting data persistence...")

    # Create a temporary storage file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        storage_path = f.name

    try:
        # Create manager and add a room
        manager1 = ChatRoomManager(storage_path=storage_path)
        config = ChatRoomConfig(
            name="Persistent Room",
            topic="Testing persistence",
            roles=["tester"],
            mode="free_form"
        )
        room_id = manager1.create_chat_room(config)
        print(f"✓ Created room in first manager: {room_id}")

        # Create a new manager instance (should load from storage)
        manager2 = ChatRoomManager(storage_path=storage_path)
        rooms = manager2.list_chat_rooms()
        assert len(rooms) == 1
        assert rooms[0].name == "Persistent Room"
        print("✓ Successfully loaded room in second manager")

        # Verify the room data
        loaded_room = manager2.get_chat_room(room_id)
        assert loaded_room.config.name == config.name
        assert loaded_room.config.topic == config.topic
        assert loaded_room.config.roles == config.roles
        print("✓ Room data integrity maintained")

        print("✓ Persistence test passed!")

    finally:
        # Clean up
        Path(storage_path).unlink(missing_ok=True)


def main():
    """Run all tests."""
    print("=== Testing ChatRoomManager Implementation ===")

    try:
        test_basic_crud_operations()
        test_multiple_rooms()
        test_error_handling()
        test_persistence()

        print("\n=== All ChatRoomManager Tests Passed! ===")
        print("✓ Basic CRUD operations work correctly")
        print("✓ Multiple room management works")
        print("✓ Error handling is proper")
        print("✓ Data persistence works")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
