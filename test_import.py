try:
    import daip_live.tui
    print("Import successful")
    print("_highlight_code_and_json" in dir(daip_live.tui.DAIP_TUI))
except Exception as e:
    print("Import failed:", e)
    import traceback
    traceback.print_exc()