# CLI命令实现计划和技术架构

基于spec-kit原则，本文档提供DAIP-LIVE缺失CLI命令的详细实施计划，确保无歧义、可执行、可验证。

## 1. 实施概述

### 1.1 项目目标
补充DAIP-LIVE系统中缺失的5个关键CLI命令，实现完整的系统管理功能：
- `daip model list` - 模型管理
- `daip session list` / `daip session clear` - 会话管理
- `daip role list` - 角色管理
- `daip knowledge sync` - 知识管理

### 1.2 实施原则
- **TDD驱动**: 测试优先，确保质量
- **模块化设计**: 每个命令独立实现，易于维护
- **统一接口**: 遵循相同的API设计模式
- **错误处理**: 完善的异常处理和用户反馈
- **性能优化**: 响应时间控制在3秒以内

## 2. 技术架构设计

### 2.1 整体架构图
```
┌─────────────────────────────────────────────────────────┐
│                 CLI Layer (Typer)                        │
├─────────────────────────────────────────────────────────┤
│  daip model list  │ daip session │ daip role │ daip sync│
├─────────────────────────────────────────────────────────┤
│              Command Implementation Layer                 │
├─────────────────────────────────────────────────────────┤
│  ModelService  │ SessionService │ RoleService │ SyncService│
├─────────────────────────────────────────────────────────┤
│              Data Access Layer                           │
├─────────────────────────────────────────────────────────┤
│  LiteLLM API  │ SQLite DB  │ Config Files │ FileSystem │
└─────────────────────────────────────────────────────────┘
```

### 2.2 模块依赖关系
```
cli.py (入口点)
├── commands/
│   ├── model_commands.py (模型相关命令)
│   ├── session_commands.py (会话相关命令)
│   ├── role_commands.py (角色相关命令)
│   └── knowledge_commands.py (知识管理命令)
├── services/
│   ├── model_service.py (模型服务)
│   ├── session_service.py (会话服务)
│   ├── role_service.py (角色服务)
│   └── knowledge_service.py (知识同步服务)
└── utils/
    ├── output_formatter.py (输出格式化)
    └── error_handler.py (错误处理)
```

### 2.3 数据流设计
```
用户输入命令 → 参数验证 → 服务层调用 → 数据访问 → 结果处理 → 格式化输出
```

## 3. 详细实施计划

### 3.1 第一阶段：基础设施搭建 (1-2天)

#### 3.1.1 目录结构创建
```bash
src/daip_live/cli/
├── __init__.py
├── commands/
│   ├── __init__.py
│   ├── model_commands.py
│   ├── session_commands.py
│   ├── role_commands.py
│   └── knowledge_commands.py
├── services/
│   ├── __init__.py
│   ├── model_service.py
│   ├── session_service.py
│   ├── role_service.py
│   └── knowledge_service.py
└── utils/
    ├── __init__.py
    ├── output_formatter.py
    └── error_handler.py
```

#### 3.1.2 基础工具类实现

##### 输出格式化器 (output_formatter.py)
```python
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from typing import List, Dict, Any, Optional
import json

class OutputFormatter:
    """统一的输出格式化器"""

    def __init__(self):
        self.console = Console()

    def format_table(self, data: List[Dict[str, Any]], title: str) -> None:
        """格式化表格输出"""
        pass

    def format_tree(self, data: Dict[str, Any], title: str) -> None:
        """格式化树形结构输出"""
        pass

    def format_json(self, data: Any) -> str:
        """格式化JSON输出"""
        return json.dumps(data, indent=2, ensure_ascii=False)

    def format_success(self, message: str) -> None:
        """格式化成功消息"""
        self.console.print(f"✅ {message}")

    def format_error(self, message: str) -> None:
        """格式化错误消息"""
        self.console.print(f"❌ {message}")

    def format_warning(self, message: str) -> None:
        """格式化警告消息"""
        self.console.print(f"⚠️  {message}")
```

##### 错误处理器 (error_handler.py)
```python
import logging
from typing import Optional, Callable, Any
from functools import wraps

class CLIError(Exception):
    """CLI命令专用异常"""
    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)

def handle_errors(func: Callable) -> Callable:
    """错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except CLIError as e:
            logging.error(f"CLI Error: {e.message}")
            print(f"❌ Error: {e.message}")
            raise typer.Exit(e.exit_code)
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            print(f"❌ Unexpected error: {str(e)}")
            if '--verbose' in sys.argv:
                import traceback
                traceback.print_exc()
            raise typer.Exit(1)
    return wrapper
```

### 3.2 第二阶段：模型管理命令实现 (2-3天)

#### 3.2.1 模型服务层 (model_service.py)

```python
from typing import List, Dict, Any, Optional
import asyncio
import litellm
from pathlib import Path

class ModelService:
    """模型管理服务"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_available_models(
        self,
        model_type: str = "all",
        status_filter: str = "available"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取可用模型列表

        Args:
            model_type: 模型类型过滤 (local/cloud/all)
            status_filter: 状态过滤 (available/all)

        Returns:
            包含本地模型和云端模型的字典
        """
        models = {
            "local": [],
            "cloud": []
        }

        # 获取云端模型
        if model_type in ["cloud", "all"]:
            try:
                cloud_models = await self._get_cloud_models()
                if status_filter == "available":
                    cloud_models = [m for m in cloud_models if m.get("available", False)]
                models["cloud"] = cloud_models
            except Exception as e:
                self.logger.warning(f"Failed to get cloud models: {e}")

        # 获取本地模型
        if model_type in ["local", "all"]:
            try:
                local_models = await self._get_local_models()
                if status_filter == "available":
                    local_models = [m for m in local_models if m.get("available", False)]
                models["local"] = local_models
            except Exception as e:
                self.logger.warning(f"Failed to get local models: {e}")

        return models

    async def _get_cloud_models(self) -> List[Dict[str, Any]]:
        """获取云端模型列表"""
        try:
            model_list = litellm.model_list
            return [
                {
                    "name": model,
                    "provider": self._get_provider_from_model(model),
                    "available": True,
                    "type": "cloud"
                }
                for model in model_list
            ]
        except Exception as e:
            self.logger.error(f"Failed to get cloud models from litellm: {e}")
            return []

    async def _get_local_models(self) -> List[Dict[str, Any]]:
        """获取本地模型列表"""
        local_models = []
        models_dir = Path("./data/models")

        if models_dir.exists():
            for model_file in models_dir.rglob("*"):
                if model_file.is_file() and self._is_model_file(model_file):
                    model_name = self._extract_model_name(model_file)
                    local_models.append({
                        "name": model_name,
                        "path": str(model_file),
                        "available": True,
                        "type": "local"
                    })

        return local_models

    def _get_provider_from_model(self, model_name: str) -> str:
        """从模型名称推断提供商"""
        if "gpt" in model_name.lower():
            return "OpenAI"
        elif "claude" in model_name.lower():
            return "Anthropic"
        elif "gemini" in model_name.lower():
            return "Google"
        else:
            return "Unknown"

    def _is_model_file(self, file_path: Path) -> bool:
        """判断是否为模型文件"""
        model_extensions = {".bin", ".gguf", ".safetensors", ".pth"}
        return file_path.suffix in model_extensions

    def _extract_model_name(self, file_path: Path) -> str:
        """从文件路径提取模型名称"""
        return file_path.stem
```

#### 3.2.2 模型命令实现 (model_commands.py)

```python
import typer
from typing import Optional
from ..services.model_service import ModelService
from ..utils.output_formatter import OutputFormatter
from ..utils.error_handler import handle_errors, CLIError

# 创建模型命令应用
model_app = typer.Typer(help="模型管理命令")

@model_app.command("list")
@handle_errors
async def model_list(
    type: Optional[str] = typer.Option(
        "all",
        "--type",
        help="过滤模型类型 (local/cloud/all)"
    ),
    status: Optional[str] = typer.Option(
        "available",
        "--status",
        help="过滤可用状态 (available/all)"
    ),
    format: Optional[str] = typer.Option(
        "table",
        "--format",
        help="输出格式 (table/json)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="显示详细信息"
    )
):
    """列出系统中所有可用的AI模型"""

    # 验证参数
    if type not in ["local", "cloud", "all"]:
        raise CLIError("Invalid type. Must be one of: local, cloud, all")

    if status not in ["available", "all"]:
        raise CLIError("Invalid status. Must be one of: available, all")

    if format not in ["table", "json"]:
        raise CLIError("Invalid format. Must be one of: table, json")

    # 获取模型列表
    model_service = ModelService()
    formatter = OutputFormatter()

    models_data = await model_service.get_available_models(type, status)

    # 格式化输出
    if format == "json":
        print(formatter.format_json(models_data))
    else:
        formatter.format_model_table(models_data, verbose)
```

### 3.3 第三阶段：会话管理命令实现 (2-3天)

#### 3.3.1 会话服务层 (session_service.py)

