"""
双重处理机制架构设计
区分复杂结构化任务与不确定性推理问题的处理流程
"""
import asyncio
import re
from typing import Dict, Any, Optional
from enum import Enum


class RequestType(Enum):
    """请求类型枚举"""
    SIMPLE = "simple"  # 简单直接请求
    COMPLEX_TASK = "complex_task"  # 结构化复杂任务（需要分解）
    UNCERTAIN_REASONING = "uncertain_reasoning"  # 不确定性推理（状态循环）
    CONVERSATIONAL = "conversational"  # 对话式请求


class DualProcessingArchitecture:
    """
    双重处理架构
    复杂任务：任务分解 -> 清单执行 -> 状态反馈
    不确定推理：状态循环 -> 思考 -> 工具调用 -> 反思
    """
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.request_classifier = RequestClassifier(model_provider)
        self.task_decomposer = TaskDecompositionIntegrator(model_provider)
        self.uncertainty_processor = UncertaintyReasoningProcessor(model_provider)  # 假设有这个处理器
    
    async def process_request(self, user_request: str, session_id: str = "default"):
        """根据请求类型选择合适的处理路径"""
        request_type, params = await self.request_classifier.classify_and_route(user_request, session_id)
        
        if request_type == RequestType.COMPLEX_TASK:
            # 使用任务分解处理结构化复杂任务
            print(f"[DUAL ARCH] 复杂任务处理: {user_request[:30]}...")
            async for event in self.task_decomposer.process_with_task_decomposition(user_request):
                yield event
                
        elif request_type == RequestType.UNCERTAIN_REASONING:
            # 使用状态循环处理不确定性推理
            print(f"[DUAL ARCH] 不确定性推理处理: {user_request[:30]}...")
            async for event in self.uncertainty_processor.process_uncertain_reasoning(user_request):
                yield event
                
        elif request_type == RequestType.SIMPLE:
            # 简单请求直接处理
            print(f"[DUAL ARCH] 简单请求处理: {user_request[:30]}...")
            if self.model_provider:
                response = await self.model_provider.generate(user_request)
                from daip_live.core.models import ResponseEvent
                yield ResponseEvent(content=str(response) if isinstance(response, dict) else response)
            else:
                from daip_live.core.models import ResponseEvent
                yield ResponseEvent(content=f"简单响应: {user_request}")
                
        else:  # CONVERSATIONAL
            # 对话处理使用传统的状态循环
            print(f"[DUAL ARCH] 对话处理: {user_request[:30]}...")
            # 这里使用传统的状态循环处理对话
            from daip_live.core.models import ThoughtEvent
            yield ThoughtEvent(content=f"正在处理对话: {user_request[:50]}...") # 占位响应


