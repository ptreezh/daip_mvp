import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Test the autocomplete functionality
try:
    from src.daip_live.tui import DAIP_TUI
    import asyncio
    
    # Create a mock TUI instance
    tui = DAIP_TUI()
    
    # Test doc command autocomplete
    print("Testing /doc command autocomplete:")
    suggestions = tui._get_autocomplete_suggestions("/doc")
    print(f"  /doc -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc ")
    print(f"  /doc  -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc f")
    print(f"  /doc f -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc e")
    print(f"  /doc e -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc export")
    print(f"  /doc export -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc export ")
    print(f"  /doc export  -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc export -")
    print(f"  /doc export - -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc export --to")
    print(f"  /doc export --to -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc export --to ")
    print(f"  /doc export --to  -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/doc export --to p")
    print(f"  /doc export --to p -> {suggestions}")
    
    # Test wiki command autocomplete
    print("\nTesting /wiki command autocomplete:")
    suggestions = tui._get_autocomplete_suggestions("/wiki")
    print(f"  /wiki -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/wiki ")
    print(f"  /wiki  -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/wiki n")
    print(f"  /wiki n -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/wiki l")
    print(f"  /wiki l -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/wiki o")
    print(f"  /wiki o -> {suggestions}")
    
    suggestions = tui._get_autocomplete_suggestions("/wiki s")
    print(f"  /wiki s -> {suggestions}")
    
    print("\nAutocomplete testing completed successfully!")
    
except Exception as e:
    print(f"Error during autocomplete testing: {e}")
    import traceback
    traceback.print_exc()