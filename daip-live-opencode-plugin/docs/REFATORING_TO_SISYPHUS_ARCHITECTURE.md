# debatewiki opencode plugin - 基于Sisyphus编排机制的重构方案

## 当前问题

当前实现使用了类构造函数，但OpenCode的插件加载机制在某些情况下可能直接调用构造函数而没有使用`new`关键字，导致错误：
```
TypeError: Cannot call a class constructor without |new|
```

## Sisyphus编排机制参考

根据oh-my-opencode架构，Sisyphus编排机制基于：
1. 智能体（Agents）- 专门处理特定任务
2. 工具（Tools）- 执行具体操作
3. Hook - 事件驱动的处理机制
4. 任务委托 - 将任务分配给专门的智能体

## 重构方案

### 1. 将类方法转换为函数

将当前的类实现转换为基于智能体和工具的函数式实现：

#### 当前实现（基于类）
```typescript
const engine = new ForumEngine();
const result = engine.executePhase(sessionId);
```

#### 重构后实现（基于Sisyphus编排）
```typescript
// 使用sisyphus_task委托给专门的智能体
const result = await sisyphus_task({
  agent: "forum-engine",
  prompt: `Execute phase for session: ${sessionId}`,
  skills: ["forum-operations"],
  run_in_background: false
});
```

### 2. 创建专门的智能体

为每种功能创建专门的智能体，而不是使用类：

```
agents/
├── forum-engine.ts          # 论坛引擎智能体
├── consensus-engine.ts      # 共识引擎智能体  
├── wiki-engine.ts           # 维基引擎智能体
├── grounded-theory-engine.ts # 扎根理论引擎智能体
└── multi-expert-engine.ts   # 多专家协同智能体
```

### 3. 实现基于工具的功能

将核心功能实现为工具，通过sisyphus_task调用：

```
tools/
├── forum-tools.ts           # 论坛相关工具
├── consensus-tools.ts       # 共识相关工具
├── wiki-tools.ts            # 维基相关工具
├── grounded-theory-tools.ts # 扎根理论相关工具
└── multi-expert-tools.ts    # 多专家协同工具
```

### 4. 使用Hook机制处理事件

实现事件驱动的处理机制，而不是在类中直接处理：

```
hooks/
├── forum-hooks.ts           # 论坛事件处理
├── consensus-hooks.ts       # 共识事件处理
├── wiki-hooks.ts            # 维基事件处理
└── theory-hooks.ts          # 理论构建事件处理
```

## 具体重构步骤

### 步骤1: 创建智能体定义

创建forum-engine智能体：
```typescript
// agents/forum-engine.ts
import { sisyphus_task } from '../utils/sisyphus';

/**
 * ForumEngine Agent
 * 
 * Coordinates specialized agents for structured discussions
 * Implements Sisyphus orchestration pattern for multi-agent collaboration
 * 
 * Skills:
 * - Multi-agent orchestration
 * - Discussion flow management
 * - Session management
 * - Message aggregation
 * - Todo tracking
 */
export async function runForumEngineTask(prompt: string, options: any = {}) {
  return await sisyphus_task({
    agent: "forum-engine",
    prompt,
    skills: ["forum-operations", "session-management", "message-aggregation"],
    run_in_background: options.background || false
  });
}
```

### 步骤2: 创建工具实现

创建论坛工具：
```typescript
// tools/forum-tools.ts
import { Tool } from '@opencode-ai/plugin';

export class StartDebateTool implements Tool {
  name = "start_debate";
  description = "Starts a multi-agent debate session";
  
  async execute(params: any) {
    // 委托给专门的智能体而不是直接实例化类
    return await sisyphus_task({
      agent: "forum-engine",
      prompt: `Start debate on topic: ${params.topic} with participants: ${params.participants.join(", ")}`,
      skills: ["forum-operations"],
      run_in_background: false
    });
  }
}
```

### 步骤3: 实现事件驱动的Hook

创建论坛Hook：
```typescript
// hooks/forum-hooks.ts
import { runForumEngineTask } from '../agents/forum-engine';

export function onUserPromptSubmit(prompt: string) {
  // 检测是否是论坛相关命令
  if (prompt.startsWith('/start-')) {
    return runForumEngineTask(prompt);
  }
}
```

## 优势

1. **与OpenCode架构一致**：使用Sisyphus编排机制，符合oh-my-opencode模式
2. **避免构造函数问题**：不再直接使用类构造函数，消除"Cannot call a class constructor without |new|"错误
3. **更好的可扩展性**：智能体和工具模式更容易扩展和维护
4. **更自然的AI交互**：智能体可以更好地理解和执行任务
5. **事件驱动**：Hook机制提供更好的事件处理能力

## 实施计划

1. **第一阶段**：创建智能体定义文件
2. **第二阶段**：实现工具层
3. **第三阶段**：实现Hook机制
4. **第四阶段**：迁移现有功能到新架构
5. **第五阶段**：测试和验证

## 与现有功能的映射

| 当前类实现 | 新智能体/工具实现 |
|------------|------------------|
| ForumEngine | forum-engine智能体 + forum-tools |
| VotingConsensus | consensus-engine智能体 + consensus-tools |
| WikiEngine | wiki-engine智能体 + wiki-tools |
| GroundedTheoryEngine | grounded-theory-engine智能体 + theory-tools |
| MultiExpertCodingEngine | multi-expert-engine智能体 + multi-expert-tools |

这种重构将使debatewiki插件完全符合Sisyphus编排机制，与oh-my-opencode架构保持一致，同时解决构造函数调用问题。