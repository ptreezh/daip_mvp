# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Project Overview

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE system) is a local-first AI agent workstation designed for single-user environments. It's a modular monolith application that enables multi-AI role collaboration, structured debates, and local knowledge management with a focus on privacy, transparency, and user control.

## Core Architecture Principles

- **Local-First**: All core data (knowledge base, configurations, session history) stored locally in SQLite and file system
- **Modular Monolith**: Single Python process with clear module boundaries communicating via direct function calls
- **Event-Driven Agent Execution**: Dynamic agent loops rather than static workflows
- **Transparency**: Real-time display of AI thinking processes and user intervention capabilities

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running the Application
> 本机无 poetry 时用 `py -m daip_live.cli.main` 等价调用（如 `py -m daip_live.cli.main run`）。
```bash
# Start interactive TUI session
poetry run daip run
# Sync knowledge base manually
poetry run daip knowledge sync

# Manage sessions (list/clear only; no show subcommand exists)
poetry run daip session list

# Run debates
poetry run daip debate start <topic>
poetry run daip debate history

# Manage AI roles
poetry run daip role list
poetry run daip role show <role_name>

# Manage models
poetry run daip model list
poetry run daip model status
```
(Note: no `project` subcommand exists in the current CLI; scaffolding commands are not available.)

### Testing
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_cli.py

# Run tests with verbose output
poetry run pytest -v

# Run tests with coverage
poetry run pytest --cov=src

# Run only specific test patterns
poetry run pytest -k "test_debate"

# Run async tests specifically
poetry run pytest --asyncio-mode=auto
```

### Code Quality
```bash
# Lint code
poetry run ruff check src/

# Format code
poetry run ruff format src/

# Type checking
poetry run mypy src/

# Apply lint fixes
poetry run ruff check --fix src/

# Check for specific issues
poetry run ruff check --select E,F,W src/
```

## Key Architecture Components

### Core Modules (P1-P8 Priority System)

**P1 - Data Persistence**: `src/daip_live/persistence/`
- SQLite database management (`database.py`)
- Schema definitions (`tables.py`)
- Knowledge metadata storage

**P2 - Knowledge Management**: `src/daip_live/knowledge/`, `src/daip_live/wiki/`
- Document ingestion and vectorization
- FAISS/ChromaDB vector storage
- Semantic search capabilities

**P3 - Model Provider**: `src/daip_live/model_provider/`
- Unified LLM interface supporting local (Ollama) and cloud models
- Embedding model abstraction
- Model switching capabilities

**P4 - Role & Tool Manager**: `src/daip_live/p4_role_manager_tools/`
- AI role configuration and management
- Tool registration and execution
- Role model configuration

**P5 - Agent Engine**: `src/daip_live/agent_engine/`
- Dynamic agent execution loops
- Intent recognition and workflow orchestration
- Session and state management

**P6 - CLI/TUI Interface**: `src/daip_live/cli.py`, `src/daip_live/tui.py`
- Command-line interface using Typer
- Terminal UI using Textual
- Enhanced TUI with real-time updates
- Keyboard shortcuts:
  - `Ctrl+Q`: Terminate current session / Exit application (press twice)
  - `Ctrl+E`: Exit application (press twice)
  - `Ctrl+C`: Copy selected text
  - `Ctrl+A`: Select all text

**P7 - Web GUI**: `src/daip_live/p7_gui/`
- FastAPI-based web interface
- REST API endpoints

**P8 - Debate System**: `src/daip_live/p8_debate_system/`
- Multi-agent structured debates
- Role selection and argument management
- Enhanced debate orchestration

### Cross-Cutting Services

**Memory System**: `src/daip_live/memory/`
- Short-term session memory
- Long-term knowledge retention
- Layered memory architecture

**Security & Permissions**: `src/daip_live/permission/`, `src/daip_live/security/`
- User permission management
- Tool execution control
- Security rule enforcement

**Container & DI**: `src/daip_live/container.py`
- Dependency injection setup
- Service lifecycle management

## Data Storage Structure

> 注（2026-08-09 实测修正）：实际数据均在项目根目录（`daip_live.db` 1.7MB、`config.yaml`、`knowledge/`、`roles/`、`backups/`），不在 `data/` 下；`data/` 仅存日志。`daip_live.db`/`knowledge/index.faiss` 已移出 git 跟踪（S3-1），备份由每日计划任务 `DAIP-Live Backup` 写入 `backups/`。

```
项目根/
├── daip_live.db              # SQLite database（不跟踪 git，每日备份）
├── knowledge/                # 用户文档 + wiki 页 + index.faiss（索引不跟踪 git）
├── roles/                   # AI role configurations (yaml)
├── config.yaml             # Main configuration（embedding_dimension=768）
├── backups/                # 每日自动备份 zip（含 db + config + knowledge）
├── data/                   # 仅日志
└── log/                    # 日志
```

## Configuration

- Main config: `config.yaml`（项目根）
- Model provider settings (local vs cloud)（当前仅本地 Ollama；云端混合路由为已确认硬需求、暂缓实施）
- API keys and endpoints（`.env`，已 gitignore）
- Role definitions stored as JSON/YAML in `roles/`

## Testing Strategy

- Unit tests for individual components
- Integration tests for agent workflows
- Real model integration tests (when available)
- Async testing support with pytest-asyncio
- Mock-based testing for external dependencies

## Development Notes

- Python 3.9+ required (excluding 3.9.7)
- Uses Poetry for dependency management
- Ruff for linting/formatting, MyPy for type checking
- Extensive test coverage with pytest
- Async/await patterns throughout for responsiveness
- Event-driven architecture with asyncio.Queue for user interventions