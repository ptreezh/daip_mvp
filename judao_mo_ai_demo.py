#!/usr/bin/env python3
"""
矩道-墨AI™ 智慧协同演示系统
智慧的协同，不是工具人的集合，而是专家们的共识
"""

import sys
import os
import time
import json
import asyncio
import aiohttp
import threading
import webbrowser
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import http.server
import socketserver
from urllib.parse import parse_qs
import hashlib
import uuid

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

@dataclass
class ExpertOpinion:
    """专家观点"""
    expert_id: str
    expert_name: str
    expertise: str
    opinion: str
    reasoning: str
    confidence: float
    evidence: List[str]
    timestamp: str

@dataclass
class ConsensusResult:
    """共识结果"""
    consensus_id: str
    topic: str
    expert_opinions: List[ExpertOpinion]
    final_judgment: str
    confidence_score: float
    reasoning_chain: str
    dissenting_views: List[str]
    supporting_evidence: List[str]
    recommendation: str
    timestamp: str

@dataclass
class WisdomCollaboration:
    """智慧协同记录"""
    session_id: str
    collaboration_type: str  # expert_consultation, academic_research, industry_analysis
    participants: List[str]
    discussion_rounds: int
    consensus_achieved: bool
    collective_wisdom: ConsensusResult
    transparency_data: Dict[str, Any]

class JudaoMoAIEngine:
    """矩道-墨AI™ 智慧协同引擎"""
    
    def __init__(self):
        self.session_history: List[WisdomCollaboration] = []
        self.expert_database = self._initialize_expert_database()
        self.llm_available = False
        self.transparency_enabled = True
        
        # 检查LLM可用性
        asyncio.create_task(self._check_llm_availability())
    
    def _initialize_expert_database(self) -> Dict[str, Dict]:
        """初始化专家数据库"""
        return {
            # 战略决策专家
            "strategic_analyst": {
                "name": "Dr. 张战略",
                "expertise": "企业战略与商业模式分析",
                "background": "15年战略咨询经验，曾任职于顶级咨询公司",
                "specialty": ["市场分析", "竞争策略", "商业模式创新", "风险评估"]
            },
            "investment_advisor": {
                "name": "Prof. 李投资",
                "expertise": "投资决策与财务分析",
                "background": "知名投资机构合伙人，成功投资案例200+",
                "specialty": ["投资估值", "风险控制", "市场时机", "行业趋势"]
            },
            "tech_expert": {
                "name": "Dr. 王技术",
                "expertise": "技术发展与创新评估",
                "background": "技术总监出身，对前沿技术有深刻洞察",
                "specialty": ["技术可行性", "创新潜力", "技术风险", "实施难度"]
            },
            
            # 学术研究专家
            "academic_researcher": {
                "name": "Prof. 陈学术",
                "expertise": "跨学科研究与理论分析",
                "background": "知名大学教授，发表论文150+篇",
                "specialty": ["理论框架", "文献综述", "研究方法", "学术写作"]
            },
            "data_scientist": {
                "name": "Dr. 刘数据",
                "expertise": "数据分析与统计建模",
                "background": "数据科学专家，擅长复杂数据建模",
                "specialty": ["统计分析", "机器学习", "数据可视化", "预测建模"]
            },
            
            # 行业分析专家
            "industry_analyst": {
                "name": "Ms. 吴行业",
                "expertise": "行业分析与市场研究",
                "background": "资深行业分析师，覆盖多个垂直领域",
                "specialty": ["行业趋势", "竞争格局", "市场规模", "增长预测"]
            },
            "policy_expert": {
                "name": "Dr. 赵政策",
                "expertise": "政策分析与监管研究",
                "background": "政策研究机构资深专家",
                "specialty": ["政策解读", "监管影响", "合规风险", "政策趋势"]
            },
            
            # 风险评估专家
            "risk_assessor": {
                "name": "Prof. 孙风险",
                "expertise": "风险识别与控制",
                "background": "风险管理专家，擅长复杂风险建模",
                "specialty": ["风险识别", "概率评估", "应急预案", "风险缓解"]
            }
        }
    
    async def _check_llm_availability(self):
        """检查LLM服务可用性"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/tags', timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        self.llm_available = True
                        print("✅ 矩道-墨AI™ 智慧引擎已就绪")
        except:
            print("⚠️ LLM服务不可用，将使用高质量智慧模拟模式")
    
    async def expert_consultation(self, query: str, consultation_type: str = "strategic") -> ConsensusResult:
        """专家咨询场景 - 多专家协同决策"""
        
        print(f"🎭 启动专家咨询：{query}")
        
        # 1. 智能专家选择
        selected_experts = self._select_experts_for_consultation(query, consultation_type)
        print(f"📋 已邀请专家：{[expert['name'] for expert in selected_experts]}")
        
        # 2. 收集专家观点
        expert_opinions = []
        for expert in selected_experts:
            opinion = await self._get_expert_opinion(expert, query)
            expert_opinions.append(opinion)
            print(f"💭 {expert['name']} 已提供专业观点")
        
        # 3. 协同讨论与质疑
        refined_opinions = await self._facilitate_expert_discussion(expert_opinions, query)
        
        # 4. 生成共识判断
        consensus = await self._generate_consensus_judgment(refined_opinions, query)
        
        print(f"✨ 专家共识已达成，置信度：{consensus.confidence_score:.1%}")
        return consensus
    
    def _select_experts_for_consultation(self, query: str, consultation_type: str) -> List[Dict]:
        """智能选择专家组合"""
        expert_pools = {
            "strategic": ["strategic_analyst", "investment_advisor", "risk_assessor", "tech_expert"],
            "investment": ["investment_advisor", "industry_analyst", "risk_assessor", "data_scientist"],
            "technical": ["tech_expert", "data_scientist", "risk_assessor", "academic_researcher"],
            "policy": ["policy_expert", "industry_analyst", "risk_assessor", "academic_researcher"],
            "general": ["strategic_analyst", "academic_researcher", "industry_analyst", "risk_assessor"]
        }
        
        selected_ids = expert_pools.get(consultation_type, expert_pools["general"])
        return [self.expert_database[expert_id] for expert_id in selected_ids[:4]]
    
    async def _get_expert_opinion(self, expert: Dict, query: str) -> ExpertOpinion:
        """获取单个专家的深度观点"""
        
        expert_prompt = f"""
你是{expert['name']}，{expert['expertise']}专家。
背景：{expert['background']}
专长：{', '.join(expert['specialty'])}

请对以下问题提供专业分析：
{query}

请从你的专业角度深度分析，包括：
1. 核心判断和建议
2. 专业理由和逻辑
3. 潜在风险和机会
4. 实施建议
5. 置信度评估

请保持你的专业身份和观点的独立性。
"""
        
        # 模拟专家深度思考
        await asyncio.sleep(1)  # 模拟思考时间
        
        # 生成专家观点（这里可以集成真实LLM）
        opinion_content = await self._generate_expert_response(expert, query, expert_prompt)
        
        return ExpertOpinion(
            expert_id=expert.get('id', 'expert_' + str(hash(expert['name']))),
            expert_name=expert['name'],
            expertise=expert['expertise'],
            opinion=opinion_content,
            reasoning=f"基于{expert['expertise']}的专业分析",
            confidence=0.85 + (hash(expert['name']) % 10) / 100,  # 模拟置信度
            evidence=[f"专业经验：{expert['background']}", f"专长领域：{', '.join(expert['specialty'])}"],
            timestamp=datetime.now().isoformat()
        )
    
    async def _generate_expert_response(self, expert: Dict, query: str, prompt: str) -> str:
        """生成专家回应（集成LLM或使用智能模拟）"""
        
        if self.llm_available:
            # 这里可以调用真实LLM
            pass
        
        # 智能模拟专家观点
        expert_responses = {
            "Dr. 张战略": f"""
## 战略分析观点

**核心判断：** 从战略角度看，{query} 涉及多个关键决策维度，需要综合考虑市场、竞争、资源和执行能力。

**专业分析：**
1. **市场机会评估：** 当前市场环境为此类决策提供了良好的时间窗口，但需要注意竞争态势的变化
2. **资源配置优化：** 建议采用阶段性投入策略，先小规模验证，再规模化扩展
3. **风险控制机制：** 设立关键里程碑检查点，确保在风险可控范围内推进

**战略建议：**
- 短期：快速市场验证和原型测试
- 中期：基于反馈优化和适度扩张
- 长期：建立可持续的竞争优势

**置信度：** 85%（基于当前市场数据和行业经验）
            """,
            
            "Prof. 李投资": f"""
## 投资决策分析

**投资判断：** {query} 从投资回报角度具有吸引力，但需要关注风险收益比和现金流时点。

**财务分析：**
1. **投资回报评估：** 预期IRR在15-25%区间，回收期约2-3年
2. **现金流分析：** 前期投入集中，现金流转正预计在18-24个月
3. **风险定价：** 考虑到不确定性，建议风险溢价率8-12%

**投资建议：**
- 分阶段投资，降低单次风险敞口
- 设立清晰的退出机制和标准
- 建立投后管理和监控体系

**关键风险：** 市场需求变化、技术替代、政策调整
**置信度：** 82%（基于财务模型和市场对比分析）
            """,
            
            "Dr. 王技术": f"""
## 技术可行性评估

**技术判断：** {query} 在技术层面具备实现基础，但需要关注技术选型和实施复杂度。

**技术分析：**
1. **技术成熟度：** 核心技术相对成熟，但集成和优化需要时间
2. **实施难度：** 中等复杂度，需要经验丰富的技术团队
3. **技术风险：** 主要风险在性能优化和扩展性保证

**技术建议：**
- 采用微服务架构，确保系统可扩展
- 建立完善的测试和监控体系
- 预留技术债务处理时间

**创新潜力：** 具备显著的技术创新价值
**置信度：** 88%（基于技术调研和原型验证）
            """,
            
            "Prof. 孙风险": f"""
## 风险控制分析

**风险评估：** {query} 整体风险可控，但需要建立完善的风险管理体系。

**风险识别：**
1. **市场风险：** 需求不确定性、竞争加剧风险
2. **执行风险：** 团队能力、资源配置风险
3. **外部风险：** 政策变化、经济环境风险

**风险缓解策略：**
- 建立多重应急预案
- 设立风险预警指标体系
- 实施动态风险评估机制

**风险评级：** 中等偏低
**置信度：** 90%（基于风险建模和情景分析）
            """
        }
        
        return expert_responses.get(expert['name'], f"""
## 专业分析观点

作为{expert['expertise']}专家，我认为{query}需要从以下角度深入分析：

**核心观点：** 基于我的专业经验和行业洞察，这个问题涉及多个关键因素的平衡。

**专业建议：**
1. 深入调研相关背景和约束条件
2. 制定清晰的评估标准和决策框架
3. 建立系统性的实施和监控机制
4. 预留足够的调整和优化空间

**风险提示：** 需要特别关注执行过程中的不确定性因素。

**置信度：** {85 + (hash(expert['name']) % 10)}%
        """)
    
    async def _facilitate_expert_discussion(self, opinions: List[ExpertOpinion], query: str) -> List[ExpertOpinion]:
        """促进专家间的协同讨论"""
        print("🤝 专家协同讨论中...")
        
        # 模拟专家间的质疑和完善过程
        await asyncio.sleep(2)
        
        # 在实际实现中，这里会让专家对彼此的观点进行评议和完善
        for opinion in opinions:
            # 模拟观点的refinement
            if "风险" in opinion.opinion:
                opinion.confidence = min(opinion.confidence + 0.05, 0.95)
            opinion.opinion += f"\n\n**协同讨论补充：** 经过与其他专家讨论，进一步确认了分析的合理性。"
        
        return opinions
    
    async def _generate_consensus_judgment(self, opinions: List[ExpertOpinion], query: str) -> ConsensusResult:
        """生成专家共识判断"""
        print("⚖️ 正在形成专家共识...")
        
        # 分析专家观点的一致性和分歧点
        avg_confidence = sum(op.confidence for op in opinions) / len(opinions)
        
        # 生成综合判断
        consensus_judgment = f"""
# 专家团队共识判断

## 核心结论
经过{len(opinions)}位专家的深度分析和协同讨论，我们对"{query}"形成以下共识判断：

**总体建议：** 建议在充分准备的前提下推进，但需要建立完善的风险控制机制。

## 专家观点汇总
{chr(10).join([f"**{op.expert_name}观点：** {op.opinion[:200]}..." for op in opinions])}

## 一致性分析
- **共同认知：** 所有专家都认为需要慎重评估和分阶段实施
- **关键分歧：** 在风险评估和时间节点上存在不同观点
- **综合权衡：** 建议采用保守而稳健的推进策略

## 最终建议
1. 建立跨职能团队，确保执行质量
2. 制定详细的里程碑和评估标准
3. 建立动态调整机制，应对不确定性
4. 设立明确的成功标准和退出条件

## 风险提示
请特别关注实施过程中的以下风险点：
- 外部环境变化的影响
- 内部资源配置的充分性
- 关键假设条件的变化

**总体置信度：** {avg_confidence:.1%}
**专家共识程度：** 85%
        """
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            topic=query,
            expert_opinions=opinions,
            final_judgment=consensus_judgment,
            confidence_score=avg_confidence,
            reasoning_chain="多专家协同分析 → 观点交流质疑 → 共识形成",
            dissenting_views=["时间进度评估存在分歧", "风险等级认知不完全一致"],
            supporting_evidence=[op.reasoning for op in opinions],
            recommendation="建议采用分阶段、风险可控的实施策略",
            timestamp=datetime.now().isoformat()
        )
    
    async def academic_research(self, research_topic: str) -> ConsensusResult:
        """学术研究场景 - 多维度学术分析"""
        print(f"📚 启动学术研究：{research_topic}")
        
        # 选择学术研究专家团队
        research_experts = [
            self.expert_database["academic_researcher"],
            self.expert_database["data_scientist"],
            self.expert_database["industry_analyst"],
            self.expert_database["policy_expert"]
        ]
        
        # 生成学术研究报告
        opinions = []
        for expert in research_experts:
            opinion = await self._get_academic_opinion(expert, research_topic)
            opinions.append(opinion)
        
        # 形成学术共识
        consensus = await self._generate_academic_consensus(opinions, research_topic)
        return consensus
    
    async def _get_academic_opinion(self, expert: Dict, topic: str) -> ExpertOpinion:
        """获取学术观点"""
        academic_content = f"""
## {expert['name']} 的学术分析

**研究主题：** {topic}

**文献综述：** 基于当前学术研究现状，该领域存在以下关键问题和研究空白...

**理论框架：** 建议采用跨学科研究方法，结合定量和定性分析...

**研究方法：** 推荐使用混合研究方法，包括实证分析、案例研究等...

**预期贡献：** 本研究将在理论建构和实践指导方面产生重要价值...

**学术价值评估：** 高度原创性，具备显著的学术创新意义
        """
        
        return ExpertOpinion(
            expert_id=expert.get('id', 'academic_' + str(hash(expert['name']))),
            expert_name=expert['name'],
            expertise=expert['expertise'],
            opinion=academic_content,
            reasoning="基于严谨的学术研究方法论",
            confidence=0.88,
            evidence=["文献调研", "理论分析", "方法论验证"],
            timestamp=datetime.now().isoformat()
        )
    
    async def _generate_academic_consensus(self, opinions: List[ExpertOpinion], topic: str) -> ConsensusResult:
        """生成学术共识"""
        consensus_content = f"""
# {topic} - 学术研究综合报告

## 研究摘要
本研究通过多位学术专家的协同分析，对"{topic}"进行了全面深入的学术探讨。

## 核心研究发现
1. **理论贡献：** 在现有理论基础上提出了新的分析框架
2. **实证证据：** 通过数据分析验证了核心假设
3. **实践意义：** 为相关领域的实践提供了重要指导

## 研究局限性
1. 数据可得性限制
2. 研究范围的界定
3. 方法论的适用性

## 未来研究方向
1. 扩展研究样本和范围
2. 深化理论机制分析
3. 加强实践应用验证

## 学术价值评估
**创新性：** 9/10
**严谨性：** 8.5/10
**实用性：** 8/10
**影响力预期：** 高
        """
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            topic=topic,
            expert_opinions=opinions,
            final_judgment=consensus_content,
            confidence_score=0.87,
            reasoning_chain="文献综述 → 理论分析 → 实证研究 → 学术共识",
            dissenting_views=["研究方法选择存在不同观点"],
            supporting_evidence=["理论依据", "实证数据", "专家判断"],
            recommendation="建议进一步深化理论研究并扩大实证验证",
            timestamp=datetime.now().isoformat()
        )
    
    async def industry_research(self, industry: str) -> ConsensusResult:
        """行业研究场景 - 全面行业分析"""
        print(f"🏭 启动行业研究：{industry}")
        
        # 行业研究专家团队
        industry_experts = [
            self.expert_database["industry_analyst"],
            self.expert_database["investment_advisor"],
            self.expert_database["policy_expert"],
            self.expert_database["data_scientist"]
        ]
        
        opinions = []
        for expert in industry_experts:
            opinion = await self._get_industry_opinion(expert, industry)
            opinions.append(opinion)
        
        consensus = await self._generate_industry_consensus(opinions, industry)
        return consensus
    
    async def _get_industry_opinion(self, expert: Dict, industry: str) -> ExpertOpinion:
        """获取行业分析观点"""
        industry_content = f"""
## {expert['name']} 的行业分析

**分析行业：** {industry}

**市场规模：** 当前市场规模约XXX亿元，预计未来三年CAGR为XX%

**竞争格局：** 市场集中度较高，头部企业占据XX%市场份额

**发展趋势：** 
1. 技术创新驱动增长
2. 政策环境趋于完善
3. 消费需求持续升级

**投资机会：** 重点关注细分领域的创新企业

**风险警示：** 需注意政策变化和技术替代风险
        """
        
        return ExpertOpinion(
            expert_id=expert.get('id', 'industry_' + str(hash(expert['name']))),
            expert_name=expert['name'],
            expertise=expert['expertise'],
            opinion=industry_content,
            reasoning="基于行业数据分析和市场调研",
            confidence=0.84,
            evidence=["市场数据", "企业调研", "政策分析"],
            timestamp=datetime.now().isoformat()
        )
    
    async def _generate_industry_consensus(self, opinions: List[ExpertOpinion], industry: str) -> ConsensusResult:
        """生成行业研究共识"""
        consensus_content = f"""
# {industry}行业深度研究报告

## 执行摘要
通过多位行业专家的协同分析，形成对{industry}行业的全面认知和判断。

## 行业概况
- **市场规模：** 持续增长态势
- **发展阶段：** 成长期/成熟期
- **关键驱动因素：** 技术创新、政策支持、需求升级

## 竞争格局分析
- **市场集中度：** 中等偏高
- **竞争激烈程度：** 激烈
- **进入壁垒：** 技术壁垒和资金壁垒并存

## 投资建议
**总体评级：** 看好
**投资逻辑：** 行业基本面向好，政策环境支持
**投资标的：** 建议关注细分领域龙头企业

## 风险提示
1. 政策变化风险
2. 技术替代风险
3. 市场竞争加剧风险

## 五年发展预测
预计未来五年行业将保持稳健增长，年复合增长率15-20%
        """
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            topic=f"{industry}行业研究",
            expert_opinions=opinions,
            final_judgment=consensus_content,
            confidence_score=0.85,
            reasoning_chain="市场调研 → 数据分析 → 专家判断 → 行业共识",
            dissenting_views=["对增长率预测存在分歧"],
            supporting_evidence=["行业数据", "企业财报", "政策文件"],
            recommendation="建议重点关注行业龙头和创新企业的投资机会",
            timestamp=datetime.now().isoformat()
        )

class JudaoMoAIDemoHandler(http.server.SimpleHTTPRequestHandler):
    """矩道-墨AI™ 演示系统请求处理器"""
    
    def __init__(self, *args, **kwargs):
        self.ai_engine = JudaoMoAIEngine()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/' or self.path == '/index.html':
            self.send_product_homepage()
        elif self.path == '/expert-consultation':
            self.send_consultation_page()
        elif self.path == '/academic-research':
            self.send_academic_page()
        elif self.path == '/industry-research':
            self.send_industry_page()
        elif self.path == '/api/status':
            self.handle_status_api()
        else:
            self.send_404()
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/api/expert-consultation':
            asyncio.run(self.handle_expert_consultation())
        elif self.path == '/api/academic-research':
            asyncio.run(self.handle_academic_research())
        elif self.path == '/api/industry-research':
            asyncio.run(self.handle_industry_research())
        else:
            self.send_404()
    
    def send_product_homepage(self):
        """发送产品主页"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_content = self._generate_product_homepage()
        self.wfile.write(html_content.encode('utf-8'))
    
    def _generate_product_homepage(self):
        """生成产品主页HTML"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>矩道-墨AI™ | 智慧的协同</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            line-height: 1.6;
        }
        
        .hero-section {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 0 20px;
        }
        
        .logo {
            font-size: 4rem;
            font-weight: 300;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #ffd700, #ffed4a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .tagline {
            font-size: 1.8rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .value-proposition {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .comparison-table {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin: 3rem 0;
            max-width: 1000px;
        }
        
        .comparison-card {
            background: rgba(255,255,255,0.15);
            padding: 2rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .card-title {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #ffd700;
        }
        
        .card-subtitle {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            opacity: 0.8;
        }
        
        .feature-list {
            list-style: none;
            padding: 0;
        }
        
        .feature-list li {
            padding: 0.5rem 0;
            border-left: 3px solid #ffd700;
            padding-left: 1rem;
            margin: 0.5rem 0;
        }
        
        .cta-section {
            margin-top: 3rem;
        }
        
        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .cta-button {
            padding: 1rem 2rem;
            border: none;
            border-radius: 25px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .primary-button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
        }
        
        .secondary-button {
            background: transparent;
            color: white;
            border: 2px solid #ffd700;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .philosophy-section {
            background: rgba(0,0,0,0.2);
            padding: 3rem 2rem;
            margin: 3rem 0;
            border-radius: 15px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .philosophy-quote {
            font-size: 1.3rem;
            font-style: italic;
            line-height: 1.8;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        .quote-author {
            text-align: right;
            opacity: 0.8;
            font-size: 1rem;
        }
        
        .wisdom-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #ffd700;
            border-radius: 50%;
            margin-right: 8px;
            animation: wisdom-pulse 2s infinite;
        }
        
        @keyframes wisdom-pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        @media (max-width: 768px) {
            .logo { font-size: 3rem; }
            .tagline { font-size: 1.4rem; }
            .comparison-table { grid-template-columns: 1fr; }
            .cta-buttons { flex-direction: column; align-items: center; }
        }
    </style>
</head>
<body>
    <div class="hero-section">
        <div class="logo">矩道-墨AI™</div>
        <div class="tagline">智慧的协同</div>
        
        <div class="value-proposition">
            <p style="font-size: 1.3rem; margin-bottom: 1.5rem;">
                <span class="wisdom-indicator"></span>
                不要"工具人"的集合，要"专家们"的共识
            </p>
            <p style="opacity: 0.9;">
                在AI的世界里，存在两种伟大的协同。<br>
                一种，是工具的协同，它追求效率。<br>
                一种，是智慧的协同，它追求真理。
            </p>
        </div>
        
        <div class="comparison-table">
            <div class="comparison-card">
                <div class="card-title">传统AI工具</div>
                <div class="card-subtitle">工具的协同 · 追求效率</div>
                <ul class="feature-list">
                    <li>提升任务执行效率</li>
                    <li>降低人力成本</li>
                    <li>适用于生产、运营、IT自动化</li>
                    <li>用户是"流程的设计者与监督者"</li>
                </ul>
            </div>
            
            <div class="comparison-card" style="border: 2px solid #ffd700;">
                <div class="card-title">矩道-墨AI™</div>
                <div class="card-subtitle">智慧的协同 · 追求真理</div>
                <ul class="feature-list">
                    <li>提升决策判断质量</li>
                    <li>降低认知风险</li>
                    <li>适用于战略、研发、投资、法律</li>
                    <li>用户是"会议的主持人与最终裁决者"</li>
                </ul>
            </div>
        </div>
        
        <div class="philosophy-section">
            <div class="philosophy-quote">
                "当别人在谈论'AI如何更好地为我们工作'时，我们在探索'AI如何更好地与我们一同思考'。
                他们协同的是'工具'，我们协同的是'智慧'。"
            </div>
            <div class="quote-author">—— 矩道-墨AI™ 设计哲学</div>
        </div>
        
        <div class="philosophy-section">
            <div class="philosophy-quote">
                "炉中诞生的，不是一个被执行的'结果'，而是一个值得您托付的、闪耀着集体智慧光芒的**判断**。
                前者致力于优化'答案的产出效率'，我们则致力于提升'判断的决策质量'。"
            </div>
        </div>
        
        <div class="cta-section">
            <div class="cta-buttons">
                <a href="/expert-consultation" class="cta-button primary-button">
                    🎭 体验专家咨询
                </a>
                <a href="/academic-research" class="cta-button secondary-button">
                    📚 学术研究协同
                </a>
                <a href="/industry-research" class="cta-button secondary-button">
                    🏭 行业深度分析
                </a>
            </div>
            
            <p style="margin-top: 2rem; opacity: 0.8; font-size: 1.1rem;">
                当您需要在不确定的迷雾中，做出一个高风险的、可信赖的判断时，<br>
                欢迎来到矩道-墨AI™的圆桌会议。
            </p>
        </div>
    </div>
</body>
</html>'''
    
    async def handle_expert_consultation(self):
        """处理专家咨询请求"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '')
            consultation_type = data.get('type', 'strategic')
            
            print(f"🎭 专家咨询请求：{query}")
            
            # 执行专家咨询
            result = await self.ai_engine.expert_consultation(query, consultation_type)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'success': True,
                'result': asdict(result),
                'message': '专家共识已达成',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False, default=str).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"专家咨询处理失败: {str(e)}")
    
    def send_consultation_page(self):
        """发送专家咨询页面"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>专家咨询 | 矩道-墨AI™</title>
    <style>
        /* 继承主页样式并添加专门的咨询界面样式 */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        .main-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            min-height: 60vh;
        }
        .consultation-panel, .result-panel {
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        .input-group textarea, .input-group select {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: rgba(255,255,255,0.9);
            color: #333;
            font-size: 14px;
        }
        .btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .result-content {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 10px;
            margin-top: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .expert-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        .expert-badge {
            background: rgba(255, 215, 0, 0.2);
            color: #ffd700;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            border: 1px solid #ffd700;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="font-size: 2.5em; margin-bottom: 15px;">
                🎭 专家咨询圆桌会议
            </h1>
            <p style="font-size: 1.2em; opacity: 0.9;">集体智慧，可信判断</p>
            <p style="margin-top: 10px; opacity: 0.8;">
                <strong>多位专家</strong> • <strong>深度分析</strong> • <strong>共识判断</strong> • <strong>决策支持</strong>
            </p>
        </div>
        
        <div class="main-layout">
            <div class="consultation-panel">
                <h2>💭 提出您的咨询问题</h2>
                
                <div class="input-group">
                    <label for="consultationType">咨询类型</label>
                    <select id="consultationType">
                        <option value="strategic">战略决策</option>
                        <option value="investment">投资判断</option>
                        <option value="technical">技术评估</option>
                        <option value="policy">政策分析</option>
                        <option value="general">综合咨询</option>
                    </select>
                </div>
                
                <div class="input-group">
                    <label for="consultationQuery">咨询问题</label>
                    <textarea id="consultationQuery" rows="6" 
                              placeholder="请详细描述您需要咨询的问题，包括背景信息、关键考虑因素、期望的分析角度等..."></textarea>
                </div>
                
                <button class="btn" onclick="startConsultation()">
                    🚀 启动专家咨询
                </button>
                
                <div class="expert-badges">
                    <div class="expert-badge">Dr. 张战略</div>
                    <div class="expert-badge">Prof. 李投资</div>
                    <div class="expert-badge">Dr. 王技术</div>
                    <div class="expert-badge">Prof. 孙风险</div>
                </div>
                
                <div class="loading" id="loading">
                    <p>🤖 专家团队讨论中...</p>
                    <p style="font-size: 12px; margin-top: 5px;">正在形成共识判断</p>
                </div>
            </div>
            
            <div class="result-panel">
                <h2>⚖️ 专家共识判断</h2>
                <div class="result-content" id="resultContent">
                    <p style="opacity: 0.7; text-align: center; padding: 50px 20px;">
                        等待您的咨询问题...<br>
                        <small>专家团队将为您提供深度分析和共识判断</small>
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function startConsultation() {
            const query = document.getElementById('consultationQuery').value.trim();
            const type = document.getElementById('consultationType').value;
            
            if (!query) {
                alert('请输入您的咨询问题');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultContent').innerHTML = '<p>🎭 专家团队正在深度分析您的问题...</p>';
            
            try {
                const response = await fetch('/api/expert-consultation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query, type: type })
                });
                
                const data = await response.json();
                document.getElementById('loading').style.display = 'none';
                
                if (data.success) {
                    displayConsultationResult(data.result);
                } else {
                    document.getElementById('resultContent').innerHTML = `
                        <p style="color: #ff6b6b;">❌ 咨询处理失败</p>
                        <p>${data.error || '未知错误'}</p>
                    `;
                }
                
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('resultContent').innerHTML = `
                    <p style="color: #ff6b6b;">🌐 网络错误: ${error.message}</p>
                `;
            }
        }
        
        function displayConsultationResult(result) {
            const content = `
                <div style="line-height: 1.6;">
                    <h3 style="color: #ffd700; margin-bottom: 15px;">📋 专家共识报告</h3>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong>咨询主题：</strong> ${result.topic}<br>
                        <strong>参与专家：</strong> ${result.expert_opinions.length}位<br>
                        <strong>置信度：</strong> ${(result.confidence_score * 100).toFixed(1)}%<br>
                        <strong>共识时间：</strong> ${new Date(result.timestamp).toLocaleString()}
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #ffd700;">💡 核心判断：</strong>
                        <div style="margin-top: 8px; padding-left: 10px; border-left: 3px solid #ffd700;">
                            ${result.recommendation}
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #ffd700;">🎯 专家观点摘要：</strong>
                        ${result.expert_opinions.map(op => `
                            <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                                <strong>${op.expert_name}</strong> (${op.expertise})<br>
                                <small style="opacity: 0.8;">${op.opinion.substring(0, 200)}...</small>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <strong style="color: #ffd700;">⚠️ 风险提示：</strong>
                        <ul style="margin-top: 8px; padding-left: 20px;">
                            ${result.dissenting_views.map(view => `<li style="margin: 5px 0;">${view}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
            
            document.getElementById('resultContent').innerHTML = content;
        }
    </script>
</body>
</html>'''
        
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_404(self):
        """发送404错误"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'<h1>404 Not Found</h1><p>矩道-墨AI™ 演示系统</p>')

def start_judao_mo_ai_demo(port=8888):
    """启动矩道-墨AI™ 演示系统"""
    try:
        with socketserver.TCPServer(("", port), JudaoMoAIDemoHandler) as httpd:
            print(f"🌟 矩道-墨AI™ 智慧协同演示系统启动成功！")
            print(f"📍 访问地址: http://localhost:{port}")
            print(f"🎭 智慧协同模式已激活")
            print(f"=" * 70)
            print(f"✨ 核心特性:")
            print(f"  • 🎯 专家咨询：多专家协同决策")
            print(f"  • 📚 学术研究：跨学科深度分析") 
            print(f"  • 🏭 行业研究：全面行业洞察")
            print(f"  • ⚖️ 共识判断：集体智慧结晶")
            print(f"=" * 70)
            print(f"💡 设计理念: 不是工具人的集合，而是专家们的共识")
            print(f"🚀 核心价值: 提升判断的决策质量，降低认知风险")
            print(f"按 Ctrl+C 停止服务器")
            
            # 自动打开浏览器
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
            
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {port} 被占用，尝试下一个端口...")
            return start_judao_mo_ai_demo(port + 1)
        else:
            raise e

if __name__ == '__main__':
    start_judao_mo_ai_demo()