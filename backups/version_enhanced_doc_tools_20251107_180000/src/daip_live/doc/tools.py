import os
import sys
import time
import json
import subprocess
import platform
import tempfile
import logging
import uuid
import threading
import queue
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Union, Set
from shutil import which
from enum import Enum


def _papers_dir() -> Path:
    d = Path(os.getcwd())/"docs"/"papers"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download_arxiv(query: str, max_n: int = 1) -> int:
    return 0


def fetch_arxiv(query: str, max_n: int = 1) -> int:
    return _download_arxiv(query, max_n=max_n)


def _has_pandoc() -> bool:
    return which("pandoc") is not None


class ConversionStatus(Enum):
    """转换状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConversionPriority(Enum):
    """转换优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class ConversionError(Exception):
    """转换错误异常类"""
    pass


class ConversionQueueFull(Exception):
    """转换队列满异常"""
    pass


@dataclass
class ConversionResult:
    """转换结果数据类"""
    success: bool
    source_file: str
    output_file: str
    format: str
    error_message: Optional[str] = None
    conversion_time: Optional[float] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    task_id: Optional[str] = None
    pages_count: Optional[int] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @property
    def has_warnings(self) -> bool:
        """是否有警告"""
        return len(self.warnings) > 0


@dataclass
class ConversionTask:
    """转换任务数据类"""
    task_id: str
    source_file: str
    output_file: str
    format: str
    options: Dict[str, Any] = field(default_factory=dict)
    priority: ConversionPriority = ConversionPriority.NORMAL
    status: ConversionStatus = ConversionStatus.PENDING
    progress: float = 0.0
    progress_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional['ConversionResult'] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换枚举和日期时间
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        if self.result:
            data['result'] = asdict(self.result)
        return data


