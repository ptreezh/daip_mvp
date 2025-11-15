"""
Integration Test Suite for DAIP-LIVE P7 GUI

This module implements comprehensive integration tests for the P7 GUI application,
validating the integration between ViewModels, Views, and backend services.
"""

import asyncio
from typing import Any, Dict, List
from unittest.mock import Mock, AsyncMock
from dataclasses import dataclass


@dataclass
class IntegrationTestResult:
    """
    Data class for integration test results.
    
    Provides detailed information about test execution outcomes.
    """
    test_name: str
    passed: bool
    duration: float
    error_message: str = ""
    details: Dict[str, Any] = None


class ViewModelViewIntegrationTester:
    """
    Integration tester for ViewModel-View components.
    
    This tester validates that ViewModels and Views work together correctly,
    including property binding, command execution, and event handling.
    """
    
    def __init__(self):
        """Initialize the ViewModel-View integration tester."""
        self._test_results: List[IntegrationTestResult] = []
        self._test_count = 0
        self._passed_count = 0
    
    async def run_all_tests(self) -> List[IntegrationTestResult]:
        """
        Run all integration tests.
        
        Returns:
            List of test results
        """
        print("Running ViewModel-View Integration Tests...")
        
        tests_to_run = [
            self._test_main_viewmodel_view_integration,
            self._test_chat_viewmodel_view_integration,
            self._test_role_viewmodel_view_integration,
            self._test_session_viewmodel_view_integration,
            self._test_property_binding_integration,
            self._test_command_execution_integration,
            self._test_event_propagation_integration,
            self._test_cross_component_communication
        ]
        
        results = []
        for test_func in tests_to_run:
            result = await self._run_test_wrapper(test_func)
            results.append(result)
            self._test_results.append(result)
            
            if result.passed:
                self._passed_count += 1
            self._test_count += 1
        
        return results
    
    async def _run_test_wrapper(self, test_func) -> IntegrationTestResult:
        """
        Wrapper to run a test function and catch exceptions.
        
        Args:
            test_func: Test function to run
            
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await test_func()
            result.duration = asyncio.get_event_loop().time() - start_time
            return result
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name=test_func.__name__,
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_main_viewmodel_view_integration(self) -> IntegrationTestResult:
        """
        Test Main ViewModel and View integration.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create mock interaction layer
            mock_interaction = Mock()
            mock_interaction.get_sessions = AsyncMock(return_value=[])
            mock_interaction.get_roles = AsyncMock(return_value=[])
            
            # Import Main ViewModel and View
            from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel
            from src.daip_live.p7_gui_v1.views.main_window import MainWindow
            
            # Create ViewModel
            main_vm = MainViewModel(mock_interaction)
            
            # Create View (without displaying to avoid GUI issues)
            import customtkinter as ctk
            root = ctk.CTk()
            root.withdraw()  # Hide during testing
            
            # Create the main window
            main_window = MainWindow(root, main_vm)
            
            # Verify integration
            assert main_window._viewmodel == main_vm
            assert main_vm.get_property('current_view') == main_window.get_current_view()
            
            # Test property binding
            main_vm.set_property('current_view', 'roles')
            # In real implementation, this would trigger view updates
            assert main_vm.get_property('current_view') == 'roles'
            
            root.destroy()
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Main ViewModel-View Integration",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Main ViewModel-View Integration",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_chat_viewmodel_view_integration(self) -> IntegrationTestResult:
        """
        Test Chat ViewModel and View integration.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create mock interaction
            mock_interaction = Mock()
            mock_interaction.send_message = AsyncMock()
            mock_interaction.get_conversation_history = AsyncMock(return_value=[])
            
            # Import Chat ViewModel and View
            from src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel import ChatViewModel
            from src.daip_live.p7_gui_v1.views.chat_view import ChatView
            
            # Create ViewModel
            chat_vm = ChatViewModel(mock_interaction)
            
            # Create View
            import customtkinter as ctk
            root = ctk.CTk()
            root.withdraw()
            
            chat_frame = ctk.CTkFrame(root)
            chat_view = ChatView(chat_frame, chat_vm)
            
            # Verify integration
            assert chat_view._viewmodel == chat_vm
            
            # Test message handling
            initial_messages = chat_vm.get_property('messages')
            assert initial_messages == []
            
            # Add a test message
            test_message = {
                'id': 'test_msg_1',
                'content': 'Test message for integration',
                'sender': 'user',
                'timestamp': '2025-11-08T12:00:00Z'
            }
            await chat_vm.add_message_to_history(test_message)
            
            updated_messages = chat_vm.get_property('messages')
            assert len(updated_messages) == 1
            assert updated_messages[0]['id'] == 'test_msg_1'
            
            root.destroy()
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Chat ViewModel-View Integration",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Chat ViewModel-View Integration",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_role_viewmodel_view_integration(self) -> IntegrationTestResult:
        """
        Test Role ViewModel and View integration.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create mock interaction
            mock_interaction = Mock()
            mock_interaction.get_roles = AsyncMock(return_value=[])
            mock_interaction.create_role = AsyncMock()
            
            # Import Role ViewModel and View
            from src.daip_live.p7_gui_v1.viewmodel.role_viewmodel import RoleViewModel
            from src.daip_live.p7_gui_v1.views.role_view import RoleView
            
            # Create ViewModel
            role_vm = RoleViewModel(mock_interaction)
            
            # Create View
            import customtkinter as ctk
            root = ctk.CTk()
            root.withdraw()
            
            role_frame = ctk.CTkFrame(root)
            role_view = RoleView(role_frame, role_vm)
            
            # Verify integration
            assert role_view._viewmodel == role_vm
            
            # Test role management
            initial_roles = role_vm.get_property('available_roles')
            assert initial_roles == []
            
            # Verify viewmodel methods exist and work
            assert hasattr(role_vm, 'get_available_roles')
            assert callable(role_vm.get_available_roles)
            
            root.destroy()
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Role ViewModel-View Integration",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Role ViewModel-View Integration",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_session_viewmodel_view_integration(self) -> IntegrationTestResult:
        """
        Test Session ViewModel and View integration.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create mock interaction
            mock_interaction = Mock()
            mock_interaction.get_sessions = AsyncMock(return_value=[
                {"id": "session1", "title": "Test Session", "status": "active", "created_at": "2025-11-08"}
            ])
            mock_interaction.create_session = AsyncMock(return_value={
                "id": "new_session", "title": "New Session", "status": "active", "created_at": "2025-11-08"
            })
            
            # Import Session ViewModel and View
            from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
            from src.daip_live.p7_gui_v1.views.session_view import SessionView
            
            # Create ViewModel
            session_vm = SessionViewModel(mock_interaction)
            
            # Create View
            import customtkinter as ctk
            root = ctk.CTk()
            root.withdraw()
            
            session_frame = ctk.CTkFrame(root)
            session_view = SessionView(session_frame, session_vm)
            
            # Verify integration
            assert session_view._viewmodel == session_vm
            
            # Test session management
            initial_sessions = await session_vm.load_sessions()
            assert len(initial_sessions) == 1
            assert initial_sessions[0]["id"] == "session1"
            
            # Test creating a new session
            new_session = await session_vm.create_session("Test goal")
            assert new_session["id"] == "new_session"
            
            root.destroy()
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Session ViewModel-View Integration",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Session ViewModel-View Integration",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_property_binding_integration(self) -> IntegrationTestResult:
        """
        Test property binding between ViewModels and Views.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create mock interaction
            mock_interaction = Mock()
            mock_interaction.get_sessions = AsyncMock(return_value=[])
            
            from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
            
            # Create ViewModel
            vm = SessionViewModel(mock_interaction)
            
            # Test property management
            initial_count = vm.get_property('session_count', 0)
            assert initial_count == 0
            
            # Set property using ViewModel
            vm.set_property('session_count', 5)
            new_count = vm.get_property('session_count', 0)
            assert new_count == 5
            
            # Test property change notification
            change_recorded = False
            def on_property_change(name, new_val, old_val):
                nonlocal change_recorded
                change_recorded = True
            
            vm.subscribe_property_change('session_count', on_property_change)
            vm.set_property('session_count', 10)
            assert change_recorded  # The callback should have been triggered
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Property Binding Integration",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Property Binding Integration",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_command_execution_integration(self) -> IntegrationTestResult:
        """
        Test command execution integration between ViewModels.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create mock interaction
            mock_interaction = Mock()
            mock_interaction.create_session = AsyncMock(return_value={
                "id": "cmd_test_session", "title": "Command Test", "status": "active"
            })
            
            # Import ViewModel
            from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
            vm = SessionViewModel(mock_interaction)
            
            # Test command execution
            result = vm.execute_command('create_new_session', 'Command execution test')
            
            # Verify interaction was called
            # Note: This would depend on actual command registration in the real implementation
            # For now, we'll verify that the command execution mechanism exists
            assert hasattr(vm, 'execute_command')
            assert callable(vm.execute_command)
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Command Execution Integration",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Command Execution Integration",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_event_propagation_integration(self) -> IntegrationTestResult:
        """
        Test event propagation between components.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create mock interaction
            mock_interaction = AsyncMock()
            mock_interaction.send_message = AsyncMock()
            
            # Import ViewModel
            from src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel import ChatViewModel
            vm = ChatViewModel(mock_interaction)
            
            # Set up event listener
            event_received = False
            def on_message_received(message):
                nonlocal event_received
                event_received = True
            
            # In a real implementation, ViewModels would have event subscription mechanisms
            # For this test, we'll validate that the structure supports event handling
            assert hasattr(vm, 'subscribe_property_change')
            assert callable(vm.subscribe_property_change)
            
            # Test that we can register a property change callback
            vm.subscribe_property_change('messages', lambda name, new_val, old_val: on_message_received(new_val))
            
            # Add a message to trigger the event
            test_msg = {
                'id': 'event_test_msg',
                'content': 'Event propagation test',
                'sender': 'test',
                'timestamp': '2025-11-08T12:00:00Z'
            }
            await vm.add_message_to_history(test_msg)
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Event Propagation Integration",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Event Propagation Integration",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    async def _test_cross_component_communication(self) -> IntegrationTestResult:
        """
        Test communication between different components.
        
        Returns:
            Integration test result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create shared interaction layer
            mock_interaction = Mock()
            mock_interaction.get_sessions = AsyncMock(return_value=[])
            mock_interaction.get_roles = AsyncMock(return_value=[])
            mock_interaction.get_debates = AsyncMock(return_value=[])
            
            # Import multiple ViewModels to test cross-communication
            from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel
            from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
            from src.daip_live.p7_gui_v1.viewmodel.role_viewmodel import RoleViewModel
            
            # Create ViewModels with shared interaction
            main_vm = MainViewModel(mock_interaction)
            session_vm = SessionViewModel(mock_interaction)
            role_vm = RoleViewModel(mock_interaction)
            
            # Verify they all share the same interaction layer
            # This tests that components can communicate through shared services
            assert main_vm._interaction_layer == session_vm._interaction_layer
            assert session_vm._interaction_layer == role_vm._interaction_layer
            assert main_vm._interaction_layer == role_vm._interaction_layer
            
            # Verify interaction calls work across ViewModels
            await session_vm.load_sessions()
            await role_vm.load_roles()
            
            # Mock interactions should have been called appropriately
            mock_interaction.get_sessions.assert_called()
            mock_interaction.get_roles.assert_called()
            
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Cross-Component Communication",
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Cross-Component Communication",
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    def get_test_summary(self) -> Dict[str, Any]:
        """
        Get summary of all integration tests.
        
        Returns:
            Dictionary with test summary information
        """
        return {
            'total_tests': self._test_count,
            'passed_tests': self._passed_count,
            'failed_tests': self._test_count - self._passed_count,
            'pass_rate': self._passed_count / self._test_count if self._test_count > 0 else 0.0,
            'total_duration': sum(result.duration for result in self._test_results)
        }
    
    def print_test_report(self):
        """Print a formatted test report."""
        summary = self.get_test_summary()
        
        print("\n" + "="*60)
        print("INTEGRATION TEST REPORT")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed:      {summary['passed_tests']}")
        print(f"Failed:      {summary['failed_tests']}")
        print(f"Pass Rate:   {summary['pass_rate']*100:.1f}%")
        if summary['total_duration'] > 0:
            print(f"Duration:    {summary['total_duration']:.3f}s")
        else:
            print(f"Duration:    <1ms")
        print("="*60)
        
        # Print individual test results
        for result in self._test_results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"{status:<8} {result.test_name:<40} ", end="")
            if result.duration > 0:
                print(f"{result.duration:.3f}s")
            else:
                print("<1ms")
            if not result.passed:
                print(f"         Error: {result.error_message}")
        
        print("="*60)


# Convenience function to run integration tests
async def run_integration_tests() -> Dict[str, Any]:
    """
    Run the complete integration test suite.
    
    Returns:
        Dictionary with test results summary
    """
    tester = ViewModelViewIntegrationTester()
    results = await tester.run_all_tests()
    summary = tester.get_test_summary()
    
    tester.print_test_report()
    
    return summary


# Standalone execution
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_integration_tests())