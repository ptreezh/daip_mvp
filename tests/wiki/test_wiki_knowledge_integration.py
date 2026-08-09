"""
Wiki知识库集成的TDD测试用例
遵循RED-GREEN-REFACTOR循环
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

from daip_live.wiki.manager import WikiManager


class TestWikiKnowledgeIntegration:
    """Wiki知识库集成功能的测试套件"""

    def test_wiki_export_to_markdown_files(self):
        """测试导出为Markdown文件"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "export"
            manager = WikiManager(wiki_root)

            # 创建测试页面
            manager.create_page(
                "Python Guide",
                "# Python Guide\n\nThis is a comprehensive Python guide.",
                ["python", "guide"],
            )
            manager.create_page(
                "Algorithm Notes",
                "# Algorithms\n\nSorting, searching, and more.",
                ["algorithms", "notes"],
            )

            # Act & Assert - 这个测试在知识库集成实现之前会失败
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_to_markdown(export_dir)

            assert success is True
            assert export_dir.exists()
            assert (export_dir / "Python_Guide.md").exists()
            assert (export_dir / "Algorithm_Notes.md").exists()

            # 验证文件内容
            content = (export_dir / "Python_Guide.md").read_text(encoding="utf-8")
            assert "# Python Guide" in content
            assert "This is a comprehensive Python guide." in content

    def test_wiki_export_to_html_structure(self):
        """测试导出为HTML结构"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "html_export"
            manager = WikiManager(wiki_root)

            manager.create_page(
                "Main Page", "# Main Page\n\nWelcome to the wiki!", ["main"]
            )
            manager.create_page(
                "Sub Page", "# Sub Page\n\nDetailed information.", ["sub"]
            )

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_to_html(export_dir)

            assert success is True
            assert export_dir.exists()
            assert (export_dir / "index.html").exists()
            assert (export_dir / "pages" / "Main_Page.html").exists()
            assert (export_dir / "pages" / "Sub_Page.html").exists()

    def test_wiki_export_to_obsidian_format(self):
        """测试导出为Obsidian格式"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "obsidian"
            manager = WikiManager(wiki_root)

            manager.create_page(
                "Project Ideas",
                "# Project Ideas\n\n- AI Assistant\n- Wiki System",
                ["projects", "ideas"],
            )
            manager.create_page(
                "Meeting Notes",
                "# Meeting Notes\n\nDiscussed new features.",
                ["meetings", "notes"],
            )

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_to_obsidian(export_dir)

            assert success is True
            assert export_dir.exists()
            assert (export_dir / "Project Ideas.md").exists()
            assert (export_dir / "Meeting Notes.md").exists()

            # 验证Obsidian格式特性（如内部链接）
            content = (export_dir / "Project Ideas.md").read_text(encoding="utf-8")
            assert "# Project Ideas" in content

    def test_wiki_generate_tag_index(self):
        """测试生成标签索引"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "export"
            manager = WikiManager(wiki_root)

            manager.create_page("Python Basics", "Python basics", ["python", "basics"])
            manager.create_page(
                "Python Advanced", "Python advanced", ["python", "advanced"]
            )
            manager.create_page("Java Intro", "Java introduction", ["java", "intro"])

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.generate_tag_index(export_dir)

            assert success is True
            assert (export_dir / "tags" / "python.md").exists()
            assert (export_dir / "tags" / "java.md").exists()

            # 验证标签页面内容
            python_content = (export_dir / "tags" / "python.md").read_text(
                encoding="utf-8"
            )
            assert "Python Basics" in python_content
            assert "Python Advanced" in python_content

    def test_wiki_create_full_site_structure(self):
        """测试创建完整站点结构"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "site"
            manager = WikiManager(wiki_root)

            # 创建页面层次结构
            manager.create_page("Home", "# Home\n\nMain page", ["main"])
            manager.create_page("User Guide", "# User Guide\n\nHow to use", ["guide"])
            manager.create_page("API Reference", "# API\n\nTechnical details", ["api"])

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.create_full_site(export_dir, format="markdown")

            assert success is True
            assert (export_dir / "index.md").exists()  # 主页
            assert (export_dir / "pages" / "User_Guide.md").exists()
            assert (export_dir / "pages" / "API_Reference.md").exists()
            assert (export_dir / "assets" / "css").exists()  # 样式目录

    def test_wiki_export_with_custom_template(self):
        """测试使用自定义模板导出"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "custom_export"
            template_dir = Path(temp_dir) / "templates"

            # 创建自定义模板
            template_dir.mkdir()
            (template_dir / "page.html").write_text(
                """
