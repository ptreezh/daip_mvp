"""
基础工具集实现

基于TDD方法实现的基础文件操作和文档处理工具集。
遵循SOLID、KISS、YAGNI设计原则，提供可靠、安全的工具功能。
"""

import os
import shutil
import yaml
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse
import subprocess
import asyncio

from daip_live.p4_role_manager_tools.tools import tool
from daip_live.core.exceptions import DAIPError


class ToolError(DAIPError):
    """基础工具错误基类"""
    pass


class FileNotFoundError(ToolError):
    """文件未找到错误"""
    pass


class PermissionError(ToolError):
    """权限错误"""
    pass


class ValidationError(ToolError):
    """验证错误"""
    pass


class DependencyError(ToolError):
    """依赖错误"""
    pass


# ============================================================================
# 文档读写工具集
# ============================================================================

@tool(tool_type="read", resource_arg="file_path")
def read_document(
    file_path: str, 
    encoding: str = "utf-8"
) -> str:
    """
    安全地读取文档内容，支持多种格式
    
    支持格式：
    - 文本格式：txt, md, yaml, json, xml, csv, log, rtf
    - 文档格式：pdf (文本提取), docx (文本提取)
    
    Args:
        file_path: 文档路径
        encoding: 文件编码，默认utf-8
    
    Returns:
        文档内容的字符串表示
    
    Raises:
        FileNotFoundError: 文件不存在
        PermissionError: 没有读取权限
        ValidationError: 路径验证失败
        DependencyError: 必要依赖未安装
    """
    # 路径安全验证
    if not _is_safe_path(file_path):
        raise ValidationError(f"Unsafe file path: {file_path}")
    
    path = Path(file_path)
    
    # 检查文件是否存在
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")
    
    # 根据文件扩展名确定处理方式
    file_ext = path.suffix.lower()
    
    try:
        # PDF文件处理
        if file_ext == ".pdf":
            return _extract_pdf_text(path)
        
        # DOCX文件处理
        elif file_ext == ".docx":
            return _extract_docx_text(path)
        
        # RTF文件处理
        elif file_ext == ".rtf":
            return _extract_rtf_text(path)
        
        # 文本文件处理
        else:
            # 先尝试指定编码
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                # 如果失败，尝试其他常见编码
                encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'utf-16']
                for alt_encoding in encodings_to_try:
                    try:
                        return path.read_text(encoding=alt_encoding)
                    except UnicodeDecodeError:
                        continue
                
                # 所有编码都失败
                raise ValidationError(f"Cannot decode file with any supported encoding: {file_path}")
    
    except PermissionError:
        raise PermissionError(f"No permission to read file: {file_path}")
    except Exception as e:
        raise ToolError(f"Error reading file {file_path}: {str(e)}")


@tool(tool_type="write", resource_arg="file_path")
def write_document(
    file_path: str, 
    content: str, 
    encoding: str = "utf-8", 
    mode: str = "overwrite"
) -> str:
    """
    安全地写入文档内容，支持多种文本格式
    
    支持格式：
    - 文本格式：txt, md, yaml, json, xml, csv, log, rtf
    
    Args:
        file_path: 目标文件路径
        content: 要写入的内容
        encoding: 文件编码，默认utf-8
        mode: 写入模式，overwrite/append，默认overwrite
    
    Returns:
        操作结果确认信息
    
    Raises:
        PermissionError: 没有写入权限
        ValidationError: 路径验证失败或参数无效
        ToolError: 其他工具错误
    """
    # 路径安全验证
    if not _is_safe_path(file_path):
        raise ValidationError(f"Unsafe file path: {file_path}")
    
    # 参数验证
    if mode not in ["overwrite", "append"]:
        raise ValidationError(f"Invalid mode: {mode}. Must be 'overwrite' or 'append'")
    
    if content is None:
        raise ValidationError("Content cannot be None")
    
    path = Path(file_path)
    
    # 根据文件扩展名进行特殊处理
    file_ext = path.suffix.lower()
    
    # RTF文件特殊处理
    if file_ext == ".rtf":
        content = _convert_to_rtf(content)
    
    # 确保目标目录存在
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError(f"No permission to create directory: {path.parent}")
    
    # 执行写入操作
    try:
        if mode == "overwrite":
            path.write_text(content, encoding=encoding)
            operation = "overwritten"
        else:  # append
            if path.exists():
                existing_content = path.read_text(encoding=encoding)
                path.write_text(existing_content + content, encoding=encoding)
            else:
                path.write_text(content, encoding=encoding)
            operation = "appended to"
        
        return f"Successfully {operation} file: {file_path} ({len(content)} characters, format: {file_ext})"
    
    except PermissionError:
        raise PermissionError(f"No permission to write file: {file_path}")
    except Exception as e:
        raise ToolError(f"Error writing file {file_path}: {str(e)}")


