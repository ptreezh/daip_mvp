#!/usr/bin/env python3
"""交互式演示流程管理器
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .demo_analyzer import DemoAnalyzer
from .demo_types import DemoStatus, DemoStepStatus
from .scenario_manager import ScenarioManager
from .step_executor import StepExecutor

logger = logging.getLogger(__name__)


class InteractiveDemoFlow:
    """交互式演示流程管理器"""

    def __init__(self, role_manager=None, workflow_engine=None, wiki_service=None):
        """初始化"""
        self.role_manager = role_manager
        self.workflow_engine = workflow_engine
        self.wiki_service = wiki_service

        # 组件
        self.scenario_manager = ScenarioManager()
        self.step_executor = StepExecutor()
        self.analyzer = DemoAnalyzer()

        # 状态
        self.current_demo = None
        self.demo_history = []

        # 配置
        self.config = {
            "record_interactions": True,
            "auto_advance": False
        }

    def get_available_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """获取可用场景"""
        return self.scenario_manager.get_available_scenarios()

    async def start_demo(self, scenario_type: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """启动演示"""
        try:
            # 获取场景信息
            scenario_info = self.scenario_manager.get_scenario(scenario_type)

            # 验证参数
            if custom_params and not self.scenario_manager.validate_scenario_params(scenario_type, custom_params):
                return {"error": "无效的自定义参数"}

            # 创建演示实例
            demo_id = str(uuid.uuid4())
            self.current_demo = {
                "demo_id": demo_id,
                "scenario_type": scenario_type,
                "scenario_info": scenario_info,
                "custom_params": custom_params or {},
                "start_time": datetime.now(),
                "current_step": 0,
                "steps": [],
                "status": DemoStatus.INITIALIZED.value,
                "user_interactions": [],
                "technical_logs": []
            }

            # 初始化步骤
            await self._initialize_steps()

            return {
                "demo_id": demo_id,
                "scenario_name": scenario_info["name"],
                "description": scenario_info["description"],
                "estimated_duration": scenario_info["duration_estimate"],
                "total_steps": len(scenario_info["steps"]),
                "customizable_params": scenario_info["customizable_params"],
                "status": "initialized"
            }

        except Exception as e:
            logger.error(f"启动演示失败: {e}")
            return {"error": str(e)}

    async def _initialize_steps(self):
        """初始化演示步骤"""
        scenario_info = self.current_demo["scenario_info"]
        step_names = scenario_info["steps"]

        for i, step_name in enumerate(step_names):
            step = {
                "step_id": f"step_{i+1}",
                "step_name": step_name,
                "step_number": i + 1,
                "status": DemoStepStatus.PENDING.value,
                "start_time": None,
                "end_time": None,
                "duration": None,
                "inputs": {},
                "outputs": {},
                "error_info": None
            }
            self.current_demo["steps"].append(step)

    async def execute_next_step(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行下一步"""
        try:
            if not self.current_demo:
                return {"error": "没有活跃的演示"}

            current_step_index = self.current_demo["current_step"]
            steps = self.current_demo["steps"]

            if current_step_index >= len(steps):
                return await self._complete_demo()

            current_step = steps[current_step_index]

            # 更新步骤状态
            current_step["status"] = DemoStepStatus.IN_PROGRESS.value
            current_step["start_time"] = datetime.now()

            # 记录用户输入
            if user_input:
                current_step["inputs"].update(user_input)
                self._record_interaction("step_input", user_input)

            # 执行步骤
            step_result = await self.step_executor.execute_step(
                self.current_demo["scenario_type"],
                current_step["step_name"],
                current_step
            )

            # 更新步骤结果
            current_step["outputs"] = step_result
            current_step["end_time"] = datetime.now()
            current_step["duration"] = (current_step["end_time"] - current_step["start_time"]).total_seconds()
            current_step["status"] = DemoStepStatus.COMPLETED.value

            # 移动到下一步
            self.current_demo["current_step"] += 1

            return {
                "step_completed": current_step["step_name"],
                "step_number": current_step["step_number"],
                "result": step_result,
                "next_step": self._get_next_step_info(),
                "progress": {
                    "completed_steps": self.current_demo["current_step"],
                    "total_steps": len(steps),
                    "percentage": (self.current_demo["current_step"] / len(steps)) * 100
                }
            }

        except Exception as e:
            logger.error(f"执行步骤失败: {e}")
            return {"error": str(e)}

    def _get_next_step_info(self) -> Optional[Dict[str, Any]]:
        """获取下一步信息"""
        if not self.current_demo:
            return None

        current_step_index = self.current_demo["current_step"]
        steps = self.current_demo["steps"]

        if current_step_index >= len(steps):
            return None

        next_step = steps[current_step_index]
        return {
            "step_name": next_step["step_name"],
            "step_number": next_step["step_number"],
            "status": next_step["status"]
        }

    async def _complete_demo(self) -> Dict[str, Any]:
        """完成演示"""
        try:
            # 更新状态
            self.current_demo["status"] = DemoStatus.COMPLETED.value
            self.current_demo["end_time"] = datetime.now()
            self.current_demo["total_duration"] = (
                self.current_demo["end_time"] - self.current_demo["start_time"]
            ).total_seconds()

            # 生成分析报告
            analysis_report = self.analyzer.analyze_demo(self.current_demo)
            self.current_demo["analysis_report"] = analysis_report

            # 生成摘要
            summary = self.analyzer.generate_summary(self.current_demo)

            # 保存到历史
            self.demo_history.append(self.current_demo.copy())

            # 清理当前演示
            completed_demo = self.current_demo
            self.current_demo = None

            return {
                "status": "demo_completed",
                "demo_id": completed_demo["demo_id"],
                "total_duration": completed_demo["total_duration"],
                "completed_steps": len(completed_demo["steps"]),
                "analysis_report": analysis_report,
                "summary": summary
            }

        except Exception as e:
            logger.error(f"完成演示失败: {e}")
            return {"error": str(e)}

    def _record_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """记录用户交互"""
        if self.current_demo and self.config["record_interactions"]:
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "type": interaction_type,
                "data": data,
                "step_context": self.current_demo["current_step"]
            }
            self.current_demo["user_interactions"].append(interaction)

    def get_current_demo_status(self) -> Optional[Dict[str, Any]]:
        """获取当前演示状态"""
        if not self.current_demo:
            return None

        return {
            "demo_id": self.current_demo["demo_id"],
            "scenario_type": self.current_demo["scenario_type"],
            "status": self.current_demo["status"],
            "current_step": self.current_demo["current_step"],
            "total_steps": len(self.current_demo["steps"]),
            "progress_percentage": (self.current_demo["current_step"] / len(self.current_demo["steps"])) * 100,
            "elapsed_time": (datetime.now() - self.current_demo["start_time"]).total_seconds()
        }

    def get_demo_history(self) -> List[Dict[str, Any]]:
        """获取演示历史"""
        return [{
            "demo_id": demo["demo_id"],
            "scenario_type": demo["scenario_type"],
            "scenario_name": demo["scenario_info"]["name"],
            "start_time": demo["start_time"].isoformat(),
            "end_time": demo.get("end_time", datetime.now()).isoformat(),
            "duration": demo.get("total_duration", 0),
            "status": demo["status"],
            "quality_score": demo.get("analysis_report", {}).get("quality_assessment", {}).get("overall_quality_score", 0)
        } for demo in self.demo_history]
