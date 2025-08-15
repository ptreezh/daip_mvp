# KIRO Specification: Personal Intelligence Hub - Dual-Entrance System

**Document Status:** Final - Ready for Implementation
**Version:** 1.0
**Date:** 2025-08-06

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Product Vision](#product-vision)
3. [Key Input](#key-input)
4. [Requirements](#requirements)
5. [Output](#output)
6. [User Personas & Journey Maps](#user-personas--journey-maps)
7. [Technical Architecture](#technical-architecture)
8. [UI/UX Specifications](#uiux-specifications)
9. [API Contracts & Data Models](#api-contracts--data-models)
10. [Implementation Phases](#implementation-phases)
11. [Testing Strategy](#testing-strategy)
12. [Integration Points](#integration-points)
13. [Success Metrics](#success-metrics)
14. [Risk Assessment](#risk-assessment)

---

## Executive Summary

The Personal Intelligence Hub (PIH) introduces a revolutionary dual-entrance interface paradigm that accommodates diverse user interaction preferences while maintaining a unified backend powered by DAIP's institutional primitives. This specification outlines the implementation of "The Secretariat" (streamlined, result-oriented) and "The Forum" (interactive, process-oriented) entrances, enabling users to engage with AI-powered collaborative intelligence through their preferred interaction style.

---

## Product Vision

### Vision Statement
Create an intelligent collaboration platform that adapts to user preferences, providing both streamlined efficiency and interactive transparency through a unified dual-entrance architecture.

### Core Objectives
1. **User-Centric Design**: Accommodate both efficiency-seeking and engagement-seeking users
2. **Unified Backend**: Leverage existing DAIP institutional primitives for consistency
3. **Seamless Experience**: Enable fluid transition between entrances without losing context
4. **Scalable Architecture**: Support future enhancements and additional entrance types

### Key Differentiators
- **Adaptive Interface**: Dynamic UI adjustment based on user behavior and preferences
- **Transparent AI**: On-demand visibility into AI decision-making processes
- **Collaborative Intelligence**: Multi-agent consensus building with human oversight
- **Context Awareness**: Persistent context across sessions and entrance types

---

## Key Input

### User Requirements Analysis
Based on comprehensive user research and the UserCase.txt requirements, we've identified two primary user archetypes:

#### Efficiency-Seeking Users
- **Primary Need**: Quick results with minimal interaction
- **Behavior Pattern**: State request → Receive outcome → Continue workflow
- **Pain Points**: Complex interfaces, unnecessary process visibility
- **Success Metric**: Task completion time and accuracy

#### Engagement-Seeking Users
- **Primary Need**: Understanding and influencing the AI process
- **Behavior Pattern**: Engage → Observe → Intervene → Collaborate
- **Pain Points**: Black-box AI systems, limited control over process
- **Success Metric**: Perceived control and understanding

### Technical Constraints
- **Platform**: Lona Web Application framework
- **Communication**: WebSocket-based real-time updates
- **Backend**: Existing DAIP institutional primitives
- **Deployment**: Self-contained with minimal external dependencies

---

## Requirements

### REQ-GLOBAL-001: Dual-Entrance Architecture
**Description**: Implement a dual-entrance user interface system supporting both efficiency-oriented and engagement-oriented interaction paradigms.

**Acceptance Criteria**:
- Users can select their preferred entrance type on first visit
- System maintains user preference across sessions
- Both entrances share the same backend services
- Context preservation when switching between entrances

### REQ-GLOBAL-002: Unified Backend Integration
**Description**: Integrate both entrances with existing DAIP institutional primitives through a unified service layer.

**Acceptance Criteria**:
- Leverage existing WorkflowEngine for task orchestration
- Utilize MultiAgentCollaborationSystem for AI agent interactions
- Integrate with SynthesisEngine for consensus building
- Maintain compatibility with existing MemoryService and WikiService

### REQ-GLOBAL-003: Real-time Communication
**Description**: Implement WebSocket-based real-time communication between frontend and backend services.

**Acceptance Criteria**:
- Sub-second latency for user interactions
- Automatic reconnection on connection loss
- Message queuing for offline scenarios
- Bidirectional communication support

---

## Entrance 1: The Secretariat (SEC-REQ)

### SEC-REQ-001: Minimalist Interface Design
**Description**: Clean, uncluttered chat-style interface prioritizing simplicity and focus.

**Technical Specifications**:
- Single-pane layout with message history
- Bottom-aligned input field with send button
- Context-aware "Show Process" toggle
- Responsive design for all screen sizes

**UI Components**:
- `ChatInterface` component for message display
- `MessageInput` component for user input
- `ProcessToggle` component for transparency control
- `MessageRenderer` for formatted message display

### SEC-REQ-002: Automated Task Execution
**Description**: Automatically execute institutional primitive workflows based on user intent.

**Workflow Integration**:
```python
# Secretariat workflow mapping
WORKFLOW_MAP = {
    "expert_consultation": "CRITICAL_REVIEW",
    "academic_research": "MULTI_PERSPECTIVE", 
    "industry_analysis": "MULTI_PERSPECTIVE",
    "casual_discussion": "SIMPLE_CHAT"
}
```

**Execution Sequence**:
1. Intent parsing via `IntentAnalysisService`
2. Expert team formation via `ExpertService`
3. Workflow execution via `WorkflowEngine`
4. Result synthesis via `SynthesisEngine`
5. Report generation via `ReportGenerationService`

### SEC-REQ-003: On-Demand Transparency
**Description**: Provide mechanism for users to view underlying process execution details.

**Transparency Features**:
- Workflow execution timeline
- Agent contributions and reasoning
- Consensus building process
- Knowledge retrieval and validation
- Performance metrics and token usage

**Implementation Approach**:
- Background process monitoring via `MonitorProcess` primitive
- Intelligent summarization for user-friendly display
- Progressive disclosure of technical details

---

## Entrance 2: The Forum (FORUM-REQ)

### FORUM-REQ-001: Interactive Debate Interface
**Description**: Multi-pane interface facilitating real-time multi-agent collaboration with user participation.

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│                     Forum Header                            │
├─────────────────────┬─────────────────────┬───────────────────┤
│   Agent Dialogue   │   User Input        │   Context Panel   │
│   Stream           │   Panel             │                   │
│                     │                     │                   │
│  • Agent Messages  │  • Intent Type      │  • Topic Summary  │
│  • User Messages   │  • Input Field      │  • Consensus      │
│  • Reasoning       │  • Optimization     │  • Key Arguments  │
│  • Timestamps      │  • Preview          │  • Status         │
│                     │                     │                   │
└─────────────────────┴─────────────────────┴───────────────────┘
```

### FORUM-REQ-002: User Intervention System
**Description**: Enable users to directly participate in AI discussions and influence decision-making.

**Intervention Types**:
- **Direct Contribution**: Add arguments and perspectives
- **Targeted Questions**: Ask specific agents for clarification
- **Process Guidance**: Redirect discussion focus
- **Consensus Challenge**: Question emerging consensus

**Input Optimization**:
```python
class UserInputOptimizer:
    def optimize_input(self, raw_input: str, intent_type: str) -> OptimizedInput:
        # Clarify intent and refine phrasing
        # Add context and structure
        # Enhance for AI understanding
        pass
```

### FORUM-REQ-003: Real-time Dynamics Display
**Description**: Show real-time information about discussion progress and consensus formation.

**Visualization Components**:
- **Consensus Meter**: Visual representation of agreement level
- **Contribution Graph**: Agent and user participation metrics
- **Argument Map**: Visual representation of discussion threads
- **Timeline View**: Sequential progression of debate

---

## Technical Architecture

### System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    Personal Intelligence Hub                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   The Forum     │    │ The Secretariat │                │
│  │   (Interactive) │    │  (Streamlined)  │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           └───────────────────────┘                        │
│                    │                                        │
│  ┌─────────────────────────────────────────────────┐      │
│  │           Entrance Manager                      │      │
│  │  • Entrance Selection                          │      │
│  │  • Context Preservation                        │      │
│  │  • UI Component Routing                         │      │
│  └─────────────────────────────────────────────────┘      │
│                    │                                        │
│  ┌─────────────────────────────────────────────────┐      │
│  │        WebSocket Manager                        │      │
│  │  • Real-time Communication                     │      │
│  │  • Message Routing                             │      │
│  │  • Connection Management                       │      │
│  └─────────────────────────────────────────────────┘      │
│                    │                                        │
│  ┌─────────────────────────────────────────────────┐      │
│  │        Personal Intelligence Service            │      │
│  │  • Intent Analysis                             │      │
│  │  • Workflow Orchestration                       │      │
│  │  • Multi-Agent Coordination                     │      │
│  └─────────────────────────────────────────────────┘      │
│                    │                                        │
│  ┌─────────────────────────────────────────────────┐      │
│  │          DAIP Core Services                     │      │
│  │  • WorkflowEngine                              │      │
│  │  • MultiAgentCollaborationSystem               │      │
│  │  • SynthesisEngine                             │      │
│  │  • MemoryService                              │      │
│  │  • ExpertService                              │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Entrance Manager
```python
class EntranceManager:
    """Manages entrance selection and context preservation"""
    
    def __init__(self):
        self.user_preferences = {}
        self.active_sessions = {}
        self.context_preserver = ContextPreserver()
    
    async def select_entrance(self, user_id: str, entrance_type: EntranceType) -> EntranceConfig:
        """Configure entrance based on user preference"""
        pass
    
    async def preserve_context(self, session_id: str, context_data: Dict[str, Any]) -> None:
        """Preserve context when switching entrances"""
        pass
```

#### 2. WebSocket Manager
```python
class WebSocketManager:
    """Handles real-time communication"""
    
    def __init__(self):
        self.connections = {}
        self.message_queue = asyncio.Queue()
        self.connection_manager = ConnectionManager()
    
    async def register_connection(self, session_id: str, websocket: WebSocket) -> None:
        """Register new WebSocket connection"""
        pass
    
    async def send_message(self, message: WebSocketMessage) -> None:
        """Send message to specific session"""
        pass
    
    async def broadcast_message(self, message: WebSocketMessage) -> None:
        """Broadcast message to all sessions"""
        pass
```

#### 3. Personal Intelligence Service
```python
class PersonalIntelligenceService:
    """Core service coordinating all backend operations"""
    
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        self.intent_analyzer = IntentAnalysisService(app_state)
        self.workflow_orchestrator = WorkflowOrchestrator(app_state)
        self.multi_agent_coordinator = MultiAgentCoordinator(app_state)
    
    async def process_request(self, request: UserRequest) -> HubResponse:
        """Process user request through appropriate pipeline"""
        pass
    
    async def get_transparency_data(self, session_id: str) -> TransparencyData:
        """Get transparency data for process visualization"""
        pass
```

### Data Models

#### Core Data Structures
```python
@dataclass
class UserRequest:
    request_id: str
    user_id: str
    content: str
    entrance_type: EntranceType
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1

@dataclass
class HubResponse:
    response_id: str
    request_id: str
    entrance_type: EntranceType
    intent_type: IntentType
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    session_id: Optional[str] = None

@dataclass
class TransparencyData:
    workflow_steps: List[WorkflowStep]
    agent_contributions: List[AgentContribution]
    consensus_metrics: ConsensusMetrics
    performance_data: PerformanceData
    knowledge_sources: List[KnowledgeSource]
```

---

## UI/UX Specifications

### The Secretariat UI Components

#### ChatInterface Component
```python
class SecretariatChatInterface(Widget):
    """Main chat interface for The Secretariat"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[ChatMessage] = []
        self.process_monitor = ProcessMonitor()
        
        # UI Elements
        self.message_history = Div(_class="message-history")
        self.input_field = TextInput(placeholder="Enter your request...")
        self.send_button = Button("Send", _class="btn-primary")
        self.process_toggle = Button("Show Process", _class="btn-secondary", visible=False)
        
        # Event Handlers
        self.send_button.handle_click(self.on_send_message)
        self.process_toggle.handle_click(self.on_toggle_process)
    
    async def on_send_message(self, event):
        """Handle message send"""
        pass
    
    async def on_toggle_process(self, event):
        """Toggle process transparency"""
        pass
    
    def render(self):
        """Render the chat interface"""
        return Div(
            self.message_history,
            Div(
                self.input_field,
                self.send_button,
                self.process_toggle,
                _class="input-area"
            ),
            _class="secretariat-chat"
        )
```

#### ProcessMonitor Component
```python
class ProcessMonitor(Widget):
    """Displays process transparency data"""
    
    def __init__(self):
        self.visible = False
        self.process_data: Optional[TransparencyData] = None
        self.detail_level = "summary"  # summary, detailed, technical
    
    def set_process_data(self, data: TransparencyData):
        """Set process data for display"""
        self.process_data = data
    
    def set_detail_level(self, level: str):
        """Set detail display level"""
        self.detail_level = level
    
    def render(self):
        """Render process monitor"""
        if not self.visible or not self.process_data:
            return Div()
        
        return Div(
            self._render_workflow_timeline(),
            self._render_agent_contributions(),
            self._render_consensus_metrics(),
            _class="process-monitor"
        )
```

### The Forum UI Components

#### ForumInterface Component
```python
class ForumInterface(Widget):
    """Main forum interface for interactive debates"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.dialogue_stream = DialogueStream()
        self.user_input_panel = UserInputPanel()
        self.context_panel = ContextPanel()
        
        # Forum controls
        self.pause_button = Button("⏸️ Pause", _class="control-button")
        self.resume_button = Button("▶️ Resume", _class="control-button", visible=False)
        
        # Event Handlers
        self.pause_button.handle_click(self.on_pause_discussion)
        self.resume_button.handle_click(self.on_resume_discussion)
    
    async def on_pause_discussion(self, event):
        """Pause the discussion"""
        pass
    
    async def on_resume_discussion(self, event):
        """Resume the discussion"""
        pass
    
    def render(self):
        """Render the forum interface"""
        return Div(
            Div(
                self.dialogue_stream,
                _class="dialogue-column"
            ),
            Div(
                self.user_input_panel,
                _class="input-column"
            ),
            Div(
                self.context_panel,
                Div(
                    self.pause_button,
                    self.resume_button,
                    _class="forum-controls"
                ),
                _class="context-column"
            ),
            _class="forum-interface"
        )
```

#### DialogueStream Component
```python
class DialogueStream(Widget):
    """Displays real-time agent and user dialogue"""
    
    def __init__(self):
        self.messages: List[ForumMessage] = []
        self.auto_scroll = True
        self.show_reasoning = False
    
    def add_message(self, message: ForumMessage):
        """Add new message to stream"""
        self.messages.append(message)
    
    def toggle_reasoning(self):
        """Toggle reasoning display"""
        self.show_reasoning = not self.show_reasoning
    
    def render(self):
        """Render dialogue stream"""
        return Div(
            *[self._render_message(msg) for msg in self.messages],
            _class="dialogue-stream"
        )
```

### CSS Styling

#### Secretariat Styles
```css
/* Secretariat Chat Interface */
.secretariat-chat {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #f8f9fa;
}

.message-history {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.message {
    margin-bottom: 15px;
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 70%;
}

.message.user {
    background: #007bff;
    color: white;
    margin-left: auto;
}

.message.assistant {
    background: white;
    color: #333;
    border: 1px solid #e9ecef;
}

.input-area {
    display: flex;
    padding: 20px;
    background: white;
    border-top: 1px solid #e9ecef;
}

.process-monitor {
    position: fixed;
    right: 20px;
    top: 20px;
    width: 400px;
    max-height: 80vh;
    background: white;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}
```

#### Forum Styles
```css
/* Forum Interface */
.forum-interface {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    height: 100vh;
    gap: 1px;
    background: #e9ecef;
}

.dialogue-column {
    background: white;
    display: flex;
    flex-direction: column;
}

.input-column {
    background: #f8f9fa;
    display: flex;
    flex-direction: column;
    padding: 20px;
}

.context-column {
    background: white;
    display: flex;
    flex-direction: column;
    padding: 20px;
}

.forum-message {
    margin-bottom: 12px;
    padding: 10px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
}

.forum-message.user {
    border-left-color: #28a745;
    background: #f8f9fa;
}

.forum-controls {
    display: flex;
    gap: 10px;
    margin-top: auto;
    padding-top: 20px;
}

.control-button {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}
```

---

## API Contracts & Data Models

### WebSocket Message Protocol

#### Message Types
```python
class WebSocketMessageType(str, Enum):
    # Core Messages
    USER_MESSAGE = "user_message"
    ASSISTANT_RESPONSE = "assistant_response"
    SYSTEM_NOTIFICATION = "system_notification"
    
    # Forum Messages
    AGENT_MESSAGE = "agent_message"
    CONSENSUS_UPDATE = "consensus_update"
    DISCUSSION_STATUS = "discussion_status"
    
    # Process Messages
    WORKFLOW_STATUS = "workflow_status"
    TRANSPARENCY_DATA = "transparency_data"
    PERFORMANCE_METRICS = "performance_metrics"
    
    # Control Messages
    SESSION_CONTROL = "session_control"
    ENTRANCE_SWITCH = "entrance_switch"
    ERROR_MESSAGE = "error_message"
```

#### Message Structure
```python
@dataclass
class WebSocketMessage:
    type: WebSocketMessageType
    payload: Dict[str, Any]
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_json(self) -> str:
        """Convert message to JSON"""
        return json.dumps({
            "type": self.type.value,
            "payload": self.payload,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        """Create message from JSON"""
        data = json.loads(json_str)
        return cls(
            type=WebSocketMessageType(data["type"]),
            payload=data["payload"],
            session_id=data["session_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data["message_id"]
        )
```

### REST API Endpoints

#### Session Management
```python
# Session Management
@app.post("/api/v1/sessions")
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    """Create new session"""
    pass

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str) -> SessionResponse:
    """Get session details"""
    pass

@app.put("/api/v1/sessions/{session_id}/entrance")
async def switch_entrance(session_id: str, request: EntranceSwitchRequest) -> SessionResponse:
    """Switch entrance type"""
    pass
```

#### Request Processing
```python
@app.post("/api/v1/process")
async def process_request(request: ProcessRequest) -> ProcessResponse:
    """Process user request"""
    pass

@app.get("/api/v1/process/{process_id}/status")
async def get_process_status(process_id: str) -> ProcessStatusResponse:
    """Get process status"""
    pass

@app.get("/api/v1/process/{process_id}/transparency")
async def get_transparency_data(process_id: str) -> TransparencyResponse:
    """Get transparency data"""
    pass
```

#### Configuration Management
```python
@app.get("/api/v1/config/entrances")
async def get_entrance_config() -> EntranceConfigResponse:
    """Get entrance configuration"""
    pass

@app.put("/api/v1/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, request: UserPreferencesRequest) -> UserPreferencesResponse:
    """Update user preferences"""
    pass
```

### Request/Response Models

#### Core Models
```python
@dataclass
class SessionCreateRequest:
    user_id: str
    entrance_type: EntranceType
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionResponse:
    session_id: str
    user_id: str
    entrance_type: EntranceType
    status: str
    created_at: datetime
    expires_at: datetime

@dataclass
class ProcessRequest:
    session_id: str
    content: str
    request_type: str
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessResponse:
    process_id: str
    session_id: str
    status: str
    estimated_duration: int
    created_at: datetime
```

---

## Implementation Phases

### Phase 1: Core Foundation (Weeks 1-2)
**Objective**: Establish basic infrastructure and Secretariat functionality

#### Tasks:
1. **Infrastructure Setup**
   - WebSocket manager implementation
   - Entrance manager development
   - Base UI components creation

2. **Secretariat Implementation**
   - Basic chat interface
   - Message processing pipeline
   - Simple workflow integration

3. **Core Services Integration**
   - Intent analysis service integration
   - Basic workflow execution
   - Memory service integration

#### Deliverables:
- Functional Secretariat entrance
- WebSocket communication system
- Basic process monitoring
- Core API endpoints

#### Success Criteria:
- Users can send messages and receive responses
- Basic workflow execution works
- WebSocket connection is stable
- Performance: <2s response time for simple queries

### Phase 2: Forum Foundation (Weeks 3-4)
**Objective**: Implement Forum interface and real-time features

#### Tasks:
1. **Forum Interface Development**
   - Multi-pane layout implementation
   - Real-time message streaming
   - User input optimization

2. **Multi-Agent Integration**
   - Real-time agent communication
   - Consensus building visualization
   - User intervention system

3. **Advanced Features**
   - Discussion controls (pause/resume)
   - Context panel implementation
   - Performance monitoring

#### Deliverables:
- Functional Forum entrance
- Real-time agent communication
- User intervention capabilities
- Discussion management controls

#### Success Criteria:
- Real-time message streaming works
- Users can intervene in discussions
- Consensus visualization is accurate
- Performance: <500ms latency for real-time updates

### Phase 3: Enhanced Features (Weeks 5-6)
**Objective**: Implement advanced features and optimization

#### Tasks:
1. **Transparency System**
   - Detailed process monitoring
   - Intelligent summarization
   - Multi-level detail views

2. **Context Preservation**
   - Cross-entrance context sharing
   - Session persistence
   - User preference learning

3. **Performance Optimization**
   - Caching strategies
   - Connection pooling
   - Message queuing optimization

#### Deliverables:
- Complete transparency system
- Seamless entrance switching
- Optimized performance
- User preference system

#### Success Criteria:
- Context preservation works across entrances
- Transparency data is comprehensive
- Performance meets targets
- User satisfaction >80%

### Phase 4: Polish & Testing (Weeks 7-8)
**Objective**: Final polish, testing, and documentation

#### Tasks:
1. **UI/UX Refinement**
   - Responsive design optimization
   - Accessibility improvements
   - Visual design polish

2. **Testing & Quality Assurance**
   - Comprehensive testing suite
   - Performance benchmarking
   - Security testing

3. **Documentation & Deployment**
   - API documentation
   - User guides
   - Deployment automation

#### Deliverables:
- Production-ready system
- Complete documentation
- Test coverage >90%
- Deployment automation

#### Success Criteria:
- All tests pass
- Documentation is complete
- System is production-ready
- Performance benchmarks met

---

## Testing Strategy

### Testing Framework
```python
# Test framework setup
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from testing.websocket_client import WebSocketTestClient
from testing.api_client import APITestClient

@pytest.fixture
def test_app():
    """Test application fixture"""
    app = create_test_app()
    yield app
    cleanup_test_app(app)

@pytest.fixture
def websocket_client():
    """WebSocket test client"""
    return WebSocketTestClient()

@pytest.fixture
def api_client():
    """API test client"""
    return APITestClient()
```

### Unit Tests

#### Entrance Manager Tests
```python
class TestEntranceManager:
    def test_entrance_selection(self, test_app):
        """Test entrance selection logic"""
        manager = EntranceManager()
        config = manager.select_entrance("user1", EntranceType.SECRETARIAT)
        assert config.entrance_type == EntranceType.SECRETARIAT
    
    def test_context_preservation(self, test_app):
        """Test context preservation across entrances"""
        manager = EntranceManager()
        context = {"session_id": "test123", "user_id": "user1"}
        asyncio.run(manager.preserve_context("test123", context))
        # Verify context is preserved
```

#### WebSocket Manager Tests
```python
class TestWebSocketManager:
    async def test_connection_registration(self, websocket_client):
        """Test WebSocket connection registration"""
        manager = WebSocketManager()
        websocket = Mock()
        await manager.register_connection("test123", websocket)
        assert "test123" in manager.connections
    
    async def test_message_routing(self, websocket_client):
        """Test message routing to specific sessions"""
        manager = WebSocketManager()
        message = WebSocketMessage(
            type=WebSocketMessageType.USER_MESSAGE,
            payload={"content": "test"},
            session_id="test123"
        )
        await manager.send_message(message)
        # Verify message is routed correctly
```

### Integration Tests

#### End-to-End Secretariat Tests
```python
class TestSecretariatIntegration:
    async def test_complete_secretariat_workflow(self, test_app):
        """Test complete Secretariat workflow"""
        # 1. Create session
        # 2. Send message
        # 3. Process workflow
        # 4. Receive response
        # 5. Verify transparency data
        pass
    
    async def test_transparency_toggle(self, test_app):
        """Test transparency toggle functionality"""
        # 1. Start task
        # 2. Toggle transparency
        # 3. Verify process data
        pass
```

#### End-to-End Forum Tests
```python
class TestForumIntegration:
    async def test_forum_discussion(self, test_app):
        """Test complete Forum discussion"""
        # 1. Start discussion
        # 2. Add user input
        # 3. Verify agent responses
        # 4. Check consensus building
        pass
    
    async def test_user_intervention(self, test_app):
        """Test user intervention capabilities"""
        # 1. Start agent discussion
        # 2. User intervenes
        # 3. Verify discussion changes
        pass
```

### Performance Tests

#### Load Testing
```python
class TestPerformance:
    async def test_concurrent_users(self, test_app):
        """Test concurrent user handling"""
        # Simulate 100 concurrent users
        # Measure response times
        # Verify system stability
        pass
    
    async def test_message_throughput(self, test_app):
        """Test message throughput"""
        # Send 1000 messages
        # Measure processing time
        # Verify no message loss
        pass
```

### Security Tests

#### Authentication & Authorization
```python
class TestSecurity:
    def test_session_authentication(self, test_app):
        """Test session authentication"""
        # Verify unauthenticated requests are rejected
        # Verify session validation works
        pass
    
    def test_input_sanitization(self, test_app):
        """Test input sanitization"""
        # Test malicious input handling
        # Verify XSS prevention
        pass
```

---

## Integration Points

### Existing DAIP Services Integration

#### 1. WorkflowEngine Integration
```python
class WorkflowOrchestrator:
    """Integrates with existing WorkflowEngine"""
    
    def __init__(self, workflow_engine: WorkflowEngine):
        self.workflow_engine = workflow_engine
        self.workflow_templates = self._load_workflow_templates()
    
    async def execute_workflow(self, workflow_type: str, context: Dict[str, Any]) -> WorkflowResult:
        """Execute workflow through existing engine"""
        template = self.workflow_templates.get(workflow_type)
        if not template:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        # Execute workflow using existing engine
        result = await self.workflow_engine.execute_workflow(template, context)
        return result
```

#### 2. MultiAgentCollaborationSystem Integration
```python
class MultiAgentCoordinator:
    """Integrates with existing MultiAgentCollaborationSystem"""
    
    def __init__(self, collaboration_system: MultiAgentCollaborationSystem):
        self.collaboration_system = collaboration_system
    
    async def start_collaboration(self, request: UserRequest) -> CollaborationSession:
        """Start multi-agent collaboration"""
        session = await self.collaboration_system.create_session(
            topic=request.content,
            mode=self._map_intent_to_mode(request.intent_type),
            context=request.context
        )
        return session
    
    async def add_user_intervention(self, session_id: str, intervention: UserIntervention) -> None:
        """Add user intervention to ongoing collaboration"""
        await self.collaboration_system.add_user_input(session_id, intervention)
```

#### 3. MemoryService Integration
```python
class ContextManager:
    """Integrates with existing MemoryService"""
    
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
    
    async def preserve_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Preserve context in memory service"""
        await self.memory_service.store_session_context(session_id, context)
    
    async def retrieve_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve context from memory service"""
        return await self.memory_service.get_session_context(session_id)
```

### Frontend Integration

#### 1. Lona Web Application Integration
```python
# main.py - Lona application entry point
from lona import LonaApp
from lona.html import HTML, Div
from frontend.entrances import SecretariatInterface, ForumInterface

app = LonaApp(__name__)

@app.route('/')
async def index(request):
    """Main entry point"""
    session_id = request.client.get('session_id')
    entrance_type = request.client.get('entrance_type', 'secretariat')
    
    if entrance_type == 'secretariat':
        return SecretariatInterface(session_id)
    else:
        return ForumInterface(session_id)

if __name__ == '__main__':
    app.run()
```

#### 2. WebSocket Integration
```python
# websocket_handler.py
async def websocket_handler(websocket, path):
    """Handle WebSocket connections"""
    session_id = await authenticate_websocket(websocket)
    
    try:
        # Register connection
        await websocket_manager.register_connection(session_id, websocket)
        
        # Handle incoming messages
        async for message in websocket:
            data = json.loads(message)
            await process_websocket_message(session_id, data)
            
    except WebSocketDisconnect:
        # Handle disconnection
        await websocket_manager.unregister_connection(session_id)
```

### External Service Integration

#### 1. LLM Service Integration
```python
class LLMServiceIntegration:
    """Integrates with LLM services"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm_interface = llm_interface
    
    async def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response using LLM service"""
        response = await self.llm_interface.generate_text(
            prompt=prompt,
            context=context,
            max_tokens=1000
        )
        return response
```

#### 2. Vector Store Integration
```python
class VectorStoreIntegration:
    """Integrates with vector store for knowledge retrieval"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    async def retrieve_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeSource]:
        """Retrieve relevant knowledge"""
        results = await self.vector_store.similarity_search(query, limit=limit)
        return results
```

---

## Success Metrics

### User Experience Metrics

#### 1. Engagement Metrics
- **Session Duration**: Target average of 15+ minutes per session
- **Return Rate**: 40% of users return within 7 days
- **Feature Adoption**: 80% of users try both entrance types
- **Task Completion**: 90% success rate for user-initiated tasks

#### 2. Satisfaction Metrics
- **User Satisfaction Score**: Target 4.5/5.0
- **Net Promoter Score**: Target +40
- **Customer Effort Score**: Target <2.0 (low effort)
- **Interface Preference**: Balanced usage between entrances

### Technical Metrics

#### 1. Performance Metrics
- **Response Time**: <2s for simple queries, <10s for complex workflows
- **Throughput**: 1000+ concurrent users
- **Uptime**: 99.9% availability
- **Error Rate**: <0.1% of requests

#### 2. System Metrics
- **Memory Usage**: <512MB per active session
- **CPU Usage**: <70% under normal load
- **Database Response**: <100ms for queries
- **WebSocket Latency**: <500ms for real-time updates

### Business Metrics

#### 1. Adoption Metrics
- **User Growth**: 20% month-over-month growth
- **Active Users**: 1000+ daily active users
- **Feature Usage**: 60% of users use advanced features
- **Integration Usage**: 50% of users integrate with external tools

#### 2. Value Metrics
- **Productivity Gain**: 30% reduction in task completion time
- **Decision Quality**: 25% improvement in decision outcomes
- **Knowledge Access**: 40% increase in knowledge utilization
- **Collaboration**: 50% increase in collaborative activities

---

## Risk Assessment

### Technical Risks

#### 1. Performance Risk
**Risk**: System may not handle expected load under peak usage
**Mitigation**:
- Implement horizontal scaling
- Use connection pooling
- Optimize database queries
- Implement caching strategies

#### 2. Real-time Communication Risk
**Risk**: WebSocket connections may be unstable under high load
**Mitigation**:
- Implement connection resilience
- Use message queuing
- Add automatic reconnection
- Implement fallback mechanisms

#### 3. Integration Risk
**Risk**: Integration with existing DAIP services may be complex
**Mitigation**:
- Thorough testing of integration points
- Implement adapter patterns
- Create comprehensive API documentation
- Plan for gradual rollout

### User Experience Risks

#### 1. Interface Complexity Risk
**Risk**: Dual-entrance system may confuse users
**Mitigation**:
- Clear onboarding process
- Contextual help and tutorials
- User preference learning
- A/B testing of different approaches

#### 2. Expectation Mismatch Risk
**Risk**: User expectations may not align with system capabilities
**Mitigation**:
- Clear communication of capabilities
- Set realistic expectations
- Provide feedback mechanisms
- Continuous improvement based on feedback

### Business Risks

#### 1. Adoption Risk
**Risk**: Users may not adopt both entrance types
**Mitigation**:
- Incentivize trying both interfaces
- Highlight unique benefits of each entrance
- Provide migration guides
- Monitor usage patterns

#### 2. Resource Risk
**Risk**: Development may require more resources than planned
**Mitigation**:
- Phased implementation approach
- Regular progress reviews
- Resource allocation monitoring
- Contingency planning

---

## Conclusion

The Personal Intelligence Hub dual-entrance system represents a significant advancement in human-AI interaction design. By providing both streamlined efficiency and interactive transparency through a unified backend, the system accommodates diverse user preferences while maintaining consistency and reliability.

The implementation approach outlined in this specification ensures a systematic, phased rollout that minimizes risk while maximizing value. The integration with existing DAIP services leverages institutional knowledge and maintains consistency with the broader ecosystem.

Success will be measured not just by technical performance, but by the system's ability to adapt to user needs and provide meaningful value in their daily workflows. The dual-entrance paradigm establishes a new standard for user-centric AI interaction design.

---

## Appendices

### Appendix A: Technical Architecture Diagrams
[Detailed architecture diagrams to be included]

### Appendix B: API Documentation
[Complete API documentation to be generated]

### Appendix C: User Interface Mockups
[UI mockups and design specifications to be included]

### Appendix D: Test Cases
[Comprehensive test case documentation to be developed]

### Appendix E: Deployment Guide
[Step-by-step deployment instructions to be created]

---

**Document Approval:**

- Product Owner: _________________________
- Technical Lead: _________________________
- UX Designer: _________________________
- QA Lead: _________________________
- Date: _________________________