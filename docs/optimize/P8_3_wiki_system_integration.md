# P8.3 维基系统 - 集成指南 (P8.3 Wiki System - Integration Guide)

## 🔗 与其他模块的集成

### 与P2知识管理集成
```python
# 维基系统与知识管理系统集成
from daip_live.p2_knowledge_manager.manager import KnowledgeManager

class WikiManager:
    def __init__(self, knowledge_manager: KnowledgeManager):
        self.knowledge_manager = knowledge_manager
    
    async def index_new_page(self, page: WikiPage):
        # 将新页面添加到知识库
        await self.knowledge_manager.add_document(
            content=page.content,
            metadata={
                "title": page.title,
                "tags": page.tags,
                "author": page.author,
                "type": "wiki_page"
            }
        )
    
    async def search_with_knowledge(self, query: str, top_k: int = 10):
        # 合并维基搜索和知识库搜索
        wiki_results = await self.search_pages(query, top_k=top_k//2)
        knowledge_results = await self.knowledge_manager.search(query, top_k=top_k//2)
        
        # 合并和排序结果
        combined_results = self._merge_search_results(wiki_results, knowledge_results)
        return combined_results
```

### 与P1数据持久化集成
```python
# 维基系统使用P1进行数据存储
from daip_live.p1_data_persistence.repositories import WikiPageRepository

class WikiManager:
    def __init__(self, page_repository: WikiPageRepository):
        self.page_repository = page_repository
    
    async def save_page(self, page: WikiPage):
        # 使用P1的Repository保存页面
        await self.page_repository.create(page.dict())
```

## 🔄 维基操作流程

### 创建页面流程
```python
# 完整页面创建流程
async def complete_page_creation(wiki_manager: WikiManager, title: str, content: str, author: str):
    # 1. 验证页面是否已存在
    existing_page = await wiki_manager.get_page(title)
    if existing_page:
        raise ValueError(f"页面 '{title}' 已存在")
    
    # 2. 创建新页面
    new_page = await wiki_manager.create_page(title, content, author)
    
    # 3. 索引到知识库
    await wiki_manager.index_new_page(new_page)
    
    # 4. 返回创建结果
    return new_page
```

## 🔌 使用示例

### 基础维基操作
```python
from daip_live.p8_wiki_system.manager import WikiManager

# 初始化维基管理器
wiki_manager = container.wiki_manager()

# 创建页面
page = await wiki_manager.create_page(
    title="Python编程基础",
    content="Python是一种高级编程语言...",
    author="user123",
    tags=["programming", "python", "tutorial"]
)

# 搜索页面
results = await wiki_manager.search_pages("Python", tags=["programming"])
for result in results:
    print(f"{result.page.title}: {result.snippet}")
```

### 高级维基功能
```python
# 获取页面历史和比较
page_history = wiki_manager.get_page_history("Python编程基础")
current_version = page_history[-1]
previous_version = page_history[-2] if len(page_history) > 1 else None

if previous_version:
    differences = compare_page_versions(current_version, previous_version)
    print(f"页面变更: {differences}")
```

## ⚡ 性能考虑
- **搜索优化**: 使用向量搜索和传统搜索相结合
- **缓存策略**: 缓存热门页面和搜索结果
- **存储优化**: 有效的页面版本存储策略

## 🐛 常见集成问题
- **索引同步**: 确保维基页面与知识库同步
- **权限控制**: 验证页面创建和编辑权限
- **引用完整性**: 维护页面间的引用关系

---
> **需要API详情？** 查看 [P8_3_wiki_system_api.md](P8_3_wiki_system_api.md)  
> **需要实现详情？** 查看 [P8_3_wiki_system_detailed.md](P8_3_wiki_system_detailed.md)