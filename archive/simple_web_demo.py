#!/usr/bin/env python3
"""Simple Web Demo App - No Unicode characters
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="DAIP-LIVE Web Demo",
    description="Web Demo Application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ChatMessage(BaseModel):
    user_input: str
    scenario_type: Optional[str] = None
    user_preferences: Optional[dict[str, Any]] = {}

class ScenarioRequest(BaseModel):
    topic: str
    scenario_type: str
    user_preferences: Optional[dict[str, Any]] = {}

# Scenario simulator
class ScenarioSimulator:
    def __init__(self):
        self.current_scenarios = {}
        
    async def simulate_academic_research(self, topic: str, preferences: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"Starting academic research scenario: {topic}")
        
        await asyncio.sleep(1)
        
        research_result = {
            "scenario_type": "academic_research",
            "topic": topic,
            "research_phases": [
                {
                    "phase": "Literature Review",
                    "content": f"Research status analysis on '{topic}':\n\n1. Theoretical foundations: Current research focuses on...\n2. Research methods: Main methods include quantitative analysis, qualitative research...\n3. Research gaps: Existing research has shortcomings in..."
                },
                {
                    "phase": "Multi-perspective Analysis",
                    "content": f"Analyzing '{topic}' from multiple disciplinary perspectives:\n\nEducation perspective: Emphasizing learning theory and teaching practice\nTechnology perspective: Focusing on algorithm optimization and system architecture\nSociology perspective: Considering social impact and ethical issues\nEconomics perspective: Analyzing cost-effectiveness and market potential"
                },
                {
                    "phase": "In-depth Research",
                    "content": f"In-depth research report on '{topic}':\n\n## 1. Core Problem Definition\nThis research aims to explore...\n\n## 2. Research Methodology\nAdopting mixed research methods...\n\n## 3. Theoretical Framework\nBuilt based on existing theories...\n\n## 4. Empirical Analysis\nDiscovered through data analysis...\n\n## 5. Conclusions and Recommendations\nResearch shows..."
                }
            ],
            "final_report": f"## {topic} - Academic Research Report\n\n### Abstract\nThis research provides an in-depth exploration of {topic} through comprehensive literature analysis, multi-perspective argumentation, and empirical research...\n\n### Main Findings\n1. Theoretical contribution: Proposed new theoretical framework\n2. Practical value: Provides guidance for practical applications\n3. Policy recommendations: Recommend relevant departments...\n\n### Research Limitations and Future Directions\nThis research has certain limitations, future research can...",
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
    
    async def simulate_expert_consultation(self, question: str, preferences: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"Starting expert consultation scenario: {question}")
        
        await asyncio.sleep(1)
        
        expert_types = [
            "Technical Architecture Expert", "Business Strategy Consultant", "Project Management Expert", 
            "Risk Assessment Expert", "Cost-Benefit Analyst", "Industry Senior Expert"
        ]
        
        selected_experts = expert_types[:3]
        
        consultation_result = {
            "scenario_type": "expert_consultation",
            "question": question,
            "matched_experts": selected_experts,
            "expert_opinions": [
                {
                    "expert": "Technical Architecture Expert",
                    "opinion": f"Technical analysis of '{question}':\n\nFeasibility: Fully feasible\nTechnical risks: Need to consider system compatibility\nImplementation suggestions: Recommend gradual migration strategy\nTechnical indicators: Expected performance improvement 30-40%",
                    "confidence": 0.88
                },
                {
                    "expert": "Business Strategy Consultant", 
                    "opinion": f"Strategic evaluation of '{question}':\n\nStrategic value: Highly aligned with company digital transformation goals\nROI: Expected cost recovery within 18 months\nCompetitive advantage: Will significantly enhance market competitiveness\nTiming: Current is the best implementation time",
                    "confidence": 0.91
                },
                {
                    "expert": "Risk Assessment Expert",
                    "opinion": f"Risk assessment of '{question}':\n\nHigh risk factors: Technical complexity, team capability\nMedium risk: Time pressure, budget control\nLow risk factors: Market acceptance, regulatory compliance\nRisk mitigation: Recommend establishing comprehensive risk control mechanisms",
                    "confidence": 0.85
                }
            ],
            "synthesis_recommendation": f"## Comprehensive Expert Recommendations\n\nBased on professional opinions from three experts, the following comprehensive recommendations are proposed for '{question}':\n\n### Core Recommendations\n**Recommended for adoption**, but needs careful implementation planning\n\n### Implementation Plan\n1. **Phase 1 (1-3 months)**: Technical solution design and team preparation\n2. **Phase 2 (4-8 months)**: Core function development and testing\n3. **Phase 3 (9-12 months)**: Full deployment and optimization\n\n### Key Considerations\n- Ensure technical team has relevant skills\n- Establish comprehensive project monitoring mechanisms\n- Reserve 20% time and budget buffer\n\n### Expected Benefits\n- Technical performance improvement: 30-40%\n- Operational efficiency improvement: 25-35%\n- ROI period: 18 months",
            "decision_framework": {
                "pros": ["Technical advancement", "Strategic alignment", "Competitive advantage"],
                "cons": ["Implementation complexity", "Resource investment", "Risk factors"],
                "recommendation": "Recommended for adoption, phased implementation"
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
    
    async def simulate_casual_discussion(self, topic: str, preferences: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"Starting casual discussion scenario: {topic}")
        
        await asyncio.sleep(1)
        
        participants = [
            "Friendly Chat", "Curious Explorer", "Humorous Commentator", "Empathetic Listener"
        ]
        
        discussion_result = {
            "scenario_type": "casual_discussion",
            "topic": topic,
            "participants": participants,
            "conversation_flow": [
                {
                    "participant": "Friendly Chat",
                    "message": f"Wow, '{topic}' is a really interesting topic! Let me share my thoughts...",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"like": 3, "smile": 2, "thinking": 1}
                },
                {
                    "participant": "Curious Explorer", 
                    "message": f"For '{topic}' I'm particularly curious about one question: what do you think is the most important factor? Personally I think...",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"like": 2, "thinking": 4, "idea": 1}
                },
                {
                    "participant": "Humorous Commentator",
                    "message": f"Haha, speaking of '{topic}', I remember something interesting... By the way, I think this angle is quite special!",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"laugh": 5, "like": 2, "celebration": 1}
                },
                {
                    "participant": "Empathetic Listener",
                    "message": f"After listening to everyone's sharing about '{topic}', I'm very touched. Everyone's experiences and perspectives are precious...",
                    "timestamp": datetime.now().isoformat(),
                    "reactions": {"heart": 3, "like": 2, "hug": 2}
                }
            ],
            "topic_extensions": [
                f"From '{topic}' extension: Related personal experience sharing",
                f"In-depth discussion: Different dimensions of '{topic}'",
                f"Light topics: Interesting stories related to '{topic}'"
            ],
            "social_elements": {
                "total_likes": 15,
                "total_reactions": 28,
                "highlighted_insights": 2,
                "topic_transitions": 3
            },
            "atmosphere_score": 0.92,
            "engagement_level": "High",
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
        user_input_lower = user_input.lower()
        
        academic_keywords = ["research", "analysis", "theory", "academic", "report", "paper", "investigation", "literature"]
        expert_keywords = ["advice", "should", "how", "whether", "decision", "choice", "evaluation", "plan"]
        casual_keywords = ["chat", "recommend", "think", "like", "share", "interesting", "fun", "movie", "music", "food"]
        
        academic_score = sum(1 for keyword in academic_keywords if keyword in user_input_lower)
        expert_score = sum(1 for keyword in expert_keywords if keyword in user_input_lower)
        casual_score = sum(1 for keyword in casual_keywords if keyword in user_input_lower)
        
        if academic_score >= expert_score and academic_score >= casual_score:
            return "academic_research"
        elif expert_score >= casual_score:
            return "expert_consultation"
        else:
            return "casual_discussion"

# Create scenario simulator instance
scenario_simulator = ScenarioSimulator()

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DAIP-LIVE Web Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
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
        .chat-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            min-height: 400px;
            margin-bottom: 20px;
            overflow-y: auto;
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
        }
        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
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
        .response-content {
            white-space: pre-wrap;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DAIP-LIVE Web Demo</h1>
            <p>Intelligent Collaboration System</p>
        </div>
        
        <div class="main-content">
            <div class="scenario-tabs">
                <button class="tab-button active" data-scenario="smart">Smart Recommendation</button>
                <button class="tab-button" data-scenario="academic_research">Academic Research</button>
                <button class="tab-button" data-scenario="expert_consultation">Expert Consultation</button>
                <button class="tab-button" data-scenario="casual_discussion">Casual Discussion</button>
            </div>
            
            <div class="chat-container" id="chat-container">
                <div class="message ai-message">
                    <div class="response-content">Welcome to DAIP-LIVE Web Demo!

I can provide you with three different collaboration experiences:

- Academic Research: In-depth analysis and research report generation
- Expert Consultation: Professional advice and decision support
- Casual Discussion: Natural conversation and social interaction

Please select a scenario tab, or directly enter your question, and I will intelligently recommend the most suitable scenario.

You can try:
- "AI in education research" (Academic Research)
- "Should we adopt microservices architecture" (Expert Consultation)
- "Any good movie recommendations" (Casual Discussion)</div>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <p>AI is thinking...</p>
            </div>
            
            <div class="input-container">
                <textarea class="input-box" id="user-input" placeholder="Please enter your question or idea..." rows="3"></textarea>
                <button class="send-button" id="send-button" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let currentScenario = 'smart';
        
        function switchScenario(scenario) {
            currentScenario = scenario;
            
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-scenario="${scenario}"]`).classList.add('active');
        }
        
        async function sendMessage() {
            const userInput = document.getElementById('user-input').value.trim();
            if (!userInput) return;
            
            const chatContainer = document.getElementById('chat-container');
            const loading = document.getElementById('loading');
            const sendButton = document.getElementById('send-button');
            
            const userMessage = document.createElement('div');
            userMessage.className = 'message user-message';
            userMessage.innerHTML = `<div class="response-content">${userInput}</div>`;
            chatContainer.appendChild(userMessage);
            
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
                
                const aiMessage = document.createElement('div');
                aiMessage.className = 'message ai-message';
                
                let content = '';
                
                if (result.success && result.result) {
                    const data = result.result;
                    
                    if (data.scenario_type === 'academic_research') {
                        content = `Academic Research Report

${data.final_report}

Research Process:
${data.research_phases.map(phase => `${phase.phase}
${phase.content}`).join('\n\n')}`;
                    }
                    else if (data.scenario_type === 'expert_consultation') {
                        content = `Expert Consultation Results

Matched Experts:
${data.matched_experts.map(expert => `• ${expert}`).join('\n')}

Expert Opinions:
${data.expert_opinions.map(opinion => `${opinion.expert} (Confidence: ${(opinion.confidence * 100).toFixed(1)}%)
${opinion.opinion}`).join('\n\n')}

${data.synthesis_recommendation}`;
                    }
                    else if (data.scenario_type === 'casual_discussion') {
                        content = `Casual Discussion

Participants:
${data.participants.join(' • ')}

Discussion:
${data.conversation_flow.map(msg => `${msg.participant}: ${msg.message}`).join('\n\n')}`;
                    }
                    else {
                        content = JSON.stringify(result, null, 2);
                    }
                } else {
                    content = 'Sorry, there was a problem processing your request. Please try again later.';
                }
                
                aiMessage.innerHTML = `<div class="response-content">${content}</div>`;
                chatContainer.appendChild(aiMessage);
                
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
            } catch (error) {
                console.error('Error:', error);
                const errorMessage = document.createElement('div');
                errorMessage.className = 'message ai-message';
                errorMessage.innerHTML = '<div class="response-content">Sorry, there is a network connection problem, please try again later.</div>';
                chatContainer.appendChild(errorMessage);
            } finally {
                loading.classList.remove('show');
                sendButton.disabled = false;
            }
        }
        
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
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def smart_chat(message: ChatMessage):
    try:
        recommended_scenario = await scenario_simulator.recommend_scenario(message.user_input)
        
        if recommended_scenario == "academic_research":
            result = await scenario_simulator.simulate_academic_research(
                message.user_input, message.user_preferences
            )
        elif recommended_scenario == "expert_consultation":
            result = await scenario_simulator.simulate_expert_consultation(
                message.user_input, message.user_preferences
            )
        else:
            result = await scenario_simulator.simulate_casual_discussion(
                message.user_input, message.user_preferences
            )
        
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

@app.get("/health")
async def health_check():
    return JSONResponse(content={
        "status": "healthy",
        "service": "DAIP-LIVE Web Demo",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.get("/status")
async def system_status():
    return JSONResponse(content={
        "service": "DAIP-LIVE Web Demo",
        "status": "running",
        "features": {
            "intelligent_scenario_recommendation": True,
            "academic_research": True,
            "expert_consultation": True,
            "casual_discussion": True
        },
        "endpoints": {
            "web_interface": "/",
            "smart_chat": "/chat",
            "scenario_execution": "/scenario",
            "health_check": "/health"
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("Starting DAIP-LIVE Web Demo Service...")
    print("Web Interface: http://127.0.0.1:8000")
    print("Health Check: http://127.0.0.1:8000/health")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )