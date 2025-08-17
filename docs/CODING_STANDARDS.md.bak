# DAIP-MVP 编码规范

本文档定义了 DAIP-MVP 项目的编码标准、文件头规范和最佳实践。所有贡献者必须严格遵守这些规范。

## 1. 代码风格

*   **PEP 8**: 所有 Python 代码必须严格遵循 [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)。
*   **Black**: 使用 `black` 作为代码格式化工具，以确保风格一致性。`.pre-commit-config.yaml` 已配置 `black`，会在每次提交时自动格式化代码。
*   **Pylint**: 使用 `pylint` 进行代码质量检查。配置见 `pyproject.toml`。目标是达到 9.5 分以上。
*   **行长度**: 最大行长度为 120 个字符。

## 2. 类型提示

*   **Mypy**: 使用 `mypy` 进行静态类型检查。配置见 `pyproject.toml`。
*   **强制类型注解**: 所有新的函数和方法都必须有完整的类型注解。不允许使用 `disallow_untyped_defs = true` 规则来禁止没有类型注解的函数定义。
*   **清晰的类型**: 尽量使用明确的类型，避免过多使用 `Any`。

## 3. 文件头规范

所有 `.py` 文件都必须包含以下格式的文件头：

```python
# -*- coding: utf-8 -*-
"""
@Time    : [YYYY-MM-DD HH:MM:SS]
@Author  : [Your Name / Team Name]
@File    : [filename.py]
@Description:
    [A brief description of the file's purpose.]
"""
```

**示例**:

```python
# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-03 17:30:00
@Author  : DAIP-LIVE Team
@File    : role_manager.py
@Description:
    Manages the loading, validation, and retrieval of role definitions.
"""
```

## 4. 文档字符串 (Docstrings)

*   所有模块、类、函数和方法都必须有文档字符串。
*   遵循 [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)。
*   推荐使用 **Google Python Style Docstrings** 格式，因为它具有良好的可读性，并且可以被 Sphinx 等文档生成工具解析。

**示例**:

```python
def example_function(param1: int, param2: str) -> bool:
    """This is an example docstring.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        bool: The return value. True for success, False otherwise.
    """
    # ... function body ...
```

## 5. 错误处理

*   **明确的异常**: 避免使用 `except:` 或 `except Exception:` 这样的通用异常捕获。应捕获尽可能具体的异常。
*   **自定义异常**: 对于应用特定的错误，应定义自定义异常类，继承自 `Exception`。
*   **日志记录**: 在捕获异常时，应使用 `logging` 模块记录详细的错误信息，包括堆栈跟踪。

## 6. 测试

*   **Pytest**: 使用 `pytest` 作为测试框架。
*   **测试覆盖率**: 所有新功能都必须有相应的单元测试和集成测试。核心逻辑应力求高测试覆盖率。
*   **测试文件命名**: 测试文件应以 `test_` 开头，例如 `test_role_manager.py`。

## 7. CI/CD

*   **Pre-commit**: 项目已配置 `pre-commit`，在每次提交时会自动运行 `black`, `pylint`, `mypy` 等检查。
*   **持续集成**: （待定）未来将集成 GitHub Actions 或类似工具，在每次推送或拉取请求时运行完整的测试套件。
