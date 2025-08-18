"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : test_entrance_use_cases.py
@Description:
    Use case tests for the Personal Intelligence Hub dual-entrance system.
    Tests user stories and business scenarios defined in the specifications.
"""

import json
import logging
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch, PropertyMock
from typing import Optional, Any

import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_dual_entrance_domain_model import (
    DomainEventPublisher,
    EntranceManager,
    EntranceSwitchedEvent,
    EntranceType,
    IntentType,
    Session,
    SessionCreatedEvent,
    SessionId,
    TransparencyData,
    User,
    UserId,
    UserIntervention,
    UserInterventionAddedEvent,
    UserPreferences,
)


# Use Case Interfaces
class UserRepository:
    """User repository interface"""
    def save(self, user: User) -> None:
        pass
    
    def find_by_id(self, user_id: UserId) -> Optional[User]:
        pass
    
    def find_by_preferences(self, preferences: UserPreferences) -> list[User]:
        pass

class SessionRepository:
    """Session repository interface"""
    def save(self, session: Session) -> None:
        pass
    
    def find_by_id(self, session_id: SessionId) -> Optional[Session]:
        pass
    
    def find_by_user(self, user_id: UserId) -> list[Session]:
        pass
    
    def find_active_sessions(self) -> list[Session]:
        pass

class TransparencyService:
    """Transparency service interface"""
    async def get_workflow_transparency(self, workflow_id: str) -> TransparencyData:
        pass
    
    async def generate_intelligent_summary(self, transparency_data: TransparencyData) -> str:
        pass

class WorkflowService:
    """Workflow service interface"""
    async def execute_workflow(self, intent_type: IntentType, context: dict[str, Any]) -> dict[str, Any]:
        pass
    
    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        pass

class MultiAgentService:
    """Multi-agent service interface"""
    async def start_collaboration(self, topic: str, context: dict[str, Any]) -> str:
        pass
    
    async def add_user_intervention(self, session_id: str, intervention: UserIntervention) -> bool:
        pass
    
    async def get_consensus_metrics(self, session_id: str) -> dict[str, float]:
        pass

# Use Cases
class CreateSessionUseCase:
    """Create session use case"""
    
    def __init__(self, user_repository: UserRepository, session_repository: SessionRepository):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.entrance_manager = EntranceManager()
        self.event_publisher = DomainEventPublisher()
    
    async def execute(self, user_id: str, entrance_type: str) -> dict[str, Any]:
        """Execute create session use case"""
        try:
            # Validate input
            user_id_obj = UserId(user_id)
            entrance_type_obj = EntranceType(entrance_type)
            
            # Find or create user
            user = self.user_repository.find_by_id(user_id_obj)
            if not user:
                preferences = UserPreferences(preferred_entrance=entrance_type_obj)
                user = User(user_id_obj, preferences)
                self.user_repository.save(user)
            
            # Create session
            session = self.entrance_manager.create_session(user_id_obj, entrance_type_obj)
            self.session_repository.save(session)
            
            # Add session to user history
            user.add_session(session.session_id)
            self.user_repository.save(user)
            
            # Publish domain event
            event = SessionCreatedEvent(
                session_id=session.session_id,
                user_id=user.user_id,
                entrance_type=session.entrance_type,
                timestamp=datetime.now()
            )
            self.event_publisher.publish(event)
            
            return {
                "success": True,
                "session_id": session.session_id.value,
                "entrance_type": session.entrance_type.value,
                "status": session.status.value,
                "created_at": session.created_at.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class SwitchEntranceUseCase:
    """Switch entrance use case"""
    
    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository
        self.entrance_manager = EntranceManager()
        self.event_publisher = DomainEventPublisher()
    
    async def execute(self, session_id: str, new_entrance: str) -> dict[str, Any]:
        """Execute switch entrance use case"""
        try:
            # Validate input
            session_id_obj = SessionId(session_id)
            new_entrance_obj = EntranceType(new_entrance)
            
            # Get session
            session = self.session_repository.find_by_id(session_id_obj)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Store old entrance for event
            old_entrance = session.entrance_type
            
            # Switch entrance
            success = self.entrance_manager.switch_entrance(session_id_obj, new_entrance_obj)
            if not success:
                return {"success": False, "error": "Failed to switch entrance"}
            
            # Save updated session
            self.session_repository.save(session)
            
            # Publish domain event
            event = EntranceSwitchedEvent(
                session_id=session.session_id,
                old_entrance=old_entrance,
                new_entrance=session.entrance_type,
                timestamp=datetime.now()
            )
            self.event_publisher.publish(event)
            
            return {
                "success": True,
                "session_id": session.session_id.value,
                "old_entrance": old_entrance.value,
                "new_entrance": session.entrance_type.value,
                "timestamp": session.last_modified.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ProcessSecretariatRequestUseCase:
    """Process Secretariat request use case"""
    
    def __init__(self, session_repository: SessionRepository, workflow_service: WorkflowService,
                 transparency_service: TransparencyService):
        self.session_repository = session_repository
        self.workflow_service = workflow_service
        self.transparency_service = transparency_service
    
    async def execute(self, session_id: str, content: str) -> dict[str, Any]:
        """Execute Secretariat request processing"""
        try:
            # Validate input
            session_id_obj = SessionId(session_id)
            
            # Get session
            session = self.session_repository.find_by_id(session_id_obj)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            if session.entrance_type != EntranceType.SECRETARIAT:
                return {"success": False, "error": "Not a Secretariat session"}
            
            # Determine intent type (simplified)
            intent_type = self._determine_intent(content)
            
            # Execute workflow
            workflow_result = await self.workflow_service.execute_workflow(
                intent_type, {"content": content, "session_id": session_id}
            )
            
            # Get transparency data
            transparency_data = await self.transparency_service.get_workflow_transparency(
                workflow_result.get("workflow_id")
            )
            
            # Update session with transparency data
            session.update_transparency_data(transparency_data)
            self.session_repository.save(session)
            
            return {
                "success": True,
                "session_id": session.session_id.value,
                "content": workflow_result.get("content"),
                "intent_type": intent_type.value,
                "workflow_id": workflow_result.get("workflow_id"),
                "execution_time": workflow_result.get("execution_time"),
                "has_transparency": transparency_data is not None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_intent(self, content: str) -> IntentType:
        """Determine intent from content (simplified)"""
        content_lower = content.lower()
        
        # Check for industry analysis first (more specific)
        if any(keyword in content_lower for keyword in ["industry", "market", "business"]):
            return IntentType.INDUSTRY_ANALYSIS
        # Check for academic research (but exclude market/industry analysis)
        elif any(keyword in content_lower for keyword in ["analyze", "research", "study"]) and \
             not any(keyword in content_lower for keyword in ["market", "industry"]):
            return IntentType.ACADEMIC_RESEARCH
        elif any(keyword in content_lower for keyword in ["expert", "consult", "advice"]):
            return IntentType.EXPERT_CONSULTATION
        else:
            return IntentType.CASUAL_DISCUSSION

class ProcessForumRequestUseCase:
    """Process Forum request use case"""
    
    def __init__(self, session_repository: SessionRepository, multi_agent_service: MultiAgentService):
        self.session_repository = session_repository
        self.multi_agent_service = multi_agent_service
    
    async def execute(self, session_id: str, topic: str) -> dict[str, Any]:
        """Execute Forum request processing"""
        try:
            # Validate input
            session_id_obj = SessionId(session_id)
            
            # Get session
            session = self.session_repository.find_by_id(session_id_obj)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            if session.entrance_type != EntranceType.FORUM:
                return {"success": False, "error": "Not a Forum session"}
            
            # Start multi-agent collaboration
            collaboration_id = await self.multi_agent_service.start_collaboration(
                topic, {"session_id": session_id}
            )
            
            # Update session context
            session.context["collaboration_id"] = collaboration_id
            session.context["topic"] = topic
            self.session_repository.save(session)
            
            return {
                "success": True,
                "session_id": session.session_id.value,
                "collaboration_id": collaboration_id,
                "topic": topic,
                "status": "collaboration_started"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class HandleUserInterventionUseCase:
    """Handle user intervention use case"""
    
    def __init__(self, session_repository: SessionRepository, multi_agent_service: MultiAgentService,
                 event_publisher: DomainEventPublisher):
        self.session_repository = session_repository
        self.multi_agent_service = multi_agent_service
        self.event_publisher = event_publisher
    
    async def execute(self, session_id: str, content: str, intent_type: str) -> dict[str, Any]:
        """Execute user intervention handling"""
        try:
            # Validate input
            session_id_obj = SessionId(session_id)
            
            # Get session
            session = self.session_repository.find_by_id(session_id_obj)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            if session.entrance_type != EntranceType.FORUM:
                return {"success": False, "error": "Not a Forum session"}
            
            # Create intervention
            intervention = UserIntervention(
                content=content,
                intent_type=intent_type,
                timestamp=datetime.now(),
                session_id=session_id
            )
            
            # Add to session
            session.add_intervention(intervention)
            self.session_repository.save(session)
            
            # Add to multi-agent collaboration
            success = await self.multi_agent_service.add_user_intervention(session_id, intervention)
            
            # Publish domain event
            event = UserInterventionAddedEvent(
                session_id=session.session_id,
                intervention=intervention,
                timestamp=datetime.now()
            )
            self.event_publisher.publish(event)
            
            return {
                "success": True,
                "session_id": session.session_id.value,
                "intervention_added": True,
                "collaboration_updated": success,
                "intervention_count": len(session.interventions)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class GetTransparencyDataUseCase:
    """Get transparency data use case"""
    
    def __init__(self, session_repository: SessionRepository, transparency_service: TransparencyService):
        self.session_repository = session_repository
        self.transparency_service = transparency_service
    
    async def execute(self, session_id: str, detail_level: str = "summary") -> dict[str, Any]:
        """Execute transparency data retrieval"""
        try:
            # Validate input
            session_id_obj = SessionId(session_id)
            
            # Get session
            session = self.session_repository.find_by_id(session_id_obj)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Get transparency data
            if session.transparency_data:
                transparency_data = session.transparency_data
            else:
                # Try to get from service
                workflow_id = session.context.get("workflow_id")
                if workflow_id:
                    transparency_data = await self.transparency_service.get_workflow_transparency(workflow_id)
                    session.update_transparency_data(transparency_data)
                    self.session_repository.save(session)
                else:
                    return {"success": False, "error": "No transparency data available"}
            
            # Generate intelligent summary if requested
            summary = None
            if detail_level == "summary":
                summary = await self.transparency_service.generate_intelligent_summary(transparency_data)
            
            return {
                "success": True,
                "session_id": session.session_id.value,
                "transparency_data": {
                    "workflow_steps": transparency_data.workflow_steps,
                    "agent_contributions": transparency_data.agent_contributions,
                    "consensus_metrics": transparency_data.consensus_metrics,
                    "performance_data": transparency_data.performance_data,
                    "knowledge_sources": transparency_data.knowledge_sources
                },
                "summary": summary,
                "detail_level": detail_level
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Test Cases
class TestEntranceUseCases:
    """Test suite for entrance use cases"""
    
    @pytest.fixture()
    def mock_user_repository(self):
        return Mock(spec=UserRepository)
    
    @pytest.fixture()
    def mock_session_repository(self):
        return Mock(spec=SessionRepository)
    
    @pytest.fixture()
    def mock_workflow_service(self):
        return Mock(spec=WorkflowService)
    
    @pytest.fixture()
    def mock_transparency_service(self):
        return Mock(spec=TransparencyService)
    
    @pytest.fixture()
    def mock_multi_agent_service(self):
        return Mock(spec=MultiAgentService)
    
    @pytest.fixture()
    def sample_user(self):
        user_id = UserId("test_user")
        preferences = UserPreferences(preferred_entrance=EntranceType.SECRETARIAT)
        return User(user_id, preferences)
    
    @pytest.fixture()
    def sample_session(self):
        user_id = UserId("test_user")
        session_id = SessionId("test_session")
        return Session(session_id, user_id, EntranceType.SECRETARIAT)
    
    @pytest.mark.asyncio()
    async def test_create_session_use_case_success(self, mock_user_repository, mock_session_repository):
        """Test successful session creation"""
        # Setup mocks
        mock_user_repository.find_by_id.return_value = None
        mock_user_repository.save = Mock()
        mock_session_repository.save = Mock()
        
        # Create use case
        use_case = CreateSessionUseCase(mock_user_repository, mock_session_repository)
        
        # Execute
        result = await use_case.execute("test_user", "secretariat")
        
        # Verify
        assert result["success"] is True
        assert result["session_id"] is not None
        assert result["entrance_type"] == "secretariat"
        assert result["status"] == "active"
        
        # Verify user was saved twice (once when created, once when session is added to history)
        assert mock_user_repository.save.call_count == 2
        
        # Verify session was saved
        mock_session_repository.save.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_create_session_use_case_existing_user(self, mock_user_repository, mock_session_repository, sample_user):
        """Test session creation with existing user"""
        # Setup mocks
        mock_user_repository.find_by_id.return_value = sample_user
        mock_session_repository.save = Mock()
        
        # Create use case
        use_case = CreateSessionUseCase(mock_user_repository, mock_session_repository)
        
        # Execute
        result = await use_case.execute("test_user", "forum")
        
        # Verify
        assert result["success"] is True
        assert result["entrance_type"] == "forum"
        
        # Verify user was not saved again (should be updated)
        # The user should have the new session added to their history
        assert len(sample_user.session_history) == 1
    
    @pytest.mark.asyncio()
    async def test_switch_entrance_use_case_success(self, mock_session_repository, sample_session):
        """Test successful entrance switching"""
        # Setup mocks
        mock_session_repository.find_by_id.return_value = sample_session
        mock_session_repository.save = Mock()
        
        # Create use case
        use_case = SwitchEntranceUseCase(mock_session_repository)
        
        # Define a side effect for switch_entrance to actually change the session's entrance_type
        def switch_entrance_side_effect(session_id, new_entrance):
            sample_session.entrance_type = new_entrance
            return True
            
        # Mock the entrance_manager to return the sample_session when get_session is called
        # and to actually change the session's entrance_type when switch_entrance is called
        with patch.object(use_case.entrance_manager, 'get_session', return_value=sample_session), \
             patch.object(use_case.entrance_manager, 'switch_entrance', side_effect=switch_entrance_side_effect):
            
            # Store the original value
            original_entrance_type = sample_session.entrance_type
            # The side effect will change it to FORUM
            
            # Execute
            result = await use_case.execute("test_session", "forum")
            
            # Restore the original entrance_type for future tests
            sample_session.entrance_type = original_entrance_type
            
            # Verify
            assert result["success"] is True
            assert result["session_id"] == "test_session"
            assert result["old_entrance"] == "secretariat"
            assert result["new_entrance"] == "forum"
            
            # Verify session was saved
            mock_session_repository.save.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_switch_entrance_use_case_session_not_found(self, mock_session_repository):
        """Test entrance switching with session not found"""
        # Setup mocks
        mock_session_repository.find_by_id.return_value = None
        
        # Create use case
        use_case = SwitchEntranceUseCase(mock_session_repository)
        
        # Execute
        result = await use_case.execute("nonexistent_session", "forum")
        
        # Verify
        assert result["success"] is False
        assert result["error"] == "Session not found"
    
    @pytest.mark.asyncio()
    async def test_process_secretariat_request_use_case_success(self, mock_session_repository, 
                                                                mock_workflow_service, mock_transparency_service, sample_session):
        """Test successful Secretariat request processing"""
        # Setup mocks
        mock_session_repository.find_by_id.return_value = sample_session
        mock_session_repository.save = Mock()
        
        mock_workflow_service.execute_workflow.return_value = {
            "workflow_id": "workflow_123",
            "content": "Analysis complete",
            "execution_time": 5.2
        }
        
        transparency_data = TransparencyData(
            workflow_steps=[{"step": "analysis"}],
            agent_contributions=[{"agent": "expert"}],
            consensus_metrics={"consensus": 0.9},
            performance_data={"time": 5.2},
            knowledge_sources=[{"source": "database"}]
        )
        mock_transparency_service.get_workflow_transparency.return_value = transparency_data
        
        # Create use case
        use_case = ProcessSecretariatRequestUseCase(
            mock_session_repository, mock_workflow_service, mock_transparency_service
        )
        
        # Execute
        result = await use_case.execute("test_session", "Analyze AI trends")
        
        # Verify
        assert result["success"] is True
        assert result["session_id"] == "test_session"
        assert result["content"] == "Analysis complete"
        assert result["intent_type"] == "academic_research"
        assert result["workflow_id"] == "workflow_123"
        assert result["has_transparency"] is True
        
        # Verify workflow was executed
        mock_workflow_service.execute_workflow.assert_called_once()
        
        # Verify transparency data was retrieved
        mock_transparency_service.get_workflow_transparency.assert_called_once()
        
        # Verify session was saved
        mock_session_repository.save.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_process_forum_request_use_case_success(self, mock_session_repository, 
                                                          mock_multi_agent_service, sample_session):
        """Test successful Forum request processing"""
        # Setup forum session
        sample_session.entrance_type = EntranceType.FORUM
        mock_session_repository.find_by_id.return_value = sample_session
        mock_session_repository.save = Mock()
        
        mock_multi_agent_service.start_collaboration.return_value = "collaboration_123"
        
        # Create use case
        use_case = ProcessForumRequestUseCase(mock_session_repository, mock_multi_agent_service)
        
        # Execute
        result = await use_case.execute("test_session", "AI ethics discussion")
        
        # Verify
        assert result["success"] is True
        assert result["session_id"] == "test_session"
        assert result["collaboration_id"] == "collaboration_123"
        assert result["topic"] == "AI ethics discussion"
        assert result["status"] == "collaboration_started"
        
        # Verify collaboration was started
        mock_multi_agent_service.start_collaboration.assert_called_once()
        
        # Verify session was saved
        mock_session_repository.save.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_handle_user_intervention_use_case_success(self, mock_session_repository, 
                                                           mock_multi_agent_service, sample_session):
        """Test successful user intervention handling"""
        # Setup forum session
        sample_session.entrance_type = EntranceType.FORUM
        mock_session_repository.find_by_id.return_value = sample_session
        mock_session_repository.save = Mock()
        
        mock_multi_agent_service.add_user_intervention.return_value = True
        
        # Create use case
        use_case = HandleUserInterventionUseCase(
            mock_session_repository, mock_multi_agent_service, DomainEventPublisher()
        )
        
        # Execute
        result = await use_case.execute("test_session", "I think privacy is important", "comment")
        
        # Verify
        assert result["success"] is True
        assert result["session_id"] == "test_session"
        assert result["intervention_added"] is True
        assert result["collaboration_updated"] is True
        assert result["intervention_count"] == 1
        
        # Verify intervention was added to session
        assert len(sample_session.interventions) == 1
        assert sample_session.interventions[0].content == "I think privacy is important"
        
        # Verify intervention was added to collaboration
        mock_multi_agent_service.add_user_intervention.assert_called_once()
        
        # Verify session was saved
        mock_session_repository.save.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_get_transparency_data_use_case_success(self, mock_session_repository, 
                                                          mock_transparency_service, sample_session):
        """Test successful transparency data retrieval"""
        # Setup mocks
        mock_session_repository.find_by_id.return_value = sample_session
        mock_session_repository.save = Mock()
        
        transparency_data = TransparencyData(
            workflow_steps=[{"step": "analysis"}],
            agent_contributions=[{"agent": "expert"}],
            consensus_metrics={"consensus": 0.9},
            performance_data={"time": 5.2},
            knowledge_sources=[{"source": "database"}]
        )
        
        mock_transparency_service.generate_intelligent_summary.return_value = "Analysis completed successfully"
        
        # Add transparency data to session
        sample_session.update_transparency_data(transparency_data)
        
        # Create use case
        use_case = GetTransparencyDataUseCase(mock_session_repository, mock_transparency_service)
        
        # Execute
        result = await use_case.execute("test_session", "summary")
        
        # Verify
        assert result["success"] is True
        assert result["session_id"] == "test_session"
        assert "transparency_data" in result
        assert result["transparency_data"]["consensus_metrics"]["consensus"] == 0.9
        assert result["summary"] == "Analysis completed successfully"
        assert result["detail_level"] == "summary"
        
        # Verify summary was generated
        mock_transparency_service.generate_intelligent_summary.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_get_transparency_data_use_case_no_data(self, mock_session_repository, 
                                                          mock_transparency_service, sample_session):
        """Test transparency data retrieval when no data is available"""
        # Setup mocks
        mock_session_repository.find_by_id.return_value = sample_session
        
        # Create use case
        use_case = GetTransparencyDataUseCase(mock_session_repository, mock_transparency_service)
        
        # Execute
        result = await use_case.execute("test_session", "summary")
        
        # Verify
        assert result["success"] is False
        assert result["error"] == "No transparency data available"
    
    def test_intent_determination_logic(self):
        """Test intent determination logic"""
        use_case = ProcessSecretariatRequestUseCase(Mock(), Mock(), Mock())
        
        # Test academic research intent
        intent = use_case._determine_intent("Please research the latest AI trends")
        assert intent == IntentType.ACADEMIC_RESEARCH
        
        # Test expert consultation intent
        intent = use_case._determine_intent("I need expert advice on machine learning")
        assert intent == IntentType.EXPERT_CONSULTATION
        
        # Test industry analysis intent
        intent = use_case._determine_intent("Analyze the AI market trends")
        assert intent == IntentType.INDUSTRY_ANALYSIS
        
        # Test casual discussion intent
        intent = use_case._determine_intent("Let's chat about AI")
        assert intent == IntentType.CASUAL_DISCUSSION
    
    @pytest.mark.asyncio()
    async def test_use_case_error_handling(self, mock_session_repository):
        """Test use case error handling"""
        # Test with invalid session ID
        use_case = SwitchEntranceUseCase(mock_session_repository)
        result = await use_case.execute("", "forum")
        assert result["success"] is False
        assert "error" in result
        
        # Test with invalid entrance type
        use_case = CreateSessionUseCase(Mock(), Mock())
        result = await use_case.execute("test_user", "invalid_entrance")
        assert result["success"] is False
        assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])