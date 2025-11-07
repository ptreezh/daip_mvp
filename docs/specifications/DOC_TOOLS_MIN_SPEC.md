# 文献下载与格式转换工具最小集规范

目标
- 为科研/写作提供开箱即用的最小工具：arXiv 下载与 Markdown 导出 PDF/DOCX

命令（TUI/CLI）
- /doc fetch <query|arxiv_id> [--max N]：检索/下载 PDF 与元数据（md 说明），保存到 ./docs/papers/
- /doc export <input.md> --to pdf|docx [--out <path>]：将 Markdown 导出为 PDF/DOCX

实现建议（YAGNI）
- arXiv：优先使用 python-arxiv 库；失败降级到简单HTTP下载（若提供直链）；保存 metadata.json 与 README.md 摘要
- 导出：
  - 首选 pandoc（自检依赖）；
  - 若缺失，docx 使用 python-docx；pdf 降级为提示+生成 .docx（用户可另行转pdf）

依赖自检与降级
- 启动或首次使用时检查：pandoc、python-docx、arxiv
- 缺失则：禁用对应选项，TUI 全局一次性告警，可关闭；给出安装提示

路径与编码
- papers 目录：./docs/papers（UTF-8，文件名净化）
- export 输出：默认与输入同目录

权限与安全
- 写文件走权限策略；网络请求仅限 arXiv 下载（可开关）

TDD 要点
- fetch：mock arxiv 返回；保存PDF/metadata；失败降级分支
- export：有/无 pandoc 分支；docx 生成校验；pdf 不可用时提示

完成标准
- 常见用例零配置成功；缺依赖能优雅降级且有引导
