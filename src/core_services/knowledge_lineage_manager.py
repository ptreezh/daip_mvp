#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识谱系管理器

管理知识的谱系关系和影响网络
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class KnowledgeLineageManager:
    """知识谱系管理器"""
    
    def __init__(self):
        """初始化知识谱系管理器"""
        self.lineage_graph = {}  # {node_id: node_data}
        self.influence_network = {}  # {node_id: [influenced_nodes]}
        self.relationships = []  # [{parent, child, type, strength}]
    
    def create_lineage_node(
        self,
        knowledge_id: str,
        content: str,
        creator: str,
        creation_time: str
    ) -> str:
        """创建谱系节点"""
        try:
            node_id = str(uuid.uuid4())
            
            node_data = {
                "node_id": node_id,
                "knowledge_id": knowledge_id,
                "content": content,
                "creator": creator,
                "creation_time": creation_time,
                "children": [],
                "parents": [],
                "influence_score": 0.0
            }
            
            self.lineage_graph[node_id] = node_data
            return node_id
            
        except Exception as e:
            logger.error(f"创建谱系节点失败: {e}")
            return None
    
    def establish_relationship(
        self,
        parent_id: str,
        child_id: str,
        relationship_type: str = "evolution",
        relationship_strength: float = 1.0
    ) -> bool:
        """建立关系"""
        try:
            if parent_id not in self.lineage_graph or child_id not in self.lineage_graph:
                return False
            
            relationship = {
                "parent_id": parent_id,
                "child_id": child_id,
                "relationship_type": relationship_type,
                "relationship_strength": relationship_strength,
                "established_time": datetime.now().isoformat()
            }
            
            self.relationships.append(relationship)
            
            # 更新节点关系
            self.lineage_graph[parent_id]["children"].append(child_id)
            self.lineage_graph[child_id]["parents"].append(parent_id)
            
            return True
            
        except Exception as e:
            logger.error(f"建立关系失败: {e}")
            return False
    
    def trace_knowledge_ancestry(self, node_id: str) -> List[Dict[str, Any]]:
        """追踪知识祖先"""
        try:
            if node_id not in self.lineage_graph:
                return []
            
            ancestry = []
            current_node = self.lineage_graph[node_id]
            
            # 递归追踪父节点
            def trace_parents(node):
                for parent_id in node["parents"]:
                    if parent_id in self.lineage_graph:
                        parent_node = self.lineage_graph[parent_id]
                        ancestry.append({
                            "node_id": parent_id,
                            "knowledge_id": parent_node["knowledge_id"],
                            "creator": parent_node["creator"],
                            "creation_time": parent_node["creation_time"]
                        })
                        trace_parents(parent_node)
            
            trace_parents(current_node)
            return ancestry
            
        except Exception as e:
            logger.error(f"追踪知识祖先失败: {e}")
            return []