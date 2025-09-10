# DAIP-LIVE TUI 简明用户手册

## 快速开始

### 启动TUI
```bash
# 安装依赖
poetry install

# 启动TUI（示例命令）
poetry run python -c "
import asyncio
from src.daip_live.tui import DAIP_TUI
from daip_live.agent_engine.executor import AgentExecutor

async def main():
    executor = AgentExecutor()
    app = DAIP_TUI(executor, '欢迎使用DAIP-LIVE')
    await app.run_async()

if __name__ == '__main__':
    asyncio.run(main())
"
```

## 核心功能

### 快捷命令
- `/pa <目标>` - 启动个人助理
- `/role add <名称> <描述>` - 创建角色
- `/role list` - 查看所有角色
- `/role view <名称>` - 查看角色详情
- `/0 [查询]` - 搜索知识库
- `/debate <主题>` - 启动辩论
- `/l` - 列出会话历史
- `/c` - 中止当前会话
- `/g` - 继续当前会话
- `/p` - 暂停当前会话
- `/t` - 显示会话树
- `/tc <序号>` - 中止并跳转会话
- `/tt <序号>` - 暂停并跳转会话

### 界面操作
- `Ctrl+Tab` - 切换输入/输出焦点
- `Ctrl+A` - 全选文本（输出模式）
- `Ctrl+C` - 复制文本（输出模式）
- `ESC` - 退出输出模式或中止所有会话

### 界面组成
1. **输出区域** - 显示系统响应和执行结果
2. **输入框** - 输入命令或问题
3. **状态栏** - 显示模型、Token使用率、系统状态

## 产品交付状态

经过全面审核，确认DAIP-LIVE系统的核心功能已经实现并完成集成：

### 已实现的核心组件
- [x] AI代理执行引擎 (AgentExecutor)
- [x] 本地大语言模型连接 (LiteLLMProvider)
- [x] 知识库搜索功能 (KnowledgeManager)
- [x] 多代理辩论系统 (DebateManager)
- [x] 数据持久化 (DatabaseManager)
- [x] 工具管理和权限系统 (ToolManager)

### 当前状态
- [x] TUI基础框架完成
- [x] 快捷命令解析实现
- [x] 会话管理功能
- [x] 角色管理功能
- [x] 知识库集成接口
- [x] 辩论系统接口
- [x] 权限对话框
- [x] UI增强功能（状态栏、语法高亮等）
- [x] 核心功能模块实现和集成

### 待完善功能
- [ ] TUI与后端组件的完整集成
- [ ] 系统配置和初始化流程优化
- [ ] 错误处理和恢复机制完善
- [ ] 性能优化和大规模数据处理
- [ ] 完整的用户文档和使用指南

### 预计完成时间
根据当前实现程度，产品达到可交付状态还需要：
- **系统集成和测试**：1-2周
- **配置和初始化流程优化**：3-5天
- **错误处理和稳定性**：3-5天
- **文档和用户指南完善**：1周

总计约需要**3-4周**时间达到最小可交付产品状态。