# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : vector_store.py
@Description:
    Vector store manager for semantic search and knowledge retrieval.
    Handles vector database operations, embeddings, and similarity search.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
import logging
import numpy as np
from dataclasses import dataclass

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    # 创建虚拟类用于类型提示
    class chromadb:
        class Client:
            pass

# 全局向量存储管理器实例
_vector_store_manager: Optional['VectorStoreManager'] = None


@dataclass
class VectorDocument:
    """向量文档"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class SearchResult:
    """搜索结果"""
    document: VectorDocument
    score: float
    metadata: Dict[str, Any]


class EmbeddingProvider:
    """嵌入提供者基类"""
    
    async def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
        raise NotImplementedError
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入"""
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    """模拟嵌入提供者"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    async def embed(self, text: str) -> List[float]:
        """生成模拟嵌入"""
        # 使用文本的哈希值作为伪随机种子
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        
        np.random.seed(seed)
        embedding = np.random.normal(0, 1, self.dimension).tolist()
        
        # 归一化
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成模拟嵌入"""
        return await asyncio.gather(*[self.embed(text) for text in texts])


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama嵌入提供者"""
    
    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.dimension = 768  # nomic-embed-text的维度
    
    async def embed(self, text: str) -> List[float]:
        """使用Ollama生成嵌入"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model_name,
                    "prompt": text,
                    "options": {
                        "temperature": 0.0
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["embedding"]
                    else:
                        logging.error(f"Ollama embedding failed: {response.status}")
                        # 降级到模拟嵌入
                        mock_provider = MockEmbeddingProvider(self.dimension)
                        return await mock_provider.embed(text)
                        
        except Exception as e:
            logging.error(f"Error generating Ollama embedding: {e}")
            # 降级到模拟嵌入
            mock_provider = MockEmbeddingProvider(self.dimension)
            return await mock_provider.embed(text)
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成Ollama嵌入"""
        return await asyncio.gather(*[self.embed(text) for text in texts])


class VectorStoreManager:
    """向量存储管理器 - 管理向量数据库和语义搜索"""
    
    def __init__(self, collection_name: str = "daip_knowledge", 
                 embedding_provider: EmbeddingProvider = None,
                 persist_directory: str = "./data/vector_store"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()
        
        # ChromaDB客户端
        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.Collection] = None
        
        # 统计信息
        self.stats = {
            "total_documents": 0,
            "searches_performed": 0,
            "documents_added": 0,
            "documents_updated": 0,
            "documents_deleted": 0,
            "embedding_cache_hits": 0,
            "embedding_cache_misses": 0,
            "average_search_time": 0.0,
            "start_time": datetime.now()
        }
        
        # 嵌入缓存
        self.embedding_cache: Dict[str, List[float]] = {}
        self.max_cache_size = 10000
        
        # 配置参数
        self.config = {
            "max_results": 10,
            "similarity_threshold": 0.7,
            "enable_cache": True,
            "enable_persistence": True,
            "batch_size": 100,
            "search_timeout": 30
        }
        
        self.is_initialized = False
    
    async def initialize(self):
        """初始化向量存储"""
        if self.is_initialized:
            return
        
        if not CHROMADB_AVAILABLE:
            logging.warning("ChromaDB not available. Vector operations will be limited.")
            self.is_initialized = True
            return
        
        try:
            # 创建ChromaDB客户端
            if self.config["enable_persistence"]:
                self.client = chromadb.PersistentClient(path=self.persist_directory)
            else:
                self.client = chromadb.EphemeralClient()
            
            # 获取或创建集合
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
            except Exception:
                self.collection = self.client.create_collection(name=self.collection_name)
            
            # 更新统计
            self.stats["total_documents"] = self.collection.count()
            
            self.is_initialized = True
            logging.info(f"Vector store initialized with {self.stats['total_documents']} documents")
            
        except Exception as e:
            logging.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def add_document(self, document: VectorDocument, embedding: List[float] = None) -> bool:
        """添加文档到向量存储"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 生成嵌入
            if embedding is None:
                embedding = await self._get_embedding(document.content)
            
            # 准备数据
            document_data = {
                "ids": [document.id],
                "documents": [document.content],
                "metadatas": [document.metadata],
                "embeddings": [embedding]
            }
            
            # 添加到集合
            if self.collection:
                self.collection.add(**document_data)
            
            # 更新缓存
            if self.config["enable_cache"]:
                self._update_embedding_cache(document.content, embedding)
            
            # 更新统计
            self.stats["documents_added"] += 1
            self.stats["total_documents"] += 1
            
            return True
            
        except Exception as e:
            logging.error(f"Error adding document {document.id}: {e}")
            return False
    
    async def add_documents_batch(self, documents: List[VectorDocument]) -> int:
        """批量添加文档"""
        if not documents:
            return 0
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 批量生成嵌入
            embeddings = await self._get_embeddings_batch([doc.content for doc in documents])
            
            # 准备数据
            document_data = {
                "ids": [doc.id for doc in documents],
                "documents": [doc.content for doc in documents],
                "metadatas": [doc.metadata for doc in documents],
                "embeddings": embeddings
            }
            
            # 批量添加到集合
            if self.collection:
                self.collection.add(**document_data)
            
            # 更新缓存
            if self.config["enable_cache"]:
                for doc, embedding in zip(documents, embeddings):
                    self._update_embedding_cache(doc.content, embedding)
            
            # 更新统计
            self.stats["documents_added"] += len(documents)
            self.stats["total_documents"] += len(documents)
            
            return len(documents)
            
        except Exception as e:
            logging.error(f"Error adding documents batch: {e}")
            return 0
    
    async def search(self, query: str, limit: int = None, 
                   filter_metadata: Dict[str, Any] = None) -> List[SearchResult]:
        """搜索相似文档"""
        if not self.is_initialized:
            await self.initialize()
        
        limit = limit or self.config["max_results"]
        
        try:
            start_time = datetime.now()
            
            # 生成查询嵌入
            query_embedding = await self._get_embedding(query)
            
            # 执行搜索
            results = []
            
            if self.collection:
                # 使用ChromaDB搜索
                chroma_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=filter_metadata,
                    include=["documents", "metadatas", "distances"]
                )
                
                # 处理结果
                for i in range(len(chroma_results["ids"][0])):
                    doc_id = chroma_results["ids"][0][i]
                    content = chroma_results["documents"][0][i]
                    metadata = chroma_results["metadatas"][0][i]
                    distance = chroma_results["distances"][0][i]
                    
                    # 转换距离为相似度分数
                    score = 1.0 / (1.0 + distance)
                    
                    document = VectorDocument(
                        id=doc_id,
                        content=content,
                        metadata=metadata,
                        embedding=query_embedding
                    )
                    
                    results.append(SearchResult(
                        document=document,
                        score=score,
                        metadata=metadata
                    ))
                
                # 过滤低相似度结果
                results = [r for r in results if r.score >= self.config["similarity_threshold"]]
            
            # 更新统计
            search_time = (datetime.now() - start_time).total_seconds()
            self.stats["searches_performed"] += 1
            self.stats["average_search_time"] = (
                (self.stats["average_search_time"] * (self.stats["searches_performed"] - 1) + search_time) /
                self.stats["searches_performed"]
            )
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching for query '{query}': {e}")
            return []
    
    async def semantic_search(self, query: str, limit: int = None,
                           filter_metadata: Dict[str, Any] = None) -> List[SearchResult]:
        """语义搜索（别名）"""
        return await self.search(query, limit, filter_metadata)
    
    async def find_similar_documents(self, document_id: str, limit: int = None) -> List[SearchResult]:
        """查找相似文档"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 获取文档
            document = await self.get_document(document_id)
            if not document:
                return []
            
            # 使用文档内容进行搜索
            return await self.search(document.content, limit)
            
        except Exception as e:
            logging.error(f"Error finding similar documents for {document_id}: {e}")
            return []
    
    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """获取文档"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            if self.collection:
                result = self.collection.get(
                    ids=[document_id],
                    include=["documents", "metadatas", "embeddings"]
                )
                
                if result["ids"]:
                    return VectorDocument(
                        id=result["ids"][0],
                        content=result["documents"][0],
                        metadata=result["metadatas"][0],
                        embedding=result["embeddings"][0] if result["embeddings"] else None
                    )
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting document {document_id}: {e}")
            return None
    
    async def update_document(self, document_id: str, new_content: str = None,
                            new_metadata: Dict[str, Any] = None) -> bool:
        """更新文档"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 获取现有文档
            existing_doc = await self.get_document(document_id)
            if not existing_doc:
                return False
            
            # 准备更新数据
            content = new_content or existing_doc.content
            metadata = new_metadata or existing_doc.metadata
            
            # 生成新的嵌入
            embedding = await self._get_embedding(content)
            
            # 更新集合
            if self.collection:
                self.collection.update(
                    ids=[document_id],
                    documents=[content],
                    metadatas=[metadata],
                    embeddings=[embedding]
                )
            
            # 更新缓存
            if self.config["enable_cache"]:
                self._update_embedding_cache(content, embedding)
            
            # 更新统计
            self.stats["documents_updated"] += 1
            
            return True
            
        except Exception as e:
            logging.error(f"Error updating document {document_id}: {e}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            if self.collection:
                self.collection.delete(ids=[document_id])
            
            # 更新统计
            self.stats["documents_deleted"] += 1
            self.stats["total_documents"] -= 1
            
            return True
            
        except Exception as e:
            logging.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def delete_documents_by_metadata(self, filter_metadata: Dict[str, Any]) -> int:
        """根据元数据删除文档"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            if self.collection:
                # 获取匹配的文档ID
                results = self.collection.get(
                    where=filter_metadata,
                    include=["ids"]
                )
                
                if results["ids"]:
                    deleted_count = len(results["ids"])
                    self.collection.delete(ids=results["ids"])
                    
                    # 更新统计
                    self.stats["documents_deleted"] += deleted_count
                    self.stats["total_documents"] -= deleted_count
                    
                    return deleted_count
            
            return 0
            
        except Exception as e:
            logging.error(f"Error deleting documents by metadata: {e}")
            return 0
    
    async def get_all_documents(self, limit: int = 100, offset: int = 0) -> List[VectorDocument]:
        """获取所有文档"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            documents = []
            
            if self.collection:
                results = self.collection.get(
                    limit=limit,
                    offset=offset,
                    include=["documents", "metadatas", "embeddings"]
                )
                
                for i in range(len(results["ids"])):
                    document = VectorDocument(
                        id=results["ids"][i],
                        content=results["documents"][i],
                        metadata=results["metadatas"][i],
                        embedding=results["embeddings"][i] if results["embeddings"] else None
                    )
                    documents.append(document)
            
            return documents
            
        except Exception as e:
            logging.error(f"Error getting all documents: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            stats = {
                "collection_name": self.collection_name,
                "total_documents": self.stats["total_documents"],
                "documents_added": self.stats["documents_added"],
                "documents_updated": self.stats["documents_updated"],
                "documents_deleted": self.stats["documents_deleted"],
                "searches_performed": self.stats["searches_performed"],
                "average_search_time": self.stats["average_search_time"],
                "embedding_cache_size": len(self.embedding_cache),
                "embedding_cache_hits": self.stats["embedding_cache_hits"],
                "embedding_cache_misses": self.stats["embedding_cache_misses"],
                "cache_hit_rate": self.stats["embedding_cache_hits"] / 
                               (self.stats["embedding_cache_hits"] + self.stats["embedding_cache_misses"]) 
                               if (self.stats["embedding_cache_hits"] + self.stats["embedding_cache_misses"]) > 0 else 0,
                "is_persistent": self.config["enable_persistence"],
                "persist_directory": self.persist_directory if self.config["enable_persistence"] else None,
                "embedding_provider": type(self.embedding_provider).__name__,
                "embedding_dimension": getattr(self.embedding_provider, 'dimension', 384)
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting collection stats: {e}")
            return {}
    
    async def clear_collection(self) -> bool:
        """清空集合"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            if self.collection:
                # 获取所有文档ID
                results = self.collection.get(include=["ids"])
                if results["ids"]:
                    self.collection.delete(ids=results["ids"])
                
                # 重置统计
                self.stats["total_documents"] = 0
                self.stats["documents_added"] = 0
                self.stats["documents_updated"] = 0
                self.stats["documents_deleted"] = 0
                
                # 清空缓存
                self.embedding_cache.clear()
                
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error clearing collection: {e}")
            return False
    
    async def _get_embedding(self, text: str) -> List[float]:
        """获取文本嵌入"""
        if self.config["enable_cache"] and text in self.embedding_cache:
            self.stats["embedding_cache_hits"] += 1
            return self.embedding_cache[text]
        
        self.stats["embedding_cache_misses"] += 1
        embedding = await self.embedding_provider.embed(text)
        
        if self.config["enable_cache"]:
            self._update_embedding_cache(text, embedding)
        
        return embedding
    
    async def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取文本嵌入"""
        if self.config["enable_cache"]:
            # 检查缓存
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                if text in self.embedding_cache:
                    cached_embeddings.append((i, self.embedding_cache[text]))
                    self.stats["embedding_cache_hits"] += 1
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # 生成未缓存的嵌入
            if uncached_texts:
                self.stats["embedding_cache_misses"] += len(uncached_texts)
                new_embeddings = await self.embedding_provider.embed_batch(uncached_texts)
                
                # 更新缓存
                for text, embedding in zip(uncached_texts, new_embeddings):
                    self._update_embedding_cache(text, embedding)
                
                # 合并结果
                all_embeddings = [None] * len(texts)
                for idx, embedding in cached_embeddings:
                    all_embeddings[idx] = embedding
                for idx, embedding in zip(uncached_indices, new_embeddings):
                    all_embeddings[idx] = embedding
                
                return all_embeddings
            else:
                return [emb for _, emb in sorted(cached_embeddings)]
        else:
            return await self.embedding_provider.embed_batch(texts)
    
    def _update_embedding_cache(self, text: str, embedding: List[float]):
        """更新嵌入缓存"""
        if len(self.embedding_cache) >= self.max_cache_size:
            # 简单的LRU缓存清理
            oldest_key = next(iter(self.embedding_cache))
            del self.embedding_cache[oldest_key]
        
        self.embedding_cache[text] = embedding
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self.is_initialized:
                return {
                    "status": "not_initialized",
                    "healthy": False,
                    "message": "Vector store not initialized"
                }
            
            # 测试基本操作
            test_doc = VectorDocument(
                id="health_check_test",
                content="Health check test document",
                metadata={"type": "test"}
            )
            
            # 添加文档
            add_success = await self.add_document(test_doc)
            
            # 搜索文档
            search_results = await self.search("health check", limit=1)
            
            # 删除文档
            delete_success = await self.delete_document("health_check_test")
            
            if add_success and len(search_results) > 0 and delete_success:
                return {
                    "status": "healthy",
                    "healthy": True,
                    "message": "Vector store is functioning properly",
                    "total_documents": self.stats["total_documents"],
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "healthy": False,
                    "message": "Basic operations test failed",
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "healthy": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }


async def get_vector_store_manager(collection_name: str = "daip_knowledge",
                                  embedding_provider: EmbeddingProvider = None) -> VectorStoreManager:
    """获取向量存储管理器实例"""
    global _vector_store_manager
    
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager(collection_name, embedding_provider)
        await _vector_store_manager.initialize()
    
    return _vector_store_manager


async def close_vector_store_connection():
    """关闭向量存储连接"""
    global _vector_store_manager
    
    if _vector_store_manager:
        _vector_store_manager = None