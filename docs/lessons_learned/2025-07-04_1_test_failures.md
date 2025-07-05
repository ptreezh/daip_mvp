# 事故复盘：单元测试反复失败事件

**日期**: 2025-07-04
**作者**: Gemini Code Assist

## 1. 问题描述

在为 `VectorStore` 和 `wiki_tools` 编写单元测试时，尽管多次尝试修复，测试用例依然反复失败。

- `test_vector_store.py` 持续报告 `AssertionError: Expected 'embeddings' to be called once. Called 0 times.`，表明 `ollama` 模块的 mock 未生效。
- `test_wiki_tools.py` 持续报告 `AssertionError`，表明 `_sanitize_filename` 函数的字符串处理逻辑存在缺陷。

## 2. 根本原因分析

1.  **不正确的 Mock 目标**: `test_vector_store.py` 中，`@patch` 的目标 (`ollama.embeddings`) 虽然看似正确，但未能精确地替换掉 `vector_store.py` 模块在导入时已经获取到的 `ollama` 对象的引用。这是 `unittest.mock` 中一个常见但关键的陷阱。
2.  **脆弱的字符串处理**: `_sanitize_filename` 函数中的正则表达式逻辑不够健壮，在处理包含特殊字符和空格的复杂组合时，会导致单词意外合并，从而产生错误的输出。

## 3. 解决方案

1.  **精确 Mock**: 遵循“在哪里使用，就在哪里 Mock” (Patch where it's used) 的黄金法则。将 `test_vector_store.py` 中的 patch 目标修改为 `src.kernel.vector_store.ollama` 和 `src.kernel.vector_store.chromadb`，确保我们替换的是被测模块内部的实际对象引用。
2.  **健壮的正则逻辑**: 重新设计了 `_sanitize_filename` 函数的实现。采用多步、更清晰的正则表达式替换逻辑，先将所有非法字符统一转换为空格，然后将连续的空格合并为单个下划线，最后清理首尾的下划线。

## 4. 核心教训

- **Mock 必须精确**: 必须深刻理解 Python 的导入和命名空间机制，确保 patch 应用在正确的命名空间上，以避免 mock 失效。
- **数据清理必须健壮**: 在处理用户输入或外部数据时（如此处的标题），必须考虑所有边缘情况，编写能够应对复杂组合的、逻辑清晰的清理函数。