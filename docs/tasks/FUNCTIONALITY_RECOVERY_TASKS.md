# DAIP-LIVE 功能恢复任务清单

**创建日期**: 2025年10月11日
**方法论**: TDD驱动开发
**置信度要求**: 每个任务 ≥ 96%
**框架**: BMAD + SPEC + KISS + YAGNI + SOLID

---

## 📋 任务执行方法论

### TDD循环 (RED-GREEN-REFACTOR)
1. **RED**: 编写失败的测试用例
2. **GREEN**: 编写最小可行代码通过测试
3. **REFACTOR**: 重构代码，保持测试通过

### 任务置信度评估
- **研究模式**: 置信度 < 80% 时进入，增加技术预研
- **创新模式**: 置信度 80-90% 时进入，探索最佳实现方案
- **计划模式**: 置信度 90-95% 时进入，细化实现计划
- **执行模式**: 置信度 ≥ 96% 时进入，开始编码实现

### 质量标准
- 每个功能模块 ≥ 90% 测试覆盖率
- 所有公共接口必须有类型提示
- 错误处理覆盖率 100%
- 性能基准测试通过

---

## 🎯 Phase 1: Wiki管理系统 (置信度: 96%)

### 📊 Phase 1 概览
**业务价值**: ⭐⭐⭐⭐⭐ (用户高频需求)
**技术复杂度**: ⭐⭐⭐ (中等)
**预估工作量**: 15-20天
**成功指标**: 用户可通过TUI完整使用Wiki功能

### 🎯 任务 1.1: Wiki核心数据模型 (置信度: 98%)

#### 子任务 1.1.1: WikiPage数据模型设计
**置信度**: 98%
**优先级**: 🔥 高

**RED阶段 - 测试用例设计**:
```python
# tests/wiki/test_wiki_page.py
import pytest
from datetime import datetime
from pathlib import Path

class TestWikiPage:
    def test_wiki_page_creation_with_minimal_data(self):
        """测试最小数据创建Wiki页面"""

    def test_wiki_page_creation_with_full_data(self):
        """测试完整数据创建Wiki页面"""

    def test_wiki_page_content_update(self):
        """测试页面内容更新"""

    def test_wiki_page_tag_management(self):
        """测试标签管理"""

    def test_wiki_page_file_path_validation(self):
        """测试文件路径验证"""

    def test_wiki_page_timestamp_management(self):
        """测试时间戳管理"""
```

**GREEN阶段 - 最小实现**:
```python
# src/daip_live/wiki/models.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

@dataclass
class WikiPage:
    title: str
    content: str
    file_path: Path
    created_at: datetime
    modified_at: datetime
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.file_path.suffix == '.md':
            raise ValueError("Wiki page must be a markdown file")

    def update_content(self, content: str) -> None:
        if not isinstance(content, str):
            raise TypeError("Content must be a string")
        self.content = content
        self.modified_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        if not tag or not tag.strip():
            raise ValueError("Tag cannot be empty")
        clean_tag = tag.strip().lower()
        if clean_tag not in self.tags:
            self.tags.append(clean_tag)

    def remove_tag(self, tag: str) -> bool:
        clean_tag = tag.strip().lower()
        if clean_tag in self.tags:
            self.tags.remove(clean_tag)
            return True
        return False
```

**REFACTOR阶段 - 优化改进**:
- 添加属性验证装饰器
- 实现内容变更历史跟踪
- 添加序列化/反序列化方法

#### 子任务 1.1.2: WikiManager核心服务
**置信度**: 97%
**优先级**: 🔥 高

