# 增强意图识别系统 - 设计文档

## 1. 系统架构
```
[用户输入]
    ↓
[上下文获取器] → [从现有SessionManager和ContextManager获取上下文]
    ↓
[QueryRewriter] → [重写后的查询 + 上下文信息]
    ↓
[PadatiousIntentRecognizer] → [语义意图结果]
    ↓
[原有意图识别器] → [规则意图结果]
    ↓
[意图融合器] → [最终意图结果]
    ↓
[上下文更新器] → [更新现有ContextManager]
    ↓
[输出意图结果]
```

## 2. 核心组件设计（基于现有组件增强，遵循SOLID原则）

### 2.1 PadatiousEnhancedIntentRecognizer（增强的Padatious意图识别器）
- **职责（SRP - 单一职责原则）**：专门负责语义意图识别，扩展原有意图识别功能
- **接口**：
  ```python
  class PadatiousEnhancedIntentRecognizer:
      def __init__(self, base_recognizer: EnhancedIntentRecognizer,
                   context_integrator: ContextIntegrator):
          """
          构造函数，使用依赖注入实现控制反转
          - base_recognizer: 原有意图识别器
          - context_integrator: 上下文集成器
          """
          self.base_recognizer = base_recognizer
          self.context_integrator = context_integrator
          self.intent_container = IntentContainer()  # Padatious容器

      def recognize_intent(self, text: str, session_id: str = "default") -> Union[Intent, ContextualIntent]:
          """
          识别用户意图，遵循现有接口但扩展功能
          - text: 用户输入文本
          - session_id: 会话ID用于上下文获取
          - 返回: 意图对象或上下文意图对象
          """
          # 从现有上下文管理器获取上下文信息
          context = self.context_integrator.get_context_for_intent_recognition(session_id)

          # 执行Padatious语义识别
          padatious_result = self._recognize_with_padatious(text, context)

          # 执行原有意图识别
          original_result = self.base_recognizer.recognize_intent(text, session_id)

          # 融合两个结果
          return self._fuse_results(padatious_result, original_result, context)

      def _recognize_with_padatious(self, text: str, context: Dict[str, Any]) -> Optional[Intent]:
          """
          使用Padatious进行语义意图识别
          - text: 输入文本
          - context: 上下文信息
          - 返回: 识别到的意图或None
          """
          # 将上下文信息注入到查询中，增强语义理解
          enriched_text = self.context_integrator.inject_context_to_query(text, context)

          # 使用Padatious进行意图识别
          result = self.intent_container.calc_intent(enriched_text)

          if result and result.conf > 0.5:  # 置信度阈值
              # 将Padatious结果转换为系统标准Intent格式
              return self._convert_padatious_result(result, text, context)
          return None

      def _convert_padatious_result(self, padatious_result, original_text: str,
                                  context: Dict[str, Any]) -> Intent:
          """
          将Padatious结果转换为系统标准Intent格式
          - padatious_result: Padatious识别结果
          - original_text: 原始输入文本
          - context: 上下文信息
          - 返回: 系统标准Intent对象
          """
          # 根据Padatious识别的意图名称映射到系统意图
          intent_name = self._map_padatious_intent_to_system(padatious_result.name)

          # 提取实体信息并转换为系统格式
          entities = self._extract_entities_from_padatious_result(padatious_result)

          return Intent(
              name=intent_name,
              confidence=padatious_result.conf,
              parameters=entities,
              source='padatious',  # 标识来源
              context_signals=self.context_integrator.extract_context_signals(original_text, context)
          )
  ```
- **遵循SOLID原则**：
  - SRP: 仅负责语义意图识别功能
  - OCP: 通过依赖注入可扩展
  - DIP: 依赖抽象而非具体实现
- **依赖**：原有EnhancedIntentRecognizer、ContextIntegrator、padatious库
- **集成点**：扩展现有的IntegratedIntentSystem

