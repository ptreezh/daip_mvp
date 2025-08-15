"""@Time    : 2025-07-24 19:30:00
@Author  : DAIP-LIVE Team
@File    : configuration_manager.py
@Description:
    Configuration management for workflow customization and user preferences.
"""
import copy
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

logger = logging.getLogger(__name__)


@dataclass
class ConfigurationOption:
    """Represents a configuration option."""
    key: str
    name: str
    description: str
    option_type: str  # "string", "integer", "float", "boolean", "list", "choice"
    default_value: Any
    choices: Optional[list[str]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    category: str = "general"
    advanced: bool = False
    requires_restart: bool = False


class ConfigurationManager:
    """Manages workflow configuration options and user preferences."""
    
    def __init__(self, config_dir: str = ".kiro/config", console: Console = None):
        """Initialize the configuration manager."""
        self.console = console or Console()
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.configurations: dict[str, dict[str, Any]] = {}
        self.configuration_options: dict[str, list[ConfigurationOption]] = {}
        self.user_preferences: dict[str, Any] = {}
        
        # Load existing configurations
        self._load_configurations()
        self._initialize_default_options()
    
    def _load_configurations(self) -> None:
        """Load existing configurations from disk."""
        try:
            # Load workflow configurations
            config_files = self.config_dir.glob("*.json")
            for config_file in config_files:
                try:
                    with open(config_file, encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    config_name = config_file.stem
                    self.configurations[config_name] = config_data
                    
                except Exception as e:
                    logger.error(f"Error loading configuration {config_file}: {e}")
            
            # Load user preferences
            prefs_file = self.config_dir / "user_preferences.json"
            if prefs_file.exists():
                with open(prefs_file, encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
        
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
    
    def _initialize_default_options(self) -> None:
        """Initialize default configuration options for workflows."""
        # Critical Review Workflow Options
        self.configuration_options["critical_review"] = [
            ConfigurationOption(
                key="generation.role_name",
                name="Generator Role Name",
                description="Name of the role responsible for content generation",
                option_type="string",
                default_value="创作者",
                category="generation"
            ),
            ConfigurationOption(
                key="generation.capture_metadata",
                name="Capture Generation Metadata",
                description="Whether to capture detailed metadata during generation",
                option_type="boolean",
                default_value=True,
                category="generation"
            ),
            ConfigurationOption(
                key="fact_extraction.min_confidence",
                name="Minimum Fact Confidence",
                description="Minimum confidence threshold for fact extraction",
                option_type="float",
                default_value=0.6,
                min_value=0.0,
                max_value=1.0,
                category="fact_extraction"
            ),
            ConfigurationOption(
                key="fact_extraction.max_facts",
                name="Maximum Facts",
                description="Maximum number of facts to extract per content",
                option_type="integer",
                default_value=20,
                min_value=1,
                max_value=100,
                category="fact_extraction"
            ),
            ConfigurationOption(
                key="parallel_review.reviewer_roles",
                name="Reviewer Roles",
                description="List of roles for parallel review",
                option_type="list",
                default_value=["批判者", "验证者"],
                category="parallel_review"
            ),
            ConfigurationOption(
                key="parallel_review.max_parallel_reviews",
                name="Maximum Parallel Reviews",
                description="Maximum number of parallel reviews to conduct",
                option_type="integer",
                default_value=5,
                min_value=1,
                max_value=10,
                category="parallel_review"
            ),
            ConfigurationOption(
                key="consensus.method",
                name="Consensus Method",
                description="Method for calculating consensus",
                option_type="choice",
                default_value="weighted_average",
                choices=["weighted_average", "majority_vote", "synthesis"],
                category="consensus"
            ),
            ConfigurationOption(
                key="consensus.credibility_threshold",
                name="Credibility Threshold",
                description="Threshold for content credibility",
                option_type="float",
                default_value=0.7,
                min_value=0.0,
                max_value=1.0,
                category="consensus"
            ),
            ConfigurationOption(
                key="revision.max_attempts",
                name="Maximum Revision Attempts",
                description="Maximum number of revision attempts",
                option_type="integer",
                default_value=3,
                min_value=1,
                max_value=10,
                category="revision"
            )
        ]
        
        # Multi-Perspective Synthesis Workflow Options
        self.configuration_options["multi_perspective"] = [
            ConfigurationOption(
                key="task_decomposition.planner_role",
                name="Planner Role Name",
                description="Name of the role responsible for task decomposition",
                option_type="string",
                default_value="规划者",
                category="task_decomposition"
            ),
            ConfigurationOption(
                key="task_decomposition.default_perspectives",
                name="Default Perspectives",
                description="Default perspectives to consider during analysis",
                option_type="list",
                default_value=["经济", "社会", "技术", "伦理"],
                category="task_decomposition"
            ),
            ConfigurationOption(
                key="task_decomposition.max_sub_problems",
                name="Maximum Sub-problems",
                description="Maximum number of sub-problems to create",
                option_type="integer",
                default_value=5,
                min_value=2,
                max_value=10,
                category="task_decomposition"
            ),
            ConfigurationOption(
                key="parallel_exploration.max_parallel_experts",
                name="Maximum Parallel Experts",
                description="Maximum number of experts to run in parallel",
                option_type="integer",
                default_value=5,
                min_value=2,
                max_value=10,
                category="parallel_exploration"
            ),
            ConfigurationOption(
                key="parallel_exploration.use_tools",
                name="Enable Tool Usage",
                description="Whether experts can use external tools",
                option_type="boolean",
                default_value=True,
                category="parallel_exploration"
            ),
            ConfigurationOption(
                key="synthesis.method",
                name="Synthesis Method",
                description="Method for synthesizing expert viewpoints",
                option_type="choice",
                default_value="dialectical",
                choices=["dialectical", "weighted", "hierarchical"],
                category="synthesis"
            ),
            ConfigurationOption(
                key="synthesis.quality_threshold",
                name="Synthesis Quality Threshold",
                description="Minimum quality threshold for synthesis",
                option_type="float",
                default_value=0.7,
                min_value=0.0,
                max_value=1.0,
                category="synthesis"
            ),
            ConfigurationOption(
                key="synthesis.include_attribution",
                name="Include Expert Attribution",
                description="Whether to include expert attribution in results",
                option_type="boolean",
                default_value=True,
                category="synthesis"
            ),
            ConfigurationOption(
                key="refinement.max_iterations",
                name="Maximum Refinement Iterations",
                description="Maximum number of refinement iterations",
                option_type="integer",
                default_value=3,
                min_value=1,
                max_value=5,
                category="refinement"
            )
        ]
        
        # User Interface Options
        self.configuration_options["user_interface"] = [
            ConfigurationOption(
                key="display.show_progress",
                name="Show Progress Indicators",
                description="Whether to show progress indicators during execution",
                option_type="boolean",
                default_value=True,
                category="display"
            ),
            ConfigurationOption(
                key="display.verbosity_level",
                name="Verbosity Level",
                description="Level of detail in output messages",
                option_type="choice",
                default_value="normal",
                choices=["minimal", "normal", "detailed", "debug"],
                category="display"
            ),
            ConfigurationOption(
                key="interaction.auto_continue_timeout",
                name="Auto-continue Timeout",
                description="Timeout in seconds for auto-continue prompts",
                option_type="float",
                default_value=30.0,
                min_value=5.0,
                max_value=300.0,
                category="interaction"
            ),
            ConfigurationOption(
                key="interaction.confirm_destructive_actions",
                name="Confirm Destructive Actions",
                description="Whether to confirm potentially destructive actions",
                option_type="boolean",
                default_value=True,
                category="interaction"
            ),
            ConfigurationOption(
                key="output.format",
                name="Default Output Format",
                description="Default format for workflow results",
                option_type="choice",
                default_value="rich",
                choices=["json", "markdown", "rich", "plain"],
                category="output"
            )
        ]
    
    async def create_configuration(
        self,
        workflow_name: str,
        config_name: str = "default",
        base_config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Create a new configuration interactively."""
        self.console.print(f"\n[blue]🎨 Creating Configuration for {workflow_name}[/blue]")
        
        if workflow_name not in self.configuration_options:
            self.console.print(f"[red]Unknown workflow: {workflow_name}[/red]")
            return {}
        
        options = self.configuration_options[workflow_name]
        config = base_config.copy() if base_config else {}
        
        # Initialize with defaults
        for option in options:
            if option.key not in config:
                self._set_nested_value(config, option.key, option.default_value)
        
        # Interactive configuration
        return await self._interactive_configuration(workflow_name, config, options)
    
    async def _interactive_configuration(
        self,
        workflow_name: str,
        config: dict[str, Any],
        options: list[ConfigurationOption]
    ) -> dict[str, Any]:
        """Handle interactive configuration creation."""
        # Group options by category
        categories = {}
        for option in options:
            if option.category not in categories:
                categories[option.category] = []
            categories[option.category].append(option)
        
        while True:
            self.console.print(f"\n[cyan]Configuration categories for {workflow_name}:[/cyan]")
            category_names = list(categories.keys())
            
            for i, category in enumerate(category_names, 1):
                option_count = len(categories[category])
                self.console.print(f"  {i}. {category.title()} ({option_count} options)")
            
            self.console.print(f"  {len(category_names) + 1}. Review and save")
            self.console.print(f"  {len(category_names) + 2}. Cancel")
            
            choice = Prompt.ask(
                "Select a category to configure",
                choices=[str(i) for i in range(1, len(category_names) + 3)],
                default=str(len(category_names) + 1)
            )
            
            choice_num = int(choice)
            
            if choice_num == len(category_names) + 1:
                # Review and save
                self._display_configuration_summary(config)
                if Confirm.ask("Save this configuration?"):
                    config_key = f"{workflow_name}_{config_name}"
                    self.configurations[config_key] = config
                    self._save_configuration(config_key, config)
                    return config
                else:
                    continue
            elif choice_num == len(category_names) + 2:
                # Cancel
                return {}
            else:
                # Configure category
                category_name = category_names[choice_num - 1]
                category_options = categories[category_name]
                config = await self._configure_category(category_name, category_options, config)
        
        return config
    
    async def _configure_category(
        self,
        category_name: str,
        options: list[ConfigurationOption],
        config: dict[str, Any]
    ) -> dict[str, Any]:
        """Configure options within a specific category."""
        self.console.print(f"\n[cyan]🔧 Configuring {category_name.title()}[/cyan]")
        
        while True:
            # Display current category configuration
            table = Table(title=f"{category_name.title()} Configuration")
            table.add_column("Option", style="cyan")
            table.add_column("Current Value", style="magenta")
            table.add_column("Description", style="dim")
            
            for option in options:
                current_value = self._get_nested_value(config, option.key, option.default_value)
                table.add_row(option.name, str(current_value), option.description)
            
            self.console.print(table)
            
            # Show options to modify
            option_names = [opt.name for opt in options]
            option_names.append("Done with this category")
            
            self.console.print("\nSelect option to modify:")
            for i, name in enumerate(option_names, 1):
                self.console.print(f"  {i}. {name}")
            
            choice = Prompt.ask(
                "Select option",
                choices=[str(i) for i in range(1, len(option_names) + 1)],
                default=str(len(option_names))
            )
            
            if int(choice) == len(option_names):
                break
            
            selected_option = options[int(choice) - 1]
            new_value = await self._get_option_value(selected_option, config)
            
            if new_value is not None:
                self._set_nested_value(config, selected_option.key, new_value)
        
        return config
    
    async def _get_option_value(
        self,
        option: ConfigurationOption,
        config: dict[str, Any]
    ) -> Any:
        """Get a configuration option value from user input."""
        current_value = self._get_nested_value(config, option.key, option.default_value)
        
        self.console.print(f"\n[yellow]Setting {option.name}[/yellow]")
        self.console.print(f"Description: {option.description}")
        self.console.print(f"Current value: {current_value}")
        
        if option.option_type == "string":
            return Prompt.ask(
                f"Enter value for {option.name}",
                default=str(current_value)
            )
        
        elif option.option_type == "integer":
            from rich.prompt import IntPrompt
            while True:
                value = IntPrompt.ask(
                    f"Enter integer value for {option.name}",
                    default=current_value
                )
                
                if option.min_value is not None and value < option.min_value:
                    self.console.print(f"[red]Value must be at least {option.min_value}[/red]")
                    continue
                if option.max_value is not None and value > option.max_value:
                    self.console.print(f"[red]Value must be at most {option.max_value}[/red]")
                    continue
                
                return value
        
        elif option.option_type == "float":
            from rich.prompt import FloatPrompt
            while True:
                value = FloatPrompt.ask(
                    f"Enter float value for {option.name}",
                    default=current_value
                )
                
                if option.min_value is not None and value < option.min_value:
                    self.console.print(f"[red]Value must be at least {option.min_value}[/red]")
                    continue
                if option.max_value is not None and value > option.max_value:
                    self.console.print(f"[red]Value must be at most {option.max_value}[/red]")
                    continue
                
                return value
        
        elif option.option_type == "boolean":
            return Confirm.ask(
                f"Enable {option.name}?",
                default=current_value
            )
        
        elif option.option_type == "choice":
            if not option.choices:
                return self._get_string_value(option, current_value)
            
            return Prompt.ask(
                f"Select value for {option.name}",
                choices=option.choices,
                default=str(current_value)
            )
        
        elif option.option_type == "list":
            current_str = ",".join(str(v) for v in current_value) if isinstance(current_value, list) else str(current_value)
            value_str = Prompt.ask(
                f"Enter comma-separated values for {option.name}",
                default=current_str
            )
            return [item.strip() for item in value_str.split(",") if item.strip()]
        
        else:
            return Prompt.ask(
                f"Enter value for {option.name}",
                default=str(current_value)
            )
    
    def _get_nested_value(self, config: dict[str, Any], key: str, default: Any = None) -> Any:
        """Get a nested configuration value using dot notation."""
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def _set_nested_value(self, config: dict[str, Any], key: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = key.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value
    
    def _display_configuration_summary(self, config: dict[str, Any]) -> None:
        """Display a summary of the configuration."""
        self.console.print("\n[blue]📋 Configuration Summary[/blue]")
        
        syntax = Syntax(
            json.dumps(config, indent=2, ensure_ascii=False),
            "json",
            theme="monokai",
            line_numbers=True
        )
        self.console.print(Panel(syntax, title="Configuration"))
    
    def _save_configuration(self, config_name: str, config: dict[str, Any]) -> bool:
        """Save configuration to disk."""
        try:
            config_file = self.config_dir / f"{config_name}.json"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ Configuration saved: {config_name}[/green]")
            return True
        
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save configuration: {e}[/red]")
            logger.error(f"Error saving configuration {config_name}: {e}")
            return False
    
    def load_configuration(self, config_name: str) -> dict[str, Any]:
        """Load a configuration by name."""
        if config_name in self.configurations:
            return copy.deepcopy(self.configurations[config_name])
        
        # Try to load from file
        config_file = self.config_dir / f"{config_name}.json"
        if config_file.exists():
            try:
                with open(config_file, encoding='utf-8') as f:
                    config = json.load(f)
                
                self.configurations[config_name] = config
                return copy.deepcopy(config)
            
            except Exception as e:
                logger.error(f"Error loading configuration {config_name}: {e}")
        
        return {}
    
    def list_configurations(self, workflow_name: str = None) -> list[str]:
        """List available configurations."""
        configs = list(self.configurations.keys())
        
        if workflow_name:
            configs = [name for name in configs if name.startswith(workflow_name)]
        
        return configs
    
    def delete_configuration(self, config_name: str) -> bool:
        """Delete a configuration."""
        # Remove from memory
        if config_name in self.configurations:
            del self.configurations[config_name]
        
        # Remove from disk
        config_file = self.config_dir / f"{config_name}.json"
        if config_file.exists():
            try:
                config_file.unlink()
                self.console.print(f"[green]✅ Configuration deleted: {config_name}[/green]")
                return True
            except Exception as e:
                self.console.print(f"[red]❌ Failed to delete configuration: {e}[/red]")
                return False
        
        return True
    
    def export_configuration(self, config_name: str, export_path: str) -> bool:
        """Export a configuration to a specific path."""
        if config_name not in self.configurations:
            self.console.print(f"[red]Configuration not found: {config_name}[/red]")
            return False
        
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.configurations[config_name], f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ Configuration exported to: {export_path}[/green]")
            return True
        
        except Exception as e:
            self.console.print(f"[red]❌ Failed to export configuration: {e}[/red]")
            return False
    
    def import_configuration(self, import_path: str, config_name: str = None) -> bool:
        """Import a configuration from a file."""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                self.console.print(f"[red]Import file not found: {import_path}[/red]")
                return False
            
            with open(import_file, encoding='utf-8') as f:
                config = json.load(f)
            
            if config_name is None:
                config_name = import_file.stem
            
            self.configurations[config_name] = config
            self._save_configuration(config_name, config)
            
            self.console.print(f"[green]✅ Configuration imported as: {config_name}[/green]")
            return True
        
        except Exception as e:
            self.console.print(f"[red]❌ Failed to import configuration: {e}[/red]")
            return False