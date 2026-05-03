"""
多模型上下文引用处理器

处理跨模型切换的上下文引用和指代消解
确保在多模型场景下上下文保持一致性和连续性
遵循SOLID原则中的单一职责原则
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from daip_live.intent_recognition.entity_extractor import Entity, EntityExtractor
from daip_live.intent_recognition.context_integrator import ContextIntegrator


class MultiModelContextReferenceHandler:
    """
    多模型上下文引用处理器

    处理跨模型切换的上下文引用和指代消解
    遵循SOLID原则：
    - SRP: 仅负责跨模型上下文引用
    - OCP: 可扩展更多模型类型
    """

    def __init__(self, 
                 context_integrator: Optional[ContextIntegrator] = None,
                 entity_extractor: Optional[EntityExtractor] = None):
        """
        初始化多模型上下文引用处理器

        Args:
            context_integrator: 上下文集成器
            entity_extractor: 实体提取器
        """
        self.context_integrator = context_integrator
        self.entity_extractor = entity_extractor
        self.logger = logging.getLogger(__name__)

        # 存储跨模型上下文信息
        self.cross_model_contexts: Dict[str, Dict[str, Any]] = {}

    def handle_cross_model_reference(self, 
                                   text: str, 
                                   current_model: str, 
                                   session_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        处理跨模型上下文引用

        Args:
            text: 用户输入文本
            current_model: 当前模型
            session_id: 会话ID

        Returns:
            处理后的文本和上下文信息
        """
        # 提取上下文中的实体和引用
        entities = []
        if self.entity_extractor:
            entities = self.entity_extractor.extract_entities_from_context(session_id)

        # 处理代词引用
        resolved_text = self._resolve_pronoun_references(text, entities)

        # 处理跨模型实体引用
        enhanced_text = self._resolve_cross_model_references(resolved_text, session_id, current_model)

        # 获取跨模型上下文信息
        cross_model_context = self._get_cross_model_context(session_id, current_model)

        return enhanced_text, cross_model_context

    def _resolve_pronoun_references(self, text: str, entities: List[Entity]) -> str:
        """
        解析代词引用

        Args:
            text: 输入文本
            entities: 实体列表

        Returns:
            解析代词引用后的文本
        """
        if not entities:
            return text

        # 按置信度排序实体，优先使用高置信度的实体
        sorted_entities = sorted(entities, key=lambda e: e.confidence, reverse=True)

        # 处理中文代词
        pronoun_replacements = {
            '它': [e.value for e in sorted_entities if e.entity_type in ['paper_id', 'topic', 'title', 'query']],
            '这': [e.value for e in sorted_entities if e.entity_type in ['topic', 'argument', 'concept', 'title']],
            '那': [e.value for e in sorted_entities if e.entity_type in ['topic', 'argument', 'concept', 'title']],
            '这个': [e.value for e in sorted_entities if e.entity_type in ['topic', 'argument', 'concept', 'title']],
            '那个': [e.value for e in sorted_entities if e.entity_type in ['topic', 'argument', 'concept', 'title']],
        }

        result_text = text

        for pronoun, possible_replacements in pronoun_replacements.items():
            if pronoun in result_text and possible_replacements:
                # 找到最相关的替换
                best_replacement = possible_replacements[0]  # 使用第一个（最高置信度）
                
                # 使用正则替换，确保准确匹配
                pattern = r'\b' + re.escape(pronoun) + r'\b'
                result_text = re.sub(pattern, str(best_replacement), result_text)

        return result_text

    def _resolve_cross_model_references(self, text: str, session_id: str, current_model: str) -> str:
        """
        解析跨模型实体引用

        Args:
            text: 输入文本
            session_id: 会话ID
            current_model: 当前模型

        Returns:
            解析跨模型引用后的文本
        """
        # 检查是否需要跨模型引用
        reference_indicators = ['它怎么样', '这个呢', '那个如何', '之前提到的', '刚才说的', '上述内容']
        
        if not any(indicator in text for indicator in reference_indicators):
            return text

        # 获取跨模型上下文
        cross_model_context = self._get_cross_model_context(session_id, current_model)

        if not cross_model_context:
            return text

        # 执行跨模型引用解析
        result_text = text

        for indicator in reference_indicators:
            if indicator in result_text:
                # 尝试从跨模型上下文中找到合适的替换内容
                replacement = self._find_appropriate_reference(cross_model_context, indicator)
                if replacement:
                    result_text = result_text.replace(indicator, f"{replacement}怎么样" if '怎么样' in indicator else replacement)

        return result_text

    def _find_appropriate_reference(self, cross_model_context: Dict[str, Any], indicator: str) -> Optional[str]:
        """
        从跨模型上下文中找到合适的引用内容

        Args:
            cross_model_context: 跨模型上下文
            indicator: 引用指示符

        Returns:
            合适的引用内容或None
        """
        # 从上下文历史中找到最近的相关内容
        conversation_history = cross_model_context.get('conversation_history', [])
        
        if conversation_history:
            # 检查最近的对话内容
            recent_content = conversation_history[-1] if conversation_history else {}
            if isinstance(recent_content, dict):
                content = recent_content.get('content', '')
                if content:
                    # 根据指示符类型返回适当的内容
                    if any(ind in indicator for ind in ['它怎么样', '这个呢', '那个如何']):
                        return content.split()[:5]  # 返回前5个词作为简洁引用
                    else:
                        return content

        return None

    def _get_cross_model_context(self, session_id: str, current_model: str) -> Dict[str, Any]:
        """
        获取跨模型上下文信息

        Args:
            session_id: 会话ID
            current_model: 当前模型

        Returns:
            跨模型上下文信息
        """
        if not self.context_integrator:
            return {}

        # 获取当前上下文
        current_context = self.context_integrator.get_context_for_intent_recognition(session_id)

        # 构建跨模型上下文
        cross_model_context = {
            'session_id': session_id,
            'current_model': current_model,
            'current_context': current_context,
            'model_switch_history': [],
            'shared_entities': [],
            'conversation_history': current_context.get('conversation_history', []),
            'last_accessed': datetime.now().isoformat()
        }

        # 保存到内部存储
        self.cross_model_contexts[session_id] = cross_model_context

        return cross_model_context

    def update_model_context(self, session_id: str, model_name: str, context_data: Dict[str, Any]) -> bool:
        """
        更新特定模型的上下文

        Args:
            session_id: 会话ID
            model_name: 模型名称
            context_data: 上下文数据

        Returns:
            是否更新成功
        """
        if session_id not in self.cross_model_contexts:
            self.cross_model_contexts[session_id] = {
                'session_id': session_id,
                'model_contexts': {},
                'model_switch_history': [],
                'shared_entities': [],
                'last_accessed': datetime.now().isoformat()
            }

        # 更新特定模型的上下文
        self.cross_model_contexts[session_id]['model_contexts'][model_name] = {
            **context_data,
            'updated_at': datetime.now().isoformat(),
            'model_name': model_name
        }

        # 记录模型切换历史
        self.cross_model_contexts[session_id]['model_switch_history'].append({
            'model_name': model_name,
            'switched_at': datetime.now().isoformat(),
            'context_keys': list(context_data.keys()) if isinstance(context_data, dict) else []
        })

        self.logger.debug(f"Updated context for model {model_name} in session {session_id}")
        return True

    def get_model_context(self, session_id: str, model_name: str) -> Optional[Dict[str, Any]]:
        """
        获取特定模型的上下文

        Args:
            session_id: 会话ID
            model_name: 模型名称

        Returns:
            模型上下文或None
        """
        if session_id in self.cross_model_contexts:
            model_contexts = self.cross_model_contexts[session_id].get('model_contexts', {})
            return model_contexts.get(model_name)

        return None

    def get_shared_context(self, session_id: str) -> Dict[str, Any]:
        """
        获取跨模型共享上下文

        Args:
            session_id: 会话ID

        Returns:
            共享上下文
        """
        if session_id in self.cross_model_contexts:
            return self.cross_model_contexts[session_id]

        return {}

    def resolve_contextual_reference(self, 
                                   text: str, 
                                   session_id: str, 
                                   reference_type: str = 'entity') -> Tuple[str, Optional[str]]:
        """
        解析上下文引用

        Args:
            text: 输入文本
            session_id: 会话ID
            reference_type: 引用类型

        Returns:
            (解析后的文本, 解析出的引用内容)
        """
        if not text or session_id not in self.cross_model_contexts:
            return text, None

        # 从文本中识别引用
        reference_content = None
        result_text = text

        if reference_type == 'entity':
            # 解析实体引用
            entities = []
            if self.entity_extractor:
                entities = self.entity_extractor.extract_entities_from_context(session_id)

            if entities:
                # 按置信度排序，取最高置信度的实体
                main_entity = max(entities, key=lambda e: e.confidence)
                # 检查文本中是否包含引用代词
                if any(pronoun in text for pronoun in ['它', '这', '那', '这个', '那个']):
                    reference_content = str(main_entity.value)
                    # 在适当的位置替换代词
                    for pronoun in ['它', '这', '那', '这个', '那个']:
                        if pronoun in text:
                            result_text = text.replace(pronoun, str(main_entity.value), 1)
                            break

        elif reference_type == 'topic':
            # 解析话题引用
            cross_context = self.cross_model_contexts[session_id]
            current_topic = cross_context.get('current_context', {}).get('current_topic', '')
            
            if current_topic and any(ref in text for ref in ['这个话题', '这个主题', '刚才的', '之前提到']):
                reference_content = current_topic
                result_text = text.replace('这个话题', current_topic).replace('刚才的', current_topic)

        elif reference_type == 'model_output':
            # 解析对前一个模型输出的引用
            model_switch_history = self.cross_model_contexts[session_id].get('model_switch_history', [])
            if model_switch_history:
                previous_output = model_switch_history[-1].get('context_keys', [])
                if previous_output and 'output' in str(previous_output):
                    reference_content = "先前模型的输出内容"
                    # 根据具体需求替换对前一个输出的引用

        return result_text, reference_content

    def maintain_context_consistency(self, session_id: str) -> bool:
        """
        维护跨模型上下文一致性

        Args:
            session_id: 会话ID

        Returns:
            是否维护成功
        """
        if session_id not in self.cross_model_contexts:
            return False

        # 可以在这里实现上下文一致性的具体维护逻辑
        # 例如：同步不同模型间的共享实体、参数等

        cross_context = self.cross_model_contexts[session_id]
        model_contexts = cross_context.get('model_contexts', {})

        # 同步共享参数
        shared_params = {}
        for model_name, context in model_contexts.items():
            if isinstance(context, dict) and 'parameters' in context:
                for param_name, param_value in context['parameters'].items():
                    if param_name not in shared_params:
                        shared_params[param_name] = param_value
                    else:
                        # 如果参数在多个模型上下文中存在，可以决定如何处理（取最新值、合并等）
                        pass

        # 将共享参数同步回各模型上下文
        for model_name in model_contexts.keys():
            if 'parameters' not in self.cross_model_contexts[session_id]['model_contexts'][model_name]:
                self.cross_model_contexts[session_id]['model_contexts'][model_name]['parameters'] = {}
            self.cross_model_contexts[session_id]['model_contexts'][model_name]['parameters'].update(shared_params)

        self.logger.debug(f"Maintained context consistency for session {session_id}")
        return True

    def validate_cross_model_reference_resolution(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证跨模型引用解析的准确性

        Args:
            test_cases: 测试用例列表

        Returns:
            验证结果
        """
        results = {
            'total_cases': len(test_cases),
            'correctly_resolved': 0,
            'errors': [],
            'accuracy': 0.0,
            'details': []
        }

        for i, test_case in enumerate(test_cases):
            try:
                input_text = test_case['input']
                session_id = test_case.get('session_id', f'test_session_{i}')
                expected_resolution = test_case['expected']
                reference_type = test_case.get('reference_type', 'entity')

                # 模拟上下文
                if session_id not in self.cross_model_contexts:
                    self.cross_model_contexts[session_id] = {
                        'current_context': {
                            'current_topic': test_case.get('topic', ''),
                            'parameters': test_case.get('parameters', {}),
                            'related_entities': test_case.get('entities', [])
                        }
                    }

                # 执行解析
                resolved_text, resolved_content = self.resolve_contextual_reference(
                    input_text, session_id, reference_type
                )

                is_correct = resolved_content == expected_resolution if expected_resolution else True
                result_detail = {
                    'input': input_text,
                    'expected': expected_resolution,
                    'resolved': resolved_content,
                    'is_correct': is_correct
                }

                results['details'].append(result_detail)

                if is_correct:
                    results['correctly_resolved'] += 1

            except Exception as e:
                error_detail = {
                    'index': i,
                    'input': test_case.get('input', 'unknown'),
                    'error': str(e)
                }
                results['errors'].append(error_detail)

        results['accuracy'] = results['correctly_resolved'] / max(1, results['total_cases'])
        return results