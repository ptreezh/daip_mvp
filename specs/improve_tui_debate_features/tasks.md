---

description: "Task list for improving TUI debate features"
---

# Tasks: Improve TUI Debate Features

**Input**: Design documents from `/specs/improve-tui-debate-features/`
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

- [X] T001 Create project structure per implementation plan following src/daip_live directory structure
- [X] T002 Analyze existing debate system architecture in src/daip_live/p8_debate_system/
- [X] T003 [P] Review existing TUI debate implementation in src/daip_live/tui.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Identify current debate event models in src/daip_live/core/models.py
- [X] T005 [P] Create enhanced debate event models for better visualization
- [X] T006 [P] Design data structures for debate history tracking
- [X] T007 Modify existing debate manager to support enhanced event tracking
- [X] T008 Update container.py to support new debate services
- [X] T009 Create enhanced debate view models in src/daip_live/tui_v1/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Enhanced Debate View (Priority: P1) 🎯 MVP

**Goal**: Improve visual representation of debate participants and turns in TUI

**Independent Test**: User can start a debate via TUI and see clear visual indicators of speakers

### Tests for User Story 1 (REQUIRED - constitution compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
> **Constitution Requirement: All code must have tests with ≥90% coverage**

- [X] T010 [P] [US1] Unit test for enhanced debate visualization in tests/unit/test_debate_visualization.py ensuring 90%+ coverage
- [X] T011 [P] [US1] Integration test for debate event display in tests/integration/test_debate_display.py ensuring event-driven communication

### Implementation for User Story 1

- [X] T012 [P] [US1] Create EnhancedDebateView model in src/daip_live/tui_v1/models.py following Pydantic patterns
- [X] T013 [P] [US1] Update TUI debate event handlers in src/daip_live/tui.py following event-driven architecture
- [X] T014 [US1] Implement visual speaker identification in src/daip_live/tui.py for [feature] ensuring CLI/TUI interface compliance
- [X] T015 [US1] Add color coding for different debate participants
- [X] T016 [US1] Add clear turn indicators for debate participants
- [X] T017 [US1] Add logging for debate visualization operations following DAIP-LIVE conventions

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently with 90%+ test coverage

---

## Phase 4: User Story 2 - Debate History Navigation (Priority: P2)

**Goal**: Implement ability to navigate and view debate history

**Independent Test**: User can access debate history after completion

### Tests for User Story 2 (REQUIRED - constitution compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
> **Constitution Requirement: All code must have tests with ≥90% coverage**

- [X] T018 [P] [US2] Unit test for debate history tracking in tests/unit/test_debate_history.py ensuring 90%+ coverage
- [X] T019 [P] [US2] Integration test for history navigation in tests/integration/test_debate_history.py ensuring event-driven communication

### Implementation for User Story 2

- [X] T020 [P] [US2] Create DebateHistory model in src/daip_live/tui_v1/models.py following Pydantic patterns
- [X] T021 [US2] Implement debate history tracking in src/daip_live/p8_debate_system/history_tracker.py using event-driven architecture
- [X] T022 [US2] Implement history view in TUI in src/daip_live/tui.py for [feature] ensuring CLI/TUI interface compliance
- [X] T023 [US2] Add CLI command to access debate history in src/daip_live/cli.py for [feature] ensuring CLI/TUI interface compliance
- [X] T024 [US2] Integrate with User Story 1 components using proper event-driven communication

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently with 90%+ test coverage

---

## Phase 5: User Story 3 - Multi-Model Debate Support (Priority: P3)

**Goal**: Implement support for different models per debate participant

**Independent Test**: User can specify different models for debate participants and verify model switching

### Tests for User Story 3 (REQUIRED - constitution compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
> **Constitution Requirement: All code must have tests with ≥90% coverage**

- [X] T025 [P] [US3] Unit test for model mapping functionality in tests/unit/test_model_mapping.py ensuring 90%+ coverage
- [X] T026 [P] [US3] Integration test for multi-model debate in tests/integration/test_multi_model_debate.py ensuring event-driven communication

### Implementation for User Story 3

- [X] T027 [P] [US3] Create ModelMapping model in src/daip_live/p4_role_manager_tools/models.py following Pydantic patterns
- [X] T028 [US3] Implement model switching logic in src/daip_live/p8_debate_system/model_manager.py using event-driven architecture
- [X] T029 [US3] Implement multi-model CLI command in src/daip_live/cli.py for [feature] ensuring CLI/TUI interface compliance
- [X] T030 [US3] Implement multi-model handling in TUI in src/daip_live/tui.py for [feature] ensuring CLI/TUI interface compliance

**Checkpoint**: All user stories should now be independently functional with 90%+ test coverage

---

## Phase N: Constitution Compliance & Cross-Cutting Concerns

**Purpose**: Ensuring all code aligns with DAIP-LIVE Constitution

- [X] TXXX [P] Verify all modules follow src/daip_live directory structure (Module-First Design)
- [X] TXXX Verify all functionality accessible via both CLI and TUI interfaces (CLI/TUI Interface)
- [X] TXXX Run test coverage analysis ensuring ≥90% coverage across all modules (Test-First)
- [X] TXXX Verify all communication uses typed events from core/models.py (Event-Driven Architecture)
- [X] TXXX Verify all naming follows established conventions (Convention over Configuration)
- [X] TXXX [P] Documentation updates in docs/ following DAIP-LIVE standards
- [X] TXXX Code cleanup and refactoring for maintainability
- [X] TXXX Performance optimization across all stories
- [X] TXXX Run final validation confirming constitution compliance

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

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Test-First principle)
- Commit after each task or logical group with constitution compliance verification
- Stop at any checkpoint to validate story independently and constitution compliance
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **CRITICAL**: All code must follow DAIP-LIVE Constitution principles: Module-First Design, CLI/TUI Interface, Test-First (NON-NEGOTIABLE), Event-Driven Architecture, Convention over Configuration