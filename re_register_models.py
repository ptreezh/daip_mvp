#!/usr/bin/env python3
"""
Script to re-register Ollama models from manifest files
"""

import os
import json
import shutil
from pathlib import Path

def find_models():
    """Find all model manifests in the Ollama directory"""
    base_path = Path("C:/Users/Zhang/.ollama/models/manifests/registry.ollama.ai/library")
    models = []

    if not base_path.exists():
        print(f"Ollama manifests directory not found: {base_path}")
        return models

    for library in base_path.iterdir():
        if library.is_dir():
            for version in library.iterdir():
                if version.is_file() and version.name != '':  # Avoid empty names
                    model_name = f"{library.name}:{version.name}"
                    models.append({
                        'name': model_name,
                        'library': library.name,
                        'version': version.name,
                        'manifest_path': str(version)
                    })

    return models

def backup_manifests():
    """Backup current manifests"""
    backup_dir = Path("C:/Users/Zhang/.ollama/models/manifests_backup")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    manifests_dir = Path("C:/Users/Zhang/.ollama/models/manifests")
    if manifests_dir.exists():
        shutil.copytree(manifests_dir, backup_dir)
        print(f"Backed up manifests to {backup_dir}")

def main():
    print("Ollama Model Re-registration Tool")
    print("=" * 40)

    # Find all models
    models = find_models()
    print(f"Found {len(models)} model manifests:")

    for model in models:
        print(f"  - {model['name']}")

    # Check if models are accessible
    print("\nTesting model access...")
    import subprocess

    working_models = []
    broken_models = []

    for model in models:
        try:
            result = subprocess.run(['ollama', 'show', model['name']],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                working_models.append(model['name'])
                print(f"✓ {model['name']} - Working")
            else:
                broken_models.append(model)
                print(f"✗ {model['name']} - Not found")
        except Exception as e:
            broken_models.append(model)
            print(f"✗ {model['name']} - Error: {e}")

    print(f"\nSummary:")
    print(f"  Working models: {len(working_models)}")
    print(f"  Broken models: {len(broken_models)}")

    if broken_models:
        print(f"\nBroken models (manifests exist but not accessible):")
        for model in broken_models:
            print(f"  - {model['name']}")
            print(f"    Path: {model['manifest_path']}")

            # Try to read the manifest to see if it's valid
            try:
                with open(model['manifest_path'], 'r') as f:
                    manifest = json.load(f)
                print(f"    Manifest valid: ✓")
            except Exception as e:
                print(f"    Manifest valid: ✗ ({e})")

if __name__ == "__main__":
    main()