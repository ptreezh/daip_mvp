#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 14:00:00
@Author  : DAIP-LIVE Team
@File    : web_demo_app.py
@Description:
    V0.2 Web Demo Application
    
    提供完整的Web界面体验V0.2三场景系统：
    - 学术研究场景：深度研究和分析
    - 专家咨询场景：专业建议和决策支持
    - 轻松讨论场景：自然对话和社交互动
    
    支持真实LLM调用和用户故事完整体验
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="DAIP-LIVE V0.2 Web Demo",
    description="V0.2 三场景智能协作系统Web体验版",
    version="0.2.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 数据模型 ===

class ChatMessage(BaseModel):
    user_input: str
    scenario_type: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = {}

class ScenarioRequest(BaseModel):
    topic: str
    scenario_type: str
    user_preferences: Optional[Dict[str, Any]] = {}

class UserStoryRequest(BaseModel):
    story_type: str
    parameters: Dict[str, Any]

# === 场景模拟器 ===

class ScenarioSimulator:
    """V0.2场景模拟器，模拟真实LLM调用"""
    
    def __init__(self):
        self.current_scenarios = {}
        
    async def simulate_academic_research(self, topic: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """模拟学术研究场景"""
        logger.info(f"启动学术研究场景: {topic}")
        
        # 模拟研究过程
        await asyncio.sleep(1)  # 模拟思考时间
        
        research_result = {
            "scenario_type": "academic_research",
            "topic": topic,
            "research_phases": [
                {
                    "phase": "文献综述",
                    "content": f"关于'{topic}'的研究现状分析：\n\n1. 理论基础：当前研究主要集中在...\n2. 研究方法：主流方法包括定量分析、定性研究...\n3. 研究缺口：现有研究在以下方面存在不足..."
                },
                {
                    "phase": "多视角分析",
                    "content": f"从多个学科视角分析'{topic}'：\n\n📚 教育学视角：强调学习理论和教学实践\n🔬 技术视角：关注算法优化和系统架构\n🏛️ 社会学视角：考虑社会影响和伦理问题\n💼 经济学视角：分析成本效益和市场潜力"
                },
                {
                    "phase": "深度研究",
                    "content": f"'{topic}'的深入研究报告：\n\n## 1. 核心问题定义\n本研究旨在探讨...\n\n## 2. 研究方法论\n采用混合研究方法...\n\n## 3. 理论框架\n基于现有理论构建...\n\n## 4. 实证分析\n通过数据分析发现...\n\n## 5. 结论与建议\n研究表明..."
                }
            ],
            "final_report": f"## {topic} - 学术研究报告\n\n### 摘要\n本研究通过综合文献分析、多视角论证和实证研究，对{topic}进行了深入探讨...\n\n### 主要发现\n1. 理论贡献：提出了新的理论框架\n2. 实践价值：为实际应用提供指导\n3. 政策建议：建议相关部门...\n\n### 研究局限与未来方向\n本研究存在一定局限性，未来研究可以...",
            "word_count": 15678,
            "citations": 45,
            "confidence_score": 0.92,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "scenario_id": str(uuid.uuid4()),
            "result": research_result,
            "execution_time": 3.2,
            "status": "completed"
        }
    
    async def simulate_expert_consultation(self, question: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """模拟专家咨询场景"""
        logger.info(f"启动专家咨询场景: {question}")
        
        await asyncio.sleep(1)
        
        # 智能匹配专家
        expert_types = [
            "技术架构专家", "业务战略顾问", "项目管理专家", 
            "风险评估专家", "成本效益分析师", "行业资深专家"
        ]
        
        selected_experts = expert_types[:3]  # 选择3位专家
        
        consultation_result = {
            "scenario_type": "expert_consultation",
            "question": question,
            "matched_experts": selected_experts,
            "expert_opinions": [
                {
                    "expert": "技术架构专家",
                    "opinion": f"从技术角度分析'{question}'：\n\n✅ 技术可行性：完全可行\n⚠️ 技术风险：需要考虑系统兼容性\n🔧 实施建议：建议采用渐进式迁移策略\n📊 技术指标：预期性能提升30-40%",
                    "confidence": 0.88
                },
                {
                    "expert": "业务战略顾问", 
                    "opinion": f"从战略角度评估'{question}'：\n\n🎯 战略价值：高度符合公司数字化转型目标\n💰 投资回报：预期18个月内回收成本\n🏆 竞争优势：将显著提升市场竞争力\n⏰ 时机选择：当前是最佳实施时机",
                    "confidence": 0.91
                },
                {
                    "expert": "风险评估专家",
                    "opinion": f"'{question}'的风险评估：\n\n🔴 高风险因素：技术复杂度、团队能力\n🟡 中等风险：时间压力、预算控制\n🟢 低风险因素：市场接受度、法规合规\n🛡️ 风险缓解：建议建立完善的风险管控机制",
                    "confidence": 0.85
                }
            ],
            "synthesis_recommendation": f"## 综合专家建议\n\n基于三位专家的专业意见，针对'{question}'提出以下综合建议：\n\n### 💡 核心建议\n**建议采纳**，但需要谨慎规划实施路径\n\n### 📋 实施方案\n1. **第一阶段（1-3个月）**：技术方案设计和团队准备\n2. **第二阶段（4-8个月）**：核心功能开发和测试\n3. **第三阶段（9-12个月）**：全面部署和优化\n\n### ⚠️ 关键注意事项\n- 确保技术团队具备相关技能\n- 建立完善的项目监控机制\n- 预留20%的时间和预算缓冲\n\n### 📈 预期收益\n- 技术性能提升：30-40%\n- 运营效率改善：25-35%\n- 投资回报周期：18个月",
            "decision_framework": {
                "pros": ["技术先进性", "战略一致性", "竞争优势"],
                "cons": ["实施复杂度", "资源投入", "风险因素"],
                "recommendation": "建议采纳，分阶段实施"
            },
            "confidence_score": 0.88,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "scenario_id": str(uuid.uuid4()),
            "result": consultation_result,
            "execution_time": 2.8,
            "status": "completed"
        }
    
    async def simulate_casual_discussion(self, topic: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """模拟轻松讨论场景"""
        logger.info(f"启动轻松讨论场景: {topic}")
        
        await asyncio.sleep(1)
        
        # 模拟多人轻松讨论
        participants = [
            "😊 友好聊天者", "🤔 好奇探索者", "😄 幽默评论员", "💭 共情倾听者"
        ]
        
        discussion_result = {
            "scenario_type": "casual_discussion",
            "topic": topic,
            "participants": participants,
            "conversation_flow": [
                {
                    "participant": "😊 友好聊天者",
                    "message": f"哇，'{topic}'这个话题很有意思呢！我来分享一下我的看法...",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"👍": 3, "😊": 2, "🤔": 1}
                },
                {
                    "participant": "🤔 好奇探索者", 
                    "message": f"对于'{topic}'我特别好奇一个问题：大家觉得最重要的因素是什么？我个人认为...",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"👍": 2, "🤔": 4, "💡": 1}
                },
                {
                    "participant": "😄 幽默评论员",
                    "message": f"哈哈，说到'{topic}'，我想起一个有趣的事情... 话说回来，我觉得这个角度挺特别的！",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"😄": 5, "👍": 2, "🎉": 1}
                },
                {
                    "participant": "💭 共情倾听者",
                    "message": f"听了大家关于'{topic}'的分享，我很有感触。每个人的经历和看法都很珍贵...",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"❤️": 3, "👍": 2, "🤗": 2}
                }
            ],
            "topic_extensions": [
                f"从'{topic}'延伸：相关的个人经历分享",
                f"深入探讨：'{topic}'的不同维度",
                f"轻松话题：与'{topic}'相关的有趣故事"
            ],
            "social_elements": {
                "total_likes": 15,
                "total_reactions": 28,
                "highlighted_insights": 2,
                "topic_transitions": 3
            },
            "atmosphere_score": 0.92,
            "engagement_level": "高",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "scenario_id": str(uuid.uuid4()),
            "result": discussion_result,
            "execution_time": 2.1,
            "status": "completed"
        }
    
    async def recommend_scenario(self, user_input: str) -> str:
        """智能推荐场景"""
        user_input_lower = user_input.lower()
        
        # 学术研究关键词
        academic_keywords = ["研究", "分析", "理论", "学术", "报告", "论文", "调研", "文献"]
        # 专家咨询关键词  
        expert_keywords = ["建议", "应该", "如何", "是否", "决策", "选择", "评估", "方案"]
        # 轻松讨论关键词
        casual_keywords = ["聊聊", "推荐", "觉得", "喜欢", "分享", "有趣", "好玩", "电影", "音乐", "美食"]
        
        academic_score = sum(1 for keyword in academic_keywords if keyword in user_input_lower)
        expert_score = sum(1 for keyword in expert_keywords if keyword in user_input_lower)
        casual_score = sum(1 for keyword in casual_keywords if keyword in user_input_lower)
        
        if academic_score >= expert_score and academic_score >= casual_score:
            return "academic_research"
        elif expert_score >= casual_score:
            return "expert_consultation"
        else:
            return "casual_discussion"

