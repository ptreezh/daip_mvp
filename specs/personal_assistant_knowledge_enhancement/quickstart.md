# Quickstart Guide: Personal Assistant and Knowledge Base Features

**Feature**: specs/personal_assistant_knowledge_enhancement/spec.md
**Created**: 2025-11-19
**For**: New developers joining the project

## Overview

This guide explains how to use and extend the personal assistant and knowledge base features in the DAIP-LIVE system.

## New Features Added

### 1. Personal Assistant Functionality
The system now recognizes natural language expressions for activating personal assistant services.

**Commands**:
- `/pa` or `/assistant` - Direct command access
- Natural language: "个人助手，请帮我分析这段代码", "PA助手，帮我总结报告", "智能助手，搜索资料" 

**Capabilities**:
- Research assistance
- Content creation
- Translation
- Explanation
- General help

### 2. Knowledge Base Management
Enhanced system for managing and searching local knowledge with semantic search capabilities.

**Commands**:
- `/knowledge sync` - Synchronize knowledge base with local files
- `/knowledge search <query>` - Semantic search in local knowledge
- Natural language: "在知识库中搜索XX", "本地知识查找XX"

**Features**:
- Semantic similarity search using FAISS
- Automatic indexing of new files
- File change detection and re-indexing
- Multi-format support (.txt, .md, .py, etc.)

### 3. Intelligent Parameter Validation
The system now detects missing parameters in user inputs and prompts for clarification.

**Examples**:
- Input: "创建维基" → Output: "请输入维基页面标题"
- Input: "论文" → Output: "请输入搜索关键词"
- Input: "开始辩论" → Output: "请输入辩论主题"

## Technical Implementation

### Intent Recognition Updates

The EnhancedIntentRecognizer now supports:

```python
# In src/daip_live/agent_engine/enhanced_intent_recognizer.py

# Personal assistant patterns
"personal_assistant": {
    "patterns": [r"个人.*助手", r"PA.*助手", r"智能.*助手", ...],
    "extract_params": self._extract_assistant_params,
    ...
}

# Knowledge search patterns  
"knowledge_search": {
    "patterns": [r".*知识库.*搜索.*", r".*在.*知识库.*查找.*", ...],
    "extract_params": self._extract_knowledge_search_params,
    ...
}
```

### Parameter Extraction and Validation

New parameter extraction functions handle missing information:

```python
def _extract_assistant_params(self, text: str, match: re.Match) -> Dict[str, Any]:
    """Extract parameters for personal assistant intent"""
    # Implementation handles missing parameters
```

### Knowledge Base Integration

The KnowledgeManager now supports semantic search:

```python
class KnowledgeManager:
    async def search(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Performs semantic search using vector embeddings"""
```

## Usage Examples

### Basic Personal Assistant Usage
```
用户: 个人助手，请帮我分析这段代码
系统: [启动个人助手分析模式，可能请求更多细节]

用户: PA助手，总结这份报告
系统: [启动总结功能]

用户: 智能助手，搜索AI伦理相关论文
系统: [执行学术搜索]
```

### Knowledge Base Operations
```
用户: /knowledge sync
系统: [同步本地知识，索引新文件]

用户: /knowledge search 深度学习
系统: [显示本地知识库中关于深度学习的匹配文档]

用户: 在知识库中搜索 量子计算
系统: [自动识别为知识库搜索意图]
```

### Wiki Collaboration Enhancement
```
用户: 创建维基 项目计划
系统: [启动多AI角色协作创建维基页面]

用户: 创建维基
系统: [提示用户输入页面标题]
```

## Extending Functionality

### Adding New Assistant Capabilities
1. Add new patterns to `personal_assistant` intent in `enhanced_intent_recognizer.py`
2. Update `_extract_assistant_params` to handle new parameters
3. Create appropriate handlers in TUI/CLI

### Adding Knowledge Base Extensions
1. Extend `KnowledgeManager.search` with new search strategies
2. Update file type handlers for new formats
3. Modify FAISS indexing for different content types

### Parameter Validation Extensions
1. Update `_check_intent_clarification` in `enhanced_intent_recognizer.py`
2. Add new validation rules for missing parameters
3. Customize user prompt messages

## Architecture Principles

- **Event-Driven**: All communication via typed events from core/models.py
- **Modular Design**: Each feature as separate module in src/daip_live/
- **Test-First**: ≥90% coverage requirement (non-negotiable)
- **Convention Over Configuration**: Follow existing naming and structure patterns
- **Natural Language First**: Support intuitive user expressions

## Troubleshooting

### Common Issues
1. **No response to "个人助手"**: Check intent patterns in recognizer
2. **Knowledge sync fails**: Verify knowledge directory exists and contains readable files
3. **Parameter validation not working**: Ensure `requires_clarification` flag is set correctly

### Debugging Tips
- Use `get_available_intents()` to see registered intent patterns
- Check logs for parameter extraction failures
- Verify model provider configuration for knowledge base functions

## Development Guidelines

When adding new features:
1. Update spec.md first (documentation-first approach)
2. Write failing tests before implementation
3. Follow event-driven architecture for all component communication
4. Maintain ≥90% test coverage
5. Add to both CLI and TUI interfaces
6. Follow existing code style and naming conventions