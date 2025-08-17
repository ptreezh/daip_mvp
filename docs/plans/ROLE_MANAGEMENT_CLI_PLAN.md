## Detailed Sub-Plan 2: Enhance Role Management CLI

**Feature:** Role Management (Create, Update, Detailed View)
**CLI Commands:**
*   `daip-cli roles create <name> --description <desc> [--tags <tag1,tag2>]`
*   `daip-cli roles update <role_id> [--name <new_name>] [--description <new_desc>] [--add-tags <tag1,tag2>] [--remove-tags <tag1,tag2>]`
*   `daip-cli roles view <role_id>`

**Goal:** Extend the existing `daip-cli roles` command to allow users to create new roles, update existing roles, and view detailed information about a specific role.

### 2.1. Requirement Specification (Kiro Specs Pattern)

**Feature Name:** Enhanced Role Management CLI
**User Story:** As a system administrator or advanced user, I want to manage AI roles from the command line, including creating new ones, updating their properties, and viewing their full details, to better configure and utilize the system's capabilities.

**Functional Requirements:**

*   **`daip-cli roles create <name> --description <desc> [--tags <tag1,tag2>]`:**
    *   **Input:**
        *   `<name>`: Required string, the name of the new role.
        *   `--description <desc>`: Required string, a brief description of the role.
        *   `--tags <tag1,tag2>`: Optional comma-separated string of tags for the role.
    *   **Behavior:**
        *   Calls `AutonomousRoleCreationSystem.create_role()` or `RoleManager.save_role()` to create a new role.
        *   Generates a unique `role_id` if not explicitly provided by the underlying service.
        *   Displays a success message with the new role's ID and name.
    *   **Error Handling:**
        *   If required arguments are missing, display an error.
        *   If role creation fails (e.g., invalid data, backend error), display an informative error message.

*   **`daip-cli roles update <role_id> [--name <new_name>] [--description <new_desc>] [--add-tags <tag1,tag2>] [--remove-tags <tag1,tag2>]`:**
    *   **Input:**
        *   `<role_id>`: Required string, the ID of the role to update.
        *   `--name <new_name>`: Optional string, new name for the role.
        *   `--description <new_desc>`: Optional string, new description for the role.
        *   `--add-tags <tag1,tag2>`: Optional comma-separated string of tags to add.
        *   `--remove-tags <tag1,tag2>`: Optional comma-separated string of tags to remove.
    *   **Behavior:**
        *   Retrieves the existing role using `RoleManager.get_role_by_id()`.
        *   Updates the role's properties based on provided options.
        *   Calls `RoleManager.save_role()` to persist changes.
        *   Displays a success message.
    *   **Error Handling:**
        *   If `<role_id>` is not found, display an error.
        *   If no update options are provided, display a warning.
        *   If role update fails, display an informative error message.

*   **`daip-cli roles view <role_id>`:**
    *   **Input:**
        *   `<role_id>`: Required string, the ID of the role to view.
    *   **Behavior:**
        *   Retrieves the role using `RoleManager.get_role_by_id()` or `RealRoleManager.get_role()`.
        *   Displays all available details of the role in a structured, readable format (e.g., using `rich.panel` or `rich.table`).
    *   **Error Handling:**
        *   If `<role_id>` is not found, display an error.

**Internal API Dependencies:**

*   `src.core_services.role_manager.RoleManager`:
    *   `get_role_by_id(role_id: str) -> Optional[Role]`
    *   `save_role(role: Role) -> bool`
*   `src.core_services.autonomous_role_creation_system.AutonomousRoleCreationSystem`:
    *   `async create_role(request: RoleGenerationRequest) -> RoleGenerationResult` (for `roles create`)
*   `src.real_demo_system.real_role_manager.RealRoleManager`:
    *   `get_role(role_id: str) -> Optional[dict[str, Any]]` (for `roles view`)

### 2.2. Test Case Design

I will design unit tests for the new CLI commands' integration with the `RoleManager` and `AutonomousRoleCreationSystem`.

