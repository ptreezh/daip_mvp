# 04 - 知识维基 - 任务列表 (TDD重构版)

## 概述
此任务列表以TDD方式涵盖了将知识维基（Wiki）功能集成到交互式CLI中的所有步骤。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 创建与查看页面

-   [ ] **RED**: **T-KW-01**: 创建测试文件 `tests/test_knowledge_wiki.py`。编写失败测试 `test_create_page_success`。该测试将mock `WikiService`，模拟用户输入 "1" (创建) 及页面数据，并断言 `wiki_service.create_entry` 被以正确的参数调用。
-   [ ] **GREEN**: **T-KW-02**: 在 `interactive_cli.py` 中实现 `start_knowledge_wiki` 和 `handle_create_wiki_page` 函数。实现逻辑以收集用户输入并调用API。让 `test_create_page_success` 测试通过。
-   [ ] **RED**: **T-KW-03**: 编写失败测试 `test_view_page_success`。配置mock的 `get_entry` 方法以返回一个包含Markdown内容的 `WikiVersion` 对象。断言API被调用，并且stdout中打印了该Markdown内容。
-   [ ] **GREEN**: **T-KW-04**: 实现 `handle_view_wiki_page` 函数，调用API并使用 `rich.markdown` 渲染结果，让 `test_view_page_success` 测试通过。
-   [ ] **RED**: **T-KW-05**: 编写失败测试 `test_view_page_not_found`。配置mock的 `get_entry` 方法以返回 `None`。断言stdout打印了“未找到”的错误消息。
-   [ ] **GREEN**: **T-KW-06**: 在 `handle_view_wiki_page` 中添加对 `None` 返回值的处理，让 `test_view_page_not_found` 测试通过。

### Epic 2: 列表、搜索与导出

-   [ ] **RED**: **T-KW-07**: 编写失败测试 `test_list_pages_success`。Mock文件系统扫描函数（如 `os.scandir`），使其返回几个模拟的目录条目。断言该扫描函数被调用，并且stdout打印出一个包含这些目录名的表格。
-   [ ] **GREEN**: **T-KW-08**: 实现 `handle_list_wiki_pages` 函数和 `_list_wiki_directories` 辅助函数，让 `test_list_pages_success` 测试通过。
-   [ ] **RED**: **T-KW-09**: 编写失败测试 `test_search_pages_success`。配置mock的 `search` 方法以返回一个固定的结果列表。断言API被调用，并且返回的列表内容被打印到stdout。
-   [ ] **GREEN**: **T-KW-10**: 实现 `handle_search_wiki_pages` 函数，让 `test_search_pages_success` 测试通过。
-   [ ] **RED**: **T-KW-11**: 编写失败测试 `test_export_page_success`。Mock `wiki_service.get_entry` 和内置的 `open` 函数。断言 `get_entry` 被调用，并且 `open` 被以正确的路径和内容写入。
-   [ ] **GREEN**: **T-KW-12**: 实现 `handle_export_wiki_page` 函数，让 `test_export_page_success` 测试通过。
-   [ ] **REFACTOR**: **T-KW-13**: 重构 `start_knowledge_wiki` 及其所有处理函数。确保代码清晰，将文件I/O和目录扫描逻辑封装好，并验证所有测试仍然通过。