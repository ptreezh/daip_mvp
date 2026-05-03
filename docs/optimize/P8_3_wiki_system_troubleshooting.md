# P8.3 维基系统 - 故障排除 (P8.3 Wiki System - Troubleshooting)

## 🚨 常见问题

### 1. 页面创建失败
**症状**: 无法创建新页面或出现错误
**可能原因**: 
- 页面标题已存在
- 标题格式不符合规范
- 存储系统问题

**解决方案**:
```python
# 检查页面创建
async def check_page_creation(wiki_manager: WikiManager, title: str, content: str):
    try:
        # 检查页面是否已存在
        existing_page = await wiki_manager.get_page(title)
        if existing_page:
            print(f"页面 '{title}' 已存在")
            return existing_page
        
        # 创建新页面
        new_page = await wiki_manager.create_page(title, content, "system")
        print(f"页面创建成功: {new_page.title}")
        return new_page
    except Exception as e:
        print(f"页面创建失败: {e}")
        # 检查标题格式
        if not is_valid_title(title):
            print("标题格式不正确")
        return None
```

### 2. 搜索结果不准确
**症状**: 搜索返回不相关或缺失结果
**可能原因**: 
- 索引未正确建立
- 搜索查询处理问题
- 知识库同步延迟

**解决方案**:
```python
# 调试搜索功能
async def debug_search(wiki_manager: WikiManager, query: str):
    print(f"搜索查询: {query}")
    
    # 维基搜索
    wiki_results = await wiki_manager.search_pages(query)
    print(f"维基搜索结果: {len(wiki_results)} 个")
    
    # 检查是否有相关页面存在
    all_pages = await wiki_manager.get_all_pages()
    relevant_titles = [p.title for p in all_pages if query.lower() in p.title.lower()]
    print(f"相关页面标题: {relevant_titles}")
    
    return wiki_results
```

## 🔧 诊断工具

### 维基系统状态检查
```python
async def check_wiki_system_health(wiki_manager: WikiManager):
    # 检查系统统计
    stats = wiki_manager.get_statistics()
    print(f"页面总数: {stats.total_pages}")
    print(f"作者总数: {stats.total_authors}")
    print(f"热门标签: {stats.most_popular_tags[:5]}")
    
    # 检查搜索功能
    sample_search = await wiki_manager.search_pages("test", top_k=1)
    if sample_search:
        print("搜索功能正常")
    else:
        print("搜索功能异常")
    
    # 检查页面访问
    sample_page = await wiki_manager.get_page("Python编程基础")
    if sample_page:
        print(f"页面访问正常: {sample_page.title}")
    else:
        print("页面访问异常")
```

### 索引完整性验证
```python
async def validate_index_integrity(wiki_manager: WikiManager):
    """验证维基页面和知识库索引的一致性"""
    wiki_pages = await wiki_manager.get_all_pages()
    print(f"维基页面总数: {len(wiki_pages)}")
    
    # 验证每个页面在知识库中的索引
    unindexed_pages = []
    for page in wiki_pages:
        search_results = await wiki_manager.knowledge_manager.search(page.title)
        if not any(page.title.lower() in r.get('content', '').lower() for r in search_results):
            unindexed_pages.append(page.title)
    
    print(f"未索引页面: {unindexed_pages}")
    return len(unindexed_pages) == 0
```

## ⚠️ 性能问题

### 搜索慢
- **检查**: 索引大小或搜索算法
- **解决方案**: 优化索引或使用缓存

### 页面加载慢
- **检查**: 存储系统或页面内容大小
- **解决方案**: 优化存储或分页加载

## 🔍 调试技巧

### 详细页面操作日志
```python
async def detailed_page_operation_log(wiki_manager: WikiManager, operation: str, **kwargs):
    print(f"=== 开始 {operation} 操作 ===")
    
    start_time = time.time()
    try:
        if operation == "create":
            result = await wiki_manager.create_page(
                title=kwargs['title'],
                content=kwargs['content'],
                author=kwargs['author']
            )
        elif operation == "search":
            result = await wiki_manager.search_pages(kwargs['query'])
        elif operation == "get":
            result = await wiki_manager.get_page(kwargs['title'])
        
        end_time = time.time()
        print(f"操作完成，耗时: {end_time - start_time:.2f}秒")
        print(f"结果类型: {type(result).__name__}")
        
        if hasattr(result, '__len__'):
            print(f"结果数量: {len(result)}")
        
        return result
    except Exception as e:
        end_time = time.time()
        print(f"操作失败，耗时: {end_time - start_time:.2f}秒")
        print(f"错误: {e}")
        raise
    finally:
        print("=== 操作结束 ===")
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 涉及的页面标题和操作
3. 系统统计信息
4. 搜索查询和期望结果

---
> **需要集成信息？** 查看 [P8_3_wiki_system_integration.md](P8_3_wiki_system_integration.md)  
> **需要API详情？** 查看 [P8_3_wiki_system_api.md](P8_3_wiki_system_api.md)