#!/usr/bin/env python3
"""
Script to clean broken Ollama models (manifests without corresponding blobs)
"""

import os
import json
import shutil
from pathlib import Path

def check_model_blobs(manifest_path):
    """Check if all blobs referenced by a manifest exist"""
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except Exception as e:
        return False, f"Invalid manifest: {e}"

    blobs_dir = Path("C:/Users/Zhang/.ollama/models/blobs")

    # Check config blob
    config_digest = manifest.get('config', {}).get('digest', '')
    if config_digest:
        config_path = blobs_dir / config_digest.replace(':', '/')
        if not config_path.exists():
            return False, f"Missing config blob: {config_digest}"

    # Check layer blobs
    for layer in manifest.get('layers', []):
        layer_digest = layer.get('digest', '')
        if layer_digest:
            layer_path = blobs_dir / layer_digest.replace(':', '/')
            if not layer_path.exists():
                return False, f"Missing layer blob: {layer_digest}"

    return True, "All blobs present"

def clean_broken_models():
    """Remove models with missing blobs"""
    manifests_dir = Path("C:/Users/Zhang/.ollama/models/manifests/registry.ollama.ai/library")
    removed_count = 0
    kept_count = 0

    if not manifests_dir.exists():
        print("Manifests directory not found!")
        return

    print("Checking models for missing blobs...")

    for library in manifests_dir.iterdir():
        if not library.is_dir():
            continue

        for version in library.iterdir():
            if not version.is_file():
                continue

            model_name = f"{library.name}:{version.name}"
            is_complete, message = check_model_blobs(version)

            if is_complete:
                print(f"✓ {model_name} - {message}")
                kept_count += 1
            else:
                print(f"✗ {model_name} - {message}")
                # Ask user before removing
                response = input(f"  Remove broken model {model_name}? (y/n): ").lower()
                if response in ['y', 'yes']:
                    version.unlink()
                    print(f"  Removed: {version}")
                    removed_count += 1

                    # Remove library directory if empty
                    try:
                        library.rmdir()  # Only works if directory is empty
                    except OSError:
                        pass  # Directory not empty, that's fine
                else:
                    print(f"  Kept: {model_name}")
                    kept_count += 1

    print(f"\nSummary:")
    print(f"  Models kept: {kept_count}")
    print(f"  Models removed: {removed_count}")

def list_current_state():
    """List current working models"""
    print("Current working models:")
    result = os.system("ollama list 2>nul")
    if result != 0:
        print("No working models found or Ollama not responding")

if __name__ == "__main__":
    print("Ollama Broken Model Cleaner")
    print("=" * 40)

    list_current_state()
    print()

    clean_broken_models()
    print()

    print("Final state:")
    list_current_state()