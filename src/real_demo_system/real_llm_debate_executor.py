#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实LLM角色辩论执行器

调用真实的大模型进行角色辩论
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_services.role_manager import RoleManager
from core_services.integrated_llm_manager import IntegratedLLMManager

logger = logging.getLogger(__name__)


class RealLLMDebateExecutor:
    """真实LLM角色辩论执行器"""
    
    def __init__(self):
        """初始化"""
        try:
            self.role_manager = RoleManager()
            self.llm_manager = IntegratedLLMManager()
            self.debate_history = []
            self.active_roles = {}
            logger.info("真实LLM辩论执行器初始化成功")
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            # 创建模拟版本以确保功能可用
            self.role_manager = None
            self.llm_manager = None
            self.debate_history = []
            self.active_roles = {}
    
    async def setup_debate_scenario(self, topic: str, role_names: List[str] = None) -> Dict[str, Any]:
        """设置辩论场景"""
        try:
            if not role_names:
                role_names = ["教育专家", "技术伦理学家", "学生代表"]
            
            # 加载角色
            roles_loaded = []
            if self.role_manager:
                try:
                    available_roles = self.role_manager.get_all_roles()
                    for role_name in role_names:
                        # 尝试找到匹配的角色
                        matching_role = None
                        for role in available_roles:
                            if role_name in role.name or role.name in role_name:
                                matching_role = role
                                break
                        
                        if matching_role:
                            roles_loaded.append({
                                "id": matching_role.id,
                                "name": matching_role.name,
                                "description": matching_role.description,
                                "system_prompt": matching_role.system_prompt,
                                "capabilities": matching_role.capabilities
                            })
                        else:
                            # 创建默认角色
                            roles_loaded.append(self._create_default_role(role_name, topic))
                except Exception as e:
                    logger.warning(f"加载角色失败，使用默认角色: {e}")
                    roles_loaded = [self._create_default_role(name, topic) for name in role_names]
            else:
                # 使用默认角色
                roles_loaded = [self._create_default_role(name, topic) for name in role_names]
            
            # 设置辩论上下文
            debate_context = {
                "topic": topic,
                "roles": roles_loaded,
                "setup_time": datetime.now().isoformat(),
                "debate_format": "结构化多轮辩论",
                "rules": {
                    "max_rounds": 3,
                    "max_response_length": 200,
                    "require_evidence": True,
                    "allow_rebuttals": True
                }
            }
            
            self.active_roles = {role["id"]: role for role in roles_loaded}
            
            return {
                "action": "场景设置",
                "description": f"成功设置关于'{topic}'的辩论场景",
                "setup_info": {
                    "topic": topic,
                    "participant_count": len(roles_loaded),
                    "roles": [{"name": r["name"], "perspective": r.get("perspective", "专业视角")} for r in roles_loaded],
                    "debate_format": "结构化多轮辩论"
                },
                "technical_details": {
                    "roles_loaded": len(roles_loaded),
                    "llm_manager_ready": self.llm_manager is not None,
                    "debate_context_created": True
                },
                "debate_context": debate_context
            }
            
        except Exception as e:
            logger.error(f"设置辩论场景失败: {e}")
            return {"error": str(e)}
    
    def _create_default_role(self, role_name: str, topic: str) -> Dict[str, Any]:
        """创建默认角色"""
        role_configs = {
            "教育专家": {
                "perspective": "教育价值",
                "stance": "支持技术在教育中的应用",
                "expertise": "教育理论、学习科学、教学方法",
                "system_prompt": f"你是一位资深教育专家，专注于{topic}在教育领域的应用。你支持技术创新在教育中的合理应用，关注学习效果和教育公平。请从教育专业角度提供观点。"
            },
            "技术伦理学家": {
                "perspective": "伦理风险",
                "stance": "谨慎评估技术风险",
                "expertise": "技术伦理、隐私保护、算法公平性",
                "system_prompt": f"你是一位技术伦理学家，专门研究{topic}的伦理影响。你关注技术应用中的伦理风险、隐私保护和社会公平问题。请从伦理角度审视技术应用。"
            },
            "学生代表": {
                "perspective": "用户体验",
                "stance": "关注实际使用体验",
                "expertise": "用户体验、学习需求、技术接受度",
                "system_prompt": f"你是学生代表，代表学习者的观点和需求。你关注{topic}对学习体验的实际影响，包括易用性、有效性和个人发展。请从学习者角度表达观点。"
            }
        }
        
        config = role_configs.get(role_name, {
            "perspective": "专业视角",
            "stance": "客观分析",
            "expertise": "相关领域专业知识",
            "system_prompt": f"你是{role_name}，请就{topic}话题提供专业观点。"
        })
        
        return {
            "id": f"role_{role_name.lower().replace(' ', '_')}",
            "name": role_name,
            "description": f"{role_name} - {config['expertise']}",
            "perspective": config["perspective"],
            "stance": config["stance"],
            "system_prompt": config["system_prompt"],
            "capabilities": ["分析", "论证", "批判性思维"]
        }
    
    async def conduct_debate_round(self, round_number: int, debate_context: Dict[str, Any], previous_statements: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """进行一轮辩论"""
        try:
            topic = debate_context["topic"]
            roles = debate_context["roles"]
            
            if not previous_statements:
                previous_statements = []
            
            round_statements = []
            
            # 为每个角色生成发言
            for i, role in enumerate(roles):
                try:
                    # 构建提示词
                    prompt = self._build_debate_prompt(role, topic, round_number, previous_statements, round_statements)
                    
                    # 调用LLM
                    if self.llm_manager:
                        try:
                            response = await self._call_llm_for_role(role, prompt)
                        except Exception as e:
                            logger.warning(f"LLM调用失败，使用模拟回复: {e}")
                            response = self._generate_simulated_response(role, topic, round_number)
                    else:
                        response = self._generate_simulated_response(role, topic, round_number)
                    
                    statement = {
                        "role_id": role["id"],
                        "role_name": role["name"],
                        "statement": response,
                        "round": round_number,
                        "order": i + 1,
                        "timestamp": datetime.now().isoformat(),
                        "perspective": role.get("perspective", "专业视角")
                    }
                    
                    round_stat