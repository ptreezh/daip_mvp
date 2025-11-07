<!-- spec-init 命令 -->
初始化一个新的规范项目，用于管理需求规格文档和计划文档。

**用法**: `/spec-init <项目名称> [--description <项目描述>]`

**参数**:
- `项目名称`: 规范项目的名称
- `--description`: 可选，项目描述

**示例**:
```bash
/spec-init "DAIP-LIVE P5重构"
/spec-init "DAIP-LIVE P6组件化" --description "TUI组件化重构项目"
```

**执行操作**:
1. 在 `.spec-kit/` 目录创建项目配置
2. 初始化默认模板（需求规格、实施计划、API规格、系统架构）
3. 创建配置文件 `config.yaml`

**输出**: 项目初始化成功信息和配置文件路径