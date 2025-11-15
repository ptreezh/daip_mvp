import pytest
import customtkinter as ctk
from unittest.mock import Mock
from src.daip_live.p7_gui_v1.views.debate_view import DebateView
from src.daip_live.p7_gui_v1.views.knowledge_view import KnowledgeView


class TestAdvancedViews:
    """TDD for Advanced Views (Debate and Knowledge)"""
    
    def test_debate_view_initialization(self):
        """RED: Test that DebateView can be initialized"""
        # Create mock ViewModel
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        # Initialize the debate view (without displaying to avoid UI issues)
        app = ctk.CTk()
        app.withdraw()  # Hide to avoid display issues
        
        frame = ctk.CTkFrame(app)
        debate_view = DebateView(frame, mock_vm)
        
        assert debate_view is not None
        assert hasattr(debate_view, '_viewmodel')
        assert hasattr(debate_view, '_parent')
        assert hasattr(debate_view, '_debate_area')
        assert hasattr(debate_view, '_participants_panel')
        assert hasattr(debate_view, '_debate_controls')
    
    def test_debate_view_has_required_components(self):
        """RED: Test that DebateView has required UI components"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        debate_view = DebateView(frame, mock_vm)
        
        # Check that required components exist
        assert hasattr(debate_view, '_debate_area')  # Main debate display area
        assert hasattr(debate_view, '_participants_panel')  # Participant management panel
        assert hasattr(debate_view, '_debate_controls')  # Debate control buttons
        assert hasattr(debate_view, '_topic_entry')  # Topic input
        assert hasattr(debate_view, '_start_button')  # Start debate button
        assert hasattr(debate_view, '_add_participant_button')  # Add participant button
        assert hasattr(debate_view, '_arguments_area')  # Arguments display area
        assert hasattr(debate_view, '_argument_input')  # Argument input field
        assert hasattr(debate_view, '_submit_argument_button')  # Submit argument button
        assert hasattr(debate_view, '_vote_area')  # Vote display area
        assert hasattr(debate_view, '_end_debate_button')  # End debate button
        
        # Check that components are properly initialized
        assert debate_view._debate_area is not None
        assert debate_view._participants_panel is not None
        assert debate_view._debate_controls is not None
        assert debate_view._topic_entry is not None
        assert debate_view._start_button is not None
        assert debate_view._arguments_area is not None
    
    def test_debate_functionality(self):
        """RED: Test debate functionality methods exist"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        debate_view = DebateView(frame, mock_vm)
        
        # Check that debate functionality methods exist
        assert hasattr(debate_view, 'start_debate')
        assert hasattr(debate_view, 'end_debate')
        assert hasattr(debate_view, 'add_participant')
        assert hasattr(debate_view, 'submit_argument')
        assert hasattr(debate_view, 'cast_vote')
        assert callable(debate_view.start_debate)
        assert callable(debate_view.end_debate)
        assert callable(debate_view.add_participant)
        assert callable(debate_view.submit_argument)
        assert callable(debate_view.cast_vote)
    
    def test_knowledge_view_initialization(self):
        """RED: Test that KnowledgeView can be initialized"""
        # Create mock ViewModel
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        # Initialize the knowledge view (without displaying to avoid UI issues)
        app = ctk.CTk()
        app.withdraw()  # Hide to avoid display issues
        
        frame = ctk.CTkFrame(app)
        knowledge_view = KnowledgeView(frame, mock_vm)
        
        assert knowledge_view is not None
        assert hasattr(knowledge_view, '_viewmodel')
        assert hasattr(knowledge_view, '_parent')
        assert hasattr(knowledge_view, '_search_frame')
        assert hasattr(knowledge_view, '_results_area')
        assert hasattr(knowledge_view, '_document_viewer')
    
    def test_knowledge_view_has_required_components(self):
        """RED: Test that KnowledgeView has required UI components"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        knowledge_view = KnowledgeView(frame, mock_vm)
        
        # Check that required components exist
        assert hasattr(knowledge_view, '_search_frame')  # Search input frame
        assert hasattr(knowledge_view, '_search_entry')  # Search input field
        assert hasattr(knowledge_view, '_search_button')  # Search button
        assert hasattr(knowledge_view, '_results_area')  # Search results area
        assert hasattr(knowledge_view, '_document_viewer')  # Document viewer area
        assert hasattr(knowledge_view, '_document_content')  # Document content display
        assert hasattr(knowledge_view, '_filters_frame')  # Filters panel
        assert hasattr(knowledge_view, '_category_filter')  # Category filter
        assert hasattr(knowledge_view, '_tag_filter')  # Tag filter
        assert hasattr(knowledge_view, '_recent_searches')  # Recent searches panel
        assert hasattr(knowledge_view, '_add_document_button')  # Add document button
        assert hasattr(knowledge_view, '_bookmarks_area')  # Bookmarks area
        
        # Check that components are properly initialized
        assert knowledge_view._search_frame is not None
        assert knowledge_view._results_area is not None
        assert knowledge_view._document_viewer is not None
        assert knowledge_view._search_entry is not None
        assert knowledge_view._search_button is not None
    
    def test_knowledge_functionality(self):
        """RED: Test knowledge functionality methods exist"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        knowledge_view = KnowledgeView(frame, mock_vm)
        
        # Check that knowledge functionality methods exist
        assert hasattr(knowledge_view, 'perform_search')
        assert hasattr(knowledge_view, 'display_results')
        assert hasattr(knowledge_view, 'view_document')
        assert hasattr(knowledge_view, 'filter_results')
        assert hasattr(knowledge_view, 'add_document')
        assert hasattr(knowledge_view, 'bookmark_document')
        assert callable(knowledge_view.perform_search)
        assert callable(knowledge_view.display_results)
        assert callable(knowledge_view.view_document)
        assert callable(knowledge_view.filter_results)
        assert callable(knowledge_view.add_document)
        assert callable(knowledge_view.bookmark_document)
    
    def test_viewmodel_binding(self):
        """RED: Test that views are properly bound to ViewModels"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        # Test Debate View binding
        debate_frame = ctk.CTkFrame(app)
        debate_view = DebateView(debate_frame, mock_vm)
        debate_view._bind_to_viewmodel()
        
        # Verify ViewModel subscription was called
        assert mock_vm.subscribe_property_change.called
        
        # Test Knowledge View binding
        knowledge_frame = ctk.CTkFrame(app)
        knowledge_view = KnowledgeView(knowledge_frame, mock_vm)
        knowledge_view._bind_to_viewmodel()
        
        # Verify ViewModel subscription was called
        assert mock_vm.subscribe_property_change.call_count >= 2  # Called for both views
    
    def test_cross_view_navigation(self):
        """RED: Test cross-view navigation functionality"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        # Both views should have navigation capabilities
        debate_frame = ctk.CTkFrame(app)
        debate_view = DebateView(debate_frame, mock_vm)
        
        knowledge_frame = ctk.CTkFrame(app)
        knowledge_view = KnowledgeView(knowledge_frame, mock_vm)
        
        # Check that navigation methods exist
        assert hasattr(debate_view, 'navigate_to_knowledge')
        assert hasattr(knowledge_view, 'navigate_to_debate')
        assert callable(debate_view.navigate_to_knowledge)
        assert callable(knowledge_view.navigate_to_debate)
    
    def test_advanced_features_functionality(self):
        """RED: Test advanced features functionality"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        # Test Debate View advanced features
        debate_frame = ctk.CTkFrame(app)
        debate_view = DebateView(debate_frame, mock_vm)
        
        assert hasattr(debate_view, '_setup_debate_participants')
        assert hasattr(debate_view, '_setup_debate_arguments')
        assert hasattr(debate_view, '_setup_debate_voting')
        assert callable(debate_view._setup_debate_participants)
        assert callable(debate_view._setup_debate_arguments)
        assert callable(debate_view._setup_debate_voting)
        
        # Test Knowledge View advanced features
        knowledge_frame = ctk.CTkFrame(app)
        knowledge_view = KnowledgeView(knowledge_frame, mock_vm)
        
        assert hasattr(knowledge_view, '_setup_document_viewer')
        assert hasattr(knowledge_view, '_setup_filters')
        assert hasattr(knowledge_view, '_setup_recent_searches')
        assert callable(knowledge_view._setup_document_viewer)
        assert callable(knowledge_view._setup_filters)
        assert callable(knowledge_view._setup_recent_searches)