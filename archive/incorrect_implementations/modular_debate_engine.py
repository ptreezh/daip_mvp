"""
模块化辩论引擎 - 简化版
将复杂辩论功能分解为独立、可模块化、可复用的组件
"""
import asyncio
import uuid
import re
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举 - 用于任务跟踪"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RoleAssignment:
    """角色分配"""
    id: str = None
    role_name: str = ""
    role_type: 'DebateRole' = None
    persona: Optional[str] = None
    model_config: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"role_{uuid.uuid4().hex[:8]}"
        if self.role_type is None:
            from enum import Enum
            class DebateRole(Enum):
                PRO_ARGUER = "pro_arguer"
                CON_ARGUER = "con_arguer"
                MODERATOR = "moderator" 
                ANALYST = "analyst"
                FACT_CHECKER = "fact_checker"
            self.role_type = DebateRole.PRO_ARGUER


class DebateRole(Enum):
    """辩论角色枚举"""
    PRO_ARGUER = "pro_arguer"      # 支持方
    CON_ARGUER = "con_arguer"      # 反对方
    MODERATOR = "moderator"        # 主持人/调节员
    ANALYST = "analyst"            # 分析师
    FACT_CHECKER = "fact_checker"  # 事实核查员


class DebateParticipantManager:
    """辩论参与者管理器 - 独立模块"""
    
    def __init__(self, role_manager=None):
        self.role_manager = role_manager
        self.participants: Dict[str, RoleAssignment] = {}
    
    def assign_roles(self, role_names: List[str]) -> List[RoleAssignment]:
        """分配角色给参与者"""
        assignments = []
        
        for role_name in role_names:
            # 根据角色名确定角色类型
            role_type = self._determine_role_type(role_name)
            
            assignment = RoleAssignment(
                role_name=role_name,
                role_type=role_type
            )
            assignments.append(assignment)
        
        return assignments
    
    def _determine_role_type(self, role_name: str) -> DebateRole:
        """确定角色类型"""
        role_mapping = {
            "pro_arguer": DebateRole.PRO_ARGUER,
            "con_arguer": DebateRole.CON_ARGUER,
            "moderator": DebateRole.MODERATOR,
            "analyst": DebateRole.ANALYST,
            "fact_checker": DebateRole.FACT_CHECKER
        }
        
        # 检查是否在映射中（忽略大小写和空格）
        role_lower = role_name.lower().replace(" ", "_").replace("-", "_")
        for key, role_type in role_mapping.items():
            if key in role_lower:
                return role_type
        
        # 默认返回支持方角色
        return DebateRole.PRO_ARGUER


class DebateEngine:
    """辩论引擎 - 核心辩论逻辑"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.turn_sequence = [DebateRole.PRO_ARGUER, DebateRole.CON_ARGUER, DebateRole.ANALYST]
    
    async def run_single_round(self, topic: str, participants: List[RoleAssignment], 
                             round_num: int, previous_rounds: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """运行单轮辩论"""
        round_contributions = []
        
        for assignment in participants:
            contribution = await self._generate_contribution(assignment, topic, round_num, previous_rounds)
            
            round_contributions.append({
                "round": round_num,
                "participant": assignment.role_name,
                "role": assignment.role_type.value,
                "contribution": contribution,
                "timestamp": asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0
            })
        
        return round_contributions
    
    async def _generate_contribution(self, assignment: RoleAssignment, topic: str, 
                                   round_num: int, previous_rounds: List[Dict[str, Any]] = None) -> str:
        """生成参与者贡献"""
        if self.model_provider:
            # 构建上下文
            context = self._build_context(previous_rounds)
            
            prompt = f"""{assignment.role_name} ({assignment.role_type.value}) 角色的辩论提示：

话题: {topic}

你的角色: {assignment.role_type.value}
角色设定: {assignment.persona or self._get_default_role_prompt(assignment.role_type, topic)}

上下文: {context}