# ============================================================================
# 目录管理工具集
# ============================================================================

@tool(tool_type="write", resource_arg="path")
def create_directory(path: str, parents: bool = True) -> str:
    """
    创建单个目录或嵌套目录结构
    
    Args:
        path: 目录路径
        parents: 是否创建父目录，默认True
    
    Returns:
        操作结果确认信息
    
    Raises:
        ValidationError: 路径验证失败
        PermissionError: 没有创建权限
        ToolError: 其他工具错误
    """
    # 路径安全验证
    if not _is_safe_path(path):
        raise ValidationError(f"Unsafe directory path: {path}")
    
    dir_path = Path(path)
    
    # 检查是否已存在
    if dir_path.exists():
        if dir_path.is_dir():
            return f"Directory already exists: {path}"
        else:
            raise ValidationError(f"Path exists but is not a directory: {path}")
    
    # 创建目录
    try:
        dir_path.mkdir(parents=parents, exist_ok=False)
        return f"Successfully created directory: {path}"
    except PermissionError:
        raise PermissionError(f"No permission to create directory: {path}")
    except Exception as e:
        raise ToolError(f"Error creating directory {path}: {str(e)}")


@tool(tool_type="write", resource_arg="base_path")
def create_directory_tree(structure: str, base_path: str = ".") -> str:
    """
    根据YAML/JSON描述创建复杂的目录树结构
    
    Args:
        structure: 目录结构描述（YAML/JSON格式）
        base_path: 基础路径，默认当前目录
    
    Returns:
        创建的目录和文件列表
    
    Raises:
        ValidationError: 结构描述格式错误或路径验证失败
        PermissionError: 没有操作权限
        ToolError: 其他工具错误
    """
    # 路径安全验证
    if not _is_safe_path(base_path):
        raise ValidationError(f"Unsafe base path: {base_path}")
    
    # 解析结构描述
    try:
        # 尝试YAML解析
        try:
            parsed_structure = yaml.safe_load(structure)
        except yaml.YAMLError:
            # YAML失败，尝试JSON
            try:
                parsed_structure = json.loads(structure)
            except json.JSONDecodeError:
                raise ValidationError("Structure must be valid YAML or JSON")
    except Exception as e:
        raise ValidationError(f"Error parsing structure: {str(e)}")
    
    if not isinstance(parsed_structure, dict):
        raise ValidationError("Structure must be a dictionary/object")
    
    base = Path(base_path)
    created_items = []
    
    def _create_structure(current_path: Path, structure: Any, current_path_str: str = ""):
        """递归创建目录结构"""
        if isinstance(structure, dict):
            for name, content in structure.items():
                item_path = current_path / name
                item_path_str = str(item_path)
                
                if not _is_safe_path(item_path_str):
                    raise ValidationError(f"Unsafe path in structure: {item_path_str}")
                
                if isinstance(content, dict):
                    # 创建子目录
                    item_path.mkdir(parents=True, exist_ok=True)
                    created_items.append(f"Directory: {item_path_str}")
                    _create_structure(item_path, content, item_path_str)
                elif isinstance(content, list):
                    # 创建目录并在其中创建文件
                    item_path.mkdir(parents=True, exist_ok=True)
                    created_items.append(f"Directory: {item_path_str}")
                    _create_structure(item_path, content, item_path_str)
                elif isinstance(content, str):
                    # 创建文件
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    item_path.write_text(content, encoding="utf-8")
                    created_items.append(f"File: {item_path_str}")
                elif content is None:
                    # 创建空目录
                    item_path.mkdir(parents=True, exist_ok=True)
                    created_items.append(f"Directory: {item_path_str}")
                else:
                    raise ValidationError(f"Invalid content type for {name}: {type(content)}")
        
        elif isinstance(structure, list):
            for item in structure:
                if isinstance(item, str):
                    # 在当前目录创建文件
                    item_path = current_path / item
                    item_path_str = str(item_path)
                    
                    if not _is_safe_path(item_path_str):
                        raise ValidationError(f"Unsafe file path in structure: {item_path_str}")
                    
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    item_path.touch()
                    created_items.append(f"File: {item_path_str}")
                else:
                    _create_structure(current_path, item, current_path_str)
    
    try:
        _create_structure(base, parsed_structure, str(base))
        
        return f"Successfully created directory tree at {base_path}:\n" + "\n".join(
            f"  - {item}" for item in created_items
        )
    
    except PermissionError:
        raise PermissionError(f"No permission to create directory tree at {base_path}")
    except Exception as e:
        raise ToolError(f"Error creating directory tree at {base_path}: {str(e)}")


