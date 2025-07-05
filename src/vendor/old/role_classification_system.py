"""角色分类和索引系统
建立多维度的角色分类体系，支持高效的角色检索和管理
"""

import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class RoleCategory:
    """角色分类"""

    id: str
    name: str
    parent_id: Optional[str]
    description: str
    keywords: list[str]
    subcategories: list[str]
    role_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoleTag:
    """角色标签"""

    id: str
    name: str
    category: str
    description: str
    usage_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SearchIndex:
    """搜索索引"""

    term: str
    role_ids: list[str]
    weight: float
    category: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RoleClassificationSystem:
    """角色分类系统"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # 分类体系
        self.categories: dict[str, RoleCategory] = {}
        self.category_hierarchy: dict[str, list[str]] = {}  # parent_id -> [child_ids]

        # 标签系统
        self.tags: dict[str, RoleTag] = {}
        self.role_tags: dict[str, list[str]] = {}  # role_id -> [tag_ids]

        # 搜索索引
        self.search_index: dict[str, SearchIndex] = {}
        self.inverted_index: dict[str, list[str]] = {}  # term -> [role_ids]

        # 角色分类映射
        self.role_categories: dict[str, str] = {}  # role_id -> category_id

        self.logger = logging.getLogger(__name__)

        # 初始化系统
        self._initialize_system()

    def _initialize_system(self):
        """初始化分类系统"""
        # 加载现有数据
        self._load_categories()
        self._load_tags()
        self._load_search_index()

        # 如果没有数据，创建默认分类体系
        if not self.categories:
            self._create_default_categories()

        if not self.tags:
            self._create_default_tags()

    def _create_default_categories(self):
        """创建默认分类体系"""
        default_categories = [
            # 一级分类
            {
                "id": "tech",
                "name": "技术专家",
                "parent_id": None,
                "description": "技术开发、工程、数据等技术领域专家",
                "keywords": ["技术", "开发", "工程", "编程", "数据", "算法", "系统"],
            },
            {
                "id": "business",
                "name": "商业专家",
                "parent_id": None,
                "description": "商业管理、市场营销、财务等商业领域专家",
                "keywords": ["商业", "管理", "营销", "财务", "战略", "运营"],
            },
            {
                "id": "academic",
                "name": "学术专家",
                "parent_id": None,
                "description": "学术研究、教育、理论等学术领域专家",
                "keywords": ["学术", "研究", "教育", "理论", "论文", "教学"],
            },
            {
                "id": "creative",
                "name": "创意专家",
                "parent_id": None,
                "description": "设计、艺术、创作等创意领域专家",
                "keywords": ["创意", "设计", "艺术", "创作", "美术", "文案"],
            },
            {
                "id": "consulting",
                "name": "咨询专家",
                "parent_id": None,
                "description": "咨询、顾问、专业服务等领域专家",
                "keywords": ["咨询", "顾问", "服务", "建议", "指导"],
            },
            # 技术子分类
            {
                "id": "tech_dev",
                "name": "软件开发",
                "parent_id": "tech",
                "description": "软件开发、编程、架构等",
                "keywords": ["开发", "编程", "代码", "软件", "架构", "框架"],
            },
            {
                "id": "tech_data",
                "name": "数据科学",
                "parent_id": "tech",
                "description": "数据分析、机器学习、人工智能等",
                "keywords": ["数据", "分析", "机器学习", "AI", "算法", "统计"],
            },
            {
                "id": "tech_infra",
                "name": "基础设施",
                "parent_id": "tech",
                "description": "系统运维、网络、安全等",
                "keywords": ["运维", "网络", "安全", "服务器", "云计算"],
            },
            # 商业子分类
            {
                "id": "business_mgmt",
                "name": "管理",
                "parent_id": "business",
                "description": "项目管理、团队管理、运营管理等",
                "keywords": ["管理", "项目", "团队", "运营", "流程"],
            },
            {
                "id": "business_marketing",
                "name": "市场营销",
                "parent_id": "business",
                "description": "市场营销、品牌、销售等",
                "keywords": ["营销", "市场", "品牌", "销售", "推广"],
            },
            {
                "id": "business_finance",
                "name": "财务",
                "parent_id": "business",
                "description": "财务管理、投资、会计等",
                "keywords": ["财务", "投资", "会计", "金融", "预算"],
            },
            # 学术子分类
            {
                "id": "academic_research",
                "name": "科学研究",
                "parent_id": "academic",
                "description": "科学研究、实验、理论等",
                "keywords": ["研究", "实验", "理论", "科学", "方法"],
            },
            {
                "id": "academic_education",
                "name": "教育",
                "parent_id": "academic",
                "description": "教学、培训、教育等",
                "keywords": ["教育", "教学", "培训", "课程", "学习"],
            },
        ]

        for cat_data in default_categories:
            category = RoleCategory(**cat_data, subcategories=[])
            self.categories[category.id] = category

            # 构建层次结构
            if category.parent_id:
                if category.parent_id not in self.category_hierarchy:
                    self.category_hierarchy[category.parent_id] = []
                self.category_hierarchy[category.parent_id].append(category.id)

                # 更新父分类的子分类列表
                if category.parent_id in self.categories:
                    self.categories[category.parent_id].subcategories.append(
                        category.id,
                    )

        self._save_categories()
        self.logger.info(f"创建了 {len(self.categories)} 个默认分类")

    def _create_default_tags(self):
        """创建默认标签"""
        default_tags = [
            # 技能标签
            {
                "id": "python",
                "name": "Python",
                "category": "技能",
                "description": "Python编程语言",
            },
            {"id": "java", "name": "Java", "category": "技能", "description": "Java编程语言"},
            {
                "id": "javascript",
                "name": "JavaScript",
                "category": "技能",
                "description": "JavaScript编程语言",
            },
            {
                "id": "machine_learning",
                "name": "机器学习",
                "category": "技能",
                "description": "机器学习技术",
            },
            {
                "id": "data_analysis",
                "name": "数据分析",
                "category": "技能",
                "description": "数据分析能力",
            },
            # 行业标签
            {
                "id": "fintech",
                "name": "金融科技",
                "category": "行业",
                "description": "金融科技行业",
            },
            {
                "id": "healthcare",
                "name": "医疗健康",
                "category": "行业",
                "description": "医疗健康行业",
            },
            {"id": "education", "name": "教育", "category": "行业", "description": "教育行业"},
            {
                "id": "ecommerce",
                "name": "电商",
                "category": "行业",
                "description": "电子商务行业",
            },
            # 经验标签
            {"id": "senior", "name": "资深", "category": "经验", "description": "资深专家"},
            {"id": "junior", "name": "初级", "category": "经验", "description": "初级专家"},
            {"id": "expert", "name": "专家", "category": "经验", "description": "领域专家"},
            # 特征标签
            {
                "id": "innovative",
                "name": "创新",
                "category": "特征",
                "description": "具有创新能力",
            },
            {
                "id": "analytical",
                "name": "分析",
                "category": "特征",
                "description": "具有分析能力",
            },
            {
                "id": "leadership",
                "name": "领导",
                "category": "特征",
                "description": "具有领导能力",
            },
            {
                "id": "communication",
                "name": "沟通",
                "category": "特征",
                "description": "具有沟通能力",
            },
        ]

        for tag_data in default_tags:
            tag = RoleTag(**tag_data)
            self.tags[tag.id] = tag

        self._save_tags()
        self.logger.info(f"创建了 {len(self.tags)} 个默认标签")

    def classify_role(self, role_data: dict[str, Any]) -> tuple[str, list[str], float]:
        """自动分类角色
        返回: (分类ID, 标签列表, 置信度)
        """
        role_text = self._extract_role_text(role_data)

        # 计算每个分类的匹配分数
        category_scores = {}
        for cat_id, category in self.categories.items():
            score = self._calculate_category_score(role_text, category)
            if score > 0:
                category_scores[cat_id] = score

        # 选择最佳分类
        best_category = None
        best_score = 0.0

        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]

        # 如果没有明确匹配，使用默认分类
        if not best_category or best_score < 0.3:
            best_category = self._get_default_category(role_data)
            best_score = 0.5

        # 自动标签
        auto_tags = self._auto_tag_role(role_text)

        return best_category, auto_tags, best_score

    def _extract_role_text(self, role_data: dict[str, Any]) -> str:
        """提取角色文本"""
        text_parts = []
        text_parts.append(role_data.get("name", ""))
        text_parts.append(role_data.get("title", ""))
        text_parts.append(role_data.get("description", ""))
        text_parts.append(role_data.get("bio", ""))
        text_parts.extend(role_data.get("specialties", []))
        text_parts.extend(role_data.get("skills", []))

        return " ".join([part for part in text_parts if part]).lower()

    def _calculate_category_score(
        self,
        role_text: str,
        category: RoleCategory,
    ) -> float:
        """计算分类匹配分数"""
        score = 0.0
        keyword_matches = 0

        for keyword in category.keywords:
            if keyword.lower() in role_text:
                keyword_matches += 1
                score += 1.0

        # 归一化分数
        if category.keywords:
            score = keyword_matches / len(category.keywords)

        return score

    def _get_default_category(self, role_data: dict[str, Any]) -> str:
        """获取默认分类"""
        # 基于现有分类字段
        existing_category = role_data.get("category", "").lower()

        category_mapping = {
            "tech": "tech",
            "technology": "tech",
            "技术": "tech",
            "business": "business",
            "management": "business",
            "管理": "business",
            "academic": "academic",
            "学术": "academic",
            "creative": "creative",
            "创意": "creative",
            "consulting": "consulting",
            "咨询": "consulting",
        }

        for key, cat_id in category_mapping.items():
            if key in existing_category:
                return cat_id

        return "consulting"  # 默认分类

    def _auto_tag_role(self, role_text: str) -> list[str]:
        """自动标记角色"""
        matched_tags = []

        for tag_id, tag in self.tags.items():
            # 检查标签名称和描述
            if tag.name.lower() in role_text or any(
                keyword.lower() in role_text for keyword in tag.description.split()
            ):
                matched_tags.append(tag_id)

        return matched_tags

    def add_role_to_system(self, role_id: str, role_data: dict[str, Any]):
        """将角色添加到分类系统"""
        # 自动分类
        category_id, auto_tags, confidence = self.classify_role(role_data)

        # 记录分类
        self.role_categories[role_id] = category_id

        # 更新分类计数
        if category_id in self.categories:
            self.categories[category_id].role_count += 1

        # 记录标签
        self.role_tags[role_id] = auto_tags

        # 更新标签使用计数
        for tag_id in auto_tags:
            if tag_id in self.tags:
                self.tags[tag_id].usage_count += 1

        # 构建搜索索引
        self._build_role_search_index(role_id, role_data)

        self.logger.info(f"角色 {role_id} 已分类到 {category_id}，标签: {auto_tags}")

    def _build_role_search_index(self, role_id: str, role_data: dict[str, Any]):
        """构建角色搜索索引"""
        # 提取所有可搜索的文本
        searchable_texts = [
            (role_data.get("name", ""), 1.0),
            (role_data.get("title", ""), 0.9),
            (" ".join(role_data.get("specialties", [])), 0.8),
            (" ".join(role_data.get("skills", [])), 0.7),
            (role_data.get("description", ""), 0.6),
            (role_data.get("bio", ""), 0.5),
        ]

        # 提取关键词并建立索引
        for text, weight in searchable_texts:
            if text:
                words = re.findall(r"\w+", text.lower())
                for word in words:
                    if len(word) > 2:  # 过滤短词
                        if word not in self.inverted_index:
                            self.inverted_index[word] = []
                        if role_id not in self.inverted_index[word]:
                            self.inverted_index[word].append(role_id)

                        # 更新搜索索引
                        index_key = f"{word}_{role_id}"
                        if index_key not in self.search_index:
                            self.search_index[index_key] = SearchIndex(
                                term=word,
                                role_ids=[role_id],
                                weight=weight,
                                category=self.role_categories.get(role_id, ""),
                            )

    def search_roles(
        self,
        query: str,
        category_filter: str = None,
        tag_filter: list[str] = None,
        limit: int = 20,
    ) -> list[str]:
        """搜索角色"""
        query_words = re.findall(r"\w+", query.lower())

        # 收集候选角色
        candidate_scores = defaultdict(float)

        for word in query_words:
            if word in self.inverted_index:
                for role_id in self.inverted_index[word]:
                    # 计算匹配分数
                    index_key = f"{word}_{role_id}"
                    if index_key in self.search_index:
                        weight = self.search_index[index_key].weight
                        candidate_scores[role_id] += weight

        # 应用过滤器
        filtered_candidates = []
        for role_id, score in candidate_scores.items():
            # 分类过滤
            if category_filter and self.role_categories.get(role_id) != category_filter:
                continue

            # 标签过滤
            if tag_filter:
                role_tags = self.role_tags.get(role_id, [])
                if not any(tag in role_tags for tag in tag_filter):
                    continue

            filtered_candidates.append((role_id, score))

        # 排序并返回
        filtered_candidates.sort(key=lambda x: x[1], reverse=True)
        return [role_id for role_id, _ in filtered_candidates[:limit]]

    def get_category_hierarchy(self) -> dict[str, Any]:
        """获取分类层次结构"""

        def build_tree(category_id: str) -> dict[str, Any]:
            category = self.categories[category_id]
            node = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "role_count": category.role_count,
                "children": [],
            }

            if category_id in self.category_hierarchy:
                for child_id in self.category_hierarchy[category_id]:
                    node["children"].append(build_tree(child_id))

            return node

        # 构建根节点树
        root_categories = [
            cat_id for cat_id, cat in self.categories.items() if cat.parent_id is None
        ]
        hierarchy = []

        for root_id in root_categories:
            hierarchy.append(build_tree(root_id))

        return {"categories": hierarchy}

    def get_role_statistics(self) -> dict[str, Any]:
        """获取角色统计信息"""
        stats = {
            "total_roles": len(self.role_categories),
            "total_categories": len(self.categories),
            "total_tags": len(self.tags),
            "category_distribution": {},
            "tag_usage": {},
            "search_index_size": len(self.search_index),
        }

        # 分类分布
        category_counts = Counter(self.role_categories.values())
        for cat_id, count in category_counts.items():
            if cat_id in self.categories:
                stats["category_distribution"][self.categories[cat_id].name] = count

        # 标签使用情况
        for tag_id, tag in self.tags.items():
            if tag.usage_count > 0:
                stats["tag_usage"][tag.name] = tag.usage_count

        return stats

    def _load_categories(self):
        """加载分类数据"""
        categories_file = self.data_dir / "role_categories.json"
        if categories_file.exists():
            try:
                with open(categories_file, encoding="utf-8") as f:
                    data = json.load(f)

                for cat_data in data.get("categories", []):
                    category = RoleCategory(**cat_data)
                    self.categories[category.id] = category

                self.category_hierarchy = data.get("hierarchy", {})
                self.logger.info(f"加载了 {len(self.categories)} 个分类")

            except Exception as e:
                self.logger.error(f"加载分类数据失败: {e}")

    def _save_categories(self):
        """保存分类数据"""
        categories_file = self.data_dir / "role_categories.json"
        try:
            data = {
                "categories": [cat.to_dict() for cat in self.categories.values()],
                "hierarchy": self.category_hierarchy,
                "last_updated": datetime.now().isoformat(),
            }

            with open(categories_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"保存分类数据失败: {e}")

    def _load_tags(self):
        """加载标签数据"""
        tags_file = self.data_dir / "role_tags.json"
        if tags_file.exists():
            try:
                with open(tags_file, encoding="utf-8") as f:
                    data = json.load(f)

                for tag_data in data.get("tags", []):
                    tag = RoleTag(**tag_data)
                    self.tags[tag.id] = tag

                self.role_tags = data.get("role_tags", {})
                self.logger.info(f"加载了 {len(self.tags)} 个标签")

            except Exception as e:
                self.logger.error(f"加载标签数据失败: {e}")

    def _save_tags(self):
        """保存标签数据"""
        tags_file = self.data_dir / "role_tags.json"
        try:
            data = {
                "tags": [tag.to_dict() for tag in self.tags.values()],
                "role_tags": self.role_tags,
                "last_updated": datetime.now().isoformat(),
            }

            with open(tags_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"保存标签数据失败: {e}")

    def _load_search_index(self):
        """加载搜索索引"""
        index_file = self.data_dir / "search_index.json"
        if index_file.exists():
            try:
                with open(index_file, encoding="utf-8") as f:
                    data = json.load(f)

                self.inverted_index = data.get("inverted_index", {})
                self.role_categories = data.get("role_categories", {})

                for index_data in data.get("search_index", []):
                    index = SearchIndex(**index_data)
                    key = f"{index.term}_{index.role_ids[0]}"
                    self.search_index[key] = index

                self.logger.info(f"加载了搜索索引: {len(self.search_index)} 条记录")

            except Exception as e:
                self.logger.error(f"加载搜索索引失败: {e}")

    def save_all_data(self):
        """保存所有数据"""
        self._save_categories()
        self._save_tags()

        # 保存搜索索引
        index_file = self.data_dir / "search_index.json"
        try:
            data = {
                "inverted_index": self.inverted_index,
                "role_categories": self.role_categories,
                "search_index": [
                    index.to_dict() for index in self.search_index.values()
                ],
                "last_updated": datetime.now().isoformat(),
            }

            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"保存搜索索引失败: {e}")

        self.logger.info("所有分类和索引数据已保存")