**Test File:** `tests/cli/test_role_management.py` (new file)

**Unit Tests (Focus on `src/cli/commands.py` and its interaction with Role APIs):**

*   **Test Case 2.2.1: Create Role - Success**
    *   **Description:** Verify successful creation of a new role with name and description.
    *   **Input:** `daip-cli roles create "New Role" --description "A test role."`
    *   **Expected Behavior:**
        *   `AutonomousRoleCreationSystem.create_role` is called with correct parameters.
        *   A success message with the new role's ID and name is printed.
    *   **Mocking Strategy:** Mock `AutonomousRoleCreationSystem.create_role` to return a successful `RoleGenerationResult`.

*   **Test Case 2.2.2: Create Role - Missing Description**
    *   **Description:** Verify error handling for missing required description.
    *   **Input:** `daip-cli roles create "New Role"`
    *   **Expected Behavior:**
        *   An error message about missing description is printed.
        *   `AutonomousRoleCreationSystem.create_role` is *not* called.

*   **Test Case 2.2.3: Create Role - With Tags**
    *   **Description:** Verify successful creation of a role with tags.
    *   **Input:** `daip-cli roles create "Tagged Role" --description "A role with tags." --tags "tag1,tag2"`
    *   **Expected Behavior:**
        *   `AutonomousRoleCreationSystem.create_role` is called with tags correctly parsed.
        *   A success message is printed.

*   **Test Case 2.2.4: Update Role - Success (Name Change)**
    *   **Description:** Verify successful update of a role's name.
    *   **Input:** `daip-cli roles update "existing_role_id" --name "Updated Role Name"`
    *   **Expected Behavior:**
        *   `RoleManager.get_role_by_id` is called.
        *   `RoleManager.save_role` is called with the updated role object.
        *   A success message is printed.
    *   **Mocking Strategy:** Mock `RoleManager.get_role_by_id` to return a mock `Role` object, and `RoleManager.save_role` to return `True`.

*   **Test Case 2.2.5: Update Role - Add Tags**
    *   **Description:** Verify successful addition of tags to an existing role.
    *   **Input:** `daip-cli roles update "existing_role_id" --add-tags "new_tag"`
    *   **Expected Behavior:**
        *   `RoleManager.get_role_by_id` is called.
        *   `RoleManager.save_role` is called with the role having the new tag.
        *   A success message is printed.

*   **Test Case 2.2.6: Update Role - Remove Tags**
    *   **Description:** Verify successful removal of tags from an existing role.
    *   **Input:** `daip-cli roles update "existing_role_id" --remove-tags "old_tag"`
    *   **Expected Behavior:**
        *   `RoleManager.get_role_by_id` is called.
        *   `RoleManager.save_role` is called with the role having the tag removed.
        *   A success message is printed.

*   **Test Case 2.2.7: Update Role - Not Found**
    *   **Description:** Verify error handling when updating a non-existent role.
    *   **Input:** `daip-cli roles update "non_existent_id" --name "New Name"`
    *   **Expected Behavior:**
        *   An error message indicating role not found is printed.
        *   `RoleManager.save_role` is *not* called.
    *   **Mocking Strategy:** Mock `RoleManager.get_role_by_id` to return `None`.

*   **Test Case 2.2.8: View Role - Success**
    *   **Description:** Verify successful display of role details.
    *   **Input:** `daip-cli roles view "existing_role_id"`
    *   **Expected Behavior:**
        *   `RealRoleManager.get_role` is called.
        *   Formatted role details (name, description, capabilities, etc.) are printed.
    *   **Mocking Strategy:** Mock `RealRoleManager.get_role` to return a mock role dictionary.

*   **Test Case 2.2.9: View Role - Not Found**
    *   **Description:** Verify error handling when viewing a non-existent role.
    *   **Input:** `daip-cli roles view "non_existent_id"`
    *   **Expected Behavior:**
        *   An error message indicating role not found is printed.
    *   **Mocking Strategy:** Mock `RealRoleManager.get_role` to return `None`.
