# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 19:30:00
@Author  : DAIP-LIVE Team
@File    : parameter_manager.py
@Description:
    Parameter management for user intervention and workflow customization.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """Parameter types for validation and input handling."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    CHOICE = "choice"
    RANGE = "range"


@dataclass
class ParameterDefinition:
    """Definition of a parameter for user input."""
    name: str
    param_type: ParameterType
    description: str
    default: Any = None
    choices: Optional[List[str]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    required: bool = True
    validator: Optional[Callable[[Any], bool]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ParameterManager:
    """Manages parameter collection and validation for workflow customization."""
    
    def __init__(self, console: Console = None):
        """Initialize the parameter manager."""
        self.console = console or Console()
        self.parameter_history: Dict[str, Any] = {}
        self.validation_errors: List[str] = []
    
    async def collect_parameters(
        self,
        parameter_definitions: List[ParameterDefinition],
        context: Dict[str, Any] = None,
        allow_skip: bool = False
    ) -> Dict[str, Any]:
        """Collect parameters from user based on definitions."""
        self.console.print("\n[blue]📝 Parameter Configuration[/blue]")
        
        if context:
            self.console.print(f"[dim]Context: {context.get('description', 'Parameter collection')}[/dim]")
        
        parameters = {}
        
        for param_def in parameter_definitions:
            try:
                value = await self._collect_single_parameter(param_def, allow_skip)
                if value is not None:
                    parameters[param_def.name] = value
                    self.parameter_history[param_def.name] = value
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Parameter collection cancelled by user[/yellow]")
                return {}
            except Exception as e:
                logger.error(f"Error collecting parameter {param_def.name}: {e}")
                self.console.print(f"[red]Error collecting {param_def.name}: {e}[/red]")
                if param_def.required:
                    return {}
        
        # Validate collected parameters
        if not self._validate_parameters(parameters, parameter_definitions):
            self.console.print("[red]Parameter validation failed[/red]")
            return {}
        
        return parameters
    
    async def _collect_single_parameter(
        self,
        param_def: ParameterDefinition,
        allow_skip: bool = False
    ) -> Any:
        """Collect a single parameter from user input."""
        self.console.print(f"\n[cyan]{param_def.name}[/cyan]: {param_def.description}")
        
        # Show default value if available
        if param_def.default is not None:
            self.console.print(f"[dim]Default: {param_def.default}[/dim]")
        
        # Show choices if available
        if param_def.choices:
            self.console.print(f"[dim]Choices: {', '.join(param_def.choices)}[/dim]")
        
        # Show range if available
        if param_def.min_value is not None or param_def.max_value is not None:
            range_str = f"Range: {param_def.min_value or 'min'} - {param_def.max_value or 'max'}"
            self.console.print(f"[dim]{range_str}[/dim]")
        
        # Skip option
        if allow_skip and not param_def.required:
            if Confirm.ask(f"Skip {param_def.name}?", default=False):
                return None
        
        # Collect value based on parameter type
        if param_def.param_type == ParameterType.STRING:
            return self._collect_string_parameter(param_def)
        elif param_def.param_type == ParameterType.INTEGER:
            return self._collect_integer_parameter(param_def)
        elif param_def.param_type == ParameterType.FLOAT:
            return self._collect_float_parameter(param_def)
        elif param_def.param_type == ParameterType.BOOLEAN:
            return self._collect_boolean_parameter(param_def)
        elif param_def.param_type == ParameterType.LIST:
            return self._collect_list_parameter(param_def)
        elif param_def.param_type == ParameterType.CHOICE:
            return self._collect_choice_parameter(param_def)
        elif param_def.param_type == ParameterType.RANGE:
            return self._collect_range_parameter(param_def)
        else:
            return self._collect_string_parameter(param_def)
    
    def _collect_string_parameter(self, param_def: ParameterDefinition) -> str:
        """Collect a string parameter."""
        while True:
            value = Prompt.ask(
                f"Enter {param_def.name}",
                default=str(param_def.default) if param_def.default is not None else None
            )
            
            if self._validate_single_parameter(value, param_def):
                return value
            
            self.console.print("[red]Invalid input. Please try again.[/red]")
    
    def _collect_integer_parameter(self, param_def: ParameterDefinition) -> int:
        """Collect an integer parameter."""
        while True:
            try:
                value = IntPrompt.ask(
                    f"Enter {param_def.name}",
                    default=param_def.default if param_def.default is not None else None
                )
                
                if self._validate_single_parameter(value, param_def):
                    return value
                
                self.console.print("[red]Value out of range. Please try again.[/red]")
            except Exception:
                self.console.print("[red]Invalid integer. Please try again.[/red]")
    
    def _collect_float_parameter(self, param_def: ParameterDefinition) -> float:
        """Collect a float parameter."""
        while True:
            try:
                value = FloatPrompt.ask(
                    f"Enter {param_def.name}",
                    default=param_def.default if param_def.default is not None else None
                )
                
                if self._validate_single_parameter(value, param_def):
                    return value
                
                self.console.print("[red]Value out of range. Please try again.[/red]")
            except Exception:
                self.console.print("[red]Invalid number. Please try again.[/red]")
    
    def _collect_boolean_parameter(self, param_def: ParameterDefinition) -> bool:
        """Collect a boolean parameter."""
        return Confirm.ask(
            f"Enable {param_def.name}?",
            default=param_def.default if param_def.default is not None else True
        )
    
    def _collect_list_parameter(self, param_def: ParameterDefinition) -> List[str]:
        """Collect a list parameter."""
        while True:
            default_str = ""
            if param_def.default and isinstance(param_def.default, list):
                default_str = ",".join(str(item) for item in param_def.default)
            
            value_str = Prompt.ask(
                f"Enter {param_def.name} (comma-separated)",
                default=default_str if default_str else None
            )
            
            if not value_str.strip():
                if param_def.required:
                    self.console.print("[red]This parameter is required.[/red]")
                    continue
                return []
            
            value_list = [item.strip() for item in value_str.split(",") if item.strip()]
            
            if self._validate_single_parameter(value_list, param_def):
                return value_list
            
            self.console.print("[red]Invalid list format. Please try again.[/red]")
    
    def _collect_choice_parameter(self, param_def: ParameterDefinition) -> str:
        """Collect a choice parameter."""
        if not param_def.choices:
            return self._collect_string_parameter(param_def)
        
        return Prompt.ask(
            f"Select {param_def.name}",
            choices=param_def.choices,
            default=str(param_def.default) if param_def.default else None
        )
    
    def _collect_range_parameter(self, param_def: ParameterDefinition) -> Dict[str, Union[int, float]]:
        """Collect a range parameter (min, max values)."""
        self.console.print(f"Enter range for {param_def.name}")
        
        min_val = None
        max_val = None
        
        if param_def.param_type == ParameterType.RANGE:
            min_val = FloatPrompt.ask("Minimum value", default=param_def.min_value)
            max_val = FloatPrompt.ask("Maximum value", default=param_def.max_value)
        
        return {"min": min_val, "max": max_val}
    
    def _validate_single_parameter(self, value: Any, param_def: ParameterDefinition) -> bool:
        """Validate a single parameter value."""
        # Check required
        if param_def.required and (value is None or value == ""):
            return False
        
        # Check choices
        if param_def.choices and value not in param_def.choices:
            return False
        
        # Check range for numeric values
        if isinstance(value, (int, float)):
            if param_def.min_value is not None and value < param_def.min_value:
                return False
            if param_def.max_value is not None and value > param_def.max_value:
                return False
        
        # Check custom validator
        if param_def.validator and not param_def.validator(value):
            return False
        
        return True
    
    def _validate_parameters(
        self,
        parameters: Dict[str, Any],
        parameter_definitions: List[ParameterDefinition]
    ) -> bool:
        """Validate all collected parameters."""
        self.validation_errors.clear()
        
        # Check for required parameters
        required_params = {p.name for p in parameter_definitions if p.required}
        provided_params = set(parameters.keys())
        missing_params = required_params - provided_params
        
        if missing_params:
            self.validation_errors.extend([f"Missing required parameter: {p}" for p in missing_params])
        
        # Validate individual parameters
        param_def_map = {p.name: p for p in parameter_definitions}
        
        for param_name, param_value in parameters.items():
            if param_name in param_def_map:
                param_def = param_def_map[param_name]
                if not self._validate_single_parameter(param_value, param_def):
                    self.validation_errors.append(f"Invalid value for {param_name}: {param_value}")
        
        if self.validation_errors:
            self.console.print("[red]Validation errors:[/red]")
            for error in self.validation_errors:
                self.console.print(f"  • {error}")
            return False
        
        return True
    
    def create_parameter_preset(
        self,
        preset_name: str,
        parameters: Dict[str, Any],
        description: str = ""
    ) -> bool:
        """Create a parameter preset for reuse."""
        preset_data = {
            "name": preset_name,
            "description": description,
            "parameters": parameters,
            "created_at": str(asyncio.get_event_loop().time())
        }
        
        # Store preset (in a real implementation, this would be persisted)
        self.parameter_history[f"preset_{preset_name}"] = preset_data
        
        self.console.print(f"[green]✅ Created parameter preset: {preset_name}[/green]")
        return True
    
    def load_parameter_preset(self, preset_name: str) -> Dict[str, Any]:
        """Load a parameter preset."""
        preset_key = f"preset_{preset_name}"
        
        if preset_key in self.parameter_history:
            preset_data = self.parameter_history[preset_key]
            self.console.print(f"[green]✅ Loaded parameter preset: {preset_name}[/green]")
            return preset_data.get("parameters", {})
        
        self.console.print(f"[red]❌ Parameter preset not found: {preset_name}[/red]")
        return {}
    
    def list_parameter_presets(self) -> List[str]:
        """List available parameter presets."""
        presets = []
        for key in self.parameter_history.keys():
            if key.startswith("preset_"):
                preset_name = key[7:]  # Remove "preset_" prefix
                presets.append(preset_name)
        
        return presets
    
    def display_parameter_summary(self, parameters: Dict[str, Any]) -> None:
        """Display a summary of collected parameters."""
        self.console.print("\n[blue]📋 Parameter Summary[/blue]")
        
        table = Table(title="Collected Parameters")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Type", style="dim")
        
        for param_name, param_value in parameters.items():
            value_str = str(param_value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            
            param_type = type(param_value).__name__
            table.add_row(param_name, value_str, param_type)
        
        self.console.print(table)
    
    async def interactive_parameter_adjustment(
        self,
        current_parameters: Dict[str, Any],
        parameter_definitions: List[ParameterDefinition]
    ) -> Dict[str, Any]:
        """Allow interactive adjustment of existing parameters."""
        self.console.print("\n[blue]🔧 Interactive Parameter Adjustment[/blue]")
        
        # Display current parameters
        self.display_parameter_summary(current_parameters)
        
        if not Confirm.ask("Would you like to modify any parameters?"):
            return current_parameters
        
        new_parameters = current_parameters.copy()
        param_def_map = {p.name: p for p in parameter_definitions}
        
        while True:
            # Show available parameters
            param_names = list(new_parameters.keys())
            param_names.append("Done")
            
            self.console.print("\nSelect parameter to modify:")
            for i, param_name in enumerate(param_names, 1):
                current_value = new_parameters.get(param_name, "N/A") if param_name != "Done" else ""
                display_text = f"{param_name}" + (f" (current: {current_value})" if param_name != "Done" else "")
                self.console.print(f"  {i}. {display_text}")
            
            choice = Prompt.ask(
                "Select parameter",
                choices=[str(i) for i in range(1, len(param_names) + 1)],
                default=str(len(param_names))
            )
            
            if int(choice) == len(param_names):
                break
            
            selected_param = param_names[int(choice) - 1]
            
            if selected_param in param_def_map:
                param_def = param_def_map[selected_param]
                # Temporarily set the current value as default
                original_default = param_def.default
                param_def.default = new_parameters.get(selected_param)
                
                new_value = await self._collect_single_parameter(param_def, allow_skip=True)
                if new_value is not None:
                    new_parameters[selected_param] = new_value
                
                # Restore original default
                param_def.default = original_default
            else:
                self.console.print(f"[yellow]Parameter {selected_param} not found in definitions[/yellow]")
        
        return new_parameters