### 2.2 ContextIntegrator（上下文集成器）
- **职责（SRP）**：专门负责从现有系统获取上下文并为意图识别服务
- **接口**：
  ```python
  class ContextIntegrator:
      def __init__(self, session_manager: SessionManager,
                   context_manager: EnhancedContextManager):
          """
          构造函数，注入依赖
          - session_manager: 会话管理器
          - context_manager: 上下文管理器
          """
          self.session_manager = session_manager
          self.context_manager = context_manager

      def get_context_for_intent_recognition(self, session_id: str) -> Dict[str, Any]:
          """
          获取用于意图识别的上下文信息
          - session_id: 会话ID
          - 返回: 包含上下文信息的字典
          """
          # 获取现有上下文
          context = self.context_manager.get_conversation_context(session_id)
          if not context:
              return {}

          # 获取会话历史
          history = self.session_manager.get_session(session_id)
          if not history:
              session_history = []
          else:
              # 限制历史长度以提高性能
              session_history = history.history[-5:] if hasattr(history, 'history') else []

          # 提取关键上下文信息
          context_info = {
              'session_id': session_id,
              'current_topic': context.topic if hasattr(context, 'topic') else '',
              'current_intent': context.current_intent if hasattr(context, 'current_intent') else '',
              'intent_history': context.intent_history if hasattr(context, 'intent_history') else [],
              'parameters': context.get_filled_parameters() if hasattr(context, 'get_filled_parameters') else {},
              'conversation_history': self._format_dialogue_history(session_history),
              'related_entities': list(context.related_entities) if hasattr(context, 'related_entities') else []
          }

          return context_info

      def inject_context_to_query(self, text: str, context: Dict[str, Any]) -> str:
          """
          将上下文信息注入到查询文本中，增强语义理解
          - text: 原始查询文本
          - context: 上下文信息
          - 返回: 注入上下文后的文本
          """
          if not context:
              return text

          # 处理代词消解
          resolved_text = self._resolve_pronouns(text, context)

          # 如果当前话题与上下文相关，增强文本
          current_topic = context.get('current_topic', '')
          if current_topic and self._is_topic_relevant(text, current_topic):
              # 添加上下文话题信息
              return f"关于{current_topic}，{resolved_text}"

          return resolved_text

      def _resolve_pronouns(self, text: str, context: Dict[str, Any]) -> str:
          """
          处理代词消解
          - text: 输入文本
          - context: 上下文信息
          - 返回: 消解代词后的文本
          """
          # 常见代词映射
          pronouns = {
              '它': '当前讨论的对象',
              '这': '当前讨论的内容',
              '那': '之前提到的内容',
              '这个': '当前讨论的对象',
              '那个': '之前提到的对象',
              '这些': '当前讨论的内容',
              '那些': '之前提到的内容'
          }

          # 从上下文中提取可能的实体
          entities = context.get('related_entities', [])

          # 如果有明确实体，优先使用实体替换代词
          for entity in entities:
              if f'它' in text and entity in text:
                  # 避免过度替换，只在合适情况下替换
                  text = re.sub(r'它(?=.*' + re.escape(entity) + ')', entity, text)
              elif f'这' in text and len(entity) > 1 and entity in text:
                  text = re.sub(r'这(?=.*' + re.escape(entity) + ')', entity, text)

          # 一般性代词替换
          for pronoun, replacement in pronouns.items():
              text = text.replace(pronoun, replacement)

          return text

      def extract_context_signals(self, query: str, context: Dict[str, Any]) -> Dict[str, float]:
          """
          从查询和上下文中提取上下文信号，用于意图识别
          - query: 查询文本
          - context: 上下文信息
          - 返回: 信号名称到权重的映射
          """
          signals = {}

          # 话题连续性信号
          current_topic = context.get('current_topic', '')
          if current_topic:
              # 检查查询是否与当前话题相关
              if self._calculate_topic_relevance(query, current_topic) > 0.7:
                  signals['topic_continuity'] = 1.0
              else:
                  signals['topic_continuity'] = 0.3

          # 会话连续性信号
          intent_history = context.get('intent_history', [])
          if intent_history:
              last_intent = intent_history[-1] if intent_history else ''
              if last_intent and self._is_intent_relevant(query, last_intent):
                  signals['intent_continuity'] = 0.8

          # 实体相关性信号
          entities = context.get('parameters', {})
          for entity_name, entity_value in entities.items():
              if str(entity_value) in query or entity_name in query:
                  signals[f'entity_{entity_name}_relevance'] = 0.9

          return signals
  ```
