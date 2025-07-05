"""任务分类器
将用户需求智能分类为"内容创作"或"文档分析"两大类
"""

import re
from enum import Enum
from typing import Any


class TaskType(Enum):
    """任务类型枚举"""

    CONTENT_CREATION = "content_creation"  # 内容创作
    DOCUMENT_ANALYSIS = "document_analysis"  # 文档分析


class TaskClassifier:
    """任务分类器

    根据用户输入的自然语言需求，智能判断任务类型并推荐相应的处理流程
    """

    def __init__(self):
        """初始化任务分类器"""
        self.creation_keywords = self._load_creation_keywords()
        self.analysis_keywords = self._load_analysis_keywords()
        self.creation_patterns = self._load_creation_patterns()
        self.analysis_patterns = self._load_analysis_patterns()

    def _load_creation_keywords(self) -> list[str]:
        """加载内容创作关键词"""
        return [
            # 论文撰写
            "撰写",
            "写作",
            "编写",
            "创作",
            "起草",
            "构思",
            "设计",
            "论文",
            "paper",
            "研究",
            "study",
            "调研",
            "survey",
            # 教材编辑
            "教材",
            "教程",
            "课程",
            "教学",
            "编辑",
            "编纂",
            "编制",
            "textbook",
            "tutorial",
            "course",
            "curriculum",
            # 报告编写
            "报告编写",
            "方案制定",
            "计划制定",
            "策划",
            "规划",
            "proposal",
            "plan",
            "strategy",
            "design",
            # 协作创作
            "协作",
            "共创",
            "合作",
            "团队",
            "分工",
            "协同",
            "collaboration",
            "teamwork",
            "cooperative",
            # 生成动词
            "生成",
            "产出",
            "输出",
            "制作",
            "建立",
            "构建",
            "generate",
            "create",
            "produce",
            "build",
            "develop",
        ]

    def _load_analysis_keywords(self) -> list[str]:
        """加载文档分析关键词"""
        return [
            # 分析动词
            "分析",
            "解析",
            "审查",
            "检查",
            "评估",
            "评价",
            "识别",
            "analyze",
            "review",
            "examine",
            "assess",
            "evaluate",
            "identify",
            # 提取动词
            "提取",
            "抽取",
            "获取",
            "收集",
            "整理",
            "归纳",
            "总结",
            "extract",
            "collect",
            "summarize",
            "organize",
            "gather",
            # 文档类型
            "财报",
            "财务报告",
            "合同",
            "协议",
            "文献",
            "论文",
            "报告",
            "financial",
            "contract",
            "agreement",
            "literature",
            "document",
            # 处理对象
            "现有",
            "已有",
            "给定",
            "提供的",
            "上传的",
            "输入的",
            "existing",
            "given",
            "provided",
            "uploaded",
            "input",
            # 结构化处理
            "结构化",
            "格式化",
            "标准化",
            "规范化",
            "整合",
            "structure",
            "format",
            "standardize",
            "integrate",
        ]

    def _load_creation_patterns(self) -> list[str]:
        """加载内容创作模式"""
        return [
            r"写.*?论文",
            r"撰写.*?报告",
            r"编写.*?教材",
            r"制定.*?方案",
            r"设计.*?流程",
            r"创建.*?协议",
            r"建立.*?体系",
            r"开发.*?系统",
            r"从.*?到.*?",  # 如"从想法到论文"
            r".*?编辑.*?",
            r".*?创作.*?",
            r".*?协作.*?",
        ]

    def _load_analysis_patterns(self) -> list[str]:
        """加载文档分析模式"""
        return [
            r"分析.*?文档",
            r"分析.*?报告",
            r"分析.*?数据",
            r"提取.*?信息",
            r"审查.*?合同",
            r"检查.*?财报",
            r"评估.*?风险",
            r"识别.*?问题",
            r"对.*?进行.*?分析",
            r"从.*?中.*?提取",
            r".*?结构化.*?",
        ]

    def classify_task(self, user_input: str) -> tuple[TaskType, float, dict[str, Any]]:
        """分类用户任务

        Args:
        ----
            user_input: 用户输入的自然语言需求

        Returns:
        -------
            (任务类型, 置信度, 详细信息)

        """
        user_input_lower = user_input.lower()

        # 计算关键词匹配分数
        creation_keyword_score = self._calculate_keyword_score(
            user_input_lower,
            self.creation_keywords,
        )
        analysis_keyword_score = self._calculate_keyword_score(
            user_input_lower,
            self.analysis_keywords,
        )

        # 计算模式匹配分数
        creation_pattern_score = self._calculate_pattern_score(
            user_input,
            self.creation_patterns,
        )
        analysis_pattern_score = self._calculate_pattern_score(
            user_input,
            self.analysis_patterns,
        )

        # 综合评分
        creation_total = creation_keyword_score + creation_pattern_score
        analysis_total = analysis_keyword_score + analysis_pattern_score

        # 特殊规则判断
        special_rules_result = self._apply_special_rules(user_input)
        if special_rules_result:
            task_type, confidence = special_rules_result
            return (
                task_type,
                confidence,
                {
                    "creation_score": creation_total,
                    "analysis_score": analysis_total,
                    "decision_reason": "特殊规则匹配",
                    "matched_keywords": self._get_matched_keywords(user_input_lower),
                },
            )

        # 基于分数判断
        if creation_total > analysis_total:
            task_type = TaskType.CONTENT_CREATION
            confidence = min(
                creation_total / (creation_total + analysis_total + 0.1),
                0.95,
            )
        elif analysis_total > creation_total:
            task_type = TaskType.DOCUMENT_ANALYSIS
            confidence = min(
                analysis_total / (creation_total + analysis_total + 0.1),
                0.95,
            )
        else:
            # 分数相等时的默认判断
            task_type = TaskType.DOCUMENT_ANALYSIS  # 默认为分析类
            confidence = 0.5

        return (
            task_type,
            confidence,
            {
                "creation_score": creation_total,
                "analysis_score": analysis_total,
                "decision_reason": "分数比较",
                "matched_keywords": self._get_matched_keywords(user_input_lower),
            },
        )

    def _calculate_keyword_score(self, text: str, keywords: list[str]) -> float:
        """计算关键词匹配分数"""
        score = 0.0
        for keyword in keywords:
            if keyword in text:
                # 根据关键词长度给予不同权重
                weight = len(keyword) / 10.0 + 0.5
                score += weight
        return score

    def _calculate_pattern_score(self, text: str, patterns: list[str]) -> float:
        """计算模式匹配分数"""
        score = 0.0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 2.0  # 模式匹配给予更高权重
        return score

    def _apply_special_rules(self, user_input: str) -> tuple[TaskType, float] | None:
        """应用特殊规则"""
        user_input_lower = user_input.lower()

        # 明确的创作任务
        creation_indicators = [
            "论文撰写",
            "教材编辑",
            "报告编写",
            "方案制定",
            "从零开始",
            "从头开始",
            "新建",
            "创建",
            "协作编辑",
            "团队创作",
            "共同撰写",
        ]

        for indicator in creation_indicators:
            if indicator in user_input_lower:
                return TaskType.CONTENT_CREATION, 0.9

        # 明确的分析任务
        analysis_indicators = [
            "分析现有",
            "分析已有",
            "分析给定",
            "分析上传",
            "提取信息",
            "结构化分析",
            "数据分析",
            "财报分析",
            "合同审查",
            "文档解析",
        ]

        for indicator in analysis_indicators:
            if indicator in user_input_lower:
                return TaskType.DOCUMENT_ANALYSIS, 0.9

        return None

    def _get_matched_keywords(self, text: str) -> dict[str, list[str]]:
        """获取匹配的关键词"""
        matched = {
            "creation": [kw for kw in self.creation_keywords if kw in text],
            "analysis": [kw for kw in self.analysis_keywords if kw in text],
        }
        return matched

    def get_recommended_workflow(self, task_type: TaskType) -> dict[str, Any]:
        """根据任务类型推荐工作流程"""
        if task_type == TaskType.CONTENT_CREATION:
            return {
                "workflow_type": "creation",
                "stages": ["需求分析与规划", "专家团队组建", "分工协作创作", "内容整合优化", "质量审查定稿"],
                "features": ["多专家协作", "分阶段创作", "版本管理", "共识机制", "质量控制"],
            }
        else:
            return {
                "workflow_type": "analysis",
                "stages": ["文档预处理", "信息提取分析", "结构化整理", "报告生成", "结果验证"],
                "features": ["智能解析", "信息提取", "结构化输出", "溯源支持", "格式标准化"],
            }


# 创建全局实例
task_classifier = TaskClassifier()
