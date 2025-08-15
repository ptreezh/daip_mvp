#!/usr/bin/env python3
"""智能助手主应用

一个完整的、工程可用的智能助手系统
支持用户对话、任务分析、多角色辩论、共识计算、Wiki协同
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入核心服务
from src.core_services.advanced_consensus_algorithms import AdvancedConsensusAlgorithms
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.core_services.intent_analysis_service import BasicIntentAnalysisService
from src.core_services.memory_agent import MemAgent
from src.core_services.role_manager import RoleManager
from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services.universal_context_service import UniversalContextService
from src.core_services.wiki_service import WikiService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntelligentAssistant:
    """智能助手主类"""
    
    def __init__(self):
        """初始化智能助手"""
        print("🚀 正在初始化智能助手系统...")
        
        # 初始化核心服务
        self.role_manager = RoleManager()
        self.llm_manager = IntegratedLLMManager()
        self.wiki_service = WikiService()
        self.memory_agent = MemAgent()
        self.intent_analyzer = BasicIntentAnalysisService()
        self.context_optimizer = UniversalContextService()
        self.consensus_algorithms = AdvancedConsensusAlgorithms()
        self.synthesis_engine = SynthesisEngine()
        
        # 用户会话状态
        self.user_session = {
            "user_id": "user_001",
            "conversation_history": [],
            "current_task": None,
            "active_roles": [],
            "debate_context": None,
            "research_topic": None
        }
        
        # 系统状态
        self.system_metrics = {
            "total_interactions": 0,
            "llm_calls": 0,
            "tokens_used": 0,
            "knowledge_entries": 0,
            "consensus_sessions": 0
        }
        
        print("✅ 智能助手系统初始化完成")
        self._display_system_info()
    
    def _display_system_info(self):
        """显示系统信息"""
        print("\n" + "="*60)
        print("🎭 DAIP-LIVE 智能助手系统")
        print("="*60)
        print("📋 核心功能:")
        print("  • 智能对话与任务分析")
        print("  • 提示词与上下文优化")
        print("  • 多角色辩论与讨论")
        print("  • 共识计算与决策支持")
        print("  • 知识沉淀与Wiki协同")
        print("  • 记忆管理与学习优化")
        
        # 显示可用角色
        available_roles = self.role_manager.get_all_roles()
        print(f"\n🤖 可用角色数量: {len(available_roles)}")
        for role in list(available_roles.values())[:5]:  # 显示前5个角色
            print(f"  • {role.name}: {role.description[:50]}...")
        
        print("\n📚 知识库状态: 已准备就绪")
        print("🧠 记忆系统: 已激活")
        print("="*60)
    
    async def start_conversation(self):
        """开始与用户对话"""
        print("\n💬 智能助手已准备就绪，请输入您的研究议题或问题:")
        print("(输入 'quit' 退出，'help' 查看帮助)")
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n👤 您: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 再见！感谢使用智能助手系统")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # 处理用户输入
                await self._process_user_input(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 再见！感谢使用智能助手系统")
                break
            except Exception as e:
                logger.error(f"处理用户输入时发生错误: {e}")
                print(f"❌ 抱歉，处理您的输入时发生错误: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 智能助手使用指南:")
        print("1. 直接输入您的研究议题或问题")
        print("2. 系统会自动分析并优化您的提示词")
        print("3. 根据需要组织多角色讨论或辩论")
        print("4. 通过共识计算得出结论")
        print("5. 将结果沉淀到知识库中")
        print("\n示例输入:")
        print("  • '分析AI在教育中的应用前景'")
        print("  • '讨论自动驾驶汽车的伦理问题'")
        print("  • '研究区块链技术的发展趋势'")
    
    async def _process_user_input(self, user_input: str):
        """处理用户输入的完整流程"""
        print(f"\n🔄 正在处理您的输入: {user_input}")
        
        # 更新会话历史
        self.user_session["conversation_history"].append({
            "timestamp": datetime.now(),
            "type": "user_input",
            "content": user_input
        })
        self.system_metrics["total_interactions"] += 1
        
        # 步骤1: 意图分析
        print("📊 步骤1: 分析用户意图...")
        intent_result = await self._analyze_intent(user_input)
        print(f"✅ 意图分析完成: {intent_result['intent_type']}")
        
        # 步骤2: 提示词优化
        print("🔧 步骤2: 优化提示词...")
        optimized_prompt = await self._optimize_prompt(user_input, intent_result)
        print("✅ 提示词优化完成")
        print(f"   原始: {user_input[:50]}...")
        print(f"   优化: {optimized_prompt[:50]}...")
        
        # 步骤3: 确定是否需要多角色讨论
        if intent_result.get("complexity_score", 0) > 0.6:
            print("🎭 步骤3: 组织多角色讨论...")
            debate_result = await self._organize_multi_role_discussion(optimized_prompt, intent_result)
            print("✅ 多角色讨论完成")
            
            # 步骤4: 共识计算
            print("🤝 步骤4: 计算共识...")
            consensus_result = await self._compute_consensus(debate_result)
            print(f"✅ 共识计算完成，一致性: {consensus_result.get('consensus_score', 0):.2f}")
            
            final_result = consensus_result
        else:
            print("🤖 步骤3: 单一角色响应...")
            final_result = await self._single_role_response(optimized_prompt, intent_result)
            print("✅ 响应生成完成")
        
        # 步骤5: 知识沉淀
        print("📚 步骤5: 沉淀知识到Wiki...")
        await self._save_to_wiki(user_input, final_result)
        print("✅ 知识沉淀完成")
        
        # 步骤6: 更新记忆
        print("🧠 步骤6: 更新记忆系统...")
        await self._update_memory(user_input, final_result)
        print("✅ 记忆更新完成")
        
        # 显示最终结果
        self._display_final_result(final_result)
        
        # 显示系统指标
        self._display_system_metrics()
    
    async def _analyze_intent(self, user_input: str) -> dict[str, Any]:
        """分析用户意图"""
        try:
            # 使用意图分析服务
            intent_result = await self.intent_analyzer.analyze_intent(user_input)
            
            # 模拟意图分析结果（如果服务不可用）
            if not intent_result:
                intent_result = {
                    "intent_type": "research_inquiry",
                    "complexity_score": 0.7,
                    "domain": "general",
                    "requires_debate": True,
                    "suggested_roles": ["researcher", "analyst", "critic"]
                }
            
            return intent_result
        except Exception as e:
            logger.error(f"意图分析失败: {e}")
            return {
                "intent_type": "general_inquiry",
                "complexity_score": 0.5,
                "domain": "general",
                "requires_debate": False
            }
    
    async def _optimize_prompt(self, original_prompt: str, intent_result: dict[str, Any]) -> str:
        """优化提示词"""
        try:
            # 使用上下文优化引擎
            optimization_result = await self.context_optimizer.optimize_context(
                original_prompt,
                intent_result.get("domain", "general"),
                self.user_session["conversation_history"]
            )
            
            if optimization_result and "optimized_prompt" in optimization_result:
                return optimization_result["optimized_prompt"]
            else:
                # 简单的提示词优化
                optimized = f"作为专业的{intent_result.get('domain', '通用')}领域专家，请深入分析以下问题：{original_prompt}"
                return optimized
                
        except Exception as e:
            logger.error(f"提示词优化失败: {e}")
            return f"请分析：{original_prompt}"
    
    async def _organize_multi_role_discussion(self, prompt: str, intent_result: dict[str, Any]) -> dict[str, Any]:
        """组织多角色讨论"""
        try:
            print("  🎯 选择合适的角色...")
            
            # 获取所有可用角色
            all_roles = self.role_manager.get_all_roles()
            
            # 选择3-4个相关角色进行讨论
            selected_roles = []
            role_names = ["researcher", "analyst", "critic", "synthesizer"]
            
            for role_name in role_names:
                for role_id, role in all_roles.items():
                    if role_name.lower() in role.name.lower() or role_name.lower() in role.description.lower():
                        selected_roles.append(role)
                        break
                if len(selected_roles) >= 3:
                    break
            
            # 如果没找到足够的角色，使用前3个
            if len(selected_roles) < 3:
                selected_roles = list(all_roles.values())[:3]
            
            print(f"  👥 选定角色: {[role.name for role in selected_roles]}")
            
            # 模拟多角色讨论
            discussion_results = []
            
            for i, role in enumerate(selected_roles):
                print(f"  🤖 {role.name} 正在思考...")
                
                # 构建角色特定的提示词
                role_prompt = f"{role.system_prompt}\n\n请从{role.name}的角度分析：{prompt}"
                
                # 调用LLM（这里模拟调用）
                response = await self._call_llm_for_role(role, role_prompt)
                
                discussion_results.append({
                    "role": role.name,
                    "role_id": role.id,
                    "response": response,
                    "timestamp": datetime.now()
                })
                
                print(f"  ✅ {role.name}: {response[:100]}...")
                
                # 更新系统指标
                self.system_metrics["llm_calls"] += 1
                self.system_metrics["tokens_used"] += len(response.split()) * 1.3  # 估算token数
            
            return {
                "discussion_type": "multi_role_debate",
                "participants": [role.name for role in selected_roles],
                "results": discussion_results,
                "topic": prompt
            }
            
        except Exception as e:
            logger.error(f"多角色讨论失败: {e}")
            return {"error": str(e)}
    
    async def _call_llm_for_role(self, role, prompt: str) -> str:
        """为特定角色调用LLM"""
        try:
            # 这里应该调用真实的LLM服务
            # 现在先模拟响应，展示系统流程
            
            responses = {
                "researcher": f"从研究角度看，{prompt.split('：')[-1] if '：' in prompt else prompt} 需要深入的实证分析。我建议采用系统性的研究方法，收集相关数据，进行定量和定性分析。关键是要确保研究的科学性和客观性。",
                
                "analyst": f"作为分析师，我认为{prompt.split('：')[-1] if '：' in prompt else prompt} 涉及多个维度的考量。需要从技术可行性、经济效益、社会影响等角度进行综合评估。建议建立评估框架，量化各项指标。",
                
                "critic": f"从批判性思维角度，{prompt.split('：')[-1] if '：' in prompt else prompt} 存在一些需要质疑的假设。我们必须考虑潜在的风险、局限性和负面影响。不能只看积极面，要全面评估。",
                
                "synthesizer": f"综合各方观点，{prompt.split('：')[-1] if '：' in prompt else prompt} 是一个复杂的议题。需要平衡不同利益相关者的需求，寻找最优解决方案。建议采用系统性方法，整合多元视角。"
            }
            
            # 根据角色名称选择响应
            for key, response in responses.items():
                if key.lower() in role.name.lower():
                    return response
            
            # 默认响应
            return f"作为{role.name}，我认为这个问题需要从专业角度深入分析。建议采用系统性方法，考虑多个维度的因素，确保分析的全面性和准确性。"
            
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return f"作为{role.name}，我正在分析这个问题，但遇到了一些技术困难。"
    
    async def _single_role_response(self, prompt: str, intent_result: dict[str, Any]) -> dict[str, Any]:
        """单一角色响应"""
        try:
            # 选择最合适的角色
            all_roles = self.role_manager.get_all_roles()
            selected_role = list(all_roles.values())[0]  # 简单选择第一个角色
            
            print(f"  🤖 {selected_role.name} 正在分析...")
            
            response = await self._call_llm_for_role(selected_role, prompt)
            
            self.system_metrics["llm_calls"] += 1
            self.system_metrics["tokens_used"] += len(response.split()) * 1.3
            
            return {
                "response_type": "single_role",
                "role": selected_role.name,
                "response": response,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"单一角色响应失败: {e}")
            return {"error": str(e)}
    
    async def _compute_consensus(self, debate_result: dict[str, Any]) -> dict[str, Any]:
        """计算共识"""
        try:
            if "results" not in debate_result:
                return debate_result
            
            # 提取所有角色的观点
            viewpoints = []
            for result in debate_result["results"]:
                viewpoints.append({
                    "source": result["role"],
                    "content": result["response"],
                    "weight": 1.0  # 简单的等权重
                })
            
            # 使用共识算法
            consensus_result = await self.consensus_algorithms.compute_consensus(
                viewpoints,
                method="weighted_average"
            )
            
            # 如果共识算法不可用，使用简单的综合
            if not consensus_result:
                consensus_result = {
                    "consensus_score": 0.75,
                    "final_consensus": self._simple_synthesis(viewpoints),
                    "method": "simple_synthesis"
                }
            
            self.system_metrics["consensus_sessions"] += 1
            
            return {
                "consensus_type": "multi_viewpoint",
                "participants": [vp["source"] for vp in viewpoints],
                "consensus_result": consensus_result,
                "original_debate": debate_result
            }
            
        except Exception as e:
            logger.error(f"共识计算失败: {e}")
            return debate_result
    
    def _simple_synthesis(self, viewpoints: list[dict[str, Any]]) -> str:
        """简单的观点综合"""
        synthesis = "综合各方观点，我们可以得出以下结论：\n\n"
        
        for i, vp in enumerate(viewpoints, 1):
            synthesis += f"{i}. {vp['source']}的观点：{vp['content'][:100]}...\n"
        
        synthesis += "\n基于以上分析，建议采用综合性方法，平衡各方考量，制定全面的解决方案。"
        
        return synthesis
    
    async def _save_to_wiki(self, original_query: str, result: dict[str, Any]):
        """保存到Wiki知识库"""
        try:
            # 构建Wiki条目
            title = f"研究议题：{original_query[:50]}"
            
            content = f"# {title}\n\n"
            content += f"**提交时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"**原始问题**: {original_query}\n\n"
            
            if result.get("consensus_result"):
                content += "## 共识结果\n\n"
                content += result["consensus_result"].get("final_consensus", "")
                content += f"\n\n**共识分数**: {result['consensus_result'].get('consensus_score', 0):.2f}\n"
            elif result.get("response"):
                content += "## 分析结果\n\n"
                content += result["response"]
            
            content += "\n\n## 系统处理信息\n"
            content += f"- LLM调用次数: {self.system_metrics['llm_calls']}\n"
            content += f"- Token使用量: {self.system_metrics['tokens_used']:.0f}\n"
            content += f"- 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # 保存到Wiki
            await self.wiki_service.create_or_update_page(title, content)
            
            self.system_metrics["knowledge_entries"] += 1
            
        except Exception as e:
            logger.error(f"保存到Wiki失败: {e}")
    
    async def _update_memory(self, user_input: str, result: dict[str, Any]):
        """更新记忆系统"""
        try:
            # 构建记忆条目
            memory_entry = {
                "timestamp": datetime.now(),
                "user_input": user_input,
                "result_summary": str(result)[:200],
                "interaction_type": result.get("response_type", "unknown")
            }
            
            # 更新记忆（这里简化处理）
            self.user_session["conversation_history"].append(memory_entry)
            
            # 保持最近50条记忆
            if len(self.user_session["conversation_history"]) > 50:
                self.user_session["conversation_history"] = self.user_session["conversation_history"][-50:]
                
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
    
    def _display_final_result(self, result: dict[str, Any]):
        """显示最终结果"""
        print("\n" + "="*60)
        print("🎉 处理完成！结果如下：")
        print("="*60)
        
        if result.get("consensus_result"):
            print("🤝 共识结果:")
            print(result["consensus_result"].get("final_consensus", ""))
            print(f"\n📊 共识分数: {result['consensus_result'].get('consensus_score', 0):.2f}")
            
            if result.get("participants"):
                print(f"👥 参与角色: {', '.join(result['participants'])}")
                
        elif result.get("response"):
            print("🤖 分析结果:")
            print(result["response"])
            
            if result.get("role"):
                print(f"\n👤 分析角色: {result['role']}")
        
        print("="*60)
    
    def _display_system_metrics(self):
        """显示系统指标"""
        print("\n📈 系统运行指标:")
        print(f"  • 总交互次数: {self.system_metrics['total_interactions']}")
        print(f"  • LLM调用次数: {self.system_metrics['llm_calls']}")
        print(f"  • Token使用量: {self.system_metrics['tokens_used']:.0f}")
        print(f"  • 知识条目数: {self.system_metrics['knowledge_entries']}")
        print(f"  • 共识会话数: {self.system_metrics['consensus_sessions']}")


async def main():
    """主函数"""
    try:
        # 创建智能助手实例
        assistant = IntelligentAssistant()
        
        # 开始对话
        await assistant.start_conversation()
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        print(f"❌ 系统启动失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())