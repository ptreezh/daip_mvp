# 基于角色的Wiki协作系统 - 设计文档

## 1. 引言
### 1.1 目的
本文档描述了基于角色的Wiki协作系统的架构设计和实现方案，以指导开发工作。

### 1.2 范围
本文档涵盖了系统的核心组件设计、接口定义、数据模型和工作流程。

## 2. 系统架构

### 2.1 总体架构图
```
+------------------+     +-------------------+     +------------------+
|   AI 角色        |     |  Wiki协作引擎     |     |   用户界面       |
|  (创建提案)      |<--->|  (评审&决策)      |<--->|  (查看&干预)     |
+------------------+     +-------------------+     +------------------+
                              |     ^
                              v     |
                        +------------------+
                        |  WikiService     |
                        |  (内容管理)      |
                        +------------------+
```

### 2.2 核心组件

#### 2.2.1 Wiki协作引擎 (WikiCollaborationEngine)
系统的核心协调组件，负责：
- 提案生命周期管理
- 角色分配和任务调度
- 决策规则执行
- 与WikiService交互

#### 2.2.2 角色接口层 (RoleInterface)
为AI角色提供API接口：
- 提案创建接口
- 评审任务获取接口
- 评审意见提交接口

#### 2.2.3 用户接口层 (UserInterface)
为用户提供CLI命令：
- 提案查看命令
- 手动审批命令
- 状态监控命令

#### 2.2.4 WikiService适配器 (WikiServiceAdapter)
与现有WikiService集成：
- 封装现有的approve/reject方法
- 提供增强的查询接口

## 3. 数据模型

### 3.1 提案 (Proposal)
```python
class Proposal:
    id: str  # 提案唯一标识
    entry_name: str  # 相关的wiki条目
    author_role: str  # 创建者角色
    content: str  # 提案内容
    change_summary: str  # 变更摘要
    status: ProposalStatus  # 状态 (proposed, reviewed, approved, rejected)
    created_at: datetime  # 创建时间
    reviewers: List[str]  # 分配的评审角色
    reviews: List[Review]  # 评审记录
    decision: Decision  # 最终决策
```

### 3.2 评审 (Review)
```python
class Review:
    id: str  # 评审记录ID
    proposal_id: str  # 关联的提案ID
    reviewer_role: str  # 评审角色
    opinion: ReviewOpinion  # 评审意见 (approve, reject, request_changes)
    comments: str  # 评审注释
    submitted_at: datetime  # 提交时间
```

### 3.3 决策 (Decision)
```python
class Decision:
    id: str  # 决策记录ID
    proposal_id: str  # 关联的提案ID
    decision_type: DecisionType  # 决策类型 (auto, manual)
    result: DecisionResult  # 决策结果 (approved, rejected)
    reason: str  # 决策理由
    decided_by: str  # 决策者 (角色名或"user")
    decided_at: datetime  # 决策时间
```

## 4. 工作流程

### 4.1 提案创建流程
1. AI角色调用`create_proposal`接口
2. Wiki协作引擎创建Proposal对象并持久化
3. 系统分析提案内容，识别相关领域
4. 根据角色专业领域分配评审任务
5. 通知相关评审角色

### 4.2 评审流程
1. 评审角色调用`get_assigned_reviews`获取任务
2. 角色调用`submit_review`提交评审意见
3. Wiki协作引擎记录评审意见
4. 检查是否所有评审已完成

### 4.3 决策流程
1. 当所有评审完成后，触发决策引擎
2. 根据配置的决策规则评估评审意见
3. 生成Decision记录
4. 如果结果是approved，调用WikiService执行更新
5. 通知相关人员决策结果

### 4.4 自动执行流程
1. 决策引擎调用WikiServiceAdapter
2. WikiServiceAdapter调用WikiService的approve方法
3. 记录执行结果
4. 更新Proposal状态

## 5. 接口设计

### 5.1 角色API接口

#### create_proposal
```
POST /api/wiki/proposals
请求体:
{
  "entry_name": "条目名称",
  "content": "新内容",
  "change_summary": "变更摘要",
  "author_role": "创建角色"
}

响应:
{
  "proposal_id": "提案ID",
  "status": "created"
}
```

#### get_assigned_reviews
```
GET /api/wiki/reviews?role={role_name}
响应:
[
  {
    "proposal_id": "提案ID",
    "entry_name": "条目名称",
    "content": "提案内容",
    "change_summary": "变更摘要",
    "author_role": "创建角色",
    "created_at": "创建时间"
  }
]
```

#### submit_review
```
POST /api/wiki/reviews
请求体:
{
  "proposal_id": "提案ID",
  "reviewer_role": "评审角色",
  "opinion": "approve|reject|request_changes",
  "comments": "评审注释"
}

响应:
{
  "review_id": "评审ID",
  "status": "submitted"
}
```

### 5.2 用户CLI增强命令

#### wiki proposal list (增强版)
```
wiki proposal list [--status STATUS] [--role ROLE] [--entry ENTRY]
```

#### wiki proposal view
```
wiki proposal view <proposal_id>
```

## 6. 决策规则引擎

### 6.1 规则配置
```yaml
decision_rules:
  - name: "simple_majority"
    description: "简单多数同意则批准"
    condition: "approved_reviews > total_reviews / 2"
    
  - name: "unanimous"
    description: "全体同意才批准"
    condition: "approved_reviews == total_reviews"
    
  - name: "expert_override"
    description: "领域专家一票否决"
    condition: "any_rejected_by_expert AND expert_opinion == 'reject'"
```

### 6.2 规则执行
决策引擎将按顺序评估规则，第一个匹配的规则将决定最终结果。

## 7. 集成考虑

### 7.1 与现有WikiService集成
- 重用现有的`approve`和`reject`方法
- 扩展`list_pending_proposals`以支持更多查询参数
- 添加新的查询方法以获取提案详情

### 7.2 与角色管理系统集成
- 获取角色的专业领域信息
- 通知角色新的评审任务
- 获取角色的权限信息

### 7.3 与通知系统集成
- 向用户发送重要提案通知
- 向角色发送评审任务通知
- 发送决策结果通知