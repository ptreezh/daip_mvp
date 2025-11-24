"""
Test script to understand the RoleModelMapping structure.
"""
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from src.daip_live.p4_role_manager_tools.role_model_config import RoleModelMapping, RoleModelConfig


def test_mapping_structure():
    """Test the structure of RoleModelMapping."""
    print("Testing RoleModelMapping structure...")
    
    # Create a RoleModelConfig
    config = RoleModelConfig(
        model_name="test-model",
        provider="test-provider",
        max_tokens=1000,
        temperature=0.7
    )
    
    # Create a RoleModelMapping
    mapping = RoleModelMapping(
        role_name="test-role",
        role_model_config=config,
        priority=1
    )
    
    print(f"Mapping type: {type(mapping)}")
    print(f"Mapping attributes: {dir(mapping)}")
    print(f"Mapping dict: {mapping.__dict__}")
    
    # Check specific attributes
    print(f"Has role_model_config: {hasattr(mapping, 'role_model_config')}")
    if hasattr(mapping, 'role_model_config'):
        print(f"role_model_config type: {type(mapping.role_model_config)}")
        print(f"role_model_config.model_name: {mapping.role_model_config.model_name}")
    
    print(f"Has model_config: {hasattr(mapping, 'model_config')}")
    if hasattr(mapping, 'model_config'):
        print(f"model_config type: {type(mapping.model_config)}")
        if hasattr(mapping.model_config, 'model_name'):
            print(f"model_config.model_name: {mapping.model_config.model_name}")
        else:
            print(f"model_config content: {mapping.model_config}")
    
    # Try to access the attributes that TUI code is trying to access
    try:
        model_name = mapping.role_model_config.model_name
        print(f"SUCCESS: mapping.role_model_config.model_name = {model_name}")
    except AttributeError as e:
        print(f"ERROR accessing role_model_config.model_name: {e}")
    
    try:
        model_name = mapping.model_config.model_name
        print(f"mapping.model_config.model_name = {model_name}")
    except AttributeError as e:
        print(f"ERROR accessing model_config.model_name: {e}")


if __name__ == "__main__":
    test_mapping_structure()