#!/usr/bin/env python3
"""真实LLM辩论助手

基于真实大模型调用的多角色深度辩论系统
支持多轮辩论、共识计算、高质量输出
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

import requests

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.core_services.role_manager import RoleManager
from src.core_services.wiki_service import WikiService

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RealLLMDebateAssistant:
    """真实LLM辩论助手"""
<<<<<<< HEAD

    def __init__(self):
        """初始化"""
        print("🚀 正在初始化真实LLM辩论助手...")

        # 初始化核心服务
        self.role_manager = RoleManager()
        self.wiki_service = WikiService()

=======
    
    def __init__(self):
        """初始化"""
        print("🚀 正在初始化真实LLM辩论助手...")
        
        # 初始化核心服务
        self.role_manager = RoleManager()
        self.wiki_service = WikiService()
        
>>>>>>> feature/core-services-refactor
        # LLM配置
        self.llm_config = {
            "base_url": "http://127.0.0.1:11434",  # Ollama默认地址
            "model": "llama3:instruct",  # 默认模型
            "temperature": 0.8,
            "max_tokens": 2000
        }
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 辩论配置
        self.debate_config = {
            "min_rounds": 5,
            "max_rounds": 8,
            "min_response_length": 500,
            "consensus_threshold": 0.7
        }
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 会话状态
        self.session = {
            "user_id": "user_001",
            "conversation_history": [],
            "current_debate": None
        }
<<<<<<< HEAD

        print("✅ 真实LLM辩论助手初始化完成")
        self._display_system_info()

=======
        
        print("✅ 真实LLM辩论助手初始化完成")
        self._display_system_info()
    
>>>>>>> feature/core-services-refactor
    def _display_system_info(self):
        """显示系统信息"""
        print("\n" + "="*70)
        print("🎭 DAIP-LIVE 真实LLM辩论助手 v2.0")
        print("="*70)
        print("🎯 核心特性:")
        print("  • 真实大模型调用 (Ollama/OpenAI)")
        print("  • 多角色深度辩论 (5-8轮)")
        print("  • 高质量输出 (每次500+字)")
        print("  • 共识与分歧计算")
        print("  • 自动Wiki词条生成")
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 测试LLM连接
        if self._test_llm_connection():
            print(f"🤖 LLM服务: ✅ 已连接 ({self.llm_config['model']})")
        else:
            print("🤖 LLM服务: ❌ 连接失败")
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 显示可用角色
        try:
            roles = self.role_manager.list_roles()
            print(f"👥 可用角色: {len(roles)}个")
<<<<<<< HEAD

            # 显示前3个角色
            for i, role in enumerate(roles[:3]):
                print(f"  • {role.name}")

        except Exception as e:
            print(f"  ⚠️ 角色加载警告: {e}")

        print("="*70)

=======
            
            # 显示前3个角色
            for i, role in enumerate(roles[:3]):
                print(f"  • {role.name}")
                
        except Exception as e:
            print(f"  ⚠️ 角色加载警告: {e}")
        
        print("="*70)
    
>>>>>>> feature/core-services-refactor
    def _test_llm_connection(self) -> bool:
        """测试LLM连接"""
        try:
            response = requests.get(f"{self.llm_config['base_url']}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    async def start_conversation(self):
        """开始对话"""
        print("\n💬 真实LLM辩论助手已准备就绪！")
        print("请输入您的研究议题，系统将:")
        print("1. 选择3-4个专业角色")
        print("2. 进行5-8轮深度辩论")
        print("3. 每轮发言500+字")
        print("4. 计算共识与分歧")
        print("5. 生成5000+字综合报告")
        print("\n输入 'quit' 退出，'demo' 运行演示")
<<<<<<< HEAD

        while True:
            try:
                user_input = input("\n👤 您: ").strip()

=======
        
        while True:
            try:
                user_input = input("\n👤 您: ").strip()
                
>>>>>>> feature/core-services-refactor
                if user_input.lower() == 'quit':
                    print("👋 感谢使用真实LLM辩论助手！")
                    break
                elif user_input.lower() == 'demo':
                    await self._run_demo()
                    continue
                elif not user_input:
                    continue
<<<<<<< HEAD

                # 处理用户输入
                await self._process_debate_request(user_input)

=======
                
                # 处理用户输入
                await self._process_debate_request(user_input)
                
>>>>>>> feature/core-services-refactor
            except KeyboardInterrupt:
                print("\n👋 感谢使用真实LLM辩论助手！")
                break
            except Exception as e:
                logger.error(f"处理输入错误: {e}")
                print(f"❌ 处理您的输入时发生错误: {e}")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    async def _run_demo(self):
        """运行演示"""
        print("\n🎬 运行演示: AI在教育中的应用前景与挑战")
        await self._process_debate_request("AI在教育中的应用前景与挑战")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    async def _process_debate_request(self, topic: str):
        """处理辩论请求"""
        print("\n🔥 启动真实LLM多角色辩论")
        print(f"📋 辩论议题: {topic}")
        print("-" * 70)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        try:
            # 步骤1: 选择角色
            print("🎭 步骤1: 智能选择辩论角色...")
            selected_roles = await self._select_debate_roles(topic)
            print(f"✅ 选定角色: {[role.name for role in selected_roles]}")
<<<<<<< HEAD

            # 步骤2: 进行多轮辩论
            print(f"\n💭 步骤2: 开始{self.debate_config['min_rounds']}-{self.debate_config['max_rounds']}轮深度辩论...")
            debate_result = await self._conduct_real_debate(topic, selected_roles)

            # 步骤3: 共识计算
            print("\n🤝 步骤3: 计算共识与分歧...")
            consensus_result = await self._calculate_consensus_and_divergence(debate_result)

            # 步骤4: 生成综合报告
            print("\n📝 步骤4: 生成综合报告...")
            final_report = await self._generate_comprehensive_report(topic, debate_result, consensus_result)

            # 步骤5: 保存到Wiki
            print("\n📚 步骤5: 保存到Wiki知识库...")
            await self._save_to_wiki(topic, final_report)

            # 显示结果
            self._display_debate_results(topic, final_report)

        except Exception as e:
            logger.error(f"辩论处理失败: {e}")
            print(f"❌ 辩论处理失败: {e}")

    async def _select_debate_roles(self, topic: str) -> List[Any]:
        """智能选择辩论角色"""
        try:
            all_roles = self.role_manager.list_roles()

=======
            
            # 步骤2: 进行多轮辩论
            print(f"\n💭 步骤2: 开始{self.debate_config['min_rounds']}-{self.debate_config['max_rounds']}轮深度辩论...")
            debate_result = await self._conduct_real_debate(topic, selected_roles)
            
            # 步骤3: 共识计算
            print("\n🤝 步骤3: 计算共识与分歧...")
            consensus_result = await self._calculate_consensus_and_divergence(debate_result)
            
            # 步骤4: 生成综合报告
            print("\n📝 步骤4: 生成综合报告...")
            final_report = await self._generate_comprehensive_report(topic, debate_result, consensus_result)
            
            # 步骤5: 保存到Wiki
            print("\n📚 步骤5: 保存到Wiki知识库...")
            await self._save_to_wiki(topic, final_report)
            
            # 显示结果
            self._display_debate_results(topic, final_report)
            
        except Exception as e:
            logger.error(f"辩论处理失败: {e}")
            print(f"❌ 辩论处理失败: {e}")
    
    async def _select_debate_roles(self, topic: str) -> list[Any]:
        """智能选择辩论角色"""
        try:
            all_roles = self.role_manager.list_roles()
            
>>>>>>> feature/core-services-refactor
            # 使用LLM智能选择最相关的角色
            selection_prompt = f"""
