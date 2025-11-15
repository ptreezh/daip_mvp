import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.viewmodel.knowledge_viewmodel import KnowledgeViewModel


class TestKnowledgeViewModel:
    """TDD for Knowledge Base ViewModel"""
    
    def test_knowledge_viewmodel_initialization(self):
        """RED: Test that KnowledgeViewModel can be initialized"""
        mock_interaction = Mock()
        vm = KnowledgeViewModel(mock_interaction)
        assert vm is not None
        assert hasattr(vm, '_interaction_layer')
        assert hasattr(vm, '_documents')
        assert hasattr(vm, '_search_results')
        assert hasattr(vm, '_knowledge_base_status')
    
    def test_knowledge_viewmodel_initial_properties(self):
        """RED: Test initial properties of KnowledgeViewModel"""
        mock_interaction = Mock()
        vm = KnowledgeViewModel(mock_interaction)
        
        # Check initial state
        assert vm.get_property('available_documents') == []
        assert vm.get_property('search_results') == []
        assert vm.get_property('search_query') == ''
        assert vm.get_property('current_document') is None
        assert vm.get_property('knowledge_base_status') is None
        assert vm.get_property('is_loading_documents') is False
        assert vm.get_property('is_searching') is False
        assert vm.get_property('total_documents') == 0
        assert vm.get_property('last_sync_date') is None
    
    @pytest.mark.asyncio
    async def test_search_knowledge_command(self):
        """RED: Test search knowledge functionality"""
        mock_interaction = AsyncMock()
        expected_results = [
            {'id': 'doc1', 'title': 'Document 1', 'content': 'Content of document 1', 'score': 0.95},
            {'id': 'doc2', 'title': 'Document 2', 'content': 'Content of document 2', 'score': 0.87}
        ]
        mock_interaction.search_knowledge.return_value = expected_results
        
        vm = KnowledgeViewModel(mock_interaction)
        results = await vm.search_knowledge('test query')
        
        assert results == expected_results
        mock_interaction.search_knowledge.assert_called_once_with('test query')
    
    @pytest.mark.asyncio
    async def test_get_knowledge_status_command(self):
        """RED: Test getting knowledge base status functionality"""
        mock_interaction = AsyncMock()
        expected_status = {
            'status': 'healthy',
            'last_sync': '2025-11-08T10:00:00Z',
            'total_documents': 100
        }
        mock_interaction.get_knowledge_status.return_value = expected_status
        
        vm = KnowledgeViewModel(mock_interaction)
        status = await vm.get_knowledge_status()
        
        assert status == expected_status
        mock_interaction.get_knowledge_status.assert_called_once()
    
    def test_property_management(self):
        """RED: Test property management functionality"""
        mock_interaction = Mock()
        vm = KnowledgeViewModel(mock_interaction)
        
        # Test setting and getting properties
        vm.set_property('search_query', 'test query')
        assert vm.get_property('search_query') == 'test query'
        
        vm.set_property('is_loading_documents', True)
        assert vm.get_property('is_loading_documents') is True
        
        vm.set_property('total_documents', 50)
        assert vm.get_property('total_documents') == 50
    
    def test_search_result_filtering(self):
        """RED: Test filtering search results"""
        mock_interaction = Mock()
        vm = KnowledgeViewModel(mock_interaction)
        
        # Add some search results
        test_results = [
            {'id': 'doc1', 'title': 'AI Ethics Document', 'content': 'Content about AI ethics', 'tags': ['ai', 'ethics']},
            {'id': 'doc2', 'title': 'Machine Learning Guide', 'content': 'Guide to ML', 'tags': ['ml', 'guide']},
            {'id': 'doc3', 'title': 'Python Programming', 'content': 'Python guide', 'tags': ['python', 'programming']}
        ]
        vm.set_property('search_results', test_results)
        
        # Test that the method exists to filter results
        assert hasattr(vm, '_filter_results_by_tags')
        assert callable(vm._filter_results_by_tags)
    
    def test_document_management(self):
        """RED: Test document management functionality"""
        mock_interaction = Mock()
        vm = KnowledgeViewModel(mock_interaction)
        
        # Test document management methods exist
        assert hasattr(vm, 'add_document')
        assert hasattr(vm, 'remove_document')
        assert callable(vm.add_document)
        assert callable(vm.remove_document)
    
    def test_recent_search_tracking(self):
        """RED: Test tracking recent searches"""
        mock_interaction = Mock()
        vm = KnowledgeViewModel(mock_interaction)
        
        # Test that recent search tracking exists
        assert hasattr(vm, '_recent_searches')
        assert isinstance(vm._recent_searches, list)
        
        # Test that method exists to get recent searches
        assert hasattr(vm, 'get_recent_searches')
        assert callable(vm.get_recent_searches)