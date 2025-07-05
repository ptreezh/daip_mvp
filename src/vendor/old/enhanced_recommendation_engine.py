"""增强版角色推荐引擎
集成向量相似度和语义匹配，提供更精准的角色推荐
"""

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
import requests

from src.chat_config import get_recommendation_config
from src.expert_library import ExpertLibrary


@dataclass
class RecommendationContext:
    """推荐上下文"""

    topic: str
    current_participants: list[str]
    desired_expertise: list[str]
    conversation_type: str = "讨论"
    domain: str = "通用"
    complexity_level: str = "中等"
    language: str = "中文"
    max_recommendations: int = 6


class VectorStore:
    """向量存储和检索"""

    def __init__(self, cache_dir: str = "data/vectors"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.vectors: dict[str, np.ndarray] = {}
        self.metadata: dict[str, dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def get_ollama_embedding(self, text, model="nomic-embed-text"):
        url = "http://localhost:11434/api/embeddings"
        payload = {"model": model, "prompt": text}
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return np.array(response.json()["embedding"], dtype=np.float32)
        except Exception as e:
            self.logger.error(f"Ollama embedding failed: {e}")
            return None

    def encode_text(self, text: str) -> Optional[np.ndarray]:
        """文本向量化，仅用Ollama"""
        vec = self.get_ollama_embedding(text, model="nomic-embed-text")
        if vec is None or not isinstance(vec, np.ndarray) or vec.size == 0:
            return None
        return vec

    def add_expert_vector(self, expert_id: str, expert_data: dict[str, Any]):
        """添加专家向量"""
        if not isinstance(expert_id, str):
            return
        # 构建专家文本描述
        text_parts = []
        text_parts.append(expert_data.get("name", ""))
        text_parts.append(expert_data.get("title", ""))
        text_parts.append(expert_data.get("description", ""))
        text_parts.append(expert_data.get("bio", ""))
        text_parts.extend(expert_data.get("specialties", []))
        text_parts.extend(expert_data.get("skills", []))

        expert_text = " ".join([part for part in text_parts if part])

        # 生成向量
        vector = self.encode_text(expert_text)
        if vector is not None:
            self.vectors[expert_id] = vector
            self.metadata[expert_id] = {
                "name": expert_data.get("name", ""),
                "category": expert_data.get("category", ""),
                "specialties": expert_data.get("specialties", []),
                "text": expert_text,
            }

    def find_similar_experts(
        self,
        query_text: str,
        top_k: int = 10,
        exclude_ids: Optional[list[str]] = None,
    ) -> list[tuple[str, float]]:
        """查找相似专家"""
        if not self.vectors:
            return []
        if exclude_ids is None:
            exclude_ids = []
        # 查询向量化
        query_vector = self.encode_text(query_text)
        if query_vector is None or query_vector.size == 0:
            self.logger.error("查询文本未能生成有效embedding，无法进行语义推荐。")
            return []
        # 计算相似度
        similarities = []
        for expert_id, expert_vector in self.vectors.items():
            if not isinstance(expert_id, str):
                continue
            if expert_id in exclude_ids:
                continue
            if (
                not isinstance(expert_vector, np.ndarray)
                or expert_vector.size == 0
                or expert_vector.shape != query_vector.shape
            ):
                self.logger.warning(f"专家{expert_id}的向量无效或shape不符，已跳过。")
                continue
            # 余弦相似度
            similarity = np.dot(query_vector, expert_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(expert_vector)
            )
            similarities.append((expert_id, float(similarity)))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def save_cache(self):
        """保存向量缓存"""
        try:
            cache_file = self.cache_dir / "expert_vectors.pkl"
            with open(cache_file, "wb") as f:
                pickle.dump({"vectors": self.vectors, "metadata": self.metadata}, f)
            self.logger.info(f"向量缓存已保存: {cache_file}")
        except Exception as e:
            self.logger.error(f"保存向量缓存失败: {e}")

    def load_cache(self):
        """加载向量缓存"""
        try:
            cache_file = self.cache_dir / "expert_vectors.pkl"
            if cache_file.exists():
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)
                    self.vectors = data.get("vectors", {})
                    self.metadata = data.get("metadata", {})
                self.logger.info(f"向量缓存已加载: {len(self.vectors)} 个专家")
        except Exception as e:
            self.logger.error(f"加载向量缓存失败: {e}")


class EnhancedRecommendationEngine:
    """增强版推荐引擎"""

    def __init__(self, expert_library: ExpertLibrary):
        self.expert_library = expert_library
        self.vector_store = VectorStore()
        self.config = get_recommendation_config()
        self.logger = logging.getLogger(__name__)

        # 加载向量缓存
        self.vector_store.load_cache()

        # 构建专家向量索引
        self._build_expert_vectors()

    def _build_expert_vectors(self):
        """构建专家向量索引"""
        experts = self.expert_library.get_all_experts()
        for expert in experts:
            expert_id = expert.get("id")
            if not expert_id or not isinstance(expert_id, str):
                continue
            if expert_id not in self.vector_store.vectors:
                self.vector_store.add_expert_vector(expert_id, expert)
        # 保存缓存
        self.vector_store.save_cache()
        self.logger.info(f"专家向量索引构建完成: {len(self.vector_store.vectors)} 个专家")

    def recommend_roles(self, context: RecommendationContext) -> list[dict[str, Any]]:
        """推荐角色"""
        self.logger.info(f"开始推荐角色，主题: {context.topic}")

        # 1. 基于向量相似度的初步筛选
        semantic_candidates = self._get_semantic_candidates(context)

        # 2. 基于规则的筛选
        rule_based_candidates = self._get_rule_based_candidates(context)

        # 3. 合并和去重候选者
        all_candidates = self._merge_candidates(
            semantic_candidates,
            rule_based_candidates,
        )

        # 4. 综合评分
        scored_candidates = self._score_candidates(all_candidates, context)

        # 5. 多样性优化
        final_recommendations = self._optimize_diversity(scored_candidates, context)

        return final_recommendations[: context.max_recommendations]

    def _get_semantic_candidates(
        self,
        context: RecommendationContext,
    ) -> list[dict[str, Any]]:
        """基于语义相似度获取候选者"""
        # 直接用Ollama，无需判断HuggingFace

        # 构建查询文本
        query_parts = [context.topic]
        query_parts.extend(context.desired_expertise)
        if context.domain != "通用":
            query_parts.append(context.domain)

        query_text = " ".join(query_parts)

        # 查找相似专家
        similar_experts = self.vector_store.find_similar_experts(
            query_text,
            top_k=20,
            exclude_ids=context.current_participants,
        )

        # 获取专家详细信息
        candidates = []
        for expert_id, similarity in similar_experts:
            expert = self.expert_library.get_expert_by_id(expert_id)
            if expert:
                expert_with_score = expert.copy()
                expert_with_score["_semantic_score"] = similarity
                candidates.append(expert_with_score)

        return candidates

    def _get_rule_based_candidates(
        self,
        context: RecommendationContext,
    ) -> list[dict[str, Any]]:
        """基于规则获取候选者"""
        candidates = []
        all_experts = self.expert_library.get_all_experts()

        for expert in all_experts:
            if expert["id"] in context.current_participants:
                continue

            # 计算规则匹配分数
            rule_score = self._calculate_rule_score(expert, context)
            if rule_score > 0.3:  # 最低阈值
                expert_with_score = expert.copy()
                expert_with_score["_rule_score"] = rule_score
                candidates.append(expert_with_score)

        return candidates

    def _calculate_rule_score(
        self,
        expert: dict[str, Any],
        context: RecommendationContext,
    ) -> float:
        """计算规则匹配分数"""
        score = 0.0

        # 领域匹配
        expert_category = expert.get("category", "").lower()
        if (
            context.domain.lower() in expert_category
            or expert_category in context.domain.lower()
        ):
            score += 0.4

        # 专业领域匹配
        expert_specialties = [s.lower() for s in expert.get("specialties", [])]
        for expertise in context.desired_expertise:
            expertise_lower = expertise.lower()
            if any(expertise_lower in spec for spec in expert_specialties):
                score += 0.3
                break

        # 技能匹配
        expert_skills = [s.lower() for s in expert.get("skills", [])]
        skill_matches = 0
        for expertise in context.desired_expertise:
            expertise_lower = expertise.lower()
            if any(expertise_lower in skill for skill in expert_skills):
                skill_matches += 1

        if skill_matches > 0:
            score += min(skill_matches * 0.2, 0.4)

        # 主题相关性
        topic_words = context.topic.lower().split()
        expert_text = (
            expert.get("description", "") + " " + expert.get("bio", "")
        ).lower()
        topic_matches = sum(1 for word in topic_words if word in expert_text)
        if topic_words:
            score += (topic_matches / len(topic_words)) * 0.3

        return min(score, 1.0)

    def _merge_candidates(
        self,
        semantic_candidates: list[dict[str, Any]],
        rule_based_candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """合并候选者"""
        merged = {}

        # 添加语义候选者
        for candidate in semantic_candidates:
            expert_id = candidate["id"]
            merged[expert_id] = candidate

        # 添加规则候选者
        for candidate in rule_based_candidates:
            expert_id = candidate["id"]
            if expert_id in merged:
                # 合并分数
                merged[expert_id]["_rule_score"] = candidate.get("_rule_score", 0.0)
            else:
                merged[expert_id] = candidate

        return list(merged.values())

    def _score_candidates(
        self,
        candidates: list[dict[str, Any]],
        context: RecommendationContext,
    ) -> list[tuple[dict[str, Any], float]]:
        """综合评分"""
        scored_candidates = []

        for candidate in candidates:
            total_score = 0.0

            # 语义相似度分数 (40%)
            semantic_score = candidate.get("_semantic_score", 0.0)
            total_score += semantic_score * 0.4

            # 规则匹配分数 (35%)
            rule_score = candidate.get("_rule_score", 0.0)
            total_score += rule_score * 0.35

            # 声誉分数 (15%)
            reputation_score = candidate.get("reputation_score", 80) / 100.0
            total_score += reputation_score * 0.15

            # 经验分数 (10%)
            experience_score = min(candidate.get("experience_years", 0) / 10.0, 1.0)
            total_score += experience_score * 0.1

            scored_candidates.append((candidate, total_score))

        # 按分数排序
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates

    def _optimize_diversity(
        self,
        scored_candidates: list[tuple[dict[str, Any], float]],
        context: RecommendationContext,
    ) -> list[dict[str, Any]]:
        """优化多样性"""
        if not scored_candidates:
            return []

        selected = []
        remaining = scored_candidates.copy()

        # 选择得分最高的
        selected.append(remaining.pop(0)[0])

        while len(selected) < context.max_recommendations and remaining:
            best_candidate = None
            best_combined_score = -1
            best_index = -1

            for i, (candidate, base_score) in enumerate(remaining):
                # 计算多样性奖励
                diversity_bonus = self._calculate_diversity_bonus(candidate, selected)

                # 综合分数
                combined_score = base_score + diversity_bonus * 0.3

                if combined_score > best_combined_score:
                    best_combined_score = combined_score
                    best_candidate = candidate
                    best_index = i

            if best_candidate:
                selected.append(best_candidate)
                remaining.pop(best_index)

        return selected

    def _calculate_diversity_bonus(
        self,
        candidate: dict[str, Any],
        selected: list[dict[str, Any]],
    ) -> float:
        """计算多样性奖励"""
        if not selected:
            return 0.0

        candidate_category = candidate.get("category", "")
        candidate_specialties = set(candidate.get("specialties", []))

        diversity_score = 0.0

        for selected_expert in selected:
            selected_category = selected_expert.get("category", "")
            selected_specialties = set(selected_expert.get("specialties", []))

            # 分类多样性
            if candidate_category != selected_category:
                diversity_score += 0.5

            # 专业领域多样性
            if candidate_specialties and selected_specialties:
                overlap = len(candidate_specialties & selected_specialties)
                total = len(candidate_specialties | selected_specialties)
                if total > 0:
                    diversity_score += (1.0 - overlap / total) * 0.5

        return diversity_score / len(selected)

    def update_expert_vector(self, expert_id: str, expert_data: dict[str, Any]):
        """更新专家向量"""
        self.vector_store.add_expert_vector(expert_id, expert_data)
        self.vector_store.save_cache()

    def get_recommendation_explanation(
        self,
        expert_id: str,
        context: RecommendationContext,
    ) -> dict[str, Any]:
        """获取推荐解释"""
        expert = self.expert_library.get_expert_by_id(expert_id)
        if not expert:
            return {}

        explanation = {
            "expert_name": expert.get("name", ""),
            "reasons": [],
            "scores": {},
        }

        # 语义相似度解释
        query_text = f"{context.topic} {' '.join(context.desired_expertise)}"
        similar_experts = self.vector_store.find_similar_experts(query_text, top_k=1)
        if similar_experts and similar_experts[0][0] == expert_id:
            explanation["reasons"].append(f"与主题'{context.topic}'语义相似度高")
            explanation["scores"]["semantic_similarity"] = similar_experts[0][1]

        # 规则匹配解释
        rule_score = self._calculate_rule_score(expert, context)
        if rule_score > 0.5:
            explanation["reasons"].append("专业领域高度匹配")
        explanation["scores"]["rule_match"] = rule_score

        return explanation

    def calculate_relevance_score(self, expert: dict[str, Any], topic: str) -> float:
        """计算专家与主题的相关性分数"""
        try:
            # 收集专家的所有文本信息
            expert_text = []
            expert_text.append(expert.get("name", ""))
            expert_text.append(expert.get("title", ""))
            expert_text.append(expert.get("description", ""))
            expert_text.append(expert.get("bio", ""))
            expert_text.extend(expert.get("specialties", []))
            expert_text.extend(expert.get("skills", []))
            expert_text.extend(expert.get("education", []))

            # 合并文本
            expert_combined = " ".join([text for text in expert_text if text])

            if not expert_combined.strip():
                return 0.0

            # 只用Ollama向量相似度
            expert_embedding = self.vector_store.encode_text(expert_combined)
            topic_embedding = self.vector_store.encode_text(topic)
            if expert_embedding is not None and topic_embedding is not None:
                similarity = np.dot(expert_embedding, topic_embedding) / (
                    np.linalg.norm(expert_embedding) * np.linalg.norm(topic_embedding)
                )
                return max(0.0, min(1.0, similarity))
            # 回退到关键词匹配
            return self._calculate_keyword_similarity(expert_combined, topic)
        except Exception as e:
            self.logger.error(f"计算相关性分数失败: {e}")
            return 0.0

    def _calculate_keyword_similarity(self, expert_text: str, topic: str) -> float:
        """基于关键词匹配计算相似度"""
        expert_words = set(expert_text.lower().split())
        topic_words = set(topic.lower().split())

        if not expert_words or not topic_words:
            return 0.0

        # 计算交集比例
        intersection = expert_words.intersection(topic_words)
        union = expert_words.union(topic_words)

        if not union:
            return 0.0

        # Jaccard相似度
        jaccard_similarity = len(intersection) / len(union)

        # 考虑专家文本长度的权重
        length_factor = min(1.0, len(expert_words) / 50)  # 50个词作为基准

        return jaccard_similarity * length_factor
