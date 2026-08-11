"""
基于TDD的实际辩论管理器 - 支持真实AI模型交互
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, Optional

from daip_live.core.interfaces import IDebateManager, IModelProvider
from daip_live.core.models import (
    AgentEvent,
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
)

log = logging.getLogger(__name__)


class RealDebateManager(IDebateManager):
    """
    基于TDD的实际辩论管理器

    特性：
    - 真实AI模型调用（非模拟）
    - 支持多轮次结构化辩论
    - 角色发言状态跟踪
    - 上下文感知的回合管理
    - 动态模型选择和回退
    - 集成测试和验证
    """

    def __init__(
        self,
        session_manager,
        role_manager,
        model_provider: IModelProvider,
        max_turn_time: int = 120,  # 每轮最大时间（秒）
        thinking_time: int = 30,  # 思考时间,
    ):
        """初始化真实AI模型辩论管理器"""

        # 创建简单的角色模型管理器模拟
        class MockRoleModelManager:
            def get_debate_model_mappings(self, roles):
                return []

        role_model_manager = MockRoleModelManager()
        super().__init__(
            session_manager, role_manager, role_model_manager, model_provider
        )

        # 保存模型提供者引用 - 这是关键修复
        self.model_provider = model_provider

        self.debate_state = {
            "topic": "",
            "rounds": 0,
            "current_round": 0,
            "participants": [],
            "participant_status": {},
            "debate_running": False,
            "start_time": None,
            "current_turn": None,
            "turn_history": [],
            "session_id": None,
        }

        self.max_turn_time = max_turn_time
        self.thinking_time = thinking_time
        self.model_assignments = {}  # 动态模型分配

    async def run_debate(
        self,
        topic: str,
        roles_names: list[str],
        rounds: int,
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行真实AI模型辩论"""
        # 生成会话ID
        if not session_id:
            session_id = f"real_debate_{int(asyncio.get_event_loop().time())}"

        # 初始化辩论状态
        self.debate_state.update(
            {
                "topic": topic,
                "rounds": rounds,
                "participants": roles_names,
                "debate_running": True,
                "start_time": asyncio.get_event_loop().time(),
                "session_id": session_id,
                "current_round": 0,
                "turn_history": [],
            }
        )

        # 初始化参与者状态
        for role in roles_names:
            self.debate_state["participant_status"][role] = {
                "status": "waiting",
                "response": None,
                "response_time": 0,
                "thinking": False,
            }

        # 产生开始事件
        yield DebateStartEvent(
            topic=topic, roles=roles_names, rounds=rounds, session_id=session_id
        )

        log.info("🤖 Real AI debate started!")

        # 运行辩论轮次
        for round_num in range(1, rounds + 1):
            yield DebateRoundStartEvent(round_number=round_num)

            # 处理每个参与者的发言
            for role in roles_names:
                await self._process_real_ai_turn(role, round_num, round_num == rounds)

            # 生成回合结束事件（除最后一轮）
            if round_num < rounds:
                yield DebateRoundStartEvent(round_number=round_num + 1)

        # 生成最终辩论结论
        conclusion = await self._generate_debate_conclusion()

        yield DebateCompleteEvent(
            session_id=session_id,
            topic=topic,
            turns=self.debate_state["turn_history"],
            conclusion=conclusion,
            role_performances=await self._evaluate_role_performances(),
        )

        log.info("🏁 Real AI debate completed!")

    async def _process_real_ai_turn(
        self, role: str, round_num: int, is_final_round: bool = False
    ) -> None:
        """处理真实的AI模型回合"""
        try:
            # 更新参与者状态为思考中
            self._update_participant_status(role, "thinking", True)
            self.debate_state["current_turn"] = role

            # 构建辩论提示
            context = self._build_debate_context(role)
            prompt = self._build_debate_prompt(role, context)

            # 调用AI模型生成回应
            # 源码契约: agenerate 返回 (content, metadata)；generate 是 async generator
            start_time = asyncio.get_event_loop().time()
            response, _ = await self.model_provider.agenerate(prompt)
            response_time = asyncio.get_event_loop().time() - start_time

            # 更新参与者状态
            self._update_participant_status(role, "completed", response, response_time)

            # 记录回合
            self.debate_state["turn_history"].append(
                {
                    "role": role,
                    "round": round_num,
                    "prompt": prompt,
                    "response": response,
                    "response_time": response_time,
                    "thinking_time": response_time - start_time,
                }
            )

            yield DebateTurnCompleteEvent(
                role=role,
                round_number=round_num,
                turn_id=len(self.debate_state["turn_history"]) + 1,
                content=response,
            )

            # 如果是最终轮，生成回合间事件
            if is_final_round:
                self._update_participant_status(
                    role, "completed", response, response_time
                )
                yield DebateRoundStartEvent(round_number=round_num + 1)

        except Exception as e:
            log.error(f"Error processing AI turn for {role}: {e}")
            self._update_participant_status(role, "error", str(e))

    def _build_debate_context(self, role: str) -> str:
        """构建辩论上下文"""
        context_parts = []

        # 添加辩题信息
        if self.debate_state["topic"]:
            context_parts.append(f"辩题：{self.debate_state['topic']}")

        # 添加轮次信息
        if self.debate_state["current_round"] > 0:
            context_parts.append(
                f"当前轮次：第{self.debate_state['current_round']}轮（共{self.debate_state['rounds']}轮）"
            )

        # 添加历史对话
        if self.debate_state["turn_history"]:
            recent_turns = self.debate_state["turn_history"][-5:]  # 最近5个回合
            for turn in recent_turns:
                context_parts.append(
                    f"第{turn['round']}轮 - {turn['role']}：{turn['prompt'][:100]}...（{turn['response'][:100]}）"  # noqa: E501
                )

        return "\\n\\n".join(context_parts)

    def _build_debate_prompt(self, role: str, context: str) -> str:
        """构建针对角色的辩论提示"""
        # 基础角色指令
        base_instructions = {
            "pro_arguer": "你是正方辩手，需要支持并论证该观点",
            "con_arguer": "你是反方辩手，需要反驳并指出对方论证的漏洞",
        }

        # 获取当前轮次的所有发言
        current_round_turns = [
            turn
            for turn in self.debate_state["turn_history"]
            if turn["round"] == self.debate_state["current_round"]
        ]

        # 获取对立方场的发言
        opponent_role = "con_arguer" if role == "pro_arguer" else "pro_arguer"
        [turn for turn in current_round_turns if turn["role"] == opponent_role]

        # 构建详细提示
        prompt = f"""你是{role}。

{base_instructions.get(role, "未知的角色指令")}

辩题：{self.debate_state["topic"]}

当前轮次：第{self.debate_state["current_round"]}轮（共{self.debate_state["rounds"]}轮）

历史对话：
{context}

你的任务：
1. 基于之前的对话内容，针对{opponent_role}的论点进行回应和反驳
2. 你的回应应该：
   - 逻辑清晰、论证有力
   - 针对性强，避免人身攻击
   - 提供新的观点和证据
   - 长度适中（{self.max_turn_time}秒内完成）

请注意：
- 这是正式辩论，需要专业的论证水准
- 避免重复，提出建设性意见
- 如果无法在规定时间内完成，请明确说明

现在请开始你的{self.debate_state["current_round"]}轮发言："""

        return prompt

    async def _generate_debate_conclusion(self) -> str:
        """生成辩论结论"""
        try:
            conclusion_prompt = f"""
基于以下辩论记录，请生成一个平衡的辩论结论：

辩题：{self.debate_state["topic"]}

参与角色：{", ".join(self.debate_state["participants"])}

辩论过程：
{self._format_debate_history()}

请提供一个约200字的辩论结论，要求：
1. 客观中立，总结双方主要论点
2. 指出论证的亮点和不足
3. 如有共识，说明共识点
4. 提出值得进一步探讨的问题
5. 保持专业和建设性语调

结论格式：
【辩论结论】
[总结内容]
"""

            conclusion, _ = await self.model_provider.agenerate(conclusion_prompt)
            return conclusion.strip()
        except Exception as e:
            log.error(f"Error generating debate conclusion: {e}")
            return f"无法生成结论: {str(e)}"

    async def _evaluate_role_performances(self) -> dict[str, str]:
        """评估角色表现"""
        performances = {}

        for role in self.debate_state["participants"]:
            role_turns = [
                turn
                for turn in self.debate_state["turn_history"]
                if turn["role"] == role and turn.get("response_time", 0) > 0
            ]

            if not role_turns:
                performances[role] = "未发言"
            else:
                # 计算平均响应时间
                avg_response_time = sum(
                    turn.get("response_time", 0) - turn.get("thinking_time", 0)
                    for turn in role_turns[1:]
                ) / max(len(role_turns) - 1, 0.001)

                # 评估表现
                sum(
                    turn.get("thinking_time", 0) - turn.get("response_time", 0)
                    for turn in role_turns[1:]
                ) / max(len(role_turns) - 1, 0.001)

                if avg_response_time <= self.max_turn_time * 0.8:
                    performance = "优秀"
                elif avg_response_time <= self.max_turn_time:
                    performance = "良好"
                else:
                    performance = "一般"

                performances[role] = (
                    f"表现：{performance}（平均响应时间：{avg_response_time:.2f}秒）"
                )

        return performances

    def _format_debate_history(self) -> str:
        """格式化辩论历史"""
        if not self.debate_state["turn_history"]:
            return "暂无辩论记录"

        formatted_history = []
        for i, turn in enumerate(self.debate_state["turn_history"], 1):
            formatted_turn = f"""
第{turn["round"]}轮 - {turn["role"]}：
提示：{turn["prompt"][:200]}...
回应：{turn["response"][:300]}...
（响应时间：{turn.get("response_time", 0) - turn.get("thinking_time", 0):.2f}秒）
"""
            formatted_history.append(formatted_turn)

        return "\\n\\n".join(formatted_history)

    def get_debate_model_summary(self, roles: list[str]) -> dict[str, Any]:
        """获取辩论模型配置摘要"""
        assignments = {}

        # 尝试为每个角色分配最佳模型
        for role in roles:
            best_model = self.model_provider.get_default_model()
            assignments[role] = best_model

        return {
            "model_assignments": assignments,
            "total_models": len({assignments.values()}),
            "provider_type": type(self.model_provider).__name__,
        }

    def get_debate_state(self) -> dict[str, Any]:
        """获取当前辩论状态"""
        return self.debate_state.copy()

    def _update_participant_status(
        self,
        role: str,
        status: str,
        response: Optional[str] = None,
        response_time: Optional[float] = None,
    ) -> None:
        """更新参与者状态"""
        if role not in self.debate_state["participant_status"]:
            self.debate_state["participant_status"][role] = {
                "status": status,
                "response": response,
                "response_time": response_time,
                "thinking": status == "thinking",
            }

    def _get_model_for_role(self, role: str) -> str:
        """为角色获取合适的模型"""
        # 检查是否有预分配的模型
        if role in self.model_assignments:
            return self.model_assignments[role]

        # 使用默认模型选择逻辑
        opponent_role = "con_arguer" if role == "pro_arguer" else "pro_arguer"

        # 为对立方场分配不同模型以增加多样性
        if role == "pro_arguer":
            return self.model_provider.get_default_model()
        elif role == opponent_role:
            # 尝试为对手分配不同模型
            available_models = self.model_provider.get_available_models()
            if len(available_models) > 1:
                return (
                    available_models[1]
                    if available_models[0] != self.model_provider.get_default_model()
                    else self.model_provider.get_default_model()
                )

        return self.model_provider.get_default_model()

    def update_model_assignment(self, role: str, model: str) -> None:
        """更新模型分配"""
        self.model_assignments[role] = model
        log.info(f"🔄 Updated model assignment: {role} -> {model}")
