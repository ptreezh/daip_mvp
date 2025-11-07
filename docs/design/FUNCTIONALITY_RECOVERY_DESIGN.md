# DAIP-LIVE 功能恢复设计文档

**设计日期**: 2025年10月11日
**设计原则**: BMAD + SPEC + KISS + YAGNI + SOLID
**置信度**: 96%

---

## 🎯 设计目标

### 主要目标
1. **消除所有占位符实现**: 确保每个声明的功能都有真实实现
2. **提升用户体验**: 完善TUI集成，确保功能可直接使用
3. **保持架构完整性**: 遵循现有设计模式，不破坏系统稳定性
4. **TDD驱动开发**: 每个功能都有完整的测试覆盖

### 成功标准
- 所有空壳功能转换为可用功能
- TUI命令与后端功能100%映射
- 测试覆盖率达到90%以上
- 用户可直接使用所有声明的功能

---

## 🏗️ 系统架构设计

### 模块依赖关系
```
TUI Interface Layer
       ↓
Command Handler Layer
       ↓
Service Layer (Business Logic)
       ↓
Data Access Layer
       ↓
External APIs / File System
```

### 设计原则应用

#### SOLID原则体现
1. **单一职责**: 每个服务类专注单一功能领域
2. **开闭原则**: 通过接口和抽象类支持扩展
3. **里氏替换**: 统一的服务接口，实现可互换
4. **接口隔离**: 小而专一的接口设计
5. **依赖倒置**: 依赖抽象，便于测试和扩展

#### KISS原则体现
- 使用现有工具和库，避免重新发明轮子
- 简单的数据流和控制流
- 清晰的错误处理策略

#### YAGNI原则体现
- 只实现当前明确需要的功能
- 避免过度设计和复杂的抽象
- 预留扩展点但不预先实现

---

## 📋 Phase 1: Wiki管理系统设计

### 需求分析 (BMAD)

#### 业务价值
- **用户需求**: 个人知识管理是AI助手的核心功能
- **使用频率**: 高频使用，日常知识积累
- **业务影响**: 显著提升用户粘性和使用体验

#### 可测量成果
- **当前状态**: 功能完全不可用 (0分)
- **目标状态**: 完全可用 (5分)
- **成功指标**: 用户可以创建、编辑、搜索Wiki页面

### 系统设计

#### 1. 核心组件设计

```python
class WikiManager:
    """Wiki管理器 - 负责Wiki页面的生命周期管理"""

    def __init__(self, wiki_dir: Path, knowledge_manager: KnowledgeManager):
        self.wiki_dir = wiki_dir
        self.knowledge_manager = knowledge_manager

    def create_page(self, title: str, content: str = "", tags: List[str] = None) -> WikiPage:
        """创建新的Wiki页面"""

    def list_pages(self, sort_by: str = "modified", limit: int = 20) -> List[WikiPage]:
        """列出Wiki页面"""

    def open_page(self, title_or_path: str) -> WikiPage:
        """打开Wiki页面"""

    def search_pages(self, query: str) -> List[WikiPage]:
        """搜索Wiki页面"""

    def delete_page(self, title: str) -> bool:
        """删除Wiki页面"""

class WikiPage:
    """Wiki页面数据模型"""

    def __init__(self, title: str, content: str, file_path: Path,
                 created_at: datetime, modified_at: datetime, tags: List[str] = None):
        self.title = title
        self.content = content
        self.file_path = file_path
        self.created_at = created_at
        self.modified_at = modified_at
        self.tags = tags or []

    def update_content(self, content: str):
        """更新页面内容"""

    def add_tag(self, tag: str):
        """添加标签"""

    def remove_tag(self, tag: str):
        """移除标签"""
```

#### 2. TUI集成设计

```python
def _handle_wiki_command(self, args: str) -> None:
    """Wiki命令处理器"""
    wiki_manager = self._get_wiki_manager()

    parts = args.strip().split(" ", 1)
    subcommand = parts[0].lower() if parts else ""
    subargs = parts[1] if len(parts) > 1 else ""

    if subcommand == "new":
        await self._handle_wiki_new(wiki_manager, subargs)
    elif subcommand == "list":
        await self._handle_wiki_list(wiki_manager)
    elif subcommand == "open":
        await self._handle_wiki_open(wiki_manager, subargs)
    elif subcommand == "search":
        await self._handle_wiki_search(wiki_manager, subargs)
    else:
        self._update_log_view("[bold red]> Usage: /wiki [new <title>|list|open <title>|search <query>][/bold red]")
```