# ============================================================================
# 学术搜索工具集
# ============================================================================

def _check_arxiv_dependency() -> bool:
    """检查arxiv依赖是否可用"""
    try:
        import arxiv
        return True
    except ImportError:
        return False


@tool(tool_type="read")
def search_academic_papers(
    query: str, 
    max_results: int = 10, 
    source: str = "arxiv"
) -> str:
    """
    根据关键词搜索学术论文
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数，默认10
        source: 搜索源，目前仅支持arxiv
    
    Returns:
        搜索结果列表
    
    Raises:
        DependencyError: arxiv依赖未安装
        ValidationError: 参数验证失败
        ToolError: 其他工具错误
    """
    # 参数验证
    if not query or not query.strip():
        raise ValidationError("Search query cannot be empty")
    
    if max_results < 1 or max_results > 100:
        raise ValidationError("max_results must be between 1 and 100")
    
    if source != "arxiv":
        raise ValidationError(f"Unsupported search source: {source}. Currently only 'arxiv' is supported.")
    
    # 检查依赖
    if not _check_arxiv_dependency():
        raise DependencyError(
            "arxiv library is not installed. Install it with: pip install arxiv"
        )
    
    try:
        import arxiv
        
        # 构建搜索
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for result in search.results():
            results.append({
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "arxiv_id": result.get_short_id(),
                "pdf_url": result.pdf_url
            })
        
        if not results:
            return f"No papers found for query: {query}"
        
        # 格式化结果
        formatted_results = [f"Found {len(results)} papers for query: {query}\n"]
        for i, paper in enumerate(results, 1):
            formatted_results.append(f"""
{i}. {paper['title']}
   Authors: {', '.join(paper['authors'])}
   Published: {paper['published']}
   arXiv ID: {paper['arxiv_id']}
   PDF: {paper['pdf_url']}
   Summary: {paper['summary'][:200]}...
""")
        
        return "\n".join(formatted_results)
    
    except Exception as e:
        raise ToolError(f"Error searching academic papers: {str(e)}")


@tool(tool_type="write", resource_arg="save_path")
def download_paper(
    paper_id: str, 
    save_path: Optional[str] = None, 
    format: str = "pdf"
) -> str:
    """
    下载学术论文到本地
    
    Args:
        paper_id: 论文ID或URL
        save_path: 保存路径，可选，默认downloads目录
        format: 下载格式，目前仅支持pdf
    
    Returns:
        下载文件路径和元数据信息
    
    Raises:
        DependencyError: arxiv依赖未安装
        ValidationError: 参数验证失败
        ToolError: 其他工具错误
    """
    # 参数验证
    if not paper_id or not paper_id.strip():
        raise ValidationError("Paper ID cannot be empty")
    
    if format != "pdf":
        raise ValidationError(f"Unsupported format: {format}. Currently only 'pdf' is supported.")
    
    # 检查依赖
    if not _check_arxiv_dependency():
        raise DependencyError(
            "arxiv library is not installed. Install it with: pip install arxiv"
        )
    
    # 解析paper_id（支持URL和ID格式）
    if paper_id.startswith("http"):
        # 从URL提取ID
        try:
            parsed = urlparse(paper_id)
            path_parts = parsed.path.split("/")
            if "arxiv.org" in parsed.netloc:
                # 处理arxiv URL格式
                if "abs" in path_parts or "pdf" in path_parts:
                    paper_id = path_parts[-1].replace(".pdf", "")
            else:
                raise ValidationError(f"Unsupported paper URL format: {paper_id}")
        except Exception:
            raise ValidationError(f"Invalid paper URL: {paper_id}")
    
    # 确定保存路径
    if not save_path:
        save_path = Path.home() / "downloads" / f"{paper_id}.pdf"
    else:
        if not _is_safe_path(save_path):
            raise ValidationError(f"Unsafe save path: {save_path}")
    
    save_path_obj = Path(save_path)
    save_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        import arxiv
        
        # 搜索论文
        search = arxiv.Search(id_list=[paper_id])
        try:
            paper = next(search.results())
        except StopIteration:
            raise ToolError(f"Paper not found with ID: {paper_id}")
        
        # 下载论文
        paper.download_pdf(dirpath=str(save_path_obj.parent), filename=save_path_obj.name)
        
        return f"""
Successfully downloaded paper:
Title: {paper.title}
Authors: {', '.join(author.name for author in paper.authors)}
Published: {paper.published.strftime("%Y-%m-%d")}
arXiv ID: {paper.get_short_id()}
Saved to: {save_path_obj.absolute()}
File size: {save_path_obj.stat().st_size} bytes
"""
    
    except Exception as e:
        raise ToolError(f"Error downloading paper {paper_id}: {str(e)}")


