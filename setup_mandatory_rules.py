#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 15:00:00
@Author  : DAIP-LIVE Team
@File    : setup_mandatory_rules.py
@Description:
    One-time setup script for mandatory rules system.
    Installs pre-commit hooks and validates environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[SETUP] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        print(f"[ERROR] Output: {e.output}")
        return False


def check_requirements():
    """Check if required tools are available"""
    print("[SETUP] Checking requirements...")
    
    required_tools = ["python", "black", "ruff", "mypy", "pre-commit"]
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"[ERROR] Missing required tools: {', '.join(missing_tools)}")
        print("[ERROR] Please install missing tools with:")
        print("  pip install black ruff mypy pre-commit")
        return False
    
    print("[SUCCESS] All required tools are available")
    return True


def setup_pre_commit():
    """Set up pre-commit hooks"""
    print("[SETUP] Setting up pre-commit hooks...")
    
    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False
    
    # Validate pre-commit configuration
    if not run_command("pre-commit run --all-files", "Validating pre-commit configuration"):
        print("[WARNING] Pre-commit validation failed - this is expected if rules are not met")
    
    return True


def create_quick_reference():
    """Create a quick reference guide"""
    quick_ref = """# DAIP-LIVE Mandatory Rules - Quick Reference

## Daily Commands
```bash
# Validate before committing
python mandatory_rules_checker.py

# Quick format check
black --check src/ tests/

# Quick lint check
ruff check src/ tests/

# Quick type check
mypy src/

# Run tests
pytest
```

## Commit Workflow
1. Make changes
2. Run `python mandatory_rules_checker.py`
3. Fix any violations
4. Run tests
5. Commit: `git commit -m "message"`
6. Pre-commit hooks run automatically
7. If violations found, fix them and try again

## Common Fixes
- Format code: `black src/ tests/`
- Fix linting: `ruff check --fix src/ tests/`
- Add type hints (based on MyPy output)
- Add file headers (see CLAUDE.md for template)

## Getting Help
- Full docs: docs/MANDATORY_RULES.md
- Report: mandatory_rules_report.json
- Team: Ask for help with rule violations
"""
    
    with open("MANDATORY_RULES_QUICK_REF.md", "w", encoding="utf-8") as f:
        f.write(quick_ref)
    
    print("[SUCCESS] Created quick reference guide: MANDATORY_RULES_QUICK_REF.md")
    return True


def main():
    """Main setup function"""
    print("=" * 60)
    print("[SETUP] DAIP-LIVE Mandatory Rules System Setup")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("[ERROR] Setup failed - missing requirements")
        sys.exit(1)
    
    # Setup pre-commit
    if not setup_pre_commit():
        print("[ERROR] Setup failed - pre-commit configuration")
        sys.exit(1)
    
    # Create quick reference
    create_quick_reference()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Mandatory rules system setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Read MANDATORY_RULES_QUICK_REF.md for daily commands")
    print("2. Read docs/MANDATORY_RULES.md for full documentation")
    print("3. Run 'python mandatory_rules_checker.py' to validate current state")
    print("4. Fix any violations before committing")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    main()