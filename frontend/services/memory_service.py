#!/usr/bin/env python3
"""记忆管理服务

连接前端记忆管理界面与后端MemAgent，提供记忆的CRUD操作和智能管理功能
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.memory_agent import MemAgent, Memory, MemoryQuery, MemoryType

logger = logging.getLogger(__name__)


class MemoryService:
    """记忆管理服务"""
    
    def __init__(self):
        """初始化记忆服务"""
        self.sskg_manager = None
        self.mem_agent = None
        self.is_initialized = False
        
    async def initialize(self):
        """初始化服务"""
        try:
            # 初始化SSKG管理器
            self.sskg_manager = EnhancedSSKGManager()
            
            # 初始化MemAgent
            model_path = Path("data/models/memagent_model.json")
            self.mem_agent = MemAgent(
                sskg_manager=self.sskg_manager,
                model_path=model_path,
                enable_rl=True
            )
            
            self.is_initialized = True
            logger.info("记忆管理服务初始化完成")
            
        except Exception as e:
            logger.error(f"记忆服务初始化失败: {e}")
            raise
    
    async def get_memories(self, 
                          source_id: Optional[str] = None,
                          memory_type: Optional[str] = None,
                          search_query: Optional[str] = None,
                          limit: int = 20) -> list[dict[str, Any]]:
        """获取记忆列表"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 构建查询
            query = MemoryQuery(
                content=search_query or "",
                memory_types=[MemoryType(memory_type)] if memory_type else None,
                source_id=source_id,
                limit=limit
            )
            
            # 从MemAgent检索记忆
            memories = self.mem_agent.retrieve_memories(
                context=search_query or "all memories",
                query=query
            )
            
            # 转换为前端格式
            result = []
            for memory in memories:
                result.append({
                    "id": memory.id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "source_id": memory.source_id,
                    "importance": memory.importance,
                    "recency": memory.recency,
                    "created_at": memory.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_accessed": memory.last_accessed.strftime("%Y-%m-%d %H:%M:%S"),
                    "access_count": memory.access_count,
                    "related_memories": memory.related_memories,
                    "metadata": memory.metadata
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取记忆失败: {e}")
            return []
    
    async def create_memory(self, 
                           content: str,
                           memory_type: str,
                           source_id: str,
                           importance: float = 0.5,
                           metadata: Optional[dict[str, Any]] = None) -> Optional[str]:
        """创建新记忆"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 创建记忆对象
            memory = Memory(
                content=content,
                memory_type=MemoryType(memory_type),
                source_id=source_id,
                importance=importance,
                recency=1.0,  # 新记忆时近性最高
                metadata=metadata or {}
            )
            
            # 存储记忆
            memory_id = self.mem_agent.store_memory(memory)
            logger.info(f"创建记忆成功: {memory_id}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"创建记忆失败: {e}")
            return None
    
    async def update_memory(self, 
                           memory_id: str,
                           content: Optional[str] = None,
                           importance: Optional[float] = None,
                           metadata: Optional[dict[str, Any]] = None) -> bool:
        """更新记忆"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 获取现有记忆
            existing_memories = await self.get_memories()
            existing_memory = next(
                (m for m in existing_memories if m["id"] == memory_id), 
                None
            )
            
            if not existing_memory:
                logger.error(f"记忆不存在: {memory_id}")
                return False
            
            # 更新记忆内容
            if content is not None:
                existing_memory["content"] = content
            if importance is not None:
                existing_memory["importance"] = importance
            if metadata is not None:
                existing_memory["metadata"].update(metadata)
            
            # 重新创建记忆对象并存储
            updated_memory = Memory(
                id=memory_id,
                content=existing_memory["content"],
                memory_type=MemoryType(existing_memory["memory_type"]),
                source_id=existing_memory["source_id"],
                importance=existing_memory["importance"],
                recency=existing_memory["recency"],
                metadata=existing_memory["metadata"]
            )
            
            # 存储更新后的记忆
            self.mem_agent.store_memory(updated_memory)
            logger.info(f"更新记忆成功: {memory_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 注意：当前MemAgent实现中没有直接的删除方法
            # 这里我们可以通过标记的方式"软删除"
            success = await self.update_memory(
                memory_id,
                metadata={"deleted": True, "deleted_at": datetime.now().isoformat()}
            )
            
            if success:
                logger.info(f"删除记忆成功: {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False
    
    async def get_memory_statistics(self, source_id: Optional[str] = None) -> dict[str, Any]:
        """获取记忆统计信息"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            memories = await self.get_memories(source_id=source_id, limit=1000)
            
            if not memories:
                return {
                    "total_count": 0,
                    "type_distribution": {},
                    "average_importance": 0.0,
                    "average_recency": 0.0,
                    "most_accessed": None
                }
            
            # 统计信息
            type_distribution = {}
            total_importance = 0
            total_recency = 0
            most_accessed = max(memories, key=lambda m: m["access_count"])
            
            for memory in memories:
                mem_type = memory["memory_type"]
                type_distribution[mem_type] = type_distribution.get(mem_type, 0) + 1
                total_importance += memory["importance"]
                total_recency += memory["recency"]
            
            return {
                "total_count": len(memories),
                "type_distribution": type_distribution,
                "average_importance": total_importance / len(memories),
                "average_recency": total_recency / len(memories),
                "most_accessed": most_accessed
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    async def organize_memories(self, source_id: str) -> dict[str, list[dict[str, Any]]]:
        """组织记忆"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            memories = await self.get_memories(source_id=source_id, limit=1000)
            
            # 转换为Memory对象
            memory_objects = []
            for mem_data in memories:
                memory_obj = Memory(
                    id=mem_data["id"],
                    content=mem_data["content"],
                    memory_type=MemoryType(mem_data["memory_type"]),
                    source_id=mem_data["source_id"],
                    importance=mem_data["importance"],
                    recency=mem_data["recency"],
                    access_count=mem_data["access_count"],
                    metadata=mem_data["metadata"]
                )
                memory_objects.append(memory_obj)
            
            # 使用MemAgent组织记忆
            organized = self.mem_agent.organize_memories(memory_objects)
            
            # 转换回前端格式
            result = {}
            for memory_type, memory_list in organized.items():
                result[memory_type.value] = [
                    {
                        "id": mem.id,
                        "content": mem.content,
                        "importance": mem.importance,
                        "recency": mem.recency,
                        "access_count": mem.access_count
                    }
                    for mem in memory_list
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"组织记忆失败: {e}")
            return {}
    
    async def share_memories(self, 
                            source_id: str, 
                            target_id: str, 
                            memory_ids: list[str]) -> bool:
        """共享记忆"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 使用MemAgent的共享功能
            success = self.mem_agent.share_memories(source_id, target_id, memory_ids)
            
            if success:
                logger.info(f"共享记忆成功: {source_id} -> {target_id}, 记忆数: {len(memory_ids)}")
            
            return success
            
        except Exception as e:
            logger.error(f"共享记忆失败: {e}")
            return False
    
    async def consolidate_memories(self, source_id: str, memory_type: Optional[str] = None) -> list[dict[str, Any]]:
        """整合记忆"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 使用MemAgent的整合功能
            mem_type = MemoryType(memory_type) if memory_type else None
            consolidated = self.mem_agent.consolidate_memories(source_id, mem_type)
            
            # 转换为前端格式
            result = []
            for memory in consolidated:
                result.append({
                    "id": memory.id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "source_id": memory.source_id,
                    "importance": memory.importance,
                    "recency": memory.recency,
                    "related_memories": memory.related_memories,
                    "metadata": memory.metadata
                })
            
            logger.info(f"整合记忆成功: {source_id}, 生成 {len(result)} 个整合记忆")
            return result
            
        except Exception as e:
            logger.error(f"整合记忆失败: {e}")
            return []