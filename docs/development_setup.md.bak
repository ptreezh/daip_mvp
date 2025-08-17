# Development Setup Guide

This guide provides comprehensive instructions for setting up a development environment for the DAIP-LIVE project.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10 or higher
- pip (Python package installer)
- git
- A text editor or IDE (VS Code recommended)
- Ollama (for local LLM support)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/daip-live.git
cd daip-live
```

### 2. Create a Virtual Environment

#### Using venv (recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```bash
  venv\Scripts\activate
  ```

- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

#### Using conda

```bash
conda create -n daip-live python=3.10
conda activate daip-live
```

### 3. Install Dependencies

```bash
pip install -e .
```

This will install the project in development mode, allowing you to make changes to the code without reinstalling.

### 4. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This will install additional dependencies needed for development, such as testing tools.

### 5. Set Up Ollama

Ollama is used for local LLM support. Follow these steps to set it up:

1. Download and install Ollama from [https://ollama.ai/](https://ollama.ai/)

2. Pull the required models:
   ```bash
   ollama pull llama3:instruct
   ollama pull nomic-embed-text:latest
   ```

3. Start the Ollama server:
   ```bash
   ollama serve
   ```

### 6. Create Configuration File

Create a `config.yaml` file in the project root with the following content:

```yaml
llm:
  provider: "ollama"
  ollama:
    generation_model: "llama3:instruct"
    embedding_model: "nomic-embed-text:latest"
    host: "http://localhost:11434"
    timeout: 30

vector_store:
  chroma_db_path: "data/chroma_db"
  role_collection_name: "roles"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

token_management:
  max_context_tokens: 4096
  cost_per_1k_input_tokens: 0.0
  cost_per_1k_output_tokens: 0.0
  enable_cost_tracking: true
  enable_context_optimization: true
  compression_threshold: 0.8

user_profile:
  data_dir: "data/user_profiles"
  max_interaction_history: 100
  enable_intent_tracking: true

session:
  auth_data_dir: "data/auth"
  session_expiry_minutes: 60
  token_expiry_minutes: 60
  enable_session_tracking: true
```

## Project Structure

The DAIP-LIVE project follows a modular architecture:

```
daip-live/
├── .kiro/                  # Kiro IDE configuration
├── configs/                # Configuration files
├── data/                   # Data storage
├── docs/                   # Documentation
├── roles/                  # Role definitions
├── schemas/                # JSON schemas
├── src/                    # Source code
│   ├── api/                # FastAPI endpoints
│   ├── cli/                # Command-line interface
│   ├── core_services/      # Core services
│   ├── kernel/             # Kernel components
│   ├── protocols/          # Protocol implementations
│   └── tools/              # Tool implementations
├── tests/                  # Test suite
└── ui/                     # User interface
```

## Running the Application

### Starting the API Server

```bash
python -m src.main
```

The API server will start on http://localhost:8000 by default.

### Using the CLI

```bash
python -m src.cli.main --help
```

This will display the available CLI commands.

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Implement your changes following the project's architecture and coding standards.

### 3. Run Tests

```bash
pytest
```

To run specific tests:

```bash
pytest tests/test_specific_module.py
```

To run tests with coverage:

```bash
pytest --cov=src
```

### 4. Format and Lint Code

```bash
# Format code
black src tests

# Check imports
isort src tests

# Lint code
ruff src tests
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

### 6. Push Changes

```bash
git push origin feature/your-feature-name
```

### 7. Create a Pull Request

Create a pull request on GitHub with a clear description of your changes.

## Extending the System

### Adding a New Service

1. Create a new file in the appropriate directory (e.g., `src/core_services/your_service.py`)
2. Define your service class
3. Update `src/app_state.py` to initialize and register your service
4. Add tests in the `tests` directory

Example service:

```python
# src/core_services/your_service.py

class YourService:
    def __init__(self, dependency1, dependency2):
        self.dependency1 = dependency1
        self.dependency2 = dependency2
        
    def your_method(self, param1, param2):
        # Implementation
        pass
```

Update `src/app_state.py`:

```python
from src.core_services.your_service import YourService

# In the AppState.__init__ method:
self.your_service = YourService(
    dependency1=self.dependency1,
    dependency2=self.dependency2
)
```

### Adding a New API Endpoint

