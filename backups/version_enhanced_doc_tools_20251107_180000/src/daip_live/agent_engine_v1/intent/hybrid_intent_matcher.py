"""
混合意图匹配器

结合关键词匹配、正则表达式、语义相似度等多种策略进行意图识别。
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict

from ..services.interfaces import IntentRecognitionResult


logger = logging.getLogger(__name__)


class HybridIntentMatcher:
    """混合意图匹配器"""

    def __init__(self):
        """初始化混合意图匹配器"""
        # 意图关键词字典
        self.intent_keywords = self._build_intent_keywords()

        # 意图正则表达式模式
        self.intent_patterns = self._build_intent_patterns()

        # 意图权重配置
        self.strategy_weights = {
            "keyword": 0.4,      # 关键词匹配权重
            "pattern": 0.4,       # 正则模式匹配权重
            "context": 0.2        # 上下文匹配权重
        }

    def _build_intent_keywords(self) -> Dict[str, List[str]]:
        """构建意图关键词字典"""
        return {
            "file_read": [
                "读取", "查看", "打开", "显示", "获取", "检查", "阅读", "查看", "show", "read",
                "open", "display", "get", "view", "cat", "less", "more"
            ],
            "file_write": [
                "写入", "创建", "保存", "生成", "编写", "新建", "添加", "更新", "修改", "编辑",
                "write", "create", "save", "generate", "make", "add", "update", "edit"
            ],
            "file_delete": [
                "删除", "移除", "清理", "清除", "移走", "去掉", "rm", "delete", "remove",
                "clean", "clear", "erase"
            ],
            "list_files": [
                "列出", "显示", "查看目录", "浏览", "ls", "dir", "list", "show", "browse"
            ],
            "data_analysis": [
                "分析", "统计", "计算", "处理", "挖掘", "聚合", "分析数据", "统计", "计算",
                "analyze", "statistics", "calculate", "process", "mining", "aggregate"
            ],
            "report_generation": [
                "报告", "报表", "生成报告", "制作报表", "输出报告", "创建文档", "report",
                "generate report", "create document", "output report"
            ],
            "security_scan": [
                "安全", "漏洞", "扫描", "检查", "审计", "安全检查", "漏洞扫描", "security",
                "scan", "vulnerability", "audit", "security check"
            ],
            "help": [
                "帮助", "说明", "指南", "文档", "教程", "使用方法", "操作指南", "help",
                "documentation", "guide", "manual", "tutorial", "how to"
            ],
            "question": [
                "什么", "为什么", "如何", "怎么", "是否", "能否", "可以吗", "吗", "呢", "？",
                "what", "why", "how", "where", "when", "can", "could", "would", "should", "?"
            ],
            "search": [
                "搜索", "查找", "寻找", "检索", "查询", "寻找", "search", "find", "look for",
                "query", "retrieve"
            ],
            "tool_execute": [
                "执行", "运行", "启动", "开始", "激活", "execute", "run", "start", "launch",
                "activate", "perform"
            ],
            "code_analysis": [
                "代码", "编程", "程序", "审查", "分析代码", "代码质量", "code", "programming",
                "review", "code analysis", "code quality"
            ],
            "deployment_config": [
                "部署", "发布", "上线", "配置", "docker", "ci", "cd", "deploy", "release",
                "publish", "deployment", "configuration"
            ],
            "monitoring_setup": [
                "监控", "监视", "观察", "告警", "仪表板", "monitor", "watch", "observe",
                "alert", "dashboard", "metrics"
            ],
            "test_creation": [
                "测试", "自动化", "单元测试", "集成测试", "test", "testing", "automation",
                "unit test", "integration test"
            ],
            "performance_test": [
                "性能", "压力", "负载", "基准", "性能测试", "压力测试", "performance",
                "stress", "load", "benchmark", "performance test"
            ],
            "system_design": [
                "设计", "架构", "规划", "方案", "权限", "设计系统", "design", "architecture",
                "planning", "solution", "permission", "system design"
            ]
        }

    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """构建意图正则表达式模式"""
        return {
            "file_read": [
                r"读取.*文件",
                r"查看.*文件",
                r"打开.*文件",
                r"显示.*文件",
                r"获取.*文件",
                r".*文件.*内容",
                r".*\.md$",
                r".*\.txt$",
                r".*\.yaml$",
                r".*\.yml$",
                r".*\.json$",
                r".*\.log$",
                r"read\s+\w+.*file",
                r"open\s+\w+.*file",
                r"show\s+\w+.*file"
            ],
            "file_write": [
                r"创建.*文件",
                r"写入.*文件",
                r"保存.*文件",
                r"生成.*文件",
                r"新建.*文件",
                r".*文件.*到",
                r".*写入.*",
                r".*保存.*",
                r"create\s+\w+.*file",
                r"write\s+\w+.*file",
                r"save.*to.*file",
                r"generate.*file"
            ],
            "file_delete": [
                r"删除.*文件",
                r"移除.*文件",
                r"清理.*文件",
                r"清除.*文件",
                r".*文件.*删除",
                r".*文件.*移除",
                r"delete.*file",
                r"remove.*file",
                r"clean.*file"
            ],
            "list_files": [
                r"列出.*文件",
                r"显示.*目录",
                r"查看.*目录",
                r"浏览.*目录",
                r"ls.*",
                r"dir.*",
                r"list.*files",
                r"show.*directory"
            ],
            "data_analysis": [
                r"分析.*数据",
                r"统计.*数据",
                r"处理.*数据",
                r"计算.*数据",
                r".*数据分析",
                r".*数据统计",
                r"analyze.*data",
                r"process.*data",
                r"calculate.*data",
                r".*\.csv$",
                r".*\.xlsx$",
                r".*\.xls$"
            ],
            "security_scan": [
                r"安全.*检查",
                r"漏洞.*扫描",
                r"安全.*审计",
                r".*安全.*",
                r".*漏洞.*",
                r"security.*check",
                r"vulnerability.*scan",
                r"security.*audit"
            ],
            "deployment_config": [
                r"部署.*应用",
                r"发布.*版本",
                r"配置.*docker",
                r"设置.*ci",
                r"设置.*cd",
                r"deploy.*application",
                r"release.*version",
                r"docker.*config",
                r"ci.*cd.*setup"
            ],
            "monitoring_setup": [
                r"配置.*监控",
                r"设置.*告警",
                r"监控.*系统",
                r"建立.*监控",
                r"setup.*monitoring",
                r"configure.*alert",
                r"monitor.*system",
                r"create.*dashboard"
            ]
        }

    def match_intent(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentRecognitionResult:
        """
        混合意图匹配

        Args:
            text: 输入文本
            context: 上下文信息

        Returns:
            意图识别结果
        """
        if not context:
            context = {}

        # 1. 关键词匹配
        keyword_results = self._keyword_match(text)

        # 2. 正则模式匹配
        pattern_results = self._pattern_match(text)

        # 3. 上下文匹配
        context_results = self._context_match(text, context)

        # 4. 综合评估
        final_intent, confidence, parameters = self._combine_results(
            keyword_results, pattern_results, context_results
        )

        return IntentRecognitionResult(
            intent=final_intent,
            confidence=confidence,
            parameters=parameters,
            reasoning=self._generate_reasoning(keyword_results, pattern_results, context_results),
            strategy_used="hybrid_matching"
        )

    def _keyword_match(self, text: str) -> Dict[str, float]:
        """关键词匹配"""
        text_lower = text.lower()
        results = {}

        for intent, keywords in self.intent_keywords.items():
            score = 0
            matched_keywords = []

            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
                    matched_keywords.append(keyword)

            if score > 0:
                # 归一化分数
                results[intent] = min(score / len(keywords), 1.0)

        return results

    def _pattern_match(self, text: str) -> Dict[str, float]:
        """正则模式匹配"""
        results = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0
            matched_patterns = []

            for pattern in patterns:
                try:
                    if re.search(pattern, text, re.IGNORECASE):
                        score += 1
                        matched_patterns.append(pattern)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{pattern}': {e}")

            if score > 0:
                # 归一化分数
                results[intent] = min(score / len(patterns), 1.0)

        return results

    def _context_match(self, text: str, context: Dict[str, Any]) -> Dict[str, float]:
        """上下文匹配"""
        results = {}
        text_lower = text.lower()

        # 用户角色上下文
        user_role = context.get("user_role", "").lower()

        # 工作目录上下文
        working_dir = context.get("working_directory", "").lower()

        # 项目类型上下文
        project_type = context.get("project_type", "").lower()

        # 最近文件上下文
        recent_files = context.get("recent_files", [])
        if isinstance(recent_files, list):
            recent_files = [f.lower() for f in recent_files]

        # 基于上下文调整意图分数
        if user_role == "developer" or user_role == "dev":
            if any(word in text_lower for word in ["代码", "code", "编程", "program"]):
                results["code_analysis"] = 0.3
            if any(word in text_lower for word in ["部署", "deploy", "发布", "release"]):
                results["deployment_config"] = 0.3
            if any(word in text_lower for word in ["测试", "test", "调试", "debug"]):
                results["test_creation"] = 0.3

        elif user_role == "analyst" or user_role == "数据分析师":
            if any(word in text_lower for word in ["数据", "data", "分析", "analyze"]):
                results["data_analysis"] = 0.3
            if any(word in text_lower for word in ["报告", "report", "报表"]):
                results["report_generation"] = 0.3

        elif user_role == "admin" or user_role == "administrator":
            if any(word in text_lower for word in ["安全", "security", "权限", "permission"]):
                results["security_scan"] = 0.3
            if any(word in text_lower for word in ["监控", "monitor", "监视", "watch"]):
                results["monitoring_setup"] = 0.3

        # 基于工作目录调整
        if any(word in working_dir for word in ["project", "src", "app"]):
            if any(word in text_lower for word in ["文件", "file"]):
                results["file_read"] = 0.2
                results["file_write"] = 0.2

        # 基于最近文件调整
        for file_name in recent_files:
            if file_name in text_lower:
                if any(word in text_lower for word in ["读取", "查看", "打开", "read", "open"]):
                    results["file_read"] = 0.4
                elif any(word in text_lower for word in ["写入", "修改", "edit", "write"]):
                    results["file_write"] = 0.4
                elif any(word in text_lower for word in ["删除", "remove", "delete"]):
                    results["file_delete"] = 0.4
                break

        return results

    def _combine_results(
        self,
        keyword_results: Dict[str, float],
        pattern_results: Dict[str, float],
        context_results: Dict[str, float]
    ) -> Tuple[str, float, Dict[str, Any]]:
        """综合评估结果"""
        # 收集所有候选意图
        all_intents = set(keyword_results.keys()) | set(pattern_results.keys()) | set(context_results.keys())

        if not all_intents:
            return "unknown", 0.0, {}

        # 计算每个意图的综合分数
        intent_scores = {}
        for intent in all_intents:
            keyword_score = keyword_results.get(intent, 0.0) * self.strategy_weights["keyword"]
            pattern_score = pattern_results.get(intent, 0.0) * self.strategy_weights["pattern"]
            context_score = context_results.get(intent, 0.0) * self.strategy_weights["context"]

            total_score = keyword_score + pattern_score + context_score
            intent_scores[intent] = total_score

        # 找到最高分数的意图
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        final_intent = best_intent[0]
        confidence = best_intent[1]

        # 提取参数
        parameters = self._extract_parameters(final_intent)

        return final_intent, confidence, parameters

    def _extract_parameters(self, intent: str) -> Dict[str, Any]:
        """提取意图参数"""
        # 这里可以实现更复杂的参数提取逻辑
        # 目前返回基本的参数结构
        return {
            "intent_type": intent,
            "extraction_method": "hybrid_matching"
        }

    def _generate_reasoning(
        self,
        keyword_results: Dict[str, float],
        pattern_results: Dict[str, float],
        context_results: Dict[str, float]
    ) -> str:
        """生成推理过程说明"""
        reasoning_parts = []

        if keyword_results:
            top_keyword = max(keyword_results.items(), key=lambda x: x[1])
            reasoning_parts.append(f"关键词匹配: {top_keyword[0]} (分数: {top_keyword[1]:.2f})")

        if pattern_results:
            top_pattern = max(pattern_results.items(), key=lambda x: x[1])
            reasoning_parts.append(f"模式匹配: {top_pattern[0]} (分数: {top_pattern[1]:.2f})")

        if context_results:
            top_context = max(context_results.items(), key=lambda x: x[1])
            reasoning_parts.append(f"上下文匹配: {top_context[0]} (分数: {top_context[1]:.2f})")

        return " | ".join(reasoning_parts) if reasoning_parts else "无匹配结果"

    def add_custom_intent(self, intent_name: str, keywords: List[str], patterns: List[str] = None):
        """添加自定义意图"""
        if patterns is None:
            patterns = []

        self.intent_keywords[intent_name] = keywords
        self.intent_patterns[intent_name] = patterns

        logger.info(f"Added custom intent '{intent_name}' with {len(keywords)} keywords and {len(patterns)} patterns")

    def update_strategy_weights(self, keyword_weight: float, pattern_weight: float, context_weight: float):
        """更新策略权重"""
        total = keyword_weight + pattern_weight + context_weight
        if abs(total - 1.0) > 0.001:
            # 归一化权重
            keyword_weight /= total
            pattern_weight /= total
            context_weight /= total

        self.strategy_weights = {
            "keyword": keyword_weight,
            "pattern": pattern_weight,
            "context": context_weight
        }

        logger.info(f"Updated strategy weights: keyword={keyword_weight:.2f}, pattern={pattern_weight:.2f}, context={context_weight:.2f}")