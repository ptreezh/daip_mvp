"""
输入验证器
遵循SOLID原则，负责验证用户输入的有效性和安全性
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import mimetypes

# python-magic 是可选依赖
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    magic = None
    MAGIC_AVAILABLE = False

from .models import ValidationError, ValidationConstants, ErrorMessages


class ValidationResult:
    """验证结果数据类

    封装验证的结果，包括成功状态、错误列表和警告列表
    """

    def __init__(
        self,
        is_valid: bool = True,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, error: str) -> None:
        """添加错误信息"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """添加警告信息"""
        self.warnings.append(warning)

    def has_errors(self) -> bool:
        """检查是否有错误"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """检查是否有警告"""
        return len(self.warnings) > 0

    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """合并另一个验证结果"""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings
        )

    def __str__(self) -> str:
        """字符串表示"""
        if self.is_valid:
            if self.has_warnings():
                return f"Validation passed with {len(self.warnings)} warning(s)"
            return "Validation passed"
        else:
            error_summary = "; ".join(self.errors[:3])
            if len(self.errors) > 3:
                error_summary += f" and {len(self.errors) - 3} more"
            return f"Validation failed: {error_summary}"


class InputValidator:
    """输入验证器

    遵循单一职责原则，专门负责验证各种类型的用户输入
    支持可配置的验证规则和自定义验证函数
    """

    def __init__(
        self,
        min_description_length: int = ValidationConstants.MIN_DESCRIPTION_LENGTH,
        max_description_length: int = ValidationConstants.MAX_DESCRIPTION_LENGTH,
        max_file_size: int = ValidationConstants.MAX_FILE_SIZE,
        supported_extensions: Optional[set] = None,
        strict_mode: bool = False
    ):
        """初始化验证器

        Args:
            min_description_length: 描述的最小长度
            max_description_length: 描述的最大长度
            max_file_size: 文件的最大大小（字节）
            supported_extensions: 支持的文件扩展名
            strict_mode: 是否使用严格模式
        """
        self.min_description_length = min_description_length
        self.max_description_length = max_description_length
        self.max_file_size = max_file_size
        self.supported_extensions = supported_extensions or ValidationConstants.SUPPORTED_FILE_EXTENSIONS
        self.strict_mode = strict_mode

        # 自定义验证规则
        self._custom_rules: Dict[str, Callable[[str], List[str]]] = {}

        # 预编译的正则表达式
        self._path_traversal_pattern = re.compile(r'\.\.[\\/]|[\\/]\.\.')
        self._invalid_filename_pattern = re.compile(r'[<>:"|?*\x00-\x1f]')
        self._sensitive_info_pattern = re.compile(
            r'(password|passwd|secret|key|token|auth)\s*[:=]\s*[^\s]+',
            re.IGNORECASE
        )

    def validate_description(self, description: str) -> ValidationResult:
        """验证项目描述

        Args:
            description: 项目描述文本

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 基本检查
        if not description or not description.strip():
            result.add_error(ErrorMessages.EMPTY_DESCRIPTION)
            return result

        cleaned_description = description.strip()

        # 长度检查
        if len(cleaned_description) < self.min_description_length:
            result.add_error(
                f"描述至少需要{self.min_description_length}个字符 "
                f"(当前: {len(cleaned_description)}, 需要: {self.min_description_length})"
            )

        if len(cleaned_description) > self.max_description_length:
            result.add_error(
                f"{ErrorMessages.DESCRIPTION_TOO_LONG} "
                f"(当前: {len(cleaned_description)}, 最大: {self.max_description_length})"
            )

        # 内容检查
        self._validate_description_content(cleaned_description, result)

        # 自定义规则检查
        for rule_name, rule_func in self._custom_rules.items():
            if rule_name.startswith("description_"):
                try:
                    rule_errors = rule_func(cleaned_description)
                    for error in rule_errors:
                        result.add_error(f"[{rule_name}] {error}")
                except Exception as e:
                    result.add_error(f"自定义规则 '{rule_name}' 执行失败: {str(e)}")

        return result

    def _validate_description_content(self, description: str, result: ValidationResult) -> None:
        """验证描述内容

        Args:
            description: 清理后的描述文本
            result: 验证结果对象
        """
        # 敏感信息检查
        sensitive_matches = self._sensitive_info_pattern.findall(description)
        if sensitive_matches:
            result.add_warning(
                f"描述中可能包含敏感信息: {', '.join(matches for matches in sensitive_matches[:3])}"
            )

        # 字符编码检查
        try:
            description.encode('utf-8')
        except UnicodeEncodeError as e:
            result.add_error(f"描述包含无效的Unicode字符: {str(e)}")

        # 重复字符检查
        if self.strict_mode and self._has_excessive_repetition(description):
            result.add_warning("描述包含过多的重复字符，建议修改")

    def validate_file_path(self, file_path: str) -> ValidationResult:
        """验证文件路径

        Args:
            file_path: 文件路径

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        if not file_path or not file_path.strip():
            result.add_error("文件路径不能为空")
            return result

        cleaned_path = file_path.strip()

        # 路径安全检查
        if self._has_path_traversal(cleaned_path):
            result.add_error("文件路径包含不安全的路径遍历字符")

        # 文件名安全检查
        filename = os.path.basename(cleaned_path)
        if self._invalid_filename_pattern.search(filename):
            result.add_error("文件名包含无效字符")

        # 文件存在性检查
        if not os.path.exists(cleaned_path):
            result.add_error(f"{ErrorMessages.FILE_NOT_FOUND}: {cleaned_path}")
            return result

        try:
            path_obj = Path(cleaned_path)

            # 文件大小检查
            file_size = path_obj.stat().st_size
            if file_size > self.max_file_size:
                result.add_error(
                    f"文件过大 "
                    f"(当前: {file_size}字节, 最大: {self.max_file_size}字节)"
                )

            # 文件扩展名检查
            file_ext = path_obj.suffix.lower()
            if file_ext not in self.supported_extensions:
                result.add_warning(
                    f"{ErrorMessages.UNSUPPORTED_FILE_FORMAT}: '{file_ext}'"
                    f"，支持的格式: {', '.join(self.supported_extensions)}"
                )

            # 文件内容检查
            self._validate_file_content(cleaned_path, result)

            # 权限检查
            if not os.access(cleaned_path, os.R_OK):
                result.add_error(f"{ErrorMessages.FILE_READ_ERROR}: 没有读取权限")

        except OSError as e:
            result.add_error(f"文件系统错误: {str(e)}")

        # 自定义规则检查
        for rule_name, rule_func in self._custom_rules.items():
            if rule_name.startswith("file_"):
                rule_errors = rule_func(cleaned_path)
                for error in rule_errors:
                    result.add_error(f"[{rule_name}] {error}")

        return result

    def _validate_file_content(self, file_path: str, result: ValidationResult) -> None:
        """验证文件内容

        Args:
            file_path: 文件路径
            result: 验证结果对象
        """
        try:
            # 检测文件类型
            file_type, _ = mimetypes.guess_type(file_path)

            # 尝试使用python-magic进行更准确的类型检测
            if MAGIC_AVAILABLE:
                try:
                    mime_type = magic.from_file(file_path, mime=True)
                    if mime_type.startswith('application/') and not mime_type.endswith('text'):
                        result.add_warning(f"文件类型为 '{mime_type}'，可能不是纯文本文件")
                except Exception:
                    # magic检测失败，继续其他检查
                    pass
            else:
                # python-magic不可用，使用mimetypes
                if file_type and not file_type.startswith('text/'):
                    result.add_warning(f"文件类型为 '{file_type}'，建议使用纯文本文件")

            # 检查文件内容是否为纯文本
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # 尝试读取前1KB内容
                    content = f.read(1024)
                    if not content:
                        result.add_warning("文件为空")
                    elif self._contains_binary_content(content):
                        result.add_warning("文件似乎包含二进制内容，建议使用纯文本文件")
            except UnicodeDecodeError:
                result.add_error("文件编码不是有效的UTF-8，请使用UTF-8编码保存文件")

        except Exception as e:
            result.add_warning(f"无法验证文件内容: {str(e)}")

    def validate_input(
        self,
        description: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> ValidationResult:
        """综合验证输入

        Args:
            description: 项目描述
            file_path: 文件路径

        Returns:
            ValidationResult: 综合验证结果
        """
        result = ValidationResult()

        # 至少需要提供一个输入
        if not description and not file_path:
            result.add_error("必须提供项目描述或项目描述文件")
            return result

        # 验证描述（只有在没有文件的情况下才强制要求描述有效）
        if description:
            desc_result = self.validate_description(description)
            # 如果同时提供了文件，描述可以为空
            if file_path and not description.strip():
                # 有文件时，空描述是可以接受的
                pass
            else:
                result = result.merge(desc_result)

        # 验证文件
        if file_path:
            file_result = self.validate_file_path(file_path)
            result = result.merge(file_result)

        # 如果两个都提供了，检查一致性
        if description and file_path:
            self._validate_input_consistency(description, file_path, result)

        return result

    def _validate_input_consistency(
        self,
        description: str,
        file_path: str,
        result: ValidationResult
    ) -> None:
        """验证输入一致性

        Args:
            description: 项目描述
            file_path: 文件路径
            result: 验证结果对象
        """
        # 如果描述很短，但提供了文件，这可能是合理的
        if len(description.strip()) < self.min_description_length and file_path:
            # 这是合理的情况，不需要警告
            pass

        # 如果描述很长，又提供了文件，可能存在重复
        elif len(description.strip()) > self.min_description_length * 2:
            result.add_warning("同时提供了详细描述和描述文件，可能存在信息重复")

    def _has_path_traversal(self, path: str) -> bool:
        """检查路径是否包含路径遍历攻击"""
        return bool(self._path_traversal_pattern.search(path))

    def _has_excessive_repetition(self, text: str) -> bool:
        """检查是否有过多的重复字符"""
        # 检查连续相同字符
        max_consecutive = 10
        if len(text) >= max_consecutive:
            consecutive_count = 1
            for i in range(1, len(text)):
                if text[i] == text[i-1]:
                    consecutive_count += 1
                    if consecutive_count >= max_consecutive:
                        return True
                else:
                    consecutive_count = 1

        # 检查重复的单词
        words = text.lower().split()
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        # 如果某个单词出现次数超过总单词数的50%
        if words and word_count:
            max_repetitions = max(word_count.values())
            if max_repetitions > len(words) * 0.5:
                return True

        return False

    def _contains_binary_content(self, content: str) -> bool:
        """检查文本是否包含二进制内容"""
        # 简单的启发式方法：检查null字节和不可打印字符的比例
        null_count = content.count('\x00')
        if null_count > 0:
            return True

        # 检查不可打印字符的比例
        printable_count = sum(1 for c in content if c.isprintable() or c.isspace())
        if len(content) > 0 and printable_count / len(content) < 0.8:
            return True

        return False

    def add_custom_rule(self, name: str, rule_func: Callable[[str], List[str]]) -> None:
        """添加自定义验证规则

        Args:
            name: 规则名称
            rule_func: 验证函数，接受字符串输入，返回错误列表
        """
        if not callable(rule_func):
            raise ValueError("规则函数必须是可调用的")
        self._custom_rules[name] = rule_func

    def remove_custom_rule(self, name: str) -> None:
        """移除自定义验证规则

        Args:
            name: 规则名称
        """
        self._custom_rules.pop(name, None)

    def get_validation_summary(self, result: ValidationResult) -> str:
        """获取验证结果的摘要信息

        Args:
            result: 验证结果

        Returns:
            str: 摘要信息
        """
        if result.is_valid:
            if result.has_warnings():
                return f"验证通过，但有 {len(result.warnings)} 个警告"
            return "验证通过"
        else:
            summary_parts = []
            if result.has_errors():
                summary_parts.append(f"{len(result.errors)} 个错误")
            if result.has_warnings():
                summary_parts.append(f"{len(result.warnings)} 个警告")
            return f"验证失败: {'，'.join(summary_parts)}"

    def configure(
        self,
        min_description_length: Optional[int] = None,
        max_description_length: Optional[int] = None,
        max_file_size: Optional[int] = None,
        supported_extensions: Optional[set] = None,
        strict_mode: Optional[bool] = None
    ) -> None:
        """配置验证器参数

        Args:
            min_description_length: 描述的最小长度
            max_description_length: 描述的最大长度
            max_file_size: 文件的最大大小
            supported_extensions: 支持的文件扩展名
            strict_mode: 是否使用严格模式
        """
        if min_description_length is not None:
            if min_description_length < 1:
                raise ValueError("最小描述长度必须大于0")
            self.min_description_length = min_description_length

        if max_description_length is not None:
            if max_description_length < self.min_description_length:
                raise ValueError("最大描述长度不能小于最小描述长度")
            self.max_description_length = max_description_length

        if max_file_size is not None:
            if max_file_size <= 0:
                raise ValueError("最大文件大小必须大于0")
            self.max_file_size = max_file_size

        if supported_extensions is not None:
            self.supported_extensions = set(supported_extensions)

        if strict_mode is not None:
            self.strict_mode = strict_mode

    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式列表"""
        return sorted(self.supported_extensions)

    def validate_file_extension(self, file_path: str) -> ValidationResult:
        """单独验证文件扩展名

        Args:
            file_path: 文件路径

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()
        file_ext = Path(file_path).suffix.lower()

        if file_ext not in self.supported_extensions:
            result.add_error(
                f"不支持的文件格式 '{file_ext}'"
                f"，支持的格式: {', '.join(self.supported_extensions)}"
            )

        return result

    def validate_path_safety(self, path: str) -> ValidationResult:
        """单独验证路径安全性

        Args:
            path: 文件路径

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        if not path:
            result.add_error("路径不能为空")
            return result

        # 路径遍历检查
        if self._has_path_traversal(path):
            result.add_error("路径包含不安全的路径遍历字符")

        # 路径长度检查
        if len(path) > 260:  # Windows路径长度限制
            result.add_warning("路径过长，在某些系统上可能不被支持")

        # 绝对路径检查
        if os.path.isabs(path):
            result.add_warning("使用了绝对路径，建议使用相对路径")

        return result