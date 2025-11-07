#!/usr/bin/env python3
"""Test script to debug the model_name error"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

def test_role_mappings():
    """Test role model mappings"""
    print("Testing RoleModelManager...")

    manager = RoleModelManager()

    # Test basic role loading
    roles = manager.list_roles()
    print(f"Available roles: {[r.name for r in roles]}")

    # Test debate mappings
    role_names = ['pro_arguer', 'con_arguer']
    print(f"\nTesting debate mappings for: {role_names}")

    mappings = manager.get_debate_model_mappings(role_names)
    print(f"Got {len(mappings)} mappings")

    for i, mapping in enumerate(mappings):
        print(f"\nMapping {i}:")
        print(f"  Type: {type(mapping)}")
        print(f"  Has role_name: {hasattr(mapping, 'role_name')}")

        if hasattr(mapping, 'role_name'):
            print(f"  Role name: {mapping.role_name}")

        print(f"  Has role_model_config: {hasattr(mapping, 'role_model_config')}")

        if hasattr(mapping, 'role_model_config'):
            config = mapping.role_model_config
            print(f"  Config type: {type(config)}")
            print(f"  Has model_name: {hasattr(config, 'model_name')}")

            if hasattr(config, 'model_name'):
                print(f"  Model name: {config.model_name}")
            else:
                print(f"  Config attributes: {dir(config)}")
                print(f"  Config dict: {config.__dict__ if hasattr(config, '__dict__') else 'No __dict__'}")
        else:
            print(f"  Mapping attributes: {dir(mapping)}")
            print(f"  Mapping dict: {mapping.__dict__ if hasattr(mapping, '__dict__') else 'No __dict__'}")

if __name__ == "__main__":
    test_role_mappings()