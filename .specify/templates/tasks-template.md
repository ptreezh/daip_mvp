---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  All tasks must align with DAIP-LIVE Constitution principles:
  - Module-First Design
  - CLI/TUI Interface
  - Test-First (NON-NEGOTIABLE)
  - Event-Driven Architecture
  - Convention over Configuration
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure aligned with DAIP-LIVE Constitution

- [ ] T001 Create project structure per implementation plan following src/daip_live directory structure
- [ ] T002 Initialize Python project with dependencies ensuring module-first design
- [ ] T003 [P] Configure linting and formatting tools ensuring 90%+ test coverage requirement

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema following DAIP-LIVE data persistence patterns
- [ ] T005 [P] Implement event-driven communication infrastructure using typed events from core/models.py
- [ ] T006 [P] Setup CLI and TUI interface frameworks ensuring both access patterns exist
- [ ] T007 Create base Pydantic models that all stories depend on following core/models.py patterns
- [ ] T008 Configure error handling and logging infrastructure with clear error reporting
- [ ] T009 Setup environment configuration management following DAIP-LIVE import conventions

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (REQUIRED - constitution compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
> **Constitution Requirement: All code must have tests with ≥90% coverage**

- [ ] T010 [P] [US1] Unit test for [core functionality] in tests/unit/test_[name].py ensuring 90%+ coverage
- [ ] T011 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py ensuring event-driven communication

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create [Entity1] model in src/daip_live/[module]/models.py following Pydantic patterns
- [ ] T013 [P] [US1] Create [Entity2] model in src/daip_live/[module]/models.py following Pydantic patterns
- [ ] T014 [US1] Implement [Service] in src/daip_live/[module]/[service].py (depends on T012, T013) using event-driven architecture
- [ ] T015 [US1] Implement CLI command in src/daip_live/cli.py for [feature] ensuring CLI/TUI interface compliance
- [ ] T016 [US1] Implement TUI handler in src/daip_live/tui.py for [feature] ensuring CLI/TUI interface compliance
- [ ] T017 [US1] Add validation and error handling with clear error messages
- [ ] T018 [US1] Add logging for user story 1 operations following DAIP-LIVE conventions

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently with 90%+ test coverage

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (REQUIRED - constitution compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
> **Constitution Requirement: All code must have tests with ≥90% coverage**

- [ ] T019 [P] [US2] Unit test for [core functionality] in tests/unit/test_[name].py ensuring 90%+ coverage
- [ ] T020 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py ensuring event-driven communication

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create [Entity] model in src/daip_live/[module]/models.py following Pydantic patterns
- [ ] T022 [US2] Implement [Service] in src/daip_live/[module]/[service].py using event-driven architecture
- [ ] T023 [US2] Implement CLI command in src/daip_live/cli.py for [feature] ensuring CLI/TUI interface compliance
- [ ] T024 [US2] Implement TUI handler in src/daip_live/tui.py for [feature] ensuring CLI/TUI interface compliance
- [ ] T025 [US2] Integrate with User Story 1 components using proper event-driven communication

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently with 90%+ test coverage

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (REQUIRED - constitution compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
> **Constitution Requirement: All code must have tests with ≥90% coverage**

- [ ] T026 [P] [US3] Unit test for [core functionality] in tests/unit/test_[name].py ensuring 90%+ coverage
- [ ] T027 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py ensuring event-driven communication

### Implementation for User Story 3

- [ ] T028 [P] [US3] Create [Entity] model in src/daip_live/[module]/models.py following Pydantic patterns
- [ ] T029 [US3] Implement [Service] in src/daip_live/[module]/[service].py using event-driven architecture
- [ ] T030 [US3] Implement CLI command in src/daip_live/cli.py for [feature] ensuring CLI/TUI interface compliance
- [ ] T031 [US3] Implement TUI handler in src/daip_live/tui.py for [feature] ensuring CLI/TUI interface compliance

**Checkpoint**: All user stories should now be independently functional with 90%+ test coverage

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Constitution Compliance & Cross-Cutting Concerns

**Purpose**: Ensuring all code aligns with DAIP-LIVE Constitution

- [ ] TXXX [P] Verify all modules follow src/daip_live directory structure (Module-First Design)
- [ ] TXXX Verify all functionality accessible via both CLI and TUI interfaces (CLI/TUI Interface)
- [ ] TXXX Run test coverage analysis ensuring ≥90% coverage across all modules (Test-First)
- [ ] TXXX Verify all communication uses typed events from core/models.py (Event-Driven Architecture)
- [ ] TXXX Verify all naming follows established conventions (Convention over Configuration)
- [ ] TXXX [P] Documentation updates in docs/ following DAIP-LIVE standards
- [ ] TXXX Code cleanup and refactoring for maintainability
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX Run final validation confirming constitution compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Constitution Compliance (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (REQUIRED) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority
- Constitution compliance check after each implementation

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for [core functionality] in tests/unit/test_[name].py ensuring 90%+ coverage"
Task: "Integration test for [user journey] in tests/integration/test_[name].py ensuring event-driven communication"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/daip_live/[module]/models.py following Pydantic patterns"
Task: "Create [Entity2] model in src/daip_live/[module]/models.py following Pydantic patterns"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup ensuring module-first design
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories) ensuring event-driven architecture
3. Complete Phase 3: User Story 1 ensuring CLI/TUI interface and 90%+ test coverage
4. **STOP and VALIDATE**: Test User Story 1 independently ensuring constitution compliance
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready with constitution compliance
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) ensuring 90%+ test coverage
3. Add User Story 2 → Test independently → Deploy/Demo ensuring constitution compliance
4. Add User Story 3 → Test independently → Deploy/Demo ensuring constitution compliance
5. Each story adds value without breaking previous stories or constitution principles

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together ensuring constitution alignment
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently while maintaining constitution compliance

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Test-First principle)
- Commit after each task or logical group with constitution compliance verification
- Stop at any checkpoint to validate story independently and constitution compliance
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **CRITICAL**: All code must follow DAIP-LIVE Constitution principles: Module-First Design, CLI/TUI Interface, Test-First (NON-NEGOTIABLE), Event-Driven Architecture, Convention over Configuration