- **遵循SOLID原则**：
  - SRP: 仅负责上下文获取和注入
  - OCP: 可扩展处理更多上下文类型
  - DIP: 依赖会话和上下文管理器的抽象接口
- **依赖**：现有SessionManager、EnhancedContextManager
- **复用**：直接使用现有上下文管理机制

### 2.3 IntentFuser（意图融合器）
- **职责（SRP - 单一职责原则）**：专门负责融合Padatious和原有意图识别的结果
- **接口**：
  ```python
  class IntentFuser:
      def __init__(self):
          # 定义不同来源意图的权重
          self.intent_weights = {
              'padatious': 0.7,  # Padatious权重
              'original': 0.3,   # 原有意图识别权重
          }

      def fuse_intents(self, padatious_result: Optional[Intent],
                      original_result: Union[Intent, ContextualIntent],
                      context: Dict[str, Any]) -> Union[Intent, ContextualIntent]:
          """
          融合两个意图识别结果
          - padatious_result: Padatious识别结果
          - original_result: 原有意图识别结果
          - context: 上下文信息
          - 返回: 融合后的意图结果
          """
          if not padatious_result:
              # 如果Padatious没有结果，返回原有意图
              return self._adjust_confidence_with_context(original_result, context)

          if not original_result:
              # 如果原有意图识别没有结果，返回Padatious结果
              return self._adjust_confidence_with_context(padatious_result, context)

          # 两个都有结果，需要融合
          return self._perform_intent_fusion(padatious_result, original_result, context)

      def _perform_intent_fusion(self, padatious_result: Intent,
                               original_result: Union[Intent, ContextualIntent],
                               context: Dict[str, Any]) -> Union[Intent, ContextualIntent]:
          """
          执行意图融合逻辑
          """
          # 获取上下文信号
          context_signals = context.get('context_signals', {})

          # 计算融合后的置信度
          fused_confidence = self._calculate_fused_confidence(
              padatious_result.confidence,
              original_result.confidence if hasattr(original_result, 'confidence') else 0.5,
              context_signals
          )

          # 选择主要意图（基于置信度和上下文相关性）
          if fused_confidence > 0.6:  # 使用融合后置信度作为判断标准
              # 基于上下文选择更好的意图
              if self._should_prefer_padatious(padatious_result, original_result, context):
                  # 使用Padatious结果，但结合原有意图的参数
                  final_intent = Intent(
                      name=padatious_result.name,
                      confidence=fused_confidence,
                      parameters={**getattr(original_result, 'parameters', {}),
                                **padatious_result.parameters},
                      source='fused_padatious_preferred'
                  )
              else:
                  # 使用原有意图结果，但结合Padatious的语义理解
                  final_intent = Intent(
                      name=original_result.name,
                      confidence=fused_confidence,
                      parameters={**getattr(original_result, 'parameters', {}),
                                **padatious_result.parameters},
                      source='fused_original_preferred'
                  )
          else:
              # 置信度太低，返回原有意图以保证稳定性
              final_intent = original_result
              final_intent.confidence = fused_confidence

          return final_intent

      def _calculate_fused_confidence(self, padatious_conf: float, original_conf: float,
                                    context_signals: Dict[str, float]) -> float:
          """
          基于上下文信号计算融合置信度
          """
          # 基础融合：加权平均
          base_confidence = (padatious_conf * self.intent_weights['padatious'] +
                           original_conf * self.intent_weights['original'])

          # 应用上下文信号调整
          for signal_name, signal_weight in context_signals.items():
              if signal_name == 'topic_continuity':
                  # 话题连续性高，增加置信度
                  base_confidence = min(base_confidence + 0.1 * signal_weight, 1.0)
              elif signal_name == 'intent_continuity':
                  # 意图连续性高，增加置信度
                  base_confidence = min(base_confidence + 0.05 * signal_weight, 1.0)

          return base_confidence

      def _should_prefer_padatious(self, padatious_result: Intent,
                                 original_result: Union[Intent, ContextualIntent],
                                 context: Dict[str, Any]) -> bool:
          """
          判断是否应该优先选择Padatious结果
          """
          # 如果Padatious置信度明显更高，优先选择
          if padatious_result.confidence > original_result.confidence + 0.2:
              return True

          # 如果上下文信号支持Padatious结果，优先选择
          context_signals = context.get('context_signals', {})
          if any('entity' in signal and signal.endswith('_relevance')
                 for signal in context_signals.keys()):
              # 如果有实体相关性信号，倾向于使用语义理解更好的Padatious
              return True

          # 默认情况下，如果置信度接近，倾向于使用原有意图以保持稳定性
          return False
  ```
- **遵循SOLID原则**：
  - SRP: 仅负责意图融合逻辑
  - OCP: 通过策略模式可扩展融合策略
  - ISP: 提供专门的融合接口
- **依赖**：Padatious和原有意图识别结果
- **集成点**：在IntegratedIntentSystem中使用

### 2.4 AntiMisrecognitionGuard（防误识别守护器）
- **职责（SRP - 单一职责原则）**：专门负责防止普通对话被误识别为论文下载等意图
- **接口**：
  ```python
  class AntiMisrecognitionGuard:
      def __init__(self):
          # 专门针对论文相关意图的权重调整
          self.paper_intent_penalty = -0.3  # 对论文意图的惩罚权重
          self.chat_intent_boost = 0.2      # 对聊天意图的增强权重
          self.misrecognition_threshold = 0.7  # 误识别风险阈值

      def apply_antimisrecognition_protection(self,
                                            intent_result: Union[Intent, ContextualIntent],
                                            context: Dict[str, Any]) -> Union[Intent, ContextualIntent]:
          """
          对意图识别结果应用防误识别保护
          - intent_result: 原意图识别结果
          - context: 上下文信息
          - 返回: 经过防误识别保护的意图结果
          """
          # 检查是否存在误识别风险
          if self._is_misrecognition_risk(intent_result, context):
              # 应用置信度惩罚
              protected_result = self._apply_protection_penalty(intent_result)
              return protected_result
          else:
              return intent_result

      def _is_misrecognition_risk(self, intent_result: Union[Intent, ContextualIntent],
                               context: Dict[str, Any]) -> bool:
          """
          检查是否存在误识别风险，特别是将普通对话误识别为论文下载
          """
          # 获取当前上下文话题
          current_topic = context.get('current_topic', '').lower()
          intent_history = context.get('intent_history', [])
          parameters = context.get('parameters', {})

          # 检查是否是论文相关意图
          paper_related_intents = ['search_papers', 'download_paper', 'papers']
          is_paper_intent = getattr(intent_result, 'name', '') in paper_related_intents

          # 检查上下文是否为非学术话题
          non_academic_context = any(keyword in current_topic for keyword in
                                   ['你好', 'hi', 'hello', '谢谢', '帮助', '助手', '聊天', '闲聊', '随便', '问题', '为什么', '啥', '啊'])

          # 检查意图历史是否也支持非学术语境
          recent_non_academic_intents = ['chat', 'question', 'personal_assistant']
          non_academic_history = any(intent in recent_non_academic_intents for intent in intent_history[-3:])

          # 检查参数是否与论文无关
          paper_unrelated_params = any(keyword in str(parameters).lower() for keyword in ['role', 'roles', '助手', '帮助'])

          # 如果是论文意图但上下文是非学术话题，则存在误识别风险
          return is_paper_intent and (non_academic_context or non_academic_history or paper_unrelated_params)

      def _apply_protection_penalty(self, intent_result: Union[Intent, ContextualIntent]) -> Union[Intent, ContextualIntent]:
          """
          对存在误识别风险的意图结果应用保护性惩罚
          """
          # 对论文相关意图应用惩罚，降低置信度
          if hasattr(intent_result, 'name') and intent_result.name in ['search_papers', 'download_paper', 'papers']:
              # 降低论文意图的置信度
              original_conf = getattr(intent_result, 'confidence', 0.0)
              adjusted_conf = max(original_conf + self.paper_intent_penalty, 0.1)  # 最低置信度0.1
              intent_result.confidence = adjusted_conf
          elif hasattr(intent_result, 'name') and intent_result.name in ['chat', 'question']:
              # 对聊天意图应用增强
              original_conf = getattr(intent_result, 'confidence', 0.0)
              adjusted_conf = min(original_conf + self.chat_intent_boost, 1.0)  # 最高置信度1.0
              intent_result.confidence = adjusted_conf

          return intent_result
  ```
