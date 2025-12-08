#!/usr/bin/env python3
"""
Script to fix Ollama blob path structure
"""

import os
import shutil
from pathlib import Path

def fix_blob_structure():
    """Fix the blob directory structure from flat to hierarchical"""

    blobs_dir = Path("C:/Users/Zhang/.ollama/models/blobs")
    sha256_dir = blobs_dir / "sha256"

    # Create sha256 subdirectory if it doesn't exist
    sha256_dir.mkdir(exist_ok=True)

    moved_count = 0
    already_correct = 0
    errors = 0

    print("Fixing Ollama blob path structure...")
    print("=" * 50)

    # Find all blob files in the flat structure
    for blob_file in blobs_dir.iterdir():
        if blob_file.is_file() and blob_file.name.startswith("sha256-"):
            original_path = blob_file
            filename = blob_file.name[7:]  # Remove 'sha256-' prefix
            target_path = sha256_dir / filename

            if target_path.exists():
                print(f"⚠ {target_path.name} already exists, skipping...")
                already_correct += 1
                continue

            try:
                # Move file to correct location
                shutil.move(str(original_path), str(target_path))
                print(f"✓ Moved: {original_path.name} -> sha256/{filename}")
                moved_count += 1
            except Exception as e:
                print(f"✗ Error moving {original_path.name}: {e}")
                errors += 1

    print(f"\nSummary:")
    print(f"  Files moved: {moved_count}")
    print(f"  Already correct: {already_correct}")
    print(f"  Errors: {errors}")

    return moved_count > 0

def verify_fix():
    """Verify that models are now accessible"""
    print("\nVerifying model access...")

    import subprocess

    models_to_check = [
        "deepseek-coder:6.7b",
        "qwen:7b-chat",
        "mistral:instruct",
        "gemma:2b",
        "yi:6b"
    ]

    working_models = []

    for model in models_to_check:
        try:
            result = subprocess.run(['ollama', 'show', model],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                working_models.append(model)
                print(f"✓ {model} - Working")
            else:
                print(f"✗ {model} - Not found")
        except Exception as e:
            print(f"✗ {model} - Error: {e}")

    if working_models:
        print(f"\n🎉 Success! {len(working_models)} models are now working:")
        for model in working_models:
            print(f"  - {model}")
    else:
        print("\n❌ No models are working yet. May need further investigation.")

if __name__ == "__main__":
    print("Ollama Blob Path Structure Fixer")
    print("=" * 50)

    # Show current status
    print("Current working models:")
    os.system("ollama list 2>nul")
    print()

    # Fix the structure
    if fix_blob_structure():
        print("\nPath structure fixed. Restarting Ollama service...")
        # Restart Ollama to reindex
        os.system("powershell -Command \"Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue\"")
        import time
        time.sleep(3)

        # Start Ollama again
        print("Starting Ollama service...")
        os.startfile("C:\\Users\\Zhang\\AppData\\Local\\Programs\\Ollama\\ollama.exe")
        time.sleep(5)

        # Verify fix
        verify_fix()

        print("\nFinal model list:")
        os.system("ollama list 2>nul")
    else:
        print("No files needed moving. The structure might already be correct.")
        verify_fix()