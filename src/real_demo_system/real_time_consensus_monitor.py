#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时共识监控器

实时监控共识形成过程并提供动态反馈
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class RealTimeConsensusMonitor:
    """实时共识监控器"""
    
    def __init__(self):
        """初始化实时共识监控器"""
        self.active_sessions = {}
        self.consensus_updates = []
        self.update_callbacks = []
        self.monitoring_tasks = {}
    
    def start_monitoring(
        self,
        participants: List[str],
        topic: str,
        session_config: Dict[str, Any] = None
    ) -> str:
        """开始监控会话"""
        try:
            session_id = str(uuid.uuid4())
            
            session_data = {
                "session_id": session_id,
                "participants": participants,
                "topic": topic,
                "start_time": datetime.now().isoformat(),
                "status": "active",
                "current_consensus": 0.0,
                "consensus_history": [],
                "participant_states": {participant: {"agreement": 0.0, "active": True} for participant in participants},
                "config": session_config or {}
            }
            
            self.active_sessions[session_id] = session_data
            
            # 启动监控任务
            task = asyncio.create_task(self._monitor_session(session_id))
            self.monitoring_tasks[session_id] = task
            
            logger.info(f"开始监控共识会话: {session_id}, 主题: {topic}")
            return session_id
            
        except Exception as e:
            logger.error(f"启动监控会话失败: {e}")
            return None
    
    def update_consensus_state(self, consensus_update: Dict[str, Any]) -> bool:
        """更新共识状态"""
        try:
            session_id = consensus_update.get("session_id")
            if not session_id or session_id not in self.active_sessions:
                logger.warning(f"无效的会话ID: {session_id}")
                return False
            
            session = self.active_sessions[session_id]
            
            # 更新共识分数
            if "current_consensus" in consensus_update:
                session["current_consensus"] = consensus_update["current_consensus"]
            
            # 更新参与者状态
            if "participant_positions" in consensus_update:
                for position in consensus_update["participant_positions"]:
                    participant = position.get("role") or position.get("participant")
                    if participant in session["participant_states"]:
                        session["participant_states"][participant]["agreement"] = position.get("agreement", 0.0)
            
            # 添加到历史记录
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "consensus_score": session["current_consensus"],
                "participant_states": session["participant_states"].copy(),
                "update_data": consensus_update
            }
            session["consensus_history"].append(history_entry)
            
            # 记录更新
            self.consensus_updates.append({
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "update": consensus_update
            })
            
            # 触发回调
            self._trigger_update_callbacks(session_id, consensus_update)
            
            return True
            
        except Exception as e:
            logger.error(f"更新共识状态失败: {e}")
            return False
    
    def get_consensus_progress(self, session_id: str) -> Dict[str, Any]:
        """获取共识进度"""
        try:
            if session_id not in self.active_sessions:
                return {"error": f"会话不存在: {session_id}"}
            
            session = self.active_sessions[session_id]
            
            # 分析趋势
            trend_analysis = self._analyze_consensus_trend(session["consensus_history"])
            
            progress_data = {
                "session_id": session_id,
                "topic": session["topic"],
                "participants": session["participants"],
                "current_consensus": session["current_consensus"],
                "participant_states": session["participant_states"],
                "trend_analysis": trend_analysis,
                "session_duration": self._calculate_session_duration(session["start_time"]),
                "total_updates": len(session["consensus_history"]),
                "status": session["status"]
            }
            
            return progress_data
            
        except Exception as e:
            logger.error(f"获取共识进度失败: {e}")
            return {"error": str(e)}
    
    def stop_monitoring(self, session_id: str) -> bool:
        """停止监控会话"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            # 更新会话状态
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["end_time"] = datetime.now().isoformat()
            
            # 取消监控任务
            if session_id in self.monitoring_tasks:
                self.monitoring_tasks[session_id].cancel()
                del self.monitoring_tasks[session_id]
            
            logger.info(f"停止监控共识会话: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"停止监控会话失败: {e}")
            return False
    
    def register_update_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """注册更新回调函数"""
        self.update_callbacks.append(callback)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """获取活跃会话列表"""
        return [
            {
                "session_id": session_id,
                "topic": session_data["topic"],
                "participants": session_data["participants"],
                "current_consensus": session_data["current_consensus"],
                "status": session_data["status"],
                "start_time": session_data["start_time"]
            }
            for session_id, session_data in self.active_sessions.items()
            if session_data["status"] == "active"
        ]
    
    async def _monitor_session(self, session_id: str) -> None:
        """监控会话的异步任务"""
        try:
            while session_id in self.active_sessions and self.active_sessions[session_id]["status"] == "active":
                # 定期检查会话状态
                await asyncio.sleep(5)  # 每5秒检查一次
                
                session = self.active_sessions[session_id]
                
                # 检查是否需要自动更新
                if self._should_trigger_auto_update(session):
                    await self._perform_auto_update(session_id)
                
                # 检查会话是否应该结束
                if self._should_end_session(session):
                    self.stop_monitoring(session_id)
                    break
                    
        except asyncio.CancelledError:
            logger.info(f"监控任务被取消: {session_id}")
        except Exception as e:
            logger.error(f"监控会话异常: {e}")
    
    def _analyze_consensus_trend(self, consensus_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析共识趋势"""
        if len(consensus_history) < 2:
            return {"trend": "insufficient_data", "direction": "unknown", "rate": 0.0}
        
        # 计算趋势
        recent_scores = [entry["consensus_score"] for entry in consensus_history[-5:]]  # 最近5次
        
        if len(recent_scores) >= 2:
            trend_direction = "increasing" if recent_scores[-1] > recent_scores[0] else "decreasing" if recent_scores[-1] < recent_scores[0] else "stable"
            
            # 计算变化率
            if len(recent_scores) > 1:
                rate = (recent_scores[-1] - recent_scores[0]) / (len(recent_scores) - 1)
            else:
                rate = 0.0
            
            return {
                "trend": "converging" if trend_direction == "increasing" else "diverging" if trend_direction == "decreasing" else "stable",
                "direction": trend_direction,
                "rate": rate,
                "recent_scores": recent_scores
            }
        
        return {"trend": "unknown", "direction": "unknown", "rate": 0.0}
    
    def _calculate_session_duration(self, start_time: str) -> str:
        """计算会话持续时间"""
        try:
            start = datetime.fromisoformat(start_time)
            duration = datetime.now() - start
            
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
        except Exception as e:
            logger.error(f"计算会话持续时间失败: {e}")
            return "unknown"
    
    def _trigger_update_callbacks(self, session_id: str, update_data: Dict[str, Any]) -> None:
        """触发更新回调"""
        for callback in self.update_callbacks:
            try:
                callback(session_id, update_data)
            except Exception as e:
                logger.error(f"回调函数执行失败: {e}")
    
    def _should_trigger_auto_update(self, session: Dict[str, Any]) -> bool:
        """判断是否应该触发自动更新"""
        # 简单的自动更新逻辑
        last_update_time = session["consensus_history"][-1]["timestamp"] if session["consensus_history"] else session["start_time"]
        
        try:
            last_update = datetime.fromisoformat(last_update_time)
            time_since_update = (datetime.now() - last_update).total_seconds()
            
            # 如果超过30秒没有更新，触发自动检查
            return time_since_update > 30
            
        except Exception:
            return False
    
    async def _perform_auto_update(self, session_id: str) -> None:
        """执行自动更新"""
        try:
            # 这里可以实现自动状态检查逻辑
            # 例如：检查参与者活跃度、共识变化等
            
            session = self.active_sessions[session_id]
            
            # 模拟自动更新
            auto_update = {
                "session_id": session_id,
                "type": "auto_update",
                "current_consensus": session["current_consensus"],
                "participant_positions": [
                    {"participant": participant, "agreement": state["agreement"]}
                    for participant, state in session["participant_states"].items()
                ]
            }
            
            self.update_consensus_state(auto_update)
            
        except Exception as e:
            logger.error(f"执行自动更新失败: {e}")
    
    def _should_end_session(self, session: Dict[str, Any]) -> bool:
        """判断会话是否应该结束"""
        # 简单的结束条件
        try:
            start_time = datetime.fromisoformat(session["start_time"])
            duration = (datetime.now() - start_time).total_seconds()
            
            # 如果会话超过1小时或共识达到很高水平，考虑结束
            return duration > 3600 or session["current_consensus"] > 0.95
            
        except Exception:
            return False
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要"""
        try:
            if session_id not in self.active_sessions:
                return {"error": f"会话不存在: {session_id}"}
            
            session = self.active_sessions[session_id]
            
            summary = {
                "session_id": session_id,
                "topic": session["topic"],
                "participants": session["participants"],
                "start_time": session["start_time"],
                "end_time": session.get("end_time"),
                "status": session["status"],
                "final_consensus": session["current_consensus"],
                "total_updates": len(session["consensus_history"]),
                "duration": self._calculate_session_duration(session["start_time"]),
                "consensus_progression": [entry["consensus_score"] for entry in session["consensus_history"]],
                "participant_final_states": session["participant_states"]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取会话摘要失败: {e}")
            return {"error": str(e)}