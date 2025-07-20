# Conversational CLI Design Document

## 1. Background

The current DAIP-LIVE CLI for starting a debate (`src/cli/main.py`) relies on static `typer.Option` arguments. This approach is inflexible and complex for users who need to configure various debate parameters (topic, roles, rounds, consensus strategy) interactively. The user explicitly requested a Q&A style conversational interface.

## 2. Goal

To transform the `start_debate` CLI command into an intuitive, interactive, and conversational flow. This will guide the user through the process of defining debate parameters, including intelligent topic extraction and role recommendations, significantly improving the user experience.

## 3. Design

### 3.1. Interactive Flow Overview

The `start_debate` function in `src/cli/main.py` will be modified to implement a sequence of interactive prompts using `rich.console.Console().input()` or similar `prompt_toolkit` based input methods for a consistent TUI experience.

The flow will be as follows:

1.  **Welcome and Initial Prompt:** Greet the user and explain the interactive setup.
2.  **Debate Topic Definition:**
    *   Prompt user: "Do you want to (1) directly enter the debate topic, or (2) provide a prompt for the AI to extract a topic?"
    *   **Option 1 (Direct Topic):** Prompt for the exact debate topic.
    *   **Option 2 (Topic from Prompt):**
        *   Prompt for a detailed text prompt (e.g., "Summarize the main debate topic from this article: [article text]").
        *   Call `kernel.llm_interface.chat()` with a specific system prompt to extract the core topic from the user's input prompt.
        *   Display the extracted topic to the user.
        *   Ask for confirmation: "Is this topic satisfactory? (y/n)". If 'n', allow user to re-enter prompt or switch to direct topic input.
3.  **Role Selection:**
    *   Based on the final debate topic, call `role_recommender_service.recommend_roles(topic)` to get a list of recommended `Role` objects.
    *   Display recommended roles: For each recommended role, show its `id`, `name`, `description`, and `capabilities`.
    *   Prompt user: "Enter the IDs of the roles you want to include (comma-separated), or type 'new' to create a new role, or 'skip' to manually enter roles."
    *   **Role Selection Logic:**
        *   Parse user input for role IDs.
        *   Validate selected role IDs against `role_manager.list_roles()`.
        *   If 'new' is entered:
            *   Initiate a sub-flow for creating a new role:
                *   Prompt for `id`, `name`, `description`, `system_prompt`, `capabilities` (comma-separated).
                *   Call `role_manager.save_role(new_role_object)`.
                *   Add the newly created role to the selected roles.
            *   After creating, return to role selection or confirm current selection.
        *   If 'skip' is entered: Allow user to manually type in role IDs without recommendations.
        *   Loop until valid roles are selected or user explicitly exits.
4.  **Number of Rounds:**
    *   Prompt user: "Enter the number of debate rounds (default: 20):"
    *   Parse input, validate it's an integer. Use default if empty.
5.  **Consensus Strategy:**
    *   List available consensus strategies (e.g., "simple_majority_vote", "weighted_vote").
    *   Prompt user: "Select a consensus strategy (default: simple_majority_vote):"
    *   Parse input, validate against available strategies. Use default if empty.
6.  **Confirmation:** Display a summary of all selected debate parameters. Ask for final confirmation before starting the debate.

### 3.2. Key Components and Interactions

*   **`src/cli/main.py`:** Will contain the primary interactive logic within the `start_debate` function.
*   **`rich.console.Console`:** Used for interactive input (`console.input`) and formatted output.
*   **`prompt_toolkit`:** The underlying TUI framework will handle the interactive elements.
*   **`src/composition.py`:** Will provide the necessary service instances (`role_manager`, `role_recommender_service`, `kernel`) to `start_debate` via the `deps` dictionary.
*   **`kernel.llm_interface`:** Used for topic extraction from user prompts.
*   **`role_recommender_service`:** Used to suggest roles based on the debate topic.
*   **`role_manager`:** Used to validate selected roles and to save newly created roles.
*   **`src/models.py`:** `DebateConfig` will be populated with the collected parameters.

### 3.3. Error Handling and User Experience

*   **Input Validation:** All user inputs will be validated (e.g., integer for rounds, valid role IDs, valid strategy names).
*   **Clear Prompts:** Prompts will be clear and provide default values or examples where appropriate.
*   **Retry Mechanism:** Invalid inputs will trigger a clear error message and allow the user to retry.
*   **Exit Option:** Users should be able to exit the setup process at any point (e.g., by typing 'q' or Ctrl+C).

## 4. Benefits

*   **Improved User Experience:** Simplifies the debate setup process, making it accessible to users unfamiliar with CLI arguments.
*   **Increased Flexibility:** Allows dynamic topic extraction and role selection, adapting to diverse user needs.
*   **Guided Workflow:** Guides users through complex configurations with clear steps and options.
*   **Reduced Errors:** Input validation and clear prompts minimize configuration mistakes.
