# P1 数据持久化 - 故障排除 (P1 Data Persistence - Troubleshooting)

## 🚨 常见问题

### 1. 数据库连接问题
**症状**: 连连接数据库失败或超时
**可能原因**: 
- 数据库文件路径不存在
- 权限不足
- 数据库文件被锁定

**解决方案**:
```python
import os
from pathlib import Path

# 检查数据库路径和权限
db_path = Path("./daip_live.db")
db_dir = db_path.parent

# 确保目录存在
db_dir.mkdir(parents=True, exist_ok=True)

# 检查权限
if not os.access(db_dir, os.W_OK):
    print(f"无法写入目录: {db_dir}")
```

### 2. 事务冲突
**症状**: 并发操作导致的事务回滚
**可能原因**: 
- 并发访问同一数据
- 长时间运行的事务

**解决方案**:
```python
import asyncio
from sqlalchemy.exc import OperationalError

async def retry_on_conflict(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                await asyncio.sleep(0.1 * (2 ** attempt))  # 指数退避
            else:
                raise
```

## 🔧 诊断工具

### 数据库状态检查
```python
async def check_database_status(db_manager):
    try:
        async with db_manager.get_session() as session:
            result = await session.execute("SELECT 1")
            print("数据库连接正常")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False
```

### 连接池监控
```python
# 监控连接池状态
def monitor_connection_pool(engine):
    print(f"当前池大小: {engine.pool.size()}")
    print(f"当前连接数: {engine.pool.checkedout()}")
    print(f"空闲连接数: {engine.pool.checkedin()}")
```

## ⚠️ 性能问题

### 连接池耗尽
- **检查**: 高并发时连接池耗尽
- **解决方案**: 增加连接池大小或优化连接使用

### 查询性能
- **检查**: 慢查询日志
- **解决方案**: 添加适当的索引

## 🔍 调试技巧

### SQL日志
```python
# 启用SQL日志
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 事务调试
```python
async def debug_transaction(repo, operation):
    print("开始事务")
    try:
        result = await operation()
        print("提交事务")
        return result
    except Exception as e:
        print(f"回滚事务: {e}")
        raise
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息
2. 数据库配置（去除敏感信息）
3. 相关操作的代码示例
4. 数据库文件的大小和表结构信息

---
> **需要集成信息？** 查看 [P1_data_persistence_integration.md](P1_data_persistence_integration.md)  
> **需要API详情？** 查看 [P1_data_persistence_api.md](P1_data_persistence_api.md)