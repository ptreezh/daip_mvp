# Technology Stack

**Analysis Date:** 2026-08-07

## Languages

**Primary:**
- Python 3.9+ - Core application language (supports 3.9.7+ and <3.13)

**Secondary:**
- SQL - Database queries through SQLAlchemy ORM
- YAML - Configuration files (`config.yaml`)
- Markdown - Documentation and wiki pages

## Runtime

**Environment:**
- Python 3.9+ with asyncio support
- Local execution environment (single-user, privacy-first)

**Package Manager:**
- Poetry (primary) - Lockfile present: `poetry.lock`
- pip/pipx - Alternative installation

## Frameworks

**Core:**
- Textual 0.66+ - TUI framework for terminal-based interactive interface
- Typer 0.17+ - CLI framework for command-line interface
- Pydantic 2.7+ - Data validation and settings management
- SQLAlchemy 2.0+ - Database ORM

**Testing:**
- pytest 8.2+ - Test runner
- pytest-asyncio 1.2+ - Async test support
- pytest-mock 3.14+ - Mocking support

**Build/Dev:**
- ruff 0.4+ - Linting and formatting
- mypy 1.10+ - Type checking
- pre-commit 3.7+ - Git hooks

## Key Dependencies

**Critical:**
- litellm 1.76+ - Multi-model LLM provider interface
- faiss-cpu 1.8+ - Vector similarity search for knowledge base
- langchain 0.2+ - LLM orchestration framework
- dependency-injector 4.41+ - Dependency injection container

**Infrastructure:**
- FastAPI 0.116+ - REST API for GUI integration
- uvicorn 0.35+ - ASGI server
- aiofiles 25.1+ - Async file operations
- rich 14.1+ - Terminal formatting

**Data/Processing:**
- PyYAML 6.0+ - Configuration parsing
- python-docx 1.1+ - Word document processing
- arxiv 2.1+ - Academic paper integration
- scholarly 1.7+ - Academic search
- numpy (via faiss) - Numerical operations

## Configuration

**Environment:**
- YAML-based configuration (`config.yaml`)
- Environment variables via `.env` (not in git)
- ConfigManager for runtime access

**Build:**
- `pyproject.toml` - Poetry-based build configuration
- `poetry.lock` - Locked dependency versions
- ruff for code formatting (line-length: 88, target-version: py39)

## Platform Requirements

**Development:**
- Python 3.9+ (3.9.7+ recommended, not 3.13)
- Poetry for dependency management
- Git for version control

**Production:**
- Local execution (single-user environment)
- SQLite for data persistence
- Optional: Ollama for local models

---

*Stack analysis: 2026-08-07*
