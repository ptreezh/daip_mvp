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
        # 检查上下文以提供更好的参数提取
        if not title or not title.strip():
            # 尝试从内容中提取标题
            if content and len(content) > 0:
                # 提取内容的第一行或第一个标题作为标题
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                    elif line and not line.startswith("#"):
                        title = line[:50].strip()  # 取首行前50个字符作为标题
                        break

        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        # 检查页面是否已存在
        if title in self._pages:
            existing_page = self._pages[title]

            # 检查文档是否为空或只有默认模板内容
            if self._is_empty_document(existing_page.content):
                # 文档为空，直接返回当作新建的文档
                self._update_existing_page(existing_page, content, tags)
                return existing_page
            else:
                # 文档不为空，改为协同编辑模式
                raise ValueError(f"Page '{title}' already exists and contains content. Use collaborative editing instead.")

        # 处理标签，过滤空字符串
        processed_tags = []
        if tags:
            processed_tags = [tag.strip() for tag in tags if tag and tag.strip()]

        now = datetime.now()
        file_path = self._get_page_file_path(title)

        page = WikiPage(
            title=title.strip(),
            content=content,
            file_path=file_path,
            created_at=now,
            modified_at=now,
            tags=processed_tags
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

    # 多角色协作功能 - 用于AI协同创建Wiki内容
    async def _add_content_by_all_roles(
        self,
        page_title: str,
        roles_instructions: Dict[str, str],
        instruction: str = ""
    ) -> WikiPage:
        """使用多个角色的AI模型协同生成内容并添加到页面"""
        if not self.role_model_manager or not self.model_provider:
            raise WikiError("WikiManager is not configured for AI content generation. RoleModelManager and ModelProvider must be provided.")

        page = self.get_page_by_title(page_title)
        if not page:
            raise PageNotFoundError(f"Page '{page_title}' not found.")

        # 获取所有角色的模型配置
        all_content_parts = []

        for role_name, role_instruction in roles_instructions.items():
            try:
                mapping = self.role_model_manager.get_role_model_mapping(role_name, use_debate_config=True)
                if not mapping:
                    raise WikiError(f"Could not find model configuration for role '{role_name}'.")

                model_config = mapping.role_model_config

                # 构建Prompt
                full_instruction = f"{instruction} {role_instruction}".strip()
                prompt = f"""You are an AI assistant acting as the role '{role_name}'.
                The current content of the wiki page '{page_title}' is:
                ---
                {page.content}
                ---
                Your task is to contribute to this page based on the following instruction:
                Instruction: {full_instruction}

                Please provide only your contribution to add to this page.
                """

                # 修复模型名称格式：如果模型名不包含provider前缀，添加ollama前缀
                model_name = model_config.model_name
                if '/' not in model_name:
                    # 假设未指定provider的模型都是ollama模型
                    model_name = f"ollama/{model_name}"

                # 生成内容
                generated_content, _ = await self.model_provider.generate(
                    prompt,
                    model=model_name,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens
                )

                all_content_parts.append(f"### Contribution by {role_name}\n{generated_content}\n")

            except Exception as e:
                # 记录错误但继续处理其他角色
                print(f"Error generating content for role '{role_name}': {e}")
                continue

        if not all_content_parts:
            raise WikiError(f"Failed to generate content for any roles: {list(roles_instructions.keys())}")

        # 合并所有角色的贡献
        new_content = page.content + "\n\n---\n" + "\n".join(all_content_parts)

        # 更新页面
        return self.update_page(page_title, new_content)

    async def create_collaborative_page(
        self,
        title: str,
        initial_content: str = "",
        roles_instructions: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None
    ) -> WikiPage:
        """创建由多个AI角色协作完成的Wiki页面"""
        if roles_instructions is None:
            roles_instructions = {
                "domain_expert": "作为领域专家，请提供专业知识和核心技术要点",
                "researcher": "作为研究员，请提供研究依据和参考资料",
                "editor": "作为编辑，请负责内容结构和语言润色",
                "analyst": "作为分析师，请提供批判性思考和改进建议"
            }

        # 首先创建基础页面
        page = self.create_page(title, initial_content, tags or [])

        # 然后让多个角色协作丰富内容
        await self._add_content_by_all_roles(title, roles_instructions, f"协作完善维基词条: {title}")

        return page

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

    def _is_empty_document(self, content: str) -> bool:
        """检查文档是否为空（10字以下视为空，可直接覆盖）

        Args:
            content: 文档内容

        Returns:
            bool: True表示文档为空（可覆盖），False表示有内容（需要协同编辑）
        """
        if not content or not content.strip():
            return True

        content_stripped = content.strip()

        # 10字以下都视为空文件，直接覆盖
        if len(content_stripped) <= 10:
            return True

        # 定义常见的空文档或默认模板模式
        empty_patterns = [
            r'^#\s*$',  # 只有标题符号
            r'^#\s+\w+$',  # 只有标题和一个词
            r'^#\s+.*?\n\n开始编辑您的内容\.\.\.\s*$',  # 默认编辑提示
            r'^#\s+.*?\n\n开始协同创建关于.*的维基页面\.\.\.\s*$',  # 协同创建默认提示
            r'^#\s+.*?\n\n\s*$',  # 标题后只有空行
        ]

        # 检查是否匹配空文档模式
        for pattern in empty_patterns:
            if re.fullmatch(pattern, content_stripped, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                return True

        # 其他情况认为有内容
        return False

    def update_page_incremental(self, title: str, section_title: str, new_content: str,
                               action: str = 'replace', tags: Optional[List[str]] = None) -> WikiPage:
        """基于wiki原则的增量编辑功能

        Args:
            title: 页面标题
            section_title: 章节标题
            new_content: 新的内容
            action: 编辑动作 ('replace', 'append', 'prepend', 'merge')
            tags: 新的标签列表

        Returns:
            WikiPage: 更新后的页面对象

        Raises:
            ValueError: 如果页面不存在
        """
        if title not in self._pages:
            raise ValueError(f"Page with title '{title}' not found")

        page = self._pages[title]

        # 解析现有内容为章节
        sections = self._parse_content_into_sections(page.content)

        # 根据操作类型处理内容
        if section_title in sections:
            # 章节存在，根据action处理
            existing_content = sections[section_title]

            if action == 'replace':
                sections[section_title] = new_content
            elif action == 'append':
                sections[section_title] = existing_content + "\n\n" + new_content
            elif action == 'prepend':
                sections[section_title] = new_content + "\n\n" + existing_content
            elif action == 'merge':
                sections[section_title] = self._merge_content(existing_content, new_content)
            else:
                raise ValueError(f"Unsupported action: {action}")
        else:
            # 章节不存在，创建新章节
            if action in ['replace', 'merge']:
                sections[section_title] = new_content
            elif action == 'append':
                # 如果章节不存在，则追加到整个页面末尾
                page.content += f"\n\n## {section_title}\n{new_content}"
                # 重新解析章节
                sections = self._parse_content_into_sections(page.content)
            else:
                raise ValueError(f"Cannot '{action}' to non-existent section without creating it first")

        # 重组完整内容
        updated_content = self._reconstruct_content_from_sections(sections)

        # 更新页面
        page.update_content(updated_content)

        # 更新标签
        if tags is not None:
            page.tags = [tag for tag in tags if tag]  # 清理空标签
            page.modified_at = datetime.now()

        # 保存到文件
        with open(page.file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        # 更新索引
        self._save_index()

        return page

    def _parse_content_into_sections(self, content: str) -> Dict[str, str]:
        """将内容解析为章节字典"""
        sections = {}
        lines = content.split('\n')
        current_section = "概述"  # 默认章节
        current_content = []

        for line in lines:
            # 检查是否是标题行（## 或 #）
            if line.strip().startswith('#'):
                # 保存上一个章节
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # 提取新的章节标题
                # 处理不同级别的标题
                if line.strip().startswith('###'):
                    current_section = line.strip()[3:].strip()  # 移除 '###' 并去除空格
                elif line.strip().startswith('##'):
                    current_section = line.strip()[2:].strip()  # 移除 '##' 并去除空格
                elif line.strip().startswith('#'):
                    current_section = line.strip()[1:].strip()  # 移除 '#' 并去除空格

                current_content = []
            else:
                current_content.append(line)

        # 保存最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _reconstruct_content_from_sections(self, sections: Dict[str, str]) -> str:
        """从章节字典重构完整内容"""
        content_parts = []

        # 按顺序重建内容（通常概述部分在前）
        if "概述" in sections:
            content_parts.append(f"# 概述\n{sections['概述']}")
            del sections["概述"]

        # 添加其他章节
        for section_title, section_content in sections.items():
            content_parts.append(f"\n## {section_title}\n{section_content}")

        return '\n'.join(content_parts)

    def _merge_content(self, existing_content: str, new_content: str) -> str:
        """智能合并两个内容块"""
        # 简单的合并策略：保留现有内容，追加新内容，并尝试去重
        combined_content = existing_content + "\n\n" + new_content

        # 去除重复段落
        paragraphs = combined_content.split('\n\n')
        unique_paragraphs = []

        for para in paragraphs:
            para_stripped = para.strip()
            if para_stripped and para_stripped not in unique_paragraphs:
                unique_paragraphs.append(para_stripped)

        return '\n\n'.join(unique_paragraphs)

    def collaborative_edit_page(self, title: str, editor_role: str, edit_instruction: str,
                               section_title: Optional[str] = None) -> WikiPage:
        """协同编辑页面 - 基于wiki原则的多人协作编辑

        Args:
            title: 页面标题
            editor_role: 编辑者角色
            edit_instruction: 编辑指令
            section_title: 目标章节标题，如果为None则编辑整个页面

        Returns:
            WikiPage: 更新后的页面对象
        """
        if title not in self._pages:
            raise ValueError(f"Page with title '{title}' not found")

        page = self._pages[title]

        # 如果指定了章节，则只对章节进行编辑
        if section_title:
            # 这里可以集成AI模型来生成基于指令的编辑内容
            # 暂时用一个模拟的编辑过程
            edit_result = f"[{editor_role}的编辑贡献] {edit_instruction}"
            return self.update_page_incremental(title, section_title, edit_result, 'append')
        else:
            # 对整个页面进行编辑
            updated_content = page.content + f"\n\n<!-- {editor_role}编辑 -->\n{edit_instruction}"
            return self.update_page(title, updated_content, page.tags)

    def _update_existing_page(self, page: WikiPage, new_content: str, new_tags: Optional[List[str]] = None) -> None:
        """更新已存在的页面（用于空文档的情况）

        Args:
            page: 已存在的页面对象
            new_content: 新的内容
            new_tags: 新的标签列表
        """
        # 更新内容
        page.update_content(new_content)

        # 更新标签
        if new_tags is not None:
            page.tags = [tag for tag in new_tags if tag]  # 清理空标签
            page.modified_at = datetime.now()

        # 保存到文件
        with open(page.file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # 更新索引
        self._save_index()