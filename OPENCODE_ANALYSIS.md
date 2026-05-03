# OpenCode 架构分析与 DAIP-LIVE 改进建议

## 📊 OpenCode 项目概览

**状态**: 已归档，项目迁移至 [Crush](https://github.com/charmbracelet/crush)

**技术栈**:
- 语言: Go 1.24+
- TUI 框架: Bubble Tea (Charm)
- LLM 集成: LiteLLM (多 provider 支持)
- 数据库: SQLite (sqlc)
- 协议: MCP (Model Context Protocol)

---

## 🏗️ 核心架构对比

### DAIP-LIVE vs OpenCode

| 维度 | DAIP-LIVE | OpenCode |
|------|-----------|----------|
| **语言** | Python | Go |
| **TUI** | Textual | Bubble Tea |
| **Provider** | LiteLLM | LiteLLM |
| **数据库** | SQLAlchemy + SQLite | sqlc + SQLite |
| **工具调用** | 自定义 | 标准化 + MCP |
| **会话管理** | 基本 | 自动压缩/摘要 |
| **配置** | YAML | JSON + 环境变量 |

---

## 🎯 OpenCode 优秀特性

### 1. 自动会话压缩 (Auto Compact)

```go
// 当 token 使用达到上下文窗口 95% 时自动触发摘要
if (tokens >= int64(float64(contextWindow)*0.95)) && config.Get().AutoCompact {
    return a, util.CmdHandler(startCompactSessionMsg{})
}
```

**学习点**: DAIP-LIVE 可以实现类似的自动会话摘要机制，避免上下文溢出。

### 2. 权限系统

```go
// 每次危险操作前请求权限
p := b.permissions.Request(
    permission.CreatePermissionRequest{
        SessionID:   sessionID,
        Path:        config.WorkingDirectory(),
        ToolName:    "bash",
        Action:      "execute",
        Description: fmt.Sprintf("Execute command: %s", params.Command),
    },
)
if !p {
    return ToolResponse{}, permission.ErrorPermissionDenied
}
```

**学习点**: DAIP-LIVE 应该实现细粒度的权限控制，特别是对于 bash 执行、文件修改等危险操作。

### 3. 多 Provider 自动切换

```go
// 按优先级自动选择可用 provider
func setProviderDefaults() {
    // 1. Copilot -> Claude -> OpenAI -> Gemini -> Groq -> OpenRouter -> Bedrock -> Azure -> VertexAI
    if hasCopilotCredentials() {
        viper.SetDefault("agents.coder.model", models.CopilotGPT4o)
        return
    }
    if apiKey := os.Getenv("ANTHROPIC_API_KEY"); apiKey != "" {
        viper.SetDefault("agents.coder.model", models.Claude37Sonnet)
        return
    }
    // ... 更多 provider
}
```

**学习点**: DAIP-LIVE 可以实现类似的智能 provider 选择逻辑。

### 4. MCP (Model Context Protocol) 支持

```go
// 动态加载 MCP 工具
func GetMcpTools(ctx context.Context, permissions permission.Service) []tools.BaseTool {
    for name, m := range config.Get().MCPServers {
        switch m.Type {
        case config.MCPStdio:
            c, err := client.NewStdioMCPClient(m.Command, m.Env, m.Args...)
            mcpTools = append(mcpTools, getTools(ctx, name, m, permissions, c)...)
        case config.MCPSse:
            c, err := client.NewSSEMCPClient(m.URL, client.WithHeaders(m.Headers))
            mcpTools = append(mcpTools, getTools(ctx, name, m, permissions, c)...)
        }
    }
    return mcpTools
}
```

**学习点**: DAIP-LIVE 应该支持 MCP 协议，扩展工具能力。

### 5. 工具系统设计

```go
// 标准化工具接口
type BaseTool interface {
    Info() ToolInfo  // 工具元数据
    Run(ctx context.Context, params ToolCall) (ToolResponse, error)  // 执行
}

// 示例：安全命令检查
var bannedCommands = []string{
    "alias", "curl", "wget", "nc", "telnet",
}

var safeReadOnlyCommands = []string{
    "ls", "echo", "pwd", "date", "git status", "git log",
    "go version", "go list", "go env",
}
```

**学习点**:
- 统一工具接口设计
- 命令白名单/黑名单机制
- 详细的工具描述（对 LLM 很重要）

### 6. 会话成本追踪

```go
func (a *agent) TrackUsage(ctx context.Context, sessionID string, model models.Model, usage provider.TokenUsage) error {
    cost := model.CostPer1MInCached/1e6*float64(usage.CacheCreationTokens) +
        model.CostPer1MOutCached/1e6*float64(usage.CacheReadTokens) +
        model.CostPer1MIn/1e6*float64(usage.InputTokens) +
        model.CostPer1MOut/1e6*float64(usage.OutputTokens)

    sess.Cost += cost
    sess.CompletionTokens = usage.OutputTokens + usage.CacheReadTokens
    sess.PromptTokens = usage.InputTokens + usage.CacheCreationTokens
}
```

**学习点**: DAIP-LIVE 应该实现成本追踪和统计。

### 7. 主题系统

```go
// 配置驱动的动态主题
func (app *App) initTheme() {
    cfg := config.Get()
    if cfg == nil || cfg.TUI.Theme == "" {
        return
    }
    err := theme.SetTheme(cfg.TUI.Theme)
}
```

**学习点**: DAIP-LIVE 可以添加主题切换功能。

### 8. 自定义命令系统

```go
// 用户定义的可复用命令
model.RegisterCommand(dialog.Command{
    ID:          "init",
    Title:       "Initialize Project",
    Description: "Create/Update the OpenCode.md memory file",
    Handler: func(cmd dialog.Command) tea.Cmd {
        // 执行逻辑
    },
})
```

**学习点**: DAIP-LIVE 的技能系统可以参考这种命令定义方式。

---

## 🔧 DAIP-LIVE 改进建议

### 1. 实现自动会话摘要

```python
# 伪代码示例
class SessionCompactor:
    async def check_and_compact(self, session: Session) -> bool:
        tokens = session.prompt_tokens + session.completion_tokens
        model = session.model
        if tokens >= model.context_window * 0.95:
            await self.summarize_and_create_new_session(session)
            return True
        return False
```

### 2. 添加权限系统

```python
class PermissionService:
    def request(self, action: str, **kwargs) -> bool:
        # 检查权限配置
        # 弹出权限请求对话框
        # 返回用户决策
        pass

# 使用
if not self.permission_service.request("bash_execute", command=cmd):
    raise PermissionDenied()
```

### 3. 实现 MCP 客户端

```python
import mcp

class MCPToolAdapter(BaseTool):
    def __init__(self, mcp_client, tool_def):
        self.client = mcp_client
        self.tool_def = tool_def

    async def execute(self, input: dict) -> ToolResult:
        result = await self.client.call_tool(self.tool_def.name, input)
        return ToolResult(content=result.text)
```

### 4. 改进工具系统

```python
# 统一工具接口
class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        pass

    @abstractmethod
    async def execute(self, **params) -> ToolResult:
        pass

# 命令白名单/黑名单
SAFE_COMMANDS = {"ls", "pwd", "echo", "git status", "git log"}
BANNED_COMMANDS = {"rm", "mkfs", "dd", "curl", "wget"}
```

### 5. 添加成本追踪

```python
class CostTracker:
    def track_usage(self, session_id: str, usage: TokenUsage, model: Model):
        cost = (usage.prompt_tokens * model.cost_per_1m_input +
                usage.completion_tokens * model.cost_per_1m_output)
        session = self.session_service.get(session_id)
        session.total_cost += cost
        session.save()
```

### 6. 多 Provider 自动切换

```python
class SmartModelSelector:
    async def select_best_model(self) -> Model:
        providers = [
            ("anthropic", "ANTHROPIC_API_KEY", ClaudeModels),
            ("openai", "OPENAI_API_KEY", OpenAIModels),
            ("groq", "GROQ_API_KEY", GroqModels),
            ("local", None, OllamaModels),
        ]

        for provider_name, env_key, model_list in providers:
            if env_key is None or os.getenv(env_key):
                return model_list[0]  # 返回该 provider 的默认模型

        return OllamaModels[0]  # 回退到本地模型
```

### 7. 添加主题支持

```python
class ThemeManager:
    THEMES = {
        "default": {...},
        "dark": {...},
        "light": {...},
        "opencode": {...},
    }

    def set_theme(self, theme_name: str):
        if theme_name in self.THEMES:
            self.current_theme = self.THEMES[theme_name]
```

### 8. 实现自定义命令/技能

```python
class CustomCommand:
    def __init__(self, id: str, title: str, description: str, handler: Callable):
        self.id = id
        self.title = title
        self.description = description
        self.handler = handler

# 注册自定义命令
manager.register_command(CustomCommand(
    id="analyze_codebase",
    title="Analyze Codebase",
    description="Create a comprehensive analysis of the project structure",
    handler=analyze_codebase_handler
))
```

---

## 📁 文件结构对比

### OpenCode

```
opencode/
├── cmd/
│   └── root.go           # CLI 入口
├── internal/
│   ├── app/              # 应用核心
│   │   └── app.go
│   ├── config/           # 配置管理
│   ├── db/               # 数据库 (sqlc)
│   ├── llm/
│   │   ├── agent/        # Agent 实现
│   │   ├── provider/     # Provider 适配
│   │   ├── tools/        # 工具集
│   │   └── models/       # 模型定义
│   ├── session/          # 会话管理
│   ├── message/          # 消息处理
│   ├── tui/              # 界面
│   │   ├── components/
│   │   ├── dialog/
│   │   └── page/
│   ├── permission/       # 权限系统
│   ├── lsp/              # LSP 集成
│   └── logging/          # 日志
├── opencode-schema.json  # schema 定义
└── .opencode.json        # 配置文件
```

### DAIP-LIVE

```
daip_live/
├── p1_persistence/       # 数据持久化
├── p2_knowledge/         # 知识管理
├── p3_model_provider/    # 模型提供者
├── p4_role_tools/        # 角色和工具
├── p5_agent_engine/      # Agent 引擎
├── p6_cli_tui/           # CLI/TUI
├── p7_gui/               # Web GUI
└── p8_debate/            # 辩论系统
```

---

## 🚀 推荐优先实现的改进

### 高优先级 (立即实现)

1. **权限系统** - 安全性至关重要
2. **命令白名单** - 防止危险操作
3. **自动会话摘要** - 避免上下文溢出
4. **成本追踪** - 用户需求

### 中优先级 (短期实现)

5. **MCP 客户端** - 扩展工具能力
6. **更好的工具描述** - 提升 LLM 工具调用准确性
7. **主题系统** - UI 改进

### 低优先级 (长期规划)

8. **自定义命令系统**
9. **多 Provider 自动切换**
10. **LSP 集成**

---

## 📚 参考资料

- OpenCode 源码: `opencode-source/`
- Bubble Tea: https://github.com/charmbracelet/bubbletea
- MCP Protocol: https://modelcontextprotocol.io/
- LiteLLM: https://github.com/BerriAI/litellm
- Crush (OpenCode 继任者): https://github.com/charmbracelet/crush
