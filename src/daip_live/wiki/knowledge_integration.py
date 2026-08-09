"""
Wiki知识库集成模块

遵循TDD RED-GREEN-REFACTOR循环开发
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .manager import WikiManager
from .models import WikiPage


@dataclass
class ValidationResult:
    """导出验证结果"""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    missing_files: list[str]


class WikiKnowledgeExporter:
    """Wiki知识库导出器

    提供多种格式的Wiki内容导出功能，包括Markdown、HTML、Obsidian等格式。
    支持模板定制、交叉引用链接、搜索索引等高级功能。
    """

    def __init__(self, wiki_manager: WikiManager):
        """初始化导出器

        Args:
            wiki_manager: Wiki管理器实例
        """
        self.wiki_manager = wiki_manager
        self.last_error: Optional[str] = None

    def export_to_markdown(self, export_dir: Path) -> bool:
        """导出为Markdown文件

        Args:
            export_dir: 导出目录

        Returns:
            bool: 导出是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            pages = self.wiki_manager.list_all_pages()

            for page in pages:
                # 生成文件名
                filename = self._sanitize_filename(page.title) + ".md"
                filepath = export_dir / filename

                # 写入Markdown内容
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(page.content)

            return True
        except Exception as e:
            self.last_error = f"Export failed: {str(e)}"
            return False

    def export_to_html(self, export_dir: Path) -> bool:
        """导出为HTML结构

        Args:
            export_dir: 导出目录

        Returns:
            bool: 导出是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            pages_dir = export_dir / "pages"
            pages_dir.mkdir(exist_ok=True)

            pages = self.wiki_manager.list_all_pages()

            # 生成页面HTML文件
            for page in pages:
                filename = self._sanitize_filename(page.title) + ".html"
                filepath = pages_dir / filename

                html_content = self._markdown_to_html(page.content, page.title)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)

            # 生成主页索引
            self._generate_html_index(export_dir, pages)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def export_to_obsidian(self, export_dir: Path) -> bool:
        """导出为Obsidian格式

        Args:
            export_dir: 导出目录

        Returns:
            bool: 导出是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            pages = self.wiki_manager.list_all_pages()

            for page in pages:
                filename = page.title + ".md"  # Obsidian保持原始标题
                filepath = export_dir / filename

                # 处理内容，转换Wiki链接格式
                processed_content = self._process_obsidian_links(page.content)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(processed_content)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def generate_tag_index(self, export_dir: Path) -> bool:
        """生成标签索引

        Args:
            export_dir: 导出目录

        Returns:
            bool: 生成是否成功
        """
        try:
            tags_dir = export_dir / "tags"
            tags_dir.mkdir(parents=True, exist_ok=True)

            pages = self.wiki_manager.list_all_pages()
            tag_pages: dict[str, list[WikiPage]] = {}

            # 按标签分组页面
            for page in pages:
                for tag in page.tags:
                    if tag not in tag_pages:
                        tag_pages[tag] = []
                    tag_pages[tag].append(page)

            # 为每个标签生成索引页面
            for tag, tagged_pages in tag_pages.items():
                filename = f"{tag}.md"
                filepath = tags_dir / filename

                content = f"# {tag.title()}\n\n"
                content += f"包含此标签的页面 ({len(tagged_pages)} 个):\n\n"

                for page in tagged_pages:
                    content += (
                        f"- [{page.title}]({self._sanitize_filename(page.title)}.md)\n"
                    )

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def create_full_site(self, export_dir: Path, format: str = "markdown") -> bool:
        """创建完整站点结构

        Args:
            export_dir: 导出目录
            format: 导出格式

        Returns:
            bool: 创建是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)

            # 导出页面到pages子目录
            pages_dir = export_dir / "pages"
            if format == "markdown":
                success = self.export_to_markdown(pages_dir)
            elif format == "html":
                success = self.export_to_html(export_dir)
            else:
                return False

            if not success:
                return False

            # 生成标签索引
            self.generate_tag_index(export_dir)

            # 创建资源目录
            assets_dir = export_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            css_dir = assets_dir / "css"
            css_dir.mkdir(exist_ok=True)

            # 创建基本CSS文件
            css_content = """
