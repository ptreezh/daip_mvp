# 工作流引擎使用指南

本文档提供了关于如何使用制度原语系统的工作流引擎（WorkflowEngine）的详细指南。工作流引擎是制度原语系统的核心组件，用于编排复杂的工作流程，协调多个原语节点的执行。

## 概述

工作流引擎提供以下核心功能：

1. **工作流定义**：通过声明式API定义包含节点和边的工作流
2. **工作流执行**：执行工作流并管理执行状态
3. **并行执行**：支持节点的并行执行
4. **状态管理**：维护工作流执行状态
5. **错误处理**：处理节点执行失败和异常情况
6. **监控和指标**：提供工作流执行的监控和指标

## 基本概念

### 工作流定义

工作流定义由以下组件组成：

- **节点（Nodes）**：工作流中的任务单元，每个节点对应一个制度原语
- **边（Edges）**：节点之间的连接，定义执行顺序和数据流
- **参数（Parameters）**：工作流的输入参数

### 制度原语

制度原语是工作流中的基本执行单元，它们封装了原子能力，如事实提取、观点综合、投票等。每个原语都实现了`InstitutionalPrimitive`接口。

## 使用示例

### 1. 创建原语注册表

首先，创建一个原语注册表并注册所需的原语：

```python
from src.institutional_primitives.registry import PrimitiveRegistry

# 创建原语注册表
registry = PrimitiveRegistry()

# 注册原语
registry.register_primitive("generation", GenerationPrimitive)
registry.register_primitive("fact_extraction", FactExtractionPrimitive)
registry.register_primitive("validation", ValidationPrimitive)
registry.register_primitive("synthesis", SynthesisPrimitive)
```

### 2. 创建工作流引擎

使用原语注册表创建工作流引擎：

```python
from src.institutional_primitives.workflow_engine import WorkflowEngine

# 创建工作流引擎
engine = WorkflowEngine(primitive_registry=registry)
```

### 3. 定义工作流

定义包含节点和边的工作流：

```python
from src.institutional_primitives.workflow_engine import WorkflowDefinition, WorkflowNode, WorkflowEdge

# 定义批判性审查工作流
critical_review_workflow = WorkflowDefinition(
    id="critical_review",
    name="批判性审查工作流",
    description="用于对生成内容进行批判性审查的工作流",
    nodes=[
        WorkflowNode(id="generate", type="generation"),
        WorkflowNode(id="extract_facts", type="fact_extraction"),
        WorkflowNode(id="validate_facts", type="validation"),
        WorkflowNode(id="synthesize", type="synthesis")
    ],
    edges=[
        WorkflowEdge(from_node="generate", to_node="extract_facts"),
        WorkflowEdge(from_node="extract_facts", to_node="validate_facts"),
        WorkflowEdge(from_node="validate_facts", to_node="synthesize")
    ]
)
```

### 4. 执行工作流

执行工作流并获取结果：

```python
import asyncio

# 执行工作流
result = await engine.execute_workflow(
    critical_review_workflow,
    {
        "topic": "人工智能",
        "role": "AI研究员"
    }
)

# 处理结果
print(f"工作流状态: {result.status}")
print(f"输出: {result.outputs}")
```

### 5. 监控工作流

获取工作流执行状态：

```python
# 获取工作流状态
status = engine.get_workflow_status(result.execution_id)
print(f"进度: {status.progress * 100:.1f}%")
print(f"已完成节点: {status.completed_nodes}")
```

### 6. 控制工作流执行

暂停、恢复或取消工作流：

```python
# 暂停工作流
await engine.pause_workflow(execution_id)

# 恢复工作流
await engine.resume_workflow(execution_id)

# 取消工作流
await engine.cancel_workflow(execution_id)
```

## 高级用法

### 条件执行

可以在边上定义条件，控制节点的执行：

```python
WorkflowEdge(
    from_node="validate_facts",
    to_node="revision",
    condition="confidence < 0.8"  # 条件表达式
)
```

### 并行执行

通过定义多个输入边，可以实现节点的并行执行：

```python
# 并行节点
WorkflowNode(id="reviewer_a", type="review"),
WorkflowNode(id="reviewer_b", type="review"),
WorkflowNode(id="reviewer_c", type="review"),

# 聚合节点
WorkflowNode(id="aggregate_reviews", type="aggregation"),

# 边定义
WorkflowEdge(from_node="extract_facts", to_node="reviewer_a"),
WorkflowEdge(from_node="extract_facts", to_node="reviewer_b"),
WorkflowEdge(from_node="extract_facts", to_node="reviewer_c"),
WorkflowEdge(from_node="reviewer_a", to_node="aggregate_reviews"),
WorkflowEdge(from_node="reviewer_b", to_node="aggregate_reviews"),
WorkflowEdge(from_node="reviewer_c", to_node="aggregate_reviews"),
```

### 错误处理

可以定义错误处理节点，处理执行失败的情况：

```python
# 错误处理节点
WorkflowNode(id="error_handler", type="error_handling"),

# 边定义
WorkflowEdge(from_node="validate_facts", to_node="error_handler", condition="error"),
```

## 最佳实践

1. **模块化设计**：将复杂工作流拆分为可重用的子工作流
2. **错误处理**：为关键节点添加错误处理逻辑
3. **参数验证**：在原语中验证输入参数
4. **状态持久化**：对于长时间运行的工作流，考虑持久化状态
5. **监控和日志**：使用工作流引擎提供的监控和指标功能

## 常见工作流模式

### 1. 批判性审查工作流

```
生成节点 -> 事实提取节点 -> 并行审查节点 -> 证据汇总节点 -> 共识计算节点 -> 修订节点
```

### 2. 多视角综合工作流

```
任务分解节点 -> 并行探索节点 -> 观点收集节点 -> 观点综合节点
```

### 3. 迭代改进工作流

```
生成节点 -> 评估节点 -> 条件判断 -> (满足条件) -> 输出节点
                     |
                     -> (不满足条件) -> 改进节点 -> 生成节点
```

## 故障排除

### 常见问题

1. **节点执行失败**：检查原语实现和输入参数
2. **工作流卡住**：检查节点依赖关系和条件表达式
3. **性能问题**：优化并行执行和资源分配

### 调试技巧

1. 使用`get_workflow_status`获取详细的执行状态
2. 检查执行跟踪中的错误信息
3. 启用详细日志记录

## 结论

工作流引擎是制度原语系统的核心组件，它使我们能够构建复杂的社会工程工作流，协调多个AI角色和服务之间的交互。通过合理设计工作流，我们可以实现高度可靠、透明和可审计的AI协作过程。