**RED阶段 - 测试用例设计**:
```python
# tests/wiki/test_wiki_manager.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

class TestWikiManager:
    @pytest.fixture
    def temp_wiki_dir(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        return wiki_dir

    @pytest.fixture
    def wiki_manager(self, temp_wiki_dir):
        knowledge_manager = Mock()
        return WikiManager(temp_wiki_dir, knowledge_manager)

    def test_create_page_with_valid_title(self, wiki_manager):
        """测试创建有效标题的页面"""

    def test_create_page_with_invalid_title(self, wiki_manager):
        """测试创建无效标题的页面"""

    def test_create_page_duplicate_title(self, wiki_manager):
        """测试创建重复标题的页面"""

    def test_list_pages_by_modified_date(self, wiki_manager):
        """测试按修改日期列出页面"""

    def test_list_pages_with_limit(self, wiki_manager):
        """测试限制数量的页面列表"""

    def test_open_existing_page(self, wiki_manager):
        """测试打开存在的页面"""

    def test_open_nonexistent_page(self, wiki_manager):
        """测试打开不存在的页面"""

    def test_search_pages_by_content(self, wiki_manager):
        """测试按内容搜索页面"""

    def test_search_pages_by_title(self, wiki_manager):
        """测试按标题搜索页面"""

    def test_delete_existing_page(self, wiki_manager):
        """测试删除存在的页面"""

    def test_delete_nonexistent_page(self, wiki_manager):
        """测试删除不存在的页面"""
```

**GREEN阶段 - 最小实现**:
```python
# src/daip_live/wiki/manager.py
import os
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime

class WikiManager:
    def __init__(self, wiki_dir: Path, knowledge_manager):
        self.wiki_dir = Path(wiki_dir)
        self.knowledge_manager = knowledge_manager
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_title(self, title: str) -> str:
        """清理标题，生成合法的文件名"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        # 移除特殊字符，替换空格为下划线
        clean_title = re.sub(r'[<>:"/\\|?*]', '', title.strip())
        clean_title = re.sub(r'\s+', '_', clean_title)

        if not clean_title:
            raise ValueError("Title contains only invalid characters")

        return clean_title

    def _get_page_path(self, title: str) -> Path:
        """获取页面文件路径"""
        clean_title = self._sanitize_title(title)
        return self.wiki_dir / f"{clean_title}.md"

    def create_page(self, title: str, content: str = "", tags: List[str] = None) -> WikiPage:
        """创建新的Wiki页面"""
        file_path = self._get_page_path(title)

        if file_path.exists():
            raise FileExistsError(f"Page '{title}' already exists")

        # 创建默认内容
        if not content:
            content = f"# {title}\n\n开始编写您的内容..."

        # 添加YAML front matter
        timestamp = datetime.now()
        yaml_header = f"---\ntitle: {title}\ncreated: {timestamp.isoformat()}\n"
        if tags:
            yaml_header += f"tags: [{', '.join(tags)}]\n"
        yaml_header += "---\n\n"

        full_content = yaml_header + content

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return WikiPage(
            title=title,
            content=full_content,
            file_path=file_path,
            created_at=timestamp,
            modified_at=timestamp,
            tags=tags or []
        )
```

### 🎯 任务 1.2: Wiki TUI集成 (置信度: 96%)

#### 子任务 1.2.1: TUI命令处理器
**置信度**: 96%
**优先级**: 🔥 高

**RED阶段 - 测试用例设计**:
```python
# tests/wiki/test_wiki_tui.py
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock

class TestWikiTUICommands:
    @pytest.fixture
    def mock_tui(self):
        tui = Mock()
        tui._update_log_view = Mock()
        tui._get_wiki_manager = Mock()
        return tui

    def test_wiki_new_command_with_title(self, mock_tui):
        """测试/wiki new <title>命令"""

    def test_wiki_new_command_without_title(self, mock_tui):
        """测试/wiki new无标题命令"""

    def test_wiki_list_command(self, mock_tui):
        """测试/wiki list命令"""

    def test_wiki_open_command_with_valid_title(self, mock_tui):
        """测试/wiki open <title>命令"""

    def test_wiki_open_command_with_invalid_title(self, mock_tui):
        """测试/wiki open无效标题命令"""

    def test_wiki_search_command_with_query(self, mock_tui):
        """测试/wiki search <query>命令"""

    def test_wiki_search_command_without_query(self, mock_tui):
        """测试/wiki search无查询命令"""

    def test_wiki_command_help(self, mock_tui):
        """测试/wiki帮助信息"""
```

