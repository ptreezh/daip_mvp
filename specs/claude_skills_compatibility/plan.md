# Implementation Plan: Claude Skills Format Compatibility

**Branch**: `feature-claude-skills-compatibility` | **Date**: 2025-11-19 | **Spec**: [link to spec.md]

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement Claude Skills format compatibility that allows automatic discovery, parsing, registration, and execution of Claude-compatible skills. This system will provide progressive disclosure of skill information and secure execution of external skills.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: pydantic, requests, yaml, pathlib, asyncio
**Storage**: Skills directory, manifest cache, skill metadata database
**Testing**: pytest with 90%+ coverage
**Target Platform**: Cross-platform
**Project Type**: Single monolithic application (determines source structure)
**Performance Goals**: <500ms for skill discovery, <2s for skill execution
**Constraints**: <80MB memory usage, maintain 90%+ test coverage, security sandboxing
**Scale/Scope**: Single user, supports multiple Claude Skills

## Constitution Compliance Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates determined based on DAIP-LIVE Constitution:
- ✅ Module-First Design: All features as well-defined modules within src/daip_live/skills/ directory structure
- ✅ CLI/TUI Interface: All functionality accessible via both interfaces  
- ✅ Test-First (NON-NEGOTIABLE): All code with ≥90% test coverage requirement
- ✅ Event-Driven Architecture: All components communicate via typed events from core/models.py
- ✅ Convention over Configuration: Follow established naming and directory structures

## Project Structure

### Documentation (this feature)

```text
specs/claude_skills_compatibility/
├── spec.md              # Feature specification document (this file)
├── plan.md              # Implementation plan (this file)
├── research.md          # Research and analysis findings
├── data-model.md        # Data model specifications  
├── quickstart.md        # Quick start guide for new developers
├── contracts/           # API contracts and interface definitions
└── tasks.md             # Task breakdown and execution plan
```

### Source Code (repository root)

```text
src/
└── daip_live/
    └── skills/
        ├── __init__.py
        ├── base.py          # Updated to support Claude Skills format
        ├── manager.py       # Enhanced with Claude Skills discovery and loading
        ├── claude_adapter.py # NEW: Claude Skills format adapter
        ├── claude_repository.py # NEW: GitHub Claude Skills downloader
        ├── claude_security.py # NEW: Security sandbox for Claude Skills
        ├── progressive_disclosure.py # NEW: Progressive skill information system
        └── models/
            └── claude_models.py    # NEW: Claude Skills data models
```

**Structure Decision**: Create dedicated Claude Skills modules that integrate with existing SkillManager architecture. Claude Skills will use adapters to work with existing DAIP-LIVE skill interfaces while maintaining security isolation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Change History

### 2025-11-19 - Initial Specification Creation  
- Created spec.md documenting Claude Skills compatibility requirements
- Defined user scenarios and acceptance criteria
- Specified security and compatibility requirements

### 2025-11-19 - Architecture Design
- Designed Claude Skills adapter pattern to convert Claude format to DAIP-LIVE format
- Planned security sandbox to isolate external skill execution
- Designed progressive disclosure UI for skill information

### 2025-11-19 - Model Definition  
- Defined data models for Claude Skills manifests and metadata
- Created security policy models for skill execution
- Designed progressive information models

### 2025-11-19 - Integration Planning
- Planned integration with existing intent recognition system
- Designed automatic skill discovery from GitHub repositories
- Created mapping between Claude Skills and natural language intents