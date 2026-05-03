# P1 数据持久化 - API参考 (P1 Data Persistence - API Reference)

## 📋 核心类与方法

### DatabaseManager
```python
class DatabaseManager:
    def get_session(self) -> AsyncSession:
        """获取数据库会话"""
    
    async def initialize_db(self) -> None:
        """初始化数据库"""
    
    async def close(self) -> None:
        """关闭数据库连接"""
```

### Repository基类
```python
class BaseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, obj: Any) -> Any:
        """创建新对象"""
    
    async def get_by_id(self, id: int) -> Any:
        """根据ID获取对象"""
    
    async def update(self, id: int, **kwargs) -> Any:
        """更新对象"""
    
    async def delete(self, id: int) -> bool:
        """删除对象"""
```

## 🧩 数据模型

### SQLAlchemy模型示例
```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String

class Base(DeclarativeBase):
    pass

class SessionModel(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    created_at = Column(DateTime)
```

### 配置模型
```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    path: str  # 数据库文件路径
```

## 🔧 依赖接口

### 依赖的外部组件
- `SQLAlchemy`: ORM框架
- `AsyncSession`: 异步数据库会话
- `Pydantic`: 配置验证

## 📡 数据操作模式
- **事务管理**: 自动事务管理
- **连接池**: 自动连接池管理
- **异步操作**: 所有操作异步支持

---
> **需要实现详情？** 查看 [P1_data_persistence_detailed.md](P1_data_persistence_detailed.md)  
> **需要集成指南？** 查看 [P1_data_persistence_integration.md](P1_data_persistence_integration.md)