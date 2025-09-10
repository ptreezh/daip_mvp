# P-AUX-MEMORY: Multi-Agent Session Management Specification

## 1. Overview

This document specifies the design for the **Multi-Agent Session Management Service**. This service is the foundational layer for managing, persisting, and retrieving structured conversations between multiple virtual AI agents (roles) and the human user.

This design supersedes any previous specifications based on a single-agent execution history model. A "Session" is now correctly understood as a container for a multi-participant interaction, such as a debate, a collaborative chat, or a workflow.

## 2. Core Concepts

- **Session**: A container for a single, cohesive interaction. It has a defined type, a list of participants, and a recorded history of the dialogue.
- **Participant**: An entity that contributes to the session. This can be a virtual AI agent (identified by a `role_id`) or the human user (identified by a special `user_id`).
- **Dialogue Turn**: A single entry in the session's history, representing a statement from one participant.

## 3. Data Models

These models will be defined in `p0_core_interfaces` (`src/daip_live/core/models.py`).

### 3.1 DialogueTurn Model

```python
class DialogueTurn(BaseModel):
    """A single utterance from a participant in a session."""
    participant_id: str  # e.g., "user_human", "role_pro_01", "role_con_02"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content: str
```

### 3.2 Session Model

```python
class Session(BaseModel):
    """
    Represents the complete record of a multi-agent interaction.
    """
    session_id: str = Field(default_factory=lambda: f"session_{uuid.uuid4()}")
    session_type: Literal["debate", "chat", "workflow"]
    goal: str  # The overall goal or topic of the session

    # Participants
    participant_ids: List[str]

    # Timestamps & Status
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: AgentState = AgentState.INIT # Represents the state of the session orchestration

    # Content
    history: List[DialogueTurn] = []
    compressed_history: Optional[str] = None  # Mid-term memory
    summary: Optional[str] = None
```

## 4. Service Interface (`SessionManager`)

**Location**: `src/daip_live/memory/session_manager.py`

### Methods

#### `create_session(goal: str, session_type: str, participant_ids: List[str]) -> Session`
- **Description**: Creates a new session instance with its initial parameters.
- **Returns**: A new `Session` object.

#### `add_dialogue_turn(session_id: str, turn: DialogueTurn)`
- **Description**: Appends a new dialogue turn to the history of a specific session. This will be the primary method for recording the conversation as it happens.
- **Returns**: `None`.

#### `end_session(session_id: str, final_status: AgentState, summary: str)`
- **Description**: Finalizes a session by setting its end time, final status, and summary.
- **Returns**: `None`.

#### `get_session(session_id: str) -> Optional[Session]`
- **Description**: Retrieves a full session record, including its dialogue history.
- **Returns**: A `Session` object or `None`.

#### `list_sessions() -> List[Session]`
- **Description**: Retrieves a list of all sessions (metadata only, without the full `history` for efficiency).
- **Returns**: A list of `Session` objects.

#### `save_session(session: Session)`
- **Description**: Saves or updates a session object directly. Useful for scenarios where the session state is manipulated outside of the standard dialogue flow.
- **Returns**: `None`.

## 5. CLI Integration

- `daip session list`: Lists all persisted sessions (`session_id`, `session_type`, `goal`, `status`).
- `daip session view <session_id>`: Shows the details of a specific session, including the full dialogue history, turn by turn.

## 6. Persistence

- The `SessionManager` will use the `P1_Data_Persistence` service (`DatabaseManager`) to save and load session data.
- Sessions are stored in a normalized schema:
  - The `sessions` table stores the main metadata for each `Session`.
  - The `dialogue_turns` table stores each `DialogueTurn` as a separate record, linked to the parent session via a foreign key (`session_id`).
- The `participant_ids` list is serialized to a JSON string for storage in the `sessions` table.