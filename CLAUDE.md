# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DAIP-LIVE (Dynamic AI Project - Live, Intelligent, Verifiable, Evolvable) is an intelligent collaboration platform focused on **hallucination suppression through social engineering**. The system creates a virtual team of AI agents with different roles and perspectives to identify, challenge, and suppress potential hallucinations through multi-role debate, adversarial discussion, and consensus mechanisms.

### Core Functionality
- **Multi-role AI collaboration**: 131+ specialized AI agents with unique expertise and perspectives
- **Three Core Scenarios**: Expert Consultation, Academic Research, and Industry Analysis
- **Forum Mode**: Advanced multi-agent debate and collaboration system
- **Dual-Entrance Architecture**: Both CLI and Web interfaces for comprehensive user experience
- **Real-time transparency monitoring**: User oversight of AI decision-making processes
- **Knowledge Management**: Integrated memory service, wiki service, and vector database

### Current Version: V0.3.12 (Production Ready)
- **Status**: 100% functional with comprehensive testing
- **Architecture**: Layered design with strict separation of concerns
- **Quality**: Production-ready with enterprise-grade error handling
- **Forum Mode**: Advanced multi-agent debate and collaboration system

## Architecture

The project follows a **layered architecture** with strict separation of concerns:

```
Application Layer (CLI + FastAPI + Web Interface)
    ↓
Protocol Layer (Workflow Manager, Debate Protocol, Agile Protocol)
    ↓  
Core Services (Role Manager, Memory Service, Wiki Service, Synthesis Engine)
    ↓
Kernel Layer (LLM Interface, Tool Executor, Context Segmenter)
```

### Key Components

**Core Services** (`src/core_services/`):
- `role_manager.py` - Manages 131+ AI role definitions and capabilities
- `memory_service.py` - Unified memory with SSKG integration for fact checking
- `wiki_service.py` - Versioned knowledge base for collaborative knowledge building
- `synthesis_engine.py` - Generates structured consensus from multi-agent discussions
- `expert_consultation_scenario.py` - Expert consultation workflow with real LLM integration
- `academic_research_scenario.py` - Academic research with literature review and analysis
- `industry_analysis_scenario.py` - Industry analysis with market intelligence
- `personal_intelligence_hub.py` - Central orchestrator for user interactions
- `forum_service.py` - Forum mode with multi-agent debate and collaboration

**Forum Service Components** (`src/core_services/forum_service.py`):
- **ForumService**: Main Forum session management and debate orchestration
- **DebateOrchestrator**: Multi-agent debate management and coordination
- **UserInterventionManager**: User input optimization and integration
- **ConsensusTracker**: Real-time consensus calculation and tracking
- **InputOptimizer**: Smart input optimization for better collaboration
- **ForumSession**: Data class for Forum session state management

**Forum API** (`src/api/routers/forum.py`):
- Session management endpoints (`/forum/sessions`)
- User intervention handling (`/forum/intervene`)
- Real-time debate state management (`/forum/state`)
- WebSocket integration for real-time updates
- Session control endpoints (`/forum/pause`, `/forum/resume`, `/forum/end`)

**Institutional Primitives** (`src/institutional_primitives/`):
- `workflow_engine.py` - Orchestrates complex multi-step workflows
- `critical_review_nodes.py` - Implements systematic peer review processes
- `multi_perspective/` - Parallel exploration and synthesis of different viewpoints

**Frontend Components** (`frontend/`):
- `components/` - Reusable UI components (chat interface, task panel, etc.)
- `services/` - Frontend services and backend connectors
- `dual_entrance_main.py` - Main web application entry point

**Personal Intelligence Hub** (`personal_intelligence_hub/`):
- Alternative frontend implementation with enhanced features
- `services/` - Hub-specific services and integrations
- `components/` - Hub-specific UI components

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

# Start web interface (dual entrance)
python frontend/dual_entrance_main.py

# Start personal intelligence hub
python personal_intelligence_hub/run_hub.py

# Alternative quick start scripts
python real_llm_integrated_demo.py      # Demo with real LLM integration
python web_demo_app.py                 # Web demo application
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

# List available roles
daip-cli roles
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

# Frontend integration tests
python frontend_integration_test.py

# Validation scripts
python validate_v0_3_11_implementation.py

# Forum mode testing
python simple_forum_test.py

# Forum service validation
python validate_forum_implementation.py
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

# Run all pre-commit hooks
pre-commit run --all-files
```

## Configuration

- Main config: `config.yaml` (auto-generated if missing)
- Default LLM: Ollama with `llama3:instruct` and `nomic-embed-text:latest`
- Vector store: ChromaDB (`data/chroma_db`)
- Roles: JSON files in `roles/` directory (131+ roles available)

### LLM Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3:instruct
ollama pull nomic-embed-text:latest
```

## Key Integration Points

