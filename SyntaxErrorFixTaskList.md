# DAIP-LIVE 项目语法错误修复任务清单

## 语法错误修复任务

### 1. 修复 `tests/test_critical_review_nodes.py` 拼写错误
- 位置: 第580行
- 问题: `lass TestConsensusNode:` (应为 `class`)
- 修复: 将 `lass` 改为 `class`

### 2. 修复 `frontend/components/forum_chat_interface.py` 括号问题
- 问题: 括号未正确闭合
- 修复: 找到并修复未正确闭合的括号

### 3. 修复 `src/core_services/git_version_release_system.py` 语法错误
- 位置: 第121行
- 问题: 语法错误
- 修复: 修复第121行的语法错误

### 4. 修复 `tests/test_sskg_storage_adapters.py` 类定义问题
- 位置: 第180行
- 问题: `class`关键字后缺少类名
- 修复: 修复第180行的不完整类定义

## 导入错误修复任务

### 5. 创建或修复 `interactive_cli.py` 模块
- 问题: 无法导入 `interactive_cli`
- 修复:
  - 确认该模块是否存在，如果不存在则创建
  - 确保该模块包含 `main` 和 `start_personal_assistant` 函数

### 6. 检查 `src.core_services.knowledge_conflict_resolver.py`
- 问题: 无法导入 `ConflictDetectionResult`
- 修复:
  - 确认 `ConflictDetectionResult` 类是否存在
  - 如果不存在，创建该类或修复导入路径

### 7. 检查 `src.core_services/storage_adapters` 模块结构
- 问题: 无法导入 `memory_bank_adapter`
- 修复:
  - 确认 `memory_bank_adapter.py` 文件是否存在
  - 如果不存在，创建该文件或修复导入路径

### 8. 检查 `src.core_services.expert_consultation_scenario.py`
- 问题: 无法导入 `PriorityLevel`
- 修复:
  - 确认 `PriorityLevel` 类是否存在
  - 如果不存在，创建该类或修复导入路径

### 9. 检查 `src.core_services.multidimensional_assessment_engine.py`
- 问题: 无法导入 `MultidimensionalAssessmentEngine`
- 修复:
  - 确认 `MultidimensionalAssessmentEngine` 类是否存在
  - 如果不存在，创建该类或修复导入路径

### 10. 检查 `src.subagents.intelligent_synthesis` 模块结构
- 问题: 无法导入 `weight_optimizer`
- 修复:
  - 确认 `weight_optimizer.py` 文件是否存在
  - 如果不存在，创建该文件或修复导入路径

### 11. 检查 `src.virtual_role_chat.sskg` 模块结构
- 问题: 无法导入 `adapters`
- 修复:
  - 确认 `adapters.py` 文件是否存在
  - 如果不存在，创建该文件或修复导入路径

## 模块结构修复任务

### 12. 修复 `src/core_services/storage_adapters/__init__.py`
- 问题: 引用了不存在的 `memory_bank_adapter` 模块
- 修复: 移除或修正对不存在模块的引用

### 13. 修复 `src/subagents/intelligent_synthesis/__init__.py`
- 问题: 引用了不存在的 `weight_optimizer` 模块
- 修复: 移除或修正对不存在模块的引用

### 14. 修复 `src/virtual_role_chat/sskg/__init__.py`
- 问题: 引用了不存在的 `adapters` 模块
- 修复: 移除或修正对不存在模块的引用

## 验证和测试任务

### 15. 重新运行测试套件
- 任务: 运行 pytest 并检查错误是否已解决
- 调整: 根据需要进行进一步修复