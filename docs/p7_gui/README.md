---
id: P7
title: Graphical User Interface (GUI)
status: Rewritten
architecture_drivers: [SOLID, KISS, Decoupling]
---

# P7: Graphical User Interface (GUI)

## 1. Principle-Driven Refactoring

This specification has been rewritten to address a fundamental architectural mismatch in the original proposal. The use of Streamlit is rejected as it violates the KISS principle for the required level of interactivity.

-   **Architectural Decision**: The GUI will be a **decoupled web application** consisting of a dedicated backend and frontend. This is the standard, simplest, and most robust solution for this problem class.
-   **Technology Stack**: 
    -   **Backend**: **FastAPI** (Python) to serve as a bridge to the `P5` agent engine.
    -   **Frontend**: A Single-Page Application (SPA) using **React** or **Vue**.
    -   **Communication**: **WebSockets** for real-time, bidirectional event streaming.
-   **Single Responsibility (SRP)**: The backend is responsible for agent lifecycle and business logic. The frontend is responsible *only* for rendering the UI and managing UI state.

## 2. Backend Specification (FastAPI)

The backend acts as a thin wrapper around the `P5` engine.

### 2.1. WebSocket Endpoint: `/ws/sessions/{session_id}`

This is the primary communication channel.

-   **Connection**: When a frontend client connects, the backend instantiates a `P5.AgentExecutor` for the given `session_id`.
-   **Downstream (Server to Client)**: The backend awaits events from the `AgentExecutor`'s event stream and immediately forwards them as JSON messages over the WebSocket. It uses the *same* `AgentEvent` contract defined for `P6`.
-   **Upstream (Client to Server)**: The backend listens for user messages from the client on the WebSocket. These messages are put onto the `asyncio.Queue` that the `AgentExecutor` is listening to.

### 2.2. HTTP API Endpoints

-   `POST /api/sessions`: Creates a new session and returns a `session_id`.
-   `POST /api/sessions/{session_id}/run`: Starts the agent execution for a given goal.
-   `GET /api/sessions`: Lists all past sessions.

## 3. Frontend Specification (React/Vue)

The frontend is a pure presentation layer.

-   **State Management**: Use a modern state management library (e.g., Zustand, Redux Toolkit, Pinia) to manage the WebSocket connection and the list of agent events.
-   **Component Architecture**: The UI will be built from a hierarchy of components.
    -   `ChatView`: The main component that connects to the WebSocket and manages the overall session state.
    -   `MessageHistory`: Renders the list of event messages.
    -   `EventRenderer`: A component that takes a single `AgentEvent` object and decides which specific display component to render (e.g., `ThoughtCard`, `ToolCallCard`).
    -   `UserInput`: The input form that sends user messages over the WebSocket.

## 4. Task List (TDD)

-   **Backend (FastAPI)**:
    1.  Write API tests (using `pytest` and `httpx`) for the session management endpoints.
    2.  Implement the HTTP endpoints.
    3.  Write tests for the WebSocket handler, mocking the `P5` engine. Test connection, receiving events, and sending messages.
    4.  Implement the WebSocket handler.
-   **Frontend (React/Vue)**:
    1.  Write component tests (e.g., with Vitest/Jest and Testing Library) for each display component (`ToolCallCard`, etc.).
    2.  Write integration tests for the main `ChatView`, mocking the WebSocket connection to test the full event rendering flow.
    3.  Implement the components and state management.

## 5. Key Architectural Decisions & Open Issues

-   **Decision (KISS/Correct Tooling)**: The Streamlit approach is abandoned. The FastAPI + SPA + WebSocket architecture is adopted as it is simpler and more suitable for the project's requirements.
-   **Decision (Code Reuse)**: The backend will leverage the exact same `AgentEvent` stream contract as the TUI, ensuring `P5` does not need to produce different outputs for different frontends.
-   **Open Issue (P0)**: The formal Pydantic models for the `AgentEvent` stream are a prerequisite for both backend and frontend development.
-   **Open Issue (Security)**: A strategy for authenticating WebSocket connections needs to be determined.

## 6. Implementation Status

-   **Overall Status**: This work package is currently in the **Planned** phase. No implementation has started yet.
-   **Backend (FastAPI)**: No code has been written for the FastAPI backend.
-   **Frontend (React/Vue)**: No code has been written for the frontend SPA.
-   **Dependencies**: The implementation of this package depends on the completion and stability of `P5` (Agent Engine) and the formalization of `AgentEvent` models in `P0`.
