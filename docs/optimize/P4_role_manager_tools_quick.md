# P4 角色与工具管理 - 快速概览 (P4 Role & Tool Management - Quick Overview)

## 🎯 核心功能
P4模块提供角色定义和安全工具执行的基础设施。

## 🔧 主要职责
- **角色管理**: 加载和管理AI角色配置
- **工具管理**: 安全的工具执行管道
- **权限控制**: 工具执行的权限管理
- **安全执行**: 6阶段安全执行管道

## 📊 核心组件
- **RoleManager**: 角色管理器
- **ToolManager**: 工具管理器
- **@tool装饰器**: 工具注册机制
- **权限系统**: 工具权限控制

## 🚀 快速启动
- **角色配置**: YAML格式定义
- **工具注册**: @tool装饰器
- **安全管道**: 6阶段执行检查
- **权限策略**: allow/deny/ask

## 📁 相关资源
- [详细设计](P4_role_manager_tools_detailed.md) - 完整的架构和实现细节
- [API参考](P4_role_manager_tools_api.md) - 详细API文档
- [集成指南](P4_role_manager_tools_integration.md) - 与其他模块的集成方式
- [故障排除](P4_role_manager_tools_troubleshooting.md) - 常见问题和解决方案

---
> **需要更详细的信息？** 请查看上述相关资源链接。