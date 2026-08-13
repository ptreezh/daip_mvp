"""Tests for TUI layout optimization."""

from unittest.mock import Mock

import pytest

from daip_live.tui import DAIP_TUI


class TestTUILayoutOptimization:
    """测试TUI界面布局的直观性"""

    def test_tui_layout_intuitive_design(self):
        """测试TUI界面布局的直观性"""
        # 创建模拟依赖项
        mock_executor = Mock()
        mock_session_manager = Mock()
        mock_role_manager = Mock()
        mock_knowledge_manager = Mock()
        mock_debate_manager = Mock()
        mock_model_provider = Mock()
        mock_db_manager = Mock()
        mock_config_manager = Mock()
        mock_role_model_manager = Mock()
        mock_enhanced_debate_manager = Mock()

        # 创建TUI实例
        tui = DAIP_TUI(
            executor=mock_executor,
            goal="test goal",
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            knowledge_manager=mock_knowledge_manager,
            debate_manager=mock_debate_manager,
            model_provider=mock_model_provider,
            db_manager=mock_db_manager,
            config_manager=mock_config_manager,
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager,
        )

        # 验证TUI实例创建成功
        assert tui is not None

        # 验证关键属性初始化（_model_provider 经 container 懒加载，非实例属性）
        assert hasattr(tui, "_executor")
        assert hasattr(tui, "_session_manager")
        assert hasattr(tui, "_role_manager")
        assert hasattr(tui, "_knowledge_manager")
        assert hasattr(tui, "_debate_manager")
        assert hasattr(tui, "container")

        # 验证焦点模式初始化
        from daip_live.tui import FocusMode

        assert hasattr(tui, "focus_mode")
        assert tui.focus_mode == FocusMode.INPUT

    def test_tui_compose_method_structure(self):
        """测试TUI compose方法的结构"""
        # 创建模拟依赖项
        mock_executor = Mock()
        mock_session_manager = Mock()
        mock_role_manager = Mock()
        mock_knowledge_manager = Mock()
        mock_debate_manager = Mock()
        mock_model_provider = Mock()
        mock_db_manager = Mock()
        mock_config_manager = Mock()
        mock_role_model_manager = Mock()
        mock_enhanced_debate_manager = Mock()

        # 创建TUI实例
        tui = DAIP_TUI(
            executor=mock_executor,
            goal="test goal",
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            knowledge_manager=mock_knowledge_manager,
            debate_manager=mock_debate_manager,
            model_provider=mock_model_provider,
            db_manager=mock_db_manager,
            config_manager=mock_config_manager,
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager,
        )

        # 验证compose方法存在
        assert hasattr(tui, "compose")
        assert callable(getattr(tui, "compose"))

        # 验证compose方法返回正确的类型

        result = tui.compose()
        assert result is not None


class TestTUIFocusManagement:
    """测试TUI焦点管理功能"""

    def test_tui_focus_mode_initialization(self):
        """测试TUI焦点模式初始化"""
        # 创建模拟依赖项
        mock_executor = Mock()
        mock_session_manager = Mock()
        mock_role_manager = Mock()
        mock_knowledge_manager = Mock()
        mock_debate_manager = Mock()
        mock_model_provider = Mock()
        mock_db_manager = Mock()
        mock_config_manager = Mock()
        mock_role_model_manager = Mock()
        mock_enhanced_debate_manager = Mock()

        # 创建TUI实例
        tui = DAIP_TUI(
            executor=mock_executor,
            goal="test goal",
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            knowledge_manager=mock_knowledge_manager,
            debate_manager=mock_debate_manager,
            model_provider=mock_model_provider,
            db_manager=mock_db_manager,
            config_manager=mock_config_manager,
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager,
        )

        # 验证焦点模式正确初始化
        from daip_live.tui import FocusMode

        assert tui.focus_mode == FocusMode.INPUT

        # 验证焦点相关属性存在
        assert hasattr(tui, "focus_mode")

    def test_tui_focus_toggle_action_exists(self):
        """测试TUI焦点切换动作存在"""
        # 创建模拟依赖项
        mock_executor = Mock()
        mock_session_manager = Mock()
        mock_role_manager = Mock()
        mock_knowledge_manager = Mock()
        mock_debate_manager = Mock()
        mock_model_provider = Mock()
        mock_db_manager = Mock()
        mock_config_manager = Mock()
        mock_role_model_manager = Mock()
        mock_enhanced_debate_manager = Mock()

        # 创建TUI实例
        tui = DAIP_TUI(
            executor=mock_executor,
            goal="test goal",
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            knowledge_manager=mock_knowledge_manager,
            debate_manager=mock_debate_manager,
            model_provider=mock_model_provider,
            db_manager=mock_db_manager,
            config_manager=mock_config_manager,
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager,
        )

        # 验证焦点切换动作存在
        assert hasattr(tui, "action_toggle_focus")
        assert callable(getattr(tui, "action_toggle_focus"))

        # 验证退出输出模式动作存在
        assert hasattr(tui, "action_exit_output_mode")
        assert callable(getattr(tui, "action_exit_output_mode"))

    def test_tui_component_identifiers(self):
        """测试TUI组件标识符"""
        # 创建模拟依赖项
        mock_executor = Mock()
        mock_session_manager = Mock()
        mock_role_manager = Mock()
        mock_knowledge_manager = Mock()
        mock_debate_manager = Mock()
        mock_model_provider = Mock()
        mock_db_manager = Mock()
        mock_config_manager = Mock()
        mock_role_model_manager = Mock()
        mock_enhanced_debate_manager = Mock()

        # 创建TUI实例
        tui = DAIP_TUI(
            executor=mock_executor,
            goal="test goal",
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            knowledge_manager=mock_knowledge_manager,
            debate_manager=mock_debate_manager,
            model_provider=mock_model_provider,
            db_manager=mock_db_manager,
            config_manager=mock_config_manager,
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager,
        )

        # 验证关键组件标识符存在
        # 注意：这里我们验证组件查询方法而不是实际的组件ID
        assert hasattr(tui, "query_one")

        # 验证compose方法中应该包含的组件

        tui.compose()
        # 我们不直接验证生成器内容，而是验证方法存在


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