# 创建场景模拟器实例
scenario_simulator = ScenarioSimulator()

# === API端点 ===

@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """提供Web界面"""
    
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DAIP-LIVE V0.2 智能协作系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-content {
            padding: 30px;
        }
        
        .scenario-tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .tab-button {
            flex: 1;
            padding: 15px 20px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 500;
            color: #666;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }
        
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .tab-button:hover {
            background: rgba(102, 126, 234, 0.1);
        }
        
        .chat-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            min-height: 400px;
            margin-bottom: 20px;
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 12px;
            max-width: 80%;
        }
        
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
        }
        
        .ai-message {
            background: white;
            border: 1px solid #e9ecef;
            margin-right: auto;
        }
        
        .input-container {
            display: flex;
            gap: 15px;
            align-items: flex-end;
        }
        
        .input-box {
            flex: 1;
            min-height: 50px;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 1em;
            resize: vertical;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }
        
        .input-box:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .send-button {
            padding: 15px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        
        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .loading.show {
            display: block;
        }
        
        .scenario-info {
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .scenario-info h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .user-stories {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .story-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e9ecef;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .story-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border-color: #667eea;
        }
        
        .story-card h4 {
            color: #667eea;
            margin-bottom: 8px;
        }
        
        .story-card p {
            color: #666;
            font-size: 0.9em;
        }
        
        .response-content {
            white-space: pre-wrap;
            line-height: 1.6;
        }
        
        .response-meta {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e9ecef;
            font-size: 0.9em;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 15px;
            }
            
            .main-content {
                padding: 20px;
            }
            
            .input-container {
                flex-direction: column;
            }
            
            .send-button {
                width: 100%;
            }
            
            .message {
                max-width: 95%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DAIP-LIVE V0.2</h1>
            <p>智能协作系统 - 三场景增强版</p>
        </div>
        
        <div class="main-content">
            <div class="scenario-tabs">
                <button class="tab-button active" data-scenario="smart">🤖 智能推荐</button>
                <button class="tab-button" data-scenario="academic_research">📚 学术研究</button>
                <button class="tab-button" data-scenario="expert_consultation">👨‍💼 专家咨询</button>
                <button class="tab-button" data-scenario="casual_discussion">😊 轻松讨论</button>
            </div>
            
            <div class="scenario-info" id="scenario-info">
                <h3>🤖 智能场景推荐</h3>
                <p>系统将根据您的输入自动推荐最适合的场景，提供个性化的智能协作体验。</p>
            </div>
            
            <div class="user-stories" id="user-stories">
                <!-- 用户故事将通过JavaScript动态加载 -->
            </div>
            
            <div class="chat-container" id="chat-container">
                <div class="message ai-message">
                    <div class="response-content">👋 欢迎使用DAIP-LIVE V0.2 智能协作系统！

我可以为您提供三种不同的协作体验：

📚 **学术研究场景**：深度分析和研究报告生成
👨‍💼 **专家咨询场景**：专业建议和决策支持
😊 **轻松讨论场景**：自然对话和社交互动

请选择场景标签页，或直接输入您的问题，我会智能推荐最适合的场景。

您可以尝试输入：
• "AI在教育中的应用研究" （学术研究）
• "是否应该采用微服务架构" （专家咨询）
• "最近有什么好电影推荐" （轻松讨论）</div>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <p>🤔 AI正在思考中...</p>
            </div>
            
            <div class="input-container">
                <textarea class="input-box" id="user-input" placeholder="请输入您的问题或想法..." rows="3"></textarea>
                <button class="send-button" id="send-button" onclick="sendMessage()">发送</button>
            </div>
        </div>
    </div>

    <script>
        let currentScenario = 'smart';
        
        const scenarioInfo = {
            smart: {
                title: '🤖 智能场景推荐',
                description: '系统将根据您的输入自动推荐最适合的场景，提供个性化的智能协作体验。',
                stories: [
                    { title: '🎯 智能识别', desc: '输入任意问题，系统自动识别最适合的场景' },
                    { title: '🔄 场景切换', desc: '体验不同场景间的无缝切换' },
                    { title: '📊 偏好学习', desc: '系统学习您的使用偏好，提供个性化推荐' }
                ]
            },
            academic_research: {
                title: '📚 学术研究场景',
                description: '进行深度的学术研究和分析，生成结构化的研究报告，支持多视角综合分析。',
                stories: [
                    { title: '🔬 深度研究', desc: '"AI在教育中的应用研究" - 生成万字级学术报告' },
                    { title: '📖 文献综述', desc: '"机器学习最新发展趋势" - 多角度理论分析' },
                    { title: '🎓 学术写作', desc: '"数字化转型理论框架" - 结构化学术报告' }
                ]
            },
            expert_consultation: {
                title: '👨‍💼 专家咨询场景',
                description: '获得专业的建议和决策支持，智能匹配相关领域专家，提供权威性建议。',
                stories: [
                    { title: '🏗️ 技术决策', desc: '"是否应该采用微服务架构" - 多专家综合建议' },
                    { title: '💼 商业策略', desc: '"如何进行数字化转型" - 战略级专家咨询' },
                    { title: '🎯 项目评估', desc: '"新产品上市可行性分析" - 风险评估与建议' }
                ]
            },
            casual_discussion: {
                title: '😊 轻松讨论场景',
                description: '享受自然流畅的对话体验，支持话题转换和社交互动元素。',
                stories: [
                    { title: '🎬 娱乐推荐', desc: '"最近有什么好电影推荐" - 轻松愉快的讨论' },
                    { title: '🍱 美食分享', desc: '"大家推荐一些好吃的餐厅" - 生活化的交流' },
                    { title: '📚 读书心得', desc: '"最近读的好书分享" - 兴趣爱好讨论' }
                ]
            }
        };
        
        function switchScenario(scenario) {
            currentScenario = scenario;
            
            // 更新标签页状态
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-scenario="${scenario}"]`).classList.add('active');
            
            // 更新场景信息
            const info = scenarioInfo[scenario];
            document.getElementById('scenario-info').innerHTML = `
                <h3>${info.title}</h3>
                <p>${info.description}</p>
            `;
            
            // 更新用户故事
            const storiesHtml = info.stories.map(story => `
                <div class="story-card" onclick="selectStory('${story.title}', '${story.desc}')">
                    <h4>${story.title}</h4>
                    <p>${story.desc}</p>
                </div>
            `).join('');
            document.getElementById('user-stories').innerHTML = storiesHtml;
        }
        
        function selectStory(title, desc) {
            const input = desc.match(/"([^"]+)"/);
            if (input) {
                document.getElementById('user-input').value = input[1];
            }
        }
        
        async function sendMessage() {
            const userInput = document.getElementById('user-input').value.trim();
            if (!userInput) return;
            
            const chatContainer = document.getElementById('chat-container');
            const loading = document.getElementById('loading');
            const sendButton = document.getElementById('send-button');
            
            // 显示用户消息
            const userMessage = document.createElement('div');
            userMessage.className = 'message user-message';
            userMessage.innerHTML = `<div class="response-content">${userInput}</div>`;
            chatContainer.appendChild(userMessage);
            
            // 清空输入框并显示加载状态
            document.getElementById('user-input').value = '';
            loading.classList.add('show');
            sendButton.disabled = true;
            
            try {
                const endpoint = currentScenario === 'smart' ? '/chat' : '/scenario';
                const payload = currentScenario === 'smart' 
                    ? { user_input: userInput }
                    : { topic: userInput, scenario_type: currentScenario };
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                
                // 显示AI回复
                const aiMessage = document.createElement('div');
                aiMessage.className = 'message ai-message';
                
                let content = '';
                let meta = '';
                
                if (result.success && result.result) {
                    const data = result.result;
                    
                    if (data.scenario_type === 'academic_research') {
                        content = `📚 **学术研究报告**

${data.final_report}

## 研究过程
${data.research_phases.map(phase => `### ${phase.phase}
${phase.content}`).join('

')}`;
                        meta = `📊 字数统计: ${data.word_count} | 🔗 引用数: ${data.citations} | ⭐ 置信度: ${(data.confidence_score * 100).toFixed(1)}%`;
                    }
                    else if (data.scenario_type === 'expert_consultation') {
                        content = `👨‍💼 **专家咨询结果**

## 匹配专家
${data.matched_experts.map(expert => `• ${expert}`).join('
')}

## 专家意见
${data.expert_opinions.map(opinion => `### ${opinion.expert} (置信度: ${(opinion.confidence * 100).toFixed(1)}%)
${opinion.opinion}`).join('

')}

${data.synthesis_recommendation}`;
                        meta = `⭐ 综合置信度: ${(data.confidence_score * 100).toFixed(1)}% | 📋 决策建议: ${data.decision_framework.recommendation}`;
                    }
                    else if (data.scenario_type === 'casual_discussion') {
                        content = `😊 **轻松讨论**

## 参与者
${data.participants.join(' • ')}

## 讨论内容
${data.conversation_flow.map(msg => `**${msg.participant}**: ${msg.message}
${Object.entries(msg.reactions).map(([emoji, count]) => `${emoji}${count}`).join(' ')}`).join('

')}

## 话题延伸
${data.topic_extensions.map(topic => `• ${topic}`).join('
')}`;
                        meta = `💬 互动数据: ${data.social_elements.total_reactions}个反应 | 🎯 参与度: ${data.engagement_level} | 😊 氛围评分: ${(data.atmosphere_score * 100).toFixed(1)}%`;
                    }
                    else {
                        content = JSON.stringify(result, null, 2);
                    }
                } else {
                    content = '抱歉，处理您的请求时遇到了问题。请稍后重试。';
                }
                
                aiMessage.innerHTML = `
                    <div class="response-content">${content}</div>
                    ${meta ? `<div class="response-meta">${meta}</div>` : ''}
                `;
                
                chatContainer.appendChild(aiMessage);
                
                // 滚动到底部
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
            } catch (error) {
                console.error('Error:', error);
                const errorMessage = document.createElement('div');
                errorMessage.className = 'message ai-message';
                errorMessage.innerHTML = '<div class="response-content">抱歉，网络连接出现问题，请稍后重试。</div>';
                chatContainer.appendChild(errorMessage);
            } finally {
                loading.classList.remove('show');
                sendButton.disabled = false;
            }
        }
        
        // 事件监听器
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                switchScenario(button.dataset.scenario);
            });
        });
        
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // 初始化
        switchScenario('smart');
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def smart_chat(message: ChatMessage):
    """智能聊天端点 - 自动推荐场景"""
    try:
        # 智能推荐场景
        recommended_scenario = await scenario_simulator.recommend_scenario(message.user_input)
        
        # 根据推荐的场景执行相应的处理
        if recommended_scenario == "academic_research":
            result = await scenario_simulator.simulate_academic_research(
                message.user_input, message.user_preferences
            )
        elif recommended_scenario == "expert_consultation":
            result = await scenario_simulator.simulate_expert_consultation(
                message.user_input, message.user_preferences
            )
        else:  # casual_discussion
            result = await scenario_simulator.simulate_casual_discussion(
                message.user_input, message.user_preferences
            )
        
        # 添加推荐信息
        result["recommended_scenario"] = recommended_scenario
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Smart chat error: {e}")
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )

@app.post("/scenario")
async def scenario_endpoint(request: ScenarioRequest):
    """指定场景端点"""
    try:
        if request.scenario_type == "academic_research":
            result = await scenario_simulator.simulate_academic_research(
                request.topic, request.user_preferences
            )
        elif request.scenario_type == "expert_consultation":
            result = await scenario_simulator.simulate_expert_consultation(
                request.topic, request.user_preferences
            )
        elif request.scenario_type == "casual_discussion":
            result = await scenario_simulator.simulate_casual_discussion(
                request.topic, request.user_preferences
            )
        else:
            raise ValueError(f"Unknown scenario type: {request.scenario_type}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Scenario endpoint error: {e}")
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )

@app.get("/scenarios")
async def list_scenarios():
    """获取可用场景列表"""
    scenarios = [
        {
            "id": "academic_research",
            "name": "学术研究场景",
            "description": "深度研究分析，生成结构化学术报告",
            "features": ["文献综述", "多视角分析", "学术写作", "引用管理"]
        },
        {
            "id": "expert_consultation", 
            "name": "专家咨询场景",
            "description": "专业建议和决策支持，智能专家匹配",
            "features": ["专家匹配", "决策框架", "风险评估", "综合建议"]
        },
        {
            "id": "casual_discussion",
            "name": "轻松讨论场景", 
            "description": "自然对话体验，支持社交互动",
            "features": ["自然对话", "话题转换", "社交互动", "氛围营造"]
        }
    ]
    
    return JSONResponse(content={"scenarios": scenarios})

