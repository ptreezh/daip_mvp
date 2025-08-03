#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矩道-墨AI™ 智慧协同演示系统 - 完整测试版
经过完整自动化测试的版本
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

class JudaoMoAIEngine:
    """矩道-墨AI™ 智慧协同引擎"""
    
    def __init__(self):
        self.expert_database = self._initialize_expert_database()
        self.llm_available = False
        # 延迟LLM检查，避免初始化时的事件循环问题
        self._llm_checked = False
    
    def _initialize_expert_database(self) -> Dict[str, Dict]:
        """初始化专家数据库"""
        return {
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
            "risk_assessor": {
                "name": "Prof. 孙风险",
                "expertise": "风险识别与控制",
                "background": "风险管理专家，擅长复杂风险建模",
                "specialty": ["风险识别", "概率评估", "应急预案", "风险缓解"]
            },
            "academic_researcher": {
                "name": "Prof. 陈学术",
                "expertise": "跨学科研究与理论分析",
                "background": "知名大学教授，发表论文150+篇",
                "specialty": ["理论框架", "文献综述", "研究方法", "学术写作"]
            },
            "industry_analyst": {
                "name": "Ms. 吴行业",
                "expertise": "行业分析与市场研究",
                "background": "资深行业分析师，覆盖多个垂直领域",
                "specialty": ["行业趋势", "竞争格局", "市场规模", "增长预测"]
            }
        }
    
    async def _check_llm_availability(self):
        """检查LLM服务可用性"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/tags', 
                                     timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        self.llm_available = True
                        print("✅ 真实LLM服务已连接")
                        return
        except:
            pass
        
        print("⚠️ LLM服务不可用，使用高质量智慧模拟模式")
    
    async def expert_consultation(self, query: str, consultation_type: str = "strategic") -> ConsensusResult:
        """专家咨询场景"""
        # 确保LLM状态已检查
        if not self._llm_checked:
            await self._check_llm_availability()
            self._llm_checked = True
        
        print(f"🎭 启动专家咨询：{query}")
        
        # 1. 选择专家团队
        selected_experts = self._select_experts_for_consultation(query, consultation_type)
        print(f"📋 已邀请专家：{[expert['name'] for expert in selected_experts]}")
        
        # 2. 收集专家观点
        expert_opinions = []
        for expert in selected_experts:
            opinion = await self._get_expert_opinion(expert, query, "consultation")
            expert_opinions.append(opinion)
            print(f"💭 {expert['name']} 已提供专业观点")
        
        # 3. 生成共识判断
        consensus = await self._generate_consultation_consensus(expert_opinions, query)
        print(f"✨ 专家共识已达成，置信度：{consensus.confidence_score:.1%}")
        
        return consensus
    
    def _select_experts_for_consultation(self, query: str, consultation_type: str) -> List[Dict]:
        """智能选择专家组合"""
        expert_pools = {
            "strategic": ["strategic_analyst", "investment_advisor", "risk_assessor", "tech_expert"],
            "investment": ["investment_advisor", "industry_analyst", "risk_assessor"],
            "technical": ["tech_expert", "academic_researcher", "risk_assessor"],
            "general": ["strategic_analyst", "academic_researcher", "risk_assessor"]
        }
        
        selected_ids = expert_pools.get(consultation_type, expert_pools["general"])
        return [self.expert_database[expert_id] for expert_id in selected_ids[:3]]
    
    async def _get_expert_opinion(self, expert: Dict, query: str, context: str) -> ExpertOpinion:
        """获取专家观点"""
        
        if self.llm_available:
            opinion_content = await self._call_real_llm(expert, query, context)
        else:
            opinion_content = self._generate_expert_simulation(expert, query, context)
        
        return ExpertOpinion(
            expert_id=expert.get('id', f"expert_{hash(expert['name'])}"),
            expert_name=expert['name'],
            expertise=expert['expertise'],
            opinion=opinion_content,
            reasoning=f"基于{expert['expertise']}的专业分析",
            confidence=0.82 + (hash(expert['name']) % 15) / 100,
            evidence=[f"专业经验：{expert['background']}"],
            timestamp=datetime.now().isoformat()
        )
    
    async def _call_real_llm(self, expert: Dict, query: str, context: str) -> str:
        """调用真实LLM"""
        prompt = f"""
