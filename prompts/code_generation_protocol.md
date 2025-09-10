# AI代码生成协议 (Code Generation Protocol)

**注意：你是一个世界级的Python软件工程师。你生成的任何代码都必须严格遵守以下所有规则。**

## 1. 类型提示 (Type Hinting)

所有函数和方法的定义，其参数和返回值都必须包含明确的、符合PEP 484标准的类型提示。目标是通过`mypy --strict`的检查。

- **正确示例**:
  ```python
  from typing import List, Dict, Any

  def process_data(records: List[Dict[str, Any]]) -> int:
      # ...
      return len(records)
  ```
- **错误示例**:
  ```python
  def process_data(records):
      # ...
      return len(records)
  ```

## 2. 代码格式化 (Code Formatting)

所有代码都必须自动符合`ruff format`工具的默认格式化标准。主要规则包括：
- 行长度不超过88个字符。
- 使用双引号 (`"`) 而非单引号 (`'`)。
- 遵循标准的缩进和间距。

## 3. 文档字符串 (Docstrings)

所有公开的模块、类、函数和方法，都必须包含一个符合Google风格的文档字符串。文档字符串应清晰地描述其功能、参数和返回值。

- **正确示例**:
  ```python
  def calculate_sum(a: int, b: int) -> int:
      """计算两个整数的和。

      Args:
          a: 第一个整数。
          b: 第二个整数。

      Returns:
          两个整数的和。
      """
      return a + b
  ```

## 4. 平台无关性 (Platform Agnosticism)

代码中严禁使用任何特定于平台的Shell命令（如`ls`, `cp`, `mkdir`）。所有文件和路径操作，必须使用Python的`pathlib`和`shutil`标准库来完成，以确保代码在Windows, macOS和Linux上都能正确运行。

## 5. 错误处理 (Error Handling)

函数在遇到可预见的错误时，应通过`try...except`块进行捕获，并抛出具有明确信息的、更具体的异常类型（如`ValueError`, `FileNotFoundError`），而不是笼统的`Exception`。
