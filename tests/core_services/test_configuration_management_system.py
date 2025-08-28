import unittest
import os
import shutil
import yaml

from src.core_services.configuration_management_system import ConfigurationManager, Environment

class TestConfigurationManagementSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_config_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        self.config_file = os.path.join(self.test_dir, "config.yaml")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_dummy_config(self, content: dict):
        with open(self.config_file, "w") as f:
            yaml.dump(content, f)

    def test_load_configuration(self):
        dummy_content = {"app": {"name": "TestApp", "version": "1.0"}, "db": {"host": "localhost"}}
        self._create_dummy_config(dummy_content)

        system = ConfigurationManager(environment=Environment.DEVELOPMENT)
        system.load_config_from_file(self.config_file)

        self.assertEqual(system.get("app.name"), "TestApp")
        self.assertEqual(system.get("db.host"), "localhost")
        self.assertEqual(system.get("app.version"), "1.0")

    def test_save_configuration(self):
        initial_content = {"setting1": "value1"}
        self._create_dummy_config(initial_content)

        system = ConfigurationManager(environment=Environment.DEVELOPMENT)
        system.load_config_from_file(self.config_file)

        system.set("setting2", "value2")
        system.save_config(self.config_file)

        with open(self.config_file, "r") as f:
            loaded_content = yaml.safe_load(f)
        self.assertEqual(loaded_content["setting1"], "value1")
        self.assertEqual(loaded_content["setting2"], "value2")

    def test_get_setting(self):
        dummy_content = {"level1": {"level2": {"key": "value"}}, "another_key": 123}
        self._create_dummy_config(dummy_content)

        system = ConfigurationManager(environment=Environment.DEVELOPMENT)
        system.load_config_from_file(self.config_file)

        self.assertEqual(system.get("level1.level2.key"), "value")
        self.assertEqual(system.get("another_key"), 123)
        self.assertIsNone(system.get("non_existent_key"))
        self.assertEqual(system.get("non_existent_key", "default_val"), "default_val")

if __name__ == "__main__":
    unittest.main()
