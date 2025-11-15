# CLI命令功能规范文档

本文档基于spec-kit原则，为DAIP-LIVE系统中缺失的CLI命令制定详细、无歧义的功能规范。

## 1. DAIP-LIVE CLI命令完整性规范

### 1.1 当前状况分析

#### 1.1.1 现有可用命令
```bash
daip run                    # 启动TUI界面 - ✅ 可用
daip debate start <topic>   # 开始辩论 - ✅ 可用
daip debate multimodel      # 多模型辩论 - ✅ 可用
daip debate history        # 查看辩论历史 - ✅ 可用
daip doc download          # 下载文档 - ✅ 可用
daip doc search            # 搜索文档 - ✅ 可用
```

#### 1.1.2 缺失的必需命令
```bash
daip model list            # 列出可用模型 - ❌ 缺失
daip session list          # 列出会话 - ❌ 缺失
daip session clear         # 清空会话 - ❌ 缺失
daip role list             # 列出角色 - ❌ 缺失
daip knowledge sync        # 同步知识库 - ❌ 缺失
```

### 1.2 功能完整性要求

#### 1.2.1 系统管理功能完整性
- **模型管理**: 用户必须能够查看系统配置的所有AI模型
- **会话管理**: 用户必须能够查看和管理历史会话记录
- **角色管理**: 用户必须能够查看系统配置的AI角色
- **知识管理**: 用户必须能够手动同步知识库

#### 1.2.2 用户体验一致性要求
- 所有命令必须遵循统一的输出格式
- 所有命令必须包含帮助信息
- 所有命令必须支持错误处理
- 所有命令必须支持详细的调试输出

## 2. 命令规范详细定义

### 2.1 `daip model list` 命令规范

#### 2.1.1 功能定义
列出系统中所有可用的AI模型，包括本地模型和云端模型。

#### 2.1.2 输出格式规范
```
Available Models List
├── Local Models
│   ├── llama2:7b (available) - /models/llama2-7b
│   ├── codellama:7b (available) - /models/codellama-7b
│   └── mistral:7b (unavailable) - /models/mistral-7b
└── Cloud Models
    ├── gpt-3.5-turbo (available) - OpenAI
    ├── gpt-4 (available) - OpenAI
    └── claude-3-sonnet (available) - Anthropic

Total: 6 models (3 local, 3 cloud)
```

#### 2.1.3 技术实现要求
- 调用 `litellm.model_list` 获取可用模型列表
- 检查本地模型文件是否存在
- 验证云端模型的API密钥配置
- 支持过滤和排序选项

#### 2.1.4 命令行选项
```bash
daip model list [OPTIONS]
  --type [local|cloud|all]  # 过滤模型类型，默认: all
  --status [available|all]  # 过滤可用状态，默认: available
  --format [table|json]     # 输出格式，默认: table
  --verbose                 # 显示详细信息
```

### 2.2 `daip session list` 命令规范

#### 2.2.1 功能定义
显示系统中所有记录的会话历史记录，包括会话ID、创建时间、状态等。

#### 2.2.2 输出格式规范
```
Recorded Sessions List
┌─────────────────────────┬──────────────┬──────────┬─────────────┬──────────────┐
│ Session ID              │ Created Time │ Type     │ Status      │ Message Count│
├─────────────────────────┼──────────────┼──────────┼─────────────┼──────────────┤
│ 2024-01-15-debate-001   │ 2024-01-15   │ debate   │ completed   │ 24           │
│ 2024-01-15-chat-001     │ 2024-01-15   │ chat     │ active      │ 8            │
│ 2024-01-14-debate-002   │ 2024-01-14   │ debate   │ completed   │ 16           │
└─────────────────────────┴──────────────┴──────────┴─────────────┴──────────────┘

Total: 3 sessions (2 completed, 1 active)
```

#### 2.2.3 技术实现要求
- 从SQLite数据库查询会话记录
- 显示会话基本信息和统计
- 支持按时间、类型、状态过滤
- 支持详细信息查看

#### 2.2.4 命令行选项
```bash
daip session list [OPTIONS]
  --type [chat|debate|all]   # 过滤会话类型，默认: all
  --status [active|completed|all]  # 过滤会话状态，默认: all
  --limit N                 # 限制显示数量，默认: 20
  --format [table|json]     # 输出格式，默认: table
  --session-id ID           # 显示特定会话详情
```

### 2.3 `daip session clear` 命令规范

#### 2.3.1 功能定义
清空系统中的所有会话记录，包含确认机制防止误操作。

