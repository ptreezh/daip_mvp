# P4-Enhancement: Roles from File Specification

## 1. Overview

This document specifies the enhancement to the `RoleManager` to load role definitions from an external YAML file instead of having them hardcoded. This makes the system more flexible and configurable by the user.

## 2. Configuration File (`roles.yaml`)

-   **Location**: The `RoleManager` will look for a `roles.yaml` file in the root directory of the project.
-   **Format**: The file will contain a top-level key `roles`, which is a list of role objects. Each object must match the `Role` Pydantic model.

**Example `roles.yaml`:**

```yaml
roles:
  - name: "pro_arguer"
    persona: "You are a passionate advocate for the topic. Your goal is to build a strong, positive case using clear arguments and evidence. You are optimistic and forward-looking."
    tools: []

  - name: "con_arguer"
    persona: "You are a skeptical and critical thinker. Your goal is to challenge the topic by identifying potential risks, flaws, and unintended consequences. You are cautious and analytical."
    tools: []

  - name: "neutral_observer"
    persona: "You are a neutral, objective observer. Your goal is to summarize the arguments from both sides, identify key points of agreement and disagreement, and ensure the debate remains fair and balanced. You do not take a side."
    tools: []
```

## 3. `RoleManager` Behavior

-   **Initialization (`__init__`)**: The `RoleManager`'s constructor will be modified to accept an optional `roles_file_path`. If not provided, it defaults to `roles.yaml`.
-   **Loading**: Upon initialization, the manager will:
    1.  Check if the roles file exists.
    2.  If it exists, read and parse the YAML content.
    3.  Use Pydantic to validate and deserialize the list of roles into a dictionary of `Role` objects, keyed by `role.name`.
-   **Error Handling**:
    -   If the file does not exist, the `RoleManager` will initialize with an empty dictionary of roles and log a warning.
    -   If the file is malformed (invalid YAML) or the data does not match the `Role` schema, the manager will raise a `ValueError`.
-   **Interface**: The public method `get_role_by_name(name: str) -> Optional[Role]` will remain unchanged, now serving roles from the file-based dictionary.

## 4. Dependencies

-   `PyYAML`: This library will be added to the project to handle YAML parsing.
