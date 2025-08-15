"""@Time    : 2025-07-21 10:00:00
@Author  : DAIP-LIVE Team
@File    : user_intervention.py
@Description: User intervention functionality for the CLI interface.
"""

import asyncio
import logging
import msvcrt  # Windows-specific keyboard input module
import threading

from rich.console import Console
from rich.prompt import Prompt

from src.models import UserInterventionCommand
from src.user_interface.interactive_controller import InteractiveController
from src.user_interface.parameter_manager import ParameterDefinition, ParameterType

# Initialize console and logger
console = Console()
logger = logging.getLogger(__name__)

class UserInterventionHandler:
    """Handles user intervention in CLI debates."""
    
    def __init__(self, command_queue):
        """Initialize the user intervention handler.
        
        Args:
            command_queue: Queue to send commands to the debate protocol
        """
        self.command_queue = command_queue
        self.running = False
        self.keyboard_thread = None
        self.interactive_controller = InteractiveController(console=console)
    
    def start_listening(self):
        """Start listening for keyboard input in a separate thread."""
        self.running = True
        self.keyboard_thread = threading.Thread(target=self._keyboard_listener)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        console.print("[dim]💡 Press 'i' at any time to intervene in the debate[/dim]")
    
    def stop_listening(self):
        """Stop listening for keyboard input."""
        self.running = False
        if self.keyboard_thread and self.keyboard_thread.is_alive():
            self.keyboard_thread.join(timeout=1.0)
    
    def _keyboard_listener(self):
        """Listen for keyboard input in a separate thread."""
        while self.running:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'i':
                        # Signal the main thread to handle intervention
                        asyncio.run_coroutine_threadsafe(self._handle_intervention(), asyncio.get_event_loop())
                    elif key == 'q':
                        # Signal to quit
                        console.print("[yellow]Quit requested. Finishing current operations...[/yellow]")
                        self.running = False
            except Exception as e:
                logger.error(f"Error in keyboard listener: {e}")
            
            # Sleep to prevent high CPU usage
            threading.Event().wait(0.1)
    
    async def _handle_intervention(self):
        """Handle user intervention by prompting for input and sending a command."""
        try:
            # Clear the current line and show prompt
            console.print("\n[bold green]User Intervention:[/bold green]")
            
            # Show intervention options
            intervention_options = [
                "Send message",
                "Modify parameters",
                "Pause workflow",
                "View current state",
                "Cancel"
            ]
            
            console.print("Intervention options:")
            for i, option in enumerate(intervention_options, 1):
                console.print(f"  {i}. {option}")
            
            choice = Prompt.ask(
                "Select intervention type",
                choices=[str(i) for i in range(1, len(intervention_options) + 1)],
                default="1"
            )
            
            choice_num = int(choice)
            
            if choice_num == 1:  # Send message
                user_input = Prompt.ask("[bold green]Enter your message[/bold green]")
                if user_input.strip():
                    command = UserInterventionCommand(content=user_input)
                    await self.command_queue.put(command)
                    console.print("[dim]Message sent. Continuing...[/dim]")
                else:
                    console.print("[yellow]Empty message ignored.[/yellow]")
            
            elif choice_num == 2:  # Modify parameters
                await self._handle_parameter_modification()
            
            elif choice_num == 3:  # Pause workflow
                await self._handle_workflow_pause()
            
            elif choice_num == 4:  # View current state
                await self._display_current_state()
            
            elif choice_num == 5:  # Cancel
                console.print("[dim]Intervention cancelled.[/dim]")
        
        except Exception as e:
            console.print(f"[red]Failed to process intervention: {e}[/red]")
            logger.error(f"Intervention handling error: {e}", exc_info=True)
    
    async def _handle_parameter_modification(self):
        """Handle parameter modification during intervention."""
        console.print("\n[blue]Parameter Modification[/blue]")
        
        # Example parameter definitions for debate
        param_defs = [
            ParameterDefinition(
                name="response_length",
                param_type=ParameterType.INTEGER,
                description="Maximum response length in words",
                default=200,
                min_value=50,
                max_value=500
            ),
            ParameterDefinition(
                name="debate_intensity",
                param_type=ParameterType.CHOICE,
                description="Intensity level of the debate",
                default="moderate",
                choices=["low", "moderate", "high"]
            ),
            ParameterDefinition(
                name="fact_checking",
                param_type=ParameterType.BOOLEAN,
                description="Enable fact checking during debate",
                default=True
            )
        ]
        
        try:
            parameters = await self.interactive_controller.collect_workflow_parameters(
                workflow_name="debate",
                parameter_definitions=param_defs,
                context={"intervention": True}
            )
            
            if parameters:
                # Send parameter modification command
                command = UserInterventionCommand(
                    content="Parameter modification",
                    metadata={"type": "parameter_modification", "parameters": parameters}
                )
                await self.command_queue.put(command)
                console.print("[green]Parameters modified successfully.[/green]")
            else:
                console.print("[yellow]No parameters modified.[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Failed to modify parameters: {e}[/red]")
            logger.error(f"Parameter modification error: {e}", exc_info=True)
    
    async def _handle_workflow_pause(self):
        """Handle workflow pause during intervention."""
        console.print("\n[yellow]Workflow Pause[/yellow]")
        
        pause_options = [
            "Pause for 30 seconds",
            "Pause for 2 minutes",
            "Pause indefinitely",
            "Save current state and pause"
        ]
        
        console.print("Pause options:")
        for i, option in enumerate(pause_options, 1):
            console.print(f"  {i}. {option}")
        
        choice = Prompt.ask(
            "Select pause option",
            choices=[str(i) for i in range(1, len(pause_options) + 1)],
            default="1"
        )
        
        choice_num = int(choice)
        pause_duration = None
        
        if choice_num == 1:
            pause_duration = 30
        elif choice_num == 2:
            pause_duration = 120
        elif choice_num == 3:
            pause_duration = -1  # Indefinite
        elif choice_num == 4:
            pause_duration = -1
            # TODO: Implement state saving
        
        # Send pause command
        command = UserInterventionCommand(
            content="Workflow pause requested",
            metadata={"type": "pause", "duration": pause_duration}
        )
        await self.command_queue.put(command)
        console.print("[yellow]Workflow pause requested.[/yellow]")
    
    async def _display_current_state(self):
        """Display current workflow state."""
        console.print("\n[blue]Current Workflow State[/blue]")
        
        # This would normally get actual state from the workflow
        # For now, show placeholder information
        state_info = {
            "current_step": "debate_round_2",
            "participants": ["Participant A", "Participant B"],
            "messages_exchanged": 8,
            "time_elapsed": "5 minutes",
            "status": "active"
        }
        
        from rich.table import Table
        
        table = Table(title="Workflow State")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        for key, value in state_info.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        
        console.print(table)
        
        # Ask if user wants to take action based on state
        if Prompt.ask("Take action based on current state?", choices=["y", "n"], default="n") == "y":
            await self._handle_state_based_action(state_info)
    
    async def _handle_state_based_action(self, state_info: dict):
        """Handle actions based on current state."""
        console.print("\n[cyan]State-based Actions[/cyan]")
        
        actions = [
            "Speed up the debate",
            "Slow down the debate",
            "Change topic focus",
            "Add new participant",
            "End current round"
        ]
        
        console.print("Available actions:")
        for i, action in enumerate(actions, 1):
            console.print(f"  {i}. {action}")
        
        choice = Prompt.ask(
            "Select action",
            choices=[str(i) for i in range(1, len(actions) + 1)]
        )
        
        selected_action = actions[int(choice) - 1]
        
        # Send state-based action command
        command = UserInterventionCommand(
            content=f"State-based action: {selected_action}",
            metadata={
                "type": "state_action",
                "action": selected_action,
                "current_state": state_info
            }
        )
        await self.command_queue.put(command)
        console.print(f"[green]Action '{selected_action}' requested.[/green]")