class FormatConverter:
    """格式转换器

    提供Markdown到多种格式的转换功能，支持Pandoc集成和错误处理。
    高级功能：异步转换、任务队列、转换历史、性能监控等。
    """

    def __init__(self, max_queue_size: int = 100, max_workers: int = 2):
        """初始化格式转换器"""
        self.pandoc_available = self.check_pandoc_availability()
        self.supported_formats = self._get_supported_formats()
        self.platform = self._detect_platform()
        self.max_queue_size = max_queue_size
        self.max_workers = max_workers

        # 转换统计
        self.conversion_stats = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "total_conversion_time": 0.0,
            "average_queue_time": 0.0,
            "peak_memory_usage": 0.0
        }

        # 任务队列和管理
        self.task_queue = queue.PriorityQueue(maxsize=max_queue_size)
        self.active_tasks: Dict[str, ConversionTask] = {}
        self.completed_tasks: List[ConversionTask] = []
        self.task_history: List[ConversionResult] = []
        self.max_history_size = 1000

        # 异步处理
        self.worker_threads: List[threading.Thread] = []
        self.is_running = False
        self._lock = threading.RLock()

        # 性能监控
        self.performance_metrics = {
            "conversions_per_minute": 0.0,
            "average_conversion_time": 0.0,
            "success_rate": 0.0,
            "queue_utilization": 0.0
        }

        # 设置日志
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # 启动工作线程
        self.start_workers()

    def check_pandoc_availability(self) -> bool:
        """检查Pandoc是否可用"""
        return _has_pandoc()

    def _get_supported_formats(self) -> List[str]:
        """获取支持的格式列表"""
        if self.pandoc_available:
            return ["pdf", "docx", "html", "txt", "rtf", "odt"]
        else:
            # 基本格式支持（不需要Pandoc）
            return ["html", "txt"]

    def _detect_platform(self) -> str:
        """检测当前平台"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "darwin"
        else:
            return "other"

    def is_format_supported(self, format_name: str) -> bool:
        """检查格式是否支持"""
        return format_name.lower() in self.supported_formats

    def get_supported_formats(self) -> List[str]:
        """获取支持格式列表"""
        return self.supported_formats.copy()

    def validate_output_path(self, source_file: str, output_file: str) -> bool:
        """验证输出路径是否有效"""
        try:
            source_path = Path(source_file)
            output_path = Path(output_file)

            # 检查源文件是否存在
            if not source_path.exists():
                return False

            # 检查输出目录是否可创建
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                return True
            except (OSError, PermissionError):
                return False
        except Exception:
            return False

    def convert_markdown_to_pdf(self,
                               source_file: str,
                               output_file: Optional[str] = None,
                               options: Optional[Dict[str, Any]] = None,
                               progress_callback: Optional[Callable[[float, str], None]] = None,
                               cancel_callback: Optional[Callable[[], bool]] = None) -> ConversionResult:
        """转换Markdown到PDF"""
        return self._convert_markdown(source_file, "pdf", output_file, options, progress_callback, cancel_callback)

    def convert_markdown_to_docx(self,
                                source_file: str,
                                output_file: Optional[str] = None,
                                options: Optional[Dict[str, Any]] = None,
                                progress_callback: Optional[Callable[[float, str], None]] = None,
                                cancel_callback: Optional[Callable[[], bool]] = None) -> ConversionResult:
        """转换Markdown到DOCX"""
        return self._convert_markdown(source_file, "docx", output_file, options, progress_callback, cancel_callback)

    def _convert_markdown(self,
                         source_file: str,
                         target_format: str,
                         output_file: Optional[str] = None,
                         options: Optional[Dict[str, Any]] = None,
                         progress_callback: Optional[Callable[[float, str], None]] = None,
                         cancel_callback: Optional[Callable[[], bool]] = None) -> ConversionResult:
        """核心Markdown转换方法"""
        start_time = time.time()

        try:
            source_path = Path(source_file)

            # 验证源文件
            if not source_path.exists():
                raise ConversionError(f"源文件不存在: {source_file}")

            # 生成输出文件路径
            if output_file is None:
                output_file = str(source_path.with_suffix(f".{target_format}"))

            output_path = Path(output_file)

            # 验证输出路径
            if not self.validate_output_path(source_file, output_file):
                raise ConversionError(f"无效的输出路径: {output_file}")

            # 更新进度
            if progress_callback:
                progress_callback(0.1, "开始转换...")

            # 检查取消
            if cancel_callback and cancel_callback():
                return ConversionResult(
                    success=False,
                    source_file=source_file,
                    output_file=output_file,
                    format=target_format,
                    error_message="转换已取消",
                    conversion_time=time.time() - start_time
                )

            # 根据格式选择转换方法
            if target_format == "pdf":
                success = self._convert_to_pdf(source_path, output_path, options or {}, progress_callback, cancel_callback)
            elif target_format == "docx":
                success = self._convert_to_docx(source_path, output_path, options or {}, progress_callback, cancel_callback)
            elif target_format == "html":
                success = self._convert_to_html(source_path, output_path, options or {}, progress_callback, cancel_callback)
            else:
                success = self._convert_with_pandoc(source_path, output_path, target_format, options or {}, progress_callback, cancel_callback)

            conversion_time = time.time() - start_time

            if success:
                # 更新统计信息
                self.conversion_stats["total_conversions"] += 1
                self.conversion_stats["successful_conversions"] += 1
                self.conversion_stats["total_conversion_time"] += conversion_time

                file_size = output_path.stat().st_size if output_path.exists() else 0

                return ConversionResult(
                    success=True,
                    source_file=source_file,
                    output_file=output_file,
                    format=target_format,
                    conversion_time=conversion_time,
                    file_size=file_size,
                    metadata={"platform": self.platform, "pandoc_used": self.pandoc_available}
                )
            else:
                self.conversion_stats["total_conversions"] += 1
                self.conversion_stats["failed_conversions"] += 1

                return ConversionResult(
                    success=False,
                    source_file=source_file,
                    output_file=output_file,
                    format=target_format,
                    error_message="转换失败",
                    conversion_time=conversion_time
                )

        except Exception as e:
            conversion_time = time.time() - start_time
            self.conversion_stats["total_conversions"] += 1
            self.conversion_stats["failed_conversions"] += 1

            return ConversionResult(
                success=False,
                source_file=source_file,
                output_file=output_file or "",
                format=target_format,
                error_message=str(e),
                conversion_time=conversion_time
            )

    def _convert_to_pdf(self, source_path: Path, output_path: Path,
                       options: Dict[str, Any],
                       progress_callback: Optional[Callable[[float, str], None]] = None,
                       cancel_callback: Optional[Callable[[], bool]] = None) -> bool:
        """转换为PDF"""
        if not self.pandoc_available:
            self.logger.error("Pandoc不可用，无法转换为PDF")
            return False

        try:
            if progress_callback:
                progress_callback(0.3, "正在生成PDF...")

            # 构建Pandoc命令
            cmd = ["pandoc", str(source_path), "-o", str(output_path)]

            # 添加选项
            if options.get("toc", False):
                cmd.append("--toc")

            if options.get("highlight-style"):
                cmd.extend(["--highlight-style", options["highlight-style"]])

            if options.get("pdf-engine"):
                cmd.extend(["--pdf-engine", options["pdf-engine"]])

            # 执行转换
            if progress_callback:
                progress_callback(0.6, "正在执行转换...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if cancel_callback and cancel_callback():
                return False

            if result.returncode == 0:
                if progress_callback:
                    progress_callback(1.0, "转换完成")
                return True
            else:
                self.logger.error(f"Pandoc转换失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("转换超时")
            return False
        except Exception as e:
            self.logger.error(f"转换过程出错: {str(e)}")
            return False

    def _convert_to_docx(self, source_path: Path, output_path: Path,
                        options: Dict[str, Any],
                        progress_callback: Optional[Callable[[float, str], None]] = None,
                        cancel_callback: Optional[Callable[[], bool]] = None) -> bool:
        """转换为DOCX"""
        if not self.pandoc_available:
            # 如果没有Pandoc，创建简单的DOCX占位符
            try:
                docx_content = self._create_simple_docx_placeholder(source_path)
                output_path.write_bytes(docx_content)
                if progress_callback:
                    progress_callback(1.0, "创建DOCX占位符")
                return True
            except Exception as e:
                self.logger.error(f"创建DOCX占位符失败: {str(e)}")
                return False

        return self._convert_with_pandoc(source_path, output_path, "docx", options, progress_callback, cancel_callback)

    def _convert_to_html(self, source_path: Path, output_path: Path,
                        options: Dict[str, Any],
                        progress_callback: Optional[Callable[[float, str], None]] = None,
                        cancel_callback: Optional[Callable[[], bool]] = None) -> bool:
        """转换为HTML"""
        try:
            if progress_callback:
                progress_callback(0.5, "正在生成HTML...")

            # 简单的Markdown到HTML转换
            md_content = source_path.read_text(encoding='utf-8')
            html_content = self._markdown_to_html_simple(md_content)

            if cancel_callback and cancel_callback():
                return False

            output_path.write_text(html_content, encoding='utf-8')

            if progress_callback:
                progress_callback(1.0, "HTML转换完成")

            return True
        except Exception as e:
            self.logger.error(f"HTML转换失败: {str(e)}")
            return False

    def _convert_with_pandoc(self, source_path: Path, output_path: Path,
                           target_format: str, options: Dict[str, Any],
                           progress_callback: Optional[Callable[[float, str], None]] = None,
                           cancel_callback: Optional[Callable[[], bool]] = None) -> bool:
        """使用Pandoc进行转换"""
        if not self.pandoc_available:
            return False

        try:
            if progress_callback:
                progress_callback(0.4, f"正在转换为{target_format}...")

            cmd = ["pandoc", str(source_path), "-o", str(output_path)]

            # 根据格式添加特定选项
            if target_format == "docx":
                cmd.extend(["--standalone"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if cancel_callback and cancel_callback():
                return False

            if result.returncode == 0:
                if progress_callback:
                    progress_callback(1.0, f"{target_format.upper()}转换完成")
                return True
            else:
                self.logger.error(f"Pandoc转换失败: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Pandoc转换出错: {str(e)}")
            return False

    def _create_simple_docx_placeholder(self, source_path: Path) -> bytes:
        """创建简单的DOCX占位符文件"""
        # 这是最小可用的DOCX占位符实现
        # 在实际项目中应使用python-docx库
        content = source_path.read_text(encoding='utf-8')
        xml_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?mso-application progid="Word.Document"?>
<w:wordDocument xmlns:w="http://schemas.microsoft.com/office/word/2003/wordml">
<w:body>
<w:p>
<w:r>
<w:t>{content}</w:t>
</w:r>
</w:p>
</w:body>
</w:wordDocument>'''
        return xml_content.encode('utf-8')

    def _markdown_to_html_simple(self, markdown_content: str) -> str:
        """简单的Markdown到HTML转换"""
        lines = markdown_content.split('\n')
        html_lines = []

        for line in lines:
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.strip() == '':
                html_lines.append('<br>')
            elif line.startswith('- '):
                html_lines.append(f'<li>{line[2:]}</li>')
            else:
                # 简单的文本处理
                line = line.replace('**', '<strong>').replace('**', '</strong>')
                line = line.replace('*', '<em>').replace('*', '</em>')
                html_lines.append(f'<p>{line}</p>')

        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Converted Document</title>
</head>
<body>
{chr(10).join(html_lines)}
</body>
</html>'''

    def batch_convert_markdown(self,
                             source_files: List[str],
                             output_dir: str,
                             format: str = "pdf",
                             options: Optional[Dict[str, Any]] = None) -> List[ConversionResult]:
        """批量转换Markdown文件（同步版本）"""
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for i, source_file in enumerate(source_files):
            try:
                source_path = Path(source_file)
                output_file = output_path / f"{source_path.stem}.{format}"

                result = self._convert_markdown(
                    source_file,
                    format,
                    str(output_file),
                    options
                )
                results.append(result)

            except Exception as e:
                results.append(ConversionResult(
                    success=False,
                    source_file=source_file,
                    output_file="",
                    format=format,
                    error_message=str(e)
                ))

        return results

    def batch_convert_markdown_async(self,
                                   source_files: List[str],
                                   output_dir: str,
                                   format: str = "pdf",
                                   options: Optional[Dict[str, Any]] = None,
                                   priority: ConversionPriority = ConversionPriority.NORMAL) -> List[str]:
        """批量转换Markdown文件（异步版本）"""
        task_ids = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for source_file in source_files:
            try:
                source_path = Path(source_file)
                output_file = output_path / f"{source_path.stem}.{format}"

                task_id = self.submit_conversion_task(
                    source_file,
                    str(output_file),
                    format,
                    options,
                    priority
                )
                task_ids.append(task_id)

            except Exception as e:
                self.logger.error(f"提交批量转换任务失败: {source_file}, 错误: {str(e)}")

        return task_ids

    def wait_for_tasks(self, task_ids: List[str], timeout: Optional[float] = None) -> List[ConversionResult]:
        """等待任务完成"""
        results = []
        start_time = time.time()

        while len(results) < len(task_ids):
            if timeout and (time.time() - start_time) > timeout:
                break

            for task_id in task_ids[:]:  # 创建副本以便修改
                task = self.get_task_status(task_id)
                if task and task.status in [ConversionStatus.COMPLETED, ConversionStatus.FAILED, ConversionStatus.CANCELLED]:
                    if task.result:
                        results.append(task.result)
                    task_ids.remove(task_id)

            time.sleep(0.1)  # 短暂等待

        return results

    def convert_markdown_with_format_detection(self,
                                             source_file: str,
                                             output_file: Optional[str] = None,
                                             preferred_format: str = "pdf") -> ConversionResult:
        """智能格式检测和转换"""
        source_path = Path(source_file)

        # 分析源文件内容来推荐最佳格式
        content = source_path.read_text(encoding='utf-8', errors='ignore')

        recommended_format = self._analyze_content_for_format(content, preferred_format)

        if output_file is None:
            output_file = str(source_path.with_suffix(f".{recommended_format}"))

        return self._convert_markdown(source_file, recommended_format, output_file)

    def _analyze_content_for_format(self, content: str, preferred_format: str) -> str:
        """分析内容并推荐最佳格式"""
        # 简单的内容分析
        has_complex_formatting = bool(re.search(r'```|!\[.*\]\(.*\)|\$\$.*\$\$', content))
        has_tables = bool(re.search(r'\|.*\|', content))
        has_math = bool(re.search(r'\$\$.*\$\$', content))

        # 根据内容特征推荐格式
        if has_math or has_complex_formatting:
            if self.pandoc_available:
                return "pdf"
            else:
                return "html"
        elif has_tables:
            return "docx" if self.pandoc_available else "html"
        else:
            return preferred_format

    def create_conversion_profile(self, name: str, options: Dict[str, Any]) -> bool:
        """创建转换配置文件"""
        try:
            profiles_dir = Path.home() / ".daip" / "conversion_profiles"
            profiles_dir.mkdir(parents=True, exist_ok=True)

            profile_file = profiles_dir / f"{name}.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(options, f, ensure_ascii=False, indent=2)

            self.logger.info(f"转换配置文件已创建: {profile_file}")
            return True

        except Exception as e:
            self.logger.error(f"创建转换配置文件失败: {str(e)}")
            return False

    def load_conversion_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """加载转换配置文件"""
        try:
            profiles_dir = Path.home() / ".daip" / "conversion_profiles"
            profile_file = profiles_dir / f"{name}.json"

            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

            return None

        except Exception as e:
            self.logger.error(f"加载转换配置文件失败: {str(e)}")
            return None

    def list_conversion_profiles(self) -> List[str]:
        """列出所有转换配置文件"""
        try:
            profiles_dir = Path.home() / ".daip" / "conversion_profiles"
            if profiles_dir.exists():
                return [f.stem for f in profiles_dir.glob("*.json")]
            return []

        except Exception as e:
            self.logger.error(f"列出转换配置文件失败: {str(e)}")
            return []

    def validate_markdown_content(self, source_file: str) -> Dict[str, Any]:
        """验证Markdown内容"""
        try:
            source_path = Path(source_file)
            content = source_path.read_text(encoding='utf-8')

            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "statistics": {
                    "lines": len(content.splitlines()),
                    "characters": len(content),
                    "words": len(content.split()),
                    "headings": len(re.findall(r'^#+\s', content, re.MULTILINE)),
                    "links": len(re.findall(r'\[.*\]\(.*\)', content)),
                    "images": len(re.findall(r'!\[.*\]\(.*\)', content)),
                    "code_blocks": len(re.findall(r'```', content)) // 2,
                    "tables": len(re.findall(r'\|.*\|', content))
                }
            }

            # 检查常见问题
            if not content.strip():
                validation_result["errors"].append("文件为空")
                validation_result["valid"] = False

            # 检查未配对的代码块
            code_block_count = len(re.findall(r'```', content))
            if code_block_count % 2 != 0:
                validation_result["warnings"].append("存在未配对的代码块标记")

            # 检查可能的链接问题
            broken_links = re.findall(r'\[.*\]\(\s*\)', content)
            if broken_links:
                validation_result["warnings"].append(f"发现 {len(broken_links)} 个空链接")

            return validation_result

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"读取文件失败: {str(e)}"],
                "warnings": [],
                "statistics": {}
            }

    def estimate_conversion_time(self, source_file: str, target_format: str) -> float:
        """估算转换时间（秒）"""
        try:
            source_path = Path(source_file)
            content = source_path.read_text(encoding='utf-8')

            # 基于文件大小和格式复杂度的简单估算
            base_time = 0.5  # 基础时间
            size_factor = len(content) / 10000  # 每10KB字符增加的时间
            complexity_factor = 0

            # 根据目标格式调整
            if target_format == "pdf":
                complexity_factor = 2.0
                if self.pandoc_available:
                    complexity_factor = 1.0
            elif target_format == "docx":
                complexity_factor = 1.5
            elif target_format == "html":
                complexity_factor = 0.5

            # 检查内容复杂度
            if re.search(r'```|\$\$.*\$\$', content):
                complexity_factor += 0.5

            estimated_time = base_time + (size_factor * complexity_factor)
            return max(estimated_time, 0.1)  # 最少0.1秒

        except Exception:
            return 1.0  # 默认估算时间

    def convert_with_template(self,
                            source_file: str,
                            output_file: str,
                            template_file: str,
                            options: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """使用模板进行转换"""
        start_time = time.time()

        try:
            source_path = Path(source_file)
            template_path = Path(template_file)
            output_path = Path(output_file)

            if not source_path.exists():
                raise ConversionError(f"源文件不存在: {source_file}")

            if not template_path.exists():
                raise ConversionError(f"模板文件不存在: {template_file}")

            # 读取模板和内容
            template_content = template_path.read_text(encoding='utf-8')
            markdown_content = source_path.read_text(encoding='utf-8')

            # 简单的模板替换
            title = source_path.stem
            body = self._markdown_to_html_simple(markdown_content)

            html_content = template_content.replace('$title$', title).replace('$body$', body)

            output_path.write_text(html_content, encoding='utf-8')

            return ConversionResult(
                success=True,
                source_file=source_file,
                output_file=output_file,
                format="html",
                conversion_time=time.time() - start_time,
                file_size=output_path.stat().st_size,
                metadata={"template_used": template_file}
            )

        except Exception as e:
            return ConversionResult(
                success=False,
                source_file=source_file,
                output_file=output_file,
                format="html",
                error_message=str(e),
                conversion_time=time.time() - start_time
            )

    def start_workers(self):
        """启动工作线程"""
        if not self.is_running:
            self.is_running = True
            for i in range(self.max_workers):
                worker = threading.Thread(target=self._worker_loop, name=f"FormatConverter-Worker-{i}")
                worker.daemon = True
                worker.start()
                self.worker_threads.append(worker)
            self.logger.info(f"启动了 {self.max_workers} 个工作线程")

    def stop_workers(self):
        """停止工作线程"""
        self.is_running = False
        # 添加停止信号到队列
        for _ in range(self.max_workers):
            try:
                self.task_queue.put((0, None))  # 停止信号
            except queue.Full:
                pass

        # 等待所有线程结束
        for worker in self.worker_threads:
            if worker.is_alive():
                worker.join(timeout=5)

        self.worker_threads.clear()
        self.logger.info("已停止所有工作线程")

    def _worker_loop(self):
        """工作线程主循环"""
        while self.is_running:
            try:
                # 获取任务（阻塞操作，最多等待1秒）
                priority, task = self.task_queue.get(timeout=1)

                if task is None:  # 停止信号
                    break

                # 执行转换
                self._execute_task(task)

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"工作线程出错: {str(e)}")

    def _execute_task(self, task: ConversionTask):
        """执行转换任务"""
        try:
            with self._lock:
                task.status = ConversionStatus.RUNNING
                task.started_at = datetime.now()
                self.active_tasks[task.task_id] = task

            # 执行实际转换
            result = self._convert_markdown(
                task.source_file,
                task.format,
                task.output_file,
                task.options,
                lambda p, m: self._update_task_progress(task.task_id, p, m)
            )

            # 更新任务状态
            with self._lock:
                task.completed_at = datetime.now()
                task.result = result
                task.status = ConversionStatus.COMPLETED if result.success else ConversionStatus.FAILED

                if not result.success:
                    task.error_message = result.error_message

                # 移动到完成列表
                self.completed_tasks.append(task)
                self.active_tasks.pop(task.task_id, None)
                self.task_history.append(result)

                # 限制历史记录大小
                if len(self.task_history) > self.max_history_size:
                    self.task_history = self.task_history[-self.max_history_size:]

                # 更新统计信息
                self._update_statistics(result)

        except Exception as e:
            with self._lock:
                task.completed_at = datetime.now()
                task.status = ConversionStatus.FAILED
                task.error_message = str(e)
                self.active_tasks.pop(task.task_id, None)

            self.logger.error(f"任务 {task.task_id} 执行失败: {str(e)}")

    def _update_task_progress(self, task_id: str, progress: float, message: str):
        """更新任务进度"""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.progress = progress
                task.progress_message = message

    def _update_statistics(self, result: ConversionResult):
        """更新统计信息"""
        self.conversion_stats["total_conversions"] += 1

        if result.success:
            self.conversion_stats["successful_conversions"] += 1
        else:
            self.conversion_stats["failed_conversions"] += 1

        if result.conversion_time:
            self.conversion_stats["total_conversion_time"] += result.conversion_time

        # 更新性能指标
        self._update_performance_metrics()

    def _update_performance_metrics(self):
        """更新性能指标"""
        total = self.conversion_stats["total_conversions"]
        if total > 0:
            self.performance_metrics["success_rate"] = (
                self.conversion_stats["successful_conversions"] / total
            )
            self.performance_metrics["average_conversion_time"] = (
                self.conversion_stats["total_conversion_time"] / total
            )

        # 计算队列利用率
        self.performance_metrics["queue_utilization"] = (
            self.task_queue.qsize() / self.max_queue_size
        )

    def submit_conversion_task(self,
                             source_file: str,
                             output_file: str,
                             format: str,
                             options: Optional[Dict[str, Any]] = None,
                             priority: ConversionPriority = ConversionPriority.NORMAL) -> str:
        """提交转换任务（异步）"""
        task_id = str(uuid.uuid4())

        task = ConversionTask(
            task_id=task_id,
            source_file=source_file,
            output_file=output_file,
            format=format,
            options=options or {},
            priority=priority
        )

        try:
            # 负优先级用于优先级队列
            priority_value = -priority.value
            self.task_queue.put((priority_value, task), timeout=5)

            self.logger.info(f"提交转换任务: {task_id} ({source_file} -> {format})")
            return task_id

        except queue.Full:
            raise ConversionQueueFull("转换队列已满，请稍后再试")

    def get_task_status(self, task_id: str) -> Optional[ConversionTask]:
        """获取任务状态"""
        with self._lock:
            # 检查活跃任务
            if task_id in self.active_tasks:
                return self.active_tasks[task_id]

            # 检查完成任务
            for task in self.completed_tasks:
                if task.task_id == task_id:
                    return task

            return None

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            # 只能取消未开始的任务
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if task.status == ConversionStatus.RUNNING:
                    return False  # 正在运行的任务无法取消

                task.status = ConversionStatus.CANCELLED
                self.active_tasks.pop(task_id, None)
                return True

            return False

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        with self._lock:
            return {
                "queue_size": self.task_queue.qsize(),
                "max_queue_size": self.max_queue_size,
                "active_tasks": len(self.active_tasks),
                "completed_tasks": len(self.completed_tasks),
                "total_workers": len(self.worker_threads),
                "is_running": self.is_running
            }

    def get_conversion_statistics(self) -> Dict[str, Any]:
        """获取转换统计信息"""
        total_time = self.conversion_stats["total_conversion_time"]
        total_conversions = self.conversion_stats["total_conversions"]

        avg_time = total_time / total_conversions if total_conversions > 0 else 0

        return {
            **self.conversion_stats,
            "average_conversion_time": avg_time,
            "success_rate": self.conversion_stats["successful_conversions"] / total_conversions if total_conversions > 0 else 0,
            **self.performance_metrics,
            "queue_status": self.get_queue_status()
        }

    def get_conversion_history(self, limit: int = 50) -> List[ConversionResult]:
        """获取转换历史"""
        with self._lock:
            return self.task_history[-limit:] if limit > 0 else self.task_history.copy()

    def export_conversion_report(self, output_file: str) -> bool:
        """导出转换报告"""
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "statistics": self.get_conversion_statistics(),
                "queue_status": self.get_queue_status(),
                "recent_conversions": [result.to_dict() for result in self.get_conversion_history(100)],
                "active_tasks": [task.to_dict() for task in self.active_tasks.values()]
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            self.logger.info(f"转换报告已导出到: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"导出报告失败: {str(e)}")
            return False

    def cleanup_completed_tasks(self, older_than_hours: int = 24) -> int:
        """清理完成的任务"""
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)

        with self._lock:
            original_count = len(self.completed_tasks)
            self.completed_tasks = [
                task for task in self.completed_tasks
                if task.completed_at and task.completed_at.timestamp() > cutoff_time
            ]

            cleaned_count = original_count - len(self.completed_tasks)

            if cleaned_count > 0:
                self.logger.info(f"清理了 {cleaned_count} 个完成的任务")

            return cleaned_count

    def __del__(self):
        """析构函数"""
        try:
            self.stop_workers()
        except:
            pass


# 保持向后兼容的函数
def export_markdown(src: str, to: str = "pdf", out: str | None = None) -> str:
    """向后兼容的导出函数"""
    converter = FormatConverter()
    result = converter._convert_markdown(src, to, out)

    if result.success:
        return result.output_file
    else:
        raise ConversionError(result.error_message or "转换失败")
