#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共识形成过程

管理和协调共识形成的各个阶段
"""

import logging
import uuid
from typing import Any, Dict, List
from src.core_services.consensus_dispatcher import UnifiedConsensusDispatcher
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class FormationStage(str, Enum):
    """共识形成阶段"""
    INITIALIZATION = "initialization"
    POSITION_COLLECTION = "position_collection"
    CONFLICT_IDENTIFICATION = "conflict_identification"
    DIALOGUE_FACILITATION = "dialogue_facilitation"
    CONVERGENCE_MONITORING = "convergence_monitoring"
    CONSENSUS_VALIDATION = "consensus_validation"
    FINALIZATION = "finalization"


class ConflictType(str, Enum):
    """冲突类型"""
    PRIORITY_DIFFERENCE = "priority_difference"
    VALUE_CONFLICT = "value_conflict"
    FACTUAL_DISAGREEMENT = "factual_disagreement"
    METHODOLOGICAL_DISPUTE = "methodological_dispute"
    RESOURCE_COMPETITION = "resource_competition"


class ConsensusFormationProcess:
    """共识形成过程管理器"""
    
    def __init__(self, dispatcher: UnifiedConsensusDispatcher):
        """初始化共识形成过程管理器"""
        self.dispatcher = dispatcher
        self.formation_stages = list(FormationStage)
        self.process_history = []
        self.active_processes = {}
        self.conflict_resolution_strategies = {
            ConflictType.PRIORITY_DIFFERENCE: self._resolve_priority_conflict,
            ConflictType.VALUE_CONFLICT: self._resolve_value_conflict,
            ConflictType.FACTUAL_DISAGREEMENT: self._resolve_factual_conflict,
            ConflictType.METHODOLOGICAL_DISPUTE: self._resolve_methodological_conflict,
            ConflictType.RESOURCE_COMPETITION: self._resolve_resource_conflict
        }
    
    def initiate_consensus_formation(
        self,
        topic: str,
        initial_positions: List[Dict[str, Any]],
        target_consensus: float = 0.8,
        process_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """启动共识形成过程"""
        try:
            formation_id = str(uuid.uuid4())
            
            process_data = {
                "formation_id": formation_id,
                "topic": topic,
                "initial_positions": initial_positions,
                "target_consensus": target_consensus,
                "current_stage": FormationStage.INITIALIZATION,
                "start_time": datetime.now().isoformat(),
                "estimated_duration": self._estimate_process_duration(initial_positions, target_consensus),
                "stages": self._create_stage_plan(initial_positions, target_consensus),
                "participants": [pos.get("participant") for pos in initial_positions],
                "current_consensus": 0.0,
                "conflicts": [],
                "resolutions": [],
                "config": process_config or {}
            }
            
            self.active_processes[formation_id] = process_data
            
            # 开始第一阶段
            self._advance_to_next_stage(formation_id)
            
            result = {
                "formation_id": formation_id,
                "status": "initiated",
                "current_stage": process_data["current_stage"],
                "stages": [stage["name"] for stage in process_data["stages"]],
                "estimated_duration": process_data["estimated_duration"],
                "participants": process_data["participants"]
            }
            
            self.process_history.append({
                "formation_id": formation_id,
                "action": "initiate",
                "timestamp": datetime.now().isoformat(),
                "data": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"启动共识形成过程失败: {e}")
            return {"error": str(e)}
    
    def facilitate_convergence(
        self,
        formation_id: str,
        convergence_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """促进共识收敛"""
        try:
            if formation_id not in self.active_processes:
                return {"error": f"进程不存在: {formation_id}"}
            
            process = self.active_processes[formation_id]
            
            # 更新当前共识水平
            if "current_consensus" in convergence_data:
                process["current_consensus"] = convergence_data["current_consensus"]
            
            # 分析收敛情况
            convergence_analysis = self._analyze_convergence(process, convergence_data)
            
            # 根据分析结果采取行动
            actions_taken = []
            
            if convergence_analysis["convergence_rate"] < 0.1:
                # 收敛缓慢，采取促进措施
                actions_taken.extend(self._apply_convergence_facilitation(process, convergence_data))
            
            if convergence_analysis["conflicts_detected"]:
                # 检测到冲突，启动冲突解决
                conflict_resolution = self.resolve_conflicts(convergence_analysis["conflicts_detected"])
                actions_taken.append(f"解决了{len(conflict_resolution['resolved_conflicts'])}个冲突")
            
            # 检查是否可以进入下一阶段
            if self._can_advance_stage(process):
                self._advance_to_next_stage(formation_id)
                actions_taken.append(f"进入阶段: {process['current_stage']}")
            
            result = {
                "formation_id": formation_id,
                "convergence_analysis": convergence_analysis,
                "actions_taken": actions_taken,
                "current_consensus": process["current_consensus"],
                "current_stage": process["current_stage"],
                "progress": self._calculate_overall_progress(process)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"促进共识收敛失败: {e}")
            return {"error": str(e)}
    
    def resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解决冲突"""
        try:
            resolved_conflicts = []
            resolution_strategies = []
            
            for conflict in conflicts:
                conflict_type = ConflictType(conflict.get("conflict_type", ConflictType.PRIORITY_DIFFERENCE))
                
                if conflict_type in self.conflict_resolution_strategies:
                    resolution = self.conflict_resolution_strategies[conflict_type](conflict)
                    
                    if resolution["success"]:
                        resolved_conflicts.append({
                            "conflict": conflict,
                            "resolution": resolution,
                            "timestamp": datetime.now().isoformat()
                        })
                        resolution_strategies.append(resolution["strategy"])
                
            result = {
                "resolved_conflicts": resolved_conflicts,
                "resolution_strategies": resolution_strategies,
                "success_rate": len(resolved_conflicts) / len(conflicts) if conflicts else 0.0,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解决冲突失败: {e}")
            return {"error": str(e)}
    
    def _create_stage_plan(self, initial_positions: List[Dict[str, Any]], target_consensus: float) -> List[Dict[str, Any]]:
        """创建阶段计划"""
        stages = []
        
        for i, stage in enumerate(self.formation_stages):
            stage_info = {
                "name": stage,
                "order": i + 1,
                "description": self._get_stage_description(stage),
                "estimated_duration": self._estimate_stage_duration(stage, initial_positions),
                "success_criteria": self._get_stage_success_criteria(stage),
                "status": "pending"
            }
            stages.append(stage_info)
        
        return stages
    
    def _estimate_process_duration(self, initial_positions: List[Dict[str, Any]], target_consensus: float) -> str:
        """估算过程持续时间"""
        # 基于参与者数量和目标共识水平估算
        base_duration = 30  # 基础30分钟
        participant_factor = len(initial_positions) * 5  # 每个参与者增加5分钟
        consensus_factor = (1.0 - target_consensus) * 20  # 目标越高，时间越长
        
        total_minutes = base_duration + participant_factor + consensus_factor
        
        hours, minutes = divmod(int(total_minutes), 60)
        return f"{hours:02d}:{minutes:02d}:00"
    
    def _get_stage_description(self, stage: FormationStage) -> str:
        """获取阶段描述"""
        descriptions = {
            FormationStage.INITIALIZATION: "初始化参与者和设置",
            FormationStage.POSITION_COLLECTION: "收集各方初始立场",
            FormationStage.CONFLICT_IDENTIFICATION: "识别立场间的冲突",
            FormationStage.DIALOGUE_FACILITATION: "促进参与者对话",
            FormationStage.CONVERGENCE_MONITORING: "监控共识收敛过程",
            FormationStage.CONSENSUS_VALIDATION: "验证达成的共识",
            FormationStage.FINALIZATION: "最终确认和文档化"
        }
        return descriptions.get(stage, "未知阶段")
    
    def _estimate_stage_duration(self, stage: FormationStage, initial_positions: List[Dict[str, Any]]) -> int:
        """估算阶段持续时间（分钟）"""
        base_durations = {
            FormationStage.INITIALIZATION: 5,
            FormationStage.POSITION_COLLECTION: 10,
            FormationStage.CONFLICT_IDENTIFICATION: 8,
            FormationStage.DIALOGUE_FACILITATION: 15,
            FormationStage.CONVERGENCE_MONITORING: 12,
            FormationStage.CONSENSUS_VALIDATION: 8,
            FormationStage.FINALIZATION: 5
        }
        
        base = base_durations.get(stage, 10)
        participant_factor = len(initial_positions) * 2
        
        return base + participant_factor
    
    def _get_stage_success_criteria(self, stage: FormationStage) -> List[str]:
        """获取阶段成功标准"""
        criteria = {
            FormationStage.INITIALIZATION: ["所有参与者已就绪", "讨论规则已确立"],
            FormationStage.POSITION_COLLECTION: ["收集到所有参与者的初始立场", "立场清晰度达标"],
            FormationStage.CONFLICT_IDENTIFICATION: ["识别出主要冲突点", "冲突分类完成"],
            FormationStage.DIALOGUE_FACILITATION: ["参与者积极参与对话", "观点交流充分"],
            FormationStage.CONVERGENCE_MONITORING: ["共识水平持续提升", "收敛趋势明显"],
            FormationStage.CONSENSUS_VALIDATION: ["达到目标共识水平", "参与者确认同意"],
            FormationStage.FINALIZATION: ["共识文档化完成", "所有参与者签署确认"]
        }
        return criteria.get(stage, ["阶段目标达成"])
    
    def _advance_to_next_stage(self, formation_id: str) -> bool:
        """进入下一阶段"""
        try:
            process = self.active_processes[formation_id]
            current_stage_index = self.formation_stages.index(process["current_stage"])
            
            # 标记当前阶段完成
            process["stages"][current_stage_index]["status"] = "completed"
            process["stages"][current_stage_index]["completion_time"] = datetime.now().isoformat()
            
            # 进入下一阶段
            if current_stage_index + 1 < len(self.formation_stages):
                next_stage = self.formation_stages[current_stage_index + 1]
                process["current_stage"] = next_stage
                process["stages"][current_stage_index + 1]["status"] = "active"
                process["stages"][current_stage_index + 1]["start_time"] = datetime.now().isoformat()
                return True
            else:
                # 所有阶段完成
                process["status"] = "completed"
                process["completion_time"] = datetime.now().isoformat()
                return False
                
        except Exception as e:
            logger.error(f"进入下一阶段失败: {e}")
            return False
    
    def _can_advance_stage(self, process: Dict[str, Any]) -> bool:
        """判断是否可以进入下一阶段"""
        current_stage = process["current_stage"]
        
        # 简单的阶段推进逻辑
        if current_stage == FormationStage.INITIALIZATION:
            return len(process["participants"]) > 0
        elif current_stage == FormationStage.POSITION_COLLECTION:
            return len(process["initial_positions"]) >= len(process["participants"])
        elif current_stage == FormationStage.CONFLICT_IDENTIFICATION:
            return True  # 总是可以进入对话阶段
        elif current_stage == FormationStage.DIALOGUE_FACILITATION:
            return process["current_consensus"] > 0.3  # 有一定共识基础
        elif current_stage == FormationStage.CONVERGENCE_MONITORING:
            return process["current_consensus"] >= process["target_consensus"]
        elif current_stage == FormationStage.CONSENSUS_VALIDATION:
            return True  # 验证后总是可以最终确认
        
        return False
    
    def _analyze_convergence(self, process: Dict[str, Any], convergence_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析收敛情况"""
        analysis = {
            "convergence_rate": 0.0,
            "conflicts_detected": [],
            "participant_engagement": {},
            "bottlenecks": []
        }
        
        # 计算收敛速度
        if "consensus_history" in convergence_data and len(convergence_data["consensus_history"]) >= 2:
            history = convergence_data["consensus_history"]
            recent_change = history[-1] - history[-2] if len(history) >= 2 else 0.0
            analysis["convergence_rate"] = recent_change
        
        # 检测冲突
        if "disagreements" in convergence_data:
            for disagreement in convergence_data["disagreements"]:
                conflict = {
                    "participants": disagreement.get("participants", []),
                    "conflict_type": disagreement.get("type", ConflictType.PRIORITY_DIFFERENCE),
                    "description": disagreement.get("description", ""),
                    "severity": disagreement.get("severity", "medium")
                }
                analysis["conflicts_detected"].append(conflict)
        
        return analysis
    
    def _apply_convergence_facilitation(self, process: Dict[str, Any], convergence_data: Dict[str, Any]) -> List[str]:
        """应用收敛促进措施"""
        actions = []
        
        # 如果收敛缓慢，采取措施
        if process["current_consensus"] < 0.5:
            actions.append("引入结构化讨论格式")
            actions.append("重新澄清讨论目标")
        
        if "low_engagement_participants" in convergence_data:
            actions.append("激励低参与度成员")
        
        return actions
    
    def _calculate_overall_progress(self, process: Dict[str, Any]) -> float:
        """计算整体进度"""
        completed_stages = sum(1 for stage in process["stages"] if stage["status"] == "completed")
        total_stages = len(process["stages"])
        
        stage_progress = completed_stages / total_stages
        consensus_progress = process["current_consensus"] / process["target_consensus"]
        
        # 综合进度（阶段进度权重0.6，共识进度权重0.4）
        return stage_progress * 0.6 + consensus_progress * 0.4
    
    # 冲突解决策略方法
    def _resolve_priority_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """解决优先级冲突"""
        return {
            "success": True,
            "strategy": "priority_negotiation",
            "resolution": "通过权重调整和优先级协商解决冲突",
            "actions": ["重新评估优先级", "寻找平衡点", "建立权重共识"]
        }
    
    def _resolve_value_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """解决价值观冲突"""
        return {
            "success": True,
            "strategy": "value_bridge_building",
            "resolution": "寻找共同价值基础，建立价值桥梁",
            "actions": ["识别共同价值", "尊重差异", "寻找兼容方案"]
        }
    
    def _resolve_factual_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """解决事实争议"""
        return {
            "success": True,
            "strategy": "evidence_based_resolution",
            "resolution": "通过证据验证和专家意见解决事实争议",
            "actions": ["收集可靠证据", "咨询专家意见", "建立事实共识"]
        }
    
    def _resolve_methodological_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """解决方法论争议"""
        return {
            "success": True,
            "strategy": "methodology_synthesis",
            "resolution": "整合不同方法论，形成综合方案",
            "actions": ["分析方法优劣", "寻找互补性", "设计混合方案"]
        }
    
    def _resolve_resource_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """解决资源竞争"""
        return {
            "success": True,
            "strategy": "resource_optimization",
            "resolution": "优化资源配置，寻找共赢方案",
            "actions": ["评估资源需求", "探索替代方案", "建立分配机制"]
        }
    
    def get_process_status(self, formation_id: str) -> Dict[str, Any]:
        """获取过程状态"""
        if formation_id not in self.active_processes:
            return {"error": f"进程不存在: {formation_id}"}
        
        process = self.active_processes[formation_id]
        
        return {
            "formation_id": formation_id,
            "topic": process["topic"],
            "current_stage": process["current_stage"],
            "current_consensus": process["current_consensus"],
            "target_consensus": process["target_consensus"],
            "progress": self._calculate_overall_progress(process),
            "participants": process["participants"],
            "stages": process["stages"],
            "conflicts": len(process["conflicts"]),
            "resolutions": len(process["resolutions"])
        }