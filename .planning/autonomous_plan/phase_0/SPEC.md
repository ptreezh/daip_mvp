# Phase 0: 地基稳定 (Foundation) - 详细规范

**目标**: 修复基础设施层，使项目具备稳定的构建和日志能力
**时间预算**: 1 周 (全自动执行)
**退出标准**: 干净构建 + 有日志
**Worktree**: `phase-0`

---

## 📋 验收标准 (Definition of Done)

```
┌─────────────────────────────────────────────────────────────┐
│                     Phase 0 验收清单                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ P0-1: SQLAlchemy 2.0 兼容性                              │
│      - persistence/database.py 使用 model_dump()            │
│      - tests/unit/persistence 全通过                         │
│      - 会话保存/加载功能验证通过                              │
│                                                             │
│  ✅ P0-2: 动态 embedding 维度                                │
│      - knowledge/manager.py 从配置读取维度                   │
│      - 支持多种 embedding 模型                              │
│      - 索引加载时验证维度匹配                                 │
│                                                             │
│  ✅ P0-3: 日志基础设施                                        │
│      - container.py 添加 basicConfig                        │
│      - RotatingFileHandler 配置                              │
│      - 日志输出到 data/logs/                                 │
│      - config.yaml 支持日志配置                              │
│                                                             │
│  ✅ P0-4: pyproject 配置修复                                  │
│      - requires-python 正确语法                             │
│      - ruff 可正常解析                                       │
│      - 所有 lint 检查通过                                     │
│                                                             │
│  ✅ 集成验证                                                  │
│      - pytest tests/unit/persistence -v 通过                │
│      - mypy src/daip_live/persistence 无错误                │
│      - ruff check src/ 无警告                                │
│      - daip run 产生日志文件                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 P0-1: SQLAlchemy 2.0 兼容性修复

### 问题诊断

**文件**: `src/daip_live/persistence/database.py:39`

```python
# 当前代码 (有问题)
session_dict = session.dict()  # SQLAlchemy 2.0 已移除此方法
```

### 解决方案 (TDD)

#### 步骤 1: 写测试 (红灯)

创建 `tests/unit/test_persistence_sqlalchemy_compat.py`:

```python
"""SQLAlchemy 2.0 兼容性测试"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from daip_live.persistence.database import DatabaseManager
from daip_live.core.models import AgentSession


def test_session_save_with_pydantic_v2():
    """测试会话保存使用 Pydantic v2 API"""
    db = DatabaseManager("sqlite:///:memory:")
    
    session = AgentSession(
        id="test-session-1",
        user_id="test-user",
        agent_type="chat",
        status="IDLE",
    )
    
    # 应该成功保存
    db.save_session(session)
    
    # 应该成功加载
    loaded = db.get_session("test-session-1")
    assert loaded.id == "test-session-1"
    assert loaded.status == "IDLE"


def test_session_model_dump_compatibility():
    """测试 model_dump() 与 SQLAlchemy 兼容"""
    session = AgentSession(
        id="test-session-2",
        user_id="test-user",
        agent_type="debate",
        status="RUNNING",
    )
    
    # Pydantic v2 的 model_dump() 返回 dict
    session_dict = session.model_dump()
    assert isinstance(session_dict, dict)
    assert session_dict["id"] == "test-session-2"
```

#### 步骤 2: 实现修复 (绿灯)

修改 `src/daip_live/persistence/database.py`:

```python
# 替换 session.dict() 为 session.model_dump()
# 旧代码:
#   session_dict = session.dict()
#   for key, value in session_dict.items():
#       setattr(db_session, key, value)

# 新代码:
def save_session(self, session: AgentSession) -> bool:
    """保存会话到数据库 (Pydantic v2 兼容)"""
    try:
        db_session = self.Session()
        existing = db_session.query(AgentSessionDB).filter(
            AgentSessionDB.id == session.id
        ).first()
        
        if existing:
            # 使用 model_dump() 替代 dict()
            session_dict = session.model_dump()
            for key, value in session_dict.items():
                setattr(existing, key, value)
        else:
            session_db = AgentSessionDB(**session.model_dump())
            db_session.add(session_db)
        
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()
        raise
    finally:
        db_session.close()
```

#### 步骤 3: 重构 (改善)

- 提取 `session_to_dict` 辅助函数
- 添加类型提示
- 更新 docstring

### 验证命令

```bash
# 在 worktree 中执行
cd .git-worktrees/phase-0
poetry run pytest tests/unit/test_persistence_sqlalchemy_compat.py -v
poetry run pytest tests/unit/persistence/ -v
```

---

## 🎯 P0-2: 动态 embedding 维度

### 问题诊断

**文件**: `src/daip_live/knowledge/manager.py:34`

```python
# 当前代码 (硬编码)
self.embedding_dim = 384  # TODO: Make this configurable
```

### 解决方案 (TDD)

#### 步骤 1: 写测试 (红灯)

创建 `tests/unit/test_knowledge_embedding_dimension.py`:

```python
"""Embedding 维度动态配置测试"""
import pytest
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider


def test_embedding_dimension_from_config():
    """测试从配置读取 embedding 维度"""
    config = {
        "embedding_model": "bge-small-en-v1.5",  # 384 维
        "embedding_dimension": 384
    }
    manager = KnowledgeManager(config)
    assert manager.embedding_dim == 384


def test_embedding_dimension_from_provider():
    """测试从 provider 动态获取维度"""
    provider = LiteLLMProvider()
    dimension = provider.get_embedding_dimension("text-embedding-3-small")
    assert dimension == 1536  # OpenAI 模型


def test_index_validation_on_load():
    """测试索引加载时验证维度匹配"""
    # 使用错误的维度应该抛出异常
    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        manager = KnowledgeManager({
            "embedding_dimension": 1536  # 与索引不匹配
        })
        manager.load_index("existing_index.faiss")
```

#### 步骤 2: 实现修复 (绿灯)

修改 `src/daip_live/knowledge/manager.py`:

```python
class KnowledgeManager:
    def __init__(self, config: dict, model_provider: LiteLLMProvider = None):
        self.config = config
        self.model_provider = model_provider or LiteLLMProvider()
        
        # 优先从配置读取，否则从 provider 获取
        self.embedding_dim = config.get("embedding_dimension")
        if self.embedding_dim is None:
            model_name = config.get("embedding_model", "nomic-embed-text")
            self.embedding_dim = self._get_embedding_dimension(model_name)
    
    def _get_embedding_dimension(self, model_name: str) -> int:
        """从 provider 获取 embedding 维度"""
        known_dimensions = {
            "nomic-embed-text": 768,
            "bge-small-en-v1.5": 384,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536,
        }
        if model_name in known_dimensions:
            return known_dimensions[model_name]
        
        # 尝试从 provider 获取
        try:
            return self.model_provider.get_embedding_dimension(model_name)
        except Exception:
            # 默认值
            return 768
    
    def load_index(self, index_path: str) -> bool:
        """加载索引并验证维度"""
        import os
        if not os.path.exists(index_path):
            return False
        
        index = faiss.read_index(index_path)
        index_dim = index.d
        
        # 验证维度匹配
        if index_dim != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch: "
                f"index has {index_dim}D but config expects {self.embedding_dim}D"
            )
        
        self.index = index
        return True
```

#### 步骤 3: 更新配置

更新 `config.yaml`:

```yaml
knowledge_base:
  embedding_model: "nomic-embed-text"
  embedding_dimension: 768  # 明确配置
  index_path: "data/knowledge/index.faiss"
```

### 验证命令

```bash
poetry run pytest tests/unit/test_knowledge_embedding_dimension.py -v
```

---

## 🎯 P0-3: 日志基础设施

### 问题诊断

当前项目无日志配置，20+ 模块使用 `logging.getLogger(__name__)` 但无 handler。

### 解决方案 (TDD)

#### 步骤 1: 写测试 (红灯)

创建 `tests/unit/test_logging_infrastructure.py`:

```python
"""日志基础设施测试"""
import os
import logging
from pathlib import Path


def test_log_file_created():
    """测试日志文件创建"""
    from daip_live.container import Container
    
    # 启动容器应初始化日志
    container = Container()
    
    # 验证日志目录存在
    log_dir = Path("data/logs")
    assert log_dir.exists()
    
    # 验证日志文件创建
    log_file = log_dir / "daip_live.log"
    # 运行一段时间后应该有日志
    assert log_file.exists() or os.path.getsize(log_file) > 0


def test_log_format():
    """测试日志格式"""
    import daip_live.persistence.database
    
    # 获取 logger
    logger = logging.getLogger("daip_live.persistence.database")
    
    # 验证有 handler
    assert len(logger.handlers) > 0
    
    # 验证 handler 是 RotatingFileHandler
    assert any(isinstance(h, logging.handlers.RotatingFileHandler) 
               for h in logger.handlers)


def test_log_rotation():
    """测试日志轮转"""
    from daip_live.config import ConfigManager
    
    config = ConfigManager().get_config()
    assert "logging" in config
    assert "max_bytes" in config["logging"]
    assert "backup_count" in config["logging"]
```

#### 步骤 2: 实现修复 (绿灯)

修改 `src/daip_live/container.py`:

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(config: dict):
    """配置日志系统"""
    log_config = config.get("logging", {})
    
    # 日志目录
    log_dir = Path(log_config.get("dir", "data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 日志级别
    level = log_config.get("level", "INFO")
    
    # 日志格式
    format_str = log_config.get(
        "format",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 文件 handler (轮转)
    max_bytes = log_config.get("max_bytes", 10 * 1024 * 1024)  # 10MB
    backup_count = log_config.get("backup_count", 5)
    
    file_handler = RotatingFileHandler(
        log_dir / "daip_live.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(format_str))
    file_handler.setLevel(level)
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_str))
    console_handler.setLevel(level)
    
    # 全局配置
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


# 在 Container.__init__ 中调用
class Container:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        
        # 设置日志
        setup_logging(self.config)
        
        # ... 其余初始化
```

#### 步骤 3: 更新配置

更新 `config.yaml`:

```yaml
logging:
  dir: "data/logs"
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

### 验证命令

```bash
poetry run pytest tests/unit/test_logging_infrastructure.py -v
daip run  # 应该产生日志文件
cat data/logs/daip_live.log  # 应该有日志内容
```

---

## 🎯 P0-4: pyproject 配置修复

### 问题诊断

`pyproject.toml:11` 中 `requires-python` 表达式 ruff 无法解析。

### 解决方案

#### 修改前

```toml
requires-python = ">=3.9.7,<3.13"  # ruff 无法解析
```

#### 修改后

```toml
requires-python = ">=3.9"  # 简化表达式
```

或者使用标准版本范围：

```toml
requires-python = ">=3.9.7, <3.13.0"
```

### 验证命令

```bash
poetry run ruff check src/ --statistics
# 应该无解析错误
```

---

## 📋 任务清单 (TASKS.md)

| ID | 任务 | 依赖 | 状态 |
|----|------|------|------|
| P0-0.1 | 创建 phase-0 worktree | - | ⏳ |
| P0-1.1 | 写 SQLAlchemy 兼容性测试 | P0-0.1 | ⏳ |
| P0-1.2 | 修复 database.py | P0-1.1 | ⏳ |
| P0-1.3 | 验证 persistence 测试 | P0-1.2 | ⏳ |
| P0-2.1 | 写 embedding 维度测试 | P0-0.1 | ⏳ |
| P0-2.2 | 修复 manager.py | P0-2.1 | ⏳ |
| P0-2.3 | 更新 config.yaml | P0-2.2 | ⏳ |
| P0-3.1 | 写日志测试 | P0-0.1 | ⏳ |
| P0-3.2 | 修复 container.py | P0-3.1 | ⏳ |
| P0-3.3 | 更新 config.yaml 日志配置 | P0-3.2 | ⏳ |
| P0-4.1 | 修复 pyproject.toml | P0-0.1 | ⏳ |
| P0-5.1 | 运行全量验证 | 全部 | ⏳ |
| P0-5.2 | 合并到主分支 | P0-5.1 | ⏳ |

---

## 🔧 执行命令 (自动化)

```bash
#!/bin/bash
# Phase 0 自动执行脚本

set -e  # 遇到错误立即退出

# 1. 创建 worktree
echo "Creating phase-0 worktree..."
git worktree add ../daip-live-phase-0 -b phase-0
cd ../daip-live-phase-0

# 2. 安装依赖
echo "Installing dependencies..."
poetry install

# 3. P0-1: SQLAlchemy 兼容性
echo "P0-1: Fixing SQLAlchemy 2.0 compatibility..."
# 创建测试文件...
# 修复 database.py...
poetry run pytest tests/unit/test_persistence_sqlalchemy_compat.py -v

# 4. P0-2: Embedding 维度
echo "P0-2: Making embedding dimension dynamic..."
# 创建测试文件...
# 修复 manager.py...
poetry run pytest tests/unit/test_knowledge_embedding_dimension.py -v

# 5. P0-3: 日志基础设施
echo "P0-3: Setting up logging infrastructure..."
# 创建测试文件...
# 修复 container.py...
poetry run pytest tests/unit/test_logging_infrastructure.py -v

# 6. P0-4: pyproject 配置
echo "P0-4: Fixing pyproject.toml..."
# 修复 requires-python
poetry run ruff check src/

# 7. 全量验证
echo "Running full validation..."
poetry run pytest tests/unit/persistence/ -v
poetry run mypy src/daip_live/persistence
poetry run ruff check src/

# 8. 提交
echo "Committing changes..."
git add .
git commit -m "phase-0: foundation stabilization

- SQLAlchemy 2.0 compatibility (model_dump)
- Dynamic embedding dimension
- Logging infrastructure
- pyproject.toml fixes"

# 9. 合并到主分支
echo "Merging to main branch..."
git checkout gnhf/-055e31
git merge phase-0 --no-ff

echo "Phase 0 completed!"
```

---

## 📊 进度跟踪 (PROGRESS.md)

```markdown
# Phase 0 进度跟踪

## 时间线
- 开始: (待定)
- P0-1 完成: (待定)
- P0-2 完成: (待定)
- P0-3 完成: (待定)
- P0-4 完成: (待定)
- Phase 0 完成: (待定)

## 验证结果
| 检查项 | 目标 | 实际 | 状态 |
|--------|------|------|------|
| persistence 测试 | 全通过 | - | ⏳ |
| mypy persistence | 无错误 | - | ⏳ |
| ruff check | 无警告 | - | ⏳ |
| 日志文件 | 存在 | - | ⏳ |
| 生产就绪评分 | 45/100 | - | ⏳ |
```

---

*Phase 0 规范完成。等待 grill-down 验证后执行。*
