# Wiki CLI 设计文档 (重构版)

## 1. 引言

### 1.1. 目的
本文档旨在详细设计 DAIP-LIVE 系统中 Wiki CLI 的架构、模块划分、接口定义和数据模型，为开发提供技术指导。

### 1.2. 范围
本文档涵盖 DAIP-LIVE 系统中 Wiki CLI 的核心功能模块设计。

### 1.3. 参考资料
*   Wiki CLI 需求文档 (重构版)
*   DAIP-LIVE 系统架构文档

## 2. 整体架构

### 2.1. 架构图
```
+-----------------+
|   CLI 命令解析  |
+-----------------+
         |
         v
+-----------------+
|  Wiki 服务接口  |
+-----------------+
         |
         v
+-----------------+
| Wiki 服务实现类 |
+-----------------+
         |
         v
+-----------------+
|   数据访问层    |
+-----------------+
```

### 2.2. 模块划分
*   **CLI 命令解析**: 负责解析用户输入的命令行参数，并调用相应的服务接口。
*   **Wiki 服务接口**: 定义 Wiki 操作的抽象接口，如创建、查看、编辑、删除、搜索、列出页面等。
*   **Wiki 服务实现类**: 实现 Wiki 服务接口，处理具体的业务逻辑。
*   **数据访问层**: 负责与底层数据存储（如文件系统、数据库）进行交互。

## 3. 详细设计

### 3.1. CLI 命令解析

#### 3.1.1. 技术选型
*   **Typer**: 用于构建 CLI 应用。
*   **Rich**: 用于美化 CLI 输出。

#### 3.1.2. 命令结构
```
daip-cli wiki create <title> [--content <content>] [--tags <tags>]
daip-cli wiki view <title_or_id>
daip-cli wiki edit <title_or_id> [--content <content>] [--tags <tags>]
daip-cli wiki delete <title_or_id> [--force]
daip-cli wiki search <keywords> [--scope <scope>]
daip-cli wiki list [--filter <filter>] [--sort <sort>]
```

#### 3.1.3. 命令实现
*   每个命令对应一个函数，函数内部调用相应的服务接口。
*   使用 Typer 的装饰器来定义命令和参数。

### 3.2. Wiki 服务接口

#### 3.2.1. 接口定义
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class WikiPage:
    id: str
    title: str
    content: str
    author: str
    created_at: str
    updated_at: str
    tags: List[str]

class WikiServiceInterface(ABC):
    @abstractmethod
    def create_page(self, title: str, content: str = "", tags: List[str] = None) -> WikiPage:
        pass

    @abstractmethod
    def get_page(self, title_or_id: str) -> WikiPage:
        pass

    @abstractmethod
    def update_page(self, title_or_id: str, content: str = None, tags: List[str] = None) -> WikiPage:
        pass

    @abstractmethod
    def delete_page(self, title_or_id: str) -> bool:
        pass

    @abstractmethod
    def search_pages(self, keywords: str, scope: str = "all") -> List[WikiPage]:
        pass

    @abstractmethod
    def list_pages(self, filter: dict = None, sort: str = "created_at") -> List[WikiPage]:
        pass
```

### 3.3. Wiki 服务实现类

#### 3.3.1. 类定义
```python
from typing import List, Optional
from .interfaces import WikiServiceInterface, WikiPage

class WikiService(WikiServiceInterface):
    def __init__(self, data_access_layer):
        self.data_access_layer = data_access_layer

    def create_page(self, title: str, content: str = "", tags: List[str] = None) -> WikiPage:
        # 实现创建页面的逻辑
        pass

    def get_page(self, title_or_id: str) -> WikiPage:
        # 实现获取页面的逻辑
        pass

    def update_page(self, title_or_id: str, content: str = None, tags: List[str] = None) -> WikiPage:
        # 实现更新页面的逻辑
        pass

    def delete_page(self, title_or_id: str) -> bool:
        # 实现删除页面的逻辑
        pass

    def search_pages(self, keywords: str, scope: str = "all") -> List[WikiPage]:
        # 实现搜索页面的逻辑
        pass

    def list_pages(self, filter: dict = None, sort: str = "created_at") -> List[WikiPage]:
        # 实现列出页面的逻辑
        pass
