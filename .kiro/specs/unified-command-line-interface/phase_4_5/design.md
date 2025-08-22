# Phase 4 & 5: Advanced Role Management, Workflows, Wiki Export & Completion - Design

## Architecture Overview

This design document outlines the technical implementation strategy for Phase 4 & 5 of the DAIP-LIVE CLI system. The design follows a modular approach, leveraging existing backend services while extending CLI capabilities.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Services Layer │    │  Data Layer     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Commands      │◄──►│ • RoleManager   │◄──►│ • Role Files    │
│ • Validation    │    │ • WikiService   │    │ • Wiki Storage  │
│ • Error Handling│    │ • WorkflowEngine│    │ • Chat Data     │
│ • Output Format │    │ • ChatRoomMgr   │    │ • Workflow Defs │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Phase 4: Technical Design

### 4.1 Advanced Role Management

#### 4.1.1 CLI Command Structure

```python
# src/cli/commands/role_commands.py
from typing import List, Optional
import typer
from rich.console import Console
from rich.table import Table

console = Console()

# Role Management Commands
role_app = typer.Typer(help="Manage AI roles in the system")

@role_app.command("create")
def create_role(
    name: str = typer.Argument(..., help="Name of the new role"),
    description: str = typer.Option(..., "--description", help="Role description"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags")
):
    """Create a new AI role with specified attributes."""
    try:
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        # Create role using RoleManager
        role_manager = RoleManager()
        role = Role(
            name=name,
            description=description,
            tags=tag_list,
            created_at=datetime.now()
        )
        
        success = role_manager.save_role(role)
        if success:
            console.print(f"✅ Role '{name}' created successfully with ID: {role.id}")
        else:
            console.print(f"❌ Failed to create role '{name}'")
            
    except Exception as e:
        handle_cli_error(e)

@role_app.command("invite")
def invite_role(
    role_id: str = typer.Argument(..., help="ID of the role to invite"),
    debate_id: str = typer.Option(..., "--to-debate", help="ID of the debate")
):
    """Invite a role to participate in a debate."""
    try:
        # Validate role and debate existence
        role_manager = RoleManager()
        role = role_manager.get_role_by_id(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")
        
        # Add role to debate (implementation depends on debate system)
        success = add_role_to_debate(role_id, debate_id)
        if success:
            console.print(f"✅ Role '{role.name}' invited to debate '{debate_id}'")
        else:
            console.print(f"❌ Failed to invite role to debate")
            
    except Exception as e:
        handle_cli_error(e)

@role_app.command("manage")
def manage_role(
    role_id: str = typer.Argument(..., help="ID of the role to manage"),
    update_description: Optional[str] = typer.Option(None, "--update-description", help="New description")
):
    """Update role attributes."""
    try:
        role_manager = RoleManager()
        role = role_manager.get_role_by_id(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")
        
        # Update role attributes
        if update_description:
            role.description = update_description
            
        success = role_manager.save_role(role)
        if success:
            console.print(f"✅ Role '{role.name}' updated successfully")
        else:
            console.print(f"❌ Failed to update role")
            
    except Exception as e:
        handle_cli_error(e)
```

#### 4.1.2 Backend Integration

The role management commands will integrate with existing `RoleManager` service:

```python
# Integration points with existing services
from src.core_services.role_manager import RoleManager
from src.core_services.role_manager import Role
from datetime import datetime

def add_role_to_debate(role_id: str, debate_id: str) -> bool:
    """Add role to debate session."""
    # This will integrate with the debate system
    # Implementation depends on MultiRoleDialogueEngine
    pass
```

### 4.2 Workflow Management System

#### 4.2.1 CLI Command Structure

