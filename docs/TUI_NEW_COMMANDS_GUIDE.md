# DAIP-LIVE TUI 新增命令完整指南

## 概述

DAIP-LIVE TUI 系统已成功增强了4个全新的命令，极大地扩展了系统的功能性。这些新命令提供了上下文管理、文档处理、知识管理和权限控制等核心功能。

## 🆕 新增命令总览

| 命令 | 功能描述 | 主要用途 |
|------|----------|----------|
| `/compact` | 上下文压缩管理 | 优化Token使用，手动压缩对话历史 |
| `/doc` | 论文下载与管理 | 搜索、下载和管理学术文献 |
| `/wiki` | Wiki知识管理 | 创建、组织、导出个人知识库 |
| `/permission` | 权限管理 | 控制工具访问权限 |

---

## 🔧 `/compact` - 上下文压缩命令

### 功能说明
手动压缩当前会话的上下文，以减少Token使用量并优化对话性能。

### 语法
```bash
/compact [模式]
```

### 子命令
- `current` - 压缩当前会话上下文
- `full` - 完全压缩（激进模式）
- `aggressive` - 激进压缩，保留最少信息

### 使用示例
```bash
# 基本压缩
/compact current

# 激进压缩
/compact aggressive

# 完整压缩
/compact full
```

### 功能特性
- ✅ 智能检测需要压缩的内容
- ✅ 保留重要信息和上下文
- ✅ 实时显示压缩前后对比
- ✅ 支持多种压缩策略
- ✅ 自动更新Token使用统计

### 应用场景
- 长时间对话后优化性能
- Token使用量接近限制时
- 需要清理历史记录开始新话题
- 系统资源紧张时的优化

---

## 📚 `/doc` - 论文管理命令

### 功能说明
提供完整的学术论文搜索、下载和管理功能，支持arXiv API集成。

### 语法
```bash
/doc <子命令> [参数]
```

### 子命令详解

#### 1. `/doc download` - 下载论文
```bash
/doc download <查询> [--max <数量>] [--arxiv]
```

**参数说明：**
- `<查询>` - 搜索关键词（必需）
- `--max <数量>` - 最大下载论文数量（默认5）
- `--arxiv` - 使用arXiv API搜索

**使用示例：**
```bash
# 下载关于机器学习的论文
/doc download "machine learning" --max 3 --arxiv

# 下载特定主题论文
/doc download "transformer architecture" --arxiv
```

#### 2. `/doc list` - 列出已下载论文
```bash
/doc list
```

**显示信息：**
- 论文标题
- 作者信息
- 下载时间
- 文件位置

#### 3. `/doc search` - 搜索本地论文
```bash
/doc search <关键词>
```

**搜索范围：**
- 论文标题
- 摘要内容
- 作者姓名
- 关键词标签

**使用示例：**
```bash
# 搜索包含"attention"的论文
/doc search "attention"

# 搜索特定作者
/doc search "vaswani"
```

### 功能特性
- ✅ arXiv API集成
- ✅ 批量下载支持
- ✅ 元数据自动提取
- ✅ 本地搜索功能
- ✅ 下载进度显示
- ✅ 错误重试机制
- ✅ 文件去重检测

### 存储位置
- PDF文件：`./docs/papers/`
- 元数据：`./docs/papers/` (JSON格式)

---

## 📝 `/wiki` - Wiki知识管理命令

### 功能说明
完整的个人知识库管理系统，支持页面创建、编辑、组织和导出。

### 语法
```bash
/wiki <子命令> [参数]
```

### 子命令详解

#### 1. `/wiki create` - 创建Wiki页面
```bash
/wiki create <标题> [--tags <标签1,标签2>]
```

**参数说明：**
- `<标题>` - 页面标题（必需）
- `--tags <标签>` - 页面标签，多个标签用逗号分隔

**使用示例：**
```bash
# 创建基本页面
/wiki create "机器学习基础"

# 创建带标签的页面
/wiki create "深度学习架构" --tags "深度学习,神经网络,AI"
```

#### 2. `/wiki list` - 列出所有页面
```bash
/wiki list
```

