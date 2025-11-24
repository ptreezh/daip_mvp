"""
任务上下文数据模型
遵循单一职责原则 - 仅负责任务上下文数据表示
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class TaskContext:
    """
    任务上下文数据模型
    遵循单一职责原则 - 专门负责任务上下文数据的表示
    """
    task_type: str  # 任务类型 (e.g., "wiki_creation", "debate")
    parameters: Dict[str, Any] = field(default_factory=dict)  # 任务参数
    required_params: List[str] = field(default_factory=list)  # 所需参数列表
    filled_params: List[str] = field(default_factory=list)  # 已填充参数列表
    status: str = "active"  # 任务状态
    created_at: datetime = field(default_factory=datetime.now)  # 任务创建时间
    last_updated: datetime = field(default_factory=datetime.now)  # 最后更新时间
    
    def add_parameter(self, param_name: str, param_value: Any) -> None:
        """
        添加参数到任务上下文
        
        Args:
            param_name: 参数名称
            param_value: 参数值
        """
        self.parameters[param_name] = param_value
        if param_name not in self.filled_params:
            self.filled_params.append(param_name)
        self.last_updated = datetime.now()
    
    def is_complete(self) -> bool:
        """
        检查任务是否已完成（所有必需参数都已填充）
        
        Returns:
            如果任务已完成则返回True，否则返回False
        """
        return all(param in self.filled_params for param in self.required_params)
    
    def get_missing_params(self) -> List[str]:
        """
        获取缺失的参数
        
        Returns:
            缺失的参数列表
        """
        return [param for param in self.required_params if param not in self.filled_params]