```python
# src/cli/commands/workflow_commands.py
from typing import Dict, Any
import json
import typer
from rich.console import Console
from rich.table import Table

console = Console()

workflow_app = typer.Typer(help="Manage workflows and institutional primitives")

@workflow_app.command("list")
def list_workflows():
    """List all available workflows."""
    try:
        registry = PrimitiveRegistry()
        workflows = registry.list_primitives()
        
        table = Table(title="Available Workflows")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Status", style="yellow")
        
        for workflow in workflows:
            table.add_row(
                workflow.id,
                workflow.name,
                workflow.description,
                workflow.status
            )
        
        console.print(table)
        
    except Exception as e:
        handle_cli_error(e)

@workflow_app.command("create")
def create_workflow(
    name: str = typer.Argument(..., help="Name of the workflow"),
    definition_file: str = typer.Option(..., "--definition", help="Path to workflow definition file")
):
    """Create a new workflow from definition file."""
    try:
        # Load and validate workflow definition
        with open(definition_file, 'r') as f:
            definition = json.load(f)
        
        # Validate workflow structure
        validate_workflow_definition(definition)
        
        # Register workflow
        registry = PrimitiveRegistry()
        workflow_id = registry.register_primitive(
            primitive_type="workflow",
            name=name,
            definition=definition
        )
        
        console.print(f"✅ Workflow '{name}' created with ID: {workflow_id}")
        
    except Exception as e:
        handle_cli_error(e)

@workflow_app.command("select")
def select_workflow(
    workflow_id: str = typer.Argument(..., help="ID of the workflow"),
    scenario_type: str = typer.Option(..., "--for-scenario", help="Scenario type")
):
    """Select a workflow for a specific scenario."""
    try:
        # Validate workflow and scenario
        registry = PrimitiveRegistry()
        workflow = registry.get_primitive(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        # Associate workflow with scenario
        success = associate_workflow_with_scenario(workflow_id, scenario_type)
        if success:
            console.print(f"✅ Workflow '{workflow.name}' selected for '{scenario_type}'")
        else:
            console.print(f"❌ Failed to select workflow")
            
    except Exception as e:
        handle_cli_error(e)

@workflow_app.command("execute")
def execute_workflow(
    workflow_id: str = typer.Argument(..., help="ID of the workflow to execute"),
    params_json: str = typer.Option(..., "--params", help="JSON parameters")
):
    """Execute a workflow with specified parameters."""
    try:
        # Parse parameters
        params = json.loads(params_json)
        
        # Execute workflow
        engine = WorkflowEngine(PrimitiveRegistry())
        execution_id = engine.execute_workflow(
            workflow_def=get_workflow_definition(workflow_id),
            params=params
        )
        
        console.print(f"🚀 Workflow execution started with ID: {execution_id}")
        
        # Monitor execution (async)
        monitor_workflow_execution(execution_id)
        
    except Exception as e:
        handle_cli_error(e)
```

#### 4.2.2 Backend Integration

```python
# src/cli/services/workflow_service.py
from typing import Dict, Any, List
from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.workflow_engine import WorkflowEngine
from src.scenario_engine.workflow_selector import WorkflowSelector

class WorkflowService:
    """Service for workflow operations."""
    
    def __init__(self):
        self.registry = PrimitiveRegistry()
        self.engine = WorkflowEngine(self.registry)
        self.selector = WorkflowSelector()
    
    def validate_workflow_definition(self, definition: Dict[str, Any]) -> bool:
        """Validate workflow definition structure."""
        required_fields = ['name', 'description', 'steps', 'primitives']
        return all(field in definition for field in required_fields)
    
    def associate_workflow_with_scenario(self, workflow_id: str, scenario_type: str) -> bool:
        """Associate workflow with scenario type."""
        return self.selector.select_workflow(workflow_id, scenario_type)
    
    def monitor_workflow_execution(self, execution_id: str) -> None:
        """Monitor workflow execution progress."""
        # Implementation for async monitoring
        pass
```

### 4.3 Wiki Integration

#### 4.3.1 CLI Command Structure

```python
# src/cli/commands/wiki_commands.py
from typing import Optional
import typer
from rich.console import Console

console = Console()

wiki_app = typer.Typer(help="Manage wiki knowledge base")

@wiki_app.command("export")
def export_wiki(
    title_or_id: str = typer.Argument(..., help="Wiki entry title or ID"),
    format_type: str = typer.Option("markdown", "--format", help="Export format")
):
    """Export wiki entry to specified format."""
    try:
        wiki_service = WikiService()
        entry = wiki_service.get_entry(title_or_id)
        
        if not entry:
            raise ValueError(f"Wiki entry '{title_or_id}' not found")
        
        # Export based on format
        if format_type.lower() == "markdown":
            content = export_to_markdown(entry)
        elif format_type.lower() == "pdf":
            content = export_to_pdf(entry)
        elif format_type.lower() == "html":
            content = export_to_html(entry)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Save to file
        filename = f"{entry.title}.{format_type}"
        with open(filename, 'w') as f:
            f.write(content)
        
        console.print(f"✅ Wiki entry exported to: {filename}")
        
    except Exception as e:
        handle_cli_error(e)

@wiki_app.command("import")
def import_wiki(
    file_path: str = typer.Argument(..., help="Path to wiki file to import"),
    title: Optional[str] = typer.Option(None, "--title", help="Custom title")
):
    """Import wiki entry from file."""
    try:
        wiki_service = WikiService()
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Determine title
        entry_title = title or Path(file_path).stem
        
        # Create wiki entry
        success = wiki_service.create_entry(
            entry_name=entry_title,
            content=content,
            metadata={"source": "cli_import"}
        )
        
        if success:
            console.print(f"✅ Wiki entry '{entry_title}' imported successfully")
        else:
            console.print(f"❌ Failed to import wiki entry")
            
    except Exception as e:
        handle_cli_error(e)
```

#### 4.3.2 Debate to Wiki Export

```python
# src/cli/commands/debate_commands.py (extended)
@debate_app.command("export-to-wiki")
def export_debate_to_wiki(
    debate_id: str = typer.Argument(..., help="ID of the debate to export"),
    wiki_title: str = typer.Option(..., "--title", help="Title for wiki entry")
):
    """Export debate results to wiki."""
    try:
        # Get debate results
        debate_engine = MultiRoleDialogueEngine()
        summary = debate_engine.get_dialogue_summary(debate_id)
        
        if not summary:
            raise ValueError(f"Debate '{debate_id}' not found or not completed")
        
        # Format debate content for wiki
        wiki_content = format_debate_for_wiki(summary)
        
        # Create wiki entry
        wiki_service = WikiService()
        success = wiki_service.create_entry(
            entry_name=wiki_title,
            content=wiki_content,
            metadata={
                "source": "debate_export",
                "debate_id": debate_id,
                "exported_at": datetime.now().isoformat()
            }
        )
        
        if success:
            console.print(f"✅ Debate exported to wiki as '{wiki_title}'")
        else:
            console.print(f"❌ Failed to export debate to wiki")
            
    except Exception as e:
        handle_cli_error(e)
```

### 4.4 Institutional Primitives

#### 4.4.1 Debate Rule Primitive

```python
# src/institutional_primitives/debate_rules.py
from typing import Dict, Any, List
from src.institutional_primitives.base import InstitutionalPrimitive

class DebateRulePrimitive(InstitutionalPrimitive):
    """Primitive for managing debate rules and procedures."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.speaking_time_limit = config.get('speaking_time_limit', 300)
        self.voting_mechanism = config.get('voting_mechanism', 'simple_majority')
        self.moderation_enabled = config.get('moderation_enabled', True)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute debate rule primitive."""
        # Implementation of debate rule logic
        return {
            "status": "completed",
            "rule_applied": self.config['name'],
            "context": context
        }
    
    def validate_config(self) -> bool:
        """Validate debate rule configuration."""
        required_fields = ['name', 'speaking_time_limit', 'voting_mechanism']
        return all(field in self.config for field in required_fields)

class ChatRulePrimitive(InstitutionalPrimitive):
    """Primitive for managing chat room rules."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.content_filter = config.get('content_filter', True)
        self.rate_limit = config.get('rate_limit', 10)
        self.moderation_level = config.get('moderation_level', 'medium')
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chat rule primitive."""
        # Implementation of chat rule logic
        return {
            "status": "completed",
            "rule_applied": self.config['name'],
            "context": context
        }
```

