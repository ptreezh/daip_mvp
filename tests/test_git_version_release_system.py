# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 16:00:00
@Author  : DAIP-LIVE Team
@File    : test_git_version_release_system.py
@Description:
    Comprehensive tests for Git Version Release System v0.3.11
    Git版本发布系统综合测试
"""

import asyncio
import pytest
import tempfile
import os
import shutil
import subprocess
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from pathlib import Path

from src.core_services.git_version_release_system import (
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
    initialize_version_release_system
)


class TestVersionInfo:
    """Test VersionInfo class."""
    
    def test_version_string_parsing(self):
        """Test version string parsing."""
        # Test standard version
        version = VersionInfo.from_string("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.prerelease is None
        assert version.build is None
        
        # Test with prerelease
        version = VersionInfo.from_string("1.2.3-alpha.1")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.prerelease == "alpha.1"
        
        # Test with build
        version = VersionInfo.from_string("1.2.3+build.123")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.build == "build.123"
        
        # Test with both prerelease and build
        version = VersionInfo.from_string("1.2.3-alpha.1+build.123")
        assert version.prerelease == "alpha.1"
        assert version.build == "build.123"
    
    def test_version_string_conversion(self):
        """Test version to string conversion."""
        version = VersionInfo(1, 2, 3)
        assert str(version) == "1.2.3"
        
        version = VersionInfo(1, 2, 3, "alpha.1")
        assert str(version) == "1.2.3-alpha.1"
        
        version = VersionInfo(1, 2, 3, "alpha.1", "build.123")
        assert str(version) == "1.2.3-alpha.1+build.123"
    
    def test_version_bumping(self):
        """Test version bumping."""
        version = VersionInfo(1, 2, 3)
        
        # Test major bump
        new_version = version.bump(ReleaseType.MAJOR)
        assert new_version.major == 2
        assert new_version.minor == 0
        assert new_version.patch == 0
        
        # Test minor bump
        new_version = version.bump(ReleaseType.MINOR)
        assert new_version.major == 1
        assert new_version.minor == 3
        assert new_version.patch == 0
        
        # Test patch bump
        new_version = version.bump(ReleaseType.PATCH)
        assert new_version.major == 1
        assert new_version.minor == 2
        assert new_version.patch == 4
        
        # Test hotfix bump
        new_version = version.bump(ReleaseType.HOTFIX)
        assert new_version.major == 1
        assert new_version.minor == 2
        assert new_version.patch == 3
        assert new_version.prerelease is not None
        assert "hotfix" in new_version.prerelease
        
        # Test RC bump
        new_version = version.bump(ReleaseType.RC)
        assert new_version.major == 1
        assert new_version.minor == 2
        assert new_version.patch == 3
        assert new_version.prerelease == "rc.1"
        
        # Test RC increment
        rc_version = VersionInfo(1, 2, 3, "rc.1")
        new_version = rc_version.bump(ReleaseType.RC)
        assert new_version.prerelease == "rc.2"
    
    def test_invalid_version_string(self):
        """Test invalid version string handling."""
        with pytest.raises(ValueError):
            VersionInfo.from_string("invalid")
        
        with pytest.raises(ValueError):
            VersionInfo.from_string("1.2")
        
        with pytest.raises(ValueError):
            VersionInfo.from_string("1.2.3.4")


class TestGitManager:
    """Test GitManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.git_manager = GitManager(self.temp_dir)
        
        # Initialize git repository
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.temp_dir, capture_output=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_current_branch(self):
        """Test getting current branch."""
        branch = self.git_manager.get_current_branch()
        assert branch == "main" or branch == "master"
    
    def test_get_latest_tag_no_tags(self):
        """Test getting latest tag when no tags exist."""
        tag = self.git_manager.get_latest_tag()
        assert tag is None
    
    def test_create_and_get_tag(self):
        """Test creating and getting tags."""
        # Create a test file and commit
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        self.git_manager.run_git_command(["add", "test.txt"])
        self.git_manager.run_git_command(["commit", "-m", "Initial commit"])
        
        # Create tag
        tag_name = "v1.0.0"
        self.git_manager.create_tag(tag_name, "Release 1.0.0")
        
        # Get latest tag
        latest_tag = self.git_manager.get_latest_tag()
        assert latest_tag == tag_name
    
    def test_get_commit_history(self):
        """Test getting commit history."""
        # Create a test file and commit
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        self.git_manager.run_git_command(["add", "test.txt"])
        self.git_manager.run_git_command(["commit", "-m", "Initial commit"])
        
        # Get commit history
        commits = self.git_manager.get_commit_history(count=5)
        assert len(commits) == 1
        assert commits[0]["message"] == "Initial commit"
        assert "hash" in commits[0]
        assert "author" in commits[0]
        assert "date" in commits[0]
    
    def test_get_working_tree_status(self):
        """Test getting working tree status."""
        # Clean working tree
        status = self.git_manager.get_working_tree_status()
        assert all(len(files) == 0 for files in status.values())
        
        # Create untracked file
        test_file = os.path.join(self.temp_dir, "untracked.txt")
        with open(test_file, "w") as f:
            f.write("untracked content")
        
        status = self.git_manager.get_working_tree_status()
        assert len(status["untracked"]) == 1
        assert "untracked.txt" in status["untracked"]
    
    def test_commit_changes(self):
        """Test committing changes."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        # Commit changes
        commit_hash = self.git_manager.commit_changes("Add test file")
        
        # Verify commit was created
        assert commit_hash is not None
        assert len(commit_hash) == 40  # SHA-1 hash length


class TestChangelogManager:
    """Test ChangelogManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "CHANGELOG.md")
        self.changelog_manager = ChangelogManager(self.changelog_file)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_generate_changelog_no_commits(self):
        """Test generating changelog with no commits."""
        with patch.object(self.changelog_manager, 'git_manager') as mock_git:
            mock_git.run_git_command.return_value.stdout = ""
            
            changelog = self.changelog_manager.generate_changelog()
            assert changelog == "No changes in this release."
    
    def test_generate_changelog_with_commits(self):
        """Test generating changelog with commits."""
        mock_commits = """- Add new feature (abc123)
- Update documentation (def456)
- Fix bug in authentication (ghi789)
- Remove deprecated code (jkl012)"""
        
        with patch.object(self.changelog_manager, 'git_manager') as mock_git:
            mock_git.run_git_command.return_value.stdout = mock_commits
            
            changelog = self.changelog_manager.generate_changelog(to_tag="v1.0.0")
            
            assert "## [v1.0.0]" in changelog
            assert "### Added" in changelog
            assert "### Changed" in changelog
            assert "### Fixed" in changelog
            assert "### Removed" in changelog
    
    def test_update_changelog_file_new_file(self):
        """Test updating changelog file when it doesn't exist."""
        new_changelog = "## [v1.0.0] - 2025-08-05\n\n### Added\n- New feature"
        
        self.changelog_manager.update_changelog_file(new_changelog, "1.0.0")
        
        assert os.path.exists(self.changelog_file)
        
        with open(self.changelog_file, 'r') as f:
            content = f.read()
            assert new_changelog in content
            assert "# Changelog" in content
    
    def test_update_changelog_file_existing_file(self):
        """Test updating changelog file when it exists."""
        # Create existing changelog
        existing_content = "# Changelog\n\n## [v0.9.0] - 2025-07-01\n\n### Added\n- Old feature"
        with open(self.changelog_file, 'w') as f:
            f.write(existing_content)
        
        new_changelog = "## [v1.0.0] - 2025-08-05\n\n### Added\n- New feature"
        
        self.changelog_manager.update_changelog_file(new_changelog, "1.0.0")
        
        with open(self.changelog_file, 'r') as f:
            content = f.read()
            assert content.startswith(new_changelog)
            assert "## [v0.9.0]" in content


