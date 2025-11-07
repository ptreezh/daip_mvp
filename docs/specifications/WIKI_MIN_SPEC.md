# 内置 Wiki 最小化规范（对齐 REQUIREMENTS 与 知识管理）

目标
- 提供本地 Markdown 为核心的个人知识库（Wiki），与现有知识检索一致集成
- 简单命令、零学习成本、与知识同步一致编码与索引

目录与编码
- 根目录：./wiki（UTF-8）
- 文件：.md；可选 YAML front-matter（title, tags）
- 链接：支持 [[Page Title]] 与相对路径链接；渲染端按需

命令（TUI/CLI）
- /wiki new <title>：创建 md 文件（去空格转下划线），带模板头
- /wiki list：列出最近编辑/创建的条目（按 mtime）
- /wiki open <title|path>：在系统默认编辑器中打开
- /wiki search <query>：直连 KnowledgeManager 语义检索并回显路径

索引与检索
- 同步入口：复用 /knowledge sync；knowledge_base.directory 增加 wiki 目录
- 哈希与去重策略与现有一致；遇到 front-matter 优先用 title 参与索引元数据

安全与权限
- 写文件走权限策略（Ask/Allow/Deny）
- 限制写入路径在 ./wiki 下

TDD 要点
- new/list/open/search 的命令测试（文件生成、列表顺序、打开失败降级提示、检索匹配）
- 索引集成测试：在 wiki 写入后 /knowledge sync 能检索到

完成标准
- 零配置可用；创建、打开、检索通路打通
- 与知识库统一同步与编码
