#!/usr/bin/env python3
"""知识图谱构建器

从文本中提取实体和关系，构建知识图谱
"""

import logging
import re
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self):
        """初始化知识图谱构建器"""
        self.entity_extractor = EntityExtractor()
        self.relation_detector = RelationDetector()

        logger.info("知识图谱构建器初始化完成")
<<<<<<< HEAD

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """提取实体"""
        return self.entity_extractor.extract(text)

    def detect_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测关系"""
        return self.relation_detector.detect(text, entities)

    def build_graph_from_text(self, text: str) -> Dict[str, Any]:
=======
    
    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        """提取实体"""
        return self.entity_extractor.extract(text)
    
    def detect_relations(self, text: str, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """检测关系"""
        return self.relation_detector.detect(text, entities)
    
    def build_graph_from_text(self, text: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """从文本构建图谱"""
        try:
            # 提取实体
            entities = self.extract_entities(text)

            # 检测关系
            relations = self.detect_relations(text, entities)

            # 构建图谱结构
            graph_structure = self._build_graph_structure(entities, relations)

            result = {
                "entities": entities,
                "relations": relations,
                "graph_structure": graph_structure,
                "source_text": text,
                "build_time": datetime.now().isoformat()
            }

            logger.info(f"从文本构建图谱完成: {len(entities)}个实体, {len(relations)}个关系")
            return result

        except Exception as e:
            logger.error(f"从文本构建图谱失败: {e}")
            return {
                "entities": [],
                "relations": [],
                "graph_structure": {"nodes": [], "edges": []},
                "error": str(e)
            }
<<<<<<< HEAD

    def _build_graph_structure(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, Any]:
=======
    
    def _build_graph_structure(self, entities: list[dict[str, Any]], relations: list[dict[str, Any]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """构建图谱结构"""
        try:
            # 创建节点
            nodes = []
            for entity in entities:
                node = {
                    "id": entity["id"],
                    "label": entity["text"],
                    "type": entity["type"],
                    "importance": entity.get("importance", 0.5),
                    "properties": entity.get("properties", {})
                }
                nodes.append(node)

            # 创建边
            edges = []
            for relation in relations:
                edge = {
                    "id": relation["id"],
                    "source": relation["source_entity"],
                    "target": relation["target_entity"],
                    "type": relation["relation_type"],
                    "weight": relation.get("confidence", 0.5),
                    "properties": relation.get("properties", {})
                }
                edges.append(edge)

            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "density": len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0.0
                }
            }

        except Exception as e:
            logger.error(f"构建图谱结构失败: {e}")
            return {"nodes": [], "edges": [], "metadata": {}}


class EntityExtractor:
    """实体提取器"""

    def __init__(self):
        """初始化实体提取器"""
        # 定义实体类型和对应的关键词模式
        self.entity_patterns = {
            "concept": [
                r"AI伦理", r"人工智能", r"机器学习", r"深度学习", r"算法",
                r"透明度", r"公平性", r"可解释性", r"隐私保护", r"数据安全"
            ],
            "technology": [
                r"神经网络", r"自然语言处理", r"计算机视觉", r"强化学习",
                r"区块链", r"云计算", r"大数据", r"物联网"
            ],
            "principle": [
                r"伦理原则", r"道德准则", r"法律法规", r"行业标准",
                r"最佳实践", r"指导方针"
            ],
            "domain": [
                r"医疗健康", r"金融服务", r"教育培训", r"交通运输",
                r"智能制造", r"智慧城市", r"电子商务"
            ]
        }
<<<<<<< HEAD

    def extract(self, text: str) -> List[Dict[str, Any]]:
=======
    
    def extract(self, text: str) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """提取实体"""
        try:
            entities = []
            entity_id = 0

            for entity_type, patterns in self.entity_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        entity = {
                            "id": f"entity_{entity_id}",
                            "text": match.group(),
                            "type": entity_type,
                            "start": match.start(),
                            "end": match.end(),
                            "importance": self._calculate_importance(match.group(), entity_type),
                            "properties": {
                                "context": text[max(0, match.start()-50):match.end()+50]
                            }
                        }
                        entities.append(entity)
                        entity_id += 1

            # 去重
            entities = self._deduplicate_entities(entities)

            logger.info(f"提取实体完成: {len(entities)}个实体")
            return entities

        except Exception as e:
            logger.error(f"提取实体失败: {e}")
            return []

    def _calculate_importance(self, entity_text: str, entity_type: str) -> float:
        """计算实体重要性"""
        # 简单的重要性计算逻辑
        base_importance = {
            "concept": 0.8,
            "technology": 0.7,
            "principle": 0.9,
            "domain": 0.6
        }.get(entity_type, 0.5)

        # 根据实体长度调整重要性
        length_factor = min(len(entity_text) / 10, 1.0)

        return min(base_importance + length_factor * 0.2, 1.0)
<<<<<<< HEAD

    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
=======
    
    def _deduplicate_entities(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """去重实体"""
        seen = set()
        unique_entities = []

        for entity in entities:
            key = (entity["text"].lower(), entity["type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities


class RelationDetector:
    """关系检测器"""

    def __init__(self):
        """初始化关系检测器"""
        # 定义关系模式
        self.relation_patterns = [
            {
                "pattern": r"(.+?)是(.+?)的(.+)",
                "relation_type": "is_a",
                "confidence": 0.8
            },
            {
                "pattern": r"(.+?)包含(.+)",
                "relation_type": "includes",
                "confidence": 0.7
            },
            {
                "pattern": r"(.+?)影响(.+)",
                "relation_type": "affects",
                "confidence": 0.6
            },
            {
                "pattern": r"(.+?)和(.+?)相关",
                "relation_type": "related_to",
                "confidence": 0.5
            },
            {
                "pattern": r"(.+?)基于(.+)",
                "relation_type": "based_on",
                "confidence": 0.7
            }
        ]
<<<<<<< HEAD

    def detect(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
=======
    
    def detect(self, text: str, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """检测关系"""
        try:
            relations = []
            relation_id = 0

            # 创建实体文本到ID的映射
            entity_map = {entity["text"]: entity["id"] for entity in entities}

            # 使用模式匹配检测关系
            for pattern_info in self.relation_patterns:
                pattern = pattern_info["pattern"]
                relation_type = pattern_info["relation_type"]
                confidence = pattern_info["confidence"]

                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 2:
                        source_text = groups[0].strip()
                        target_text = groups[1].strip()

                        # 查找对应的实体
                        source_entity = self._find_matching_entity(source_text, entity_map)
                        target_entity = self._find_matching_entity(target_text, entity_map)

                        if source_entity and target_entity and source_entity != target_entity:
                            relation = {
                                "id": f"relation_{relation_id}",
                                "source_entity": source_entity,
                                "target_entity": target_entity,
                                "relation_type": relation_type,
                                "confidence": confidence,
                                "context": match.group(),
                                "properties": {
                                    "pattern_matched": pattern,
                                    "full_context": text[max(0, match.start()-100):match.end()+100]
                                }
                            }
                            relations.append(relation)
                            relation_id += 1

            # 基于实体共现检测隐式关系
            cooccurrence_relations = self._detect_cooccurrence_relations(text, entities)
            relations.extend(cooccurrence_relations)

            logger.info(f"检测关系完成: {len(relations)}个关系")
            return relations

        except Exception as e:
            logger.error(f"检测关系失败: {e}")
            return []
<<<<<<< HEAD

    def _find_matching_entity(self, text: str, entity_map: Dict[str, str]) -> str:
=======
    
    def _find_matching_entity(self, text: str, entity_map: dict[str, str]) -> str:
>>>>>>> feature/core-services-refactor
        """查找匹配的实体"""
        # 精确匹配
        if text in entity_map:
            return entity_map[text]

        # 模糊匹配
        for entity_text, entity_id in entity_map.items():
            if text.lower() in entity_text.lower() or entity_text.lower() in text.lower():
                return entity_id

        return None
<<<<<<< HEAD

    def _detect_cooccurrence_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
=======
    
    def _detect_cooccurrence_relations(self, text: str, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """基于共现检测关系"""
        relations = []
        relation_id = len([r for r in relations]) + 1000  # 避免ID冲突

        # 检测在同一句子中出现的实体对
        sentences = re.split(r'[。！？.!?]', text)

        for sentence in sentences:
            sentence_entities = []
            for entity in entities:
                if entity["text"] in sentence:
                    sentence_entities.append(entity)

            # 为同一句子中的实体对创建关系
            for i in range(len(sentence_entities)):
                for j in range(i + 1, len(sentence_entities)):
                    entity1 = sentence_entities[i]
                    entity2 = sentence_entities[j]

                    relation = {
                        "id": f"relation_{relation_id}",
                        "source_entity": entity1["id"],
                        "target_entity": entity2["id"],
                        "relation_type": "co_occurs",
                        "confidence": 0.3,
                        "context": sentence,
                        "properties": {
                            "detection_method": "cooccurrence",
                            "sentence_context": sentence
                        }
                    }
                    relations.append(relation)
                    relation_id += 1

        return relations
