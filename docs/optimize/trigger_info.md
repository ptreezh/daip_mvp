# 触发信息概览 (Trigger Information Overview)

## 🔘 基本触发方式

### CLI 触发
- `daip run` - 启动TUI界面
- `daip debate start "主题" --roles 支持者,反对者` - 开始辩论
- `daip wiki create "页面名"` - 创建Wiki页面
- `daip ask "自然语言请求"` - 智能意图识别

### TUI 界面触发
- 输入 `/copy` - 复制对话内容
- 输入 `/copy_recent 20` - 复制最近20行对话
- 对话框直接输入 - 智能意图识别

## 🎯 核心功能触发点

1. **多模型辩论系统** - `daip debate` 命令
2. **Wiki协作系统** - `daip wiki` 命令
3. **知识管理** - `daip knowledge` 命令
4. **智能意图识别** - `daip ask` 命令
5. **文档处理** - `daip doc` 命令

## 🧠 智能识别触发

- **意图识别**: 自然语言输入自动识别意图
- **上下文感知**: 根据会话历史提供相关功能
- **模型选择**: 根据任务类型自动选择合适的AI模型

> **重要**: 以上为触发信息概览，详细功能说明请见 [core_functions.md](core_functions.md)。