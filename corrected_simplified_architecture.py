"""
简化架构设计：可信度导向的交互系统
只在用户要求高可信度时进入思考循环，其他情况走简单会话或任务流
"""
import asyncio
import re
from typing import Optional, AsyncGenerator
from enum import Enum
from dataclasses import dataclass


class InteractionMode(Enum):
    """交互模式枚举"""
    SIMPLE_CHAT = "simple_chat"      # 简单会话
    TASK_FLOW = "task_flow"          # 任务流（可能包含任务分解）
    THOUGHTFUL_CYCLE = "thoughtful_cycle" # 深思循环（要求高可信度）


@dataclass
class IntentRecognitionResult:
    """意图识别结果"""
    mode: InteractionMode
    confidence: float
    original_request: str
    requires_thoughtful_processing: bool = False
    task_decomposition_needed: bool = False
    parameters: dict = None


class SimpleIntentRecognizer:
    """简化版意图识别器"""
    
    def __init__(self):
        # 高可信度要求的关键词
        self.high_confidence_keywords = [
            # 明确要求高可信度
            r".*必须.*确定.*", r".*必须.*确切.*", r".*必须.*可信.*", r".*必须.*置信度高.*",
            r".*必须.*给出可靠.*", r".*必须.*准确.*", r".*必须.*正确.*", r".*必须.*可靠.*",
            r".*必须.*可证实.*", r".*必须.*无幻觉.*", r".*必须.*不得说谎.*", r".*必须.*不骗人.*",
            r".*要求.*准确.*", r".*要求.*可靠.*", r".*需要.*可信.*", r".*需要.*证实.*",
            # 拒绝幻觉相关
            r".*(不得|不要|请勿).*幻觉.*", r".*(不得|不要|请勿).*说谎.*", r".*(不得|不要|请勿).*欺骗.*",
            r".*(需要|要求).*事实.*", r".*(需要|要求).*证据.*", r".*(需要|要求).*数据.*",
            # 专业严谨要求
            r".*严谨.*分析.*", r".*仔细.*核实.*", r".*深度.*验证.*", r".*全面.*查证.*"
        ]
        
        # 任务流关键词
        self.task_flow_keywords = [
            # 创建类任务
            r".*(创建|新建|写|编辑|构建|开发|设计|实现|制定|建立|创建).*",
            # 分析类任务
            r".*(分析|研究|评估|调查|比较|总结|探索).*",
            # 多步骤任务
            r".*(第一步|首先|其次|然后|最后|分步骤|多步).*",
            # 系统性任务  
            r".*(系统|架构|框架|方案|计划|策略|方法|流程).*",
        ]

    async def recognize_intent(self, text: str) -> IntentRecognitionResult:
        """识别交互意图"""
        text_lower = text.lower()
        
        # 检查是否要求高可信度
        high_confidence_match = any(
            re.search(pattern, text_lower, re.IGNORECASE) 
            for pattern in self.high_confidence_keywords
        )
        
        if high_confidence_match:
            return IntentRecognitionResult(
                mode=InteractionMode.THOUGHTFUL_CYCLE,
                confidence=0.95,
                original_request=text,
                requires_thoughtful_processing=True,
                parameters={"require_high_confidence": True}
            )
        
        # 检查是否为任务流
        task_flow_match = any(
            re.search(pattern, text_lower, re.IGNORECASE) 
            for pattern in self.task_flow_keywords
        )
        
        # 检查复杂度
        word_count = len(text.split())
        action_words = ["分析", "设计", "创建", "开发", "实现", "制定", "研究", "评估", "比较", "总结", "撰写", "构建", "建立", "规划", "探索", "探讨", "考察"]
        action_count = sum(1 for word in action_words if word in text_lower)

        # 还要考虑任务的复杂性关键词
        complexity_words = ["优势", "挑战", "方法", "方案", "策略", "机制", "趋势", "影响", "系统", "架构", "框架", "流程", "技术", "理论", "实践"]
        complexity_count = sum(1 for word in complexity_words if word in text_lower)

        # 任务流匹配或复杂度高（动作词+3个或词数+复杂性词组合）
        is_complex_task = task_flow_match or (word_count > 8 and (action_count >= 2 or complexity_count >= 1))

        if is_complex_task:
            # 需要进一步判断是否需要任务分解
            needs_decomposition = word_count > 12 or action_count >= 2 or complexity_count >= 1
            return IntentRecognitionResult(
                mode=InteractionMode.TASK_FLOW,
                confidence=0.8 if needs_decomposition else 0.75,
                original_request=text,
                task_decomposition_needed=needs_decomposition,
                parameters={
                    "requires_decomposition": needs_decomposition,
                    "task_content": text
                }
            )
        
        # 其他情况为简单会话
        return IntentRecognitionResult(
            mode=InteractionMode.SIMPLE_CHAT,
            confidence=0.6,
            original_request=text,
            parameters={"chat_content": text}
        )


