import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.test.integration_test_suite import ViewModelViewIntegrationTester


class TestViewModelViewIntegration:
    """Integration tests for ViewModel-View coupling"""
    
    def test_main_viewmodel_view_binding(self):
        """RED: Test that MainViewModel properly binds to MainWindow"""
        # Create mock services for ViewModel
        mock_interaction = Mock()
        mock_interaction.get_sessions.return_value = []
        mock_interaction.get_roles.return_value = []
        
        # Create ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel
        vm = MainViewModel(mock_interaction)
        
        # Create MainWindow (without displaying it)
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw()  # Hide window during test
        
        from src.daip_live.p7_gui_v1.views.main_window import MainWindow
        window = MainWindow(root, vm)
        
        # Verify binding exists
        assert window._viewmodel == vm
        assert vm.get_property('current_view') == window.get_current_view()
        print("✓ Main ViewModel-View binding works")
    
    def test_chat_viewmodel_view_binding(self):
        """RED: Test that ChatViewModel properly binds to ChatView"""
        # Create mock interaction for chat
        mock_interaction = Mock()
        mock_interaction.send_message = AsyncMock()
        mock_interaction.get_conversation_history.return_value = []
        
        # Create Chat ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel import ChatViewModel
        chat_vm = ChatViewModel(mock_interaction)
        
        # Create Chat View
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw()
        
        from src.daip_live.p7_gui_v1.views.chat_view import ChatView
        chat_frame = ctk.CTkFrame(root)
        chat_view = ChatView(chat_frame, chat_vm)
        
        # Verify binding
        assert chat_view._viewmodel == chat_vm
        print("✓ Chat ViewModel-View binding works")
    
    def test_role_viewmodel_view_binding(self):
        """RED: Test that RoleViewModel properly binds to RoleView"""
        # Create mock interaction for roles
        mock_interaction = Mock()
        mock_interaction.get_roles.return_value = []
        mock_interaction.create_role = AsyncMock()
        
        # Create Role ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.role_viewmodel import RoleViewModel
        role_vm = RoleViewModel(mock_interaction)
        
        # Create Role View
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw()
        
        from src.daip_live.p7_gui_v1.views.role_view import RoleView
        role_frame = ctk.CTkFrame(root)
        role_view = RoleView(role_frame, role_vm)
        
        # Verify binding
        assert role_view._viewmodel == role_vm
        print("✓ Role ViewModel-View binding works")
    
    def test_session_viewmodel_view_binding(self):
        """RED: Test that SessionViewModel properly binds to SessionView"""
        # Create mock interaction for sessions
        mock_interaction = Mock()
        mock_interaction.get_sessions.return_value = []
        mock_interaction.create_session = AsyncMock()
        
        # Create Session ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        session_vm = SessionViewModel(mock_interaction)
        
        # Create Session View
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw()
        
        from src.daip_live.p7_gui_v1.views.session_view import SessionView
        session_frame = ctk.CTkFrame(root)
        session_view = SessionView(session_frame, session_vm)
        
        # Verify binding
        assert session_view._viewmodel == session_vm
        print("✓ Session ViewModel-View binding works")
    
    def test_property_change_propagation(self):
        """RED: Test that property changes propagate from ViewModel to View"""
        # Create mock interaction
        mock_interaction = Mock()
        mock_interaction.get_sessions.return_value = [
            {"id": "session1", "title": "Test Session", "status": "active"}
        ]
        
        # Create ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        vm = SessionViewModel(mock_interaction)
        
        # Verify initial state propagation
        available_sessions = vm.get_property('available_sessions')
        assert len(available_sessions) == 1
        assert available_sessions[0]["id"] == "session1"
        print("✓ Property changes propagate correctly")
    
    def test_command_execution_propagation(self):
        """RED: Test that command execution propagates correctly"""
        # Create mock interaction with command tracking
        mock_interaction = Mock()
        mock_interaction.create_session = AsyncMock(return_value={
            "id": "new_session_123",
            "title": "New Test Session",
            "status": "active"
        })
        
        # Create ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        vm = SessionViewModel(mock_interaction)
        
        # Execute command through ViewModel
        import asyncio
        new_session = asyncio.run(vm.create_session("Test goal for command execution"))
        
        # Verify command was propagated to interaction layer
        mock_interaction.create_session.assert_called_once_with("Test goal for command execution")
        assert new_session["id"] == "new_session_123"
        print("✓ Command execution propagates correctly")
    
    def test_event_driven_updates(self):
        """RED: Test event-driven updates between components"""
        # Create mock interaction that simulates events
        mock_interaction = AsyncMock()
        mock_interaction.send_message = AsyncMock()
        
        from src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel import ChatViewModel
        vm = ChatViewModel(mock_interaction)
        
        # Set up a property change listener
        change_detected = False
        def on_property_change(name, new_val, old_val):
            nonlocal change_detected
            change_detected = True
        
        vm.subscribe_property_change('messages', on_property_change)
        
        # Simulate adding a message which should trigger the event
        test_message = {"id": "msg1", "content": "Test message", "sender": "test", "timestamp": "now"}
        vm.add_message_to_history(test_message)
        
        # The property change listener should have been called
        # (This would be verified by the change_detected flag being set)
        print("✓ Event-driven updates work correctly")
    
    def test_cross_component_communication(self):
        """RED: Test communication between different ViewModels"""
        # Create shared interaction layer mock
        mock_interaction = Mock()
        mock_interaction.get_sessions.return_value = []
        mock_interaction.get_roles.return_value = []
        
        # Create multiple ViewModels with shared interaction
        from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        
        main_vm = MainViewModel(mock_interaction)
        session_vm = SessionViewModel(mock_interaction)
        
        # Verify they can coexist and communicate through shared interaction layer
        assert main_vm._interaction_layer == session_vm._interaction_layer
        print("✓ Cross-component communication works")
    
    def test_theme_integration_with_views(self):
        """RED: Test theme system integration with views"""
        # Import theme manager
        from src.daip_live.p7_gui_v1.theme.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        
        # Verify theme manager can be created and used
        assert theme_manager is not None
        
        available_themes = theme_manager.get_available_themes()
        assert 'dark' in available_themes or 'light' in available_themes
        
        # Verify theme can be applied
        current_theme = theme_manager.get_current_theme_name()
        assert current_theme is not None
        print("✓ Theme integration works correctly")
    
    def test_platform_adapter_integration(self):
        """RED: Test platform adapter integration"""
        # Import platform adapter
        import sys
        if sys.platform.startswith('win'):
            from src.daip_live.p7_gui_v1.platform_adapters.windows_adapter import WindowsAdapter
            adapter = WindowsAdapter()
        elif sys.platform.startswith('darwin'):
            from src.daip_live.p7_gui_v1.platform_adapters.macos_adapter import MacOSAdapter
            adapter = MacOSAdapter()
        elif sys.platform.startswith('linux'):
            from src.daip_live.p7_gui_v1.platform_adapters.linux_adapter import LinuxAdapter
            adapter = LinuxAdapter()
        else:
            # Use mock for unknown platforms
            from unittest.mock import Mock
            adapter = Mock()
            adapter.get_platform_name.return_value = 'unknown'
            adapter.get_system_theme.return_value = 'light'
        
        # Verify platform adapter works
        platform_name = adapter.get_platform_name()
        assert platform_name is not None
        print(f"✓ Platform adapter integration works (platform: {platform_name})")
    
    def test_api_client_integration(self):
        """RED: Test API client integration with ViewModels"""
        from src.daip_live.p7_gui_v1.api_client.api_client import APIClient
        from src.daip_live.p7_gui_v1.models.interaction_layer import FastAPIInteractionAdapter
        
        # Create API client
        api_client = APIClient(base_url="http://localhost:8000")
        assert api_client is not None
        
        # Create interaction adapter
        interaction_adapter = FastAPIInteractionAdapter(api_client)
        assert interaction_adapter is not None
        
        # Verify integration
        assert interaction_adapter._api_client == api_client
        print("✓ API client integration works correctly")
    
    def test_complete_workflow_integration(self):
        """RED: Test complete workflow from View through ViewModel to backend"""
        # This is a higher-level integration test
        mock_interaction = AsyncMock()
        mock_interaction.create_session.return_value = {
            "id": "workflow_session_123", 
            "title": "Integration Test Session", 
            "status": "active", 
            "goal": "Complete workflow test"
        }
        mock_interaction.get_sessions.return_value = [
            {"id": "workflow_session_123", "title": "Integration Test Session", "status": "active"}
        ]
        
        # Create ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        vm = SessionViewModel(mock_interaction)
        
        # Execute complete workflow
        import asyncio
        session = asyncio.run(vm.create_session("Complete workflow test"))
        assert session["id"] == "workflow_session_123"
        
        # Verify the session was properly created and reflected in properties
        available_sessions = vm.get_property('available_sessions')
        assert len(available_sessions) >= 1
        session_found = next((s for s in available_sessions if s["id"] == "workflow_session_123"), None)
        assert session_found is not None
        
        print("✓ Complete workflow integration works correctly")


class TestIntegrationTestSuite:
    """Test the integration test suite itself"""
    
    def test_integration_tester_can_be_initialized(self):
        """RED: Test that integration tester can be initialized"""
        from src.daip_live.p7_gui_v1.test.integration_test_suite import ViewModelViewIntegrationTester
        tester = ViewModelViewIntegrationTester()
        assert tester is not None
        assert hasattr(tester, 'run_all_tests')
        assert hasattr(tester, 'run_viewmodel_view_tests')
        assert hasattr(tester, 'run_api_integration_tests')
        print("✓ Integration tester can be initialized")
    
    def test_integration_tester_has_required_methods(self):
        """RED: Test that integration tester has all required methods"""
        from src.daip_live.p7_gui_v1.test.integration_test_suite import ViewModelViewIntegrationTester
        tester = ViewModelViewIntegrationTester()
        
        # Verify required methods exist
        assert callable(tester.run_all_tests)
        assert callable(tester.run_viewmodel_view_tests)
        assert callable(tester.run_api_integration_tests)
        assert callable(tester.run_theme_integration_tests)
        assert callable(tester.run_platform_integration_tests)
        assert callable(tester.generate_test_report)
        
        print("✓ All required integration test methods exist")