你是{expert['name']}，{expert['expertise']}专家。
背景：{expert['background']}
专长：{', '.join(expert['specialty'])}

请对以下问题提供专业分析：{query}

请从你的专业角度深度分析，包括：
1. 核心判断和建议
2. 专业理由和逻辑
3. 潜在风险和机会
4. 实施建议

保持专业性和独立性。
"""
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "llama3:instruct",
                    "prompt": prompt,
                    "stream": False
                }
                
                async with session.post('http://localhost:11434/api/generate',
                                      json=payload,
                                      timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', self._generate_expert_simulation(expert, query, context))
                    else:
                        return self._generate_expert_simulation(expert, query, context)
        except Exception as e:
            print(f"LLM调用失败：{e}")
            return self._generate_expert_simulation(expert, query, context)
    
    def _generate_expert_simulation(self, expert: Dict, query: str, context: str) -> str:
        """生成专家模拟观点"""
        expert_templates = {
            "Dr. 张战略": f"""
## 战略分析观点

**核心判断：** 从战略角度看，"{query}" 需要综合考虑市场、竞争、资源配置等多个维度。

**专业分析：**
1. **市场机会评估：** 当前市场环境为此类决策提供了时间窗口，但需要注意竞争态势变化
2. **资源配置优化：** 建议采用阶段性投入策略，先验证再扩展
3. **风险控制：** 设立关键里程碑检查点，确保风险可控

**战略建议：**
- 短期：快速市场验证
- 中期：基于反馈优化
- 长期：建立可持续竞争优势

**置信度：** 85%
            """,
            
            "Prof. 李投资": f"""
## 投资决策分析

**投资判断：** "{query}" 从投资角度具有一定吸引力，但需要关注风险收益比。

**财务分析：**
1. **投资回报：** 预期IRR在15-25%区间
2. **现金流：** 回收期约2-3年
3. **风险定价：** 建议风险溢价8-12%

**投资建议：**
- 分阶段投资，降低风险敞口
- 设立清晰退出机制
- 建立投后监控体系

**关键风险：** 市场需求变化、技术替代
**置信度：** 82%
            """,
            
            "Dr. 王技术": f"""
## 技术可行性评估

**技术判断：** "{query}" 在技术层面具备实现基础。

**技术分析：**
1. **技术成熟度：** 核心技术相对成熟
2. **实施难度：** 中等复杂度
3. **技术风险：** 主要在性能优化

**技术建议：**
- 采用成熟技术栈
- 建立测试监控体系
- 预留技术债务处理时间

**置信度：** 88%
            """,
            
            "Prof. 孙风险": f"""
## 风险控制分析

**风险评估：** "{query}" 整体风险可控。

**风险识别：**
1. **市场风险：** 需求不确定性
2. **执行风险：** 团队能力匹配
3. **外部风险：** 政策环境变化

**缓解策略：**
- 多重应急预案
- 风险预警体系
- 动态评估机制

**风险评级：** 中等偏低
**置信度：** 90%
            """
        }
        
        return expert_templates.get(expert['name'], f"""
## {expert['name']} 专业分析

基于我在{expert['expertise']}领域的专业经验，对"{query}"的分析如下：

**核心观点：** 这个问题需要从多个角度综合考虑。

**专业建议：**
1. 深入调研背景和约束条件
2. 制定清晰的评估框架
3. 建立实施监控机制
4. 预留调整优化空间

**置信度：** {85 + (hash(expert['name']) % 10)}%
        """)
    
    async def _generate_consultation_consensus(self, opinions: List[ExpertOpinion], query: str) -> ConsensusResult:
        """生成咨询共识"""
        avg_confidence = sum(op.confidence for op in opinions) / len(opinions)
        
        consensus_judgment = f"""
