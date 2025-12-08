# 个人版最小化权限策略规范（对齐 REQUIREMENTS_SPECIFICATION）

目标
- 在个人用户版本内提供最低成本、最高安全的操作防护，仅覆盖高风险能力；默认安全、可追溯、可配置
- 对齐文档：REQUIREMENTS_SPECIFICATION.md 第4.4节“安全性需求”（工具权限控制）

范围（YAGNI）
- 覆盖对象：高风险操作
  - 文件写入/删除/移动（包括生成器、脚手架写文件）
  - 执行外部命令（bash/shell 等）
- 非覆盖：纯读操作、纯内存计算、只读检索

策略模型（KISS）
- 三元策略：Allow / Deny / Ask（默认 Ask）
- 通配支持：按工具名与参数模式（如：
  - allow: ["ls", "git status", "write:wiki/*"]
  - deny:  ["rm *", "mv /*", "curl file://*"]
  - 其他全部 Ask）
- 优先级：显式条目 > 通配 > 默认值（Ask）

配置（config.yaml 新增）
permissions:
  default: "ask"
  rules:
    - match: "write:*"
      action: "ask"
    - match: "bash:git status"
      action: "allow"
    - match: "bash:rm *"
      action: "deny"

交互流程（TUI）
- Ask 时弹窗显示：工具名、参数摘要、影响范围
- 用户选择 Allow/Deny 一次性生效；会话期内可选择“记住本规则”（只在本会话）
- 记录审计日志：时间、规则命中、用户选择、目标

审计与可追溯
- 本地日志文件 logs/permissions.log（UTF-8），不含敏感内容
- 可配置最大大小与滚动

失败降级
- 当未能渲染弹窗时（无UI上下文），自动降级为 Deny 并提示用户重试

边界与安全
- 对文件路径进行归一化与沙箱校验，仅允许在允许的工作区目录下写入（项目根、wiki、roles、workflows 等）
- 对外部命令提供白名单，禁止交互式与危险参数（例如不允许 "rm -rf" 类）

TDD 要点
- 单测：规则解析与优先级；通配匹配；默认 Ask；日志记录
- 集成：TUI 弹窗回路；会话级“记住”规则；沙箱路径校验
- 端到端：对写文件与外部命令触发 Ask，用户确认后成功；未确认则拒绝

完成标准
- 默认配置下，任一高风险操作均需用户一次确认
- 可通过配置将已知安全操作置为 Allow；危害操作为 Deny
- log、沙箱、降级路径可用
