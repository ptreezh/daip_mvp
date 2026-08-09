"""
测试输入验证器
遵循TDD原则：先写测试，再实现功能
"""

import os
import tempfile

import pytest

from daip_live.scaffolding.input_validator import InputValidator, ValidationResult
from daip_live.scaffolding.models import ValidationConstants


class TestValidationResult:
    """测试验证结果数据类"""

    def test_validation_result_creation_success(self):
        """测试成功验证结果创建"""
        # TC-1.3.1: 成功结果测试
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validation_result_creation_with_warnings(self):
        """测试包含警告的验证结果"""
        # TC-1.3.2: 警告结果测试
        warnings = ["文件较大", "建议使用更具体的描述"]
        result = ValidationResult(is_valid=True, errors=[], warnings=warnings)

        assert result.is_valid
        assert result.warnings == warnings

    def test_validation_result_creation_with_errors(self):
        """测试包含错误的验证结果"""
        # TC-1.3.3: 错误结果测试
        errors = ["描述为空", "文件不存在"]
        result = ValidationResult(is_valid=False, errors=errors, warnings=[])

        assert not result.is_valid
        assert result.errors == errors

    def test_validation_result_add_error(self):
        """测试添加错误"""
        # TC-1.3.4: 动态添加错误测试
        result = ValidationResult(is_valid=True)
        result.add_error("新的错误")

        assert not result.is_valid
        assert "新的错误" in result.errors

    def test_validation_result_add_warning(self):
        """测试添加警告"""
        # TC-1.3.5: 动态添加警告测试
        result = ValidationResult(is_valid=True)
        result.add_warning("新的警告")

        assert result.is_valid
        assert "新的警告" in result.warnings

    def test_validation_result_str_representation(self):
        """测试字符串表示"""
        # TC-1.3.6: 字符串表示测试
        result = ValidationResult(
            is_valid=False, errors=["错误1", "错误2"], warnings=["警告1"]
        )
        result_str = str(result)

        assert "Validation failed" in result_str
        assert "错误1" in result_str
        assert "错误2" in result_str

    def test_validation_result_has_errors(self):
        """测试是否有错误的检查"""
        # TC-1.3.7: 错误检查测试
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=False, errors=["错误"])

        assert not result1.has_errors()
        assert result2.has_errors()

    def test_validation_result_has_warnings(self):
        """测试是否有警告的检查"""
        # TC-1.3.8: 警告检查测试
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=True, warnings=["警告"])

        assert not result1.has_warnings()
        assert result2.has_warnings()