- **遵循SOLID原则**：
  - SRP: 仅负责防误识别保护功能
  - OCP: 可扩展更多保护策略
  - DIP: 依赖意图和上下文抽象
- **专门针对需求3.4（语义消歧能力）**：实现防止普通对话被误识别为论文下载的机制
- **目标**：确保"你好啊，为啥找不到roles"不被误识别为论文意图
- **依赖**：意图结果和上下文信息
- **集成点**：在意图识别后处理流程中使用

### 2.5 SemanticDisambiguator（语义消歧器）
- **职责（SRP - 单一职责原则）**：专门负责语义层面的意图消歧
- **接口**：
  ```python
  class SemanticDisambiguator:
      def disambiguate_intent(self,
                            candidate_intents: List[Intent],
                            context: Dict[str, Any]) -> Intent:
          """
          对多个候选意图进行语义消歧，选择最合适的意图
          - candidate_intents: 候选意图列表
          - context: 上下文信息
          - 返回: 经语义消歧后选择的最佳意图
          """
          # 基于上下文信息对候选意图进行评分
          scored_intents = []
          for intent in candidate_intents:
              score = self._calculate_contextual_score(intent, context)
              scored_intents.append((intent, score))

          # 选择评分最高的意图
          best_intent, best_score = max(scored_intents, key=lambda x: x[1])
          return best_intent

      def _calculate_contextual_score(self, intent: Intent, context: Dict[str, Any]) -> float:
          """
          基于上下文计算意图的匹配分数
          """
          base_score = getattr(intent, 'confidence', 0.0)

          # 获取上下文信息
          current_topic = context.get('current_topic', '').lower()
          intent_history = context.get('intent_history', [])
          parameters = context.get('parameters', {})

          # 根据上下文调整分数
          if intent.name in ['chat', 'question'] and any(keyword in current_topic
                   for keyword in ['你好', 'hi', 'hello', '谢谢', '帮助', '助手', '聊天', '问题']):
              # 普通对话意图在聊天上下文中得分增加
              base_score += 0.2
          elif intent.name in ['search_papers', 'download_paper'] and not any(keyword in current_topic
                   for keyword in ['论文', 'arxiv', '学术', '研究', 'paper', 'download']):
              # 论文意图在非学术上下文中得分降低
              base_score -= 0.3

          return min(base_score, 1.0)  # 限制最大分数为1.0
  ```
- **遵循SOLID原则**：
  - SRP: 仅负责语义消歧
  - OCP: 可扩展更多消歧策略
- **依赖**：候选意图列表和上下文信息
- **集成点**：在意图识别最终决策阶段使用

