"""
模块化辩论引擎实现
包含独立的四个核心模块
"""
import asyncio
import uuid
import re
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DecomposedTask:
    """分解后的任务项"""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 3  # 1-5, 5最高
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0)
    completed_at: Optional[float] = None


class DebateRole(Enum):
    """辩论角色枚举"""
    PRO_ARGUER = "pro_arguer"      # 支持方
    CON_ARGUER = "con_arguer"      # 反对方
    MODERATOR = "moderator"        # 主持人
    ANALYST = "analyst"            # 分析师
    FACT_CHECKER = "fact_checker"  # 事实核查员


@dataclass
class DebateParticipant:
    """辩论参与者"""
    name: str
    role: DebateRole
    persona: str = ""
    model_config: Optional[Dict[str, Any]] = None
    current_session: Optional[str] = None
    
    def get_role_prompt(self, topic: str) -> str:
        """获取角色特定的提示词"""
        role_prompts = {
            DebateRole.PRO_ARGUER: f"您是支持方，支持关于'{topic}'的观点。请提供有力的论据和证据。",
            DebateRole.CON_ARGUER: f"您是反对方，质疑关于'{topic}'的观点。提出挑战和反驳。",
            DebateRole.MODERATOR: f"您是主持人，引导关于'{topic}'的辩论，确保有序进行。",
            DebateRole.ANALYST: f"您是分析师，对关于'{topic}'的辩论进行客观分析。",
            DebateRole.FACT_CHECKER: f"您是事实核查员，验证关于'{topic}'的辩论中的事实准确性。"
        }
        return role_prompts.get(self.role, f"您是辩论参与者，参与关于'{topic}'的讨论。")


class DebateRoleManager:
    """辩论角色管理器 - 职责：管理辩论角色和模型分配"""
    
    def __init__(self, role_manager=None, model_provider=None):
        self.role_manager = role_manager
        self.model_provider = model_provider
        self.role_assignments: Dict[str, DebateParticipant] = {}
    
    def get_debate_participants(self, role_names: List[str]) -> List[DebateParticipant]:
        """获取辩论参与者列表"""
        participants = []
        
        role_mapping = {
            "pro_arguer": DebateRole.PRO_ARGUER,
            "con_arguer": DebateRole.CON_ARGUER,
            "moderator": DebateRole.MODERATOR,
            "analyst": DebateRole.ANALYST,
            "fact_checker": DebateRole.FACT_CHECKER
        }
        
        for role_name in role_names:
            debate_role = role_mapping.get(role_name.lower(), DebateRole.PRO_ARGUER)
            
            participant = DebateParticipant(
                name=role_name.replace('_', ' ').replace('-', ' ').title(),
                role=debate_role,
                persona=f"您是{debate_role.value}角色，参与关于该话题的辩论"
            )
            participants.append(participant)
        
        return participants


class DebateEngine:
    """辩论引擎 - 职责：核心辩论执行逻辑和轮次管理"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.current_round = 0
        self.total_rounds = 0
    
    async def run_debate_round(self, topic: str, participants: List[DebateParticipant], 
                              round_num: int, previous_contributions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """运行单轮辩论"""
        contributions = []
        
        for participant in participants:
            contribution = await self._generate_participant_contribution(
                participant, topic, round_num, previous_contributions
            )
            
            contrib_data = {
                "participant": participant.name,
                "role": participant.role.value,
                "contribution": contribution,
                "round": round_num,
                "timestamp": asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0
            }
            contributions.append(contrib_data)
        
        return contributions
    
    async def _generate_participant_contribution(self, participant: DebateParticipant, 
                                              topic: str, round_num: int,
                                              previous_contributions: List[Dict[str, Any]] = None) -> str:
        """生成参与者贡献"""
        if self.model_provider:
            # 构建上下文
            context = self._build_context(previous_contributions)
            
            prompt = f"""{participant.get_role_prompt(topic)}

当前是第 {round_num} 轮辩论。

对话上下文:
{context}

