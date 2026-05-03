# 📝 规范化提示词表述

请为P1数据持久化模块实现统一的数据存储接口抽象。具体要求：

- 定义DataStoreInterface抽象基类
- 支持JSON、SQLite、文件三种存储后端
- 实现save、load、delete、list_keys核心方法
- 确保线程安全和异常处理
- 满足性能要求：响应时间<100ms