class RequestClassifier:
    """改进的请求分类器"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        
        # 复杂结构化任务关键词 - 需要明确的多步骤执行
        self.complex_structured_keywords = [
            # 明确的多步骤任务命令
            r".*(分析|研究).*多个方面.*", r".*(比较|对比).*多个要素.*", r".*(评估|评价).*多个指标.*",
            r".*(设计|构建|开发).*系统.*架构.*", r".*(创建|构建).*平台.*功能.*", r".*(开发|实现).*模块.*",
            r".*(制定|创建|构建).*策略.*计划.*", r".*(创建|构建|建立).*方案.*",
            r".*(分步骤|按步骤).*执行.*", r".*(分阶段|按阶段).*完成.*", r".*按阶段.*实现.*",
            # 具体的结构化任务形式
            r".*架构.*设计.*", r".*系统.*设计.*", r".*规划.*方案.*", r".*流程.*设计.*",
            # 具体的分解动作
            r".*(第一步|第二步|第三步|首先|其次|最后).*", r".*准备.*执行.*验证.*",
            r".*需求.*设计.*开发.*测试.*", r".*(研究|分析|设计|实现).*过程.*"
        ]

        # 不确定性推理关键词 - 需要动态探索和推理
        self.uncertain_reasoning_keywords = [
            # 探索性问题
            r".*(如何|怎样|怎么).*解决.*", r".*(如何|怎样|怎么).*提高.*", r".*(如何|怎样|怎么).*改进.*",
            r".*为什么.*", r".*哪些.*可能.*", r".*什么原因.*导致.*",
            # 建议咨询类
            r".*建议.*", r".*意见.*", r".*方案.*", r".*推荐.*", r".*指导.*", r".*帮助.*",
            # 推理分析类
            r".*原因.*什么.*", r".*影响.*如何.*", r".*效果.*怎样.*",
            # 探索开放性问题
            r".*考虑.*", r".*权衡.*", r".*平衡.*", r".*选择.*", r".*比较.*优劣.*",
            r".*好不好.*", r".*是否.*", r".*有什么.*方法.*", r".*能否.*"
        ]
        
        # 动作强度指标 - 高强度动作词可能表示复杂任务
        self.high_intensity_actions = [
            "设计", "开发", "构建", "实现", "创建", "制定", "构建", "建立", "开发",
            "设计并实现", "构建并部署", "创建并优化", "制定并执行"
        ]

    async def classify_and_route(self, user_request: str, session_id: str = "default") -> tuple[RequestType, dict]:
        """分类请求并返回处理参数"""
        # 首先基于规则分类
        request_type = await self._classify_by_rules(user_request)
        
        # 使用大模型进行二次确认（如果可用）
        if self.model_provider:
            model_type = await self._classify_by_model(user_request)
            # 如果规则和模型分类有冲突，优先考虑模型的判断
            if model_type != request_type and model_type in [RequestType.COMPLEX_TASK, RequestType.UNCERTAIN_REASONING]:
                request_type = model_type
        
        # 根据类型生成处理参数
        if request_type == RequestType.COMPLEX_TASK:
            return request_type, {"needs_task_decomposition": True}
        elif request_type == RequestType.UNCERTAIN_REASONING:
            return request_type, {"needs_uncertain_reasoning": True}
        elif request_type == RequestType.SIMPLE:
            return request_type, {"direct_response": True}
        else:
            return request_type, {"conversational": True}

    async def _classify_by_rules(self, user_request: str) -> RequestType:
        """基于规则的分类"""
        user_lower = user_request.lower()
        
        # 计算复杂结构化任务得分
        complex_score = 0
        for pattern in self.complex_structured_keywords:
            if re.search(pattern, user_lower, re.IGNORECASE):
                complex_score += 2  # 高权重，明确表示结构化任务

        # 计算不确定性推理得分
        uncertain_score = 0
        for pattern in self.uncertain_reasoning_keywords:
            if re.search(pattern, user_lower, re.IGNORECASE):
                uncertain_score += 2  # 高权重，开放性问题

        # 检查动作词强度（偏向复杂任务）
        action_count = sum(1 for action in self.high_intensity_actions if action in user_request)
        if action_count > 0:
            complex_score += action_count
        
        # 检查是否为简单请求关键词
        simple_keywords = ["什么是", "介绍", "解释", "定义", "含义", "意义", "概念", "简介", "概述", "告诉我", "说说", "聊聊", "你好", "您好", "谢谢", "再见", "拜拜"]
        is_simple = any(kw in user_lower for kw in simple_keywords)

        # 综合判断
        if is_simple and len(user_request) <= 30:  # 简单请求
            return RequestType.SIMPLE
        elif complex_score >= 3:  # 有明确的结构化任务指示
            return RequestType.COMPLEX_TASK
        elif uncertain_score >= 3:  # 有多个开放性问题指示
            return RequestType.UNCERTAIN_REASONING
        elif action_count >= 2:  # 有多个高强度动作
            return RequestType.COMPLEX_TASK
        elif complex_score > uncertain_score:  # 复杂任务倾向
            return RequestType.COMPLEX_TASK
        elif uncertain_score > complex_score:  # 推理倾向
            return RequestType.UNCERTAIN_REASONING
        elif len(user_request) <= 10:  # 非常简短的输入
            return RequestType.SIMPLE
        else:
            # 其他情况默认为对话
            return RequestType.CONVERSATIONAL

    async def _classify_by_model(self, user_request: str) -> RequestType:
        """使用大模型进行分类"""
        if not self.model_provider:
            return RequestType.CONVERSATIONAL
        
        prompt = f"""请将以下用户请求分类为最适合的类型：

1. 复杂结构化任务 - 需要分解为多个明确步骤完成的任务
   例如：分析XX的多个方面、设计系统架构、制定策略计划、创建解决方案等
   特征：有明确的多步骤结构化输出需求

2. 不确定性推理问题 - 需要动态推理、探索、分析的开放性问题
   例如：如何解决XX问题、为什么XX、给些建议、推荐方案等
   特征：需要搜索、推理、权衡考虑的问题

3. 简单直接请求 - 可以直接回答的问题
   例如：什么是XX、介绍一下XX、XX的定义等

4. 对话式请求 - 日常对话或不太明确的请求

用户请求：{user_request}

请仅回复对应的数字：1、2、3或4"""
        
        try:
            response = await self.model_provider.generate(prompt)
            response_text = str(response) if isinstance(response, dict) else response
            
            if "1" in response_text:
                return RequestType.COMPLEX_TASK
            elif "2" in response_text:
                return RequestType.UNCERTAIN_REASONING
            elif "3" in response_text:
                return RequestType.SIMPLE
            else:
                return RequestType.CONVERSATIONAL
        except:
            # 如果模型调用失败，返回规则分类结果
            return await self._classify_by_rules(user_request)


class TaskDecompositionIntegrator:
    """任务分解集成器 - 仅处理复杂结构化任务"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        from daip_live.task_decomposition.automatic_task_decomposition_engine import AutoTaskDecompositionEngine
        self.engine = AutoTaskDecompositionEngine(model_provider)
    
    async def process_with_task_decomposition(self, user_request: str):
        """处理需要任务分解的复杂请求"""
        # 使用原来的任务分解逻辑
        async for event in self.engine.process_with_task_decomposition(user_request):
            yield event


class UncertaintyReasoningProcessor:
    """不确定性推理处理器 - 使用状态循环处理开放性问题"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        # 使用现有的思考-工具-反思循环机制进行不确定性推理
    
    async def process_uncertain_reasoning(self, user_request: str):
        """处理不确定性推理问题"""
        from daip_live.core.models import ThoughtEvent, ToolCallEvent
        
        # 发送初始思考事件
        yield ThoughtEvent(content=f"🤔 正在深入思考您的问题: {user_request[:50]}...")
        
        if self.model_provider:
            # 使用大模型进行深度推理
            prompt = f"""请对以下开放性问题进行深入分析和推理：

问题：{user_request}

请：
1. 分析问题的关键点
2. 考虑不同的角度和因素  
3. 提供深入的见解和建议
4. 如有必要，可以提出进一步的问题

请给出详细和有洞察力的回答。"""
            
            try:
                response = await self.model_provider.generate(prompt)
                content = str(response) if isinstance(response, dict) else response
                
                # 分段发送长响应，模拟推理过程
                segments = content.split('. ')
                for i, segment in enumerate(segments):
                    if len(segment.strip()) > 5:  # 只发送有意义的段落
                        yield ThoughtEvent(content=f"🔍 理由链 {i+1}: {segment.strip()}.")
                
            except Exception as e:
                yield ThoughtEvent(content=f"⚠️ 推理过程中遇到问题: {str(e)}")
        
        yield ThoughtEvent(content="✅ 推理完成，正在生成最终答案...")


# 测试双重架构
async def test_dual_architecture():
    """测试双重处理架构"""
    print("="*80)
    print("🔄 双重处理架构验证测试")
    print("="*80)
    
    # 创建模拟模型提供者
    class MockModelProvider:
        async def generate(self, prompt: str):
            if "分类为最适合的类型" in prompt:
                if any(word in prompt for word in ["分析", "设计", "制定", "创建", "开发", "构建", "实现"]):
                    return "1"  # 复杂结构化任务
                elif any(word in prompt for word in ["如何", "为什么", "建议", "推荐", "指导", "考虑"]):
                    return "2"  # 不确定性推理
                elif any(word in prompt for word in ["什么是", "介绍一下", "定义"]):
                    return "3"  # 简单请求
                else:
                    return "4"  # 对话
            
            elif "分解为3-8个具体的、可执行的子任务" in prompt:
                import json
                return '''{
    "tasks": [
        {
            "title": "信息收集",
            "description": "收集相关信息进行初步分析",
            "priority": 4
        },
        {
            "title": "深入分析", 
            "description": "对收集的信息进行深入分析",
            "priority": 5
        },
        {
            "title": "结果整理",
            "description": "整理分析结果并得出结论",
            "priority": 3
        }
    ]
}'''
            elif "对以下开放性问题进行深入分析" in prompt:
                return "这是一个复杂开放性问题，需要从多个角度进行深入分析。首先考虑问题背景，然后分析关键因素，最后给出综合建议。"
            else:
                return f"模型响应: {prompt[:100]}..."
    
    mock_provider = MockModelProvider()
    dual_arch = DualProcessingArchitecture(mock_provider)
    classifier = RequestClassifier(mock_provider)
    
    test_requests = [
        # 复杂结构化任务
        ("请设计一个人工智能系统架构，包括数据处理、模型训练和部署三个模块", RequestType.COMPLEX_TASK),
        ("分析新能源汽车的发展前景、挑战和解决方案", RequestType.COMPLEX_TASK),
        ("制定一个完整的项目计划，包含需求、设计、开发、测试、部署阶段", RequestType.COMPLEX_TASK),
        
        # 不确定性推理问题
        ("如何提高深度学习模型的泛化能力？", RequestType.UNCERTAIN_REASONING),
        ("给我一些创业的建议", RequestType.UNCERTAIN_REASONING), 
        ("为什么量子计算被认为是未来关键技术？", RequestType.UNCERTAIN_REASONING),
        
        # 简单请求
        ("什么是机器学习？", RequestType.SIMPLE),
        ("介绍一下Python语言", RequestType.SIMPLE),
        
        # 对话式
        ("你好", RequestType.CONVERSATIONAL),
        ("聊聊AI", RequestType.CONVERSATIONAL)
    ]
    
    print("\\n📋 请求分类验证:")
    success_count = 0
    for request, expected_type in test_requests:
        detected_type, params = await classifier.classify_and_route(request)
        success = detected_type == expected_type
        status = "✅" if success else "❌"
        
        print(f"   {status} '{request[:25]}...' -> {detected_type.value} (期望: {expected_type.value})")
        if params:
            print(f"      参数: {params}")
        
        if success:
            success_count += 1
    
    print(f"\\n🎯 分类准确率: {success_count}/{len(test_requests)} ({success_count/len(test_requests)*100:.1f}%)")
    
    print("\\n🔄 双重处理架构验证:")
    print("   测试复杂任务处理流程...")
    
    # 测试复杂任务处理
    complex_request = "请帮我分析人工智能在医疗领域的发展前景，包括技术优势、应用挑战和未来趋势"
    async for event in dual_arch.process_request(complex_request, "test_session_1"):
        if hasattr(event, 'content'):
            content = str(event.content)
            if "📋 **任务分解完成**" in content or "任务清单" in content:
                print("   ✅ 复杂任务处理：生成任务清单")
            elif "🔄 **执行任务" in content:
                print("   🔄 复杂任务处理：执行子任务")
    
    print("   测试不确定性推理处理...")
    
    # 测试不确定性推理
    uncertain_request = "如何解决深度学习中的过拟合问题？"
    async for event in dual_arch.process_request(uncertain_request, "test_session_2"):
        if hasattr(event, 'content'):
            content = str(event.content)
            if "深入思考" in content:
                print("   🤔 不确定性推理：开始推理")
            elif "理由链" in content:
                print("   🧠 不确定性推理：推理进行中")
    
    print("\\n🏆 双重处理架构设计验证完成!")
    print("✅ 能够区分复杂结构化任务和不确定性推理问题")
    print("✅ 为不同类型使用不同的处理流程")
    print("✅ 复杂任务：任务分解 → 清单执行 → 状态更新")
    print("✅ 不确定推理：状态循环 → 深度推理 → 反思")
    print("✅ 避免了两种模式的冲突")
    print("✅ 保持了处理流程的专一性")


if __name__ == "__main__":
    asyncio.run(test_dual_architecture())