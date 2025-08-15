"""@Time    : 2025-07-24 19:30:00
@Author  : DAIP-LIVE Team
@File    : workflow_steering.py
@Description:
    Workflow steering capabilities for real-time user intervention.
"""
import asyncio
import logging
import time
<<<<<<< HEAD
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
=======
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

logger = logging.getLogger(__name__)


class SteeringAction(Enum):
    """Available steering actions during workflow execution."""

    CONTINUE = "continue"
    PAUSE = "pause"
    MODIFY_PARAMETERS = "modify_parameters"
    SKIP_STEP = "skip_step"
    RETRY_STEP = "retry_step"
    INJECT_DATA = "inject_data"
    CHANGE_DIRECTION = "change_direction"
    EMERGENCY_STOP = "emergency_stop"
    SAVE_CHECKPOINT = "save_checkpoint"
    LOAD_CHECKPOINT = "load_checkpoint"


@dataclass
class SteeringPoint:
    """Represents a point in the workflow where user can intervene."""

    id: str
    name: str
    description: str
    workflow_step: str
    available_actions: list[SteeringAction]
    context: dict[str, Any] = field(default_factory=dict)
    auto_continue_timeout: Optional[float] = None
    priority: int = 1  # 1=low, 2=medium, 3=high


@dataclass
class SteeringCommand:
    """Command issued by user during workflow steering."""

    action: SteeringAction
    parameters: dict[str, Any] = field(default_factory=dict)
    target_step: Optional[str] = None
    message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class WorkflowSteering:
    """Manages real-time workflow steering and user intervention."""

    def __init__(self, console: Console = None):
        """Initialize the workflow steering system."""
        self.console = console or Console()
        self.steering_points: dict[str, SteeringPoint] = {}
        self.active_steering: bool = False
        self.steering_queue: asyncio.Queue = asyncio.Queue()
<<<<<<< HEAD
        self.command_callbacks: Dict[SteeringAction, List[Callable]] = {}
        self.workflow_state: Dict[str, Any] = {}
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        self.steering_history: List[SteeringCommand] = []

=======
        self.command_callbacks: dict[SteeringAction, list[Callable]] = {}
        self.workflow_state: dict[str, Any] = {}
        self.checkpoints: dict[str, dict[str, Any]] = {}
        self.steering_history: list[SteeringCommand] = []
    
