"""
Wiki管理器核心服务

遵循TDD RED-GREEN-REFACTOR循环开发
"""

import json
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from .models import WikiPage


@dataclass
class WikiStatistics:
    """Wiki统计信息"""
    total_pages: int
    total_tags: int
    total_words: int
    last_updated: datetime
    most_used_tags: List[tuple]
    pages_by_reading_time: Dict[str, int]


class WikiError(Exception):
    """Wiki管理器基础异常"""
    pass


class PageNotFoundError(WikiError):
    """页面未找到异常"""
    pass


class PageAlreadyExistsError(WikiError):
    """页面已存在异常"""
    pass


class InvalidTitleError(WikiError):
    """无效标题异常"""
    pass


class WikiManager:
    """Wiki管理器

    提供Wiki页面的创建、管理、搜索功能。
    支持持久化存储、标签管理、内容搜索等高级功能。
    """

    def __init__(self, wiki_root: Path, role_model_manager: Optional[RoleModelManager] = None, model_provider: Optional[LiteLLMProvider] = None):
        """初始化Wiki管理器

        Args:
            wiki_root: Wiki存储根目录
            role_model_manager: 角色模型管理器依赖
            model_provider: 模型提供者依赖
        """
        if not isinstance(wiki_root, Path):
            raise TypeError("wiki_root must be a Path object")

        self.wiki_root = wiki_root
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider
        
        self._ensure_directory_exists()
        self._pages: Dict[str, WikiPage] = {}
        self._load_existing_pages()

    def _ensure_directory_exists(self) -> None:
        """确保Wiki根目录存在"""
        self.wiki_root.mkdir(parents=True, exist_ok=True)

    def _get_page_file_path(self, title: str) -> Path:
        """根据标题生成页面文件路径"""
        # 清理标题中的特殊字符
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        clean_title = clean_title.strip('_').lower()

        return self.wiki_root / f"{clean_title}.md"

    def _get_index_file_path(self) -> Path:
        """获取索引文件路径"""
        return self.wiki_root / ".wiki_index.json"

    def _load_existing_pages(self) -> None:
        """加载已存在的页面"""
        index_file = self._get_index_file_path()
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

                for page_data in index_data.get('pages', []):
                    try:
                        page = WikiPage.from_dict(page_data)
                        self._pages[page.title] = page
                    except Exception:
                        # 跳过损坏的页面数据
                        continue
            except (json.JSONDecodeError, KeyError):
                # 如果索引文件损坏，忽略它
                pass

    def _save_index(self) -> None:
        """保存页面索引"""
        index_file = self._get_index_file_path()
        index_data = {
            'pages': [page.to_dict() for page in self._pages.values()],
            'last_updated': datetime.now().isoformat()
        }

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    def get_page_count(self) -> int:
        """获取页面总数"""
        return len(self._pages)

    def create_page(self, title: str, content: str, tags: Optional[List[str]] = None) -> WikiPage:
        """创建新的Wiki页面

        Args:
            title: 页面标题
            content: 页面内容
            tags: 页面标签列表

        Returns:
            WikiPage: 创建的页面对象

        Raises:
            ValueError: 如果标题为空或已存在（保持向后兼容）
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        if title in self._pages:
            raise ValueError(f"Page with title '{title}' already exists")

        now = datetime.now()
        file_path = self._get_page_file_path(title)

        page = WikiPage(
            title=title.strip(),
            content=content,
            file_path=file_path,
            created_at=now,
            modified_at=now,
            tags=tags or []
        )

        # 保存页面到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 添加到内存和索引
        self._pages[title] = page
        self._save_index()

        return page

    def get_page_by_title(self, title: str) -> Optional[WikiPage]:
        """根据标题获取页面

        Args:
            title: 页面标题

        Returns:
            Optional[WikiPage]: 页面对象，如果不存在返回None
        """
        return self._pages.get(title)

    def list_all_pages(self) -> List[WikiPage]:
        """列出所有页面

        Returns:
            List[WikiPage]: 所有页面列表
        """
        return list(self._pages.values())

    def search_pages_by_tag(self, tag: str) -> List[WikiPage]:
        """按标签搜索页面

        Args:
            tag: 搜索标签

        Returns:
            List[WikiPage]: 包含指定标签的页面列表
        """
        return [page for page in self._pages.values() if page.has_tag(tag)]

    def search_pages_by_content(self, search_term: str) -> List[WikiPage]:
        """按内容搜索页面

        Args:
            search_term: 搜索关键词

        Returns:
            List[WikiPage]: 包含指定关键词的页面列表
        """
        search_term_lower = search_term.lower()
        return [
            page for page in self._pages.values()
            if search_term_lower in page.content.lower()
        ]

    def update_page(self, title: str, new_content: str, new_tags: Optional[List[str]] = None) -> WikiPage:
        """更新现有页面

        Args:
            title: 页面标题
            new_content: 新内容
            new_tags: 新标签列表

        Returns:
            WikiPage: 更新后的页面对象

        Raises:
            ValueError: 如果页面不存在（保持向后兼容）
        """
        if title not in self._pages:
            raise ValueError(f"Page with title '{title}' not found")

        page = self._pages[title]
        page.update_content(new_content)

        if new_tags is not None:
            # 更新标签
            time.sleep(0.001)  # 确保时间戳差异
            page.tags = [tag for tag in new_tags if tag]  # 清理空标签
            page.modified_at = datetime.now()

        # 保存到文件
        with open(page.file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # 更新索引
        self._save_index()

        return page

    def delete_page(self, title: str) -> bool:
        """删除页面

        Args:
            title: 页面标题

        Returns:
            bool: 如果页面存在并被删除返回True，否则返回False
        """
        if title not in self._pages:
            return False

        page = self._pages[title]

        # 删除文件
        if page.file_path.exists():
            page.file_path.unlink()

        # 从内存中删除
        del self._pages[title]

        # 更新索引
        self._save_index()

        return True

    def get_all_tags(self) -> List[str]:
        """获取所有标签

        Returns:
            List[str]: 所有标签的列表（去重）
        """
        all_tags = set()
        for page in self._pages.values():
            all_tags.update(page.tags)
        return sorted(list(all_tags))

    def get_statistics(self) -> WikiStatistics:
        """获取Wiki统计信息

        Returns:
            WikiStatistics: 统计信息对象
        """
        if not self._pages:
            return WikiStatistics(
                total_pages=0,
                total_tags=0,
                total_words=0,
                last_updated=datetime.now(),
                most_used_tags=[],
                pages_by_reading_time={}
            )

        # 统计标签使用频率
        tag_count: Dict[str, int] = {}
        total_words = 0
        pages_by_reading_time: Dict[str, int] = {}

        for page in self._pages.values():
            # 统计标签
            for tag in page.tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1

            # 统计字数
            total_words += page.get_word_count()

            # 统计阅读时间分布
            reading_time = page.get_reading_time()
            time_category = f"{reading_time}min"
            pages_by_reading_time[time_category] = pages_by_reading_time.get(time_category, 0) + 1

        # 获取最常用的标签（前10个）
        most_used_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:10]

        return WikiStatistics(
            total_pages=len(self._pages),
            total_tags=len(self.get_all_tags()),
            total_words=total_words,
            last_updated=datetime.now(),
            most_used_tags=most_used_tags,
            pages_by_reading_time=pages_by_reading_time
        )

    def batch_create_pages(self, pages_data: List[Dict[str, Any]]) -> List[WikiPage]:
        """批量创建页面

        Args:
            pages_data: 页面数据列表，每个元素包含 title, content, tags

        Returns:
            List[WikiPage]: 创建的页面列表

        Raises:
            ValueError: 如果任何页面标题无效或已存在
        """
        created_pages = []

        for page_data in pages_data:
            try:
                page = self.create_page(
                    title=page_data['title'],
                    content=page_data['content'],
                    tags=page_data.get('tags', [])
                )
                created_pages.append(page)
            except ValueError as e:
                # 清理已创建的页面以保持一致性
                for created_page in created_pages:
                    try:
                        self.delete_page(created_page.title)
                    except Exception:
                        pass  # 忽略清理过程中的错误
                raise

        return created_pages

    def batch_delete_pages(self, titles: List[str]) -> Dict[str, bool]:
        """批量删除页面

        Args:
            titles: 要删除的页面标题列表

        Returns:
            Dict[str, bool]: 删除结果，键为标题，值为是否成功删除
        """
        results = {}
        for title in titles:
            results[title] = self.delete_page(title)
        return results

    def export_pages(self, output_dir: Path, format: str = 'markdown') -> None:
        """导出所有页面

        Args:
            output_dir: 输出目录
            format: 导出格式 ('markdown' 或 'json')

        Raises:
            ValueError: 如果格式不支持
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if format == 'markdown':
            for page in self._pages.values():
                output_path = output_dir / page.file_path.name
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(page.content)

        elif format == 'json':
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_pages': len(self._pages),
                'pages': [page.to_dict() for page in self._pages.values()]
            }

            output_path = output_dir / 'wiki_export.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def search_advanced(self, query: str, search_type: str = 'content', tags: Optional[List[str]] = None) -> List[WikiPage]:
        """高级搜索功能

        Args:
            query: 搜索关键词
            search_type: 搜索类型 ('content', 'title', 'both')
            tags: 可选的标签过滤条件

        Returns:
            List[WikiPage]: 搜索结果
        """
        # 首先验证搜索类型
        if search_type not in ['content', 'title', 'both']:
            raise ValueError(f"Invalid search type: {search_type}")

        results = []

        for page in self._pages.values():
            # 标签过滤
            if tags and not all(page.has_tag(tag) for tag in tags):
                continue

            # 内容搜索
            query_lower = query.lower()
            matches = False

            if search_type == 'content':
                matches = query_lower in page.content.lower()
            elif search_type == 'title':
                matches = query_lower in page.title.lower()
            elif search_type == 'both':
                matches = (query_lower in page.content.lower() or
                          query_lower in page.title.lower())

            if matches:
                results.append(page)

        return results

    def get_recent_pages(self, limit: int = 10) -> List[WikiPage]:
        """获取最近修改的页面

        Args:
            limit: 返回页面数量限制

        Returns:
            List[WikiPage]: 按修改时间排序的页面列表
        """
        sorted_pages = sorted(
            self._pages.values(),
            key=lambda page: page.modified_at,
            reverse=True
        )
        return sorted_pages[:limit]

    async def add_content_by_role(self, page_title: str, role_name: str, instruction: str) -> WikiPage:
        """使用指定角色的AI模型生成内容并追加到页面末尾"""
        if not self.role_model_manager or not self.model_provider:
            raise WikiError("WikiManager is not configured for AI content generation. RoleModelManager and ModelProvider must be provided.")

        page = self.get_page_by_title(page_title)
        if not page:
            raise PageNotFoundError(f"Page '{page_title}' not found.")

        # 获取角色的模型配置
        mapping = self.role_model_manager.get_role_model_mapping(role_name, use_debate_config=True)
        if not mapping:
            raise WikiError(f"Could not find model configuration for role '{role_name}'.")
        
        model_config = mapping.role_model_config

        # 构建Prompt
        prompt = f"""You are an AI assistant acting as the role '{role_name}'.
        The current content of the wiki page '{page_title}' is:
        ---
        {page.content}
        ---
        Your task is to add a new section based on the following instruction:
        Instruction: {instruction}
        
        Please provide only the new content to be added.
        """

        # 生成内容
        generated_content, _ = await self.model_provider.generate(
            prompt,
            model=model_config.model_name,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens
        )

        # 更新页面
        new_content = page.content + "\n\n---\n" + f"## Contribution by {role_name}\n\n" + generated_content
        return self.update_page(page_title, new_content)