# 🎨 规范设计文档

## 设计原则
- **单一职责原则**：每个存储类只负责一种存储方式
- **开放封闭原则**：通过接口抽象支持扩展
- **依赖倒置原则**：高层模块依赖抽象而非具体实现

## 架构设计
- 抽象层：DataStoreInterface定义标准接口
- 实现层：JSONStorage、SQLiteStorage、FileStorage
- 工厂层：StorageFactory负责实例创建
- 管理层：PersistenceManager统一管理