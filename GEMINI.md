# DAIP-LIVE Project Context

## 1. Project Overview

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE system) is an open-source, local-first AI agent platform built in Python. It is designed to be a "second brain" and "efficient execution partner" for knowledge workers and developers by automating complex, multi-step tasks.

The project's core value propositions are:
-   **Privacy & Trust**: All user data and knowledge bases are processed and stored locally.
-   **Transparency & Control**: The agent's entire thinking process (planning, tool use) is visible to the user, who can intervene and steer the agent in real-time.
-   **Integration & Extensibility**: The agent can be grounded in a user's local file-based knowledge base (RAG) and can be extended with new tools.

## 2. Architecture

The system is a **modular monolith** designed for a local, single-user environment. It is composed of several work packages (P0-P8) with clear responsibilities:

-   **P0-P1**: Defines core data types and provides data persistence via SQLAlchemy.
-   **P2**: The `KnowledgeManager` service, which uses `faiss-cpu` and `langchain` to create and query a local vector knowledge base from user documents.
-   **P3**: The `ModelProvider` service, a factory for interacting with various LLMs (local and cloud).
-   **P4**: The `RoleManager` and `ToolManager`, which define agent personas and provide a secure execution pipeline for tools.
-   **P5**: The `AgentEngine`, which is the core of the system. It implements a sophisticated, **Confidence-Driven State Machine** that allows the agent to plan, execute, and **self-reflect** on its answers to improve reliability, especially with smaller local models.
-   **P6-P8**: The user interface layers (CLI/TUI/GUI) and high-level workflow orchestration.

## 3. Building and Running

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

**Key Dependencies:**
-   Python >=3.9
-   CLI/TUI: `typer`, `textual`
-   GUI: `streamlit`
-   Core: `sqlalchemy`, `faiss-cpu`, `langchain`, `pydantic`

**To install dependencies:**
```bash
poetry install
```

**To run the application (inferred):**

The primary entry point is a CLI built with `typer`. Common commands would be:
```bash
# Run the agent in an interactive TUI session
poetry run daip run "<Your Goal>"

# Manually sync the knowledge base
poetry run daip knowledge sync
```

**To run tests:**
```bash
poetry run pytest
```

## 4. Development Conventions

-   **Code Quality**: The project enforces a strict code quality standard using:
    -   **`ruff`** for formatting and linting.
    -   **`mypy --strict`** for static type checking.
-   **Pre-Commit**: A `.pre-commit-config.yaml` is present, indicating that these quality checks are likely run automatically before each commit.
-   **Testing**: The project uses `pytest`. The design documents emphasize a Test-Driven Development (TDD) approach, with a heavy reliance on mocking external services (`P1`-`P4`) to test the core agent logic (`P5`) in isolation.
