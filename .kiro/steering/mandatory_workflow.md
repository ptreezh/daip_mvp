---
inclusion: always
priority: critical
---

# 强制工作流程规范

## 🚨 每次任务执行的强制流程

### 阶段1：任务接收和初始分析 (MANDATORY)

```python
def task_reception_phase(task_description: str):
    """任务接收阶段 - 强制执行"""
    
    # 1. 记录任务开始
    log_task_start(task_description)
    
    # 2. 强制执行组件扫描
    component_scan_results = mandatory_component_scan()
    
    # 3. 验证任务假设
    validate_task_assumptions(task_description, component_scan_results)
    
    # 4. 生成初始分析报告
    initial_analysis = generate_initial_analysis(component_scan_results)
    
    return initial_analysis
```

#### 1.1 强制组件扫描清单

**每次任务开始前必须执行：**

- [ ] 扫描 `src/core_services/` 目录，统计所有 `.py` 文件
- [ ] 搜索所有包含 `Service` 的类定义
- [ ] 验证任务中提到的每个组件是否实际存在
- [ ] 测试关键组件的导入可用性
- [ ] 记录所有发现的"意外"组件

#### 1.2 任务假设验证清单

**对任务描述中的每个假设进行验证：**

- [ ] 如果任务说"需要实现X"，验证X是否真的不存在
- [ ] 如果任务说"基于现有Y"，验证Y的实际完成状态
- [ ] 如果任务估算时间，验证估算是否基于准确的现状分析
- [ ] 记录所有与任务描述不符的发现

### 阶段2：深度分析和验证 (MANDATORY)

```python
def deep_analysis_phase(initial_findings: Dict):
    """深度分析阶段 - 强制执行"""
    
    # 1. 代码级别验证
    code_verification = verify_at_code_level(initial_findings)
    
    # 2. 功能测试验证
    functionality_tests = test_component_functionality(initial_findings)
    
    # 3. 集成点分析
    integration_analysis = analyze_integration_points(initial_findings)
    
    # 4. 交叉验证
    cross_validation = cross_validate_findings(
        code_verification, 
        functionality_tests, 
        integration_analysis
    )
    
    return cross_validation
```

#### 2.1 代码级别验证清单

- [ ] 阅读每个相关组件的源代码
- [ ] 验证类的方法签名和参数
- [ ] 检查依赖关系和导入语句
- [ ] 确认接口的实际实现程度

#### 2.2 功能测试验证清单

- [ ] 尝试导入每个关键组件
- [ ] 实例化主要类并测试基本方法
- [ ] 验证组件间的协作是否正常
- [ ] 测试错误处理和边界情况

### 阶段3：执行计划制定 (MANDATORY)

```python
def execution_planning_phase(verified_findings: Dict):
    """执行计划制定 - 基于验证后的发现"""
    
    # 1. 重新评估任务复杂度
    complexity_reassessment = reassess_task_complexity(verified_findings)
    
    # 2. 调整实施策略
    adjusted_strategy = adjust_implementation_strategy(complexity_reassessment)
    
    # 3. 更新时间估算
    updated_timeline = update_time_estimates(adjusted_strategy)
    
    # 4. 识别风险点
    risk_assessment = identify_execution_risks(adjusted_strategy)
    
    return ExecutionPlan(
        strategy=adjusted_strategy,
        timeline=updated_timeline,
        risks=risk_assessment
    )
```

#### 3.1 策略调整检查点

- [ ] 基于实际发现调整开发策略（构建 vs 集成 vs 优化）
- [ ] 重新评估所需的技能和工具
- [ ] 调整质量保证方法
- [ ] 更新交付物清单

### 阶段4：执行和持续验证 (MANDATORY)

```python
def execution_phase(execution_plan: ExecutionPlan):
    """执行阶段 - 持续验证"""
    
    for step in execution_plan.steps:
        # 1. 执行前验证
        pre_execution_check(step)
        
        # 2. 执行步骤
        result = execute_step(step)
        
        # 3. 执行后验证
        post_execution_verification(step, result)
        
        # 4. 更新状态
        update_execution_status(step, result)
```

#### 4.1 执行中检查点

- [ ] 每个步骤开始前验证前置条件
- [ ] 执行过程中监控是否偏离计划
- [ ] 每个步骤完成后验证输出质量
- [ ] 发现问题时立即停止并重新分析

### 阶段5：完成验证和交付 (MANDATORY)

```python
def completion_phase(execution_results: List[StepResult]):
    """完成验证阶段 - 强制质量门禁"""
    
    # 1. 功能完整性验证
    functionality_check = verify_functionality_completeness(execution_results)
    
    # 2. 集成测试
    integration_test = run_integration_tests(execution_results)
    
    # 3. 性能验证
    performance_check = verify_performance_requirements(execution_results)
    
    # 4. 文档更新验证
    documentation_check = verify_documentation_updates(execution_results)
    
    # 5. 最终质量门禁
    final_quality_gate = run_final_quality_checks([
        functionality_check,
        integration_test, 
        performance_check,
        documentation_check
    ])
    
    if not final_quality_gate.passed:
        raise TaskNotCompleteError("质量门禁未通过，任务未完成")
    
    return CompletionReport(final_quality_gate)
```