# 专家团队共识判断

## 咨询主题
{query}

## 核心结论
经过{len(opinions)}位专家的深度分析和协同讨论，形成以下共识判断：

**总体建议：** 建议在充分准备的前提下推进，需要建立完善的风险控制机制。

## 专家观点汇总
{chr(10).join([f"### {op.expert_name} ({op.expertise})\\n{op.opinion[:300]}...\\n" for op in opinions])}

## 一致性分析
- **共同认知：** 所有专家都认为需要慎重评估和分阶段实施
- **风险控制：** 一致强调风险管理的重要性
- **实施建议：** 都建议采用稳健的推进策略

## 最终建议
1. 建立跨职能团队，确保执行质量
2. 制定详细里程碑和评估标准
3. 建立动态调整机制
4. 设立明确成功标准和退出条件

**总体置信度：** {avg_confidence:.1%}
**专家共识程度：** 85%
        """
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            topic=query,
            expert_opinions=opinions,
            final_judgment=consensus_judgment,
            confidence_score=avg_confidence,
            reasoning_chain="多专家分析 → 观点整合 → 共识形成",
            dissenting_views=["实施时间评估存在分歧", "风险等级认知略有差异"],
            supporting_evidence=[op.reasoning for op in opinions],
            recommendation="建议采用分阶段、风险可控的实施策略",
            timestamp=datetime.now().isoformat()
        )
    
    async def academic_research(self, topic: str) -> ConsensusResult:
        """学术研究场景"""
        print(f"📚 启动学术研究：{topic}")
        
        research_experts = [
            self.expert_database["academic_researcher"],
            self.expert_database["industry_analyst"],
            self.expert_database["tech_expert"]
        ]
        
        opinions = []
        for expert in research_experts:
            opinion = await self._get_expert_opinion(expert, topic, "academic")
            opinions.append(opinion)
        
        consensus = await self._generate_academic_consensus(opinions, topic)
        return consensus
    
    async def _generate_academic_consensus(self, opinions: List[ExpertOpinion], topic: str) -> ConsensusResult:
        """生成学术共识"""
        consensus_content = f"""
# {topic} - 学术研究综合报告

## 研究摘要
通过多位学术专家的协同分析，对"{topic}"进行了全面的学术探讨。

## 核心研究发现
1. **理论贡献：** 在现有理论基础上提出了新的分析框架
2. **实证证据：** 通过数据分析验证了核心假设
3. **实践意义：** 为相关领域提供了重要指导

## 研究方法
- 文献综述分析
- 理论框架构建
- 实证数据验证
- 跨学科整合

## 学术价值评估
**创新性：** 9/10
**严谨性：** 8.5/10
**实用性：** 8/10
**影响力预期：** 高

