# DAIP-LIVE 脚手架系统用户手册

## 目录

1. [快速开始](#快速开始)
2. [基础概念](#基础概念)
3. [命令详解](#命令详解)
4. [配置指南](#配置指南)
5. [模板系统](#模板系统)
6. [高级功能](#高级功能)
7. [最佳实践](#最佳实践)
8. [故障排除](#故障排除)
9. [API参考](#api参考)

---

## 快速开始

### 安装和初始化

确保您已经安装了DAIP-LIVE系统：

```bash
# 检查DAIP-LIVE是否安装
poetry run daip --version

# 启动DAIP-LIVE TUI界面
poetry run daip run
```

### 第一个项目

5分钟创建您的第一个项目：

```bash
# 方法1：使用TUI界面（推荐新手）
poetry run daip run
# 在界面中选择 "Scaffold" -> "New Project"

# 方法2：使用命令行（适合高级用户）
poetry run daip project create "我的Web应用" \
  --description "一个使用React和Node.js的现代化Web应用" \
  --output ./my_web_app
```

### 验证安装

```bash
# 检查脚手架功能
poetry run daip scaffold --help

# 查看可用模板
poetry run daip template list

# 验证LLM连接
poetry run daip model test
```

---

## 基础概念

### 项目类型

DAIP-LIVE支持三种项目类型：

#### 1. 独立项目 (Independent)
```bash
poetry run daip project create "独立应用" --type independent
```
- **特点**：完全独立，可脱离DAIP-LIVE运行
- **输出**：标准项目结构，包含完整配置文件
- **适用**：Web应用、API服务、数据科学项目

#### 2. DAIP模块 (DAIP Module)
```bash
poetry run daip project create "DAIP扩展" --type daip_module
```
- **特点**：集成到DAIP-LIVE生态系统中
- **输出**：符合DAIP架构的模块结构
- **适用**：AI角色、工具扩展、数据处理器

#### 3. 集成项目 (Integrated)
```bash
poetry run daip project create "集成工具" --type integrated
```
- **特点**：可独立运行，但提供DAIP-LIVE集成接口
- **输出**：独立项目 + DAIP集成层
- **适用**：第三方工具、数据分析工具、可视化组件

### 生成策略

#### 模板驱动 (Template-Driven)
```bash
poetry run daip project create "项目" --strategy template --template flask_api
```
- 基于预定义模板
- 快速、可预测
- 适合标准化的项目类型

#### AI生成 (AI-Powered)
```bash
poetry run daip project create "项目" --strategy ai --description "详细描述"
```
- 基于LLM智能生成
- 灵活、个性化
- 适合定制化需求

#### 混合模式 (Hybrid)
```bash
poetry run daip project create "项目" --strategy hybrid \
  --template base_flask \
  --description "添加用户认证和API文档功能"
```
- 模板为基础，AI进行定制
- 平衡速度和灵活性
- 适合大多数场景

---

## 命令详解

### 核心命令

#### `daip project create`

创建新项目的核心命令。

```bash
# 基础语法
daip project create <项目名称> [选项]

# 完整示例
daip project create "电商后端API" \
  --description "基于Django REST Framework的电商后端服务，包含用户管理、商品管理、订单处理等功能" \
  --output ./ecommerce_api \
  --type independent \
  --strategy hybrid \
  --template django_api \
  --tech-stack "Django,PostgreSQL,Redis,Docker" \
  --features "JWT认证,API文档,缓存,测试框架"
```

**主要选项：**

| 选项 | 简写 | 描述 | 示例 |
|------|------|------|------|
| `--description` | `-d` | 项目描述 | "创建一个RESTful API服务" |
| `--output` | `-o` | 输出目录 | ./my_project |
| `--type` | `-t` | 项目类型 | independent, daip_module, integrated |
| `--strategy` | `-s` | 生成策略 | template, ai, hybrid |
| `--template` | `--` | 使用模板 | flask_api, django_web |
| `--tech-stack` | `--` | 技术栈 | "Python,React,PostgreSQL" |
| `--features` | `-f` | 功能特性 | "认证,缓存,测试" |
| `--interactive` | `-i` | 交互式模式 | 启用交互确认 |
| `--dry-run` | `--` | 预览模式 | 只生成预览，不创建文件 |

#### `daip template`

模板管理命令。

```bash
# 列出所有可用模板
daip template list

# 显示模板详情
daip template show flask_api

# 创建自定义模板
daip template create "我的Flask模板" \
  --source ./my_template \
  --description "适合快速API开发的Flask模板"

# 更新模板
daip template update flask_api

# 删除模板
daip template delete old_template
```

#### `daip scaffold`

脚手架管理命令。

```bash
# 显示脚手架状态
daip scaffold status

# 配置脚手架
daip scaffold config

# 测试脚手架功能
daip scaffold test

# 重置脚手架配置
daip scaffold reset
```

### 高级命令

#### `daip project validate`

验证项目结构和配置。

```bash
# 验证当前目录项目
daip project validate

# 验证指定项目
daip project validate ./my_project

# 严格模式验证
daip project validate --strict

# 生成验证报告
daip project validate --report validation_report.json
```

#### `daip project enhance`

增强现有项目。

```bash
# 添加新功能
daip project enhance --add-feature "用户认证" \
  --template jwt_auth

# 升级项目结构
daip project enhance --upgrade-structure

# 添加最佳实践
daip project enhance --add-best-practices

# 生成文档
daip project enhance --generate-docs
```

#### `daip project migrate`

项目迁移和重构。

```bash
# 分析项目结构
daip project migrate --analyze ./old_project

# 迁移到新架构
daip project migrate ./old_project --to ./new_project \
  --target-architecture microservices

# 重构项目
daip project migrate ./project --refactor \
  --pattern "extract_service_layer"
```

---

## 配置指南

### 全局配置

全局配置文件位置：`~/.daip/scaffold/config.yaml`

```yaml
# 全局脚手架配置
scaffold:
  default_type: independent
  default_strategy: hybrid
  default_output_dir: ./projects

  # LLM配置
  llm:
    provider: openai
    model: gpt-4
    temperature: 0.7
    max_tokens: 4000

  # 模板配置
  templates:
    cache_enabled: true
    auto_update: true
    custom_template_dirs:
      - ~/.daip/templates
      - ./custom_templates

  # 验证配置
  validation:
    strict_mode: false
    auto_fix: true
    ignore_patterns:
      - "*.log"
      - "node_modules/*"

  # 安全配置
  security:
    scan_secrets: true
    validate_dependencies: true
    forbid_patterns:
      - "hardcoded_password"
      - "api_key_in_code"
```

### 项目配置

项目级配置文件：`.daip-scaffold.yaml`

```yaml
# 项目特定配置
project:
  name: "我的Web应用"
  type: independent
  version: "1.0.0"

# 技术栈配置
tech_stack:
  backend:
    framework: Django
    version: "4.2"
    database: PostgreSQL
    cache: Redis

  frontend:
    framework: React
    version: "18"
    styling: Tailwind CSS

# 功能模块
features:
  - name: "用户认证"
    enabled: true
    template: "jwt_auth"
  - name: "API文档"
    enabled: true
    template: "swagger_docs"
  - name: "缓存"
    enabled: true
    config:
      type: "redis"
      ttl: 3600

# 开发配置
development:
  hot_reload: true
  debug_mode: true
  test_coverage: true

# 部署配置
deployment:
  docker: true
  kubernetes: false
  environment_variables:
    - DEBUG=False
    - DATABASE_URL=${DB_URL}
```

### 环境配置

#### 开发环境
```bash
export DAIP_ENV=development
export DAIP_LOG_LEVEL=debug
export DAIP_CACHE_ENABLED=false
```

#### 生产环境
```bash
export DAIP_ENV=production
export DAIP_LOG_LEVEL=info
export DAIP_CACHE_ENABLED=true
```

---

## 模板系统

### 模板结构

标准模板目录结构：

```
my_template/
├── template.yaml              # 模板元数据
├── files/                     # 模板文件
│   ├── {{project_name}}/
│   │   ├── src/
│   │   │   └── main.py
│   │   ├── tests/
│   │   └── README.md
├── hooks/                     # 生命周期钩子
│   ├── pre_generate.py        # 生成前钩子
│   ├── post_generate.py       # 生成后钩子
│   └── validate.py            # 验证钩子
├── variables/                 # 变量定义
│   ├── required.yaml          # 必需变量
│   └── optional.yaml          # 可选变量
└── examples/                  # 示例配置
    └── basic.yaml
```

### 模板配置

**template.yaml示例：**

```yaml
name: "Flask API模板"
version: "1.2.0"
description: "快速创建RESTful API的Flask模板"
author: "DAIP-LIVE Team"
tags: ["flask", "api", "rest", "python"]

# 支持的项目类型
supported_types:
  - independent
  - integrated

# 技术栈
tech_stack:
  language: Python
  framework: Flask
  database: PostgreSQL (可选)
  testing: pytest

# 必需变量
required_variables:
  - name: project_name
    description: "项目名称"
    type: string
    validation: "^[a-zA-Z][a-zA-Z0-9_-]*$"

  - name: project_description
    description: "项目描述"
    type: string
    default: "A Flask REST API application"

# 可选变量
optional_variables:
  - name: enable_auth
    description: "启用用户认证"
    type: boolean
    default: false

  - name: database_type
    description: "数据库类型"
    type: enum
    options: ["postgresql", "mysql", "sqlite"]
    default: "sqlite"

# 功能特性
features:
  - name: "基础API结构"
    included: true
  - name: "用户认证"
    condition: "enable_auth == true"
    template_subdir: "auth"
  - name: "数据库集成"
    condition: "database_type != 'none'"
    template_subdir: "database"

# 依赖配置
dependencies:
  required:
    - Flask>=2.3.0
    - Flask-RESTful>=0.3.10

  optional:
    Flask-JWT-Extended: "enable_auth == true"
    SQLAlchemy: "database_type in ['postgresql', 'mysql']"
    psycopg2-binary: "database_type == 'postgresql'"

# 开发依赖
dev_dependencies:
  - pytest>=7.0.0
  - pytest-cov>=4.0.0
  - black>=23.0.0
  - flake8>=6.0.0
```

### 模板语法

#### 变量替换
```python
# files/{{project_name}}/src/main.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "{{project_description}}"

if __name__ == '__main__':
    app.run(debug={{debug_mode}})
```

#### 条件渲染
```yaml
# 条件包含文件
files/{{project_name}}/auth.py:
  condition: "enable_auth == true"

# 条件内容
{% if enable_auth %}
from flask_jwt_extended import JWTManager
jwt = JWTManager(app)
{% endif %}
```

#### 循环渲染
```python
# 动态生成路由
{% for model in models %}
@app.route('/api/{{model.name | lower}}', methods=['GET', 'POST'])
def {{model.name | lower}}_endpoint():
    """{{model.description}}"""
    pass
{% endfor %}
```

#### 过滤器
```yaml
# 内置过滤器
{{project_name | snake_case}}     # my_project_name
{{project_name | camel_case}}     # myProjectName
{{project_name | kebab_case}}     # my-project-name
{{project_description | title}}  # My Project Description
{{version | default('1.0.0')}}    # 默认值
```

### 自定义模板开发

#### 创建基础模板

```bash
# 创建模板目录
mkdir -p my_template/{files,hooks,variables,examples}

# 创建模板配置
cat > my_template/template.yaml << EOF
name: "我的自定义模板"
version: "1.0.0"
description: "一个简单的基础模板"
EOF

# 创建模板文件
mkdir -p my_template/files/{{project_name}}
cat > my_template/files/{{project_name}}/README.md << EOF
# {{project_name}}

{{project_description}}

## 快速开始

1. 安装依赖
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. 运行应用
   \`\`\`bash
   python main.py
   \`\`\`
EOF
```

#### 添加钩子脚本

```python
# hooks/pre_generate.py
def pre_generate(context):
    """生成前的处理逻辑"""
    project_name = context.get('project_name')

    # 验证项目名称
    if not project_name.isidentifier():
        raise ValueError(f"项目名称 '{project_name}' 不是有效的Python标识符")

    # 添加自定义变量
    context['project_slug'] = project_name.lower().replace('_', '-')

    return context

# hooks/post_generate.py
def post_generate(project_path, context):
    """生成后的处理逻辑"""
    import os

    # 创建虚拟环境
    venv_path = os.path.join(project_path, 'venv')
    os.system(f'python -m venv {venv_path}')

    # 初始化Git仓库
    os.system(f'cd {project_path} && git init')

    print(f"✅ 项目 '{context['project_name']}' 已成功创建！")
    print(f"📍 位置: {project_path}")
    print(f"🔧 下一步: cd {project_path} && source venv/bin/activate")
```

---

## 高级功能

### 插件系统

#### 创建插件

```python
# plugins/my_plugin.py
from daip_live.scaffolding import Plugin

class MyPlugin(Plugin):
    name = "my_plugin"
    version = "1.0.0"

    def on_project_create(self, project, context):
        """项目创建时触发"""
        # 添加自定义文件
        self.add_custom_files(project, context)

        # 执行自定义逻辑
        self.setup_project_structure(project)

    def add_custom_files(self, project, context):
        """添加自定义文件"""
        custom_files = {
            '.myconfig': 'my_custom_config_content',
            'scripts/setup.sh': '#!/bin/bash\necho "Setting up..."'
        }

        for file_path, content in custom_files.items():
            project.add_file(file_path, content)

# 注册插件
plugin = MyPlugin()
register_plugin(plugin)
```

#### 使用插件

```bash
# 安装插件
daip plugin install my_plugin

# 列出已安装插件
daip plugin list

# 启用/禁用插件
daip plugin enable my_plugin
daip plugin disable my_plugin
```

### 批量操作

#### 批量创建项目

```bash
# 从配置文件批量创建
daip project batch-create --config projects.yaml

# projects.yaml示例:
projects:
  - name: "用户服务"
    description: "用户管理微服务"
    template: "microservice"
    tech_stack: "Spring Boot,MySQL"

  - name: "订单服务"
    description: "订单处理微服务"
    template: "microservice"
    tech_stack: "Spring Boot,PostgreSQL"

# 使用脚本批量创建
for service in user order payment inventory; do
  daip project create "${service}-service" \
    --template microservice \
    --description "${service}管理微服务" \
    --output "./microservices/${service}-service"
done
```

#### 批量更新

```bash
# 批量更新项目
daip project batch-update --pattern "./services/*" \
  --add-feature "性能监控" \
  --upgrade-dependencies

# 批量验证
daip project batch-validate --pattern "./projects/*" \
  --report validation_report.json
```

### 集成CI/CD

#### GitHub Actions集成

```yaml
# .github/workflows/scaffold-validate.yml
name: Scaffold Validation

on:
  push:
    paths:
      - '.daip-scaffold.yaml'
      - 'src/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup DAIP-LIVE
      run: |
        curl -sSL https://install.daip.live | bash
        daip setup

    - name: Validate Project
      run: |
        daip project validate --strict

    - name: Generate Documentation
      run: |
        daip project enhance --generate-docs

    - name: Security Scan
      run: |
        daip project scan --security
```

#### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Validate Scaffold') {
            steps {
                sh 'daip project validate --strict'
            }
        }

        stage('Update Dependencies') {
            steps {
                sh 'daip project enhance --update-dependencies'
            }
        }

        stage('Generate Docs') {
            steps {
                sh 'daip project enhance --generate-docs'
                archiveArtifacts artifacts: 'docs/**', fingerprint: true
            }
        }
    }

    post {
        always {
            sh 'daip project validate --report validation.json'
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'validation.json',
                reportName: 'Validation Report'
            ])
        }
    }
}
```

### 团队协作

#### 模板共享

```bash
# 发布模板到团队仓库
daip template publish my_template \
  --repository git@github.com:myorg/daip-templates.git \
  --tag v1.0.0

# 从团队仓库安装模板
daip template install my_template \
  --repository git@github.com:myorg/daip-templates.git

# 同步团队模板
daip template sync --repository git@github.com:myorg/daip-templates.git
```

#### 项目标准化

```bash
# 创建团队标准
daip standards create --name "公司微服务标准" \
  --config-file standards.yaml

# 应用标准到项目
daip project apply-standards ./my_project \
  --standards "公司微服务标准"

# 检查合规性
daip project check-compliance ./my_project \
  --standards "公司微服务标准"
```

---

## 最佳实践

### 项目组织

#### 目录结构最佳实践

```
recommended_project_structure/
├── src/                       # 源代码
│   ├── core/                 # 核心业务逻辑
│   ├── models/               # 数据模型
│   ├── services/             # 业务服务
│   ├── controllers/          # 控制器/视图
│   └── utils/                # 工具函数
├── tests/                    # 测试代码
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── e2e/                  # 端到端测试
├── docs/                     # 文档
│   ├── api/                  # API文档
│   ├── guides/               # 使用指南
│   └── examples/             # 示例代码
├── scripts/                  # 脚本
│   ├── setup.sh              # 环境设置
│   ├── deploy.sh             # 部署脚本
│   └── migrate.sh            # 数据迁移
├── config/                   # 配置文件
│   ├── development.yaml      # 开发环境配置
│   ├── production.yaml       # 生产环境配置
│   └── testing.yaml          # 测试环境配置
├── docker/                   # Docker相关
│   ├── Dockerfile            # 应用镜像
│   ├── docker-compose.yml    # 开发环境
│   └── docker-compose.prod.yml # 生产环境
└── k8s/                      # Kubernetes配置
    ├── deployment.yaml       # 部署配置
    ├── service.yaml          # 服务配置
    └── ingress.yaml          # 入口配置
```

#### 命名规范

```yaml
# 项目命名规范
naming_conventions:
  project_name:
    format: "kebab-case"
    examples: ["user-service", "order-management", "data-processor"]

  file_names:
    format: "snake_case"
    examples: ["user_service.py", "order_controller.js", "data_processor.rs"]

  class_names:
    format: "PascalCase"
    examples: ["UserService", "OrderController", "DataProcessor"]

  function_names:
    format: "snake_case"
    examples: ["get_user", "create_order", "process_data"]
```

### 安全最佳实践

#### 依赖管理

```yaml
# 安全依赖配置
security:
  dependency_scanning:
    enabled: true
    fail_on_vulnerabilities: true

  allowed_licenses:
    - MIT
    - Apache-2.0
    - BSD-3-Clause

  forbidden_packages:
    - requests  # 使用更安全的替代品
    - pickle    # 避免安全风险

  version_constraints:
    ">=1.0.0,<2.0.0"  # 锁定主版本
```

#### 代码安全

```python
# 安全代码模板示例
import os
from cryptography.fernet import Fernet

class SecurityConfig:
    """安全配置类"""

    def __init__(self):
        # 从环境变量读取敏感配置
        self.secret_key = os.environ.get('SECRET_KEY')
        if not self.secret_key:
            raise ValueError("SECRET_KEY环境变量必须设置")

    def encrypt_data(self, data):
        """加密敏感数据"""
        key = Fernet.generate_key()
        f = Fernet(key)
        return f.encrypt(data.encode())

    def validate_input(self, user_input):
        """输入验证"""
        if not isinstance(user_input, str):
            raise TypeError("输入必须是字符串")

        # SQL注入防护
        dangerous_chars = ["'", ";", "--", "/*", "*/"]
        if any(char in user_input for char in dangerous_chars):
            raise ValueError("输入包含危险字符")

        return user_input
```

### 性能优化

#### 项目结构优化

```yaml
# 性能优化配置
performance:
  lazy_loading:
    enabled: true
    modules: ["admin", "reports", "analytics"]

  caching:
    enabled: true
    strategy: "redis"
    ttl: 3600

  database_optimization:
    connection_pooling: true
    max_connections: 20
    query_optimization: true

  static_assets:
    cdn_enabled: true
    compression: true
    minification: true
```

#### 代码优化

```python
# 性能优化示例
import asyncio
from functools import lru_cache
from typing import List

class OptimizedService:
    """优化的服务类"""

    def __init__(self):
        self._cache = {}

    @lru_cache(maxsize=128)
    def expensive_operation(self, param: str) -> str:
        """缓存计算结果"""
        # 模拟耗时操作
        result = self._compute_expensive_result(param)
        return result

    async def batch_process(self, items: List[str]) -> List[str]:
        """批量异步处理"""
        semaphore = asyncio.Semaphore(10)  # 限制并发数

        async def process_item(item):
            async with semaphore:
                return await self._process_single_item(item)

        tasks = [process_item(item) for item in items]
        return await asyncio.gather(*tasks)

    @property
    def cached_data(self):
        """惰性加载缓存数据"""
        if 'data' not in self._cache:
            self._cache['data'] = self._load_data()
        return self._cache['data']
```

### 可维护性

#### 文档自动化

```bash
# 自动生成API文档
daip project enhance --generate-api-docs \
  --format openapi \
  --output docs/api/

# 生成架构图
daip project enhance --generate-architecture-diagram \
  --format svg \
  --output docs/architecture/

# 生成依赖关系图
daip project enhance --generate-dependency-graph \
  --output docs/dependencies/
```

#### 测试自动化

```yaml
# 测试配置
testing:
  unit_tests:
    coverage_threshold: 80
    fail_on_low_coverage: true

  integration_tests:
    enabled: true
    database_memory: true

  e2e_tests:
    enabled: true
    browser: chrome

  performance_tests:
    enabled: true
    load_test_duration: "10m"
    concurrent_users: 100
```

---

## 故障排除

### 常见问题

#### 1. 项目创建失败

**问题：** `daip project create` 命令失败

**排查步骤：**
```bash
# 检查DAIP-LIVE状态
daip status

# 验证配置
daip config validate

# 查看详细日志
daip project create "test" --verbose

# 检查权限
ls -la ./output_directory
```

**常见解决方案：**
```bash
# 权限问题
chmod 755 ./output_directory

# 磁盘空间不足
df -h

# 网络连接问题
ping api.openai.com
```

#### 2. 模板问题

**问题：** 模板不存在或损坏

**解决方法：**
```bash
# 重新下载模板
daip template refresh

# 验证模板完整性
daip template verify flask_api

# 重置模板缓存
daip template cache clear

# 手动安装模板
daip template install flask_api --force
```

#### 3. LLM连接问题

**问题：** AI生成功能不工作

**诊断步骤：**
```bash
# 测试LLM连接
daip llm test

# 检查API密钥
daip config show llm.api_key

# 验证模型可用性
daip model list
```

**解决方案：**
```yaml
# 配置备用提供商
llm:
  primary_provider: openai
  fallback_provider: anthropic
  local_provider: ollama
```

#### 4. 依赖冲突

**问题：** 生成的项目依赖冲突

**解决方法：**
```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 升级依赖管理器
pip install --upgrade pip setuptools wheel

# 解决冲突
daip project resolve-dependencies --strategy upgrade
```

### 调试工具

#### 调试模式

```bash
# 启用详细日志
export DAIP_LOG_LEVEL=debug

# 启用调试模式
daip project create "test" --debug

# 生成调试报告
daip debug report --output debug_report.json
```

#### 性能分析

```bash
# 分析项目生成性能
daip benchmark create --template flask_api --iterations 10

# 分析LLM调用性能
daip llm benchmark --prompt "test" --iterations 5

# 内存使用分析
daip profile memory --command "daip project create test"
```

### 错误代码参考

| 错误代码 | 描述 | 解决方案 |
|----------|------|----------|
| `S001` | 模板不存在 | `daip template install <template_name>` |
| `S002` | 项目名称无效 | 使用有效的项目名称（字母、数字、下划线） |
| `S003` | 输出目录无权限 | 检查目录权限或使用其他目录 |
| `S004` | LLM连接失败 | 检查网络连接和API密钥 |
| `S005` | 依赖冲突 | 使用虚拟环境或解决依赖冲突 |
| `S006` | 模板语法错误 | 检查模板语法和变量定义 |
| `S007` | 磁盘空间不足 | 清理磁盘空间或使用其他位置 |

---

## API参考

### Python API

#### 基础API

```python
from daip_live.scaffolding import ScaffoldEngine, ProjectTemplate

# 创建脚手架引擎
engine = ScaffoldEngine()

# 创建项目
result = await engine.create_project(
    name="my_project",
    description="A sample project",
    template="flask_api",
    output_dir="./my_project"
)

# 检查结果
if result.success:
    print(f"项目创建成功: {result.project_path}")
else:
    print(f"创建失败: {result.errors}")
```

#### 高级API

```python
from daip_live.scaffolding import (
    ProjectConfig,
    GenerationRequest,
    TemplateEngine
)

# 配置项目
config = ProjectConfig(
    name="advanced_project",
    type="independent",
    tech_stack=["Python", "Flask", "PostgreSQL"],
    features=["auth", "api_docs", "testing"]
)

# 创建生成请求
request = GenerationRequest(
    description="创建一个高级Web应用",
    config=config,
    template="advanced_flask",
    custom_variables={
        "enable_caching": True,
        "cache_type": "redis"
    }
)

# 执行生成
result = await engine.generate(request)

# 自定义模板引擎
template_engine = TemplateEngine()
template_engine.register_filter("custom_filter", lambda x: x.upper())

# 使用自定义模板
template = ProjectTemplate.from_directory("./my_template")
result = await template.render(context)
```

### REST API

#### 项目管理

```bash
# 创建项目
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "api_project",
    "description": "REST API项目",
    "template": "flask_api",
    "config": {
      "type": "independent",
      "tech_stack": ["Python", "Flask"]
    }
  }'

# 获取项目状态
curl http://localhost:8000/api/v1/projects/api_project/status

# 列出所有项目
curl http://localhost:8000/api/v1/projects

# 删除项目
curl -X DELETE http://localhost:8000/api/v1/projects/api_project
```

#### 模板管理

```bash
# 获取模板列表
curl http://localhost:8000/api/v1/templates

# 获取模板详情
curl http://localhost:8000/api/v1/templates/flask_api

# 创建模板
curl -X POST http://localhost:8000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom_template",
    "description": "自定义模板",
    "files": {...},
    "config": {...}
  }'
```

### WebSocket API

#### 实时进度监控

```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/scaffold');

// 监听进度更新
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    switch(data.type) {
        case 'progress':
            console.log(`进度: ${data.progress}%`);
            console.log(`当前步骤: ${data.step}`);
            break;

        case 'file_created':
            console.log(`创建文件: ${data.file_path}`);
            break;

        case 'completed':
            console.log('项目创建完成!');
            console.log(`项目路径: ${data.project_path}`);
            break;

        case 'error':
            console.error(`错误: ${data.error}`);
            break;
    }
};

// 发送创建请求
ws.send(JSON.stringify({
    action: 'create_project',
    data: {
        name: 'realtime_project',
        template: 'flask_api',
        description: '实时监控的项目创建'
    }
}));
```

### 配置API

#### 获取和设置配置

```python
import requests

# 获取当前配置
response = requests.get('http://localhost:8000/api/v1/config')
config = response.json()

# 更新配置
new_config = {
    "default_type": "independent",
    "llm": {
        "provider": "openai",
        "model": "gpt-4"
    }
}

response = requests.put(
    'http://localhost:8000/api/v1/config',
    json=new_config
)
```

---

## 附录

### 版本历史

| 版本 | 发布日期 | 主要功能 |
|------|----------|----------|
| 2.0.0 | 2024-01-15 | 重构架构，添加插件系统 |
| 1.5.0 | 2023-12-01 | 添加批量操作和团队协作 |
| 1.2.0 | 2023-10-15 | WebSocket实时监控 |
| 1.0.0 | 2023-08-01 | 初始版本发布 |

### 贡献指南

欢迎为DAIP-LIVE脚手架系统贡献代码！

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 支持和社区

- **文档**: https://docs.daip.live/scaffold
- **GitHub**: https://github.com/daip-live/scaffold
- **社区**: https://community.daip.live
- **问题报告**: https://github.com/daip-live/scaffold/issues

### 许可证

DAIP-LIVE脚手架系统使用MIT许可证。详见[LICENSE](../LICENSE)文件。

---

*本手册持续更新中，最新版本请访问在线文档。*