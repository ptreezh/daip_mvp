"""
Command Parser for newP6 TUI

Implements command parsing logic following TDD approach.
"""

import shlex
from typing import List, Dict, Any, Optional

from .models import Command


class CommandParser:
    """Parses raw command strings into Command objects"""

    def parse(self, command_str: str) -> Command:
        """Parse a command string into a Command object"""
        # Handle empty/whitespace commands
        if not command_str or command_str.strip() == "":
            return Command(raw=command_str, command="")

        # Use shlex to handle quoted arguments properly
        try:
            tokens = shlex.split(command_str.strip())
        except ValueError:
            # Fallback to simple split if shlex fails
            tokens = command_str.strip().split()

        if not tokens:
            return Command(raw=command_str, command="")

        # Parse command and action
        command = tokens[0]
        action = None
        args_start = 1

        # Check if there's an action (second token that's not an option)
        if len(tokens) > 1 and not tokens[1].startswith("--"):
            action = tokens[1]
            args_start = 2

        # Parse arguments and options
        args = []
        options = {}
        i = args_start

        while i < len(tokens):
            token = tokens[i]
            if token.startswith("--"):
                # Handle option
                if "=" in token:
                    # Option with value: --option=value
                    key, value = token[2:].split("=", 1)
                    options[key] = value
                elif i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                    # Option with separate value: --option value
                    key = token[2:]
                    value = tokens[i + 1]
                    options[key] = value
                    i += 1  # Skip the value
                else:
                    # Boolean option: --flag
                    key = token[2:]
                    options[key] = True
            else:
                # Regular argument
                args.append(token)
            i += 1

        return Command(
            raw=command_str,
            command=command,
            action=action,
            args=args,
            options=options
        )