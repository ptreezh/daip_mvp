"""真实多角色聊天系统
支持从角色库动态加载，调用真实大模型，智能推荐角色
"""

import asyncio
import hashlib
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import requests

from src.chat_config import (
    DEFAULT_CHAT_MODEL,
    get_chat_model_config,
    get_prompt_template,
    get_recommendation_config,
    get_system_config,
)
from src.expert_library import ExpertLibrary


@dataclass
class ChatMessage:
    """聊天消息"""

    id: str
    role_id: str
    role_name: str
    content: str
    timestamp: str
    message_type: str = "text"  # text, system, action
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChatParticipant:
    """聊天参与者"""

    role_id: str
    role_name: str
    role_data: dict[str, Any]
    is_active: bool = True
    last_activity: Optional[str] = None
    message_count: int = 0

    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now().isoformat()


@dataclass
class ChatRoom:
    """聊天室"""

    room_id: str
    room_name: str
    topic: str
    participants: list[ChatParticipant]
    messages: list[ChatMessage]
    created_at: str
    last_activity: str
    is_active: bool = True
    room_config: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.room_config is None:
            self.room_config = {}


class ModelInterface:
    """大模型接口"""

    def __init__(self, model_type: str = DEFAULT_CHAT_MODEL):
        self.model_type = model_type
        self.config = get_chat_model_config(model_type)
        self.logger = logging.getLogger(__name__)

    async def generate_response(
        self,
        prompt: str,
        role_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """生成角色响应"""
        try:
            if self.config["api_type"] == "ollama":
                return await self._call_ollama(prompt, role_context)
            elif self.config["api_type"] == "openai":
                return await self._call_openai(prompt, role_context)
            elif self.config["api_type"] == "anthropic":
                return await self._call_anthropic(prompt, role_context)
            else:
                raise ValueError(f"Unsupported API type: {self.config['api_type']}")
        except Exception as e:
            self.logger.error(f"Model generation failed: {e}")
            return f"[系统消息] 角色响应生成失败: {e!s}"

    async def _call_ollama(
        self,
        prompt: str,
        role_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """调用Ollama模型"""
        try:
            import aiohttp

            payload = {
                "model": self.config["model_name"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config["temperature"],
                    "num_predict": self.config["max_tokens"],
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['base_url']}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config["timeout"]),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "").strip()
                    else:
                        error_text = await response.text()
                        self.logger.warning(
                            f"Ollama API error: {response.status} - {error_text}",
                        )
                        # 优雅降级到同步调用
                        return self._call_ollama_sync(prompt)

        except Exception as e:
            self.logger.warning(f"Ollama async call failed: {e}")
            # 同步备用调用
            return self._call_ollama_sync(prompt)

    def _call_ollama_sync(self, prompt: str) -> str:
        """同步调用Ollama（备用方案）"""
        try:
            payload = {
                "model": self.config["model_name"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config["temperature"],
                    "num_predict": self.config["max_tokens"],
                },
            }

            response = requests.post(
                f"{self.config['base_url']}/api/generate",
                json=payload,
                timeout=self.config["timeout"],
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                self.logger.warning(f"Ollama sync API error: {response.status_code}")
                return "[角色暂时无法响应，请稍后再试]"

        except Exception as e:
            self.logger.error(f"Ollama sync call failed: {e}")
            return "[角色暂时无法响应，请稍后再试]"

    async def _call_openai(
        self,
        prompt: str,
        role_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """调用OpenAI模型"""
        try:
            import openai
            from openai.types.chat import ChatCompletionMessageParam

            client = openai.AsyncOpenAI(api_key=self.config["api_key"])

            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]

            response = await client.chat.completions.create(
                model=self.config["model_name"],
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                timeout=self.config["timeout"],
            )

            content = response.choices[0].message.content
            return content.strip() if content else ""

        except Exception as e:
            self.logger.error(f"OpenAI call failed: {e}")
            return f"[OpenAI模型暂时不可用: {e!s}]"

    async def _call_anthropic(
        self,
        prompt: str,
        role_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """调用Anthropic模型"""
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=self.config["api_key"])

            response = await client.messages.create(
                model=self.config["model_name"],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                messages=[{"role": "user", "content": prompt}],
            )

            text = ""
            if response.content and isinstance(response.content, list):
                first = response.content[0]
                text_val = getattr(first, "text", None)
                if isinstance(text_val, str):
                    text = text_val
            return text.strip()

        except Exception as e:
            self.logger.error(f"Anthropic call failed: {e}")
            return f"[Claude模型暂时不可用: {e!s}]"


class RoleRecommendationEngine:
    """角色推荐引擎"""

    def __init__(self, expert_library: ExpertLibrary):
        self.expert_library = expert_library
        self.config = get_recommendation_config()
        self.recent_roles = []  # 最近使用的角色

    def recommend_roles(
        self,
        topic: str,
        current_participants: Optional[list[str]] = None,
        desired_expertise: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """推荐合适的角色"""
        if current_participants is None:
            current_participants = []
        if desired_expertise is None:
            desired_expertise = []

        # 获取所有专家
        all_experts = self.expert_library.get_all_experts()

        # 过滤已参与的角色
        available_experts = [
            expert for expert in all_experts if expert["id"] not in current_participants
        ]

        # 排除最近使用的角色
        if self.config["exclude_recent_roles"]:
            available_experts = [
                expert
                for expert in available_experts
                if expert["id"]
                not in self.recent_roles[-self.config["recent_roles_window"] :]
            ]

        if not available_experts:
            return []

        # 计算推荐分数
        scored_experts = []
        for expert in available_experts:
            score = self._calculate_recommendation_score(
                expert,
                topic,
                desired_expertise,
            )
            scored_experts.append((expert, score))

        # 排序并选择top推荐
        scored_experts.sort(key=lambda x: x[1], reverse=True)

        # 应用多样性过滤
        recommended = self._apply_diversity_filter(scored_experts)

        # 限制推荐数量
        count = min(self.config["recommendation_count"], len(recommended))
        final_recommendations = recommended[:count]

        return [expert for expert, score in final_recommendations]

    def _calculate_recommendation_score(
        self,
        expert: dict[str, Any],
        topic: str,
        desired_expertise: Optional[list[str]],
    ) -> float:
        """计算推荐分数"""
        score = 0.0

        # 相关性分数
        relevance_score = self._calculate_relevance_score(
            expert,
            topic,
            desired_expertise,
        )
        score += relevance_score * self.config["relevance_weight"]

        # 热门度分数（基于声誉）
        popularity_score = expert["reputation_score"] / 100.0
        score += popularity_score * self.config["popularity_weight"]

        # 新颖性分数（基于使用频率）
        novelty_score = self._calculate_novelty_score(expert)
        score += novelty_score * self.config["novelty_weight"]

        return score

    def _calculate_relevance_score(
        self,
        expert: dict[str, Any],
        topic: str,
        desired_expertise: Optional[list[str]],
    ) -> float:
        """计算相关性分数"""
        score = 0.0

        # 检查专业领域匹配
        specialties = expert.get("specialties", [])
        skills = expert.get("skills", [])
        description = expert.get("description", "")
        bio = expert.get("bio", "")

        # 主题相关性
        topic_words = topic.lower().split()
        all_expert_text = " ".join(specialties + skills + [description, bio]).lower()

        topic_matches = sum(1 for word in topic_words if word in all_expert_text)
        if topic_words:
            score += (topic_matches / len(topic_words)) * 0.5

        # 期望专业领域匹配
        if desired_expertise:
            expertise_matches = 0
            for expertise in desired_expertise:
                expertise_lower = expertise.lower()
                if any(expertise_lower in spec.lower() for spec in specialties):
                    expertise_matches += 1
                elif any(expertise_lower in skill.lower() for skill in skills):
                    expertise_matches += 0.8
                elif expertise_lower in all_expert_text:
                    expertise_matches += 0.5

            score += (expertise_matches / len(desired_expertise)) * 0.5

        return min(score, 1.0)

    def _calculate_novelty_score(self, expert: dict[str, Any]) -> float:
        """计算新颖性分数"""
        expert_id = expert["id"]

        # 基于最近使用频率计算新颖性
        recent_usage = self.recent_roles.count(expert_id)
        max_usage = max(
            [self.recent_roles.count(eid) for eid in set(self.recent_roles)],
            default=1,
        )

        if max_usage == 0:
            return 1.0

        novelty = 1.0 - (recent_usage / max_usage)
        return novelty

    def _apply_diversity_filter(
        self,
        scored_experts: list[tuple[dict[str, Any], float]],
    ) -> list[tuple[dict[str, Any], float]]:
        """应用多样性过滤"""
        if not scored_experts:
            return []

        selected = []
        remaining = scored_experts.copy()

        # 选择第一个（分数最高的）
        selected.append(remaining.pop(0))

        while remaining and len(selected) < self.config["recommendation_count"]:
            best_candidate = None
            best_diversity_score = -1
            best_index = -1

            for i, (candidate, score) in enumerate(remaining):
                # 计算与已选择角色的多样性
                diversity = self._calculate_diversity(
                    candidate,
                    [s[0] for s in selected],
                )

                # 综合分数 = 原始分数 * (1 + 多样性因子 * 多样性分数)
                combined_score = score * (
                    1 + self.config["diversity_factor"] * diversity
                )

                if combined_score > best_diversity_score:
                    best_diversity_score = combined_score
                    best_candidate = (candidate, score)
                    best_index = i

            if best_candidate:
                selected.append(best_candidate)
                remaining.pop(best_index)

        return selected

    def _calculate_diversity(
        self,
        candidate: dict[str, Any],
        selected: list[dict[str, Any]],
    ) -> float:
        """计算多样性分数"""
        if not selected:
            return 1.0

        candidate_category = candidate.get("category", "")
        candidate_specialties = set(candidate.get("specialties", []))

        diversity_scores = []

        for selected_expert in selected:
            selected_category = selected_expert.get("category", "")
            selected_specialties = set(selected_expert.get("specialties", []))

            # 分类多样性
            category_diversity = 1.0 if candidate_category != selected_category else 0.3

            # 专业领域多样性
            if candidate_specialties and selected_specialties:
                overlap = len(candidate_specialties & selected_specialties)
                total = len(candidate_specialties | selected_specialties)
                specialty_diversity = 1.0 - (overlap / total) if total > 0 else 0.0
            else:
                specialty_diversity = 1.0

            # 综合多样性
            diversity = (category_diversity + specialty_diversity) / 2
            diversity_scores.append(diversity)

        # 返回平均多样性
        return sum(diversity_scores) / len(diversity_scores)

    def add_recent_role(self, role_id: str):
        """添加最近使用的角色"""
        self.recent_roles.append(role_id)

        # 限制历史长度
        max_history = self.config["recent_roles_window"] * 3
        if len(self.recent_roles) > max_history:
            self.recent_roles = self.recent_roles[-max_history:]

    def get_random_roles(
        self,
        count: int = 6,
        category: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """随机获取角色"""
        if category:
            experts = self.expert_library.get_experts_by_category(category)
        else:
            experts = self.expert_library.get_all_experts()

        if not experts:
            return []

        # 随机选择
        selected_count = min(count, len(experts))
        return random.sample(experts, selected_count)


class MultiRoleChatEngine:
    """多角色聊天引擎"""

    def __init__(
        self,
        expert_library: ExpertLibrary,
        model_type: str = DEFAULT_CHAT_MODEL,
    ):
        self.expert_library = expert_library
        self.model_interface = ModelInterface(model_type)
        self.recommendation_engine = RoleRecommendationEngine(expert_library)
        self.chat_rooms: dict[str, ChatRoom] = {}
        self.system_config = get_system_config()
        self.logger = logging.getLogger(__name__)

        # 初始化线程池
        self.executor = ThreadPoolExecutor(max_workers=8)

    def create_chat_room(
        self,
        room_name: str,
        topic: str,
        initial_participants: Optional[list[str]] = None,
    ) -> str:
        """创建聊天室"""
        room_id = hashlib.md5(
            f"{room_name}_{topic}_{time.time()}".encode(),
        ).hexdigest()[:16]

        participants = []
        if initial_participants:
            for role_id in initial_participants:
                expert = self.expert_library.get_expert_by_id(role_id)
                if expert:
                    participant = ChatParticipant(
                        role_id=role_id,
                        role_name=expert["name"],
                        role_data=expert,
                    )
                    participants.append(participant)

        chat_room = ChatRoom(
            room_id=room_id,
            room_name=room_name,
            topic=topic,
            participants=participants,
            messages=[],
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
        )

        self.chat_rooms[room_id] = chat_room

        # 添加系统消息
        system_message = ChatMessage(
            id=self._generate_message_id(),
            role_id="system",
            role_name="系统",
            content=f"聊天室 '{room_name}' 已创建，讨论主题：{topic}",
            timestamp=datetime.now().isoformat(),
            message_type="system",
        )
        chat_room.messages.append(system_message)

        self.logger.info(f"Created chat room: {room_id} - {room_name}")
        return room_id

    def add_participant(self, room_id: str, role_id: str) -> bool:
        """添加参与者到聊天室"""
        if room_id not in self.chat_rooms:
            return False

        chat_room = self.chat_rooms[room_id]

        # 检查是否已经参与
        if any(p.role_id == role_id for p in chat_room.participants):
            return False

        # 检查参与者数量限制
        max_participants = self.system_config.get("max_concurrent_roles", 8)
        if len(chat_room.participants) >= max_participants:
            return False

        expert = self.expert_library.get_expert_by_id(role_id)
        if not expert:
            return False

        participant = ChatParticipant(
            role_id=role_id,
            role_name=expert["name"],
            role_data=expert,
        )

        chat_room.participants.append(participant)
        chat_room.last_activity = datetime.now().isoformat()

        # 添加加入消息
        join_message = ChatMessage(
            id=self._generate_message_id(),
            role_id="system",
            role_name="系统",
            content=f"{expert['name']} ({expert['title']}) 加入了聊天",
            timestamp=datetime.now().isoformat(),
            message_type="system",
        )
        chat_room.messages.append(join_message)

        # 记录到推荐引擎
        self.recommendation_engine.add_recent_role(role_id)

        return True

    def remove_participant(self, room_id: str, role_id: str) -> bool:
        """移除参与者"""
        if room_id not in self.chat_rooms:
            return False

        chat_room = self.chat_rooms[room_id]

        # 查找并移除参与者
        for i, participant in enumerate(chat_room.participants):
            if participant.role_id == role_id:
                removed_participant = chat_room.participants.pop(i)

                # 添加离开消息
                leave_message = ChatMessage(
                    id=self._generate_message_id(),
                    role_id="system",
                    role_name="系统",
                    content=f"{removed_participant.role_name} 离开了聊天",
                    timestamp=datetime.now().isoformat(),
                    message_type="system",
                )
                chat_room.messages.append(leave_message)
                chat_room.last_activity = datetime.now().isoformat()

                return True

        return False

    async def send_user_message(
        self,
        room_id: str,
        content: str,
        sender_name: str = "用户",
    ) -> bool:
        """发送用户消息"""
        if room_id not in self.chat_rooms:
            return False

        chat_room = self.chat_rooms[room_id]

        # 创建用户消息
        user_message = ChatMessage(
            id=self._generate_message_id(),
            role_id="user",
            role_name=sender_name,
            content=content,
            timestamp=datetime.now().isoformat(),
            message_type="text",
        )

        chat_room.messages.append(user_message)
        chat_room.last_activity = datetime.now().isoformat()

        # 限制消息历史长度
        max_history = self.system_config.get("max_history_length", 50)
        if len(chat_room.messages) > max_history:
            # 保留系统消息和最近的消息
            system_messages = [
                msg for msg in chat_room.messages if msg.message_type == "system"
            ]
            recent_messages = [
                msg for msg in chat_room.messages if msg.message_type != "system"
            ][-max_history:]
            chat_room.messages = system_messages + recent_messages

        return True

    async def generate_role_responses(
        self,
        room_id: str,
        target_roles: Optional[list[str]] = None,
    ) -> list[ChatMessage]:
        """生成角色响应"""
        if room_id not in self.chat_rooms:
            return []

        chat_room = self.chat_rooms[room_id]

        # 确定响应的角色
        if target_roles:
            responding_participants = [
                p
                for p in chat_room.participants
                if p.role_id in target_roles and p.is_active
            ]
        else:
            # 随机选择1-3个活跃角色响应
            active_participants = [p for p in chat_room.participants if p.is_active]
            response_count = min(random.randint(1, 3), len(active_participants))
            responding_participants = random.sample(active_participants, response_count)

        if not responding_participants:
            return []

        # 并发生成响应
        response_tasks = []
        for participant in responding_participants:
            task = self._generate_single_role_response(chat_room, participant)
            response_tasks.append(task)

        # 等待所有响应完成
        responses = []
        try:
            completed_responses = await asyncio.gather(
                *response_tasks,
                return_exceptions=True,
            )

            for i, response in enumerate(completed_responses):
                if isinstance(response, ChatMessage):
                    responses.append(response)
                    chat_room.messages.append(response)

                    # 更新参与者活动
                    responding_participants[
                        i
                    ].last_activity = datetime.now().isoformat()
                    responding_participants[i].message_count += 1
                elif isinstance(response, Exception):
                    self.logger.error(f"Role response generation failed: {response}")

        except Exception as e:
            self.logger.error(f"Failed to generate role responses: {e}")

        chat_room.last_activity = datetime.now().isoformat()
        return responses

    async def _generate_single_role_response(
        self,
        chat_room: ChatRoom,
        participant: ChatParticipant,
    ) -> ChatMessage:
        """生成单个角色的响应"""
        try:
            # 构建角色提示词
            prompt = self._build_role_prompt(chat_room, participant)

            # 调用模型生成响应
            response_content = await self.model_interface.generate_response(
                prompt,
                participant.role_data,
            )

            # 创建响应消息
            response_message = ChatMessage(
                id=self._generate_message_id(),
                role_id=participant.role_id,
                role_name=participant.role_name,
                content=response_content,
                timestamp=datetime.now().isoformat(),
                message_type="text",
                metadata={
                    "model_type": self.model_interface.model_type,
                    "role_category": participant.role_data.get("category", ""),
                    "generation_time": datetime.now().isoformat(),
                },
            )

            return response_message

        except Exception as e:
            self.logger.error(
                f"Failed to generate response for {participant.role_name}: {e}",
            )

            # 返回错误消息
            error_message = ChatMessage(
                id=self._generate_message_id(),
                role_id=participant.role_id,
                role_name=participant.role_name,
                content="[抱歉，我暂时无法回应，请稍后再试]",
                timestamp=datetime.now().isoformat(),
                message_type="text",
                metadata={"error": str(e)},
            )

            return error_message

    def _build_role_prompt(
        self,
        chat_room: ChatRoom,
        participant: ChatParticipant,
    ) -> str:
        """构建角色提示词"""
        role_data = participant.role_data

        # 获取聊天历史
        recent_messages = chat_room.messages[-10:]  # 最近10条消息
        chat_history = []

        for msg in recent_messages:
            if msg.message_type == "text":
                chat_history.append(f"{msg.role_name}: {msg.content}")

        chat_history_text = "\n".join(chat_history) if chat_history else "对话刚开始"

        # 获取其他参与者信息
        other_participants = [
            f"{p.role_name} ({p.role_data.get('title', '')})"
            for p in chat_room.participants
            if p.role_id != participant.role_id
        ]
        participants_text = (
            ", ".join(other_participants) if other_participants else "无其他参与者"
        )

        # 构建系统提示词
        system_prompt = get_prompt_template("role_system_prompt").format(
            role_name=role_data.get("name", "专家"),
            role_description=role_data.get("description", "专业人士"),
            specialties=", ".join(role_data.get("specialties", [])),
            skills=", ".join(role_data.get("skills", [])),
            experience_years=role_data.get("experience_years", 0),
            bio=role_data.get("bio", ""),
            context=f"讨论主题：{chat_room.topic}\n参与者：{participants_text}\n最近对话：\n{chat_history_text}",
        )

        return system_prompt

    def get_room_recommendations(
        self,
        room_id: str,
        count: int = 6,
    ) -> list[dict[str, Any]]:
        """获取聊天室角色推荐"""
        if room_id not in self.chat_rooms:
            return []

        chat_room = self.chat_rooms[room_id]
        current_participants = [p.role_id for p in chat_room.participants]

        # 基于主题推荐角色
        recommendations = self.recommendation_engine.recommend_roles(
            topic=chat_room.topic,
            current_participants=current_participants,
        )

        return recommendations[:count]

    def get_random_recommendations(
        self,
        count: int = 6,
        category: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """获取随机角色推荐"""
        return self.recommendation_engine.get_random_roles(count, category)

    def get_chat_room(self, room_id: Optional[str]) -> Optional[ChatRoom]:
        """获取聊天室信息"""
        if room_id is None:
            return None
        return self.chat_rooms.get(room_id)

    def get_all_rooms(self) -> list[ChatRoom]:
        """获取所有聊天室"""
        return list(self.chat_rooms.values())

    def delete_chat_room(self, room_id: str) -> bool:
        """删除聊天室"""
        if room_id in self.chat_rooms:
            del self.chat_rooms[room_id]
            return True
        return False

    def _generate_message_id(self) -> str:
        """生成消息ID"""
        return hashlib.md5(f"{time.time()}_{random.random()}".encode()).hexdigest()[:16]

    def get_chat_statistics(self) -> dict[str, Any]:
        """获取聊天统计信息"""
        total_rooms = len(self.chat_rooms)
        active_rooms = len(
            [room for room in self.chat_rooms.values() if room.is_active],
        )
        total_messages = sum(len(room.messages) for room in self.chat_rooms.values())
        total_participants = sum(
            len(room.participants) for room in self.chat_rooms.values()
        )

        return {
            "total_rooms": total_rooms,
            "active_rooms": active_rooms,
            "total_messages": total_messages,
            "total_participants": total_participants,
            "available_experts": len(self.expert_library.experts),
            "model_type": self.model_interface.model_type,
        }
