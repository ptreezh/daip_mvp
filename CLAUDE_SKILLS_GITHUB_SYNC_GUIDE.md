# Claude Code Skills GitHub 同步使用说明

## 功能概述

DAIP-LIVE 系统现在支持从 GitHub 同步 Claude Code Skills，允许用户下载、管理和使用社区创建的技能。

## 支持的功能

### 1. 从 GitHub 下载 Claude Skills

使用 `/skill download` 命令可以从任何包含 Claude Skills 的 GitHub 仓库下载技能：

```
/skill download https://github.com/anthropics/claude-tools
```

### 2. 管理已下载的技能

- 列出所有可用技能：`/skill list`
- 查看技能详细信息：`/skill info <skill_name>`
- 从本地目录重新加载技能：`/skill reload`

### 3. 使用 PPT 生成技能

```
/ppt create --content "# Presentation Title\n\n## Slide 1\nContent here\n\n## Slide 2\nMore content" --title "My Presentation" --output "my_presentation.pptx"
```

### 4. 使用问卷调查技能

- 创建问卷：`/survey create --content "Question 1?\nA. Option A\nB. Option B"`
- 分析结果：`/survey analyze --data "Response data here"`
- 总结结果：`/survey summarize --data "Response data here"`

## 技术实现细节

### GitHub 下载器 (GitHubSkillDownloader)
- 使用 GitHub API 获取仓库内容
- 支持 HTTPS 和 SSH 格式的仓库 URL
- 自动检测包含 `manifest.json` 和 `tools.json` 的技能目录
- 支持递归下载子目录中的技能

### Claude Skill 适配器 (ClaudeSkillAdapter)
- 将 Claude 格式的技能适配为 DAIP-LIVE 的技能格式
- 解析 `manifest.json` 和 `tools.json` 文件
- 处理 Claude Skills 的 JSON Schema 验证

### 技能管理器增强 (EnhancedClaudeSkillsManager)
- 集成 GitHub 下载、实时文件监控、上下文限制处理等功能
- 自动将下载的技能加载到技能管理器中

## 使用示例

### 示例 1: 下载社区技能
```
/skill download https://github.com/anthropics/claude-computer-use-tools
```

### 示例 2: 使用下载的技能
下载完成后，系统将自动加载技能，用户可以通过自然语言使用这些技能。

### 示例 3: 创建 PPT 演示文稿
```
/ppt create --content "# AI 发展趋势\n\n## 机器学习\n机器学习是AI的核心...\n\n## 深度学习\n深度学习在图像识别等领域表现突出..." --title "AI 技术展望"
```

### 示例 4: 创建调查问卷
```
/survey create --content "1. 您对AI技术的了解程度？\nA. 非常了解\nB. 了解一些\nC. 不太了解\nD. 完全不了解"
```

## 系统架构

1. **TUI Command Processor** - 处理用户输入的命令
2. **Skill Command Handler** - 处理技能相关的命令
3. **GitHubSkillDownloader** - 负责从 GitHub 下载技能
4. **EnhancedClaudeSkillsManager** - 管理 Claude Skills 的整个生命周期
5. **SkillManager** - 核心技能管理器

## 安全考虑

- 运行时沙箱 (ClaudeSkillsRuntimeSandbox) 限制技能执行的资源使用
- JSON Schema 验证确保参数安全
- 权限控制限制技能的系统访问能力

## 故障排除

如果技能下载失败：
1. 检查 GitHub URL 是否正确
2. 确认仓库包含有效的 Claude Skills (manifest.json 和 tools.json)
3. 确认网络连接正常

## 开发者说明

要添加新的 Claude Skills，只需创建包含以下文件的目录：
- `manifest.json` - 技能元数据
- `tools.json` - 工具定义

然后将整个目录放到 `./claude_skills` 目录下，系统会自动加载。