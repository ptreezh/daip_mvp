"""
WikiPage扩展功能的测试用例
验证REFACTOR阶段新增的高级功能
"""

import pytest
from datetime import datetime
from pathlib import Path
import json

from daip_live.wiki.models import WikiPage


class TestWikiPageExtended:
    """WikiPage扩展功能的测试套件"""

    def test_wiki_page_serialization_to_dict(self):
        """测试序列化为字典"""
        # Arrange
        created = datetime(2023, 1, 1, 10, 0, 0)
        modified = datetime(2023, 1, 1, 10, 30, 0)
        page = WikiPage(
            title="Test Page",
            content="# Test Page\n\nThis is a test page with **bold** text.",
            file_path=Path("test_page.md"),
            created_at=created,
            modified_at=modified,
            tags=["test", "documentation"]
        )

        # Act
        result = page.to_dict()

        # Assert
        expected_keys = {
            'title', 'content', 'file_path', 'created_at', 'modified_at',
            'tags', 'word_count', 'reading_time'
        }
        assert set(result.keys()) == expected_keys
        assert result['title'] == "Test Page"
        assert result['tags'] == ["test", "documentation"]
        assert result['word_count'] == 11  # "# Test Page\n\nThis is a test page with **bold** text."
        assert result['reading_time'] == 1  # 9 words / 200 per minute = 0.045 -> 1

    def test_wiki_page_serialization_to_json(self):
        """测试序列化为JSON"""
        # Arrange
        page = WikiPage(
            title="JSON Test",
            content="Content for JSON test",
            file_path=Path("json_test.md"),
            created_at=datetime(2023, 1, 1, 10, 0, 0),
            modified_at=datetime(2023, 1, 1, 10, 30, 0),
            tags=["json", "serialization"]
        )

        # Act
        json_str = page.to_json()
        data = json.loads(json_str)

        # Assert
        assert data['title'] == "JSON Test"
        assert data['content'] == "Content for JSON test"
        assert data['tags'] == ["json", "serialization"]

    def test_wiki_page_deserialization_from_dict(self):
        """测试从字典反序列化"""
        # Arrange
        data = {
            'title': "Dict Test",
            'content': "Content from dict",
            'file_path': "dict_test.md",
            'created_at': "2023-01-01T10:00:00",
            'modified_at': "2023-01-01T10:30:00",
            'tags': ["dict", "deserialization"]
        }

        # Act
        page = WikiPage.from_dict(data)

        # Assert
        assert page.title == "Dict Test"
        assert page.content == "Content from dict"
        assert page.file_path == Path("dict_test.md")
        assert page.tags == ["dict", "deserialization"]
        assert isinstance(page.created_at, datetime)
        assert isinstance(page.modified_at, datetime)

    def test_wiki_page_deserialization_from_json(self):
        """测试从JSON反序列化"""
        # Arrange
        json_str = json.dumps({
            'title': "JSON Test",
            'content': "Content from JSON",
            'file_path': "json_test.md",
            'created_at': "2023-01-01T10:00:00",
            'modified_at': "2023-01-01T10:30:00",
            'tags': ["json", "deserialization"]
        })

        # Act
        page = WikiPage.from_json(json_str)

        # Assert
        assert page.title == "JSON Test"
        assert page.content == "Content from JSON"
        assert page.file_path == Path("json_test.md")
        assert page.tags == ["json", "deserialization"]

    def test_wiki_page_content_preview_short_content(self):
        """测试短内容预览"""
        # Arrange
        page = WikiPage(
            title="Short Content",
            content="Short content",
            file_path=Path("short.md"),
            created_at=datetime.now(),
            modified_at=datetime.now()
        )

        # Act
        preview = page.get_content_preview(50)

        # Assert
        assert preview == "Short content"

    def test_wiki_page_content_preview_long_content(self):
        """测试长内容预览"""
        # Arrange
        long_content = "This is a very long content that should be truncated " * 10
        page = WikiPage(
            title="Long Content",
            content=long_content,
            file_path=Path("long.md"),
            created_at=datetime.now(),
            modified_at=datetime.now()
        )

        # Act
        preview = page.get_content_preview(50)

        # Assert
        assert preview.endswith("...")
        assert len(preview) <= 53  # 50 chars + "..."

    def test_wiki_page_word_count(self):
        """测试字数统计"""
        # Arrange
        page = WikiPage(
            title="Word Count Test",
            content="This is a test page with multiple words.",
            file_path=Path("word_count.md"),
            created_at=datetime.now(),
            modified_at=datetime.now()
        )

        # Act
        count = page.get_word_count()

        # Assert
        assert count == 8

    def test_wiki_page_reading_time_calculation(self):
        """测试阅读时间计算"""
        # Arrange
        page = WikiPage(
            title="Reading Time Test",
            content="This content has exactly fifty words. " * 5,  # 50 words
            file_path=Path("reading.md"),
            created_at=datetime.now(),
            modified_at=datetime.now()
        )

        # Act
        reading_time = page.get_reading_time()

        # Assert
        assert reading_time == 1  # 50 words / 200 per minute = 0.25 -> 1

    def test_wiki_page_has_tag_functionality(self):
        """测试标签检查功能"""
        # Arrange
        page = WikiPage(
            title="Tag Test",
            content="Content",
            file_path=Path("tag.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
            tags=["python", "wiki", "documentation"]
        )

        # Act & Assert
        assert page.has_tag("python") is True
        assert page.has_tag("PYTHON") is False  # 源码权威: 大小写敏感（validate_tag 不规范化）
        assert page.has_tag("java") is False
        assert page.has_tag("python") is True

    def test_wiki_page_content_history_tracking(self):
        """测试内容变更历史跟踪"""
        # Arrange
        page = WikiPage(
            title="History Test",
            content="Original content",
            file_path=Path("history.md"),
            created_at=datetime.now(),
            modified_at=datetime.now()
        )

        initial_history_length = len(page._content_history)

        # Act - 第一次更新
        page.update_content("First update")
        first_history_length = len(page._content_history)

        # Act - 第二次更新
        page.update_content("Second update with much more content to test major change detection. " * 20)  # 增加更多内容
        second_history_length = len(page._content_history)

        # Assert
        assert initial_history_length == 1  # 初始状态
        assert first_history_length == 2  # +1 更新
        assert second_history_length == 3  # +1 更新

        # 验证历史记录
        assert page._content_history[0]['change_type'] == "initial"
        assert page._content_history[1]['change_type'] == "minor"  # 短更新
        assert page._content_history[2]['change_type'] == "major"  # 长更新

    def test_wiki_page_tag_cleaning(self):
        """测试标签清理功能"""
        # Arrange & Act
        page = WikiPage(
            title="Tag Cleaning Test",
            content="Content",
            file_path=Path("tags.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
            tags=["Python!", "  documentation  ", "test-tag", "123tag", "invalid tag!@#"]
        )

        # 源码权威: validate_tag（models.py:15-25）仅 strip + 移除文件系统危险字符，
        # 保留大小写与标点；"invalid tag!@#" 中的空格保留
        expected_tags = ["Python!", "documentation", "test-tag", "123tag", "invalid tag!@#"]
        assert page.tags == expected_tags