# 04 - 知识维基 - 需求文档 (TDD重构版)

## 1. 简介
该模块为用户提供了一个创建和管理知识库（Wiki）的界面。用户可以创建、查看、搜索和导出Wiki页面。

## 2. 用户故事
- **As a user**, I want to create a new Wiki page with a title and content.
- **As a user**, I want to view the content of an existing Wiki page by its name.
- **As a user**, I want to list all available Wiki pages.
- **As a user**, I want to search for Wiki pages containing specific keywords.
- **As a user**, I want to export a Wiki page to a Markdown file.

## 3. 功能性需求
- **FR-KW-01**: **必须**提供一个Wiki子菜单，包含以下选项：
    - `[1]` 创建新Wiki页面
    - `[2]` 查看Wiki页面
    - `[3]` 列出所有Wiki页面
    - `[4]` 搜索Wiki页面
    - `[5]` 导出Wiki页面
    - `[0]` 返回主菜单
- **FR-KW-02**: **创建新页面**:
    - **必须**提示用户输入页面标题和内容（可从文件或直接输入）。
    - **必须**调用 `WikiService.create_entry` API。
- **FR-KW-03**: **查看页面**:
    - **必须**提示用户输入页面名称。
    - **必须**调用 `WikiService.get_entry` API。
    - **必须**使用Markdown格式在终端渲染页面内容。
- **FR-KW-04**: **列出所有页面**:
    - **必须**能以列表形式展示所有Wiki页面的标题和ID。（此功能需要 `WikiService` 提供一个 `list_pages` 或类似方法。**API勘察**: `WikiService` 没有直接的 `list_pages` 方法，需要通过扫描wiki目录来实现）。
- **FR-KW-05**: **搜索页面**:
    - **必须**提示用户输入搜索关键词。
    - **必须**调用 `WikiService.search` API。
    - **必须**显示搜索结果片段。
- **FR-KW-06**: **导出页面**:
    - **必须**提示用户选择一个页面和导出文件路径。
    - **必须**调用 `WikiService.get_entry` 获取内容，并将其保存到本地文件。

## 4. 验收测试用例
- **ATC-KW-01: 成功创建并查看页面**
    - **Given**: 用户在Wiki子菜单。
    - **When**: 用户选择 "创建" -> 输入标题 "Test Page" 和内容 "Hello" -> 然后选择 "查看" -> 输入 "Test Page"。
    - **Then**: `WikiService.create_entry` **必须**被成功调用。
    - **And**: `WikiService.get_entry` **必须**被成功调用。
    - **And**: "Hello" **必须**被显示在终端。
- **ATC-KW-02: 成功搜索页面**
    - **Given**: Wiki中存在一个包含 "semantic search" 的页面。
    - **When**: 用户选择 "搜索" 并输入 "semantic"。
    - **Then**: `WikiService.search` **必须**被以 `query='semantic'` 为参数调用。
    - **And**: 包含 "semantic search" 的结果片段**必须**被显示在终端。
- **ATC-KW-03: 查看不存在的页面**
    - **Given**: 用户在Wiki子菜单。
    - **When**: 用户选择 "查看" 并输入一个不存在的页面名称 "NonExistentPage"。
    - **Then**: `WikiService.get_entry` **必须**被调用并返回 `None`。
    - **And**: CLI**必须**显示一条清晰的“页面未找到”错误消息。