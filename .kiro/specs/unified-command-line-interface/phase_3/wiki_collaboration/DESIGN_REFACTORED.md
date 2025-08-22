# 基于角色的Wiki协作系统 - 重构后设计文档

## 1. 引言
### 1.1 目的
本文档描述了基于角色的Wiki协作系统的架构设计和实现方案，以指导开发工作。

### 1.2 范围
本文档涵盖了系统的核心组件设计、接口定义、数据模型和工作流程。

## 2. 系统架构

### 2.1 总体架构图
```
+------------------+     +-------------------+     +------------------+
|   系统用户       |     | Wiki协作协调器    |     |   AI 角色        |
|  (发起任务)      |<--->|  (指派&协调)      |<--->|  (参与协作)      |
+------------------+     +-------------------+     +------------------+
                              |     ^
                              v     |
                        +------------------+
                        |  WikiService     |
                        |  (内容管理)      |
                        +------------------+
```

### 2.2 核心组件

#### 2.2.1 Wiki协作协调器 (WikiCollaborationCoordinator)
系统的核心协调组件，负责：
- 协作任务生命周期管理
- 角色指派和任务调度
- 协作过程协调
- 与WikiService交互

#### 2.2.2 用户接口层 (UserInterface)
为用户提供CLI命令：
- 任务发起命令
- 任务状态查看命令
- 结果确认命令

#### 2.2.3 角色协作接口层 (RoleCollaborationInterface)
为AI角色提供协作接口：
- 任务信息接收接口
- 反馈提交接口
- 状态查询接口

#### 2.2.4 WikiService适配器 (WikiServiceAdapter)
与现有WikiService集成：
- 封装现有的内容管理方法
- 提供协作任务执行接口

## 3. 数据模型

### 3.1 协作任务 (CollaborationTask)
```python
class CollaborationTask:
    id: str  # 任务唯一标识
    entry_name: str  # 相关的wiki条目
    task_type: TaskType  # 任务类型 (create, edit, review)
    status: TaskStatus  # 状态 (pending, in_progress, completed, rejected)
    created_at: datetime  # 创建时间
    initiated_by: str  # 发起者
    assigned_roles: List[RoleAssignment]  # 指派的角色
    feedbacks: List[RoleFeedback]  # 角色反馈
    result: CollaborationResult  # 协作结果
    completed_at: datetime  # 完成时间
```

### 3.2 角色指派 (RoleAssignment)
```python
class RoleAssignment:
    id: str  # 指派记录ID
    task_id: str  # 关联的任务ID
    role_name: str  # 角色名
    assigned_at: datetime  # 指派时间
    status: AssignmentStatus  # 状态 (assigned, feedback_submitted, timeout)
```

### 3.3 角色反馈 (RoleFeedback)
```python
class RoleFeedback:
    id: str  # 反馈记录ID
    task_id: str  # 关联的任务ID
    role_name: str  # 反馈角色
    content: str  # 反馈内容
    submitted_at: datetime  # 提交时间
```

### 3.4 协作结果 (CollaborationResult)
```python
class CollaborationResult:
    id: str  # 结果记录ID
    task_id: str  # 关联的任务ID
    suggested_content: str  # 建议的内容
    summary: str  # 协作摘要
    generated_at: datetime  # 生成时间
    approved_by: str  # 确认者 ("user" 或 None)
    approved_at: datetime  # 确认时间
```

## 4. 工作流程

### 4.1 任务发起流程
1. 用户调用`wiki collaborate start`命令
2. Wiki协作协调器创建CollaborationTask对象并持久化
3. 系统分析任务内容，识别相关领域
4. 根据角色专业领域指派参与角色
5. 通知相关角色任务信息

### 4.2 角色参与流程
1. 被指派角色接收任务通知
2. 角色分析任务内容，形成反馈意见
3. 角色调用接口提交反馈
4. Wiki协作协调器记录反馈意见

### 4.3 协作协调流程
1. Wiki协作协调器监控任务进度
2. 当所有角色提交反馈或超时时，汇总反馈意见
3. 生成协作结果和建议方案
4. 更新任务状态为待确认

### 4.4 用户确认流程
1. 用户调用`wiki collaborate view`查看任务详情
2. 用户决定批准或拒绝建议方案
3. 如果批准，调用WikiService执行更新
4. 如果拒绝，任务标记为已拒绝

### 4.5 自动执行流程
1. 用户批准后，协调器调用WikiServiceAdapter
2. WikiServiceAdapter调用WikiService执行内容更新
3. 记录执行结果
4. 更新任务状态为已完成

## 5. 接口设计

### 5.1 用户CLI命令

#### wiki collaborate start
```
wiki collaborate start <entry_name> [--type TYPE] [--content CONTENT]
参数:
  entry_name: 目标wiki条目
  type: 任务类型 (create, edit, review)
  content: 初始内容（仅创建任务需要）
```

#### wiki collaborate status
```
wiki collaborate status <task_id>
参数:
  task_id: 任务ID
```

#### wiki collaborate view
```
wiki collaborate view <task_id>
参数:
  task_id: 任务ID
```

#### wiki collaborate approve
```
wiki collaborate approve <task_id>
参数:
  task_id: 任务ID
```

#### wiki collaborate reject
```
wiki collaborate reject <task_id>
参数:
  task_id: 任务ID
```

### 5.2 角色内部接口

#### receive_task
```
receive_task(task_info: dict)
参数:
  task_info: 包含任务信息的字典
```

#### submit_feedback
```
submit_feedback(task_id: str, feedback: str)
参数:
  task_id: 任务ID
  feedback: 反馈内容
```

#### get_task_status
```
get_task_status(task_id: str) -> TaskStatus
参数:
  task_id: 任务ID
返回:
  任务状态
```

## 6. 角色指派策略

### 6.1 领域匹配算法
```python
def assign_roles(task_content: str, task_type: TaskType) -> List[str]:
    # 1. 提取任务内容中的关键词
    keywords = extract_keywords(task_content)
    
    # 2. 分析关键词对应的领域
    domains = analyze_domains(keywords)
    
    # 3. 匹配领域专家角色
    expert_roles = find_expert_roles(domains)
    
    # 4. 根据任务类型调整角色数量
    if task_type == TaskType.CREATE:
        return expert_roles[:3]  # 创建任务指派3个角色
    elif task_type == TaskType.EDIT:
        return expert_roles[:2]  # 编辑任务指派2个角色
    else:  # REVIEW
        return expert_roles[:1]  # 评审任务指派1个角色
```

### 6.2 备用角色机制
```python
def get_backup_roles(primary_roles: List[str]) -> List[str]:
    # 获取未被指派的通用领域角色作为备用
    all_roles = get_all_roles()
    backup_roles = [r for r in all_roles if r not in primary_roles]
    return backup_roles[:2]  # 最多2个备用角色
```

## 7. 集成考虑

### 7.1 与现有WikiService集成
- 重用现有的内容管理方法
- 扩展接口以支持协作任务执行
- 保持数据格式兼容性

### 7.2 与角色管理系统集成
- 获取角色的专业领域信息
- 通知角色新的协作任务
- 获取角色的可用性状态

### 7.3 与通知系统集成
- 向用户发送任务状态变更通知
- 向角色发送任务指派通知
- 发送协作结果通知