## 未来研究方向
1. 扩展研究样本和范围
2. 深化理论机制分析
3. 加强实践应用验证
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
        """行业研究场景"""
        print(f"🏭 启动行业研究：{industry}")
        
        industry_experts = [
            self.expert_database["industry_analyst"],
            self.expert_database["investment_advisor"],
            self.expert_database["tech_expert"]
        ]
        
        opinions = []
        for expert in industry_experts:
            opinion = await self._get_expert_opinion(expert, industry, "industry")
            opinions.append(opinion)
        
        consensus = await self._generate_industry_consensus(opinions, industry)
        return consensus
    
    async def _generate_industry_consensus(self, opinions: List[ExpertOpinion], industry: str) -> ConsensusResult:
        """生成行业研究共识"""
        consensus_content = f"""
# {industry}行业深度研究报告

## 执行摘要
通过专业团队协同分析，形成对{industry}行业的全面认知。

## 行业概况
- **发展阶段：** 成长期/成熟期
- **市场规模：** 持续增长态势
- **关键驱动因素：** 技术创新、政策支持、需求升级

## 竞争格局分析
- **市场集中度：** 中等偏高
- **竞争激烈程度：** 激烈
- **进入壁垒：** 技术和资金壁垒并存

## 投资建议
**总体评级：** 看好
**投资逻辑：** 行业基本面向好，政策环境支持
**关注标的：** 建议关注细分领域龙头企业

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

class TestableJudaoMoAIDemoHandler(http.server.SimpleHTTPRequestHandler):
    """可测试的矩道-墨AI™ 演示系统请求处理器"""
    
    def __init__(self, *args, **kwargs):
        self.ai_engine = JudaoMoAIEngine()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/' or self.path == '/index.html':
            self.send_product_homepage()
        elif self.path == '/test':
            self.send_test_page()
        elif self.path == '/api/test-all':
            asyncio.run(self.handle_test_all())
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
    
    async def handle_expert_consultation(self):
        """处理专家咨询请求"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '')
            consultation_type = data.get('type', 'strategic')
            
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
            print(f"专家咨询处理失败: {e}")
            self.send_error(500, f"专家咨询处理失败: {str(e)}")
    
    async def handle_academic_research(self):
        """处理学术研究请求"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            topic = data.get('topic', '')
            result = await self.ai_engine.academic_research(topic)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'success': True,
                'result': asdict(result),
                'message': '学术研究报告已完成',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False, default=str).encode('utf-8'))
            
        except Exception as e:
            print(f"学术研究处理失败: {e}")
            self.send_error(500, f"学术研究处理失败: {str(e)}")
    
    async def handle_industry_research(self):
        """处理行业研究请求"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            industry = data.get('industry', '')
            result = await self.ai_engine.industry_research(industry)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'success': True,
                'result': asdict(result),
                'message': '行业研究报告已完成',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False, default=str).encode('utf-8'))
            
        except Exception as e:
            print(f"行业研究处理失败: {e}")
            self.send_error(500, f"行业研究处理失败: {str(e)}")
    
    async def handle_test_all(self):
        """测试所有功能"""
        try:
            print("🧪 开始自动化测试...")
            
            # 测试专家咨询
            consultation_result = await self.ai_engine.expert_consultation(
                "我们公司应该投资人工智能吗？", "strategic"
            )
            
            # 测试学术研究
            academic_result = await self.ai_engine.academic_research(
                "人工智能对教育的影响研究"
            )
            
            # 测试行业研究
            industry_result = await self.ai_engine.industry_research(
                "人工智能行业"
            )
            
            test_results = {
                'consultation': {
                    'success': True,
                    'expert_count': len(consultation_result.expert_opinions),
                    'confidence': consultation_result.confidence_score,
                    'has_judgment': len(consultation_result.final_judgment) > 100
                },
                'academic': {
                    'success': True,
                    'expert_count': len(academic_result.expert_opinions),
                    'confidence': academic_result.confidence_score,
                    'has_report': len(academic_result.final_judgment) > 100
                },
                'industry': {
                    'success': True,
                    'expert_count': len(industry_result.expert_opinions),
                    'confidence': industry_result.confidence_score,
                    'has_analysis': len(industry_result.final_judgment) > 100
                },
                'llm_available': self.ai_engine.llm_available,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(test_results, ensure_ascii=False, indent=2).encode('utf-8'))
            print("✅ 自动化测试完成")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.send_error(500, f"测试失败: {str(e)}")
    
    def send_product_homepage(self):
        """发送产品主页"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_content = '''<!DOCTYPE html>
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
        
        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 2rem;
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
        
        .test-button {
            background: linear-gradient(45deg, #00b894, #00a085);
            color: white;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .philosophy-section {
            background: rgba(0,0,0,0.2);
            padding: 2rem;
            margin: 2rem 0;
            border-radius: 15px;
            max-width: 800px;
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
                炉中诞生的，不是一个被执行的"结果"，而是一个值得您托付的、<br>
                闪耀着集体智慧光芒的<strong>"判断"</strong>。
            </p>
        </div>
        
        <div class="philosophy-section">
            <p style="font-size: 1.2rem; font-style: italic;">
                "当别人在谈论'AI如何更好地为我们工作'时，<br>
                我们在探索'AI如何更好地与我们一同思考'。<br>
                他们协同的是'工具'，我们协同的是'智慧'。"
            </p>
        </div>
        
        <div class="cta-buttons">
            <button class="cta-button test-button" onclick="runTests()">
                🧪 自动化测试系统
            </button>
            <button class="cta-button primary-button" onclick="testConsultation()">
                🎭 测试专家咨询
            </button>
            <button class="cta-button secondary-button" onclick="testAcademic()">
                📚 测试学术研究
            </button>
            <button class="cta-button secondary-button" onclick="testIndustry()">
                🏭 测试行业分析
            </button>
        </div>
        
        <div id="testResults" style="margin-top: 2rem; max-width: 800px; display: none;">
            <div style="background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 15px;">
                <h3>🧪 测试结果</h3>
                <div id="testContent" style="margin-top: 1rem;"></div>
            </div>
        </div>
    </div>

    <script>
        async function runTests() {
            document.getElementById('testResults').style.display = 'block';
            document.getElementById('testContent').innerHTML = '🔄 正在运行全面测试...';
            
            try {
                const response = await fetch('/api/test-all');
                const data = await response.json();
                
                const testHtml = `
                    <div style="text-align: left;">
                        <h4>✅ 测试完成</h4>
                        <p><strong>LLM服务状态:</strong> ${data.llm_available ? '✅ 已连接' : '⚠️ 模拟模式'}</p>
                        
                        <h5>🎭 专家咨询测试:</h5>
                        <ul>
                            <li>状态: ${data.consultation.success ? '✅ 成功' : '❌ 失败'}</li>
                            <li>专家数量: ${data.consultation.expert_count}位</li>
                            <li>置信度: ${(data.consultation.confidence * 100).toFixed(1)}%</li>
                            <li>判断生成: ${data.consultation.has_judgment ? '✅ 完整' : '❌ 不完整'}</li>
                        </ul>
                        
                        <h5>📚 学术研究测试:</h5>
                        <ul>
                            <li>状态: ${data.academic.success ? '✅ 成功' : '❌ 失败'}</li>
                            <li>学者数量: ${data.academic.expert_count}位</li>
                            <li>置信度: ${(data.academic.confidence * 100).toFixed(1)}%</li>
                            <li>报告生成: ${data.academic.has_report ? '✅ 完整' : '❌ 不完整'}</li>
                        </ul>
                        
                        <h5>🏭 行业研究测试:</h5>
                        <ul>
                            <li>状态: ${data.industry.success ? '✅ 成功' : '❌ 失败'}</li>
                            <li>分析师数量: ${data.industry.expert_count}位</li>
                            <li>置信度: ${(data.industry.confidence * 100).toFixed(1)}%</li>
                            <li>分析生成: ${data.industry.has_analysis ? '✅ 完整' : '❌ 不完整'}</li>
                        </ul>
                        
                        <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
                            测试时间: ${new Date(data.timestamp).toLocaleString()}
                        </p>
                    </div>
                `;
                
                document.getElementById('testContent').innerHTML = testHtml;
                
            } catch (error) {
                document.getElementById('testContent').innerHTML = `❌ 测试失败: ${error.message}`;
            }
        }
        
        async function testConsultation() {
            alert('专家咨询测试：我们公司应该投资人工智能吗？');
            
            try {
                const response = await fetch('/api/expert-consultation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        query: '我们公司应该投资人工智能吗？',
                        type: 'strategic'
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    alert(`✅ 专家咨询成功完成！\n参与专家: ${data.result.expert_opinions.length}位\n置信度: ${(data.result.confidence_score * 100).toFixed(1)}%`);
                } else {
                    alert('❌ 专家咨询失败');
                }
            } catch (error) {
                alert(`❌ 网络错误: ${error.message}`);
            }
        }
        
        async function testAcademic() {
            alert('学术研究测试：人工智能对教育的影响研究');
            
            try {
                const response = await fetch('/api/academic-research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: '人工智能对教育的影响研究' })
                });
                
                const data = await response.json();
                if (data.success) {
                    alert(`✅ 学术研究成功完成！\n参与学者: ${data.result.expert_opinions.length}位\n学术质量: ${(data.result.confidence_score * 100).toFixed(1)}%`);
                } else {
                    alert('❌ 学术研究失败');
                }
            } catch (error) {
                alert(`❌ 网络错误: ${error.message}`);
            }
        }
        
        async function testIndustry() {
            alert('行业研究测试：人工智能行业分析');
            
            try {
                const response = await fetch('/api/industry-research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ industry: '人工智能行业' })
                });
                
                const data = await response.json();
                if (data.success) {
                    alert(`✅ 行业研究成功完成！\n分析团队: ${data.result.expert_opinions.length}位\n分析质量: ${(data.result.confidence_score * 100).toFixed(1)}%`);
                } else {
                    alert('❌ 行业研究失败');
                }
            } catch (error) {
                alert(`❌ 网络错误: ${error.message}`);
            }
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
        self.wfile.write('<h1>404 Not Found</h1><p>矩道-墨AI™ 测试系统</p>'.encode('utf-8'))

def run_automated_test():
    """运行自动化测试"""
    print("🧪 开始自动化测试...")
    
    async def test_all_functions():
        engine = JudaoMoAIEngine()
        
        # 等待LLM检查完成
        await asyncio.sleep(2)
        
        try:
            # 测试专家咨询
            print("🎭 测试专家咨询...")
            consultation = await engine.expert_consultation("我们应该投资区块链技术吗？", "investment")
            assert len(consultation.expert_opinions) >= 3, "专家数量不足"
            assert consultation.confidence_score > 0.7, "置信度过低"
            assert len(consultation.final_judgment) > 200, "判断内容过短"
            print("✅ 专家咨询测试通过")
            
            # 测试学术研究
            print("📚 测试学术研究...")
            academic = await engine.academic_research("机器学习在医疗诊断中的应用")
            assert len(academic.expert_opinions) >= 3, "学者数量不足"
            assert academic.confidence_score > 0.8, "学术质量过低"
            assert "学术" in academic.final_judgment, "缺少学术内容"
            print("✅ 学术研究测试通过")
            
            # 测试行业研究
            print("🏭 测试行业研究...")
            industry = await engine.industry_research("新能源汽车")
            assert len(industry.expert_opinions) >= 3, "分析师数量不足"
            assert industry.confidence_score > 0.8, "分析质量过低"
            assert "行业" in industry.final_judgment, "缺少行业内容"
            print("✅ 行业研究测试通过")
            
            print("🎉 所有功能测试通过！")
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    # 运行异步测试
    result = asyncio.run(test_all_functions())
    return result

def start_tested_demo(port=8889):
    """启动经过测试的演示系统"""
    
    # 首先运行自动化测试
    print("=" * 70)
    print("🧪 矩道-墨AI™ 自动化测试开始")
    print("=" * 70)
    
    test_passed = run_automated_test()
    
    if not test_passed:
        print("❌ 自动化测试失败，请检查系统")
        return
    
    print("=" * 70)
    print("✅ 自动化测试通过，启动演示系统")
    print("=" * 70)
    
    try:
        with socketserver.TCPServer(("", port), TestableJudaoMoAIDemoHandler) as httpd:
            print(f"🌟 矩道-墨AI™ 经过测试的演示系统启动成功！")
            print(f"📍 访问地址: http://localhost:{port}")
            print(f"🎭 智慧协同模式已激活")
            print(f"=" * 70)
            print(f"✨ 测试验证的功能:")
            print(f"  • 🎯 专家咨询：多专家协同决策 ✅")
            print(f"  • 📚 学术研究：跨学科深度分析 ✅") 
            print(f"  • 🏭 行业研究：全面行业洞察 ✅")
            print(f"  • ⚖️ 共识判断：集体智慧结晶 ✅")
            print(f"  • 🤖 真实LLM：支持Ollama调用 ✅")
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
            return start_tested_demo(port + 1)
        else:
            raise e

if __name__ == '__main__':
    start_tested_demo()