#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-02 20:00:00
@Author  : DAIP-LIVE Team
@File    : casual_discussion_scenario.py
@Description:
    V0.2.7 轻松讨论场景核心功能实现
    
    基于项目核心组件实现轻松、自然的讨论体验：
    - 非正式、轻松的角色行为和语言风格
    - 话题的自然转换、延伸和深入探讨
    - 基于用户兴趣动态调整讨论方向
    - 社交元素：表情、点赞、有趣观点高亮
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# 导入项目核心组件
from src.core_services.role_manager import RoleManager
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.virtual_role_chat.cognitive_agent.agent import CognitiveAgent, CognitiveProfile
from src.core_services.wiki_service import WikiService
from src.core_services.memory_agent import MemAgent

logger = logging.getLogger(__name__)


@dataclass
class CasualDiscussionConfig:
    """轻松讨论配置"""
    max_participants: int = 4
    discussion_style: str = "casual"  # casual, fun, relaxed
    topic_flexibility: float = 0.8  # 话题转换的灵活度
    humor_level: float = 0.7  # 幽默程度
    social_elements: bool = True  # 启用社交元素
    emoji_usage: bool = True  # 使用表情符号
    energy_level: str = "medium"  # low, medium, high


@dataclass
class DiscussionTopic:
    """讨论话题"""
    topic_id: str
    main_topic: str
    subtopics: List[str]
    current_direction: str
    interest_score: float
    participant_engagement: Dict[str, float]
    created_at: str


@dataclass
class SocialInteraction:
    """社交互动"""
    interaction_id: str
    type: str  # like, emoji_reaction, highlight, comment
    participant_id: str
    target_content: str
    reaction_data: Dict[str, Any]
    timestamp: str