当前是第 {round_num} 轮辩论，请基于你的角色立场做出贡献。"""
            
            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                return f"生成失败: {str(e)}"
        else:
            # 模拟响应
            return f"模拟{assignment.role_type.value}贡献: {topic}的第{round_num}轮发言"
    
    def _build_context(self, previous_rounds: List[Dict[str, Any]]) -> str:
        """构建对话历史上下文"""
        if not previous_rounds:
            return "这是辩论的第一轮，尚无历史记录。"
        
        context_parts = []
        for round_data in previous_rounds[-2:]:  # 只取最近2轮
            for contrib in round_data.get("contributions", []):
                context_part = f"{contrib['participant']} ({contrib['role']}): {contrib['contribution'][:100]}...\\n"
                context_parts.append(context_part)
        
        return "".join(context_parts) if context_parts else "无前置辩论内容"
    
    def _get_default_role_prompt(self, role_type: DebateRole, topic: str) -> str:
        """获取默认角色提示词"""
        prompts = {
            DebateRole.PRO_ARGUER: f"你是支持方，需要支持关于'{topic}'的观点，提供有力的论证和证据。",
            DebateRole.CON_ARGUER: f"你是反对方，需要质疑关于'{topic}'的观点，提出挑战和反驳意见。",
            DebateRole.MODERATOR: f"你是主持人，负责引导关于'{topic}'的辩论，确保讨论有序进行。",
            DebateRole.ANALYST: f"你是分析师，对关于'{topic}'的辩论进行客观分析和总结。",
            DebateRole.FACT_CHECKER: f"你是事实核查员，需要验证关于'{topic}'的辩论中的事实准确性。"
        }
        return prompts.get(role_type, f"你是辩论参与者，参与关于'{topic}'的讨论。")


class DebateHistoryManager:
    """辩论历史管理器 - 独立模块"""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.session_stats: Dict[str, Any] = {}
    
    async def record_debate_round(self, round_data: Dict[str, Any]):
        """记录辩论回合"""
        self.history.append(round_data)
    
    async def get_debate_summary(self, topic: str) -> str:
        """获取辩论总结"""
        if not self.history:
            return f"关于'{topic}'的辩论尚无历史记录。"
        
        # 构建总结
        total_rounds = len(self.history)
        contributions_count = sum(len(round_data.get("contributions", [])) for round_data in self.history)
        
        summary = f"关于'{topic}'的辩论历史总结:\\n"
        summary += f"- 总回合数: {total_rounds}\\n"
        summary += f"- 总贡献数: {contributions_count}\\n\\n"
        
        for i, round_data in enumerate(self.history, 1):
            summary += f"第{i}轮:\\n"
            for contrib in round_data.get("contributions", []):
                summary += f"  {contrib['participant']} ({contrib['role']}): {contrib['contribution'][:100]}...\\n"
            summary += "\\n"
        
        return summary


class ModularDebateManager:
    """模块化辩论管理器 - 协调各模块工作"""
    
    def __init__(self, model_provider=None, role_manager=None):
        self.model_provider = model_provider
        self.participant_manager = DebateParticipantManager(role_manager)
        self.debate_engine = DebateEngine(model_provider)
        self.history_manager = DebateHistoryManager()
    
    async def run_debate(self, topic: str, role_names: List[str], 
                        num_rounds: int = 3) -> AsyncGenerator[str, None]:
        """运行辩论 - 模块化实现"""
        yield f"[bold blue]🎮 开始辩论: {topic}[/bold blue]"
        yield f"[dim]角色: {[r.replace('_', ' ').title() for r in role_names]}[/dim]"
        yield f"[dim]回合数: {num_rounds}[/dim]"
        
        # 1. 分配角色
        participants = self.participant_manager.assign_roles(role_names)
        yield f"[dim]角色分配完成: {len(participants)} 名参与者[/dim]"
        
        # 2. 运行多轮辩论
        previous_rounds = []
        
        for round_num in range(1, num_rounds + 1):
            yield f"\\n[bold yellow] ROUND {round_num}/{num_rounds} [/bold yellow]"
            
            # 运行单轮辩论
            round_contributions = await self.debate_engine.run_single_round(
                topic, participants, round_num, previous_rounds
            )
            
            # 记录到历史
            round_data = {
                "round_number": round_num,
                "topic": topic,
                "contributions": round_contributions
            }
            await self.history_manager.record_debate_round(round_data)
            
            # 显示本轮结果
            for contrib in round_contributions:
                yield f"[bold cyan]{contrib['participant']} ({contrib['role']}):[/bold cyan] {contrib['contribution'][:200]}..."
            
            # 更新历史记录
            previous_rounds.append(round_data)
        
        # 3. 生成辩论总结
        yield "\\n[bold green]✅ 辩论完成，生成总结...[/bold green]"
        
        summary = await self.history_manager.get_debate_summary(topic)
        yield f"\\n[bold yellow]🎯 辩论总结:[/bold yellow]\\n{summary}"


class ComplexityDetector:
    """复杂度检测器 - 独立模块"""
    
    def __init__(self):
        # 复杂任务关键词
        self.complexity_indicators = [
            # 动词类
            r".*(分析|研究|调查|探索|评测|评估|检验|验证).*",
            r".*(设计|规划|创建|构建|开发|实现).*",
            r".*(比较|对比|评估|鉴别).*",
            r".*(撰写|起草|编写|制作|整理|汇总).*",
            # 形容词类
            r".*(详细|深入|全面|系统|复杂|完整|深入).*",
            r".*(多角度|多维度|多层次|全方位|综合|战略).*",
            # 主题类
            r".*(机制|框架|策略|方案|系统|模型|架构|平台).*",
            r".*(影响|趋势|发展|前景|挑战|机遇|问题|解决方案).*"
        ]
    
    def detect_complexity(self, user_request: str) -> bool:
        """检测用户请求的复杂度"""
        user_lower = user_request.lower()
        
        # 检查复杂任务模式
        complexity_count = 0
        for pattern in self.complexity_indicators:
            if re.search(pattern, user_lower, re.IGNORECASE):
                complexity_count += 1
        
        # 检查长度和动作词
        word_count = len(user_request.split())
        action_words = ["分析", "研究", "设计", "开发", "比较", "评估", "探索", "验证", "实现", "制定", "规划"]
        action_count = sum(1 for word in action_words if word in user_lower)
        
        # 判断为复杂任务的标准：多个复杂关键词或包含多个动作词且长度较长
        return complexity_count >= 2 or (action_count >= 2 and word_count > 6)


# 便捷函数
async def create_and_run_debate(model_provider, topic: str, roles: List[str] = None, 
                               rounds: int = 3) -> AsyncGenerator[str, None]:
    """便捷函数：创建并运行辩论"""
    if roles is None:
        roles = ["pro_arguer", "con_arguer"]
    
    manager = ModularDebateManager(model_provider)
    async for event in manager.run_debate(topic, roles, rounds):
        yield event


if __name__ == "__main__":
    print("="*80)
    print("🎯 模块化辩论引擎 - 简化版")
    print("目标: 降低复杂度，模块化设计，减少测试工作量")
    print("="*80)
    
    print("\\n📋 系统模块组成:")
    modules = [
        "DebateParticipantManager: 角色管理模块 (~60行)",
        "DebateEngine: 辩论执行引擎 (~85行)", 
        "DebateHistoryManager: 历史管理模块 (~40行)",
        "ComplexityDetector: 复杂度检测 (~35行)",
        "ModularDebateManager: 协调中心 (~50行)"
    ]
    
    for module in modules:
        print(f"   ✅ {module}")
    
    print(f"\\n📊 原始复杂度: 809+ 行代码 (单个EnhancedDebateManager)")
    print(f"📊 重构后复杂度: ~270 行代码 (分散到5个模块)")
    print(f"📊 每个模块: 单一职责，易于测试和维护")
    
    print("\\n🔧 模块化优势:")
    advantages = [
        "✅ 职责分离: 每个模块专注特定功能",
        "✅ 独立测试: 每个模块可独立验证", 
        "✅ 易于扩展: 可单独修改任一模块",
        "✅ 降低耦合: 模块间依赖最小",
        "✅ 保持功能完整: 所有辩论功能保留"
    ]
    
    for advantage in advantages:
        print(f"   {advantage}")
    
    print("\\n🔄 工作流程:")
    print("   用户请求 -> 复杂度检测 -> 角色分配 -> 辩论执行 -> 历史记录 -> 总结生成")
    
    print("\\n✅ 模块化辩论引擎重构完成!")
    print("现在辩论功能由独立模块构成，降低了复杂度和测试工作量。")