**PersonalAssistant Service**: The main orchestrator located in:
- `src/core_services/personal_intelligence_hub.py` (primary)
- `frontend/services/personal_assistant.py` (frontend-specific)

**Four Core Scenarios**:
- **Expert Consultation**: Intelligent expert matching and decision support
- **Academic Research**: Literature review, research gap identification, academic writing
- **Industry Analysis**: Market analysis, competitive landscape, trend forecasting
- **Forum Mode**: Advanced multi-agent debate and real-time collaboration

**Forum Mode Features**:
- **Multi-Agent Debate**: Real-time collaboration between AI agents with different perspectives
- **User Intervention**: Smart input optimization and seamless integration into ongoing debates
- **Consensus Tracking**: Real-time consensus calculation and visualization
- **Session Management**: Complete session lifecycle control (start, pause, resume, end)
- **Real-time Communication**: WebSocket-based updates and state management
- **Intelligent Agent Selection**: Automatic matching of agents to debate topics
- **Debate Orchestration**: Structured debate process management and coordination

**Workflow Selection**: Automatic selection between:
- `CRITICAL_REVIEW` - Systematic peer review for quality assurance
- `MULTI_PERSPECTIVE` - Parallel exploration of different viewpoints  
- `SIMPLE_CHAT` - Direct conversation mode
- `FORUM_DEBATE` - Multi-agent real-time debate and collaboration

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
│   ├── scenario_services/  # Three core scenarios
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
└── scenarios/              # Predefined use case scenarios

frontend/                   # Web interface
├── components/            # UI components
├── services/              # Frontend services
├── static/                # CSS, JS, images
└── dual_entrance_main.py  # Main web app

personal_intelligence_hub/  # Alternative frontend
├── components/            # Hub-specific components
├── services/              # Hub services
└── run_hub.py             # Hub entry point
```

**Key Files:**
- `src/main.py` - FastAPI application entry point
- `src/app_state.py` - Application-wide dependency injection
- `src/config.py` - Configuration management
- `pyproject.toml` - Poetry dependencies and tool configurations
- `config.yaml` - Runtime configuration (auto-generated)
- `frontend/dual_entrance_main.py` - Web interface entry point

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
- Frontend integration tests for web interface
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

### Adding New Scenario
1. Create scenario service in `src/core_services/`
2. Implement scenario-specific workflow logic
3. Register with scenario integration service
4. Add frontend integration and API endpoints

### Forum Mode Development
**Forum Service Architecture**:
- Main service: `src/core_services/forum_service.py`
- API endpoints: `src/api/routers/forum.py`
- Frontend components: `frontend/components/forum/`
- WebSocket integration: Real-time debate updates

**Key Forum Components**:
1. **ForumService**: Central orchestration and session management
2. **DebateOrchestrator**: Multi-agent debate coordination
3. **UserInterventionManager**: Smart input optimization
4. **ConsensusTracker**: Real-time consensus calculation
5. **InputOptimizer**: User input enhancement

**Forum Session Lifecycle**:
1. **Start Session**: Create new Forum session with topic and agent selection
2. **Active Debate**: Real-time multi-agent collaboration with consensus tracking
3. **User Intervention**: Optimize and integrate user input into ongoing debates
4. **Pause/Resume**: Session control for debate management
5. **End Session**: Generate final consensus and save to memory

**Forum API Usage**:
```bash
# Start Forum session
curl -X POST "http://localhost:8000/forum/sessions" \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI ethics in autonomous vehicles", "user_id": "user123"}'

# Get session context
curl "http://localhost:8000/forum/sessions/{session_id}/context"

# Handle user intervention
curl -X POST "http://localhost:8000/forum/sessions/{session_id}/intervene" \
  -H "Content-Type: application/json" \
  -d '{"content": "What about safety considerations?", "intent": "question"}'

# Pause session
curl -X POST "http://localhost:8000/forum/sessions/{session_id}/pause"

# Resume session
curl -X POST "http://localhost:8000/forum/sessions/{session_id}/resume"

# End session
curl -X POST "http://localhost:8000/forum/sessions/{session_id}/end"
```

### Debugging Tips
- Use `daip-cli status` for comprehensive system health check
- Enable debug logging in `config.yaml` (`log_level: "DEBUG"`)
- Check individual service status via `/status` API endpoint
- Monitor ChromaDB connections and role loading separately
- Use frontend integration tests to verify web interface functionality

**Forum Mode Debugging**:
- Check Forum service status: `curl "http://localhost:8000/forum/status"`
- Monitor active sessions: `curl "http://localhost:8000/forum/sessions"`
- Test WebSocket connectivity: Use frontend WebSocket debugging tools
- Verify consensus tracking: Check session context endpoints
- Validate user intervention: Test intervention optimization and integration
- Monitor debate orchestration: Check debate state and agent coordination

### Validation and Diagnostic Scripts
```bash
# Comprehensive system validation
python validate_v0_3_11_implementation.py

