<!-- Sync Impact Report:
Version change: N/A → 1.0.0
Modified principles: N/A (new constitution)
Added sections: All sections added for DAIP-LIVE project
Removed sections: All template placeholders removed
Templates requiring updates: ✅ .specify/templates/plan-template.md, ✅ .specify/templates/spec-template.md, ✅ .specify/templates/tasks-template.md, ✅ .specify/templates/agent-file-template.md, ✅ .specify/templates/checklist-template.md
Follow-up TODOs: None
-->

# DAIP-LIVE Constitution

## Core Principles

### I. Module-First Design
Every feature starts as a well-defined module within the src/daip_live directory structure; Modules must be self-contained with clear responsibilities, following the SOLID principles; Clear purpose required - no organizational-only modules without specific functionality.

### II. CLI/TUI Interface
Every core functionality is accessible via both CLI and TUI interfaces; All communication follows structured input/output protocols with consistent event models defined in core/models.py; Support both command-line arguments and interactive modes for different user scenarios.

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: Unit tests written before implementation → Integration tests cover component interactions → Tests must fail initially → Then implement to make tests pass; Red-Green-Refactor cycle strictly enforced with 90%+ coverage requirement.

### IV. Event-Driven Architecture
All communication between components follows an event-driven pattern; Services yield and consume typed events defined in core/models.py using Pydantic models; Loose coupling achieved through event streams rather than direct function calls or shared state.

### V. Convention over Configuration
Follow established project naming conventions and directory structures to minimize cognitive load; Default configurations should work out-of-the-box; Import convention: always use daip_live prefix for internal modules (from daip_live.core import... instead of from src.daip_live.core import...).

## Development Standards

The DAIP-LIVE project implements a modular monolith architecture with clear separation of concerns:
- Core services in P0-P8 packages with well-defined responsibilities
- Dependency injection container for managing component lifecycles
- Async/await patterns for non-blocking operations
- Pydantic models for all data structures and configuration

## Testing and Quality Assurance

All code must meet the following standards:
- Unit test coverage ≥ 90%
- Integration tests for inter-component communication
- Type hints on all public interfaces
- Comprehensive error handling and logging
- Performance benchmarks for critical paths
- Security-focused validation for all external inputs

## Governance
The DAIP-LIVE Constitution supersedes all other development practices; Amendments require documentation, approval by core team, and migration plan for existing code; All PRs/reviews must verify compliance with these principles; Use PROJECT_EXECUTION_STANDARDS.md for detailed development guidance.

**Version**: 1.0.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-11-06