**GREEN阶段 - 最小实现**:
```python
# src/daip_live/wiki/tui_integration.py
import asyncio
from typing import Optional

class WikiTUIHandler:
    def __init__(self, tui_app):
        self.tui = tui_app

    def get_wiki_manager(self):
        """获取Wiki管理器实例"""
        if not hasattr(self.tui, '_wiki_manager'):
            from daip_live.wiki.manager import WikiManager
            wiki_dir = Path.cwd() / "wiki"
            self.tui._wiki_manager = WikiManager(wiki_dir, self.tui._knowledge_manager)
        return self.tui._wiki_manager

    async def handle_wiki_command(self, args: str) -> None:
        """处理Wiki命令"""
        wiki_manager = self.get_wiki_manager()

        parts = args.strip().split(" ", 1)
        subcommand = parts[0].lower() if parts else ""
        subargs = parts[1] if len(parts) > 1 else ""

        try:
            if subcommand == "new":
                await self._handle_wiki_new(wiki_manager, subargs)
            elif subcommand == "list":
                await self._handle_wiki_list(wiki_manager)
            elif subcommand == "open":
                await self._handle_wiki_open(wiki_manager, subargs)
            elif subcommand == "search":
                await self._handle_wiki_search(wiki_manager, subargs)
            else:
                self.tui._update_log_view("[bold red]> Usage: /wiki [new <title>|list|open <title>|search <query>][/bold red]")
        except Exception as e:
            self.tui._update_log_view(f"[bold red]> Wiki command error: {e}[/bold red]")

    async def _handle_wiki_new(self, wiki_manager, title: str) -> None:
        """处理创建Wiki页面"""
        if not title:
            self.tui._update_log_view("[bold yellow]> Usage: /wiki new <title>[/bold yellow]")
            return

        try:
            page = wiki_manager.create_page(title)
            self.tui._update_log_view(f"[bold green]> ✓ Created wiki page: {page.title}[/bold green]")
            self.tui._update_log_view(f"[dim]   Path: {page.file_path}[/dim]")
        except FileExistsError:
            self.tui._update_log_view(f"[bold red]> Page '{title}' already exists[/bold red]")
        except Exception as e:
            self.tui._update_log_view(f"[bold red]> Failed to create page: {e}[/bold red]")
```

### 🎯 任务 1.3: Wiki知识库集成 (置信度: 95%)

#### 子任务 1.3.1: 知识库同步器
**置信度**: 95%
**优先级**: ⚠️ 中

**RED阶段 - 测试用例设计**:
```python
# tests/wiki/test_knowledge_integration.py
import pytest
from unittest.mock import Mock, AsyncMock

class TestWikiKnowledgeIntegration:
    def test_sync_wiki_pages_to_knowledge_base(self):
        """测试Wiki页面同步到知识库"""

    def test_incremental_sync_only_new_pages(self):
        """测试增量同步只处理新页面"""

    def test_search_wiki_content_through_knowledge_manager(self):
        """测试通过知识管理器搜索Wiki内容"""

    def test_handle_sync_errors_gracefully(self):
        """测试优雅处理同步错误"""
```

---

## 🎯 Phase 2: 论文下载工具 (置信度: 94%)

### 📊 Phase 2 概览
**业务价值**: ⭐⭐⭐⭐ (研究人员需求)
**技术复杂度**: ⭐⭐⭐⭐ (网络调用 + 文件处理)
**预估工作量**: 10-15天
**成功指标**: 用户可搜索和下载arXiv论文

### 🎯 任务 2.1: ArXiv集成核心 (置信度: 92%)

#### 子任务 2.1.1: ArXiv API客户端
**置信度**: 92%
**优先级**: 🔥 高

**研究模式需求**:
- [ ] 调研python-arxiv库的最佳使用方式
- [ ] 验证API限制和错误处理策略
- [ ] 研究并发下载的最佳实践

**创新模式需求**:
- [ ] 设计智能的论文推荐算法
- [ ] 探索本地缓存策略
- [ ] 设计批量下载优化方案

