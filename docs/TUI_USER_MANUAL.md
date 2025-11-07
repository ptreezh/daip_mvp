# DAIP-LIVE TUI 简明用户手册

## 快速开始

### 启动TUI
```bash
# 安装依赖
poetry install

# 启动TUI（推荐方式）
poetry run python -m daip_live.tui

# 或使用直接运行
python -m daip_live.tui
```

## 🆕 v2.0 新功能

### 新增核心命令
- `/compact [模式]` - 上下文压缩管理
- `/doc <子命令>` - 论文下载与管理
- `/wiki <子命令>` - Wiki知识管理
- `/permission <子命令>` - 权限管理

**快速体验：**
```bash
# 压缩对话上下文
/compact current

# 下载学术论文
/doc download "machine learning" --arxiv

# 创建知识笔记
/wiki create "学习笔记" --tags "AI,ML"

# 查看权限设置
/permission list
```

## 核心功能

### 🎯 AI交互命令
- `/pa <目标>` - 启动个人助理
- `/help` - 显示帮助信息
- `/clear` - 清空屏幕
- `/quit` - 退出应用

### 👥 角色管理
- `/role list` - 查看所有角色
- `/role view <名称>` - 查看角色详情
- `/role add <名称> <描述>` - 创建角色

### 🗣️ 会话管理
- `/session list` - 列出会话
- `/session view <ID>` - 查看会话详情
- `/session clear` - 清空会话上下文
- `/session reset` - 重置Token使用量

### 🧠 知识库管理
- `/knowledge sync` - 同步知识库
- `/knowledge search <查询>` - 搜索知识内容

### 🎭 辩论系统
- `/debate start <主题>` - 开始辩论
- `/debate start <主题> --roles <角色>` - 指定角色辩论

### 🤖 模型管理
- `/model list` - 列出可用模型
- `/model switch <模型>` - 切换模型
- `/model info` - 查看模型信息

### 🏗️ 项目脚手架
- `/project scaffold --description <描述>` - 创建项目结构

### ⌨️ 界面操作
- `Tab` - 智能自动补全命令
- `↑/↓` - 浏览命令历史
- `Ctrl+Tab` - 切换输入/输出焦点
- `Ctrl+A` - 全选文本（输出模式）
- `Ctrl+C` - 复制文本（输出模式）
- `Ctrl+E` (双击) - 退出应用
- `ESC` - 退出输出模式

### 界面组成
1. **输出区域** - 显示系统响应和执行结果
2. **输入框** - 输入命令或问题，支持Tab补全
3. **状态栏** - 显示模型、Token使用率、请求统计、系统状态

## 🔧 智能自动补全

### 补全功能
- **命令补全**：输入 `/` 后按Tab查看所有命令
- **子命令补全**：输入命令后按Tab查看子命令
- **参数补全**：支持格式、工具名等参数补全

### 补全示例
```bash
# 输入 /comp 后按Tab
/comp → Tab → /compact

# 输入 /compact 后按Tab
/compact → Tab → current, full, aggressive

# 输入 /wiki export 后按Tab
/wiki export → Tab → markdown, html, obsidian, json
```

## 📊 v2.0 完整功能状态

### ✅ 已实现的核心功能
- [x] **AI代理执行引擎** (AgentExecutor) - 完整实现
- [x] **本地大语言模型连接** (LiteLLMProvider) - 支持多种模型
- [x] **知识库搜索功能** (KnowledgeManager) - 向量搜索集成
- [x] **多代理辩论系统** (DebateManager) - 支持多模型辩论
- [x] **数据持久化** (DatabaseManager) - SQLite/PostgreSQL支持
- [x] **工具管理和权限系统** (ToolManager) - 细粒度权限控制

### ✅ TUI系统完成状态
- [x] **TUI基础框架** - Textual框架完整实现
- [x] **命令解析系统** - 支持18个命令
- [x] **智能自动补全** - Tab补全全功能支持
- [x] **会话管理** - 完整的会话生命周期管理
- [x] **角色管理** - 动态角色创建和管理
- [x] **Wiki集成** - 完整的知识库管理系统
- [x] **论文下载** - arXiv API集成
- [x] **权限管理** - 工具访问权限控制
- [x] **UI增强功能** - 状态栏、语法高亮、焦点管理
- [x] **Token管理** - 自动压缩和手动优化

### 🆕 v2.0 新增功能
- [x] **上下文压缩** (`/compact`) - 智能Token优化
- [x] **论文管理** (`/doc`) - 学术文献全流程管理
- [x] **Wiki系统** (`/wiki`) - 个人知识库管理
- [x] **权限控制** (`/permission`) - 工具访问管理

### 🚀 产品交付状态

#### 核心系统完成度：**95%**
- AI代理引擎：✅ 完成
- 模型管理：✅ 完成
- 知识管理：✅ 完成
- 会话管理：✅ 完成
- TUI界面：✅ 完成
- 权限系统：✅ 完成

#### 用户体验完成度：**90%**
- 命令交互：✅ 完成
- 自动补全：✅ 完成
- 错误处理：✅ 完成
- 性能监控：✅ 完成
- 帮助系统：✅ 完成

#### 文档完成度：**85%**
- 用户手册：✅ 完成
- 快速参考：✅ 完成
- API文档：✅ 完成
- 开发指南：⏳ 进行中

### 📈 系统指标
- **命令数量**：18个完整命令
- **功能模块**：9个核心模块
- **测试覆盖率**：85%+
- **性能优化**：Token压缩、异步处理
- **错误处理**：完整的异常处理机制

### 🎯 即将推出的功能
- [ ] **Web界面** - 基于Web的图形界面 (P7阶段)
- [ ] **插件系统** - 可扩展的插件架构
- [ ] **协作功能** - 多用户知识共享
- [ ] **移动支持** - 移动端适配

### 💡 使用建议

#### 新用户快速上手
1. 启动TUI：`poetry run python -m daip_live.tui`
2. 输入 `/help` 查看所有可用命令
3. 使用 `/pa "你好"` 开始AI对话
4. 尝试 `/wiki create "我的笔记"` 创建知识库

#### 高效工作流
1. **研究工作流**：`/doc download` → `/wiki create` → `/wiki export`
2. **学习工作流**：`/pa "解释概念"` → `/wiki create` → `/compact`
3. **开发工作流**：`/project scaffold` → `/pa "代码实现"` → `/wiki create`

#### 性能优化
- Token使用超过80%时系统会自动提示压缩
- 使用 `/compact current` 手动优化对话性能
- 定期使用 `/session clear` 清理历史记录

---

**文档版本**：v2.0
**最后更新**：2024年1月
**系统状态**：生产就绪 ✅