#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 17:45:00
@Author  : DAIP-LIVE Team
@File    : knowledge_web_interface.py
@Description:
    V0.3.4 知识检索和可视化Web界面
    
    提供直观的Web界面用于：
    - 知识检索查询输入
    - 多模态检索结果展示
    - 交互式知识图谱可视化
    - 知识质量评估展示
    - 实时知识发现
"""

from flask import Blueprint, render_template, request, jsonify, session
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.core_services.knowledge_retrieval_visualization import (
    KnowledgeRetrievalEngine,
    RetrievalQuery,
    RetrievalMode,
    VisualizationType,
    create_knowledge_retrieval_engine
)
from src.core_services.memory_agent import MemAgent
from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.role_manager import RoleManager

logger = logging.getLogger(__name__)

# 创建蓝图
knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/knowledge')

# 全局检索引擎实例
retrieval_engine: Optional[KnowledgeRetrievalEngine] = None

def initialize_knowledge_system():
    """初始化知识系统"""
    global retrieval_engine
    
    try:
        # 创建核心组件实例
        mem_agent = MemAgent()
        sskg_manager = EnhancedSSKGManager()
        role_manager = RoleManager()
        
        # 创建检索引擎
        retrieval_engine = create_knowledge_retrieval_engine(
            mem_agent, sskg_manager, role_manager
        )
        
        # 初始化（在后台运行）
        asyncio.create_task(retrieval_engine.initialize())
        
        logger.info("知识系统初始化完成")
        
    except Exception as e:
        logger.error(f"知识系统初始化失败: {e}")
        # 创建空实现作为降级方案
        retrieval_engine = None

@knowledge_bp.route('/')
def knowledge_home():
    """知识系统主页"""
    return render_template('knowledge/home.html')

@knowledge_bp.route('/search')
def search_page():
    """知识检索页面"""
    return render_template('knowledge/search.html')

@knowledge_bp.route('/api/search', methods=['POST'])
def api_search():
    """知识检索API"""
    
    if not retrieval_engine:
        return jsonify({"error": "知识检索引擎未初始化"}), 500
    
    try:
        data = request.get_json()
        
        # 构建检索查询
        query = RetrievalQuery(
            query_id=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            query_text=data.get('query', ''),
            retrieval_mode=RetrievalMode(data.get('mode', 'semantic')),
            max_results=data.get('max_results', 20),
            include_related=data.get('include_related', True),
            visualization_request=VisualizationType(data.get('visualization', 'knowledge_graph')) if data.get('visualization') else None,
            user_id=session.get('user_id'),
            filters=data.get('filters', {}),
            context=data.get('context', {})
        )
        
        # 执行检索
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(retrieval_engine.retrieve_knowledge(query))
        loop.close()
        
        # 准备返回数据
        response_data = {
            "query_id": result.query_id,
            "total_results": result.total_results,
            "processing_time": result.processing_time,
            "nodes": [
                {
                    "id": node.node_id,
                    "content": node.content,
                    "type": node.node_type,
                    "importance": node.importance,
                    "quality": node.quality.value,
                    "created_at": node.created_at.isoformat(),
                    "metadata": node.metadata
                }
                for node in result.matched_nodes
            ],
            "relations": [
                {
                    "id": rel.relation_id,
                    "source": rel.source_node,
                    "target": rel.target_node,
                    "type": rel.relation_type,
                    "strength": rel.strength,
                    "confidence": rel.confidence
                }
                for rel in result.related_relations
            ],
            "relevance_scores": result.relevance_scores,
            "visualization_data": result.visualization_data,
            "quality_assessment": result.quality_assessment,
            "clusters": result.clusters
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"知识检索API错误: {e}")
        return jsonify({"error": f"检索失败: {str(e)}"}), 500

@knowledge_bp.route('/api/discover_patterns', methods=['POST'])
def api_discover_patterns():
    """知识模式发现API"""
    
    if not retrieval_engine:
        return jsonify({"error": "知识检索引擎未初始化"}), 500
    
    try:
        data = request.get_json()
        
        analysis_scope = data.get('scope', 'global')
        pattern_types = data.get('pattern_types', ['clusters', 'communities', 'temporal_patterns'])
        
        # 执行模式发现
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        patterns = loop.run_until_complete(
            retrieval_engine.discover_knowledge_patterns(analysis_scope, pattern_types)
        )
        loop.close()
        
        return jsonify(patterns)
        
    except Exception as e:
        logger.error(f"模式发现API错误: {e}")
        return jsonify({"error": f"模式发现失败: {str(e)}"}), 500

@knowledge_bp.route('/api/interactive_map', methods=['POST'])
def api_interactive_map():
    """交互式知识地图API"""
    
    if not retrieval_engine:
        return jsonify({"error": "知识检索引擎未初始化"}), 500
    
    try:
        data = request.get_json()
        
        focus_concept = data.get('focus_concept')
        depth = data.get('depth', 3)
        layout_algorithm = data.get('layout_algorithm', 'force_directed')
        
        # 构建交互式地图
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        map_data = loop.run_until_complete(
            retrieval_engine.build_interactive_knowledge_map(
                focus_concept, depth, layout_algorithm
            )
        )
        loop.close()
        
        return jsonify(map_data)
        
    except Exception as e:
        logger.error(f"交互式地图API错误: {e}")
        return jsonify({"error": f"地图生成失败: {str(e)}"}), 500

@knowledge_bp.route('/api/statistics')
def api_statistics():
    """知识统计API"""
    
    if not retrieval_engine:
        return jsonify({"error": "知识检索引擎未初始化"}), 500
    
    try:
        stats = retrieval_engine.get_retrieval_statistics()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"统计API错误: {e}")
        return jsonify({"error": f"获取统计失败: {str(e)}"}), 500

@knowledge_bp.route('/visualization')
def visualization_page():
    """知识可视化页面"""
    return render_template('knowledge/visualization.html')

@knowledge_bp.route('/graph')
def graph_page():
    """知识图谱页面"""
    return render_template('knowledge/graph.html')

@knowledge_bp.route('/patterns')
def patterns_page():
    """知识模式页面"""
    return render_template('knowledge/patterns.html')

# 初始化知识系统
initialize_knowledge_system()