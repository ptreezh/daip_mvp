"""
语义匹配器实现 - 支持自然语言变体和同义表达的理解
文件: semantic_matcher.py
根据TDD原则：实现使测试通过的功能
"""
import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime


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
                r".*[创建|新建|写|编辑|构建|创建个|做一个|建立|搭建].*[维基|wiki|百科|词条|页面|条目]",
                r".*[维基|wiki|百科].*[创建|新建|编辑|写|建设]",
                r".*[协作|一起|共同|联合].*[创建|写|编辑].*[维基|百科|词条|页面]",
                r".*[一起|协同|多方|多模型].*[构建|制作|建立].*[维基|百科|知识库]"
            ],
            
            # 辩论相关同义表达
            "debate_start": [
                r".*[辩论|讨论|争辩|探讨|交流].*[开始|发起|启动|开始一个]",
                r".*[多模型|多智能体|AI|多个].*[辩论|讨论|交流]",
                r".*[协作|多人|团队].*[辩论|讨论|探讨]",
                r".*[开始|启动|发起].*[辩论|讨论|争辩|交流].*[AI|模型|智能体]"
            ],
            
            # 技能执行相关同义表达
            "skill_execution": [
                r".*[帮我|请帮我|帮我一下|麻烦你|劳驾].*[分析|处理|总结|搜索|查找|生成|翻译|整理]",
                r".*[请|请求|需要].*[助手|AI|智能].*[分析|处理|总结|搜索|查找|生成|翻译|整理]",
                r".*[执行|运行|启动].*[技能|工具|功能|程序|处理]",
                r".*[解析|理解|审视|评估].*[以下|这段|此].*[内容|文本|信息|材料|文档]"
            ]
        }
        
        # 语义权重映射
        self.intent_mappings = {
            "wiki_creation": "create_wiki",
            "debate_start": "start_debate",
            "skill_execution": "execute_skill"
        }

        # 关键词提取模式
        self.keyword_extraction_patterns = {
            "wiki_creation": [
                r"(?:创建|新建|写|编辑|构建|创建个|做一个|建立|搭建).*(?:维基|wiki|百科|词条|页面|条目)\s+(.+?)(?:\s*[。？！]|$)",
                r"(?:维基|wiki|百科|词条|页面|条目)\s+(.+?)(?:\s*[。？！]|$)",
                r".*[协作|一起|共同|联合|多人|多方].*[创建|写|编辑|构建].*\s+(.+?)(?:\s*[。？！]|$)",
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

    def compute_semantic_similarity(self, text: str, intent_category: str) -> float:
        """计算文本与意图类别的语义相似度"""
        patterns = self.synonym_groups.get(intent_category, [])
        
        similarity_scores = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 计算匹配权重
                for match in matches:
                    score = min(len(match) / len(text), 1.0) * 0.7  # 基础匹配权重
                    similarity_scores.append(score)
        
        # 如果没有完全匹配，检查是否包含相关关键词
        if not similarity_scores:
            related_keywords = {
                "wiki_creation": ["创建", "维基", "百科", "wiki", "词条", "页面", "协作", "共同", "编辑", "撰写"],
                "debate_start": ["辩论", "讨论", "争辩", "探讨", "多模型", "多智能", "AI协作", "交流"],
                "skill_execution": ["帮我", "帮我分析", "帮我处理", "请你", "请帮我", "分析", "处理", "执行", "运行"]
            }
            
            keywords = related_keywords.get(intent_category, [])
            keyword_matches = sum(1 for kw in keywords if kw in text)
            if keyword_matches > 0:
                similarity_scores.append(keyword_matches * 0.1)  # 关键词权重
        
        return max(similarity_scores) if similarity_scores else 0.0

    def match_intent_by_semantics(self, text: str) -> Optional[Tuple[str, float, Dict[str, Any]]]:
        """基于语义匹配意图"""
        best_intent = None
        best_confidence = 0.0
        best_params = {}
        
        for category, patterns in self.synonym_groups.items():
            confidence = self.compute_semantic_similarity(text, category)
            
            if confidence > best_confidence:
                # 提取关键词参数
                params = self.extract_keywords_by_semantics(text, category)
                best_intent = self.intent_mappings.get(category, category)
                best_confidence = confidence
                best_params = params
        
        if best_intent:
            return best_intent, best_confidence, best_params
        else:
            return None, 0.0, {}

    def extract_keywords_by_semantics(self, text: str, intent_category: str) -> Dict[str, Any]:
        """基于语义提取关键词"""
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


# 扩展LLMBasedIntentAnalyzer以使用语义匹配
class EnhancedLLMBasedIntentAnalyzer:
    """
    增强的大模型意图分析器
    结合语义匹配和向量相似度进行意图分析
    """
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.semantic_matcher = SemanticSimilarityMatcher()
        
        # 意图模板库 - 用于语义相似度匹配
        self.intent_templates = {
            "create_wiki": [
                "创建维基 [主题]",
                "写个维基 [内容]", 
                "新建百科 [词条]",
                "创建词条 [主题]",
                "协作编写维基 [内容]",
                "共同创建百科 [词条]",
                "构建知识页面 [主题]"
            ],
            "start_debate": [
                "辩论 [主题]",
                "讨论 [话题]", 
                "多模型辩论 [主题]",
                "AI们辩论 [话题]",
                "开始辩论 [主题]",
                "发起讨论 [话题]",
                "多方探讨 [问题]"
            ],
            "execute_skill": [
                "帮我分析 [内容]",
                "帮我处理 [文档]",
                "请帮我 [动作] [内容]",
                "执行技能 [任务]",
                "运行工具 [内容]",
                "帮我 [动作] [对象]"
            ]
        }

    async def analyze_intent_by_semantics(self, user_input: str) -> Optional[Dict[str, Any]]:
        """使用语义分析方法分析意图"""
        # 首先使用语义匹配器
        intent_name, confidence, params = self.semantic_matcher.match_intent_by_semantics(user_input)
        
        if intent_name:
            return {
                "intent_name": intent_name,
                "confidence": confidence,
                "parameters": params,
                "requires_clarification": self._needs_clarification(intent_name, params, user_input),
                "explanation": f"通过语义相似度匹配识别: {intent_name} (置信度: {confidence:.2f})"
            }
        
        return None

    def _needs_clarification(self, intent_name: str, params: Dict[str, Any], original_input: str) -> bool:
        """判断是否需要澄清"""
        if intent_name == "create_wiki":
            # 如果标题提取为空或与原始输入相同，需要澄清
            title = params.get("title", "")
            if not title or title.strip() == "" or title == original_input:
                return True
        elif intent_name == "start_debate":
            # 如果主题提取为空或与原始输入相同，需要澄清
            topic = params.get("topic", "")
            if not topic or topic.strip() == "" or topic == original_input:
                return True
        elif intent_name == "execute_skill":
            # 如果内容提取为空或与原始输入相同，需要澄清
            content = params.get("content", "")
            if not content or content.strip() == "" or content == original_input:
                return True
        
        return False


if __name__ == "__main__":
    print("="*70)
    print("🧠 语义匹配器实现验证")
    print("="*70)
    
    # 验证语义匹配器的基本功能
    matcher = SemanticSimilarityMatcher()
    
    test_cases = [
        ("创建维基 人工智能", "wiki_creation", "基础维基创建"),
        ("一起协作写个维基", "wiki_creation", "协作维基创建"),
        ("多智能体辩论 AI伦理", "debate_start", "多智能体辩论"),
        ("帮我分析这段内容", "skill_execution", "技能执行请求"),
        ("解析以下文本", "skill_execution", "技能执行变体")
    ]
    
    print("\\n🔍 语义匹配验证:")
    for text, expected_category, description in test_cases:
        similarity = matcher.compute_semantic_similarity(text, expected_category)
        print(f"  {description}: '{text}' -> {expected_category}, 相似度: {similarity:.2f}")
    
    print("\\n🎯 意图分析验证:")
    analyzer = EnhancedLLMBasedIntentAnalyzer()
    for text, expected_category, description in test_cases:
        import asyncio
        try:
            result = asyncio.run(analyzer.analyze_intent_by_semantics(text))
            if result:
                print(f"  {description}: '{text}' -> {result['intent_name']}, 置信度: {result['confidence']:.2f}")
            else:
                print(f"  {description}: '{text}' -> 无匹配")
        except Exception as e:
            print(f"  {description}: '{text}' -> 错误: {e}")
    
    print("\\n✅ 语义匹配器实现完成!")
    print("   - 同义表达识别功能")
    print("   - 语义相似度计算") 
    print("   - 参数提取功能")
    print("   - 澄清需求判断")