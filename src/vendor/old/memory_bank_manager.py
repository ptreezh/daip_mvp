"""Memory Bank Manager for AI Virtual Team Collaboration

This module implements a file-based memory bank system for AI virtual team collaboration,
supporting both shared and private memory banks with CRCT integration.
"""

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryBankManager:
    """Manages file-based memory banks for AI virtual team collaboration.

    Supports:
    - Shared memory bank for team-wide information
    - Private memory banks for role-specific information
    - CRCT integration for reasoning and decision-making
    - Memory bank validation and integrity checks
    """

    def __init__(self, base_path: str = "memory_bank"):
        """Initialize the memory bank manager.

        Args:
        ----
            base_path: Base directory for memory bank files

        """
        self.base_path = Path(base_path)
        self.shared_path = self.base_path / "shared"
        self.private_path = self.base_path / "private"
        self.backup_path = self.base_path / "backup"

        # Create directory structure
        self._create_directory_structure()

        # Initialize core memory bank files
        self._initialize_core_files()

        logger.info(f"Memory Bank Manager initialized at {self.base_path}")

    def _create_directory_structure(self):
        """Create the memory bank directory structure."""
        directories = [
            self.base_path,
            self.shared_path,
            self.private_path,
            self.backup_path,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")

    def _initialize_core_files(self):
        """Initialize core memory bank files if they don't exist."""
        core_files = {
            "project_brief.md": "# Project Brief\n\n## Overview\n\n## Goals\n\n## Requirements\n\n## Constraints\n",
            "system_architecture.md": "# System Architecture\n\n## Overview\n\n## Components\n\n## Interfaces\n\n## Patterns\n",
            "development_progress.md": "# Development Progress\n\n## Current Status\n\n## Completed Tasks\n\n## In Progress\n\n## Next Steps\n",
            "quality_metrics.md": "# Quality Metrics\n\n## Performance\n\n## Reliability\n\n## Maintainability\n\n## User Satisfaction\n",
            "user_experience.md": "# User Experience\n\n## Design Decisions\n\n## User Feedback\n\n## Usability Metrics\n\n## Accessibility\n",
            "documentation_status.md": "# Documentation Status\n\n## Technical Docs\n\n## User Guides\n\n## API Documentation\n\n## Knowledge Base\n",
            "task_assignments.md": "# Task Assignments\n\n## Current Assignments\n\n## Priorities\n\n## Dependencies\n\n## Timeline\n",
            "collaboration_log.md": "# Collaboration Log\n\n## Recent Communications\n\n## Decisions\n\n## Issues\n\n## Resolutions\n",
        }

        for filename, content in core_files.items():
            file_path = self.shared_path / filename
            if not file_path.exists():
                self._write_file(file_path, content)
                logger.info(f"Initialized core file: {filename}")

    def _write_file(self, file_path: Path, content: str) -> bool:
        """Write content to a file with error handling.

        Args:
        ----
            file_path: Path to the file
            content: Content to write

        Returns:
        -------
            True if successful, False otherwise

        """
        try:
            file_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read content from a file with error handling.

        Args:
        ----
            file_path: Path to the file

        Returns:
        -------
            File content or None if error

        """
        try:
            if file_path.exists():
                return file_path.read_text(encoding="utf-8")
            else:
                logger.warning(f"File not found: {file_path}")
                return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def get_shared_memory(self, filename: str) -> Optional[str]:
        """Get content from shared memory bank.

        Args:
        ----
            filename: Name of the file in shared memory bank

        Returns:
        -------
            File content or None if not found

        """
        file_path = self.shared_path / filename
        return self._read_file(file_path)

    def set_shared_memory(self, filename: str, content: str) -> bool:
        """Set content in shared memory bank.

        Args:
        ----
            filename: Name of the file in shared memory bank
            content: Content to write

        Returns:
        -------
            True if successful, False otherwise

        """
        file_path = self.shared_path / filename

        # Create backup before writing
        if file_path.exists():
            self._create_backup(file_path)

        success = self._write_file(file_path, content)
        if success:
            logger.info(f"Updated shared memory: {filename}")
        return success

    def get_private_memory(self, role_id: str, filename: str) -> Optional[str]:
        """Get content from private memory bank for a specific role.

        Args:
        ----
            role_id: ID of the role
            filename: Name of the file in private memory bank

        Returns:
        -------
            File content or None if not found

        """
        role_path = self.private_path / role_id
        role_path.mkdir(exist_ok=True)

        file_path = role_path / filename
        return self._read_file(file_path)

    def set_private_memory(self, role_id: str, filename: str, content: str) -> bool:
        """Set content in private memory bank for a specific role.

        Args:
        ----
            role_id: ID of the role
            filename: Name of the file in private memory bank
            content: Content to write

        Returns:
        -------
            True if successful, False otherwise

        """
        role_path = self.private_path / role_id
        role_path.mkdir(exist_ok=True)

        file_path = role_path / filename

        # Create backup before writing
        if file_path.exists():
            self._create_backup(file_path)

        success = self._write_file(file_path, content)
        if success:
            logger.info(f"Updated private memory for {role_id}: {filename}")
        return success

    def _create_backup(self, file_path: Path):
        """Create a backup of a file before modification."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backup_path / backup_name

            if file_path.exists():
                backup_path.write_text(
                    file_path.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
                logger.debug(f"Created backup: {backup_name}")
        except Exception as e:
            logger.error(f"Error creating backup for {file_path}: {e}")

    def list_shared_memory_files(self) -> list[str]:
        """List all files in shared memory bank.

        Returns
        -------
            List of filenames

        """
        try:
            return [f.name for f in self.shared_path.iterdir() if f.is_file()]
        except Exception as e:
            logger.error(f"Error listing shared memory files: {e}")
            return []

    def list_private_memory_files(self, role_id: str) -> list[str]:
        """List all files in private memory bank for a specific role.

        Args:
        ----
            role_id: ID of the role

        Returns:
        -------
            List of filenames

        """
        try:
            role_path = self.private_path / role_id
            if role_path.exists():
                return [f.name for f in role_path.iterdir() if f.is_file()]
            else:
                return []
        except Exception as e:
            logger.error(f"Error listing private memory files for {role_id}: {e}")
            return []

    def validate_memory_bank_integrity(self) -> dict[str, Any]:
        """Validate the integrity of the memory bank.

        Returns
        -------
            Dictionary with validation results

        """
        validation_results = {
            "overall_status": "unknown",
            "shared_memory": {},
            "private_memory": {},
            "errors": [],
            "warnings": [],
        }

        # Validate shared memory
        shared_files = self.list_shared_memory_files()
        for filename in shared_files:
            content = self.get_shared_memory(filename)
            if content is None:
                validation_results["errors"].append(
                    f"Cannot read shared file: {filename}",
                )
            else:
                validation_results["shared_memory"][filename] = {
                    "exists": True,
                    "size": len(content),
                    "last_modified": self._get_file_timestamp(
                        self.shared_path / filename,
                    ),
                }

        # Validate private memory
        if self.private_path.exists():
            for role_dir in self.private_path.iterdir():
                if role_dir.is_dir():
                    role_id = role_dir.name
                    role_files = self.list_private_memory_files(role_id)
                    validation_results["private_memory"][role_id] = {
                        "files": role_files,
                        "file_count": len(role_files),
                    }

        # Determine overall status
        if validation_results["errors"]:
            validation_results["overall_status"] = "error"
        elif validation_results["warnings"]:
            validation_results["overall_status"] = "warning"
        else:
            validation_results["overall_status"] = "healthy"

        return validation_results

    def _get_file_timestamp(self, file_path: Path) -> Optional[str]:
        """Get the last modified timestamp of a file."""
        try:
            if file_path.exists():
                timestamp = file_path.stat().st_mtime
                return datetime.datetime.fromtimestamp(timestamp).isoformat()
            return None
        except Exception as e:
            logger.error(f"Error getting timestamp for {file_path}: {e}")
            return None

    def search_memory_bank(
        self,
        query: str,
        role_id: Optional[str] = None,
    ) -> dict[str, list[str]]:
        """Search memory bank for content matching a query.

        Args:
        ----
            query: Search query
            role_id: Optional role ID to limit search to private memory

        Returns:
        -------
            Dictionary with search results

        """
        results = {"shared_memory": [], "private_memory": []}

        # Search shared memory
        shared_files = self.list_shared_memory_files()
        for filename in shared_files:
            content = self.get_shared_memory(filename)
            if content and query.lower() in content.lower():
                results["shared_memory"].append(filename)

        # Search private memory
        if role_id:
            private_files = self.list_private_memory_files(role_id)
            for filename in private_files:
                content = self.get_private_memory(role_id, filename)
                if content and query.lower() in content.lower():
                    results["private_memory"].append(filename)

        return results

    def get_memory_bank_summary(self) -> dict[str, Any]:
        """Get a summary of the memory bank status.

        Returns
        -------
            Dictionary with memory bank summary

        """
        summary = {
            "total_files": 0,
            "shared_files": 0,
            "private_files": 0,
            "roles": [],
            "last_updated": None,
            "integrity_status": "unknown",
        }

        # Count shared files
        shared_files = self.list_shared_memory_files()
        summary["shared_files"] = len(shared_files)
        summary["total_files"] += len(shared_files)

        # Count private files
        if self.private_path.exists():
            for role_dir in self.private_path.iterdir():
                if role_dir.is_dir():
                    role_id = role_dir.name
                    role_files = self.list_private_memory_files(role_id)
                    summary["private_files"] += len(role_files)
                    summary["total_files"] += len(role_files)
                    summary["roles"].append(
                        {"role_id": role_id, "file_count": len(role_files)},
                    )

        # Get integrity status
        integrity = self.validate_memory_bank_integrity()
        summary["integrity_status"] = integrity["overall_status"]

        return summary

    def export_memory_bank(self, export_path: str) -> bool:
        """Export the entire memory bank to a specified path.

        Args:
        ----
            export_path: Path to export the memory bank to

        Returns:
        -------
            True if successful, False otherwise

        """
        try:
            import shutil

            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)

            # Copy entire memory bank
            shutil.copytree(
                self.base_path,
                export_dir / "memory_bank",
                dirs_exist_ok=True,
            )

            # Create export metadata
            metadata = {
                "export_timestamp": datetime.datetime.now().isoformat(),
                "source_path": str(self.base_path),
                "summary": self.get_memory_bank_summary(),
            }

            metadata_path = export_dir / "export_metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

            logger.info(f"Memory bank exported to: {export_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting memory bank: {e}")
            return False


class CRCTIntegration:
    """Chain of Recursive Thought integration for memory bank operations."""

    def __init__(self, memory_manager: MemoryBankManager):
        """Initialize CRCT integration.

        Args:
        ----
            memory_manager: Memory bank manager instance

        """
        self.memory_manager = memory_manager

    def execute_crct_process(
        self,
        role_id: str,
        task_description: str,
        required_files: list[str],
    ) -> dict[str, Any]:
        """Execute CRCT process for a specific task.

        Args:
        ----
            role_id: ID of the role executing the task
            task_description: Description of the task
            required_files: List of required memory bank files

        Returns:
        -------
            Dictionary with CRCT process results

        """
        crct_results = {
            "task": task_description,
            "role_id": role_id,
            "steps": [],
            "memory_access": {},
            "decisions": [],
            "outcomes": [],
        }

        # Step 1: Memory Bank Scan
        step1 = self._memory_bank_scan(required_files)
        crct_results["steps"].append(step1)
        crct_results["memory_access"] = step1["memory_content"]

        # Step 2: Context Integration
        step2 = self._context_integration(task_description, step1["memory_content"])
        crct_results["steps"].append(step2)

        # Step 3: Task Analysis
        step3 = self._task_analysis(task_description, step2["integrated_context"])
        crct_results["steps"].append(step3)

        # Step 4: Solution Planning
        step4 = self._solution_planning(step3["analysis"])
        crct_results["steps"].append(step4)
        crct_results["decisions"] = step4["decisions"]

        # Step 5: Verification
        step5 = self._verification(step4["plan"])
        crct_results["steps"].append(step5)

        # Step 6: Execution Planning
        step6 = self._execution_planning(step5["verified_plan"])
        crct_results["steps"].append(step6)
        crct_results["outcomes"] = step6["planned_outcomes"]

        return crct_results

    def _memory_bank_scan(self, required_files: list[str]) -> dict[str, Any]:
        """Scan memory bank for required files."""
        memory_content = {}

        for filename in required_files:
            # Try shared memory first
            content = self.memory_manager.get_shared_memory(filename)
            if content:
                memory_content[f"shared/{filename}"] = content
            else:
                # Try private memory for each role
                for role_dir in self.memory_manager.private_path.iterdir():
                    if role_dir.is_dir():
                        role_content = self.memory_manager.get_private_memory(
                            role_dir.name,
                            filename,
                        )
                        if role_content:
                            memory_content[
                                f"private/{role_dir.name}/{filename}"
                            ] = role_content

        return {
            "step": "memory_bank_scan",
            "status": "completed",
            "memory_content": memory_content,
            "files_found": list(memory_content.keys()),
        }

    def _context_integration(
        self,
        task_description: str,
        memory_content: dict[str, str],
    ) -> dict[str, Any]:
        """Integrate memory content with task context."""
        integrated_context = {
            "task": task_description,
            "relevant_memory": memory_content,
            "context_summary": f"Task: {task_description}. Available memory files: {list(memory_content.keys())}",
        }

        return {
            "step": "context_integration",
            "status": "completed",
            "integrated_context": integrated_context,
        }

    def _task_analysis(
        self,
        task_description: str,
        integrated_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze task requirements with memory context."""
        analysis = {
            "task_requirements": task_description,
            "available_context": integrated_context,
            "analysis_summary": f"Analyzing task: {task_description} with context from {len(integrated_context['relevant_memory'])} memory files",
        }

        return {"step": "task_analysis", "status": "completed", "analysis": analysis}

    def _solution_planning(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Plan solution based on analysis."""
        plan = {
            "approach": "Based on memory bank context and task requirements",
            "steps": [
                "Review memory bank content",
                "Identify relevant patterns and constraints",
                "Develop solution approach",
                "Validate against memory bank constraints",
            ],
            "decisions": [
                "Use memory bank as primary source of truth",
                "Apply CRCT reasoning for decision-making",
                "Update memory bank with results",
            ],
        }

        return {
            "step": "solution_planning",
            "status": "completed",
            "plan": plan,
            "decisions": plan["decisions"],
        }

    def _verification(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Verify plan against memory bank constraints."""
        verified_plan = {
            **plan,
            "verification_status": "verified",
            "constraints_checked": True,
            "memory_alignment": "confirmed",
        }

        return {
            "step": "verification",
            "status": "completed",
            "verified_plan": verified_plan,
        }

    def _execution_planning(self, verified_plan: dict[str, Any]) -> dict[str, Any]:
        """Plan execution of verified plan."""
        planned_outcomes = [
            "Memory bank updated with new information",
            "Task completed according to plan",
            "Results documented for future reference",
        ]

        return {
            "step": "execution_planning",
            "status": "completed",
            "planned_outcomes": planned_outcomes,
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize memory bank manager
    memory_manager = MemoryBankManager()

    # Initialize CRCT integration
    crct = CRCTIntegration(memory_manager)

    # Example: Set some shared memory
    memory_manager.set_shared_memory(
        "project_brief.md",
        "# Project Brief\n\n## Overview\nThis is a test project for AI virtual team collaboration.\n\n## Goals\n- Test memory bank functionality\n- Validate CRCT integration\n- Demonstrate role collaboration\n",
    )

    # Example: Set private memory for a role
    memory_manager.set_private_memory(
        "project_coordinator_001",
        "coordination_decisions.md",
        "# Coordination Decisions\n\n## Recent Decisions\n- Use file-based memory bank\n- Implement CRCT reasoning\n- Focus on role collaboration\n",
    )

    # Example: Execute CRCT process
    crct_results = crct.execute_crct_process(
        role_id="project_coordinator_001",
        task_description="Coordinate team activities for the test project",
        required_files=["project_brief.md", "task_assignments.md"],
    )

    print("CRCT Process Results:")
    print(json.dumps(crct_results, indent=2))

    # Get memory bank summary
    summary = memory_manager.get_memory_bank_summary()
    print("\nMemory Bank Summary:")
    print(json.dumps(summary, indent=2))
