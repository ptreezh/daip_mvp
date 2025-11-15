"""
AI PSY ASCII Art Logo Generator

Creates a colored ASCII art logo for the TUI startup screen.
"""
from rich.console import Console
from rich.text import Text
from rich.style import Style
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
import time
import asyncio
import random


class PersonalAILogo:
    """AI PSY ASCII art logo with colors and animation."""
    
    def __init__(self):
        self.console = Console()
        
        # Define multiple ASCII art variants for AGENT PSY LAB
        self.logo_variants = [
            # Variant 1: Original style
            [
                r"    ____      _           _       ",
                r"   / ___| ___| | ___  ___| |_     ",
                r"  | |  _ / _ \ |/ _ \/ __| __|   ",
                r"  | |_| |  __/ |  __/ (__| |_    ",
                r"   \____|\___|_|\___|\___|\__|   ",
                r"                                  ",
                r"  _____        _           _       ",
                r" |_   _|____ _| |_ ___  __| |     ",
                r"   | |/ _ \ __| __/ _ \/ _` |     ",
                r"   | |  __/__ \ ||  __/ (_| |     ",
                r"   |_|\___|___/\__\___|\__,_|     ",
                r"                                  ",
                r"  _        _   _           _      ",
                r" | |_ __ _| |_(_) ___ __ _| |___  ",
                r" | __/ _` | __| |/ __/ _` | / __| ",
                r" | || (_| | |_| | (_| (_| | \__ \ ",
                r"  \__\__,_|\__|_|\___\__,_|_|___/ ",
                r"                                  ",
                r"      AGENT PSY LAB               ",
                r"                                  ",
                r"    🤖 Intelligent Agent Lab       ",
                r"           welcome!                "
            ],
            # Variant 2: Modern style
            [
                r"  _______      _           _       ",
                r" |__   __|    | |         | |     ",
                r"    | |  _ __ | | _____  _| |_    ",
                r"    | | | '_ \| |/ _ \ \/ / __|   ",
                r"    | | | | | | |  __/>  <| |_    ",
                r"    |_| |_| |_|_|\___/_/\_\\__|   ",
                r"                                  ",
                r"  ______                         ",
                r" |  ____|                        ",
                r" | |__ ___  ___ _ __ _   _        ",
                r" |  __/ _ \/ _ \ '__| | | |       ",
                r" | | |  __/  __/ |  | |_| |       ",
                r" |_|  \___|\___|_|   \__, |       ",
                r"                      __/ |       ",
                r"                     |___/        ",
                r"                                  ",
                r"  _    ___   ___  _   _ ___       ",
                r" | |  / _ \ / _ \| \ | |_ _|      ",
                r" | |_| | | | | | |  \| || |       ",
                r" |  _| |_| | |_| | |\  || |       ",
                r" |_|  \___/ \___/|_| \_|___|      ",
                r"                                  ",
                r"       AGENT PSY LAB v3.0         ",
                r"                                  ",
                r"    🤖 Advanced Intelligence Lab    ",
                r"         Ready for Action!        "
            ],
            # Variant 3: Minimalist style
            [
                r"   ___    _   _  ___  ",
                r"  / _ \  | | | |/ _ \ ",
                r" | | | | | | | | (_) |",
                r" | | | | | |_| |\__, |",
                r" |_| |_|  \___/   /_/  ",
                r"                      ",
                r"   _   _ _   _ _      ",
                r"  | \ | (_) (_) |     ",
                r"  |  \| | | |_| |___  ",
                r"  | . ` | | | | / __| ",
                r"  | |\  | | | | \__ \ ",
                r"  |_| \_|_|_|_|_|___/ ",
                r"                      ",
                r"    AGENT PSY LAB      ",
                r"                      ",
                r"  🧠 Smart & Effective ",
                r"      Let's Go!       "
            ],
            # Variant 4: Cyber style
            [
                r"  dP   dP 888888ba  dP     dP    ",
                r"  88   88 88    `8b 88     88    ",
                r"  88   88 88     88 88    .8P    ",
                r"  88   88 88     88 88    d8'    ",
                r"  88   88 88    .8P 88  .d8P     ",
                r"  `88888P' 8888888P' 888888'     ",
                r"                                  ",
                r"   .8888b oo dP           dP       ",
                r"   88   `    88           88       ",
                r"   88aaa`b.d8888P .d888b88       ",
                r"   88   .8P `88__  8'  `88       ",
                r"   88   `8b  `88'' 88   88       ",
                r"   dP   `YP   88   `88888P       ",
                r"                                  ",
                r"      AGENT PSY LAB-CYBER         ",
                r"                                  ",
                r"    ⚡ Cybernetic Intelligence    ",
                r"       System Online             "
            ]
        ]
        
        # Randomly select a logo variant
        self.logo_art = random.choice(self.logo_variants)
        
        # Define color schemes for different parts
        self.color_schemes = {
            "ai": [
                Style(color="bright_cyan", bold=True),
                Style(color="cyan", bold=True),
                Style(color="blue", bold=True),
                Style(color="bright_blue", bold=True),
                Style(color="deep_sky_blue1", bold=True),
            ],
            "psy": [
                Style(color="magenta", bold=True),
                Style(color="purple", bold=True),
                Style(color="purple3", bold=True),
                Style(color="medium_purple", bold=True),
                Style(color="dark_magenta", bold=True),
            ],
            "divider": [
                Style(color="white", dim=True),
            ],
            "tagline": [
                Style(color="yellow", bold=True),
            ],
            "version": [
                Style(color="green", bold=True),
            ]
        }
    
    def create_animated_logo(self) -> Text:
        """Create the complete logo with rainbow animation effect."""
        logo_text = Text()
        
        for line_num, line in enumerate(self.logo_art):
            colored_line = Text()
            
            # Apply different color schemes based on line content
            if line_num < 5:  # AGENT part
                colors = self.color_schemes["ai"]
                color_index = line_num % len(colors)
            elif line_num < 7:  # Divider lines
                colors = self.color_schemes["divider"]
                color_index = 0
            elif line_num < 12:  # PSY part
                colors = self.color_schemes["psy"]
                color_index = (line_num - 7) % len(colors)
            elif line_num < 14:  # Divider lines
                colors = self.color_schemes["divider"]
                color_index = 0
            elif line_num == 14:  # LAB part
                # Special handling for LAB line
                colors = self.color_schemes["divider"]  # Use divider color for LAB
                color_index = 0
            elif line_num == 15:  # Tagline
                colors = self.color_schemes["tagline"]
                color_index = 0
            else:  # Default
                colors = self.color_schemes["ai"]
                color_index = line_num % len(colors)
            
            for char in line:
                if char != ' ':
                    colored_line.append(char, colors[color_index])
                else:
                    colored_line.append(char)
            
            logo_text.append(colored_line)
            logo_text.append("\n")
        
        return logo_text
    
    def create_gradient_logo(self) -> Text:
        """Create logo with gradient color effect."""
        logo_text = Text()
        
        for line_num, line in enumerate(self.logo_art):
            colored_line = Text()
            
            # Calculate gradient color based on position
            gradient_factor = line_num / max(len(self.logo_art) - 1, 1)
            
            # Interpolate between AI and PSY colors
            r = int(100 + 100 * gradient_factor)
            g = int(150 - 50 * gradient_factor)
            b = int(200 - 100 * gradient_factor)
            
            color = Style(color=f"rgb({r},{g},{b})", bold=True)
            
            for char in line:
                if char != ' ':
                    colored_line.append(char, style=color)
                else:
                    colored_line.append(char)
            
            logo_text.append(colored_line)
            logo_text.append("\n")
        
        return logo_text
    
    def create_cyberpunk_logo(self) -> Text:
        """Create cyberpunk-style logo with neon colors."""
        logo_text = Text()
        
        cyber_colors = [
            Style(color="bright_green", bold=True),  # Neon green
            Style(color="bright_cyan", bold=True),   # Electric blue
            Style(color="bright_magenta", bold=True), # Hot pink
            Style(color="bright_yellow", bold=True), # Electric yellow
            Style(color="bright_red", bold=True)     # Cyber red
        ]
        
        color_index = 0
        for line in self.logo_art:
            colored_line = Text()
            
            for char in line:
                if char != ' ':
                    colored_line.append(char, style=cyber_colors[color_index % len(cyber_colors)])
                else:
                    colored_line.append(char)
            
            logo_text.append(colored_line)
            logo_text.append("\n")
            color_index += 1
        
        return logo_text
    
    async def animate_typewriter_tui(self, log_callback, delay: float = 0.02):
        """Animate logo with typewriter effect for TUI display."""
        result_text = Text()
        
        for line in self.logo_art:
            line_text = Text()
            
            # Animate character by character
            for char in line:
                line_text.append(char)
                
                # Create panel for current progress
                panel_content = Text()
                panel_content.append(result_text)
                panel_content.append(line_text)
                
                panel = Panel(
                    Align.center(panel_content),
                    border_style="bright_cyan",
                    title="[bold magenta]AI PSY[/bold magenta]",
                    subtitle="[dim]Psychological AI System[/dim]"
                )
                
                # Call the logging callback to update the TUI
                log_callback(panel)
                await asyncio.sleep(delay)
            
            # Add the completed line to result
            result_text.append(line_text)
            result_text.append("\n")
    
    def display_instant(self, style: str = "gradient"):
        """Display logo instantly with specified style."""
        # Create logo based on style
        if style == "gradient":
            logo_text = self.create_gradient_logo()
        elif style == "cyberpunk":
            logo_text = self.create_cyberpunk_logo()
        else:  # default animated
            logo_text = self.create_animated_logo()
        
        # Create panel
        panel = Panel(
            Align.center(logo_text),
            border_style="bright_cyan",
            title="[bold cyan]AGENT PSY LAB[/bold cyan]",
            subtitle="[dim]Intelligent Agent Laboratory[/dim]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    async def display_animated(self, style: str = "typewriter", log_callback=None):
        """Display logo with animation."""
        if style == "typewriter":
            if log_callback:
                await self.animate_typewriter_tui(log_callback, delay=0.01)
            else:
                logo_text = self.create_gradient_logo()
                await self.animate_typewriter(logo_text, delay=0.01)
        else:
            # For other animations, display instantly for now
            self.display_instant(style)
    
    async def animate_typewriter(self, logo_text: Text, delay: float = 0.01):
        """Animate logo with typewriter effect."""
        lines = logo_text.plain.split('\n')
        for i, line in enumerate(lines):
            if i < len(lines) - 1:  # Skip empty last line if exists
                partial_line = Text(line)
                panel = Panel(
                    Align.center(partial_line),
                    border_style="bright_cyan",
                    title="[bold cyan]AGENT PSY LAB[/bold cyan]",
                    subtitle="[dim]Intelligent Agent Laboratory[/dim]"
                )
                self.console.clear()
                self.console.print(panel)
                await asyncio.sleep(delay)
    
    async def display_animated_tui(self, log_callback, style: str = "typewriter"):
        """Display logo with animation for TUI interface."""
        if style == "typewriter":
            await self.animate_typewriter_tui(log_callback, delay=0.01)
        else:
            # For other animations, display instantly
            self.display_instant(style)
            # Convert to TUI-friendly display
            logo_text = self.create_gradient_logo() if style == "gradient" else self.create_cyberpunk_logo()
            log_callback(Panel(
                Align.center(logo_text),
                border_style="bright_cyan",
                title="[bold cyan]AGENT PSY LAB[/bold cyan]",
                subtitle="[dim]Intelligent Agent Laboratory[/dim]"
            ))
    
    def get_logo_styles(self) -> list:
        """Get available logo styles."""
        return ["gradient", "cyberpunk", "animated", "typewriter"]
    
    async def animate_typewriter_tui(self, log_callback, delay: float = 0.02):
        """Animate logo with typewriter effect for TUI display."""
        result_text = Text()
        
        for line in self.logo_art:
            line_text = Text()
            
            # Animate character by character
            for char in line:
                line_text.append(char)
                
                # Create panel for current progress
                panel_content = Text()
                panel_content.append(result_text)
                panel_content.append(line_text)
                
                panel = Panel(
                    Align.center(panel_content),
                    border_style="bright_cyan",
                    title="[bold magenta]AI PSY[/bold magenta]",
                    subtitle="[dim]Psychological AI System[/dim]"
                )
                
                # Call the logging callback to update the TUI
                log_callback(panel)
                await asyncio.sleep(delay)
            
            # Add the completed line to result
            result_text.append(line_text)
            result_text.append("\n")