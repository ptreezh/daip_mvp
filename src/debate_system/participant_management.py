#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辩论参与者管理系统

管理辩论参与者的角色、权限、认证和行为控制。
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .debate_flow_definition import ParticipantRole, DebatePhase


class Permission(Enum):
    """权限枚举"""
    VIEW_DEBATE = "view_debate"
    JOIN_DEBATE = "join_debate"
    LEAVE_DEBATE = "leave_debate"
    MAKE_STATEMENT = "make_statement"
    ASK_QUESTION = "ask_question"
    PROVIDE_REBUTTAL = "provide_rebuttal"
    SUBMIT_EVIDENCE = "submit_evidence"
    MODERATE_DEBATE = "moderate_debate"
    CONTROL_FLOW = "control_flow"
    MANAGE_PARTICIPANTS = "manage_participants"
    END_DEBATE = "end_debate"


class ActionType(Enum):
    """行为类型枚举"""
    CONTRIBUTION = "contribution"
    INTERACTION = "interaction"
    MODERATION = "moderation"
    EVALUATION = "evaluation"
    SYSTEM = "system"


@dataclass
class ParticipantCredentials:
    """参与者凭证"""
    participant_id: str
    authentication_token: str
    role: ParticipantRole
    verified: bool = False
    verification_level: int = 0
    issued_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    issuer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionRecord:
    """行为记录"""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    participant_id: str = ""
    action_type: ActionType = ActionType.CONTRIBUTION
    permission_used: Permission = Permission.VIEW_DEBATE
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    round_number: int = 1
    phase: DebatePhase = DebatePhase.MAIN_ARGUMENTS
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    impact_score: Optional[float] = None


class ParticipantManager:
    """参与者管理器"""
    
    def __init__(self):
        self.participants: Dict[str, ParticipantCredentials] = {}
        self.action_history: List[ActionRecord] = []
    
    def register_participant(self,
                           participant_id: str,
                           role: ParticipantRole,
                           authentication_token: str,
                           verification_level: int = 0) -> ParticipantCredentials:
        """注册参与者"""
        credentials = ParticipantCredentials(
            participant_id=participant_id,
            authentication_token=authentication_token,
            role=role,
            verification_level=verification_level,
            verified=verification_level > 0
        )
        
        self.participants[participant_id] = credentials
        return credentials
    
    def authenticate_participant(self,
                               participant_id: str,
                               authentication_token: str) -> bool:
        """认证参与者"""
        if participant_id not in self.participants:
            return False
        
        credentials = self.participants[participant_id]
        return credentials.authentication_token == authentication_token
    
    def check_permission(self,
                        participant_id: str,
                        permission: Permission,
                        context: Dict[str, Any]) -> bool:
        """检查参与者权限"""
        if participant_id not in self.participants:
            return False
        
        credentials = self.participants[participant_id]
        
        # 简单的权限检查逻辑
        if credentials.role == ParticipantRole.MODERATOR:
            return True  # 主持人拥有所有权限
        
        if credentials.role in [ParticipantRole.EXPERT, ParticipantRole.PROPONENT, ParticipantRole.OPPONENT]:
            return permission in [
                Permission.VIEW_DEBATE, Permission.MAKE_STATEMENT,
                Permission.PROVIDE_REBUTTAL, Permission.SUBMIT_EVIDENCE
            ]
        
        if credentials.role == ParticipantRole.OBSERVER:
            return permission == Permission.VIEW_DEBATE
        
        return False
    
    def record_action(self,
                     participant_id: str,
                     action_type: ActionType,
                     permission_used: Permission,
                     session_id: str,
                     success: bool = True,
                     details: Optional[Dict[str, Any]] = None) -> ActionRecord:
        """记录参与者行为"""
        record = ActionRecord(
            participant_id=participant_id,
            action_type=action_type,
            permission_used=permission_used,
            session_id=session_id,
            success=success,
            details=details or {}
        )
        
        self.action_history.append(record)
        return record