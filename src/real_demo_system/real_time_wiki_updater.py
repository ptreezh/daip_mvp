#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时Wiki更新器

基于辩论结果自动更新知识库
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class RealTimeWikiUpdater:
    """实时Wiki更新器"""
    
    def __init__(self):
        """初始化实时Wiki更新器"""
        try:
            from src.core_services.wiki_service import WikiService
            self.wiki_service = WikiService()
        except ImportError:
            logger.warning("WikiService不可用，使用模拟实现")
            self.wiki_service = None
        
        self.update_queue = []
        self.update_history = []
        self.processing = False
    
    def process_debate_result(self, debate_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理辩论结果并更新Wiki"""
        try:
            update_result = {
                "update_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "topic": debate_result.get("topic", "未知主题"),
                "updated_entries": [],
                "new_entries": [],
                "quality_scores": {}
            }
            
            # 提取关键信息
            consensus = debate_result.get("consensus", {})
            new_insights = debate_result.get("new_insights", [])
            evidence = debate_result.get("evidence", [])
            
            # 处理共识内容
            if consensus and consensus.get("key_points"):
                for point in consensus["key_points"]:
                    entry_data = {
                        "title": f"{debate_result['topic']} - {point[:50]}...",
                        "content": point,
                        "source": "辩论共识",
                        "confidence": consensus.get("agreement_level", 0.5),
                        "contributors": debate_result.get("participants", []),
                        "evidence": evidence
                    }
                    
                    # 创建或更新知识条目
                    if self.wiki_service:
                        # 使用WikiService的create_entry方法
                        wiki_version = self.wiki_service.create_entry(
                            entry_name=f"debate_consensus_{len(update_result['new_entries']) + 1}",
                            content=point,
                            author_role="debate_system",
                            tags=["辩论", "共识"],
                            category="辩论结果"
                        )
                        entry_id = wiki_version.entry_name if wiki_version else f"entry_{len(update_result['new_entries']) + 1}"
                    else:
                        entry_id = f"entry_{len(update_result['new_entries']) + 1}"
                    
                    update_result["new_entries"].append({
                        "entry_id": entry_id,
                        "title": entry_data["title"],
                        "content": entry_data["content"]
                    })
                    
                    # 评估质量
                    quality_score = self._evaluate_content_quality(entry_data)
                    update_result["quality_scores"][entry_id] = quality_score
            
            # 处理新洞察
            for insight in new_insights:
                insight_entry = {
                    "title": f"洞察: {insight[:50]}...",
                    "content": insight,
                    "source": "辩论洞察",
                    "confidence": 0.7,  # 洞察的默认置信度
                    "contributors": debate_result.get("participants", []),
                    "evidence": evidence
                }
                
                if self.wiki_service:
                    # 使用WikiService的create_entry方法
                    wiki_version = self.wiki_service.create_entry(
                        entry_name=f"debate_insight_{len(update_result['new_entries']) + 1}",
                        content=insight,
                        author_role="debate_system",
                        tags=["辩论", "洞察"],
                        category="辩论洞察"
                    )
                    entry_id = wiki_version.entry_name if wiki_version else f"insight_{len(update_result['new_entries']) + 1}"
                else:
                    entry_id = f"insight_{len(update_result['new_entries']) + 1}"
                
                update_result["new_entries"].append({
                    "entry_id": entry_id,
                    "title": insight_entry["title"],
                    "content": insight_entry["content"]
                })
                
                quality_score = self._evaluate_content_quality(insight_entry)
                update_result["quality_scores"][entry_id] = quality_score
            
            # 记录更新历史
            self.update_history.append(update_result)
            
            return update_result
            
        except Exception as e:
            logger.error(f"处理辩论结果失败: {e}")
            return {"error": str(e)}
    
    def auto_update_knowledge(
        self,
        topic: str,
        new_information: List[str]
    ) -> Dict[str, Any]:
        """自动更新知识"""
        try:
            update_result = {
                "success": True,
                "topic": topic,
                "updated_entries": [],
                "timestamp": datetime.now().isoformat()
            }
            
            for info in new_information:
                # 检查是否存在相关条目
                existing_entries = self._find_related_entries(topic, info)
                
                if existing_entries:
                    # 更新现有条目
                    for entry in existing_entries:
                        updated_entry = self._merge_information(entry, info)
                        
                        if self.wiki_service:
                            # WikiService没有直接的update方法，需要创建新版本
                            # 这里简化处理，记录更新意图
                            pass
                        
                        update_result["updated_entries"].append({
                            "entry_id": entry["id"],
                            "old_content": entry.get("content", ""),
                            "new_content": updated_entry.get("content", ""),
                            "update_type": "content_enhancement"
                        })
                else:
                    # 创建新条目
                    new_entry = {
                        "title": f"{topic} - {info[:50]}...",
                        "content": info,
                        "source": "自动更新",
                        "confidence": 0.6,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if self.wiki_service:
                        # 使用WikiService的create_entry方法
                        wiki_version = self.wiki_service.create_entry(
                            entry_name=f"auto_update_{len(update_result['updated_entries']) + 1}",
                            content=info,
                            author_role="auto_system",
                            tags=["自动更新"],
                            category="自动生成"
                        )
                        entry_id = wiki_version.entry_name if wiki_version else f"auto_{len(update_result['updated_entries']) + 1}"
                    else:
                        entry_id = f"auto_{len(update_result['updated_entries']) + 1}"
                    
                    update_result["updated_entries"].append({
                        "entry_id": entry_id,
                        "title": new_entry["title"],
                        "content": new_entry["content"],
                        "update_type": "new_entry"
                    })
            
            return update_result
            
        except Exception as e:
            logger.error(f"自动更新知识失败: {e}")
            return {"success": False, "error": str(e)}
    
    def track_changes(self, change_data: Dict[str, Any]) -> str:
        """追踪变更"""
        try:
            change_id = str(uuid.uuid4())
            
            change_record = {
                "change_id": change_id,
                "timestamp": datetime.now().isoformat(),
                "change_type": change_data.get("change_type", "unknown"),
                "entity_id": change_data.get("entity_id"),
                "old_value": change_data.get("old_value"),
                "new_value": change_data.get("new_value"),
                "reason": change_data.get("reason", ""),
                "contributor": change_data.get("contributor", "system")
            }
            
            # 添加到更新历史
            self.update_history.append(change_record)
            
            return change_id
            
        except Exception as e:
            logger.error(f"追踪变更失败: {e}")
            return None
    
    def _evaluate_content_quality(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """评估内容质量"""
        try:
            quality_score = {
                "accuracy": 0.0,
                "completeness": 0.0,
                "reliability": 0.0,
                "overall": 0.0
            }
            
            # 基于置信度评估准确性
            confidence = content_data.get("confidence", 0.5)
            quality_score["accuracy"] = confidence
            
            # 基于内容长度和结构评估完整性
            content = content_data.get("content", "")
            if len(content) > 100:
                quality_score["completeness"] = 0.8
            elif len(content) > 50:
                quality_score["completeness"] = 0.6
            else:
                quality_score["completeness"] = 0.4
            
            # 基于证据和来源评估可靠性
            evidence = content_data.get("evidence", [])
            contributors = content_data.get("contributors", [])
            
            reliability_factors = 0
            if evidence:
                reliability_factors += len(evidence) * 0.2
            if contributors:
                reliability_factors += len(contributors) * 0.1
            
            quality_score["reliability"] = min(reliability_factors, 1.0)
            
            # 计算总体质量
            quality_score["overall"] = (
                quality_score["accuracy"] * 0.4 +
                quality_score["completeness"] * 0.3 +
                quality_score["reliability"] * 0.3
            )
            
            return quality_score
            
        except Exception as e:
            logger.error(f"评估内容质量失败: {e}")
            return {"accuracy": 0.0, "completeness": 0.0, "reliability": 0.0, "overall": 0.0}
    
    def _find_related_entries(self, topic: str, information: str) -> List[Dict[str, Any]]:
        """查找相关条目"""
        try:
            if self.wiki_service:
                # 使用Wiki服务搜索
                search_results = self.wiki_service.search(topic)
                return [{"id": result, "title": result, "content": f"关于{result}的信息", "relevance": 0.8} for result in search_results]
            else:
                # 模拟搜索结果
                return [
                    {
                        "id": f"related_{topic.replace(' ', '_')}",
                        "title": f"相关条目: {topic}",
                        "content": f"关于{topic}的现有信息",
                        "relevance": 0.8
                    }
                ]
                
        except Exception as e:
            logger.error(f"查找相关条目失败: {e}")
            return []
    
    def _merge_information(self, existing_entry: Dict[str, Any], new_info: str) -> Dict[str, Any]:
        """合并信息"""
        try:
            merged_entry = existing_entry.copy()
            
            # 简单的信息合并策略
            existing_content = existing_entry.get("content", "")
            
            if new_info not in existing_content:
                merged_entry["content"] = f"{existing_content}\n\n补充信息: {new_info}"
                merged_entry["last_updated"] = datetime.now().isoformat()
                merged_entry["update_reason"] = "信息补充"
            
            return merged_entry
            
        except Exception as e:
            logger.error(f"合并信息失败: {e}")
            return existing_entry
    
    def get_update_statistics(self) -> Dict[str, Any]:
        """获取更新统计"""
        try:
            stats = {
                "total_updates": len(self.update_history),
                "successful_updates": 0,
                "failed_updates": 0,
                "recent_updates": [],
                "update_frequency": {}
            }
            
            # 统计成功和失败的更新
            for update in self.update_history:
                if "error" in update:
                    stats["failed_updates"] += 1
                else:
                    stats["successful_updates"] += 1
            
            # 获取最近的更新
            stats["recent_updates"] = self.update_history[-5:] if len(self.update_history) >= 5 else self.update_history
            
            # 计算更新频率（按日期）
            from collections import defaultdict
            frequency = defaultdict(int)
            
            for update in self.update_history:
                timestamp = update.get("timestamp", "")
                if timestamp:
                    date = timestamp.split("T")[0]  # 提取日期部分
                    frequency[date] += 1
            
            stats["update_frequency"] = dict(frequency)
            
            return stats
            
        except Exception as e:
            logger.error(f"获取更新统计失败: {e}")
            return {"error": str(e)}
    
    def clear_update_history(self) -> bool:
        """清除更新历史"""
        try:
            self.update_history.clear()
            self.update_queue.clear()
            return True
        except Exception as e:
            logger.error(f"清除更新历史失败: {e}")
            return False