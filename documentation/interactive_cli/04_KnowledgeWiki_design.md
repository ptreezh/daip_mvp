# 04 - 知识维基 - 设计文档 (TDD重构版)

## 1. 技术方法
Wiki功能将由 `start_knowledge_wiki()` 函数入口进行管理。

- **API依赖**: 此模块将严格依赖 `WikiService` 提供的API，所有方法的调用都必须参照 `documentation/GLOBAL_API_DICTIONARY.md`。
- **内容渲染**: 使用 `rich.markdown` 组件来渲染从 `get_entry` API获取的Wiki页面内容，以正确显示格式。
- **文件交互**: 对于创建和导出功能，将直接使用Python内置的文件I/O操作来读取用户指定的文件或写入导出的文件。
- **缺失API的补充实现**: `WikiService` 没有提供 `list_pages` 的API。因此，CLI将实现一个辅助函数，通过直接扫描 `WikiService` 使用的存储目录（例如 `daip_mvp_project/memory_bank/wiki/`）的子目录名称来获取所有Wiki条目的列表。这是一个客户端的补充实现，以满足 `FR-KW-04` 需求。

## 2. 组件交互
- **`start_knowledge_wiki()`**:
    - 初始化 `WikiService` 的一个实例。
    - 显示Wiki子菜单。
- **`handle_create_wiki_page()`**:
    - 提示用户输入 `title`, `content` (从文件或直接输入), `author`, `tags`, `category`。
    - 调用 `wiki_service.create_entry(...)`。
    - 打印成功或失败信息。
- **`handle_view_wiki_page()`**:
    - 提示用户输入 `entry_name`。
    - 调用 `wiki_service.get_entry(entry_name)`。
    - 如果页面存在，使用 `rich.markdown` 渲染其内容并打印。否则，打印未找到的错误消息。
- **`handle_list_wiki_pages()`**:
    - 调用本地实现的辅助函数 `_list_wiki_directories()`，该函数扫描wiki存储目录。
    - 使用 `rich.table` 格式化并显示扫描到的目录（即页面）列表。
- **`handle_search_wiki_pages()`**:
    - 提示用户输入 `query`。
    - 调用 `wiki_service.search(query)`。
    - 格式化并打印返回的结果片段列表。
- **`handle_export_wiki_page()`**:
    - 提示用户输入 `entry_name` 和目标 `file_path`。
    - 调用 `wiki_service.get_entry(entry_name)` 获取内容。
    - 将返回内容的 `content` 字段写入本地文件。

## 3. CLI流程 / 用户界面
**查看页面:**
```
> 请输入要查看的Wiki页面的名称: Consensus Algorithms
(CLI calls get_entry)
---
# Consensus Algorithms
A consensus algorithm is a process...
---
```

## 4. 测试策略
- **单元测试 (`tests/test_knowledge_wiki.py`)**:
    - **目标**: 独立测试Wiki CLI的UI和流程逻辑。
    - **Mock**:
        - `WikiService` 将被完全mock。
        - `create_entry` 将返回一个模拟的 `WikiVersion` 对象。
        - `get_entry` 将根据输入返回一个模拟的 `WikiVersion` 对象或 `None`。
        - `search` 将返回一个固定的结果列表。
        - 文件系统扫描 (`os.scandir` 或 `pathlib.Path.iterdir`) 将被mock，以返回一个固定的目录列表，用于测试 `handle_list_wiki_pages`。
    - **断言**:
        - 验证当用户执行各项操作时，对应的 `WikiService` 方法被以正确的参数调用。
        - 验证 `get_entry` 的返回内容被正确地传递给了 `rich.markdown`。
        - 验证 `handle_list_wiki_pages` 能够正确处理mock的文件系统扫描结果并打印表格。
        - 验证当 `get_entry` 返回 `None` 时，CLI能打印出“未找到”的错误消息。
        - 验证所有API调用和文件操作都被 `try-except` 块包裹，能正确处理异常。