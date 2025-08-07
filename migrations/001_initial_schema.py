# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : 001_initial_schema.py
@Description:
    Initial database schema migration.
    Creates all necessary tables for the DAIP backend.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from ..infrastructure.database import (
    BaseModel, UserModel, SessionModel, TaskModel, 
    MessageModel, DebateModel, SystemEventModel
)


logger = logging.getLogger(__name__)


class Migration001:
    """初始数据库架构迁移"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
    
    async def up(self):
        """执行迁移"""
        logger.info("Starting initial schema migration...")
        
        try:
            # 创建数据库引擎
            self.engine = create_async_engine(
                self.database_url,
                echo=True,
                future=True
            )
            
            # 创建会话工厂
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 创建表
            async with self.engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.create_all)
            
            # 插入初始数据
            await self._insert_initial_data()
            
            logger.info("Initial schema migration completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            if self.engine:
                await self.engine.dispose()
    
    async def down(self):
        """回滚迁移"""
        logger.info("Rolling back initial schema migration...")
        
        try:
            # 创建数据库引擎
            self.engine = create_async_engine(
                self.database_url,
                echo=True,
                future=True
            )
            
            # 删除表
            async with self.engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.drop_all)
            
            logger.info("Rollback completed successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise
        finally:
            if self.engine:
                await self.engine.dispose()
    
    async def _insert_initial_data(self):
        """插入初始数据"""
        logger.info("Inserting initial data...")
        
        async with self.session_factory() as session:
            try:
                # 插入默认用户
                default_user = UserModel(
                    user_id="default_user",
                    username="默认用户",
                    email="user@daip.live",
                    preferred_entrance="secretariat",
                    preferences={
                        "language": "zh-CN",
                        "theme": "light",
                        "notification_enabled": True,
                        "auto_transparency": False,
                        "detail_level": "comprehensive"
                    },
                    is_active=True
                )
                session.add(default_user)
                
                # 插入管理员用户
                admin_user = UserModel(
                    user_id="admin_user",
                    username="管理员",
                    email="admin@daip.live",
                    preferred_entrance="secretariat",
                    preferences={
                        "language": "zh-CN",
                        "theme": "dark",
                        "notification_enabled": True,
                        "auto_transparency": True,
                        "detail_level": "comprehensive"
                    },
                    is_active=True
                )
                session.add(admin_user)
                
                await session.commit()
                logger.info("Initial users inserted successfully")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to insert initial data: {e}")
                raise
    
    async def get_migration_info(self) -> Dict[str, Any]:
        """获取迁移信息"""
        return {
            "migration_id": "001_initial_schema",
            "description": "Initial database schema",
            "applied_at": datetime.now().isoformat(),
            "tables_created": [
                "users",
                "sessions", 
                "tasks",
                "messages",
                "debates",
                "system_events"
            ]
        }


async def run_migration(database_url: str, action: str = "up"):
    """运行迁移"""
    migration = Migration001(database_url)
    
    if action == "up":
        await migration.up()
    elif action == "down":
        await migration.down()
    else:
        raise ValueError(f"Unknown action: {action}")
    
    return await migration.get_migration_info()


if __name__ == "__main__":
    import sys
    import os
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 从环境变量获取数据库URL
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://daip:daip@localhost:5432/daip_db")
    
    # 运行迁移
    action = sys.argv[1] if len(sys.argv) > 1 else "up"
    
    async def main():
        try:
            result = await run_migration(database_url, action)
            print(f"Migration completed: {result}")
        except Exception as e:
            print(f"Migration failed: {e}")
            sys.exit(1)
    
    asyncio.run(main())