# 🛠️ 环境配置指南

本指南将帮助您快速设置DAIP-LIVE的开发环境，让您能够顺利运行和学习这个AI应用系统。

## 📋 系统要求

### **基本要求**
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python版本**: Python 3.9 或更高版本
- **内存**: 至少 4GB RAM
- **存储**: 至少 2GB 可用空间

### **推荐配置**
- **Python版本**: Python 3.11+
- **内存**: 8GB+ RAM
- **存储**: 5GB+ 可用空间
- **终端**: 现代终端 (Windows Terminal, iTerm2, GNOME Terminal)

## 🚀 快速安装

### **方法一：使用Poetry (推荐)**

Poetry是Python的现代依赖管理工具，推荐用于开发环境。

```bash
# 1. 安装Poetry (如果尚未安装)
curl -sSL https://install.python-poetry.org | python3 -

# 2. 克隆项目
git clone https://github.com/ptreezh/daip_mvp.git
cd daip_mvp

# 3. 安装依赖
poetry install

# 4. 激活虚拟环境
poetry shell

# 5. 验证安装
daip --version
```

### **方法二：使用pip安装**

如果您更熟悉传统的pip安装方式：

```bash
# 1. 克隆项目
git clone https://github.com/ptreezh/daip_mvp.git
cd daip_mvp

# 2. 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 升级pip
pip install --upgrade pip

# 4. 安装项目依赖
pip install -e .

# 5. 验证安装
daip --version
```

## 🔧 详细配置步骤

### **1. Python环境检查**

```bash
# 检查Python版本
python --version
# 应该显示 Python 3.9.0 或更高版本

# 检查pip版本
pip --version
# 建议使用最新版本的pip
```

### **2. 依赖库安装**

项目依赖包括以下主要库：

```txt
# 核心依赖
textual>=0.41.0      # TUI框架
sqlalchemy>=2.0.0     # ORM框架
litellm>=1.0.0        # LLM统一接口
pyperclip>=1.8.0      # 剪贴板功能
faiss-cpu>=1.7.0      # 向量搜索 (可选)

# 开发依赖
pytest>=7.0.0        # 测试框架
ruff>=0.1.0           # 代码检查
mypy>=1.0.0           # 类型检查
black>=23.0.0         # 代码格式化
```

### **3. 配置文件初始化**

```bash
# 创建配置文件
python -c "from daip_live.config import create_config_yaml_if_not_exists; create_config_yaml_if_not_exists()"

# 检查配置文件
ls -la config.yaml
```

配置文件 `config.yaml` 包含以下关键设置：

```yaml
# 数据库配置
database:
  url: "sqlite:///daip_live.db"

# 模型提供者配置
model_provider:
  default_provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"

# Wiki和知识库配置
wiki:
  knowledge_dir: "./knowledge"
  vector_store_dir: "./knowledge/index.faiss"

# TUI界面配置
tui:
  theme: "default"
  max_log_entries: 1000
```

### **4. 可选组件安装**

#### **Ollama (本地AI模型)**
```bash
# 安装Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Windows用户请从 https://ollama.com 下载安装包

# 启动Ollama服务
ollama serve

# 下载模型 (示例)
ollama pull llama2
ollama pull mistral
```

#### **额外Python库**
```bash
# 用于更好的数学计算
pip install numpy matplotlib

# 用于网络请求和API调用
pip install requests aiohttp

# 用于文档处理
pip install beautifulsoup4 lxml

# 用于图像处理 (如果需要)
pip install pillow opencv-python
```

## ✅ 验证安装

### **基础验证**
```bash
# 检查命令是否可用
daip --help

# 检查模块导入
python -c "from daip_live.tui.simplified_main import SimplifiedTUI; print('✅ 导入成功')"

# 检查复制功能
python -c "import pyperclip; print('✅ pyperclip可用')"
```

### **功能验证**
```bash
# 运行快速开始示例
python tutor/examples/basic_usage/quick_start.py

# 启动TUI界面 (可选)
daip run
```

### **测试验证**
```bash
# 运行基础测试
python -m pytest tests/ -v

# 代码质量检查
ruff check src/
mypy src/
```

## 🔧 常见问题解决

### **问题1: Python版本不兼容**
```bash
# 解决方案：使用pyenv管理Python版本
pyenv install 3.11.0
pyenv local 3.11.0
```

### **问题2: 依赖安装失败**
```bash
# 解决方案：升级pip和setuptools
pip install --upgrade pip setuptools wheel
pip install -e . --no-cache-dir
```

### **问题3: 权限问题 (Linux/macOS)**
```bash
# 解决方案：使用用户安装
pip install --user -e .

# 或配置虚拟环境
python -m venv --system-site-packages venv
```

### **问题4: Windows路径问题**
```bash
# 解决方案：使用PowerShell而不是CMD
# 或者使用WSL (Windows Subsystem for Linux)
```

### **问题5: 终端兼容性问题**
- **Windows**: 使用 Windows Terminal 而不是传统CMD
- **macOS**: 使用 iTerm2 或更新系统终端
- **Linux**: 确保终端支持UTF-8和颜色显示

## 🎯 下一步

环境配置完成后，您可以：

1. 🎮 **运行示例**: `python tutor/examples/basic_usage/quick_start.py`
2. 📖 **阅读教程**: 查看 `tutor/tutorials/` 目录下的教程
3. 🧪 **尝试练习**: 开始 `tutor/exercises/` 中的练习
4. 🚀 **启动应用**: 运行 `daip run` 体验完整功能

## 💡 学习建议

- **循序渐进**: 先运行示例，再阅读源码
- **动手实践**: 尝试修改配置和代码
- **文档学习**: 阅读项目规格书了解架构
- **社区参与**: 在GitHub上提问和贡献

遇到问题时，请查看：
- 📖 [项目文档](../docs/)
- 🐛 [问题反馈](https://github.com/ptreezh/daip_mvp/issues)
- 💬 [社区讨论](https://github.com/ptreezh/daip_mvp/discussions)

---

**🎉 环境配置完成！准备开始您的AI应用开发学习之旅！**