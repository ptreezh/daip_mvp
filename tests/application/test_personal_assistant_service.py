"""
Personal Assistant Service Tests
========================

This module contains comprehensive tests for the PersonalAssistantService.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.domain.value_objects import EntranceType, IntentType, TaskStatus, ConsensusLevel, MessageIntent
from src.domain.entities import User, UserPreference
from src.application.personal_assistant_service import PersonalAssistantService


class TestPersonalAssistantService:
    """Tests for the PersonalAssistantService"""
    
    @pytest.fixture
    def assistant_service(self):
        """Create a PersonalAssistantService instance for testing"""
        with patch('src.application.personal_assistant_service.SecretariatUseCase') as mock_secretariat, \\
             patch('src.application.personal_assistant_service.ForumUseCase') as mock_forum, \\
             patch('src.application.personal_assistant_service.EntranceSwitchingUseCase') as mock_entrance:
            
            # Create mock instances
            mock_secretariat_instance = AsyncMock()
            mock_forum_instance = AsyncMock()
            mock_entrance_instance = AsyncMock()
            
            # Configure return values for the mocks
            mock_secretariat.return_value = mock_secretariat_instance
            mock_forum.return_value = mock_forum_instance
            mock_entrance.return_value = mock_entrance_instance
            
            # Create the service instance
            service = PersonalAssistantService()
            
            # Return the service with its mocked dependencies
            return service
    
    @pytest.mark.asyncio
    async def test_initialize(self, assistant_service):
        """Test service initialization"""
        # Ensure service is not already initialized
        assistant_service.is_initialized = False
        
        await assistant_service.initialize()
        
        assert assistant_service.is_initialized == True
        assert assistant_service.startup_time is not None
        assert isinstance(assistant_service.startup_time, datetime)
        assert len(assistant_service.users) > 0
    
    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self, assistant_service):
        """Test service initialization when already initialized"""
        # First initialize the service
        await assistant_service.initialize()
        initial_startup_time = assistant_service.startup_time
        
        # Try to initialize again
        await assistant_service.initialize()
        
        # Should not change the startup time
        assert assistant_service.startup_time == initial_startup_time
    
    @pytest.mark.asyncio
    async def test_create_session(self, assistant_service):
        """Test creating a session"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Create a test user if it doesn't exist
        user_id = "test_user_2"
        if user_id not in assistant_service.users:
            user = User(
                user_id=user_id,
                username="Test User 2",
                email="test2@example.com",
                preferred_entrance=None,
                preferences=UserPreference(
                    preferred_entrance=EntranceType.SECRETARIAT,
                    language="en-US",
                    theme="light",
                    notification_enabled=True,
                    auto_transparency=False,
                    detail_level="comprehensive"
                )
            )
            assistant_service.users[user_id] = user
        
        # Mock the entrance selector to return a specific entrance type
        with patch.object(assistant_service.entrance_selector, 'select_entrance', AsyncMock(return_value=EntranceType.SECRETARIAT)):
            # Mock the create_session method to return a predefined value
            assistant_service.secretariat_use_case.create_session = AsyncMock(return_value=Mock(session_id="test_session"))
            
            # Create session
            context = {"topic": "Test topic"}
            session_info = await assistant_service.create_session(user_id, context)
            
            assert isinstance(session_info, dict)
            assert "session_id" in session_info
            assert "user_id" in session_info
            assert "entrance_type" in session_info
            assert session_info["user_id"] == user_id
            assert session_info["session_id"] in assistant_service.sessions
    
    @pytest.mark.asyncio
    async def test_create_session_user_not_found(self, assistant_service):
        """Test creating a session with non-existent user"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Try to create session for non-existent user
        with pytest.raises(ValueError, match="User nonexistent_user not found"):
            await assistant_service.create_session("nonexistent_user", {})
    
    @pytest.mark.asyncio
    async def test_process_user_input_secretariat(self, assistant_service):
        """Test processing user input for Secretariat entrance"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Create a session first
        user_id = "test_user_3"
        if user_id not in assistant_service.users:
            user = User(
                user_id=user_id,
                username="Test User 3",
                email="test3@example.com",
                preferred_entrance=EntranceType.SECRETARIAT,
                preferences=UserPreference(
                    preferred_entrance=EntranceType.SECRETARIAT,
                    language="en-US",
                    theme="light",
                    notification_enabled=True,
                    auto_transparency=False,
                    detail_level="comprehensive"
                )
            )
            assistant_service.users[user_id] = user
        
        # Mock the entrance selector to return SECRETARIAT
        with patch.object(assistant_service.entrance_selector, 'select_entrance', AsyncMock(return_value=EntranceType.SECRETARIAT)):
            # Mock the create_session method to return a predefined value
            assistant_service.secretariat_use_case.create_session = AsyncMock(return_value=Mock(session_id="test_session"))
            
            context = {}
            session_info = await assistant_service.create_session(user_id, context)
            session_id = session_info["session_id"]
            
            # Process input
            user_input = {
                "content": "Analyze the impact of AI on job markets",
                "priority": "normal",
                "context": {}
            }
            
            # Mock the secretariat use case to avoid complex dependencies
            with patch.object(assistant_service, 'secretariat_use_case') as mock_secretariat:
                mock_secretariat.submit_task = AsyncMock(return_value={
                    "task_id": "test_task",
                    "workflow_id": "test_workflow",
                    "estimated_duration": 10.0
                })
                
                # Mock the session aggregate
                mock_session_aggregate = Mock()
                mock_session_aggregate.session_id = session_id
                mock_session_aggregate.user_id = user_id
                assistant_service.sessions[session_id] = mock_session_aggregate
                
                # Mock the add_message method to avoid errors
                mock_session_aggregate.add_message = Mock()
                
                result = await assistant_service.process_user_input(session_id, user_input)
                
                assert isinstance(result, dict)
                assert "type" in result
                assert "task_id" in result
                assert "workflow_id" in result
                assert "estimated_duration" in result
                assert result["type"] == "task_created"
    
    @pytest.mark.asyncio
    async def test_process_user_input_forum(self, assistant_service):
        """Test processing user input for Forum entrance"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Create a session first
        user_id = "test_user_4"
        if user_id not in assistant_service.users:
            user = User(
                user_id=user_id,
                username="Test User 4",
                email="test4@example.com",
                preferred_entrance=EntranceType.FORUM,
                preferences=UserPreference(
                    preferred_entrance=EntranceType.FORUM,
                    language="en-US",
                    theme="light",
                    notification_enabled=True,
                    auto_transparency=False,
                    detail_level="comprehensive"
                )
            )
            assistant_service.users[user_id] = user
        
        # Mock the entrance selector to return FORUM
        with patch.object(assistant_service.entrance_selector, 'select_entrance', AsyncMock(return_value=EntranceType.FORUM)):
            # Mock the create_session method to return a predefined value
            assistant_service.forum_use_case.create_forum_session = AsyncMock(return_value=Mock(session_id="test_session"))
            
            context = {"topic": "Test topic"}
            session_info = await assistant_service.create_session(user_id, context)
            session_id = session_info["session_id"]
            
            # Process input
            user_input = {
                "content": "I have a suggestion for improving the workflow",
                "intent": "suggestion",
                "context": {}
            }
            
            # Mock the forum use case to avoid complex dependencies
            with patch.object(assistant_service, 'forum_use_case') as mock_forum:
                mock_forum.handle_user_intervention = AsyncMock(return_value={
                    "message_id": "test_message",
                    "integration_result": "Integrated successfully"
                })
                
                # Mock the session aggregate
                mock_session_aggregate = Mock()
                mock_session_aggregate.session_id = session_id
                mock_session_aggregate.user_id = user_id
                mock_session_aggregate.entrance_type = EntranceType.FORUM
                assistant_service.sessions[session_id] = mock_session_aggregate
                
                result = await assistant_service.process_user_input(session_id, user_input)
                
                assert isinstance(result, dict)
                assert "type" in result
                assert "message_id" in result
                assert "integration_result" in result
                assert result["type"] == "intervention_processed"
    
    @pytest.mark.asyncio
    async def test_process_user_input_session_not_found(self, assistant_service):
        """Test processing user input for non-existent session"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Try to process input for non-existent session
        with pytest.raises(ValueError, match="Session nonexistent_session not found"):
            await assistant_service.process_user_input("nonexistent_session", {"content": "test"})
    
    def test_analyze_input_intent_question(self, assistant_service):
        """Test analyzing input intent for question"""
        question_content = "What are the effects of climate change?"
        intent = assistant_service._analyze_input_intent(question_content)
        assert isinstance(intent, IntentType)
        assert intent == IntentType.QUESTION
    
    def test_analyze_input_intent_analysis(self, assistant_service):
        """Test analyzing input intent for analysis"""
        analysis_content = "Analyze the impact of social media on mental health"
        intent = assistant_service._analyze_input_intent(analysis_content)
        assert isinstance(intent, IntentType)
        assert intent == IntentType.ANALYSIS
    
    def test_analyze_input_intent_discussion(self, assistant_service):
        """Test analyzing input intent for discussion"""
        discussion_content = "Let's discuss the pros and cons of remote work"
        intent = assistant_service._analyze_input_intent(discussion_content)
        assert isinstance(intent, IntentType)
        assert intent == IntentType.DISCUSSION
    
    def test_analyze_input_intent_comment(self, assistant_service):
        """Test analyzing input intent for comment (default)"""
        comment_content = "This is an interesting point"
        intent = assistant_service._analyze_input_intent(comment_content)
        assert isinstance(intent, IntentType)
        assert intent == IntentType.COMMENT
    
    @pytest.mark.asyncio
    async def test_get_session_status_secretariat(self, assistant_service):
        """Test getting session status for Secretariat entrance"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Create a session first
        user_id = "test_user_5"
        if user_id not in assistant_service.users:
            user = User(
                user_id=user_id,
                username="Test User 5",
                email="test5@example.com",
                preferred_entrance=EntranceType.SECRETARIAT,
                preferences=UserPreference(
                    preferred_entrance=EntranceType.SECRETARIAT,
                    language="en-US",
                    theme="light",
                    notification_enabled=True,
                    auto_transparency=False,
                    detail_level="comprehensive"
                )
            )
            assistant_service.users[user_id] = user
        
        # Mock the entrance selector to return SECRETARIAT
        with patch.object(assistant_service.entrance_selector, 'select_entrance', AsyncMock(return_value=EntranceType.SECRETARIAT)):
            # Mock the create_session method to return a predefined value
            assistant_service.secretariat_use_case.create_session = AsyncMock(return_value=Mock(session_id="test_session"))
            
            context = {}
            session_info = await assistant_service.create_session(user_id, context)
            session_id = session_info["session_id"]
            
            # Mock the session aggregate
            mock_session_aggregate = Mock()
            mock_session_aggregate.session_id = session_id
            mock_session_aggregate.user_id = user_id
            mock_session_aggregate.entrance_type = EntranceType.SECRETARIAT
            
            # Mock the session object within the aggregate
            mock_session = Mock()
            mock_session.status.value = "active"
            mock_session.created_at = datetime.now()
            mock_session.updated_at = datetime.now()
            mock_session_aggregate.session = mock_session
            
            # Mock methods
            mock_session_aggregate.get_duration = Mock(return_value=10.0)
            mock_session_aggregate.get_task_count = Mock(return_value=2)
            mock_session_aggregate.messages = ["message1", "message2"]
            
            # Mock tasks
            mock_task1 = Mock()
            mock_task1.status = TaskStatus.COMPLETED
            mock_task2 = Mock()
            mock_task2.status = TaskStatus.RUNNING
            mock_session_aggregate.tasks = [mock_task1, mock_task2]
            
            assistant_service.sessions[session_id] = mock_session_aggregate
            
            # Get session status
            status = await assistant_service.get_session_status(session_id)
            
            assert isinstance(status, dict)
            assert "session_id" in status
            assert "user_id" in status
            assert "entrance_type" in status
            assert "status" in status
            assert "completed_tasks" in status
            assert "running_tasks" in status
            assert "pending_tasks" in status
            assert status["session_id"] == session_id
            assert status["user_id"] == user_id
            assert status["entrance_type"] == "secretariat"
    
    @pytest.mark.asyncio
    async def test_get_session_status_forum(self, assistant_service):
        """Test getting session status for Forum entrance"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Create a session first
        user_id = "test_user_6"
        if user_id not in assistant_service.users:
            user = User(
                user_id=user_id,
                username="Test User 6",
                email="test6@example.com",
                preferred_entrance=EntranceType.FORUM,
                preferences=UserPreference(
                    preferred_entrance=EntranceType.FORUM,
                    language="en-US",
                    theme="light",
                    notification_enabled=True,
                    auto_transparency=False,
                    detail_level="comprehensive"
                )
            )
            assistant_service.users[user_id] = user
        
        # Mock the entrance selector to return FORUM
        with patch.object(assistant_service.entrance_selector, 'select_entrance', AsyncMock(return_value=EntranceType.FORUM)):
            # Mock the create_session method to return a predefined value
            assistant_service.forum_use_case.create_forum_session = AsyncMock(return_value=Mock(session_id="test_session"))
            
            context = {"topic": "Test topic"}
            session_info = await assistant_service.create_session(user_id, context)
            session_id = session_info["session_id"]
            
            # Mock the session aggregate
            mock_session_aggregate = Mock()
            mock_session_aggregate.session_id = session_id
            mock_session_aggregate.user_id = user_id
            mock_session_aggregate.entrance_type = EntranceType.FORUM
            
            # Mock the session object within the aggregate
            mock_session = Mock()
            mock_session.status.value = "active"
            mock_session.created_at = datetime.now()
            mock_session.updated_at = datetime.now()
            mock_session_aggregate.session = mock_session
            
            # Mock methods
            mock_session_aggregate.get_duration = Mock(return_value=15.0)
            mock_session_aggregate.get_task_count = Mock(return_value=0)
            mock_session_aggregate.messages = ["message1", "message2", "message3"]
            
            # Mock debate
            mock_debate = Mock()
            mock_debate.debate_id = "test_debate"
            mock_debate.topic = "Test topic"
            mock_debate.status = "active"
            mock_debate.participants = ["user1", "user2"]
            mock_debate.messages = ["message1", "message2", "message3"]
            mock_session_aggregate.debate = mock_debate
            
            assistant_service.sessions[session_id] = mock_session_aggregate
            
            # Mock consensus tracker
            with patch.object(assistant_service.consensus_tracker, 'calculate_consensus', AsyncMock(return_value=ConsensusLevel(0.6))):
                # Get session status
                status = await assistant_service.get_session_status(session_id)
                
                assert isinstance(status, dict)
                assert "session_id" in status
                assert "user_id" in status
                assert "entrance_type" in status
                assert "status" in status
                assert "debate_id" in status
                assert "debate_topic" in status
                assert "consensus_level" in status
                assert status["session_id"] == session_id
                assert status["user_id"] == user_id
                assert status["entrance_type"] == "forum"
                assert status["debate_id"] == "test_debate"
    
    @pytest.mark.asyncio
    async def test_get_session_status_not_found(self, assistant_service):
        """Test getting session status for non-existent session"""
        # First initialize the service
        if not assistant_service.is_initialized:
            await assistant_service.initialize()
        
        # Try to get status for non-existent session
        with pytest.raises(ValueError, match="Session nonexistent_session not found"):
            await assistant_service.get_session_status("nonexistent_session")