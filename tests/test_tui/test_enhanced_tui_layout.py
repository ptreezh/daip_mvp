"""Tests for enhanced TUI layout optimization."""

import pytest
from unittest.mock import Mock, patch

from daip_live.tui_enhanced import EnhancedDAIP_TUI


class TestEnhancedTUILayout:
    """测试增强版TUI界面布局"""

    def test_enhanced_tui_layout_structure(self):
        """测试增强版TUI布局结构"""
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
        
        # 创建增强版TUI实例
        tui = EnhancedDAIP_TUI(
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
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        # 验证TUI实例创建成功
        assert tui is not None
        
        # 验证关键属性初始化
        assert hasattr(tui, '_executor')
        assert hasattr(tui, '_session_manager')
        assert hasattr(tui, '_role_manager')
        assert hasattr(tui, '_knowledge_manager')
        assert hasattr(tui, '_debate_manager')
        assert hasattr(tui, '_model_provider')
        
        # 验证焦点模式初始化
        from daip_live.tui_enhanced import FocusMode
        assert hasattr(tui, 'focus_mode')
        assert tui.focus_mode == FocusMode.INPUT

    def test_enhanced_tui_compose_method(self):
        """测试增强版TUI compose方法"""
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
        
        # 创建增强版TUI实例
        tui = EnhancedDAIP_TUI(
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
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        # 验证compose方法存在
        assert hasattr(tui, 'compose')
        assert callable(getattr(tui, 'compose'))
        
        # 验证compose方法返回正确的类型
        from textual.app import ComposeResult
        result = tui.compose()
        assert result is not None

    def test_enhanced_tui_focus_management(self):
        """测试增强版TUI焦点管理"""
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
        
        # 创建增强版TUI实例
        tui = EnhancedDAIP_TUI(
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
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        # 验证焦点模式正确初始化
        from daip_live.tui_enhanced import FocusMode
        assert tui.focus_mode == FocusMode.INPUT
        
        # 验证焦点相关动作存在
        assert hasattr(tui, 'action_toggle_focus')
        assert callable(getattr(tui, 'action_toggle_focus'))
        
        assert hasattr(tui, 'action_exit_output_mode')
        assert callable(getattr(tui, 'action_exit_output_mode'))

    def test_enhanced_tui_component_identifiers(self):
        """测试增强版TUI组件标识符"""
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
        
        # 创建增强版TUI实例
        tui = EnhancedDAIP_TUI(
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
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        # 验证关键组件查询方法存在
        assert hasattr(tui, 'query_one')

    @patch('daip_live.tui_enhanced.Header')
    @patch('daip_live.tui_enhanced.RichLog')
    @patch('daip_live.tui_enhanced.Input')
    @patch('daip_live.tui_enhanced.Static')
    @patch('daip_live.tui_enhanced.Footer')
    @patch('daip_live.tui_enhanced.Vertical')
    @patch('daip_live.tui_enhanced.Horizontal')
    def test_enhanced_tui_layout_components(
        self, 
        mock_horizontal,
        mock_vertical,
        mock_footer, 
        mock_static, 
        mock_input, 
        mock_richlog, 
        mock_header
    ):
        """测试增强版TUI布局组件"""
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
        
        # 创建增强版TUI实例
        tui = EnhancedDAIP_TUI(
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
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        # 验证compose方法可以调用
        from textual.app import ComposeResult
        result = list(tui.compose())
        
        # 验证组件被创建（通过模拟对象）
        assert mock_header.called
        assert mock_vertical.called
        assert mock_horizontal.called
        assert mock_richlog.called
        assert mock_input.called
        assert mock_static.called
        assert mock_footer.called


class TestEnhancedTUIFunctionality:
    """测试增强版TUI功能"""

    def test_enhanced_tui_bindings(self):
        """测试增强版TUI快捷键绑定"""
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
        
        # 创建增强版TUI实例
        tui = EnhancedDAIP_TUI(
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
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        # 验证BINDINGS属性存在
        assert hasattr(tui, 'BINDINGS')
        assert isinstance(tui.BINDINGS, list)
        
        # 验证关键快捷键绑定存在
        bindings = [str(binding.key) for binding in tui.BINDINGS]
        assert "ctrl+tab" in bindings
        assert "ctrl+a" in bindings
        assert "ctrl+c" in bindings
        assert "ctrl+e" in bindings
        assert "escape" in bindings

    def test_enhanced_tui_focus_modes(self):
        """测试增强版TUI焦点模式"""
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
        
        # 创建增强版TUI实例
        tui = EnhancedDAIP_TUI(
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
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        # 验证焦点模式枚举存在
        from daip_live.tui_enhanced import FocusMode
        assert FocusMode.INPUT is not None
        assert FocusMode.OUTPUT is not None
        
        # 验证默认焦点模式
        assert tui.focus_mode == FocusMode.INPUT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])