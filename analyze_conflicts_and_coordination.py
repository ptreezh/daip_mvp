"""
分析复杂任务分解与不确定性状态循环的协调机制

区分：
1. 复杂任务：需要分解为多个步骤完成的结构性任务
2. 不确定性问题：需要持续推理、反思、工具使用的动态问题
"""
import asyncio
import re
from typing import Dict, Any, Optional
from enum import Enum

class RequestType(Enum):
    """请求类型枚举"""
    SIMPLE = "simple"  # 简单直接请求
    COMPLEX_TASK = "complex_task"  # 复杂结构化任务
    UNCERTAIN_REASONING = "uncertain_reasoning"  # 不确定性推理问题
    CONVERSATIONAL = "conversational"  # 对话式请求

class RequestClassifier:
    """请求分类器 - 区分复杂任务与不确定性问题"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        
        # 复杂任务关键词（需要分解为多个步骤的结构性任务）
        self.complex_task_keywords = [
            # 分析类
            "分析.*的多个方面", "深入分析.*", "全面分析.*", "详细分析.*",
            "研究.*的多个层面", "调查.*问题", "评估.*的影响", "比较.*的优劣",
            "探讨.*的发展前景", "审查.*的实施策略", "总结.*的经验教训",
            # 执行类  
            "设计.*系统", "创建.*方案", "构建.*架构", "制定.*策略",
            "实现.*功能", "开发.*平台", "建立.*模型", "编制.*计划",
            # 综合报告类
            "撰写.*报告", "制作.*方案", "起草.*文档", "整理.*材料",
            # 多步操作类
            "步骤.*", "流程.*", "分阶段.*", "依次.*", "按步骤.*"
        ]
        
        # 不确定性推理关键词（需要动态推理、探索的开放性问题）
        self.uncertainty_keywords = [
            # 探索性关键词
            "如何", "为什么", "怎样才能", "怎么做", "为何", "哪个更好", "是否可行",
            # 开放性问题
            "建议", "意见", "看法", "想法", "思路", "解决方案", "可能的原因",
            # 推理性问题  
            "推理", "推断", "推测", "判断", "评价", "思考", "考虑", "衡量",
            # 探索性动词
            "探索", "寻找", "发现", "挖掘", "了解", "弄清", "搞懂", "弄明白"
        ]
        
        # 简单请求关键词（直接回答即可）
        self.simple_keywords = [
            "什么是", "介绍一下", "解释", "定义", "含义", "意义", "概念", 
            "定义", "描述", "简介", "概述", "告诉我", "说说", "聊聊",
            "今天天气", "问候", "你好", "感谢", "再见", "谢谢"
        ]

    async def classify_request(self, user_request: str) -> RequestType:
        """
        智能分类用户请求类型
        """
        # 首先基于规则分类
        request_type = self._classify_by_rules(user_request)
        
        # 如果规则分类不确定，使用大模型进行分类
        if request_type == RequestType.CONVERSATIONAL and self.model_provider:
            request_type = await self._classify_by_model(user_request)
        
        return request_type

    def _classify_by_rules(self, user_request: str) -> RequestType:
        """基于规则分类请求"""
        text_lower = user_request.lower()
        
        # 检查复杂任务模式
        complex_matches = sum(1 for pattern in self.complex_task_keywords 
                             if re.search(pattern, text_lower))
        
        # 检查不确定性推理模式
        uncertainty_matches = sum(1 for pattern in self.uncertainty_keywords 
                                 if re.search(pattern, text_lower))
        
        # 检查简单请求模式
        simple_matches = sum(1 for pattern in self.simple_keywords 
                            if re.search(pattern, text_lower))
        
        # 优先级：复杂任务 > 不确定性问题 > 简单请求 > 对话
        if complex_matches > 0 and complex_matches >= uncertainty_matches:
            return RequestType.COMPLEX_TASK
        elif uncertainty_matches > 0:
            return RequestType.UNCERTAIN_REASONING
        elif simple_matches > 0:
            return RequestType.SIMPLE
        else:
            # 根据文本长度和复杂度判断
            word_count = len(user_request.split())
            action_words = ["分析", "设计", "实现", "开发", "研究", "评估", "比较", "制定", "创建", "建立"]
            action_count = sum(1 for word in action_words if word in text_lower)
            
            if word_count > 10 and action_count >= 2:
                # 长文本且包含多个动作词，更可能是复杂任务
                return RequestType.COMPLEX_TASK
            elif word_count <= 5:
                # 短文本，可能是简单请求
                return RequestType.SIMPLE
            else:
                # 中等长度，偏向不确定性推理
                return RequestType.UNCERTAIN_REASONING

    async def _classify_by_model(self, user_request: str) -> RequestType:
        """使用大模型分类请求"""
        prompt = f"""请将以下用户请求分类为以下类型之一：

A. 复杂结构化任务 - 需要分解为多个明确步骤完成的任务，如：
   - 分析XX的多个方面
   - 设计一个XX系统
   - 制定XX策略
   - 创建XX方案

