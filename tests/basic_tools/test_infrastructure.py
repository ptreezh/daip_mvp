"""
基础工具集测试配置和辅助工具

提供测试基础设施、Mock对象和测试数据生成功能。
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
import json

from daip_live.core.models import SessionContext, ToolPermissionConfig
from daip_live.p4_role_manager_tools.tool_manager import ToolManager


class TestDirectoryManager:
    """测试目录管理器"""
    
    def __init__(self):
        self.temp_dir = None
        self.test_files = []
    
    def __enter__(self):
        """上下文管理器入口"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="daip_test_"))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, content: str, filename: str, encoding: str = "utf-8") -> Path:
        """创建测试文件"""
        file_path = self.temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding=encoding)
        self.test_files.append(file_path)
        return file_path
    
    def create_test_directory(self, dirname: str) -> Path:
        """创建测试目录"""
        dir_path = self.temp_dir / dirname
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    def create_complex_structure(self, structure_dict: Dict[str, Any]) -> Path:
        """根据字典创建复杂的文件结构"""
        base_path = self.temp_dir
        
        def _create_structure(current_path: Path, structure: Any):
            if isinstance(structure, dict):
                for name, content in structure.items():
                    item_path = current_path / name
                    if isinstance(content, dict):
                        item_path.mkdir(parents=True, exist_ok=True)
                        _create_structure(item_path, content)
                    elif isinstance(content, list):
                        item_path.mkdir(parents=True, exist_ok=True)
                        for item in content:
                            if isinstance(item, str):
                                (item_path / item).touch()
                            else:
                                _create_structure(item_path, item)
                    else:
                        item_path.write_text(str(content), encoding="utf-8")
                        self.test_files.append(item_path)
            elif isinstance(structure, list):
                for item in structure:
                    if isinstance(item, str):
                        (current_path / item).touch()
                        self.test_files.append(current_path / item)
        
        _create_structure(base_path, structure_dict)
        return base_path
    
    def get_path(self, *path_parts) -> Path:
        """获取测试路径"""
        return self.temp_dir / Path(*path_parts)


class MockDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_test_documents() -> Dict[str, str]:
        """生成测试文档内容"""
        return {
            "simple_text": "This is a simple test document.\nIt has multiple lines.\nAnd some basic content.",
            "markdown_doc": """# Test Markdown Document

## Section 1
This is a test markdown document with **bold** and *italic* text.

## Section 2  
- List item 1
- List item 2
- List item 3

```python
def test_function():
    return "Hello, World!"
```
""",
            "json_data": json.dumps({
                "name": "Test Project",
                "version": "1.0.0",
                "dependencies": ["pytest", "requests"],
                "config": {
                    "debug": True,
                    "port": 8080
                }
            }, indent=2),
            "yaml_config": """
project:
  name: Test Project
  version: 1.0.0
  
settings:
  debug: true
  timeout: 30
  
dependencies:
  - pytest>=6.0.0
  - requests>=2.25.0
""",
            "python_script": '''#!/usr/bin/env python3
"""
Test Python script generated for testing purposes.
"""

import sys
import os

def main():
    """Main function."""
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
        }
    
    @staticmethod
    def generate_directory_structures() -> Dict[str, Dict]:
        """生成目录结构模板"""
        return {
            "python_project": {
                "src": {
                    "package_name": {
                        "__init__.py": "",
                        "main.py": "def main():\n    pass\n",
                        "utils": {
                            "__init__.py": "",
                            "helpers.py": "def helper():\n    pass\n"
                        }
                    }
                },
                "tests": {
                    "__init__.py": "",
                    "test_main.py": "def test_main():\n    assert True\n"
                },
                "docs": {
                    "README.md": "# Test Project\n\nThis is a test project.\n",
                    "API.md": "# API Documentation\n"
                },
                "requirements.txt": "pytest>=6.0.0\nrequests>=2.25.0\n",
                "setup.py": "from setuptools import setup\n\nsetup(\n    name=\"test_project\",\n    version=\"1.0.0\"\n)\n"
            },
            "web_project": {
                "frontend": {
                    "src": {
                        "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Test</title>\n</head>\n<body>\n    <h1>Test Page</h1>\n</body>\n</html>",
                        "css": {
                            "style.css": "body { font-family: Arial; }\n"
                        },
                        "js": {
                            "app.js": "console.log('Hello, World!');\n"
                        }
                    }
                },
                "backend": {
                    "app.py": "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Hello, World!'\n",
                    "requirements.txt": "Flask>=2.0.0\n"
                }
            },
            "research_project": {
                "literature": {
                    "papers": {
                        "paper1.md": "# Paper 1\n\nAbstract...\n",
                        "paper2.md": "# Paper 2\n\nAbstract...\n"
                    },
                    "notes": {
                        "summary.md": "# Literature Summary\n\nKey findings...\n"
                    }
                },
                "data": {
                    "raw": {},
                    "processed": {}
                },
                "analysis": {
                    "notebook.ipynb": '{"cells": []}',
                    "script.py": "import pandas as pd\n\ndef analyze_data():\n    pass\n"
                },
                "report": {
                    "draft.md": "# Research Report\n\nIntroduction...\n",
                    "final.md": "# Final Report\n\nFindings...\n"
                }
            }
        }
    
    @staticmethod
    def generate_mock_academic_results() -> List[Dict[str, Any]]:
        """生成模拟学术搜索结果"""
        return [
            {
                "title": "Test Paper 1: Machine Learning Applications",
                "authors": ["John Doe", "Jane Smith"],
                "summary": "This paper explores various applications of machine learning in real-world scenarios...",
                "published": "2023-01-15",
                "arxiv_id": "2301.12345",
                "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf"
            },
            {
                "title": "Test Paper 2: Natural Language Processing Advances", 
                "authors": ["Alice Johnson", "Bob Brown"],
                "summary": "Recent advances in natural language processing have revolutionized text analysis...",
                "published": "2023-02-20",
                "arxiv_id": "2302.67890",
                "pdf_url": "https://arxiv.org/pdf/2302.67890.pdf"
            },
            {
                "title": "Test Paper 3: Computer Vision Techniques",
                "authors": ["Charlie Wilson", "Diana Davis"],
                "summary": "This paper presents novel computer vision techniques for object detection...",
                "published": "2023-03-10",
                "arxiv_id": "2303.54321",
                "pdf_url": "https://arxiv.org/pdf/2303.54321.pdf"
            }
        ]


class MockExternalServices:
    """外部服务Mock对象"""
    
    @staticmethod
    def create_mock_arxiv_client():
        """创建模拟的arxiv客户端"""
        mock_client = Mock()
        
        # 模拟搜索结果
        mock_search = Mock()
        mock_results = [
            Mock(
                title="Test Paper 1",
                summary="Test summary 1",
                authors=[Mock(name="John Doe")],
                published="2023-01-01",
                entry_id="http://arxiv.org/abs/2301.00001",
                pdf_url="https://arxiv.org/pdf/2301.00001.pdf"
            )
        ]
        mock_search.results.return_value = mock_results
        mock_client.query.return_value = mock_search
        
        return mock_client
    
    @staticmethod
    def create_mock_llm_provider():
        """创建模拟的LLM提供商"""
        mock_provider = Mock()
        mock_response = Mock()
        mock_response.content = '''#!/usr/bin/env python3
"""
Generated test script
"""

def main():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    main()
'''
        mock_provider.generate.return_value = mock_response
        
        return mock_provider
    
    @staticmethod
    def create_mock_pandoc_process():
        """创建模拟的pandoc进程"""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Conversion successful"
        mock_process.stderr = ""
        return mock_process


class ToolTestHarness:
    """工具测试工具类"""
    
    def __init__(self):
        self.tool_manager = ToolManager()
        self.tool_manager.tool_permission_config = ToolPermissionConfig(default="allow")
        self.session_context = SessionContext()
    
    def register_test_tool(self, tool_func):
        """注册测试工具"""
        self.tool_manager.register_tool(tool_func)
        return tool_func
    
    def execute_tool_safely(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """安全执行工具并返回结果"""
        result = {
            "success": False,
            "result": None,
            "error": None,
            "execution_time": None
        }
        
        import time
        start_time = time.time()
        
        try:
            output = self.tool_manager.execute_tool(
                tool_name, 
                args, 
                self.session_context
            )
            result["success"] = True
            result["result"] = output
        except Exception as e:
            result["error"] = str(e)
            result["error_type"] = type(e).__name__
        finally:
            result["execution_time"] = time.time() - start_time
        
        return result
    
    def assert_tool_success(self, execution_result: Dict[str, Any]):
        """断言工具执行成功"""
        assert execution_result["success"], f"Tool execution failed: {execution_result['error']}"
        assert execution_result["error"] is None
    
    def assert_tool_error(self, execution_result: Dict[str, Any], expected_error_type: str = None):
        """断言工具执行失败"""
        assert not execution_result["success"], "Tool execution should have failed but succeeded"
        assert execution_result["error"] is not None
        
        if expected_error_type:
            assert execution_result["error_type"] == expected_error_type, \
                f"Expected error type {expected_error_type}, got {execution_result['error_type']}"
    
    def measure_performance(self, tool_name: str, args: Dict[str, Any], iterations: int = 10) -> Dict[str, float]:
        """测量工具性能"""
        import time
        
        times = []
        memory_usage = []
        
        for _ in range(iterations):
            start_time = time.time()
            result = self.execute_tool_safely(tool_name, args)
            end_time = time.time()
            
            times.append(end_time - start_time)
            # 注意：实际项目中应该使用memory_profiler等工具测量内存
        
        return {
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times),
            "iterations": iterations
        }


# 测试固件
@pytest.fixture
def test_dir_manager():
    """测试目录管理器固件"""
    with TestDirectoryManager() as manager:
        yield manager


@pytest.fixture
def mock_data_generator():
    """测试数据生成器固件"""
    return MockDataGenerator()


@pytest.fixture
def tool_test_harness():
    """工具测试工具固件"""
    return ToolTestHarness()


@pytest.fixture
def sample_documents(mock_data_generator):
    """示例文档固件"""
    return mock_data_generator.generate_test_documents()


@pytest.fixture
def sample_structures(mock_data_generator):
    """示例目录结构固件"""
    return mock_data_generator.generate_directory_structures()


@pytest.fixture
def mock_academic_results():
    """模拟学术结果固件"""
    return MockDataGenerator.generate_mock_academic_results()


# 自定义断言函数
def assert_file_exists(file_path: Path, message: str = None):
    """断言文件存在"""
    assert file_path.exists(), message or f"File should exist: {file_path}"


def assert_file_content(file_path: Path, expected_content: str, encoding: str = "utf-8"):
    """断言文件内容匹配"""
    assert_file_exists(file_path)
    actual_content = file_path.read_text(encoding=encoding)
    assert actual_content == expected_content, \
        f"File content mismatch. Expected: {expected_content!r}, Got: {actual_content!r}"


def assert_directory_exists(dir_path: Path, message: str = None):
    """断言目录存在"""
    assert dir_path.exists() and dir_path.is_dir(), \
        message or f"Directory should exist: {dir_path}"


def assert_directory_structure(base_path: Path, expected_structure: Dict[str, Any]):
    """断言目录结构匹配"""
    assert_directory_exists(base_path)
    
    def _check_structure(current_path: Path, structure: Any):
        if isinstance(structure, dict):
            for name, content in structure.items():
                item_path = current_path / name
                if isinstance(content, dict):
                    assert_directory_exists(item_path)
                    _check_structure(item_path, content)
                elif isinstance(content, str):
                    assert_file_exists(item_path)
                    actual_content = item_path.read_text(encoding="utf-8")
                    assert actual_content == content, \
                        f"Content mismatch in {item_path}"
                elif content is None:
                    assert_directory_exists(item_path)
        elif isinstance(structure, list):
            for item in structure:
                if isinstance(item, str):
                    assert_file_exists(current_path / item)
    
    _check_structure(base_path, expected_structure)


# 性能测试装饰器
def performance_test(max_execution_time: float = None, max_memory_mb: float = None):
    """性能测试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            import psutil
            import os
            
            # 记录开始时间和内存
            start_time = time.time()
            process = psutil.Process(os.getpid())
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行测试
            result = func(*args, **kwargs)
            
            # 记录结束时间和内存
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            execution_time = end_time - start_time
            memory_increase = end_memory - start_memory
            
            # 性能断言
            if max_execution_time:
                assert execution_time <= max_execution_time, \
                    f"Execution time {execution_time:.3f}s exceeds maximum {max_execution_time}s"
            
            if max_memory_mb:
                assert memory_increase <= max_memory_mb, \
                    f"Memory increase {memory_increase:.2f}MB exceeds maximum {max_memory_mb}MB"
            
            # 返回结果和性能数据
            return {
                "result": result,
                "execution_time": execution_time,
                "memory_increase_mb": memory_increase
            }
        
        return wrapper
    return decorator


# 测试数据验证器
class TestDataValidator:
    """测试数据验证器"""
    
    @staticmethod
    def is_valid_yaml(content: str) -> bool:
        """验证YAML格式"""
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError:
            return False
    
    @staticmethod
    def is_valid_json(content: str) -> bool:
        """验证JSON格式"""
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False
    
    @staticmethod
    def is_valid_python_code(content: str) -> bool:
        """验证Python代码语法"""
        try:
            compile(content, "<string>", "exec")
            return True
        except SyntaxError:
            return False
    
    @staticmethod
    def is_safe_path(path: Path, base_path: Path) -> bool:
        """验证路径安全性（防止路径遍历攻击）"""
        try:
            resolved_path = path.resolve()
            resolved_base = base_path.resolve()
            return str(resolved_path).startswith(str(resolved_base))
        except (OSError, ValueError):
            return False


if __name__ == "__main__":
    # 可以运行一些基本的验证测试
    print("Testing test infrastructure...")
    
    # 测试目录管理器
    with TestDirectoryManager() as manager:
        test_file = manager.create_test_file("Hello, World!", "test.txt")
        print(f"Created test file: {test_file}")
        assert test_file.exists()
        assert test_file.read_text() == "Hello, World!"
    
    # 测试数据生成器
    generator = MockDataGenerator()
    documents = generator.generate_test_documents()
    print(f"Generated {len(documents)} test documents")
    
    # 测试数据验证器
    yaml_content = "test: value"
    assert TestDataValidator.is_valid_yaml(yaml_content)
    
    json_content = '{"test": "value"}'
    assert TestDataValidator.is_valid_json(json_content)
    
    python_content = "print('Hello, World!')"
    assert TestDataValidator.is_valid_python_code(python_content)
    
    print("All infrastructure tests passed!")