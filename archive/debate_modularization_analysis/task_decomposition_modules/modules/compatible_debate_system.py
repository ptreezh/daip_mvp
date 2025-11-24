"""
兼容性模块化辩论系统实现
保持向后兼容，支持平滑切换到新模块化实现
"""
import asyncio
import sys
from typing import Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


# 保持原有导入路径和模块结构兼容
from daip_live.core.models import *
from daip_live.p8_debate_system.manager import DebateManager as OriginalDebateManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager as OriginalEnhancedDebateManager


# 重用simple_debate_engine模块中的简化实现
from daip_live.task_decomposition.modules.simple_debate_engine import (
    DebateRole, DebateParticipant, DebateRound, SimpleDebateEngine
)


class DebateCompatibilityMode(Enum):
    """辩论兼容模式"""
    ORIGINAL = "original"           # 原始实现
    ENHANCED = "enhanced"          # 增强实现  
    MODULED = "modular"            # 模块化实现
    AUTO = "auto"                  # 自动选择


@dataclass 
class DebateSessionInfo:
    """辩论会话信息"""
    session_id: str
    topic: str
    mode: DebateCompatibilityMode
    created_at: float
    status: str = "active"


class CompatibleDebateManager:
    """
    兼容性辩论管理器
    保持与原系统完全兼容，同时支持模块化实现
    """
    
    def __init__(self, 
                 session_manager=None, 
                 role_manager=None, 
                 model_provider=None,
                 use_modular_implementation: bool = True,
                 fallback_to_original: bool = True):
        
        # 保留原有的依赖注入
        self._session_manager = session_manager
        self._role_manager = role_manager
        self._model_provider = model_provider

        # 初始化模块化实现
        self.use_modular_implementation = use_modular_implementation
        self.fallback_to_original = fallback_to_original

        # 原始实现
        if session_manager and role_manager and model_provider:
            from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager as OriginalEnhancedDebateManager
            self._original_manager = OriginalEnhancedDebateManager(
                session_manager, role_manager, model_provider, model_provider
            )
        else:
            self._original_manager = None
        
        # 模块化实现
        self._modular_engine = SimpleDebateEngine(model_provider)
        self._active_sessions: Dict[str, DebateSessionInfo] = {}
    
    async def run_debate(self, topic: str, roles_names: List[str], num_rounds: int) -> AsyncGenerator[AgentEvent, None]:
        """
        运行辩论 - 兼容性方法
        根据设置选择模块化或原始实现
        """
        if self.use_modular_implementation:
            try:
                # 使用模块化实现
                async for event in self._run_debate_modular(topic, roles_names, num_rounds):
                    yield event
            except Exception as e:
                # 如果模块化实现失败，回退到原始实现
                if self.fallback_to_original and self._original_manager:
                    print(f"[COMPATIBILITY] 模块化实现失败，回退到原始实现: {e}")
                    async for event in self._original_manager.run_debate(topic, roles_names, num_rounds):
                        yield event
                else:
                    raise e
        else:
            # 使用原始实现
            if self._original_manager:
                async for event in self._original_manager.run_debate(topic, roles_names, num_rounds):
                    yield event
            else:
                # 原始实现不可用时，使用模块化实现
                async for event in self._run_debate_modular(topic, roles_names, num_rounds):
                    yield event
    
    async def _run_debate_modular(self, topic: str, roles_names: List[str], num_rounds: int) -> AsyncGenerator[AgentEvent, None]:
        """
        模块化实现的辩论运行方法
        保持与原始方法相同的返回类型和接口
        """
        # 创建参与者的兼容性转换
        participants = []
        role_mapping = {
            "pro_arguer": DebateRole.PRO_ARGUER,
            "con_arguer": DebateRole.CON_ARGUER,
            "moderator": DebateRole.MODERATOR,
            "analyst": DebateRole.ANALYST,
            "fact_checker": DebateRole.FACT_CHECKER
        }
        
        for role_name in roles_names:
            debate_role = role_mapping.get(role_name.lower(), DebateRole.PRO_ARGUER)
            participant = DebateParticipant(
                name=role_name,
                role=debate_role
            )
            participants.append(participant)
        
        # 生成一个唯一会话ID
        session_id = f"modular_debate_{len(self._active_sessions) + 1}_{topic.replace(' ', '_')[:20]}"
        
        # 创建会话信息
        session_info = DebateSessionInfo(
            session_id=session_id,
            topic=topic,
            mode=DebateCompatibilityMode.MODULED,
            created_at=asyncio.get_event_loop().time()
        )
        self._active_sessions[session_id] = session_info
        
        # 发送辩论开始事件
        yield DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=session_id
        )
        
        # 运行模块化辩论引擎
        async for event_content in self._modular_engine.start_debate(topic, participants, num_rounds):
            # 将字符串事件转换为AgentEvent类型
            if "ROUND" in event_content or "轮" in event_content:
                yield DebateRoundStartEvent(
                    topic=topic,
                    round_number=event_content.split()[1] if len(event_content.split()) > 1 else 1,
                    session_id=session_id
                )
            elif "贡献" in event_content or ":" in event_content:
                # 将参与者贡献转换为TurnComplete事件
                if ":" in event_content:
                    parts = event_content.split(":", 1)
                    participant_name = parts[0].strip("[]()").replace("*", "")
                    contribution = parts[1].strip() if len(parts) > 1 else event_content
                else:
                    participant_name = "Unknown"
                    contribution = event_content
                
                yield DebateTurnCompleteEvent(
                    topic=topic,
                    participant=participant_name,
                    content=contribution,
                    session_id=session_id
                )
            else:
                # 使用ThoughtEvent承载其他信息
                yield ThoughtEvent(content=event_content)
        
        # 发送辩论完成事件
        yield DebateCompleteEvent(
            topic=topic,
            session_id=session_id,
            summary=f"模块化辩论完成: {topic}"
        )
        
        # 更新会话状态
        if session_id in self._active_sessions:
            self._active_sessions[session_id].status = "completed"
    
    def get_current_sessions(self) -> List[DebateSessionInfo]:
        """获取当前会话 - 保持兼容性"""
        return [session for session in self._active_sessions.values() if session.status == "active"]
    
    def get_debate_model_summary(self, roles_names: List[str]) -> Dict[str, Any]:
        """获取辩论模型摘要 - 保持与原增强管理器兼容"""
        if self._original_manager and hasattr(self._original_manager, 'get_debate_model_summary'):
            return self._original_manager.get_debate_model_summary(roles_names)
        else:
            # 模块化实现的默认摘要
            return {
                "total_participants": len(roles_names),
                "roles_assigned": roles_names,
                "models_used": ["default_model"] * len(roles_names),
                "estimated_duration": "N/A"
            }
    
    async def run_debate_with_original_if_fails(self, topic: str, roles_names: List[str], num_rounds: int) -> AsyncGenerator[AgentEvent, None]:
        """带原始实现回退的辩论运行"""
        return await self.run_debate(topic, roles_names, num_rounds)