class TestInputValidator:
    """测试输入验证器"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.validator = InputValidator()

    def _create_temp_file(self, content: str, suffix: str = ".txt") -> tuple:
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

    def test_validate_valid_description(self):
        """测试有效的描述验证"""
        # TC-1.3.9: 有效描述测试
        description = "这是一个有效的项目描述，包含足够的详细信息来生成合理的项目结构。这个描述详细说明了项目的目标、技术栈和主要功能模块。"  # noqa: E501
        result = self.validator.validate_description(description)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_empty_description(self):
        """测试空描述验证"""
        # TC-1.3.10: 空描述测试
        result = self.validator.validate_description("")

        assert not result.is_valid
        assert any("不能为空" in error for error in result.errors)

    def test_validate_too_short_description(self):
        """测试描述过短验证"""
        # TC-1.3.11: 描述过短测试
        short_desc = "太短"
        result = self.validator.validate_description(short_desc)

        assert not result.is_valid
        assert any("至少需要" in error for error in result.errors)

    def test_validate_too_long_description(self):
        """测试描述过长验证"""
        # TC-1.3.12: 描述过长测试
        long_desc = "a" * (ValidationConstants.MAX_DESCRIPTION_LENGTH + 1)
        result = self.validator.validate_description(long_desc)

        assert not result.is_valid
        assert any("不能超过" in error for error in result.errors)

    def test_validate_description_with_whitespace(self):
        """测试只包含空格的描述"""
        # TC-1.3.13: 空格描述测试
        result = self.validator.validate_description("   \t\n  ")

        assert not result.is_valid
        assert any("不能为空" in error for error in result.errors)

    def test_validate_description_with_unicode(self):
        """测试包含Unicode字符的描述"""
        # TC-1.3.14: Unicode描述测试
        unicode_desc = "这是一个包含特殊符号的项目描述：🚀 AI助手 αβγ émojis"
        result = self.validator.validate_description(unicode_desc)

        assert result.is_valid

    def test_validate_existing_file_path(self):
        """测试存在的文件路径验证"""
        # TC-1.3.15: 现有文件测试
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "test_file.txt")

        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write("test content")

            result = self.validator.validate_file_path(temp_file_path)
            assert result.is_valid

        finally:
            # 清理临时目录和文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            os.rmdir(temp_dir)

    def test_validate_nonexistent_file_path(self):
        """测试不存在的文件路径验证"""
        # TC-1.3.16: 不存在文件测试
        nonexistent_path = "/path/to/nonexistent/file.txt"
        result = self.validator.validate_file_path(nonexistent_path)

        assert not result.is_valid
        assert any("不存在" in error for error in result.errors)

    def test_validate_empty_file_path(self):
        """测试空文件路径验证"""
        # TC-1.3.17: 空路径测试
        result = self.validator.validate_file_path("")

        assert not result.is_valid
        assert any("不能为空" in error for error in result.errors)

    def test_validate_file_path_with_invalid_characters(self):
        """测试包含无效字符的文件路径"""
        # TC-1.3.18: 无效字符路径测试
        invalid_paths = [
            "file<name>.txt",  # 包含尖括号
            "file|name.txt",  # 包含管道符
            "file?.txt",  # 包含问号
            "../etc/passwd",  # 路径遍历尝试
        ]

        for invalid_path in invalid_paths:
            result = self.validator.validate_file_path(invalid_path)
            assert not result.is_valid, f"Path '{invalid_path}' should be invalid"

    def test_validate_file_size_within_limit(self):
        """测试文件大小在限制内"""
        # TC-1.3.19: 正常文件大小测试
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "test_file.txt")

        try:
            content = "x" * 1000  # 1KB文件
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(content)

            result = self.validator.validate_file_path(temp_file_path)
            assert result.is_valid

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            os.rmdir(temp_dir)

    def test_validate_file_size_exceeds_limit(self):
        """测试文件大小超过限制"""
        # TC-1.3.20: 大文件测试
        # 创建一个小的测试文件（避免创建真正的大文件）
        temp_file_path, cleanup = self._create_temp_file("small content")

        # 临时修改验证器的限制为很小的值来测试
        original_max_size = self.validator.max_file_size
        self.validator.max_file_size = 10  # 设置为10字节

        try:
            result = self.validator.validate_file_path(temp_file_path)
            assert not result.is_valid
            assert any("过大" in error for error in result.errors)
        finally:
            # 恢复原始设置
            self.validator.max_file_size = original_max_size
            cleanup()

    def test_validate_unsupported_file_extension(self):
        """测试不支持的文件扩展名"""
        # TC-1.3.21: 不支持扩展名测试
        temp_file_path, cleanup = self._create_temp_file("test content", ".exe")

        try:
            result = self.validator.validate_file_path(temp_file_path)
            # 应该有警告但不失败
            assert any("不支持的文件格式" in warning for warning in result.warnings)
        finally:
            cleanup()

    def test_validate_supported_file_extensions(self):
        """测试支持的文件扩展名"""
        # TC-1.3.22: 支持扩展名测试
        supported_extensions = [".txt", ".md", ".docx"]

        for ext in supported_extensions:
            temp_file_path, cleanup = self._create_temp_file("test content", ext)

            try:
                result = self.validator.validate_file_path(temp_file_path)
                assert result.is_valid
                # 不应该有格式相关的警告
                format_warnings = [w for w in result.warnings if "格式" in w]
                assert len(format_warnings) == 0
            finally:
                cleanup()

    def test_validate_file_content_encoding(self):
        """测试文件内容编码验证"""
        # TC-1.3.23: 文件编码测试
        content = "测试内容 🚀 αβγ"
        temp_file_path, cleanup = self._create_temp_file(content)

        try:
            result = self.validator.validate_file_path(temp_file_path)
            assert result.is_valid
        finally:
            cleanup()

    def test_validate_binary_file_warning(self):
        """测试二进制文件警告"""
        # TC-1.3.24: 二进制文件警告测试
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "test_binary_file.txt")

        try:
            # 写入一些二进制数据
            with open(temp_file_path, "wb") as f:
                f.write(b"\x00\x01\x02\x03\x04\x05")

            result = self.validator.validate_file_path(temp_file_path)
            # 应该有二进制文件的警告
            assert any("二进制" in warning for warning in result.warnings)

        finally:
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                os.rmdir(temp_dir)
            except OSError:
                pass  # 忽略清理错误

    def test_validate_comprehensive_input(self):
        """测试综合输入验证"""
        # TC-1.3.25: 综合验证测试
        description = "完整的项目描述，包含足够的信息"
        temp_file_path, cleanup = self._create_temp_file(description)

        try:
            # 验证描述
            desc_result = self.validator.validate_description(description)
            assert desc_result.is_valid

            # 验证文件
            file_result = self.validator.validate_file_path(temp_file_path)
            assert file_result.is_valid

            # 综合验证
            combined_result = self.validator.validate_input(
                description=description, file_path=temp_file_path
            )
            assert combined_result.is_valid

        finally:
            cleanup()

    def test_validate_input_conflicting_requirements(self):
        """测试冲突的输入要求"""
        # TC-1.3.26: 冲突输入测试
        # 空描述但提供了文件路径 - 这是有效的
        temp_file_path, cleanup = self._create_temp_file("文件内容")

        try:
            result = self.validator.validate_input(
                description="",  # 空描述
                file_path=temp_file_path,  # 但有文件
            )
            assert result.is_valid

        finally:
            cleanup()

    def test_validate_input_both_empty(self):
        """测试描述和文件都为空"""
        # TC-1.3.27: 全空输入测试
        result = self.validator.validate_input(description="", file_path=None)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_get_validation_summary(self):
        """测试获取验证摘要"""
        # TC-1.3.28: 验证摘要测试
        result = ValidationResult(
            is_valid=False, errors=["错误1"], warnings=["警告1", "警告2"]
        )

        summary = self.validator.get_validation_summary(result)
        assert "验证失败" in summary
        assert "1 个错误" in summary
        assert "2 个警告" in summary

    def test_custom_validation_rules(self):
        """测试自定义验证规则"""

        # TC-1.3.29: 自定义规则测试
        def custom_rule(text: str) -> list:
            if "密码" in text:
                return ["描述中不应包含敏感信息"]
            return []

        validator = InputValidator()
        validator.add_custom_rule("description_sensitive", custom_rule)

        result = validator.validate_description("这是一个包含密码的项目描述")
        assert not result.is_valid
        assert any("不应包含敏感信息" in error for error in result.errors)
        assert any("敏感信息" in error for error in result.errors)

    def test_validator_configuration(self):
        """测试验证器配置"""
        # TC-1.3.30: 配置测试
        validator = InputValidator(
            min_description_length=20,
            max_description_length=1000,
            max_file_size=512 * 1024,  # 512KB
        )

        # 测试配置是否生效
        short_desc = "太短的描述"
        result = validator.validate_description(short_desc)
        assert not result.is_valid

        # 测试长度要求是否符合配置
        error_messages = " ".join(result.errors)
        assert "至少需要20个字符" in error_messages


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])