```python
from typing import List, Dict, Any, Optional
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

class SessionService:
    """会话管理服务"""

    def __init__(self, db_path: str = "data/daip_live.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    async def list_sessions(
        self,
        session_type: str = "all",
        status_filter: str = "all",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取会话列表

        Args:
            session_type: 会话类型过滤 (chat/debate/all)
            status_filter: 状态过滤 (active/completed/all)
            limit: 限制返回数量

        Returns:
            会话列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 构建查询条件
                conditions = []
                params = []

                if session_type != "all":
                    conditions.append("session_type = ?")
                    params.append(session_type)

                if status_filter != "all":
                    conditions.append("status = ?")
                    params.append(status_filter)

                where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
                limit_clause = f" LIMIT {limit}" if limit else ""

                query = f"""
                SELECT
                    session_id,
                    created_at,
                    session_type,
                    status,
                    message_count,
                    metadata
                FROM sessions
                {where_clause}
                ORDER BY created_at DESC
                {limit_clause}
                """

                cursor.execute(query, params)
                rows = cursor.fetchall()

                sessions = []
                for row in rows:
                    sessions.append({
                        "session_id": row[0],
                        "created_at": row[1],
                        "session_type": row[2],
                        "status": row[3],
                        "message_count": row[4] or 0,
                        "metadata": json.loads(row[5]) if row[5] else {}
                    })

                return sessions

        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return []

    async def clear_all_sessions(
        self,
        backup_before: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        清空所有会话

        Args:
            backup_before: 清空前创建备份
            dry_run: 仅显示将要删除的内容

        Returns:
            操作结果
        """
        try:
            # 获取将要删除的会话统计
            sessions = await self.list_sessions(limit=None)
            total_sessions = len(sessions)
            total_messages = sum(s.get("message_count", 0) for s in sessions)

            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "sessions_to_delete": total_sessions,
                    "messages_to_delete": total_messages,
                    "sessions": sessions
                }

            # 创建备份
            backup_path = None
            if backup_before:
                backup_path = await self._create_backup()

            # 执行删除
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 删除会话相关记录
                cursor.execute("DELETE FROM session_messages")
                cursor.execute("DELETE FROM sessions")

                # 重置自增ID
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='sessions'")

                conn.commit()

            return {
                "success": True,
                "backup_path": backup_path,
                "deleted_sessions": total_sessions,
                "deleted_messages": total_messages
            }

        except sqlite3.Error as e:
            self.logger.error(f"Database error during clear: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_backup(self) -> str:
        """创建数据库备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/backups/daip_live_backup_{timestamp}.db"

        Path("data/backups").mkdir(exist_ok=True)

        import shutil
        shutil.copy2(self.db_path, backup_path)

        self.logger.info(f"Database backup created: {backup_path}")
        return backup_path
```

### 3.4 第四阶段：角色和知识管理命令实现 (2-3天)

#### 3.4.1 角色服务层 (role_service.py)

```python
from typing import List, Dict, Any, Optional
import yaml
import json
from pathlib import Path

class RoleService:
    """角色管理服务"""

    def __init__(self, roles_dir: str = "data/roles"):
        self.roles_dir = Path(roles_dir)
        self.logger = logging.getLogger(__name__)

    async def list_roles(
        self,
        role_type: str = "all",
        model_filter: Optional[str] = None,
        validate_config: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取角色列表

        Args:
            role_type: 角色类型过滤 (debate/expert/all)
            model_filter: 过滤使用指定模型的角色
            validate_config: 是否验证角色配置

        Returns:
            角色列表
        """
        roles = []

        if not self.roles_dir.exists():
            self.logger.warning(f"Roles directory not found: {self.roles_dir}")
            return roles

        for role_file in self.roles_dir.rglob("*.yaml"):
            try:
                role_data = await self._load_role_config(role_file)

                if role_type != "all" and role_data.get("type") != role_type:
                    continue

                if model_filter and role_data.get("model") != model_filter:
                    continue

                if validate_config:
                    validation_result = await self._validate_role_config(role_data)
                    role_data["validation"] = validation_result

                role_data["config_file"] = str(role_file)
                roles.append(role_data)

            except Exception as e:
                self.logger.error(f"Failed to load role from {role_file}: {e}")

        return roles

    async def _load_role_config(self, config_file: Path) -> Dict[str, Any]:
        """加载角色配置文件"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    async def _validate_role_config(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证角色配置"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        required_fields = ["name", "description", "type", "model"]
        for field in required_fields:
            if field not in role_data:
                validation["errors"].append(f"Missing required field: {field}")
                validation["valid"] = False

        return validation
```

#### 3.4.2 知识同步服务层 (knowledge_service.py)

