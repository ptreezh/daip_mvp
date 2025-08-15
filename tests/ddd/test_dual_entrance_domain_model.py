"""@Time    : 2025-08-06 10:00:00
@Author  : DAIP-LIVE Team
@File    : test_dual_entrance_domain_model.py
@Description:
    Domain-Driven Design test cases for the Personal Intelligence Hub dual-entrance system.
    Tests core domain entities, value objects, aggregates, and domain services.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import pytest


# Domain Models
class EntranceType(Enum):
    """Entrance type enumeration - Value Object"""
    SECRETARIAT = "secretariat"
    FORUM = "forum"

class IntentType(Enum):
    """Intent type enumeration - Value Object"""
    EXPERT_CONSULTATION = "expert_consultation"
    ACADEMIC_RESEARCH = "academic_research"
    INDUSTRY_ANALYSIS = "industry_analysis"
    CASUAL_DISCUSSION = "casual_discussion"

class SessionStatus(Enum):
    """Session status enumeration - Value Object"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"

@dataclass
class UserPreferences:
    """User preferences - Value Object"""
    preferred_entrance: EntranceType
    show_transparency: bool = False
    auto_save_context: bool = True
    notification_enabled: bool = True
    
    def __post_init__(self):
        if not isinstance(self.preferred_entrance, EntranceType):
            raise ValueError("Invalid entrance type")

@dataclass
class TransparencyData:
    """Transparency data - Value Object"""
    workflow_steps: list[dict[str, Any]]
    agent_contributions: list[dict[str, Any]]
    consensus_metrics: dict[str, float]
    performance_data: dict[str, Any]
    knowledge_sources: list[dict[str, Any]]
    
    def __post_init__(self):
        if not isinstance(self.workflow_steps, list):
            raise ValueError("Workflow steps must be a list")
        if not isinstance(self.consensus_metrics, dict):
            raise ValueError("Consensus metrics must be a dictionary")

@dataclass
class UserIntervention:
    """User intervention - Value Object"""
    content: str
    intent_type: str
    timestamp: datetime
    session_id: str
    
    def __post_init__(self):
        if not self.content.strip():
            raise ValueError("Intervention content cannot be empty")
        if not self.session_id:
            raise ValueError("Session ID is required")

class UserId:
    """User ID - Value Object"""
    def __init__(self, user_id: str):
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user ID")
        self.value = user_id
    
    def __eq__(self, other):
        return isinstance(other, UserId) and self.value == other.value
    
    def __hash__(self):
        return hash(self.value)

class SessionId:
    """Session ID - Value Object"""
    def __init__(self, session_id: str):
        if not session_id or not isinstance(session_id, str):
            raise ValueError("Invalid session ID")
        self.value = session_id
    
    def __eq__(self, other):
        return isinstance(other, SessionId) and self.value == other.value
    
    def __hash__(self):
        return hash(self.value)

class User:
    """User entity - Aggregate Root"""
    def __init__(self, user_id: UserId, preferences: UserPreferences):
        self.user_id = user_id
        self.preferences = preferences
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.session_history: list[SessionId] = []
    
    def update_preferences(self, preferences: UserPreferences):
        """Update user preferences"""
        self.preferences = preferences
        self.last_active = datetime.now()
    
    def add_session(self, session_id: SessionId):
        """Add session to user history"""
        if session_id not in self.session_history:
            self.session_history.append(session_id)
        self.last_active = datetime.now()
    
    def get_active_sessions(self) -> list[SessionId]:
        """Get active sessions (simplified)"""
        return self.session_history[-5:]  # Last 5 sessions

