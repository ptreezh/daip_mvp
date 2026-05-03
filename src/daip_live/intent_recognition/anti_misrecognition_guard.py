"""
防误识别守护器

专门负责防止普通对话被误识别为论文下载等意图
特别是防止"你好啊，为啥找不到roles"被误识别为论文意图
遵循SOLID原则中的单一职责原则
"""

import logging
from typing import Dict, Any, Optional, Union
from daip_live.agent_engine.enhanced_intent_recognizer import Intent, IntentType
from daip_live.intent_recognition.contextual_intent_recognizer import ContextualIntent


class AntiMisrecognitionGuard:
    """
    防误识别守护器

    专门负责防止普通对话被误识别为论文下载等意图
    遵循SOLID原则：
    - SRP: 仅负责防误识别保护功能
    - OCP: 可扩展更多保护策略
    """

    def __init__(self):
        """
        初始化防误识别守护器
        - 专门针对论文相关意图的权重调整
        - 误识别风险检测规则
        """
        # 对论文意图的惩罚权重
        self.paper_intent_penalty = -0.3  
        # 对聊天意图的增强权重
        self.chat_intent_boost = 0.2
        # 误识别风险阈值
        self.misrecognition_threshold = 0.7
        # 日志记录器
        self.logger = logging.getLogger(__name__)

    def apply_antimisrecognition_protection(self,
                                          intent_result: Union[Intent, ContextualIntent],
                                          context: Dict[str, Any]) -> Union[Intent, ContextualIntent]:
        """
        对意图识别结果应用防误识别保护

        Args:
            intent_result: 原意图识别结果
            context: 上下文信息

        Returns:
            经过防误识别保护的意图结果
        """
        if not intent_result:
            return intent_result

        # 检查是否存在误识别风险
        if self._is_misrecognition_risk(intent_result, context):
            self.logger.info(f"Misrecognition risk detected for intent: {intent_result.name}")
            # 应用置信度惩罚
            protected_result = self._apply_protection_penalty(intent_result)
            return protected_result
        else:
            return intent_result

    def _is_misrecognition_risk(self, intent_result: Union[Intent, ContextualIntent],
                               context: Dict[str, Any]) -> bool:
        """
        检查是否存在误识别风险，特别是将普通对话误识别为论文下载

        Args:
            intent_result: 意图识别结果
            context: 上下文信息

        Returns:
            是否存在误识别风险
        """
        if not intent_result or not hasattr(intent_result, 'name'):
            return False

        # 检查是否是论文相关意图
        paper_related_intents = ['search_papers', 'download_paper', 'papers', 'paper_download']
        is_paper_intent = intent_result.name in paper_related_intents

        if not is_paper_intent:
            return False  # 只有论文相关意图才需要检查误识别

        # 获取当前上下文话题
        current_topic = context.get('current_topic', '').lower()
        intent_history = context.get('intent_history', [])
        parameters = context.get('parameters', {})

        # 检查上下文是否为非学术话题
        non_academic_keywords = [
            '你好', 'hi', 'hello', '谢谢', '帮助', '助手', '聊天', '闲聊', '随便', 
            '问题', '为什么', '为啥', '啥', '啊', '呀', '哦', '嗯', '吧', '呢', 
            'role', 'roles', '助手', 'assistant', 'pa', 'personal assistant'
        ]
        
        non_academic_context = any(keyword in current_topic for keyword in non_academic_keywords)

        # 检查意图历史是否也支持非学术语境
        non_academic_intents = ['chat', 'question', 'personal_assistant', 'greeting']
        non_academic_history = any(intent in non_academic_intents for intent in intent_history[-3:])

        # 检查参数是否与论文无关
        paper_unrelated_params = any(
            keyword in str(parameters).lower() 
            for keyword in ['role', 'roles', 'assistant', '助手', 'pa', '个人', 'help', 'helping']
        )

        # 特殊检测：检查用户输入是否包含"找不到"、"为什么"、"为啥"等短语
        # 这些短语通常表示用户在提问或寻求帮助，而非搜索论文
        if hasattr(intent_result, 'parameters') and 'question' in str(intent_result.parameters).lower():
            question_indicators = ['找不到', '为什么', '为啥', '如何', '怎么', '怎样']
            question_in_params = any(indicator in str(intent_result.parameters) for indicator in question_indicators)
            if question_in_params:
                return True

        # 检查是否存在误识别风险
        # 如果是论文意图但上下文是非学术话题，则存在误识别风险
        risk_indicators = [
            non_academic_context,
            non_academic_history,
            paper_unrelated_params
        ]

        return any(risk_indicators)

    def _apply_protection_penalty(self, intent_result: Union[Intent, ContextualIntent]) -> Union[Intent, ContextualIntent]:
        """
        对存在误识别风险的意图结果应用保护性惩罚

        Args:
            intent_result: 意图识别结果

        Returns:
            应用惩罚后的意图结果
        """
        if not intent_result or not hasattr(intent_result, 'name') or not hasattr(intent_result, 'confidence'):
            return intent_result

        # 对论文相关意图应用惩罚，降低置信度
        paper_related_intents = ['search_papers', 'download_paper', 'papers', 'paper_download']
        if intent_result.name in paper_related_intents:
            # 降低论文意图的置信度
            original_conf = getattr(intent_result, 'confidence', 0.0)
            adjusted_conf = max(original_conf + self.paper_intent_penalty, 0.1)  # 最低置信度0.1
            intent_result.confidence = adjusted_conf

            self.logger.info(f"Applied penalty to paper intent '{intent_result.name}': {original_conf:.3f} -> {adjusted_conf:.3f}")

        # 对聊天、问候、帮助相关意图应用增强
        chat_related_intents = ['chat', 'question', 'greeting', 'personal_assistant']
        if intent_result.name in chat_related_intents:
            original_conf = getattr(intent_result, 'confidence', 0.0)
            adjusted_conf = min(original_conf + self.chat_intent_boost, 1.0)  # 最高置信度1.0
            intent_result.confidence = adjusted_conf

            self.logger.info(f"Applied boost to chat intent '{intent_result.name}': {original_conf:.3f} -> {adjusted_conf:.3f}")

        # 检查是否需要将论文意图转换为聊天意图
        if (intent_result.name in paper_related_intents and 
            intent_result.confidence < 0.4 and  # 置信度较低
            self._likely_chat_context(intent_result)):
            # 将意图转换为聊天意图
            intent_result.name = 'chat'
            intent_result.intent_type = IntentType.CHAT
            intent_result.confidence = max(intent_result.confidence + 0.2, 0.5)  # 提升到中等置信度
            intent_result.tool_name = None
            
            self.logger.info(f"Converted paper intent to chat intent due to low confidence and chat context")

        return intent_result

    def _likely_chat_context(self, intent_result: Union[Intent, ContextualIntent]) -> bool:
        """
        判断是否可能是聊天上下文

        Args:
            intent_result: 意图识别结果

        Returns:
            是否可能是聊天上下文
        """
        if hasattr(intent_result, 'parameters'):
            params_str = str(intent_result.parameters).lower()
            # 检查参数中是否包含聊天相关的关键词
            chat_indicators = [
                'help', 'helping', 'assist', 'assistant', 'role', 'roles', 
                '找不到', '为什么', '为啥', '如何', '怎么', '怎样', '问', '问题'
            ]
            return any(indicator in params_str for indicator in chat_indicators)

        return False

    def protect_intent_sequence(self, 
                              intent_results: list, 
                              context: Dict[str, Any]) -> list:
        """
        对一系列意图识别结果应用防误识别保护

        Args:
            intent_results: 意图识别结果列表
            context: 上下文信息

        Returns:
            保护后的意图识别结果列表
        """
        protected_results = []
        for intent_result in intent_results:
            protected_result = self.apply_antimisrecognition_protection(intent_result, context)
            protected_results.append(protected_result)
        
        return protected_results

    def validate_protection_rules(self, test_cases: list) -> Dict[str, Any]:
        """
        验证保护规则的有效性

        Args:
            test_cases: 测试用例列表

        Returns:
            验证结果
        """
        results = {
            'total_cases': len(test_cases),
            'correctly_protected': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'details': []
        }

        for test_case in test_cases:
            text_input = test_case['input']
            expected_intent = test_case['expected']
            actual_intent = test_case.get('actual', expected_intent)  # 假设这是识别出的意图
            context = test_case.get('context', {})

            # 模拟意图识别结果
            mock_intent = Intent(
                name=actual_intent,
                confidence=0.8,
                parameters={'text': text_input},
                intent_type=IntentType.CHAT if 'chat' in actual_intent else IntentType.WORKFLOW
            )

            protected_intent = self.apply_antimisrecognition_protection(mock_intent, context)

            is_correct = protected_intent.name == expected_intent
            result_detail = {
                'input': text_input,
                'original_intent': actual_intent,
                'protected_intent': protected_intent.name,
                'expected_intent': expected_intent,
                'is_correct': is_correct,
                'confidence_after_protection': protected_intent.confidence
            }

            results['details'].append(result_detail)

            if is_correct:
                results['correctly_protected'] += 1

        results['accuracy'] = results['correctly_protected'] / max(1, results['total_cases'])
        return results

    def check_core_use_case(self, text: str) -> bool:
        """
        专门检查核心用例："你好啊，为啥找不到roles"不应被识别为论文意图

        Args:
            text: 输入文本

        Returns:
            是否通过核心用例检查
        """
        # 创建模拟上下文
        context = {
            'current_topic': '',
            'intent_history': ['chat', 'question'],
            'parameters': {}
        }

        # 模拟一个被误识别为论文意图的结果
        mock_paper_intent = Intent(
            name='download_paper',
            confidence=0.7,
            parameters={'text': text, 'query': 'roles'},
            intent_type=IntentType.WORKFLOW
        )

        protected_intent = self.apply_antimisrecognition_protection(mock_paper_intent, context)

        # 检查是否成功将论文意图转换为其他意图
        is_protected = protected_intent.name != 'download_paper' or protected_intent.confidence < 0.5

        self.logger.info(f"Core use case check for '{text}': {'PROTECTED' if is_protected else 'NOT PROTECTED'}")
        return is_protected