import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase, main

from src.core_services.role_manager import Role, RoleManager

# Dummy JSON content for testing individual role files
TEST_RESEARCHER_JSON = {
    "id": "test_researcher",
    "name": "Test Researcher",
    "description": "A test role for research.",
    "system_prompt": "You are a test researcher.",
    "capabilities": ["test_research", "test_analysis"]
}

TEST_WRITER_JSON = {
    "id": "test_writer",
    "name": "Test Writer",
    "description": "A test role for writing.",
    "system_prompt": "You are a test writer.",
    "capabilities": ["test_writing"]
}

MALFORMED_JSON = """
{
    "id": "bad_role",
    "name": "Bad",
    "description": "This JSON is malformed",
    "system_prompt": "This will fail"
    // Missing comma and invalid comment
}
"""


class TestRoleManager(TestCase):
    def setUp(self):
        # Create a temporary directory for role JSON files
        self.test_dir = tempfile.mkdtemp()
        self.roles_directory = Path(self.test_dir)

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_load_roles_successfully(self):
        # Create individual JSON role files
        researcher_file = self.roles_directory / "test_researcher.json"
        writer_file = self.roles_directory / "test_writer.json"
        
        with open(researcher_file, "w", encoding="utf-8") as f:
            json.dump(TEST_RESEARCHER_JSON, f)
        
        with open(writer_file, "w", encoding="utf-8") as f:
            json.dump(TEST_WRITER_JSON, f)

        role_manager = RoleManager(roles_directory=self.roles_directory)

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
        # Create a role file to ensure the manager is working
        researcher_file = self.roles_directory / "test_researcher.json"
        with open(researcher_file, "w", encoding="utf-8") as f:
            json.dump(TEST_RESEARCHER_JSON, f)

        role_manager = RoleManager(roles_directory=self.roles_directory)
        role = role_manager.get_role_by_id("nonexistent_role")
        self.assertIsNone(role)

    def test_init_with_nonexistent_directory(self):
        nonexistent_path = Path("nonexistent/path/to/roles")
        role_manager = RoleManager(roles_directory=nonexistent_path)
        self.assertEqual(len(role_manager.list_roles()), 0)

    def test_init_with_malformed_json(self):
        # Create a malformed JSON file
        bad_role_file = self.roles_directory / "bad_role.json"
        with open(bad_role_file, "w", encoding="utf-8") as f:
            f.write(MALFORMED_JSON)

        role_manager = RoleManager(roles_directory=self.roles_directory)
        # Should load 0 roles due to malformed JSON
        self.assertEqual(len(role_manager.list_roles()), 0)

    def test_init_with_empty_directory(self):
        # Use empty directory (already created in setUp)
        role_manager = RoleManager(roles_directory=self.roles_directory)
        self.assertEqual(len(role_manager.list_roles()), 0)


if __name__ == "__main__":
    main()