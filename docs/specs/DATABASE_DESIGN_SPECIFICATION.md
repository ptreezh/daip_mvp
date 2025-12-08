# 数据库设计说明书 (单机版)

## 1. 概述

本文档详细描述了DAIP-LIVE（单机版）的本地数据存储方案。为对齐单机、单用户、零外部依赖的目标，系统采用以 **SQLite** 和 **本地文件** 为核心的轻量级持久化策略。

## 2. 数据存储架构

### 2.1 技术选型
- **结构化数据**: **SQLite**。一个单一的数据库文件（例如 `data/daip.db`）存储所有关系型数据，无需安装和运行数据库服务。
- **向量化知识**: **嵌入式向量数据库 (如 FAISS, ChromaDB)**。向量索引直接以文件形式存储在本地（例如 `data/vector_store/`），随应用启动加载。
- **配置**: **YAML 或 JSON 文件** (例如 `config.yaml`)。用于存储系统设置、模型偏好等。
- **日志**: **纯文本文件** (例如 `logs/app.log`)。

### 2.2 数据文件结构
```
/your_project_root
├── data/
│   ├── daip.db              # SQLite数据库文件
│   └── vector_store/        # 向量索引文件目录
│       ├── faiss.index
│       └── ...
├── knowledge/               # 用户存放的原始知识文档
│   ├── doc1.md
│   └── report.pdf
├── logs/
│   └── app.log              # 应用日志
└── config.yaml              # 主配置文件
```

## 3. SQLite 数据库设计 (`daip.db`)

所有表都将在一个SQLite数据库文件中。主键建议使用自增整数（INTEGER PRIMARY KEY）以获得最佳性能，或在需要时使用UUID的文本表示（TEXT）。

### 3.1 角色管理模块

#### 3.1.1 角色表 (roles)
| 字段名 | 数据类型 | 约束 | 描述 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 角色唯一标识符 |
| name | TEXT | UNIQUE, NOT NULL | 角色名称 |
| description | TEXT | | 角色描述 |
| capabilities | TEXT | | 角色能力列表 (JSON格式存储) |
| personality | TEXT | | 角色个性配置 (JSON格式存储) |
| prompt_template | TEXT | | 提示词模板 |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |
| updated_at | TEXT | NOT NULL | 更新时间 (ISO 8601) |

### 3.2 会话管理模块

#### 3.2.1 会话表 (sessions)
| 字段名 | 数据类型 | 约束 | 描述 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 会话唯一标识符 |
| title | TEXT | NOT NULL | 会话标题 |
| type | TEXT | NOT NULL | 会话类型 (chat/debate/workflow) |
| status | TEXT | NOT NULL | 会话状态 (active/completed) |
| context_summary | TEXT | | 会话上下文摘要（长期记忆） |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |
| updated_at | TEXT | NOT NULL | 更新时间 (ISO 8601) |

#### 3.2.2 消息表 (messages)
| 字段名 | 数据类型 | 约束 | 描述 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 消息唯一标识符 |
| session_id | INTEGER | FK(sessions.id), NOT NULL | 关联会话ID |
| sender_name | TEXT | NOT NULL | 发送者名称 (角色名或'user') |
| content | TEXT | NOT NULL | 消息内容 |
| metadata | TEXT | | 消息元数据 (JSON格式存储) |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |

### 3.3 Agent执行引擎模块

#### 3.3.1 Todo任务表 (todos)
此表用于存储Agent为自己制定的任务计划，是实现自主规划的核心。

| 字段名 | 数据类型 | 约束 | 描述 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 任务唯一标识符 |
| session_id | INTEGER | FK(sessions.id), NOT NULL | 关联的会话ID |
| parent_id | INTEGER | FK(todos.id) | 父任务ID，用于支持子任务结构 |
| description | TEXT | NOT NULL | 任务的自然语言描述 |
| status | TEXT | NOT NULL | 任务状态 (pending/in_progress/completed/failed) |
| priority | TEXT | DEFAULT 'medium' | 任务优先级 (high/medium/low) |
| result_json | TEXT | | 任务完成后的结果，以JSON格式存储 |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |
| updated_at | TEXT | NOT NULL | 最后更新时间 (ISO 8601) |