class Session:
    """Session entity - Aggregate Root"""
    def __init__(self, session_id: SessionId, user_id: UserId, entrance_type: EntranceType):
        self.session_id = session_id
        self.user_id = user_id
        self.entrance_type = entrance_type
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(hours=24)
        self.context: dict[str, Any] = {}
        self.transparency_data: Optional[TransparencyData] = None
        self.interventions: list[UserIntervention] = []
    
    def switch_entrance(self, new_entrance: EntranceType):
        """Switch entrance type"""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError("Cannot switch entrance on inactive session")
        
        # Preserve context before switching
        self._preserve_context()
        self.entrance_type = new_entrance
        self.last_modified = datetime.now()
    
    def add_intervention(self, intervention: UserIntervention):
        """Add user intervention"""
        if intervention.session_id != self.session_id.value:
            raise ValueError("Intervention session ID mismatch")
        
        self.interventions.append(intervention)
        self.last_modified = datetime.now()
    
    def update_transparency_data(self, data: TransparencyData):
        """Update transparency data"""
        self.transparency_data = data
        self.last_modified = datetime.now()
    
    def pause(self):
        """Pause session"""
        if self.status == SessionStatus.ACTIVE:
            self.status = SessionStatus.PAUSED
            self.last_modified = datetime.now()
    
    def resume(self):
        """Resume session"""
        if self.status == SessionStatus.PAUSED:
            self.status = SessionStatus.ACTIVE
            self.last_modified = datetime.now()
    
    def complete(self):
        """Complete session"""
        self.status = SessionStatus.COMPLETED
        self.last_modified = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expires_at
    
    def _preserve_context(self):
        """Preserve context when switching entrances"""
        # Implementation would save current state
        pass

class EntranceManager:
    """Entrance manager - Domain Service"""
    def __init__(self):
        self.active_sessions: dict[SessionId, Session] = {}
        self.user_preferences: dict[UserId, UserPreferences] = {}
    
    def create_session(self, user_id: UserId, entrance_type: EntranceType) -> Session:
        """Create new session"""
        session_id = SessionId(str(uuid.uuid4()))
        
        # Get user preferences or create defaults
        preferences = self.user_preferences.get(user_id, 
            UserPreferences(preferred_entrance=entrance_type))
        
        session = Session(session_id, user_id, entrance_type)
        self.active_sessions[session_id] = session
        
        return session
    
    def get_session(self, session_id: SessionId) -> Optional[Session]:
        """Get session by ID"""
        session = self.active_sessions.get(session_id)
        if session and session.is_expired():
            self.active_sessions.pop(session_id, None)
            return None
        return session
    
    def switch_entrance(self, session_id: SessionId, new_entrance: EntranceType) -> bool:
        """Switch entrance type for session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        try:
            session.switch_entrance(new_entrance)
            return True
        except ValueError:
            return False
    
    def update_user_preferences(self, user_id: UserId, preferences: UserPreferences):
        """Update user preferences"""
        self.user_preferences[user_id] = preferences
    
    def get_user_preferences(self, user_id: UserId) -> UserPreferences:
        """Get user preferences"""
        return self.user_preferences.get(user_id, 
            UserPreferences(preferred_entrance=EntranceType.SECRETARIAT))

# Domain Events
@dataclass
class SessionCreatedEvent:
    """Session created domain event"""
    session_id: SessionId
    user_id: UserId
    entrance_type: EntranceType
    timestamp: datetime

@dataclass
class EntranceSwitchedEvent:
    """Entrance switched domain event"""
    session_id: SessionId
    old_entrance: EntranceType
    new_entrance: EntranceType
    timestamp: datetime

@dataclass
class UserInterventionAddedEvent:
    """User intervention added domain event"""
    session_id: SessionId
    intervention: UserIntervention
    timestamp: datetime

class DomainEventPublisher:
    """Domain event publisher - Domain Service"""
    def __init__(self):
        self.subscribers: dict[str, list] = {}
    
    def subscribe(self, event_type: str, handler):
        """Subscribe to domain events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event):
        """Publish domain event"""
        event_type = event.__class__.__name__
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(event)

