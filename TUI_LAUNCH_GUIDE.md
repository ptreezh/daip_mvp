# DAIP-LIVE TUI 启动和界面验证指南

## 项目验证状态
✅ **TUI核心功能** - 正常  
✅ **模块导入** - 正常  
✅ **依赖注入** - 正常  
✅ **配置加载** - 正常  
✅ **数据库连接** - 正常  
✅ **角色管理** - 正常  

## 启动前准备

### 1. 环境要求
- Python 3.9+
- Windows 10/11 (推荐)
- Ollama服务运行正常
- 项目文件完整

### 2. 验证环境
```bash
# 检查Python版本
python --version

# 检查Ollama服务
ollama list

# 检查项目文件
dir config.yaml daip_live.db roles
```

## 推荐启动方式

### 方式1：Windows Terminal (推荐)
1. 安装 [Windows Terminal](https://aka.ms/terminal)
2. 打开Windows Terminal
3. 执行以下命令：
```bash
cd /d D:\DAIP\refactdoc
python -m daip_live.cli run
```

### 方式2：VS Code终端
1. 在VS Code中打开项目目录
2. 使用 `Ctrl+Shift+P` 打开命令面板
3. 选择 "Terminal: Create New Terminal"
4. 执行以下命令：
```bash
cd /d D:\DAIP\refactdoc
python -m daip_live.cli run
```

### 方式3：PowerShell 7+
```bash
cd /d D:\DAIP\refactdoc
python -m daip_live.cli run
```

## 预期界面元素

启动后应看到以下界面元素：

### 1. Header标题栏
```
┌─ DAIP_TUI ──────────────────────────────────────────────────────┐
```

### 2. RichLog输出区域
- 显示欢迎信息
- 显示人格AI logo
- 显示系统状态信息

### 3. Input输入框
```
└─ Enter command or message... ────────────────────────────────────┘
```

### 4. StatusBar状态栏
```
Model: llama3:8b | Tokens: 0/8192 (0%) | Status: Ready | Focus: Input
```

## 界面验证步骤

### 1. 启动验证
- [ ] TUI启动后界面显示正常
- [ ] 头部标题栏显示正确
- [ ] 中间输出区域显示欢迎信息和logo
- [ ] 底部输入框和状态栏显示正常

### 2. 功能验证
- [ ] 输入 `/help` 显示帮助信息
- [ ] 输入 `/role list` 显示角色列表
- [ ] 输入 `/pa 你好` 开始对话
- [ ] 状态栏信息更新正常

### 3. 交互验证
- [ ] 能够正常输入命令
- [ ] 能够接收系统响应
- [ ] 界面刷新正常
- [ ] Ctrl+E 可以退出

## 常见问题解决

### 问题1：界面显示异常或乱码
**解决方案：**
- 使用Windows Terminal
- 设置环境变量：`set PYTHONIOENCODING=utf-8`

### 问题2：启动后无响应
**解决方案：**
- 确保Ollama服务运行：`ollama serve`
- 检查网络连接

### 问题3：依赖错误
**解决方案：**
- 运行 `poetry install`
- 检查Python版本

## 启动命令参考

### 基本启动
```bash
python -m daip_live.cli run
```

### 带初始目标启动
```bash
python -m daip_live.cli run "开始与人格AI对话"
```

### 查看可用命令
```bash
python -m daip_live.cli --help
```

## 常用TUI命令

- `/help` - 显示帮助信息
- `/pa <目标>` - 启动个人助手
- `/role list` - 列出所有角色
- `/session list` - 列出会话
- `/debate start <主题>` - 开始辩论
- `/quit` 或 `Ctrl+E` (两次) - 退出

## 确认完成

当您看到以下界面元素时，说明TUI已正确启动：

```
┌─ DAIP_TUI ──────────────────────────────────────────────────────┐
│                                                               │
│            人格AI Logo (动画显示)                             │
│                                                               │
│         Welcome to 人格AI! Ready for your command.           │
│                                                               │
└─ Enter command or message... ──────────────────────────────────┘
Model: llama3:8b | Tokens: 0/8192 (0%) | Status: Ready | Focus: Input
```