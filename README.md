# DAIP-LIVE - 动态AI驱动项目执行系统

## 🚀 项目简介

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE system) 是一个智能协作平台，支持多AI角色协作与知识管理。它利用AI提示词和MCP协议，让开发更智能、更高效。

## 📋 功能特性

### 核心功能
- **多AI角色协作**: 支持多个AI角色协同工作
- **智能辩论系统**: 结构化辩论与共识形成
- **知识管理**: 基于向量数据库的智能检索
- **个人助理**: 统一入口处理复杂任务
- **Wiki协作**: 知识沉淀与团队协作

### 技术特性
- **实时协作**: WebSocket支持实时交互
- **可扩展架构**: 插件化设计，易于扩展
- **多语言支持**: 中英文双语界面
- **安全验证**: 完善的输入验证和错误处理

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **后端** | Python 3.10+, FastAPI, Typer |
| **AI/ML** | Langchain, LlamaIndex, Ollama |
| **数据库** | ChromaDB (向量数据库) |
| **前端** | Streamlit (可选) |
| **工具** | Pydantic, Rich, Ruff |

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Ollama (本地AI模型)
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/ptreezh/daip_mvp.git
cd daip_mvp_project
```

2. **安装依赖**
```bash
# 使用Poetry (推荐)
pip install poetry
poetry install

# 或使用pip
pip install -r requirements.txt
```

3. **配置环境**
```bash
cp .env.example .env
# 编辑.env文件配置Ollama等参数
```

4. **启动服务**
```bash
# 启动CLI
python -m src.cli.main --help

# 启动Web界面
streamlit run src/debate_system/web_interface.py
```

## 📖 使用指南

### CLI命令
```bash
# 查看帮助
python -m src.cli.main --help

# 启动辩论
python -m src.cli.main start "人工智能的伦理问题"

# 使用个人助理
python -m src.cli.main pa chat "帮我分析这个项目"

# 查看角色列表
python -m src.cli.main roles list
```

### Web界面
访问 `http://localhost:8501` 使用Web界面

## 🏗️ 项目结构

```
daip_mvp_project/
├── src/                    # 核心源代码
│   ├── cli/               # 命令行界面
│   ├── core_services/     # 核心服务
│   ├── debate_system/     # 辩论系统
│   └── workflows/         # 工作流引擎
├── roles/                 # AI角色定义
├── data/                  # 数据存储
├── tests/                 # 测试代码
├── docs/                  # 项目文档
└── configs/               # 配置文件
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_cli.py

# 覆盖率测试
pytest --cov=src tests/
```

## 🔧 开发

### 代码规范
- 使用Ruff进行代码检查: `ruff check src/`
- 使用Black格式化: `black src/`
- 类型检查: `mypy src/`

### 提交规范
- 使用pre-commit hooks
- 遵循Conventional Commits规范

## 📄 文档

- [API文档](docs/API.md)
- [用户指南](docs/USER_GUIDE.md)
- [开发文档](docs/DEVELOPMENT.md)
- [部署指南](docs/DEPLOYMENT.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🆘 支持

- 📧 邮箱: support@daip-live.com
- 💬 讨论: GitHub Issues
- 📖 文档: [项目Wiki](https://github.com/ptreezh/daip_mvp/wiki)