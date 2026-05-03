# 故障排除 (Troubleshooting)

## 🚨 常见问题与解决方案

### 启动问题

#### 问题：无法启动应用
**症状**: 运行`daip run`时出现ImportError或ModuleNotFoundError
**解决方案**:
1. 确认已正确安装依赖：`pip install -e .`
2. 检查Python版本是否符合要求（3.9+）
3. 确认虚拟环境已激活

#### 问题：TUI界面无法启动
**症状**: 启动TUI时出现Textual相关错误
**解决方案**:
1. 重新安装Textual：`pip install textual>=0.66.0`
2. 检查终端是否支持ANSI颜色
3. 尝试使用不同终端（如Windows Terminal、iTerm2等）

### 模型连接问题

#### 问题：模型连接失败
**症状**: 无法连接到指定的LLM提供者
**解决方案**:
1. 检查API密钥是否正确配置
2. 确认网络连接正常
3. 验证模型服务是否正在运行（如Ollama）
4. 检查配置文件中的模型名称是否正确

#### 问题：本地模型无法加载
**症状**: 使用Ollama或LlamaCpp时无法加载模型
**解决方案**:
1. 确认模型已正确下载：`ollama list`
2. 检查模型名称是否与配置文件中的一致
3. 验证系统资源是否充足（内存、磁盘空间）

### 知识库问题

#### 问题：知识库搜索不返回结果
**症状**: 知识库搜索始终返回空结果
**解决方案**:
1. 确认文档已正确放置在知识库目录
2. 手动触发知识库同步：`daip knowledge sync`
3. 检查文档格式是否受支持（.md, .txt, .pdf等）
4. 验证向量数据库是否正确构建

#### 问题：知识库同步失败
**症状**: 知识库同步过程中出现错误
**解决方案**:
1. 检查知识库目录路径权限
2. 确认文档格式正确且未损坏
3. 增加超时时间或减少批处理大小
4. 查看日志文件获取详细错误信息

### 工具执行问题

#### 问题：工具权限被拒绝
**症状**: 尝试执行工具时收到权限错误
**解决方案**:
1. 检查配置文件中的工具权限设置
2. 将特定工具权限设置为"ask"以便手动确认
3. 确认安全策略配置正确

#### 问题：外部工具无法执行
**症状**: 尝试执行shell命令或外部程序失败
**解决方案**:
1. 确认所需程序已安装并可在PATH中找到
2. 检查配置文件中是否允许执行此类工具
3. 验证文件路径是否在允许的目录范围内

## 🔧 诊断步骤

### 1. 检查日志
- **日志位置**: `./logs/daip.log`
- **日志级别**: 在配置中设置为DEBUG以获取详细信息
- **查看命令**: `tail -f ./logs/daip.log`

### 2. 验证配置
```bash
# 验证配置文件格式
python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

### 3. 依赖检查
```bash
# 检查已安装的包
pip list | grep daip
pip list | grep textual
pip list | grep litellm
```

### 4. 环境验证
- Python版本：`python --version`
- 系统资源：检查内存和磁盘空间
- 网络连接：测试API端点可达性

## 🧪 测试命令

### 基础功能测试
```bash
# 测试CLI基本功能
daip --help

# 测试模型连接
daip ask "你好"

# 测试知识库功能
daip knowledge search "测试"
```

### 模块特定测试
```bash
# 测试辩论功能
daip debate start "测试主题" --roles pro_arguer,con_arguer

# 测试维基功能
daip wiki search "测试"
```

## 📞 支持渠道

### 社区支持
- **GitHub Issues**: https://github.com/ptreezh/daip_mvp/issues
- **GitHub Discussions**: https://github.com/ptreezh/daip_mvp/discussions

### 提供信息
当寻求支持时，请提供：
1. 完整的错误信息
2. 系统信息（操作系统、Python版本）
3. 相关配置文件内容（请清除敏感信息）
4. 操作步骤复现问题

## 🔍 调试技巧

### 启用详细日志
在启动应用时添加`--debug`参数：
```bash
daip run --debug
```

### 逐步排错
1. 从最简单的功能开始测试
2. 逐步增加复杂度
3. 隔离问题组件

### 环境隔离
使用虚拟环境确保依赖无冲突：
```bash
python -m venv daip_env
source daip_env/bin/activate  # Linux/Mac
# 或 daip_env\Scripts\activate  # Windows
pip install -e .
```

## 📄 相关文档

- `docs/quality_assurance.md` - 质量保证文档
- `docs/development_process.md` - 开发流程文档
- `docs/testing_framework.md` - 测试框架文档