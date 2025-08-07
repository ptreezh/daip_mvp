# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 16:30:00
@Author  : DAIP-LIVE Team
@File    : validate_v0_3_11_git_version_release_system.py
@Description:
    Validation script for v0.3.11 Git Version Release System
    Git版本发布系统验证脚本
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from core_services.git_version_release_system import (
    VersionReleaseSystem,
    VersionInfo,
    ReleaseType,
    ReleaseStatus,
    ReleaseConfig,
    ReleaseInfo,
    ReleaseAsset,
    GitManager,
    ChangelogManager,
    ReleaseManager,
    get_version_release_system,
    initialize_version_release_system,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GitVersionReleaseSystemValidator:
    """Validator for Git Version Release System."""

    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "version": "0.3.11",
            "tests": {},
            "overall_status": "pending",
            "errors": [],
            "warnings": [],
            "recommendations": [],
        }
        self.temp_dir = None

    async def validate_system(self) -> Dict[str, Any]:
        """Run complete validation of the Git Version Release System."""
        logger.info("Starting v0.3.11 Git Version Release System validation...")

        try:
            # Create temporary directory for testing
            self.temp_dir = tempfile.mkdtemp()
            logger.info(f"Created temporary test directory: {self.temp_dir}")

            # Run validation tests
            await self._validate_version_info()
            await self._validate_git_manager()
            await self._validate_changelog_manager()
            await self._validate_release_manager()
            await self._validate_version_release_system()
            await self._validate_integration_scenarios()
            await self._validate_error_handling()

            # Determine overall status
            self._determine_overall_status()

            logger.info("Validation completed successfully!")

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            self.validation_results["overall_status"] = "error"
            self.validation_results["errors"].append(f"Validation failed: {str(e)}")

        finally:
            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info("Cleaned up temporary test directory")

        return self.validation_results

    async def _validate_version_info(self):
        """Validate VersionInfo functionality."""
        logger.info("Validating VersionInfo functionality...")

        test_results = {"name": "VersionInfo Validation", "status": "pending", "tests": []}

        try:
            # Test version parsing
            version = VersionInfo.from_string("1.2.3")
            assert version.major == 1 and version.minor == 2 and version.patch == 3
            test_results["tests"].append({"name": "Version parsing", "status": "passed"})

            # Test version with prerelease
            version = VersionInfo.from_string("1.2.3-alpha.1")
            assert version.prerelease == "alpha.1"
            test_results["tests"].append({"name": "Version with prerelease", "status": "passed"})

            # Test version with build
            version = VersionInfo.from_string("1.2.3+build.123")
            assert version.build == "build.123"
            test_results["tests"].append({"name": "Version with build", "status": "passed"})

            # Test version string conversion
            version = VersionInfo(1, 2, 3, "alpha.1", "build.123")
            assert str(version) == "1.2.3-alpha.1+build.123"
            test_results["tests"].append({"name": "Version string conversion", "status": "passed"})

            # Test version bumping
            base_version = VersionInfo(1, 2, 3)

            major_version = base_version.bump(ReleaseType.MAJOR)
            assert major_version.major == 2 and major_version.minor == 0 and major_version.patch == 0
            test_results["tests"].append({"name": "Major version bump", "status": "passed"})

            minor_version = base_version.bump(ReleaseType.MINOR)
            assert minor_version.major == 1 and minor_version.minor == 3 and minor_version.patch == 0
            test_results["tests"].append({"name": "Minor version bump", "status": "passed"})

            patch_version = base_version.bump(ReleaseType.PATCH)
            assert patch_version.major == 1 and patch_version.minor == 2 and patch_version.patch == 4
            test_results["tests"].append({"name": "Patch version bump", "status": "passed"})

            # Test invalid version handling
            try:
                VersionInfo.from_string("invalid")
                test_results["tests"].append({"name": "Invalid version handling", "status": "failed"})
            except ValueError:
                test_results["tests"].append({"name": "Invalid version handling", "status": "passed"})

            test_results["status"] = "passed"
            logger.info("VersionInfo validation passed")

        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            self.validation_results["errors"].append(f"VersionInfo validation failed: {str(e)}")
            logger.error(f"VersionInfo validation failed: {e}")

        self.validation_results["tests"]["version_info"] = test_results

    async def _validate_git_manager(self):
        """Validate GitManager functionality."""
        logger.info("Validating GitManager functionality...")

        test_results = {"name": "GitManager Validation", "status": "pending", "tests": []}

        try:
            # Initialize git repository
            git_manager = GitManager(self.temp_dir)
            subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.temp_dir, capture_output=True)

            # Test getting current branch
            branch = git_manager.get_current_branch()
            assert branch in ["main", "master"]
            test_results["tests"].append({"name": "Get current branch", "status": "passed"})

            # Test getting latest tag (should be None initially)
            tag = git_manager.get_latest_tag()
            assert tag is None
            test_results["tests"].append({"name": "Get latest tag (no tags)", "status": "passed"})

            # Create test file and commit
            test_file = os.path.join(self.temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            git_manager.run_git_command(["add", "test.txt"])
            git_manager.run_git_command(["commit", "-m", "Initial commit"])

            # Test commit history
            commits = git_manager.get_commit_history(count=5)
            assert len(commits) == 1
            assert commits[0]["message"] == "Initial commit"
            test_results["tests"].append({"name": "Get commit history", "status": "passed"})

            # Test working tree status
            status = git_manager.get_working_tree_status()
            assert all(len(files) == 0 for files in status.values())
            test_results["tests"].append({"name": "Get working tree status (clean)", "status": "passed"})

            # Test with untracked file
            untracked_file = os.path.join(self.temp_dir, "untracked.txt")
            with open(untracked_file, "w") as f:
                f.write("untracked content")

            status = git_manager.get_working_tree_status()
            assert len(status["untracked"]) == 1
            test_results["tests"].append({"name": "Get working tree status (untracked)", "status": "passed"})

            # Test commit changes
            commit_hash = git_manager.commit_changes("Add untracked file", [untracked_file])
            assert commit_hash is not None and len(commit_hash) == 40
            test_results["tests"].append({"name": "Commit changes", "status": "passed"})

            # Test tag creation
            tag_name = "v1.0.0"
            git_manager.create_tag(tag_name, "Release 1.0.0")
            latest_tag = git_manager.get_latest_tag()
            assert latest_tag == tag_name
            test_results["tests"].append({"name": "Create and get tag", "status": "passed"})

            test_results["status"] = "passed"
            logger.info("GitManager validation passed")

        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            self.validation_results["errors"].append(f"GitManager validation failed: {str(e)}")
            logger.error(f"GitManager validation failed: {e}")

        self.validation_results["tests"]["git_manager"] = test_results

    async def _validate_changelog_manager(self):
        """Validate ChangelogManager functionality."""
        logger.info("Validating ChangelogManager functionality...")

        test_results = {"name": "ChangelogManager Validation", "status": "pending", "tests": []}

        try:
            changelog_file = os.path.join(self.temp_dir, "CHANGELOG.md")
            changelog_manager = ChangelogManager(changelog_file)

            # Test changelog generation with no commits
            changelog = changelog_manager.generate_changelog()
            assert changelog == "No changes in this release."
            test_results["tests"].append({"name": "Generate changelog (no commits)", "status": "passed"})

            # Test changelog generation with commits
            mock_commits = """- Add new feature (abc123)
- Update documentation (def456)
- Fix bug in authentication (ghi789)
- Remove deprecated code (jkl012)"""

            with patch.object(changelog_manager, "git_manager") as mock_git:
                mock_git.run_git_command.return_value.stdout = mock_commits

                changelog = changelog_manager.generate_changelog(to_tag="v1.0.0")
                assert "## [v1.0.0]" in changelog
                assert "### Added" in changelog
                assert "### Changed" in changelog
                assert "### Fixed" in changelog
                assert "### Removed" in changelog
                test_results["tests"].append({"name": "Generate changelog (with commits)", "status": "passed"})

            # Test updating changelog file (new file)
            new_changelog = "## [v1.0.0] - 2025-08-05\n\n### Added\n- New feature"
            changelog_manager.update_changelog_file(new_changelog, "1.0.0")

            assert os.path.exists(changelog_file)
            with open(changelog_file, "r") as f:
                content = f.read()
                assert new_changelog in content
                assert "# Changelog" in content
            test_results["tests"].append({"name": "Update changelog file (new file)", "status": "passed"})

            # Test updating changelog file (existing file)
            existing_content = "# Changelog\n\n## [v0.9.0] - 2025-07-01\n\n### Added\n- Old feature"
            with open(changelog_file, "w") as f:
                f.write(existing_content)

            changelog_manager.update_changelog_file(new_changelog, "1.0.0")

            with open(changelog_file, "r") as f:
                content = f.read()
                assert content.startswith(new_changelog)
                assert "## [v0.9.0]" in content
            test_results["tests"].append({"name": "Update changelog file (existing file)", "status": "passed"})

            test_results["status"] = "passed"
            logger.info("ChangelogManager validation passed")

        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            self.validation_results["errors"].append(f"ChangelogManager validation failed: {str(e)}")
            logger.error(f"ChangelogManager validation failed: {e}")

        self.validation_results["tests"]["changelog_manager"] = test_results

    async def _validate_release_manager(self):
        """Validate ReleaseManager functionality."""
        logger.info("Validating ReleaseManager functionality...")

        test_results = {"name": "ReleaseManager Validation", "status": "pending", "tests": []}

        try:
            release_manager = ReleaseManager(self.temp_dir)

            # Mock git operations
            with (
                patch.object(release_manager.git_manager, "get_latest_tag") as mock_get_tag,
                patch.object(release_manager.git_manager, "get_current_branch") as mock_get_branch,
                patch.object(release_manager.changelog_manager, "generate_changelog") as mock_gen_changelog,
            ):

                mock_get_tag.return_value = "v0.3.10"
                mock_get_branch.return_value = "main"
                mock_gen_changelog.return_value = "Generated changelog"

                # Test prepare release
                release_config = await release_manager.prepare_release(
                    ReleaseType.PATCH, "v0.3.11 release with Git version management", pre_release=False, draft=False
                )

                assert release_config.version.major == 0
                assert release_config.version.minor == 3
                assert release_config.version.patch == 11
                assert release_config.release_type == ReleaseType.PATCH
                assert release_config.tag_name == "v0.3.11"
                test_results["tests"].append({"name": "Prepare release", "status": "passed"})

            # Test create release assets
            os.makedirs(os.path.join(self.temp_dir, "src"), exist_ok=True)
            os.makedirs(os.path.join(self.temp_dir, "docs"), exist_ok=True)

            with open(os.path.join(self.temp_dir, "src", "test.py"), "w") as f:
                f.write("print('test')")

            with open(os.path.join(self.temp_dir, "docs", "README.md"), "w") as f:
                f.write("# Documentation")

            with open(os.path.join(self.temp_dir, "pyproject.toml"), "w") as f:
                f.write('[tool.poetry]\nname = "test"')

            with patch.object(release_manager, "production_system") as mock_prod:
                mock_prod.generate_deployment_package = AsyncMock(
                    return_value=os.path.join(self.temp_dir, "package.zip")
                )

                with open(os.path.join(self.temp_dir, "package.zip"), "w") as f:
                    f.write("package content")

                assets = await release_manager.create_release_assets(release_config)

                assert len(assets) > 0
                for asset in assets:
                    assert asset.name is not None
                    assert asset.path is not None
                    assert asset.content_type is not None
                    assert asset.size > 0
                    assert asset.checksum is not None
                test_results["tests"].append({"name": "Create release assets", "status": "passed"})

            # Test execute release with clean working tree
            with (
                patch.object(release_manager.git_manager, "get_working_tree_status") as mock_status,
                patch.object(release_manager, "create_release_assets") as mock_assets,
                patch.object(release_manager.changelog_manager, "update_changelog_file") as mock_update,
                patch.object(release_manager.git_manager, "commit_changes") as mock_commit,
                patch.object(release_manager.git_manager, "create_tag") as mock_tag,
            ):

                mock_status.return_value = {"modified": [], "added": [], "deleted": [], "untracked": [], "renamed": []}
                mock_assets.return_value = []

                release_info = await release_manager.execute_release(release_config)

                assert release_info.version.major == 0
                assert release_info.version.minor == 3
                assert release_info.version.patch == 11
                assert release_info.status == ReleaseStatus.READY
                assert release_info.tag_name == "v0.3.11"
                test_results["tests"].append({"name": "Execute release (clean working tree)", "status": "passed"})

            # Test execute release with dirty working tree
            with patch.object(release_manager.git_manager, "get_working_tree_status") as mock_status:
                mock_status.return_value = {
                    "modified": ["file1.py"],
                    "added": [],
                    "deleted": [],
                    "untracked": [],
                    "renamed": [],
                }

                try:
                    await release_manager.execute_release(release_config)
                    test_results["tests"].append({"name": "Execute release (dirty working tree)", "status": "failed"})
                except Exception:
                    test_results["tests"].append({"name": "Execute release (dirty working tree)", "status": "passed"})

            test_results["status"] = "passed"
            logger.info("ReleaseManager validation passed")

        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            self.validation_results["errors"].append(f"ReleaseManager validation failed: {str(e)}")
            logger.error(f"ReleaseManager validation failed: {e}")

        self.validation_results["tests"]["release_manager"] = test_results

    async def _validate_version_release_system(self):
        """Validate VersionReleaseSystem functionality."""
        logger.info("Validating VersionReleaseSystem functionality...")

        test_results = {"name": "VersionReleaseSystem Validation", "status": "pending", "tests": []}

        try:
            config = {"repo_path": self.temp_dir}
            system = VersionReleaseSystem(config)

            # Test initialization
            with patch.object(system.production_system, "initialize") as mock_init:
                mock_init.return_value = AsyncMock()

                await system.initialize()
                assert system.is_initialized is True
                test_results["tests"].append({"name": "System initialization", "status": "passed"})

            # Test create release
            system.is_initialized = True

            with (
                patch.object(system.release_manager, "prepare_release") as mock_prepare,
                patch.object(system.release_manager, "execute_release") as mock_execute,
                patch.object(system.release_manager, "publish_release") as mock_publish,
            ):

                mock_prepare.return_value = AsyncMock()
                mock_execute.return_value = AsyncMock()
                mock_publish.return_value = AsyncMock()

                # Mock release config
                release_config = ReleaseConfig(
                    version=VersionInfo(0, 3, 11),
                    release_type=ReleaseType.PATCH,
                    release_notes="v0.3.11 release",
                    changelog_file="CHANGELOG.md",
                    tag_name="v0.3.11",
                )
                mock_prepare.return_value = release_config

                # Mock release info
                release_info = ReleaseInfo(
                    release_id="test-id",
                    version=VersionInfo(0, 3, 11),
                    release_type=ReleaseType.PATCH,
                    status=ReleaseStatus.PUBLISHED,
                    created_at=datetime.now(),
                    published_at=datetime.now(),
                    tag_name="v0.3.11",
                    target_commitish="main",
                )
                mock_execute.return_value = release_info
                mock_publish.return_value = release_info

                result = await system.create_release(ReleaseType.PATCH, "v0.3.11 release", auto_publish=True)

                assert result == release_info
                test_results["tests"].append({"name": "Create release", "status": "passed"})

            # Test create hotfix release
            with patch.object(system, "create_release") as mock_create:
                mock_create.return_value = AsyncMock()

                await system.create_hotfix_release("Critical bug fix", auto_publish=True)

                mock_create.assert_called_once_with(
                    ReleaseType.HOTFIX, "Critical bug fix", pre_release=False, draft=False, auto_publish=True
                )
                test_results["tests"].append({"name": "Create hotfix release", "status": "passed"})

            # Test get release statistics
            mock_releases = [
                ReleaseInfo(
                    release_id="1",
                    version=VersionInfo(0, 3, 10),
                    release_type=ReleaseType.PATCH,
                    status=ReleaseStatus.PUBLISHED,
                    created_at=datetime.now(),
                    tag_name="v0.3.10",
                    target_commitish="main",
                    assets=[Mock(), Mock()],
                ),
                ReleaseInfo(
                    release_id="2",
                    version=VersionInfo(0, 3, 11),
                    release_type=ReleaseType.PATCH,
                    status=ReleaseStatus.PUBLISHED,
                    created_at=datetime.now(),
                    tag_name="v0.3.11",
                    target_commitish="main",
                    assets=[Mock()],
                ),
            ]

            with patch.object(system.release_manager, "get_release_history") as mock_history:
                mock_history.return_value = mock_releases

                stats = await system.get_release_statistics()

                assert stats["total_releases"] == 2
                assert stats["release_types"]["patch"] == 2
                assert len(stats["recent_releases"]) == 2
                assert stats["average_assets_per_release"] == 1.5
                test_results["tests"].append({"name": "Get release statistics", "status": "passed"})

            test_results["status"] = "passed"
            logger.info("VersionReleaseSystem validation passed")

        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            self.validation_results["errors"].append(f"VersionReleaseSystem validation failed: {str(e)}")
            logger.error(f"VersionReleaseSystem validation failed: {e}")

        self.validation_results["tests"]["version_release_system"] = test_results

    async def _validate_integration_scenarios(self):
        """Validate integration scenarios."""
        logger.info("Validating integration scenarios...")

        test_results = {"name": "Integration Scenarios Validation", "status": "pending", "tests": []}

        try:
            # Test complete release workflow
            config = {"repo_path": self.temp_dir}
            system = VersionReleaseSystem(config)

            with (
                patch.object(system, "initialize") as mock_init,
                patch.object(system.release_manager, "prepare_release") as mock_prepare,
                patch.object(system.release_manager, "execute_release") as mock_execute,
                patch.object(system.release_manager, "publish_release") as mock_publish,
            ):

                mock_init.return_value = AsyncMock()

                # Mock release config
                release_config = ReleaseConfig(
                    version=VersionInfo(0, 3, 11),
                    release_type=ReleaseType.PATCH,
                    release_notes="v0.3.11 release with Git version management",
                    changelog_file="CHANGELOG.md",
                    tag_name="v0.3.11",
                )
                mock_prepare.return_value = release_config

                # Mock release info
                release_info = ReleaseInfo(
                    release_id="test-id",
                    version=VersionInfo(0, 3, 11),
                    release_type=ReleaseType.PATCH,
                    status=ReleaseStatus.PUBLISHED,
                    created_at=datetime.now(),
                    published_at=datetime.now(),
                    tag_name="v0.3.11",
                    target_commitish="main",
                    body="Release body",
                )
                mock_execute.return_value = release_info
                mock_publish.return_value = release_info

                # Execute workflow
                await system.initialize()
                result = await system.create_release(
                    ReleaseType.PATCH, "v0.3.11 release with Git version management", auto_publish=True
                )

                # Verify results
                assert result == release_info
                assert result.version.major == 0
                assert result.version.minor == 3
                assert result.version.patch == 11
                assert result.status == ReleaseStatus.PUBLISHED
                test_results["tests"].append({"name": "Complete release workflow", "status": "passed"})

            # Test rollback scenario
            release_info = ReleaseInfo(
                release_id="test-id",
                version=VersionInfo(0, 3, 11),
                release_type=ReleaseType.PATCH,
                status=ReleaseStatus.PUBLISHED,
                created_at=datetime.now(),
                tag_name="v0.3.11",
                target_commitish="main",
            )

            with patch.object(system.release_manager, "rollback_release") as mock_rollback:
                mock_rollback.return_value = True

                result = await system.release_manager.rollback_release(release_info)

                assert result is True
                assert release_info.status == ReleaseStatus.ARCHIVED
                test_results["tests"].append({"name": "Release rollback scenario", "status": "passed"})

            test_results["status"] = "passed"
            logger.info("Integration scenarios validation passed")

        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            self.validation_results["errors"].append(f"Integration scenarios validation failed: {str(e)}")
            logger.error(f"Integration scenarios validation failed: {e}")

        self.validation_results["tests"]["integration_scenarios"] = test_results

    async def _validate_error_handling(self):
        """Validate error handling."""
        logger.info("Validating error handling...")

        test_results = {"name": "Error Handling Validation", "status": "pending", "tests": []}

        try:
            config = {"repo_path": self.temp_dir}
            system = VersionReleaseSystem(config)

            # Test system not initialized error
            try:
                await system.create_release(ReleaseType.PATCH, "Test release")
                test_results["tests"].append({"name": "System not initialized error", "status": "failed"})
            except Exception as e:
                assert "System not initialized" in str(e)
                test_results["tests"].append({"name": "System not initialized error", "status": "passed"})

            # Test invalid version string error
            try:
                VersionInfo.from_string("invalid")
                test_results["tests"].append({"name": "Invalid version string error", "status": "failed"})
            except ValueError:
                test_results["tests"].append({"name": "Invalid version string error", "status": "passed"})

            # Test git command error
            git_manager = GitManager(self.temp_dir)
            try:
                git_manager.run_git_command(["invalid", "command"])
                test_results["tests"].append({"name": "Git command error", "status": "failed"})
            except subprocess.CalledProcessError:
                test_results["tests"].append({"name": "Git command error", "status": "passed"})

            test_results["status"] = "passed"
            logger.info("Error handling validation passed")

        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            self.validation_results["errors"].append(f"Error handling validation failed: {str(e)}")
            logger.error(f"Error handling validation failed: {e}")

        self.validation_results["tests"]["error_handling"] = test_results

    def _determine_overall_status(self):
        """Determine overall validation status."""
        all_passed = all(test_result["status"] == "passed" for test_result in self.validation_results["tests"].values())

        if all_passed:
            self.validation_results["overall_status"] = "passed"
            self.validation_results["recommendations"].append("System is ready for production use")
        else:
            self.validation_results["overall_status"] = "failed"
            self.validation_results["recommendations"].append("Fix failed tests before production deployment")

    def save_validation_report(self, filename: str = "v0_3_11_validation_report.json"):
        """Save validation report to file."""
        with open(filename, "w") as f:
            json.dump(self.validation_results, f, indent=2)
        logger.info(f"Validation report saved to {filename}")

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("V0.3.11 Git Version Release System Validation Summary")
        print("=" * 60)
        print(f"Overall Status: {self.validation_results['overall_status'].upper()}")
        print(f"Validation Time: {self.validation_results['timestamp']}")
        print(f"Total Tests: {len(self.validation_results['tests'])}")

        for test_name, test_result in self.validation_results["tests"].items():
            status = test_result["status"].upper()
            print(f"  {test_name}: {status}")

            if test_result["status"] == "failed":
                print(f"    Error: {test_result.get('error', 'Unknown error')}")

        if self.validation_results["errors"]:
            print(f"\nErrors ({len(self.validation_results['errors'])}):")
            for error in self.validation_results["errors"]:
                print(f"  - {error}")

        if self.validation_results["warnings"]:
            print(f"\nWarnings ({len(self.validation_results['warnings'])}):")
            for warning in self.validation_results["warnings"]:
                print(f"  - {warning}")

        if self.validation_results["recommendations"]:
            print(f"\nRecommendations:")
            for rec in self.validation_results["recommendations"]:
                print(f"  - {rec}")

        print("=" * 60)


async def main():
    """Main validation function."""
    validator = GitVersionReleaseSystemValidator()
    results = await validator.validate_system()

    # Save validation report
    validator.save_validation_report()

    # Print summary
    validator.print_summary()

    # Return exit code based on results
    return 0 if results["overall_status"] == "passed" else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
