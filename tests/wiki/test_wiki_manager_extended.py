"""
WikiManager扩展功能的测试用例
验证REFACTOR阶段新增的高级功能
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import json

from daip_live.wiki.manager import WikiManager, WikiStatistics


class TestWikiManagerExtended:
    """WikiManager扩展功能的测试套件"""

    def test_wiki_manager_statistics_empty_wiki(self):
        """测试空Wiki的统计信息"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # Act
            stats = manager.get_statistics()

            # Assert
            assert stats.total_pages == 0
            assert stats.total_tags == 0
            assert stats.total_words == 0
            assert stats.most_used_tags == []
            assert stats.pages_by_reading_time == {}

    def test_wiki_manager_statistics_with_content(self):
        """测试有内容的Wiki统计信息"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # 创建多个页面
            manager.create_page("Python Guide", "Python is a programming language", ["python", "programming"])
            manager.create_page("Java Tutorial", "Java is also a programming language", ["java", "programming"])
            manager.create_page("Python Tips", "Python tips and tricks", ["python", "tips"])
            manager.create_page("Short Note", "Brief content", ["notes"])

            # Act
            stats = manager.get_statistics()

            # Assert
            assert stats.total_pages == 4
            assert stats.total_tags == 5  # python, programming, java, tips, notes
            assert stats.total_words > 0

            # 验证最常用标签
            tag_names = [tag for tag, count in stats.most_used_tags]
            assert "python" in tag_names
            assert "programming" in tag_names

            # 验证阅读时间分布
            assert len(stats.pages_by_reading_time) > 0

    def test_wiki_manager_batch_create_pages_success(self):
        """测试批量创建页面成功"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            pages_data = [
                {"title": "Page 1", "content": "Content 1", "tags": ["tag1"]},
                {"title": "Page 2", "content": "Content 2", "tags": ["tag2"]},
                {"title": "Page 3", "content": "Content 3", "tags": ["tag3"]},
            ]

            # Act
            created_pages = manager.batch_create_pages(pages_data)

            # Assert
            assert len(created_pages) == 3
            assert manager.get_page_count() == 3
            for i, page in enumerate(created_pages):
                assert page.title == f"Page {i+1}"
                assert page.content == f"Content {i+1}"

    def test_wiki_manager_batch_create_pages_with_invalid_title(self):
        """测试批量创建页面时包含无效标题"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            pages_data = [
                {"title": "Valid Page", "content": "Valid content", "tags": ["valid"]},
                # 源码权威: 空标题+非空内容会从内容提取标题（manager.py:144-156），
                # 只有标题和内容都空才抛 "Title cannot be empty"
                {"title": "", "content": "", "tags": ["invalid"]},  # 空标题+空内容
            ]

            # Act & Assert
            with pytest.raises(ValueError, match="Title cannot be empty"):
                manager.batch_create_pages(pages_data)

            # 确保没有创建任何页面（事务性）
            assert manager.get_page_count() == 0

    def test_wiki_manager_batch_create_pages_with_duplicate(self):
        """测试批量创建页面时包含重复标题"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # 先创建一个页面
            manager.create_page("Existing Page", "Existing content", ["existing"])

            pages_data = [
                {"title": "New Page", "content": "New content", "tags": ["new"]},
                {"title": "Existing Page", "content": "Duplicate content", "tags": ["duplicate"]},
            ]

            # Act & Assert
            with pytest.raises(ValueError, match="already exists"):
                manager.batch_create_pages(pages_data)

            # 确保只有原始页面存在
            assert manager.get_page_count() == 1
            assert manager.get_page_by_title("Existing Page") is not None
            assert manager.get_page_by_title("New Page") is None

    def test_wiki_manager_batch_delete_pages(self):
        """测试批量删除页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # 创建多个页面
            manager.create_page("Page 1", "Content 1", ["tag1"])
            manager.create_page("Page 2", "Content 2", ["tag2"])
            manager.create_page("Page 3", "Content 3", ["tag3"])

            # Act
            results = manager.batch_delete_pages(["Page 1", "Page 3", "Nonexistent Page"])

            # Assert
            assert results["Page 1"] is True
            assert results["Page 3"] is True
            assert results["Nonexistent Page"] is False
            assert manager.get_page_count() == 1
            assert manager.get_page_by_title("Page 2") is not None

    def test_wiki_manager_export_pages_markdown_format(self):
        """测试导出页面为Markdown格式"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            export_dir = Path(temp_dir) / "export"

            # 创建测试页面
            manager.create_page("Test Page", "# Test Content\n\nThis is a test.", ["test"])

            # Act
            manager.export_pages(export_dir, format='markdown')

            # Assert
            assert export_dir.exists()
            exported_file = export_dir / "test_page.md"
            assert exported_file.exists()

            with open(exported_file, 'r', encoding='utf-8') as f:
                content = f.read()
            assert "# Test Content" in content
            assert "This is a test." in content

    def test_wiki_manager_export_pages_json_format(self):
        """测试导出页面为JSON格式"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            export_dir = Path(temp_dir) / "export"

            # 创建测试页面
            manager.create_page("Test Page", "Test content", ["test"])

            # Act
            manager.export_pages(export_dir, format='json')

            # Assert
            assert export_dir.exists()
            exported_file = export_dir / "wiki_export.json"
            assert exported_file.exists()

            with open(exported_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)

            assert export_data['total_pages'] == 1
            assert 'export_date' in export_data
            assert len(export_data['pages']) == 1
            assert export_data['pages'][0]['title'] == "Test Page"

    def test_wiki_manager_export_pages_unsupported_format(self):
        """测试导出不支持的格式"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            export_dir = Path(temp_dir) / "export"

            # Act & Assert
            with pytest.raises(ValueError, match="Unsupported export format"):
                manager.export_pages(export_dir, format='unsupported')

    def test_wiki_manager_advanced_search_content_only(self):
        """测试高级搜索 - 仅内容"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            manager.create_page("Python Guide", "Content about Python programming", ["python"])
            manager.create_page("Java Tutorial", "Content about Java programming", ["java"])

            # Act
            results = manager.search_advanced("python", search_type='content')

            # Assert
            assert len(results) == 1
            assert results[0].title == "Python Guide"

    def test_wiki_manager_advanced_search_title_only(self):
        """测试高级搜索 - 仅标题"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            manager.create_page("Python Guide", "Content about Python programming", ["python"])
            manager.create_page("Learning Python", "Content for beginners", ["python", "beginner"])

            # Act
            results = manager.search_advanced("python", search_type='title')

            # Assert
            assert len(results) == 2
            titles = [page.title for page in results]
            assert "Python Guide" in titles
            assert "Learning Python" in titles

    def test_wiki_manager_advanced_search_both(self):
        """测试高级搜索 - 标题和内容"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            manager.create_page("Programming Guide", "Content about programming", ["guide"])
            manager.create_page("Tips", "Programming tips for beginners", ["tips"])
            manager.create_page("Learning", "General learning content", ["learning"])

            # Act
            results = manager.search_advanced("programming", search_type='both')

            # Assert
            assert len(results) == 2  # 标题匹配一个，内容匹配一个
            titles = [page.title for page in results]
            assert "Programming Guide" in titles
            assert "Tips" in titles

    def test_wiki_manager_advanced_search_with_tag_filter(self):
        """测试高级搜索 - 带标签过滤"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            manager.create_page("Python Basics", "Python programming basics", ["python", "basics"])
            manager.create_page("Python Advanced", "Advanced Python topics", ["python", "advanced"])
            manager.create_page("Java Basics", "Java programming basics", ["java", "basics"])

            # Act
            results = manager.search_advanced("basics", search_type='content', tags=["python"])

            # Assert
            assert len(results) == 1
            assert results[0].title == "Python Basics"

    def test_wiki_manager_advanced_search_invalid_type(self):
        """测试高级搜索 - 无效搜索类型"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # Act & Assert
            with pytest.raises(ValueError, match="Invalid search type: invalid"):
                manager.search_advanced("query", search_type='invalid')

    def test_wiki_manager_get_recent_pages(self):
        """测试获取最近修改的页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # 创建页面（会有不同的时间戳）
            page1 = manager.create_page("Page 1", "Content 1", ["test"])
            page2 = manager.create_page("Page 2", "Content 2", ["test"])
            page3 = manager.create_page("Page 3", "Content 3", ["test"])

            # 更新第一个页面使其成为最新
            import time
            time.sleep(0.1)  # 确保时间差
            manager.update_page("Page 1", "Updated content 1")

            # Act
            recent_pages = manager.get_recent_pages(limit=2)

            # Assert
            assert len(recent_pages) == 2
            assert recent_pages[0].title == "Page 1"  # 最新的是刚更新的页面
            assert recent_pages[1].title in ["Page 2", "Page 3"]

    def test_wiki_manager_get_recent_pages_limit(self):
        """测试获取最近页面的数量限制"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # 创建5个页面
            for i in range(5):
                manager.create_page(f"Page {i+1}", f"Content {i+1}", ["test"])

            # Act
            recent_pages = manager.get_recent_pages(limit=3)

            # Assert
            assert len(recent_pages) == 3

    def test_wiki_manager_empty_get_recent_pages(self):
        """测试空Wiki获取最近页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            # Act
            recent_pages = manager.get_recent_pages()

            # Assert
            assert len(recent_pages) == 0

    def test_wiki_manager_statistics_dataclass_structure(self):
        """测试统计信息数据结构"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)

            manager.create_page("Test", "Test content", ["test"])

            # Act
            stats = manager.get_statistics()

            # Assert - 验证数据结构
            assert isinstance(stats, WikiStatistics)
            assert isinstance(stats.total_pages, int)
            assert isinstance(stats.total_tags, int)
            assert isinstance(stats.total_words, int)
            assert isinstance(stats.last_updated, datetime)
            assert isinstance(stats.most_used_tags, list)
            assert isinstance(stats.pages_by_reading_time, dict)

            # 验证most_used_tags元素结构
            if stats.most_used_tags:
                tag, count = stats.most_used_tags[0]
                assert isinstance(tag, str)
                assert isinstance(count, int)