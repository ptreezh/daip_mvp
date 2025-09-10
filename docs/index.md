# DAIP-LIVE Documentation Hub

Welcome to the central documentation for the Dynamic AI Personality (DAIP-LIVE) project. This documentation is structured to be the **Single Source of Truth (SSOT)** for all requirements, specifications, and development plans.

The project is divided into several distinct work packages (P0-P8), each with a dedicated section containing its full specification, task list, and testing strategy.

## Work Packages

| ID | Name | Description | Status | Link |
| :--- | :--- | :--- | :--- | :--- |
| P0 | Core Interfaces & Types | Defines the fundamental data structures, types, and API contracts used across the entire system. | `Not Started` | [Specification](./p0_core_interfaces/README.md) |
| P1 | Data Persistence Service | Manages the storage and retrieval of all project data, including debates, roles, and user sessions. | `Not Started` | [Specification](./p1_data_persistence/README.md) |
| P2 | Knowledge Management Service | Handles the ingestion, processing, and retrieval of knowledge from various sources. | `Not Started` | [Specification](./p2_knowledge_manager/README.md) |
| P3 | Model Provider Service | Provides a unified interface to interact with various Large Language Models (LLMs). | `Not Started` | [Specification](./p3_model_provider/README.md) |
| P4 | Role Manager & Tools Logic | Manages the agent roles, their associated tools, and the logic for tool execution. | `Not Started` | [Specification](./p4_role_manager_tools/README.md) |
| P5 | Agent Engine Logic | The core logic engine that orchestrates agent interactions, debates, and task execution. | `Not Started` | [Specification](./p5_agent_engine/README.md) |
| P6 | CLI & TUI Interfaces | Implements the Command-Line Interface (CLI) and Text-based User Interface (TUI) for user interaction. | `Not Started` | [Specification](./p6_cli_tui/README.md) |
| P7 | GUI Interface | Implements the Graphical User Interface (GUI) for a rich user experience. | `Not Started` | [Specification](./p7_gui/README.md) |
| P8 | Human-in-the-Loop Assistant | Defines the system for human oversight, intervention, and collaboration with AI agents. | `Not Started` | [Specification](./p8_human_assistant/README.md) |

## Legacy Documents

All original, pre-refactoring documents have been moved to the `../docs_archive/` directory for historical reference.