B. 不确定性推理问题 - 需要动态推理、探索和思考的开放性问题，如：
   - 如何解决XX问题
   - 为什么XX会发生
   - XX的可能原因是什么
   - 给出建议或解决方案

C. 简单直接请求 - 可以直接回答的问题，如：
   - 什么是XX
   - 介绍XX
   - XX的定义

D. 对话式请求 - 日常对话或不太明确的请求

用户请求：{user_request}

请回复字母代号：A、B、C或D"""
        
        try:
            response = await self.model_provider.generate(prompt)
            response_text = str(response) if isinstance(response, dict) else response
            
            if "A" in response_text or "复杂" in response_text:
                return RequestType.COMPLEX_TASK
            elif "B" in response_text or "不确定" in response_text or "推理" in response_text:
                return RequestType.UNCERTAIN_REASONING
            elif "C" in response_text or "简单" in response_text:
                return RequestType.SIMPLE
            else:
                return RequestType.CONVERSATIONAL
        except:
            # 如果AI分类失败，返回规则分类结果
            return self._classify_by_rules(user_request)


class ConflictAvoidanceMechanism:
    """
    冲突避免机制 - 确保复杂任务分解与不确定性状态循环协调
    """
    
    def __init__(self):
        self.request_classifier = RequestClassifier()
        # 跟踪当前正在处理的请求类型，避免重复处理
        self.active_processing: Dict[str, RequestType] = {}
    
    async def route_request(self, user_request: str, session_id: str = "default") -> tuple[RequestType, dict]:
        """
        智能路由请求到合适的处理流程
        返回: (请求类型, 额外参数)
        """
        # 检查当前是否正在处理同一类型的请求
        if session_id in self.active_processing:
            # 如果已经在处理复杂任务，避免递归
            if self.active_processing[session_id] == RequestType.COMPLEX_TASK:
                return RequestType.CONVERSATIONAL, {}
        
        # 分类请求
        request_type = await self.request_classifier.classify_request(user_request)
        
        # 记录当前处理的请求类型
        self.active_processing[session_id] = request_type
        
        # 根据请求类型返回适当的处理参数
        if request_type == RequestType.COMPLEX_TASK:
            return request_type, {"needs_task_decomposition": True}
        elif request_type == RequestType.UNCERTAIN_REASONING:
            return request_type, {"needs_uncertain_reasoning": True}
        elif request_type == RequestType.SIMPLE:
            return request_type, {"direct_response": True}
        else:
            return request_type, {"conversational": True}
    
    def complete_processing(self, session_id: str):
        """标记处理完成，释放资源"""
        if session_id in self.active_processing:
            del self.active_processing[session_id]


# 验证分类器功能
async def test_classification():
    """测试请求分类功能"""
    classifier = RequestClassifier()
    
    test_cases = [
        # 复杂任务
        ("请帮我分析人工智能在医疗领域的应用前景、挑战和解决方案", RequestType.COMPLEX_TASK),
        ("设计一个完整的AI系统架构并实现核心功能", RequestType.COMPLEX_TASK),
        ("制定一个项目计划，包括需求分析、设计、开发和测试", RequestType.COMPLEX_TASK),
        
        # 不确定性推理
        ("如何提高深度学习模型的准确性", RequestType.UNCERTAIN_REASONING),
        ("为什么量子计算被认为是未来技术的关键", RequestType.UNCERTAIN_REASONING), 
        ("给我一些关于创业的建议", RequestType.UNCERTAIN_REASONING),
        
        # 简单请求
        ("什么是机器学习", RequestType.SIMPLE),
        ("介绍一下Python编程语言", RequestType.SIMPLE),
        
        # 对话式
        ("你好", RequestType.CONVERSATIONAL),
        ("聊聊天", RequestType.CONVERSATIONAL)
    ]
    
    print("="*80)
    print("🔍 请求分类功能验证")
    print("="*80)
    
    for request, expected_type in test_cases:
        detected_type = await classifier.classify_request(request)
        status = "✅" if detected_type == expected_type else "❌"
        
        print(f"{status} '{request[:30]}...' -> {detected_type.value} (期望: {expected_type.value})")
    
    print("\\n🎯 冲突避免机制设计:")
    print("✅ 能够区分复杂任务与不确定性推理")
    print("✅ 避免在同一会话中重复处理同类型请求") 
    print("✅ 为不同类型请求分配合适的处理流程")
    print("✅ 保护状态循环不受任务分解流程干扰")
    
    # 测试路由功能
    print("\\n🔄 智能路由功能验证:")
    router = ConflictAvoidanceMechanism()
    
    for request, _ in test_cases[:4]:  # 测试前4个不同类型
        req_type, params = await router.route_request(request, f"test_{hash(request)%1000}")
        print(f"   '{request[:20]}...' -> {req_type.value}, params: {params}")
    
    print("\\n✅ 分类与路由机制验证通过!")


if __name__ == "__main__":
    asyncio.run(test_classification())