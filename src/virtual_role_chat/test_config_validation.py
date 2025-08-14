"""Test script for chat room configuration validation.
"""

from src.virtual_role_chat.config_validator import ConfigValidator
from src.virtual_role_chat.models import ChatRoomConfig


def test_basic_validation():
    """Test basic configuration validation."""
    print("Testing basic configuration validation...")

    validator = ConfigValidator()

    # Test valid configuration
    config = ChatRoomConfig(
        name="Test Room",
        description="A test chat room",
        topic="AI Ethics",
        roles=["philosopher", "scientist", "ethicist"],
        mode="free_form",
        interaction_rules={"max_response_length": 500}
    )

    result = validator.validate_config(config)
    print(f"✓ Valid free-form config: {result.is_valid}")
    assert result.is_valid

    # Test invalid mode (using a valid mode but with direct validation)
    try:
        # We'll test the validator's internal method directly since Pydantic already validates the mode
        result = validator._validate_mode_config("invalid_mode", {})
        print(f"✓ Invalid mode detected: {not result.is_valid}")
        print(f"  Reason: {result.reasoning}")
        assert not result.is_valid
    except ValueError as e:
        print(f"✓ Invalid mode detected through exception: {e}")
        # This is also acceptable

    # Test missing name
    missing_name_config = ChatRoomConfig(
        name="",
        description="A room with missing name",
        topic="Testing",
        roles=["tester"],
        mode="free_form",
        interaction_rules={}
    )

    result = validator.validate_config(missing_name_config)
    print(f"✓ Missing name detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid

    # Test missing topic
    missing_topic_config = ChatRoomConfig(
        name="Missing Topic Room",
        description="A room with missing topic",
        topic="",
        roles=["tester"],
        mode="free_form",
        interaction_rules={}
    )

    result = validator.validate_config(missing_topic_config)
    print(f"✓ Missing topic detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid


def test_structured_mode_validation():
    """Test structured mode configuration validation."""
    print("\nTesting structured mode validation...")

    validator = ConfigValidator()

    # Test valid structured mode configuration
    valid_structured_config = ChatRoomConfig(
        name="Structured Discussion",
        description="A structured discussion",
        topic="Climate Change Solutions",
        roles=["scientist", "policy_maker", "activist"],
        mode="structured",
        interaction_rules={
            "phases": ["introduction", "exploration", "synthesis"],
            "time_limit_per_phase": {
                "introduction": 300,
                "exploration": 600,
                "synthesis": 300
            }
        }
    )

    result = validator.validate_config(valid_structured_config)
    print(f"✓ Valid structured config: {result.is_valid}")
    assert result.is_valid

    # Test missing required parameter (phases)
    missing_phases_config = ChatRoomConfig(
        name="Missing Phases",
        description="A structured discussion missing phases",
        topic="Climate Change",
        roles=["scientist", "policy_maker"],
        mode="structured",
        interaction_rules={
            "time_limit_per_phase": {
                "introduction": 300,
                "exploration": 600
            }
        }
    )

    result = validator.validate_config(missing_phases_config)
    print(f"✓ Missing phases detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid

    # Test invalid phases format
    invalid_phases_config = ChatRoomConfig(
        name="Invalid Phases",
        description="A structured discussion with invalid phases",
        topic="Climate Change",
        roles=["scientist", "policy_maker"],
        mode="structured",
        interaction_rules={
            "phases": "introduction,exploration,synthesis",  # Should be a list
            "time_limit_per_phase": {
                "introduction": 300,
                "exploration": 600,
                "synthesis": 300
            }
        }
    )

    result = validator.validate_config(invalid_phases_config)
    print(f"✓ Invalid phases format detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid

    # Test invalid time_limit_per_phase format
    invalid_time_limits_config = ChatRoomConfig(
        name="Invalid Time Limits",
        description="A structured discussion with invalid time limits",
        topic="Climate Change",
        roles=["scientist", "policy_maker"],
        mode="structured",
        interaction_rules={
            "phases": ["introduction", "exploration", "synthesis"],
            "time_limit_per_phase": [300, 600, 300]  # Should be a dictionary
        }
    )

    result = validator.validate_config(invalid_time_limits_config)
    print(f"✓ Invalid time limits format detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid


def test_debate_mode_validation():
    """Test debate mode configuration validation."""
    print("\nTesting debate mode validation...")

    validator = ConfigValidator()

    # Test valid debate mode configuration
    valid_debate_config = ChatRoomConfig(
        name="Oxford Debate",
        description="A formal Oxford-style debate",
        topic="AI Ethics and Regulation",
        roles=["philosopher", "ethicist", "policy_maker", "technologist"],
        mode="debate",
        interaction_rules={
            "debate_format": "oxford",
            "proposition_roles": ["philosopher", "policy_maker"],
            "opposition_roles": ["ethicist", "technologist"],
            "turn_based": True,
            "time_limit": 300
        }
    )

    result = validator.validate_config(valid_debate_config)
    print(f"✓ Valid debate config: {result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert result.is_valid

    # Test missing required parameter (debate_format)
    missing_format_config = ChatRoomConfig(
        name="Missing Format",
        description="A debate missing format",
        topic="AI Ethics",
        roles=["philosopher", "ethicist"],
        mode="debate",
        interaction_rules={
            "turn_based": True,
            "time_limit": 300
        }
    )

    result = validator.validate_config(missing_format_config)
    print(f"✓ Missing debate format detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid

    # Test invalid debate_format value
    invalid_format_config = ChatRoomConfig(
        name="Invalid Format",
        description="A debate with invalid format",
        topic="AI Ethics",
        roles=["philosopher", "ethicist"],
        mode="debate",
        interaction_rules={
            "debate_format": "invalid_format",
            "turn_based": True,
            "time_limit": 300
        }
    )

    result = validator.validate_config(invalid_format_config)
    print(f"✓ Invalid debate format detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid

    # Test missing proposition/opposition roles for Oxford format
    missing_roles_config = ChatRoomConfig(
        name="Missing Roles",
        description="An Oxford debate missing role assignments",
        topic="AI Ethics",
        roles=["philosopher", "ethicist", "policy_maker", "technologist"],
        mode="debate",
        interaction_rules={
            "debate_format": "oxford",
            "turn_based": True,
            "time_limit": 300
        }
    )

    result = validator.validate_config(missing_roles_config)
    print(f"✓ Missing role assignments detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid

    # Test invalid time_limit value
    invalid_time_limit_config = ChatRoomConfig(
        name="Invalid Time Limit",
        description="A debate with invalid time limit",
        topic="AI Ethics",
        roles=["philosopher", "ethicist"],
        mode="debate",
        interaction_rules={
            "debate_format": "oxford",
            "proposition_roles": ["philosopher"],
            "opposition_roles": ["ethicist"],
            "turn_based": True,
            "time_limit": -300  # Should be positive
        }
    )

    result = validator.validate_config(invalid_time_limit_config)
    print(f"✓ Invalid time limit detected: {not result.is_valid}")
    print(f"  Reason: {result.reasoning}")
    assert not result.is_valid


def test_template_generation():
    """Test template generation for different modes."""
    print("\nTesting template generation...")

    validator = ConfigValidator()

    # Test template generation for all modes
    for mode in validator.VALID_MODES:
        template = validator.generate_mode_template(mode)
        print(f"✓ Generated template for {mode} mode")

        # Verify that the template has the required parameters
        schema = validator.get_mode_schema(mode)
        for param in schema["required"]:
            assert param in template, f"Required parameter {param} missing from {mode} template"

    # Test invalid mode
    try:
        template = validator.generate_mode_template("invalid_mode")
        print("❌ Should have failed with invalid mode")
        assert False
    except ValueError as e:
        print(f"✓ Correctly caught invalid mode: {e}")


def main():
    """Run all tests."""
    print("=== Testing Chat Room Configuration Validation ===")

    try:
        test_basic_validation()
        test_structured_mode_validation()
        test_debate_mode_validation()
        test_template_generation()

        print("\n=== All Configuration Validation Tests Passed! ===")
        print("✓ Basic validation works")
        print("✓ Structured mode validation works")
        print("✓ Debate mode validation works")
        print("✓ Template generation works")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
