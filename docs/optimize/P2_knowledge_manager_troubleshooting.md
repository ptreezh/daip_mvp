# P2 知识管理器 - 故障排除 (P2 Knowledge Manager - Troubleshooting)

## 🚨 常见问题

### 1. 向量搜索不准确
**症状**: 搜索结果与查询不相关
**可能原因**: 
- 嵌入模型质量差
- 向量索引问题
- 文档预处理不当

**解决方案**:
```python
# 检查嵌入质量
async def check_embedding_quality(km: KnowledgeManager, test_query: str):
    # 获取嵌入向量
    embedding = await km.model_provider.embed(test_query)
    print(f"嵌入维度: {len(embedding)}")
    print(f"嵌入范围: [{min(embedding)}, {max(embedding)}]")
```

### 2. 知识库性能问题
**症状**: 搜索响应慢或内存使用高
**可能原因**: 
- 知识库过大
- 索引效率低

**解决方案**:
- 重建向量索引
- 分割大型知识库
- 优化搜索top_k参数

## 🔧 诊断工具

### 知识库状态检查
```python
async def check_knowledge_base_status(km: KnowledgeManager):
    stats = await km.sync_knowledge_base()
    print(f"文档总数: {stats.get('total_docs', 0)}")
    print(f"最后同步时间: {stats.get('last_sync', 'N/A')}")
    print(f"索引状态: {stats.get('index_status', 'N/A')}")
```

### 搜索性能监控
```python
import time

async def monitor_search_performance(km: KnowledgeManager, query: str):
    start_time = time.time()
    results = await km.search(query)
    end_time = time.time()
    
    print(f"搜索耗时: {end_time - start_time:.2f}秒")
    print(f"返回结果数: {len(results)}")
    return results
```

## ⚠️ 性能问题

### 高内存使用
- **检查**: 知识库过大或加载了过多文档
- **解决方案**: 实现分页或文档分片

### 慢搜索响应
- **检查**: 向量索引未优化
- **解决方案**: 重建索引或使用近似搜索

## 🔍 调试技巧

### 向量相似度调试
```python
# 调试向量相似度计算
async def debug_similarity(km: KnowledgeManager, query: str, doc_content: str):
    query_vec = await km.model_provider.embed(query)
    doc_vec = await km.model_provider.embed(doc_content)
    
    # 计算相似度（余弦相似度）
    similarity = cosine_similarity([query_vec], [doc_vec])[0][0]
    print(f"相似度: {similarity}")
```

### 文档分块调试
```python
# 调试文档分块策略
def debug_chunking_strategy(text: str, chunk_size: int = 512):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)
        print(f"块 {len(chunks)}: {len(chunk)} 字符")
    return chunks
```

## 📞 支持信息
当寻求支持时，请提供：
1. 搜索查询和期望结果
2. 知识库大小和文档数量
3. 嵌入模型配置
4. 搜索性能指标（响应时间、结果质量）

---
> **需要集成信息？** 查看 [P2_knowledge_manager_integration.md](P2_knowledge_manager_integration.md)  
> **需要API详情？** 查看 [P2_knowledge_manager_api.md](P2_knowledge_manager_api.md)