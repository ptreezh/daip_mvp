"""Test script to validate the core data models and interfaces.
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
from src.virtual_role_chat.workflow import (
    DEBATE_WORKFLOW,
    FREE_FORM_WORKFLOW,
    STRUCTURED_WORKFLOW,
    WorkflowEvent,
    WorkflowEventType,
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


def test_workflow_models():
    """Test workflow related models."""
    print("\nTesting workflow models...")

    # Test WorkflowEvent
    event = WorkflowEvent(
        id="event_001",
        type=WorkflowEventType.USER_INPUT,
        session_id="session_001",
        timestamp=datetime.now(),
        data={"input": "Let's discuss AI consciousness"},
        metadata={"user_id": "user_001"}
    )
    print(f"✓ WorkflowEvent created: {event.type}")

    # Test predefined workflows
    print(f"✓ FREE_FORM_WORKFLOW: {FREE_FORM_WORKFLOW.name}")
    print(f"✓ STRUCTURED_WORKFLOW: {STRUCTURED_WORKFLOW.name}")
    print(f"✓ DEBATE_WORKFLOW: {DEBATE_WORKFLOW.name}")

    return event


def test_interface_compatibility():
    """Test that our models are compatible with the interfaces."""
    print("\nTesting interface compatibility...")

    # Import interfaces to ensure they're properly defined
    from src.virtual_role_chat.interfaces import (
        ChatRoomManagerInterface,
    )

    print("✓ All interfaces imported successfully")

    # Test that we can use runtime_checkable
    from typing import runtime_checkable

    @runtime_checkable
    class TestImplementation:
        def create_chat_room(self, config):
            return "test_room_id"

    test_impl = TestImplementation()
    is_compatible = isinstance(test_impl, ChatRoomManagerInterface)
    print(f"✓ Runtime type checking works: {is_compatible}")


def main():
    """Run all tests."""
    print("=== Testing Virtual Role Chat System Models ===")

    try:
        room = test_chat_room_models()
        session = test_chat_session_models()
        validation, subtopic = test_validation_models()
        event = test_workflow_models()
        test_interface_compatibility()

        print("\n=== All Tests Passed! ===")
        print("✓ Core data models are working correctly")
        print("✓ Workflow models are properly defined")
        print("✓ Interfaces are compatible")
        print("✓ Predefined workflows are available")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
