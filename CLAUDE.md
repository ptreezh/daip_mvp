# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DAIP-LIVE (Dynamic AI Project - Live, Intelligent, Verifiable, Evolvable) is an intelligent collaboration platform focused on **hallucination suppression through social engineering**. The system creates a virtual team of AI agents with different roles and perspectives to identify, challenge, and suppress potential hallucinations through multi-role debate, adversarial discussion, and consensus mechanisms.

### Core Functionality
- **Multi-role AI collaboration**: Virtual team of specialized agents with unique expertise and perspectives
- **Academic research assistance**: Complex topic analysis through structured debates and consensus building
- **Automated agile project execution**: Task decomposition and knowledge management with version control
- **Real-time transparency monitoring**: User oversight of AI decision-making processes

## Architecture

The project follows a **layered architecture** with strict separation of concerns:

```
Application Layer (CLI + FastAPI)
    ↓
Protocol Layer (Workflow Manager, Debate Protocol, Agile Protocol)
    ↓  
Core Services (Role Manager, Memory Service, Wiki Service, Synthesis Engine)
    ↓
Kernel Layer (LLM Interface, Tool Executor, Context Segmenter)
```

### Key Components

**Core Services** (`src/core_services/`):
- `role_manager.py` - Manages AI role definitions and capabilities
- `memory_service.py` - Unified memory with SSKG integration for fact checking
- `wiki_service.py` - Versioned knowledge base for collaborative knowledge building
- `synthesis_engine.py` - Generates structured consensus from multi-agent discussions
- `consensus_models.py` + `*_algorithm.py` - Pluggable consensus algorithms (simple majority, Bayesian, weighted voting)
- `personal_assistant_adapter.py` - Unified entry point for user interactions

**Institutional Primitives** (`src/institutional_primitives/`):
- `workflow_engine.py` - Orchestrates complex multi-step workflows
- `critical_review_nodes.py` - Implements systematic peer review processes
- `multi_perspective/` - Parallel exploration and synthesis of different viewpoints

**Virtual Role Chat** (`src/virtual_role_chat/`):
- `cognitive_agent/` - Individual AI agent with belief systems and reasoning
- `context_optimizer/` - Dynamic context adaptation for optimal performance
- `sskg/` - Semantic Structured Knowledge Graph for fact validation

## Development Commands

### Environment Setup
```bash
# Install with Poetry (preferred)
poetry install

# Or with pip
pip install -e .

# Install Ollama models (required for local LLM)
ollama pull llama3:instruct
ollama pull nomic-embed-text:latest
```

### Development Server
```bash
# Start FastAPI backend (main entry point)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Alternative quick start scripts
python run.py                           # Basic server
python real_llm_integrated_demo.py      # Demo with real LLM integration
python auto_demo_system.py              # Automated demo system
```

### CLI Usage
```bash
# CLI entry point (defined in pyproject.toml)
daip-cli status

# Alternative CLI access
python -m src.cli.main status
python src/cli/main.py status

# Start debates and workflows
daip-cli start "topic" --role "expert1" --role "expert2" --rounds 3
```

### Testing
```bash
# Run all tests with pytest
pytest

# Run specific test categories
pytest tests/core_services/
pytest tests/institutional_primitives/
pytest tests/cli/

# Run with coverage
pytest --cov=src --cov-report=html

# Test specific components
pytest tests/test_role_manager.py -v
pytest src/core_services/test_consensus_models.py -v

# Integration testing
python test_real_llm_integration.py
python comprehensive_validation.py
```

### Code Quality
```bash
# Format code (configured for 120 line length)
black src/ tests/

# Type checking with mypy (strict mode enabled)
mypy src/

# Linting with Ruff (replaces pylint for speed)
ruff check src/ tests/
ruff format src/ tests/

# Legacy pylint (if needed)
pylint src/

# Run all pre-commit hooks
pre-commit run --all-files
```

## Configuration

- Main config: `config.yaml` (auto-generated if missing)
- Default LLM: Ollama with `llama3:instruct` and `nomic-embed-text:latest`
- Vector store: ChromaDB (`data/chroma_db`)
- Roles: JSON files in `roles/` directory