# ============================================================================
# 文档格式转换工具集
# ============================================================================

def _check_pandoc_dependency() -> bool:
    """检查pandoc是否可用"""
    try:
        result = subprocess.run(["pandoc", "--version"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _check_python_docx_dependency() -> bool:
    """检查python-docx依赖是否可用"""
    try:
        import docx
        return True
    except ImportError:
        return False


@tool(tool_type="read", resource_arg="source_path")
def convert_document_format(
    source_path: str, 
    target_path: str, 
    source_format: Optional[str] = None, 
    target_format: str = "markdown",
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    在不同文档格式之间转换
    
    Args:
        source_path: 源文件路径
        target_path: 目标文件路径
        source_format: 源格式（可选，自动检测）
        target_format: 目标格式
        options: 转换选项（可选）
    
    Returns:
        转换结果信息
    
    Raises:
        DependencyError: 必要依赖未安装
        ValidationError: 参数验证失败
        ToolError: 其他工具错误
    """
    # 路径安全验证
    if not _is_safe_path(source_path) or not _is_safe_path(target_path):
        raise ValidationError("Unsafe file path")
    
    # 参数验证
    source = Path(source_path)
    target = Path(target_path)
    
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    if not source.is_file():
        raise ValidationError(f"Source path is not a file: {source_path}")
    
    # 确保目标目录存在
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # 自动检测源格式
    if not source_format:
        source_format = source.suffix.lower().lstrip(".")
    
    supported_conversions = {
        ("markdown", "docx"): _check_pandoc_dependency,
        ("markdown", "pdf"): _check_pandoc_dependency,
        ("docx", "pdf"): _check_pandoc_dependency,
        ("docx", "markdown"): _check_pandoc_dependency,
    }
    
    conversion_key = (source_format, target_format)
    if conversion_key not in supported_conversions:
        raise ValidationError(
            f"Unsupported conversion: {source_format} -> {target_format}. "
            f"Supported conversions: {list(supported_conversions.keys())}"
        )
    
    # 检查依赖
    if not supported_conversions[conversion_key]():
        raise DependencyError(
            f"Required dependency not available for {source_format} -> {target_format} conversion. "
            f"Please install pandoc: https://pandoc.org/installing.html"
        )
    
    try:
        # 使用pandoc进行转换
        cmd = ["pandoc", str(source), "-o", str(target)]
        
        # 添加转换选项
        if options:
            for key, value in options.items():
                if isinstance(value, bool) and value:
                    cmd.extend([f"--{key}"])
                elif isinstance(value, str):
                    cmd.extend([f"--{key}={value}"])
        
        # 执行转换
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise ToolError(f"Pandoc conversion failed: {result.stderr}")
        
        # 验证输出文件
        if not target.exists():
            raise ToolError("Conversion succeeded but output file was not created")
        
        return f"""
Successfully converted document:
Source: {source_path} ({source_format})
Target: {target_path} ({target_format})
Output file size: {target.stat().st_size} bytes
"""
    
    except subprocess.TimeoutExpired:
        raise ToolError("Document conversion timed out (5 minutes)")
    except Exception as e:
        raise ToolError(f"Error converting document: {str(e)}")


@tool(tool_type="read", resource_arg="source_dir")
def batch_convert_documents(
    source_dir: str, 
    target_dir: str, 
    source_format: str, 
    target_format: str, 
    recursive: bool = True
) -> str:
    """
    批量转换目录中的文档
    
    Args:
        source_dir: 源目录
        target_dir: 目标目录
        source_format: 源格式
        target_format: 目标格式
        recursive: 是否递归处理子目录
    
    Returns:
        批量转换结果统计
    
    Raises:
        ValidationError: 参数验证失败
        ToolError: 其他工具错误
    """
    # 路径安全验证
    if not _is_safe_path(source_dir) or not _is_safe_path(target_dir):
        raise ValidationError("Unsafe directory path")
    
    # 参数验证
    source = Path(source_dir)
    target = Path(target_dir)
    
    if not source.exists() or not source.is_dir():
        raise ValidationError(f"Source directory not found: {source_dir}")
    
    # 查找源格式文件
    source_files = []
    pattern = f"**/*.{source_format}" if recursive else f"*.{source_format}"
    
    for file_path in source.glob(pattern):
        if file_path.is_file():
            source_files.append(file_path)
    
    if not source_files:
        return f"No {source_format} files found in {source_dir}"
    
    # 创建目标目录结构
    converted_files = []
    failed_files = []
    
    for source_file in source_files:
        try:
            # 计算相对路径并保持目录结构
            relative_path = source_file.relative_to(source)
            target_file = target / relative_path.with_suffix(f".{target_format}")
            
            # 确保目标目录存在
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 执行转换
            conversion_result = convert_document_format(
                str(source_file), 
                str(target_file), 
                source_format, 
                target_format
            )
            
            converted_files.append({
                "source": str(source_file),
                "target": str(target_file),
                "result": conversion_result
            })
            
        except Exception as e:
            failed_files.append({
                "file": str(source_file),
                "error": str(e)
            })
    
    # 生成结果报告
    report = [
        f"Batch conversion completed for {source_format} -> {target_format}",
        f"Source directory: {source_dir}",
        f"Target directory: {target_dir}",
        f"Total files found: {len(source_files)}",
        f"Successfully converted: {len(converted_files)}",
        f"Failed conversions: {len(failed_files)}"
    ]
    
    if converted_files:
        report.append("\nSuccessfully converted files:")
        for conv in converted_files[:10]:  # 显示前10个
            report.append(f"  ✓ {conv['source']} -> {conv['target']}")
        if len(converted_files) > 10:
            report.append(f"  ... and {len(converted_files) - 10} more")
    
    if failed_files:
        report.append("\nFailed conversions:")
        for fail in failed_files:
            report.append(f"  ✗ {fail['file']}: {fail['error']}")
    
    return "\n".join(report)


# ============================================================================
# Python代码生成工具
# ============================================================================

def _check_llm_dependency() -> bool:
    """检查LLM依赖是否可用"""
    try:
        from daip_live.model_provider.provider import LiteLLMProvider
        return True
    except ImportError:
        return False


@tool(tool_type="write", resource_arg="script_path")
def generate_python_script(
    description: str, 
    script_path: str, 
    template: str = "basic"
) -> str:
    """
    根据需求描述生成Python脚本
    
    Args:
        description: 功能描述
        script_path: 脚本保存路径
        template: 代码模板，basic/advanced
    
    Returns:
        生成的脚本内容和路径
    
    Raises:
        DependencyError: LLM依赖未安装
        ValidationError: 参数验证失败
        ToolError: 其他工具错误
    """
    # 参数验证
    if not description or not description.strip():
        raise ValidationError("Description cannot be empty")
    
    if not _is_safe_path(script_path):
        raise ValidationError(f"Unsafe script path: {script_path}")
    
    if template not in ["basic", "advanced"]:
        raise ValidationError(f"Unsupported template: {template}")
    
    # 检查LLM依赖
    if not _check_llm_dependency():
        raise DependencyError(
            "LLM provider is not available. Please check your configuration."
        )
    
    try:
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.container import Container
        
        # 获取LLM提供者
        container = Container()
        container.config.from_yaml("config.yaml")
        llm_provider = container.model_provider()
        
        # 构建生成提示
        prompt = f"""
Generate a Python script based on the following description:

Description: {description}

Requirements:
- Generate a complete, runnable Python script
- Include proper error handling
- Add necessary imports
- Include docstrings and comments
- Follow Python best practices
- Make the script executable
- Add a main() function and if __name__ == "__main__" block

Template level: {template}

Please provide only the Python code, no additional explanation.
"""
        
        # 生成代码
        response = llm_provider.generate(prompt)
        generated_code = response.content.strip()
        
        # 基本验证
        if not generated_code or len(generated_code) < 50:
            raise ToolError("Generated code is too short or empty")
        
        # 确保脚本路径的目录存在
        script_path_obj = Path(script_path)
        script_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入脚本
        script_path_obj.write_text(generated_code, encoding="utf-8")
        
        # 验证生成的代码语法
        try:
            compile(generated_code, script_path, "exec")
        except SyntaxError as e:
            raise ToolError(f"Generated code has syntax errors: {e}")
        
        return f"""
Successfully generated Python script:
Description: {description}
Template: {template}
Saved to: {script_path_obj.absolute()}
Code length: {len(generated_code)} characters

Generated code preview:
```python
{generated_code[:500]}{'...' if len(generated_code) > 500 else ''}
```
"""
    
    except Exception as e:
        raise ToolError(f"Error generating Python script: {str(e)}")


# ============================================================================
# 工具注册和初始化
# ============================================================================

def register_basic_tools(tool_manager) -> None:
    """
    注册所有基础工具到ToolManager
    
    Args:
        tool_manager: ToolManager实例
    """
    basic_tools = [
        read_document,
        write_document,
        create_directory,
        create_directory_tree,
        search_academic_papers,
        download_paper,
        convert_document_format,
        batch_convert_documents,
        generate_python_script,
        create_interactive_role,
        save_role_configuration,
        list_available_roles,
    ]
    
    for tool_func in basic_tools:
        try:
            tool_manager.register_tool(tool_func)
        except Exception as e:
            print(f"Warning: Failed to register tool {tool_func.__name__}: {e}")


# ============================================================================
# 文档格式处理辅助函数
# ============================================================================

def _extract_pdf_text(file_path: Path) -> str:
    """从PDF文件提取文本内容"""
    try:
        import PyPDF2
    except ImportError:
        raise DependencyError(
            "PyPDF2 library is not installed. Install it with: pip install PyPDF2"
        )
    
    try:
        text_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
        
        return "\n".join(text_content)
    
    except Exception as e:
        raise ToolError(f"Error extracting text from PDF {file_path}: {str(e)}")


def _extract_docx_text(file_path: Path) -> str:
    """从DOCX文件提取文本内容"""
    try:
        import docx
    except ImportError:
        raise DependencyError(
            "python-docx library is not installed. Install it with: pip install python-docx"
        )
    
    try:
        doc = docx.Document(file_path)
        text_content = []
        
        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)
        
        return "\n".join(text_content)
    
    except Exception as e:
        raise ToolError(f"Error extracting text from DOCX {file_path}: {str(e)}")


def _extract_rtf_text(file_path: Path) -> str:
    """从RTF文件提取文本内容"""
    try:
        from striprtf.striprtf import rtf_to_text
    except ImportError:
        raise DependencyError(
            "striprtf library is not installed. Install it with: pip install striprtf"
        )
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            rtf_content = file.read()
        
        return rtf_to_text(rtf_content)
    
    except Exception as e:
        raise ToolError(f"Error extracting text from RTF {file_path}: {str(e)}")


def _convert_to_rtf(text: str) -> str:
    """将纯文本转换为RTF格式"""
    # 简单的RTF格式转换
    rtf_header = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}"
    rtf_footer = r"}"
    
    # 转义特殊字符
    escaped_text = text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')
    escaped_text = escaped_text.replace('\n', '\\par ')
    
    return f"{rtf_header}{escaped_text}{rtf_footer}"


# ============================================================================
# 角色创建工具集
# ============================================================================

@tool(tool_type="write", resource_arg="role_name")
def create_interactive_role(
    role_name: str,
    role_description: Optional[str] = None,
    save_to_current_dir: bool = True,
    use_llm_generation: bool = False
) -> str:
    """
    交互式创建角色
    
    工作流程：
    1. 验证角色名称
    2. 获取角色描述（通过参数或交互式输入）
    3. 选择是否使用LLM生成详细角色配置
    4. 用户确认保存
    5. 保存到roles目录
    
    Args:
        role_name: 角色名称
        role_description: 角色描述（可选）
        save_to_current_dir: 是否保存到当前目录的roles文件夹，默认True
        use_llm_generation: 是否使用LLM生成详细配置，默认False
    
    Returns:
        创建结果和角色信息
    
    Raises:
        ValidationError: 参数验证失败
        ToolError: 其他工具错误
    """
    # 参数验证
    if not role_name or not role_name.strip():
        raise ValidationError("Role name cannot be empty")
    
    # 角色名称验证（只允许字母、数字、下划线）
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', role_name):
        raise ValidationError("Role name can only contain letters, numbers, and underscores")
    
    # 确定保存目录
    if save_to_current_dir:
        roles_dir = Path.cwd() / "roles"
    else:
        # 使用系统配置的角色目录
        roles_dir = Path("roles")  # 这里可以根据实际配置调整
    
    roles_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查角色是否已存在
    role_file = roles_dir / f"{role_name}.yaml"
    if role_file.exists():
        raise ValidationError(f"Role '{role_name}' already exists at {role_file}")
    
    # 如果没有提供描述，使用默认描述
    if not role_description:
        role_description = f"A specialized AI role named {role_name}"
    
    # 基础角色配置
    base_config = {
        "name": role_name,
        "persona": role_description,
        "tools": ["read_document", "write_document", "create_directory"],
        "system_prompt": f"You are {role_name}. {role_description}",
        "created_by": "interactive_creation",
        "version": "1.0.0"
    }
    
    # 如果使用LLM生成详细配置
    if use_llm_generation:
        enhanced_config = _generate_enhanced_role_config(role_name, role_description)
        final_config = {**base_config, **enhanced_config}
    else:
        final_config = base_config
    
    # 生成YAML内容
    try:
        yaml_content = yaml.dump(final_config, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise ToolError(f"Error generating YAML content: {str(e)}")
    
    return f"""
Role '{role_name}' is ready to be created:

Generated Configuration:
```yaml
{yaml_content}
```

Save location: {role_file.absolute()}
LLM Enhancement: {'Enabled' if use_llm_generation else 'Disabled'}

Please review the configuration above. If you want to proceed with saving, call the save_role_tool with:
- role_name: "{role_name}"
- config_content: the YAML content above
- confirm_save: true
"""


@tool(tool_type="write", resource_arg="role_name")
def save_role_configuration(
    role_name: str,
    config_content: str,
    confirm_save: bool = False,
    save_to_current_dir: bool = True
) -> str:
    """
    保存角色配置到文件
    
    Args:
        role_name: 角色名称
        config_content: YAML格式的配置内容
        confirm_save: 确认保存，必须为True才能执行保存
        save_to_current_dir: 是否保存到当前目录的roles文件夹
    
    Returns:
        保存结果
    
    Raises:
        ValidationError: 参数验证失败
        ToolError: 其他工具错误
    """
    # 参数验证
    if not role_name or not role_name.strip():
        raise ValidationError("Role name cannot be empty")
    
    if not config_content or not config_content.strip():
        raise ValidationError("Configuration content cannot be empty")
    
    if not confirm_save:
        raise ValidationError("confirm_save must be True to save the role")
    
    # 验证YAML格式
    try:
        parsed_config = yaml.safe_load(config_content)
        if not isinstance(parsed_config, dict):
            raise ValidationError("Configuration must be a valid YAML dictionary")
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML configuration: {str(e)}")
    
    # 确定保存目录
    if save_to_current_dir:
        roles_dir = Path.cwd() / "roles"
    else:
        roles_dir = Path("roles")
    
    roles_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    role_file = roles_dir / f"{role_name}.yaml"
    
    try:
        role_file.write_text(config_content, encoding="utf-8")
        
        return f"""
Successfully saved role '{role_name}':
- File: {role_file.absolute()}
- Size: {len(config_content)} characters
- Configuration keys: {list(parsed_config.keys())}

The role is now available for use in the system.
"""
    
    except Exception as e:
        raise ToolError(f"Error saving role configuration: {str(e)}")


@tool(tool_type="read")
def list_available_roles(directory: str = "roles") -> str:
    """
    列出可用的角色
    
    Args:
        directory: 角色目录路径，默认为"roles"
    
    Returns:
        可用角色列表
    """
    roles_path = Path(directory)
    
    if not roles_path.exists():
        return f"No roles directory found at {roles_path.absolute()}"
    
    role_files = list(roles_path.glob("*.yaml"))
    
    if not role_files:
        return f"No role files found in {roles_path.absolute()}"
    
    role_info = []
    for role_file in sorted(role_files):
        try:
            with open(role_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            role_name = config.get('name', role_file.stem)
            role_persona = config.get('persona', 'No description available')
            
            # 截断过长的描述
            if len(role_persona) > 100:
                role_persona = role_persona[:100] + "..."
            
            role_info.append(f"- {role_name}: {role_persona}")
        
        except Exception as e:
            role_info.append(f"- {role_file.stem}: [Error loading: {str(e)}]")
    
    return f"""
Available roles in {roles_path.absolute()}:
{chr(10).join(role_info)}

Total: {len(role_files)} roles found.
"""


# ============================================================================
# 辅助函数
# ============================================================================

def _generate_enhanced_role_config(role_name: str, description: str) -> Dict[str, Any]:
    """使用LLM生成增强的角色配置"""
    try:
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.container import Container
        
        # 获取LLM提供者
        container = Container()
        container.config.from_yaml("config.yaml")
        llm_provider = container.model_provider()
        
        prompt = f"""
Generate a detailed AI role configuration based on the following information:

Role Name: {role_name}
Description: {description}

Please generate a comprehensive role configuration in YAML format that includes:
1. A detailed persona (3-5 sentences describing the role's character and expertise)
2. A system prompt that defines how the role should behave
3. Appropriate tools for this role (choose from: read_document, write_document, create_directory, 
   create_directory_tree, search_academic_papers, download_paper, convert_document_format, 
   batch_convert_documents, generate_python_script)
4. Configuration parameters like temperature, max_tokens if relevant
5. Any additional metadata that would be helpful

Provide only the YAML content, no explanations.
"""
        
        response = llm_provider.generate(prompt)
        yaml_content = response.content.strip()
        
        # 解析生成的YAML
        try:
            enhanced_config = yaml.safe_load(yaml_content)
            if isinstance(enhanced_config, dict):
                return enhanced_config
            else:
                # 如果生成的内容不是字典，返回基本增强
                return {
                    "enhanced_persona": yaml_content,
                    "generation_method": "llm_freeform",
                    "tools": ["read_document", "write_document", "create_directory"]
                }
        except yaml.YAMLError:
            # YAML解析失败，返回基本增强
            return {
                "enhanced_persona": yaml_content,
                "generation_method": "llm_freeform",
                "tools": ["read_document", "write_document", "create_directory"]
            }
    
    except Exception as e:
        # LLM生成失败，返回基本配置
        return {
            "generation_error": str(e),
            "generation_method": "fallback",
            "enhanced_persona": f"An AI assistant specializing in {description}",
            "tools": ["read_document", "write_document", "create_directory"]
        }


def _is_safe_path(path: str) -> bool:
    """
    检查路径是否安全（防止路径遍历攻击）
    
    Args:
        path: 要检查的路径
    
    Returns:
        路径是否安全
    """
    try:
        resolved_path = Path(path).resolve()
        
        # 检查路径中是否包含可疑的组件
        path_str = str(resolved_path)
        suspicious_patterns = ["..", "~", "$", "null", "/dev", "/proc"]
        
        for pattern in suspicious_patterns:
            if pattern in path_str:
                return False
        
        # 确保路径不指向系统目录
        system_dirs = ["/etc", "/bin", "/sbin", "/usr/bin", "/usr/sbin", "/System"]
        for system_dir in system_dirs:
            if path_str.startswith(system_dir):
                return False
        
        return True
    
    except (OSError, ValueError):
        return False


def get_tool_info(tool_func) -> Dict[str, Any]:
    """
    获取工具信息
    
    Args:
        tool_func: 工具函数
    
    Returns:
        工具信息字典
    """
    return {
        "name": tool_func.__name__,
        "description": tool_func.__doc__ or "",
        "type": getattr(tool_func, "tool_type", "unknown"),
        "resource_arg": getattr(tool_func, "resource_arg", None),
        "input_schema": getattr(tool_func, "input_schema", None),
    }


def check_dependencies() -> Dict[str, bool]:
    """
    检查所有外部依赖的可用性
    
    Returns:
        依赖状态字典
    """
    return {
        "arxiv": _check_arxiv_dependency(),
        "pandoc": _check_pandoc_dependency(),
        "python-docx": _check_python_docx_dependency(),
        "llm_provider": _check_llm_dependency(),
        "pypdf2": _check_pypdf2_dependency(),
        "striprtf": _check_striprtf_dependency(),
    }


def _check_pypdf2_dependency() -> bool:
    """检查PyPDF2依赖是否可用"""
    try:
        import PyPDF2
        return True
    except ImportError:
        return False


def _check_striprtf_dependency() -> bool:
    """检查striprtf依赖是否可用"""
    try:
        from striprtf.striprtf import rtf_to_text
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    # 可以直接运行进行基本测试
    print("Basic Tools Module")
    print("Available tools:")
    
    tools_info = [
        read_document,
        write_document,
        create_directory,
        create_directory_tree,
        search_academic_papers,
        download_paper,
        convert_document_format,
        batch_convert_documents,
        generate_python_script,
    ]
    
    for tool_func in tools_info:
        info = get_tool_info(tool_func)
        print(f"  - {info['name']}: {info['description'][:60]}...")
    
    print("\nDependency status:")
    deps = check_dependencies()
    for dep, status in deps.items():
        print(f"  - {dep}: {'✓' if status else '✗'}")