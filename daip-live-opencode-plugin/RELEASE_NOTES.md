# debatewiki opencode plugin - 发布说明

## 版本信息
- **包名**: debatewiki
- **版本**: 1.0.0
- **发布日期**: 2026年1月12日

## 发布内容

debatewiki opencode plugin 是一个多智能体论坛辩论、维基协作和知识综合系统，设计为 OpenCode Agent Extension。它实现了混合 TypeScript/JavaScript + Go 架构，遵循 Sisyphus Orchestrator 模式。

### 核心功能

1. **论坛引擎 (ForumEngine)**
   - 协调专门智能体进行结构化讨论
   - 十种讨论流程类型：
     1. 自由辩论 (Free Debate)
     2. 对抗辩论 (Adversarial Debate) 
     3. 小组讨论 (Group Discussion)
     4. 苏格拉底辩论 (Socratic Debate)
     5. 限时辩论 (Time-Limited Debate)
     6. 共识驱动辩论 (Consensus-Driven Debate)
     7. 角色扮演辩论 (Role-Playing Debate)
     8. 动态加权辩论 (Dynamic Weighted Debate)
     9. 多轮淘汰辩论 (Multi-Round Elimination)
     10. 专家评审辩论 (Expert Review Debate)

2. **共识算法 (Consensus Algorithms)**
   - 投票共识 (Voting Consensus)
   - 审议共识 (Deliberation Consensus)
   - 加权共识 (Weighted Consensus)

3. **维基协作 (Wiki Collaboration)**
   - 同步和异步多智能体编辑
   - 版本控制和冲突解决
   - 多智能体审查工作流

4. **扎根理论引擎 (Grounded Theory Engine)**
   - 开放编码 (Open Coding)
   - 主轴编码 (Axial Coding)
   - 选择编码 (Selective Coding)
   - 饱和度检验 (Saturation Testing)
   - 多专家协同编码 (Multi-Expert Coding)

## 安装说明

### 使用 npm 安装
```bash
npm install -g debatewiki
```

### 配置 OpenCode
编辑 `~/.config/opencode/opencode.json` 文件：
```json
{
  "plugin": [
    "oh-my-opencode",
    "debatewiki"
  ],
  "$schema": "https://opencode.ai/config.json"
}
```

## 使用说明

### 启动辩论
```
/start-free-debate topic="AI伦理" participants=proponent,opponent,moderator
/start-adversarial-debate topic="气候变化政策" rounds=6
/start-group-discussion topic="股票市场分析" agents=insight,media,query,moderator
```

### 计算共识
```
/consensus-voting threshold=0.7
/consensus-deliberation max_rounds=10
/consensus-weighted weights="insight:0.8,media:0.6,query:0.7"
```

### 维基协作
```
/wiki-create title="AI研究" content="..."
/wiki-collaborate page_id="..." roles="researcher,reviewer,synthesizer"
/wiki-review page_id="..."
```

### 扎根理论研究
```
/gt-create-project name="用户满意度研究" description="研究用户满意度影响因素"
/gt-open-coding project_id="..." document_id="..." document_content="..."
/gt-axial-coding project_id="..." category="user_satisfaction" codes=["code1", "code2"]
/gt-selective-coding project_id="..." core_category="user_satisfaction" story_line="..."
/gt-saturation-test project_id="..." new_document_content="..."
```

## 技术亮点

1. **纯Go实现**: 使用纯Go SQLite实现 (github.com/glebarez/go-sqlite)，无需CGO
2. **多专家协同**: 支持多专家协同编码和共识达成
3. **模块化架构**: 清晰的模块划分，便于扩展和维护
4. **类型安全**: 完整的TypeScript类型定义
5. **测试覆盖**: 全面的单元和集成测试

## 交付准备状态

### ✅ 已完成
- 代码语法和类型错误修复
- 构建系统配置
- 单元和集成测试 (TypeScript)
- 端到端功能验证
- multi-expert-engine.ts 业务逻辑实现
- Go单元测试 (使用纯Go SQLite实现)
- 性能和安全测试框架
- 集成测试框架
- 包配置用于npm分发
- 内存存储实现用于CGO-free测试
- 插件接口抽象用于多存储后端
- npm包已成功发布

### 📋 发布后需完成
- OpenCode 集成测试 (在真实环境中)
- 性能和安全测试执行
- 完整API文档

## 贡献

欢迎贡献！请阅读 CONTRIBUTING.md 了解贡献指南。

## 许可证

MIT 许可证 - 详见 LICENSE 文件
