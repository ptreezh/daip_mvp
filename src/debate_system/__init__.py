#!/usr/bin/env python3
"""多轮辩论系统模块

提供完整的多轮辩论功能，包括：
- 辩论流程定义和管理
- 参与者角色和权限控制
- 辩论状态管理和持久化
- 实时通知和同步机制
"""

from .debate_flow_definition import (
    DebateContribution,
    DebateFormat,
    DebateParticipant,
    DebatePhase,
    DebateRound,
    DebateRules,
    DebateSession,
    DebateStatus,
    ParticipantRole,
)
from .debate_state_manager import (
    DebateStateManager,
    MemoryStateStorage,
    StateChange,
    StateChangeType,
    StateSnapshot,
    StateStorage,
)
from .participant_management import ActionRecord, ActionType, ParticipantCredentials, ParticipantManager, Permission

__all__ = [
    # 辩论流程定义
    'DebatePhase', 'ParticipantRole', 'DebateStatus', 'DebateFormat',
    'DebateSession', 'DebateRound', 'DebateContribution', 'DebateParticipant',
    'DebateRules',
<<<<<<< HEAD

    # 参与者管理
    'Permission', 'ActionType', 'ParticipantManager',
    'ParticipantCredentials', 'ActionRecord',

    # 状态管理
    'StateChangeType', 'StateChange', 'StateSnapshot',
    'DebateStateManager', 'StateStorage', 'MemoryStateStorage'
]
=======
    
    # 参与者管理
    'Permission', 'ActionType', 'ParticipantManager',
    'ParticipantCredentials', 'ActionRecord',
    
    # 状态管理
    'StateChangeType', 'StateChange', 'StateSnapshot',
    'DebateStateManager', 'StateStorage', 'MemoryStateStorage'
]
>>>>>>> feature/core-services-refactor