```python
from typing import List, Dict, Any, Optional
import asyncio
from pathlib import Path
import logging

class KnowledgeService:
    """知识库同步服务"""

    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.logger = logging.getLogger(__name__)

    async def sync_knowledge_base(
        self,
        force: bool = False,
        dry_run: bool = False,
        batch_size: int = 10,
        embedding_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        同步知识库

        Args:
            force: 强制完全重新同步
            dry_run: 仅显示将要处理的内容
            batch_size: 批处理大小
            embedding_model: 指定嵌入模型

        Returns:
            同步结果
        """
        sync_result = {
            "success": False,
            "processed_files": 0,
            "error_files": 0,
            "generated_embeddings": 0,
            "errors": []
        }

        try:
            # 扫描文档文件
            documents = await self._scan_documents()

            if dry_run:
                sync_result.update({
                    "success": True,
                    "dry_run": True,
                    "files_to_process": len(documents),
                    "documents": documents
                })
                return sync_result

            # 处理文档
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                await self._process_document_batch(batch, embedding_model)
                sync_result["processed_files"] += len(batch)

            sync_result["success"] = True

        except Exception as e:
            sync_result["errors"].append(str(e))
            self.logger.error(f"Knowledge sync error: {e}")

        return sync_result

    async def _scan_documents(self) -> List[Dict[str, Any]]:
        """扫描知识库目录中的文档"""
        documents = []
        supported_extensions = {".pdf", ".md", ".txt", ".docx"}

        for file_path in self.knowledge_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in supported_extensions:
                documents.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "type": file_path.suffix,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })

        return documents

    async def _process_document_batch(
        self,
        documents: List[Dict[str, Any]],
        embedding_model: Optional[str]
    ):
        """处理文档批次"""
        # 这里需要集成实际的文档处理和向量化逻辑
        # 暂时使用模拟实现
        for doc in documents:
            try:
                # 模拟文档处理
                await asyncio.sleep(0.1)  # 模拟处理时间
                self.logger.info(f"Processed document: {doc['name']}")
            except Exception as e:
                self.logger.error(f"Failed to process {doc['name']}: {e}")
```

## 4. 测试策略

### 4.1 单元测试结构
```
tests/
├── cli/
│   ├── test_model_commands.py
│   ├── test_session_commands.py
│   ├── test_role_commands.py
│   └── test_knowledge_commands.py
├── services/
│   ├── test_model_service.py
│   ├── test_session_service.py
│   ├── test_role_service.py
│   └── test_knowledge_service.py
└── utils/
    ├── test_output_formatter.py
    └── test_error_handler.py
```

### 4.2 测试覆盖率要求
- 每个命令函数: 100% 覆盖率
- 每个服务方法: 95%+ 覆盖率
- 错误处理场景: 100% 覆盖率
- 边界条件测试: 100% 覆盖率

### 4.3 性能测试要求
- 命令响应时间: < 3秒
- 大数据集处理: 1000+记录
- 内存使用: < 100MB
- 并发支持: 10+ 同时调用

## 5. 部署和集成

### 5.1 集成步骤
1. 将新命令集成到主CLI应用
2. 更新帮助文档和man页面
3. 添加到CI/CD流水线
4. 执行集成测试
5. 用户验收测试

### 5.2 向后兼容性
- 保持现有命令接口不变
- 新增选项使用默认值
- 错误信息向后兼容
- 支持旧版配置文件

## 6. 风险评估和缓解

### 6.1 技术风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 依赖API变更 | 中 | 高 | 使用版本锁定，实现适配器 |
| 性能问题 | 低 | 中 | 性能测试，优化查询 |
| 数据损坏 | 低 | 高 | 备份机制，事务处理 |

### 6.2 业务风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 用户体验下降 | 低 | 中 | 用户测试，反馈收集 |
| 命令不一致 | 中 | 低 | 统一接口设计，代码审查 |

## 7. 成功标准

### 7.1 功能标准
- [ ] 所有5个命令完全可用
- [ ] 输出格式符合规范
- [ ] 错误处理完善
- [ ] 帮助信息清晰

### 7.2 质量标准
- [ ] 代码覆盖率 > 90%
- [ ] 所有测试通过
- [ ] 性能指标达标
- [ ] 安全审查通过

### 7.3 用户体验标准
- [ ] 命令易于使用
- [ ] 输出信息有用
- [ ] 错误信息友好
- [ ] 响应时间满意

---

## 实施时间表

- **第1周**: 基础设施搭建 + 模型管理命令
- **第2周**: 会话管理命令 + 测试
- **第3周**: 角色和知识管理命令 + 集成测试
- **第4周**: 文档完善 + 用户验收测试 + 部署

总预计时间：**4周**