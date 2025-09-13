"""
基础工具集模块初始化文件

提供基础工具集的统一接口和注册功能。
"""

from .core import (
    # 文档读写工具
    read_document,
    write_document,
    
    # 目录管理工具
    create_directory,
    create_directory_tree,
    
    # 学术搜索工具
    search_academic_papers,
    download_paper,
    
    # 文档转换工具
    convert_document_format,
    batch_convert_documents,
    
    # 代码生成工具
    generate_python_script,
    
    # 角色创建工具
    create_interactive_role,
    save_role_configuration,
    list_available_roles,
    
    # 工具注册和检查
    register_basic_tools,
    check_dependencies,
    get_tool_info,
    
    # 异常类
    ToolError,
    FileNotFoundError,
    PermissionError,
    ValidationError,
    DependencyError,
)

__version__ = "1.0.0"
__author__ = "DAIP-LIVE Team"

# 所有可用工具的列表
AVAILABLE_TOOLS = [
    "read_document",
    "write_document", 
    "create_directory",
    "create_directory_tree",
    "search_academic_papers",
    "download_paper",
    "convert_document_format",
    "batch_convert_documents",
    "generate_python_script",
    "create_interactive_role",
    "save_role_configuration",
    "list_available_roles",
]

# 支持的文档格式
SUPPORTED_READ_FORMATS = [
    ".txt", ".md", ".yaml", ".yml", ".json", ".xml", ".csv", ".log", 
    ".pdf", ".docx", ".rtf"
]

SUPPORTED_WRITE_FORMATS = [
    ".txt", ".md", ".yaml", ".yml", ".json", ".xml", ".csv", ".log", ".rtf"
]

def get_supported_formats() -> dict:
    """获取支持的文档格式信息"""
    return {
        "read": SUPPORTED_READ_FORMATS,
        "write": SUPPORTED_WRITE_FORMATS,
        "convert": [
            ("markdown", "docx"),
            ("markdown", "pdf"), 
            ("docx", "pdf"),
            ("docx", "markdown"),
        ]
    }

def get_tool_documentation(tool_name: str) -> str:
    """获取工具的文档说明"""
    tool_map = {
        "read_document": read_document.__doc__,
        "write_document": write_document.__doc__,
        "create_directory": create_directory.__doc__,
        "create_directory_tree": create_directory_tree.__doc__,
        "search_academic_papers": search_academic_papers.__doc__,
        "download_paper": download_paper.__doc__,
        "convert_document_format": convert_document_format.__doc__,
        "batch_convert_documents": batch_convert_documents.__doc__,
        "generate_python_script": generate_python_script.__doc__,
        "create_interactive_role": create_interactive_role.__doc__,
        "save_role_configuration": save_role_configuration.__doc__,
        "list_available_roles": list_available_roles.__doc__,
    }
    
    return tool_map.get(tool_name, f"Tool '{tool_name}' not found or has no documentation.")

def auto_register_tools(tool_manager) -> None:
    """
    自动注册所有基础工具到ToolManager
    
    这是推荐的注册方式，会自动处理依赖检查和错误处理
    
    Args:
        tool_manager: ToolManager实例
    """
    try:
        # 检查依赖状态
        deps = check_dependencies()
        missing_deps = [dep for dep, status in deps.items() if not status]
        
        if missing_deps:
            print(f"Warning: Missing optional dependencies: {', '.join(missing_deps)}")
            print("Some tools may not function properly without these dependencies.")
        
        # 注册工具
        register_basic_tools(tool_manager)
        print(f"Successfully registered {len(AVAILABLE_TOOLS)} basic tools")
        
    except Exception as e:
        print(f"Error during tool registration: {e}")
        raise

def get_tool_categories() -> dict:
    """获取工具分类信息"""
    return {
        "Document Operations": [
            "read_document",
            "write_document",
        ],
        "Directory Management": [
            "create_directory", 
            "create_directory_tree",
        ],
        "Academic Research": [
            "search_academic_papers",
            "download_paper",
        ],
        "Document Conversion": [
            "convert_document_format",
            "batch_convert_documents",
        ],
        "Code Generation": [
            "generate_python_script",
        ],
        "Role Management": [
            "create_interactive_role",
            "save_role_configuration", 
            "list_available_roles",
        ],
    }

__all__ = [
    # 工具函数
    "read_document",
    "write_document",
    "create_directory", 
    "create_directory_tree",
    "search_academic_papers",
    "download_paper",
    "convert_document_format",
    "batch_convert_documents",
    "generate_python_script",
    "create_interactive_role",
    "save_role_configuration",
    "list_available_roles",
    
    # 注册和检查函数
    "register_basic_tools",
    "check_dependencies",
    "get_tool_info",
    "auto_register_tools",
    
    # 异常类
    "ToolError",
    "FileNotFoundError", 
    "PermissionError",
    "ValidationError",
    "DependencyError",
    
    # 常量和信息
    "AVAILABLE_TOOLS",
    "SUPPORTED_READ_FORMATS",
    "SUPPORTED_WRITE_FORMATS",
    "get_supported_formats",
    "get_tool_documentation",
    "get_tool_categories",
]

# 模块级别的初始化检查
def _check_module_compatibility():
    """检查模块兼容性和依赖"""
    import sys
    import platform
    
    issues = []
    
    # Python版本检查
    if sys.version_info < (3, 8):
        issues.append("Python 3.8 or higher is required")
    
    # 平台特定检查
    if platform.system() == "Windows":
        # Windows平台可能有路径长度限制等问题
        pass
    
    return issues

# 在模块导入时执行兼容性检查
compatibility_issues = _check_module_compatibility()
if compatibility_issues:
    import warnings
    warnings.warn(
        f"Basic tools module compatibility issues: {'; '.join(compatibility_issues)}",
        RuntimeWarning,
        stacklevel=2
    )