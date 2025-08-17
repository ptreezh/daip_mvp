#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人知识图谱

管理用户的个人知识网络和关系
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class PersonalKnowledgeGraph:
    """个人知识图谱"""
    
    def __init__(self, user_id: str = "default_user"):
        """初始化个人知识图谱"""
        self.user_id = user_id
        self.knowledge_nodes = {}  # {node_id: node_data}
        self.relationships = []  # [{source, target, type, strength}]
        self.user_profile = {
            "user_id": user_id,
            "creation_time": datetime.now().isoformat(),
            "total_nodes": 0,
            "total_relationships": 0,
            "knowledge_domains": set()
        }
        
        # 节点类型定义
        self.node_types = {
            "concept": "概念",
            "domain": "领域",
            "technology": "技术",
            "principle": "原则",
            "concern": "关注点",
            "method": "方法",
            "tool": "工具"
        }
    
    def add_knowledge_node(
        self,
        concept: str,
        node_type: str = "concept",
        importance: float = 0.5,
        metadata: Dict[str, Any] = None
    ) -> str:
        """添加知识节点"""
        try:
            node_id = str(uuid.uuid4())
            
            node_data = {
                "node_id": node_id,
                "concept": concept,
                "node_type": node_type,
                "importance": importance,
                "creation_time": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0,
                "metadata": metadata or {},
                "connected_nodes": []
            }
            
            self.knowledge_nodes[node_id] = node_data
            
            # 更新用户档案
            self.user_profile["total_nodes"] += 1
            self.user_profile["knowledge_domains"].add(node_type)
            
            logger.info(f"添加知识节点: {concept} ({node_type})")
            return node_id
            
        except Exception as e:
            logger.error(f"添加知识节点失败: {e}")
            return None
    
    def create_relationship(
        self,
        source_concept: str,
        target_concept: str,
        relation_type: str = "related_to",
        strength: float = 0.5
    ) -> bool:
        """创建关系"""
        try:
            # 查找节点ID
            source_id = self._find_node_by_concept(source_concept)
            target_id = self._find_node_by_concept(target_concept)
            
            if not source_id or not target_id:
                logger.warning(f"无法找到节点: {source_concept} 或 {target_concept}")
                return False
            
            relationship = {
                "relationship_id": str(uuid.uuid4()),
                "source_id": source_id,
                "target_id": target_id,
                "source_concept": source_concept,
                "target_concept": target_concept,
                "relation_type": relation_type,
                "strength": strength,
                "creation_time": datetime.now().isoformat()
            }
            
            self.relationships.append(relationship)
            
            # 更新节点的连接信息
            self.knowledge_nodes[source_id]["connected_nodes"].append(target_id)
            self.knowledge_nodes[target_id]["connected_nodes"].append(source_id)
            
            # 更新用户档案
            self.user_profile["total_relationships"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"创建关系失败: {e}")
            return False
    
    def query_knowledge(
        self,
        query: str,
        query_type: str = "concept_search",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """查询知识"""
        try:
            results = []
            
            if query_type == "concept_search":
                # 概念搜索
                for node_id, node_data in self.knowledge_nodes.items():
                    if query.lower() in node_data["concept"].lower():
                        # 更新访问信息
                        node_data["last_accessed"] = datetime.now().isoformat()
                        node_data["access_count"] += 1
                        
                        result = {
                            "node_id": node_id,
                            "concept": node_data["concept"],
                            "node_type": node_data["node_type"],
                            "importance": node_data["importance"],
                            "relevance_score": self._calculate_relevance(query, node_data)
                        }
                        results.append(result)
            
            elif query_type == "related_concepts":
                # 相关概念搜索
                base_node_id = self._find_node_by_concept(query)
                if base_node_id:
                    related_nodes = self._get_related_nodes(base_node_id)
                    for related_id in related_nodes:
                        if related_id in self.knowledge_nodes:
                            node_data = self.knowledge_nodes[related_id]
                            result = {
                                "node_id": related_id,
                                "concept": node_data["concept"],
                                "node_type": node_data["node_type"],
                                "importance": node_data["importance"],
                                "relation_strength": self._get_relation_strength(base_node_id, related_id)
                            }
                            results.append(result)
            
            # 按相关性排序并限制结果数量
            if query_type == "concept_search":
                results.sort(key=lambda x: x["relevance_score"], reverse=True)
            elif query_type == "related_concepts":
                results.sort(key=lambda x: x["relation_strength"], reverse=True)
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"查询知识失败: {e}")
            return []
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """获取知识摘要"""
        try:
            # 计算统计信息
            node_type_counts = {}
            importance_distribution = []
            
            for node_data in self.knowledge_nodes.values():
                node_type = node_data["node_type"]
                node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
                importance_distribution.append(node_data["importance"])
            
            # 找出最重要的概念
            top_concepts = sorted(
                self.knowledge_nodes.values(),
                key=lambda x: x["importance"],
                reverse=True
            )[:5]
            
            # 找出最活跃的概念（访问次数最多）
            most_accessed = sorted(
                self.knowledge_nodes.values(),
                key=lambda x: x["access_count"],
                reverse=True
            )[:5]
            
            summary = {
                "user_id": self.user_id,
                "total_nodes": len(self.knowledge_nodes),
                "total_relationships": len(self.relationships),
                "knowledge_domains": list(self.user_profile["knowledge_domains"]),
                "node_type_distribution": node_type_counts,
                "average_importance": sum(importance_distribution) / len(importance_distribution) if importance_distribution else 0.0,
                "top_concepts": [{
                    "concept": node["concept"],
                    "importance": node["importance"],
                    "node_type": node["node_type"]
                } for node in top_concepts],
                "most_accessed_concepts": [{
                    "concept": node["concept"],
                    "access_count": node["access_count"],
                    "last_accessed": node["last_accessed"]
                } for node in most_accessed],
                "graph_density": self._calculate_graph_density()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取知识摘要失败: {e}")
            return {"error": str(e)}
    
    def _find_node_by_concept(self, concept: str) -> Optional[str]:
        """根据概念查找节点ID"""
        for node_id, node_data in self.knowledge_nodes.items():
            if node_data["concept"] == concept:
                return node_id
        return None
    
    def _get_related_nodes(self, node_id: str) -> List[str]:
        """获取相关节点"""
        related_nodes = []
        
        for relationship in self.relationships:
            if relationship["source_id"] == node_id:
                related_nodes.append(relationship["target_id"])
            elif relationship["target_id"] == node_id:
                related_nodes.append(relationship["source_id"])
        
        return related_nodes
    
    def _get_relation_strength(self, source_id: str, target_id: str) -> float:
        """获取关系强度"""
        for relationship in self.relationships:
            if ((relationship["source_id"] == source_id and relationship["target_id"] == target_id) or
                (relationship["source_id"] == target_id and relationship["target_id"] == source_id)):
                return relationship["strength"]
        return 0.0
    
    def _calculate_relevance(self, query: str, node_data: Dict[str, Any]) -> float:
        """计算相关性分数"""
        try:
            concept = node_data["concept"].lower()
            query_lower = query.lower()
            
            # 简单的相关性计算
            if query_lower == concept:
                return 1.0
            elif query_lower in concept:
                return 0.8
            elif any(word in concept for word in query_lower.split()):
                return 0.6
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"计算相关性失败: {e}")
            return 0.0
    
    def _calculate_graph_density(self) -> float:
        """计算图密度"""
        try:
            num_nodes = len(self.knowledge_nodes)
            num_edges = len(self.relationships)
            
            if num_nodes <= 1:
                return 0.0
            
            max_possible_edges = num_nodes * (num_nodes - 1) / 2
            density = num_edges / max_possible_edges if max_possible_edges > 0 else 0.0
            
            return density
            
        except Exception as e:
            logger.error(f"计算图密度失败: {e}")
            return 0.0