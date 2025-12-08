# DAIP-LIVE 项目结构规范

## 🏗️ **规范化目录结构**

```
daip_mvp/                          # SPEC驱动开发示范项目
├── 📄 README.md                   # 项目总览和快速开始
├── 📄 PROJECT_SPEC.md             # 项目规格说明书
├── 📄 DEVELOPMENT_PROCESS.md      # SPEC驱动开发流程
├── 📄 CHANGELOG.md                # 版本变更记录
├── 📄 LICENSE                     # 开源许可证
├── 📄 pyproject.toml              # Python项目配置
├── 📄 poetry.lock                 # 依赖锁定文件
├── 📄 config.yaml                 # 应用配置文件
│
├── 📁 src/                        # 核心源代码
│   └── daip_live/                 # 主要应用包
│       ├── __init__.py
│       ├── cli/                   # 命令行接口
│       ├── tui/                   # 文本用户界面
│       ├── agent_engine/          # AI代理引擎
│       ├── wiki/                  # Wiki协作系统
│       ├── debate_system/         # 辩论系统
│       └── ...
│
├── 📁 docs/                       # 项目文档
│   ├── 📁 specs/                  # 技术规格文档
│   │   ├── ARCHITECTURE_SPEC.md   # 架构设计规格
│   │   ├── API_SPEC.md           # API接口规格
│   │   ├── TUI_SPEC.md           # TUI设计规格
│   │   └── DEBATE_SPEC.md        # 辩论系统规格
│   ├── 📁 process/                # 开发过程文档
│   │   ├── SPEC_DRIVEN_DEVELOPMENT.md  # SPEC驱动开发方法
│   │   ├── ITERATION_LOGS/       # 迭代日志
│   │   └── VALIDATION_REPORTS/   # 验证报告
│   └── 📁 user_guide/             # 用户指南
│       ├── QUICK_START.md        # 快速开始
│       └── USER_MANUAL.md        # 用户手册
│
├── 📁 development/                # 开发过程文件
│   ├── 📁 intermediate/           # 中间实现版本
│   │   ├── prototype_v1/         # 原型版本1
│   │   ├── refactoring_v1/       # 重构版本1
│   │   └── feature_snapshots/    # 功能快照
│   ├── 📁 validation/             # 验证和测试
│   │   ├── unit_tests/           # 单元测试
│   │   ├── integration_tests/    # 集成测试
│   │   └── e2e_tests/            # 端到端测试
│   └── 📁 tools/                  # 开发工具脚本
│       ├── setup_env.py         # 环境设置
│       └── validate_code.py     # 代码验证
│
├── 📁 archive/                    # 历史存档
│   ├── 📁 deprecated/             # 已弃用代码
│   ├── 📁 experimental/          # 实验性功能
│   └── 📁 backups/               # 备份文件
│
├── 📁 examples/                   # 示例和演示
│   ├── basic_usage/             # 基础使用示例
│   └── advanced_scenarios/      # 高级场景示例
│
└── 📁 knowledge/                  # 知识库
    ├── 📁 wiki/                  # Wiki内容
    └── 📁 vector_store/          # 向量存储
```

## 📋 **文件分类原则**

### ✅ **保留文件**
- **核心源代码**: `src/daip_live/` 下的所有实现
- **配置文件**: `config.yaml`, `pyproject.toml`
- **规范文档**: `docs/specs/` 下的技术规格
- **用户文档**: `docs/user_guide/` 下的使用指南
- **测试文件**: `development/validation/` 下的测试
- **中间过程**: `development/intermediate/` 下的重要版本

### ❌ **清理文件**
- **临时脚本**: 根目录下的 `debug_*.py`, `test_*.py`, `fix_*.py`
- **重复代码**: 多个版本的相同功能实现
- **调试文件**: 各种临时的调试和验证脚本
- **备份文件**: `.bak`, `.backup`, `.old` 等文件

## 🔄 **SPEC驱动开发流程**

1. **规格定义** (`docs/specs/`)
2. **原型实现** (`development/intermediate/prototype_v1/`)
3. **验证测试** (`development/validation/`)
4. **重构优化** (`development/intermediate/refactoring_v1/`)
5. **文档更新** (`docs/process/`)
6. **版本发布** (`CHANGELOG.md`)

## 📊 **项目状态追踪**

- **当前版本**: v2.1.0
- **开发阶段**: 规范化和开源准备
- **主要功能**: AI辩论系统 + Wiki协作 + TUI界面
- **技术栈**: Python + Textual + Ollama + SQLite