# Frontend integration testing
python frontend_integration_test.py

# Test real LLM integration
python test_real_llm_integration.py

# Check Ollama service connectivity
python check_ollama_service.py

# System diagnosis
python comprehensive_system_diagnosis.py

# Git version release system
python execute_v0_3_11_release.py
```

## Important Notes

- **Dual-Entrance Architecture**: Both CLI and web interfaces are fully functional
- **Local LLM focus**: System designed for local models (Ollama) but supports cloud APIs
- **Production-grade components**: Core services have comprehensive testing and production-level quality
- **Modular consensus**: Consensus algorithms are pluggable and can be swapped without system changes
- **Context optimization**: System automatically handles long contexts through segmentation and summarization
- **Four Core Scenarios**: Expert Consultation, Academic Research, Industry Analysis, and Forum Mode are fully implemented
- **131+ AI Roles**: Comprehensive role library covering various domains and expertise areas
- **Forum Mode**: Advanced multi-agent debate system with real-time consensus tracking and user intervention optimization
- **Real-time Communication**: WebSocket-based architecture for live debate updates and state management
- **Session Management**: Complete lifecycle control for Forum debates with pause/resume/end capabilities

---

## 📋 MANDATORY DEVELOPMENT RULES

### 🚨 CRITICAL RULES (MUST FOLLOW)

1. **Code Quality Gates**
   - **NO COMMIT** without passing: `black src/ tests/ && ruff check src/ tests/ && mypy src/`
   - **NO EXCEPTIONS** for type hints - all functions require complete type annotations
   - **NO GENERIC EXCEPTIONS** - use specific exception types only

2. **File Headers MANDATORY**
   - **ALL .py files** must have standardized header:
   ```python
   # -*- coding: utf-8 -*-
   """
   @Time    : YYYY-MM-DD HH:MM:SS
   @Author  : DAIP-LIVE Team
   @File    : filename.py
   @Description:
       [Purpose description]
   """
   ```

3. **Testing Requirements**
   - **NEW CODE** = **NEW TESTS** - no features without test coverage
   - **MINIMUM 95%** pylint score for all new code
   - **ALL TESTS** must pass before any commit

4. **Documentation Standards**
   - **Google Style Docstrings** for all functions, classes, and modules
   - **NO CODE** without proper documentation
   - **Type hints** are part of documentation

### ⚠️ ENFORCEMENT RULES

5. **Pre-commit Hooks**
   - **pre-commit run --all-files** must pass before any commit
   - **Black formatting** is automatic and mandatory
   - **Ruff linting** failures block commits

6. **Architecture Compliance**
   - **STRICT LAYERED ARCHITECTURE** - no cross-layer dependencies
   - **DEPENDENCY INJECTION** through `AppState` only
   - **NO DIRECT IMPORTS** between services - use app_state

7. **Performance Standards**
   - **TOKEN EFFICIENCY** - optimize prompts and context
   - **MEMORY MANAGEMENT** - proper cleanup and resource management
   - **CONCURRENT PROCESSING** where appropriate

### 🔄 WORKFLOW RULES

8. **Development Process**
   - **BRANCH PROTECTION** - work on feature branches only
   - **INCREMENTAL COMMITS** - small, focused changes
   - **CODE REVIEW** - all changes must be reviewed

9. **Validation Requirements**
   - **COMPREHENSIVE TESTING** before any merge
   - **PERFORMANCE BENCHMARKS** for all new features
   - **MEMORY LEAK CHECKS** for long-running processes

### 🔧 CONFIGURATION RULES

10. **Environment Standards**
    - **PYTHON 3.10+** only - no legacy versions
    - **POETRY DEPENDENCIES** - no pip install without pyproject.toml update
    - **CONFIG FILES** - use config.yaml for runtime configuration

### 📊 QUALITY METRICS

11. **Code Quality Thresholds**
    - **Mypy strict mode** - no type errors allowed
    - **Ruff score** - zero warnings, zero errors
    - **Black formatting** - 100% compliance
    - **Test coverage** - minimum 80% for new code

12. **Documentation Metrics**
    - **100% docstring coverage** for public APIs
    - **README updates** for all new features
    - **CLAUDE.md updates** for architectural changes

---

**VIOLATION CONSEQUENCES**: Any violation of these rules will result in immediate rejection of code changes and required remediation before resuming work.

## 📖 Additional Resources

- **Full Documentation**: See `docs/MANDATORY_RULES.md` for comprehensive usage guide
- **Validation Tools**: Use `python mandatory_rules_checker.py` for local validation
- **CI/CD Integration**: Automatic enforcement via GitHub Actions
- **Troubleshooting**: Common issues and solutions documented in MANDATORY_RULES.md
- **Project Status**: See `PROJECT_STATUS_REPORT.md` for current development status
- **Implementation Reports**: See `V0_3_11_IMPLEMENTATION_COMPLETE.md` for milestone completion