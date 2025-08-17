# DAIP-LIVE 项目语法错误修复计划

## 问题文件分类

### 1. 语法错误类文件
- `tests/test_critical_review_nodes.py` - 行580: `lass TestConsensusNode:` (应为 `class`)
- `frontend/components/forum_chat_interface.py` - 括号未正确闭合
- `src/core_services/git_version_release_system.py` - 行121: 语法错误
- `tests/test_sskg_storage_adapters.py` - 行180: `class`关键字后缺少类名

### 2. 导入错误类文件
- `tests/test_cli_framework.py` - 无法导入 `interactive_cli`
- `tests/test_personal_assistant_main.py` - 无法导入 `interactive_cli`
- `tests/test_knowledge_conflict_resolver.py` - 无法从 `src.core_services.knowledge_conflict_resolver` 导入 `ConflictDetectionResult`
- `tests/test_storage_adapters.py` - 无法导入 `src.core_services.storage_adapters.memory_bank_adapter`
- `tests/test_user_stories.py` - 无法从 `src.core_services.expert_consultation_scenario` 导入 `PriorityLevel`
- `tests/test_v0_3_5_critical_review.py` - 无法从 `src.core_services.multidimensional_assessment_engine` 导入 `MultidimensionalAssessmentEngine`
- `tests/test_v0_3_7_performance_monitoring.py` - 无法导入 `src.subagents.intelligent_synthesis.weight_optimizer`
- `tests/v0_3_4_integration_test.py` - 无法导入 `src.virtual_role_chat.sskg.adapters`
- `tests/v0_3_6_integration_test.py` - 无法导入 `src.subagents.intelligent_synthesis.weight_optimizer`

### 3. 模块结构问题
- `src/core_services/storage_adapters/__init__.py` - 引用了不存在的 `memory_bank_adapter` 模块
- `src/subagents/intelligent_synthesis/__init__.py` - 引用了不存在的 `weight_optimizer` 模块
- `src/virtual_role_chat/sskg/__init__.py` - 引用了不存在的 `adapters` 模块

## 系统修复计划

### 第一阶段：修复语法错误 (预计2-3小时)
1. 修复 `tests/test_critical_review_nodes.py` 中的拼写错误
2. 修复 `frontend/components/forum_chat_interface.py` 中的括号问题
3. 修复 `src/core_services/git_version_release_system.py` 中的语法错误
4. 修复 `tests/test_sskg_storage_adapters.py` 中的类定义问题

### 第二阶段：解决导入错误 (预计3-4小时)
1. 创建或修复 `interactive_cli.py` 模块
2. 检查并修复 `src.core_services.knowledge_conflict_resolver.py` 中的 `ConflictDetectionResult` 类
3. 检查并修复 `src.core_services.storage_adapters` 模块结构
4. 检查并修复 `src.core_services.expert_consultation_scenario.py` 中的 `PriorityLevel` 类
5. 检查并修复 `src.core_services.multidimensional_assessment_engine.py` 中的 `MultidimensionalAssessmentEngine` 类
6. 检查并修复 `src.subagents.intelligent_synthesis` 模块结构
7. 检查并修复 `src.virtual_role_chat.sskg` 模块结构

### 第三阶段：重构模块结构 (预计1-2小时)
1. 修复 `src/core_services/storage_adapters/__init__.py`
2. 修复 `src/subagents/intelligent_synthesis/__init__.py`
3. 修复 `src/virtual_role_chat/sskg/__init__.py`

### 第四阶段：验证和测试 (预计1小时)
1. 重新运行测试套件，验证修复结果
2. 根据测试结果进行必要的调整