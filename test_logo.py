#!/usr/bin/env python3
"""
AGENTPSY Logo Test Script

Test the ASCII art logo display with different styles and animations.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from daip_live.tui_logo import PersonalAILogo
import pytest


@pytest.mark.asyncio
async def test_logo_styles():
    logo = PersonalAILogo()
    
    print("=" * 60)
    print("AGENTPSY Logo Style Test")
    print("=" * 60)
    
    # Test instant styles
    styles = ["gradient", "cyberpunk"]
    
    for style in styles:
        print(f"\n--- Testing {style.upper()} style ---")
        logo.display_instant(style)
        print("Style displayed. Continuing...")
    
    # Test animated styles
    print(f"\n--- Testing TYPEWRITER animation ---")
    await logo.display_animated("typewriter")
    
    print("\n" + "=" * 60)
    print("Logo test completed!")
    print("=" * 60)


def test_logo_in_console():
    """Test logo display in regular console."""
    logo = PersonalAILogo()
    
    print("Testing logo in console environment...")
    logo.display_instant("gradient")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        test_logo_in_console()
    else:
        asyncio.run(test_logo_styles())