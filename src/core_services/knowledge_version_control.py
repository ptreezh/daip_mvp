#!/usr/bin/env python3
"""知识版本控制

管理知识条目的版本历史和变更追踪
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class KnowledgeVersionControl:
    """知识版本控制系统"""
    
    def __init__(self):
        """初始化知识版本控制系统"""
        self.versions = {}  # {entity_id: [version_data]}
        self.change_log = []
        self.current_versions = {}  # {entity_id: current_version_id}
    
    def create_version(
        self,
        content: dict[str, Any],
        change_description: str = "",
        entity_id: str = None
    ) -> str:
        """创建新版本"""
        try:
            if entity_id is None:
                entity_id = self._generate_entity_id(content)
            
            version_id = str(uuid.uuid4())
            
            version_data = {
                "version_id": version_id,
                "entity_id": entity_id,
                "content": content.copy(),
                "change_description": change_description,
                "timestamp": datetime.now().isoformat(),
                "content_hash": self._calculate_content_hash(content),
                "version_number": self._get_next_version_number(entity_id),
                "author": content.get("author", "system"),
                "parent_version": self.current_versions.get(entity_id)
            }
            
            # 添加到版本历史
            if entity_id not in self.versions:
                self.versions[entity_id] = []
            
            self.versions[entity_id].append(version_data)
            self.current_versions[entity_id] = version_id
            
            # 记录变更日志
            change_entry = {
                "change_id": str(uuid.uuid4()),
                "entity_id": entity_id,
                "version_id": version_id,
                "change_type": "version_created",
                "description": change_description,
                "timestamp": datetime.now().isoformat(),
                "author": version_data["author"]
            }
            
            self.change_log.append(change_entry)
            
            logger.info(f"创建版本: {version_id} for entity: {entity_id}")
            return version_id
            
        except Exception as e:
            logger.error(f"创建版本失败: {e}")
            return None
    
    def compare_versions(
        self,
        entity_id: str,
        version1_id: str,
        version2_id: str
    ) -> dict[str, Any]:
        """比较两个版本"""
        try:
            if entity_id not in self.versions:
                return {"error": f"实体不存在: {entity_id}"}
            
            version1 = self._find_version(entity_id, version1_id)
            version2 = self._find_version(entity_id, version2_id)
            
            if not version1 or not version2:
                return {"error": "版本不存在"}
            
            comparison = {
                "entity_id": entity_id,
                "version1": {
                    "version_id": version1_id,
                    "timestamp": version1["timestamp"],
                    "version_number": version1["version_number"]
                },
                "version2": {
                    "version_id": version2_id,
                    "timestamp": version2["timestamp"],
                    "version_number": version2["version_number"]
                },
                "differences": self._calculate_differences(version1["content"], version2["content"]),
                "similarity_score": self._calculate_similarity(version1["content"], version2["content"])
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"比较版本失败: {e}")
            return {"error": str(e)}
    
    def rollback_version(
        self,
        entity_id: str,
        target_version_id: str,
        rollback_reason: str = ""
    ) -> bool:
        """回滚到指定版本"""
        try:
            if entity_id not in self.versions:
                logger.error(f"实体不存在: {entity_id}")
                return False
            
            target_version = self._find_version(entity_id, target_version_id)
            if not target_version:
                logger.error(f"目标版本不存在: {target_version_id}")
                return False
            
            # 创建回滚版本（基于目标版本的内容）
            rollback_content = target_version["content"].copy()
            rollback_content["rollback_info"] = {
                "rollback_from": self.current_versions.get(entity_id),
                "rollback_to": target_version_id,
                "rollback_reason": rollback_reason,
                "rollback_timestamp": datetime.now().isoformat()
            }
            
            rollback_version_id = self.create_version(
                content=rollback_content,
                change_description=f"回滚到版本 {target_version['version_number']}: {rollback_reason}",
                entity_id=entity_id
            )
            
            if rollback_version_id:
                # 记录回滚操作
                rollback_entry = {
                    "change_id": str(uuid.uuid4()),
                    "entity_id": entity_id,
                    "change_type": "rollback",
                    "from_version": self.current_versions.get(entity_id),
                    "to_version": target_version_id,
                    "new_version": rollback_version_id,
                    "reason": rollback_reason,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.change_log.append(rollback_entry)
                
                logger.info(f"成功回滚实体 {entity_id} 到版本 {target_version_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"回滚版本失败: {e}")
            return False
    
    def get_version_history(self, entity_id: str) -> list[dict[str, Any]]:
        """获取版本历史"""
        try:
            if entity_id not in self.versions:
                return []
            
            # 返回版本历史的摘要信息
            history = []
            for version in self.versions[entity_id]:
                history_entry = {
                    "version_id": version["version_id"],
                    "version_number": version["version_number"],
                    "timestamp": version["timestamp"],
                    "author": version["author"],
                    "change_description": version["change_description"],
                    "content_hash": version["content_hash"],
                    "is_current": version["version_id"] == self.current_versions.get(entity_id)
                }
                history.append(history_entry)
            
            # 按版本号排序
            history.sort(key=lambda x: x["version_number"])
            return history
            
        except Exception as e:
            logger.error(f"获取版本历史失败: {e}")
            return []
    
    def get_current_version(self, entity_id: str) -> Optional[dict[str, Any]]:
        """获取当前版本"""
        try:
            if entity_id not in self.current_versions:
                return None
            
            current_version_id = self.current_versions[entity_id]
            return self._find_version(entity_id, current_version_id)
            
        except Exception as e:
            logger.error(f"获取当前版本失败: {e}")
            return None
    
    def _generate_entity_id(self, content: dict[str, Any]) -> str:
        """生成实体ID"""
        # 基于内容标题或关键信息生成ID
        title = content.get("title", "")
        if title:
            # 使用标题生成ID
            entity_id = title.lower().replace(" ", "_").replace("-", "_")
            # 移除特殊字符
            entity_id = "".join(c for c in entity_id if c.isalnum() or c == "_")
            return entity_id[:50]  # 限制长度
        else:
            # 使用UUID作为后备
            return str(uuid.uuid4())
    
    def _calculate_content_hash(self, content: dict[str, Any]) -> str:
        """计算内容哈希"""
        try:
            # 创建内容的标准化JSON表示
            content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
            return hashlib.md5(content_str.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"计算内容哈希失败: {e}")
            return ""
    
    def _get_next_version_number(self, entity_id: str) -> int:
        """获取下一个版本号"""
        if entity_id not in self.versions or not self.versions[entity_id]:
            return 1
        
        max_version = max(version["version_number"] for version in self.versions[entity_id])
        return max_version + 1
    
    def _find_version(self, entity_id: str, version_id: str) -> Optional[dict[str, Any]]:
        """查找指定版本"""
        if entity_id not in self.versions:
            return None
        
        for version in self.versions[entity_id]:
            if version["version_id"] == version_id:
                return version
        
        return None
    
    def _calculate_differences(self, content1: dict[str, Any], content2: dict[str, Any]) -> list[dict[str, Any]]:
        """计算内容差异"""
        differences = []
        
        # 比较所有键
        all_keys = set(content1.keys()) | set(content2.keys())
        
        for key in all_keys:
            if key not in content1:
                differences.append({
                    "type": "added",
                    "field": key,
                    "new_value": content2[key]
                })
            elif key not in content2:
                differences.append({
                    "type": "removed",
                    "field": key,
                    "old_value": content1[key]
                })
            elif content1[key] != content2[key]:
                differences.append({
                    "type": "modified",
                    "field": key,
                    "old_value": content1[key],
                    "new_value": content2[key]
                })
        
        return differences
    
    def _calculate_similarity(self, content1: dict[str, Any], content2: dict[str, Any]) -> float:
        """计算内容相似度"""
        try:
            # 简单的相似度计算
            all_keys = set(content1.keys()) | set(content2.keys())
            if not all_keys:
                return 1.0
            
            same_keys = 0
            for key in all_keys:
                if key in content1 and key in content2 and content1[key] == content2[key]:
                    same_keys += 1
            
            return same_keys / len(all_keys)
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    def get_change_statistics(self) -> dict[str, Any]:
        """获取变更统计"""
        try:
            stats = {
                "total_entities": len(self.versions),
                "total_versions": sum(len(versions) for versions in self.versions.values()),
                "total_changes": len(self.change_log),
                "change_types": {},
                "active_authors": set(),
                "recent_changes": []
            }
            
            # 统计变更类型
            for change in self.change_log:
                change_type = change.get("change_type", "unknown")
                stats["change_types"][change_type] = stats["change_types"].get(change_type, 0) + 1
                
                # 收集活跃作者
                author = change.get("author", "unknown")
                stats["active_authors"].add(author)
            
            # 转换为列表
            stats["active_authors"] = list(stats["active_authors"])
            
            # 获取最近的变更
            stats["recent_changes"] = self.change_log[-10:] if len(self.change_log) >= 10 else self.change_log
            
            return stats
            
        except Exception as e:
            logger.error(f"获取变更统计失败: {e}")
            return {"error": str(e)}
    
    def export_version_data(self, entity_id: str, version_id: str = None) -> dict[str, Any]:
        """导出版本数据"""
        try:
            if entity_id not in self.versions:
                return {"error": f"实体不存在: {entity_id}"}
            
            if version_id is None:
                version_id = self.current_versions.get(entity_id)
            
            version = self._find_version(entity_id, version_id)
            if not version:
                return {"error": f"版本不存在: {version_id}"}
            
            export_data = {
                "entity_id": entity_id,
                "version_data": version,
                "version_history": self.get_version_history(entity_id),
                "export_timestamp": datetime.now().isoformat()
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"导出版本数据失败: {e}")
            return {"error": str(e)}