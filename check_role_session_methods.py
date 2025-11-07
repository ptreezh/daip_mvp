import sys
sys.path.insert(0, 'src')
from daip_live.tui import DAIP_TUI
tui = DAIP_TUI()
methods = [m for m in dir(tui) if 'role' in m.lower() or 'session' in m.lower()]
print('Role/Session methods:', sorted(methods))