# Test Cases
class TestDualEntranceDomainModel:
    """Test suite for dual-entrance domain model"""
    
    def test_user_id_value_object(self):
        """Test User ID value object"""
        # Valid user ID
        user_id = UserId("test_user_123")
        assert user_id.value == "test_user_123"
        
        # Invalid user ID
        with pytest.raises(ValueError):
            UserId("")
        
        with pytest.raises(ValueError):
            UserId(None)
        
        # Equality
        user_id1 = UserId("test_user")
        user_id2 = UserId("test_user")
        assert user_id1 == user_id2
        assert hash(user_id1) == hash(user_id2)
    
    def test_session_id_value_object(self):
        """Test Session ID value object"""
        # Valid session ID
        session_id = SessionId("session_123")
        assert session_id.value == "session_123"
        
        # Invalid session ID
        with pytest.raises(ValueError):
            SessionId("")
        
        with pytest.raises(ValueError):
            SessionId(None)
        
        # Equality
        session_id1 = SessionId("session_123")
        session_id2 = SessionId("session_123")
        assert session_id1 == session_id2
        assert hash(session_id1) == hash(session_id2)
    
    def test_user_preferences_value_object(self):
        """Test User preferences value object"""
        # Valid preferences
        preferences = UserPreferences(
            preferred_entrance=EntranceType.SECRETARIAT,
            show_transparency=True
        )
        assert preferences.preferred_entrance == EntranceType.SECRETARIAT
        assert preferences.show_transparency is True
        
        # Invalid entrance type
        with pytest.raises(ValueError):
            UserPreferences(preferred_entrance="invalid")
    
    def test_transparency_data_value_object(self):
        """Test Transparency data value object"""
        # Valid transparency data
        data = TransparencyData(
            workflow_steps=[{"step": "test"}],
            agent_contributions=[{"agent": "test"}],
            consensus_metrics={"consensus": 0.8},
            performance_data={"time": 1.0},
            knowledge_sources=[{"source": "test"}]
        )
        assert len(data.workflow_steps) == 1
        assert data.consensus_metrics["consensus"] == 0.8
        
        # Invalid workflow steps
        with pytest.raises(ValueError):
            TransparencyData(
                workflow_steps="invalid",
                agent_contributions=[],
                consensus_metrics={},
                performance_data={},
                knowledge_sources=[]
            )
        
        # Invalid consensus metrics
        with pytest.raises(ValueError):
            TransparencyData(
                workflow_steps=[],
                agent_contributions=[],
                consensus_metrics="invalid",
                performance_data={},
                knowledge_sources=[]
            )
    
    def test_user_intervention_value_object(self):
        """Test User intervention value object"""
        # Valid intervention
        intervention = UserIntervention(
            content="Test intervention",
            intent_type="comment",
            timestamp=datetime.now(),
            session_id="session_123"
        )
        assert intervention.content == "Test intervention"
        assert intervention.intent_type == "comment"
        
        # Empty content
        with pytest.raises(ValueError):
            UserIntervention(
                content="",
                intent_type="comment",
                timestamp=datetime.now(),
                session_id="session_123"
            )
        
        # Empty session ID
        with pytest.raises(ValueError):
            UserIntervention(
                content="Test",
                intent_type="comment",
                timestamp=datetime.now(),
                session_id=""
            )
    
    def test_user_entity(self):
        """Test User entity"""
        user_id = UserId("test_user")
        preferences = UserPreferences(preferred_entrance=EntranceType.SECRETARIAT)
        
        user = User(user_id, preferences)
        assert user.user_id == user_id
        assert user.preferences == preferences
        assert len(user.session_history) == 0
        
        # Update preferences
        new_preferences = UserPreferences(preferred_entrance=EntranceType.FORUM)
        user.update_preferences(new_preferences)
        assert user.preferences == new_preferences
        
        # Add session
        session_id = SessionId("session_123")
        user.add_session(session_id)
        assert session_id in user.session_history
        assert len(user.session_history) == 1
        
        # Get active sessions
        active_sessions = user.get_active_sessions()
        assert session_id in active_sessions
    
    def test_session_entity(self):
        """Test Session entity"""
        user_id = UserId("test_user")
        session_id = SessionId("session_123")
        
        session = Session(session_id, user_id, EntranceType.SECRETARIAT)
        assert session.session_id == session_id
        assert session.user_id == user_id
        assert session.entrance_type == EntranceType.SECRETARIAT
        assert session.status == SessionStatus.ACTIVE
        assert len(session.interventions) == 0
        
        # Switch entrance
        session.switch_entrance(EntranceType.FORUM)
        assert session.entrance_type == EntranceType.FORUM
        
        # Add intervention
        intervention = UserIntervention(
            content="Test intervention",
            intent_type="comment",
            timestamp=datetime.now(),
            session_id="session_123"
        )
        session.add_intervention(intervention)
        assert len(session.interventions) == 1
        assert session.interventions[0] == intervention
        
        # Update transparency data
        transparency_data = TransparencyData(
            workflow_steps=[{"step": "test"}],
            agent_contributions=[{"agent": "test"}],
            consensus_metrics={"consensus": 0.8},
            performance_data={"time": 1.0},
            knowledge_sources=[{"source": "test"}]
        )
        session.update_transparency_data(transparency_data)
        assert session.transparency_data == transparency_data
        
        # Pause/resume session
        session.pause()
        assert session.status == SessionStatus.PAUSED
        
        session.resume()
        assert session.status == SessionStatus.ACTIVE
        
        # Complete session
        session.complete()
        assert session.status == SessionStatus.COMPLETED
        
        # Test session expiration
        expired_session = Session(SessionId("expired"), user_id, EntranceType.SECRETARIAT)
        expired_session.expires_at = datetime.now() - timedelta(hours=1)
        assert expired_session.is_expired() is True
    
    def test_entrance_manager_domain_service(self):
        """Test Entrance manager domain service"""
        manager = EntranceManager()
        user_id = UserId("test_user")
        
        # Create session
        session = manager.create_session(user_id, EntranceType.SECRETARIAT)
        assert session.user_id == user_id
        assert session.entrance_type == EntranceType.SECRETARIAT
        assert session.session_id in manager.active_sessions
        
        # Get session
        retrieved_session = manager.get_session(session.session_id)
        assert retrieved_session == session
        
        # Switch entrance
        success = manager.switch_entrance(session.session_id, EntranceType.FORUM)
        assert success is True
        assert session.entrance_type == EntranceType.FORUM
        
        # Update user preferences
        preferences = UserPreferences(preferred_entrance=EntranceType.FORUM)
        manager.update_user_preferences(user_id, preferences)
        
        # Get user preferences
        retrieved_preferences = manager.get_user_preferences(user_id)
        assert retrieved_preferences == preferences
    
    def test_domain_event_publisher(self):
        """Test Domain event publisher"""
        publisher = DomainEventPublisher()
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        # Subscribe to events
        publisher.subscribe("SessionCreatedEvent", event_handler)
        
        # Publish event
        event = SessionCreatedEvent(
            session_id=SessionId("test_session"),
            user_id=UserId("test_user"),
            entrance_type=EntranceType.SECRETARIAT,
            timestamp=datetime.now()
        )
        publisher.publish(event)
        
        # Verify event was received
        assert len(events_received) == 1
        assert events_received[0] == event
    
    def test_session_business_rules(self):
        """Test session business rules"""
        user_id = UserId("test_user")
        session_id = SessionId("session_123")
        
        session = Session(session_id, user_id, EntranceType.SECRETARIAT)
        
        # Cannot switch entrance on inactive session
        session.pause()
        with pytest.raises(ValueError):
            session.switch_entrance(EntranceType.FORUM)
        
        # Cannot add intervention with wrong session ID
        intervention = UserIntervention(
            content="Test",
            intent_type="comment",
            timestamp=datetime.now(),
            session_id="wrong_session"
        )
        with pytest.raises(ValueError):
            session.add_intervention(intervention)
    
    def test_aggregate_boundaries(self):
        """Test aggregate boundaries"""
        user_id = UserId("test_user")
        session_id = SessionId("session_123")
        
        # User is aggregate root for user data
        user = User(user_id, UserPreferences(preferred_entrance=EntranceType.SECRETARIAT))
        
        # Session is aggregate root for session data
        session = Session(session_id, user_id, EntranceType.SECRETARIAT)
        
        # Test that session manages its own interventions
        intervention = UserIntervention(
            content="Test intervention",
            intent_type="comment",
            timestamp=datetime.now(),
            session_id="session_123"
        )
        session.add_intervention(intervention)
        
        # Intervention is part of session aggregate
        assert len(session.interventions) == 1
        assert session.interventions[0].content == "Test intervention"
    
    def test_domain_service_orchestration(self):
        """Test domain service orchestration"""
        manager = EntranceManager()
        user_id = UserId("test_user")
        
        # Create session with default preferences
        session = manager.create_session(user_id, EntranceType.SECRETARIAT)
        
        # Update user preferences
        new_preferences = UserPreferences(
            preferred_entrance=EntranceType.FORUM,
            show_transparency=True
        )
        manager.update_user_preferences(user_id, new_preferences)
        
        # Create new session should use updated preferences
        new_session = manager.create_session(user_id, EntranceType.SECRETARIAT)
        
        # Verify service maintains state correctly
        assert len(manager.active_sessions) == 2
        assert manager.user_preferences[user_id] == new_preferences

if __name__ == "__main__":
    pytest.main([__file__, "-v"])