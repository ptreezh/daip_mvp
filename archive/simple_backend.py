#!/usr/bin/env python3
"""@Time    : 2025-08-06 11:58:00
@Author  : DAIP-LIVE Team
@File    : simple_backend.py
@Description:
    Simplified backend service for frontend integration testing
"""

import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DAIP-LIVE Simple Backend API",
    description="Simplified backend for frontend integration testing",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Root endpoint"""
    return {"message": "DAIP-LIVE Simple Backend API is running."}

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "message": "Service is operational"}

@app.get("/status")
async def detailed_status():
    """Detailed system status"""
    return {
        "timestamp": datetime.now().isoformat(),
        "service": {
            "name": "DAIP-LIVE Simple Backend API",
            "version": "0.1.0",
            "status": "running"
        },
        "overall_status": "healthy"
    }

@app.get("/scenarios")
async def get_scenarios():
    """Get available scenarios"""
    return {
        "scenarios": [
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
    }

@app.get("/roles")
async def get_roles():
    """Get roles (simplified)"""
    return {
        "roles": [
            {"id": "expert1", "name": "技术专家", "description": "技术领域专家"},
            {"id": "expert2", "name": "业务专家", "description": "业务领域专家"},
            {"id": "expert3", "name": "研究专家", "description": "研究方法专家"}
        ],
        "total_count": 3
    }

@app.get("/memory")
async def get_memory_status():
    """Get memory service status"""
    return {
        "status": "active",
        "service": "Memory Service",
        "message": "Memory service is running and accessible",
        "features": ["short_term_memory", "long_term_memory", "context_management", "retrieval_optimization"]
    }

@app.get("/wiki")
async def get_wiki_status():
    """Get wiki service status"""
    return {
        "status": "active",
        "service": "Wiki Service",
        "message": "Wiki service is running and accessible",
        "features": ["version_control", "collaborative_editing", "change_tracking", "knowledge_organization"]
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Starting DAIP-LIVE Simple Backend service...")
    print("Backend API: http://localhost:8002")
    print("API documentation: http://localhost:8002/docs")
    print("Health check: http://localhost:8002/health")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
        log_level="info"
    )