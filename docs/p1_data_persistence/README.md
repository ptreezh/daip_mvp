---
id: P1
title: Data Persistence Service
status: Finalized
architecture_drivers: [SOLID, KISS, KDD]
---

# P1: Data Persistence Service

## 1. Overview

This work package (`P1`) implements the Data Access Object (DAO) layer for the application. It provides a `DatabaseManager` class that encapsulates all direct interactions with a local **SQLite** database, offering a stable, typed API for higher-level services to create, retrieve, update, and delete data. It has a single responsibility: managing the lifecycle of structured data.

## 2. `DatabaseManager` API Specification

The public API of this package is the `DatabaseManager` class. It operates exclusively on data models defined in `P0`.

```python
# All models are imported from P0
from P0_Core_Interfaces_Types import Session, Message, TodoItem, ConsensusResult, AssistantState

class DatabaseManager:
    def __init__(self, db_path: str):
        """Initializes the database connection and ensures schema exists."""
        pass

    # Session Methods
    def add_session(self, title: str, type: str) -> Session:
        pass

    def get_session(self, session_id: int) -> Optional[Session]:
        pass

    # Message Methods
    def add_message(self, message_data: Message) -> Message:
        pass

    # ... other CRUD methods for TodoItem, ConsensusResult, etc. ...

    # State Management
    def save_assistant_state(self, session_id: int, state: AssistantState) -> None:
        pass

    def load_assistant_state(self, session_id: int) -> Optional[AssistantState]:
        pass
```

## 3. Database Schema Specification

This section is the single source of truth for the database schema. The implementation must create these tables if they do not exist.

-   **`sessions`**
    -   `id` INTEGER PRIMARY KEY
    -   `title` TEXT NOT NULL
    -   `type` TEXT NOT NULL
    -   `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-   **`messages`**
    -   `id` INTEGER PRIMARY KEY
    -   `session_id` INTEGER NOT NULL, FOREIGN KEY(`session_id`) REFERENCES `sessions`(`id`)
    -   `role` TEXT NOT NULL
    -   `content` TEXT NOT NULL
    -   `metadata_json` TEXT
    -   `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-   **`knowledge_sources`**
    -   `id` INTEGER PRIMARY KEY
    -   `file_path` TEXT NOT NULL UNIQUE
    -   `file_hash` TEXT NOT NULL
    -   `last_modified` TIMESTAMP NOT NULL

*(Other tables like `todos`, `consensus_results` follow a similar, clear structure.)*

## 4. Implementation Policies & Requirements

These are mandatory technical requirements for the implementation.

-   **ORM**: Use of a lightweight ORM like **SQLAlchemy Core** or **SQLModel** is recommended to map between the schema and Pydantic models.
-   **Connection Management**: The `DatabaseManager` **must** manage the SQLite connection lifecycle. For multi-threaded access (e.g., from a web server), it must use a thread-safe connection pool (e.g., `sqlalchemy.pool.QueuePool`).
-   **Transactions**: All write operations that touch more than one table, or involve a read-modify-write pattern, **must** be wrapped in a database transaction to ensure atomicity.
-   **Foreign Keys**: The implementation **must** enable foreign key support in SQLite (`PRAGMA foreign_keys = ON;`) for every connection to ensure data integrity.
-   **Indexing**: Indexes **must** be created on all foreign key columns (e.g., `messages.session_id`) and any fields that are frequently used in `WHERE` clauses.
-   **Migrations**: Schema changes after the initial release **must** be managed via a migration tool like **Alembic**. Migration scripts must be version-controlled.
-   **Error Handling**: Low-level `sqlite3` or SQLAlchemy exceptions **must** be caught and re-raised as specific, custom exceptions defined in `P0` (e.g., `RecordNotFoundError`, `DatabaseError`).

## 5. Test Plan Summary

-   **TDD Approach**: All methods must be developed via TDD.
-   **Test Database**: All tests **must** run against an in-memory SQLite database (`:memory:`) to ensure speed and isolation.
-   **Key Test Cases**:
    -   Verify all CRUD operations for each model.
    -   Verify that violating a `FOREIGN KEY` or `UNIQUE` constraint correctly raises an `IntegrityError`.
    -   Verify that the data migration system can successfully upgrade the schema from v1 to v2.
-   **Acceptance**: Test coverage >= 90%; passes `ruff` and `mypy --strict`.

## 6. Implementation Status

-   **`DatabaseManager` Class**: The class structure is defined, and the constructor is implemented. It is integrated into the `cli.py` for application startup.
-   **CRUD Operations**: The specific CRUD methods (e.g., `add_session`, `get_session`, `add_message`) are currently placeholders. Actual database interaction logic for these methods is pending implementation.
-   **Schema Creation**: The logic for creating the database schema (tables) on startup is pending implementation.
