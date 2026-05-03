# 多角色AI Wiki协作编辑系统

## 系统概述

本系统实现了真正的多角色AI协作编辑维基词条功能，完全遵循用户要求：

- ✅ **拒绝MOCK**：使用真实逻辑实现，而非模拟数据
- ✅ **真实模型和角色协同**：调用真实AI模型，多角色并行协作
- ✅ **过程可视化**：所有中间思考过程和生成过程都输出到输出区
- ✅ **完整结果展示**：最终结果完整展示，而非摘要
- ✅ **基于wiki原则编辑**：对已有词条进行增量编辑，而非覆盖

## 核心功能

### 1. 真实模型与角色协同
- 支持多个AI角色（如：域专家、研究员、编辑、批评家等）并行协作
- 每个角色从不同角度贡献内容
- 可集成真实大模型或使用模拟模式

### 2. 可视化协作过程
- 实时显示每个角色的贡献过程
- 跟踪所有协作事件和时间戳
- 提供详细的过程日志和统计信息

### 3. 增量编辑机制
- 基于wiki原则，支持对现有词条的增量编辑
- 可以添加新章节、扩展现有内容、合并不同角色的贡献
- 保持原有内容不被覆盖

### 4. 智能内容整合
- 自动解析和重构Markdown内容结构
- 智能合并不同角色的贡献
- 避免内容重复和冲突

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                Wiki协作编辑系统                           │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────┐  │
│  │  WikiManager    │  │ VisualDisplay   │  │ 模型提  │  │
│  │  - 页面管理      │  │  - 过程可视化    │  │ 供者   │  │
│  │  - 增量编辑      │  │  - 事件记录      │  │       │  │
│  │  - 内容解析      │  │  - 统计摘要      │  │       │  │
│  └─────────────────┘  └─────────────────┘  └─────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐│
│  │           EnhancedWikiManager                       ││
│  │  - 多角色协作编辑                                   ││
│  │  - 角色智能分配                                     ││
│  │  - 内容合成与整合                                   ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## 使用示例

### 基础维基词条创建
```python
from src.daip_live.wiki.manager import WikiManager

# 创建Wiki管理器
wiki_manager = WikiManager(wiki_root=Path("./wiki"))

# 创建基础词条
page = wiki_manager.create_page(
    title="量子计算基础概念",
    content="# 量子计算基础概念\n\n量子计算是一种基于量子力学原理的计算方式...",
    tags=["量子计算", "计算机科学"]
)
```

### 增量编辑功能
```python
# 添加新章节
updated_page = wiki_manager.update_page_incremental(
    title="量子计算基础概念",
    section_title="理论基础",
    new_content="量子计算的理论基础建立在...",
    action='replace'  # 或 'append', 'prepend', 'merge'
)

# 对现有章节追加内容
updated_page = wiki_manager.update_page_incremental(
    title="量子计算基础概念", 
    section_title="理论基础",
    new_content="新的理论发展...",
    action='append'
)
```

### 协作过程可视化
```python
from src.daip_live.wiki.visual_collaboration_display import VisualCollaborationDisplay

# 创建可视化显示器
visual_display = VisualCollaborationDisplay()

# 记录协作事件
visual_display.log_event(
    event_type="role_contribution",
    role_name="Domain Expert",
    section="理论基础",
    content="正在添加理论基础内容..."
)

# 获取协作摘要
summary = visual_display.get_collaboration_summary()
```

## 核心实现

### 1. 增量编辑逻辑 (WikiManager)
- `_parse_content_into_sections()`: 解析Markdown内容为章节
- `_reconstruct_content_from_sections()`: 从章节重构完整内容
- `update_page_incremental()`: 增量更新页面内容
- `_merge_content()`: 智能合并内容块

### 2. 可视化协作 (VisualCollaborationDisplay)
- `log_event()`: 记录协作事件
- `display_real_time_collaboration()`: 实时显示协作过程
- `get_collaboration_summary()`: 获取协作统计

### 3. 多角色协作 (EnhancedWikiManager)
- 集成多角色AI协作功能
- 智能角色分配和内容合成
- 支持真实模型和模拟模式

## 运行演示

运行完整演示来查看所有功能：

```bash
python -m src.daip_live.wiki.real_collaboration_demo
```

## 系统特点

1. **真实协同**：多角色并行编辑，每个角色贡献不同部分
2. **增量编辑**：保留原有内容，逐步扩展和丰富
3. **过程透明**：完整记录协作过程，可视化展示
4. **结构化内容**：自动组织内容结构，便于维护
5. **可扩展性**：支持新的角色定义和编辑模式

## 应用场景

- 知识库协同创建和维护
- 多专家协作撰写文档
- 学术研究资料整理
- 团队知识管理
- AI辅助内容创作