**RED阶段 - 测试用例设计**:
```python
# tests/doc/test_arxiv_client.py
import pytest
from unittest.mock import Mock, patch, AsyncMock

class TestArxivClient:
    @pytest.fixture
    def arxiv_client(self, tmp_path):
        return ArxivDownloader(tmp_path / "papers")

    @patch('arxiv.Client')
    def test_search_papers_with_valid_query(self, mock_client, arxiv_client):
        """测试有效查询搜索论文"""

    @patch('arxiv.Client')
    def test_search_papers_with_empty_query(self, mock_client, arxiv_client):
        """测试空查询处理"""

    @patch('arxiv.Client')
    def test_download_paper_by_valid_id(self, mock_client, arxiv_client):
        """测试通过有效ID下载论文"""

    @patch('arxiv.Client')
    def test_download_paper_with_network_error(self, mock_client, arxiv_client):
        """测试网络错误处理"""

    @patch('arxiv.Client')
    def test_download_paper_with_invalid_id(self, mock_client, arxiv_client):
        """测试无效ID处理"""
```

**GREEN阶段 - 最小实现**:
```python
# src/daip_live/doc/arxiv_client.py
import asyncio
from pathlib import Path
from typing import List, Optional
import arxiv

class ArxivDownloader:
    def __init__(self, papers_dir: Path):
        self.papers_dir = Path(papers_dir)
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        self.client = arxiv.Client()

    async def search_and_download(self, query: str, max_results: int = 5) -> 'DownloadResult':
        """搜索并下载论文"""
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            downloaded_count = 0
            results = []

            for result in self.client.results(search):
                try:
                    download_result = await self._download_paper(result)
                    if download_result.success:
                        downloaded_count += 1
                        results.append(download_result)
                except Exception as e:
                    # 单个论文下载失败不影响其他论文
                    continue

            return DownloadResult(
                query=query,
                total_found=len(results),
                downloaded=downloaded_count,
                papers=results
            )

        except Exception as e:
            raise ArxivDownloadError(f"Search failed: {e}")

    async def _download_paper(self, paper: arxiv.Result) -> 'PaperDownloadResult':
        """下载单个论文"""
        # 实现下载逻辑
        pass
```

### 🎯 任务 2.2: 依赖检查和降级 (置信度: 96%)

#### 子任务 2.2.1: 依赖管理器
**置信度**: 96%
**优先级**: ⚠️ 中

**RED阶段 - 测试用例设计**:
```python
# tests/doc/test_dependency_manager.py
import pytest
from unittest.mock import patch, Mock

class TestDependencyManager:
    def test_check_arxiv_library_available(self):
        """测试arxiv库可用性检查"""

    def test_check_arxiv_library_unavailable(self):
        """测试arxiv库不可用情况"""

    def test_check_pandoc_available(self):
        """测试Pandoc可用性检查"""

    def test_feature_enablement_based_on_dependencies(self):
        """测试基于依赖的功能启用"""

    def test_graceful_degradation_when_dependencies_missing(self):
        """测试依赖缺失时的优雅降级"""
```

### 🎯 任务 2.3: TUI命令集成 (置信度: 96%)

#### 子任务 2.3.1: 文档命令处理器
**置信度**: 96%
**优先级**: 🔥 高

**RED阶段 - 测试用例设计**:
```python
# tests/doc/test_doc_tui.py
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestDocTUICommands:
    @pytest.fixture
    def mock_tui(self):
        tui = Mock()
        tui._update_log_view = Mock()
        tui._get_paper_manager = Mock()
        return tui

    async def test_doc_fetch_with_valid_query(self, mock_tui):
        """测试/doc fetch <query>命令"""

    async def test_doc_fetch_with_empty_query(self, mock_tui):
        """测试/doc fetch空查询"""

    async def test_doc_export_markdown_to_pdf(self, mock_tui):
        """测试/doc export <file> --to pdf"""

    async def test_doc_export_markdown_to_docx(self, mock_tui):
        """测试/doc export <file> --to docx"""

    async def test_doc_export_file_not_found(self, mock_tui):
        """测试导出不存在的文件"""

    async def test_doc_export_dependency_missing(self, mock_tui):
        """测试依赖缺失时的导出"""
```

---

## 🎯 Phase 3: 格式转换工具 (置信度: 96%)