### 2.4 QueryRewriter（查询重写器，基于现有session_context_recognizer）
- **职责（SRP）**：专门负责查询文本的预处理和上下文注入
- **接口**：
  ```python
  class QueryRewriter:
      def __init__(self, entity_extractor: EntityExtractor):
          """
          构造函数
          - entity_extractor: 实体提取器，用于指代消解
          """
          self.entity_extractor = entity_extractor

      def rewrite_query_with_context(self, text: str, session_id: str) -> str:
          """
          基于会话上下文重写查询
          - text: 原始查询文本
          - session_id: 会话ID
          - 返回: 重写后的查询文本
          """
          # 获取会话中的相关实体
          entities = self.entity_extractor.extract_entities_from_context(session_id)

          # 执行代词消解
          resolved_text = self.resolve_pronouns(text, entities)

          # 执行省略表达补全
          completed_text = self.expand_ellipsis(resolved_text, entities)

          return completed_text

      def resolve_pronouns(self, text: str, entities: List[Entity]) -> str:
          """
          执行代词消解
          - text: 输入文本
          - entities: 上下文中的实体列表
          - 返回: 消解代词后的文本
          """
          # 定义代词消解规则
          pronoun_rules = [
              # 规则格式：(代词模式, 对应实体类型, 替换逻辑)
              ('它', ['paper_id', 'topic', 'title'], self._resolve_it_pronoun),
              ('这', ['topic', 'argument', 'concept'], self._resolve_this_pronoun),
              ('那', ['topic', 'argument', 'concept'], self._resolve_that_pronoun),
              ('这个', ['topic', 'argument', 'concept'], self._resolve_this_pronoun),
              ('那个', ['topic', 'argument', 'concept'], self._resolve_that_pronoun),
          ]

          result_text = text

          for pronoun, entity_types, resolver_func in pronoun_rules:
              # 查找文本中的代词
              if pronoun in result_text:
                  # 在实体中找到最相关的实体进行替换
                  relevant_entity = self._find_most_relevant_entity(entities, entity_types)
                  if relevant_entity:
                      # 应用消解规则
                      result_text = resolver_func(result_text, pronoun, relevant_entity.value)

          return result_text

      def _resolve_it_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
          """
          解析"它"代词
          """
          # 使用正则替换，确保上下文准确性
          return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

      def _resolve_this_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
          """
          解析"这/这个"代词
          """
          return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

      def _resolve_that_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
          """
          解析"那/那个"代词
          """
          return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

      def _find_most_relevant_entity(self, entities: List[Entity],
                                   target_types: List[str]) -> Optional[Entity]:
          """
          根据类型查找最相关的实体
          """
          # 按类型匹配优先级查找
          for entity_type in target_types:
              for entity in entities:
                  if entity.entity_type == entity_type:
                      return entity

          # 如果没有精确匹配，返回第一个匹配的实体
          for entity in entities:
              if entity.entity_type in target_types:
                  return entity

          return None

      def expand_ellipsis(self, text: str, context: Dict[str, Any]) -> str:
          """
          补全省略表达
          - text: 输入文本
          - context: 上下文信息
          - 返回: 补全后的文本
          """
          # 常见省略表达映射
          ellipsis_patterns = [
              (r'是', r'是(上文提到的内容|之前讨论的|前面说的)'),
              (r'好', r'好(按你说的|这样|这样办)'),
              (r'行', r'行(按计划|这样|可以)'),
              (r'对', r'对(你说的|上文|这样)'),
          ]

          result_text = text

          for pattern, replacement in ellipsis_patterns:
              result_text = re.sub(pattern, replacement, result_text)

          return result_text
  ```
- **遵循SOLID原则**：
  - SRP: 仅负责查询文本重写
  - OCP: 可扩展更多重写规则
- **复用**：基于现有SessionContextAwareRecognizer扩展理念
- **集成点**：与现有SessionManager和EnhancedContextManager集成

