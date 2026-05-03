# DAIP-LIVE 规范文档总览 (Specification Documentation Overview)

## 📋 概述

本文档汇总了DAIP-LIVE项目的所有规范文档，按照功能模块和主题进行分类，便于AI系统理解和检索。

## 📚 文档分类

### 1. 智能体记忆与学习系统 (Agent Memory & Learning System)
- **路径**: `docs/specs_agent_memory/`
- **内容**: 智能体记忆与自学习系统的分析、技术规格、实施计划等
- **相关文档**:
  - `agent_memory_learning_analysis.md` - 智能体记忆与学习系统分析
  - `agent_memory_learning_implementation_plan.md` - 实施计划
  - `agent_memory_learning_technical_spec.md` - 技术规格
  - `advanced_agent_memory_brainstorming.md` - 高级头脑风暴
  - `agent_memory_project_structure.md` - 项目结构

### 2. 架构规范 (Architecture Specifications)
- **路径**: `docs/specs_architecture/`
- **内容**: 系统架构设计、分层架构计划等
- **相关文档**:
  - `HIERARCHICAL_ARCHITECTURE_PLAN.md` - 分层架构计划

### 3. 设计规范 (Design Specifications)
- **路径**: `docs/specs_design/`
- **内容**: 系统设计文档、任务系统设计等
- **相关文档**:
  - `DESIGN.md` - 系统设计文档
  - `task_system_design.md` - 任务系统设计

### 4. 规划与实施 (Planning & Implementation)
- **路径**: `docs/specs_planning/`
- **内容**: 实施计划、重构计划等
- **相关文档**:
  - `IMPLEMENTATION_PLAN.md` - 实施计划
  - `P5_P6_P7_REFACTORING_PLAN.md` - P5-P7模块重构计划
  - `IMPLEMENTATION_SUMMARY.md` - 实施总结

### 5. 意图识别规范 (Intent Recognition Specifications)
- **路径**: `docs/specs_intent_recognition/`
- **内容**: 意图识别相关规范和用户指南
- **相关文档**:
  - `cli_intent_recognition_task.md` - CLI意图识别任务
  - `CONTEXTUAL_INTENT_SOLUTION_USER_GUIDE.md` - 上下文意图解决方案用户指南

### 6. 辩论系统规范 (Debate System Specifications)
- **路径**: `docs/specs_debate/`
- **内容**: 辩论系统模块化分析等相关文档
- **相关文档**:
  - `debate_modularization_analysis_goals.md` - 辩论模块化分析目标

### 7. 维基系统规范 (Wiki System Specifications)
- **路径**: `docs/specs_wiki/`
- **内容**: 维基系统相关规范文档
- **相关文档**: (待补充)

### 8. 分析与评估 (Analysis & Evaluation)
- **路径**: `docs/specs_analysis/`
- **内容**: 项目设计原则分析等
- **相关文档**:
  - `KISS_YAGNI_SOLID_analysis.md` - KISS/YAGNI/SOLID原则分析

## 🔍 检索说明

AI系统可通过以下方式快速定位所需信息：

1. **按功能模块检索**：根据所需功能确定对应模块目录
2. **按文档类型检索**：分析、设计、规划、技术规格等
3. **按关键字检索**：在对应目录中搜索特定概念或功能

## 🏗️ 系统架构说明

DAIP-LIVE采用模块化单体架构，分为P0-P8共9个核心模块：
- **P0**: 核心接口与类型定义
- **P1**: 数据持久化
- **P2**: 知识管理器
- **P3**: 模型提供者
- **P4**: 角色与工具管理
- **P5**: 代理引擎
- **P6**: CLI/TUI界面
- **P7**: GUI界面
- **P8**: 高级系统（辩论、维基等）

## 🔄 更新说明

所有新创建的规范文档应按照上述分类原则存放，保持文档结构的一致性和可维护性。

## 📌 交叉引用

- 主项目规格：`docs/specs/PROJECT_SPEC.md`
- 系统架构：`docs/specs/SYSTEM_ARCHITECTURE.md`
- 详细架构：`docs/specs/DETAILED_SYSTEM_ARCHITECTURE.md`
- 各模块规格：`docs/p{N}/` 目录下