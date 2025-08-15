"""@Time    : 2025-07-24 19:00:00
@Author  : DAIP-LIVE Team
@File    : interactive_controller.py
@Description:
    Interactive controller for user intervention and workflow customization.
"""
import json
import logging
import time
from collections.abc import Callable
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.syntax import Syntax
from rich.table import Table

from .configuration_manager import ConfigurationManager
from .parameter_manager import ParameterDefinition, ParameterManager
from .workflow_steering import SteeringAction, WorkflowSteering

logger = logging.getLogger(__name__)


class InteractiveController:
    """Controller for interactive user intervention and workflow customization."""
    
    def __init__(self, console: Console = None, config_dir: str = ".kiro/config"):
        """Initialize the interactive controller."""
        self.console = console or Console()
        self.intervention_callbacks: dict[str, list[Callable]] = {}
        self.customization_options: dict[str, dict[str, Any]] = {}
        
        # Initialize component managers
        self.parameter_manager = ParameterManager(console=self.console)
        self.workflow_steering = WorkflowSteering(console=self.console)
        self.configuration_manager = ConfigurationManager(config_dir=config_dir, console=self.console)
    
    def register_intervention_point(
        self,
        point_id: str,
        callback: Callable,
        description: str = "",
        auto_continue: bool = False
    ) -> None:
        """Register an intervention point in the workflow."""
        if point_id not in self.intervention_callbacks:
            self.intervention_callbacks[point_id] = []
        
        self.intervention_callbacks[point_id].append({
            "callback": callback,
            "description": description,
            "auto_continue": auto_continue
        })
    
    async def trigger_intervention(
        self,
        point_id: str,
        context: dict[str, Any],
        options: list[str] = None
    ) -> dict[str, Any]:
        """Trigger user intervention at a specific point."""
        if point_id not in self.intervention_callbacks:
            return {"action": "continue", "data": {}}
        
        self.console.print(f"\n[yellow]⚠️  Intervention Point: {point_id}[/yellow]")
        
        # Show context information
        if context:
            self._display_context(context)
        
        # Show available options
        default_options = ["continue", "modify", "pause", "cancel"]
        available_options = options or default_options
        
        self.console.print("\n[blue]Available actions:[/blue]")
        for i, option in enumerate(available_options, 1):
            self.console.print(f"  {i}. {option.title()}")
        
        # Get user choice
        choice = Prompt.ask(
            "What would you like to do?",
            choices=[str(i) for i in range(1, len(available_options) + 1)],
            default="1"
        )
        
        selected_action = available_options[int(choice) - 1]
        
        # Handle the selected action
        if selected_action == "continue":
            return {"action": "continue", "data": {}}
        elif selected_action == "modify":
            return await self._handle_modification(context)
        elif selected_action == "pause":
            return await self._handle_pause()
        elif selected_action == "cancel":
            return {"action": "cancel", "data": {}}
        else:
            # Custom action - call registered callbacks
            for callback_info in self.intervention_callbacks[point_id]:
                if callback_info["description"] == selected_action:
                    result = await callback_info["callback"](context)
                    return result
            
            return {"action": "continue", "data": {}}
    
    async def customize_workflow_config(
        self,
        workflow_name: str,
        current_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Allow user to customize workflow configuration interactively."""
        self.console.print(f"\n[blue]🔧 Customizing {workflow_name} Configuration[/blue]")
        
        # Display current configuration
        self._display_config(current_config)
        
        if not Confirm.ask("Would you like to modify the configuration?"):
            return current_config
        
        # Create a copy for modification
        new_config = current_config.copy()
        
        # Interactive configuration modification
        while True:
            self.console.print("\n[blue]Configuration sections:[/blue]")
            sections = list(new_config.keys())
            
            for i, section in enumerate(sections, 1):
                self.console.print(f"  {i}. {section}")
            
            self.console.print(f"  {len(sections) + 1}. Done")
            
            choice = Prompt.ask(
                "Select a section to modify",
                choices=[str(i) for i in range(1, len(sections) + 2)],
                default=str(len(sections) + 1)
            )
            
            if int(choice) == len(sections) + 1:
                break
            
            section_name = sections[int(choice) - 1]
            new_config[section_name] = await self._modify_config_section(
                section_name,
                new_config[section_name]
            )
        
        return new_config
    
    async def get_user_parameters(
        self,
        parameter_definitions: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """Get parameters from user based on definitions."""
        self.console.print("\n[blue]📝 Parameter Configuration[/blue]")
        
        parameters = {}
        
        for param_name, param_def in parameter_definitions.items():
            param_type = param_def.get("type", "string")
            description = param_def.get("description", "")
            default = param_def.get("default")
            choices = param_def.get("choices")
            
            self.console.print(f"\n[cyan]{param_name}[/cyan]: {description}")
            
            if param_type == "string":
                if choices:
                    value = Prompt.ask(
                        f"Select {param_name}",
                        choices=choices,
                        default=str(default) if default else None
                    )
                else:
                    value = Prompt.ask(
                        f"Enter {param_name}",
                        default=str(default) if default else None
                    )
            elif param_type == "integer":
                value = IntPrompt.ask(
                    f"Enter {param_name}",
                    default=default if default is not None else None
                )
            elif param_type == "float":
                value = FloatPrompt.ask(
                    f"Enter {param_name}",
                    default=default if default is not None else None
                )
            elif param_type == "boolean":
                value = Confirm.ask(
                    f"Enable {param_name}?",
                    default=default if default is not None else True
                )
            elif param_type == "list":
                value_str = Prompt.ask(
                    f"Enter {param_name} (comma-separated)",
                    default=",".join(default) if default else ""
                )
                value = [item.strip() for item in value_str.split(",") if item.strip()]
            else:
                value = Prompt.ask(
                    f"Enter {param_name}",
                    default=str(default) if default else None
                )
            
            parameters[param_name] = value
        
        return parameters
    
    def create_workflow_steering_menu(
        self,
        workflow_state: dict[str, Any],
        available_actions: list[str]
    ) -> str:
        """Create an interactive menu for workflow steering."""
        self.console.print("\n[yellow]🎛️  Workflow Steering[/yellow]")
        
        # Display current workflow state
        self._display_workflow_state(workflow_state)
        
        # Show available actions
        self.console.print("\n[blue]Available steering actions:[/blue]")
        for i, action in enumerate(available_actions, 1):
            self.console.print(f"  {i}. {action}")
        
        choice = Prompt.ask(
            "Select an action",
            choices=[str(i) for i in range(1, len(available_actions) + 1)],
            default="1"
        )
        
        return available_actions[int(choice) - 1]
    
    async def configure_quality_thresholds(
        self,
        current_thresholds: dict[str, float]
    ) -> dict[str, float]:
        """Interactive configuration of quality thresholds."""
        self.console.print("\n[blue]🎯 Quality Threshold Configuration[/blue]")
        
        # Display current thresholds
        table = Table(title="Current Quality Thresholds")
        table.add_column("Metric", style="cyan")
        table.add_column("Threshold", style="magenta")
        
        for metric, threshold in current_thresholds.items():
            table.add_row(metric, f"{threshold:.2f}")
        
        self.console.print(table)
        
        if not Confirm.ask("Would you like to modify these thresholds?"):
            return current_thresholds
        
        new_thresholds = current_thresholds.copy()
        
        for metric, current_value in current_thresholds.items():
            new_value = FloatPrompt.ask(
                f"Enter threshold for {metric} (0.0-1.0)",
                default=current_value
            )
            
            # Validate range
            new_value = max(0.0, min(1.0, new_value))
            new_thresholds[metric] = new_value
        
        return new_thresholds
    
    def display_workflow_options(
        self,
        workflow_name: str,
        options: dict[str, Any]
    ) -> None:
        """Display available workflow options."""
        self.console.print(f"\n[blue]⚙️  {workflow_name} Options[/blue]")
        
        for category, settings in options.items():
            self.console.print(f"\n[cyan]{category.title()}:[/cyan]")
            
            if isinstance(settings, dict):
                for key, value in settings.items():
                    self.console.print(f"  • {key}: {value}")
            else:
                self.console.print(f"  • {settings}")
    
    async def _handle_modification(self, context: dict[str, Any]) -> dict[str, Any]:
        """Handle modification request from user."""
        self.console.print("\n[blue]🔧 Modification Options[/blue]")
        
        # Show modifiable elements
        modifiable_keys = [key for key in context.keys() if not key.startswith("_")]
        
        if not modifiable_keys:
            self.console.print("[yellow]No modifiable elements available[/yellow]")
            return {"action": "continue", "data": {}}
        
        self.console.print("Modifiable elements:")
        for i, key in enumerate(modifiable_keys, 1):
            self.console.print(f"  {i}. {key}: {context[key]}")
        
        choice = Prompt.ask(
            "Select element to modify",
            choices=[str(i) for i in range(1, len(modifiable_keys) + 1)]
        )
        
        selected_key = modifiable_keys[int(choice) - 1]
        current_value = context[selected_key]
        
        # Get new value based on type
        if isinstance(current_value, bool):
            new_value = Confirm.ask(f"New value for {selected_key}", default=current_value)
        elif isinstance(current_value, int):
            new_value = IntPrompt.ask(f"New value for {selected_key}", default=current_value)
        elif isinstance(current_value, float):
            new_value = FloatPrompt.ask(f"New value for {selected_key}", default=current_value)
        elif isinstance(current_value, list):
            value_str = Prompt.ask(
                f"New value for {selected_key} (comma-separated)",
                default=",".join(str(v) for v in current_value)
            )
            new_value = [item.strip() for item in value_str.split(",")]
        else:
            new_value = Prompt.ask(f"New value for {selected_key}", default=str(current_value))
        
        return {
            "action": "modify",
            "data": {
                "key": selected_key,
                "old_value": current_value,
                "new_value": new_value
            }
        }
    
    async def _handle_pause(self) -> dict[str, Any]:
        """Handle pause request from user."""
        self.console.print("\n[yellow]⏸️  Workflow Paused[/yellow]")
        
        options = [
            "Resume workflow",
            "Save current state",
            "Load different configuration",
            "Cancel workflow"
        ]
        
        self.console.print("Pause options:")
        for i, option in enumerate(options, 1):
            self.console.print(f"  {i}. {option}")
        
        choice = Prompt.ask(
            "What would you like to do?",
            choices=[str(i) for i in range(1, len(options) + 1)],
            default="1"
        )
        
        selected_option = options[int(choice) - 1]
        
        if selected_option == "Resume workflow":
            return {"action": "continue", "data": {}}
        elif selected_option == "Save current state":
            filename = Prompt.ask("Enter filename to save state", default="workflow_state.json")
            return {"action": "save_state", "data": {"filename": filename}}
        elif selected_option == "Load different configuration":
            filename = Prompt.ask("Enter configuration filename", default="config.json")
            return {"action": "load_config", "data": {"filename": filename}}
        else:
            return {"action": "cancel", "data": {}}
    
    async def _modify_config_section(
        self,
        section_name: str,
        section_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Modify a specific configuration section."""
        self.console.print(f"\n[cyan]Modifying {section_name}:[/cyan]")
        
        new_section = section_config.copy()
        
        while True:
            # Display current section configuration
            table = Table(title=f"{section_name} Configuration")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in new_section.items():
                table.add_row(key, str(value))
            
            self.console.print(table)
            
            # Ask what to modify
            keys = list(new_section.keys())
            keys.append("Done")
            
            self.console.print("\nSelect parameter to modify:")
            for i, key in enumerate(keys, 1):
                self.console.print(f"  {i}. {key}")
            
            choice = Prompt.ask(
                "Select parameter",
                choices=[str(i) for i in range(1, len(keys) + 1)],
                default=str(len(keys))
            )
            
            if int(choice) == len(keys):
                break
            
            selected_key = keys[int(choice) - 1]
            current_value = new_section[selected_key]
            
            # Get new value
            if isinstance(current_value, bool):
                new_value = Confirm.ask(f"New value for {selected_key}", default=current_value)
            elif isinstance(current_value, int):
                new_value = IntPrompt.ask(f"New value for {selected_key}", default=current_value)
            elif isinstance(current_value, float):
                new_value = FloatPrompt.ask(f"New value for {selected_key}", default=current_value)
            elif isinstance(current_value, list):
                value_str = Prompt.ask(
                    f"New value for {selected_key} (comma-separated)",
                    default=",".join(str(v) for v in current_value)
                )
                new_value = [item.strip() for item in value_str.split(",")]
            else:
                new_value = Prompt.ask(f"New value for {selected_key}", default=str(current_value))
            
            new_section[selected_key] = new_value
        
        return new_section
    
    async def collect_workflow_parameters(
        self,
        workflow_name: str,
        parameter_definitions: list[ParameterDefinition],
        context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Collect workflow parameters using the parameter manager."""
        self.console.print(f"\n[blue]📝 Collecting Parameters for {workflow_name}[/blue]")
        
        return await self.parameter_manager.collect_parameters(
            parameter_definitions=parameter_definitions,
            context=context or {"workflow": workflow_name},
            allow_skip=True
        )
    
    async def setup_workflow_steering(
        self,
        workflow_name: str,
        steering_points: list[dict[str, Any]]
    ) -> None:
        """Setup workflow steering points."""
        self.console.print(f"\n[blue]🎛️  Setting up Steering for {workflow_name}[/blue]")
        
        for point_config in steering_points:
            self.workflow_steering.register_steering_point(
                point_id=point_config["id"],
                name=point_config["name"],
                description=point_config["description"],
                workflow_step=point_config["workflow_step"],
                available_actions=[SteeringAction(action) for action in point_config.get("actions", ["continue"])],
                auto_continue_timeout=point_config.get("auto_continue_timeout"),
                priority=point_config.get("priority", 1)
            )
    
    async def trigger_workflow_steering(
        self,
        point_id: str,
        context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Trigger workflow steering at a specific point."""
        command = await self.workflow_steering.trigger_steering_point(
            point_id=point_id,
            context=context
        )
        
        return {
            "action": command.action.value,
            "parameters": command.parameters,
            "target_step": command.target_step,
            "message": command.message,
            "timestamp": command.timestamp
        }
    
    async def create_workflow_configuration(
        self,
        workflow_name: str,
        config_name: str = "custom"
    ) -> dict[str, Any]:
        """Create a workflow configuration interactively."""
        return await self.configuration_manager.create_configuration(
            workflow_name=workflow_name,
            config_name=config_name
        )
    
    def load_workflow_configuration(
        self,
        config_name: str
    ) -> dict[str, Any]:
        """Load a workflow configuration."""
        return self.configuration_manager.load_configuration(config_name)
    
    def save_workflow_configuration(
        self,
        config_name: str,
        config: dict[str, Any]
    ) -> bool:
        """Save a workflow configuration."""
        return self.configuration_manager._save_configuration(config_name, config)
    
    def list_workflow_configurations(
        self,
        workflow_name: str = None
    ) -> list[str]:
        """List available workflow configurations."""
        return self.configuration_manager.list_configurations(workflow_name)
    
    async def adjust_workflow_parameters(
        self,
        current_parameters: dict[str, Any],
        parameter_definitions: list[ParameterDefinition]
    ) -> dict[str, Any]:
        """Allow interactive adjustment of workflow parameters."""
        return await self.parameter_manager.interactive_parameter_adjustment(
            current_parameters=current_parameters,
            parameter_definitions=parameter_definitions
        )
    
    def create_parameter_preset(
        self,
        preset_name: str,
        parameters: dict[str, Any],
        description: str = ""
    ) -> bool:
        """Create a parameter preset for reuse."""
        return self.parameter_manager.create_parameter_preset(
            preset_name=preset_name,
            parameters=parameters,
            description=description
        )
    
    def load_parameter_preset(self, preset_name: str) -> dict[str, Any]:
        """Load a parameter preset."""
        return self.parameter_manager.load_parameter_preset(preset_name)
    
    def get_steering_history(self) -> list[dict[str, Any]]:
        """Get the history of steering commands."""
        commands = self.workflow_steering.get_steering_history()
        return [
            {
                "action": cmd.action.value,
                "parameters": cmd.parameters,
                "target_step": cmd.target_step,
                "message": cmd.message,
                "timestamp": cmd.timestamp
            }
            for cmd in commands
        ]
    
    def display_intervention_summary(
        self,
        interventions: list[dict[str, Any]]
    ) -> None:
        """Display a summary of user interventions."""
        if not interventions:
            self.console.print("[dim]No interventions recorded[/dim]")
            return
        
        self.console.print("\n[blue]📊 Intervention Summary[/blue]")
        
        table = Table(title="User Interventions")
        table.add_column("Timestamp", style="dim")
        table.add_column("Action", style="cyan")
        table.add_column("Target Step", style="magenta")
        table.add_column("Message", style="green")
        
        for intervention in interventions[-10:]:  # Show last 10
            timestamp = time.strftime("%H:%M:%S", time.localtime(intervention.get("timestamp", 0)))
            action = intervention.get("action", "unknown")
            target_step = intervention.get("target_step", "N/A")
            message = intervention.get("message", "")
            
            if len(message) > 50:
                message = message[:47] + "..."
            
            table.add_row(timestamp, action, target_step, message)
        
        self.console.print(table)
    
    async def handle_workflow_customization_menu(
        self,
        workflow_name: str,
        current_config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Display and handle workflow customization menu."""
        self.console.print(f"\n[blue]🔧 Workflow Customization: {workflow_name}[/blue]")
        
        options = [
            "Create new configuration",
            "Load existing configuration",
            "Modify current configuration",
            "Save current configuration",
            "Export configuration",
            "Import configuration",
            "View configuration summary",
            "Done"
        ]
        
        while True:
            self.console.print("\nCustomization options:")
            for i, option in enumerate(options, 1):
                self.console.print(f"  {i}. {option}")
            
            choice = Prompt.ask(
                "Select an option",
                choices=[str(i) for i in range(1, len(options) + 1)],
                default=str(len(options))
            )
            
            choice_num = int(choice)
            
            if choice_num == 1:  # Create new configuration
                config_name = Prompt.ask("Enter configuration name", default="custom")
                current_config = await self.create_workflow_configuration(workflow_name, config_name)
            
            elif choice_num == 2:  # Load existing configuration
                configs = self.list_workflow_configurations(workflow_name)
                if configs:
                    self.console.print("Available configurations:")
                    for i, config in enumerate(configs, 1):
                        self.console.print(f"  {i}. {config}")
                    
                    config_choice = Prompt.ask(
                        "Select configuration",
                        choices=[str(i) for i in range(1, len(configs) + 1)]
                    )
                    selected_config = configs[int(config_choice) - 1]
                    current_config = self.load_workflow_configuration(selected_config)
                else:
                    self.console.print("[yellow]No configurations available[/yellow]")
            
            elif choice_num == 3:  # Modify current configuration
                if current_config:
                    current_config = await self.customize_workflow_config(workflow_name, current_config)
                else:
                    self.console.print("[yellow]No current configuration to modify[/yellow]")
            
            elif choice_num == 4:  # Save current configuration
                if current_config:
                    config_name = Prompt.ask("Enter configuration name", default="custom")
                    self.save_workflow_configuration(f"{workflow_name}_{config_name}", current_config)
                else:
                    self.console.print("[yellow]No current configuration to save[/yellow]")
            
            elif choice_num == 5:  # Export configuration
                if current_config:
                    export_path = Prompt.ask("Enter export path", default=f"{workflow_name}_config.json")
                    config_name = f"{workflow_name}_temp"
                    self.configuration_manager.configurations[config_name] = current_config
                    self.configuration_manager.export_configuration(config_name, export_path)
                else:
                    self.console.print("[yellow]No current configuration to export[/yellow]")
            
            elif choice_num == 6:  # Import configuration
                import_path = Prompt.ask("Enter import path")
                config_name = Prompt.ask("Enter configuration name", default="imported")
                if self.configuration_manager.import_configuration(import_path, f"{workflow_name}_{config_name}"):
                    current_config = self.load_workflow_configuration(f"{workflow_name}_{config_name}")
            
            elif choice_num == 7:  # View configuration summary
                if current_config:
                    self.configuration_manager._display_configuration_summary(current_config)
                else:
                    self.console.print("[yellow]No current configuration to display[/yellow]")
            
            elif choice_num == 8:  # Done
                break
        
        return current_config or {}
    
    def _display_context(self, context: dict[str, Any]) -> None:
        """Display context information."""
        self.console.print("\n[blue]Current Context:[/blue]")
        
        for key, value in context.items():
            if not key.startswith("_"):  # Skip private keys
                if isinstance(value, (dict, list)):
                    # For complex objects, show a summary
                    if isinstance(value, dict):
                        summary = f"Dict with {len(value)} keys"
                    else:
                        summary = f"List with {len(value)} items"
                    self.console.print(f"  • {key}: {summary}")
                else:
                    # Show simple values directly
                    display_value = str(value)
                    if len(display_value) > 100:
                        display_value = display_value[:97] + "..."
                    self.console.print(f"  • {key}: {display_value}")
    
    def _display_config(self, config: dict[str, Any]) -> None:
        """Display configuration in a readable format."""
        syntax = Syntax(
            json.dumps(config, indent=2, ensure_ascii=False),
            "json",
            theme="monokai",
            line_numbers=True
        )
        self.console.print(Panel(syntax, title="Current Configuration"))
    
    def _display_workflow_state(self, state: dict[str, Any]) -> None:
        """Display current workflow state."""
        self.console.print("\n[blue]Current Workflow State:[/blue]")
        
        # Show key state information
        important_keys = ["current_step", "progress", "status", "execution_id"]
        
        for key in important_keys:
            if key in state:
                self.console.print(f"  • {key}: {state[key]}")
        
        # Show other state information
        other_keys = [k for k in state.keys() if k not in important_keys and not k.startswith("_")]
        if other_keys:
            self.console.print("\n[dim]Other state information:[/dim]")
            for key in other_keys[:5]:  # Limit to first 5 items
                value = state[key]
                if isinstance(value, (dict, list)):
                    summary = f"({type(value).__name__} with {len(value)} items)"
                else:
                    summary = str(value)[:50] + ("..." if len(str(value)) > 50 else "")
                self.console.print(f"  • {key}: {summary}")