```

#### 3.3.2. 业务逻辑
*   **创建页面**:
    1.  验证页面标题是否唯一。
    2.  创建 `WikiPage` 对象。
    3.  调用数据访问层保存页面。
*   **获取页面**:
    1.  根据标题或 ID 查找页面。
    2.  返回 `WikiPage` 对象。
*   **更新页面**:
    1.  根据标题或 ID 查找页面。
    2.  更新页面内容和元数据。
    3.  调用数据访问层保存更新后的页面。
*   **删除页面**:
    1.  根据标题或 ID 查找页面。
    2.  调用数据访问层删除页面。
*   **搜索页面**:
    1.  根据关键词在页面标题、内容、标签中进行搜索。
    2.  返回匹配的 `WikiPage` 对象列表。
*   **列出页面**:
    1.  根据过滤条件筛选页面。
    2.  根据排序方式对页面进行排序。
    3.  返回 `WikiPage` 对象列表。

### 3.4. 数据访问层

#### 3.4.1. 技术选型
*   **文件系统**: 初始版本使用文件系统存储 Wiki 页面。
*   **JSON**: 使用 JSON 格式存储页面数据。

#### 3.4.2. 数据模型
*   **页面文件**: 每个 Wiki 页面存储为一个独立的 JSON 文件。
*   **文件名**: 使用页面标题或 ID 作为文件名。
*   **文件内容**: 包含页面的所有元数据和内容。

#### 3.4.3. 接口定义
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from .interfaces import WikiPage

class DataAccessLayerInterface(ABC):
    @abstractmethod
    def save_page(self, page: WikiPage) -> bool:
        pass

    @abstractmethod
    def load_page(self, title_or_id: str) -> WikiPage:
        pass

    @abstractmethod
    def delete_page(self, title_or_id: str) -> bool:
        pass

    @abstractmethod
    def search_pages(self, keywords: str, scope: str = "all") -> List[WikiPage]:
        pass

    @abstractmethod
    def list_pages(self, filter: dict = None, sort: str = "created_at") -> List[WikiPage]:
        pass
```

#### 3.4.4. 实现
```python
import os
import json
from typing import List, Optional
from .interfaces import WikiPage, DataAccessLayerInterface

class FileSystemDataAccessLayer(DataAccessLayerInterface):
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def save_page(self, page: WikiPage) -> bool:
        # 实现保存页面到文件系统的逻辑
        pass

    def load_page(self, title_or_id: str) -> WikiPage:
        # 实现从文件系统加载页面的逻辑
        pass

    def delete_page(self, title_or_id: str) -> bool:
        # 实现从文件系统删除页面的逻辑
        pass

    def search_pages(self, keywords: str, scope: str = "all") -> List[WikiPage]:
        # 实现从文件系统搜索页面的逻辑
        pass

    def list_pages(self, filter: dict = None, sort: str = "created_at") -> List[WikiPage]:
        # 实现从文件系统列出页面的逻辑
        pass
```

## 4. 数据模型

### 4.1. WikiPage
*   **id** (str): 页面唯一标识符。
*   **title** (str): 页面标题。
*   **content** (str): 页面内容。
*   **author** (str): 页面作者。
*   **created_at** (str): 页面创建时间。
*   **updated_at** (str): 页面最后更新时间。
*   **tags** (List[str]): 页面标签列表。

## 5. 错误处理

### 5.1. 异常定义
```python
class WikiServiceError(Exception):
    """Wiki 服务相关的基础异常类"""
    pass

class PageNotFoundError(WikiServiceError):
    """页面未找到异常"""
    pass

class PageAlreadyExistsError(WikiServiceError):
    """页面已存在异常"""
    pass

class InvalidInputError(WikiServiceError):
    """无效输入异常"""
    pass
```

### 5.2. 异常处理
*   在服务实现类中捕获底层异常，并转换为定义的异常类型。
*   在 CLI 命令解析层捕获服务异常，并向用户显示友好的错误信息。

## 6. 安全性设计

### 6.1. 输入验证
*   对所有用户输入进行严格的验证，防止注入攻击。

### 6.2. 权限控制
*   (未来考虑) 实现基于角色的权限控制，限制对敏感页面的访问和修改。

## 7. 可扩展性设计

### 7.1. 插件化架构
*   通过定义清晰的接口，支持未来通过插件扩展功能。

### 7.2. 配置管理
*   支持通过配置文件管理 Wiki CLI 的行为。

## 8. 性能优化

### 8.1. 缓存机制
*   (未来考虑) 实现页面缓存，提高访问速度。

### 8.2. 索引优化
*   (未来考虑) 为搜索功能建立索引，提高搜索效率。