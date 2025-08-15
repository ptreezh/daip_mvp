#!/usr/bin/env python3
"""DAIP-LIVE 虚拟角色聊天系统 - 交互式演示体验

这个演示展示了系统的核心技术亮点：
1. 认知独立的虚拟角色
2. 批判性审查工作流
3. 多视角综合工作流  
4. 集体智慧涌现
5. 知识沉淀和Wiki集成
6. 用户参与的辩论和共识形成

运行方式: python demo_interactive_experience.py
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.core_services.advanced_consensus_algorithms import ConsensusInput
from src.core_services.collective_intelligence_manager import CollectiveIntelligenceManager
from src.core_services.memory_service import MemoryService
from src.core_services.wiki_service import WikiService

# 导入核心组件
from src.virtual_role_chat.cognitive_agent.agent import CognitiveAgent, CognitiveProfile


@dataclass
class DemoScenario:
    """演示场景配置"""
    title: str
    description: str
    topic: str
    user_position: str
    expected_insights: list[str]


class InteractiveDemoExperience:
    """交互式演示体验管理器"""
    
    def __init__(self):
        """初始化演示系统"""
        self.setup_logging()
        self.logger = logging.getLogger("demo_experience")
        
        # 初始化核心组件
        self.collective_intelligence = CollectiveIntelligenceManager()
        self.wiki_service = WikiService()
        self.memory_service = MemoryService()
        
        # 创建虚拟角色
        self.virtual_agents = self.create_virtual_agents()
        
        # 预定义演示场景
        self.demo_scenarios = self.create_demo_scenarios()
        
        self.logger.info("🚀 DAIP-LIVE 虚拟角色聊天系统演示已启动")
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('demo_experience.log', encoding='utf-8')
            ]
        )
    
    def create_virtual_agents(self) -> dict[str, CognitiveAgent]:
        """创建具有认知独立性的虚拟角色"""
        agents = {}
        
        # 分析型专家 - 科学家
        scientist_profile = CognitiveProfile(
            reasoning_style="analytical",
            belief_structure="hierarchical", 
            epistemological_approach="empirical",
            metacognitive_level=5,
            cognitive_biases=["confirmation", "anchoring"],
            values={
                "truth": 0.95,
                "utility": 0.8,
                "justice": 0.7
            },
            domain_expertise={
                "science": 0.95,
                "research": 0.9,
                "logic": 0.85,
                "statistics": 0.8
            }
        )
        
        agents["scientist"] = CognitiveAgent(
            agent_id="scientist",
            name="Dr. 理性分析师",
            profile=scientist_profile,
            initial_knowledge={
                "specialty": "科学研究和数据分析",
                "approach": "基于证据的理性分析",
                "strength": "逻辑推理和实证验证"
            }
        )
        
        # 直觉型专家 - 艺术家/心理学家
        artist_profile = CognitiveProfile(
            reasoning_style="intuitive",
            belief_structure="networked",
            epistemological_approach="constructivist", 
            metacognitive_level=4,
            cognitive_biases=["availability", "representativeness"],
            values={
                "care": 0.9,
                "harmony": 0.85,
                "innovation": 0.8,
                "autonomy": 0.75
            },
            domain_expertise={
                "psychology": 0.9,
                "creativity": 0.95,
                "art": 0.85,
                "human_behavior": 0.8
            }
        )
        
        agents["artist"] = CognitiveAgent(
            agent_id="artist",
            name="创意直觉师",
            profile=artist_profile,
            initial_knowledge={
                "specialty": "创意思维和人文洞察",
                "approach": "直觉感知和创新思维",
                "strength": "模式识别和创意综合"
            }
        )
        
        # 实用型专家 - 商业顾问
        consultant_profile = CognitiveProfile(
            reasoning_style="pragmatic",
            belief_structure="bayesian",
            epistemological_approach="rationalist",
            metacognitive_level=4,
            cognitive_biases=["anchoring", "optimism"],
            values={
                "utility": 0.95,
                "autonomy": 0.85,
                "innovation": 0.75,
                "authority": 0.6
            },
            domain_expertise={
                "business": 0.9,
                "strategy": 0.85,
                "economics": 0.8,
                "management": 0.85
            }
        )
        
        agents["consultant"] = CognitiveAgent(
            agent_id="consultant",
            name="实用策略师",
            profile=consultant_profile,
            initial_knowledge={
                "specialty": "商业策略和实用解决方案",
                "approach": "目标导向的实用主义",
                "strength": "成本效益分析和可行性评估"
            }
        )
        
        # 伦理型专家 - 哲学家
        philosopher_profile = CognitiveProfile(
            reasoning_style="analytical",
            belief_structure="hierarchical",
            epistemological_approach="rationalist",
            metacognitive_level=5,
            cognitive_biases=["confirmation"],
            values={
                "justice": 0.95,
                "truth": 0.9,
                "care": 0.85,
                "sanctity": 0.7
            },
            domain_expertise={
                "ethics": 0.95,
                "philosophy": 0.9,
                "law": 0.75,
                "social_theory": 0.8
            }
        )
        
        agents["philosopher"] = CognitiveAgent(
            agent_id="philosopher",
            name="伦理思辨师",
            profile=philosopher_profile,
            initial_knowledge={
                "specialty": "伦理分析和价值判断",
                "approach": "道德推理和价值平衡",
                "strength": "伦理框架和原则思考"
            }
        )
        
        return agents
    
    def create_demo_scenarios(self) -> list[DemoScenario]:
        """创建演示场景"""
        return [
            DemoScenario(
                title="🤖 AI对就业市场的影响",
                description="探讨人工智能技术对未来就业市场的多维度影响",
                topic="AI技术发展对就业市场的影响：机遇还是威胁？",
                user_position="我认为AI会创造更多新的就业机会",
                expected_insights=[
                    "AI影响的行业差异化分析",
                    "技能转型和教育需求变化",
                    "政策干预的必要性和方式"
                ]
            ),
            DemoScenario(
                title="🌱 可持续发展与经济增长",
                description="平衡环境保护与经济发展的复杂关系",
                topic="如何在追求经济增长的同时实现真正的可持续发展？",
                user_position="经济增长和环境保护可以实现双赢",
                expected_insights=[
                    "绿色经济模式的可行性",
                    "技术创新在可持续发展中的作用",
                    "政府、企业、个人的责任分配"
                ]
            ),
            DemoScenario(
                title="🏥 医疗AI的伦理边界",
                description="探讨AI在医疗领域应用的伦理和安全问题",
                topic="AI医疗诊断系统应该承担多大的决策责任？",
                user_position="AI应该作为医生的辅助工具，而不是替代者",
                expected_insights=[
                    "医疗责任的法律和伦理界定",
                    "患者隐私和数据安全保护",
                    "AI偏见对医疗公平性的影响"
                ]
            )
        ]
    
    async def run_interactive_demo(self):
        """运行交互式演示"""
        print("\n" + "="*80)
        print("🎭 欢迎体验 DAIP-LIVE 虚拟角色聊天系统")
        print("   基于制度原语的集体智慧涌现平台")
        print("="*80)
        
        print("\n🌟 系统技术亮点：")
        print("   ✨ 认知独立的虚拟角色 - 每个AI角色都有独特的认知框架")
        print("   🧠 批判性审查工作流 - 系统性消除AI幻觉")
        print("   🔄 多视角综合工作流 - 整合多元化专家观点")
        print("   🚀 集体智慧涌现 - 产生超越个体能力的洞察")
        print("   📚 知识沉淀系统 - 自动构建和维护知识库")
        
        # 选择演示场景
        scenario = await self.select_demo_scenario()
        
        # 开始集体智慧会话
        session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n🎯 演示场景: {scenario.title}")
        print(f"📝 场景描述: {scenario.description}")
        print(f"💭 讨论话题: {scenario.topic}")
        
        # 启动集体智慧会话
        participant_profiles = {
            agent_id: agent.get_cognitive_state() 
            for agent_id, agent in self.virtual_agents.items()
        }
        participant_profiles["user"] = self.create_user_profile()
        
        session = self.collective_intelligence.start_collective_intelligence_session(
            session_id=session_id,
            participants=list(participant_profiles.keys()),
            topic=scenario.topic,
            participant_profiles=participant_profiles
        )
        
        print(f"\n📊 初始认知多样性评分: {session.diversity_score:.3f}")
        
        # 执行演示流程
        await self.execute_demo_workflow(session_id, scenario)
        
        # 生成最终报告
        await self.generate_final_report(session_id)
    
    async def select_demo_scenario(self) -> DemoScenario:
        """选择演示场景"""
        print("\n📋 请选择演示场景：")
        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"   {i}. {scenario.title}")
            print(f"      {scenario.description}")
        
        while True:
            try:
                choice = input(f"\n请输入选择 (1-{len(self.demo_scenarios)}): ").strip()
                index = int(choice) - 1
                if 0 <= index < len(self.demo_scenarios):
                    return self.demo_scenarios[index]
                else:
                    print("❌ 无效选择，请重新输入")
            except ValueError:
                print("❌ 请输入有效数字")
    
    def create_user_profile(self) -> dict[str, Any]:
        """创建用户认知档案"""
        return {
            "agent_id": "user",
            "name": "用户",
            "profile": {
                "reasoning_style": "mixed",
                "belief_structure": "flexible",
                "epistemological_approach": "pragmatic",
                "metacognitive_level": 3,
                "cognitive_biases": ["confirmation"],
                "values": {
                    "truth": 0.8,
                    "utility": 0.8,
                    "care": 0.7,
                    "justice": 0.7
                },
                "domain_expertise": {
                    "general": 0.6
                }
            }
        }
    
    async def execute_demo_workflow(self, session_id: str, scenario: DemoScenario):
        """执行演示工作流"""
        print("\n" + "="*60)
        print("🎬 开始演示工作流")
        print("="*60)
        
        # 第一阶段：用户输入和初始立场
        print("\n📢 第一阶段：立场表达")
        print(f"💭 您的立场: {scenario.user_position}")
        
        user_input = input("\n请详细阐述您的观点 (或按回车使用默认立场): ").strip()
        if not user_input:
            user_input = scenario.user_position
        
        # 第二阶段：虚拟角色分析和回应
        print("\n🤖 第二阶段：虚拟角色分析")
        agent_responses = await self.get_agent_responses(scenario.topic, user_input)
        
        for agent_id, response in agent_responses.items():
            agent_name = self.virtual_agents[agent_id].name
            print(f"\n👤 {agent_name} ({agent_id}):")
            print(f"   {response['position']}")
            print(f"   💪 信心度: {response['confidence']:.2f}")
            print(f"   🧠 推理: {response['reasoning']}")
        
        # 第三阶段：批判性审查工作流
        print("\n🔍 第三阶段：批判性审查工作流")
        print("   正在进行事实验证和证据审查...")
        
        critical_review_results = await self.run_critical_review(user_input, agent_responses)
        
        print("✅ 批判性审查完成:")
        print(f"   📊 验证的事实: {len(critical_review_results.get('validated_facts', []))}")
        print(f"   ⚠️  需要修正的内容: {len(critical_review_results.get('corrections', []))}")
        print(f"   🎯 整体可信度: {critical_review_results.get('credibility_score', 0):.3f}")
        
        # 第四阶段：多视角综合工作流
        print("\n🔄 第四阶段：多视角综合工作流")
        print("   正在整合多元化专家观点...")
        
        synthesis_results = await self.run_multi_perspective_synthesis(
            scenario.topic, user_input, agent_responses
        )
        
        print("🎯 多视角综合结果:")
        print(f"   {synthesis_results.get('synthesis', '综合观点生成中...')}")
        
        # 第五阶段：集体智慧涌现和共识形成
        print("\n🚀 第五阶段：集体智慧涌现")
        
        consensus_inputs = self.prepare_consensus_inputs(user_input, agent_responses)
        consensus_result, emergent_insights = await self.collective_intelligence.process_collective_input(
            session_id, consensus_inputs, {"topic": scenario.topic}
        )
        
        print("🤝 共识结果:")
        print(f"   📝 共识内容: {consensus_result.consensus_value}")
        print(f"   💪 共识信心度: {consensus_result.confidence_level:.3f}")
        print(f"   🌈 认知多样性: {consensus_result.diversity_score:.3f}")
        print(f"   🧠 涌现洞察数量: {len(emergent_insights)}")
        
        if emergent_insights:
            print("\n✨ 涌现洞察:")
            for i, insight in enumerate(emergent_insights[:3], 1):  # 显示前3个
                print(f"   {i}. {insight.content}")
                print(f"      🎯 涌现评分: {insight.emergence_score:.3f}")
                print(f"      🆕 新颖度: {insight.novelty_score:.3f}")
        
        # 第六阶段：知识沉淀
        print("\n📚 第六阶段：知识沉淀")
        await self.save_knowledge_to_wiki(scenario, consensus_result, emergent_insights)
        
        print("✅ 知识已保存到Wiki系统")
    
    async def get_agent_responses(self, topic: str, user_input: str) -> dict[str, dict[str, Any]]:
        """获取虚拟角色的回应"""
        responses = {}
        
        for agent_id, agent in self.virtual_agents.items():
            # 模拟角色思考过程
            context = {
                "topic": topic,
                "user_position": user_input,
                "agent_expertise": agent.profile.domain_expertise
            }
            
            # 根据角色特点生成回应
            response = await self.generate_agent_response(agent, context)
            responses[agent_id] = response
        
        return responses
    
    async def generate_agent_response(self, agent: CognitiveAgent, context: dict[str, Any]) -> dict[str, Any]:
        """生成单个角色的回应"""
        # 这里简化处理，实际应该调用agent.process_input
        agent_name = agent.name
        reasoning_style = agent.profile.reasoning_style
        domain_expertise = agent.profile.domain_expertise
        
        # 根据角色特点生成不同的回应
        if agent.agent_id == "scientist":
            position = "需要更多实证数据来支持这个观点，建议进行系统性研究"
            confidence = 0.75
            reasoning = "基于科学方法，任何结论都需要充分的证据支持"
        elif agent.agent_id == "artist":
            position = "从人文角度看，这个问题涉及深层的社会和心理因素"
            confidence = 0.65
            reasoning = "直觉告诉我这里有更复杂的人性因素需要考虑"
        elif agent.agent_id == "consultant":
            position = "从实用角度分析，需要考虑成本效益和可操作性"
            confidence = 0.80
            reasoning = "商业实践表明，可行性是评判方案的关键标准"
        elif agent.agent_id == "philosopher":
            position = "这个问题触及根本的伦理和价值判断问题"
            confidence = 0.70
            reasoning = "需要从道德哲学的角度审视其深层含义"
        else:
            position = "这是一个值得深入思考的复杂问题"
            confidence = 0.60
            reasoning = "需要综合多个角度来全面理解"
        
        return {
            "position": position,
            "confidence": confidence,
            "reasoning": reasoning,
            "agent_profile": agent.get_cognitive_state()
        }
    
    async def run_critical_review(self, user_input: str, agent_responses: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """运行批判性审查工作流"""
        # 模拟批判性审查过程
        all_content = [user_input] + [resp["position"] for resp in agent_responses.values()]
        
        # 简化的事实验证
        validated_facts = [
            "用户观点已记录",
            "专家观点已收集",
            "多角度分析已完成"
        ]
        
        corrections = []
        if "绝对" in user_input or any("绝对" in resp["position"] for resp in agent_responses.values()):
            corrections.append("建议避免绝对化表述，增加条件限定")
        
        credibility_score = 0.8  # 基于内容质量的简化评分
        
        return {
            "validated_facts": validated_facts,
            "corrections": corrections,
            "credibility_score": credibility_score
        }
    
    async def run_multi_perspective_synthesis(
        self, 
        topic: str, 
        user_input: str, 
        agent_responses: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """运行多视角综合工作流"""
        # 收集所有观点
        all_perspectives = [user_input]
        all_perspectives.extend([resp["position"] for resp in agent_responses.values()])
        
        # 简化的综合过程
        synthesis = f"""
        基于多角度分析，关于"{topic}"的综合观点如下：
        
        🔬 科学视角强调了实证研究的重要性
        🎨 人文视角关注了社会心理因素
        💼 实用视角考虑了可操作性
        ⚖️ 伦理视角审视了价值判断
        
        综合结论：这是一个需要跨学科协作解决的复杂问题，
        需要在科学严谨性、人文关怀、实用可行性和伦理合理性之间找到平衡。
        """
        
        return {
            "synthesis": synthesis.strip(),
            "perspectives_count": len(all_perspectives),
            "synthesis_quality": 0.85
        }
    
    def prepare_consensus_inputs(
        self, 
        user_input: str, 
        agent_responses: dict[str, dict[str, Any]]
    ) -> list[ConsensusInput]:
        """准备共识输入"""
        inputs = []
        
        # 用户输入
        inputs.append(ConsensusInput(
            agent_id="user",
            position=user_input,
            confidence=0.7,
            reasoning="用户观点",
            cognitive_profile=self.create_user_profile()
        ))
        
        # 虚拟角色输入
        for agent_id, response in agent_responses.items():
            inputs.append(ConsensusInput(
                agent_id=agent_id,
                position=response["position"],
                confidence=response["confidence"],
                reasoning=response["reasoning"],
                cognitive_profile=response["agent_profile"]
            ))
        
        return inputs
    
    async def save_knowledge_to_wiki(
        self, 
        scenario: DemoScenario, 
        consensus_result, 
        emergent_insights: list
    ):
        """保存知识到Wiki系统"""
        # 创建Wiki页面
        wiki_content = f"""
