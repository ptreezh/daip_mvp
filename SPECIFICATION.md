# DAIP-LIVE Hierarchical Architecture Specification

## Overview
This document specifies the requirements for implementing a hierarchical architecture in DAIP-LIVE with specialized Subagents and a Skills system.

## Core Architecture Hierarchy
1. **User Interaction Layer** - TUI/GUI interfaces for user input and output
2. **Subagent Management Layer** - Orchestrates and manages specialized Subagents
3. **Specialized Subagent Layer** - Domain-specific expert agents
4. **Skills Layer** - Modular, reusable capabilities
5. **Model Layer** - Chinese language model providers

## Specialized Theory Subagents

### 1.扎根理论专家 (Grounded Theory Expert)
- **Purpose**: Chinese qualitative data localization coding and theory construction
- **Capabilities**:
  - Chinese text coding and categorization
  - Theory building from qualitative data
  - Localization of Western theoretical frameworks
  - Concept mapping and relationship identification

### 2.SNA专家 (Social Network Analysis Expert)
- **Purpose**: Chinese social relationship network analysis and localization interpretation
- **Capabilities**:
  - Social network visualization and analysis
  - Relationship pattern identification
  - Cultural context interpretation
  - Network metrics calculation

### 3.场域分析专家 (Field Analysis Expert)
- **Purpose**: Chinese education/academic field analysis and capital structure examination
- **Capabilities**:
  - Field theory application to Chinese contexts
  - Capital structure analysis (economic, cultural, social)
  - Power dynamics identification
  - Institutional analysis

### 4.ANT专家 (Actor-Network Theory Expert)
- **Purpose**: Science and technology policy/healthcare network analysis and localization tracking
- **Capabilities**:
  - Actor-network mapping
  - Technology and society relationship analysis
  - Policy network tracing
  - Healthcare system analysis

### 5.中文本土化专家 (Chinese Localization Expert)
- **Purpose**: Concept localization, methodology adaptation, and language optimization
- **Capabilities**:
  - Concept translation and adaptation
  - Methodology localization
  - Language optimization for Chinese contexts
  - Cultural sensitivity adjustment

## Skills System

### Core Principles
1. **Modular Design**: Each skill is independently developed and tested
2. **Chinese Optimization**: Preprocessing, postprocessing, and format optimization for Chinese
3. **Dynamic Loading**: Support for loading new skills from marketplace
4. **Collaboration Mechanism**: Multi-skill combination execution
5. **Task Decomposition**: Complex tasks automatically broken into subtasks
6. **Subagent Allocation**: Optimal Subagent selection based on capability matching
7. **Parallel Execution**: Independent tasks processed in parallel
8. **Result Synthesis**: Intelligent aggregation of multi-Subagent results

### Skill Characteristics
- **Self-contained**: Each skill has clear inputs, outputs, and functionality
- **Versioned**: Skills can be updated independently
- **Configurable**: Parameters can be adjusted for specific use cases
- **Traceable**: Execution history and performance metrics tracked
- **Reusable**: Skills can be combined in different workflows

## Integration Requirements
- Seamless integration with existing DAIP-LIVE architecture
- Backward compatibility with current features
- Performance optimization for parallel execution
- Robust error handling and recovery mechanisms
- Comprehensive logging and monitoring capabilities