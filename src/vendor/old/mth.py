from datetime import datetime
from typing import Any, Optional

from src.models import LegacyTask as Task
from src.protocol_validator import format_protocol_validation_result, validate_protocol
from src.sskg import SSKG  # 导入 SSKG 类


class ModularToolHandlers:
    def __init__(self, sskg_instance: SSKG):
        self.sskg = sskg_instance

    def create_task(
        self,
        description: str,
        due_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """创建一个新的待办事项或任务。
        Args:
            description (str): 任务的详细描述。
            due_date (Optional[str]): 任务的截止日期，格式为 YYYY-MM-DD。
        Returns:
            Dict[str, Any]: 包含操作结果的字典。
        """
        # 如果提供了 due_date，验证其格式
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                return {"success": False, "message": "无效的 due_date 格式。请使用 YYYY-MM-DD。"}

        new_task = Task(description=description, due_date=due_date)
        try:
            self.sskg.save_task(new_task)
            return {
                "success": True,
                "message": f"任务 '{description}' (ID: {new_task.task_id[:8]}) 创建成功。",
            }
        except Exception as e:
            return {"success": False, "message": f"创建任务失败: {e}"}

    def get_task_info(self, query: str) -> dict[str, Any]:
        """根据关键词或任务ID查询现有任务的信息。
        Args:
            query (str): 用于搜索任务的关键词或任务ID。
        Returns:
            Dict[str, Any]: 包含查询结果的字典。
        """
        try:
            found_tasks = self.sskg.get_tasks_by_query(query)

            if found_tasks:
                task_details = [task.model_dump() for task in found_tasks]
                return {
                    "success": True,
                    "tasks": task_details,
                    "message": f"找到 {len(found_tasks)} 个匹配 '{query}' 的任务。",
                }
            else:
                return {"success": False, "message": f"未找到匹配 '{query}' 的任务。"}
        except Exception as e:
            return {"success": False, "message": f"查询任务失败: {e}"}

    def validate_protocol(self, yaml_content: str) -> dict[str, Any]:
        """验证YAML字符串是否符合DAIP协议模式。
        Args:
            yaml_content (str): 要验证的YAML内容字符串
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        try:
            result = validate_protocol(yaml_content)
            formatted_result = format_protocol_validation_result(result)

            return {
                "success": result["success"],
                "message": formatted_result,
                "validation_details": result,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"协议验证过程中发生错误: {e!s}",
                "validation_details": {"success": False, "error": str(e)},
            }
