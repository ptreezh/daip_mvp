# DAIP-LIVE TUI 命令快速参考

## 🚀 快速启动

```bash
# 启动TUI
poetry run python -m daip_live.tui

# 或使用直接运行
python -m daip_live.tui
```

## 📋 所有命令总览

### 🆕 新增命令 (v2.0)
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/compact` | 上下文压缩 | `/compact current` |
| `/doc` | 论文管理 | `/doc download "ML" --arxiv` |
| `/wiki` | 知识管理 | `/wiki create "笔记"` |
| `/permission` | 权限管理 | `/permission list` |

### 🎯 核心命令
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/pa <目标>` | 启动个人助理 | `/pa "帮我写代码"` |
| `/help` | 显示帮助 | `/help` |
| `/clear` | 清空屏幕 | `/clear` |
| `/quit` | 退出应用 | `/quit` |

### 👥 角色管理
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/role list` | 列出角色 | `/role list` |
| `/role view <名称>` | 查看角色 | `/role view assistant` |
| `/role add <名称> <描述>` | 添加角色 | `/role add coder "编程专家"` |

### 🗣️ 会话管理
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/session list` | 列出会话 | `/session list` |
| `/session view <ID>` | 查看会话 | `/session view abc123` |
| `/session clear` | 清空会话 | `/session clear` |
| `/session reset` | 重置Token | `/session reset` |

### 🧠 知识库
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/knowledge sync` | 同步知识库 | `/knowledge sync` |
| `/knowledge search <查询>` | 搜索知识 | `/knowledge search "Python"` |

### 🎭 辩论系统
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/debate start <主题>` | 开始辩论 | `/debate start "AI未来"` |
| `/debate start <主题> --roles <角色>` | 指定角色辩论 | `/debate start "主题" --roles "专家,批评者"` |

### 🤖 模型管理
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/model list` | 列出模型 | `/model list` |
| `/model switch <模型>` | 切换模型 | `/model switch llama3` |
| `/model info` | 模型信息 | `/model info` |

### 🏗️ 项目脚手架
| 命令 | 功能 | 快速示例 |
|------|------|----------|
| `/project scaffold --description <描述>` | 创建项目 | `/project scaffold --description "Web应用"` |

---

## 🔧 新命令详细语法

### `/compact` - 上下文压缩
```bash
/compact [current|full|aggressive]
```
**示例：**
```bash
/compact current      # 压缩当前会话
/compact full         # 完整压缩
/compact aggressive   # 激进压缩
```

### `/doc` - 论文管理
```bash
# 下载论文
/doc download <查询> [--max <数量>] [--arxiv]

# 列出论文
/doc list

# 搜索论文
/doc search <关键词>
```
**示例：**
```bash
/doc download "transformer" --max 3 --arxiv
/doc list
/doc search "attention"
```

### `/wiki` - 知识管理
```bash
# 创建页面
/wiki create <标题> [--tags <标签>]

# 列出页面
/wiki list

# 搜索内容
/wiki search <关键词>

# 导出Wiki
/wiki export <格式> [目录]

# 其他功能
/wiki delete <标题>
/wiki import <文件>
/wiki stats
```
**示例：**
```bash
/wiki create "学习笔记" --tags "AI,机器学习"
/wiki list
/wiki search "神经网络"
/wiki export markdown ./export
```

### `/permission` - 权限管理
```bash
/permission list
/permission grant <工具> <用户>
/permission revoke <工具> <用户>
/permission check <工具>
/permission reset <用户>
```
**示例：**
```bash
/permission list
/permission grant paper-downloader user1
/permission check gemini-cli
```

---

## ⌨️ 快捷键

### 基本操作
| 快捷键 | 功能 |
|--------|------|
| `Tab` | 自动补全命令 |
| `↑/↓` | 浏览命令历史 |
| `Enter` | 执行命令 |
| `Esc` | 退出当前模式 |

### 界面控制
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Tab` | 切换输入/输出焦点 |
| `Ctrl+A` | 全选文本（输出模式） |
| `Ctrl+C` | 复制文本（输出模式） |
| `Ctrl+E` (双击) | 退出应用 |