#### 3. 知识库集成设计

```python
class WikiKnowledgeIntegrator:
    """Wiki与知识库集成器"""

    def __init__(self, wiki_manager: WikiManager, knowledge_manager: KnowledgeManager):
        self.wiki_manager = wiki_manager
        self.knowledge_manager = knowledge_manager

    async def sync_wiki_to_knowledge(self) -> Dict[str, int]:
        """将Wiki页面同步到知识库"""

    def get_wiki_search_results(self, query: str) -> List[KnowledgeResult]:
        """获取Wiki搜索结果"""
```

### 文件结构设计
```
wiki/
├── templates/
│   ├── default.md          # 默认页面模板
│   └── meeting_notes.md    # 会议笔记模板
├── assets/
│   └── images/            # 图片资源
├── index.md              # 首页
└── [pages].md            # 用户页面
```

### 错误处理策略
1. **文件操作错误**: 优雅降级，提供清晰的错误信息
2. **权限错误**: 集成现有权限系统
3. **搜索错误**: 降级到文件名搜索
4. **模板错误**: 使用基础模板

---

## 📋 Phase 2: 论文下载工具设计

### 需求分析 (BMAD)

#### 业务价值
- **用户需求**: 研究人员和学生的核心需求
- **使用频率**: 中频使用，研究阶段高频
- **业务影响**: 提升学术研究效率

#### 可测量成果
- **当前状态**: 空实现 (0分)
- **目标状态**: 完全可用 (5分)
- **成功指标**: 用户可以搜索、下载、管理论文

### 系统设计

#### 1. 核心组件设计

```python
class ArxivDownloader:
    """arXiv论文下载器"""

    def __init__(self, papers_dir: Path):
        self.papers_dir = papers_dir
        self.client = arxiv.Client()  # 使用python-arxiv库

    async def search_and_download(self, query: str, max_results: int = 5) -> DownloadResult:
        """搜索并下载论文"""

    async def download_by_id(self, arxiv_id: str) -> DownloadResult:
        """通过ID下载论文"""

    def _save_metadata(self, paper: arxiv.Result, download_path: Path):
        """保存论文元数据"""

class PaperManager:
    """论文管理器"""

    def __init__(self, papers_dir: Path):
        self.papers_dir = papers_dir
        self.downloader = ArxivDownloader(papers_dir)

    def list_papers(self, sort_by: str = "downloaded") -> List[PaperInfo]:
        """列出已下载的论文"""

    def search_papers(self, query: str) -> List[PaperInfo]:
        """搜索本地论文"""

    def delete_paper(self, arxiv_id: str) -> bool:
        """删除论文"""

class PaperInfo:
    """论文信息数据模型"""

    def __init__(self, arxiv_id: str, title: str, authors: List[str],
                 abstract: str, published: datetime, pdf_path: Path, metadata_path: Path):
        self.arxiv_id = arxiv_id
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.published = published
        self.pdf_path = pdf_path
        self.metadata_path = metadata_path
```

#### 2. TUI集成设计

```python
def _handle_doc_command(self, args: str) -> None:
    """文档命令处理器"""
    paper_manager = self._get_paper_manager()

    parts = args.strip().split(" ", 1)
    subcommand = parts[0].lower() if parts else ""
    subargs = parts[1] if len(parts) > 1 else ""

    if subcommand == "fetch":
        await self._handle_doc_fetch(paper_manager, subargs)
    elif subcommand == "export":
        await self._handle_doc_export(subargs)
    elif subcommand == "list":
        await self._handle_doc_list(paper_manager)
    else:
        self._update_log_view("[bold red]> Usage: /doc [fetch <query>|export <file> --to <format>|list][/bold red]")
```

#### 3. 依赖检查和降级设计

```python
class DependencyChecker:
    """依赖检查器"""

    @staticmethod
    def check_arxiv_library() -> bool:
        """检查arxiv库"""

    @staticmethod
    def check_pandoc() -> bool:
        """检查pandoc"""

    @staticmethod
    def check_python_docx() -> bool:
        """检查python-docx"""

class FeatureManager:
    """功能管理器 - 根据依赖启用/禁用功能"""

    def __init__(self):
        self.dependencies = DependencyChecker()
        self.enabled_features = self._evaluate_features()

    def _evaluate_features(self) -> Dict[str, bool]:
        """评估可用功能"""
        return {
            'arxiv_download': self.dependencies.check_arxiv_library(),
            'pandoc_export': self.dependencies.check_pandoc(),
            'docx_export': self.dependencies.check_python_docx()
        }
```