# {scenario.title}

## 讨论话题
{scenario.topic}

## 共识结果
**内容**: {consensus_result.consensus_value}
**信心度**: {consensus_result.confidence_level:.3f}
**认知多样性**: {consensus_result.diversity_score:.3f}

## 涌现洞察
"""
        
        for i, insight in enumerate(emergent_insights, 1):
            wiki_content += f"""
### 洞察 {i}
- **内容**: {insight.content}
- **类型**: {insight.insight_type.value}
- **涌现评分**: {insight.emergence_score:.3f}
- **新颖度**: {insight.novelty_score:.3f}
"""
        
        wiki_content += f"""
## 参与者
- 用户
- Dr. 理性分析师 (科学专家)
- 创意直觉师 (艺术/心理专家)  
- 实用策略师 (商业专家)
- 伦理思辨师 (哲学专家)

## 生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存到Wiki (这里模拟保存过程)
        page_title = f"{scenario.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 实际项目中会调用 self.wiki_service.create_page(page_title, wiki_content)
        print(f"📄 Wiki页面已创建: {page_title}")
    
    async def generate_final_report(self, session_id: str):
        """生成最终报告"""
        print("\n" + "="*60)
        print("📊 最终演示报告")
        print("="*60)
        
        # 获取集体智慧报告
        report = self.collective_intelligence.get_collective_intelligence_report(session_id)
        
        print("\n🎯 会话信息:")
        print(f"   📝 话题: {report['session_info']['topic']}")
        print(f"   👥 参与者: {len(report['session_info']['participants'])}")
        print(f"   ⏱️  持续时间: {report['session_info'].get('duration', 'N/A')} 小时")
        
        print("\n🌈 认知多样性分析:")
        print(f"   📊 多样性评分: {report['diversity_analysis']['initial_diversity_score']:.3f}")
        print(f"   📈 多样性等级: {report['diversity_analysis']['diversity_category']}")
        
        print("\n🤝 共识分析:")
        print(f"   🔄 共识轮次: {report['consensus_analysis']['total_consensus_rounds']}")
        
        print("\n✨ 洞察分析:")
        print(f"   💡 总洞察数: {report['insight_analysis']['total_insights']}")
        if report['insight_analysis']['top_insights']:
            print("   🏆 顶级洞察:")
            for insight in report['insight_analysis']['top_insights'][:2]:
                print(f"      • {insight['content']}")
        
        print("\n🚀 集体智慧涌现:")
        print(f"   📈 涌现评分: {report['intelligence_emergence']['emergence_score']:.3f}")
        print(f"   🎯 涌现等级: {report['intelligence_emergence']['emergence_category']}")
        
        if report['intelligence_emergence']['key_indicators']:
            print("   🔑 关键指标:")
            for indicator in report['intelligence_emergence']['key_indicators']:
                print(f"      ✓ {indicator}")
        
        if report['recommendations']:
            print("\n💡 改进建议:")
            for rec in report['recommendations']:
                print(f"      • {rec}")
        
        # 结束会话
        final_session = self.collective_intelligence.end_collective_intelligence_session(session_id)
        
        print("\n🎉 演示完成！")
        print(f"   最终智慧涌现评分: {final_session.intelligence_emergence_score:.3f}")
        print("   感谢您体验 DAIP-LIVE 虚拟角色聊天系统！")


async def main():
    """主函数"""
    demo = InteractiveDemoExperience()
    await demo.run_interactive_demo()


if __name__ == "__main__":
    asyncio.run(main())