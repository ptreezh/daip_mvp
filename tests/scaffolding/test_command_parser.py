"""
测试脚手架命令解析器
遵循TDD原则：先写测试，再实现功能
"""

import pytest
from daip_live.scaffolding.command_parser import ScaffoldCommandParser
from daip_live.scaffolding.models import (
    InputType,
    ScaffoldCommand,
    ValidationError
)


class TestScaffoldCommandParser:
    """测试脚手架命令解析器"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.parser = ScaffoldCommandParser()

    def test_parse_simple_text_command(self):
        """测试解析简单文本命令"""
        # TC-1.2.1: 简单文本输入测试
        command = self.parser.parse("一个简单的Web应用项目")

        assert command.input_type == InputType.TEXT
        assert command.description == "一个简单的Web应用项目"
        assert command.file_path is None
        assert command.auto_confirm == False

    def test_parse_empty_text_command(self):
        """测试解析空文本命令"""
        # TC-1.2.2: 空输入测试
        command = self.parser.parse("")

        assert command.input_type == InputType.TEXT
        assert command.description == ""
        assert command.auto_confirm == False

    def test_parse_file_command_with_flag(self):
        """测试解析带文件标志的命令"""
        # TC-1.2.3: 文件标志测试
        command = self.parser.parse("--file project_desc.txt")

        assert command.input_type == InputType.FILE
        assert command.file_path == "project_desc.txt"
        assert command.description == ""
        assert command.auto_confirm == False

    def test_parse_file_command_with_short_flag(self):
        """测试解析短文件标志的命令"""
        # TC-1.2.4: 短标志测试
        command = self.parser.parse("-f project_desc.txt")

        assert command.input_type == InputType.FILE
        assert command.file_path == "project_desc.txt"

    def test_parse_file_command_with_long_flag(self):
        """测试解析长文件标志的命令"""
        # TC-1.2.5: 长标志测试
        command = self.parser.parse("--from-file /path/to/desc.txt")

        assert command.input_type == InputType.FILE
        assert command.file_path == "/path/to/desc.txt"

    def test_parse_auto_confirm_command(self):
        """测试解析自动确认命令"""
        # TC-1.2.6: 自动确认测试
        command = self.parser.parse("--yes 简单的项目")

        assert command.input_type == InputType.TEXT
        assert command.description == "简单的项目"
        assert command.auto_confirm == True

    def test_parse_short_auto_confirm_command(self):
        """测试解析短自动确认命令"""
        # TC-1.2.7: 短确认标志测试
        command = self.parser.parse("-y 快速生成")

        assert command.auto_confirm == True

    def test_parse_file_with_auto_confirm(self):
        """测试解析文件加自动确认命令"""
        # TC-1.2.8: 文件+确认测试
        command = self.parser.parse("--file desc.txt --yes")

        assert command.input_type == InputType.FILE
        assert command.file_path == "desc.txt"
        assert command.auto_confirm == True

    def test_parse_complex_command(self):
        """测试解析复杂命令"""
        # TC-1.2.9: 复合选项测试
        command = self.parser.parse(
            "--from-file project_description.md --yes create a web application"
        )

        assert command.input_type == InputType.FILE
        assert command.file_path == "project_description.md"
        assert command.auto_confirm == True

    def test_parse_with_extra_spaces(self):
        """测试解析带多余空格的命令"""
        # TC-1.2.10: 空格处理测试
        command = self.parser.parse("  --file   desc.txt   --yes   ")

        assert command.input_type == InputType.FILE
        assert command.file_path == "desc.txt"
        assert command.auto_confirm == True

    def test_parse_description_with_special_chars(self):
        """测试解析包含特殊字符的描述"""
        # TC-1.2.11: 特殊字符测试
        description = "创建一个AI驱动的项目，包含🚀、αβγ等特殊符号"
        command = self.parser.parse(description)

        assert command.input_type == InputType.TEXT
        assert command.description == description

    def test_parse_file_path_with_spaces(self):
        """测试解析带空格的文件路径"""
        # TC-1.2.12: 文件路径空格测试
        command = self.parser.parse('--file "project description.txt"')

        assert command.input_type == InputType.FILE
        # 注意：实际实现中可能需要处理引号

    def test_unrecognized_flags(self):
        """测试解析无法识别的标志"""
        # TC-1.2.13: 未知标志测试
        command = self.parser.parse("--unknown-flag --file test.txt")

        # 应该忽略无法识别的标志
        assert command.input_type == InputType.FILE
        assert command.file_path == "test.txt"

    def test_multiple_file_flags(self):
        """测试多个文件标志的情况"""
        # TC-1.2.14: 多文件标志测试
        command = self.parser.parse("--file first.txt --file second.txt")

        # 应该使用最后一个
        assert command.input_type == InputType.FILE
        assert command.file_path == "second.txt"

    def test_validate_command_success(self):
        """测试命令验证成功"""
        # TC-1.2.15: 验证成功测试
        command = ScaffoldCommand(
            input_type=InputType.TEXT,
            description="Valid description with enough content"
        )

        # 不应该抛出异常
        self.parser.validate(command)

    def test_validate_command_empty_description(self):
        """测试命令验证失败 - 空描述"""
        # TC-1.2.16: 验证空描述测试
        command = ScaffoldCommand(
            input_type=InputType.TEXT,
            description=""
        )

        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate(command)

        assert "描述不能为空" in str(exc_info.value)

    def test_validate_command_file_no_path(self):
        """测试命令验证失败 - 文件无路径"""
        # TC-1.2.17: 验证文件路径测试
        command = ScaffoldCommand(
            input_type=InputType.FILE,
            description="",  # 文件输入时描述可以为空
            file_path=None
        )

        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate(command)

        assert "文件路径不能为空" in str(exc_info.value)

    def test_validate_command_short_description(self):
        """测试命令验证失败 - 描述太短"""
        # TC-1.2.18: 验证描述长度测试
        command = ScaffoldCommand(
            input_type=InputType.TEXT,
            description="太短"
        )

        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate(command)

        assert "至少需要" in str(exc_info.value)

    def test_parse_and_validate_integration(self):
        """测试解析和验证集成"""
        # TC-1.2.19: 集成测试
        # 有效的命令
        valid_command = self.parser.parse("一个包含足够内容的详细项目描述，用于测试验证功能")
        try:
            self.parser.validate(valid_command)
            validation_passed = True
        except ValidationError:
            validation_passed = False
        assert validation_passed

        # 无效的命令
        invalid_command = self.parser.parse("")
        with pytest.raises(ValidationError):
            self.parser.validate(invalid_command)

    def test_parse_help_command(self):
        """测试解析帮助命令"""
        # TC-1.2.20: 帮助命令测试
        help_commands = ["help", "--help", "-h"]

        for help_cmd in help_commands:
            command = self.parser.parse(help_cmd)
            # 帮助命令应该返回None
            assert command is None  # 根据我们的实现，帮助命令返回None

    def test_get_help_message(self):
        """测试获取帮助信息"""
        # TC-1.2.21: 帮助信息测试
        help_message = self.parser.get_help_message()

        assert "scaffold" in help_message.lower()
        assert "file" in help_message.lower()
        assert "yes" in help_message.lower()

    def test_parse_quoted_arguments(self):
        """测试解析带引号的参数"""
        # TC-1.2.22: 引号参数测试
        command = self.parser.parse('--file "my project desc.txt"')

        # 实现需要处理引号
        assert command.input_type == InputType.FILE
        assert command.file_path == "my project desc.txt"  # 引号应该被正确处理

    def test_edge_cases(self):
        """测试边界情况"""
        # TC-1.2.23: 边界情况测试
        edge_cases = [
            "--",  # 只有分隔符 - 应该作为文本
            "--yes",  # 只有确认标志 - 应该是自动确认的文本命令
        ]

        for case in edge_cases:
            command = self.parser.parse(case)
            assert command is not None

        # 测试无效的文件选项（应该抛出异常）
        with pytest.raises(ValidationError):
            self.parser.parse("--file")  # 文件选项缺少路径


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])