>>>>>>> feature/core-services-refactor
    def register_steering_point(
        self,
        point_id: str,
        name: str,
        description: str,
        workflow_step: str,
        available_actions: list[SteeringAction] = None,
        auto_continue_timeout: Optional[float] = None,
        priority: int = 1
    ) -> None:
        """Register a steering point in the workflow."""
        if available_actions is None:
            available_actions = [
                SteeringAction.CONTINUE,
                SteeringAction.PAUSE,
                SteeringAction.MODIFY_PARAMETERS
            ]

        steering_point = SteeringPoint(
            id=point_id,
            name=name,
            description=description,
            workflow_step=workflow_step,
            available_actions=available_actions,
            auto_continue_timeout=auto_continue_timeout,
            priority=priority
        )

        self.steering_points[point_id] = steering_point
        logger.info(f"Registered steering point: {point_id}")

    def register_command_callback(
        self,
        action: SteeringAction,
        callback: Callable[[SteeringCommand], Any]
    ) -> None:
        """Register a callback for a specific steering action."""
        if action not in self.command_callbacks:
            self.command_callbacks[action] = []

        self.command_callbacks[action].append(callback)

    async def trigger_steering_point(
        self,
        point_id: str,
        context: dict[str, Any] = None,
        force_interaction: bool = False
    ) -> SteeringCommand:
        """Trigger a steering point and wait for user input."""
        if point_id not in self.steering_points:
            logger.warning(f"Unknown steering point: {point_id}")
            return SteeringCommand(action=SteeringAction.CONTINUE)

        steering_point = self.steering_points[point_id]
        steering_point.context = context or {}

        # Update workflow state
        self.workflow_state.update(context or {})

        # Check if we should auto-continue
        if not force_interaction and steering_point.auto_continue_timeout:
            command = await self._handle_auto_continue(steering_point)
            if command:
                return command

        # Display steering interface
        return await self._display_steering_interface(steering_point)

    async def _handle_auto_continue(
        self,
        steering_point: SteeringPoint
    ) -> Optional[SteeringCommand]:
        """Handle auto-continue with timeout."""
        self.console.print(f"\n[yellow]⚠️  Steering Point: {steering_point.name}[/yellow]")
        self.console.print(f"[dim]{steering_point.description}[/dim]")

        if steering_point.auto_continue_timeout:
            self.console.print(f"[dim]Auto-continuing in {steering_point.auto_continue_timeout}s (press any key to intervene)[/dim]")

            # Wait for timeout or user input
            try:
                # This is a simplified version - in a real implementation,
                # you'd want to use proper async keyboard input handling
                await asyncio.sleep(steering_point.auto_continue_timeout)
                return SteeringCommand(action=SteeringAction.CONTINUE)
            except KeyboardInterrupt:
                # User interrupted - show full interface
                return None

        return None

    async def _display_steering_interface(
        self,
        steering_point: SteeringPoint
    ) -> SteeringCommand:
        """Display the interactive steering interface."""
        self.console.print(f"\n[blue]🎛️  Workflow Steering: {steering_point.name}[/blue]")
        self.console.print(f"[dim]{steering_point.description}[/dim]")

        # Display current context
        if steering_point.context:
            self._display_steering_context(steering_point.context)

        # Display available actions
        actions = steering_point.available_actions
        action_names = [action.value.replace("_", " ").title() for action in actions]

        self.console.print("\n[cyan]Available actions:[/cyan]")
        for i, (action, name) in enumerate(zip(actions, action_names, strict=False), 1):
            self.console.print(f"  {i}. {name}")

        # Get user choice
        choice = Prompt.ask(
            "Select an action",
            choices=[str(i) for i in range(1, len(actions) + 1)],
            default="1"
        )

        selected_action = actions[int(choice) - 1]

        # Handle the selected action
        command = await self._handle_steering_action(selected_action, steering_point)

        # Record in history
        self.steering_history.append(command)

        # Execute callbacks
        await self._execute_command_callbacks(command)

        return command

    async def _handle_steering_action(
        self,
        action: SteeringAction,
        steering_point: SteeringPoint
    ) -> SteeringCommand:
        """Handle a specific steering action."""
        command_params = {}
        message = None

        if action == SteeringAction.CONTINUE:
            self.console.print("[green]✅ Continuing workflow...[/green]")

        elif action == SteeringAction.PAUSE:
            message = await self._handle_pause_action()

        elif action == SteeringAction.MODIFY_PARAMETERS:
            command_params = await self._handle_modify_parameters()

        elif action == SteeringAction.SKIP_STEP:
            command_params = await self._handle_skip_step()

        elif action == SteeringAction.RETRY_STEP:
            command_params = await self._handle_retry_step()

        elif action == SteeringAction.INJECT_DATA:
            command_params = await self._handle_inject_data()

        elif action == SteeringAction.CHANGE_DIRECTION:
            command_params = await self._handle_change_direction()

        elif action == SteeringAction.EMERGENCY_STOP:
            message = "Emergency stop requested by user"
            self.console.print("[red]🛑 Emergency stop activated[/red]")

        elif action == SteeringAction.SAVE_CHECKPOINT:
            command_params = await self._handle_save_checkpoint()

        elif action == SteeringAction.LOAD_CHECKPOINT:
            command_params = await self._handle_load_checkpoint()

        return SteeringCommand(
            action=action,
            parameters=command_params,
            target_step=steering_point.workflow_step,
            message=message
        )

    async def _handle_pause_action(self) -> str:
        """Handle pause action."""
        self.console.print("[yellow]⏸️  Workflow paused[/yellow]")

        pause_options = [
            "Resume immediately",
            "Resume after delay",
            "Wait for manual resume",
            "Save state and exit"
        ]

        self.console.print("Pause options:")
        for i, option in enumerate(pause_options, 1):
            self.console.print(f"  {i}. {option}")

        choice = Prompt.ask(
            "Select pause option",
            choices=[str(i) for i in range(1, len(pause_options) + 1)],
            default="1"
        )

        selected_option = pause_options[int(choice) - 1]

        if selected_option == "Resume after delay":
            from rich.prompt import IntPrompt
            delay = IntPrompt.ask("Enter delay in seconds", default=5)
            return f"Paused for {delay} seconds"

        return f"Paused: {selected_option}"
<<<<<<< HEAD

    async def _handle_modify_parameters(self) -> Dict[str, Any]:
