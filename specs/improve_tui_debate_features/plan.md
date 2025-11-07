# Implementation Plan: Improve TUI Debate Features

**Branch**: `improve-tui-debate-features` | **Date**: 2025-11-06 | **Spec**: [link to spec.md]

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the TUI debate functionality by improving visual representation of debate participants, adding history navigation, and implementing multi-model support for different debate roles.

## Technical Context

**Language/Version**: Python 3.9+  
**Primary Dependencies**: textual, pydantic, asyncio, dependency-injector  
**Storage**: N/A (in-memory session storage)  
**Testing**: pytest  
**Target Platform**: Cross-platform (Windows, macOS, Linux)  
**Project Type**: Single monolithic application (determines source structure)  
**Performance Goals**: <500ms response time for debate state updates  
**Constraints**: <80MB memory usage, maintain 90%+ test coverage  
**Scale/Scope**: Single user, multiple concurrent debate sessions possible  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates determined based on DAIP-LIVE Constitution:
- Module-First Design: All features must be designed as well-defined modules within the src/daip_live directory structure
- CLI/TUI Interface: All functionality must be accessible via CLI and TUI interfaces
- Test-First (NON-NEGOTIABLE): All code must have tests with ≥90% coverage requirement
- Event-Driven Architecture: All components must communicate via typed events defined in core/models.py
- Convention over Configuration: All code must follow established naming conventions and directory structures

## Project Structure

### Documentation (this feature)

```text
specs/improve-tui-debate-features/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── daip_live/
│   ├── agent_engine/          # Agent execution engine
│   ├── p8_debate_system/      # Debate system components
│   ├── tui_v1/                # TUI components
│   ├── core/                  # Core models and interfaces
│   ├── memory/                # Memory services
│   └── container.py           # Dependency injection
```

**Structure Decision**: Implement debate enhancements as extensions to existing modules in src/daip_live/, following existing architecture patterns with new classes for enhanced functionality while maintaining compatibility with existing interfaces.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |