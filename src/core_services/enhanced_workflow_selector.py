#!/usr/bin/env python3
"""增强的工作流选择器

基于现有PersonalAssistant的工作流选择机制进行优化，提升意图识别准确率到≥90%，
并支持学术研究、专家咨询、轻松讨论三大场景的智能识别。
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """场景类型枚举"""
    ACADEMIC_RESEARCH = "academic_research"      # 学术研究
    EXPERT_CONSULTATION = "expert_consultation"  # 专家咨询
    CASUAL_DISCUSSION = "casual_discussion"      # 轻松讨论


class WorkflowType(Enum):
    """工作流类型枚举"""
    CRITICAL_REVIEW = "critical_review"
    MULTI_PERSPECTIVE = "multi_perspective"
    CUSTOM = "custom"


@dataclass
class EnhancedIntentResult:
    """增强的意图分析结果"""
    workflow_type: WorkflowType
    scenario_type: ScenarioType
    confidence: float
    reasoning: str
    topic: str
    keywords_matched: list[str]
    scenario_confidence: float


class EnhancedWorkflowSelector:
    """增强的工作流选择器"""
    
    def __init__(self):
        """初始化增强的工作流选择器"""
        self.scenario_patterns = self._build_scenario_patterns()
        self.workflow_patterns = self._build_workflow_patterns()
        logger.info("Enhanced Workflow Selector initialized")
    
    def _build_scenario_patterns(self) -> dict[ScenarioType, dict[str, Any]]:
        """构建场景识别模式"""
        return {
            ScenarioType.ACADEMIC_RESEARCH: {
                "keywords": [
                    # 研究相关
                    "研究", "分析", "探讨", "调研", "论文", "学术", "理论",
                    "实验", "数据", "统计", "模型", "假设", "验证", "证明",
                    # 学科领域
                    "人工智能", "机器学习", "深度学习", "区块链", "量子",
                    "生物", "医学", "物理", "化学", "经济学", "心理学",
                    # 研究动词
                    "investigate", "analyze", "explore", "study", "examine",
                    "research", "evaluate", "assess", "compare", "contrast"
                ],
                "patterns": [
                    r".*研究.*发展.*趋势",
                    r".*分析.*应用.*前景",
                    r".*探讨.*影响.*因素",
                    r".*调研.*现状.*问题",
                    r".*论文.*观点.*理论",
                    r".*实验.*结果.*数据"
                ],
                "indicators": [
                    "前景", "趋势", "发展", "现状", "问题", "挑战", "机遇",
                    "理论", "实践", "应用", "技术", "方法", "策略"
                ],
                "weight": 1.2  # 学术研究权重
            },
            
            ScenarioType.EXPERT_CONSULTATION: {
                "keywords": [
                    # 咨询相关
                    "建议", "推荐", "指导", "咨询", "帮助", "支持", "解决",
                    "选择", "决策", "方案", "策略", "计划", "建议", "意见",
                    # 问题导向
                    "问题", "困难", "挑战", "风险", "机会", "选项", "方向",
                    "如何", "怎么", "什么", "哪个", "哪种", "应该", "需要",
                    # 业务相关
                    "创业", "投资", "营销", "管理", "技术栈", "产品", "市场"
                ],
                "patterns": [
                    r".*应该.*选择.*什么",
                    r".*如何.*制定.*策略",
                    r".*需要.*注意.*风险",
                    r".*推荐.*什么.*方案",
                    r".*给.*建议.*意见",
                    r".*帮.*解决.*问题"
                ],
                "indicators": [
                    "建议", "推荐", "指导", "帮助", "支持", "解决方案",
                    "最佳实践", "经验", "专业", "权威", "可靠"
                ],
                "weight": 1.1  # 专家咨询权重
            },
            
            ScenarioType.CASUAL_DISCUSSION: {
                "keywords": [
                    # 轻松话题
                    "聊聊", "谈谈", "讨论", "分享", "交流", "互动", "话题",
                    "有趣", "好玩", "轻松", "随便", "闲聊", "聊天", "畅谈",
                    # 生活相关
                    "电影", "音乐", "旅行", "美食", "游戏", "运动", "娱乐",
                    "生活", "经历", "故事", "感受", "体验", "心情", "想法",
                    # 社交用语
                    "大家", "朋友们", "各位", "一起", "共同", "互相", "彼此",
                    # 观点收集相关（从专家咨询移过来）
                    "听听", "各方", "观点", "看法", "意见"
                ],
                "patterns": [
                    r".*大家.*觉得.*怎么样",
                    r".*聊聊.*经历.*体验",
                    r".*推荐.*好.*的",
                    r".*分享.*一些.*有趣",
                    r".*谈谈.*看法.*想法",
                    r".*一起.*讨论.*话题"
                ],
                "indicators": [
                    "有趣", "好玩", "轻松", "愉快", "开心", "分享",
                    "交流", "互动", "社交", "友好", "温馨"
                ],
                "weight": 1.0  # 轻松讨论权重
            }
        }
    
    def _build_workflow_patterns(self) -> dict[WorkflowType, dict[str, Any]]:
        """构建工作流识别模式"""
        return {
            WorkflowType.CRITICAL_REVIEW: {
                "keywords": [
                    "分析", "审查", "评估", "检查", "验证", "审核", "评价",
                    "批判", "质疑", "挑战", "反驳", "辩驳", "论证", "证伪",
                    "可行性", "风险", "问题", "漏洞", "缺陷", "不足", "局限",
                    "逻辑", "合理性", "准确性", "有效性", "可靠性"
                ],
                "patterns": [
                    r".*分析.*可行性.*风险",
                    r".*审查.*逻辑.*漏洞",
                    r".*检查.*是否.*问题",
                    r".*评估.*方案.*效果",
                    r".*验证.*结论.*正确"
                ],
                "weight": 1.0
            },
            
            WorkflowType.MULTI_PERSPECTIVE: {
                "keywords": [
                    "讨论", "观点", "角度", "看法", "意见", "立场", "观念",
                    "多角度", "多方面", "综合", "全面", "整体", "系统",
                    "不同", "各种", "多种", "各方", "多元", "多样", "丰富",
                    "对比", "比较", "权衡", "平衡", "统一", "整合"
                ],
                "patterns": [
                    r".*不同.*角度.*分析",
                    r".*各种.*观点.*看法",
                    r".*多方面.*考虑.*因素",
                    r".*综合.*各方.*意见",
                    r".*听听.*大家.*想法"
                ],
                "weight": 1.0
            }
        }
    
    def analyze_scenario(self, user_input: str) -> tuple[ScenarioType, float, list[str]]:
        """分析用户输入的场景类型"""
        input_lower = user_input.lower()
        scenario_scores = {}
        matched_keywords = {}
        
        for scenario_type, config in self.scenario_patterns.items():
            score = 0
            keywords_found = []
            
            # 关键词匹配
            for keyword in config["keywords"]:
                if keyword.lower() in input_lower:
                    score += 1
                    keywords_found.append(keyword)
            
            # 模式匹配
            for pattern in config["patterns"]:
                if re.search(pattern, user_input):
                    score += 2  # 模式匹配权重更高
                    keywords_found.append(f"pattern:{pattern[:20]}...")
            
            # 指示词匹配
            for indicator in config["indicators"]:
                if indicator.lower() in input_lower:
                    score += 0.5
                    keywords_found.append(f"indicator:{indicator}")
            
            # 应用权重
            weighted_score = score * config["weight"]
            scenario_scores[scenario_type] = weighted_score
            matched_keywords[scenario_type] = keywords_found
        
        # 选择得分最高的场景
        if not scenario_scores or max(scenario_scores.values()) == 0:
            # 默认场景：根据输入长度和复杂度判断
            if len(user_input) > 50 and any(word in input_lower for word in ["分析", "研究", "探讨"]):
                best_scenario = ScenarioType.ACADEMIC_RESEARCH
                confidence = 0.6
            elif any(word in input_lower for word in ["如何", "建议", "推荐", "帮助"]):
                best_scenario = ScenarioType.EXPERT_CONSULTATION
                confidence = 0.6
            else:
                best_scenario = ScenarioType.CASUAL_DISCUSSION
                confidence = 0.5
            keywords_found = []
        else:
            best_scenario = max(scenario_scores, key=scenario_scores.get)
            max_score = scenario_scores[best_scenario]
            total_score = sum(scenario_scores.values())
            confidence = min(0.95, 0.5 + (max_score / max(total_score, 1)) * 0.4)
            keywords_found = matched_keywords[best_scenario]
        
        return best_scenario, confidence, keywords_found
    
    def analyze_workflow(self, user_input: str, scenario_type: ScenarioType) -> tuple[WorkflowType, float, list[str]]:
        """基于场景类型分析工作流类型"""
        input_lower = user_input.lower()
        workflow_scores = {}
        matched_keywords = {}
        
        # 基于场景的工作流偏好
        scenario_workflow_preference = {
            ScenarioType.ACADEMIC_RESEARCH: {
                WorkflowType.MULTI_PERSPECTIVE: 1.4,  # 学术研究强烈偏向多视角
                WorkflowType.CRITICAL_REVIEW: 0.9
            },
            ScenarioType.EXPERT_CONSULTATION: {
                WorkflowType.CRITICAL_REVIEW: 1.2,    # 专家咨询偏向批判性审查
                WorkflowType.MULTI_PERSPECTIVE: 1.0
            },
            ScenarioType.CASUAL_DISCUSSION: {
                WorkflowType.MULTI_PERSPECTIVE: 1.3,  # 轻松讨论偏向多视角
                WorkflowType.CRITICAL_REVIEW: 0.8
            }
        }
        
        for workflow_type, config in self.workflow_patterns.items():
            score = 0
            keywords_found = []
            
            # 关键词匹配
            for keyword in config["keywords"]:
                if keyword.lower() in input_lower:
                    score += 1
                    keywords_found.append(keyword)
            
            # 模式匹配
            for pattern in config["patterns"]:
                if re.search(pattern, user_input):
                    score += 2
                    keywords_found.append(f"pattern:{pattern[:20]}...")
            
            # 应用场景偏好
            scenario_preference = scenario_workflow_preference.get(scenario_type, {})
            preference_weight = scenario_preference.get(workflow_type, 1.0)
            
            weighted_score = score * config["weight"] * preference_weight
            workflow_scores[workflow_type] = weighted_score
            matched_keywords[workflow_type] = keywords_found
        
        # 选择得分最高的工作流
        if not workflow_scores or max(workflow_scores.values()) == 0:
            # 基于场景的默认工作流
            if scenario_type == ScenarioType.EXPERT_CONSULTATION:
                best_workflow = WorkflowType.CRITICAL_REVIEW
                confidence = 0.6
            else:
                best_workflow = WorkflowType.MULTI_PERSPECTIVE
                confidence = 0.6
            keywords_found = []
        else:
            best_workflow = max(workflow_scores, key=workflow_scores.get)
            max_score = workflow_scores[best_workflow]
            total_score = sum(workflow_scores.values())
            confidence = min(0.95, 0.6 + (max_score / max(total_score, 1)) * 0.3)
            keywords_found = matched_keywords[best_workflow]
        
        return best_workflow, confidence, keywords_found
    
    def select_workflow(self, user_input: str, context: Optional[dict[str, Any]] = None) -> EnhancedIntentResult:
        """智能选择工作流"""
        try:
            # 1. 分析场景类型
            scenario_type, scenario_confidence, scenario_keywords = self.analyze_scenario(user_input)
            
            # 2. 基于场景分析工作流类型
            workflow_type, workflow_confidence, workflow_keywords = self.analyze_workflow(user_input, scenario_type)
            
            # 3. 计算综合置信度
            overall_confidence = (scenario_confidence + workflow_confidence) / 2
            
            # 4. 生成推理说明
            reasoning_parts = []
            reasoning_parts.append(f"场景识别: {scenario_type.value} (置信度: {scenario_confidence:.2f})")
            reasoning_parts.append(f"工作流选择: {workflow_type.value} (置信度: {workflow_confidence:.2f})")
            
            if scenario_keywords:
                reasoning_parts.append(f"场景关键词: {', '.join(scenario_keywords[:3])}")
            if workflow_keywords:
                reasoning_parts.append(f"工作流关键词: {', '.join(workflow_keywords[:3])}")
            
            reasoning = "; ".join(reasoning_parts)
            
            # 5. 提取主题
            topic = self._extract_topic(user_input)
            
            return EnhancedIntentResult(
                workflow_type=workflow_type,
                scenario_type=scenario_type,
                confidence=overall_confidence,
                reasoning=reasoning,
                topic=topic,
                keywords_matched=scenario_keywords + workflow_keywords,
                scenario_confidence=scenario_confidence
            )
            
        except Exception as e:
            logger.error(f"Enhanced workflow selection failed: {e}")
            # 降级到简单选择
            return self._fallback_selection(user_input)
    
    def _extract_topic(self, user_input: str) -> str:
        """提取主题"""
        # 简单的主题提取：取前50个字符或第一句话
        sentences = re.split(r'[。！？.!?]', user_input)
        if sentences and len(sentences[0]) > 0:
            topic = sentences[0].strip()
            return topic if len(topic) <= 50 else topic[:47] + "..."
        else:
            return user_input[:50] + "..." if len(user_input) > 50 else user_input
    
    def _fallback_selection(self, user_input: str) -> EnhancedIntentResult:
        """降级选择策略"""
        # 简单的关键词匹配
        input_lower = user_input.lower()
        
        if any(keyword in input_lower for keyword in ["分析", "审查", "评估", "检查"]):
            workflow_type = WorkflowType.CRITICAL_REVIEW
            scenario_type = ScenarioType.EXPERT_CONSULTATION
            confidence = 0.6
        elif any(keyword in input_lower for keyword in ["讨论", "观点", "角度", "看法"]):
            workflow_type = WorkflowType.MULTI_PERSPECTIVE
            scenario_type = ScenarioType.CASUAL_DISCUSSION
            confidence = 0.6
        else:
            workflow_type = WorkflowType.MULTI_PERSPECTIVE
            scenario_type = ScenarioType.CASUAL_DISCUSSION
            confidence = 0.5
        
        return EnhancedIntentResult(
            workflow_type=workflow_type,
            scenario_type=scenario_type,
            confidence=confidence,
            reasoning="降级策略：基于简单关键词匹配",
            topic=self._extract_topic(user_input),
            keywords_matched=[],
            scenario_confidence=confidence
        )


# 全局实例
_enhanced_selector = None

def get_enhanced_workflow_selector() -> EnhancedWorkflowSelector:
    """获取增强工作流选择器的全局实例"""
    global _enhanced_selector
    if _enhanced_selector is None:
        _enhanced_selector = EnhancedWorkflowSelector()
    return _enhanced_selector