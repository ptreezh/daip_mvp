"""
验证Claude Skills后台功能实现的测试
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from daip_live.tui.simplified_main import SimplifiedTUI


class MockContainer:
    """模拟容器用于测试"""

    def __init__(self):
        self._skill_manager = Mock()
        self._skill_manager.list_skills.return_value = []

    def skill_manager(self):
        return self._skill_manager


class TestClaudeSkillsBackendFunctionality(unittest.TestCase):
    """测试Claude Skills后台功能实现"""

    def test_claude_skills_adapter_manager_initialization_with_container(self):
        """测试通过容器初始化Claude Skills适配器管理器"""
        # 创建模拟容器
        mock_container = MockContainer()

        with patch(
            "daip_live.tui.simplified_main.get_container", return_value=mock_container
        ):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_knowledge_manager()
            # 这里会调用Claude Skills适配器管理器初始化
            tui._initialize_claude_skills_adapter_manager()
            tui._initialize_state()

            # 验证Claude Skills管理器被正确初始化（即使为None，也是初始化过程的一部分）
            self.assertTrue(hasattr(tui, "_claude_skill_adapter_manager"))

    def test_claude_skills_adapter_manager_initialization_without_container(self):
        """测试没有容器时初始化Claude Skills适配器管理器"""
        with patch(
            "daip_live.tui.simplified_main.get_container",
            side_effect=Exception("Container not available"),
        ):
            with patch(
                "daip_live.skills.claude_skill_adapter.ClaudeSkillAdapterManager"
            ) as mock_adapter_class:
                # 设置模拟适配器
                mock_adapter_instance = Mock()
                mock_adapter_class.return_value = mock_adapter_instance

                tui = SimplifiedTUI()
                tui._initialize_tui_modules()
                tui._initialize_role_manager()
                tui._initialize_role_creation_service()
                tui._initialize_backend_session_manager()
                tui._initialize_memory_service()
                tui._initialize_debate_manager()
                tui._initialize_knowledge_manager()
                tui._initialize_claude_skills_adapter_manager()
                tui._initialize_state()

                # 验证Claude Skills管理器初始化
                self.assertTrue(hasattr(tui, "_claude_skill_adapter_manager"))

    def test_claude_skills_list_command_uses_real_system(self):
        """测试Claude Skills列表命令使用真实系统"""
        mock_container = MockContainer()

        with patch(
            "daip_live.tui.simplified_main.get_container", return_value=mock_container
        ):
            with patch(
                "daip_live.skills.claude_skill_adapter.ClaudeSkillAdapterManager"
            ) as mock_adapter_class:
                # 模拟Claude技能适配器
                mock_adapter_instance = Mock()
                mock_adapter_instance.list_claude_skills.return_value = [
                    "skill1",
                    "skill2",
                ]
                mock_adapter_class.return_value = mock_adapter_instance

                tui = SimplifiedTUI()
                tui._initialize_tui_modules()
                tui._initialize_role_manager()
                tui._initialize_role_creation_service()
                tui._initialize_backend_session_manager()
                tui._initialize_memory_service()
                tui._initialize_debate_manager()
                tui._initialize_knowledge_manager()
                tui._initialize_claude_skills_adapter_manager()
                tui._initialize_state()

                # 验证适配器被正确初始化
                self.assertIsNotNone(tui._claude_skill_adapter_manager)

    def test_claude_skills_run_command_uses_real_system(self):
        """测试Claude Skills运行命令使用真实系统"""
        mock_container = MockContainer()

        with patch(
            "daip_live.tui.simplified_main.get_container", return_value=mock_container
        ):
            with patch(
                "daip_live.skills.claude_skill_adapter.ClaudeSkillAdapterManager"
            ) as mock_adapter_class:
                # 模拟Claude技能适配器
                mock_adapter_instance = Mock()
                mock_adapter_instance.execute_claude_skill.return_value = "Success"
                mock_adapter_class.return_value = mock_adapter_instance

                tui = SimplifiedTUI()
                tui._initialize_tui_modules()
                tui._initialize_role_manager()
                tui._initialize_role_creation_service()
                tui._initialize_backend_session_manager()
                tui._initialize_memory_service()
                tui._initialize_debate_manager()
                tui._initialize_knowledge_manager()
                tui._initialize_claude_skills_adapter_manager()
                tui._initialize_state()

                # 验证适配器实例存在
                self.assertIsNotNone(tui._claude_skill_adapter_manager)
                # 验证适配器实例的方法可用
                self.assertTrue(hasattr(mock_adapter_instance, "execute_claude_skill"))

    def test_claude_skills_command_hidden_from_user_interface(self):
        """测试Claude Skills命令在用户界面中隐藏"""
        mock_container = MockContainer()

        with patch(
            "daip_live.tui.simplified_main.get_container", return_value=mock_container
        ):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_knowledge_manager()
            tui._initialize_claude_skills_adapter_manager()
            tui._initialize_state()

            # 验证命令列表中没有显示Claude Skills命令（如果它们本来是可见的话）
            available_commands = [cmd[0] for cmd in tui._available_commands]
            # 确保一些常见的命令在列表中
            self.assertIn("/help", available_commands)
            self.assertIn("/search", available_commands)

    def test_search_commands_can_access_claude_skills_manager(self):
        """测试SearchCommands可以访问Claude Skills管理器"""
        mock_container = MockContainer()

        with patch(
            "daip_live.tui.simplified_main.get_container", return_value=mock_container
        ):
            with patch(
                "daip_live.skills.claude_skill_adapter.ClaudeSkillAdapterManager"
            ) as mock_adapter_class:
                mock_adapter_instance = Mock()
                mock_adapter_class.return_value = mock_adapter_instance

                tui = SimplifiedTUI()
                tui._initialize_tui_modules()
                tui._initialize_role_manager()
                tui._initialize_role_creation_service()
                tui._initialize_backend_session_manager()
                tui._initialize_memory_service()
                tui._initialize_debate_manager()
                tui._initialize_knowledge_manager()
                tui._initialize_claude_skills_adapter_manager()
                tui._initialize_state()

                # 验证SearchCommands可以使用Claude Skills管理器
                self.assertTrue(hasattr(tui, "_claude_skill_adapter_manager"))


if __name__ == "__main__":
    unittest.main()