=======
    
    async def _handle_modify_parameters(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handle parameter modification."""
        self.console.print("[blue]🔧 Parameter Modification[/blue]")

        # Get current parameters from workflow state
        current_params = self.workflow_state.get("parameters", {})

        if not current_params:
            self.console.print("[yellow]No parameters available for modification[/yellow]")
            return {}

        # Display current parameters
        table = Table(title="Current Parameters")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")

        for param_name, param_value in current_params.items():
            table.add_row(param_name, str(param_value))

        self.console.print(table)

        # Select parameter to modify
        param_names = list(current_params.keys())
        param_names.append("Cancel")

        self.console.print("\nSelect parameter to modify:")
        for i, param_name in enumerate(param_names, 1):
            self.console.print(f"  {i}. {param_name}")

        choice = Prompt.ask(
            "Select parameter",
            choices=[str(i) for i in range(1, len(param_names) + 1)],
            default=str(len(param_names))
        )

        if int(choice) == len(param_names):
            return {}

        selected_param = param_names[int(choice) - 1]
        current_value = current_params[selected_param]

        # Get new value
        new_value = Prompt.ask(
            f"Enter new value for {selected_param}",
            default=str(current_value)
        )

        # Try to convert to appropriate type
        try:
            if isinstance(current_value, bool):
                new_value = new_value.lower() in ('true', 'yes', '1', 'on')
            elif isinstance(current_value, int):
                new_value = int(new_value)
            elif isinstance(current_value, float):
                new_value = float(new_value)
            elif isinstance(current_value, list):
                new_value = [item.strip() for item in new_value.split(",")]
        except ValueError:
            self.console.print("[yellow]Warning: Could not convert value type, using string[/yellow]")

        return {
            "parameter_name": selected_param,
            "old_value": current_value,
            "new_value": new_value
        }
<<<<<<< HEAD

    async def _handle_skip_step(self) -> Dict[str, Any]:
=======
    
    async def _handle_skip_step(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handle step skipping."""
        self.console.print("[yellow]⏭️  Skip Step[/yellow]")

        reason = Prompt.ask("Reason for skipping step", default="User requested")

        return {
            "skip_reason": reason,
            "skip_timestamp": time.time()
        }
<<<<<<< HEAD

    async def _handle_retry_step(self) -> Dict[str, Any]:
=======
    
    async def _handle_retry_step(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handle step retry."""
        self.console.print("[blue]🔄 Retry Step[/blue]")

        retry_options = [
            "Retry with same parameters",
            "Retry with modified parameters",
            "Retry with different approach"
        ]

        self.console.print("Retry options:")
        for i, option in enumerate(retry_options, 1):
            self.console.print(f"  {i}. {option}")

        choice = Prompt.ask(
            "Select retry option",
            choices=[str(i) for i in range(1, len(retry_options) + 1)],
            default="1"
        )

        selected_option = retry_options[int(choice) - 1]

        return {
            "retry_type": selected_option,
            "retry_timestamp": time.time()
        }
<<<<<<< HEAD

    async def _handle_inject_data(self) -> Dict[str, Any]:
=======
    
    async def _handle_inject_data(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handle data injection."""
        self.console.print("[green]💉 Inject Data[/green]")

        data_key = Prompt.ask("Enter data key")
        data_value = Prompt.ask("Enter data value")

        # Try to parse as JSON if it looks like structured data
        if data_value.startswith(("{", "[")):
            try:
                import json
                data_value = json.loads(data_value)
            except json.JSONDecodeError:
                pass

        return {
            "injection_key": data_key,
            "injection_value": data_value,
            "injection_timestamp": time.time()
        }
<<<<<<< HEAD

    async def _handle_change_direction(self) -> Dict[str, Any]:
=======
    
    async def _handle_change_direction(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handle workflow direction change."""
        self.console.print("[purple]🔀 Change Direction[/purple]")

        new_direction = Prompt.ask("Enter new workflow direction/goal")
        priority = Prompt.ask(
            "Priority level",
            choices=["low", "medium", "high"],
            default="medium"
        )

        return {
            "new_direction": new_direction,
            "priority": priority,
            "change_timestamp": time.time()
        }
<<<<<<< HEAD

    async def _handle_save_checkpoint(self) -> Dict[str, Any]:
=======
    
    async def _handle_save_checkpoint(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handle checkpoint saving."""
        self.console.print("[blue]💾 Save Checkpoint[/blue]")

        checkpoint_name = Prompt.ask("Enter checkpoint name", default=f"checkpoint_{int(time.time())}")
        description = Prompt.ask("Enter checkpoint description", default="User-created checkpoint")

        # Save current workflow state
        checkpoint_data = {
            "name": checkpoint_name,
            "description": description,
            "workflow_state": self.workflow_state.copy(),
            "timestamp": time.time()
        }

        self.checkpoints[checkpoint_name] = checkpoint_data

        self.console.print(f"[green]✅ Checkpoint '{checkpoint_name}' saved[/green]")

        return {
            "checkpoint_name": checkpoint_name,
            "checkpoint_description": description
        }
<<<<<<< HEAD

    async def _handle_load_checkpoint(self) -> Dict[str, Any]:
=======
    
    async def _handle_load_checkpoint(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Handle checkpoint loading."""
        self.console.print("[blue]📂 Load Checkpoint[/blue]")

        if not self.checkpoints:
            self.console.print("[yellow]No checkpoints available[/yellow]")
            return {}

        # Display available checkpoints
        checkpoint_names = list(self.checkpoints.keys())
        checkpoint_names.append("Cancel")

        self.console.print("Available checkpoints:")
        for i, name in enumerate(checkpoint_names, 1):
            if name != "Cancel":
                checkpoint = self.checkpoints[name]
                timestamp = time.ctime(checkpoint["timestamp"])
                self.console.print(f"  {i}. {name} ({timestamp})")
            else:
                self.console.print(f"  {i}. {name}")

        choice = Prompt.ask(
            "Select checkpoint",
            choices=[str(i) for i in range(1, len(checkpoint_names) + 1)],
            default=str(len(checkpoint_names))
        )

        if int(choice) == len(checkpoint_names):
            return {}

        selected_checkpoint = checkpoint_names[int(choice) - 1]
        checkpoint_data = self.checkpoints[selected_checkpoint]

        self.console.print(f"[green]✅ Loading checkpoint '{selected_checkpoint}'[/green]")

        return {
            "checkpoint_name": selected_checkpoint,
            "checkpoint_data": checkpoint_data
        }
<<<<<<< HEAD

    def _display_steering_context(self, context: Dict[str, Any]) -> None:
=======
    
    def _display_steering_context(self, context: dict[str, Any]) -> None:
>>>>>>> feature/core-services-refactor
        """Display current steering context."""
        self.console.print("\n[blue]Current Context:[/blue]")

        # Show key context information
        important_keys = ["current_step", "progress", "status", "execution_id", "parameters"]

        for key in important_keys:
            if key in context:
                value = context[key]
                if isinstance(value, dict) and len(value) > 3:
                    value_str = f"Dict with {len(value)} keys"
                elif isinstance(value, list) and len(value) > 5:
                    value_str = f"List with {len(value)} items"
                else:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:97] + "..."

                self.console.print(f"  • {key}: {value_str}")

    async def _execute_command_callbacks(self, command: SteeringCommand) -> None:
        """Execute registered callbacks for a steering command."""
        if command.action in self.command_callbacks:
            for callback in self.command_callbacks[command.action]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(command)
                    else:
                        callback(command)
                except Exception as e:
                    logger.error(f"Error executing steering callback: {e}")
<<<<<<< HEAD

    def get_steering_history(self) -> List[SteeringCommand]:
=======
    
    def get_steering_history(self) -> list[SteeringCommand]:
>>>>>>> feature/core-services-refactor
        """Get the history of steering commands."""
        return self.steering_history.copy()

    def clear_steering_history(self) -> None:
        """Clear the steering command history."""
        self.steering_history.clear()
<<<<<<< HEAD

    def get_available_checkpoints(self) -> List[str]:
=======
    
    def get_available_checkpoints(self) -> list[str]:
>>>>>>> feature/core-services-refactor
        """Get list of available checkpoint names."""
        return list(self.checkpoints.keys())

    def delete_checkpoint(self, checkpoint_name: str) -> bool:
        """Delete a checkpoint."""
        if checkpoint_name in self.checkpoints:
            del self.checkpoints[checkpoint_name]
            self.console.print(f"[green]✅ Checkpoint '{checkpoint_name}' deleted[/green]")
            return True

        self.console.print(f"[red]❌ Checkpoint '{checkpoint_name}' not found[/red]")
        return False