### 错误处理策略
1. **网络错误**: 重试机制 + 优雅降级
2. **依赖缺失**: 禁用相关功能，提供安装提示
3. **文件错误**: 磁盘空间检查 + 权限验证
4. **API限制**: 速率限制 + 缓存机制

---

## 📋 Phase 3: 格式转换工具设计

### 需求分析 (BMAD)

#### 业务价值
- **用户需求**: 文档格式转换需求
- **使用频率**: 低频但重要
- **业务影响**: 完善文档处理生态

#### 可测量成果
- **当前状态**: 占位符实现 (1分)
- **目标状态**: 完全可用 (5分)
- **成功指标**: 支持PDF和DOCX导出

### 系统设计

#### 1. 核心组件设计

```python
class DocumentConverter:
    """文档转换器"""

    def __init__(self):
        self.pandoc_available = DependencyChecker.check_pandoc()
        self.docx_available = DependencyChecker.check_python_docx()

    async def convert_to_pdf(self, markdown_path: Path, output_path: Path = None) -> ConversionResult:
        """转换为PDF"""

    async def convert_to_docx(self, markdown_path: Path, output_path: Path = None) -> ConversionResult:
        """转换为DOCX"""

    def _convert_with_pandoc(self, input_path: Path, output_path: Path, format: str) -> ConversionResult:
        """使用Pandoc转换"""

    def _convert_with_python_docx(self, markdown_path: Path, output_path: Path) -> ConversionResult:
        """使用python-docx转换"""
```

#### 2. 转换策略设计

```python
class ConversionStrategy:
    """转换策略"""

    @staticmethod
    def get_best_converter(target_format: str, available_tools: List[str]) -> str:
        """获取最佳转换器"""

    @staticmethod
    def create_fallback_content(content: str, format: str) -> bytes:
        """创建降级内容"""
```

### 错误处理策略
1. **工具缺失**: 使用降级策略
2. **转换失败**: 提供详细错误信息
3. **格式不支持**: 明确告知支持格式
4. **大文件处理**: 进度显示 + 超时处理

---

## 🧪 TDD测试策略

### 测试金字塔设计
```
        E2E Tests (5%)
       ─────────────────
    Integration Tests (15%)
   ─────────────────────────
Unit Tests (80%)
```

### 测试设计原则
1. **Arrange-Act-Assert**: 清晰的测试结构
2. **Given-When-Then**: 行为驱动测试
3. **AAA + Mock**: 依赖隔离测试
4. **Property Testing**: 属性验证测试

### 关键测试场景
1. **Wiki管理测试**:
   - 页面创建、编辑、删除
   - 搜索功能验证
   - 权限控制测试
   - 文件系统错误处理

2. **论文下载测试**:
   - Mock arXiv API
   - 文件下载验证
   - 元数据解析测试
   - 网络错误处理

3. **格式转换测试**:
   - 各种输入格式测试
   - 依赖缺失场景
   - 转换质量验证
   - 错误恢复测试

---

## 📊 质量保证策略

### 代码质量标准
1. **类型提示**: 100%类型覆盖
2. **文档字符串**: 所有公共接口
3. **错误处理**: 完整的异常处理
4. **日志记录**: 关键操作日志

### 性能要求
1. **响应时间**: UI操作 < 2秒
2. **下载速度**: 网络限制下的优化
3. **搜索性能**: 千页级搜索 < 1秒
4. **内存使用**: 合理的内存占用

### 安全考虑
1. **文件系统安全**: 路径验证和沙箱
2. **网络安全**: HTTPS和证书验证
3. **权限控制**: 最小权限原则
4. **输入验证**: 严格的输入校验

---

## 🔄 迭代改进计划

### 反馈循环设计
1. **用户反馈**: TUI内反馈机制
2. **性能监控**: 关键指标监控
3. **错误跟踪**: 自动错误报告
4. **使用统计**: 功能使用分析

### 持续改进策略
1. **A/B测试**: 功能效果验证
2. **用户访谈**: 深度需求了解
3. **性能优化**: 基于使用数据优化
4. **功能迭代**: 基于反馈的快速迭代

---

**设计总结**: 本设计文档遵循了BMAD、SPEC、KISS、YAGNI和SOLID原则，确保了系统的可维护性、可扩展性和用户价值。通过分阶段实现和TDD驱动，可以高质量地完成所有缺失功能的开发。