"""
@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : tui_framework.py
@Description: Interactive TUI framework using prompt_toolkit for DAIP-LIVE system.
"""

import asyncio

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import (
    Layout,
    HSplit,
    Window,
    FormattedTextControl,
    BufferControl
)
from prompt_toolkit.styles import Style

from rich.console import Console

console = Console()

class DAIPTUI:
    """Interactive TUI framework for DAIP-LIVE system."""
    
    def __init__(self):
        self.application = None
        self.layout = None
        self.key_bindings = KeyBindings()
        self.style = Style.from_dict({
            '': 'bg:#000000 #ffffff',
            'status': 'bg:#444444 #ffffff',
            'input': 'bg:#222222 #ffffff',
            'output': 'bg:#111111 #ffffff',
            'menu': 'bg:#333333 #ffffff',
            'selected': 'bg:#008800 #ffffff',
            'error': 'bg:#880000 #ffffff',
            'warning': 'bg:#884400 #ffffff',
            'success': 'bg:#008800 #ffffff',
        })
        
        # Initialize buffers
        self.input_buffer = Buffer()
        self.output_buffer = Buffer()
        self.status_buffer = Buffer()
        
        self._setup_key_bindings()
        self._setup_layout()
        
    def _setup_key_bindings(self):
        """Set up key bindings for the TUI."""
        
        @self.key_bindings.add('c-c')
        def _(event):
            """Handle Ctrl+C - exit application."""
            event.app.exit()
            
        @self.key_bindings.add('c-l')
        def _(event):
            """Handle Ctrl+L - clear output."""
            self.output_buffer.text = ''
            
        @self.key_bindings.add('enter')
        def _(event):
            """Handle Enter - process input."""
            if self.input_buffer.text.strip():
                self._process_input(self.input_buffer.text)
                self.input_buffer.reset()
    
    def _setup_layout(self):
        """Set up the TUI layout."""
        
        # Status bar
        status_bar = Window(
            content=FormattedTextControl(
                text=self._get_status_text,
                style='class:status'
            ),
            height=1,
            style='class:status'
        )
        
        # Output area
        output_area = Window(
            content=BufferControl(
                buffer=self.output_buffer,
                style='class:output'
            ),
            wrap_lines=True,
            style='class:output'
        )
        
        # Input area
        input_area = Window(
            content=BufferControl(
                buffer=self.input_buffer,
                style='class:input'
            ),
            height=3,
            style='class:input'
        )
        
        # Main layout
        self.layout = Layout(
            HSplit([
                status_bar,
                output_area,
                input_area
            ])
        )
    
    def _get_status_text(self) -> str:
        """Get current status text."""
        return "DAIP-LIVE TUI | Press Ctrl+C to exit | Ctrl+L to clear"
    
    def _process_input(self, text: str):
        """Process user input."""
        # Add input to output buffer
        self.output_buffer.text += f"\n> {text}"
        
        # Handle special commands
        if text.lower() in ['exit', 'quit', 'q']:
            self.application.exit()
            return
        elif text.lower() in ['clear', 'cls']:
            self.output_buffer.text = ''
            return
        elif text.lower() in ['help', '?']:
            self._show_help()
            return
        elif text.lower().startswith('wiki '):
            self._handle_wiki_command(text[5:])
            return
        
        # Default: echo input
        self.output_buffer.text += f"\nEcho: {text}"
    
    def _show_help(self):
        """Show help information."""
        help_text = """
DAIP-LIVE TUI Commands:
  help, ?        - Show this help
  exit, quit, q  - Exit the application
  clear, cls     - Clear the output
  wiki [command] - Wiki-related commands
  
Available Wiki Commands:
  wiki capabilities   - Show wiki collaboration capabilities
  wiki generate [topic] - Generate wiki content for a topic
  wiki status        - Show wiki service status
"""
        self.output_buffer.text += help_text
    
    def _handle_wiki_command(self, command: str):
        """Handle wiki-related commands with graceful error handling."""
        try:
            if command.strip() == 'capabilities':
                self._show_wiki_capabilities()
            elif command.strip().startswith('generate '):
                topic = command[9:].strip()
                if topic:
                    self._generate_wiki_content(topic)
                else:
                    self.output_buffer.text += "\nError: Please specify a topic for wiki generation"
            elif command.strip() == 'status':
                self._show_wiki_status()
            else:
                self.output_buffer.text += f"\nUnknown wiki command: {command}"
        except Exception as e:
            self.output_buffer.text += f"\nError executing wiki command: {e}"
            self.output_buffer.text += "\nWiki features may not be fully available in this mode"
    
    def _show_wiki_capabilities(self):
        """Show wiki collaboration capabilities."""
        try:
            # Try to import and use wiki service
            from src.core_services.wiki_service import WikiService
            wiki_service = WikiService()
            
            if hasattr(wiki_service, 'get_capabilities'):
                capabilities = wiki_service.get_capabilities()
                self.output_buffer.text += f"\nWiki Capabilities: {capabilities}"
            else:
                self.output_buffer.text += "\nWiki capabilities method not available"
                
        except ImportError:
            self.output_buffer.text += "\nWiki service not available (ImportError)"
        except Exception as e:
            self.output_buffer.text += f"\nError accessing wiki capabilities: {e}"
    
    def _generate_wiki_content(self, topic: str):
        """Generate wiki content for a topic."""
        try:
            # Try to import and use wiki content generator
            from src.core_services.wiki_content_generator import WikiContentGenerator
            from src.core_services.role_manager import RoleManager
            from src.core_services.integrated_llm_manager import IntegratedLLMManager
            
            role_manager = RoleManager()
            llm_manager = IntegratedLLMManager()
            
            generator = WikiContentGenerator(role_manager, llm_manager)
            
            self.output_buffer.text += f"\nGenerating wiki content for: {topic}"
            
            # Run generation asynchronously
            async def generate_async():
                try:
                    result = await generator.generate_wiki_content(topic)
                    self.output_buffer.text += f"\nGenerated content:\n{result}"
                except Exception as e:
                    self.output_buffer.text += f"\nError during generation: {e}"
            
            # Run in background
            asyncio.create_task(generate_async())
            
        except ImportError:
            self.output_buffer.text += "\nWiki content generation not available (ImportError)"
        except Exception as e:
            self.output_buffer.text += f"\nError initializing wiki generation: {e}"
    
    def _show_wiki_status(self):
        """Show wiki service status."""
        try:
            from src.core_services.wiki_service import WikiService
            wiki_service = WikiService()
            
            status = "Available"
            if hasattr(wiki_service, 'check_health'):
                health = wiki_service.check_health()
                status = f"Healthy: {health}"
            
            self.output_buffer.text += f"\nWiki Service Status: {status}"
            
        except ImportError:
            self.output_buffer.text += "\nWiki service not available (ImportError)"
        except Exception as e:
            self.output_buffer.text += f"\nError checking wiki status: {e}"
    
    def run(self):
        """Run the TUI application."""
        self.application = Application(
            layout=self.layout,
            key_bindings=self.key_bindings,
            style=self.style,
            full_screen=True
        )
        
        # Initial message
        self.output_buffer.text = "Welcome to DAIP-LIVE Interactive TUI!\nType 'help' for available commands."
        
        try:
            self.application.run()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            console.print(f"Error running TUI: {e}")

def start_interactive_tui():
    """Start the interactive TUI."""
    tui = DAIPTUI()
    tui.run()

if __name__ == "__main__":
    start_interactive_tui()