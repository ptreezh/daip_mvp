"""Utilities for robust path resolution in the DAIP system."""

import os
from pathlib import Path
from typing import Optional


def find_roles_directory(roles_dir: str = "roles", start_path: Optional[str] = None) -> Optional[Path]:
    """
    Find the roles directory using multiple search strategies.
    
    Args:
        roles_dir: The name of the roles directory (default "roles")
        start_path: Path to start searching from (default: current working directory)
        
    Returns:
        Path object pointing to the roles directory, or None if not found
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)
    
    # Strategy 1: Check if provided path is already absolute and exists
    if start_path.is_absolute() and start_path.exists() and start_path.is_dir():
        return start_path

    # Strategy 2: Check common project structures relative to current working directory
    search_paths = [
        # Direct from current dir
        start_path / roles_dir,
        
        # From common project roots (relative to current dir)
        start_path / roles_dir,
        start_path / "src" / "daip_live" / roles_dir,
        start_path / "daip_live" / roles_dir,
        start_path / "src" / roles_dir,
        
        # Common development paths
        start_path.parent / roles_dir,  # parent directory
        start_path.parent / "src" / "daip_live" / roles_dir,
        start_path.parent.parent / roles_dir,  # 2 levels up
        start_path.parent.parent / "src" / "daip_live" / roles_dir,
        start_path.parent.parent.parent / roles_dir,  # 3 levels up
        start_path.parent.parent.parent / "src" / "daip_live" / roles_dir,
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_search_paths = []
    for path in search_paths:
        abs_path = path.resolve()
        if abs_path not in seen:
            seen.add(abs_path)
            unique_search_paths.append(path)
    
    # Check each path in order
    for path in unique_search_paths:
        try:
            resolved_path = path.resolve()
            if resolved_path.exists() and resolved_path.is_dir():
                return resolved_path
        except (OSError, RuntimeError):
            # Skip paths that can't be resolved (e.g. due to permissions or circular symlinks)
            continue
    
    # If none found, return None to indicate directory doesn't exist
    return None


def ensure_roles_directory(roles_dir: str = "roles", start_path: Optional[str] = None) -> Path:
    """
    Ensure the roles directory exists, creating it if necessary.
    
    Args:
        roles_dir: The name of the roles directory (default "roles")
        start_path: Path to start searching from (default: current working directory)
        
    Returns:
        Path object pointing to the roles directory
    """
    if start_path is None:
        start_path = Path.cwd()
    
    # First, try to find existing directory
    found_path = find_roles_directory(roles_dir, start_path)
    if found_path:
        return found_path
    
    # If not found, create it in the most sensible location
    # Try in current working directory first
    try:
        new_path = Path(start_path) / roles_dir
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path
    except Exception:
        # If that fails, try relative to this file's location
        try:
            script_path = Path(__file__).resolve().parent
            new_path = script_path / ".." / ".." / roles_dir
            new_path = new_path.resolve()
            new_path.mkdir(parents=True, exist_ok=True)
            return new_path
        except Exception:
            # Last resort: create in temp directory
            import tempfile
            temp_roles_path = Path(tempfile.mkdtemp()) / roles_dir
            temp_roles_path.mkdir(exist_ok=True)
            return temp_roles_path


def find_project_root(marker_files: list = None) -> Optional[Path]:
    """
    Find the project root directory by looking for marker files/directories.
    
    Args:
        marker_files: List of files/directories that indicate project root.
                     Defaults to common markers like 'pyproject.toml', 'setup.py', etc.
        
    Returns:
        Path object pointing to the project root, or None if not found
    """
    if marker_files is None:
        marker_files = [
            'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt',
            'Pipfile', 'poetry.lock', 'package.json', 'Cargo.toml',
            '.git', '.hg', 'README.md', 'README.rst', 'README.txt'
        ]
    
    current_path = Path.cwd().resolve()
    
    # Walk up the directory tree looking for marker files
    for parent in [current_path] + list(current_path.parents):
        for marker in marker_files:
            if (parent / marker).exists():
                return parent
    
    # If we get to root without finding markers, return None
    return None


def get_configured_roles_path(configured_roles_dir: str = "roles") -> Path:
    """
    Get the roles directory path using a robust resolution strategy.
    
    Args:
        configured_roles_dir: The configured roles directory path
        
    Returns:
        Path object pointing to the roles directory
    """
    # If it's already an absolute path and exists, use it
    abs_path = Path(configured_roles_dir).resolve()
    if abs_path.is_absolute() and abs_path.exists() and abs_path.is_dir():
        return abs_path
    
    # Try to find it using our search strategies
    search_result = find_roles_directory(configured_roles_dir)
    if search_result:
        return search_result
    
    # If not found, ensure it's created in a sensible location
    return ensure_roles_directory(configured_roles_dir)


if __name__ == "__main__":
    # Test the path resolution functions
    print("Testing path resolution functions...")
    
    print(f"Current working directory: {Path.cwd()}")
    
    # Test finding roles directory
    roles_path = find_roles_directory()
    if roles_path:
        print(f"Found roles directory: {roles_path}")
    else:
        print("Roles directory not found, would be created")
        roles_path = ensure_roles_directory()
        print(f"Ensured roles directory: {roles_path}")
    
    # Test finding project root
    project_root = find_project_root()
    if project_root:
        print(f"Found project root: {project_root}")
    else:
        print("Could not determine project root")
    
    print("Path resolution test completed.")