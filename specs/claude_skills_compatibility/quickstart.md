# Quickstart Guide: Claude Skills Integration

**Feature**: specs/claude_skills_compatibility/spec.md
**Created**: 2025-11-19
**For**: New developers and users wanting to leverage Claude Skills features

## Overview

This guide explains how to use and extend the Claude Skills integration in DAIP-LIVE, allowing seamless integration of external Claude-compatible skills into the DAIP-LIVE system.

## Core Capabilities

### 1. Claude Skills Format Compatibility
The system now supports Claude Skills format including:
- **manifest.json** - Defines skill metadata (name, description, version, etc.)
- **tools.json** - Defines skill tools and their JSON Schema parameters
- **Automatic parsing** - Converts Claude format to DAIP-LIVE internal format
- **Security isolation** - Sandboxed execution for safety

### 2. Natural Language Integration
Users can now interact with Claude Skills using natural language:

```
> 论文 人工智能
# System automatically finds relevant Claude Skills for paper search

> 创建维基 项目计划
# System uses appropriate skills for wiki creation

> 帮我分析这段文本
# System identifies and executes text analysis skill
```

### 3. Progressive Disclosure
The system provides information gradually based on user needs:
- Stage 1: Basic skill listing with descriptions
- Stage 2: Parameter requirements and JSON Schema
- Stage 3: Examples and usage patterns
- Stage 4: Execution results and feedback

## Usage Examples

### Via Natural Language (Recommended)
```
# Search for papers
> 论文 量子计算
> 搜索关于量子计算的论文

# Create wiki pages
> 创建维基 人工智能伦理
> 写个维基 机器学习

# Use Claude Skills
> 帮我分析这份文档
> 查找相关信息
> 智能助手帮我处理这个数据
```

### Via Explicit Commands
```
# Skill management
/knowledge skill list                # List all available skills
/knowledge skill search <query>     # Search for specific skills  
/knowledge skill run <skill> <params> # Run a specific skill with parameters

# For Claude-specific skills
/skill list                        # List Claude skills
/skill info <skill_name>           # Show skill details and parameters
/skill run <skill_name> "query"    # Execute Claude skill
```

### Parameter Clarification
If you provide an incomplete request, the system will ask for missing information:

```
> 创建维基
# System responds: "请输入维基页面标题，例如：创建维基 人工智能"

> 论文
# System responds: "请输入搜索关键词，例如：论文 人工智能"
```

## Skill Architecture

### Claude Skills Integration Flow
```
1. User Input: Natural language or specific command
2. Intent Recognition: Identifies if Claude Skills are relevant
3. Skill Mapping: Finds appropriate Claude Skill based on JSON Schema and functionality
4. Parameter Validation: Validates against JSON Schema specification
5. Security Check: Ensures safe execution with resource limits
6. Skill Execution: Runs in secure sandbox environment
7. Result Processing: Returns formatted results to user
```

### Key Components
- **ClaudeSkillAdapter**: Converts Claude format to DAIP format
- **ClaudeSkillRepository**: Manages download and discovery from GitHub
- **ClaudeSkillSandbox**: Provides secure execution environment
- **ProgressiveSkillInfoService**: Handles gradual information disclosure
- **ClaudeSkillMapper**: Maps natural language to appropriate skills

## Integration Points

### With Existing Systems
- **Intent Recognition**: Seamlessly integrated with existing natural language processing
- **TUI**: Works within the Textual-based terminal UI
- **Event System**: Communicates via standard DAIP-LIVE events
- **Session Management**: Preserves context during skill execution
- **Permission System**: Respects user permission controls

## Security Features

### Sandboxing
- Network access limited to specified domains
- Execution time limits (default 30 seconds)
- Resource consumption monitoring
- Isolated execution environment

### Authentication
- Secure credential handling
- API key validation
- Authentication requirement detection

## Development Guidelines

### Adding New Claude Skills
1. Place Claude Skills directory containing `manifest.json` and `tools.json` in the skills directory
2. The system will automatically discover, parse, and register them
3. Skills will appear in natural language recognition

### Creating Claude-Compatible Skills
Follow the Claude Skills format specifications:
1. Create `manifest.json` with skill metadata
2. Create `tools.json` with tool definitions and JSON Schema
3. Ensure parameter validation compliance
4. Test in sandboxed environment

## Best Practices

1. **Security First**: Always validate security requirements for new skills
2. **Natural Language**: Design skills to work with common user expressions
3. **Progressive Info**: Provide clear, gradual information to users
4. **JSON Schema**: Use clear and comprehensive JSON Schema for parameters
5. **Error Handling**: Implement graceful error handling and user feedback

## Troubleshooting

### Common Issues
1. **Skill not recognized**: Check if manifest.json is valid JSON
2. **Missing parameters**: System will prompt for required parameters based on JSON Schema
3. **Authentication failures**: Ensure credentials are properly configured
4. **Execution timeouts**: Increase timeout in security policy if needed
5. **Network restrictions**: Update allowed domains in security policy

### Debugging Skills
- Use `/skill list` to see available skills
- Use `/skill info <skill_name>` to see parameter requirements
- Check system logs for detailed execution information

## Performance Considerations

- Claude Skills execution time is limited by security policy
- HTTP requests are subject to timeout controls
- Large responses may be truncated for display
- Execution context is preserved for multi-turn skills

## Future Extensions

- **Skill Marketplace**: Centralized repository of verified Claude Skills
- **Skill Chaining**: Multiple skills working in sequence
- **Visual Interfaces**: Web UI for skill discovery and management
- **Advanced Analytics**: Skill usage and effectiveness metrics

---

**Ready to use**: Claude Skills integration is now fully operational. Simply place Claude-compatible skills in the skills directory or add via natural language expressions!