# 简化版Wiki协作系统 - 系统设计

## 1. 引言
### 1.1 目的
本文档描述了简化版Wiki协作系统的架构设计，严格遵循KISS、YAGNI和SOLID原则。

### 1.2 范围
本文档涵盖系统的核心组件设计、接口定义和简化的工作流程。

## 2. 系统架构

### 2.1 总体架构图
```
+------------------+     +-------------------+     +------------------+
|   系统用户       |     |   智能助手        |     |   AI 角色        |
|  (表达意图)      |---->|  (优化&协调)      |---->|  (专业反馈)      |
+------------------+     +-------------------+     +------------------+
                              |     ^
                              v     |
                        +------------------+
                        |  WikiService     |
                        |  (内容更新)      |
                        +------------------+
```

### 2.2 核心组件（严格遵循单一职责原则）

#### 2.2.1 意图优化器 (IntentOptimizer)
**职责**：优化用户表达的意图
- 接收用户自然语言输入
- 识别意图类型和目标条目
- 生成清晰的任务描述

#### 2.2.2 任务协调器 (TaskCoordinator)
**职责**：协调整个协作任务流程
- 发起协作任务
- 调用角色协调器获取反馈
- 调用执行器执行更新
- 发送状态通知

#### 2.2.3 角色协调器 (RoleCoordinator)
**职责**：管理角色参与
- 根据任务内容指派角色
- 收集角色反馈
- 汇总反馈意见

#### 2.2.4 执行器 (Executor)
**职责**：执行最终的知识更新
- 基于反馈生成更新内容
- 调用WikiService执行更新
- 记录执行历史

## 3. 数据模型（简化设计）

### 3.1 简化任务 (SimpleTask)
```python
class SimpleTask:
    id: str  # 任务ID
    user_input: str  # 用户原始输入
    optimized_intent: str  # 优化后的意图
    target_entry: str  # 目标条目
    task_type: str  # 任务类型 (create/update/enhance)
    status: str  # 状态 (pending/processing/completed/failed)
    created_at: datetime  # 创建时间
    completed_at: datetime  # 完成时间
```

### 3.2 角色反馈 (RoleFeedback)
```python
class RoleFeedback:
    task_id: str  # 关联任务ID
    role_name: str  # 角色名
    feedback: str  # 反馈内容
    submitted_at: datetime  # 提交时间
```

### 3.3 执行记录 (ExecutionRecord)
```python
class ExecutionRecord:
    task_id: str  # 关联任务ID
    old_content: str  # 更新前内容
    new_content: str  -  # 更新后内容
    executed_at: datetime  # 执行时间
    success: bool  # 是否成功
```

## 4. 工作流程（极度简化）

### 4.1 完整流程
1. **用户输入**：用户通过CLI输入`wiki update "更新需求"`
2. **意图优化**：智能助手优化用户意图
3. **任务发起**：自动创建SimpleTask
4. **角色指派**：根据任务内容指派相关角色
5. **反馈收集**：收集所有角色的反馈
6. **内容生成**：基于反馈生成更新内容
7. **执行更新**：调用WikiService执行更新
8. **状态通知**：通知用户任务完成

### 4.2 每个步骤的详细说明

#### 步骤1-2: 用户输入与意图优化
```
用户: wiki update "机器学习词条需要更新最新的大模型进展"
意图优化器:
  - 识别目标条目: "机器学习"
  - 识别任务类型: update
  - 优化意图: "更新机器学习词条，添加大语言模型的最新进展"
```

#### 步骤3-4: 任务发起与角色指派
```
任务协调器:
  - 创建SimpleTask对象
  - 调用角色协调器指派角色
角色协调器:
  - 分析任务内容关键词: ["机器学习", "大语言模型"]
  - 指派角色: ["AI研究员", "NLP专家"]
```

#### 步骤5-6: 反馈收集与内容生成
```
角色协调器:
  - 收集"AI研究员"反馈: "建议添加Transformer架构的演进..."
  - 收集"NLP专家"反馈: "需要补充BERT、GPT等模型的比较..."
执行器:
  - 汇总反馈生成更新内容
```

#### 步骤7-8: 执行更新与状态通知
```
执行器:
  - 调用WikiService.update_entry()执行更新
  - 记录ExecutionRecord
任务协调器:
  - 发送完成通知给用户
```

## 5. 接口设计（遵循接口隔离原则）

### 5.1 核心接口

#### IntentOptimizer接口
```python
class IntentOptimizer:
    def optimize(self, user_input: str) -> dict:
        """
        优化用户意图
        返回: {
            "target_entry": "目标条目",
            "task_type": "任务类型",
            "optimized_intent": "优化后的意图描述"
        }
        """
        pass
```

#### TaskCoordinator接口
```python
class TaskCoordinator:
    def initiate_task(self, user_input: str) -> str:
        """
        发起协作任务
        返回: 任务ID
        """
        pass
        
    def get_task_status(self, task_id: str) -> dict:
        """
        获取任务状态
        """
        pass
```

#### RoleCoordinator接口
```python
class RoleCoordinator:
    def assign_and_collect(self, task: SimpleTask) -> List[RoleFeedback]:
        """
        指派角色并收集反馈
        返回: 角色反馈列表
        """
        pass
```

#### Executor接口
```python
class Executor:
    def execute(self, task: SimpleTask, feedbacks: List[RoleFeedback]) -> bool:
        """
        执行任务
        返回: 是否成功
        """
        pass
```

## 6. SOLID原则应用详解

### 6.1 单一职责原则 (SRP)
- 每个组件只有一个改变的理由
- IntentOptimizer只负责意图优化
- TaskCoordinator只负责任务协调
- RoleCoordinator只负责角色管理
- Executor只负责执行更新

### 6.2 开闭原则 (OCP)
- 对扩展开放：可以通过添加新的角色类型来扩展系统
- 对修改关闭：现有组件不需要因为新角色的添加而修改

### 6.3 里氏替换原则 (LSP)
- 所有组件都可以通过其接口被替换
- 例如，可以有不同实现的IntentOptimizer

### 6.4 接口隔离原则 (ISP)
- 每个组件只依赖于它需要的接口
- 用户不依赖于角色协调的复杂接口
- 角色不依赖于意图优化的内部逻辑

### 6.5 依赖倒置原则 (DIP)
- 高层模块(TaskCoordinator)依赖于抽象接口
- 低层模块(IntentOptimizer等)实现抽象接口
- 通过依赖注入实现组件解耦

## 7. KISS原则应用
- 架构简单：4个核心组件
- 流程简单：8个明确步骤
- 接口简单：每个组件接口不超过3个方法
- 数据模型简单：只保留核心字段

## 8. YAGNI原则应用
- 不实现角色间讨论机制
- 不实现复杂的争议解决
- 不实现多轮反馈
- 不实现复杂的权限管理
- 只实现当前必需的功能