### 2.5 EntityExtractor（实体提取器）
- **职责（SRP）**：专门负责从对话历史和上下文中提取实体
- **接口**：
  ```python
  class EntityExtractor:
      def __init__(self, session_manager: SessionManager,
                   context_manager: EnhancedContextManager):
          """
          构造函数
          - session_manager: 会话管理器
          - context_manager: 上下文管理器
          """
          self.session_manager = session_manager
          self.context_manager = context_manager

      def extract_entities_from_context(self, session_id: str) -> List[Entity]:
          """
          从会话上下文中提取实体
          - session_id: 会话ID
          - 返回: 实体列表
          """
          # 获取会话历史
          session = self.session_manager.get_session(session_id)
          if not session:
              return []

          # 从历史对话中提取实体
          entities = []
          if hasattr(session, 'history'):
              for turn in session.history[-10:]:  # 最近10次对话
                  entities.extend(self._extract_entities_from_dialogue_turn(turn))

          # 获取当前上下文中的参数实体
          context = self.context_manager.get_conversation_context(session_id)
          if context:
              params = context.get_filled_parameters()
              for param_name, param_value in params.items():
                  entities.append(Entity(
                      name=param_name,
                      value=param_value,
                      position=(0, len(str(param_value))),
                      confidence=0.9,
                      entity_type=self._infer_entity_type(param_name, param_value)
                  ))

          return entities

      def _extract_entities_from_dialogue_turn(self, turn: DialogueTurn) -> List[Entity]:
          """
          从对话回合中提取实体
          - turn: 对话回合
          - 返回: 从该回合提取的实体列表
          """
          entities = []

          # 使用正则表达式提取常见实体类型
          content = turn.content

          # 提取论文ID (如 arXiv ID: 1234.56789)
          paper_id_matches = re.finditer(r'\b(\d{4}\.\d{4,5}(v\d+)?)\b', content)
          for match in paper_id_matches:
              entities.append(Entity(
                  name='paper_id',
                  value=match.group(1),
                  position=match.span(),
                  confidence=1.0,
                  entity_type='paper_id'
              ))

          # 提取主题词
          topic_matches = re.finditer(r'关于\s*([^\s，。,.\n]+)[\s，。,.\n]', content)
          for match in topic_matches:
              topic = match.group(1).strip('的')
              if len(topic) > 1:  # 避免单字符
                  entities.append(Entity(
                      name='topic',
                      value=topic,
                      position=match.span(),
                      confidence=0.8,
                      entity_type='topic'
                  ))

          # 提取标题（如"创建维基 XXX"）
          title_matches = re.finditer(r'(?:创建|写个|新建|编辑)\s*(?:维基|百科|词条)\s+([^\s，。,.\n]+)', content)
          for match in title_matches:
              title = match.group(1)
              entities.append(Entity(
                  name='title',
                  value=title,
                  position=match.span(),
                  confidence=0.85,
                  entity_type='title'
              ))

          return entities

      def _infer_entity_type(self, param_name: str, param_value: Any) -> str:
          """
          推断参数的实体类型
          """
          type_mapping = {
              'topic': 'topic',
              'title': 'title',
              'query': 'query',
              'paper_id': 'paper_id',
              'search_query': 'query',
              'role_name': 'role',
              'model_name': 'model'
          }

          if param_name in type_mapping:
              return type_mapping[param_name]

          # 根据值的内容推断类型
          str_value = str(param_value).lower()
          if any(keyword in str_value for keyword in ['arxiv', '1234.', 'paper', 'article']):
              return 'paper_id'
          elif len(str_value) > 30:  # 看起来像内容
              return 'content'
          else:
              return 'general'
  ```
- **遵循SOLID原则**：
  - SRP: 仅负责实体提取
  - DIP: 依赖会话和上下文管理器的抽象接口
- **依赖**：现有SessionManager对话历史、EnhancedContextManager

## 3. 数据结构设计（基于现有模型）

### 3.1 Context（复用现有模型）
- **复用**：直接使用现有ConversationContext或ContextualIntent中的上下文字段
- **扩展**：添加Padatious相关字段
- **兼容性**：保持与现有Session、DialogueTurn模型兼容

