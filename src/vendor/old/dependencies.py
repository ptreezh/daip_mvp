"""DAIP Insight Engine - 依赖注入与数据库会话管理模块

本模块提供数据库会话（Session）和核心服务的依赖注入功能，适用于FastAPI等框架的全局依赖管理。
所有全局变量、函数均具备类型注解和详细文档，支持自动化API文档工具提取。
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from src.config import DATABASE_PATH

# 创建数据库引擎（全局单例）
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)

# 创建会话工厂（全局单例）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """获取数据库会话的依赖注入函数。
    用于FastAPI等框架的Depends注入，自动管理会话关闭。
    Yields:
        Session: SQLAlchemy数据库会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库，自动创建所有SQLModel表结构。
    """
    SQLModel.metadata.create_all(engine)


# --- API文档片段 ---
# 本模块所有依赖注入函数、全局变量均已补充类型注解和用途说明，支持Sphinx/自动化API文档工具提取。