### 3.4 静态工作流管理模块 (可选)

#### 3.4.1 工作流定义表 (workflows)
| 字段名 | 数据类型 | 约束 | 描述 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 工作流唯一标识符 |
| name | TEXT | UNIQUE, NOT NULL | 工作流名称 |
| description | TEXT | | 工作流描述 |
| definition | TEXT | NOT NULL | 工作流定义 (JSON格式存储) |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |
| updated_at | TEXT | NOT NULL | 更新时间 (ISO 8601) |

#### 3.3.2 工作流执行实例表 (workflow_executions)
| 字段名 | 数据类型 | 约束 | 描述 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 执行实例唯一标识符 |
| workflow_id | INTEGER | FK(workflows.id), NOT NULL | 关联工作流ID |
| status | TEXT | NOT NULL | 执行状态 (running/completed/failed) |
| inputs | TEXT | | 输入参数 (JSON格式存储) |
| outputs | TEXT | | 输出结果 (JSON格式存储) |
| started_at | TEXT | | 开始时间 (ISO 8601) |
| completed_at | TEXT | | 完成时间 (ISO 8601) |

### 3.4 知识库元数据模块

#### 3.4.1 知识源文件表 (knowledge_sources)
此表用于追踪知识库中的源文件及其处理状态。

| 字段名 | 数据类型 | 约束 | 描述 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 文件唯一标识符 |
| file_path | TEXT | UNIQUE, NOT NULL | 文件在本地的绝对路径 |
| file_hash | TEXT | NOT NULL | 文件内容的哈希值 (用于检测变更) |
| status | TEXT | NOT NULL | 处理状态 (indexed/pending/error) |
| indexed_at | TEXT | | 最新索引时间 (ISO 8601) |
| created_at | TEXT | NOT NULL | 首次发现时间 (ISO 8601) |

## 4. 嵌入式向量数据库设计

向量数据库不使用独立的表结构，而是作为一个“黑盒”文件存储。其内部逻辑由选择的库（如FAISS, ChromaDB）管理。我们需要定义的是存储在其中的数据结构。

### 4.1 知识块 (Knowledge Chunk)
当知识管理器处理一个源文件时，会将其切分成多个“块”（Chunk），每个块作为一个独立的条目存入向量数据库。

| 属性名 | 数据类型 | 描述 |
|---|---|---|
| chunk_id | TEXT | 块的唯一标识符 (例如 `file_id:chunk_index`) |
| source_file_id | INTEGER | 关联的源文件ID (knowledge_sources.id) |
| content | TEXT | 块的原文内容 |
| embedding | FLOAT[] | 内容对应的向量表示 |
| metadata | TEXT | 元数据 (如页码、章节等，JSON格式) |

## 5. 数据安全与备份

### 5.1 数据安全
- 由于是单机应用，主要的安全风险来自对本地文件的未授权访问。操作系统本身的文件权限是第一道防线。
- 如果配置文件中包含敏感的API密钥，应建议用户使用操作系统的密钥管理工具（如Windows Credential Manager, macOS Keychain）或环境变量，而不是明文存储在`config.yaml`中。

### 5.2 数据备份
- **策略**: 备份变得非常简单。用户只需定期复制包含所有数据文件的根目录（或`data/`目录）即可完成一次完整的系统备份。
- **恢复**: 将备份的文件和目录直接覆盖回去即可完成恢复。

## 6. 性能与优化

### 6.1 索引优化 (SQLite)
- 在所有外键字段（如`messages.session_id`）上创建索引。
- 在经常用于查询的字段（如`sessions.status`）上创建索引。
- SQLite的`ANALYZE`命令可以定期运行以优化查询计划。

### 6.2 查询优化
- 避免在代码中进行大量的N+1查询，合理使用`JOIN`。
- 对于频繁访问且不常变动的数据（如角色配置），可以在应用启动时加载到内存中，避免重复的数据库查询。