/* Wiki Site Styles */
body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
h1, h2, h3 { color: #333; }
a { color: #0066cc; }
.tag { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
            """
            with open(css_dir / "style.css", "w", encoding="utf-8") as f:
                f.write(css_content)

            # 生成主页索引
            self._generate_site_index(export_dir)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def export_with_template(
        self, export_dir: Path, template_path: Path, format: str = "html"
    ) -> bool:
        """使用自定义模板导出

        Args:
            export_dir: 导出目录
            template_path: 模板文件路径
            format: 导出格式

        Returns:
            bool: 导出是否成功
        """
        try:
            if not template_path.exists():
                self.last_error = f"模板文件不存在: {template_path}"
                return False

            template_content = template_path.read_text(encoding="utf-8")
            export_dir.mkdir(parents=True, exist_ok=True)

            pages = self.wiki_manager.list_all_pages()

            for page in pages:
                # 替换模板变量
                rendered_content = template_content.replace("{{title}}", page.title)
                rendered_content = rendered_content.replace("{{content}}", page.content)
                rendered_content = rendered_content.replace(
                    "{{tags}}", ", ".join(page.tags)
                )

                filename = self._sanitize_filename(page.title) + ".html"
                filepath = export_dir / filename

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(rendered_content)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def export_with_metadata(self, export_dir: Path, format: str = "json") -> bool:
        """导出元数据

        Args:
            export_dir: 导出目录
            format: 导出格式

        Returns:
            bool: 导出是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            pages = self.wiki_manager.list_all_pages()

            metadata = {
                "export_date": datetime.now().isoformat(),
                "total_pages": len(pages),
                "pages": [],
            }

            for page in pages:
                page_metadata = {
                    "title": page.title,
                    "content": page.content,
                    "tags": page.tags,
                    "created_at": page.created_at.isoformat(),
                    "modified_at": page.modified_at.isoformat(),
                    "word_count": page.get_word_count(),
                    "reading_time": page.get_reading_time(),
                }
                metadata["pages"].append(page_metadata)

            metadata_file = export_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def export_with_cross_references(
        self, export_dir: Path, format: str = "markdown"
    ) -> bool:
        """导出交叉引用链接

        Args:
            export_dir: 导出目录
            format: 导出格式

        Returns:
            bool: 导出是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            pages = self.wiki_manager.list_all_pages()

            # 创建页面标题映射
            title_map = {page.title: page for page in pages}

            for page in pages:
                # 处理Wiki链接 [[Page Name]]
                processed_content = self._process_wiki_links(page.content, title_map)

                filename = self._sanitize_filename(page.title) + ".md"
                filepath = export_dir / filename

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(processed_content)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def create_search_index(self, export_dir: Path) -> bool:
        """创建搜索索引

        Args:
            export_dir: 导出目录

        Returns:
            bool: 创建是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            pages = self.wiki_manager.list_all_pages()

            search_index = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "documents": [],
            }

            for page in pages:
                # 简化的搜索索引
                doc = {
                    "id": page.title,
                    "title": page.title,
                    "content": page.content,
                    "tags": page.tags,
                    "url": f"{self._sanitize_filename(page.title)}.md",
                    "created_at": page.created_at.isoformat(),
                    "modified_at": page.modified_at.isoformat(),
                    "word_count": page.get_word_count(),
                }
                search_index["documents"].append(doc)

            index_file = export_dir / "search_index.json"
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(search_index, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def export_with_validation(
        self, export_dir: Path, format: str = "markdown"
    ) -> bool:
        """导出并验证

        Args:
            export_dir: 导出目录
            format: 导出格式

        Returns:
            bool: 导出是否成功
        """
        # 先执行导出
        if format == "markdown":
            success = self.export_to_markdown(export_dir)
        elif format == "html":
            success = self.export_to_html(export_dir)
        else:
            self.last_error = f"不支持的格式: {format}"
            return False

        if not success:
            return False

        # 执行验证
        validation_result = self.validate_export(export_dir)

        # 记录验证结果
        validation_file = export_dir / "validation_result.json"
        validation_data = {
            "is_valid": validation_result.is_valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "missing_files": validation_result.missing_files,
        }

        with open(validation_file, "w", encoding="utf-8") as f:
            json.dump(validation_data, f, ensure_ascii=False, indent=2)

        return validation_result.is_valid

    def incremental_export(self, export_dir: Path, format: str = "markdown") -> bool:
        """增量导出

        Args:
            export_dir: 导出目录
            format: 导出格式

        Returns:
            bool: 导出是否成功
        """
        try:
            # 检查是否已存在导出
            if not export_dir.exists():
                # 如果不存在，执行完整导出
                return (
                    self.export_to_markdown(export_dir)
                    if format == "markdown"
                    else self.export_to_html(export_dir)
                )

            # 导出所有页面（简化实现：总是重新导出所有文件）
            success = self.export_to_markdown(export_dir)

            return success
        except Exception as e:
            self.last_error = str(e)
            return False

    def export_with_configuration(
        self, export_dir: Path, config: dict[str, Any]
    ) -> bool:
        """使用配置导出

        Args:
            export_dir: 导出目录
            config: 导出配置

        Returns:
            bool: 导出是否成功
        """
        try:
            export_dir.mkdir(parents=True, exist_ok=True)

            # 执行基础导出到根目录（配置导出的特殊行为）
            success = self.export_to_markdown(export_dir)
            if not success:
                return False

            # 根据配置添加额外功能
            if config.get("create_index", False):
                self._generate_site_index(export_dir)

            if config.get("include_tags", False):
                self.generate_tag_index(export_dir)

            if config.get("include_metadata", False):
                self.export_with_metadata(export_dir)

            # 保存配置
            config_file = export_dir / "export_config.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def get_last_error(self) -> Optional[str]:
        """获取最后的错误信息

        Returns:
            Optional[str]: 错误信息
        """
        return self.last_error

    def validate_export(self, export_dir: Path) -> ValidationResult:
        """验证导出结果

        Args:
            export_dir: 导出目录

        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []
        missing_files = []

        try:
            pages = self.wiki_manager.list_all_pages()

            # 检查所有页面是否都已导出
            for page in pages:
                filename = self._sanitize_filename(page.title) + ".md"
                filepath = export_dir / filename

                if not filepath.exists():
                    missing_files.append(filename)
                    errors.append(f"缺失文件: {filename}")

            # 检查导出目录结构
            if not export_dir.exists():
                errors.append("导出目录不存在")

            # 检查空页面
            for page in pages:
                if not page.content.strip():
                    warnings.append(f"页面 '{page.title}' 内容为空")

        except Exception as e:
            errors.append(f"验证过程中出错: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            missing_files=missing_files,
        )

    # 私有辅助方法
    def _sanitize_filename(self, title: str) -> str:
        """清理文件名，移除不安全字符"""
        # 移除或替换不安全的字符
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", title)
        # 将空格替换为下划线
        sanitized = re.sub(r"\s+", "_", sanitized)
        # 移除多个连续的下划线
        sanitized = re.sub(r"_+", "_", sanitized)
        # 移除开头和结尾的下划线
        sanitized = sanitized.strip("_")
        return sanitized

    def _markdown_to_html(self, content: str, title: str) -> str:
        """简单的Markdown到HTML转换"""
        # 这是一个简化的实现，实际项目中应使用专业的Markdown解析器
        html = "<!DOCTYPE html>\n<html>\n<head>\n"
        html += f"<title>{title}</title>\n"
        html += '<meta charset="utf-8">\n'
        html += "</head>\n<body>\n"
        html += f"<h1>{title}</h1>\n"

        # 简单的Markdown转换
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                level = len(line) - len(line.lstrip("#"))
                text = line.lstrip("# ").strip()
                html += f"<h{level}>{text}</h{level}>\n"
            elif line.strip():
                html += f"<p>{line}</p>\n"

        html += "</body>\n</html>"
        return html

    def _process_obsidian_links(self, content: str) -> str:
        """处理Obsidian格式的链接"""
        # Obsidian使用 [[Page Name]] 格式的链接
        # 简化实现，保持原格式
        return content

    def _process_wiki_links(self, content: str, title_map: dict[str, WikiPage]) -> str:
        """处理Wiki链接 [[Page Name]]"""

        def replace_link(match):
            page_name = match.group(1)
            if page_name in title_map:
                target_file = f"{self._sanitize_filename(page_name)}.md"
                return f"[{page_name}]({target_file})"
            return match.group(0)

        # 替换 [[Page Name]] 格式的链接
        return re.sub(r"\[\[([^\]]+)\]\]", replace_link, content)

    def _generate_html_index(self, export_dir: Path, pages: list[WikiPage]) -> None:
        """生成HTML索引页面"""
        index_content = """<!DOCTYPE html>
<html>
<head>
    <title>Wiki Index</title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <h1>Wiki Index</h1>
    <ul>
"""
        for page in pages:
            filename = f"{self._sanitize_filename(page.title)}.html"
            index_content += (
                f'        <li><a href="pages/{filename}">{page.title}</a></li>\n'
            )

        index_content += """    </ul>
</body>
</html>
"""
        index_file = export_dir / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(index_content)

    def _generate_site_index(self, export_dir: Path) -> None:
        """生成站点索引"""
        pages = self.wiki_manager.list_all_pages()

        index_content = "# Wiki Index\n\n"
        index_content += f"共 {len(pages)} 个页面\n\n"
        index_content += "## 页面列表\n\n"

        for page in pages:
            filename = f"{self._sanitize_filename(page.title)}.md"
            tags_str = ", ".join(page.tags) if page.tags else ""
            index_content += f"- [{page.title}](pages/{filename})"
            if tags_str:
                index_content += f" - `{tags_str}`"
            index_content += "\n"

        index_file = export_dir / "index.md"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(index_content)

    def _is_valid_path(self, path: Path) -> bool:
        """检查路径是否有效

        Args:
            path: 要检查的路径

        Returns:
            bool: 路径是否有效
        """
        try:
            # 对于Unix风格的绝对路径（如/invalid/path），在Windows上无效
            if str(path).startswith("/") and not path.is_absolute():
                return False

            # 尝试解析路径，如果抛出异常则为无效路径
            resolved = path.resolve()

            # 检查路径是否包含明显的无效字符
            invalid_chars = '<>:"|?*'
            path_str = str(resolved)
            if any(char in path_str for char in invalid_chars):
                return False

            return True
        except (OSError, ValueError):
            return False
