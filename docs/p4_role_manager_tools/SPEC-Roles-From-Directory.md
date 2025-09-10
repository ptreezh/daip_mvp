# P4-Enhancement: Roles from Directory Specification

## 1. Overview

This document specifies a new, more modular approach for the `RoleManager`. Role definitions will be loaded from a dedicated directory, with each role defined in its own YAML file. This supersedes the previous single-file approach.

## 2. Directory Structure

-   **Default Directory**: The `RoleManager` will look for a `roles/` directory in the project root.
-   **Role Files**: Each `.yaml` or `.yml` file within this directory is considered a role definition. The filename (without the extension) will be used as the unique `name` of the role.

**Example Directory Structure:**

```
roles/
├── pro_arguer.yaml
├── con_arguer.yaml
└── neutral_observer.yaml
```

## 3. Role File Format

Each file will contain the keys for a single role, *excluding* the `name` (as it is derived from the filename).

**Example `pro_arguer.yaml`:**

```yaml
persona: "You are a passionate advocate for the topic. Your goal is to build a strong, positive case using clear arguments and evidence. You are optimistic and forward-looking."
tools: []
```

## 4. `RoleManager` Behavior

-   **Initialization (`__init__`)**: The constructor will accept an optional `roles_dir_path`, defaulting to `"roles"`.
-   **Loading**: Upon initialization, the manager will:
    1.  Scan the specified directory for all `*.yaml` and `*.yml` files.
    2.  For each file found:
        a.  Use the filename (e.g., `pro_arguer`) as the `role.name`.
        b.  Read and parse the file's YAML content.
        c.  Combine the name and the parsed data to create a `Role` object.
        d.  Validate the object using the Pydantic `Role` model.
        e.  Store the valid `Role` object in its internal dictionary.
-   **Error Handling**:
    -   If the directory does not exist, log a warning and initialize with zero roles.
    -   If a file is malformed YAML, log a warning for that file and skip it.
    -   If a file's data does not conform to the `Role` model (e.g., missing `persona`), log a warning for that file and skip it.

## 5. Dependencies

-   `PyYAML`: Already in the project.