**显示信息：**
- 页面标题
- 标签信息
- 字数统计
- 最后修改时间
- 预计阅读时间

#### 3. `/wiki search` - 搜索Wiki内容
```bash
/wiki search <关键词>
```

**搜索范围：**
- 页面标题
- 页面内容
- 标签信息

#### 4. `/wiki export` - 导出Wiki
```bash
/wiki export <格式> [输出目录]
```

**支持格式：**
- `markdown` - Markdown格式
- `html` - HTML网页格式
- `obsidian` - Obsidian兼容格式
- `json` - JSON数据格式

**使用示例：**
```bash
# 导出为Markdown
/wiki export markdown ./export

# 导出为Obsidian格式
/wiki export obsidian ./obsidian_vault
```

#### 5. `/wiki delete` - 删除页面
```bash
/wiki delete <页面标题>
```

#### 6. `/wiki import` - 导入页面
```bash
/wiki import <文件路径>
```

#### 7. `/wiki stats` - 统计信息
```bash
/wiki stats
```

### 功能特性
- ✅ Markdown格式支持
- ✅ 标签分类系统
- ✅ 全文搜索功能
- ✅ 多格式导出
- ✅ 字数统计
- ✅ 阅读时间估算
- ✅ 版本历史跟踪
- ✅ 交叉引用链接

### 存储结构
```
./wiki/
├── pages/           # Wiki页面文件
├── assets/          # 附件资源
├── templates/       # 页面模板
└── exports/         # 导出文件
```

---

## 🔐 `/permission` - 权限管理命令

### 功能说明
管理系统工具的访问权限，提供细粒度的权限控制。

### 语法
```bash
/permission <子命令> [参数]
```

### 子命令详解

#### 1. `/permission list` - 列出权限设置
```bash
/permission list
```

**显示信息：**
- 当前权限状态
- 工具访问级别
- 用户权限列表

#### 2. `/permission grant` - 授予权限
```bash
/permission grant <工具名> <用户名>
```

**支持的工具：**
- `gemini-cli` - Gemini CLI工具
- `playwright` - 网页自动化工具
- `exa-search` - 搜索工具
- `context7` - 上下文管理工具
- `deepwiki` - Wiki深度搜索
- `paper-downloader` - 论文下载工具
- `format-converter` - 格式转换工具

**使用示例：**
```bash
# 授予论文下载权限
/permission grant paper-downloader user1

# 授予网页自动化权限
/permission grant playwright admin
```

#### 3. `/permission revoke` - 撤销权限
```bash
/permission revoke <工具名> <用户名>
```

#### 4. `/permission check` - 检查权限
```bash
/permission check <工具名>
```

#### 5. `/permission reset` - 重置权限
```bash
/permission reset <用户名>
```

### 功能特性
- ✅ 工具级别权限控制
- ✅ 用户权限管理
- ✅ 权限继承机制
- ✅ 审计日志记录
- ✅ 临时权限支持

---

## 🎮 智能自动补全

### 补全机制
所有新命令都支持智能Tab补全：

1. **命令补全**
   - 输入 `/comp` → Tab → `/compact`
   - 输入 `/doc` → Tab → 显示所有子命令

2. **子命令补全**
   - `/compact ` → Tab → `current`, `full`, `aggressive`
   - `/wiki ` → Tab → `create`, `list`, `search`, `export`, 等

3. **参数补全**
   - `/wiki export ` → Tab → `markdown`, `html`, `obsidian`, `json`
   - `/permission grant ` → Tab → 显示所有可用工具

### 补全示例
```bash
# 输入 /doc 然后按Tab
/doc → Tab → download, list, search, batch, status, report

# 选择download后继续补全
/doc download → 输入查询 → Tab补全历史搜索

# Wiki导出格式补全
/wiki export → Tab → markdown, html, obsidian, json
```

---

## 🚀 快速上手指南

### 1. 启动TUI
```bash
cd /path/to/daip-live
poetry install
poetry run python -m daip_live.tui
```

### 2. 基本工作流程

