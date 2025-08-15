"""
@Time    : 2025-08-05 15:00:00
@Author  : DAIP-LIVE Team
@File    : git_version_release_system.py
@Description:
    V0.3.11 Git Version Release System
    Git版本发布系统
"""

import asyncio
import json
import logging
import subprocess
import re
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import uuid
import shutil
import tempfile
import zipfile
import yaml

from .production_ready_preparation_system import (
    ProductionReadySystem,
    DeploymentEnvironment,
    DeploymentStrategy,
    get_production_ready_system
)

logger = logging.getLogger(__name__)


class ReleaseType(Enum):
    """Release types."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    HOTFIX = "hotfix"
    RC = "rc"


class ReleaseStatus(Enum):
    """Release status."""
    DRAFT = "draft"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class VersionInfo:
    """Version information."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    @classmethod
    def from_string(cls, version_str: str) -> 'VersionInfo':
        """Parse version string."""
        # Match semantic versioning pattern
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$'
        match = re.match(pattern, version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4),
            build=match.group(5)
        )

    def bump(self, release_type: ReleaseType) -> 'VersionInfo':
        """Bump version."""
        if release_type == ReleaseType.MAJOR:
            return VersionInfo(
                major=self.major + 1,
                minor=0,
                patch=0,
                self.prerelease,
                self.build
            )
        elif release_type == ReleaseType.MINOR:
            return VersionInfo(
                major=self.major,
                minor=self.minor + 1,
                patch=0,
                self.prerelease,
                self.build
            )
        elif release_type == ReleaseType.PATCH:
            return VersionInfo(
                major=self.major,
                minor=self.minor,
                patch=self.patch + 1,
                self.prerelease,
                self.build
            )
        elif release_type == ReleaseType.HOTFIX:
            # Hotfix patches the current version
            return VersionInfo(
                major=self.major,
                minor=self.minor,
                patch=self.patch,
                self.prerelease=f"hotfix.{datetime.now().strftime('%Y%m%d')}",
                self.build
            )
        elif release_type == ReleaseType.RC:
            # Release candidate
            rc_count = 1
            if self.prerelease and self.prerelease.startswith('rc.'):
                try:
                    rc_count = int(self.prerelease.split('.')[1]) + 1
                except (ValueError, IndexError):
                    rc_count = 1
            return VersionInfo(
                major=self.major,
                minor=self.minor,
                patch=self.patch,
                prerelease=f"rc.{rc_count}",
                self.build
            )
        else:
            raise ValueError(f"Unknown release type: {release_type}")


@dataclass
class ReleaseConfig:
    """Release configuration."""
    version: VersionInfo
    release_type: ReleaseType
    release_notes: str
    changelog_file: str
    assets: List[str] = field(default_factory=list)
    pre_release: bool = False
    draft: bool = False
    tag_name: Optional[str] = None
    target_commitish: Optional[str] = None
    name: Optional[str] = None
    body: Optional[str] = None


@dataclass
class ReleaseAsset:
    """Release asset."""
    name: str
    path: str
    content_type: str
    size: int
    checksum: str
    description: str = ""


@dataclass
class ReleaseInfo:
    """Release information."""
    release_id: str
    version: VersionInfo
    release_type: ReleaseType
    status: ReleaseStatus
    created_at: datetime
    published_at: Optional[datetime] = None
    tag_name: str
    target_commitish: str
    assets: List[ReleaseAsset] = field(default_factory=list)
    download_count: int = 0
    body: str = ""
    author: str = ""


class GitManager:
    """Git operations manager."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def run_git_command(self, command: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run git command."""
        try:
            return subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(command)}")
            logger.error(f"Error: {e.stderr}")
            raise
    
    def get_current_branch(self) -> str:
        """Get current branch."""
        result = self.run_git_command(["branch", "--show-current"])
        return result.stdout.strip()
    
    def get_latest_tag(self) -> Optional[str]:
        """Get latest tag."""
        try:
            result = self.run_git_command(["describe", "--tags", "--abbrev=0"])
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_commit_history(self, count: int = 10) -> List[Dict[str, str]]:
        """Get commit history."""
        result = self.run_git_command([
            "log", f"--max-count={count}", 
            "--pretty=format:%H|%an|%ae|%ad|%s",
            "--date=short"
        ])
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })
        
        return commits
    
    def create_tag(self, tag_name: str, message: str, commitish: Optional[str] = None) -> str:
        """Create git tag."""
        command = ["tag", "-a", tag_name, "-m", message]
        if commitish:
            command.append(commitish)
        
        self.run_git_command(command)
        return tag_name
    
    def push_tag(self, tag_name: str, remote: str = "origin") -> None:
        """Push tag to remote."""
        self.run_git_command(["push", remote, tag_name])
    
    def create_branch(self, branch_name: str, from_commitish: Optional[str] = None) -> None:
        """Create new branch."""
        command = ["checkout", "-b", branch_name]
        if from_commitish:
            command.append(from_commitish)
        
        self.run_git_command(command)
    
    def merge_branch(self, source_branch: str, target_branch: str, message: Optional[str] = None) -> None:
        """Merge branch."""
        current_branch = self.get_current_branch()
        
        if current_branch != target_branch:
            self.run_git_command(["checkout", target_branch])
        
        try:
            if message:
                self.run_git_command(["merge", "--no-ff", "-m", message, source_branch])
            else:
                self.run_git_command(["merge", "--no-ff", source_branch])
        finally:
            if current_branch != target_branch:
                self.run_git_command(["checkout", current_branch])
    
    def get_working_tree_status(self) -> Dict[str, List[str]]:
        """Get working tree status."""
        result = self.run_git_command(["status", "--porcelain"])
        
        status = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": [],
            "renamed": []
        }
        
        for line in result.stdout.strip().split('\n'):
            if line:
                code = line[:2]
                file_path = line[3:]
                
                if code == " M":
                    status["modified"].append(file_path)
                elif code == "A ":
                    status["added"].append(file_path)
                elif code == " D":
                    status["deleted"].append(file_path)
                elif code == "??":
                    status["untracked"].append(file_path)
                elif code.startswith("R"):
                    status["renamed"].append(file_path)
        
        return status
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> str:
        """Commit changes."""
        if files:
            self.run_git_command(["add"] + files)
        else:
            self.run_git_command(["add", "."])
        
        result = self.run_git_command(["commit", "-m", message])
        
        # Get commit hash
        hash_result = self.run_git_command(["rev-parse", "HEAD"])
        return hash_result.stdout.strip()
    
    def get_remote_url(self, remote: str = "origin") -> Optional[str]:
        """Get remote URL."""
        try:
            result = self.run_git_command(["remote", "get-url", remote])
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None


class ChangelogManager:
    """Changelog manager."""
    
    def __init__(self, changelog_file: str = "CHANGELOG.md"):
        self.changelog_file = changelog_file
    
    def generate_changelog(self, from_tag: Optional[str] = None, to_tag: Optional[str] = None) -> str:
        """Generate changelog from git commits."""
        git_manager = GitManager()
        
        # Get commit range
        if from_tag and to_tag:
            commits = git_manager.run_git_command([
                "log", f"{from_tag}..{to_tag}", 
                "--pretty=format:- %s (%h)"
            ]).stdout.strip()
        elif from_tag:
            commits = git_manager.run_git_command([
                "log", f"{from_tag}..HEAD", 
                "--pretty=format:- %s (%h)"
            ]).stdout.strip()
        else:
            commits = git_manager.run_git_command([
                "log", "--pretty=format:- %s (%h)"
            ]).stdout.strip()
        
        if not commits:
            return "No changes in this release."
        
        # Generate changelog
        changelog = f"""## [{to_tag or 'Unreleased'}] - {datetime.now().strftime('%Y-%m-%d')}

### Added
{self._categorize_commits(commits, 'add|feat|new')}

### Changed
{self._categorize_commits(commits, 'change|update|modify|improve')}

### Fixed
{self._categorize_commits(commits, 'fix|bug|repair')}

### Removed
{self._categorize_commits(commits, 'remove|delete|deprecate')}

"""
        return changelog
    
    def _categorize_commits(self, commits: str, keywords: str) -> str:
        """Categorize commits by keywords."""
        if not commits:
            return ""
        
        pattern = re.compile(keywords, re.IGNORECASE)
        categorized = []
        
        for line in commits.split('\n'):
            if line and pattern.search(line):
                categorized.append(line)
        
        return '\n'.join(categorized) if categorized else "No changes in this category."
    
    def update_changelog_file(self, new_changelog: str, version: str) -> None:
        """Update changelog file."""
        if os.path.exists(self.changelog_file):
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        else:
            existing_content = "# Changelog\n\n"
        
        # Insert new changelog at the beginning
        updated_content = new_changelog + "\n" + existing_content
        
        with open(self.changelog_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"Changelog file updated: {self.changelog_file}")


class ReleaseManager:
    """Release manager."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.git_manager = GitManager(repo_path)
        self.changelog_manager = ChangelogManager()
        self.production_system = get_production_ready_system()
        self.releases: List[ReleaseInfo] = []
    
    async def prepare_release(self, 
                            release_type: ReleaseType,
                            release_notes: str,
                            pre_release: bool = False,
                            draft: bool = False) -> ReleaseConfig:
        """Prepare release configuration."""
        logger.info(f"Preparing {release_type.value} release...")
        
        # Get current version
        current_tag = self.git_manager.get_latest_tag()
        if current_tag:
            current_version = VersionInfo.from_string(current_tag.lstrip('v'))
        else:
            current_version = VersionInfo(0, 1, 0)
        
        # Bump version
        new_version = current_version.bump(release_type)
        
        # Generate tag name
        tag_name = f"v{new_version}"
        
        # Generate changelog
        changelog = self.changelog_manager.generate_changelog(current_tag, tag_name)
        
        # Create release config
        release_config = ReleaseConfig(
            version=new_version,
            release_type=release_type,
            release_notes=release_notes,
            changelog_file=self.changelog_manager.changelog_file,
            pre_release=pre_release,
            draft=draft,
            tag_name=tag_name,
            target_commitish=self.git_manager.get_current_branch(),
            name=f"Release {new_version}",
            body=f"{release_notes}\n\n{changelog}"
        )
        
        logger.info(f"Release prepared: {tag_name}")
        return release_config
    
    async def create_release_assets(self, release_config: ReleaseConfig) -> List[ReleaseAsset]:
        """Create release assets."""
        assets = []
        
        try:
            # Generate deployment package
            package_path = await self.production_system.generate_deployment_package(str(release_config.version))
            
            if package_path and os.path.exists(package_path):
                asset = ReleaseAsset(
                    name=os.path.basename(package_path),
                    path=package_path,
                    content_type="application/zip",
                    size=os.path.getsize(package_path),
                    checksum=self._calculate_checksum(package_path),
                    description=f"Deployment package for {release_config.version}"
                )
                assets.append(asset)
            
            # Create source archive
            source_archive = await self._create_source_archive(release_config)
            if source_archive:
                asset = ReleaseAsset(
                    name=os.path.basename(source_archive),
                    path=source_archive,
                    content_type="application/zip",
                    size=os.path.getsize(source_archive),
                    checksum=self._calculate_checksum(source_archive),
                    description=f"Source archive for {release_config.version}"
                )
                assets.append(source_archive)
            
            # Create documentation archive
            docs_archive = await self._create_docs_archive(release_config)
            if docs_archive:
                asset = ReleaseAsset(
                    name=os.path.basename(docs_archive),
                    path=docs_archive,
                    content_type="application/zip",
                    size=os.path.getsize(docs_archive),
                    checksum=self._calculate_checksum(docs_archive),
                    description=f"Documentation archive for {release_config.version}"
                )
                assets.append(docs_archive)
            
            logger.info(f"Created {len(assets)} release assets")
            return assets
            
        except Exception as e:
            logger.error(f"Failed to create release assets: {e}")
            return []
    
    async def _create_source_archive(self, release_config: ReleaseConfig) -> Optional[str]:
        """Create source archive."""
        try:
            archive_path = f"releases/{release_config.tag_name}/source.zip"
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add source files
                for root, dirs, files in os.walk("src"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not file_path.endswith('.pyc'):
                            zipf.write(file_path, os.path.relpath(file_path, "."))
                
                # Add configuration files
                config_files = ["pyproject.toml", "requirements.txt", "config.yaml"]
                for file in config_files:
                    if os.path.exists(file):
                        zipf.write(file, file)
            
            logger.info(f"Source archive created: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create source archive: {e}")
            return None
    
    async def _create_docs_archive(self, release_config: ReleaseConfig) -> Optional[str]:
        """Create documentation archive."""
        try:
            if not os.path.exists("docs"):
                return None
            
            archive_path = f"releases/{release_config.tag_name}/docs.zip"
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk("docs"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, "docs"))
            
            logger.info(f"Documentation archive created: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create documentation archive: {e}")
            return None
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def execute_release(self, release_config: ReleaseConfig) -> ReleaseInfo:
        """Execute release process."""
        logger.info(f"Executing release: {release_config.tag_name}")
        
        # Check if working directory is clean
        status = self.git_manager.get_working_tree_status()
        if any(status.values()):
            raise Exception("Working directory is not clean. Please commit or stash changes.")
        
        # Create release assets
        assets = await self.create_release_assets(release_config)
        
        # Update changelog
        self.changelog_manager.update_changelog_file(release_config.body, str(release_config.version))
        
        # Commit changelog changes
        self.git_manager.commit_changes(
            f"Update changelog for {release_config.tag_name}",
            [self.changelog_manager.changelog_file]
        )
        
        # Create git tag
        tag_message = f"Release {release_config.tag_name}\n\n{release_config.release_notes}"
        self.git_manager.create_tag(release_config.tag_name, tag_message)
        
        # Create release info
        release_info = ReleaseInfo(
            release_id=str(uuid.uuid4()),
            version=release_config.version,
            release_type=release_config.release_type,
            status=ReleaseStatus.READY,
            created_at=datetime.now(),
            tag_name=release_config.tag_name,
            target_commitish=release_config.target_commitish,
            assets=assets,
            body=release_config.body
        )
        
        # Store release info
        self.releases.append(release_info)
        
        logger.info(f"Release executed successfully: {release_config.tag_name}")
        return release_info
    
    async def publish_release(self, release_info: ReleaseInfo, remote: str = "origin") -> ReleaseInfo:
        """Publish release to remote."""
        logger.info(f"Publishing release: {release_info.tag_name}")
        
        try:
            # Push changes to remote
            self.git_manager.run_git_command(["push", remote, release_info.target_commitish])
            
            # Push tag to remote
            self.git_manager.push_tag(release_info.tag_name, remote)
            
            # Update release status
            release_info.status = ReleaseStatus.PUBLISHED
            release_info.published_at = datetime.now()
            
            logger.info(f"Release published successfully: {release_info.tag_name}")
            return release_info
            
        except Exception as e:
            logger.error(f"Failed to publish release: {e}")
            release_info.status = ReleaseStatus.READY
            return release_info
    
    async def rollback_release(self, release_info: ReleaseInfo) -> bool:
        """Rollback release."""
        logger.info(f"Rolling back release: {release_info.tag_name}")
        
        try:
            # Delete local tag
            self.git_manager.run_git_command(["tag", "-d", release_info.tag_name])
            
            # Delete remote tag if it exists
            try:
                self.git_manager.run_git_command(["push", "origin", f":refs/tags/{release_info.tag_name}"])
            except subprocess.CalledProcessError:
                pass  # Tag might not exist on remote
            
            # Update release status
            release_info.status = ReleaseStatus.ARCHIVED
            
            logger.info(f"Release rolled back successfully: {release_info.tag_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback release: {e}")
            return False
    
    def get_release_history(self, limit: int = 10) -> List[ReleaseInfo]:
        """Get release history."""
        return self.releases[-limit:]
    
    def get_release_by_tag(self, tag_name: str) -> Optional[ReleaseInfo]:
        """Get release by tag name."""
        for release in self.releases:
            if release.tag_name == tag_name:
                return release
        return None


class VersionReleaseSystem:
    """Version release system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.release_manager = ReleaseManager(config.get("repo_path", "."))
        self.production_system = get_production_ready_system()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize version release system."""
        try:
            await self.production_system.initialize()
            self.is_initialized = True
            logger.info("Version release system initialized successfully")
        except Exception as e:
            logger.error(f"Version release system initialization failed: {e}")
            raise
    
    async def create_release(self, 
                           release_type: ReleaseType,
                           release_notes: str,
                           pre_release: bool = False,
                           draft: bool = False,
                           auto_publish: bool = False) -> ReleaseInfo:
        """Create and optionally publish release."""
        if not self.is_initialized:
            raise Exception("System not initialized")
        
        # Prepare release
        release_config = await self.release_manager.prepare_release(
            release_type, release_notes, pre_release, draft
        )
        
        # Execute release
        release_info = await self.release_manager.execute_release(release_config)
        
        # Publish if requested
        if auto_publish and not draft:
            release_info = await self.release_manager.publish_release(release_info)
        
        return release_info
    
    async def create_hotfix_release(self, 
                                  fix_description: str,
                                  auto_publish: bool = True) -> ReleaseInfo:
        """Create hotfix release."""
        return await self.create_release(
            ReleaseType.HOTFIX,
            fix_description,
            pre_release=False,
            draft=False,
            auto_publish=auto_publish
        )
    
    async def get_release_statistics(self) -> Dict[str, Any]:
        """Get release statistics."""
        releases = self.release_manager.get_release_history(limit=100)
        
        stats = {
            "total_releases": len(releases),
            "release_types": {},
            "recent_releases": [],
            "average_assets_per_release": 0
        }
        
        # Count release types
        for release in releases:
            release_type = release.release_type.value
            stats["release_types"][release_type] = stats["release_types"].get(release_type, 0) + 1
        
        # Recent releases
        stats["recent_releases"] = [
            {
                "tag": release.tag_name,
                "version": str(release.version),
                "type": release.release_type.value,
                "status": release.status.value,
                "created_at": release.created_at.isoformat(),
                "assets_count": len(release.assets)
            }
            for release in releases[-5:]
        ]
        
        # Average assets per release
        if releases:
            total_assets = sum(len(release.assets) for release in releases)
            stats["average_assets_per_release"] = total_assets / len(releases)
        
        return stats


# Global instance
_version_release_system: Optional[VersionReleaseSystem] = None


def get_version_release_system() -> VersionReleaseSystem:
    """Get global version release system instance."""
    global _version_release_system
    if _version_release_system is None:
        config = {
            "repo_path": ".",
            "auto_publish": False,
            "create_assets": True
        }
        _version_release_system = VersionReleaseSystem(config)
    return _version_release_system


async def initialize_version_release_system(config: Dict[str, Any]):
    """Initialize version release system."""
    global _version_release_system
    _version_release_system = VersionReleaseSystem(config)
    await _version_release_system.initialize()