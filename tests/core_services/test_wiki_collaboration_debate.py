"""Test Wiki collaboration with debate engine integration"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.core_services.wiki_service import WikiService


class TestWikiCollaborationWithDebate:
    """Test Wiki collaboration with debate engine integration"""
    
    def test_initiate_collaborative_edit_returns_expected_result(self, tmp_path):
        """Test that initiate_collaborative_edit returns expected result"""
        # Setup
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        wiki_service = WikiService(str(wiki_dir))
        topic = "人工智能伦理"
        
        # Mock the import method to avoid dependency issues
        with patch.object(wiki_service, '_import_debate_components') as mock_import:
            mock_import.return_value = {
                "MultiRoleDialogueEngine": Mock(),
                "RoleManager": Mock(),
                "IntegratedLLMManager": Mock(),
                "CognitiveAgent": Mock(),
                "MemAgent": Mock(),
                "ParticipantManager": Mock()
            }
            
            # Execute
            result = wiki_service.initiate_collaborative_edit(topic)
            
            # Verify
            assert "status" in result
            assert result["status"] == "initiated"
            assert "topic" in result
            assert result["topic"] == topic
            assert "session_id" in result
            assert result["session_id"].startswith("collab_")
            assert "message" in result
            # Check that the message contains either Chinese or English success indicator
            assert "成功" in result["message"] or "successfully" in result["message"]
    
    def test_initiate_collaborative_edit_handles_exception(self, tmp_path):
        """Test that initiate_collaborative_edit handles exceptions gracefully"""
        # Setup
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        wiki_service = WikiService(str(wiki_dir))
        topic = "人工智能伦理"
        
        # Execute with a mocked exception
        with patch.object(wiki_service, '_import_debate_components') as mock_import:
            mock_import.side_effect = Exception("Test exception")
            result = wiki_service.initiate_collaborative_edit(topic)
        
        # Verify
        assert "error" in result
        assert "Test exception" in result["error"]