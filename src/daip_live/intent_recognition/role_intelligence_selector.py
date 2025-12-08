"""
角色智能选择器
根据主题自动选择最适合的角色组合进行协作
"""

import re
from typing import List, Dict, Any, Optional
from daip_live.p4_role_manager_tools.role_manager import RoleManager


class RoleIntelligenceSelector:
    """基于主题智能选择角色的选择器"""

    def __init__(self, role_manager: RoleManager):
        """初始化角色选择器

        Args:
            role_manager: 角色管理器实例
        """
        self.role_manager = role_manager

        # 定义角色到关键词的映射
        self.role_keywords = {
            "domain_expert": [
                "技术", "原理", "算法", "架构", "设计", "实现", "开发", "编程",
                "系统", "工程", "科学", "理论", "方法", "技术栈", "框架"
            ],
            "researcher": [
                "研究", "数据", "分析", "报告", "论文", "调查", "统计", "实验",
                "测试", "评估", "证据", "文献", "参考", "案例", "样本"
            ],
            "editor": [
                "编辑", "写作", "文档", "说明", "介绍", "概述", "总结", "结构",
                "格式", "规范", "语言", "表达", "叙述", "文本", "内容"
            ],
            "critic": [
                "评价", "批评", "问题", "缺陷", "风险", "挑战", "限制", "缺点",
                "弱点", "不足", "改进", "优化", "建议", "意见", "反思"
            ],
            "analyst": [
                "分析", "趋势", "预测", "市场", "商业", "投资", "战略", "规划",
                "前景", "发展", "未来", "机会", "竞争", "优势", "劣势"
            ],
            "teacher": [
                "教学", "学习", "教育", "培训", "指导", "入门", "基础", "初级",
                "教程", "课程", "知识", "概念", "解释", "说明", "理解"
            ]
        }

        # 定义主题类型到推荐角色的映射
        self.topic_role_mapping = {
            "technical": ["domain_expert", "researcher", "editor"],
            "research": ["researcher", "domain_expert", "critic"],
            "analysis": ["analyst", "researcher", "critic"],
            "educational": ["teacher", "domain_expert", "editor"],
            "review": ["critic", "researcher", "editor"],
            "development": ["domain_expert", "analyst", "editor"],
            "comprehensive": ["domain_expert", "researcher", "editor", "critic"]
        }

    def analyze_topic_for_roles(self, topic: str, max_roles: int = 4) -> List[str]:
        """分析主题并选择最适合的角色

        Args:
            topic: 主题描述
            max_roles: 最大返回角色数量

        Returns:
            List[str]: 推荐的角色列表
        """
        if not topic or not isinstance(topic, str):
            return ["domain_expert", "researcher", "editor"][:max_roles]

        topic_lower = topic.lower()

        # 计算每个角色的匹配分数
        role_scores = {}

        for role, keywords in self.role_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in topic_lower:
                    score += 1
            role_scores[role] = score

        # 识别主题类型
        topic_type = self._identify_topic_type(topic_lower)

        # 根据主题类型获取基础角色列表
        base_roles = self.topic_role_mapping.get(topic_type, ["domain_expert", "researcher", "editor"])

        # 结合关键词匹配分数和主题类型推荐
        final_scores = {}
        for role in base_roles:
            # 主题类型推荐的基础分数
            base_score = 10 if role in base_roles else 0

            # 关键词匹配分数
            keyword_score = role_scores.get(role, 0)

            # 总分 = 基础分数 + 关键词分数
            final_scores[role] = base_score + keyword_score

        # 添加其他有关键词匹配的角色
        for role, score in role_scores.items():
            if role not in final_scores and score > 0:
                final_scores[role] = score

        # 按分数排序并选择前N个角色
        sorted_roles = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        selected_roles = [role for role, score in sorted_roles[:max_roles] if score > 0]

        # 如果没有角色被选中，返回默认角色
        if not selected_roles:
            selected_roles = ["domain_expert", "researcher", "editor"][:max_roles]

        return selected_roles

    def _identify_topic_type(self, topic_lower: str) -> str:
        """识别主题类型

        Args:
            topic_lower: 小写的主题字符串

        Returns:
            str: 主题类型
        """
        # 技术类主题关键词
        technical_keywords = ["技术", "开发", "编程", "系统", "算法", "架构", "设计模式"]
        # 研究类主题关键词
        research_keywords = ["研究", "分析", "调查", "报告", "数据", "实验", "测试"]
        # 分析类主题关键词
        analysis_keywords = ["分析", "趋势", "市场", "商业", "投资", "战略", "预测"]
        # 教育类主题关键词
        educational_keywords = ["教学", "学习", "教程", "入门", "基础", "概念", "解释"]
        # 评审类主题关键词
        review_keywords = ["评价", "评估", "审查", "批评", "优缺点", "对比"]
        # 开发类主题关键词
        development_keywords = ["开发", "建设", "实施", "部署", "项目", "产品"]

        # 计算各类别的匹配分数
        category_scores = {
            "technical": sum(1 for kw in technical_keywords if kw in topic_lower),
            "research": sum(1 for kw in research_keywords if kw in topic_lower),
            "analysis": sum(1 for kw in analysis_keywords if kw in topic_lower),
            "educational": sum(1 for kw in educational_keywords if kw in topic_lower),
            "review": sum(1 for kw in review_keywords if kw in topic_lower),
            "development": sum(1 for kw in development_keywords if kw in topic_lower)
        }

        # 找到分数最高的类别
        max_score = max(category_scores.values())
        if max_score > 0:
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            return best_category

        # 如果没有明确类别，返回综合类型
        return "comprehensive"

    def get_role_recommendation_reason(self, topic: str, selected_roles: List[str]) -> Dict[str, str]:
        """获取角色推荐的理由

        Args:
            topic: 主题
            selected_roles: 选择的角色列表

        Returns:
            Dict[str, str]: 角色到推荐理由的映射
        """
        topic_lower = topic.lower()
        reasons = {}

        role_reasons = {
            "domain_expert": "该主题涉及专业技术知识，需要领域专家提供深入见解",
            "researcher": "该主题需要研究支撑，提供数据和分析依据",
            "editor": "该主题需要良好的结构和表达，确保内容清晰易懂",
            "critic": "该主题需要批判性思考，识别问题和改进空间",
            "analyst": "该主题需要分析视角，评估趋势和影响",
            "teacher": "该主题需要教学角度，确保概念清晰和易于理解"
        }

        for role in selected_roles:
            reasons[role] = role_reasons.get(role, "基于主题分析推荐此角色")

        return reasons

    def enhance_role_selection_with_context(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None,
        max_roles: int = 4
    ) -> List[str]:
        """基于上下文增强角色选择

        Args:
            topic: 主题
            context: 上下文信息，可包含：目标受众、内容类型、复杂度等
            max_roles: 最大角色数量

        Returns:
            List[str]: 增强后的角色选择
        """
        # 基础角色选择
        base_roles = self.analyze_topic_for_roles(topic, max_roles)

        if not context:
            return base_roles

        # 根据上下文调整角色选择
        enhanced_roles = base_roles.copy()

        # 目标受众考虑
        target_audience = context.get("target_audience", "")
        if target_audience == "beginners":
            if "teacher" not in enhanced_roles:
                enhanced_roles.append("teacher")
        elif target_audience == "experts":
            if "critic" not in enhanced_roles:
                enhanced_roles.append("critic")

        # 内容类型考虑
        content_type = context.get("content_type", "")
        if content_type == "tutorial":
            if "teacher" not in enhanced_roles:
                enhanced_roles.append("teacher")
        elif content_type == "review":
            if "critic" not in enhanced_roles:
                enhanced_roles.append("critic")
        elif content_type == "research_paper":
            if "researcher" not in enhanced_roles:
                enhanced_roles.append("researcher")

        # 复杂度考虑
        complexity = context.get("complexity", "")
        if complexity == "high":
            if "analyst" not in enhanced_roles:
                enhanced_roles.append("analyst")

        # 限制角色数量
        return enhanced_roles[:max_roles]