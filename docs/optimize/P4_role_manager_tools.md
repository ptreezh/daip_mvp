# P4 角色与工具管理 (Role & Tool Management)

## 📋 概述

P4模块提供了定义代理角色(`RoleManager`)和其能力(`ToolManager`)的关键基础设施。该模块是代理能力和系统安全的交汇点，实现了安全的多阶段工具执行管道。

## 🔧 核心功能

### 角色管理 (RoleManager)
- **角色加载**: 从`roles/`目录的YAML文件加载角色定义
- **角色验证**: 使用P0中的`RoleConfig`模型验证角色配置
- **系统提示注入**: 注入自省循环的元指令，要求代理提供置信度评分
- **角色缓存**: 在内存中缓存角色对象以提高访问效率

### 工具管理 (ToolManager)
- **@tool装饰器**: 唯一的工具注册机制，使用inspect模块自动创建Pydantic模型
- **6阶段安全执行管道**: 实现完整的工具执行安全检查
- **权限控制**: 基于配置文件的工具执行权限管理

## 🏗️ 系统架构

### 角色管理系统
- **RoleManager**: 负责加载、验证和管理角色配置
- **角色定义**: 以YAML格式存储在`roles/`目录中
- **系统提示注入**: 自动向每个系统提示添加置信度评分指令

### 工具安全执行管道
```
┌─────────────────────────────────────────┐
│         Tool Execution Pipeline         │
├─────────────────────────────────────────┤
│ 1. Discovery      │ Find tool in registry│
├─────────────────────────────────────────┤
│ 2. Input Validation │ Validate args     │
├─────────────────────────────────────────┤
│ 3. Precondition Check │ Write-After-Read │
├─────────────────────────────────────────┤
│ 4. Permission Check │ Allow/Deny/Ask    │
├─────────────────────────────────────────┤
│ 5. Execution      │ Call tool function  │
├─────────────────────────────────────────┤
│ 6. Result Formatting │ Standardize output│
└─────────────────────────────────────────┘
```

## 🛡️ 安全机制

### 6阶段执行管道详解
1. **发现阶段**: 在注册表中查找工具，找不到则失败
2. **输入验证**: 使用工具的Pydantic模型验证参数，验证失败则失败
3. **前置条件检查**: 验证写操作的资源是否已读取(Write-After-Read)
4. **权限检查**: 根据配置执行允许/拒绝/询问操作
5. **执行阶段**: 在try/except块中执行工具函数
6. **结果格式化**: 将返回值或捕获的异常标准化为代理可读格式

### 权限控制系统
- **配置驱动**: 从`config.yaml`中的`ToolPermissionConfig`加载
- **三级权限**: `allow`(允许)、`deny`(拒绝)、`ask`(询问)
- **用户交互**: `ask`模式通过UI层提示用户确认

### 安全策略
- **路径遍历防护**: 验证文件路径在允许的项目目录内
- **依赖检查**: 启动时检查外部命令行工具的存在性
- **沙箱执行**: 在受限环境中执行工具(如适用)

## 🧰 工具系统

### @tool装饰器机制
- **自动注册**: 使用装饰器自动注册函数为工具
- **类型推断**: 使用类型提示自动生成Pydantic验证模型
- **文档提取**: 提取函数文档字符串作为工具描述

### 工具执行上下文
- **SessionContext**: 包含会话上下文信息，如最近读取的资源
- **资源跟踪**: 跟踪读取和写入操作以执行前置条件检查

## 📁 代码结构

```
src/daip_live/p4_role_manager_tools/
├── __init__.py
├── role_manager.py      # 角色管理器
├── tool_manager.py      # 工具管理器，包含6阶段执行管道
├── decorators.py        # @tool装饰器实现
├── models.py            # 角色和工具相关模型
├── interfaces.py        # 角色和工具相关接口
├── security.py          # 安全检查相关功能
├── config.py            # 角色和工具配置管理
└── utils/               # 工具函数
    ├── validation.py    # 输入验证工具
    └── permission.py    # 权限检查工具
```

## 🔐 安全考虑

- **工具执行安全**: 通过6阶段管道确保工具执行安全
- **访问控制**: 基于配置的细粒度权限控制
- **路径安全**: 防止路径遍历攻击
- **输入验证**: 严格的参数验证防止注入攻击

## 🧪 测试策略

- **管道测试**: 为每个执行阶段的每个失败模式编写测试
- **权限测试**: 验证`allow`/`deny`/`ask`权限模式
- **安全测试**: 测试路径遍历防护等安全机制
- **功能测试**: 验证工具注册和执行的完整流程

## 📄 相关规格文档

- `docs/specs/ROLE_MANAGEMENT_REQUIREMENTS.md` - 角色管理需求规格
- `docs/specs/ROLE_MODEL_CONFIGURATION_REQUIREMENTS.md` - 角色模型配置需求规格
- `docs/p4_role_manager_tools/README.md` - P4模块具体实现文档
- `docs/p4_role_manager_tools/SPEC-Roles-From-Directory.md` - 角色从目录加载规格
- `docs/p4_role_manager_tools/SPEC-Roles-From-File.md` - 角色从文件加载规格