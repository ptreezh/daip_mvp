# P1 数据持久化 - 集成指南 (P1 Data Persistence - Integration Guide)

## 🔗 与其他模块的集成

### 与P0核心接口集成
```python
# 遵循P0的数据契约
from daip_live.core.models import Session as CoreSession

class SessionRepository:
    async def save_session(self, core_session: CoreSession) -> bool:
        # 将核心会话模型保存到数据库
        pass
```

### 与P5代理引擎集成
```python
# P5使用P1进行会话持久化
from daip_live.p1_data_persistence.repositories.session_repo import SessionRepository

class AgentExecutor:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo
    
    async def save_session_state(self, session_id: int):
        await self.session_repo.update(session_id, state=self.state)
```

## 🔄 数据操作模式

### Repository模式使用
```python
# 标准的Repository使用模式
from daip_live.p1_data_persistence.repositories import SessionRepository

async def use_repository_example():
    # 从依赖注入容器获取repository
    session_repo = container.session_repository()
    
    # 创建新会话
    new_session = await session_repo.create({
        "title": "Test Session",
        "status": "active"
    })
    
    # 获取会话
    session = await session_repo.get_by_id(new_session.id)
    
    # 更新会话
    updated_session = await session_repo.update(
        session.id, 
        status="completed"
    )
    
    return updated_session
```

### 事务管理
```python
# 事务操作示例
from sqlalchemy.ext.asyncio import AsyncSession

async def transaction_example(session: AsyncSession):
    try:
        # 执行多个相关操作
        await session.execute(...)  # 操作1
        await session.execute(...)  # 操作2
        await session.commit()  # 提交事务
    except Exception:
        await session.rollback()  # 回滚事务
        raise
```

## 🔌 使用示例

### 基本CRUD操作
```python
from daip_live.p1_data_persistence.database import DatabaseManager
from daip_live.p1_data_persistence.repositories import SessionRepository

# 初始化数据库管理器
db_manager = DatabaseManager(config=DatabaseConfig(path="./daip_live.db"))
await db_manager.initialize_db()

# 使用Repository进行操作
async with db_manager.get_session() as session:
    repo = SessionRepository(session)
    
    # 创建
    new_item = await repo.create({"name": "test", "value": 100})
    
    # 读取
    item = await repo.get_by_id(new_item.id)
    
    # 更新
    updated_item = await repo.update(item.id, value=200)
    
    # 删除
    await repo.delete(updated_item.id)
```

### 配置管理
```python
from daip_live.p1_data_persistence.config import DatabaseConfig

# 创建数据库配置
config = DatabaseConfig(
    path="./data/daip_live.db"
)
```

## ⚡ 性能考虑
- **连接池**: 合理设置连接池大小
- **批量操作**: 使用批量操作提高性能
- **索引优化**: 为频繁查询的字段创建索引

## 🐛 常见集成问题
- **连接池耗尽**: 增加连接池大小或优化连接使用
- **事务冲突**: 实现重试机制
- **并发访问**: 使用适当的锁机制

---
> **需要API详情？** 查看 [P1_data_persistence_api.md](P1_data_persistence_api.md)  
> **需要实现详情？** 查看 [P1_data_persistence_detailed.md](P1_data_persistence_detailed.md)