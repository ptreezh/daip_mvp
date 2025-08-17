# DAIP-LIVE Configuration System

This document describes the unified configuration system for the DAIP-LIVE project.

## Overview

The DAIP-LIVE configuration system provides a centralized way to manage application settings. It uses Pydantic models for validation and provides sensible defaults for all settings.

## Configuration File

The configuration is loaded from a `config.yaml` file in the project root directory. If this file doesn't exist, default values are used.

Example configuration file:

```yaml
# LLM Provider Configuration
llm:
  provider: "ollama"
  ollama:
    generation_model: "llama3:instruct"
    embedding_model: "nomic-embed-text:latest"
    host: "http://localhost:11434"
    timeout: 30

# Vector Store Configuration
vector_store:
  chroma_db_path: "data/chroma_db"
  role_collection_name: "roles"

# Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Usage

To use the configuration in your code:

```python
from src.config import settings

# Access configuration values
log_level = settings.log_level
llm_provider = settings.llm.provider
```

## Configuration Models

The configuration is defined using Pydantic models, which provide validation and default values:

- `AppConfig`: Root configuration model
- `LLMConfig`: LLM provider configuration
- `VectorStoreConfig`: Vector store configuration
- `LoggingConfig`: Logging configuration
- `TokenManagementConfig`: Token management configuration
- `UserProfileConfig`: User profile configuration
- `SessionConfig`: Session management configuration

## Advanced Usage

### Reloading Configuration

To reload the configuration from disk:

```python
from src.config import reload_config

# Reload configuration
config = reload_config()
```

### Getting Current Configuration

To get the current configuration without reloading:

```python
from src.config import get_config

# Get current configuration
config = get_config()
```

## Best Practices

1. Always import the `settings` object from `src.config` rather than creating your own configuration loading logic
2. Use type hints when accessing configuration values to get IDE support
3. Don't modify the configuration values at runtime unless absolutely necessary
4. If you need to add new configuration options, update the Pydantic models in `src/config.py`