import json
import logging
from collections.abc import Callable
from typing import Any, Optional

logging.basicConfig(
    filename="workflow.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class ProtocolScheduler:
    """协议调度器：DAG推进stage，支持异常处理、流程持久化、详细日志、AI接口标准化。"""

    def __init__(
        self,
        protocol: dict[str, Any],
        ai_executor: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
        human_acceptance_callback: Optional[
            Callable[[str, dict[str, Any]], bool]
        ] = None,
        state_path: str = "workflow_state.json",
    ):
        self.protocol = protocol
        self.stages = {s["stage_name"]: s for s in protocol["stages"]}
        self.completed = set()
        self.results = {}
        self.retry_count = {}
        self.ai_executor = ai_executor
        self.human_acceptance_callback = human_acceptance_callback
        self.state_path = state_path
        self.history = []  # 历史记录

    def can_run(self, stage_name):
        stage = self.stages[stage_name]
        return all(dep in self.completed for dep in stage.get("depends_on", []))

    def save_state(self):
        state = {
            "completed": list(self.completed),
            "results": self.results,
            "retry_count": self.retry_count,
            "history": self.history,
        }
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logging.info("[持久化] 流程状态已保存")

    def load_state(self):
        with open(self.state_path, encoding="utf-8") as f:
            state = json.load(f)
        self.completed = set(state["completed"])
        self.results = state["results"]
        self.retry_count = state.get("retry_count", {})
        self.history = state.get("history", [])
        logging.info("[恢复] 流程状态已恢复")

    def log_history(self, event: str, detail: Any):
        self.history.append({"event": event, "detail": detail})
        self.save_state()

    def run(self, external_inputs: dict[str, Any]):
        pending = set(self.stages.keys()) - self.completed
        while pending:
            runnable = [s for s in pending if self.can_run(s)]
            if not runnable:
                logging.error("[异常] Deadlock or missing dependency")
                raise Exception("Deadlock or missing dependency")
            for stage_name in runnable:
                stage = self.stages[stage_name]
                max_retries = stage.get("max_retries", 1)
                try:
                    # 收集输入
                    inputs = {}
                    for inp in stage.get("inputs", []):
                        if inp["type"] == "external":
                            inputs[inp["key"]] = external_inputs[inp["key"]]
                        elif inp["type"] == "stage":
                            inputs[inp["key"]] = self.results[inp["from_stage"]][
                                inp["key"]
                            ]
                    # AI接口标准化调用
                    result = self.ai_executor(stage, inputs)
                    if not isinstance(result, dict) or "status" not in result:
                        raise Exception("AI服务返回格式错误，必须包含status字段")
                    if result["status"] != "success":
                        raise Exception(result.get("error", "AI服务返回失败"))
                    self.results[stage_name] = result["result"]
                    self.completed.add(stage_name)
                    self.retry_count[stage_name] = 0
                    self.log_history(
                        "stage_success",
                        {"stage": stage_name, "result": result["result"]},
                    )
                    logging.info(f"[成功] {stage_name} 执行成功")
                    # 人工验收节点
                    if stage.get("acceptance_required", False):
                        if self.human_acceptance_callback:
                            accepted = self.human_acceptance_callback(
                                stage_name,
                                result["result"],
                            )
                            self.log_history(
                                "human_acceptance",
                                {"stage": stage_name, "accepted": accepted},
                            )
                            if not accepted:
                                logging.warning(f"[人工驳回] {stage_name} 被人工驳回，流程挂起")
                                return False
                except Exception as e:
                    self.retry_count[stage_name] = (
                        self.retry_count.get(stage_name, 0) + 1
                    )
                    self.log_history(
                        "stage_error",
                        {
                            "stage": stage_name,
                            "error": str(e),
                            "retry": self.retry_count[stage_name],
                        },
                    )
                    logging.error(
                        f"[异常] {stage_name} 执行失败: {e!s} (第{self.retry_count[stage_name]}次)",
                    )
                    if self.retry_count[stage_name] < max_retries:
                        continue  # 重试
                    else:
                        # 进入人工介入或回溯
                        logging.critical(f"[人工介入] {stage_name} 多次失败，需人工处理或回溯")
                        self.log_history(
                            "manual_intervention",
                            {"stage": stage_name, "error": str(e)},
                        )
                        return False
            pending = set(self.stages.keys()) - self.completed
        self.save_state()
        return True

    def rollback_to_stage(self, stage_name: str):
        """回溯到指定stage，清除其后所有结果和完成状态"""
        if stage_name not in self.stages:
            raise Exception(f"Stage {stage_name} 不存在")
        idx = list(self.stages.keys()).index(stage_name)
        keep = set(list(self.stages.keys())[: idx + 1])
        self.completed = self.completed & keep
        self.results = {k: v for k, v in self.results.items() if k in keep}
        self.save_state()
        self.log_history("rollback", {"to_stage": stage_name})
        logging.warning(f"[回溯] 流程已回溯到 {stage_name}")


# **警告：以下为占位实现，必须用真实服务替换！**
# def dummy_ai_executor(stage, inputs):
#     raise NotImplementedError("必须实现真实AI服务接口，禁止占位实现！")
# def dummy_human_acceptance(stage_name, result):
#     raise NotImplementedError("必须实现真实人工验收接口，禁止占位实现！")

# 用法示例：
# if __name__ == "__main__":
#     with open("example_protocol.yaml", "r", encoding="utf-8") as f:
#         protocol = yaml.safe_load(f)
#     # **警告：必须传入真实AI服务和人工验收回调！**
#     scheduler = ProtocolScheduler(protocol, ai_executor=..., human_acceptance_callback=...)
#     scheduler.run({"document_text": "示例文档内容"})
