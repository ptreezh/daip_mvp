#!/usr/bin/env python3
"""Personal Intelligence Hub - Main App Tests

测试主应用入口点和基本功能
"""

from unittest.mock import Mock, patch

import pytest

from personal_intelligence_hub.main_app import IndexView, PersonalIntelligenceHubView, app


class TestMainApp:
    """主应用测试类"""
    
    def test_app_initialization(self):
        """测试应用初始化"""
        assert app is not None
        assert hasattr(app, 'settings')
        assert hasattr(app, 'routes')
    
    def test_routes_configuration(self):
        """测试路由配置"""
        routes = app.routes
        assert len(routes) >= 2  # 至少有index和hub路由


class TestPersonalIntelligenceHubView:
    """Personal Intelligence Hub视图测试类"""
    
    @patch('personal_intelligence_hub.services.personal_assistant.PersonalAssistantService')
    def test_view_initialization(self, mock_assistant_service):
        """测试视图初始化"""
        mock_assistant_service.return_value = Mock()
        
        view = PersonalIntelligenceHubView()
        assert view.assistant_service is not None
        assert view.chat_interface is None  # 延迟初始化
    
    @patch('personal_intelligence_hub.services.personal_assistant.PersonalAssistantService')
    def test_handle_request_components_initialization(self, mock_assistant_service):
        """测试请求处理时组件初始化"""
        mock_assistant_service.return_value = Mock()
        
        view = PersonalIntelligenceHubView()
        mock_request = Mock()
        
        html_response = view.handle_request(mock_request)
        
        # 验证组件已初始化
        assert view.chat_interface is not None
        assert view.transparency_monitor is not None
        assert view.wiki_panel is not None
        assert view.task_panel is not None
        
        # 验证HTML结构
        assert html_response is not None


class TestIndexView:
    """首页视图测试类"""
    
    def test_handle_request(self):
        """测试首页请求处理"""
        view = IndexView()
        mock_request = Mock()
        
        html_response = view.handle_request(mock_request)
        
        assert html_response is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])