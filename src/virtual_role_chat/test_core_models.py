"""Simple test script to validate the core data models.
"""

from datetime import datetime

from src.virtual_role_chat.models import (
    ChatMessage,
    ChatRoom,
    ChatRoomConfig,
    ChatSession,
    SubTopic,
    TransparencyLevel,
    ValidationResult,
)


def test_chat_room_models():
    """Test ChatRoom related models."""
    print("Testing ChatRoom models...")

    # Test ChatRoomConfig
    config = ChatRoomConfig(
        name="Test Room",
        description="A test chat room",
        topic="AI Ethics",
        roles=["philosopher", "scientist", "ethicist"],
        mode="free_form",
        interaction_rules={"max_response_length": 500}
    )
    print(f"✓ ChatRoomConfig created: {config.name}")
    print(f"  - Config JSON: {config.model_dump_json()}")

    # Test ChatRoom
    room = ChatRoom(
        id="room_001",
        config=config,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status="active"
    )
    print(f"✓ ChatRoom created: {room.id}")

    return room


def test_chat_session_models():
    """Test ChatSession related models."""
    print("\nTesting ChatSession models...")

    # Test ChatMessage
    message = ChatMessage(
        id="msg_001",
        session_id="session_001",
        sender_id="philosopher",
        sender_type="role",
        content="What are the ethical implications of AI consciousness?",
        timestamp=datetime.now(),
        metadata={"confidence": 0.9}
    )
    print(f"✓ ChatMessage created: {message.sender_id}")

    # Test ChatSession
    session = ChatSession(
        id="session_001",
        room_id="room_001",
        start_time=datetime.now(),
        status="active",
        messages=[message],
        metadata={"transparency_level": "moderate"}
    )
    print(f"✓ ChatSession created: {session.id}")

    return session


def test_validation_models():
    """Test validation and processing models."""
    print("\nTesting validation models...")

    # Test ValidationResult
    validation = ValidationResult(
        is_valid=True,
        confidence=0.85,
        reasoning="Statement is consistent with established facts",
        suggested_correction=None
    )
    print(f"✓ ValidationResult created: valid={validation.is_valid}")

    # Test SubTopic
    subtopic = SubTopic(
        id="subtopic_001",
        parent_topic_id="topic_001",
        content="Machine consciousness definition",
        complexity=0.8,
        required_expertise=["philosophy", "cognitive_science"]
    )
    print(f"✓ SubTopic created: {subtopic.content}")

    # Test TransparencyLevel
    transparency = TransparencyLevel.DETAILED
    print(f"✓ TransparencyLevel: {transparency}")

    return validation, subtopic


def main():
    """Run all tests."""
    print("=== Testing Virtual Role Chat System Core Models ===")

    try:
        room = test_chat_room_models()
        session = test_chat_session_models()
        validation, subtopic = test_validation_models()

        print("\n=== All Tests Passed! ===")
        print("✓ Core data models are working correctly")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