## Phase 5: Technical Design

### 5.1 Error Handling System

#### 5.1.1 Global Error Handler

```python
# src/cli/error_handling.py
from typing import Type, Dict, Any
import typer
from rich.console import Console

console = Console()

class CLIError(Exception):
    """Base class for CLI errors."""
    pass

class ValidationError(CLIError):
    """Validation error."""
    pass

class ServiceUnavailableError(CLIError):
    """Service unavailable error."""
    pass

class FileNotFoundError(CLIError):
    """File not found error."""
    pass

# Error mapping
ERROR_MAPPING: Dict[Type[Exception], str] = {
    ValidationError: "❌ Validation Error: {}",
    ServiceUnavailableError: "🔴 Service Unavailable: {}",
    FileNotFoundError: "📁 File Not Found: {}",
    ValueError: "⚠️ Invalid Input: {}",
    KeyError: "🔑 Missing Required Field: {}",
    json.JSONDecodeError: "📋 Invalid JSON Format: {}",
    FileNotFoundError: "📁 File Not Found: {}"
}

def handle_cli_error(error: Exception) -> None:
    """Handle CLI errors with user-friendly messages."""
    error_type = type(error)
    
    if error_type in ERROR_MAPPING:
        message = ERROR_MAPPING[error_type].format(str(error))
        console.print(message)
    else:
        console.print(f"❌ Unexpected Error: {str(error)}")
    
    # Log detailed error for debugging
    logging.error(f"CLI Error: {error_type.__name__}: {str(error)}")

def validate_parameter(param_name: str, param_value: Any, validation_rules: Dict[str, Any]) -> None:
    """Validate parameter against rules."""
    if 'required' in validation_rules and validation_rules['required'] and not param_value:
        raise ValidationError(f"Parameter '{param_name}' is required")
    
    if 'type' in validation_rules:
        expected_type = validation_rules['type']
        if not isinstance(param_value, expected_type):
            raise ValidationError(f"Parameter '{param_name}' must be of type {expected_type.__name__}")
    
    if 'min_length' in validation_rules and len(str(param_value)) < validation_rules['min_length']:
        raise ValidationError(f"Parameter '{param_name}' must be at least {validation_rules['min_length']} characters")
    
    if 'max_length' in validation_rules and len(str(param_value)) > validation_rules['max_length']:
        raise ValidationError(f"Parameter '{param_name}' must be at most {validation_rules['max_length']} characters")
```

#### 5.1.2 Input Validation Middleware

```python
# src/cli/validation.py
from typing import Any, Dict, Callable
import functools
import re

def validate_command(func: Callable) -> Callable:
    """Decorator for command validation."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Validate common parameters
            for param_name, param_value in kwargs.items():
                if param_value is not None:
                    validate_parameter_by_name(param_name, param_value)
            
            return func(*args, **kwargs)
        except ValidationError as e:
            handle_cli_error(e)
            raise typer.Exit(1)
    
    return wrapper

def validate_parameter_by_name(param_name: str, param_value: Any) -> None:
    """Validate parameter by name with predefined rules."""
    validation_rules = {
        'role_id': {
            'required': True,
            'type': str,
            'pattern': r'^[a-zA-Z0-9_-]+$',
            'min_length': 3,
            'max_length': 50
        },
        'debate_id': {
            'required': True,
            'type': str,
            'pattern': r'^[a-zA-Z0-9_-]+$',
            'min_length': 3,
            'max_length': 50
        },
        'workflow_id': {
            'required': True,
            'type': str,
            'pattern': r'^[a-zA-Z0-9_-]+$',
            'min_length': 3,
            'max_length': 50
        },
        'title': {
            'required': True,
            'type': str,
            'min_length': 1,
            'max_length': 200
        },
        'description': {
            'required': False,
            'type': str,
            'max_length': 1000
        }
    }
    
    if param_name in validation_rules:
        rules = validation_rules[param_name]
        validate_parameter(param_name, param_value, rules)
        
        # Pattern validation
        if 'pattern' in rules:
            if not re.match(rules['pattern'], str(param_value)):
                raise ValidationError(f"Parameter '{param_name}' contains invalid characters")
```

