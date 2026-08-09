"""
文件系统适配器
遵循SOLID原则，提供异步文件操作功能
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

# 异步文件操作库
try:
    import aiofiles

    AIOFILES_AVAILABLE = True
except ImportError:
    aiofiles = None
    AIOFILES_AVAILABLE = False

from .models import FileOperationError


class FileOperationResult:
    """文件操作结果

    封装文件操作的结果，包括成功状态、数据和错误信息
    """

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[FileOperationError] = None,
        error_code: Optional[str] = None,
        operation_type: Optional[str] = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code
        self.operation_type = operation_type
        self.timestamp = datetime.now()

    @property
    def is_success(self) -> bool:
        """操作是否成功"""
        return self.success

    @property
    def is_failure(self) -> bool:
        """操作是否失败"""
        return not self.success

    def __str__(self) -> str:
        """字符串表示"""
        if self.success:
            return f"FileOperationResult(success=True, operation={self.operation_type})"
        else:
            return f"FileOperationResult(success=False, error={self.error}, operation={self.operation_type})"  # noqa: E501

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (
            f"FileOperationResult(success={self.success}, data={self.data}, "
            f"error={self.error}, error_code={self.error_code}, "
            f"operation_type={self.operation_type}, timestamp={self.timestamp})"
        )


class FileSystemAdapter:
    """文件系统适配器

    遵循单一职责原则，专门负责异步文件系统操作
    提供统一的文件操作接口，支持错误处理和批量操作
    """

    def __init__(
        self,
        chunk_size: int = 8192,
        create_directories: bool = True,
        overwrite_existing: bool = True,
        encoding: str = "utf-8",
    ):
        """初始化文件系统适配器

        Args:
            chunk_size: 文件读取的块大小
            create_directories: 写入文件时是否自动创建目录
            overwrite_existing: 是否覆盖已存在的文件
            encoding: 文件编码格式
        """
        self.chunk_size = chunk_size
        self.create_directories = create_directories
        self.overwrite_existing = overwrite_existing
        self.encoding = encoding

        # 验证依赖
        if not AIOFILES_AVAILABLE:
            raise ImportError("aiofiles is required for async file operations")

    async def read_file(self, file_path: Union[str, Path]) -> FileOperationResult:
        """异步读取文件

        Args:
            file_path: 文件路径

        Returns:
            FileOperationResult: 读取结果，包含文件内容或错误信息
        """
        operation_type = "read_file"
        file_path = Path(file_path)

        try:
            # 检查文件是否存在
            if not file_path.exists():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"File not found: {file_path}", "FILE_NOT_FOUND"
                    ),
                    error_code="FILE_NOT_FOUND",
                    operation_type=operation_type,
                )

            # 检查是否为文件
            if not file_path.is_file():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Path is not a file: {file_path}", "NOT_A_FILE"
                    ),
                    error_code="NOT_A_FILE",
                    operation_type=operation_type,
                )

            # 异步读取文件
            async with aiofiles.open(file_path, "r", encoding=self.encoding) as file:
                content = await file.read()

            return FileOperationResult(
                success=True, data=content, operation_type=operation_type
            )

        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Permission denied: {str(e)}", "PERMISSION_DENIED"
                ),
                error_code="PERMISSION_DENIED",
                operation_type=operation_type,
            )
        except UnicodeDecodeError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"File encoding error: {str(e)}", "ENCODING_ERROR"
                ),
                error_code="ENCODING_ERROR",
                operation_type=operation_type,
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Unexpected error reading file: {str(e)}", "READ_ERROR"
                ),
                error_code="READ_ERROR",
                operation_type=operation_type,
            )

    async def write_file(
        self,
        file_path: Union[str, Path],
        content: str,
        create_directories: Optional[bool] = None,
    ) -> FileOperationResult:
        """异步写入文件

        Args:
            file_path: 文件路径
            content: 文件内容
            create_directories: 是否自动创建目录，None表示使用实例默认值

        Returns:
            FileOperationResult: 写入结果，包含写入的字节数或错误信息
        """
        operation_type = "write_file"
        file_path = Path(file_path)

        try:
            # 创建目录（如果需要）
            should_create_dirs = (
                create_directories
                if create_directories is not None
                else self.create_directories
            )

            if should_create_dirs:
                parent_dir = file_path.parent
                await self.create_directory(parent_dir)

            # 检查文件是否已存在
            if file_path.exists() and not self.overwrite_existing:
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"File already exists: {file_path}", "FILE_EXISTS"
                    ),
                    error_code="FILE_EXISTS",
                    operation_type=operation_type,
                )

            # 异步写入文件
            async with aiofiles.open(file_path, "w", encoding=self.encoding) as file:
                bytes_written = await file.write(content)
                await file.flush()  # 确保数据写入磁盘

            return FileOperationResult(
                success=True, data=bytes_written, operation_type=operation_type
            )

        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Permission denied: {str(e)}", "PERMISSION_DENIED"
                ),
                error_code="PERMISSION_DENIED",
                operation_type=operation_type,
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Unexpected error writing file: {str(e)}", "WRITE_ERROR"
                ),
                error_code="WRITE_ERROR",
                operation_type=operation_type,
            )

    async def create_directory(
        self, dir_path: Union[str, Path], exist_ok: bool = True
    ) -> FileOperationResult:
        """异步创建目录

        Args:
            dir_path: 目录路径
            exist_ok: 如果目录已存在是否忽略错误

        Returns:
            FileOperationResult: 创建结果
        """
        operation_type = "create_directory"
        dir_path = Path(dir_path)

        try:
            dir_path.mkdir(parents=True, exist_ok=exist_ok)

            return FileOperationResult(
                success=True, data=str(dir_path), operation_type=operation_type
            )

        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Permission denied: {str(e)}", "PERMISSION_DENIED"
                ),
                error_code="PERMISSION_DENIED",
                operation_type=operation_type,
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Unexpected error creating directory: {str(e)}", "CREATE_DIR_ERROR"
                ),
                error_code="CREATE_DIR_ERROR",
                operation_type=operation_type,
            )

    async def exists(self, path: Union[str, Path]) -> FileOperationResult:
        """检查路径是否存在

        Args:
            path: 要检查的路径

        Returns:
            FileOperationResult: 检查结果，data为bool值
        """
        operation_type = "exists"
        path = Path(path)

        try:
            exists = path.exists()
            return FileOperationResult(
                success=True, data=exists, operation_type=operation_type
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Error checking path existence: {str(e)}", "EXISTS_CHECK_ERROR"
                ),
                error_code="EXISTS_CHECK_ERROR",
                operation_type=operation_type,
            )

    async def is_file(self, path: Union[str, Path]) -> FileOperationResult:
        """检查路径是否为文件

        Args:
            path: 要检查的路径

        Returns:
            FileOperationResult: 检查结果，data为bool值
        """
        operation_type = "is_file"
        path = Path(path)

        try:
            is_file = path.is_file()
            return FileOperationResult(
                success=True, data=is_file, operation_type=operation_type
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Error checking if path is file: {str(e)}", "IS_FILE_CHECK_ERROR"
                ),
                error_code="IS_FILE_CHECK_ERROR",
                operation_type=operation_type,
            )

    async def get_file_info(self, file_path: Union[str, Path]) -> FileOperationResult:
        """获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            FileOperationResult: 文件信息字典或错误
        """
        operation_type = "get_file_info"
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"File not found: {file_path}", "FILE_NOT_FOUND"
                    ),
                    error_code="FILE_NOT_FOUND",
                    operation_type=operation_type,
                )

            stat = file_path.stat()

            info = {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
                "accessed_at": datetime.fromtimestamp(stat.st_atime),
            }

            return FileOperationResult(
                success=True, data=info, operation_type=operation_type
            )

        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Error getting file info: {str(e)}", "GET_INFO_ERROR"
                ),
                error_code="GET_INFO_ERROR",
                operation_type=operation_type,
            )

    async def list_directory(
        self, dir_path: Union[str, Path], include_hidden: bool = False
    ) -> FileOperationResult:
        """列出目录内容

        Args:
            dir_path: 目录路径
            include_hidden: 是否包含隐藏文件

        Returns:
            FileOperationResult: 目录内容列表或错误
        """
        operation_type = "list_directory"
        dir_path = Path(dir_path)

        try:
            if not dir_path.exists():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Directory not found: {dir_path}", "FILE_NOT_FOUND"
                    ),
                    error_code="FILE_NOT_FOUND",
                    operation_type=operation_type,
                )

            if not dir_path.is_dir():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Path is not a directory: {dir_path}", "NOT_A_DIRECTORY"
                    ),
                    error_code="NOT_A_DIRECTORY",
                    operation_type=operation_type,
                )

            items = []
            for item in dir_path.iterdir():
                if not include_hidden and item.name.startswith("."):
                    continue

                try:
                    stat = item.stat()
                    item_info = {
                        "name": item.name,
                        "path": str(item),
                        "is_file": item.is_file(),
                        "is_directory": item.is_dir(),
                        "size": stat.st_size if item.is_file() else 0,
                        "created_at": datetime.fromtimestamp(stat.st_ctime),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime),
                    }
                    items.append(item_info)
                except (OSError, PermissionError):
                    # 跳过无法访问的文件
                    continue

            return FileOperationResult(
                success=True, data=items, operation_type=operation_type
            )

        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Permission denied: {str(e)}", "PERMISSION_DENIED"
                ),
                error_code="PERMISSION_DENIED",
                operation_type=operation_type,
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Error listing directory: {str(e)}", "LIST_DIR_ERROR"
                ),
                error_code="LIST_DIR_ERROR",
                operation_type=operation_type,
            )

    async def delete_file(self, file_path: Union[str, Path]) -> FileOperationResult:
        """删除文件

        Args:
            file_path: 文件路径

        Returns:
            FileOperationResult: 删除结果
        """
        operation_type = "delete_file"
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"File not found: {file_path}", "FILE_NOT_FOUND"
                    ),
                    error_code="FILE_NOT_FOUND",
                    operation_type=operation_type,
                )

            if not file_path.is_file():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Path is not a file: {file_path}", "NOT_A_FILE"
                    ),
                    error_code="NOT_A_FILE",
                    operation_type=operation_type,
                )

            file_path.unlink()

            return FileOperationResult(
                success=True, data=str(file_path), operation_type=operation_type
            )

        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Permission denied: {str(e)}", "PERMISSION_DENIED"
                ),
                error_code="PERMISSION_DENIED",
                operation_type=operation_type,
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Error deleting file: {str(e)}", "DELETE_ERROR"
                ),
                error_code="DELETE_ERROR",
                operation_type=operation_type,
            )

    async def copy_file(
        self, source_path: Union[str, Path], dest_path: Union[str, Path]
    ) -> FileOperationResult:
        """复制文件

        Args:
            source_path: 源文件路径
            dest_path: 目标文件路径

        Returns:
            FileOperationResult: 复制结果
        """
        operation_type = "copy_file"
        source_path = Path(source_path)
        dest_path = Path(dest_path)

        try:
            # 检查源文件
            if not source_path.exists():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Source file not found: {source_path}", "FILE_NOT_FOUND"
                    ),
                    error_code="FILE_NOT_FOUND",
                    operation_type=operation_type,
                )

            if not source_path.is_file():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Source path is not a file: {source_path}", "NOT_A_FILE"
                    ),
                    error_code="NOT_A_FILE",
                    operation_type=operation_type,
                )

            # 创建目标目录
            await self.create_directory(dest_path.parent)

            # 复制文件
            shutil.copy2(source_path, dest_path)

            return FileOperationResult(
                success=True,
                data={"source": str(source_path), "destination": str(dest_path)},
                operation_type=operation_type,
            )

        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Permission denied: {str(e)}", "PERMISSION_DENIED"
                ),
                error_code="PERMISSION_DENIED",
                operation_type=operation_type,
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(f"Error copying file: {str(e)}", "COPY_ERROR"),
                error_code="COPY_ERROR",
                operation_type=operation_type,
            )

    async def move_file(
        self, source_path: Union[str, Path], dest_path: Union[str, Path]
    ) -> FileOperationResult:
        """移动文件

        Args:
            source_path: 源文件路径
            dest_path: 目标文件路径

        Returns:
            FileOperationResult: 移动结果
        """
        operation_type = "move_file"
        source_path = Path(source_path)
        dest_path = Path(dest_path)

        try:
            # 检查源文件
            if not source_path.exists():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Source file not found: {source_path}", "FILE_NOT_FOUND"
                    ),
                    error_code="FILE_NOT_FOUND",
                    operation_type=operation_type,
                )

            if not source_path.is_file():
                return FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Source path is not a file: {source_path}", "NOT_A_FILE"
                    ),
                    error_code="NOT_A_FILE",
                    operation_type=operation_type,
                )

            # 创建目标目录
            await self.create_directory(dest_path.parent)

            # 移动文件
            shutil.move(str(source_path), str(dest_path))

            return FileOperationResult(
                success=True,
                data={"source": str(source_path), "destination": str(dest_path)},
                operation_type=operation_type,
            )

        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Permission denied: {str(e)}", "PERMISSION_DENIED"
                ),
                error_code="PERMISSION_DENIED",
                operation_type=operation_type,
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(f"Error moving file: {str(e)}", "MOVE_ERROR"),
                error_code="MOVE_ERROR",
                operation_type=operation_type,
            )

    async def batch_operations(
        self, operations: list[tuple[str, ...]]
    ) -> list[FileOperationResult]:
        """批量执行文件操作

        Args:
            operations: 操作列表，每个操作为元组 (operation_name, args...)

        Returns:
            List[FileOperationResult]: 操作结果列表
        """
        results = []

        for operation in operations:
            if not operation:
                continue

            operation_name = operation[0].lower()
            args = operation[1:]

            try:
                if operation_name == "read":
                    result = await self.read_file(*args)
                elif operation_name == "write":
                    result = await self.write_file(*args)
                elif operation_name == "create_directory":
                    result = await self.create_directory(*args)
                elif operation_name == "exists":
                    result = await self.exists(*args)
                elif operation_name == "is_file":
                    result = await self.is_file(*args)
                elif operation_name == "get_file_info":
                    result = await self.get_file_info(*args)
                elif operation_name == "list_directory":
                    result = await self.list_directory(*args)
                elif operation_name == "delete_file":
                    result = await self.delete_file(*args)
                elif operation_name == "copy_file":
                    result = await self.copy_file(*args)
                elif operation_name == "move_file":
                    result = await self.move_file(*args)
                else:
                    result = FileOperationResult(
                        success=False,
                        error=FileOperationError(
                            f"Unknown operation: {operation_name}", "UNKNOWN_OPERATION"
                        ),
                        error_code="UNKNOWN_OPERATION",
                        operation_type=operation_name,
                    )

            except Exception as e:
                result = FileOperationResult(
                    success=False,
                    error=FileOperationError(
                        f"Error executing {operation_name}: {str(e)}", "EXECUTION_ERROR"
                    ),
                    error_code="EXECUTION_ERROR",
                    operation_type=operation_name,
                )

            results.append(result)

        return results

    async def get_disk_usage(self, path: Union[str, Path]) -> FileOperationResult:
        """获取磁盘使用情况

        Args:
            path: 路径

        Returns:
            FileOperationResult: 磁盘使用信息
        """
        operation_type = "get_disk_usage"
        path = Path(path)

        try:
            usage = shutil.disk_usage(path)

            usage_info = {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "path": str(path),
            }

            return FileOperationResult(
                success=True, data=usage_info, operation_type=operation_type
            )

        except Exception as e:
            return FileOperationResult(
                success=False,
                error=FileOperationError(
                    f"Error getting disk usage: {str(e)}", "DISK_USAGE_ERROR"
                ),
                error_code="DISK_USAGE_ERROR",
                operation_type=operation_type,
            )