#### 5.1 完成验证清单

- [ ] 所有声称完成的功能都经过测试验证
- [ ] 集成测试100%通过
- [ ] 性能指标满足要求
- [ ] 文档与实际实现一致
- [ ] 没有已知的严重缺陷

## 🔧 工具化支持

### 自动化检查脚本

#### mandatory_pre_task_check.py

```python
#!/usr/bin/env python3
"""
强制任务前检查脚本
每次任务开始前必须运行
"""

import os
import sys
import subprocess
from pathlib import Path

def mandatory_component_scan():
    """强制组件扫描"""
    print("🔍 执行强制组件扫描...")
    
    # 1. 统计核心服务
    core_services_path = Path("src/core_services")
    if core_services_path.exists():
        py_files = list(core_services_path.glob("*.py"))
        print(f"📊 发现 {len(py_files)} 个核心服务文件")
    else:
        print("⚠️ src/core_services 目录不存在")
    
    # 2. 搜索Service类
    result = subprocess.run([
        "grep", "-r", "class.*Service", "--include=*.py", "."
    ], capture_output=True, text=True)
    
    service_classes = result.stdout.strip().split('\n') if result.stdout.strip() else []
    print(f"📊 发现 {len(service_classes)} 个Service类")
    
    # 3. 验证关键组件
    key_components = [
        "PersonalAssistantService",
        "IntentAnalysisService", 
        "RoleManager",
        "WorkflowEngine"
    ]
    
    for component in key_components:
        try:
            result = subprocess.run([
                "grep", "-r", component, "--include=*.py", "."
            ], capture_output=True, text=True)
            
            if result.stdout.strip():
                print(f"✅ {component} 存在")
            else:
                print(f"❌ {component} 未找到")
        except Exception as e:
            print(f"⚠️ 检查 {component} 时出错: {e}")
    
    return {
        "core_services_count": len(py_files) if 'py_files' in locals() else 0,
        "service_classes_count": len(service_classes),
        "key_components_status": "completed"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python mandatory_pre_task_check.py '任务描述'")
        sys.exit(1)
    
    task_description = sys.argv[1]
    print(f"📋 任务: {task_description}")
    
    scan_results = mandatory_component_scan()
    
    print("\n✅ 强制检查完成")
    print("⚠️ 请基于以上发现重新评估任务复杂度和实施策略")
```

### 质量门禁脚本

#### mandatory_quality_gate.py

```python
#!/usr/bin/env python3
"""
强制质量门禁检查
任务完成前必须通过
"""

def run_mandatory_quality_checks():
    """运行强制质量检查"""
    checks = [
        check_import_functionality,
        check_basic_functionality,
        check_integration_points,
        check_documentation_consistency
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
            print(f"✅ {check.__name__}: PASSED")
        except Exception as e:
            print(f"❌ {check.__name__}: FAILED - {e}")
            results.append(False)
    
    if all(results):
        print("\n🎉 所有质量门禁检查通过！")
        return True
    else:
        print("\n🚨 质量门禁检查失败，任务未完成！")
        return False

def check_import_functionality():
    """检查导入功能"""
    # 实现导入测试逻辑
    return True

def check_basic_functionality():
    """检查基本功能"""
    # 实现功能测试逻辑
    return True

def check_integration_points():
    """检查集成点"""
    # 实现集成测试逻辑
    return True

def check_documentation_consistency():
    """检查文档一致性"""
    # 实现文档验证逻辑
    return True

if __name__ == "__main__":
    success = run_mandatory_quality_checks()
    sys.exit(0 if success else 1)
```

## 🚨 违规处理

### 强制执行机制

**任何跳过强制流程的行为都将导致：**

1. **立即停止当前任务**
2. **重新执行完整流程**
3. **更新预防措施**
4. **记录违规原因**

### 违规类型和处理

#### A级违规（严重）

- 跳过组件扫描直接开始编码
- 基于文档推测而非代码验证
- 质量门禁未通过就声称完成

**处理**: 立即停止，从阶段1重新开始

#### B级违规（中等）

- 部分跳过验证步骤
- 验证不充分就进入下一阶段
- 发现问题但未及时调整策略

**处理**: 回退到上一阶段，补充验证

#### C级违规（轻微）

- 文档更新不及时
- 检查清单填写不完整
- 工具使用不规范

**处理**: 立即修正，继续执行

## 📊 效果监控

### 关键指标

- **分析准确率**: 后续验证中发现的错误率 < 5%
- **组件发现完整率**: 遗漏重要组件的比例 < 10%
- **时间估算准确率**: 实际时间与估算时间偏差 < 20%
- **质量门禁通过率**: 首次通过率 > 90%

### 持续改进

每次任务完成后：

1. 记录实际执行情况
2. 分析偏差原因
3. 更新工作流程
4. 完善检查工具

---

**这个工作流程是强制性的，不可跳过，不可简化！**
**质量和准确性比速度更重要！**