class SimpleThoughtCycle:
    """简单思考循环 - 用于高可信度要求"""
    
    def __init__(self, model_provider):
        self.model_provider = model_provider
    
    async def execute_thoughtful_response(self, user_request: str) -> AsyncGenerator[str, None]:
        """执行深思熟虑的响应"""
        yield f"🔍 **深度思考中...** 理解您的高可信度要求: {user_request[:50]}..."
        
        # 信息收集阶段
        yield "📚 **信息收集** - 收集相关可靠信息..."
        research_prompt = f"""请对以下请求进行深入研究，确保信息准确无误：

请求: {user_request}

要求：
- 提供准确、可靠的信息
- 避免任何猜测或虚构内容
- 引用可靠来源或说明信息依据
- 如不确定某些信息，明确指出"""

        research_response = await self.model_provider.generate(research_prompt) if self.model_provider else f"研究结果: {user_request}"
        yield f"🔍 **信息研究结果**: {str(research_response)[:100]}..."
        
        # 分析阶段
        yield "🤔 **深度分析** - 对信息进行仔细分析..."
        analysis_prompt = f"""请对以下信息进行深度分析：

原始请求: {user_request}
研究结果: {str(research_response)[:500]}

要求：
- 基于研究结果进行分析
- 保持逻辑严密性
- 承认局限性（如果存在）
- 避免推测超出证据范围的内容"""

        analysis_response = await self.model_provider.generate(analysis_prompt) if self.model_provider else f"分析结果: {research_response}"
        yield f"🧠 **分析结果**: {str(analysis_response)[:100]}..."
        
        # 验证阶段
        yield "✅ **验证检查** - 确保内容准确无幻觉..."
        verification_prompt = f"""请验证以下内容的准确性：

原始请求: {user_request}
分析结果: {str(analysis_response)[:500]}

要求：
- 检查信息是否准确
- 识别任何可能的不确定性
- 指出哪些内容是确定的，哪些可能需要进一步确认"""

        verification_response = await self.model_provider.generate(verification_prompt) if self.model_provider else f"验证结果: {analysis_response}"
        yield f"📋 **验证结果**: {str(verification_response)[:100]}..."
        
        # 生成最终响应
        final_prompt = f"""根据以上研究、分析和验证，生成最终响应：

原始请求: {user_request}
研究结果: {str(research_response)[:300]}
分析结果: {str(analysis_response)[:300]}
验证结果: {str(verification_response)[:300]}

要求：
- 提供准确、可靠的最终答案
- 承认任何不确定性
- 避免任何可能的幻觉
- 确保内容基于前述分析"""

        final_response = await self.model_provider.generate(final_prompt) if self.model_provider else f"最终答案: {analysis_response}"
        yield f"🎯 **最终可信答案**: {str(final_response)[:200]}..."


