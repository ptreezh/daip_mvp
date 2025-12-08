# DAIP-LIVE 脚手架系统快速参考

## 一分钟入门

```bash
# 启动DAIP-LIVE
poetry run daip run

# 创建第一个项目（TUI方式）
选择 "Scaffold" -> "New Project" -> 输入描述 -> 确认

# 创建第一个项目（命令行方式）
poetry run daip project create "我的Web应用" \
  --description "React + Node.js全栈应用" \
  --output ./my_app
```

## 常用命令速查

### 项目创建
```bash
# 基础项目创建
daip project create "项目名" -d "项目描述"

# 指定模板
daip project create "API服务" \
  --template flask_api \
  --output ./api_service

# 交互式创建
daip project create "项目" --interactive

# 预览模式（不实际创建文件）
daip project create "测试" --dry-run
```

### 模板管理
```bash
# 列出模板
daip template list

# 查看模板详情
daip template show flask_api

# 创建自定义模板
daip template create "我的模板" --source ./template_dir

# 更新模板
daip template update flask_api
```

### 项目管理
```bash
# 验证项目结构
daip project validate

# 增强项目
daip project enhance --add-feature "用户认证"

# 生成文档
daip project enhance --generate-docs
```

## 常用模板

| 模板名称 | 描述 | 技术栈 |
|----------|------|--------|
| `flask_api` | Flask RESTful API | Python, Flask, PostgreSQL |
| `django_web` | Django Web应用 | Python, Django, SQLite |
| `react_app` | React前端应用 | React, TypeScript, Vite |
| `fastapi_microservice` | FastAPI微服务 | Python, FastAPI, Docker |
| `node_service` | Node.js服务 | Node.js, Express, MongoDB |
| `data_science` | 数据科学项目 | Python, Jupyter, Pandas |
| `ml_model` | 机器学习模型 | Python, Scikit-learn, MLflow |
| `static_site` | 静态网站 | HTML, CSS, JavaScript |

## 项目类型对比

| 类型 | 独立性 | 集成度 | 适用场景 |
|------|--------|--------|----------|
| `independent` | ✅ 完全独立 | ❌ 无集成 | 通用Web应用、API服务 |
| `daip_module` | ❌ 依赖DAIP | ✅ 深度集成 | AI角色、工具扩展 |
| `integrated` | ✅ 可独立运行 | ✅ 可选集成 | 第三方工具、数据分析 |

## 配置文件示例

### 全局配置 (`~/.daip/scaffold/config.yaml`)
```yaml
scaffold:
  default_type: independent
  default_strategy: hybrid
  llm:
    provider: openai
    model: gpt-4
  templates:
    auto_update: true
```

### 项目配置 (`.daip-scaffold.yaml`)
```yaml
project:
  name: "我的应用"
  type: independent
tech_stack:
  backend: Django
  frontend: React
features:
  - name: "用户认证"
    enabled: true
```

## 最佳实践速查

### 项目命名
```bash
✅ 好的命名: user-service, order_management, data-processor
❌ 坏的命名: proj, test, temp, 带空格的名称
```

### 目录结构
```
project_name/
├── src/           # 源代码
├── tests/         # 测试代码
├── docs/          # 文档
├── config/        # 配置文件
├── scripts/       # 脚本
└── README.md      # 项目说明
```

### 安全配置
```yaml
security:
  env_vars:        # 环境变量
    - SECRET_KEY
    - DATABASE_URL
  forbidden_patterns:  # 禁止模式
    - "hardcoded_password"
    - "api_key_in_code"
```

## 故障排除速查

| 问题 | 检查项 | 解决方案 |
|------|--------|----------|
| 创建失败 | 权限、磁盘空间、网络 | `chmod 755`, `df -h`, `ping google.com` |
| 模板错误 | 模板存在性、语法 | `daip template verify <name>` |
| LLM不工作 | API密钥、网络 | `daip llm test`, 检查配置 |
| 依赖冲突 | 虚拟环境、Python版本 | 使用venv, 检查Python兼容性 |

## 常用组合命令

### 完整项目创建流程
```bash
# 1. 创建项目
daip project create "完整应用" \
  --template django_web \
  --features "JWT认证,API文档,缓存"

# 2. 进入项目
cd complete_app

# 3. 设置虚拟环境
python -m venv venv && source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行测试
pytest

# 6. 启动开发服务器
python manage.py runserver
```

### 批量微服务创建
```bash
services=("user" "order" "payment" "inventory")

for service in "${services[@]}"; do
  daip project create "${service}-service" \
    --template fastapi_microservice \
    --output "./microservices/${service}-service" \
    --features "监控,日志,健康检查"
done
```

### 项目维护命令
```bash
# 定期更新
daip project enhance --update-dependencies
daip project enhance --generate-docs
daip project validate --strict

# 安全检查
daip project scan --security
daip project check-compliance --standards company_standards
```

## 环境变量速查

```bash
# 开发环境
export DAIP_ENV=development
export DAIP_LOG_LEVEL=debug
export DAIP_CACHE_ENABLED=false

# 生产环境
export DAIP_ENV=production
export DAIP_LOG_LEVEL=info
export DAIP_CACHE_ENABLED=true

# LLM配置
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key
```

## 键盘快捷键（TUI模式）

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+N` | 新建项目 |
| `Ctrl+O` | 打开项目 |
| `Ctrl+S` | 保存配置 |
| `Ctrl+Q` | 退出 |
| `F1` | 帮助 |
| `F5` | 刷新模板列表 |
| `Tab` | 切换面板 |
| `Enter` | 确认选择 |
| `Esc` | 取消操作 |

## 性能优化建议

### 大型项目生成
```bash
# 使用并行处理
daip project create "大型项目" \
  --parallel-workers 4 \
  --chunk-size 10

# 启用缓存
daip config set cache.enabled true
daip config set cache.ttl 3600
```

### LLM调用优化
```yaml
llm:
  temperature: 0.7      # 平衡创造性和一致性
  max_tokens: 4000      # 控制响应长度
  timeout: 30          # 请求超时时间
  retry_attempts: 3    # 重试次数
```

---

## 更多资源

- **完整文档**: [USER_MANUAL.md](USER_MANUAL.md)
- **用户场景**: [USER_SCENARIOS.md](USER_SCENARIOS.md)
- **API参考**: [API_REFERENCE.md](API_REFERENCE.md)
- **在线帮助**: `daip --help`
- **社区支持**: https://community.daip.live

---

*保持这个快速参考在手边，随时查阅常用命令和配置！*