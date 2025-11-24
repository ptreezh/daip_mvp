"""
完整的语义匹配器实现
"""
import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass 
class SemanticMatchResult:
    """语义匹配结果"""
    intent_name: str
    confidence: float
    parameters: Dict[str, Any]
    explanation: str


class SemanticSimilarityMatcher:
    """
    语义相似度匹配器
    使用预定义的同义词典和模式匹配来检测语义相似性
    """
    
    def __init__(self):
        # 定义同义词组和相关表达模式
        self.synonym_groups = {
            # 维基相关同义表达
            "wiki_creation": [
                r".*[创建|新建|写|编辑|构建|创建个|做一个|建立|搭建].*[维基|wiki|百科|词条|页面|条目].*",
                r".*[维基|wiki|百科|词条|页面|条目].*[创建|新建|编辑|写|建设].*",
                r".*[协作|一起|共同|联合|多人|多角色|多模型].*[创建|写|编辑].*[维基|百科|词条|页面].*",
                r".*[一起|协同|多方|多模型].*[构建|制作|建立].*[维基|百科|知识库].*",
                r".*[词条|维基|百科].*[协作|共同].*[编辑|编写|制作]"
            ],
            
            # 辩论相关同义表达
            "debate_start": [
                r".*[辩论|讨论|争辩|探讨|交流].*[开始|发起|启动|开始一个].*",
                r".*[多模型|多智能体|AI|多个].*[辩论|讨论|交流].*",
                r".*[协作|多人|团队].*[辩论|讨论|探讨].*",
                r".*[开始|启动|发起].*[辩论|讨论|争辩|交流].*[AI|模型|智能体].*",
                r".*[AI|模型|智能体].*[一起|共同|协作].*[辩论|讨论]"
            ],
            
            # 技能执行相关同义表达
            "skill_execution": [
                r".*[帮我|请帮我|帮我一下|麻烦你|劳驾].*[分析|处理|总结|搜索|查找|生成|翻译|整理].*",
                r".*[请|请求|需要].*[助手|AI|智能].*[分析|处理|总结|搜索|查找|生成|翻译|整理].*",
                r".*[执行|运行|启动].*[技能|工具|功能|程序|处理].*",
                r".*[解析|理解|审视|评估].*[以下|这段|此].*[内容|文本|信息|材料|文档].*",
                r".*[帮我|请帮我].*[帮我|帮助].*[这个|这段|这些].*[内容|文本|文档]"
            ]
        }
        
        # 关键词提取模式
        self.keyword_extraction_patterns = {
            "wiki_creation": [
                r"(?:创建|新建|写|编辑|构建|创建个|做一个|建立|搭建).*(?:维基|wiki|百科|词条|页面|条目)\s+(.+?)(?:\s*[。？！]|$)",
                r"(?:维基|wiki|百科|词条|页面|条目)\s+(.+?)(?:\s*[。？！]|$)",
                r".*[协作|一起|共同|联合|多人|多方].*[创建|写|编辑].*\s+(.+?)(?:\s*[。？！]|$)",
                r".*[创建|写|协作].*[维基|百科|词条].*\s+(.+?)(?:\s*[。？！]|$)"
            ],
            
            "debate_start": [
                r"(?:辩论|讨论|争辩|探讨)\s+(.+?)(?:\s*[。？！]|$)",
                r"(?:关于|就).*(?:的|关于).*(?:辩论|讨论|争辩)\s+(.+?)(?:\s*[。？！]|$)",
                r".*[辩论|讨论|交流]\s+(.+?)(?:\s*[。？！]|$)",
                r".*[多模型|多智能体|AI|多个].*[辩论|讨论].*\s+(.+?)(?:\s*[。？！]|$)"
            ],
            
            "skill_execution": [
                r"(?:帮我|请帮我|帮我一下).*[:：\s]*(.+?)(?:\s*[。？！]|$)",
                r".*[:：]\s*(.+?)(?:\s*[。？！]|$)",
                r"(?:分析|处理|总结|搜索|查找|生成|翻译|整理)\s+(.+?)(?:\s*[。？！]|$)",
                r".*[帮我|请帮我|帮我一下|请帮我].*[分析|处理|总结|搜索|查找|生成|翻译|整理]\s+(.+?)(?:\s*[。？！]|$)"
            ]
        }
        
        # 意图映射
        self.intent_mappings = {
            "wiki_creation": "create_wiki",
            "debate_start": "start_debate", 
            "skill_execution": "execute_skill"
        }

    def compute_semantic_similarity(self, text: str, intent_category: str) -> float:
        """计算文本与意图类别的语义相似度"""
        patterns = self.synonym_groups.get(intent_category, [])
        
        similarity_scores = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # 匹配成功，计算基础权重
                base_score = 0.6  # 基础匹配得分
                # 根据匹配的详细程度调整得分
                similarity_scores.append(base_score)
        
        # 如果有关键词提取，增加权重
        keyword_params = self._extract_keywords_by_category(text, intent_category)
        if keyword_params and any(val for val in keyword_params.values() if val):  # 如果提取到有效参数
            similarity_scores = [score + 0.2 for score in similarity_scores]  # 增加参数匹配权重
        
        return max(similarity_scores) if similarity_scores else 0.0

    def match_intent_by_semantics(self, text: str) -> SemanticMatchResult:
        """基于语义匹配意图"""
        best_intent = None
        best_confidence = 0.0
        best_params = {}

        for category, _ in self.synonym_groups.items():
            confidence = self.compute_semantic_similarity(text, category)

            if confidence > best_confidence and confidence > 0.5:  # 阈值设定为0.5
                # 提取关键词参数
                params = self._extract_keywords_by_category(text, category)
                intent_name = self.intent_mappings.get(category, category)

                if intent_name:
                    best_intent = intent_name
                    best_confidence = confidence
                    best_params = params

        if best_intent:
            return SemanticMatchResult(
                intent_name=best_intent,
                confidence=best_confidence,
                parameters=best_params,
                explanation=f"通过语义相似度匹配识别: {best_intent} (置信度: {best_confidence:.2f})"
            )
        else:
            return SemanticMatchResult(
                intent_name="question",
                confidence=0.3,
                parameters={"query": text},
                explanation="语义匹配未找到高置信度意图，返回默认问题类型"
            )

    def _extract_keywords_by_category(self, text: str, intent_category: str) -> Dict[str, Any]:
        """基于类别提取关键词"""
        patterns = self.keyword_extraction_patterns.get(intent_category, [])
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m and m.groups():
                keyword = m.group(1).strip()
                if keyword and keyword != text.strip():  # 确保提取的不是整个文本
                    if intent_category == "wiki_creation":
                        return {"title": keyword, "content": "", "tags": []}
                    elif intent_category == "debate_start":
                        return {"topic": keyword, "roles": None, "rounds": 3}
                    elif intent_category == "skill_execution":
                        return {"content": keyword, "skill_type": "general", "original_request": text}
        
        return {"raw_text": text, "extracted": False}
        
    def get_all_semantic_matches(self, text: str) -> List[SemanticMatchResult]:
        """获取所有语义匹配结果（用于模糊匹配场景）"""
        all_matches = []
        
        for category, _ in self.synonym_groups.items():
            confidence = self.compute_semantic_similarity(text, category)
            if confidence > 0.3:  # 只要超过低阈值就返回
                params = self._extract_keywords_by_category(text, category)
                intent_name = self.intent_mappings.get(category, category)
                
                match_result = SemanticMatchResult(
                    intent_name=intent_name,
                    confidence=confidence,
                    parameters=params,
                    explanation=f"语义匹配结果: {intent_name} (置信度: {confidence:.2f})"
                )
                
                all_matches.append(match_result)
        
        # 按置信度降序排列
        all_matches.sort(key=lambda x: x.confidence, reverse=True)
        return all_matches


if __name__ == "__main__":
    print("="*70)
    print("🧠 语义匹配器实现 - 完整版")
    print("="*70)
    
    matcher = SemanticSimilarityMatcher()
    
    test_cases = [
        ("创建维基 人工智能历史", "维基创建测试"),
        ("一起协作写个维基 量子计算", "协作维基创建测试"),
        ("多模型辩论 深度学习未来", "多模型辩论测试"),
        ("帮我分析这段文本内容", "技能执行测试"),
        ("请帮我处理这个文档", "技能执行测试2"),
    ]
    
    print("\\n🔍 语义匹配结果:")
    for text, description in test_cases:
        result = matcher.match_intent_by_semantics(text)
        print(f"  {description}: '{text}'")
        print(f"    意图: {result.intent_name}")
        print(f"    置信度: {result.confidence:.2f}")
        print(f"    参数: {result.parameters}")
        print()
    
    print("✅ 语义匹配器实现完成!")