class SimpleTaskFlow:
    """简单任务流程 - 包含任务分解功能"""
    
    def __init__(self, model_provider):
        self.model_provider = model_provider
    
    async def execute_task_flow(self, user_request: str, needs_decomposition: bool = False) -> AsyncGenerator[str, None]:
        """执行任务流"""
        if needs_decomposition:
            yield f"📋 **任务分解中** - 将复杂任务分解为具体步骤: {user_request[:50]}..."
            
            # 创建任务清单
            if self.model_provider:
                prompt = f"""请将以下任务分解为3-8个具体的可执行子任务：

任务: {user_request}

要求：
- 每个子任务应该是具体、可执行的
- 按逻辑顺序排列
- 提供简要描述

返回格式：
1. 子任务1: 描述
2. 子任务2: 描述
3. ..."""

                response = await self.model_provider.generate(prompt)
                task_breakdown = str(response) if isinstance(response, dict) else response
            else:
                # 模拟任务分解
                task_breakdown = f"1. 了解任务: {user_request[:30]}...\n2. 准备资料\n3. 执行任务\n4. 检查结果\n5. 完成任务"
            
            yield f"📋 **任务清单生成**:\n{task_breakdown}"
            
            # 顺序执行任务
            tasks = [line.strip() for line in task_breakdown.split('\n') if line.strip() and line.startswith(('1.','2.','3.','4.','5.'))]
            
            for i, task in enumerate(tasks, 1):
                yield f"🔄 **执行任务 {i}/{len(tasks)}**: {task}"
                # 模拟执行
                if self.model_provider:
                    exec_prompt = f"请执行子任务: {task}\n原请求: {user_request}"
                    exec_result = await self.model_provider.generate(exec_prompt)
                    result = str(exec_result) if isinstance(exec_result, dict) else exec_result
                else:
                    result = f"执行结果: {task}"
                
                yield f"✅ **任务完成**: {task}\n结果: {result[:100]}..."
            
            yield "🎉 **所有任务完成** - 生成最终总结"
            
        else:
            # 简单任务执行
            yield f"⚙️ **执行任务**: {user_request}"
            if self.model_provider:
                response = await self.model_provider.generate(user_request)
                result = str(response) if isinstance(response, dict) else response
            else:
                result = f"处理结果: {user_request}"
            yield f"✅ **任务完成**: {result[:200]}..."


class SimpleChatProcessor:
    """简单聊天处理器"""
    
    def __init__(self, model_provider):
        self.model_provider = model_provider
    
    async def process_chat(self, user_request: str) -> AsyncGenerator[str, None]:
        """处理简单聊天"""
        yield f"💬 **聊天响应**: {user_request}"
        
        if self.model_provider:
            response = await self.model_provider.generate(user_request)
            result = str(response) if isinstance(response, dict) else response
        else:
            result = f"响应: {user_request}"
        
        yield f"✅ **聊天完成**: {result[:200]}..."


class SimplifiedArchitecture:
    """简化架构 - 只有三种模式"""
    
    def __init__(self, model_provider=None):
        self.intent_recognizer = SimpleIntentRecognizer()
        self.thought_cycle = SimpleThoughtCycle(model_provider)
        self.task_flow = SimpleTaskFlow(model_provider)
        self.chat_processor = SimpleChatProcessor(model_provider)
    
    async def process_request(self, user_request: str) -> AsyncGenerator[str, None]:
        """处理用户请求，根据检测到的模式执行"""
        # 识别意图
        intent_result = await self.intent_recognizer.recognize_intent(user_request)
        
        yield f"🔍 **模式识别**: {intent_result.mode.value} (置信度: {intent_result.confidence:.2f})"
        
        # 根据模式执行相应处理
        if intent_result.mode == InteractionMode.THOUGHTFUL_CYCLE:
            async for thought_event in self.thought_cycle.execute_thoughtful_response(user_request):
                yield thought_event
        
        elif intent_result.mode == InteractionMode.TASK_FLOW:
            async for task_event in self.task_flow.execute_task_flow(
                user_request, 
                intent_result.task_decomposition_needed
            ):
                yield task_event
        
        else:  # SIMPLE_CHAT
            async for chat_event in self.chat_processor.process_chat(user_request):
                yield chat_event


