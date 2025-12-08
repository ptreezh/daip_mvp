
# DAIP-LIVE: SPEC驱动开发示范项目

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/code_quality-A-brightgreen.svg)](docs/process/validation_reports/)

> 🎓 **展示SPEC驱动开发方法的完整AI应用示范项目**

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE System) 是一个综合性的AI助手系统，展示了从概念到开源的完整SPEC驱动开发流程。项目实现多模型协作、自然语言处理、Wiki协作和智能辩论系统。

## ✨ **核心特色**

### 🤖 **多模型AI协作**
- 支持OpenAI、Claude、本地Ollama等多种AI模型
- 智能角色扮演和协作辩论
- 自然语言驱动的交互体验

### 📝 **Wiki协作系统**
- 多角色共同创建和编辑知识库
- 向量搜索和智能分类
- 完整的版本控制和历史追踪

### 🖥️ **现代化TUI界面**
- 直观的命令行界面
- 真实的复制功能 (`/copy`, `/copy_recent`)
- 响应式设计和流畅体验

### 🏗️ **模块化架构**
- P1-P8模块化设计
- 高内聚低耦合
- 易于扩展和维护

## 🚀 **快速开始**

### **环境要求**
- Python 3.9+
- Poetry (推荐) 或 pip
- Ollama (可选，用于本地模型)

### **安装步骤**

```bash
# 克隆项目
git clone https://github.com/ptreezh/daip_mvp.git
cd daip_mvp

# 使用Poetry安装依赖 (推荐)
poetry install

# 或使用pip安装
pip install -e .

# 初始化配置
python -c "from daip_live.config import create_config_yaml_if_not_exists; create_config_yaml_if_not_exists()"

# 启动应用
daip run
```

### **基本使用**

```bash
# 启动TUI界面
daip run

# 启动辩论
daip debate start "人工智能的未来发展" --roles 乐观主义者,悲观主义者

# 创建Wiki页面
daip wiki create "机器学习基础概念"

# 查看帮助
daip --help
```

## 🎯 **核心功能**

### **智能对话**
- 🧠 先进的意图识别和上下文理解
- 💬 多轮对话和会话管理
- 📋 对话内容复制和导出

### **复制功能** (最新实现)
```bash
# 复制所有对话内容
/copy

# 复制最近20行
/copy_recent 20

# 使用快捷键
Ctrl+C  # 复制内容
Ctrl+A  # 全选提示
```

### **多模型辩论**
- 🎭 不同AI角色扮演不同观点
- 🔍 深度分析和多角度讨论
- 📊 辩论过程记录和总结

### **Wiki协作**
- ✏️ 多人协作编辑
- 🔍 智能搜索和分类
- 📚 知识库管理

## 📚 **学习路径**

### **初学者**
1. 📖 阅读 [项目规格书](docs/specs/PROJECT_SPEC.md)
2. 🎮 运行基础示例
3. 🔧 学习TUI界面使用
4. 💡 理解AI对话功能

### **开发者**
1. 🏗️ 研究模块化架构
2. 🔍 分析SPEC驱动开发流程
3. 🧪 运行测试用例
4. 🤝 参与开源贡献

### **研究者**
1. 📊 分析多模型协作机制
2. 🧠 研究意图识别算法
3. 📈 评估系统性能
4. 🔬 扩展AI能力

## 📖 **文档结构**

```
docs/
├── 📁 specs/                  # 技术规格文档
│   ├── PROJECT_SPEC.md        # 项目总体规格
│   ├── ARCHITECTURE_SPEC.md   # 架构设计规格
│   └── API_SPEC.md           # API接口规格
├── 📁 process/               # 开发过程文档
│   ├── SPEC_DRIVEN_DEVELOPMENT.md  # 开发方法
│   └── validation_reports/   # 验证报告
└── 📁 user_guide/           # 用户指南
    ├── QUICK_START.md       # 快速开始
    └── USER_MANUAL.md       # 用户手册
```

## 🛠️ **开发工具链**

### **核心技术**
- **Python 3.9+**: 主要编程语言
- **Textual**: 现代化TUI框架
- **SQLAlchemy**: ORM数据库操作
- **LiteLLM**: 统一LLM接口
- **FAISS**: 向量搜索存储

### **质量保证**
- **pytest**: 测试框架
- **ruff**: 代码检查和格式化
- **mypy**: 静态类型检查
- **black**: 代码格式化

## 📊 **项目状态**

- ✅ **核心功能**: 完整实现并测试
- ✅ **复制功能**: 真实可用，移除虚假实现
- ✅ **TUI界面**: 模块化设计完成
- ✅ **文档**: 完整的规格和用户指南
- 🔄 **性能优化**: 持续改进中
- 📋 **插件系统**: 规划阶段

## 🤝 **如何贡献**

我们欢迎所有形式的贡献！

### **贡献方式**
- 🐛 报告Bug和问题
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🧪 编写测试用例

### **贡献流程**
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

详见 [贡献指南](CONTRIBUTING.md)

## 📄 **许可证**

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🌟 **致谢**

感谢所有为这个项目做出贡献的开发者和用户！

## 📞 **联系方式**

- **项目主页**: https://github.com/ptreezh/daip_mvp
- **问题反馈**: [GitHub Issues](https://github.com/ptreezh/daip_mvp/issues)
- **功能讨论**: [GitHub Discussions](https://github.com/ptreezh/daip_mvp/discussions)

---

<div align="center">

**🚀 让我们一起探索AI应用开发的最佳实践！**

</div>