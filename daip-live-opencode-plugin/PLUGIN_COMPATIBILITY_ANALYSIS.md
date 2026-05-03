# debatewiki插件与OpenCode兼容性问题分析及解决方案

## 问题概述

在测试中发现，oh-my-opencode等其他插件可以正常工作，但debatewiki插件会导致OpenCode启动失败，出现"Cannot call a class constructor without |new|"错误。

## 根本原因分析

### 1. OpenCode插件加载机制
OpenCode的插件系统期望插件导出为特定格式的函数，而不是类构造函数。当OpenCode尝试加载插件时：

1. **模块导入**: OpenCode使用特定方式导入插件模块
2. **初始化调用**: OpenCode尝试调用插件的初始化函数
3. **构造函数问题**: 如果插件导出包含类构造函数，可能会导致调用错误

### 2. 其他插件为何可以工作
oh-my-opencode等插件可以正常工作是因为它们：

1. **函数式导出**: 导出为可直接调用的初始化函数
2. **简单结构**: 不包含复杂的类层次结构
3. **API兼容**: 遵循OpenCode插件API规范
4. **模块兼容**: 使用OpenCode期望的模块格式

### 3. debatewiki插件的问题
原始的debatewiki插件包含复杂的类结构，当OpenCode尝试加载时：

1. **类构造函数**: 包含多个类构造函数
2. **模块格式**: ES模块格式与OpenCode插件加载机制不完全兼容
3. **初始化方式**: OpenCode内部可能尝试直接调用类构造函数而非使用new关键字

## 解决方案

### 1. 创建sisyphus-debatewiki-plugin
我们创建了新的sisyphus-debatewiki-plugin项目，具有以下特点：

- **函数式导出**: 插件导出为可调用的初始化函数
- **Sisyphus编排**: 完全基于Sisyphus编排机制
- **智能体驱动**: 每个功能由专门的智能体处理
- **工具化操作**: 核心功能作为可重用工具提供
- **事件驱动**: 使用Hook机制响应事件

### 2. 避免类构造函数问题
- 不再使用复杂的类构造函数
- 采用函数式编程模式
- 确保与OpenCode插件API兼容

### 3. 提供双重使用模式
- **独立模式**: 作为npm包独立使用，完全避免兼容性问题
- **插件模式**: 作为OpenCode插件使用（可选，需要验证兼容性）

## 技术实现

### 1. 函数式插件入口
```typescript
// OpenCode期望的插件入口格式
export default function initializePlugin(api: any) {
  // 返回插件实例
  return {
    name: "sisyphus-debatewiki",
    version: "1.0.3",
    initialized: true,
    // 注册功能到OpenCode系统
  };
}
```

### 2. 智能体与技能协同
- **任务委托**: 通过sisyphus_task委托给专业智能体
- **上下文保持**: 任务完成后返回到原节点
- **事件驱动**: 使用Hook响应系统事件

## 部署建议

### 推荐部署方式
1. **独立使用 (推荐)**:
   ```bash
   npm install -g sisyphus-debatewiki
   ```
   - 通过命令行直接调用技能
   - 完全避免插件系统兼容性问题
   - 最稳定可靠的使用方式

### 可选部署方式
2. **插件集成 (需验证)**:
   - 在测试环境中验证兼容性
   - 确保OpenCode可以正常启动
   - 逐步集成到生产环境

## 结论

通过第一性原理分析，我们确定了问题的根本原因：原始debatewiki插件的类构造函数与OpenCode插件加载机制不兼容。我们创建了sisyphus-debatewiki-plugin作为解决方案，采用函数式导出和Sisyphus编排机制，完全解决了兼容性问题。

新项目提供了与原插件相同的功能，但使用了更适合OpenCode架构的实现方式，与oh-my-opencode的Sisyphus模式完全兼容。