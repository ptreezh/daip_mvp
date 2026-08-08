"""
WikiManager核心服务的TDD测试用例
遵循RED-GREEN-REFACTOR循环
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import json

from daip_live.wiki.models import WikiPage


class TestWikiManager:
    """WikiManager核心服务的完整测试套件"""

    def test_wiki_manager_creation_with_directory(self):
        """测试创建WikiManager实例"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)

            # Act & Assert - 这个测试在WikiManager实现之前会失败
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            assert manager.wiki_root == wiki_root
            assert wiki_root.exists()
            assert manager.get_page_count() == 0

    def test_wiki_manager_creates_directory_if_not_exists(self):
        """测试如果目录不存在则自动创建"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir) / "new_wiki"

            # Act
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # Assert
            assert wiki_root.exists()
            assert wiki_root.is_dir()
            assert manager.wiki_root == wiki_root

    def test_wiki_manager_create_new_page(self):
        """测试创建新的Wiki页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # Act
            page = manager.create_page(
                title="Test Page",
                content="# Test Page\n\nThis is a test page.",
                tags=["test", "documentation"]
            )

            # Assert
            assert page is not None
            assert page.title == "Test Page"
            assert "test" in page.tags
            assert "documentation" in page.tags
            assert manager.get_page_count() == 1
            assert page.file_path.exists()

    def test_wiki_manager_create_page_with_invalid_title(self):
        """测试创建页面时标题验证"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # Act & Assert
            # 源码权威: 空标题+非空内容会从内容首行提取标题（manager.py:144-156），
            # 只有标题和内容都为空才抛 "Title cannot be empty"
            with pytest.raises(ValueError, match="Title cannot be empty"):
                manager.create_page(title="", content="")

            with pytest.raises(ValueError, match="Title cannot be empty"):
                manager.create_page(title="   ", content="")

    def test_wiki_manager_create_page_duplicate_title(self):
        """测试创建重复标题的页面应该失败"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建第一个页面
            manager.create_page(
                title="Test Page",
                content="First page content",
                tags=["test"]
            )

            # Act & Assert - 尝试创建重复标题
            # 源码权威: manager.py:172 raise "Page 'Test Page' already exists and contains content..."
            with pytest.raises(ValueError, match="already exists"):
                manager.create_page(
                    title="Test Page",  # 相同标题
                    content="Second page content",
                    tags=["test2"]
                )

    def test_wiki_manager_get_page_by_title(self):
        """测试通过标题获取页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建测试页面
            created_page = manager.create_page(
                title="Searchable Page",
                content="Content for searching",
                tags=["search", "test"]
            )

            # Act
            found_page = manager.get_page_by_title("Searchable Page")

            # Assert
            assert found_page is not None
            assert found_page.title == "Searchable Page"
            assert found_page.content == "Content for searching"
            assert found_page.file_path == created_page.file_path

    def test_wiki_manager_get_nonexistent_page(self):
        """测试获取不存在的页面返回None"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # Act
            page = manager.get_page_by_title("Nonexistent Page")

            # Assert
            assert page is None

    def test_wiki_manager_list_all_pages(self):
        """测试列出所有页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建多个页面
            pages_data = [
                ("Page 1", "Content 1", ["tag1"]),
                ("Page 2", "Content 2", ["tag2"]),
                ("Page 3", "Content 3", ["tag3"])
            ]

            for title, content, tags in pages_data:
                manager.create_page(title=title, content=content, tags=tags)

            # Act
            all_pages = manager.list_all_pages()

            # Assert
            assert len(all_pages) == 3
            titles = [page.title for page in all_pages]
            assert "Page 1" in titles
            assert "Page 2" in titles
            assert "Page 3" in titles

    def test_wiki_manager_search_pages_by_tag(self):
        """测试按标签搜索页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建不同标签的页面
            manager.create_page("Python Guide", "Python content", ["python", "programming"])
            manager.create_page("Java Guide", "Java content", ["java", "programming"])
            manager.create_page("Python Tips", "Python tips", ["python", "tips"])
            manager.create_page("General Notes", "General content", ["notes"])

            # Act
            python_pages = manager.search_pages_by_tag("python")
            programming_pages = manager.search_pages_by_tag("programming")
            nonexistent_pages = manager.search_pages_by_tag("nonexistent")

            # Assert
            assert len(python_pages) == 2
            assert len(programming_pages) == 2
            assert len(nonexistent_pages) == 0

            python_titles = [page.title for page in python_pages]
            assert "Python Guide" in python_titles
            assert "Python Tips" in python_titles

    def test_wiki_manager_search_pages_by_content(self):
        """测试按内容搜索页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建包含不同内容的页面
            manager.create_page("Algorithm Guide", "Content about sorting algorithms", ["algorithms"])
            manager.create_page("Data Structures", "Content about data structures", ["data"])
            manager.create_page("Sorting Tips", "Tips for efficient sorting", ["tips"])

            # Act
            algorithm_pages = manager.search_pages_by_content("sorting")
            data_pages = manager.search_pages_by_content("data structures")
            nonexistent_pages = manager.search_pages_by_content("nonexistent term")

            # Assert
            assert len(algorithm_pages) == 2  # "Algorithm Guide" 和 "Sorting Tips"
            assert len(data_pages) == 1     # 只有 "Data Structures"
            assert len(nonexistent_pages) == 0

    def test_wiki_manager_update_existing_page(self):
        """测试更新现有页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建页面
            page = manager.create_page(
                title="Update Test",
                content="Original content",
                tags=["original"]
            )
            original_modified = page.modified_at

            # Act
            updated_page = manager.update_page(
                title="Update Test",
                new_content="# Updated Title\n\nUpdated content with more details",
                new_tags=["updated", "test"]
            )

            # Assert
            assert updated_page is not None
            assert updated_page.content == "# Updated Title\n\nUpdated content with more details"
            assert "updated" in updated_page.tags
            assert "test" in updated_page.tags
            assert updated_page.modified_at > original_modified

    def test_wiki_manager_update_nonexistent_page(self):
        """测试更新不存在的页面应该失败"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # Act & Assert
            with pytest.raises(ValueError, match="Page with title.*not found"):
                manager.update_page(
                    title="Nonexistent Page",
                    new_content="Updated content",
                    new_tags=["updated"]
                )

    def test_wiki_manager_delete_page(self):
        """测试删除页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建页面
            manager.create_page("Delete Test", "Content to delete", ["test"])
            assert manager.get_page_count() == 1

            # Act
            result = manager.delete_page("Delete Test")

            # Assert
            assert result is True
            assert manager.get_page_count() == 0
            assert manager.get_page_by_title("Delete Test") is None

    def test_wiki_manager_delete_nonexistent_page(self):
        """测试删除不存在的页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # Act
            result = manager.delete_page("Nonexistent Page")

            # Assert
            assert result is False

    def test_wiki_manager_get_all_tags(self):
        """测试获取所有标签"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # 创建带不同标签的页面
            manager.create_page("Page 1", "Content 1", ["python", "algorithms"])
            manager.create_page("Page 2", "Content 2", ["java", "algorithms"])
            manager.create_page("Page 3", "Content 3", ["python", "tips"])

            # Act
            all_tags = manager.get_all_tags()

            # Assert
            expected_tags = {"python", "algorithms", "java", "tips"}
            assert set(all_tags) == expected_tags

    def test_wiki_manager_persistence_saves_and_loads(self):
        """测试持久化保存和加载功能"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager

            # 创建第一个管理器实例并添加数据
            manager1 = WikiManager(wiki_root)
            page1 = manager1.create_page("Persistent Page", "Persistent content", ["persistent"])

            # Act - 创建新的管理器实例应该加载已有数据
            manager2 = WikiManager(wiki_root)

            # Assert
            assert manager2.get_page_count() == 1
            loaded_page = manager2.get_page_by_title("Persistent Page")
            assert loaded_page is not None
            assert loaded_page.title == "Persistent Page"
            assert loaded_page.content == "Persistent content"
            assert "persistent" in loaded_page.tags

    def test_wiki_manager_file_naming_sanitization(self):
        """测试文件名清理功能"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.manager import WikiManager
            manager = WikiManager(wiki_root)

            # Act - 创建包含特殊字符的标题
            page = manager.create_page(
                title="Test Page!@#$%^&*()",
                content="Content",
                tags=["test"]
            )

            # Assert
            assert page is not None
            assert page.file_path.name == "test_page.md"  # 特殊字符被清理
            assert page.file_path.exists()