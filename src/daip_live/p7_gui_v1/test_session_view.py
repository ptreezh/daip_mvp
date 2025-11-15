import pytest
import customtkinter as ctk
from unittest.mock import Mock
from src.daip_live.p7_gui_v1.views.session_view import SessionView


class TestSessionView:
    """TDD for Session Management View"""
    
    def test_session_view_initialization(self):
        """RED: Test that SessionView can be initialized"""
        # Create a mock ViewModel
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        # Initialize the session view (without actually displaying it)
        app = ctk.CTk()
        app.withdraw()  # Hide it to avoid display issues during testing
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        
        assert session_view is not None
        assert hasattr(session_view, '_viewmodel')
        assert hasattr(session_view, '_parent')
        assert hasattr(session_view, '_session_listbox')
        assert hasattr(session_view, '_session_details_frame')
    
    def test_session_view_has_required_components(self):
        """RED: Test that SessionView has required UI components"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        session_view._setup_components()
        
        # Check that required components exist
        assert hasattr(session_view, '_session_listbox')  # Listbox for sessions
        assert hasattr(session_view, '_session_details_frame')  # Frame for session details
        assert hasattr(session_view, '_session_id_label')  # Label for session ID
        assert hasattr(session_view, '_session_title_label')  # Label for session title
        assert hasattr(session_view, '_session_status_label')  # Label for session status
        assert hasattr(session_view, '_session_created_label')  # Label for creation date
        assert hasattr(session_view, '_session_goal_text')  # Text box for session goal
        assert hasattr(session_view, '_load_button')  # Button to load session
        assert hasattr(session_view, '_delete_button')  # Button to delete session
        assert hasattr(session_view, '_new_session_button')  # Button to create new session
        assert hasattr(session_view, '_search_entry')  # Entry for searching sessions
        assert hasattr(session_view, '_refresh_button')  # Button to refresh sessions
        
        # Check that components are properly initialized
        assert session_view._session_listbox is not None
        assert session_view._session_details_frame is not None
        assert session_view._load_button is not None
        assert session_view._delete_button is not None
        assert session_view._new_session_button is not None
        assert session_view._search_entry is not None
        assert session_view._refresh_button is not None
    
    def test_session_listing_functionality(self):
        """RED: Test that sessions can be listed"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'id': 'session1', 'title': 'Session 1', 'status': 'active', 'created_at': '2025-11-08', 'goal': 'Test goal 1'},
            {'id': 'session2', 'title': 'Session 2', 'status': 'completed', 'created_at': '2025-11-07', 'goal': 'Test goal 2'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        session_view._setup_components()
        
        # Check that the method exists to populate sessions
        assert hasattr(session_view, '_populate_sessions_list')
        assert callable(session_view._populate_sessions_list)
    
    def test_session_selection_functionality(self):
        """RED: Test session selection functionality"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'id': 'session1', 'title': 'Session 1', 'status': 'active', 'created_at': '2025-11-08', 'goal': 'Test goal 1'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Selected session: session1')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        session_view._setup_components()
        
        # Check that session selection methods exist
        assert hasattr(session_view, 'select_session')
        assert callable(session_view.select_session)
    
    def test_session_action_functions(self):
        """RED: Test session action functions (create, delete, load)"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'id': 'session1', 'title': 'Test Session', 'status': 'active', 'created_at': '2025-11-08', 'goal': 'Test goal'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        session_view._setup_components()
        
        # Check that action methods exist
        assert hasattr(session_view, '_create_new_session')
        assert hasattr(session_view, '_load_selected_session')
        assert hasattr(session_view, '_delete_selected_session')
        assert callable(session_view._create_new_session)
        assert callable(session_view._load_selected_session)
        assert callable(session_view._delete_selected_session)
    
    def test_session_search_functionality(self):
        """RED: Test session search functionality"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'id': 'session1', 'title': 'Test Session', 'status': 'active', 'created_at': '2025-11-08', 'goal': 'Test goal'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        session_view._setup_components()
        
        # Check that search methods exist
        assert hasattr(session_view, '_search_sessions')
        assert callable(session_view._search_sessions)
    
    def test_viewmodel_binding(self):
        """RED: Test that view is bound to ViewModel"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        session_view._setup_components()
        session_view._bind_to_viewmodel()
        
        # Verify that the viewmodel binding was set up
        assert mock_vm.subscribe_property_change.called
    
    def test_session_details_display(self):
        """RED: Test displaying session details"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'id': 'session1', 'title': 'Test Session', 'status': 'active', 'created_at': '2025-11-08', 'goal': 'Test goal'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        session_view = SessionView(frame, mock_vm)
        session_view._setup_components()
        
        # Check that the method exists to display session details
        assert hasattr(session_view, '_display_session_details')
        assert callable(session_view._display_session_details)