<!DOCTYPE html>
<html>
<head><title>{{title}}</title></head>
<body>
<h1>{{title}}</h1>
<div class="content">{{content}}</div>
<div class="tags">{{tags}}</div>
</body>
</html>
            """,
                encoding="utf-8",
            )

            manager = WikiManager(wiki_root)
            manager.create_page("Test Page", "# Test\n\nContent", ["test"])

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_with_template(
                export_dir, template_dir / "page.html", format="html"
            )

            assert success is True
            output_file = export_dir / "Test_Page.html"
            assert output_file.exists()

            content = output_file.read_text(encoding="utf-8")
            assert "<title>Test Page</title>" in content
            assert "<h1>Test Page</h1>" in content

    def test_wiki_export_preserves_metadata(self):
        """测试导出时保留元数据"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "meta_export"
            manager = WikiManager(wiki_root)

            created_time = datetime(2023, 1, 1, 10, 0, 0)
            modified_time = datetime(2023, 1, 2, 15, 30, 0)

            page = manager.create_page(
                "Metadata Test", "Content with metadata", ["metadata", "test"]
            )
            # 模拟修改时间（在实际实现中会更复杂）
            page.created_at = created_time
            page.modified_at = modified_time

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_with_metadata(export_dir, format="json")

            assert success is True
            metadata_file = export_dir / "metadata.json"
            assert metadata_file.exists()

            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            assert "pages" in metadata
            assert len(metadata["pages"]) == 1

            page_meta = metadata["pages"][0]
            assert page_meta["title"] == "Metadata Test"
            assert page_meta["tags"] == ["metadata", "test"]

    def test_wiki_cross_reference_links(self):
        """测试交叉引用链接生成"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "links_export"
            manager = WikiManager(wiki_root)

            manager.create_page(
                "Page One", "See [[Page Two]] for more details.", ["page1"]
            )
            manager.create_page("Page Two", "Referenced from [[Page One]].", ["page2"])

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_with_cross_references(
                export_dir, format="markdown"
            )

            assert success is True

            # 验证交叉引用链接
            content1 = (export_dir / "Page_One.md").read_text(encoding="utf-8")
            content2 = (export_dir / "Page_Two.md").read_text(encoding="utf-8")

            # 在实际实现中会处理Wiki链接转换
            assert "Page Two" in content1
            assert "Page One" in content2

    def test_wiki_export_search_index(self):
        """测试导出搜索索引"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "search_export"
            manager = WikiManager(wiki_root)

            manager.create_page(
                "Search Test", "Content about search functionality", ["search", "test"]
            )
            manager.create_page(
                "Index Guide", "How to use the index", ["index", "guide"]
            )

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.create_search_index(export_dir)

            assert success is True
            index_file = export_dir / "search_index.json"
            assert index_file.exists()

            index_data = json.loads(index_file.read_text(encoding="utf-8"))
            assert "documents" in index_data
            assert len(index_data["documents"]) == 2

            # 验证索引包含必要字段
            for doc in index_data["documents"]:
                assert "title" in doc
                assert "content" in doc
                assert "tags" in doc
                assert "url" in doc

    def test_wiki_export_validation(self):
        """测试导出验证功能"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "validated_export"
            manager = WikiManager(wiki_root)

            manager.create_page("Valid Page", "Valid content", ["valid"])

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_with_validation(export_dir, format="markdown")

            assert success is True

            # 验证导出结果
            validation_result = exporter.validate_export(export_dir)
            assert validation_result.is_valid is True
            assert len(validation_result.errors) == 0
            assert len(validation_result.warnings) == 0

    def test_wiki_incremental_export(self):
        """测试增量导出功能"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "incremental_export"
            manager = WikiManager(wiki_root)

            # 初始导出
            manager.create_page("Page 1", "Content 1", ["page1"])

            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            initial_success = exporter.export_to_markdown(export_dir)
            assert initial_success is True

            # 添加新页面
            manager.create_page("Page 2", "Content 2", ["page2"])

            # Act - 增量导出
            incremental_success = exporter.incremental_export(export_dir)

            # Assert
            assert incremental_success is True
            assert (export_dir / "Page_2.md").exists()
            assert (export_dir / "Page_1.md").exists()  # 原有文件应该仍然存在

    def test_wiki_export_configuration(self):
        """测试导出配置功能"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "configured_export"
            manager = WikiManager(wiki_root)

            manager.create_page("Configured Page", "Content", ["config"])

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            # 配置导出选项
            config = {
                "include_tags": True,
                "include_metadata": True,
                "create_index": True,
                "custom_css": True,
                "date_format": "%Y-%m-%d",
                "max_preview_length": 200,
            }

            success = exporter.export_with_configuration(export_dir, config)

            assert success is True
            assert (export_dir / "Configured_Page.md").exists()
            assert (export_dir / "index.md").exists()  # 配置要求创建索引

    def test_wiki_export_error_handling(self):
        """测试导出错误处理"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            # 跨平台无效路径：含 NUL 字符（Windows 和 Linux 均无法创建）
            invalid_export_dir = Path(temp_dir) / "\x00invalid"
            manager = WikiManager(wiki_root)

            manager.create_page("Test Page", "Content", ["test"])

            # Act & Assert
            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter

            exporter = WikiKnowledgeExporter(manager)

            success = exporter.export_to_markdown(invalid_export_dir)

            assert success is False

            # 验证错误信息
            error_info = exporter.get_last_error()
            assert error_info is not None
            assert (
                "failed" in error_info.lower()
                or "error" in error_info.lower()
                or "invalid" in error_info.lower()
            )
