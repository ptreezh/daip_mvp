"""
测试文件系统适配器
遵循TDD原则：先写测试，再实现功能
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from daip_live.scaffolding.file_system_adapter import (
    FileOperationResult,
    FileSystemAdapter,
)
from daip_live.scaffolding.models import FileOperationError


class TestFileOperationResult:
    """测试文件操作结果"""

    def test_file_operation_result_creation_success(self):
        """测试成功操作结果创建"""
        # TC-1.4.1: 成功结果测试
        result = FileOperationResult(success=True, data="test content")

        assert result.success
        assert result.data == "test content"
        assert result.error is None
        assert result.error_code is None

    def test_file_operation_result_creation_failure(self):
        """测试失败操作结果创建"""
        # TC-1.4.2: 失败结果测试
        error = FileOperationError("File not found", "FILE_NOT_FOUND")
        result = FileOperationResult(success=False, error=error)

        assert not result.success
        assert result.error.message == "File not found"
        assert result.error.error_code == "FILE_NOT_FOUND"
        assert result.data is None

    def test_file_operation_result_properties(self):
        """测试操作结果属性"""
        # TC-1.4.3: 属性测试
        result_success = FileOperationResult(success=True)
        result_failure = FileOperationResult(success=False)

        assert result_success.is_success
        assert not result_success.is_failure
        assert not result_failure.is_success
        assert result_failure.is_failure

    def test_file_operation_result_str_representation(self):
        """测试字符串表示"""
        # TC-1.4.4: 字符串表示测试
        success_result = FileOperationResult(success=True, data="content")
        failure_result = FileOperationResult(
            success=False, error=FileOperationError("Test error", "TEST_ERROR")
        )

        success_str = str(success_result)
        failure_str = str(failure_result)

        assert "success" in success_str.lower()
        assert "success=false" in failure_str.lower()
        assert "test error" in failure_str.lower()


class TestFileSystemAdapter:
    """测试文件系统适配器"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.adapter = FileSystemAdapter()

    def _create_temp_directory(self):
        """创建临时目录"""
        return tempfile.mkdtemp()

    def _create_temp_file(self, content: str = "", suffix: str = ".txt") -> tuple:
        """创建临时文件并返回路径和清理函数"""
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, f"test_file{suffix}")

        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        def cleanup():
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                os.rmdir(temp_dir)
            except OSError:
                pass  # 忽略清理错误

        return temp_file_path, cleanup

    @pytest.mark.asyncio
    async def test_read_file_success(self):
        """测试成功读取文件"""
        # TC-1.4.5: 文件读取成功测试
        test_content = "这是测试内容\n包含中文和English"
        temp_file_path, cleanup = self._create_temp_file(test_content)

        try:
            result = await self.adapter.read_file(temp_file_path)

            assert result.success
            assert result.data == test_content
            assert result.error is None

        finally:
            cleanup()

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """测试读取不存在的文件"""
        # TC-1.4.6: 文件不存在测试
        nonexistent_path = "/path/to/nonexistent/file.txt"

        result = await self.adapter.read_file(nonexistent_path)

        assert not result.success
        assert result.error is not None
        assert "not found" in result.error.message.lower()
        assert result.error.error_code == "FILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_read_file_permission_denied(self):
        """测试读取权限被拒绝的文件"""
        # TC-1.4.7: 权限拒绝测试
        # 使用mock来模拟权限错误
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch("aiofiles.open", side_effect=PermissionError("Permission denied")),
        ):
            result = await self.adapter.read_file("some_path.txt")

            assert not result.success
            assert "permission" in result.error.message.lower()
            assert result.error.error_code == "PERMISSION_DENIED"

    @pytest.mark.asyncio
    async def test_write_file_success(self):
        """测试成功写入文件"""
        # TC-1.4.8: 文件写入成功测试
        temp_dir = self._create_temp_directory()
        temp_file_path = os.path.join(temp_dir, "new_file.txt")
        test_content = "新的文件内容"

        try:
            result = await self.adapter.write_file(temp_file_path, test_content)

            assert result.success
            assert result.data is not None  # 写入的字节数

            # 验证文件确实被写入
            with open(temp_file_path, encoding="utf-8") as f:
                assert f.read() == test_content

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_write_file_create_directory(self):
        """测试写入文件时自动创建目录"""
        # TC-1.4.9: 自动创建目录测试
        temp_dir = self._create_temp_directory()
        nested_dir = os.path.join(temp_dir, "nested", "directory")
        temp_file_path = os.path.join(nested_dir, "file.txt")
        test_content = "嵌套目录中的文件"

        try:
            result = await self.adapter.write_file(temp_file_path, test_content)

            assert result.success
            assert os.path.exists(temp_file_path)

            with open(temp_file_path, encoding="utf-8") as f:
                assert f.read() == test_content

        finally:
            # 清理嵌套目录
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_write_file_permission_denied(self):
        """测试写入权限被拒绝"""
        # TC-1.4.10: 写入权限测试
        with patch("aiofiles.open", side_effect=PermissionError("Permission denied")):
            result = await self.adapter.write_file("protected_path.txt", "content")

            assert not result.success
            assert result.error.error_code == "PERMISSION_DENIED"

    @pytest.mark.asyncio
    async def test_create_directory_success(self):
        """测试成功创建目录"""
        # TC-1.4.11: 创建目录成功测试
        temp_dir = self._create_temp_directory()
        new_dir_path = os.path.join(temp_dir, "new_directory")

        try:
            result = await self.adapter.create_directory(new_dir_path)

            assert result.success
            assert os.path.exists(new_dir_path)
            assert os.path.isdir(new_dir_path)

        finally:
            if os.path.exists(new_dir_path):
                os.rmdir(new_dir_path)
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_create_nested_directory_success(self):
        """测试成功创建嵌套目录"""
        # TC-1.4.12: 嵌套目录创建测试
        temp_dir = self._create_temp_directory()
        nested_dir_path = os.path.join(temp_dir, "level1", "level2", "level3")

        try:
            result = await self.adapter.create_directory(nested_dir_path)

            assert result.success
            assert os.path.exists(nested_dir_path)
            assert os.path.isdir(nested_dir_path)

        finally:
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_create_directory_already_exists(self):
        """测试创建已存在的目录"""
        # TC-1.4.13: 目录已存在测试
        temp_dir = self._create_temp_directory()
        # 目录已经存在

        try:
            result = await self.adapter.create_directory(temp_dir)

            # 应该成功，因为目录已存在是可接受的状态
            assert result.success

        finally:
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_create_directory_permission_denied(self):
        """测试创建目录权限被拒绝"""
        # TC-1.4.14: 目录创建权限测试
        with patch(
            "pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")
        ):
            result = await self.adapter.create_directory("/protected/path")

            assert not result.success
            assert result.error.error_code == "PERMISSION_DENIED"

    @pytest.mark.asyncio
    async def test_exists_file_true(self):
        """测试检查存在的文件"""
        # TC-1.4.15: 文件存在检查测试
        temp_file_path, cleanup = self._create_temp_file("test content")

        try:
            result = await self.adapter.exists(temp_file_path)

            assert result.success
            assert result.data

        finally:
            cleanup()

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """测试检查不存在的路径"""
        # TC-1.4.16: 路径不存在测试
        nonexistent_path = "/path/to/nonexistent/file"

        result = await self.adapter.exists(nonexistent_path)

        assert result.success
        assert not result.data

    @pytest.mark.asyncio
    async def test_is_file_true(self):
        """测试检查路径是文件"""
        # TC-1.4.17: 是文件检查测试
        temp_file_path, cleanup = self._create_temp_file("test content")

        try:
            result = await self.adapter.is_file(temp_file_path)

            assert result.success
            assert result.data

        finally:
            cleanup()

    @pytest.mark.asyncio
    async def test_is_file_false(self):
        """测试检查路径不是文件"""
        # TC-1.4.18: 不是文件检查测试
        temp_dir = self._create_temp_directory()

        try:
            result = await self.adapter.is_file(temp_dir)

            assert result.success
            assert not result.data

        finally:
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_get_file_info_success(self):
        """测试成功获取文件信息"""
        # TC-1.4.19: 文件信息获取测试
        test_content = "测试文件内容"
        temp_file_path, cleanup = self._create_temp_file(test_content)

        try:
            result = await self.adapter.get_file_info(temp_file_path)

            assert result.success
            info = result.data
            assert info["size"] > 0
            assert info["is_file"]
            assert not info["is_directory"]
            assert "created_at" in info
            assert "modified_at" in info

        finally:
            cleanup()

    @pytest.mark.asyncio
    async def test_get_file_info_not_found(self):
        """测试获取不存在文件的信息"""
        # TC-1.4.20: 文件不存在信息测试
        nonexistent_path = "/path/to/nonexistent/file.txt"

        result = await self.adapter.get_file_info(nonexistent_path)

        assert not result.success
        assert result.error.error_code == "FILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_list_directory_success(self):
        """测试成功列出目录内容"""
        # TC-1.4.21: 目录列表测试
        temp_dir = self._create_temp_directory()

        # 创建一些测试文件
        test_files = ["file1.txt", "file2.md", "subdir"]
        for filename in test_files:
            path = os.path.join(temp_dir, filename)
            if filename == "subdir":
                os.mkdir(path)
            else:
                with open(path, "w") as f:
                    f.write(f"Content of {filename}")

        try:
            result = await self.adapter.list_directory(temp_dir)

            assert result.success
            items = result.data
            assert len(items) >= 3

            # 检查是否包含我们创建的文件
            item_names = [item["name"] for item in items]
            assert "file1.txt" in item_names
            assert "file2.md" in item_names
            assert "subdir" in item_names

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_list_directory_not_found(self):
        """测试列出不存在目录的内容"""
        # TC-1.4.22: 目录不存在列表测试
        nonexistent_dir = "/path/to/nonexistent/directory"

        result = await self.adapter.list_directory(nonexistent_dir)

        assert not result.success
        assert result.error.error_code == "FILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_delete_file_success(self):
        """测试成功删除文件"""
        # TC-1.4.23: 文件删除测试
        temp_file_path, cleanup = self._create_temp_file("test content")

        try:
            # 确保文件存在
            assert os.path.exists(temp_file_path)

            result = await self.adapter.delete_file(temp_file_path)

            assert result.success
            assert not os.path.exists(temp_file_path)
        finally:
            # 只有在文件仍然存在时才清理
            if os.path.exists(temp_file_path):
                cleanup()

    @pytest.mark.asyncio
    async def test_delete_file_not_found(self):
        """测试删除不存在的文件"""
        # TC-1.4.24: 删除不存在文件测试
        nonexistent_path = "/path/to/nonexistent/file.txt"

        result = await self.adapter.delete_file(nonexistent_path)

        assert not result.success
        assert result.error.error_code == "FILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_copy_file_success(self):
        """测试成功复制文件"""
        # TC-1.4.25: 文件复制测试
        test_content = "要复制的文件内容"
        temp_file_path, cleanup = self._create_temp_file(test_content)
        temp_dir = self._create_temp_directory()
        dest_path = os.path.join(temp_dir, "copied_file.txt")

        try:
            result = await self.adapter.copy_file(temp_file_path, dest_path)

            assert result.success
            assert os.path.exists(dest_path)

            # 验证内容是否正确
            with open(dest_path, encoding="utf-8") as f:
                assert f.read() == test_content

        finally:
            cleanup()
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_copy_file_source_not_found(self):
        """测试复制不存在的源文件"""
        # TC-1.4.26: 源文件不存在测试
        nonexistent_source = "/path/to/nonexistent/source.txt"
        dest_path = "dest.txt"

        result = await self.adapter.copy_file(nonexistent_source, dest_path)

        assert not result.success
        assert result.error.error_code == "FILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_move_file_success(self):
        """测试成功移动文件"""
        # TC-1.4.27: 文件移动测试
        test_content = "要移动的文件内容"
        temp_file_path, cleanup = self._create_temp_file(test_content)
        temp_dir = self._create_temp_directory()
        dest_path = os.path.join(temp_dir, "moved_file.txt")

        try:
            result = await self.adapter.move_file(temp_file_path, dest_path)

            assert result.success
            assert not os.path.exists(temp_file_path)  # 原文件不应存在
            assert os.path.exists(dest_path)  # 目标文件应该存在

            # 验证内容是否正确
            with open(dest_path, encoding="utf-8") as f:
                assert f.read() == test_content

        finally:
            # cleanup不再需要，因为原文件已被移动
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_move_file_source_not_found(self):
        """测试移动不存在的源文件"""
        # TC-1.4.28: 源文件不存在移动测试
        nonexistent_source = "/path/to/nonexistent/source.txt"
        dest_path = "dest.txt"

        result = await self.adapter.move_file(nonexistent_source, dest_path)

        assert not result.success
        assert result.error.error_code == "FILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_batch_operations_success(self):
        """测试批量操作成功"""
        # TC-1.4.29: 批量操作测试
        temp_dir = self._create_temp_directory()

        operations = [
            ("write", os.path.join(temp_dir, "file1.txt"), "content1"),
            ("write", os.path.join(temp_dir, "file2.txt"), "content2"),
            ("create_directory", os.path.join(temp_dir, "subdir")),
            ("exists", os.path.join(temp_dir, "file1.txt")),
        ]

        try:
            results = await self.adapter.batch_operations(operations)

            assert len(results) == len(operations)
            assert all(result.success for result in results)
            assert os.path.exists(os.path.join(temp_dir, "file1.txt"))
            assert os.path.exists(os.path.join(temp_dir, "file2.txt"))
            assert os.path.exists(os.path.join(temp_dir, "subdir"))

        finally:
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_batch_operations_partial_failure(self):
        """测试批量操作部分失败"""
        # TC-1.4.30: 批量操作部分失败测试
        temp_dir = self._create_temp_directory()

        # 使用一个会导致权限错误或无效路径的操作
        operations = [
            ("write", os.path.join(temp_dir, "file1.txt"), "content1"),
            ("unknown_operation", "some_arg"),  # 这个会失败 - 未知操作
            ("exists", os.path.join(temp_dir, "file1.txt")),
        ]

        try:
            results = await self.adapter.batch_operations(operations)

            assert len(results) == len(operations)
            assert results[0].success  # 第一个操作成功
            assert not results[1].success  # 第二个操作失败
            assert results[2].success  # 第三个操作成功

        finally:
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_adapter_configuration(self):
        """测试适配器配置"""
        # TC-1.4.31: 配置测试
        adapter = FileSystemAdapter(
            chunk_size=8192, create_directories=True, overwrite_existing=False
        )

        assert adapter.chunk_size == 8192
        assert adapter.create_directories
        assert not adapter.overwrite_existing

    @pytest.mark.asyncio
    async def test_write_file_overwrite_protection(self):
        """测试写入文件时的覆盖保护"""
        # TC-1.4.32: 覆盖保护测试
        temp_file_path, cleanup = self._create_temp_file("original content")

        # 创建不允许覆盖的适配器
        adapter = FileSystemAdapter(overwrite_existing=False)

        try:
            result = await adapter.write_file(temp_file_path, "new content")

            assert not result.success
            assert result.error.error_code == "FILE_EXISTS"

            # 验证原文件未被修改
            with open(temp_file_path, encoding="utf-8") as f:
                assert f.read() == "original content"

        finally:
            cleanup()


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])
