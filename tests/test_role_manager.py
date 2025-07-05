import os
import shutil
import tempfile
from unittest import TestCase, main

from src.core_services.role_manager import Role, RoleManager

# Dummy YAML content for testing
DUMMY_ROLES_YAML = """
- id: "test_researcher"
  name: "Test Researcher"
  description: "A test role for research."
  system_prompt: "You are a test researcher."
  capabilities:
    - "test_research"
    - "test_analysis"

- id: "test_writer"
  name: "Test Writer"
  description: "A test role for writing."
  system_prompt: "You are a test writer."
  capabilities:
    - "test_writing"
"""

MALFORMED_YAML = """
- id: "bad_role"
  name: "Bad"
  description: "This YAML is missing a colon"
  system_prompt "This will fail"
"""


class TestRoleManager(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "roles.yaml")

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_load_roles_successfully(self):
        # Create a dummy config file
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(DUMMY_ROLES_YAML)

        role_manager = RoleManager(config_path=self.config_path)

        # Test list_roles
        roles = role_manager.list_roles()
        self.assertEqual(len(roles), 2)

        # Test get_role_by_id
        researcher_role = role_manager.get_role_by_id("test_researcher")
        self.assertIsNotNone(researcher_role)
        self.assertIsInstance(researcher_role, Role)
        self.assertEqual(researcher_role.name, "Test Researcher")
        self.assertEqual(researcher_role.capabilities, ["test_research", "test_analysis"])

        writer_role = role_manager.get_role_by_id("test_writer")
        self.assertIsNotNone(writer_role)
        self.assertEqual(writer_role.system_prompt, "You are a test writer.")

    def test_get_nonexistent_role(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(DUMMY_ROLES_YAML)

        role_manager = RoleManager(config_path=self.config_path)
        role = role_manager.get_role_by_id("nonexistent_role")
        self.assertIsNone(role)

    def test_init_with_nonexistent_file(self):
        role_manager = RoleManager(config_path="nonexistent/path/to/roles.yaml")
        self.assertEqual(len(role_manager.list_roles()), 0)

    def test_init_with_malformed_yaml(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(MALFORMED_YAML)

        role_manager = RoleManager(config_path=self.config_path)
        self.assertEqual(len(role_manager.list_roles()), 0)

    def test_init_with_empty_yaml(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("")  # Empty file

        role_manager = RoleManager(config_path=self.config_path)
        self.assertEqual(len(role_manager.list_roles()), 0)


if __name__ == "__main__":
    main()