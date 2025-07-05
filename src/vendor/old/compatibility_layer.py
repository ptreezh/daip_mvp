"""兼容性层 - 为旧代码提供向后兼容的接口
"""

from src.interfaces import MemoryFilters
from src.service_container import get_container

# 获取统一服务
try:
    container = get_container()
    memory_service = container.get_memory_service()
    role_service = container.get_role_service()
except:
    memory_service = None
    role_service = None


# 兼容旧的memory_bank接口
def create_memory_bank(role_name: str) -> str:
    """兼容旧的create_memory_bank函数"""
    if memory_service and role_service:
        role_service.create_role_identity(
            {
                "id": role_name,
                "name": role_name,
                "title": role_name,
                "category": "general",
                "specialties": [],
                "description": f"Auto-created role: {role_name}",
                "bio": "",
                "skills": [],
                "experience_years": 0,
                "reputation_score": 0.0,
                "contact_info": {},
                "languages": [],
                "availability": "available",
                "location": "",
                "education": [],
                "certifications": [],
                "projects": [],
            },
        )
        return f"unified_memory_bank/{role_name}"
    else:
        # 回退到原始实现
        from tools.memory_bank import create_memory_bank as original_create

        return original_create(role_name)


def write_memory(role_name: str, content: str) -> str:
    """兼容旧的write_memory函数"""
    if memory_service:
        memory_id = memory_service.add_memory(
            role_id=role_name,
            content=content,
            memory_type="dialogue",
            importance=0.5,
        )
        return f"unified_memory/{memory_id}"
    else:
        from tools.memory_bank import write_memory as original_write

        return original_write(role_name, content)


def read_memory(role_name: str) -> str:
    """兼容旧的read_memory函数"""
    if memory_service:
        filters = MemoryFilters(limit=1)
        memories = memory_service.retrieve_memories(role_name, filters)
        return memories[0].content if memories else ""
    else:
        from tools.memory_bank import read_memory as original_read

        return original_read(role_name)


def list_memories(role_name: str, limit=None, tag=None, keyword=None):
    """兼容旧的list_memories函数"""
    if memory_service:
        filters = MemoryFilters(limit=limit or 50, tags=[tag] if tag else None)
        memories = memory_service.retrieve_memories(role_name, filters)

        # 转换为旧格式
        result = []
        for memory in memories:
            if keyword and keyword not in memory.content:
                continue
            result.append(
                {
                    "content": memory.content,
                    "timestamp": memory.timestamp,
                    "tags": memory.tags,
                },
            )
        return result
    else:
        from tools.memory_bank import list_memories as original_list

        return original_list(role_name, limit, tag, keyword)


# 兼容file_tools接口
def add_memory(
    agent_id: str,
    content: str,
    tags=None,
    source=None,
    embedding=None,
) -> str:
    """兼容旧的add_memory函数"""
    if memory_service:
        return memory_service.add_memory(
            role_id=agent_id,
            content=content,
            memory_type="experience",
            importance=0.5,
            tags=tags or [],
            metadata={"source": source} if source else None,
        )
    else:
        from tools.file_tools import add_memory as original_add

        return original_add(agent_id, content, tags, source, embedding)


def get_memory(agent_id: str, memory_id: str):
    """兼容旧的get_memory函数"""
    if memory_service:
        filters = MemoryFilters(limit=100)
        memories = memory_service.retrieve_memories(agent_id, filters)
        for memory in memories:
            if memory.id == memory_id:
                return {
                    "id": memory.id,
                    "content": memory.content,
                    "timestamp": memory.timestamp,
                    "tags": memory.tags,
                }
        return None
    else:
        from tools.file_tools import get_memory as original_get

        return original_get(agent_id, memory_id)
