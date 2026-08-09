"""
WikiPage数据模型的TDD测试用例
遵循RED-GREEN-REFACTOR循环
"""

from datetime import datetime
from pathlib import Path

import pytest

from daip_live.wiki.models import WikiPage


class TestWikiPage:
    """WikiPage数据模型的完整测试套件"""

    def test_wiki_page_creation_with_minimal_data(self):
        """测试最小数据创建Wiki页面"""
        # Arrange
        title = "Test Page"
        content = "# Test Page\n\nThis is a test page."
        file_path = Path("test_page.md")
        created_at = datetime.now()
        modified_at = created_at

        # Act & Assert - 这个测试在WikiPage实现之前会失败
        page = WikiPage(
            title=title,
            content=content,
            file_path=file_path,
            created_at=created_at,
            modified_at=modified_at,
        )

        assert page.title == title
        assert page.content == content
        assert page.file_path == file_path
        assert page.created_at == created_at
        assert page.modified_at == modified_at
        assert page.tags == []

    def test_wiki_page_creation_with_full_data(self):
        """测试完整数据创建Wiki页面"""
        # Arrange
        title = "Full Test Page"
        content = "# Full Test Page\n\nThis is a full test page with tags."
        file_path = Path("full_test_page.md")
        created_at = datetime.now()
        modified_at = created_at
        tags = ["test", "documentation", "wiki"]

        # Act & Assert
        page = WikiPage(
            title=title,
            content=content,
            file_path=file_path,
            created_at=created_at,
            modified_at=modified_at,
            tags=tags,
        )

        assert page.title == title
        assert page.content == content
        assert page.file_path == file_path
        assert page.created_at == created_at
        assert page.modified_at == modified_at
        assert page.tags == tags

    def test_wiki_page_content_update(self):
        """测试页面内容更新"""
        # Arrange
        created = datetime(2023, 1, 1, 10, 0, 0)
        modified = datetime(2023, 1, 1, 10, 30, 0)
        page = WikiPage(
            title="Test Page",
            content="Original content",
            file_path=Path("test.md"),
            created_at=created,
            modified_at=modified,
        )
        original_modified = page.modified_at
        new_content = "# Updated Title\n\nUpdated content"

        # Act
        page.update_content(new_content)

        # Assert
        assert page.content == new_content
        assert page.modified_at > original_modified
        assert page.created_at == created  # 创建时间不应改变

    def test_wiki_page_content_update_with_invalid_type(self):
        """测试无效类型的内容更新应该抛出异常"""
        # Arrange
        page = WikiPage(
            title="Test Page",
            content="Original content",
            file_path=Path("test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
        )

        # Act & Assert
        with pytest.raises(TypeError, match="Content must be a string"):
            page.update_content(123)  # 传入非字符串类型

    def test_wiki_page_tag_management_add_tag(self):
        """测试添加标签"""
        # Arrange
        page = WikiPage(
            title="Test Page",
            content="Content",
            file_path=Path("test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
        )

        # Act
        page.add_tag("python")
        page.add_tag("documentation")
        page.add_tag(
            "PYTHON"
        )  # 源码权威: validate_tag 保留大小写（models.py:15-25），PYTHON 是不同标签

        # Assert
        assert "python" in page.tags
        assert "documentation" in page.tags
        assert "PYTHON" in page.tags
        assert len(page.tags) == 3  # PYTHON 未规范化，与 python 并存

    def test_wiki_page_tag_management_add_empty_tag(self):
        """测试添加空标签应该抛出异常"""
        # Arrange
        page = WikiPage(
            title="Test Page",
            content="Content",
            file_path=Path("test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Tag cannot be empty"):
            page.add_tag("")

        with pytest.raises(ValueError, match="Tag cannot be empty"):
            page.add_tag("   ")  # 只有空格

    def test_wiki_page_tag_management_remove_tag(self):
        """测试移除标签"""
        # Arrange
        page = WikiPage(
            title="Test Page",
            content="Content",
            file_path=Path("test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
            tags=["python", "documentation", "wiki"],
        )

        # Act
        result1 = page.remove_tag("python")
        result2 = page.remove_tag("nonexistent")
        result3 = page.remove_tag(
            "DOCUMENTATION"
        )  # 源码权威: 大小写敏感（validate_tag 不规范化）

        # Assert
        assert result1 is True  # 成功移除
        assert result2 is False  # 标签不存在
        assert result3 is False  # DOCUMENTATION 与 documentation 大小写不同
        assert "python" not in page.tags
        assert "documentation" in page.tags  # documentation 未被移除（大小写敏感）
        assert "wiki" in page.tags
        assert len(page.tags) == 2

    def test_wiki_page_file_path_validation_markdown_only(self):
        """测试文件路径验证 - 只允许markdown文件"""
        # Act & Assert
        with pytest.raises(ValueError, match="Wiki page must be a markdown file"):
            WikiPage(
                title="Test",
                content="Content",
                file_path=Path("test.txt"),  # 非markdown文件
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )

        with pytest.raises(ValueError, match="Wiki page must be a markdown file"):
            WikiPage(
                title="Test",
                content="Content",
                file_path=Path("test"),  # 无扩展名
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )

    def test_wiki_page_empty_title_validation(self):
        """测试空标题验证"""
        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            WikiPage(
                title="",  # 空标题
                content="Content",
                file_path=Path("test.md"),
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )

        with pytest.raises(ValueError, match="Title cannot be empty"):
            WikiPage(
                title="   ",  # 只有空格
                content="Content",
                file_path=Path("test.md"),
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )

    def test_wiki_page_timestamp_management(self):
        """测试时间戳管理"""
        # Arrange
        created = datetime(2023, 1, 1, 10, 0, 0)
        modified = datetime(2023, 1, 1, 10, 30, 0)

        # Act
        page = WikiPage(
            title="Test Page",
            content="Content",
            file_path=Path("test.md"),
            created_at=created,
            modified_at=modified,
        )

        # Assert
        assert page.created_at == created
        assert page.modified_at == modified

        # 测试内容更新时修改时间自动更新
        page.update_content("Updated content")
        assert page.modified_at > modified
        assert page.created_at == created  # 创建时间不应改变

    def test_wiki_page_tags_parameter_immutability(self):
        """测试标签参数的不可变性"""
        # Arrange
        original_tags = ["tag1", "tag2"]
        page = WikiPage(
            title="Test Page",
            content="Content",
            file_path=Path("test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
            tags=original_tags.copy(),
        )

        # Act - 修改原始列表
        original_tags.append("tag3")

        # Assert - 页面标签不应受影响
        assert len(page.tags) == 2
        assert "tag3" not in page.tags
        assert page.tags == ["tag1", "tag2"]
