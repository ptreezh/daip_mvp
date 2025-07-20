"""增强的工具检索系统
基于多维度相似性和语义理解的智能工具检索
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

# 可选依赖处理
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import jieba

    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


@dataclass
class ToolMatch:
    """工具匹配结果"""

    tool_name: str
    confidence: float
    match_reasons: list[str]
    semantic_score: float
    keyword_score: float
    context_score: float


class EnhancedToolRetrieval:
    """增强的工具检索系统

    特性：
    1. 多维度相似性计算（语义、关键词、上下文）
    2. 动态权重调整
    3. 工具使用历史学习
    4. 上下文感知检索
    """

    def __init__(self, tools_definitions: list[dict[str, Any]]):
        self.logger = logging.getLogger(__name__)
        self.tools_definitions = tools_definitions
        self.tool_index = self._build_tool_index()
        self.usage_history = {}
        self.tfidf_vectorizer = None
        self.tool_vectors = None
        self._initialize_vectorizer()

        # 工具类别映射
        self.tool_categories = {
            "task_management": [
                "create_task",
                "get_task_info",
                "delete_task",
                "list_tasks",
                "update_task",
                "get_task_tree",
                "add_task_comment",
                "sign_task",
            ],
            "collaboration": [
                "list_roles",
                "set_active_role",
                "consensus_calculation",
                "set_collaboration_mode",
                "decompose_task",
            ],
            "memory_operations": [
                "save_role_memory",
                "read_role_memory",
                "read_wiki",
                "write_wiki",
                "edit_wiki",
                "vote_wiki_edit",
            ],
            "validation": ["validate_protocol"],
            "optimization": ["prompt_optimization"],
        }

        # 反向映射：工具名 -> 类别
        self.tool_to_category = {}
        for category, tools in self.tool_categories.items():
            for tool in tools:
                self.tool_to_category[tool] = category

    def _build_tool_index(self) -> dict[str, dict[str, Any]]:
        """构建工具索引"""
        index = {}
        for tool_def in self.tools_definitions:
            function_info = tool_def.get("function", {})
            tool_name = function_info.get("name", "")

            # 提取工具的所有文本信息
            description = function_info.get("description", "")
            parameters = function_info.get("parameters", {})

            # 构建搜索文本
            search_text = f"{tool_name} {description}"

            # 添加参数信息
            if "properties" in parameters:
                for param_name, param_info in parameters["properties"].items():
                    param_desc = param_info.get("description", "")
                    search_text += f" {param_name} {param_desc}"

            index[tool_name] = {
                "definition": tool_def,
                "search_text": search_text,
                "description": description,
                "parameters": parameters,
                "keywords": self._extract_keywords(search_text),
            }

        return index

    def _extract_keywords(self, text: str) -> list[str]:
        """提取关键词"""
        keywords = []

        # 中文分词（如果jieba可用）
        if JIEBA_AVAILABLE:
            chinese_words = list(jieba.cut(text))
            keywords.extend(chinese_words)
        else:
            # 简单的中文字符分割
            chinese_chars = re.findall(r"[\u4e00-\u9fff]+", text)
            keywords.extend(chinese_chars)

        # 英文单词提取
        english_words = re.findall(r"[a-zA-Z]+", text)
        keywords.extend(english_words)

        # 合并并去重
        keywords = list(set(keywords))

        # 过滤停用词和短词
        stop_words = {
            "的",
            "是",
            "在",
            "有",
            "和",
            "或",
            "a",
            "an",
            "the",
            "and",
            "or",
            "to",
            "for",
            "of",
            "with",
        }
        keywords = [
            word.lower()
            for word in keywords
            if len(word) > 1 and word.lower() not in stop_words
        ]

        return keywords

    def _initialize_vectorizer(self):
        """初始化TF-IDF向量化器"""
        if not self.tool_index or not SKLEARN_AVAILABLE:
            self.logger.warning("sklearn不可用，将使用简化的检索方法")
            return

        # 准备文档
        documents = [info["search_text"] for info in self.tool_index.values()]

        # 创建TF-IDF向量化器
        # 根据文档数量调整参数
        doc_count = len(documents)
        max_df = (
            min(0.95, max(0.5, (doc_count - 1) / doc_count)) if doc_count > 1 else 1.0
        )

        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=min(1000, doc_count * 10),
            stop_words=None,  # 我们已经在关键词提取中处理了停用词
            ngram_range=(1, 2),  # 使用1-gram和2-gram
            min_df=1,
            max_df=max_df,
        )

        try:
            self.tool_vectors = self.tfidf_vectorizer.fit_transform(documents)
            self.logger.info(f"成功初始化工具向量化器，处理了{len(documents)}个工具")
        except Exception as e:
            self.logger.warning(f"初始化向量化器失败，将使用简化检索: {e}")
            self.tfidf_vectorizer = None
            self.tool_vectors = None

    def search_tools(
        self,
        query: str,
        k: int = 5,
        context: dict[str, Any] = None,
    ) -> list[ToolMatch]:
        """搜索相关工具

        Args:
        ----
            query: 查询文本
            k: 返回结果数量
            context: 上下文信息

        Returns:
        -------
            匹配的工具列表

        """
        if not self.tool_index:
            return []

        context = context or {}
        matches = []

        # 1. 语义相似性搜索
        semantic_matches = self._semantic_search(query, k * 2)

        # 2. 关键词匹配
        keyword_matches = self._keyword_search(query, k * 2)

        # 3. 上下文相关性
        context_matches = self._context_search(query, context, k * 2)

        # 4. 合并和评分
        all_matches = {}

        # 合并语义匹配
        for tool_name, score in semantic_matches:
            if tool_name not in all_matches:
                all_matches[tool_name] = ToolMatch(
                    tool_name=tool_name,
                    confidence=0,
                    match_reasons=[],
                    semantic_score=score,
                    keyword_score=0,
                    context_score=0,
                )
            all_matches[tool_name].semantic_score = score
            if score > 0.3:
                all_matches[tool_name].match_reasons.append(f"语义相似度: {score:.3f}")

        # 合并关键词匹配
        for tool_name, score in keyword_matches:
            if tool_name not in all_matches:
                all_matches[tool_name] = ToolMatch(
                    tool_name=tool_name,
                    confidence=0,
                    match_reasons=[],
                    semantic_score=0,
                    keyword_score=score,
                    context_score=0,
                )
            all_matches[tool_name].keyword_score = score
            if score > 0.3:
                all_matches[tool_name].match_reasons.append(f"关键词匹配: {score:.3f}")

        # 合并上下文匹配
        for tool_name, score in context_matches:
            if tool_name in all_matches:
                all_matches[tool_name].context_score = score
                if score > 0.3:
                    all_matches[tool_name].match_reasons.append(f"上下文相关: {score:.3f}")

        # 5. 计算综合置信度
        for match in all_matches.values():
            # 动态权重调整
            weights = self._calculate_dynamic_weights(query, context)

            match.confidence = (
                match.semantic_score * weights["semantic"]
                + match.keyword_score * weights["keyword"]
                + match.context_score * weights["context"]
            )

            # 历史使用加权
            if match.tool_name in self.usage_history:
                usage_boost = min(self.usage_history[match.tool_name] / 10, 0.1)
                match.confidence += usage_boost
                if usage_boost > 0.05:
                    match.match_reasons.append(f"历史使用频率加成: +{usage_boost:.3f}")

        # 6. 排序和返回
        sorted_matches = sorted(
            all_matches.values(),
            key=lambda x: x.confidence,
            reverse=True,
        )

        # 记录搜索结果
        self.logger.info(f"工具搜索查询: '{query}' -> 找到{len(sorted_matches)}个匹配")
        for i, match in enumerate(sorted_matches[:k]):
            self.logger.info(
                f"  {i+1}. {match.tool_name} (置信度: {match.confidence:.3f})",
            )

        return sorted_matches[:k]

    def _semantic_search(self, query: str, k: int) -> list[tuple[str, float]]:
        """语义相似性搜索"""
        if (
            not SKLEARN_AVAILABLE
            or not self.tfidf_vectorizer
            or self.tool_vectors is None
        ):
            # 回退到简单的文本匹配
            return self._simple_text_search(query, k)

        try:
            # 向量化查询
            query_vector = self.tfidf_vectorizer.transform([query])

            # 计算相似度
            similarities = cosine_similarity(query_vector, self.tool_vectors).flatten()

            # 确保similarities是numpy数组
            if not isinstance(similarities, np.ndarray):
                similarities = np.array(similarities)

            # 获取top-k结果
            if SKLEARN_AVAILABLE:
                top_indices = np.argsort(similarities)[::-1][:k]

                results = []
                tool_names = list(self.tool_index.keys())
                for idx in top_indices:
                    similarity_score = float(similarities[idx])
                    if similarity_score > 0:
                        results.append((tool_names[idx], similarity_score))

            return results
        except Exception as e:
            self.logger.error(f"语义搜索失败: {e}")
            return self._simple_text_search(query, k)

    def _simple_text_search(self, query: str, k: int) -> list[tuple[str, float]]:
        """简单文本搜索（sklearn不可用时的回退方案）"""
        query_lower = query.lower()
        results = []

        for tool_name, tool_info in self.tool_index.items():
            search_text = tool_info["search_text"].lower()

            # 简单的包含匹配评分
            score = 0
            query_words = query_lower.split()
            for word in query_words:
                if word in search_text:
                    score += 1

            if score > 0:
                # 归一化评分
                normalized_score = score / len(query_words)
                results.append((tool_name, normalized_score))

        # 排序并返回top-k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def _keyword_search(self, query: str, k: int) -> list[tuple[str, float]]:
        """关键词匹配搜索"""
        query_keywords = set(self._extract_keywords(query))
        if not query_keywords:
            return []

        results = []
        for tool_name, tool_info in self.tool_index.items():
            tool_keywords = set(tool_info["keywords"])

            # 计算关键词重叠度
            intersection = query_keywords.intersection(tool_keywords)
            union = query_keywords.union(tool_keywords)

            if intersection:
                jaccard_score = len(intersection) / len(union)
                overlap_score = len(intersection) / len(query_keywords)

                # 综合评分
                keyword_score = jaccard_score * 0.4 + overlap_score * 0.6
                results.append((tool_name, keyword_score))

        # 排序并返回top-k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def _context_search(
        self,
        query: str,
        context: dict[str, Any],
        k: int,
    ) -> list[tuple[str, float]]:
        """上下文相关性搜索"""
        results = []

        # 从上下文中提取信息
        current_role = context.get("current_role", "")
        recent_tools = context.get("recent_tools", [])
        conversation_topic = context.get("topic", "")

        for tool_name, tool_info in self.tool_index.items():
            context_score = 0

            # 1. 工具类别相关性
            tool_category = self.tool_to_category.get(tool_name, "")
            if tool_category:
                # 基于查询内容推断类别偏好
                if "任务" in query or "task" in query.lower():
                    if tool_category == "task_management":
                        context_score += 0.3
                elif "协作" in query or "角色" in query or "collaboration" in query.lower():
                    if tool_category == "collaboration":
                        context_score += 0.3
                elif "记忆" in query or "保存" in query or "memory" in query.lower():
                    if tool_category == "memory_operations":
                        context_score += 0.3

            # 2. 最近使用的工具相关性
            if recent_tools:
                for recent_tool in recent_tools[-3:]:  # 考虑最近3个工具
                    if recent_tool == tool_name:
                        context_score += 0.2
                    elif self.tool_to_category.get(recent_tool) == tool_category:
                        context_score += 0.1

            # 3. 角色相关性
            if current_role and tool_category == "collaboration":
                context_score += 0.1

            if context_score > 0:
                results.append((tool_name, context_score))

        # 排序并返回top-k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def _calculate_dynamic_weights(
        self,
        query: str,
        context: dict[str, Any],
    ) -> dict[str, float]:
        """计算动态权重"""
        # 默认权重
        weights = {"semantic": 0.5, "keyword": 0.3, "context": 0.2}

        # 根据查询长度调整
        query_length = len(query)
        if query_length < 10:  # 短查询，更依赖关键词
            weights["keyword"] += 0.1
            weights["semantic"] -= 0.1
        elif query_length > 50:  # 长查询，更依赖语义
            weights["semantic"] += 0.1
            weights["keyword"] -= 0.1

        # 根据上下文信息调整
        if context.get("recent_tools") or context.get("current_role"):
            weights["context"] += 0.1
            weights["semantic"] -= 0.05
            weights["keyword"] -= 0.05

        return weights

    def update_usage_history(self, tool_name: str):
        """更新工具使用历史"""
        if tool_name not in self.usage_history:
            self.usage_history[tool_name] = 0
        self.usage_history[tool_name] += 1

    def get_tool_recommendations(
        self,
        query: str,
        context: dict[str, Any] = None,
    ) -> list[str]:
        """获取工具推荐列表"""
        matches = self.search_tools(query, k=5, context=context)
        return [match.tool_name for match in matches if match.confidence > 0.2]
