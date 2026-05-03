# P2 知识管理器 - 集成指南 (P2 Knowledge Manager - Integration Guide)

## 🔗 与其他模块的集成

### 与P3模型提供者集成
```python
# P2使用P3进行文本嵌入
from daip_live.p3_model_provider.provider import LiteLLMProvider

class KnowledgeManager:
    def __init__(self, model_provider: LiteLLMProvider):
        self.model_provider = model_provider
    
    async def embed_text(self, text: str) -> List[float]:
        return await self.model_provider.embed(text)
```

### 与P5代理引擎集成
```python
# P5使用P2进行知识检索
from daip_live.p2_knowledge_manager.manager import KnowledgeManager

class AgentExecutor:
    def __init__(self, knowledge_manager: KnowledgeManager):
        self.knowledge_manager = knowledge_manager
    
    async def retrieve_context(self, query: str):
        results = await self.knowledge_manager.search(query, top_k=3)
        return [r.snippet for r in results]
```

## 🔄 知识检索模式

### 语义搜索使用
```python
# 语义搜索示例
async def semantic_search_example(knowledge_manager: KnowledgeManager):
    # 执行语义搜索
    search_results = await knowledge_manager.search(
        query_text="项目管理最佳实践", 
        top_k=5
    )
    
    # 处理搜索结果
    for result in search_results:
        print(f"相似度: {result.similarity}")
        print(f"内容: {result.snippet}")
```

### 知识注入到对话
```python
# 将知识注入到代理对话中
async def inject_knowledge_to_agent(agent_executor, knowledge_manager, user_query):
    # 检索相关知识
    knowledge_results = await knowledge_manager.search(user_query)
    
    # 构造增强上下文
    context = build_context_with_knowledge(user_query, knowledge_results)
    
    # 传递给代理执行
    async for event in agent_executor.chat_run(context):
        yield event
```

## 🔌 使用示例

### 基础知识管理
```python
from daip_live.p2_knowledge_manager.manager import KnowledgeManager
from daip_live.p3_model_provider.provider import LiteLLMProvider

# 初始化知识管理器
model_provider = LiteLLMProvider(config)
knowledge_manager = KnowledgeManager(model_provider)

# 添加文档
await knowledge_manager.add_document(
    content="项目管理包括范围、时间、成本、质量、资源、沟通、风险、采购和利益相关者管理。",
    metadata={"category": "project_management", "source": "textbook"}
)

# 执行搜索
results = await knowledge_manager.search("项目管理包括哪些方面", top_k=1)
print(results[0].snippet)
```

### 批量知识处理
```python
# 批量添加知识
async def batch_add_knowledge(km: KnowledgeManager, documents: List[Dict]):
    for doc in documents:
        await km.add_document(doc["content"], doc["metadata"])
    
    # 同步知识库
    sync_result = await km.sync_knowledge_base()
    print(f"同步完成: {sync_result}")
```

## ⚡ 性能考虑
- **向量缓存**: 缓存嵌入向量以避免重复计算
- **分批处理**: 大量文档分批处理
- **索引优化**: 定期重建向量索引

## 🐛 常见集成问题
- **嵌入模型不可用**: 确保P3模型提供者配置正确
- **向量维度不匹配**: 检查嵌入模型的输出维度
- **搜索性能**: 优化向量索引和查询参数

---
> **需要API详情？** 查看 [P2_knowledge_manager_api.md](P2_knowledge_manager_api.md)  
> **需要实现详情？** 查看 [P2_knowledge_manager_detailed.md](P2_knowledge_manager_detailed.md)