# P8.1 辩论系统 - API参考 (P8.1 Debate System - API Reference)

## 📋 核心类与方法

### DebateManager
```python
class DebateManager:
    async def run_debate(self, topic: str, roles: List[str], rounds: int) -> AsyncGenerator[DebateEvent, None]:
        """运行辩论流程"""
    
    def get_debate_model_summary(self, roles: List[str]) -> Dict:
        """获取辩论模型摘要"""
    
    async def get_debate_statistics(self, session_id: str) -> DebateStatistics:
        """获取辩论统计信息"""
    
    def get_available_roles(self) -> List[str]:
        """获取可用角色列表"""
    
    async def save_debate_transcript(self, session_id: str, filename: str) -> bool:
        """保存辩论记录"""
```

## 🧩 事件类型

### 辩论事件
```python
from pydantic import BaseModel
from typing import Literal, List, Optional, Dict

class DebateStartEvent(BaseModel):
    type: Literal["debate_start"]
    topic: str
    roles: List[str]
    rounds: int
    session_id: str
    timestamp: datetime

class DebateRoundStartEvent(BaseModel):
    type: Literal["round_start"]
    round_number: int
    topic: str
    timestamp: datetime

class DebateTurnCompleteEvent(BaseModel):
    type: Literal["turn_complete"]
    round_number: int
    participant: str
    position: str  # 正方、反方等
    content: str
    content_preview: str
    token_count: Optional[int] = None
    timestamp: datetime

class DebateCompleteEvent(BaseModel):
    type: Literal["debate_complete"]
    session_id: str
    topic: str
    summary: str
    consensus: Optional[str]
    final_positions: Dict[str, str]
    timestamp: datetime

class TokenUsageEvent(BaseModel):
    type: Literal["token_usage"]
    usage_info: Dict[str, int]  # {"prompt_tokens": x, "completion_tokens": y, "total_tokens": z}
    timestamp: datetime

class ThoughtEvent(BaseModel):
    type: Literal["thought"]
    content: str
    timestamp: datetime

DebateEvent = Union[
    DebateStartEvent, DebateRoundStartEvent, DebateTurnCompleteEvent,
    DebateCompleteEvent, TokenUsageEvent, ThoughtEvent
]
```

## 🔧 数据模型

### 辩论统计信息
```python
class DebateStatistics(BaseModel):
    session_id: str
    total_turns: int
    avg_response_length: float
    participation_balance: Dict[str, float]  # 每个角色的参与度
    discussion_depth: float  # 讨论深度指标
    consensus_level: Optional[float]  # 共识水平
```

### 辩论配置
```python
class DebateConfig(BaseModel):
    default_rounds: int = 3
    max_response_length: int = 2000
    enable_consensus_generation: bool = True
    enable_transcript_storage: bool = True
```

## 🔌 集成接口

### 依赖的外部组件
- `P4 RoleManager`: 角色管理
- `P3 ModelProvider`: 模型调用
- `P0 IKnowledgeManager`: 知识检索（可选）

### 事件流模式
- **异步生成器**: `AsyncGenerator[DebateEvent, None]`
- **实时流式**: 支持实时显示辩论进展
- **类型安全**: 使用联合类型确保事件处理安全

---
> **需要实现详情？** 查看 [P8_1_debate_system_detailed.md](P8_1_debate_system_detailed.md)  
> **需要集成指南？** 查看 [P8_1_debate_system_integration.md](P8_1_debate_system_integration.md)