### 导航操作
| 快捷键 | 功能 |
|--------|------|
| `↑` | 命令历史向上 |
| `↓` | 命令历史向下 |
| `←/→` | 光标移动 |
| `Home/End` | 行首/行尾 |

---

## 💡 使用技巧

### 1. 自动补全
- 输入命令开头，按 `Tab` 查看可用选项
- 输入部分命令，按 `Tab` 自动补全
- 支持子命令和参数补全

### 2. 命令历史
- 使用 `↑/↓` 浏览历史命令
- 历史记录自动保存最近10条
- 支持跨会话历史保存

### 3. 多行输入
- 某些命令支持多行参数
- 使用 `\` 续行（计划中）
- 支持引号包裹复杂参数

### 4. 批量操作
```bash
# 批量下载论文（计划中）
/doc download "paper1,paper2,paper3"

# 批量创建Wiki页面（计划中）
/wiki create "页面1,页面2,页面3"
```

### 5. 管道操作（计划中）
```bash
# 搜索结果导出
/wiki search "Python" | export json

# 论文信息处理
/doc list | filter "2023" | export csv
```

---

## 🔍 搜索技巧

### Wiki搜索
```bash
# 按标题搜索
/wiki search "title:机器学习"

# 按标签搜索
/wiki search "tag:深度学习"

# 按内容搜索
/wiki search "神经网络"

# 组合搜索
/wiki search "title:学习 tag:AI"
```

### 论文搜索
```bash
# 按作者搜索
/doc search "author:Geoffrey Hinton"

# 按年份搜索
/doc search "year:2023"

# 按关键词搜索
/doc search "transformer attention"

# 高级搜索（计划中）
/doc search "title:attention author:vaswani year:2017"
```

---

## 📊 状态监控

### Token使用
- 状态栏实时显示Token使用情况
- 自动在80%时触发压缩警告
- 支持 `/compact` 手动优化

### 系统状态
```bash
# 查看详细状态（计划中）
/status

# 查看性能统计
/stats

# 查看命令历史
/history
```

---

## 🛠️ 故障排除

### 常见问题快速解决

#### 命令不识别
```bash
# 检查命令拼写
/help

# 查看所有可用命令
/help all

# 重新加载命令
/reload
```

#### 权限问题
```bash
# 检查当前权限
/permission list

# 重置权限
/permission reset --all

# 重新登录
/login
```

#### 网络问题
```bash
# 检查网络状态
/doc status

# 使用备用镜像
/doc download "query" --mirror backup

# 重试操作
/retry
```

### 调试模式
```bash
# 启用调试
/debug on

# 查看详细日志
/log level verbose

# 运行诊断
/diagnose
```

---

## 📚 进阶功能

### 1. 配置管理
```bash
# 查看配置
/config show

# 设置配置
/config set key value

# 重置配置
/config reset
```

### 2. 脚本执行（计划中）
```bash
# 执行脚本文件
/script run my_commands.txt

# 录制操作
/script record session.txt

# 回放操作
/script play session.txt
```

### 3. 插件系统（计划中）
```bash
# 列出插件
/plugin list

# 安装插件
/plugin install plugin_name

# 启用/禁用插件
/plugin enable plugin_name
/plugin disable plugin_name
```

---

## 📞 获取帮助

### 内置帮助
- `/help` - 基本帮助信息
- `/help <命令>` - 特定命令帮助
- `/help advanced` - 高级功能帮助

### 示例命令
- `/examples` - 查看使用示例
- `/examples <命令>` - 特定命令示例

### 文档链接
- [完整用户手册](./TUI_NEW_COMMANDS_GUIDE.md)
- [系统架构文档](./specifications/SYSTEM_ARCHITECTURE.md)
- [API文档](./specifications/WEB_API_REQUIREMENTS.md)

---

**版本信息**：v2.0
**更新日期**：2024年1月
**适用系统**：DAIP-LIVE TUI