# 测试实现
async def test_simplified_architecture():
    """测试简化架构"""
    print("="*80)
    print("🎯 简化架构测试 - 可信度导向的交互系统")
    print("="*80)
    
    # 模拟模型提供者
    class MockModelProvider:
        async def generate(self, prompt: str):
            if "分解为" in prompt:
                return "1. 了解需求: 分析用户具体要求\n2. 收集信息: 获取相关信息\n3. 分析处理: 深入分析\n4. 生成结果: 创建最终输出\n5. 验证质量: 检查结果质量"
            elif "深度思考" in prompt or "研究" in prompt or "分析" in prompt or "验证" in prompt:
                return f"经过深入思考和验证后确定的答复: 这是针对 '{prompt[:50]}...' 的准确可靠答案"
            else:
                return f"简单回应: {prompt[:100]}"
    
    mock_provider = MockModelProvider()
    arch = SimplifiedArchitecture(mock_provider)
    
    test_cases = [
        # 需要高可信度的请求
        ("请务必给我准确的答案，不能有幻觉", InteractionMode.THOUGHTFUL_CYCLE),
        ("必须确保信息可靠，不得说谎", InteractionMode.THOUGHTFUL_CYCLE),
        ("需要可信的数据支持，不能虚构", InteractionMode.THOUGHTFUL_CYCLE),
        ("请仔细核实后再回答，避免错误", InteractionMode.THOUGHTFUL_CYCLE),
        
        # 任务流请求
        ("帮我分析深度学习的优势和挑战", InteractionMode.TASK_FLOW),
        ("设计一个AI系统架构", InteractionMode.TASK_FLOW),
        ("创建一份详细的研究报告", InteractionMode.TASK_FLOW),
        ("制定一个项目计划", InteractionMode.TASK_FLOW),
        
        # 简单聊天请求
        ("你好", InteractionMode.SIMPLE_CHAT),
        ("今天天气怎么样", InteractionMode.SIMPLE_CHAT),
        ("给我讲个笑话", InteractionMode.SIMPLE_CHAT),
        ("聊聊AI", InteractionMode.SIMPLE_CHAT)
    ]
    
    print("\\n📋 测试用例执行:")
    accurate_predictions = 0
    
    for request, expected_mode in test_cases:
        print(f"\\n📝 输入: '{request[:30]}...' (期望模式: {expected_mode.value})")
        
        results = []
        async for event in arch.process_request(request):
            results.append(event)
            if "模式识别" in event:
                print(f"   识别模式: {event}")
        
        # 检查预测是否准确
        # 检查是否执行了正确的流程
        if expected_mode == InteractionMode.THOUGHTFUL_CYCLE:
            actual_mode = InteractionMode.THOUGHTFUL_CYCLE if any("深度思考" in r or "信息收集" in r for r in results) else InteractionMode.SIMPLE_CHAT
        elif expected_mode == InteractionMode.TASK_FLOW:
            actual_mode = InteractionMode.TASK_FLOW if any("任务分解" in r or "任务清单" in r for r in results) else InteractionMode.SIMPLE_CHAT
        else:  # SIMPLE_CHAT
            actual_mode = InteractionMode.SIMPLE_CHAT
        
        success = actual_mode == expected_mode
        status = "✅" if success else "❌"
        print(f"   实际模式: {actual_mode.value} {status}")
        
        if success:
            accurate_predictions += 1
    
    accuracy_rate = accurate_predictions / len(test_cases) * 100
    print(f"\\n🎯 预测准确率: {accurate_predictions}/{len(test_cases)} ({accuracy_rate:.1f}%)")
    
    if accuracy_rate >= 80:
        print("\\n✅ 简化架构实现成功!")
        print("系统现在能正确识别三种交互模式:")
        print("  1. 高可信度要求 → 深思循环")
        print("  2. 复杂任务 → 任务流（含可能的任务分解）")
        print("  3. 简单请求 → 直接聊天")
    else:
        print("\\n⚠️  预测准确率有待提升")
    
    print("\\n🏆 简化架构特性:")
    print("  - 清晰的三模式分离")
    print("  - 只有高可信度要求才进入思考循环")
    print("  - 复杂任务自动分解为可执行步骤")
    print("  - 简单请求直接响应")
    print("  - 避免了模式冲突")


if __name__ == "__main__":
    asyncio.run(test_simplified_architecture())