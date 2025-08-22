"""聊天室规则引擎实现

这个模块实现了聊天室内的制度原语规则引擎，控制虚拟角色发言行为和交互规则。
"""

import asyncio
import logging
import random
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque

from .models import ChatRoomConfig, ChatMessage

logger = logging.getLogger(__name__)


class InteractionMode(Enum):
    """交互模式枚举"""
    FREE_FORM = "free_form"  # 自由形式，角色可以随时发言
    TURN_BASED = "turn_based"  # 轮流发言
    RANDOM = "random"  # 随机发言
    DEBATE = "debate"  # 辩论模式


class PromptGenerationStrategy(Enum):
    """提示词生成策略枚举"""
    SIMPLE = "simple"  # 简单提示词（仅当前消息）
    CONTEXTUAL = "contextual"  # 上下文提示词（包含最近几条消息）
    SUMMARIZED = "summarized"  # 汇总提示词（包含消息摘要）


@dataclass
class ChatRuleContext:
    """聊天规则上下文"""
    room_config: ChatRoomConfig
    current_turn: int
    last_speaker: Optional[str]
    message_history: List[ChatMessage]
    active_participants: List[str]
    

class ChatRulesEngine:
    """聊天室规则引擎
    
    控制聊天室内虚拟角色的发言行为和交互规则。
    """
    
    def __init__(self, debug: bool = False):
        """初始化聊天室规则引擎
        
        Args:
            debug: 是否启用调试模式，启用后会输出详细的规则决策过程
        """
        self.logger = logging.getLogger(__name__)
        self.debug = debug
        
    def determine_next_speaker(self, context: ChatRuleContext) -> Optional[str]:
        """确定下一个发言者
        
        Args:
            context: 聊天规则上下文
            
        Returns:
            下一个发言者的角色ID，如果没有人应该发言则返回None
        """
        if not context.active_participants:
            if self.debug:
                print("[DEBUG] 没有活跃参与者，无法确定下一个发言者")
            return None
            
        mode = context.room_config.mode
        rules = context.room_config.interaction_rules
        
        if self.debug:
            print(f"[DEBUG] 确定下一个发言者 - 模式: {mode}")
            print(f"[DEBUG] 活跃参与者: {context.active_participants}")
            print(f"[DEBUG] 当前轮次: {context.current_turn}")
            print(f"[DEBUG] 上一个发言者: {context.last_speaker}")
        
        # 根据不同的交互模式确定下一个发言者
        if mode == InteractionMode.FREE_FORM.value:
            # 自由形式：任何角色都可以发言
            # 在规则引擎中，我们不强制任何特定角色发言
            # 但在实际实现中，可能需要基于其他因素选择
            if self.debug:
                print("[DEBUG] 自由发言模式，不强制特定角色发言")
            return None  # 让外部逻辑决定
            
        elif mode == InteractionMode.TURN_BASED.value:
            # 轮流发言：按照固定顺序轮流发言
            if self.debug:
                print("[DEBUG] 轮流发言模式")
            return self._determine_turn_based_speaker(context)
            
        elif mode == InteractionMode.RANDOM.value:
            # 随机发言：随机选择发言人
            if self.debug:
                print("[DEBUG] 随机发言模式")
            return self._determine_random_speaker(context)
            
        elif mode == InteractionMode.DEBATE.value:
            # 辩论模式：基于辩论规则选择发言人
            if self.debug:
                print("[DEBUG] 辩论模式")
            return self._determine_debate_speaker(context)
            
        else:
            # 默认：自由形式
            if self.debug:
                print(f"[DEBUG] 未知模式 '{mode}'，使用默认自由发言模式")
            return None
    
    def _determine_turn_based_speaker(self, context: ChatRuleContext) -> str:
        """确定轮流发言模式下的下一个发言者"""
        participants = context.active_participants
        if not participants:
            if self.debug:
                print("[DEBUG] 没有参与者，无法确定轮流发言者")
            return None
            
        # 简单的轮流机制：基于轮次选择
        next_index = context.current_turn % len(participants)
        selected_speaker = participants[next_index]
        
        if self.debug:
            print(f"[DEBUG] 轮流发言选择 - 参与者数: {len(participants)}, 当前轮次: {context.current_turn}, 选择索引: {next_index}, 选择角色: {selected_speaker}")
            
        return selected_speaker
    
    def _determine_random_speaker(self, context: ChatRuleContext) -> str:
        """确定随机发言模式下的下一个发言者"""
        participants = context.active_participants
        if not participants:
            if self.debug:
                print("[DEBUG] 没有参与者，无法确定随机发言者")
            return None
            
        # 添加一些权重机制，避免同一角色连续发言
        if context.last_speaker and len(participants) > 1:
            # 降低上次发言者的权重
            candidates = [p for p in participants if p != context.last_speaker]
            if candidates:
                selected_speaker = random.choice(candidates)
                if self.debug:
                    print(f"[DEBUG] 随机发言选择 - 排除上次发言者 '{context.last_speaker}'，从 {candidates} 中随机选择: {selected_speaker}")
                return selected_speaker
                
        # 完全随机选择
        selected_speaker = random.choice(participants)
        if self.debug:
            print(f"[DEBUG] 随机发言选择 - 从所有参与者 {participants} 中随机选择: {selected_speaker}")
        return selected_speaker
    
    def _determine_debate_speaker(self, context: ChatRuleContext) -> str:
        """确定辩论模式下的下一个发言者"""
        participants = context.active_participants
        if not participants:
            if self.debug:
                print("[DEBUG] 没有参与者，无法确定辩论发言者")
            return None
            
        # 简单的辩论机制：交替选择不同角色
        if context.last_speaker:
            # 选择与上次发言者不同的角色
            candidates = [p for p in participants if p != context.last_speaker]
            if candidates:
                selected_speaker = random.choice(candidates)
                if self.debug:
                    print(f"[DEBUG] 辩论发言选择 - 上次发言者为 '{context.last_speaker}'，从其他候选人 {candidates} 中随机选择: {selected_speaker}")
                return selected_speaker
                
        # 如果没有上次发言者，随机选择
        selected_speaker = random.choice(participants)
        if self.debug:
            print(f"[DEBUG] 辩论发言选择 - 无上次发言者，从所有参与者 {participants} 中随机选择: {selected_speaker}")
        return selected_speaker
    
    def generate_role_prompt(self, role_id: str, context: ChatRuleContext) -> str:
        """为指定角色生成发言提示词
        
        Args:
            role_id: 角色ID
            context: 聊天规则上下文
            
        Returns:
            为角色生成的提示词
        """
        strategy = context.room_config.interaction_rules.get(
            "prompt_strategy", 
            PromptGenerationStrategy.CONTEXTUAL.value
        )
        
        if self.debug:
            print(f"[DEBUG] 为角色 '{role_id}' 生成提示词 - 策略: {strategy}")
        
        # 根据策略生成提示词
        if strategy == PromptGenerationStrategy.SIMPLE.value:
            prompt = self._generate_simple_prompt(role_id, context)
        elif strategy == PromptGenerationStrategy.CONTEXTUAL.value:
            prompt = self._generate_contextual_prompt(role_id, context)
        elif strategy == PromptGenerationStrategy.SUMMARIZED.value:
            prompt = self._generate_summarized_prompt(role_id, context)
        else:
            # 默认使用上下文提示词
            if self.debug:
                print(f"[DEBUG] 未知策略 '{strategy}'，使用默认上下文提示词策略")
            prompt = self._generate_contextual_prompt(role_id, context)
            
        if self.debug:
            print(f"[DEBUG] 生成的提示词:\n{prompt}\n" + "="*50)
            
        return prompt
    
    def _generate_simple_prompt(self, role_id: str, context: ChatRuleContext) -> str:
        """生成简单提示词"""
        topic = context.room_config.topic
        prompt = f"请就'{topic}'发表您的看法。"
        
        if self.debug:
            print(f"[DEBUG] 生成简单提示词 - 主题: {topic}")
            
        return prompt
    
    def _generate_contextual_prompt(self, role_id: str, context: ChatRuleContext) -> str:
        """生成上下文提示词"""
        topic = context.room_config.topic
        
        # 获取最近几条消息作为上下文
        recent_messages = context.message_history[-3:]  # 最近3条消息
        context_text = "\n".join([
            f"[{msg.timestamp.strftime('%H:%M:%S')}] {msg.sender_id}: {msg.content}" 
            for msg in recent_messages
        ])
        
        if self.debug:
            print(f"[DEBUG] 生成上下文提示词 - 主题: {topic}")
            print(f"[DEBUG] 最近消息数: {len(recent_messages)}")
            if recent_messages:
                print("[DEBUG] 最近消息:")
                for i, msg in enumerate(recent_messages):
                    print(f"  {i+1}. [{msg.timestamp.strftime('%H:%M:%S')}] {msg.sender_id}: {msg.content[:50]}...")
        
        prompt = f"""您是'{role_id}'角色，正在参与关于'{topic}'的讨论。

讨论上下文:
{context_text}

请基于以上上下文发表您的看法，或者回应其他角色的观点。"""
        
        return prompt
    
    def _generate_summarized_prompt(self, role_id: str, context: ChatRuleContext) -> str:
        """生成汇总提示词"""
        topic = context.room_config.topic
        
        # 简单的消息摘要（实际实现中可以使用更复杂的摘要算法）
        if context.message_history:
            # 统计各角色的发言次数
            role_counts = {}
            for msg in context.message_history[-10:]:  # 最近10条消息
                role_counts[msg.sender_id] = role_counts.get(msg.sender_id, 0) + 1
            
            summary_parts = []
            for role, count in role_counts.items():
                summary_parts.append(f"{role}发言{count}次")
            
            summary = "，".join(summary_parts)
            
            if self.debug:
                print(f"[DEBUG] 生成汇总提示词 - 主题: {topic}")
                print(f"[DEBUG] 角色发言统计: {role_counts}")
        else:
            summary = "暂无发言记录"
            if self.debug:
                print(f"[DEBUG] 生成汇总提示词 - 主题: {topic}, 无发言记录")
        
        prompt = f"""您是'{role_id}'角色，正在参与关于'{topic}'的讨论。

讨论摘要:
{summary}

请基于讨论摘要发表您的独特见解。"""
        
        return prompt
    
    def should_role_respond(self, role_id: str, context: ChatRuleContext) -> bool:
        """判断角色是否应该响应
        
        Args:
            role_id: 角色ID
            context: 聊天规则上下文
            
        Returns:
            如果角色应该响应则返回True，否则返回False
        """
        mode = context.room_config.mode
        
        if self.debug:
            print(f"[DEBUG] 判断角色 '{role_id}' 是否应该响应 - 模式: {mode}")
        
        # 在自由发言模式下，角色通常应该响应
        if mode == InteractionMode.FREE_FORM.value:
            if self.debug:
                print(f"[DEBUG] 自由发言模式，角色 '{role_id}' 应该响应")
            return True
            
        # 在轮流发言模式下，只有被选中的角色才应该响应
        if mode == InteractionMode.TURN_BASED.value:
            next_speaker = self.determine_next_speaker(context)
            should_respond = next_speaker == role_id
            if self.debug:
                print(f"[DEBUG] 轮流发言模式 - 下一个发言者: {next_speaker}, 角色 '{role_id}' {'应该' if should_respond else '不应该'} 响应")
            return should_respond
            
        # 在随机发言模式下，有一定概率响应
        if mode == InteractionMode.RANDOM.value:
            # 70%的概率响应
            probability = random.random()
            should_respond = probability < 0.7
            if self.debug:
                print(f"[DEBUG] 随机发言模式 - 随机概率: {probability:.2f}, 阈值: 0.7, 角色 '{role_id}' {'应该' if should_respond else '不应该'} 响应")
            return should_respond
            
        # 在辩论模式下，通常应该响应
        if mode == InteractionMode.DEBATE.value:
            if self.debug:
                print(f"[DEBUG] 辩论模式，角色 '{role_id}' 应该响应")
            return True
            
        # 默认情况
        if self.debug:
            print(f"[DEBUG] 默认情况，角色 '{role_id}' 应该响应")
        return True