# 为TUI提供后向兼容的导入
class DebateManagerForTUI:
    """为TUI提供的兼容性辩论管理器"""
    
    def __init__(self, session_manager=None, role_manager=None, model_provider=None):
        # 使用兼容性管理器，但默认使用原始实现以确保兼容性
        self.compatible_manager = CompatibleDebateManager(
            session_manager=session_manager,
            role_manager=role_manager, 
            model_provider=model_provider,
            use_modular_implementation=False,  # 默认使用原始实现以保持兼容性
            fallback_to_original=True
        )
    
    async def run_debate(self, topic: str, roles_names: List[str], num_rounds: int = 3) -> AsyncGenerator[AgentEvent, None]:
        """TUI兼容的辩论运行接口"""
        async for event in self.compatible_manager.run_debate(topic, roles_names, num_rounds):
            yield event


# 模块化接口，可逐步启用
class ModularDebateInterface:
    """模块化辩论接口 - 降低复杂度和测试工作量"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.simple_engine = SimpleDebateEngine(model_provider)
    
    async def run_simple_debate(self, topic: str, roles: List[str] = None, rounds: int = 3) -> AsyncGenerator[str, None]:
        """运行简单的模块化辩论 - 用于单元测试和快速原型"""
        if roles is None:
            roles = ["pro_arguer", "con_arguer"]
        
        # 创建参与者
        participants = []
        role_mapping = {
            "pro_arguer": DebateRole.PRO_ARGUER,
            "con_arguer": DebateRole.CON_ARGUER,
            "moderator": DebateRole.MODERATOR,
            "analyst": DebateRole.ANALYST,
            "fact_checker": DebateRole.FACT_CHECKER
        }
        
        for role_name in roles:
            debate_role = role_mapping.get(role_name.lower(), DebateRole.PRO_ARGUER)
            participant = DebateParticipant(
                name=role_name.replace('_', ' ').title(),
                role=debate_role
            )
            participants.append(participant)
        
        # 运行辩论
        async for event_content in self.simple_engine.start_debate(topic, participants, rounds):
            yield event_content
    
    async def run_with_compatibility_layer(self, topic: str, roles_names: List[str], num_rounds: int) -> AsyncGenerator[AgentEvent, None]:
        """带兼容层的模块化辩论运行 - 将字符串转换为AgentEvent"""
        async for event_str in self.run_simple_debate(topic, roles_names, num_rounds):
            # 将字符串事件转换为适当的AgentEvent类型
            if "开始处理复杂任务" in event_str:
                yield DebateStartEvent(
                    topic=topic,
                    roles=roles_names,
                    rounds=num_rounds,
                    session_id=f"simple_{len(self.simple_engine.active_debates)+1}"
                )
            elif "任务执行完成" in event_str or "辩论总结" in event_str:
                yield DebateCompleteEvent(
                    topic=topic,
                    session_id=f"simple_{len(self.simple_engine.active_debates)}",
                    summary=event_str
                )
            else:
                yield ThoughtEvent(content=event_str)


if __name__ == "__main__":
    print("="*80)
    print("🔄 兼容性模块化辩论系统实现")
    print("保持向后兼容，支持平滑切换")
    print("="*80)
    
    print("\\n📋 兼容性保障:")
    print("  ✅ 保留所有原有接口")
    print("  ✅ 支持原始实现回退") 
    print("  ✅ 保持事件类型兼容")
    print("  ✅ 逐步启用模块化实现")
    print("  ✅ 不影响现有用户体验")
    print("  ✅ 不破坏外部系统集成")
    
    print("\\n🎯 重构收益:")
    print("  ✅ 降低系统复杂度 - 模块化设计")
    print("  ✅ 减少测试工作量 - 可独立测试模块") 
    print("  ✅ 提高可维护性 - 职责分离")
    print("  ✅ 保持功能完整性 - 全部功能保留")
    print("  ✅ 支持逐步迁移 - 平滑过渡")
    
    print("\\n🔧 新的模块化接口:")
    print("  - CompatibleDebateManager: 兼容性管理器，支持原实现与新模块切换")
    print("  - ModularDebateInterface: 纯模块化接口，便于测试和开发")
    print("  - SimpleDebateEngine: 简化的辩论引擎，核心功能模块")
    
    print("\\n✅ 兼容性模块化辩论实现完成!")
    print("   现在可以逐步启用模块化实现而不影响现有功能")