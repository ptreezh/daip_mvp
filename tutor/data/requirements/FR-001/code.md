# 💻 代码实现

## 核心接口定义

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class DataStoreInterface(ABC):
    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def list_keys(self) -> List[str]:
        pass
```