### LLM Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3:instruct
ollama pull nomic-embed-text:latest
```

## Key Integration Points

**PersonalAssistant Service**: The main orchestrator located in both:
- `frontend/services/personal_assistant.py` (basic version)
- `personal_intelligence_hub/services/personal_assistant.py` (full-featured)

**Workflow Selection**: Automatic selection between:
- `CRITICAL_REVIEW` - Systematic peer review for quality assurance
- `MULTI_PERSPECTIVE` - Parallel exploration of different viewpoints  
- `SIMPLE_CHAT` - Direct conversation mode

**Memory Integration**: All services connect through:
- SSKG Manager for structured knowledge
- MemAgent for contextual memory
- Wiki Service for collaborative knowledge building

## Development Patterns

### Coding Standards (from docs/CODING_STANDARDS.md)
- **PEP 8 compliance**: All Python code must follow PEP 8 standards
- **Type annotations**: All functions require complete type hints (mypy strict mode)
- **File headers**: All .py files must include standardized headers with @Time, @Author, @File, @Description
- **Google Style Docstrings**: Use Google Python Style for all docstrings
- **Line length**: Maximum 120 characters (configured in black and ruff)
- **Error handling**: Use specific exceptions, avoid generic except clauses

### File Structure Convention
```
src/
├── core_services/          # Business logic services
│   ├── consensus_models.py + *_algorithm.py  # Pluggable consensus algorithms
│   ├── role_manager.py     # AI role definitions and capabilities
│   ├── memory_service.py   # Unified memory with SSKG integration
│   ├── wiki_service.py     # Versioned knowledge base
│   └── synthesis_engine.py # Consensus generation from discussions
├── institutional_primitives/  # Workflow orchestration
│   ├── workflow_engine.py  # Core workflow execution
│   ├── critical_review_nodes.py  # Peer review processes
│   └── multi_perspective/  # Parallel viewpoint exploration
├── virtual_role_chat/      # Multi-agent system
│   ├── cognitive_agent/    # Individual AI agents with beliefs
│   ├── context_optimizer/  # Dynamic context adaptation
│   └── sskg/              # Semantic knowledge graphs
├── kernel/                 # Low-level utilities
│   ├── llm_interface.py   # LLM abstraction layer
│   ├── ollama_llm.py      # Ollama-specific implementation
│   └── vector_store.py    # ChromaDB integration
├── api/                    # FastAPI endpoints
│   └── routers/           # API route definitions
├── cli/                    # Command-line interface
│   └── main.py           # CLI entry point (daip-cli command)
├── protocols/              # High-level workflows
├── real_demo_system/       # Demo and validation components
└── scenarios/              # Predefined use case scenarios
```

**Key Files:**
- `src/main.py` - FastAPI application entry point
- `src/app_state.py` - Application-wide dependency injection
- `src/config.py` - Configuration management
- `pyproject.toml` - Poetry dependencies and tool configurations
- `config.yaml` - Runtime configuration (auto-generated)

### Service Integration Pattern
Services follow dependency injection through `AppState` in `src/app_state.py`. All services are initialized once and shared across the application.

### Error Handling
- Use specific exception types from `src/core/exceptions.py`
- Log errors with appropriate levels using the configured logger
- Implement graceful degradation for non-critical failures

### Testing Strategy
- Unit tests for individual components
- Integration tests for service interactions  
- End-to-end tests for complete workflows
- Mock external dependencies (LLM calls, file I/O)

## Common Tasks

### Adding a New Role
1. Create JSON file in `roles/` directory
2. Define role characteristics, expertise, and prompt template
3. Test role loading with `daip-cli roles`

### Implementing New Consensus Algorithm
1. Extend `ConsensusAlgorithmInterface` in `src/core_services/`
2. Register in `ConsensusStrategyFactory`
3. Add integration tests

### Adding Workflow Nodes
1. Inherit from base classes in `src/institutional_primitives/base.py`
2. Implement required methods (`execute`, `validate_inputs`)
3. Register in workflow templates

### Debugging Tips
- Use `daip-cli status` for comprehensive system health check
- Enable debug logging in `config.yaml` (`log_level: "DEBUG"`)
- Check individual service status via `/status` API endpoint
- Monitor ChromaDB connections and role loading separately

### Validation and Diagnostic Scripts
```bash
# Comprehensive system validation
python comprehensive_validation.py

# Test real LLM integration
python test_real_llm_integration.py

# Validate V0.2.3 implementation
python validate_v0_2_3_implementation.py

# Check Ollama service connectivity
python check_ollama_service.py

# Auto-test and start validation
python auto_test_and_start.py

# System diagnosis
python comprehensive_system_diagnosis.py
```

## Important Notes

- **CLI-first development**: All functionality must be accessible via CLI before adding web UI
- **Local LLM focus**: System designed for local models (Ollama) but supports cloud APIs
- **Production-grade components**: Core services have 100% test coverage and production-level quality
- **Modular consensus**: Consensus algorithms are pluggable and can be swapped without system changes
- **Context optimization**: System automatically handles long contexts through segmentation and summarization