class TestReleaseManager:
    """Test ReleaseManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.release_manager = ReleaseManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_prepare_release(self):
        """Test preparing release."""
        with patch.object(self.release_manager.git_manager, 'get_latest_tag') as mock_get_tag, \
             patch.object(self.release_manager.git_manager, 'get_current_branch') as mock_get_branch, \
             patch.object(self.release_manager.changelog_manager, 'generate_changelog') as mock_gen_changelog:
            
            mock_get_tag.return_value = "v0.3.10"
            mock_get_branch.return_value = "main"
            mock_gen_changelog.return_value = "Generated changelog"
            
            release_config = await self.release_manager.prepare_release(
                ReleaseType.MINOR,
                "Release notes",
                pre_release=False,
                draft=False
            )
            
            assert release_config.version.major == 0
            assert release_config.version.minor == 3
            assert release_config.version.patch == 11
            assert release_config.release_type == ReleaseType.MINOR
            assert release_config.tag_name == "v0.3.11"
            assert release_config.release_notes == "Release notes"
    
    @pytest.mark.asyncio
    async def test_prepare_release_no_existing_tag(self):
        """Test preparing release when no existing tag exists."""
        with patch.object(self.release_manager.git_manager, 'get_latest_tag') as mock_get_tag, \
             patch.object(self.release_manager.git_manager, 'get_current_branch') as mock_get_branch, \
             patch.object(self.release_manager.changelog_manager, 'generate_changelog') as mock_gen_changelog:
            
            mock_get_tag.return_value = None
            mock_get_branch.return_value = "main"
            mock_gen_changelog.return_value = "Generated changelog"
            
            release_config = await self.release_manager.prepare_release(
                ReleaseType.MAJOR,
                "Initial release"
            )
            
            assert release_config.version.major == 1
            assert release_config.version.minor == 0
            assert release_config.version.patch == 0
            assert release_config.tag_name == "v1.0.0"
    
    @pytest.mark.asyncio
    async def test_create_release_assets(self):
        """Test creating release assets."""
        # Create test directory structure
        os.makedirs(os.path.join(self.temp_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "docs"), exist_ok=True)
        
        # Create test files
        with open(os.path.join(self.temp_dir, "src", "test.py"), "w") as f:
            f.write("print('test')")
        
        with open(os.path.join(self.temp_dir, "docs", "README.md"), "w") as f:
            f.write("# Documentation")
        
        with open(os.path.join(self.temp_dir, "pyproject.toml"), "w") as f:
            f.write("[tool.poetry]\nname = \"test\"")
        
        # Mock production system
        with patch.object(self.release_manager, 'production_system') as mock_prod:
            mock_prod.generate_deployment_package = AsyncMock(return_value=os.path.join(self.temp_dir, "package.zip"))
            
            # Create package file
            with open(os.path.join(self.temp_dir, "package.zip"), "w") as f:
                f.write("package content")
            
            release_config = ReleaseConfig(
                version=VersionInfo(1, 0, 0),
                release_type=ReleaseType.MAJOR,
                release_notes="Test release",
                changelog_file="CHANGELOG.md",
                tag_name="v1.0.0"
            )
            
            assets = await self.release_manager.create_release_assets(release_config)
            
            assert len(assets) > 0
            for asset in assets:
                assert asset.name is not None
                assert asset.path is not None
                assert asset.content_type is not None
                assert asset.size > 0
                assert asset.checksum is not None
    
    @pytest.mark.asyncio
    async def test_execute_release_clean_working_tree(self):
        """Test executing release with clean working tree."""
        with patch.object(self.release_manager.git_manager, 'get_working_tree_status') as mock_status, \
             patch.object(self.release_manager, 'create_release_assets') as mock_assets, \
             patch.object(self.release_manager.changelog_manager, 'update_changelog_file') as mock_update, \
             patch.object(self.release_manager.git_manager, 'commit_changes') as mock_commit, \
             patch.object(self.release_manager.git_manager, 'create_tag') as mock_tag:
            
            mock_status.return_value = {
                "modified": [], "added": [], "deleted": [], "untracked": [], "renamed": []
            }
            mock_assets.return_value = []
            
            release_config = ReleaseConfig(
                version=VersionInfo(1, 0, 0),
                release_type=ReleaseType.MAJOR,
                release_notes="Test release",
                changelog_file="CHANGELOG.md",
                tag_name="v1.0.0",
                target_commitish="main",
                body="Release body"
            )
            
            release_info = await self.release_manager.execute_release(release_config)
            
            assert release_info.version.major == 1
            assert release_info.release_type == ReleaseType.MAJOR
            assert release_info.status == ReleaseStatus.READY
            assert release_info.tag_name == "v1.0.0"
            assert release_info.target_commitish == "main"
            
            mock_update.assert_called_once()
            mock_commit.assert_called_once()
            mock_tag.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_release_dirty_working_tree(self):
        """Test executing release with dirty working tree."""
        with patch.object(self.release_manager.git_manager, 'get_working_tree_status') as mock_status:
            mock_status.return_value = {
                "modified": ["file1.py"], "added": [], "deleted": [], "untracked": [], "renamed": []
            }
            
            release_config = ReleaseConfig(
                version=VersionInfo(1, 0, 0),
                release_type=ReleaseType.MAJOR,
                release_notes="Test release",
                changelog_file="CHANGELOG.md",
                tag_name="v1.0.0"
            )
            
            with pytest.raises(Exception) as exc_info:
                await self.release_manager.execute_release(release_config)
            
            assert "Working directory is not clean" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_publish_release(self):
        """Test publishing release."""
        release_info = ReleaseInfo(
            release_id="test-id",
            version=VersionInfo(1, 0, 0),
            release_type=ReleaseType.MAJOR,
            status=ReleaseStatus.READY,
            created_at=datetime.now(),
            tag_name="v1.0.0",
            target_commitish="main"
        )
        
        with patch.object(self.release_manager.git_manager, 'run_git_command') as mock_git:
            await self.release_manager.publish_release(release_info)
            
            assert release_info.status == ReleaseStatus.PUBLISHED
            assert release_info.published_at is not None
            
            # Verify git commands were called
            mock_git.assert_any_call(["push", "origin", "main"])
            mock_git.assert_any_call(["push", "origin", "v1.0.0"])
    
    @pytest.mark.asyncio
    async def test_rollback_release(self):
        """Test rolling back release."""
        release_info = ReleaseInfo(
            release_id="test-id",
            version=VersionInfo(1, 0, 0),
            release_type=ReleaseType.MAJOR,
            status=ReleaseStatus.PUBLISHED,
            created_at=datetime.now(),
            tag_name="v1.0.0",
            target_commitish="main"
        )
        
        with patch.object(self.release_manager.git_manager, 'run_git_command') as mock_git:
            result = await self.release_manager.rollback_release(release_info)
            
            assert result is True
            assert release_info.status == ReleaseStatus.ARCHIVED
            
            # Verify git commands were called
            mock_git.assert_any_call(["tag", "-d", "v1.0.0"])
            mock_git.assert_any_call(["push", "origin", ":refs/tags/v1.0.0"])


class TestVersionReleaseSystem:
    """Test VersionReleaseSystem class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.config = {
            "repo_path": ".",
            "auto_publish": False,
            "create_assets": True
        }
        self.system = VersionReleaseSystem(self.config)
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test system initialization."""
        with patch.object(self.system.production_system, 'initialize') as mock_init:
            mock_init.return_value = AsyncMock()
            
            await self.system.initialize()
            
            assert self.system.is_initialized is True
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_release_not_initialized(self):
        """Test creating release when system is not initialized."""
        with pytest.raises(Exception) as exc_info:
            await self.system.create_release(
                ReleaseType.MAJOR,
                "Test release"
            )
        
        assert "System not initialized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_release_success(self):
        """Test successful release creation."""
        self.system.is_initialized = True
        
        with patch.object(self.system.release_manager, 'prepare_release') as mock_prepare, \
             patch.object(self.system.release_manager, 'execute_release') as mock_execute, \
             patch.object(self.system.release_manager, 'publish_release') as mock_publish:
            
            mock_prepare.return_value = AsyncMock()
            mock_execute.return_value = AsyncMock()
            mock_publish.return_value = AsyncMock()
            
            # Mock release config
            release_config = ReleaseConfig(
                version=VersionInfo(1, 0, 0),
                release_type=ReleaseType.MAJOR,
                release_notes="Test release",
                changelog_file="CHANGELOG.md",
                tag_name="v1.0.0"
            )
            mock_prepare.return_value = release_config
            
            # Mock release info
            release_info = ReleaseInfo(
                release_id="test-id",
                version=VersionInfo(1, 0, 0),
                release_type=ReleaseType.MAJOR,
                status=ReleaseStatus.READY,
                created_at=datetime.now(),
                tag_name="v1.0.0",
                target_commitish="main"
            )
            mock_execute.return_value = release_info
            mock_publish.return_value = release_info
            
            result = await self.system.create_release(
                ReleaseType.MAJOR,
                "Test release",
                auto_publish=True
            )
            
            assert result == release_info
            mock_prepare.assert_called_once()
            mock_execute.assert_called_once()
            mock_publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_hotfix_release(self):
        """Test creating hotfix release."""
        self.system.is_initialized = True
        
        with patch.object(self.system, 'create_release') as mock_create:
            mock_create.return_value = AsyncMock()
            
            await self.system.create_hotfix_release(
                "Critical bug fix",
                auto_publish=True
            )
            
            mock_create.assert_called_once_with(
                ReleaseType.HOTFIX,
                "Critical bug fix",
                pre_release=False,
                draft=False,
                auto_publish=True
            )
    
    @pytest.mark.asyncio
    async def test_get_release_statistics(self):
        """Test getting release statistics."""
        # Mock release history
        mock_releases = [
            ReleaseInfo(
                release_id="1",
                version=VersionInfo(1, 0, 0),
                release_type=ReleaseType.MAJOR,
                status=ReleaseStatus.PUBLISHED,
                created_at=datetime.now(),
                tag_name="v1.0.0",
                target_commitish="main",
                assets=[Mock(), Mock()]
            ),
            ReleaseInfo(
                release_id="2",
                version=VersionInfo(1, 0, 1),
                release_type=ReleaseType.PATCH,
                status=ReleaseStatus.PUBLISHED,
                created_at=datetime.now(),
                tag_name="v1.0.1",
                target_commitish="main",
                assets=[Mock()]
            )
        ]
        
        with patch.object(self.system.release_manager, 'get_release_history') as mock_history:
            mock_history.return_value = mock_releases
            
            stats = await self.system.get_release_statistics()
            
            assert stats["total_releases"] == 2
            assert stats["release_types"]["major"] == 1
            assert stats["release_types"]["patch"] == 1
            assert len(stats["recent_releases"]) == 2
            assert stats["average_assets_per_release"] == 1.5


class TestGlobalFunctions:
    """Test global functions."""
    
    def test_get_version_release_system(self):
        """Test getting global version release system instance."""
        # Clear global instance
        import src.core_services.git_version_release_system as git_module
        git_module._version_release_system = None
        
        system = get_version_release_system()
        assert isinstance(system, VersionReleaseSystem)
        
        # Test singleton behavior
        system2 = get_version_release_system()
        assert system is system2
    
    @pytest.mark.asyncio
    async def test_initialize_version_release_system(self):
        """Test initializing version release system."""
        config = {"repo_path": "."}
        
        with patch.object(VersionReleaseSystem, 'initialize') as mock_init:
            mock_init.return_value = AsyncMock()
            
            await initialize_version_release_system(config)
            
            mock_init.assert_called_once()


class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_release_workflow(self):
        """Test complete release workflow from preparation to publishing."""
        # This is an integration test that would require a real git repository
        # For now, we'll mock the components
        
        config = {"repo_path": "."}
        system = VersionReleaseSystem(config)
        
        with patch.object(system, 'initialize') as mock_init, \
             patch.object(system.release_manager, 'prepare_release') as mock_prepare, \
             patch.object(system.release_manager, 'execute_release') as mock_execute, \
             patch.object(system.release_manager, 'publish_release') as mock_publish:
            
            mock_init.return_value = AsyncMock()
            
            # Mock release config
            release_config = ReleaseConfig(
                version=VersionInfo(0, 3, 11),
                release_type=ReleaseType.PATCH,
                release_notes="v0.3.11 release with Git version management",
                changelog_file="CHANGELOG.md",
                tag_name="v0.3.11"
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
                body="Release body"
            )
            mock_execute.return_value = release_info
            mock_publish.return_value = release_info
            
            # Execute workflow
            await system.initialize()
            result = await system.create_release(
                ReleaseType.PATCH,
                "v0.3.11 release with Git version management",
                auto_publish=True
            )
            
            # Verify results
            assert result == release_info
            assert result.version.major == 0
            assert result.version.minor == 3
            assert result.version.patch == 11
            assert result.status == ReleaseStatus.PUBLISHED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])