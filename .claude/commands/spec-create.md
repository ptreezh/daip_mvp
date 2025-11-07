<!-- spec-create 命令 -->
基于模板创建规范文档。

**用法**: `/spec-create <模板名称> <输出文件> [--var key=value]`

**参数**:
- `模板名称`: 可用模板包括：
  - `requirements` - 软件需求规格文档
  - `implementation-plan` - 实施计划文档
  - `api-spec` - API规格文档
  - `system-architecture` - 系统架构设计文档
- `输出文件`: 输出文档的路径
- `--var`: 可选，模板变量（可多次使用）

**示例**:
```bash
# 创建需求规格文档
/spec-create requirements docs/P5_REFACTORING_REQUIREMENTS.md --var project_name="DAIP-LIVE P5重构" --var version="1.0.0"

# 创建实施计划文档
/spec-create implementation-plan docs/P5_IMPLEMENTATION_PLAN.md --var project_name="DAIP-LIVE P5重构" --var duration="4周" --var manager="系统架构师"

# 创建系统架构文档
/spec-create system-architecture docs/P5_ARCHITECTURE.md --var system_name="P5 Agent Engine" --var architect="架构团队"
```

**常用模板变量**:
- `project_name` - 项目名称
- `version` - 版本号
- `author` - 作者（从配置文件获取）
- `created_date` - 创建日期（自动生成）
- `description` - 项目描述
- `duration` - 预计工期
- `manager` - 项目经理

**执行操作**:
1. 读取指定模板文件
2. 替换模板变量
3. 创建输出目录（如果不存在）
4. 生成规范文档

**输出**: 文档创建成功信息和文件路径