### 5.2 Help System

#### 5.2.1 Enhanced Help System

```python
# src/cli/help_system.py
from typing import Dict, List
import typer
from rich.console import Console
from rich.markdown import Markdown

console = Console()

class HelpSystem:
    """Enhanced help system for CLI commands."""
    
    def __init__(self):
        self.command_help = {
            'roles': {
                'description': 'Manage AI roles in the system',
                'commands': {
                    'create': {
                        'description': 'Create a new AI role',
                        'usage': 'daip-cli roles create <name> --description <desc> [--tags <tag1,tag2>]',
                        'examples': [
                            'daip-cli roles create "AI Ethicist" --description "Expert in AI ethics" --tags "ethics,ai"',
                            'daip-cli roles create "Data Scientist" --description "Expert in data analysis"'
                        ],
                        'parameters': {
                            'name': 'Name of the role (required)',
                            '--description': 'Description of the role (required)',
                            '--tags': 'Comma-separated tags for the role (optional)'
                        }
                    },
                    'invite': {
                        'description': 'Invite a role to participate in a debate',
                        'usage': 'daip-cli roles invite <role_id> --to-debate <debate_id>',
                        'examples': [
                            'daip-cli roles invite ethicist_001 --to-debate debate_001'
                        ],
                        'parameters': {
                            'role_id': 'ID of the role to invite (required)',
                            '--to-debate': 'ID of the debate (required)'
                        }
                    }
                }
            },
            'workflow': {
                'description': 'Manage workflows and institutional primitives',
                'commands': {
                    'list': {
                        'description': 'List all available workflows',
                        'usage': 'daip-cli workflow list',
                        'examples': ['daip-cli workflow list'],
                        'parameters': {}
                    },
                    'create': {
                        'description': 'Create a new workflow from definition file',
                        'usage': 'daip-cli workflow create <name> --definition <file_path>',
                        'examples': [
                            'daip-cli workflow create "Debate Rules" --definition debate_rules.json'
                        ],
                        'parameters': {
                            'name': 'Name of the workflow (required)',
                            '--definition': 'Path to workflow definition file (required)'
                        }
                    }
                }
            }
        }
    
    def show_command_help(self, command: str, subcommand: str = None) -> None:
        """Show help for a specific command."""
        if command not in self.command_help:
            console.print(f"❌ Unknown command: {command}")
            return
        
        cmd_info = self.command_help[command]
        
        if subcommand:
            if subcommand not in cmd_info['commands']:
                console.print(f"❌ Unknown subcommand: {subcommand}")
                return
            
            subcmd_info = cmd_info['commands'][subcommand]
            self._show_subcommand_help(command, subcommand, subcmd_info)
        else:
            self._show_command_help(command, cmd_info)
    
    def _show_command_help(self, command: str, cmd_info: Dict) -> None:
        """Show help for a command group."""
        console.print(f"\n# {command.upper()}\n")
        console.print(f"**Description:** {cmd_info['description']}\n")
        
        table = Table(title=f"Available {command} commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="green")
        
        for subcmd, subcmd_info in cmd_info['commands'].items():
            table.add_row(subcmd, subcmd_info['description'])
        
        console.print(table)
    
    def _show_subcommand_help(self, command: str, subcommand: str, subcmd_info: Dict) -> None:
        """Show help for a specific subcommand."""
        console.print(f"\n# {command.upper()} {subcommand.upper()}\n")
        console.print(f"**Description:** {subcmd_info['description']}\n")
        console.print(f"**Usage:** `{subcmd_info['usage']}`\n")
        
        if subcmd_info['examples']:
            console.print("**Examples:**")
            for example in subcmd_info['examples']:
                console.print(f"- `{example}`")
            console.print()
        
        if subcmd_info['parameters']:
            console.print("**Parameters:**")
            for param, desc in subcmd_info['parameters'].items():
                console.print(f"- `{param}`: {desc}")
            console.print()
```

### 5.3 Performance Optimization

#### 5.3.1 Caching Layer