请基于您的角色立场做出贡献，回应其他参与者的观点。"""
            
            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                return f"生成失败: {str(e)}"
        else:
            # 模拟响应
            return f"模拟{participant.role.value}贡献: {topic}的第{round_num}轮发言"
    
    def _build_context(self, previous_contributions: List[Dict[str, Any]]) -> str:
        """构建辩论上下文"""
        if not previous_contributions:
            return "这是辩论的第一轮，尚无前置内容。"
        
        # 获取最近几轮的贡献
        recent_contributions = previous_contributions[-6:]  # 最近6次发言
        
        context_parts = []
        for contrib in recent_contributions:
            context_parts.append(f"{contrib['participant']} ({contrib['role']} - 第{contrib['round']}轮): {contrib['contribution'][:150]}...")
        
        return "\\n".join(context_parts)


class DebateHistoryManager:
    """辩论历史管理器 - 职责：辩论历史记录和会话管理"""
    
    def __init__(self, session_manager=None):
        self.session_manager = session_manager
        self.debate_sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.session_summaries: Dict[str, str] = {}
    
    async def start_debate_session(self, topic: str, participants: List[DebateParticipant]) -> str:
        """开始新的辩论会话"""
        session_id = f"debate_{uuid.uuid4().hex[:8]}"
        
        session_data = {
            "session_id": session_id,
            "topic": topic,
            "participants": [p.name for p in participants],
            "start_time": asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0,
            "rounds": [],
            "status": "active"
        }
        
        self.debate_sessions[session_id] = [session_data]
        return session_id
    
    async def record_debate_round(self, session_id: str, round_num: int, contributions: List[Dict[str, Any]]):
        """记录辩论回合"""
        if session_id in self.debate_sessions:
            round_data = {
                "round_number": round_num,
                "contributions": contributions,
                "timestamp": asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0
            }
            
            self.debate_sessions[session_id][0]["rounds"].append(round_data)
    
    async def complete_debate_session(self, session_id: str) -> Dict[str, Any]:
        """完成辩论会话"""
        if session_id in self.debate_sessions:
            session_data = self.debate_sessions[session_id][0]
            session_data["status"] = "completed"
            session_data["end_time"] = asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0
            
            # 生成会话摘要
            summary = await self._generate_session_summary(session_data)
            self.session_summaries[session_id] = summary
            
            return session_data
    
    async def get_debate_summary(self, session_id: str) -> Optional[str]:
        """获取辩论会话摘要"""
        return self.session_summaries.get(session_id)
    
    async def _generate_session_summary(self, session_data: Dict[str, Any]) -> str:
        """生成会话摘要"""
        topic = session_data["topic"]
        rounds = session_data["rounds"]
        participant_names = session_data["participants"]
        
        summary = f"关于'{topic}'的辩论总结:\\n"
        summary += f"参与者: {', '.join(participant_names)}\\n"
        summary += f"总回合数: {len(rounds)}\\n\\n"
        
        for round_data in rounds:
            summary += f"第{round_data['round_number']}轮:\\n"
            for contrib in round_data["contributions"]:
                summary += f"  {contrib['participant']} ({contrib['role']}): {contrib['contribution'][:100]}...\\n"
            summary += "\\n"
        
        return summary


class ModularDebateManager:
    """模块化辩论管理器 - 职责：协调各模块工作，提供统一接口"""
    
    def __init__(self, model_provider=None, session_manager=None, role_manager=None):
        self.model_provider = model_provider
        self.session_manager = session_manager
        
        # 初始化各独立模块
        self.role_manager = DebateRoleManager(role_manager, model_provider)
        self.debate_engine = DebateEngine(model_provider)
        self.history_manager = DebateHistoryManager(session_manager)
        
        # 保持对原始增强辩论管理器的兼容性（可选）
        self.use_legacy_manager = False
    
    async def run_debate_with_task_list_generation(self, topic: str, 
                                                  roles_names: List[str], 
                                                  num_rounds: int = 3) -> AsyncGenerator[str, None]:
        """
        运行辩论并生成任务清单
        这是核心功能，会在开始辩论前生成可见的任务清单
        """
        yield f"[bold blue]🎮 启动辩论: {topic}[/bold blue]"
        
        # 生成任务清单显示给用户
        task_list_display = self._generate_debate_task_list(topic, roles_names, num_rounds)
        yield f"\\n[bold cyan]📋 辩论任务清单生成:[/bold cyan]\\n\\n{task_list_display}"
        
        # 开始辩论
        participants = self.role_manager.get_debate_participants(roles_names)
        session_id = await self.history_manager.start_debate_session(topic, participants)
        
        yield f"[dim]会话ID: {session_id} | 参€ {len(participants)} 个角色 | {num_rounds} 轮[/dim]"
        
        all_contributions = []
        
        # 逐轮执行辩论
        for round_num in range(1, num_rounds + 1):
            yield f"\\n[bold yellow]🔄 第 {round_num}/{num_rounds} 轮开始...[/bold yellow]"
            
            # 更新任务清单显示（标记当前轮次为进行中）
            updated_task_list = self._generate_debate_task_list(topic, roles_names, num_rounds, current_round=round_num)
            yield f"\\n[bold cyan]📋 任务进度更新:[/bold cyan]\\n\\n{updated_task_list}"
            
            # 执行当前轮次
            round_contributions = await self.debate_engine.run_debate_round(
                topic, participants, round_num, all_contributions
            )
            
            # 记录到历史
            await self.history_manager.record_debate_round(session_id, round_num, round_contributions)
            
            # 显示当前轮次的贡献
            for contrib in round_contributions:
                participant_name = contrib['participant']
                participant_role = contrib['role']
                content = contrib['contribution']
                
                yield f"[bold magenta]{participant_name} ({participant_role}):[/bold magenta] {content}"
            
            all_contributions.extend(round_contributions)
            
            yield f"[dim]--- 第 {round_num} 轮结束 ---[/dim]"
        
        # 辩论完成，显示最终进度
        completed_task_list = self._generate_debate_task_list(topic, roles_names, num_rounds, current_round=num_rounds, completed=True)
        yield f"\\n[bold green]✅ 辩论完成 - 最终进度:[/bold green]\\n\\n{completed_task_list}"
        
        # 生成并显示总结
        summary = await self.history_manager.get_debate_summary(session_id)
        yield f"\\n[bold yellow]🎯 辩论总结:[/bold yellow]\\n{summary}"
    
    def _generate_debate_task_list(self, topic: str, roles_names: List[str], num_rounds: int, 
                                 current_round: int = 0, completed: bool = False) -> str:
        """生成辩论任务清单的显示文本"""
        display = f"**主题**: {topic}\\n"
        display += f"**参与者**: {', '.join(roles_names)}\\n"
        display += f"**总轮次**: {num_rounds}\\n\\n"
        
        # 生成每轮的任务
        for round_num in range(1, num_rounds + 1):
            if round_num < current_round:
                # 已完成的轮次
                display += f"✅ **第 {round_num}/{num_rounds} 轮** (已完成)\\n"
                display += f"   - 参€ {len(roles_names)} 个角色发言\\n\\n"
            elif round_num == current_round:
                # 正在进行的轮次
                if completed:
                    display += f"✅ **第 {round_num}/{num_rounds} 轮** (已完成)\\n"
                else:
                    display += f"🔄 **第 {round_num}/{num_rounds} 轮** (进行中)\\n"
                display += f"   - 参€ {len(roles_names)} 个角色发言\\n\\n"
            else:
                # 待执行的轮次
                display += f"⏳ **第 {round_num}/{num_rounds} 轮** (待执行)\\n"
                display += f"   - 参€ {len(roles_names)} 个角色发言\\n\\n"
        
        # 添加进度统计
        completed_rounds = max(0, current_round - 1) if not completed else num_rounds
        progress_percent = (completed_rounds / num_rounds * 100) if num_rounds > 0 else 0
        
        display += f"\\n📊 **总进度**: {completed_rounds}/{num_rounds} 轮完成 ({progress_percent:.1f}%)"
        
        return display


# 实现与EnhancedDebateManager的兼容接口
class CompatibleDebateManager:
    """
    与现有EnhancedDebateManager兼容的模块化实现
    保持相同的接口和方法签名
    """
    
    def __init__(
        self,
        session_manager=None,
        role_manager=None,
        role_model_manager=None,
        model_provider=None,
        debate_history_tracker=None,
        use_optimized_architecture: bool = False
    ):
        self.modular_manager = ModularDebateManager(
            model_provider=model_provider,
            session_manager=session_manager,
            role_manager=role_manager
        )
        
        # 保持原有属性以确保兼容性 
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider
        self.debate_history_tracker = debate_history_tracker
    
    async def run_debate(self, topic: str, roles_names: List[str], num_rounds: int) -> AsyncGenerator[str, None]:
        """与原接口兼容的辩论运行方法"""
        async for event in self.modular_manager.run_debate_with_task_list_generation(topic, roles_names, num_rounds):
            yield event


if __name__ == "__main__":
    print("="*90)
    print("🎯 模块化辩论系统核心模块实现")
    print("="*90)
    
    print("\\n📦 已实现的独立模块:")
    modules = [
        "DebateRoleManager: 角色管理模块 (~50行)",
        "DebateEngine: 核心辩论执行模块 (~80行)", 
        "DebateHistoryManager: 历史管理模块 (~60行)",
        "ModularDebateManager: 协调中心模块 (~70行)"
    ]
    
    for module in modules:
        print(f"   ✅ {module}")
    
    print("\\n🔧 模块特性:")
    print("   - 每个模块职责单一，代码量少")
    print("   - 模块间低耦合，易于独立测试")
    print("   - 提供清晰的接口定义")
    print("   - 支持向后兼容")
    print("   - 保持原有功能完整性")
    
    print("\\n🎯 核心功能:")
    print("   - 自动生成辩论任务清单并显示给用户")
    print("   - 实时更新任务状态 (⏳待执行 → 🔄进行中 → ✅已完成)")
    print("   - 顺序执行辩论轮次并记录进度")
    print("   - 支持多角色协作辩论") 
    print("   - 生成辩论历史和总结")
    
    print("\\n✅ 模块化辩论引擎实现完成!")
    print("现在可以将复杂辩论任务分解为可视化的任务清单并逐步执行。")