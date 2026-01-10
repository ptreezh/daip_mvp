from src.daip_live.tui_modular import DAIP_TUI
import sys

print('TUI class imports successfully', file=sys.stdout)
tui = DAIP_TUI()
print('TUI instance created successfully', file=sys.stdout)
print('TUI type:', type(tui).__name__, file=sys.stdout)