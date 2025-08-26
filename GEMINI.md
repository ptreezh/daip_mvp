The project is a Python-based AI-driven system, `DAIP-LIVE`, designed for dynamic project execution and intelligent collaboration. It leverages FastAPI for potential web interfaces (though the current focus is CLI) and a React/TypeScript frontend (currently not in scope for CLI-first). The core functionalities revolve around AI-powered debates, intelligent assistants, and knowledge management.

The primary CLI entry point is `daip-cli.py`, which uses `src/cli/main.py` and the `typer` library to provide command-line functionalities.

### Project Overview

DAIP-LIVE is an intelligent collaboration system that facilitates various AI-driven interactions, including:
*   **Debate System:** Enables multi-role AI debates on specified topics with configurable rounds and consensus strategies.
*   **Role Management:** Manages and lists AI roles that can participate in debates and other scenarios.
*   **System Monitoring:** Provides a `status` command to check the health and configuration of various system components (LLM, vector store, dependencies).
*   **Intelligent Scenarios:** (Currently simulated in `web_demo_app.py`) Academic Research, Expert Consultation, and Casual Discussion.

The project structure suggests a modular design with distinct domains like `core_services`, `application`, `debate_system`, `virtual_role_chat`, `institutional_primitives`, and `workflows`.

### Building and Running

The project is primarily Python-based.

*   **Dependencies:** Dependencies are listed in `requirements.txt` and `poetry.lock`.
    *   To install: `pip install -r requirements.txt` or `poetry install`
*   **Running the CLI:**
    *   The main CLI application can be run using `python daip-cli.py <command> [options]`.
    *   Alternatively, if installed as a package, it might be directly executable as `daip-cli <command> [options]`.

### Development Conventions

*   **Language:** Python for backend/CLI, TypeScript/React for frontend.
*   **CLI Framework:** `typer` for command-line interfaces.
*   **Web Framework:** `FastAPI` for backend APIs.
*   **Frontend Framework:** `React.js` with `Ant Design` and `Redux Toolkit`.
*   **Logging:** Uses Python's `logging` module.
*   **Configuration:** `src/config.py` and `config.yaml` for settings.
*   **Testing:** `pytest` is used for testing (indicated by `pytest.ini` and numerous `test_*.py` files).
*   **Code Quality:** `ruff.toml` indicates `ruff` is used for linting.

### Existing CLI Commands

The `daip-cli` currently supports the following commands:

*   **`daip-cli start <topic> [--role <role_name>] [--rounds <num>] [--consensus <strategy>] [--verbose] [--save] [--output <file>]`**
    *   Starts a new debate.
    *   `topic`: The subject of the debate.
    *   `--role`: Specify AI roles (can be used multiple times).
    *   `--rounds`: Number of debate rounds (default: 3).
    *   `--consensus`: Consensus strategy (`simple_majority_vote`, `weighted_vote`, `consensus_building`, `expert_judgment`).
    *   `--verbose`: Enable detailed output.
    *   `--save`: Save debate results.
    *   `--output`: Output file for results (default: `debate_results.txt`).
    *   *Example:* `daip-cli start "Should AI be regulated?" --role "AI Ethicist" --role "Tech Innovator" --rounds 5 --consensus weighted_vote`

*   **`daip-cli roles`**
    *   Lists all available AI roles that can participate in debates.
    *   *Example:* `daip-cli roles`

*   **`daip-cli status`**
    *   Checks the overall system health, including configuration, LLM provider, vector store, and dependencies.
    *   *Example:* `daip-cli status`

*   **`daip-cli help`**
    *   Displays detailed help and usage examples for the CLI.
    *   *Example:* `daip-cli help`

### Proposed CLI Extensions for Requested Features

To fulfill the user's request for a comprehensive CLI experience, the following commands would need to be implemented or extended:

*   **Personal Assistant:**
    *   **`daip-cli assistant chat <query>`**: Interact with the personal assistant.
        *   *Relevant files to investigate:* `src/application/personal_assistant_service.py`, `src/intelligent_assistant_app.py`.

*   **Debate Hall Enhancements:**
    *   **`daip-cli debate view-disagreements <debate_id>`**: View points of disagreement in an ongoing or completed debate.
        *   *Relevant files to investigate:* `src/real_demo_system/transparent_conflict_resolution.py`, `src/debate_system/argument_analysis.py`.
    *   **`daip-cli debate select-consensus-algorithm <debate_id> <algorithm_name>`**: Select a consensus algorithm for a specific debate. (This might be part of `start` or a separate command for dynamic selection).
        *   *Relevant files to investigate:* `src/protocols/consensus_strategies.py`, `src/core_services/consensus_algorithm_selector.py`.

*   **Chat Room:**
    *   **`daip-cli chat start [--room <room_name>]`**: Start a new chat room.
    *   **`daip-cli chat message <room_id> <message>`**: Send a message in a chat room.
    *   **`daip-cli chat history <room_id>`**: View chat history.
        *   *Relevant files to investigate:* `src/core_services/chat_service.py`, `src/virtual_role_chat/chat_room_manager.py`.

*   **Knowledge Creation / Wiki:**
    *   **`daip-cli wiki create <title> --content <file_path>`**: Create a new Wiki page from a file.
    *   **`daip-cli wiki view <title_or_id>`**: View a Wiki page.
    *   **`daip-cli wiki export <title_or_id> --format <format>`**: Export a Wiki page (e.g., to Markdown, PDF).
    *   **`daip-cli debate export-to-wiki <debate_id> --title <wiki_title>`**: Export debate results to a new Wiki page.
        *   *Relevant files to investigate:* `src/core_services/wiki_service.py`, `src/tools/wiki_tools.py`, `src/real_demo_system/wiki_knowledge_system.py`, `src/real_demo_system/real_time_wiki_updater.py`.

*   **Role Management / Creation:**
    *   **`daip-cli roles create <name> --description <desc> [--tags <tag1,tag2>]`**: Create a new AI role.
    *   **`daip-cli roles invite <role_id> --to-debate <debate_id>`**: Invite a role to an active debate.
    *   **`daip-cli roles manage <role_id> --update-description <new_desc>`**: Update an existing role's properties.
        *   *Relevant files to investigate:* `src/core_services/role_manager.py`, `src/core_services/autonomous_role_creation_system.py`, `src/real_demo_system/real_role_manager.py`.

*   **Workflow Management (Institutional Primitives):**
    *   **`daip-cli workflow list`**: List available institutional primitives/workflows.
    *   **`daip-cli workflow create <name> --definition <file_path>`**: Create a new custom workflow/primitive.
    *   **`daip-cli workflow select <workflow_id> --for-scenario <scenario_type>`**: Select a workflow for a specific scenario.
    *   **`daip-cli workflow execute <workflow_id> --params <json_string>`**: Execute a specific workflow with parameters.
        *   *Relevant files to investigate:* `src/institutional_primitives`, `src/workflows`, `src/institutional_primitives/registry.py`, `src/institutional_primitives/workflow_engine.py`, `src/scenario_engine/workflow_selector.py`.