### 📊 Phase 3 概览
**业务价值**: ⭐⭐⭐ (辅助功能)
**技术复杂度**: ⭐⭐⭐ (外部工具集成)
**预估工作量**: 5-8天
**成功指标**: 支持Markdown到PDF/DOCX转换

### 🎯 任务 3.1: 格式转换核心 (置信度: 96%)

#### 子任务 3.1.1: 文档转换器
**置信度**: 96%
**优先级**: ⚠️ 中

**RED阶段 - 测试用例设计**:
```python
# tests/doc/test_document_converter.py
import pytest
from pathlib import Path
from unittest.mock import patch, Mock

class TestDocumentConverter:
    def test_convert_markdown_to_pdf_with_pandoc(self):
        """测试使用Pandoc转换Markdown到PDF"""

    def test_convert_markdown_to_docx_with_pandoc(self):
        """测试使用Pandoc转换Markdown到DOCX"""

    def test_convert_markdown_to_docx_with_python_docx(self):
        """测试使用python-docx转换Markdown到DOCX"""

    def test_handle_missing_dependencies_gracefully(self):
        """测试优雅处理缺失依赖"""

    def test_handle_conversion_errors(self):
        """测试转换错误处理"""

    def test_handle_large_file_conversion(self):
        """测试大文件转换处理"""
```

**GREEN阶段 - 最小实现**:
```python
# src/daip_live/doc/converter.py
import asyncio
from pathlib import Path
from typing import Optional
from subprocess import run, PIPE

class DocumentConverter:
    def __init__(self):
        self.pandoc_available = self._check_pandoc()
        self.docx_available = self._check_python_docx()

    def _check_pandoc(self) -> bool:
        """检查Pandoc是否可用"""
        try:
            result = run(['pandoc', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, TimeoutError):
            return False

    def _check_python_docx(self) -> bool:
        """检查python-docx是否可用"""
        try:
            import docx
            return True
        except ImportError:
            return False

    async def convert_to_pdf(self, markdown_path: Path, output_path: Optional[Path] = None) -> 'ConversionResult':
        """转换为PDF"""
        if not self.pandoc_available:
            return ConversionResult(
                success=False,
                error="Pandoc is not available. Install pandoc to enable PDF conversion."
            )

        if output_path is None:
            output_path = markdown_path.with_suffix('.pdf')

        try:
            cmd = [
                'pandoc',
                str(markdown_path),
                '-o', str(output_path),
                '--pdf-engine=xelatex'  # 使用xelatex以支持中文
            ]

            result = run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return ConversionResult(success=True, output_path=output_path)
            else:
                return ConversionResult(
                    success=False,
                    error=f"Pandoc conversion failed: {result.stderr}"
                )

        except Exception as e:
            return ConversionResult(success=False, error=str(e))
```

---

## 📊 总体执行计划

### 时间线规划
```
Week 1-2: Wiki管理系统
├── Day 1-3: 核心数据模型 (任务1.1)
├── Day 4-6: TUI集成 (任务1.2)
├── Day 7-8: 知识库集成 (任务1.3)
└── Day 9-10: 测试和优化

Week 3: 论文下载工具
├── Day 11-13: ArXiv集成 (任务2.1)
├── Day 14-15: 依赖管理 (任务2.2)
└── Day 16-17: TUI集成 (任务2.3)

Week 4: 格式转换工具
├── Day 18-20: 格式转换核心 (任务3.1)
├── Day 21-22: TUI集成和测试
└── Day 23-25: 整体测试和优化
```

### 质量检查点
- **每日**: 单元测试覆盖率 ≥ 90%
- **每周**: 集成测试通过率 100%
- **Phase结束**: 用户验收测试通过

### 风险缓解策略
1. **技术风险**: 提前技术预研，准备备选方案
2. **进度风险**: 每周进度评估，及时调整计划
3. **质量风险**: 严格的代码审查和测试标准

---

**任务总结**: 本任务清单遵循TDD方法论，确保每个功能的实现都有完整的测试覆盖。通过分阶段、分任务的方式，保证高质量地完成所有缺失功能的开发工作。