```python
# src/cli/cache.py
from typing import Any, Dict, Optional
import json
import time
from pathlib import Path

class CLICache:
    """Simple caching layer for CLI operations."""
    
    def __init__(self, cache_dir: str = ".cli_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if time.time() - data['timestamp'] < self.cache_duration:
                    return data['value']
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value."""
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'value': value,
                'timestamp': time.time()
            }, f)
    
    def clear(self) -> None:
        """Clear all cached values."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
```

### 5.4 Code Quality Integration

#### 5.4.1 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

## Integration Strategy

### 5.5 Service Integration Points

The CLI will integrate with existing backend services through well-defined interfaces:

1. **RoleManager**: For all role-related operations
2. **WikiService**: For wiki import/export functionality
3. **WorkflowEngine**: For workflow execution
4. **ChatRoomManager**: For chat room operations
5. **MultiRoleDialogueEngine**: For debate operations

### 5.6 Error Handling Integration

All CLI commands will use the centralized error handling system to ensure consistent error reporting and user experience.

### 5.7 Configuration Management

The CLI will support configuration through:
- Command-line arguments
- Environment variables
- Configuration files (config.yaml)
- User preferences

## Testing Strategy

### 5.8 Unit Testing

```python
# tests/cli/test_role_commands.py
import pytest
from unittest.mock import Mock, patch
from src.cli.commands.role_commands import create_role
from src.core_services.role_manager import RoleManager

class TestRoleCommands:
    
    @patch('src.cli.commands.role_commands.RoleManager')
    def test_create_role_success(self, mock_role_manager):
        """Test successful role creation."""
        # Setup
        mock_manager = Mock()
        mock_role_manager.return_value = mock_manager
        mock_manager.save_role.return_value = True
        
        # Execute
        result = create_role("Test Role", "--description", "A test role")
        
        # Verify
        mock_manager.save_role.assert_called_once()
        assert "created successfully" in result
    
    @patch('src.cli.commands.role_commands.RoleManager')
    def test_create_role_failure(self, mock_role_manager):
        """Test role creation failure."""
        # Setup
        mock_manager = Mock()
        mock_role_manager.return_value = mock_manager
        mock_manager.save_role.return_value = False
        
        # Execute
        result = create_role("Test Role", "--description", "A test role")
        
        # Verify
        mock_manager.save_role.assert_called_once()
        assert "Failed to create" in result
```

### 5.9 Integration Testing

```python
# tests/cli/test_workflow_integration.py
import pytest
from src.cli.commands.workflow_commands import execute_workflow
from src.institutional_primitives.workflow_engine import WorkflowEngine

class TestWorkflowIntegration:
    
    def test_workflow_execution_integration(self):
        """Test end-to-end workflow execution."""
        # This test would require actual backend services
        # Consider using test containers or mocks
        pass
```

## Deployment Strategy

### 5.10 CLI Distribution

The CLI will be distributed through:
1. PyPI package installation
2. Docker container
3. Standalone executable (using PyInstaller)
4. Development installation from source

### 5.11 Configuration Management

Environment-specific configuration will be handled through:
- Development: config.dev.yaml
- Testing: config.test.yaml
- Production: config.prod.yaml

## Monitoring and Observability

### 5.12 CLI Usage Analytics

Basic usage analytics will be collected to improve the CLI:
- Command usage frequency
- Error rates
- Performance metrics
- User feedback

### 5.13 Logging

Structured logging will be implemented for:
- Debugging
- Audit trails
- Performance monitoring
- Error tracking

## Security Considerations

### 5.14 Input Validation

All user inputs will be validated to prevent:
- Command injection
- Path traversal attacks
- XSS attacks
- Data corruption

### 5.15 Access Control

Role-based access control will be implemented for:
- Administrative operations
- Sensitive data access
- System configuration changes

## Conclusion

This design provides a comprehensive technical blueprint for implementing Phase 4 & 5 of the DAIP-LIVE CLI system. The modular architecture, robust error handling, and comprehensive testing strategy will ensure a high-quality, maintainable, and user-friendly CLI experience.