作为角色选择专家，请从以下角色中选择3-4个最适合讨论"{topic}"的角色。
要求选择的角色具有不同的专业背景和观点，能够产生有价值的辩论。

可选角色列表:
{chr(10).join([f"- {role.name}: {role.description[:100]}..." for role in all_roles[:20]])}

请只返回选中的角色名称，每行一个，格式如下:
角色名称1
角色名称2
角色名称3
角色名称4
"""
<<<<<<< HEAD

            selected_names = await self._call_llm(selection_prompt, max_tokens=500)

=======
            
            selected_names = await self._call_llm(selection_prompt, max_tokens=500)
            
>>>>>>> feature/core-services-refactor
            # 解析选择结果
            selected_roles = []
            for line in selected_names.strip().split('\n'):
                role_name = line.strip()
                for role in all_roles:
                    if role_name in role.name:
                        selected_roles.append(role)
                        break
                if len(selected_roles) >= 4:
                    break
<<<<<<< HEAD

            # 如果LLM选择失败，使用默认策略
            if len(selected_roles) < 3:
                selected_roles = all_roles[:4]

            return selected_roles[:4]

=======
            
            # 如果LLM选择失败，使用默认策略
            if len(selected_roles) < 3:
                selected_roles = all_roles[:4]
            
            return selected_roles[:4]
            
>>>>>>> feature/core-services-refactor
        except Exception as e:
            logger.error(f"角色选择失败: {e}")
            # 返回前4个角色作为备选
            return self.role_manager.list_roles()[:4]
<<<<<<< HEAD

    async def _conduct_real_debate(self, topic: str, roles: List[Any]) -> Dict[str, Any]:
        """进行真实的多轮辩论"""
        debate_history = []
        round_count = 0

        print(f"  🎯 辩论议题: {topic}")
        print(f"  👥 参与角色: {len(roles)}个")
        print(f"  🔄 计划轮数: {self.debate_config['min_rounds']}-{self.debate_config['max_rounds']}轮")

=======
    
    async def _conduct_real_debate(self, topic: str, roles: list[Any]) -> dict[str, Any]:
        """进行真实的多轮辩论"""
        debate_history = []
        round_count = 0
        
        print(f"  🎯 辩论议题: {topic}")
        print(f"  👥 参与角色: {len(roles)}个")
        print(f"  🔄 计划轮数: {self.debate_config['min_rounds']}-{self.debate_config['max_rounds']}轮")
        
>>>>>>> feature/core-services-refactor
        # 初始化每个角色的立场
        for role in roles:
            initial_prompt = f"""
你是{role.name}。以下是你的专业背景和特点:
{role.description}

现在需要你就"{topic}"这个议题发表你的专业观点。

要求:
1. 发言不少于500字
2. 体现你的专业背景和独特视角
3. 提出具体的观点和论据
4. 可以适当质疑其他可能的观点

请开始你的发言:
"""
<<<<<<< HEAD

            print(f"\n  🤖 {role.name} 正在深度思考...")
            response = await self._call_llm(initial_prompt, max_tokens=2000)

=======
            
            print(f"\n  🤖 {role.name} 正在深度思考...")
            response = await self._call_llm(initial_prompt, max_tokens=2000)
            
>>>>>>> feature/core-services-refactor
            debate_entry = {
                "round": 1,
                "role_name": role.name,
                "role_id": role.id,
                "response": response,
                "timestamp": datetime.now(),
                "word_count": len(response.split())
            }
<<<<<<< HEAD

            debate_history.append(debate_entry)
            print(f"  ✅ {role.name}: {len(response.split())}字 - {response[:100]}...")

        round_count = 1

        # 进行多轮辩论
        for round_num in range(2, self.debate_config['max_rounds'] + 1):
            print(f"\n  🔄 第{round_num}轮辩论开始...")

            # 为每个角色准备上下文
            context = self._build_debate_context(debate_history, round_num - 1)

            round_responses = []

=======
            
            debate_history.append(debate_entry)
            print(f"  ✅ {role.name}: {len(response.split())}字 - {response[:100]}...")
        
        round_count = 1
        
        # 进行多轮辩论
        for round_num in range(2, self.debate_config['max_rounds'] + 1):
            print(f"\n  🔄 第{round_num}轮辩论开始...")
            
            # 为每个角色准备上下文
            context = self._build_debate_context(debate_history, round_num - 1)
            
            round_responses = []
            
>>>>>>> feature/core-services-refactor
            for role in roles:
                debate_prompt = f"""
你是{role.name}。以下是你的专业背景:
{role.description}

辩论议题: {topic}

以下是前面几轮的辩论内容:
{context}

现在是第{round_num}轮辩论。请基于前面的讨论内容:
1. 回应其他角色的观点
2. 进一步阐述或修正你的立场
3. 提出新的论据或反驳
4. 发言不少于500字
5. 保持你的专业角色特色

请开始你的发言:
"""
<<<<<<< HEAD

                print(f"    🤖 {role.name} 正在回应...")
                response = await self._call_llm(debate_prompt, max_tokens=2000)

=======
                
                print(f"    🤖 {role.name} 正在回应...")
                response = await self._call_llm(debate_prompt, max_tokens=2000)
                
>>>>>>> feature/core-services-refactor
                debate_entry = {
                    "round": round_num,
                    "role_name": role.name,
                    "role_id": role.id,
                    "response": response,
                    "timestamp": datetime.now(),
                    "word_count": len(response.split())
                }
<<<<<<< HEAD

                debate_history.append(debate_entry)
                round_responses.append(debate_entry)
                print(f"    ✅ {role.name}: {len(response.split())}字")

=======
                
                debate_history.append(debate_entry)
                round_responses.append(debate_entry)
                print(f"    ✅ {role.name}: {len(response.split())}字")
            
>>>>>>> feature/core-services-refactor
            # 检查是否达到最小轮数
            if round_num >= self.debate_config['min_rounds']:
                # 评估是否需要继续辩论
                if await self._should_continue_debate(round_responses):
                    continue
                else:
                    print(f"  🏁 辩论在第{round_num}轮自然结束")
                    break
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        return {
            "topic": topic,
            "participants": [role.name for role in roles],
            "total_rounds": round_num,
            "debate_history": debate_history,
            "total_words": sum(entry["word_count"] for entry in debate_history)
        }
<<<<<<< HEAD

    def _build_debate_context(self, debate_history: List[Dict], max_rounds: int) -> str:
        """构建辩论上下文"""
        context = ""

=======
    
    def _build_debate_context(self, debate_history: list[dict], max_rounds: int) -> str:
        """构建辩论上下文"""
        context = ""
        
>>>>>>> feature/core-services-refactor
        for round_num in range(1, max_rounds + 1):
            round_entries = [entry for entry in debate_history if entry["round"] == round_num]
            if round_entries:
                context += f"\n=== 第{round_num}轮 ===\n"
                for entry in round_entries:
                    # 只显示前200字作为上下文
                    preview = entry["response"][:200] + "..." if len(entry["response"]) > 200 else entry["response"]
                    context += f"\n{entry['role_name']}: {preview}\n"
<<<<<<< HEAD

        return context

    async def _should_continue_debate(self, round_responses: List[Dict]) -> bool:
=======
        
        return context
    
    async def _should_continue_debate(self, round_responses: list[dict]) -> bool:
>>>>>>> feature/core-services-refactor
        """判断是否应该继续辩论"""
        try:
            # 简单策略：如果回应中包含新观点或强烈反驳，继续辩论
            continue_keywords = ["但是", "然而", "不同意", "反对", "质疑", "新的观点", "进一步", "补充"]
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            for response in round_responses:
                content = response["response"]
                if any(keyword in content for keyword in continue_keywords):
                    return True
<<<<<<< HEAD

            return False

        except Exception as e:
            logger.error(f"判断辩论继续失败: {e}")
            return False

    async def _calculate_consensus_and_divergence(self, debate_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算共识与分歧"""
        try:
            debate_history = debate_result["debate_history"]

=======
            
            return False
            
        except Exception as e:
            logger.error(f"判断辩论继续失败: {e}")
            return False
    
    async def _calculate_consensus_and_divergence(self, debate_result: dict[str, Any]) -> dict[str, Any]:
        """计算共识与分歧"""
        try:
            debate_history = debate_result["debate_history"]
            
>>>>>>> feature/core-services-refactor
            # 使用LLM分析共识和分歧
            analysis_prompt = f"""
作为辩论分析专家，请分析以下多轮辩论的共识和分歧情况。

辩论议题: {debate_result['topic']}
参与者: {', '.join(debate_result['participants'])}
总轮数: {debate_result['total_rounds']}

辩论内容摘要:
{self._summarize_debate_for_analysis(debate_history)}

请分析并返回以下内容:
1. 共识点 (各方都认同的观点)
2. 主要分歧 (存在明显分歧的观点)
3. 共识度评分 (0-1之间的数值)
4. 分歧度评分 (0-1之间的数值)

请按以下格式返回:
共识点:
- [共识点1]
- [共识点2]

主要分歧:
- [分歧点1]
- [分歧点2]

共识度: [0.XX]
分歧度: [0.XX]
"""
<<<<<<< HEAD

            analysis_result = await self._call_llm(analysis_prompt, max_tokens=1500)

            # 解析分析结果
            consensus_score = 0.7  # 默认值
            divergence_score = 0.3  # 默认值

=======
            
            analysis_result = await self._call_llm(analysis_prompt, max_tokens=1500)
            
            # 解析分析结果
            consensus_score = 0.7  # 默认值
            divergence_score = 0.3  # 默认值
            
>>>>>>> feature/core-services-refactor
            # 尝试提取分数
            import re
            consensus_match = re.search(r'共识度:\s*([0-9.]+)', analysis_result)
            divergence_match = re.search(r'分歧度:\s*([0-9.]+)', analysis_result)
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            if consensus_match:
                consensus_score = float(consensus_match.group(1))
            if divergence_match:
                divergence_score = float(divergence_match.group(1))
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            return {
                "analysis_text": analysis_result,
                "consensus_score": consensus_score,
                "divergence_score": divergence_score,
                "total_participants": len(debate_result['participants']),
                "analysis_timestamp": datetime.now()
            }
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        except Exception as e:
            logger.error(f"共识分歧计算失败: {e}")
            return {
                "analysis_text": "分析过程中遇到技术问题",
                "consensus_score": 0.5,
                "divergence_score": 0.5,
                "total_participants": len(debate_result.get('participants', [])),
                "analysis_timestamp": datetime.now()
            }
<<<<<<< HEAD

    def _summarize_debate_for_analysis(self, debate_history: List[Dict]) -> str:
        """为分析总结辩论内容"""
        summary = ""

=======
    
    def _summarize_debate_for_analysis(self, debate_history: list[dict]) -> str:
        """为分析总结辩论内容"""
        summary = ""
        
>>>>>>> feature/core-services-refactor
        for entry in debate_history:
            # 每个发言只取前300字
            preview = entry["response"][:300] + "..." if len(entry["response"]) > 300 else entry["response"]
            summary += f"\n第{entry['round']}轮 - {entry['role_name']}: {preview}\n"
<<<<<<< HEAD

        return summary

    async def _generate_comprehensive_report(self, topic: str, debate_result: Dict, consensus_result: Dict) -> Dict[str, Any]:
=======
        
        return summary
    
    async def _generate_comprehensive_report(self, topic: str, debate_result: dict, consensus_result: dict) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """生成综合报告"""
        try:
            # 使用LLM生成高质量综合报告
            report_prompt = f"""
作为学术报告撰写专家，请基于以下多轮辩论内容生成一份高质量的综合研究报告。

辩论议题: {topic}
参与专家: {', '.join(debate_result['participants'])}
辩论轮数: {debate_result['total_rounds']}
总字数: {debate_result['total_words']}

共识分析:
{consensus_result['analysis_text']}

完整辩论记录:
{self._format_full_debate_for_report(debate_result['debate_history'])}

请生成一份不少于5000字的综合报告，包含以下部分:
1. 执行摘要 (500字)
2. 议题背景与重要性 (800字)
3. 各方观点详细分析 (2000字)
4. 共识与分歧分析 (800字)
5. 综合结论与建议 (900字)

要求:
- 学术性强，逻辑清晰
- 客观公正，平衡各方观点
- 结论有理有据
- 语言专业，表达准确
"""
<<<<<<< HEAD

            print("  📝 正在生成综合报告...")
            comprehensive_report = await self._call_llm(report_prompt, max_tokens=8000)

=======
            
            print("  📝 正在生成综合报告...")
            comprehensive_report = await self._call_llm(report_prompt, max_tokens=8000)
            
>>>>>>> feature/core-services-refactor
            return {
                "topic": topic,
                "report_content": comprehensive_report,
                "debate_summary": debate_result,
                "consensus_analysis": consensus_result,
                "generation_timestamp": datetime.now(),
                "word_count": len(comprehensive_report.split())
            }
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        except Exception as e:
            logger.error(f"生成综合报告失败: {e}")
            return {
                "topic": topic,
                "report_content": "报告生成过程中遇到技术问题",
                "debate_summary": debate_result,
                "consensus_analysis": consensus_result,
                "generation_timestamp": datetime.now(),
                "word_count": 0
            }
<<<<<<< HEAD

    def _format_full_debate_for_report(self, debate_history: List[Dict]) -> str:
        """为报告格式化完整辩论记录"""
        formatted = ""

=======
    
    def _format_full_debate_for_report(self, debate_history: list[dict]) -> str:
        """为报告格式化完整辩论记录"""
        formatted = ""
        
>>>>>>> feature/core-services-refactor
        current_round = 0
        for entry in debate_history:
            if entry["round"] != current_round:
                current_round = entry["round"]
                formatted += f"\n=== 第{current_round}轮辩论 ===\n"
<<<<<<< HEAD

            formatted += f"\n【{entry['role_name']}】\n{entry['response']}\n"

        return formatted

    async def _save_to_wiki(self, topic: str, report: Dict[str, Any]):
        """保存到Wiki"""
        try:
            title = f"深度辩论报告：{topic}"

=======
            
            formatted += f"\n【{entry['role_name']}】\n{entry['response']}\n"
        
        return formatted
    
    async def _save_to_wiki(self, topic: str, report: dict[str, Any]):
        """保存到Wiki"""
        try:
            title = f"深度辩论报告：{topic}"
            
>>>>>>> feature/core-services-refactor
            content = f"""# {title}

**生成时间**: {report['generation_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
**报告字数**: {report['word_count']}字
**辩论轮数**: {report['debate_summary']['total_rounds']}轮
**参与专家**: {', '.join(report['debate_summary']['participants'])}

## 综合报告

{report['report_content']}

## 辩论统计

- **总发言字数**: {report['debate_summary']['total_words']}字
- **共识度**: {report['consensus_analysis']['consensus_score']:.2f}
- **分歧度**: {report['consensus_analysis']['divergence_score']:.2f}

---
*本报告由DAIP-LIVE真实LLM辩论助手自动生成*
"""
<<<<<<< HEAD

            self.wiki_service.create_entry(title, content, "debate_assistant", ["辩论", "研究"], "深度分析")
            print("  ✅ 报告已保存到Wiki知识库")

        except Exception as e:
            logger.error(f"保存到Wiki失败: {e}")
            print("  ⚠️ Wiki保存失败，但报告已生成")

=======
            
            self.wiki_service.create_entry(title, content, "debate_assistant", ["辩论", "研究"], "深度分析")
            print("  ✅ 报告已保存到Wiki知识库")
            
        except Exception as e:
            logger.error(f"保存到Wiki失败: {e}")
            print("  ⚠️ Wiki保存失败，但报告已生成")
    
>>>>>>> feature/core-services-refactor
    async def _call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用真实LLM"""
        try:
            payload = {
                "model": self.llm_config["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.llm_config["temperature"],
                    "num_predict": max_tokens
                }
            }
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            response = requests.post(
                f"{self.llm_config['base_url']}/api/generate",
                json=payload,
                timeout=120
            )
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"LLM调用失败: {response.status_code}")
                return "LLM调用失败，请检查服务状态"
<<<<<<< HEAD

        except Exception as e:
            logger.error(f"LLM调用异常: {e}")
            return f"LLM调用异常: {str(e)}"

    def _display_debate_results(self, topic: str, report: Dict[str, Any]):
=======
                
        except Exception as e:
            logger.error(f"LLM调用异常: {e}")
            return f"LLM调用异常: {str(e)}"
    
    def _display_debate_results(self, topic: str, report: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """显示辩论结果"""
        print("\n" + "="*70)
        print("🎉 真实LLM多轮辩论完成！")
        print("="*70)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        print(f"📋 辩论议题: {topic}")
        print(f"👥 参与专家: {', '.join(report['debate_summary']['participants'])}")
        print(f"🔄 辩论轮数: {report['debate_summary']['total_rounds']}轮")
        print(f"📝 总发言字数: {report['debate_summary']['total_words']}字")
        print(f"📊 综合报告字数: {report['word_count']}字")
<<<<<<< HEAD

        print(f"\n🤝 共识度: {report['consensus_analysis']['consensus_score']:.2f}")
        print(f"⚡ 分歧度: {report['consensus_analysis']['divergence_score']:.2f}")

        print("\n📚 完整报告已保存到Wiki知识库")
        print(f"🕒 生成时间: {report['generation_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

=======
        
        print(f"\n🤝 共识度: {report['consensus_analysis']['consensus_score']:.2f}")
        print(f"⚡ 分歧度: {report['consensus_analysis']['divergence_score']:.2f}")
        
        print("\n📚 完整报告已保存到Wiki知识库")
        print(f"🕒 生成时间: {report['generation_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
>>>>>>> feature/core-services-refactor
        # 显示报告预览
        if report['report_content']:
            preview = report['report_content'][:500] + "..." if len(report['report_content']) > 500 else report['report_content']
            print("\n📖 报告预览:")
            print("-" * 50)
            print(preview)
            print("-" * 50)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        print("="*70)


async def main():
    """主函数"""
    try:
        assistant = RealLLMDebateAssistant()
        await assistant.start_conversation()
    except Exception as e:
        logger.error(f"系统运行失败: {e}")
        print(f"❌ 系统运行失败: {e}")


if __name__ == "__main__":
<<<<<<< HEAD
    asyncio.run(main())
=======
    asyncio.run(main())
>>>>>>> feature/core-services-refactor
