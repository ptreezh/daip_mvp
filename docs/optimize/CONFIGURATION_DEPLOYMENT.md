# 配置与部署 (Configuration & Deployment)

## 📋 概述

本部分文档介绍DAIP-LIVE系统的配置管理和部署方式。系统支持本地优先的部署模式，确保用户数据隐私和系统性能。

## ⚙️ 配置管理

### 主配置文件 (config.yaml)
系统使用YAML格式的主配置文件来管理所有配置参数：

```yaml
# 数据库配置
database:
  path: "./daip_live.db"

# LLM提供者配置
llm_provider:
  default_model: "gpt-4o"  # 默认使用模型
  embedding_model: "text-embedding-ada-002"  # 嵌入模型

# 知识库配置
knowledge_base:
  directory: "./knowledge"  # 知识库目录
  auto_sync: true  # 是否自动同步知识库

# 模型提供者配置
provider:
  name: "openai"  # 当前使用的提供者
  api_key: "your-api-key"  # API密钥
  base_url: null  # API基础URL
  temperature: 0.7  # 模型温度参数

# 工具权限配置
tool_permissions:
  default: "ask"  # 默认权限策略
  tools:
    file_operations: "ask"  # 文件操作权限
    shell_commands: "deny"  # shell命令权限
    web_search: "allow"  # 网络搜索权限

# 其他配置
logging:
  level: "INFO"  # 日志级别
  file: "./logs/daip.log"  # 日志文件路径
```

### 环境变量支持
系统支持通过环境变量覆盖配置文件中的参数：

```bash
# 设置API密钥
export OPENAI_API_KEY="your-openai-api-key"

# 设置模型提供者
export DAIP_MODEL_PROVIDER="ollama"

# 设置知识库路径
export DAIP_KNOWLEDGE_DIR="./my_knowledge"
```

## 🚀 部署方式

### 本地部署 (推荐)
适用于大多数用户，优先使用本地模型以保护数据隐私：

```bash
# 1. 安装依赖
pip install daip-live

# 2. 初始化配置
python -c "from daip_live.config import create_config_yaml_if_not_exists; create_config_yaml_if_not_exists()"

# 3. 启动应用
daip run
```

### 本地模型部署 (Ollama)
使用Ollama部署本地大语言模型：

```bash
# 1. 安装Ollama (https://ollama.ai)
# 2. 拉取模型
ollama pull llama3:8b
ollama pull nomic-embed-text

# 3. 配置DAIP-LIVE使用Ollama
# 在config.yaml中设置:
# provider:
#   name: "ollama"
#   default_model: "llama3:8b"
```

### 开发环境部署
适用于开发者和贡献者：

```bash
# 1. 克隆项目
git clone https://github.com/ptreezh/daip_mvp.git
cd daip_mvp

# 2. 安装开发依赖
poetry install  # 或 pip install -e .

# 3. 运行开发版本
python -m daip_live.cli.main run
```

## 🏗️ 系统架构部署

### 单体架构 (推荐)
所有组件运行在单个Python进程中，适用于本地单用户环境：

- **性能**: 最佳性能，无网络延迟
- **隐私**: 所有数据处理在本地完成
- **维护**: 简单易维护

### Docker部署 (高级)
适用于需要隔离或服务部署的场景：

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["daip", "run"]
```

## 🔐 安全配置

### API密钥管理
- **加密存储**: 在生产环境中建议加密存储API密钥
- **访问控制**: 限制对配置文件的访问权限
- **定期轮换**: 定期轮换API密钥

### 网络安全
- **本地优先**: 默认配置不对外暴露网络接口
- **防火墙**: 建议在服务器部署时配置防火墙
- **HTTPS**: Web界面建议通过HTTPS访问

## 📊 性能优化

### 本地模型优化
- **模型选择**: 根据硬件能力选择合适的本地模型
- **量化模型**: 使用量化模型减少内存占用
- **批处理**: 合理设置批处理大小

### 知识库优化
- **索引优化**: 定期重建知识库向量索引
- **分片存储**: 对于大型知识库考虑分片存储
- **缓存策略**: 启用查询结果缓存

## 🔧 疑难解答

### 常见部署问题
1. **模型连接失败**: 检查API密钥和网络连接
2. **权限错误**: 检查配置文件和目录权限
3. **性能问题**: 检查硬件资源和模型配置

### 日志与调试
- **日志位置**: `./logs/daip.log`
- **调试模式**: 启动时添加`--debug`参数
- **详细日志**: 在配置中设置日志级别为`DEBUG`

## 📄 相关规格文档

- `docs/specs/DEPLOYMENT_AND_OPERATIONS_MANUAL.md` - 部署和操作手册
- `docs/specs/DATABASE_DESIGN_SPECIFICATION.md` - 数据库设计规格
- `docs/production_wiki_system_summary.md` - 生产环境维基系统总结