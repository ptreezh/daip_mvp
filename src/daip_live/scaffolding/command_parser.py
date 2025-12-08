"""
脚手架命令解析器
遵循SOLID原则，负责解析和验证用户输入的脚手架命令
"""

import re
import shlex
from typing import List, Optional, Tuple
from .models import (
    InputType,
    ScaffoldCommand,
    ValidationError,
    ErrorMessages,
    ValidationConstants
)


class ScaffoldCommandParser:
    """脚手架命令解析器

    负责解析用户输入的命令字符串，生成ScaffoldCommand对象
    支持多种输入格式和选项
    """

    # 定义命令行选项映射
    OPTION_PATTERNS = {
        'file': [
            re.compile(r'^--file\s+(.+)$'),
            re.compile(r'^-f\s+(.+)$'),
            re.compile(r'^--from-file\s+(.+)$'),
        ],
        'yes': [
            re.compile(r'^--yes$'),
            re.compile(r'^-y$'),
            re.compile(r'^--auto-confirm$'),
        ],
        'help': [
            re.compile(r'^--help$'),
            re.compile(r'^-h$'),
            re.compile(r'^help$'),
        ]
    }

    def __init__(self):
        """初始化解析器"""
        self._reset_state()

    def _reset_state(self) -> None:
        """重置解析状态"""
        self._input_type = InputType.TEXT
        self._description = ""
        self._file_path = None
        self._auto_confirm = False
        self._is_help = False

    def parse(self, command_str: str) -> Optional[ScaffoldCommand]:
        """解析命令字符串

        Args:
            command_str: 用户输入的命令字符串

        Returns:
            ScaffoldCommand对象，如果是帮助命令则返回None

        Raises:
            ValidationError: 当命令格式无效时
        """
        # 重置状态
        self._reset_state()

        if not command_str or not command_str.strip():
            # 空命令，返回文本输入命令
            return ScaffoldCommand(
                input_type=InputType.TEXT,
                description=""
            )

        # 清理输入
        command_str = command_str.strip()

        # 检查是否为帮助命令
        if self._is_help_command(command_str):
            self._is_help = True
            return None

        # 使用shlex分割参数，支持引号
        try:
            tokens = shlex.split(command_str)
        except ValueError as e:
            # 引号不匹配等错误
            raise ValidationError([f"命令格式错误: {str(e)}"])

        # 简化的选项解析
        description_parts = []
        i = 0
        while i < len(tokens):
            token = tokens[i].lower()

            # 处理文件选项
            if token in ['--file', '-f', '--from-file']:
                if i + 1 < len(tokens):
                    self._file_path = tokens[i + 1]
                    self._input_type = InputType.FILE
                    i += 2  # 跳过选项和值
                else:
                    raise ValidationError([f"文件选项需要指定文件路径: {token}"])
                continue

            # 处理确认选项
            elif token in ['--yes', '-y', '--auto-confirm']:
                self._auto_confirm = True
                i += 1
                continue

            # 其他情况作为描述
            else:
                # 保持原始大小写和特殊字符
                if i < len(tokens):
                    description_parts.append(tokens[i])
                i += 1

        # 组合描述
        self._description = " ".join(description_parts)

        # 创建命令对象
        command = ScaffoldCommand(
            input_type=self._input_type,
            description=self._description,
            file_path=self._file_path,
            auto_confirm=self._auto_confirm
        )

        return command

    def _is_help_command(self, command_str: str) -> bool:
        """检查是否为帮助命令"""
        for pattern in self.OPTION_PATTERNS['help']:
            if pattern.match(command_str.strip().lower()):
                return True
        return False

    def _match_file_option(self, tokens: List[str], index: int) -> bool:
        """匹配并处理文件选项"""
        if index >= len(tokens):
            return False

        token = tokens[index].lower()

        for pattern in self.OPTION_PATTERNS['file']:
            match = pattern.match(token)
            if match:
                # 如果模式已经包含值（如--file=value）
                if match.groups():
                    self._file_path = match.group(1)
                    return True
                else:
                    # 检查是否是标志格式（如--file, -f）
                    if token in ['--file', '-f', '--from-file']:
                        # 下一个token是值
                        if index + 1 < len(tokens):
                            self._file_path = tokens[index + 1]
                            self._input_type = InputType.FILE
                            return True
                        else:
                            raise ValidationError([f"文件选项需要指定文件路径: {token}"])
                    else:
                        # 处理直接跟在标志后面的值
                        return False

        return False

    def _match_yes_option(self, tokens: List[str], index: int) -> bool:
        """匹配并处理确认选项"""
        if index >= len(tokens):
            return False

        token = tokens[index].lower()

        for pattern in self.OPTION_PATTERNS['yes']:
            if pattern.match(token):
                self._auto_confirm = True
                return True

        return False

    def validate(self, command: ScaffoldCommand) -> None:
        """验证命令的有效性

        Args:
            command: 要验证的命令

        Raises:
            ValidationError: 当命令无效时
        """
        errors = []

        # 基本验证
        basic_errors = command.validate()
        if basic_errors:
            errors.extend(basic_errors)

        # 额外验证
        if command.input_type == InputType.TEXT:
            if not command.description or not command.description.strip():
                errors.append(ErrorMessages.EMPTY_DESCRIPTION)
            elif len(command.description) < ValidationConstants.MIN_DESCRIPTION_LENGTH:
                errors.append(
                    f"{ErrorMessages.DESCRIPTION_TOO_SHORT} "
                    f"(当前: {len(command.description)}, 需要: {ValidationConstants.MIN_DESCRIPTION_LENGTH})"
                )
            elif len(command.description) > ValidationConstants.MAX_DESCRIPTION_LENGTH:
                errors.append(
                    f"{ErrorMessages.DESCRIPTION_TOO_LONG} "
                    f"(当前: {len(command.description)}, 最大: {ValidationConstants.MAX_DESCRIPTION_LENGTH})"
                )

        elif command.input_type == InputType.FILE:
            if not command.file_path:
                errors.append("文件输入时必须指定文件路径")

        if errors:
            raise ValidationError(errors)

    def is_help_command(self, command_str: str) -> bool:
        """检查是否为帮助命令"""
        return self._is_help_command(command_str)

    def get_help_message(self) -> str:
        """获取帮助信息"""
        help_text = """
🏗️ DAIP-LIVE 脚手架命令帮助

用法:
  /scaffold [选项] [项目描述]

选项:
  -f, --file <路径>        从文件读取项目描述
      --from-file <路径>   从文件读取项目描述（长格式）
  -y, --yes              自动确认，跳过预览确认
  -h, --help             显示此帮助信息

示例:
  /scaffold "创建一个Web应用项目，包含用户认证和数据库"
  /scaffold --file project_desc.txt
  /scaffold -f desc.txt --yes

文件格式:
  支持 .txt, .md, .docx 格式
  最大文件大小: 1MB

描述要求:
  最小长度: 10个字符
  最大长度: 5000个字符
  支持中文和英文

更多信息请查看用户手册。
        """.strip()

        return help_text

    def parse_with_validation(self, command_str: str) -> ScaffoldCommand:
        """解析命令并立即验证

        Args:
            command_str: 命令字符串

        Returns:
            验证通过的ScaffoldCommand

        Raises:
            ValidationError: 解析或验证失败
        """
        command = self.parse(command_str)
        if command is None:
            raise ValidationError(["无效的帮助命令"])

        self.validate(command)
        return command

    def get_command_summary(self, command: ScaffoldCommand) -> str:
        """获取命令摘要信息"""
        if command.input_type == InputType.TEXT:
            source = f"文本描述: {command.description[:50]}{'...' if len(command.description) > 50 else ''}"
        else:
            source = f"文件: {command.file_path}"

        summary = f"""
脚手架命令摘要:
- 输入类型: {command.input_type.value}
- 内容来源: {source}
- 自动确认: {'是' if command.auto_confirm else '否'}
        """.strip()

        return summary


