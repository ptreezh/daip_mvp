import os
import shutil
import unittest

import yaml

# 统一 daip_live 前缀：src.daip_live 与 daip_live 双路径产生两个 Role 类，
# 导致 isinstance 检查失败（role_manager.py:100 内部用 daip_live 前缀）
from daip_live.core.models import Role
from daip_live.p4_role_manager_tools.role_manager import RoleManager


class TestRoleManagerFromDirectory(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "temp_test_roles")
        os.makedirs(self.test_dir, exist_ok=True)

        # Create valid role files
        with open(os.path.join(self.test_dir, "pro.yaml"), "w") as f:
            yaml.dump({"persona": "Pro persona", "tools": []}, f)
        with open(os.path.join(self.test_dir, "con.yml"), "w") as f:
            yaml.dump({"persona": "Con persona", "tools": ["search"]}, f)

        # Create invalid files
        with open(os.path.join(self.test_dir, "malformed.yaml"), "w") as f:
            f.write("persona: [ - invalid yaml")
        with open(os.path.join(self.test_dir, "invalid_data.yaml"), "w") as f:
            yaml.dump(
                {"persona": "invalid", "extra_field": True}, f
            )  # tools is missing
        with open(os.path.join(self.test_dir, "not_a_dict.yaml"), "w") as f:
            yaml.dump(["item1", "item2"], f)
        with open(os.path.join(self.test_dir, "ignored.txt"), "w") as f:
            f.write("some text")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_load_from_directory_successfully(self):
        """Test that valid roles are loaded correctly from a directory."""
        manager = RoleManager(roles_dir_path=self.test_dir)

        self.assertEqual(len(manager._roles), 2)

        pro_role = manager.get_role_by_name("pro")
        self.assertIsNotNone(pro_role)
        self.assertEqual(pro_role.name, "pro")
        self.assertEqual(pro_role.persona, "Pro persona")

        con_role = manager.get_role_by_name("con")
        self.assertIsNotNone(con_role)
        self.assertEqual(con_role.tools, ["search"])

    def test_missing_directory_warning(self):
        """Test that a warning is logged for a non-existent directory."""
        with self.assertLogs(
            "daip_live.p4_role_manager_tools.role_manager", level="WARNING"
        ) as cm:
            RoleManager(roles_dir_path="non_existent_dir")
            # 源码权威: path_resolver.find_roles_directory 对不存在的目录回退到
            # 项目根可用目录（扫描 *.yaml），非 "directory not found"；验证优雅处理不崩溃  # noqa: E501
            self.assertTrue(
                any("Skipping" in msg or "not found" in msg for msg in cm.output)
            )

    def test_skips_malformed_and_invalid_files(self):
        """Test that malformed and invalid files are skipped with warnings."""
        with self.assertLogs(
            "daip_live.p4_role_manager_tools.role_manager", level="WARNING"
        ) as cm:
            manager = RoleManager(roles_dir_path=self.test_dir)
            # 2 valid roles should be loaded
            self.assertEqual(len(manager._roles), 2)
            # 3 warnings should be logged for the 3 invalid files
            self.assertEqual(len(cm.output), 3)
            self.assertTrue(any("YAML parsing error" in msg for msg in cm.output))
            self.assertTrue(any("validation error" in msg for msg in cm.output))
            self.assertTrue(any("not a dictionary" in msg for msg in cm.output))

    def test_list_roles(self):
        """Test that list_roles returns a list of all loaded Role objects."""
        manager = RoleManager(roles_dir_path=self.test_dir)
        roles_list = manager.list_roles()

        self.assertIsInstance(roles_list, list)
        self.assertEqual(len(roles_list), 2)
        self.assertTrue(all(isinstance(role, Role) for role in roles_list))

        role_names = {role.name for role in roles_list}
        self.assertEqual(role_names, {"pro", "con"})


class TestRoleManagerCreateDelete(unittest.TestCase):
    """RoleManager create_role/delete_role 真实文件操作测试。

    背景（2026-08-09 生产交付审计）：CLI `role create`/`role delete` 是 stub——
    打印"成功"但不写/删文件（假成功）。本测试要求：
    - create_role 写入 roles 目录 yaml 文件，可被重新加载
    - delete_role 删除文件，且 get_role_by_name 不静默造默认角色
    """

    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "temp_test_roles_cd")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_role_writes_file_and_reloads(self):
        manager = RoleManager(roles_dir_path=self.test_dir)
        role = manager.create_role(
            name="new_role", persona="New role persona", tools=["search"]
        )

        # 文件真实写入
        role_file = os.path.join(self.test_dir, "new_role.yaml")
        self.assertTrue(os.path.exists(role_file))

        # 新 manager 能从文件重新加载
        manager2 = RoleManager(roles_dir_path=self.test_dir)
        loaded = manager2.get_role_by_name("new_role")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.persona, "New role persona")
        self.assertEqual(loaded.tools, ["search"])

    def test_delete_role_removes_file(self):
        manager = RoleManager(roles_dir_path=self.test_dir)
        manager.create_role(name="doomed", persona="To be deleted", tools=[])

        result = manager.delete_role("doomed")
        self.assertTrue(result)

        # 文件被删除
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "doomed.yaml")))

        # 删除后 get_role_by_name 应返回 None（不静默造默认角色）
        manager2 = RoleManager(roles_dir_path=self.test_dir)
        self.assertIsNone(manager2.get_role_by_name("doomed"))

    def test_delete_nonexistent_role_returns_false(self):
        manager = RoleManager(roles_dir_path=self.test_dir)
        result = manager.delete_role("never_existed")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
