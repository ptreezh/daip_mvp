# 项目级提示词构建服务设计文档

## 第一性原理分析

### 1. 核心问题识别
- **上下文组装复杂性**: 不同场景需要不同的上下文结构和信息密度
- **模板管理困难**: 静态模板无法适应动态的对话场景和用户需求
- **性能优化需求**: 大量上下文组装导致Token消耗和延迟问题
- **一致性保证**: 跨服务的提示词风格和质量需要统一标准

### 2. 设计原则
1. **解耦原则**: 提示词构建逻辑与业务逻辑完全分离
2. **可扩展性**: 支持新的提示词模板和构建策略
3. **高性能**: 优化Token使用和生成速度
4. **可观测性**: 完整的监控和调试能力

## 架构设计

### 系统级服务层次结构

```
DAIP项目系统
├── 应用层 (FastAPI + CLI)
├── 协议层 (Workflow Manager, Debate Protocol)
├── 核心服务层
│   ├── 提示词构建服务 ← 新增系统级服务
│   ├── 专业角色管理服务 ← 新增系统级服务
│   ├── Role Manager
│   ├── Memory Service
│   └── Wiki Service
├── 虚拟角色聊天层
│   ├── Cognitive Agent
│   ├── Context Optimizer
│   └── SSKG (带CQS接口)
└── 内核层 (LLM Interface, Tool Executor)
```

### 提示词构建服务架构

```
Prompt Building Service (src/core_services/prompt_building_service.py)
├── Context Assembly Engine
│   ├── Dynamic Context Builder
│   ├── Multi-Source Context Merger
│   ├── Context Compression Engine
│   └── Context Quality Validator
├── Template Management System
│   ├── Template Repository
│   ├── Template Version Control
│   ├── Dynamic Template Generator
│   └── Template Performance Analyzer
├── Optimization Engine
│   ├── Token Usage Optimizer
│   ├── Context Relevance Scorer
│   ├── Performance Profiler
│   └── Caching Strategy Manager
└── Quality Assurance System
    ├── Prompt Validator
    ├── Consistency Checker
    ├── A/B Testing Framework
    └── Quality Metrics Collector
```

## 核心组件设计

### 1. Context Assembly Engine

**职责**: 智能组装不同来源的上下文信息

**核心接口**:
```python
class IContextAssemblyEngine(ABC):
    async def assemble_context(
        self, 
        context_spec: ContextSpec,
        sources: List[ContextSource],
        constraints: ContextConstraints
    ) -> AssembledContext
    
    async def optimize_context_size(
        self, 
        context: AssembledContext,
        target_tokens: int
    ) -> OptimizedContext
```

### 2. Template Management System

**职责**: 管理和动态生成提示词模板

**核心接口**:
```python
class ITemplateManager(ABC):
    async def get_template(
        self, 
        template_id: str,
        context: Dict[str, Any]
    ) -> PromptTemplate
    
    async def generate_dynamic_template(
        self,
        scenario: ScenarioSpec,
        requirements: TemplateRequirements
    ) -> PromptTemplate
```

### 3. Optimization Engine

**职责**: 优化提示词性能和效果

**核心接口**:
```python
class IOptimizationEngine(ABC):
    async def optimize_prompt(
        self,
        prompt: Prompt,
        optimization_goals: OptimizationGoals
    ) -> OptimizedPrompt
    
    async def analyze_performance(
        self,
        prompt: Prompt,
        metrics: List[str]
    ) -> PerformanceAnalysis
```

## 实现计划

### 阶段1: 核心架构设计 (当前)
- 设计系统级服务接口
- 定义数据模型和规范
- 确定与现有服务的集成点

### 阶段2: Context Assembly Engine实现
- 实现多源上下文合并
- 实现上下文压缩算法
- 实现质量验证机制

### 阶段3: Template Management实现
- 实现模板仓储
- 实现动态模板生成
- 实现版本控制

### 阶段4: Optimization Engine实现
- 实现Token优化算法
- 实现性能分析
- 实现缓存策略

### 阶段5: Quality Assurance实现
- 实现一致性检查
- 实现A/B测试框架
- 实现质量指标收集

## 技术选型

### 存储层
- **模板存储**: 文件系统 + SQLite索引
- **缓存**: Redis (提示词结果缓存)
- **配置**: YAML配置文件

### 算法选择
- **上下文压缩**: 基于重要性评分的智能截断
- **模板匹配**: 语义相似度 + 规则匹配
- **性能优化**: 遗传算法优化Token分配

### 集成点设计
- **Role Manager**: 获取角色特定的提示词要求
- **Memory Service**: 获取对话历史和上下文信息
- **Wiki Service**: 获取知识库相关内容
- **LLM Interface**: 直接集成优化后的提示词

## 质量保证

### 测试策略
1. **单元测试**: 每个组件独立测试，覆盖率>95%
2. **集成测试**: 跨服务交互测试
3. **性能测试**: Token使用效率和响应时间
4. **A/B测试**: 不同提示词策略的效果对比

### 监控指标
- 平均Token使用量 < 基线的80%
- 提示词生成时间 < 100ms
- 上下文相关性分数 > 0.85
- 模板匹配准确率 > 90%

## 风险评估与缓解

### 技术风险
- **复杂度管理**: 渐进式实现，模块化设计
- **性能瓶颈**: 缓存策略和异步处理
- **质量控制**: 完整的测试和监控体系

### 集成风险
- **向后兼容**: 保持现有接口，逐步迁移
- **服务依赖**: 降级机制和错误处理
- **数据一致性**: 事务性操作和状态同步