class CommandSuggestion:
    """命令建议生成器"""

    @staticmethod
    def suggest_completions(partial_input: str) -> List[str]:
        """根据部分输入提供建议"""
        suggestions = []

        partial_lower = partial_input.lower()

        # 基本命令建议
        if "--f".startswith(partial_lower):
            suggestions.extend(["--file ", "--from-file "])
        elif "--y".startswith(partial_lower):
            suggestions.extend(["--yes", "-y"])
        elif "--h".startswith(partial_lower):
            suggestions.extend(["--help", "-h"])

        # 完整选项建议
        if partial_lower.endswith("--"):
            suggestions.extend(["--file ", "--yes", "--help"])
        elif partial_lower.endswith("-"):
            suggestions.extend(["-f ", "-y", "-h"])

        return suggestions

    @staticmethod
    def get_example_commands() -> List[str]:
        """获取示例命令"""
        return [
            '/scaffold "创建一个包含用户认证的Web应用"',
            '/scaffold --file project_desc.txt',
            '/scaffold -f desc.md --yes',
            '/scaffold -h'
        ]


class CommandHistory:
    """命令历史管理器"""

    def __init__(self, max_history: int = 100):
        self._history: List[str] = []
        self._max_history = max_history

    def add_command(self, command: str) -> None:
        """添加命令到历史"""
        if command and command.strip():
            # 避免重复
            if not self._history or self._history[-1] != command:
                self._history.append(command)
                if len(self._history) > self._max_history:
                    self._history.pop(0)

    def get_previous_command(self, current_index: int) -> Optional[str]:
        """获取上一个命令"""
        if current_index < len(self._history):
            return self._history[current_index]
        return None

    def get_next_command(self, current_index: int) -> Optional[str]:
        """获取下一个命令"""
        if current_index > 0 and current_index - 1 < len(self._history):
            return self._history[current_index - 1]
        return None

    def get_recent_commands(self, count: int = 10) -> List[str]:
        """获取最近的命令"""
        return self._history[-count:]

    def clear_history(self) -> None:
        """清空历史"""
        self._history.clear()