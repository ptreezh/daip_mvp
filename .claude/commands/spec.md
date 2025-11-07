# spec.kit 规范管理命令

## 概述

spec.kit 是 Claude Code CLI 的规范管理工具，用于创建和管理标准化的需求规格文档、实施计划文档等。

## 使用方法

### 初始化规范项目
```bash
spec-kit init <项目名称> [--description <项目描述>]
```

**示例:**
```bash
spec-kit init "DAIP-LIVE重构项目" --description "P5-P7模块重构规范管理"
```

### 创建规范文档
```bash
spec-kit create <模板名称> <输出文件> [--var key=value]
```

**可用模板:**
- `requirements` - 软件需求规格文档
- `implementation-plan` - 实施计划文档
- `api-spec` - API规格文档
- `system-architecture` - 系统架构设计文档

**示例:**
```bash
# 创建需求规格文档
spec-kit create requirements docs/requirements.md --var project_name="DAIP-LIVE P5重构" --var version="1.0.0"

# 创建实施计划文档
spec-kit create implementation-plan docs/plan.md --var project_name="DAIP-LIVE" --var duration="12周"
```

### 列出所有模板
```bash
spec-kit list
```

### 验证规范文档
```bash
spec-kit validate <文档路径>
```

### 查看项目状态
```bash
spec-kit status
```

## 配置文件

spec.kit 在 `.spec-kit/config.yaml` 中存储配置：

```yaml
version: "1.0.0"
default_author: "Claude Code"
default_language: "zh-CN"
output_format: "markdown"
auto_timestamp: true
template_variables:
  project_name: "DAIP-LIVE"
  company: ""
  department: ""
```

## 工作流程

1. **初始化项目**: 使用 `spec-kit init` 创建规范项目
2. **创建文档**: 使用 `spec-kit create` 基于模板创建规范文档
3. **验证文档**: 使用 `spec-kit validate` 检查文档完整性
4. **更新配置**: 编辑 `.spec-kit/config.yaml` 自定义配置

## 模板变量

在创建文档时可以使用以下变量：

- `project_name` - 项目名称
- `version` - 版本号
- `author` - 作者
- `created_date` - 创建日期
- `description` - 描述

## 输出格式

spec.kit 支持 Markdown 格式输出，便于与现有的文档工具链集成。