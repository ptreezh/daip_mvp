#!/usr/bin/env python3
"""Check dependency integrity and conflicts."""

import sys
import os
from pathlib import Path

def analyze_dependency_conflicts():
    """Analyze potential dependency conflicts between pyproject.toml and requirements.txt."""
    
    print("Analyzing dependency conflicts...")
    
    # Read pyproject.toml dependencies
    pyproject_deps = {}
    try:
        with open("pyproject.toml", 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Simple parsing for dependencies section
        in_deps = False
        for line in content.split('\n'):
            if '[tool.poetry.dependencies]' in line:
                in_deps = True
                continue
            if in_deps and line.strip().startswith('['):
                in_deps = False
                continue
            
            if in_deps and '=' in line and not line.strip().startswith('#') and line.strip():
                parts = line.split('=')
                if len(parts) >= 2:
                    package = parts[0].strip()
                    version = parts[1].strip().strip('"\'')
                    if package and version and not package.startswith('python'):
                        pyproject_deps[package] = version
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        return
    
    # Read requirements.txt dependencies
    requirements_deps = {}
    try:
        with open("requirements.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '==' in line:
                    parts = line.split('==')
                    if len(parts) >= 2:
                        package = parts[0].strip()
                        version = parts[1].strip()
                        requirements_deps[package] = version
    except Exception as e:
        print(f"Error reading requirements.txt: {e}")
        return
    
    print(f"Found {len(pyproject_deps)} dependencies in pyproject.toml")
    print(f"Found {len(requirements_deps)} dependencies in requirements.txt")
    
    # Check for conflicts
    conflicts = []
    common_packages = set(pyproject_deps.keys()) & set(requirements_deps.keys())
    
    for package in common_packages:
        pyproject_ver = pyproject_deps[package]
        requirements_ver = requirements_deps[package]
        
        if pyproject_ver != requirements_ver:
            conflicts.append({
                'package': package,
                'pyproject': pyproject_ver,
                'requirements': requirements_ver
            })
    
    if conflicts:
        print("\n⚠️  Dependency conflicts found:")
        for conflict in conflicts:
            print(f"  {conflict['package']}: pyproject.toml={conflict['pyproject']}, requirements.txt={conflict['requirements']}")
    else:
        print("\n✓ No dependency conflicts found between pyproject.toml and requirements.txt")
    
    # Check for missing packages
    missing_in_requirements = set(pyproject_deps.keys()) - set(requirements_deps.keys())
    missing_in_pyproject = set(requirements_deps.keys()) - set(pyproject_deps.keys())
    
    if missing_in_requirements:
        print("\n⚠️  Packages in pyproject.toml but missing in requirements.txt:")
        for package in sorted(missing_in_requirements):
            print(f"  {package}: {pyproject_deps[package]}")
    
    if missing_in_pyproject:
        print("\n⚠️  Packages in requirements.txt but missing in pyproject.toml:")
        for package in sorted(missing_in_pyproject):
            print(f"  {package}: {requirements_deps[package]}")

def check_critical_dependencies():
    """Check for critical dependencies that should be present."""
    
    print("\nChecking critical dependencies...")
    
    critical_deps = [
        'fastapi', 'uvicorn', 'pydantic', 'ollama', 'chromadb',
        'langchain', 'llama-index', 'sqlmodel', 'pytest'
    ]
    
    # Check pyproject.toml
    try:
        with open("pyproject.toml", 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
        missing_in_pyproject = []
        for dep in critical_deps:
            if f'"{dep}"' not in content and f"'{dep}'" not in content:
                missing_in_pyproject.append(dep)
        
        if missing_in_pyproject:
            print("⚠️  Critical dependencies missing in pyproject.toml:")
            for dep in missing_in_pyproject:
                print(f"  {dep}")
        else:
            print("✓ All critical dependencies found in pyproject.toml")
            
    except Exception as e:
        print(f"Error checking pyproject.toml: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Dependency Integrity Check")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    analyze_dependency_conflicts()
    check_critical_dependencies()
    
    print("\n" + "=" * 60)
    print("Dependency check completed.")
    print("=" * 60)