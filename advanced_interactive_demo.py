#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAIP-LIVE 高级交互式演示系统

这个演示系统提供完整的透明度和深度体验，包括：
1. 详细的虚拟角色观点展开
2. 用户自定义话题
3. 完整的透明度展示（模型调用、提示词、tokens等）
4. 个人助手优化
5. 上下文优化和多轮对话
6. Wiki系统查看

运行方式: python advanced_interactive_demo.py
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 模拟LLM调用和相关服务
class MockLLMInterface:
    """模拟LLM接口，展示真实调用过程"""
    
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        self.total_tokens = 0
        self.call_history = []
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """模拟LLM响应生成"""
        # 模拟token计算
        input_tokens = len(prompt.split()) * 1.3  # 粗略估算
        output_tokens = 150 + len(prompt.split()) * 0.2  # 基于输入长度估算输出
        
        call_info = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "total_tokens": int(input_tokens + output_tokens),
            "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "context_optimization": context.get("optimized", False) if context else False
        }
        
        self.call_history.append(call_info)
        self.total_tokens += call_info["total_tokens"]
        
        # 模拟响应时间
        await asyncio.sleep(0.5)
        
        return call_info


@dataclass
class VirtualAgent:
    """增强的虚拟角色类"""
    agent_id: str
    name: str
    specialty: str
    reasoning_style: str
    core_values: Dict[str, float]
    personality_traits: List[str]
    domain_expertise: Dict[str, float]
    cognitive_biases: List[str]
    base_prompt_template: str
    model_name: str = "gpt-4"
    
    def __post_init__(self):
        self.llm_interface = MockLLMInterface(self.model_name)
        self.conversation_history = []
        self.context_optimizer = MockContextOptimizer()
    
    async def generate_response(self, topic: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成详细的角色响应"""
        # 构建完整提示词
        full_prompt = self._build_full_prompt(topic, user_input, context)
        
        # 上下文优化
        optimized_prompt, optimization_info = await self.context_optimizer.optimize_prompt(
            full_prompt, self.conversation_history
        )
        
        # LLM调用
        llm_call_info = await self.llm_interface.generate_response(
            optimized_prompt, 
            {"optimized": True, "agent_id": self.agent_id}
        )
        
        # 生成角色特定的响应内容
        response_content = self._generate_role_specific_response(topic, user_input)
        
        return {
            "content": response_content,
            "llm_call_info": llm_call_info,
            "optimization_info": optimization_info,
            "prompt_info": {
                "original_prompt": full_prompt,
                "optimized_prompt": optimized_prompt,
                "prompt_length": len(optimized_prompt),
                "optimization_applied": True
            },
            "agent_metadata": {
                "reasoning_style": self.reasoning_style,
                "core_values": self.core_values,
                "expertise_relevance": self._calculate_expertise_relevance(topic)
            }
        }
    
    def _build_full_prompt(self, topic: str, user_input: str, context: Dict[str, Any] = None) -> str:
        """构建完整的提示词"""
        return self.base_prompt_template.format(
            name=self.name,
            specialty=self.specialty,
            reasoning_style=self.reasoning_style,
            core_values=", ".join([f"{k}: {v}" for k, v in self.core_values.items()]),
            personality_traits=", ".join(self.personality_traits),
            topic=topic,
            user_input=user_input,
            context=json.dumps(context) if context else "{}"
        ) 
   
    def _generate_role_specific_response(self, topic: str, user_input: str) -> Dict[str, Any]:
        """生成角色特定的详细响应"""
        if self.agent_id == "scientist":
            return {
                "position": f"基于当前科学研究，关于'{topic}'需要更多实证数据支持。我建议采用系统性的研究方法，包括大规模数据收集、对照实验和长期跟踪研究。",
                "detailed_analysis": [
                    "现有研究的局限性：样本量不足，研究周期较短",
                    "建议的研究方法：随机对照试验、纵向研究、元分析",
                    "需要关注的变量：时间因素、地域差异、个体差异",
                    "预期的研究周期：至少3-5年的长期跟踪"
                ],
                "evidence_requirements": [
                    "至少1000个样本的大规模调研",
                    "多个独立研究机构的交叉验证",
                    "国际对比数据的支持"
                ],
                "confidence": 0.78,
                "reasoning_depth": "深度分析",
                "key_concerns": ["数据质量", "研究方法", "结果可重复性"]
            }
        elif self.agent_id == "artist":
            return {
                "position": f"从人文和创意角度看，'{topic}'涉及深层的情感、文化和社会心理因素。我们不能仅从技术或数据角度理解，还需要考虑人类的内在需求和价值追求。",
                "detailed_analysis": [
                    "情感维度：人们对变化的恐惧、希望和适应过程",
                    "文化影响：不同文化背景下的理解和接受度差异",
                    "创意价值：人类独特的创造力和想象力的不可替代性",
                    "社会心理：群体认同、个人价值感和社会归属感"
                ],
                "creative_insights": [
                    "艺术和创意领域的独特视角",
                    "人文关怀在技术发展中的重要性",
                    "情感智能与理性分析的平衡"
                ],
                "confidence": 0.68,
                "reasoning_depth": "直觉洞察",
                "key_concerns": ["人文价值", "情感需求", "创意保护"]
            }
        elif self.agent_id == "consultant":
            return {
                "position": f"从商业和实施角度，'{topic}'的关键在于制定可操作的战略和风险管控措施。我们需要明确的实施路径、成功指标和应急预案。",
                "detailed_analysis": [
                    "市场机会分析：潜在收益、市场规模、竞争态势",
                    "实施可行性：资源需求、时间周期、技术门槛",
                    "风险评估：技术风险、市场风险、政策风险",
                    "投资回报：成本效益分析、盈亏平衡点、长期价值"
                ],
                "strategic_recommendations": [
                    "分阶段实施策略，降低整体风险",
                    "建立关键绩效指标(KPI)监控体系",
                    "制定多种情景下的应对方案"
                ],
                "confidence": 0.82,
                "reasoning_depth": "战略分析",
                "key_concerns": ["可行性", "投资回报", "风险控制"]
            }
        elif self.agent_id == "philosopher":
            return {
                "position": f"'{topic}'触及根本的伦理和价值判断问题。我们必须从道德哲学的角度审视其对人类尊严、社会公正和未来发展的深层影响。",
                "detailed_analysis": [
                    "伦理原则：尊重人的尊严、促进公共福利、维护社会公正",
                    "价值冲突：效率与公平、个人自由与集体利益的平衡",
                    "道德责任：不同利益相关者的责任分配和义务",
                    "长远影响：对未来世代的责任和可持续发展"
                ],
                "ethical_framework": [
                    "功利主义视角：最大化整体福利",
                    "义务论视角：遵循道德义务和原则",
                    "德性伦理：培养良好品格和美德"
                ],
                "confidence": 0.74,
                "reasoning_depth": "哲学思辨",
                "key_concerns": ["道德原则", "社会公正", "人类福祉"]
            }
        
        return {
            "position": "这是一个需要深入思考的复杂问题",
            "detailed_analysis": ["需要更多信息进行分析"],
            "confidence": 0.5,
            "reasoning_depth": "基础分析",
            "key_concerns": ["信息不足"]
        }
    
    def _calculate_expertise_relevance(self, topic: str) -> float:
        """计算专业相关性"""
        topic_lower = topic.lower()
        relevance = 0.0
        
        for domain, expertise_level in self.domain_expertise.items():
            if domain.lower() in topic_lower:
                relevance += expertise_level
        
        return min(relevance, 1.0)


class MockContextOptimizer:
    """模拟上下文优化器"""
    
    def __init__(self):
        self.optimization_history = []
    
    async def optimize_prompt(self, original_prompt: str, conversation_history: List[Dict]) -> tuple:
        """优化提示词和上下文"""
        # 模拟优化过程
        await asyncio.sleep(0.2)
        
        optimization_info = {
            "original_length": len(original_prompt),
            "optimized_length": len(original_prompt) + 50,  # 模拟优化后长度变化
            "compression_ratio": 0.95,
            "context_elements_added": ["relevant_history", "domain_knowledge"],
            "optimization_techniques": ["context_compression", "relevance_filtering", "coherence_enhancement"],
            "conversation_turns_considered": len(conversation_history),
            "memory_retrieval_applied": True
        }
        
        # 模拟优化后的提示词
        optimized_prompt = f"""[CONTEXT_OPTIMIZED]
{original_prompt}

[ADDITIONAL_CONTEXT]
- Conversation history: {len(conversation_history)} previous turns
- Relevant domain knowledge integrated
- Context coherence enhanced
- Memory retrieval applied
"""
        
        self.optimization_history.append(optimization_info)
        
        return optimized_prompt, optimization_info


class MockPersonalAssistant:
    """模拟个人助手优化"""
    
    def __init__(self):
        self.optimization_count = 0
    
    async def optimize_user_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """优化用户输入"""
        self.optimization_count += 1
        
        # 模拟优化过程
        await asyncio.sleep(0.3)
        
        optimization_info = {
            "original_input": user_input,
            "optimized_input": f"{user_input} [经过个人助手优化：增加了上下文信息和结构化表达]",
            "optimization_applied": True,
            "improvements": [
                "语言表达优化",
                "逻辑结构调整", 
                "关键信息提取",
                "上下文补充"
            ],
            "optimization_score": 0.85,
            "processing_time": 0.3
        }
        
        return optimization_info


class MockWikiSystem:
    """模拟Wiki系统"""
    
    def __init__(self):
        self.pages = {}
        self.page_counter = 0
    
    def create_page(self, title: str, content: Dict[str, Any]) -> str:
        """创建Wiki页面"""
        self.page_counter += 1
        page_id = f"wiki_{self.page_counter:04d}"
        
        wiki_page = {
            "id": page_id,
            "title": title,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "tags": content.get("tags", []),
            "quality_score": content.get("quality_score", 0.0),
            "view_count": 0,
            "edit_count": 0
        }
        
        self.pages[page_id] = wiki_page
        return page_id
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """获取Wiki页面"""
        if page_id in self.pages:
            self.pages[page_id]["view_count"] += 1
            return self.pages[page_id]
        return None
    
    def list_pages(self) -> List[Dict[str, Any]]:
        """列出所有页面"""
        return [
            {
                "id": page_id,
                "title": page["title"],
                "created_at": page["created_at"],
                "quality_score": page["quality_score"],
                "view_count": page["view_count"]
            }
            for page_id, page in self.pages.items()
        ]
    
    def search_pages(self, query: str) -> List[Dict[str, Any]]:
        """搜索Wiki页面"""
        results = []
        query_lower = query.lower()
        
        for page_id, page in self.pages.items():
            if (query_lower in page["title"].lower() or 
                any(query_lower in tag.lower() for tag in page["tags"])):
                results.append({
                    "id": page_id,
                    "title": page["title"],
                    "relevance_score": 0.8,  # 模拟相关性评分
                    "snippet": str(page["content"])[:200] + "..."
                })
        
        return results
clas
s AdvancedInteractiveDemo:
    """高级交互式演示系统"""
    
    def __init__(self):
        """初始化演示系统"""
        self.setup_logging()
        self.logger = logging.getLogger("advanced_demo")
        
        # 初始化组件
        self.personal_assistant = MockPersonalAssistant()
        self.wiki_system = MockWikiSystem()
        
        # 创建增强的虚拟角色
        self.virtual_agents = self.create_enhanced_virtual_agents()
        
        # 系统统计
        self.session_stats = {
            "start_time": datetime.now(),
            "total_llm_calls": 0,
            "total_tokens": 0,
            "optimization_count": 0,
            "wiki_pages_created": 0
        }
        
        self.logger.info("🚀 高级交互式演示系统已启动")
    
    def setup_logging(self):
        """设置详细日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('advanced_demo.log', encoding='utf-8')
            ]
        )
    
    def create_enhanced_virtual_agents(self) -> Dict[str, VirtualAgent]:
        """创建增强的虚拟角色"""
        agents = {}
        
        # 科学家角色
        agents["scientist"] = VirtualAgent(
            agent_id="scientist",
            name="Dr. 理性分析师",
            specialty="科学研究、数据分析、实证验证",
            reasoning_style="analytical",
            core_values={"truth": 0.95, "utility": 0.8, "objectivity": 0.9},
            personality_traits=["严谨", "理性", "质疑精神", "证据导向"],
            domain_expertise={
                "science": 0.95, "research": 0.9, "statistics": 0.85, 
                "methodology": 0.9, "data_analysis": 0.88
            },
            cognitive_biases=["confirmation_bias", "anchoring_bias"],
            base_prompt_template="""你是{name}，一位{specialty}专家。
你的推理风格是{reasoning_style}，核心价值观包括：{core_values}。
你的性格特征：{personality_traits}。

请针对话题"{topic}"和用户观点"{user_input}"，从科学和实证的角度提供深入分析。
要求：
1. 提供具体的研究方法建议
2. 指出现有证据的不足
3. 建议需要收集的数据类型
4. 评估结论的可信度
5. 考虑研究的局限性

上下文信息：{context}
""",
            model_name="gpt-4-turbo"
        )
        
        # 艺术家角色
        agents["artist"] = VirtualAgent(
            agent_id="artist",
            name="创意直觉师",
            specialty="创意思维、人文洞察、社会心理分析",
            reasoning_style="intuitive",
            core_values={"care": 0.9, "innovation": 0.85, "harmony": 0.8},
            personality_traits=["感性", "创新", "同理心", "直觉敏锐"],
            domain_expertise={
                "creativity": 0.95, "psychology": 0.8, "art": 0.9,
                "human_behavior": 0.85, "cultural_analysis": 0.8
            },
            cognitive_biases=["availability_heuristic", "representativeness"],
            base_prompt_template="""你是{name}，一位{specialty}专家。
你的推理风格是{reasoning_style}，核心价值观包括：{core_values}。
你的性格特征：{personality_traits}。

请针对话题"{topic}"和用户观点"{user_input}"，从人文和创意的角度提供深入洞察。
要求：
1. 分析情感和心理层面的影响
2. 考虑文化和社会背景因素
3. 提供创新的解决思路
4. 关注人文价值和意义
5. 探讨长远的社会影响

上下文信息：{context}
""",
            model_name="gpt-4-turbo"
        )
        
        # 顾问角色
        agents["consultant"] = VirtualAgent(
            agent_id="consultant",
            name="实用策略师",
            specialty="商业策略、实施规划、风险管理",
            reasoning_style="pragmatic",
            core_values={"utility": 0.95, "efficiency": 0.9, "results": 0.85},
            personality_traits=["实用", "目标导向", "风险意识", "执行力强"],
            domain_expertise={
                "business": 0.9, "strategy": 0.88, "risk_management": 0.85,
                "project_management": 0.8, "economics": 0.82
            },
            cognitive_biases=["optimism_bias", "planning_fallacy"],
            base_prompt_template="""你是{name}，一位{specialty}专家。
你的推理风格是{reasoning_style}，核心价值观包括：{core_values}。
你的性格特征：{personality_traits}。

请针对话题"{topic}"和用户观点"{user_input}"，从商业和实施的角度提供战略分析。
要求：
1. 分析市场机会和挑战
2. 制定具体的实施计划
3. 识别关键风险和应对措施
4. 评估投资回报和成本效益
5. 提供可操作的建议

上下文信息：{context}
""",
            model_name="gpt-4-turbo"
        )
        
        # 哲学家角色
        agents["philosopher"] = VirtualAgent(
            agent_id="philosopher",
            name="伦理思辨师",
            specialty="伦理分析、价值判断、哲学思辨",
            reasoning_style="reflective",
            core_values={"justice": 0.95, "truth": 0.9, "wisdom": 0.85},
            personality_traits=["深思", "原则性", "批判性", "价值导向"],
            domain_expertise={
                "ethics": 0.95, "philosophy": 0.9, "moral_reasoning": 0.88,
                "social_theory": 0.8, "value_systems": 0.85
            },
            cognitive_biases=["confirmation_bias", "moral_licensing"],
            base_prompt_template="""你是{name}，一位{specialty}专家。
你的推理风格是{reasoning_style}，核心价值观包括：{core_values}。
你的性格特征：{personality_traits}。

请针对话题"{topic}"和用户观点"{user_input}"，从伦理和哲学的角度提供深度思辨。
要求：
1. 分析涉及的伦理原则和价值冲突
2. 探讨道德责任和义务
3. 考虑不同伦理框架的观点
4. 评估对社会公正的影响
5. 提供价值判断的依据

上下文信息：{context}
""",
            model_name="gpt-4-turbo"
        )
        
        return agents
    
    async def run_advanced_demo(self):
        """运行高级交互式演示"""
        print("\n" + "="*100)
        print("🎭 DAIP-LIVE 高级虚拟角色聊天系统 - 完全透明演示")
        print("   基于制度原语的集体智慧涌现平台 - 技术深度展示版")
        print("="*100)
        
        print("\n🌟 系统技术特色：")
        print("   ✨ 4个认知独立的虚拟角色 (完整提示词和模型调用透明)")
        print("   🧠 个人助手输入优化 (用户输入智能增强)")
        print("   🔄 上下文优化和多轮对话 (智能摘要和记忆管理)")
        print("   🚀 集体智慧涌现 (高级共识算法和洞察检测)")
        print("   📚 完整Wiki系统 (可查看、搜索、管理知识)")
        print("   📊 完全透明的系统调用 (tokens、模型、优化过程)")
        
        # 获取用户自定义话题
        topic = await self.get_custom_topic()
        
        # 获取用户观点并优化
        user_input, optimization_info = await self.get_optimized_user_input(topic)
        
        # 显示优化透明度
        self.show_optimization_transparency(optimization_info)
        
        # 开始深度演示流程
        await self.execute_advanced_workflow(topic, user_input)
        
        # 展示Wiki系统
        await self.demonstrate_wiki_system()
        
        # 生成完整透明度报告
        await self.generate_transparency_report()
    
    async def get_custom_topic(self) -> str:
        """获取用户自定义话题"""
        print("\n💭 话题设置")
        print("="*50)
        print("您可以输入任何您感兴趣的话题进行深度分析。")
        print("建议选择复杂、有争议或需要多角度思考的话题。")
        
        print("\n📝 话题示例：")
        print("   • 人工智能对教育的影响")
        print("   • 基因编辑技术的伦理边界")
        print("   • 远程工作对社会结构的改变")
        print("   • 数字货币的未来发展")
        print("   • 气候变化的解决方案")
        print("   • 社交媒体对心理健康的影响")
        
        while True:
            topic = input("\n请输入您想讨论的话题: ").strip()
            if topic:
                print(f"\n✅ 话题确认: {topic}")
                confirm = input("确认使用这个话题吗？(y/n): ").strip().lower()
                if confirm in ['y', 'yes', '是', '确认', '']:
                    return topic
                else:
                    continue
            else:
                print("❌ 话题不能为空，请重新输入")
    
    async def get_optimized_user_input(self, topic: str) -> tuple:
        """获取并优化用户输入"""
        print(f"\n💭 观点输入")
        print("="*50)
        print(f"话题: {topic}")
        print("\n请分享您对这个话题的观点、看法或疑问。")
        print("您可以包括：")
        print("   • 您的立场和观点")
        print("   • 支持观点的理由")
        print("   • 您关心的具体问题")
        print("   • 希望探讨的方向")
        
        user_input = input("\n请输入您的观点: ").strip()
        
        if not user_input:
            user_input = f"我对{topic}这个话题很感兴趣，希望能从多个角度深入了解和分析。"
            print(f"使用默认观点: {user_input}")
        
        print("\n🔄 正在通过个人助手优化您的输入...")
        optimization_info = await self.personal_assistant.optimize_user_input(user_input, {"topic": topic})
        
        return optimization_info["optimized_input"], optimization_info
    
    def show_optimization_transparency(self, optimization_info: Dict[str, Any]):
        """显示优化透明度信息"""
        print("\n📊 个人助手优化透明度")
        print("="*50)
        print(f"原始输入: {optimization_info['original_input']}")
        print(f"优化后输入: {optimization_info['optimized_input']}")
        print(f"优化评分: {optimization_info['optimization_score']:.2f}")
        print(f"处理时间: {optimization_info['processing_time']:.2f}秒")
        print("优化改进:")
        for improvement in optimization_info['improvements']:
            print(f"   ✓ {improvement}")
        
        input("\n按回车键继续到虚拟角色分析阶段...")
    
    async def execute_advanced_workflow(self, topic: str, user_input: str):
        """执行高级工作流"""
        print("\n" + "="*80)
        print("🎬 开始深度集体智慧涌现过程")
        print("="*80)
        
        # 第一阶段：虚拟角色深度分析
        print(f"\n🤖 第一阶段：虚拟角色认知独立深度分析")
        print("正在启动4个认知独立的虚拟角色进行深度思考...")
        
        agent_responses = {}
        total_tokens = 0
        
        for agent_id, agent in self.virtual_agents.items():
            print(f"\n{'='*60}")
            print(f"🧠 {agent.name} 正在分析...")
            print(f"{'='*60}")
            
            # 显示角色信息
            print(f"📋 角色信息:")
            print(f"   🎯 专长: {agent.specialty}")
            print(f"   🧠 推理风格: {agent.reasoning_style}")
            print(f"   💎 核心价值: {', '.join([f'{k}({v})' for k, v in agent.core_values.items()])}")
            print(f"   🎭 性格特征: {', '.join(agent.personality_traits)}")
            print(f"   🔧 使用模型: {agent.model_name}")
            
            # 显示专业相关性
            relevance = agent._calculate_expertise_relevance(topic)
            print(f"   📊 话题相关性: {relevance:.2f}")
            
            # 生成响应
            response = await agent.generate_response(topic, user_input, {"depth": "detailed"})
            agent_responses[agent_id] = response
            
            # 显示LLM调用透明度
            llm_info = response["llm_call_info"]
            print(f"\n📡 LLM调用信息:")
            print(f"   🤖 模型: {llm_info['model']}")
            print(f"   📝 输入tokens: {llm_info['input_tokens']}")
            print(f"   📤 输出tokens: {llm_info['output_tokens']}")
            print(f"   📊 总tokens: {llm_info['total_tokens']}")
            print(f"   ⏱️  调用时间: {llm_info['timestamp']}")
            
            total_tokens += llm_info['total_tokens']
            self.session_stats['total_llm_calls'] += 1
            
            # 显示上下文优化信息
            opt_info = response["optimization_info"]
            print(f"\n🔄 上下文优化信息:")
            print(f"   📏 原始长度: {opt_info['original_length']} 字符")
            print(f"   📏 优化长度: {opt_info['optimized_length']} 字符")
            print(f"   📊 压缩比: {opt_info['compression_ratio']:.2f}")
            print(f"   🧠 记忆检索: {'✓' if opt_info['memory_retrieval_applied'] else '✗'}")
            print(f"   🔧 优化技术: {', '.join(opt_info['optimization_techniques'])}")
            
            # 显示提示词信息
            prompt_info = response["prompt_info"]
            print(f"\n📝 提示词信息:")
            print(f"   📏 提示词长度: {prompt_info['prompt_length']} 字符")
            print(f"   🔄 优化应用: {'✓' if prompt_info['optimization_applied'] else '✗'}")
            print(f"   📋 原始提示词预览:")
            print(f"      {prompt_info['original_prompt'][:200]}...")
            
            # 显示详细分析结果
            content = response["content"]
            print(f"\n💭 {agent.name} 的深度分析:")
            print(f"   🎯 核心观点: {content['position']}")
            print(f"   💪 信心度: {content['confidence']:.2f}")
            print(f"   🔍 分析深度: {content['reasoning_depth']}")
            
            print(f"\n📊 详细分析要点:")
            for i, point in enumerate(content['detailed_analysis'], 1):
                print(f"   {i}. {point}")
            
            if 'evidence_requirements' in content:
                print(f"\n📋 证据要求:")
                for req in content['evidence_requirements']:
                    print(f"   • {req}")
            
            if 'strategic_recommendations' in content:
                print(f"\n💡 战略建议:")
                for rec in content['strategic_recommendations']:
                    print(f"   • {rec}")
            
            if 'creative_insights' in content:
                print(f"\n✨ 创意洞察:")
                for insight in content['creative_insights']:
                    print(f"   • {insight}")
            
            if 'ethical_framework' in content:
                print(f"\n⚖️ 伦理框架:")
                for framework in content['ethical_framework']:
                    print(f"   • {framework}")
            
            print(f"\n🎯 关键关注点: {', '.join(content['key_concerns'])}")
            
            input(f"\n按回车键查看下一个角色的分析...")
        
        self.session_stats['total_tokens'] = total_tokens
        
        # 继续其他阶段...
        await self.run_critical_review_stage(topic, user_input, agent_responses)
        await self.run_synthesis_stage(topic, user_input, agent_responses)
        await self.run_intelligence_emergence_stage(agent_responses)
    
    async def run_critical_review_stage(self, topic: str, user_input: str, agent_responses: Dict):
        """运行批判性审查阶段"""
        print(f"\n🔍 第二阶段：批判性审查工作流")
        print("="*60)
        print("正在进行多角色交叉验证、事实审查和质量评估...")
        
        # 模拟批判性审查过程
        for i in range(5):
            stages = ["事实提取", "证据验证", "逻辑审查", "偏见检测", "质量评估"]
            print(f"   🔍 {stages[i]}中...")
            await asyncio.sleep(0.8)
        
        # 生成审查结果
        review_results = await self.generate_critical_review_results(topic, user_input, agent_responses)
        
        print(f"\n✅ 批判性审查完成:")
        print(f"   📊 验证事实: {len(review_results['validated_facts'])} 项")
        print(f"   ⚠️  发现问题: {len(review_results['issues_found'])} 项")
        print(f"   🔧 修正建议: {len(review_results['corrections'])} 项")
        print(f"   🎯 整体可信度: {review_results['credibility_score']:.3f}")
        print(f"   📈 质量评分: {review_results['quality_score']:.3f}")
        
        print(f"\n📋 主要验证事实:")
        for i, fact in enumerate(review_results['validated_facts'][:5], 1):
            print(f"   {i}. ✓ {fact}")
        
        if review_results['issues_found']:
            print(f"\n⚠️  发现的问题:")
            for i, issue in enumerate(review_results['issues_found'], 1):
                print(f"   {i}. ⚠️ {issue}")
        
        if review_results['corrections']:
            print(f"\n🔧 修正建议:")
            for i, correction in enumerate(review_results['corrections'], 1):
                print(f"   {i}. 💡 {correction}")
        
        input("\n按回车键继续到多视角综合阶段...")
        
        return review_results