"""
模块化辩论引擎 - 简化版
将复杂的辩论系统重构成模块化、可复用的组件
"""
import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
from dataclasses import dataclass
from enum import Enum


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
    
    def get_role_prompt(self, topic: str) -> str:
        """获取角色特定的提示词"""
        role_prompts = {
            DebateRole.PRO_ARGUER: f"您是支持方，支持关于'{topic}'的观点。请提供有力的论证和证据。",
            DebateRole.CON_ARGUER: f"您是反对方，质疑关于'{topic}'的观点。请提出挑战和反驳。",
            DebateRole.MODERATOR: f"您是主持人，负责引导关于'{topic}'的辩论，确保讨论有序进行。",
            DebateRole.ANALYST: f"您是分析师，对关于'{topic}'的辩论进行客观分析。",
            DebateRole.FACT_CHECKER: f"您是事实核查员，验证关于'{topic}'的辩论中的事实准确性。"
        }
        return role_prompts.get(self.role, f"您是辩论参与者，参与关于'{topic}'的讨论。")


@dataclass
class DebateRound:
    """辩论回合"""
    round_number: int
    topic: str
    participants: List[DebateParticipant]
    contributions: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.contributions is None:
            self.contributions = []


class SimpleDebateEngine:
    """
    简化版辩论引擎
    消除复杂依赖，保持核心功能
    """
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.active_debates: Dict[str, List[DebateRound]] = {}
    
    async def start_debate(self, topic: str, participants: List[DebateParticipant], 
                          rounds: int = 3) -> AsyncGenerator[str, None]:
        """启动辩论"""
        debate_id = f"debate_{len(self.active_debates) + 1}"
        
        # 添加到活动辩论
        self.active_debates[debate_id] = []
        
        yield f"[bold blue]🎮 辩论开始: {topic}[/bold blue]"
        yield f"[dim]参与者: {[p.name for p in participants]}[/dim]"
        yield f"[dim]回合数: {rounds}[/dim]"
        
        # 执行多轮辩论
        for round_num in range(1, rounds + 1):
            yield f"\\n[bold yellow] ROUND {round_num}/{rounds} [/bold yellow]"
            
            round_obj = DebateRound(round_number=round_num, topic=topic, participants=participants)
            
            # 每个参与者轮流发言
            for participant in participants:
                contribution = await self._generate_participant_contribution(participant, topic, round_num)
                
                round_obj.contributions.append({
                    "participant": participant.name,
                    "role": participant.role.value,
                    "contribution": contribution,
                    "round": round_num
                })
                
                yield f"[bold cyan]{participant.name} ({participant.role.value}):[/bold cyan] {contribution}"
            
            self.active_debates[debate_id].append(round_obj)
            
            yield f"[dim]--- 第 {round_num} 轮结束 ---[/dim]"
        
        # 生成总结
        summary = await self._generate_debate_summary(topic, self.active_debates[debate_id])
        yield f"\\n[bold green]🎯 辩论总结:[/bold green]\\n{summary}"
        
        # 移除活动辩论
        del self.active_debates[debate_id]
    
    async def _generate_participant_contribution(self, participant: DebateParticipant, 
                                               topic: str, round_num: int) -> str:
        """生成参与者贡献"""
        if self.model_provider:
            prompt = f"""{participant.get_role_prompt(topic)}

当前是第 {round_num} 轮辩论。

请基于您的角色立场，就上述话题发表观点或回应其他参与者。"""
            
            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                return f"[{participant.role.value}角色] 生成内容失败: {e}"
        else:
            # 模拟响应
            return f"模拟{participant.role.value}贡献: 这是关于{topic}的第{round_num}轮发言"
    
    async def _generate_debate_summary(self, topic: str, 
                                     debate_rounds: List[DebateRound]) -> str:
        """生成辩论总结"""
        if self.model_provider:
            # 构建辩论历史
            history_parts = []
            for round_obj in debate_rounds:
                history_parts.append(f"第{round_obj.round_number}轮:")
                for contrib in round_obj.contributions:
                    history_parts.append(f"  {contrib['participant']}: {contrib['contribution'][:100]}...")
            
            history = "\\n".join(history_parts)
            
            prompt = f"""根据以下辩论历史，生成对关于"{topic}"的辩论的总结。

辩论历史:
{history}

请提供一个客观、全面的总结，包括各方观点和主要论据。"""
            
            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except:
                # 返回基本总结
                pass
        
        # 默认总结
        total_contributions = sum(len(round.contributions) for round in debate_rounds)
        return f"关于'{topic}'的辩论已完成。共进行了{len(debate_rounds)}轮，{total_contributions}次发言。"


class DebateModule:
    """
    模块化的辩论功能
    可独立使用或集成到其他系统中
    """
    
    def __init__(self, model_provider=None):
        self.engine = SimpleDebateEngine(model_provider)
    
    async def run_simple_debate(self, topic: str, roles: List[str] = None, 
                               rounds: int = 3) -> AsyncGenerator[str, None]:
        """运行简化辩论"""
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
            role_enum = role_mapping.get(role_name.lower(), DebateRole.PRO_ARGUER)
            participant = DebateParticipant(
                name=role_name.replace('_', ' ').title(),
                role=role_enum
            )
            participants.append(participant)
        
        # 运行辩论
        async for event in self.engine.start_debate(topic, participants, rounds):
            yield event


# 便捷的辩论启动函数
async def create_and_run_debate(model_provider, topic: str, roles: List[str] = None, rounds: int = 3):
    """便捷函数：创建并运行辩论"""
    debate_module = DebateModule(model_provider)
    async for event in debate_module.run_simple_debate(topic, roles, rounds):
        yield event


if __name__ == "__main__":
    print("="*80)
    print("🎯 模块化辩论引擎 - 简化版实现")
    print("="*80)
    
    print("\\n📋 简化版辩论引擎特性:")
    print("  ✅ 独立模块，无复杂依赖")
    print("  ✅ 支持多角色辩论")
    print("  ✅ 模块化设计，易于集成")
    print("  ✅ 简化API，易于使用")
    print("  ✅ 支持多轮辩论")
    print("  ✅ 自动生成总结")
    
    # 模拟测试
    async def mock_test():
        class MockModelProvider:
            async def generate(self, prompt: str):
                return f"模拟回复: {prompt[:100]}..."
        
        print("\\n🧪 生成一个简化辩论示例:")
        debate_module = DebateModule(MockModelProvider())
        
        counter = 0
        async for event in debate_module.run_simple_debate("人工智能的伦理影响", ["pro_arguer", "con_arguer", "analyst"], 2):
            counter += 1
            print(f"  事件 {counter}: {event[:100]}...{'...' if len(event) > 100 else ''}")
            if counter >= 10:  # 限制输出
                print("  ...")
                break
    
    asyncio.run(mock_test())
    
    print("\\n✅ 简化版模块化辩论引擎创建成功!")
    print("现在可以轻松集成到任何系统中，复杂度大幅降低。")