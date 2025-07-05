# Feature Migration Plan: Integrating Role and Virtual Team Management

## 1. 目标 (Objective)

This plan details the migration of the legacy Role Management and Virtual Team functionalities from the `src/vendor/old` directory into the new, service-oriented architecture. The goal is to complete another step towards the eventual removal of the `old` directory by refactoring these specific features.

## 2. 核心原则 (Core Principles)

- **服务化 (Service-Oriented):** Encapsulate all business logic into discrete, testable services located in `src/services`.
- **依赖注入 (Dependency Injection):** Utilize a central service container (`src/core/container.py`) to manage service lifecycles and dependencies, ensuring a single source of truth for stateful services (e.g., `ExpertLibraryService`).
- **瘦API层 (Thin API Layer):** FastAPI routers in `src/api/routers/` will be responsible only for handling HTTP protocol details, delegating all business logic to the appropriate services.
- **清晰的入口点 (Clear Entry Point):** The application will have a single, unambiguous entry point in `src/main.py`.

## 3. 迁移计划 (Migration Plan)

The migration is divided into four distinct phases to ensure a structured and manageable process.

### Phase 1: Service and Model Migration

#### Step 1.1: Migrate and Extend Data Models

This step isolates the data structures from the legacy logic.
- **Action:** Move the `Expert` dataclass from `src/vendor/old/expert_library.py` to a new file `src/models/expert.py`.
- **Enhancement:** Add the new dynamic capability fields to the `Expert` model: `prompt_template: str` and `tool_access_policy: dict`.
- **Action:** Create `src/models/virtual_team.py` and move the `VirtualProject` and `VirtualTask` dataclasses from `src/vendor/old/virtual_team_project_engine.py`.

#### Step 1.2: Refactor `ExpertLibrary` into `ExpertLibraryService`

This service will become the sole manager of role and expert data.

- **Action:** Create `src/services/expert_library_service.py`.
- **Refactor:**
    - Move the `ExpertLibrary` class logic from `src/vendor/old/expert_library.py` into a new `ExpertLibraryService` class.
    - Remove any auto-loading logic from the service's `__init__`. Loading will be managed by the container.

#### Step 1.3: Refactor `VirtualTeamProjectEngine` into `VirtualTeamService`

This service will manage virtual projects and tasks.

- **Action:** Create `src/services/virtual_team_service.py`.
- **Refactor:**
    - Move the `VirtualTeamProjectEngine` class logic from `src/vendor/old/virtual_team_project_engine.py` into a new `VirtualTeamService` class.
    - Modify its `__init__` to accept dependencies (e.g., `ExpertLibraryService`) via arguments.
    - Correct the `create_task` method to expect `priority` as an `int`.

#### Step 1.4: Register New Services in Container

Wire the new services into the application.

- **Action:** In the existing service container (e.g., `src/core/container.py`), register `ExpertLibraryService` and `VirtualTeamService` as singletons. Ensure their dependencies are correctly injected.

### Phase 2: Refactor the API Layer

#### Step 2.1: Refactor `roles` API

Decouple the API from direct data access.

- **Action:**
    - Remove all direct file I/O (`os.path`, `json.load/dump`) and direct state manipulation.
    - Create a FastAPI dependency (e.g., `get_expert_library_service`) to inject the `ExpertLibraryService` singleton.
    - Rewrite all endpoints (`get_roles`, `create_role`, etc.) to delegate logic to the injected service.

#### Step 2.2: Create and Refactor `team` API

Create a new, clean API for virtual team management.

- **Action:**
    - Create the new router file `src/api/routers/team.py`.
    - Move endpoints from `src/vendor/old/virtual_team_api.py`.
    - Delete the old `get_engine()` function and use FastAPI's `Depends` to inject the `VirtualTeamService` singleton.
    - Update the `CreateTaskRequest` model to use `priority: int`.

#### Step 2.3: Implement Role Recommendation Service

Introduce the new intelligent recommendation feature.

- **Action:**
    - Create `src/services/role_recommendation_service.py`.
    - Implement the `RoleRecommendationService` class, which will depend on `ExpertLibraryService`.
    - Register the new service as a singleton in `src/core/container.py`.
    - Add a new `/recommend_team` endpoint to `src/api/routers/roles.py` that uses this service.

### Phase 3: Integration and Cleanup

#### Step 3.1: Update `main.py`

Finalize the application's startup process.

- **Action:**
    - Update `src/main.py` to include the new `team_router`.
    - Remove any inclusion of the old `virtual_team_api.py` router.

#### Step 3.2: Remove Migrated `old` Files

The final step to complete this migration cycle.

- **Action:** Delete the now-redundant files from `src/vendor/old`: `expert_library.py`, `virtual_team_project_engine.py`, and `virtual_team_api.py`.
- **Verification:** Perform a project-wide search for any remaining imports from the deleted files and resolve them.
