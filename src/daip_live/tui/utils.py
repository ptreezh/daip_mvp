"""TUI工具函数和辅助功能模块"""

import os
import time
from typing import List, Optional, Callable
from textual.app import ComposeResult


class FocusMode:
    """焦点模式枚举"""
    INPUT = "input"
    OUTPUT = "output"


class TUIUtils:
    """TUI工具函数类"""

    @staticmethod
    def format_time_duration(seconds: float) -> str:
        """格式化时间时长"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + suffix

    @staticmethod
    def safe_filename(filename: str) -> str:
        """生成安全的文件名"""
        # 移除或替换不安全的字符
        unsafe_chars = '<>:"/\\|?*'
        safe_name = filename
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        return safe_name

    @staticmethod
    def parse_time_range(time_str: str) -> Optional[tuple]:
        """解析时间范围字符串"""
        try:
            if 'ago' in time_str:
                # 相对时间，如 "1 hour ago", "2 days ago"
                return ('relative', time_str)
            elif time_str.isdigit():
                # Unix时间戳
                return ('timestamp', int(time_str))
            else:
                # 尝试解析为日期时间
                from datetime import datetime
                return ('datetime', datetime.fromisoformat(time_str))
        except:
            return None

    @staticmethod
    def get_status_color(status: str) -> str:
        """根据状态获取颜色"""
        status_colors = {
            'active': 'green',
            'inactive': 'yellow',
            'error': 'red',
            'completed': 'blue',
            'pending': 'cyan',
            'cancelled': 'dim'
        }
        return status_colors.get(status.lower(), 'white')

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        # 简单的相似度计算
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())

        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = set1.intersection(set2)
        union = set1.union(set2)

        return len(intersection) / len(union)

    @staticmethod
    def format_number(num: int) -> str:
        """格式化数字，添加千分位分隔符"""
        return f"{num:,}"

    @staticmethod
    def get_emoji_for_type(content_type: str) -> str:
        """根据内容类型获取对应的emoji"""
        emoji_map = {
            'debate': '🏛️',
            'chat': '💬',
            'task': '📋',
            'file': '📁',
            'document': '📄',
            'code': '💻',
            'image': '🖼️',
            'video': '🎬',
            'audio': '🎵',
            'link': '🔗',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'info': 'ℹ️',
            'help': '❓'
        }
        return emoji_map.get(content_type.lower(), '📝')

    @staticmethod
    def parse_args(command: str) -> List[str]:
        """解析命令参数，支持引号"""
        import shlex
        try:
            return shlex.split(command)
        except:
            # 如果解析失败，使用简单分割
            return command.split()

    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


class HistoryManager:
    """输入历史管理器"""

    def __init__(self, max_history: int = 100, history_file: str = None):
        self.max_history = max_history
        self.history_file = history_file or os.path.join(os.path.expanduser("~"), ".daip_tui_history")
        self.history: List[str] = []
        self.load_history()

    def add(self, command: str):
        """添加命令到历史"""
        if command and command.strip():
            # 避免重复
            if command not in self.history:
                self.history.append(command.strip())
                # 限制历史长度
                if len(self.history) > self.max_history:
                    self.history.pop(0)
                self.save_history()

    def get_previous(self, current_index: int) -> str:
        """获取上一条历史命令"""
        if 0 < current_index < len(self.history):
            return self.history[-current_index]
        return ""

    def get_next(self, current_index: int) -> str:
        """获取下一条历史命令"""
        if current_index > 1:
            return self.history[-current_index + 1]
        elif current_index == 1:
            return self.history[-1]
        return ""

    def search(self, query: str) -> List[str]:
        """搜索历史命令"""
        query_lower = query.lower()
        return [cmd for cmd in self.history if query_lower in cmd.lower()]

    def load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = [line.strip() for line in f.readlines() if line.strip()]
        except Exception:
            self.history = []

    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for cmd in self.history:
                    f.write(cmd + '\n')
        except Exception:
            pass  # 静默失败，不影响主要功能


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = {
            'response_times': [],
            'command_counts': {},
            'error_counts': {},
            'start_time': time.time()
        }

    def record_response_time(self, duration: float):
        """记录响应时间"""
        self.metrics['response_times'].append(duration)
        # 只保留最近100次记录
        if len(self.metrics['response_times']) > 100:
            self.metrics['response_times'].pop(0)

    def record_command(self, command: str):
        """记录命令执行"""
        self.metrics['command_counts'][command] = self.metrics['command_counts'].get(command, 0) + 1

    def record_error(self, error_type: str):
        """记录错误"""
        self.metrics['error_counts'][error_type] = self.metrics['error_counts'].get(error_type, 0) + 1

    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        if not self.metrics['response_times']:
            return 0.0
        return sum(self.metrics['response_times']) / len(self.metrics['response_times'])

    def get_uptime(self) -> float:
        """获取运行时间"""
        return time.time() - self.metrics['start_time']

    def get_stats_summary(self) -> dict:
        """获取统计摘要"""
        return {
            'uptime': self.get_uptime(),
            'avg_response_time': self.get_average_response_time(),
            'total_commands': sum(self.metrics['command_counts'].values()),
            'total_errors': sum(self.metrics['error_counts'].values()),
            'command_counts': dict(self.metrics['command_counts']),
            'error_counts': dict(self.metrics['error_counts'])
        }


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(os.path.expanduser("~"), ".daip_tui_config.json")
        self.config = self.load_config()

    def load_config(self) -> dict:
        """加载配置"""
        default_config = {
            'theme': 'default',
            'auto_save': True,
            'max_history': 100,
            'show_timestamps': True,
            'enable_animations': True,
            'confirm_dangerous_operations': True,
            'auto_backup': False,
            'language': 'zh'
        }

        try:
            if os.path.exists(self.config_file):
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                default_config.update(loaded_config)
        except Exception:
            pass

        return default_config

    def save_config(self):
        """保存配置"""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()


class ThemeManager:
    """主题管理器"""

    THEMES = {
        'default': {
            'background': '#000000',
            'foreground': '#ffffff',
            'accent': '#00ff00',
            'error': '#ff0000',
            'warning': '#ffff00',
            'info': '#00ffff'
        },
        'dark': {
            'background': '#1a1a1a',
            'foreground': '#ffffff',
            'accent': '#0088ff',
            'error': '#ff4444',
            'warning': '#ffaa00',
            'info': '#00aaff'
        },
        'light': {
            'background': '#ffffff',
            'foreground': '#000000',
            'accent': '#0066cc',
            'error': '#cc0000',
            'warning': '#ff8800',
            'info': '#0088cc'
        }
    }

    @classmethod
    def get_theme(cls, theme_name: str) -> dict:
        """获取主题"""
        return cls.THEMES.get(theme_name, cls.THEMES['default'])

    @classmethod
    def list_themes(cls) -> List[str]:
        """列出所有可用主题"""
        return list(cls.THEMES.keys())


class Logger:
    """简单日志记录器"""

    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(os.path.expanduser("~"), ".daip_tui.log")

    def log(self, level: str, message: str):
        """记录日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception:
            pass  # 静默失败

    def info(self, message: str):
        """信息日志"""
        self.log("INFO", message)

    def warning(self, message: str):
        """警告日志"""
        self.log("WARNING", message)

    def error(self, message: str):
        """错误日志"""
        self.log("ERROR", message)

    def debug(self, message: str):
        """调试日志"""
        self.log("DEBUG", message)