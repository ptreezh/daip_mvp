"""
智能角色选择器
根据协作主题从roles目录智能选择最合适的角色
"""

import json
from pathlib import Path
from typing import Optional

from daip_live.p4_role_manager_tools.role_manager import RoleManager


class RoleIntelligenceSelector:
    """
    智能角色选择器
    基于协作主题分析，从角色定义中选择最相关的角色
    """

    def __init__(self, role_manager: RoleManager, roles_dir: Optional[Path] = None):
        self.role_manager = role_manager
        self.roles_dir = roles_dir or Path("roles")
        self.default_roles = ["domain_expert", "researcher", "editor", "critic"]

    def analyze_topic_for_roles(self, topic: str, max_roles: int = 4) -> list[str]:
        """
        分析主题以选择最相关的角色

        Args:
            topic: 协作主题
            max_roles: 最大返回角色数

        Returns:
            List[str]: 选择的角色列表，按相关性排序
        """
        try:
            # 获取所有可用角色
            all_roles = self._get_all_available_roles()

            if not all_roles:
                # 如果无法获取角色，则返回默认角色
                return self.default_roles[:max_roles]

            # 基于主题关键词分析选择角色
            selected_roles = self._select_roles_by_topic_analysis(
                topic, all_roles, max_roles
            )

            # 如果选择的角色数量不足，补充默认角色
            if len(selected_roles) < max_roles:
                for default_role in self.default_roles:
                    if (
                        default_role not in selected_roles
                        and len(selected_roles) < max_roles
                    ):
                        selected_roles.append(default_role)

            # 确保不超过最大数量
            return selected_roles[:max_roles]

        except Exception:
            # 发生异常时，返回默认角色
            return self.default_roles[:max_roles]

    def _get_all_available_roles(self) -> list[str]:
        """获取所有可用的角色名称"""
        try:
            # 尝试使用RoleManager获取角色列表
            if hasattr(self.role_manager, "list_roles"):
                return self.role_manager.list_roles()
            else:
                # 如果RoleManager无法提供角色列表，从roles目录扫描
                role_files = []
                if self.roles_dir.exists():
                    for file_path in self.roles_dir.glob("*.json"):
                        role_name = file_path.stem
                        role_files.append(role_name)
                return role_files
        except Exception:
            # 如果获取角色列表失败，返回空列表
            return []

    def _select_roles_by_topic_analysis(
        self, topic: str, all_roles: list[str], max_roles: int
    ) -> list[str]:
        """
        基于主题分析选择角色

        Args:
            topic: 协作主题
            all_roles: 所有可用角色
            max_roles: 最大返回角色数

        Returns:
            List[str]: 按相关性排序的角色列表
        """
        # 主题关键词提取（简单实现，可后续优化）
        topic_keywords = self._extract_keywords(topic.lower())

        # 计算每个角色与主题的相关性得分
        role_scores = {}

        for role_name in all_roles:
            score = self._calculate_role_topic_score(role_name, topic_keywords)
            role_scores[role_name] = score

        # 按得分排序，返回得分最高的角色
        sorted_roles = sorted(
            role_scores.keys(), key=lambda x: role_scores[x], reverse=True
        )
        return sorted_roles[:max_roles]

    def _extract_keywords(self, text: str) -> list[str]:
        """从文本中提取关键词"""
        # 简单的关键字提取：按空格分割并过滤掉常见停用词
        import re

        # 分词（支持中英文）
        words = re.findall(r"[\w]+", text)

        # 过滤掉常见的停用词
        stop_words = {
            "的",
            "了",
            "在",
            "是",
            "我",
            "有",
            "和",
            "就",
            "不",
            "人",
            "都",
            "一",
            "一个",
            "上",
            "也",
            "很",
            "到",
            "说",
            "要",
            "去",
            "你",
            "会",
            "着",
            "没有",
            "看",
            "好",
            "自己",
            "这",
            "那",
            "它",
            "他",
            "她",
            "我们",
            "你们",
            "他们",
            "这个",
            "那个",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
        }

        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return keywords

    def _calculate_role_topic_score(
        self, role_name: str, topic_keywords: list[str]
    ) -> int:
        """
        计算角色与主题的相关性得分

        Args:
            role_name: 角色名称
            topic_keywords: 主题关键词列表

        Returns:
            int: 相关性得分
        """
        score = 0

        # 检查角色名称与主题关键词的匹配
        for keyword in topic_keywords:
            if keyword in role_name.lower():
                score += 3  # 角色名称匹配权重较高

        # 如果可能，尝试从角色定义中获取更多信息
        try:
            # 尝试获取角色描述信息以进行更详细匹配
            role_description = self._get_role_description(role_name)
            if role_description:
                role_desc_keywords = self._extract_keywords(role_description.lower())
                for keyword in topic_keywords:
                    if keyword in role_desc_keywords:
                        score += 2  # 角色描述匹配权重中等
                    # 检查反向匹配
                    for desc_keyword in role_desc_keywords:
                        if keyword in desc_keyword or desc_keyword in keyword:
                            score += 1  # 部分匹配权重较低
        except Exception:
            # 如果无法获取角色描述，仅基于名称匹配
            pass

        return score

    def _get_role_description(self, role_name: str) -> Optional[str]:
        """
        获取角色的描述信息

        Args:
            role_name: 角色名称

        Returns:
            Optional[str]: 角色描述，如果无法获取则返回None
        """
        try:
            # 尝试使用RoleManager获取角色信息
            if hasattr(self.role_manager, "get_role_info"):
                role_info = self.role_manager.get_role_info(role_name)
                if isinstance(role_info, dict) and "persona" in role_info:
                    return role_info["persona"]

            # 如果RoleManager不可用，尝试直接读取角色文件
            role_file_path = self.roles_dir / f"{role_name}.json"
            if role_file_path.exists():
                with open(role_file_path, encoding="utf-8") as f:
                    role_data = json.load(f)
                    if isinstance(role_data, dict):
                        # 尝试获取角色描述字段
                        return role_data.get(
                            "persona", role_data.get("description", "")
                        )
        except Exception:
            # 如果无法获取角色描述，返回None
            pass

        return None
