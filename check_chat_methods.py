import sys
sys.path.insert(0, 'src')
from daip_live.tui import DAIP_TUI
tui = DAIP_TUI()
methods = [m for m in dir(tui) if 'chat' in m.lower()]
print('Chat-related methods:', methods)