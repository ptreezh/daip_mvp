# P6 CLI/TUI 界面 (CLI/TUI Interface)

## 📋 概述

P6模块负责系统的命令行界面(CLI)和终端用户界面(TUI)，为用户提供与DAIP-LIVE系统交互的主要入口。该模块实现了直观的命令行工具和功能丰富的终端界面。

## 🔧 核心功能

### CLI (命令行界面)
- **Typer框架**: 基于Typer实现的命令行界面
- **多命令支持**: 支持debate、wiki、doc、knowledge等多种命令
- **参数验证**: 集成参数验证和错误处理
- **帮助系统**: 自动生成命令帮助信息

### TUI (终端用户界面)
- **Textual框架**: 基于Textual的现代化终端界面
- **实时交互**: 支持实时输入和输出
- **响应式设计**: 适配不同终端尺寸
- **复制功能**: 实现内容复制到剪贴板功能

### 交互功能
- **自然语言处理**: 支持`daip ask`命令进行自然语言交互
- **命令自动完成**: 提供命令和参数的自动完成功能
- **历史记录**: 保存和访问命令历史
- **状态显示**: 实时显示系统状态和代理执行状态

## 🏗️ 系统架构

### CLI架构
```
┌─────────────────────────────────────────┐
│              CLI Layer                  │
├─────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Main Command  │ │   Sub Commands  ││
│  │     (run)       │ │ (debate, wiki, ││
│  │                 │ │  doc, knowledge)││
│  └─────────────────┘ └─────────────────┘│
├─────────────────────────────────────────┤
│        Business Logic Layer             │
│     (P5 Agent Engine, P8 Systems)       │
└─────────────────────────────────────────┘
```

### TUI架构
- **App类**: Textual的主应用类
- **Widget组件**: 不同功能区域的UI组件
- **事件处理**: 用户交互事件的处理机制
- **状态同步**: 与后端状态的实时同步

## 🛠️ 实现细节

### CLI实现
```python
# CLI主入口
@app.command()
def run():
    """启动DAIP-TUI界面"""
    tui = DAIP_TUI()
    tui.run()

# 辩论命令
@debate_app.command("start")
def debate_start(
    topic: str = typer.Argument(..., help="辩论主题"),
    roles: str = typer.Option("pro_arguer,con_arguer", help="参与辩论的角色"),
    rounds: int = typer.Option(1, help="辩论轮次")
):
    # 辩论启动逻辑
```

### TUI实现
- **布局管理**: 响应式布局，包含对话区域和系统状态区域
- **事件流处理**: 实时处理AgentEvent事件流
- **用户输入**: 处理用户输入和命令执行

## 🔧 关键功能

### 复制功能
- **`/copy`**: 复制所有对话内容到剪贴板
- **`/copy_recent N`**: 复制最近N行对话内容
- **快捷键支持**: 支持Ctrl+C等快捷键

### 命令系统
- **结构化命令**: 如`daip debate start`、`daip wiki create`
- **自然语言命令**: 如`daip ask "请帮我分析这个主题"`
- **会话管理**: 支持会话的创建、切换和管理

### 实时反馈
- **状态监控**: 实时显示代理执行状态
- **进度指示**: 显示长时间操作的进度
- **错误显示**: 清晰的错误信息显示

## 📁 代码结构

```
src/daip_live/p6_cli_tui/
├── __init__.py
├── main.py            # CLI主入口
├── tui.py             # TUI主实现
├── commands/          # 各种命令实现
│   ├── base.py        # 命令基类
│   ├── debate.py      # 辩论相关命令
│   ├── wiki.py        # Wiki相关命令
│   ├── knowledge.py   # 知识管理命令
│   └── doc.py         # 文档处理命令
├── widgets/           # TUI组件
│   ├── base.py        # 基础组件
│   ├── chat.py        # 聊天组件
│   ├── status.py      # 状态组件
│   └── input.py       # 输入组件
├── utils/             # 工具函数
│   ├── clipboard.py   # 剪贴板功能
│   ├── validators.py  # 参数验证
│   └── formatters.py  # 输出格式化
├── models.py          # 界面相关数据模型
├── interfaces.py      # 界面相关接口
└── config.py          # 界面配置管理
```

## 🔐 安全考虑

- **输入验证**: 验证所有用户输入的安全性
- **命令执行**: 安全地执行用户命令
- **权限控制**: 与P4模块协作处理工具权限请求

## 🧪 测试策略

- **命令测试**: 测试所有CLI命令的功能
- **界面测试**: 测试TUI组件的交互功能
- **集成测试**: 测试界面与后端服务的集成
- **用户体验测试**: 验证界面的易用性

## 📄 相关规格文档

- `docs/specs/CLI_INTERFACE_REQUIREMENTS.md` - CLI接口需求规格
- `docs/specs/TUI_COMPONENT_SPEC.md` - TUI组件规格
- `docs/p6_cli_tui/README.md` - P6模块实现文档
- `docs/TUI_USER_MANUAL.md` - TUI用户手册
- `docs/TUI_TESTING_USER_GUIDE.md` - TUI测试用户指南