#### 2.3.2 交互流程规范
```
$ daip session clear
⚠️  WARNING: This will permanently delete ALL session records.
This includes:
- Chat histories
- Debate transcripts
- Model interaction logs
- Session metadata

Affected sessions: 3
Total messages to delete: 48

Type 'DELETE ALL SESSIONS' to confirm: [ ]
```

#### 2.3.3 技术实现要求
- 删除数据库中的会话相关记录
- 删除相关的文件系统数据
- 提供回滚机制（可选）
- 记录删除操作日志

#### 2.3.4 命令行选项
```bash
daip session clear [OPTIONS]
  --force                   # 跳过确认提示
  --backup-before-clear     # 清空前创建备份
  --dry-run                 # 显示将要删除的内容，不实际执行
```

### 2.4 `daip role list` 命令规范

#### 2.4.1 功能定义
显示系统中所有配置的AI角色，包括角色描述和模型配置。

#### 2.4.2 输出格式规范
```
Available Roles List
├── Debate Roles
│   ├── pro_arguer - "Supports the given topic with logical arguments"
│   │   └── Model: llama2:7b
│   ├── con_arguer - "Opposes the given topic with counter-arguments"
│   │   └── Model: mistral:7b
│   └── moderator - "Moderates debate discussions neutrally"
│       └── Model: gpt-3.5-turbo
└── Expert Roles
    ├── economist - "Analyzes economic impacts and policies"
    │   └── Model: gpt-4
    └── policymaker - "Evaluates policy implications"
        └── Model: claude-3-sonnet

Total: 5 roles (3 debate, 2 expert)
```

#### 2.4.3 技术实现要求
- 从角色配置文件读取角色定义
- 显示角色描述和模型映射
- 验证角色配置的完整性
- 支持角色配置验证

#### 2.4.4 命令行选项
```bash
daip role list [OPTIONS]
  --type [debate|expert|all]    # 过滤角色类型，默认: all
  --model MODEL                 # 显示使用指定模型的角色
  --format [table|json|detail]  # 输出格式，默认: table
  --validate                    # 验证角色配置完整性
```

### 2.5 `daip knowledge sync` 命令规范

#### 2.5.1 功能定义
手动同步知识库，重新索引文档并更新向量数据库。

#### 2.5.2 输出格式规范
```
Knowledge Base Synchronization
├── Scanning directories
│   └── ./data/knowledge ... [23 files found]
├── Processing documents
│   ├── PDF files ... [12 processed]
│   ├── Markdown files ... [8 processed]
│   └── Text files ... [3 processed]
├── Updating vector database
│   └── Embeddings generated ... [156 vectors]
└── Building search index
    └── Index created successfully

✅ Sync completed: 23 documents, 156 vectors, 0 errors
```

#### 2.5.3 技术实现要求
- 扫描知识库目录变更
- 重新处理新增或修改的文档
- 更新向量嵌入数据库
- 重建搜索索引
- 处理错误和重试机制

#### 2.5.4 命令行选项
```bash
daip knowledge sync [OPTIONS]
  --force                    # 强制完全重新同步
  --dry-run                  # 显示将要同步的内容，不实际执行
  --batch-size N             # 批处理大小，默认: 10
  --embedding-model MODEL    # 指定嵌入模型，默认: 使用默认模型
  --parallel-threads N       # 并行处理线程数，默认: 4
```

## 3. 实现技术规范

### 3.1 代码结构要求
- 所有CLI命令必须实现为单独的函数
- 使用typer装饰器定义命令接口
- 实现统一的错误处理机制
- 遵循异步编程模式（当需要时）

### 3.2 输出格式标准
- 使用Rich库进行格式化输出
- 统一的表格格式和颜色方案
- 支持JSON输出用于脚本集成
- 国际化支持（可选）

### 3.3 错误处理规范
- 所有命令必须捕获和处理异常
- 提供用户友好的错误信息
- 支持调试模式输出详细错误
- 记录错误日志

### 3.4 测试要求
- 每个命令必须有对应的单元测试
- 集成测试验证完整功能
- 性能测试确保响应时间
- 错误场景测试

## 4. 验收标准

### 4.1 功能验收标准
- 所有5个缺失命令完全可用
- 输出格式符合规范定义
- 错误处理机制正常工作
- 性能满足要求（响应时间<3秒）

### 4.2 质量验收标准
- 代码覆盖率 > 90%
- 通过所有静态代码分析
- 遵循项目编码规范
- 文档完整且准确

### 4.3 用户体验验收标准
- 命令帮助信息清晰明确
- 输出格式美观且一致
- 错误信息用户友好
- 支持常用使用场景