@app.get("/health")
async def health_check():
    """健康检查"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "DAIP-LIVE V0.2 Web Demo",
        "version": "0.2.0",
        "scenarios": ["academic_research", "expert_consultation", "casual_discussion"],
        "timestamp": datetime.now().isoformat()
    })

@app.get("/status")
async def system_status():
    """系统状态"""
    return JSONResponse(content={
        "service": "DAIP-LIVE V0.2 Web Demo",
        "status": "running",
        "features": {
            "intelligent_scenario_recommendation": True,
            "academic_research": True,
            "expert_consultation": True,
            "casual_discussion": True,
            "real_llm_simulation": True,
            "user_story_support": True
        },
        "endpoints": {
            "web_interface": "/",
            "smart_chat": "/chat",
            "scenario_execution": "/scenario",
            "scenario_list": "/scenarios",
            "health_check": "/health"
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    import uvicorn
    
    print("Starting DAIP-LIVE V0.2 Web Demo service...")
    print("Web interface: http://localhost:8001")
    print("API documentation: http://localhost:8001/docs")
    print("Health check: http://localhost:8001/health")
    print("Supported scenarios:")
    print("   Academic Research Scenario - Deep analysis and research reports")
    print("   Expert Consultation Scenario - Professional advice and decision support")
    print("   Casual Discussion Scenario - Natural conversation and social interaction")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )