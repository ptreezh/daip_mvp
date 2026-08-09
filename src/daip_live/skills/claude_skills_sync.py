"""
Claude Skills 同步和管理模块
用于从GitHub等源下载和管理Claude兼容技能
"""

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import aiohttp
from pydantic import BaseModel, Field


class SkillManifest(BaseModel):
    """技能清单模型"""

    name: str
    version: str
    description: str
    manifest_version: str
    author: Optional[str] = None
    api: Optional[dict[str, Any]] = None
    tags: list[str] = Field(default_factory=list)
    tools: list[dict[str, Any]] = Field(default_factory=list)


class ClaudeSkillsManager:
    """Claude技能管理器 - 负责下载、安装和管理Claude兼容技能"""

    def __init__(self, skills_directory: str = "./claude_skills"):
        self.skills_directory = Path(skills_directory)
        self.skills_directory.mkdir(exist_ok=True)

    async def download_skill_from_github(
        self, repo_url: str, skill_name: str = None
    ) -> bool:
        """从GitHub仓库下载技能"""
        try:
            # 解析URL获取仓库信息
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) < 2:
                return False

            # 构建下载URL
            owner, repo = path_parts[0], path_parts[1]
            download_url = (
                f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
            )

            # 创建临时目录下载
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # 下载ZIP文件
                async with aiohttp.ClientSession() as session:
                    async with session.get(download_url) as response:
                        if response.status != 200:
                            # 尝试其他分支名
                            download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
                            async with session.get(download_url) as response:
                                if response.status != 200:
                                    return False

                        zip_path = temp_path / "repo.zip"
                        with open(zip_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)

                # 解压文件
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_path)

                # 查找包含 manifest.json 的目录
                extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir()]
                if not extracted_dirs:
                    return False

                extracted_dir = extracted_dirs[0]  # 通常是 repo-name-branch

                # 在提取的目录中查找包含 manifest.json 的子目录
                skill_dirs = []
                for item in extracted_dir.rglob("manifest.json"):
                    skill_dir = item.parent
                    skill_dirs.append(skill_dir)

                if not skill_dirs:
                    return False

                # 复制技能目录到本地技能目录
                for skill_dir in skill_dirs:
                    skill_name_from_path = skill_dir.name
                    target_dir = self.skills_directory / skill_name_from_path

                    # 如果目标目录已存在，先删除
                    if target_dir.exists():
                        shutil.rmtree(target_dir)

                    # 复制技能目录
                    shutil.copytree(skill_dir, target_dir)

                return True

        except Exception:
            return False

    async def download_skill_from_url(self, url: str) -> bool:
        """从URL下载单个技能"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return False

                    # 创建临时文件下载内容
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".zip"
                    ) as temp_file:
                        async for chunk in response.content.iter_chunked(8192):
                            temp_file.write(chunk)
                        temp_path = Path(temp_file.name)

            # 解压ZIP文件到技能目录
            try:
                with zipfile.ZipFile(temp_path, "r") as zip_ref:
                    # 获取所有文件名
                    file_names = zip_ref.namelist()

                    # 检查是否包含必要的技能文件
                    has_manifest = any("manifest.json" in name for name in file_names)
                    if not has_manifest:
                        return False

                    # 提取到技能目录
                    zip_ref.extractall(self.skills_directory)
                    return True

            finally:
                # 清理临时文件
                temp_path.unlink()

        except Exception:
            return False

    def load_skills_from_directory(self) -> list[SkillManifest]:
        """从本地目录加载所有技能"""
        manifests = []

        # 遍历技能目录中的所有子目录
        for skill_dir in self.skills_directory.iterdir():
            if skill_dir.is_dir():
                manifest_file = skill_dir / "manifest.json"
                tools_file = skill_dir / "tools.json"

                if manifest_file.exists():  # 只需要manifest.json
                    try:
                        import json

                        with open(manifest_file, encoding="utf-8") as f:
                            manifest_data = json.load(f)

                        # 加载tools.json如果存在
                        tools_data = []
                        if tools_file.exists():
                            with open(tools_file, encoding="utf-8") as f:
                                tools_data = json.load(f).get("tools", [])

                        manifest = SkillManifest(
                            name=manifest_data.get("name", skill_dir.name),
                            version=manifest_data.get("version", "1.0"),
                            description=manifest_data.get(
                                "description", f"Skill from {skill_dir.name}"
                            ),
                            manifest_version=manifest_data.get(
                                "manifest_version", "1.0"
                            ),
                            author=manifest_data.get("author"),
                            api=manifest_data.get("api"),
                            tags=manifest_data.get("tags", []),
                            tools=tools_data,
                        )

                        manifests.append(manifest)

                    except Exception:
                        pass

        return manifests

    def get_available_skill_names(self) -> list[str]:
        """获取所有可用技能名称"""
        manifests = self.load_skills_from_directory()
        return [manifest.name for manifest in manifests]

    def sync_official_skills(self) -> bool:
        """同步官方Claude技能仓库"""
        official_repos = [
            "https://github.com/anthropics/claude-tools",
            "https://github.com/anthropics/claude-computer-use-tools",
        ]

        success = True
        for repo_url in official_repos:
            try:
                # 由于同步是异步操作，这里需要特殊处理
                # 我们可以使用asyncio.run但需要在异步上下文中
                pass
            except Exception:
                success = False

        return success


# 同步异步版本的同步方法
async def sync_claude_skills_from_official_repo() -> bool:
    """异步同步官方Claude技能仓库"""
    manager = ClaudeSkillsManager()

    official_repos = [
        ("https://github.com/anthropics/claude-tools", "claude-tools"),
        (
            "https://github.com/anthropics/claude-computer-use-tools",
            "computer-use-tools",
        ),
    ]

    success = True
    for repo_url, repo_name in official_repos:
        try:
            result = await manager.download_skill_from_github(repo_url)
            if not result:
                # 可以在这里添加备用仓库
                success = False
        except Exception:
            success = False

    return success