#### 学术研究工作流
```bash
# 1. 搜索相关论文
/doc download "attention mechanism" --max 5 --arxiv

# 2. 查看下载的论文
/doc list

# 3. 创建研究笔记Wiki页面
/wiki create "Attention机制研究" --tags "NLP,注意力机制,深度学习"

# 4. 导出研究成果
/wiki export markdown ./research_output
```

#### 知识管理工作流
```bash
# 1. 创建项目Wiki
/wiki create "项目名称" --tags "项目,正在进行"

# 2. 压缩旧对话上下文
/compact current

# 3. 搜索相关知识
/wiki search "相关技术"

# 4. 导出知识库
/wiki export obsidian ./knowledge_vault
```

### 3. 权限设置
```bash
# 查看当前权限
/permission list

# 授予特定工具权限
/permission grant paper-downloader researcher

# 检查权限状态
/permission check paper-downloader
```

---

## 🔧 高级功能

### 1. 批量操作
```bash
# 批量下载论文（实现中）
/doc batch "arxiv_id1,arxiv_id2,arxiv_id3"

# 批量导出Wiki
/wiki export all --format markdown
```

### 2. 搜索过滤器
```bash
# 按标签搜索Wiki
/wiki search "tag:机器学习"

# 按作者搜索论文
/doc search "author:Geoffrey Hinton"

# 按时间范围搜索
/doc search "date:2023" --arxiv
```

### 3. 配置管理
```bash
# 设置默认下载目录
/doc config --set download_dir ./papers

# 设置Wiki默认模板
/wiki config --set template academic

# 设置权限策略
/permission config --set default_policy restricted
```

---

## 📊 性能监控

### 系统状态
所有命令都集成了性能监控功能：

- **Token使用量** - 实时显示当前Token使用情况
- **执行时间** - 记录每个命令的执行时间
- **成功率统计** - 跟踪命令执行成功率
- **错误日志** - 详细的错误信息和调试信息

### 监控命令
```bash
# 查看系统状态（计划中）
/status

# 查看命令统计
/stats

# 查看性能报告
/performance
```

---

## 🐛 故障排除

### 常见问题

#### 1. 论文下载失败
**问题**：`/doc download` 命令失败
**解决方案**：
```bash
# 检查网络连接
/doc status

# 使用不同的arXiv镜像
/doc download "query" --mirror alternative

# 减少并发下载数量
/doc download "query" --max 1
```

#### 2. Wiki页面创建失败
**问题**：`/wiki create` 命令报错
**解决方案**：
```bash
# 检查Wiki目录权限
/wiki status

# 创建Wiki目录
mkdir -p ./wiki/pages

# 重新初始化Wiki系统
/wiki init --force
```

#### 3. 权限设置无效
**问题**：`/permission` 命令不生效
**解决方案**：
```bash
# 重置权限系统
/permission reset --all

# 重新加载权限配置
/permission reload

# 检查权限日志
/permission audit
```

### 调试模式
```bash
# 启用详细日志
/debug on

# 执行命令并查看详细输出
/compact current --verbose

# 禁用调试模式
/debug off
```

---

## 📈 未来规划

### 短期计划（1-2周）
- [ ] 完善错误处理机制
- [ ] 添加配置文件支持
- [ ] 实现命令历史记录
- [ ] 优化性能监控

### 中期计划（1个月）
- [ ] 添加更多导出格式
- [ ] 实现模板系统
- [ ] 添加协作功能
- [ ] 支持插件系统

### 长期计划（3个月）
- [ ] Web界面集成
- [ ] 移动端支持
- [ ] 云同步功能
- [ ] AI智能推荐

---

## 📞 技术支持

### 获取帮助
- 在TUI中输入 `/help` 查看基本帮助
- 使用 `--help` 参数查看具体命令帮助
- 查看系统日志获取详细错误信息

### 反馈渠道
- GitHub Issues：报告bug和功能请求
- 文档反馈：帮助改进文档质量
- 社区讨论：分享使用经验和最佳实践

---

**文档版本**：v1.0
**最后更新**：2024年1月
**维护者**：DAIP-LIVE开发团队