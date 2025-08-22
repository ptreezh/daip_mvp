# -*- coding: utf-8 -*-
"""@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : __init__.py
@Description: Wiki management commands for the DAIP-LIVE CLI.
"""

import typer

# --- App Definitions ---
app = typer.Typer(help="Wiki management commands for DAIP-LIVE.")

# Sub-app for collaborative features
collaborate_app = typer.Typer(help="Collaborative wiki features.")
app.add_typer(collaborate_app, name="collaborate")

# Sub-app for proposal management
proposal_app = typer.Typer(help="Edit proposal management.")
app.add_typer(proposal_app, name="proposal")

# Import and register all command modules
from . import basic_commands
from . import collaborate_commands
from . import proposal_commands

# Register basic commands
app.add_typer(basic_commands.app, name="")

# Register collaborate commands
app.add_typer(collaborate_commands.app, name="collaborate")

# Register proposal commands
app.add_typer(proposal_commands.app, name="proposal")