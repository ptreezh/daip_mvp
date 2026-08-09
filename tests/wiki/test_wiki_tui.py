"""
Wiki TUI界面的TDD测试用例
遵循RED-GREEN-REFACTOR循环
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from textual.widgets import Input

from daip_live.wiki.manager import WikiManager


class TestWikiTUIApp:
    """Wiki TUI应用的测试套件"""

    def test_wiki_tui_app_initialization(self):
        """测试Wiki TUI应用初始化"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)

            # Act & Assert - 这个测试在WikiTUIApp实现之前会失败
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            assert app.wiki_root == wiki_root
            assert isinstance(app.wiki_manager, WikiManager)

    def test_wiki_tui_app_loads_existing_wiki(self):
        """测试TUI应用加载已有Wiki数据"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)

            # 预先创建一些Wiki页面
            manager = WikiManager(wiki_root)
            manager.create_page("Test Page", "Test content", ["test"])
            manager.create_page("Another Page", "Another content", ["another"])

            # Act
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Assert
            assert app.get_page_count() == 2

    def test_wiki_tui_shows_page_list_on_startup(self):
        """测试启动时显示页面列表"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            manager.create_page("Page 1", "Content 1", ["tag1"])
            manager.create_page("Page 2", "Content 2", ["tag2"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            with patch.object(app, "query_one") as mock_query:
                mock_table = Mock()
                mock_query.return_value = mock_table

                app.on_mount()

                # Assert
                mock_table.clear.assert_called_once()
                # 验证添加了行数据（具体实现时检查调用参数）

    def test_wiki_tui_new_page_dialog(self):
        """测试新建页面对话框"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            with patch.object(app, "push_screen") as mock_push:
                app.action_new_page()

            # Assert
            mock_push.assert_called_once()
            # 验证推送了新建页面屏幕

    def test_wiki_tui_create_page_from_dialog(self):
        """测试从对话框创建页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # 模拟用户输入
            title_input = Mock(spec=Input)
            title_input.value = "New Test Page"

            content_input = Mock(spec=Input)
            content_input.value = "# New Test Page\n\nThis is a new page."

            tags_input = Mock(spec=Input)
            tags_input.value = "test,new"

            # Act
            result = app.create_page_from_dialog(
                title=title_input, content=content_input, tags=tags_input
            )

            # Assert
            assert result is True
            assert app.get_page_count() == 1

            page = app.wiki_manager.get_page_by_title("New Test Page")
            assert page is not None
            assert page.content == "# New Test Page\n\nThis is a new page."
            assert "test" in page.tags
            assert "new" in page.tags

    def test_wiki_tui_create_page_with_empty_title_error(self):
        """测试创建页面时空标题错误处理"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            title_input = Mock(spec=Input)
            title_input.value = ""  # 空标题

            content_input = Mock(spec=Input)
            content_input.value = (
                ""  # 源码权威: 空标题+非空内容会从内容提取标题，须都为空才报错
            )

            tags_input = Mock(spec=Input)

            # Act & Assert
            with pytest.raises(ValueError, match="Title cannot be empty"):
                app.create_page_from_dialog(
                    title=title_input, content=content_input, tags=tags_input
                )

    def test_wiki_tui_create_page_duplicate_title_error(self):
        """测试创建页面时重复标题错误处理"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            manager.create_page("Existing Page", "Existing content")

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            title_input = Mock(spec=Input)
            title_input.value = "Existing Page"  # 重复标题

            content_input = Mock(spec=Input)
            content_input.value = "New content"

            tags_input = Mock(spec=Input)

            # Act & Assert
            with pytest.raises(ValueError, match="already exists"):
                app.create_page_from_dialog(
                    title=title_input, content=content_input, tags=tags_input
                )

    def test_wiki_tui_open_page_viewer(self):
        """测试打开页面查看器"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            page = manager.create_page("Test Page", "# Test\n\nContent", ["test"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            with patch.object(app, "push_screen") as mock_push:
                app.open_page_viewer(page)

            # Assert
            mock_push.assert_called_once()
            # 验证推送了页面查看器屏幕

    def test_wiki_tui_edit_page(self):
        """测试编辑页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            page = manager.create_page("Test Page", "Original content", ["test"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # 模拟编辑对话框
            title_input = Mock(spec=Input)
            title_input.value = "Test Page"

            content_input = Mock(spec=Input)
            content_input.value = "Updated content"

            tags_input = Mock(spec=Input)
            tags_input.value = "test,updated"

            # Act
            result = app.update_page_from_dialog(
                page=page, title=title_input, content=content_input, tags=tags_input
            )

            # Assert
            assert result is True

            updated_page = app.wiki_manager.get_page_by_title("Test Page")
            assert updated_page.content == "Updated content"
            assert "updated" in updated_page.tags

    def test_wiki_tui_delete_page_confirmation(self):
        """测试删除页面确认对话框"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            page = manager.create_page("Test Page", "Content", ["test"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            with patch.object(app, "push_screen") as mock_push:
                app.show_delete_confirmation(page)

            # Assert
            mock_push.assert_called_once()
            # 验证推送了删除确认屏幕

    def test_wiki_tui_confirm_delete_page(self):
        """测试确认删除页面"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            page = manager.create_page("Test Page", "Content", ["test"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            result = app.delete_page(page)

            # Assert
            assert result is True
            assert app.get_page_count() == 0
            assert app.wiki_manager.get_page_by_title("Test Page") is None

    def test_wiki_tui_search_functionality(self):
        """测试搜索功能"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            manager.create_page("Python Guide", "Python programming guide", ["python"])
            manager.create_page("Java Tutorial", "Java programming tutorial", ["java"])
            manager.create_page("Python Tips", "Python tips and tricks", ["python"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            search_input = Mock(spec=Input)
            search_input.value = "python"

            # Act
            with patch.object(app, "update_search_results") as mock_update:
                app.perform_search(search_input)

            # Assert
            mock_update.assert_called_once()
            # 验证搜索结果包含2个Python相关页面

    def test_wiki_tui_filter_by_tags(self):
        """测试按标签过滤"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            manager.create_page("Python Guide", "Python content", ["python", "guide"])
            manager.create_page("Java Guide", "Java content", ["java", "guide"])
            manager.create_page("Python Tips", "Python tips", ["python", "tips"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            app.filter_by_tags(["python"])

            # Assert
            assert app.current_filter_tags == ["python"]
            # 验证只显示包含python标签的页面（通过内部状态检查）

    def test_wiki_tui_show_statistics(self):
        """测试显示统计信息"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            manager = WikiManager(wiki_root)
            manager.create_page("Page 1", "Content 1", ["tag1"])
            manager.create_page("Page 2", "Content 2", ["tag2"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            with patch.object(app, "push_screen") as mock_push:
                app.show_statistics()

            # Assert
            mock_push.assert_called_once()
            # 验证推送了统计信息屏幕

    def test_wiki_tui_export_wiki(self):
        """测试导出Wiki功能"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            export_dir = Path(temp_dir) / "export"
            manager = WikiManager(wiki_root)
            manager.create_page("Test Page", "Test content", ["test"])

            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            result = app.export_wiki(export_dir, format="markdown")

            # Assert
            assert result is True
            assert export_dir.exists()
            assert (export_dir / "test_page.md").exists()

    def test_wiki_tui_keyboard_shortcuts(self):
        """测试键盘快捷键"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act & Assert - 验证快捷键绑定
            assert hasattr(app, "action_new_page")  # Ctrl+N
            assert hasattr(app, "action_search")  # Ctrl+F
            assert hasattr(app, "action_quit")  # Ctrl+Q

    def test_wiki_tui_error_handling_display(self):
        """测试错误处理和显示"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            with patch.object(app, "notify") as mock_notify:
                app.show_error("Test error message")

            # Assert
            mock_notify.assert_called_once_with("Test error message", severity="error")

    def test_wiki_tui_success_notification(self):
        """测试成功通知显示"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_root = Path(temp_dir)
            from daip_live.wiki.tui import WikiTUIApp

            app = WikiTUIApp(wiki_root)

            # Act
            with patch.object(app, "notify") as mock_notify:
                app.show_success("Operation completed successfully")

            # Assert
            mock_notify.assert_called_once_with(
                "Operation completed successfully", severity="success"
            )