1. Create a new file in `src/api/routers` or update an existing one
2. Define your router and endpoints
3. Update `src/main.py` to include your router

Example router:

```python
# src/api/routers/your_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from src.api import dependencies

router = APIRouter(
    prefix="/api/your-resource",
    tags=["your-resource"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_resources(app_state=Depends(dependencies.get_app_state)):
    return await app_state.your_service.get_resources()

@router.post("/")
async def create_resource(request: YourRequestModel, app_state=Depends(dependencies.get_app_state)):
    return await app_state.your_service.create_resource(request)
```

Update `src/main.py`:

```python
from src.api.routers import your_router

# In the app initialization section:
app.include_router(your_router.router)
```

### Adding a New Consensus Strategy

1. Create a new file in `src/protocols/consensus_strategies`
2. Define your strategy class that implements the `ConsensusStrategy` interface
3. Update `src/protocols/consensus_strategies/__init__.py` to export your strategy
4. Update `src/main.py` to register your strategy

Example strategy:

```python
# src/protocols/consensus_strategies/your_strategy.py

from src.protocols.consensus_strategies.base import ConsensusStrategy
from src.models import Opinion, ConsensusResult

class YourStrategy(ConsensusStrategy):
    def __init__(self, your_param=None):
        self.your_param = your_param
        
    async def execute(self, opinions):
        # Implementation
        return ConsensusResult(
            consensus_text="Your consensus text",
            agreement_level=0.8,
            method_description="Your strategy description"
        )
```

Update `src/protocols/consensus_strategies/__init__.py`:

```python
from src.protocols.consensus_strategies.base import ConsensusStrategy, ConsensusStrategyFactory
from src.protocols.consensus_strategies.simple_majority_vote import SimpleMajorityVoteStrategy
from src.protocols.consensus_strategies.your_strategy import YourStrategy

__all__ = [
    "ConsensusStrategy",
    "ConsensusStrategyFactory",
    "SimpleMajorityVoteStrategy",
    "YourStrategy",
]
```

Update `src/main.py`:

```python
from src.protocols.consensus_strategies import ConsensusStrategyFactory, YourStrategy

# In the startup_event function:
consensus_factory = ConsensusStrategyFactory()
consensus_factory.register("simple_majority_vote", SimpleMajorityVoteStrategy)
consensus_factory.register("your_strategy", YourStrategy)
```

## Debugging

### Enabling Debug Logging

Update the `log_level` in `config.yaml`:

```yaml
logging:
  level: "DEBUG"
```

### Using the Debugger

If you're using VS Code, you can use the built-in debugger:

1. Create a `.vscode/launch.json` file:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: FastAPI",
         "type": "python",
         "request": "launch",
         "module": "src.main",
         "console": "integratedTerminal"
       },
       {
         "name": "Python: CLI",
         "type": "python",
         "request": "launch",
         "module": "src.cli.main",
         "args": ["--help"],
         "console": "integratedTerminal"
       }
     ]
   }
   ```

2. Set breakpoints in your code
3. Start the debugger using the "Run and Debug" panel

## Common Issues and Solutions

### ImportError: No module named 'src'

Make sure you've installed the project in development mode:

```bash
pip install -e .
```

### LLM Connection Issues

Ensure Ollama is running:

```bash
ollama serve
```

Check the Ollama logs for errors:

```bash
tail -f ~/.ollama/logs/ollama.log
```

### Database Connection Issues

Ensure the data directory exists:

```bash
mkdir -p data/chroma_db
```

### CLI Command Not Found

If the `daip-cli` command is not found, ensure you've installed the project correctly:

```bash
pip install -e .
```

## Contributing

### Code Style

The project follows these coding standards:

- PEP 8 for Python code style
- Black for code formatting
- isort for import sorting
- Ruff for linting

### Documentation

- Use docstrings for all public functions, classes, and methods
- Follow the Google docstring style
- Update the documentation when making significant changes

### Testing

- Write unit tests for all new functionality
- Maintain or improve test coverage
- Use pytest fixtures for test setup

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Ollama Documentation](https://ollama.ai/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## Support

If you encounter any issues or have questions, please:

1. Check the documentation
2. Search for existing issues on GitHub
3. Create a new issue if needed

## License

This project is licensed under the [MIT License](LICENSE).