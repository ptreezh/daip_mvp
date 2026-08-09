# ruff: noqa: E501
import unittest

from daip_live.p4_role_manager_tools.role_model_config import (
    EnhancedRole,
    RoleModelConfig,
)


class TestRoleYamlParsing(unittest.TestCase):
    """
    Test suite to diagnose issues with parsing role YAML data into EnhancedRole models.
    This test is designed to fail if the `debate_model_config` is not parsed correctly.
    """

    def test_enhanced_role_parses_debate_config_from_dict(self):
        """
        [GREEN] TDD Test: Validates that EnhancedRole correctly parses `debate_model_config`  # noqa: E501
        from a dictionary, simulating data loaded from a YAML file.
        """
        # This dictionary mimics the structure of pro_arguer.yaml
        mock_yaml_data = {
            "name": "pro_arguer",
            "persona": "A test persona.",
            "tools": [],
            "model_configs": [
                {
                    "model_name": "llama3:instruct",
                    "provider": "ollama",
                    "is_primary": True,
                }
            ],
            "debate_model_config": {
                "model_name": "llama3:instruct-debate",
                "provider": "ollama",
                "max_tokens": 3000,
                "temperature": 0.8,
            },
        }

        # --- Act ---
        # Attempt to create the EnhancedRole object from the dictionary
        role = EnhancedRole(**mock_yaml_data)

        # --- Assert ---
        # 1. Check that debate_model_config is not None
        self.assertIsNotNone(
            role.debate_model_config,
            "Validation failed: `debate_model_config` should be parsed and not be None.",  # noqa: E501
        )

        # 2. Check that it is the correct type
        self.assertIsInstance(
            role.debate_model_config,
            RoleModelConfig,
            f"Validation failed: `debate_model_config` should be an instance of RoleModelConfig, but got {type(role.debate_model_config)}.",  # noqa: E501
        )

        # 3. Check that the nested model_name is correct
        self.assertEqual(
            role.debate_model_config.model_name,
            "llama3:instruct-debate",
            "Validation failed: The model name within `debate_model_config` was not parsed correctly.",  # noqa: E501
        )
