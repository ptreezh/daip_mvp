# TUI测试用户手册

## 简介

本文档介绍了如何运行和体验DAIP-LIVE系统的TUI（文本用户界面）测试。TUI提供了丰富的交互功能，包括快捷命令、会话管理、角色管理等。

## 先决条件

确保已安装所有依赖：
```bash
poetry install
```

## 运行TUI测试

### 1. 运行所有TUI测试

```bash
poetry run python -m pytest tests/test_tui* -v
```

### 2. 运行特定功能测试

```bash
# 运行命令处理测试
poetry run python -m pytest tests/test_tui_commands.py -v

# 运行焦点切换功能测试
poetry run python -m pytest tests/test_tui_focus.py -v

# 运行权限对话框测试
poetry run python -m pytest tests/test_tui_permission.py -v

# 运行语法高亮测试
poetry run python -m pytest tests/test_tui_syntax_highlighting.py -v
```

### 3. 运行单个测试用例

```bash
# 示例：运行特定的测试方法
poetry run python -m pytest tests/test_tui_commands.py::TestTUICommandHandlers::test_handle_pa_command_with_args -v
```

## TUI快捷命令体验

在TUI界面中，可以使用以下快捷命令：

### 个人助理命令
- `/pa <goal>` - 启动个人助理会话

### 角色管理命令
- `/role add <name> <persona>` - 创建新角色
- `/role view <role_name>` - 查看角色详情
- `/role list` - 列出所有角色

### 知识库命令
- `/0 [query]` - 搜索或同步知识库

### 辩论系统命令
- `/debate <topic>` - 启动辩论会话

### 会话管理命令
- `/v [query]` - 搜索会话
- `/l` - 列出所有会话
- `/c` - 中止当前会话
- `/g` - 继续当前会话
- `/p` - 暂停当前会话
- `/t` - 显示会话树
- `/tc <index>` - 中止并跳转到指定会话
- `/tt <index>` - 暂停并跳转到指定会话

### 焦点切换
- `Ctrl+Tab` - 在输入框和输出区域间切换焦点
- `Ctrl+A` - 在输出模式下全选文本
- `Ctrl+C` - 在输出模式下复制选中文本
- `ESC` - 退出输出模式或中止所有会话

## 测试覆盖范围

TUI测试涵盖了以下功能：

1. **命令处理** - 所有快捷命令的解析和执行
2. **会话管理** - 会话创建、暂停、中止、跳转等功能
3. **角色管理** - 角色创建、查看、列表等功能
4. **知识库集成** - 知识库搜索和同步功能
5. **辩论系统** - 辩论会话的创建和管理
6. **权限处理** - 工具权限请求和响应处理
7. **UI功能** - 焦点切换、文本选择、复制等功能
8. **语法高亮** - JSON和代码的语法高亮显示

## 常见问题

### 测试失败
如果遇到测试失败，请检查：
1. 是否所有依赖都已正确安装
2. 测试文件是否被意外修改
3. Python环境是否正确配置

### 语法高亮问题
如果遇到语法高亮相关的错误，可能需要检查`src/daip_live/tui.py`中的正则表达式实现。

## 贡献测试

要添加新的测试用例：
1. 在`tests/`目录下找到相应的测试文件
2. 添加新的测试方法
3. 运行测试确保新测试通过
4. 提交更改