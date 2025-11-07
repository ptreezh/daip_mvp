import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Try to run CLI directly
try:
    from daip_live.cli import app
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    # Capture output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    print("Running CLI help command...")
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        try:
            app(['--help'])
        except SystemExit:
            pass  # Typer uses SystemExit, which is normal
    
    stdout_result = stdout_capture.getvalue()
    stderr_result = stderr_capture.getvalue()
    
    print("STDOUT:")
    print(stdout_result)
    print("STDERR:")
    print(stderr_result)
    
except Exception as e:
    print(f"Error running CLI: {e}")
    import traceback
    traceback.print_exc()