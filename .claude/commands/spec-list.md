<!-- spec-list 命令 -->
列出所有可用的规范文档模板。

**用法**: `/spec-list`

**输出内容**:
- 所有可用模板的名称
- 模板的基本描述
- 模板的使用方法

**示例输出**:
```
📋 可用模板:

📄 requirements - 软件需求规格文档模板
📄 implementation-plan - 实施计划文档模板
📄 api-spec - API规格文档模板
📄 system-architecture - 系统架构设计文档模板

使用方法: /spec-create <模板名称> <输出文件> [参数]
```

**执行操作**:
1. 扫描 `.spec-kit/templates/` 目录
2. 列出所有 `.md.j2` 模板文件
3. 显示模板的基本信息