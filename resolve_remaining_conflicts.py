import os
import subprocess
import sys

# List of files with conflicts (obtained from previous findstr command)
files_with_conflicts = [
    "src/core_services/api_contract_generator.py",
    "src/core_services/git_version_release_system.py",
    "src/core_services/integration_test_algorithm_registry.py",
    "src/core_services/integration_test_consensus_models.py",
    "src/core_services/run_knowledge_tests.py",
    "src/core_services/test_algorithm_registry.py",
    "src/core_services/test_algorithm_selector.py",
    "src/core_services/test_consensus_models.py",
    "src/core_services/test_dispatcher_simple.py",
    "src/core_services/test_fallback_manager.py",
    "src/core_services/test_fallback_manager_simple.py",
    "src/core_services/test_knowledge_integration.py",
    "src/core_services/test_knowledge_lifecycle.py",
    "src/core_services/test_unified_consensus_dispatcher.py",
    "src/debate_system/comprehensive_test_suite.py",
    "src/debate_system/tests/test_multi_role_dialogue_integration.py",
    "src/debate_system/test_web_interface.py",
    "src/institutional_primitives/test_custom_primitive_creation.py",
    "src/institutional_primitives/test_role_consensus_customization.py",
    "src/real_demo_system/test_memory_interface.py",
    "src/real_demo_system/test_real_demo_system.py",
]

def file_has_conflict_markers(file_path):
    """Check if a file contains conflict markers."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return "<<<<<<< HEAD" in content or "=======" in content or ">>>>>>> " in content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def restore_file_from_commit(file_path, commit):
    """Restore a file from a specific commit."""
    try:
        subprocess.run(["git", "checkout", commit, "--", file_path], check=True, capture_output=True)
        print(f"Restored {file_path} from {commit}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to restore {file_path} from {commit}: {e}")
        return False

def main():
    # Get the list of files that have conflicts
    files_to_process = []
    
    # Check if files in the list actually have conflicts
    for file_path in files_with_conflicts:
        if file_has_conflict_markers(file_path):
            files_to_process.append(file_path)
    
    print(f"Found {len(files_to_process)} files with conflicts.")
    
    # Try to restore each file from fa881da
    commit = "fa881da"
    restored_files = []
    failed_files = []
    
    for file_path in files_to_process:
        print(f"Processing {file_path}...")
        if restore_file_from_commit(file_path, commit):
            restored_files.append(file_path)
        else:
            failed_files.append(file_path)
    
    print(f"\nRestored {len(restored_files)} files from {commit}.")
    print(f"Failed to restore {len(failed_files)} files from {commit}.")
    
    # Add restored files to git
    if restored_files:
        try:
            subprocess.run(["git", "add"] + restored_files, check=True, capture_output=True)
            print("Added restored files to git.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to add restored files to git: {e}")
    
    # Print failed files for manual handling
    if failed_files:
        print("\nFiles that failed to restore (need manual conflict resolution):")
        for file_path in failed_files:
            print(f"  {file_path}")

if __name__ == "__main__":
    main()