### 3.2 Intent（扩展现有Intent模型）
- **复用**：继承现有Intent类
- **扩展**：
  ```python
  class EnhancedIntent(Intent):
      source: str  # 'padatious', 'regex', 'original', 'fused'
      context_signals: Dict[str, float]  # 上下文信号及其权重
      confidence_adjustments: Dict[str, float]  # 置信度调整原因和幅度
  ```

## 4. 系统集成设计

### 4.1 与IntegratedIntentSystem集成
- **扩展点**：在recognize_intent方法中加入Padatious逻辑
- **兼容性策略**：
  - 保持原有方法签名不变
  - 添加Padatious相关参数作为可选参数
  - 错误回退到原有意图识别器
- **SOLID体现**：
  - OCP: 通过策略模式扩展功能
  - LSP: 保持原有接口行为

### 4.2 与SessionManager集成
- **复用**：直接使用现有SessionManager进行会话管理
- **扩展**：在现有session history基础上做上下文分析
- **数据一致性**：保持与现有数据库表结构兼容

### 4.3 与EnhancedContextManager集成
- **复用**：直接使用现有上下文管理机制
- **增强**：在现有参数、实体追踪基础上增加语义理解
- **兼容性**：保持与现有上下文API兼容

## 5. 算法设计

### 5.1 上下文感知意图识别算法
1. 使用ContextIntegrator从现有SessionManager获取上下文
2. 使用QueryRewriter处理代词消解和上下文引用
3. 并行执行Padatious和原有意图识别器
4. 使用IntentFuser融合结果，考虑上下文相关性
5. 更新现有ContextManager

### 5.2 上下文增强策略
- 利用现有对话历史中的实体进行指代消解
- 基于现有话题连续性调整意图置信度
- 使用现有session context进行意图消歧

### 5.3 语义消歧与防误识别算法
- **核心机制**：通过AntiMisrecognitionGuard和SemanticDisambiguator组件协同工作，识别"论文"相关词汇在现有上下文中的含义，防止普通对话被误识别为论文下载意图
- **上下文判断逻辑**：
  - 如果现有上下文是非学术话题（如问候、聊天、帮助请求等），AntiMisrecognitionGuard将显著降低论文相关意图权重（-0.3置信度惩罚）
  - 如果现有上下文是学术讨论或知识查询，SemanticDisambiguator将适当提高论文意图权重
  - 检查用户输入中是否包含明确的论文/学术关键词（如arXiv, research, academic, journal, publication等）
  - 检查上下文中是否有明确的论文ID或搜索需求
- **具体实现**：
  - AntiMisrecognitionGuard实现`_is_misrecognition_risk`方法来检测误识别风险
  - AntiMisrecognitionGuard实现`_apply_protection_penalty`方法对误识别风险应用置信度惩罚
  - SemanticDisambiguator实现`_calculate_contextual_score`方法进行语义消歧评分
  - 当检测到误识别风险时，系统会：
    1. AntiMisrecognitionGuard降低论文相关意图的置信度
    2. SemanticDisambiguator提高普通对话意图的上下文匹配分数
    3. 确保"你好啊，为啥找不到roles"等普通对话不会被识别为论文意图
- **准确率目标**：普通对话识别准确率≥95%，论文意图误识别率≤3%，整体准确率≥92%

## 6. 错误处理与恢复

### 6.1 Padatious失败处理
- 自动回退到原有意图识别器
- 记录失败日志用于后续分析
- 保持现有错误处理机制不变

### 6.2 上下文不一致处理
- 利用现有ContextManager的过期检测机制
- 保持现有上下文清理策略
- 与现有session状态管理兼容

## 7. 部署配置

### 7.1 环境依赖
- Python >= 3.8
- padatious >= 0.4.0
- 现有DAIP-LIVE依赖（无需额外数据库）

### 7.2 配置参数
- Padatious启用开关
- 融合权重配置
- 与现有配置文件格式兼容