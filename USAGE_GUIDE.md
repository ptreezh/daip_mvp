# DAIP-LIVE 使用指南

## 🎯 系统状态

✅ **系统可用**：所有核心组件已成功加载
✅ **多模型辩论功能**：已就绪
✅ **TUI界面**：可正常启动

## 🚀 快速开始

### 1. 启动主界面
```bash
# 方法1：直接启动TUI（推荐）
python -c "from daip_live.tui_modular import DAIP_TUI; DAIP_TUI().run()"

# 方法2：使用模块方式
python -m daip_live.tui_modular
```

### 2. 测试系统状态
```bash
# 运行系统测试
python test_system.py

# 测试辩论功能
python test_debate.py
```

## 🤖 多模型辩论功能

### 功能特点
- **多模型支持**：可以为不同角色分配不同的AI模型
- **角色系统**：预定义的角色（经济学家、政策制定者等）
- **实时辩论**：多轮辩论，支持实时用户介入
- **历史记录**：完整的辩论历史追踪

### 当前状态
- ✅ Enhanced Debate Manager：已加载
- ✅ Role-based model assignment：已加载
- ✅ Multi-round debating：已加载
- ✅ Session management：已加载
- ⚠️ 模型检测：需要配置Ollama或API密钥

## ⚙️ 配置要求

### 基本配置
系统已检测到 `config.yaml` 配置文件：
- 数据库路径：`daip_live.db`
- 默认模型：`ollama/llama3`
- 嵌入模型：`ollama/nomic-embed-text`

### 模型配置选项

#### 选项1：本地模型（推荐）
```bash
# 安装Ollama
# 下载地址：https://ollama.ai/

# 拉取模型
ollama pull llama3
ollama pull nomic-embed-text

# 启动Ollama服务
ollama serve
```

#### 选项2：云端模型
编辑 `config.yaml` 添加API密钥：
```yaml
llm_provider:
  default_model: gpt-3.5-turbo
  api_key: "your-openai-api-key"
```

## 🎭 辩论系统使用

### 启动TUI后：
1. **选择辩论功能**：在主界面选择 "Debate"
2. **选择角色**：从预定义角色中选择或创建新角色
3. **设定主题**：输入辩论主题
4. **开始辩论**：系统会自动为不同角色分配模型并开始辩论

### 示例辩论流程
```
1. 启动TUI
2. 选择 "Start New Debate"
3. 选择角色：[经济学家, 技术专家, 政策制定者]
4. 输入主题："AI对就业市场的影响"
5. 系统自动开始多轮辩论
6. 可以实时查看各角色观点
7. 支持用户介入和引导辩论方向
```

## 🛠️ 开发者选项

### 测试单个组件
```python
# 测试TUI
from daip_live.tui_modular import DAIP_TUI
tui = DAIP_TUI()

# 测试辩论管理器
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
# ... 其他组件初始化
```

### 扩展功能
- 添加新角色：编辑 `roles/` 目录下的配置文件
- 自定义模型：修改 `config.yaml` 中的模型配置
- 集成新工具：扩展 `p4_role_manager_tools/` 中的工具管理

## 📋 当前系统架构

```
DAIP-LIVE System
├── P1: Data Persistence ✅
├── P2: Knowledge Management ✅
├── P3: Model Provider ✅
├── P4: Role & Tool Management ✅
├── P5: Agent Engine ✅
├── P6: Terminal Interface (TUI) ✅
├── P7: GUI Interface (开发中)
└── P8: Debate System ✅
```

## 🚨 注意事项

1. **模型依赖**：需要安装Ollama或配置云端API才能使用AI功能
2. **终端要求**：TUI需要现代终端支持（推荐使用Windows Terminal、iTerm2等）
3. **内存要求**：本地模型需要至少4GB内存
4. **网络连接**：云端模型需要稳定的网络连接

## 🎯 下一步

1. **安装Ollama**（如果还没有）
2. **拉取AI模型**：`ollama pull llama3`
3. **启动TUI**：运行启动命令
4. **开始辩论**：体验多模型AI辩论功能

---

*更新时间：2025-12-04*
*系统版本：DAIP-LIVE v2.1.0-modular-simplified*