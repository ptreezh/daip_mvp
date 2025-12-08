"""
Wiki页面数据模型

遵循TDD RED-GREEN-REFACTOR循环开发
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def validate_tag(tag: str) -> str:
    """验证并清理标签"""
    if not isinstance(tag, str):
        raise TypeError("Tag must be a string")
    clean_tag = tag.strip()
    if not clean_tag:
        raise ValueError("Tag cannot be empty")
    # 移除有问题的特殊字符，但保留Unicode字符（包括中文）
    # 只移除可能导致文件系统问题的字符
    clean_tag = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', clean_tag)
    return clean_tag


@dataclass
class WikiPage:
    """Wiki页面数据模型

    表示一个Wiki页面的完整信息，包括内容、元数据和标签管理功能。
    支持序列化/反序列化、内容变更历史跟踪等高级功能。
    """

    title: str
    content: str
    file_path: Path
    created_at: datetime
    modified_at: datetime
    tags: List[str] = field(default_factory=list)
    _content_history: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def __post_init__(self):
        """初始化后的验证和设置"""
        # 验证标题
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        # 验证文件路径
        if not isinstance(self.file_path, Path):
            self.file_path = Path(self.file_path)

        if self.file_path.suffix.lower() != '.md':
            raise ValueError("Wiki page must be a markdown file")

        # 确保tags是列表的副本（避免外部修改影响）
        if self.tags is None:
            self.tags = []
        else:
            self.tags = [validate_tag(tag) for tag in self.tags]

        # 记录初始内容历史
        self._record_content_change("initial", self.content)

    def _record_content_change(self, change_type: str, content: str) -> None:
        """记录内容变更历史"""
        self._content_history.append({
            'timestamp': datetime.now(),
            'change_type': change_type,
            'content_length': len(content),
            'content_preview': content[:100] + "..." if len(content) > 100 else content
        })

    def update_content(self, content: str) -> None:
        """更新页面内容

        Args:
            content: 新的页面内容

        Raises:
            TypeError: 如果content不是字符串类型
        """
        if not isinstance(content, str):
            raise TypeError("Content must be a string")

        old_content = self.content
        self.content = content
        self.modified_at = datetime.now()

        # 记录内容变更
        change_type = "minor" if len(content) - len(old_content) < 100 else "major"
        self._record_content_change(change_type, content)

    def add_tag(self, tag: str) -> bool:
        """添加标签

        Args:
            tag: 要添加的标签

        Returns:
            bool: 如果标签是新添加的返回True，如果已存在返回False

        Raises:
            ValueError: 如果标签为空或只包含空白字符
        """
        clean_tag = validate_tag(tag)

        if clean_tag in self.tags:
            return False

        self.tags.append(clean_tag)
        self.modified_at = datetime.now()
        return True

    def remove_tag(self, tag: str) -> bool:
        """移除标签

        Args:
            tag: 要移除的标签

        Returns:
            bool: 如果标签存在并被移除返回True，否则返回False
        """
        clean_tag = validate_tag(tag)

        if clean_tag in self.tags:
            self.tags.remove(clean_tag)
            self.modified_at = datetime.now()
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """检查是否包含指定标签"""
        clean_tag = validate_tag(tag)
        return clean_tag in self.tags

    def get_content_preview(self, max_length: int = 200) -> str:
        """获取内容预览"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."

    def get_word_count(self) -> int:
        """获取内容字数"""
        return len(self.content.split())

    def get_reading_time(self, words_per_minute: int = 200) -> int:
        """估算阅读时间（分钟）"""
        word_count = self.get_word_count()
        return max(1, round(word_count / words_per_minute))

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'content': self.content,
            'file_path': str(self.file_path),
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'tags': self.tags.copy(),
            'word_count': self.get_word_count(),
            'reading_time': self.get_reading_time()
        }

    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WikiPage':
        """从字典创建WikiPage实例"""
        return cls(
            title=data['title'],
            content=data['content'],
            file_path=Path(data['file_path']),
            created_at=datetime.fromisoformat(data['created_at']),
            modified_at=datetime.fromisoformat(data['modified_at']),
            tags=data.get('tags', [])
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'WikiPage':
        """从JSON字符串创建WikiPage实例"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """字符串表示"""
        return f"WikiPage(title='{self.title}', tags={self.tags})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"WikiPage(title='{self.title}', file_path='{self.file_path}', "
                f"created_at='{self.created_at}', modified_at='{self.modified_at}', "
                f"tags={self.tags})")