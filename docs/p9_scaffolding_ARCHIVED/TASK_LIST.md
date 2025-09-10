# P9: AI-driven Scaffolding Task List

-   [x] **T-P9-01**: Register the `scaffold` command in the CLI.
    -   **Description**: Add a new `project` subcommand and a `scaffold` command to `cli.py`. The initial implementation should just print a confirmation message.
    -   **Acceptance Criteria**: Running `poetry run daip project scaffold --description "test"` executes without errors and prints a message.

-   [x] **T-P9-02**: Implement the core LLM interaction logic.
    -   **Description**: Create a new service/manager that takes the user's description, wraps it in a meta-prompt, and calls the `ModelProvider`.
    -   **Acceptance Criteria**: The service can successfully get a structured (e.g., JSON/YAML) response from the LLM containing filenames and content.

-   [x] **T-P9-03**: Implement YAML validation and self-correction loop.
    -   **Description**: After receiving the LLM response, parse and validate the YAML content. If validation fails, send the error back to the LLM for self-correction (up to 2 retries).
    -   **Acceptance Criteria**: Invalid YAML from the LLM is correctly identified and a self-correction attempt is triggered.

-   [x] **T-P9-04**: Implement user preview and confirmation.
    -   **Description**: Display the validated, to-be-created filenames and their content to the user in the console and await a `[y/N]` confirmation.
    -   **Acceptance Criteria**: The user can clearly see what will be created and can abort the process.

-   [x] **T-P9-05**: Implement file writing logic.
    -   **Description**: Upon user confirmation, write the files to the correct directories (`roles/`, `workflows/`, `prompts/`).
    -   **Acceptance Criteria**: Files are correctly created in the local filesystem.