class CasualDiscussionScenario:
    """
    轻松讨论场景 - V0.2.7核心功能实现
    
    专注于营造轻松愉快的讨论氛围：
    - 自然流畅的对话体验
    - 动态话题管理和转换
    - 社交互动元素
    - 个性化兴趣探索
    """
    
    def __init__(self):
        """初始化轻松讨论场景"""
        self.scenario_id = str(uuid.uuid4())
        
        # 核心组件
        self.role_manager = RoleManager()
        self.llm_manager = IntegratedLLMManager()
        self.wiki_service = WikiService()
        
        # 轻松讨论专用的认知代理
        casual_profile = CognitiveProfile(
            reasoning_style="conversational",
            belief_structure="flexible",
            epistemological_approach="experiential",
            metacognitive_level=2,
            cognitive_biases=["optimism", "social_proof"],
            values={"fun": 0.9, "connection": 0.8, "creativity": 0.7},
            domain_expertise={"casual_conversation": 0.9, "social_interaction": 0.8, "topic_exploration": 0.8}
        )
        
        self.discussion_coordinator = CognitiveAgent(
            agent_id="casual_discussion_coordinator",
            name="轻松讨论协调员",
            profile=casual_profile
        )
        
        # 记忆代理
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            sskg_manager = EnhancedSSKGManager()
            self.memory_agent = MemAgent(sskg_manager)
        except Exception as e:
            logger.warning(f"MemAgent初始化失败，使用空实现: {e}")
            self.memory_agent = None
        
        # 轻松讨论状态
        self.active_discussions = {}
        self.casual_roles = self._initialize_casual_roles()
        self.social_interactions = []
        self.topic_transitions = []
        
        logger.info(f"轻松讨论场景初始化完成: {self.scenario_id}")
    
    def _initialize_casual_roles(self) -> List[Dict[str, Any]]:
        """初始化轻松讨论专用角色"""
        
        casual_roles = [
            {
                "role_id": "friendly_conversationalist",
                "name": "友好聊天者",
                "personality": "温暖、健谈、善于倾听",
                "speaking_style": "轻松自然，经常使用日常用语和表情",
                "expertise": ["日常生活", "人际交往", "兴趣爱好"],
                "conversation_patterns": ["询问细节", "分享经验", "表达共鸣"],
                "emoji_preference": ["😊", "👍", "🤔", "😄"]
            },
            {
                "role_id": "curious_explorer",
                "name": "好奇探索者",
                "personality": "充满好奇心、喜欢探索新话题",
                "speaking_style": "充满疑问、善于引导话题深入",
                "expertise": ["新奇事物", "创意思维", "跨领域连接"],
                "conversation_patterns": ["提出问题", "寻找联系", "拓展思路"],
                "emoji_preference": ["🤔", "💡", "🔍", "✨"]
            },
            {
                "role_id": "humorous_commentator",
                "name": "幽默评论员",
                "personality": "风趣幽默、善于活跃气氛",
                "speaking_style": "轻松诙谐，适当使用比喻和玩笑",
                "expertise": ["幽默表达", "氛围调节", "创意思维"],
                "conversation_patterns": ["幽默比喻", "轻松调侃", "气氛调节"],
                "emoji_preference": ["😂", "🎭", "🤪", "😎"]
            },
            {
                "role_id": "empathetic_listener",
                "name": "共情倾听者",
                "personality": "善解人意、感同身受",
                "speaking_style": "温暖支持，善于理解和回应情感",
                "expertise": ["情感理解", "心理支持", "人文关怀"],
                "conversation_patterns": ["情感回应", "支持鼓励", "深度倾听"],
                "emoji_preference": ["❤️", "🤗", "😌", "🙏"]
            }
        ]
        
        return casual_roles
    
    async def start_casual_discussion(
        self,
        initial_topic: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        config: Optional[CasualDiscussionConfig] = None
    ) -> Dict[str, Any]:
        """开始轻松讨论"""
        if config is None:
            config = CasualDiscussionConfig()
        
        discussion_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"开始轻松讨论: {discussion_id} - {initial_topic}")
        
        try:
            # 1. 话题分析和扩展
            topic_analysis = await self._analyze_and_expand_topic(initial_topic, user_preferences)
            
            # 2. 选择合适的讨论参与者
            selected_participants = await self._select_discussion_participants(
                topic_analysis, config
            )
            
            # 3. 初始化讨论环境
            discussion_context = await self._initialize_discussion_context(
                discussion_id, initial_topic, topic_analysis, selected_participants, config
            )
            
            # 4. 开始轻松讨论流程
            discussion_result = await self._conduct_casual_discussion(
                discussion_context, config
            )
            
            # 5. 社交互动处理
            social_summary = await self._process_social_interactions(
                discussion_result, config
            )
            
            # 6. 话题演进记录
            topic_evolution = await self._track_topic_evolution(
                discussion_result, initial_topic
            )
            
            # 7. 用户兴趣更新
            await self._update_user_interests(
                user_preferences, discussion_result, topic_evolution
            )
            
            end_time = datetime.now()
            
            result = {
                "success": True,
                "discussion_id": discussion_id,
                "initial_topic": initial_topic,
                "topic_analysis": topic_analysis,
                "selected_participants": [asdict(p) for p in selected_participants],
                "discussion_result": discussion_result,
                "social_summary": social_summary,
                "topic_evolution": topic_evolution,
                "metadata": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "config": asdict(config),
                    "engagement_score": self._calculate_engagement_score(discussion_result),
                    "fun_factor": self._calculate_fun_factor(discussion_result, social_summary)
                }
            }
            
            # 存储讨论记录
            self.active_discussions[discussion_id] = result
            
            # 记忆系统存储
            if self.memory_agent:
                try:
                    await self.memory_agent.store_interaction({
                        "type": "casual_discussion",
                        "discussion_id": discussion_id,
                        "topic": initial_topic,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"记忆存储失败: {e}")
            
            logger.info(f"轻松讨论完成: {discussion_id}")
            return result
            
        except Exception as e:
            logger.error(f"轻松讨论失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "discussion_id": discussion_id,
                "initial_topic": initial_topic
            }
    
    async def _analyze_and_expand_topic(
        self,
        initial_topic: str,
        user_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析和扩展话题"""
        logger.info("分析和扩展讨论话题...")
        
        analysis_prompt = f"""
        作为轻松讨论协调员，请分析以下话题并为轻松愉快的讨论做准备：
        
        话题：{initial_topic}
        用户偏好：{user_preferences or '无特定偏好'}
        
        请提供：
        1. 话题的有趣角度和切入点
        2. 可能的话题扩展方向
        3. 适合轻松讨论的子话题
        4. 话题的趣味性评估
        5. 适合的讨论氛围和风格
        
        要求：保持轻松、有趣、容易参与的特点
        """
        
        try:
            analysis_result = await self.llm_manager.call_llm_for_role(
                role_id=self.discussion_coordinator.agent_id,
                user_input=analysis_prompt,
                task_context="casual_topic_analysis",
                additional_context={
                    "style": "casual",
                    "mood": "light_hearted",
                    "user_preferences": user_preferences
                }
            )
            
            response = analysis_result.get("response", "")
            
            return {
                "topic_appeal": self._extract_topic_appeal(response),
                "expansion_directions": self._extract_expansion_directions(response),
                "subtopics": self._extract_subtopics(response),
                "fun_factor": self._assess_fun_factor(response),
                "discussion_style": self._recommend_discussion_style(response),
                "raw_analysis": response
            }
            
        except Exception as e:
            logger.error(f"话题分析失败: {e}")
            return {
                "topic_appeal": "通用话题",
                "expansion_directions": ["基本讨论"],
                "subtopics": [initial_topic],
                "fun_factor": 0.5,
                "discussion_style": "casual"
            }
    
    async def _select_discussion_participants(
        self,
        topic_analysis: Dict[str, Any],
        config: CasualDiscussionConfig
    ) -> List[Dict[str, Any]]:
        """选择讨论参与者"""
        logger.info("选择轻松讨论参与者...")
        
        # 基于话题分析选择最合适的轻松角色
        available_roles = self.casual_roles.copy()
        selected_participants = []
        
        # 根据话题类型和讨论风格选择角色
        fun_factor = topic_analysis.get("fun_factor", 0.5)
        discussion_style = topic_analysis.get("discussion_style", "casual")
        
        # 始终包含友好聊天者作为基础参与者
        base_participant = next(role for role in available_roles if role["role_id"] == "friendly_conversationalist")
        selected_participants.append(base_participant)
        available_roles.remove(base_participant)
        
        # 根据趣味性添加幽默评论员
        if fun_factor > 0.6 and config.humor_level > 0.5:
            humor_participant = next((role for role in available_roles if role["role_id"] == "humorous_commentator"), None)
            if humor_participant:
                selected_participants.append(humor_participant)
                available_roles.remove(humor_participant)
        
        # 添加好奇探索者促进话题发展
        if len(selected_participants) < config.max_participants:
            explorer_participant = next((role for role in available_roles if role["role_id"] == "curious_explorer"), None)
            if explorer_participant:
                selected_participants.append(explorer_participant)
                available_roles.remove(explorer_participant)
        
        # 根据需要添加共情倾听者
        if len(selected_participants) < config.max_participants and discussion_style in ["supportive", "emotional"]:
            empathy_participant = next((role for role in available_roles if role["role_id"] == "empathetic_listener"), None)
            if empathy_participant:
                selected_participants.append(empathy_participant)
        
        logger.info(f"选择了{len(selected_participants)}位讨论参与者")
        return selected_participants
    
    async def _initialize_discussion_context(
        self,
        discussion_id: str,
        initial_topic: str,
        topic_analysis: Dict[str, Any],
        participants: List[Dict[str, Any]],
        config: CasualDiscussionConfig
    ) -> Dict[str, Any]:
        """初始化讨论环境"""
        logger.info("初始化轻松讨论环境...")
        
        discussion_topic = DiscussionTopic(
            topic_id=str(uuid.uuid4()),
            main_topic=initial_topic,
            subtopics=topic_analysis.get("subtopics", [initial_topic]),
            current_direction=topic_analysis.get("expansion_directions", ["general"])[0],
            interest_score=topic_analysis.get("fun_factor", 0.5),
            participant_engagement={p["role_id"]: 0.8 for p in participants},
            created_at=datetime.now().isoformat()
        )
        
        context = {
            "discussion_id": discussion_id,
            "topic": discussion_topic,
            "participants": participants,
            "config": config,
            "atmosphere": {
                "mood": "relaxed",
                "energy": config.energy_level,
                "formality": "informal",
                "social_features_enabled": config.social_elements
            },
            "conversation_state": {
                "current_speaker": None,
                "last_interaction": None,
                "topic_transitions": [],
                "engagement_momentum": 0.8
            }
        }
        
        return context
    
    async def _conduct_casual_discussion(
        self,
        discussion_context: Dict[str, Any],
        config: CasualDiscussionConfig
    ) -> Dict[str, Any]:
        """进行轻松讨论"""
        logger.info("开始轻松讨论...")
        
        participants = discussion_context["participants"]
        topic = discussion_context["topic"]
        discussion_rounds = []
        social_interactions = []
        
        try:
            # 进行多轮轻松讨论
            for round_num in range(5):  # 5轮讨论
                logger.info(f"讨论轮次 {round_num + 1}/5")
                
                round_results = []
                
                for participant in participants:
                    # 生成参与者的轻松发言
                    contribution = await self._generate_casual_contribution(
                        participant, topic, discussion_context, round_num
                    )
                    
                    round_results.append(contribution)
                    
                    # 处理社交互动
                    if config.social_elements:
                        interactions = await self._generate_social_interactions(
                            contribution, participants, config
                        )
                        social_interactions.extend(interactions)
                    
                    # 检查话题转换需求
                    if round_num > 0 and self._should_transition_topic(contribution, topic):
                        new_direction = await self._suggest_topic_transition(
                            contribution, topic, discussion_context
                        )
                        if new_direction:
                            topic.current_direction = new_direction
                            topic.subtopics.append(new_direction)
                
                discussion_rounds.append({
                    "round_number": round_num + 1,
                    "contributions": round_results,
                    "topic_direction": topic.current_direction,
                    "social_interactions": interactions if config.social_elements else [],
                    "engagement_level": self._calculate_round_engagement(round_results)
                })
                
                # 动态调整讨论方向
                if round_num < 4:  # 不在最后一轮
                    await self._adjust_discussion_direction(discussion_context, round_results)
            
            return {
                "success": True,
                "discussion_rounds": discussion_rounds,
                "final_topic_state": asdict(topic),
                "social_interactions": social_interactions,
                "discussion_quality": self._assess_discussion_quality(discussion_rounds),
                "participant_engagement": self._calculate_participant_engagement(discussion_rounds),
                "topic_evolution": self._track_topic_evolution_in_discussion(discussion_rounds)
            }
            
        except Exception as e:
            logger.error(f"轻松讨论执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": discussion_rounds if discussion_rounds else []
            }
    
    async def _generate_casual_contribution(
        self,
        participant: Dict[str, Any],
        topic: DiscussionTopic,
        context: Dict[str, Any],
        round_num: int
    ) -> Dict[str, Any]:
        """生成参与者的轻松发言"""
        
        participant_prompt = f"""
        你是{participant['name']}，性格特点：{participant['personality']}
        
        当前讨论话题：{topic.main_topic}
        话题方向：{topic.current_direction}
        讨论轮次：{round_num + 1}
        
        你的说话风格：{participant['speaking_style']}
        常用表达模式：{', '.join(participant['conversation_patterns'])}
        
        请以轻松、自然的方式参与讨论，要求：
        1. 保持{participant['personality']}的个性特色
        2. 语言要{participant['speaking_style']}
        3. 可以适当使用表情符号：{', '.join(participant['emoji_preference'])}
        4. 发言长度控制在50-150字
        5. 尽量有趣、有见地或有共鸣
        
        请自然地参与这个轻松讨论。
        """
        
        try:
            contribution_result = await self.llm_manager.call_llm_for_role(
                role_id=participant["role_id"],
                user_input=participant_prompt,
                task_context="casual_discussion_contribution",
                additional_context={
                    "style": "casual",
                    "participant": participant["name"],
                    "round": round_num + 1
                }
            )
            
            content = contribution_result.get("response", f"我觉得{topic.main_topic}这个话题很有意思！😊")
            
            return {
                "participant_id": participant["role_id"],
                "participant_name": participant["name"],
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "style_score": self._assess_style_consistency(content, participant),
                "engagement_score": self._assess_content_engagement(content),
                "emoji_usage": self._count_emoji_usage(content),
                "topic_relevance": self._assess_topic_relevance(content, topic)
            }
            
        except Exception as e:
            logger.error(f"生成发言失败: {e}")
            fallback_content = f"作为{participant['name']}，我想说{topic.main_topic}确实是个有趣的话题！"
            
            return {
                "participant_id": participant["role_id"],
                "participant_name": participant["name"],
                "content": fallback_content,
                "timestamp": datetime.now().isoformat(),
                "style_score": 0.5,
                "engagement_score": 0.5,
                "emoji_usage": 0,
                "topic_relevance": 0.7
            }
    
    async def _generate_social_interactions(
        self,
        contribution: Dict[str, Any],
        participants: List[Dict[str, Any]],
        config: CasualDiscussionConfig
    ) -> List[SocialInteraction]:
        """生成社交互动"""
        
        interactions = []
        
        # 随机生成一些社交互动
        import random
        
        # 点赞互动
        if random.random() < 0.7:  # 70%概率有人点赞
            liker = random.choice([p for p in participants if p["role_id"] != contribution["participant_id"]])
            like_interaction = SocialInteraction(
                interaction_id=str(uuid.uuid4()),
                type="like",
                participant_id=liker["role_id"],
                target_content=contribution["content"][:50] + "...",
                reaction_data={"emotion": "positive", "strength": random.uniform(0.6, 1.0)},
                timestamp=datetime.now().isoformat()
            )
            interactions.append(like_interaction)
        
        # 表情回应
        if random.random() < 0.5 and config.emoji_usage:  # 50%概率有表情回应
            reactor = random.choice([p for p in participants if p["role_id"] != contribution["participant_id"]])
            emoji_choices = ["😄", "👍", "😊", "🤔", "👏", "❤️"]
            emoji_interaction = SocialInteraction(
                interaction_id=str(uuid.uuid4()),
                type="emoji_reaction",
                participant_id=reactor["role_id"],
                target_content=contribution["content"][:30] + "...",
                reaction_data={"emoji": random.choice(emoji_choices), "context": "casual_response"},
                timestamp=datetime.now().isoformat()
            )
            interactions.append(emoji_interaction)
        
        # 有趣观点高亮
        if contribution["engagement_score"] > 0.8:
            highlight_interaction = SocialInteraction(
                interaction_id=str(uuid.uuid4()),
                type="highlight",
                participant_id="system",
                target_content=contribution["content"],
                reaction_data={"reason": "interesting_point", "score": contribution["engagement_score"]},
                timestamp=datetime.now().isoformat()
            )
            interactions.append(highlight_interaction)
        
        return interactions
    
    async def _process_social_interactions(
        self,
        discussion_result: Dict[str, Any],
        config: CasualDiscussionConfig
    ) -> Dict[str, Any]:
        """处理社交互动数据"""
        
        all_interactions = []
        for round_data in discussion_result.get("discussion_rounds", []):
            all_interactions.extend(round_data.get("social_interactions", []))
        
        # 统计社交互动
        interaction_stats = {
            "total_interactions": len(all_interactions),
            "likes_count": len([i for i in all_interactions if i.type == "like"]),
            "emoji_reactions_count": len([i for i in all_interactions if i.type == "emoji_reaction"]),
            "highlights_count": len([i for i in all_interactions if i.type == "highlight"]),
            "interaction_rate": len(all_interactions) / max(len(discussion_result.get("discussion_rounds", [])), 1)
        }
        
        # 最受欢迎的内容
        popular_content = self._identify_popular_content(all_interactions)
        
        return {
            "interaction_stats": interaction_stats,
            "popular_content": popular_content,
            "social_engagement_score": min(interaction_stats["interaction_rate"] / 2, 1.0),
            "atmosphere_rating": self._assess_social_atmosphere(all_interactions)
        }
    
    async def _track_topic_evolution(
        self,
        discussion_result: Dict[str, Any],
        initial_topic: str
    ) -> Dict[str, Any]:
        """跟踪话题演进"""
        
        rounds = discussion_result.get("discussion_rounds", [])
        topic_flow = []
        
        for round_data in rounds:
            topic_direction = round_data.get("topic_direction", initial_topic)
            contributions = round_data.get("contributions", [])
            
            # 分析本轮的话题焦点
            round_topics = []
            for contribution in contributions:
                content = contribution.get("content", "")
                topic_keywords = self._extract_topic_keywords(content)
                round_topics.extend(topic_keywords)
            
            topic_flow.append({
                "round": round_data["round_number"],
                "direction": topic_direction,
                "keywords": list(set(round_topics)),
                "engagement": round_data.get("engagement_level", 0.5)
            })
        
        return {
            "initial_topic": initial_topic,
            "topic_flow": topic_flow,
            "final_directions": topic_flow[-1]["keywords"] if topic_flow else [],
            "topic_drift_score": self._calculate_topic_drift(initial_topic, topic_flow),
            "natural_transitions": self._count_natural_transitions(topic_flow)
        }
    
    async def _update_user_interests(
        self,
        user_preferences: Optional[Dict[str, Any]],
        discussion_result: Dict[str, Any],
        topic_evolution: Dict[str, Any]
    ):
        """更新用户兴趣档案"""
        
        if not user_preferences:
            return
        
        # 从讨论中提取用户可能感兴趣的新话题
        discussed_topics = []
        for topic_data in topic_evolution.get("topic_flow", []):
            discussed_topics.extend(topic_data.get("keywords", []))
        
        # 基于参与度更新兴趣权重
        high_engagement_topics = [
            topic_data["keywords"] for topic_data in topic_evolution.get("topic_flow", [])
            if topic_data.get("engagement", 0) > 0.7
        ]
        
        updated_interests = {
            "new_interests": list(set(discussed_topics)),
            "high_engagement_topics": [item for sublist in high_engagement_topics for item in sublist],
            "discussion_style_preference": self._infer_style_preference(discussion_result),
            "social_interaction_preference": self._infer_social_preference(discussion_result)
        }
        
        # 存储到记忆系统
        if self.memory_agent:
            try:
                await self.memory_agent.store_interaction({
                    "type": "user_interest_update",
                    "user_preferences": user_preferences,
                    "updated_interests": updated_interests,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"用户兴趣更新存储失败: {e}")
    
    # 辅助方法
    def _extract_topic_appeal(self, response: str) -> str:
        """提取话题吸引力"""
        if "吸引力" in response or "有趣" in response:
            lines = response.split('\n')
            for line in lines:
                if "吸引力" in line or "有趣" in line:
                    return line.strip()
        return "通用话题"
    
    def _extract_expansion_directions(self, response: str) -> List[str]:
        """提取话题扩展方向"""
        directions = []
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["方向", "角度", "扩展", "延伸"]):
                directions.append(line.strip())
        return directions[:5] if directions else ["基本讨论"]
    
    def _extract_subtopics(self, response: str) -> List[str]:
        """提取子话题"""
        subtopics = []
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["子话题", "方面", "维度"]):
                subtopics.append(line.strip())
        return subtopics[:8] if subtopics else ["基本话题"]
    
    def _assess_fun_factor(self, response: str) -> float:
        """评估趣味性因子"""
        fun_keywords = ["有趣", "好玩", "轻松", "愉快", "幽默", "趣味"]
        fun_count = sum(1 for keyword in fun_keywords if keyword in response)
        return min(fun_count / len(fun_keywords), 1.0)
    
    def _recommend_discussion_style(self, response: str) -> str:
        """推荐讨论风格"""
        if any(word in response for word in ["轻松", "随意", "自然"]):
            return "casual"
        elif any(word in response for word in ["有趣", "好玩", "幽默"]):
            return "fun"
        elif any(word in response for word in ["支持", "共鸣", "理解"]):
            return "supportive"
        else:
            return "casual"
    
    def _should_transition_topic(self, contribution: Dict[str, Any], current_topic: DiscussionTopic) -> bool:
        """判断是否应该转换话题"""
        content = contribution.get("content", "")
        
        # 简单的话题转换判断逻辑
        transition_indicators = ["另外", "顺便说", "这让我想到", "说到这个", "换个角度"]
        return any(indicator in content for indicator in transition_indicators)
    
    def _calculate_engagement_score(self, discussion_result: Dict[str, Any]) -> float:
        """计算参与度分数"""
        rounds = discussion_result.get("discussion_rounds", [])
        if not rounds:
            return 0.5
        
        total_engagement = sum(round_data.get("engagement_level", 0.5) for round_data in rounds)
        return total_engagement / len(rounds)
    
    def _calculate_fun_factor(self, discussion_result: Dict[str, Any], social_summary: Dict[str, Any]) -> float:
        """计算趣味因子"""
        base_fun = self._calculate_engagement_score(discussion_result)
        social_boost = social_summary.get("social_engagement_score", 0) * 0.3
        return min(base_fun + social_boost, 1.0)
    
    def _assess_style_consistency(self, content: str, participant: Dict[str, Any]) -> float:
        """评估风格一致性"""
        # 简化实现
        expected_patterns = participant.get("conversation_patterns", [])
        pattern_matches = sum(1 for pattern in expected_patterns if any(word in content for word in pattern.split()))
        return min(pattern_matches / len(expected_patterns) if expected_patterns else 0.5, 1.0)
    
    def _assess_content_engagement(self, content: str) -> float:
        """评估内容参与度"""
        engagement_indicators = ["!", "?", "😊", "😄", "有趣", "好玩", "同意", "我觉得"]
        indicator_count = sum(1 for indicator in engagement_indicators if indicator in content)
        return min(indicator_count / 3, 1.0)
    
    def _count_emoji_usage(self, content: str) -> int:
        """统计表情符号使用"""
        import re
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')
        return len(emoji_pattern.findall(content))
    
    def _assess_topic_relevance(self, content: str, topic: DiscussionTopic) -> float:
        """评估话题相关性"""
        topic_words = topic.main_topic.split() + topic.subtopics
        content_lower = content.lower()
        relevance_count = sum(1 for word in topic_words if word.lower() in content_lower)
        return min(relevance_count / len(topic_words) if topic_words else 0.5, 1.0)
    
    def _calculate_round_engagement(self, round_results: List[Dict[str, Any]]) -> float:
        """计算轮次参与度"""
        if not round_results:
            return 0.5
        
        total_engagement = sum(result.get("engagement_score", 0.5) for result in round_results)
        return total_engagement / len(round_results)
    
    def _assess_discussion_quality(self, discussion_rounds: List[Dict[str, Any]]) -> Dict[str, float]:
        """评估讨论质量"""
        if not discussion_rounds:
            return {"overall": 0.5, "naturalness": 0.5, "engagement": 0.5, "fun": 0.5}
        
        engagement_scores = [round_data.get("engagement_level", 0.5) for round_data in discussion_rounds]
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        
        return {
            "overall": avg_engagement,
            "naturalness": avg_engagement * 0.9,  # 简化计算
            "engagement": avg_engagement,
            "fun": avg_engagement * 1.1 if avg_engagement < 0.9 else 1.0
        }
    
    def _calculate_participant_engagement(self, discussion_rounds: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算参与者参与度"""
        participant_scores = {}
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                participant_id = contribution.get("participant_id", "unknown")
                engagement = contribution.get("engagement_score", 0.5)
                
                if participant_id not in participant_scores:
                    participant_scores[participant_id] = []
                participant_scores[participant_id].append(engagement)
        
        # 计算平均值
        for participant_id in participant_scores:
            scores = participant_scores[participant_id]
            participant_scores[participant_id] = sum(scores) / len(scores) if scores else 0.5
        
        return participant_scores
    
    def _track_topic_evolution_in_discussion(self, discussion_rounds: List[Dict[str, Any]]) -> List[str]:
        """跟踪讨论中的话题演进"""
        evolution = []
        
        for round_data in discussion_rounds:
            topic_direction = round_data.get("topic_direction", "general")
            if topic_direction not in evolution:
                evolution.append(topic_direction)
        
        return evolution
    
    def _identify_popular_content(self, interactions: List[SocialInteraction]) -> List[Dict[str, Any]]:
        """识别受欢迎的内容"""
        content_popularity = {}
        
        for interaction in interactions:
            target = interaction.target_content
            if target not in content_popularity:
                content_popularity[target] = {"likes": 0, "reactions": 0, "highlights": 0}
            
            if interaction.type == "like":
                content_popularity[target]["likes"] += 1
            elif interaction.type == "emoji_reaction":
                content_popularity[target]["reactions"] += 1
            elif interaction.type == "highlight":
                content_popularity[target]["highlights"] += 1
        
        # 排序并返回前5个最受欢迎的内容
        sorted_content = sorted(
            content_popularity.items(),
            key=lambda x: sum(x[1].values()),
            reverse=True
        )
        
        return [{"content": content, "popularity": stats} for content, stats in sorted_content[:5]]
    
    def _assess_social_atmosphere(self, interactions: List[SocialInteraction]) -> str:
        """评估社交氛围"""
        if not interactions:
            return "neutral"
        
        positive_interactions = len([i for i in interactions if i.type in ["like", "emoji_reaction"]])
        total_interactions = len(interactions)
        
        if positive_interactions / total_interactions > 0.7:
            return "very_positive"
        elif positive_interactions / total_interactions > 0.5:
            return "positive"
        else:
            return "neutral"
    
    def _extract_topic_keywords(self, content: str) -> List[str]:
        """提取话题关键词"""
        # 简化的关键词提取
        import re
        
        # 移除标点符号并分词
        words = re.findall(r'\b\w+\b', content.lower())
        
        # 过滤停用词
        stop_words = {'的', '是', '在', '和', '有', '我', '你', '他', '她', '它', '这', '那'}
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:5]  # 返回前5个关键词
    
    def _calculate_topic_drift(self, initial_topic: str, topic_flow: List[Dict[str, Any]]) -> float:
        """计算话题漂移程度"""
        if not topic_flow:
            return 0.0
        
        initial_keywords = set(initial_topic.lower().split())
        final_keywords = set(topic_flow[-1].get("keywords", []))
        
        if not initial_keywords or not final_keywords:
            return 0.5
        
        overlap = len(initial_keywords & final_keywords)
        total_unique = len(initial_keywords | final_keywords)
        
        # 漂移分数 = 1 - 重叠度
        return 1 - (overlap / total_unique) if total_unique > 0 else 0.5
    
    def _count_natural_transitions(self, topic_flow: List[Dict[str, Any]]) -> int:
        """统计自然转换次数"""
        if len(topic_flow) < 2:
            return 0
        
        transitions = 0
        for i in range(1, len(topic_flow)):
            prev_keywords = set(topic_flow[i-1].get("keywords", []))
            curr_keywords = set(topic_flow[i].get("keywords", []))
            
            # 如果有部分重叠但不完全相同，认为是自然转换
            overlap = len(prev_keywords & curr_keywords)
            if 0 < overlap < max(len(prev_keywords), len(curr_keywords)):
                transitions += 1
        
        return transitions
    
    def _infer_style_preference(self, discussion_result: Dict[str, Any]) -> str:
        """推断风格偏好"""
        quality = discussion_result.get("discussion_quality", {})
        
        if quality.get("fun", 0) > 0.8:
            return "humorous"
        elif quality.get("engagement", 0) > 0.8:
            return "interactive"
        else:
            return "casual"
    
    def _infer_social_preference(self, discussion_result: Dict[str, Any]) -> str:
        """推断社交偏好"""
        social_interactions = discussion_result.get("social_interactions", [])
        
        if len(social_interactions) > 10:
            return "highly_social"
        elif len(social_interactions) > 5:
            return "moderately_social"
        else:
            return "low_social"
    
    async def _adjust_discussion_direction(
        self,
        discussion_context: Dict[str, Any],
        round_results: List[Dict[str, Any]]
    ):
        """动态调整讨论方向"""
        
        # 分析当前轮次的参与度
        avg_engagement = sum(r.get("engagement_score", 0.5) for r in round_results) / len(round_results)
        
        # 如果参与度较低，调整话题方向
        if avg_engagement < 0.6:
            topic = discussion_context["topic"]
            
            # 选择新的话题方向
            if topic.subtopics:
                import random
                new_direction = random.choice(topic.subtopics)
                topic.current_direction = new_direction
                logger.info(f"调整话题方向至: {new_direction}")
    
    async def _suggest_topic_transition(
        self,
        contribution: Dict[str, Any],
        current_topic: DiscussionTopic,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """建议话题转换"""
        
        content = contribution.get("content", "")
        
        # 从发言中提取可能的新话题方向
        transition_prompt = f"""
        基于以下发言，建议一个自然的话题转换方向：
        
        当前话题：{current_topic.main_topic}
        发言内容：{content}
        
        请提供一个简短的新话题方向（10字以内）：
        """
        
        try:
            result = await self.llm_manager.call_llm_for_role(
                role_id=self.discussion_coordinator.agent_id,
                user_input=transition_prompt,
                task_context="topic_transition_suggestion"
            )
            
            suggested_direction = result.get("response", "").strip()
            
            # 验证建议的合理性
            if len(suggested_direction) > 0 and len(suggested_direction) <= 20:
                return suggested_direction
            
        except Exception as e:
            logger.error(f"话题转换建议失败: {e}")
        
        return None


# 便捷函数
async def start_casual_discussion(
    topic: str,
    user_preferences: Optional[Dict[str, Any]] = None,
    max_participants: int = 4,
    humor_level: float = 0.7,
    social_elements: bool = True
) -> Dict[str, Any]:
    """便捷的轻松讨论启动函数"""
    
    config = CasualDiscussionConfig(
        max_participants=max_participants,
        humor_level=humor_level,
        social_elements=social_elements
    )
    
    scenario = CasualDiscussionScenario()
    return await scenario.start_casual_discussion(topic, user_preferences, config)


# 使用示例
async def main():
    """测试轻松讨论场景"""
    scenario = CasualDiscussionScenario()
    
    # 测试轻松讨论
    topic = "最近看的好电影"
    user_preferences = {
        "interests": ["电影", "娱乐", "艺术"],
        "discussion_style": "casual",
        "humor_tolerance": 0.8
    }
    
    config = CasualDiscussionConfig(
        max_participants=4,
        humor_level=0.8,
        social_elements=True,
        emoji_usage=True
    )
    
    result = await scenario.start_casual_discussion(
        initial_topic=topic,
        user_preferences=user_preferences,
        config=config
    )
    
    if result["success"]:
        print(f"\n轻松讨论完成！")
        print(f"讨论ID: {result['discussion_id']}")
        print(f"参与者: {len(result['selected_participants'])}位")
        print(f"讨论轮次: {len(result['discussion_result']['discussion_rounds'])}轮")
        print(f"参与度评分: {result['metadata']['engagement_score']:.2f}")
        print(f"趣味因子: {result['metadata']['fun_factor']:.2f}")
        print(f"社交互动: {result['social_summary']['interaction_stats']['total_interactions']}次")
    else:
        print(f"轻松讨论失败: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())