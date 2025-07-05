import json
import os
import sys
import uuid
from typing import Any, Optional

import yaml

from src.lim import LLMInteractionModule
from src.tool_calling_optimizer import ToolCallingOptimizer
from src.tool_config import tool_config  # 统一配置管理
from src.unified_tool_manager import UnifiedToolManager  # 替换ToolManager

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from token_utils import count_tokens, get_max_context_length


class Orchestrator:
    def __init__(
        self,
        sskg_instance: Any,
        biz_type: str = "financial_report",
        model_name: str = "gpt-3.5-turbo",
    ):
        self.sskg_instance = sskg_instance
        self.biz_type = biz_type
        self.protocol = self._load_protocol()
        self.llm_interaction_module = LLMInteractionModule(sskg_instance)
        self.tool_manager = UnifiedToolManager(
            sskg_instance,
            config=tool_config.to_dict(),
        )  # 统一工具管理器
        self.all_loaded_tool_definitions: list[dict[str, Any]] = []
        self.model_name = model_name
        self.context_limit = get_max_context_length(model_name)
        self.summary_threshold = 0.4  # 默认40%

        # 初始化工具调用优化器（已统一配置）
        self.tool_optimizer = ToolCallingOptimizer(tool_config.get_calling_config())

    def set_biz_type(self, biz_type: str):
        self.biz_type = biz_type
        self.protocol = self._load_protocol()

    def _load_protocol(self):
        protocol_dir = os.path.join("protocols", self.biz_type)
        protocol_files = [f for f in os.listdir(protocol_dir) if f.endswith(".yaml")]
        if not protocol_files:
            raise FileNotFoundError(f"No protocol YAML found in {protocol_dir}")
        protocol_path = os.path.join(protocol_dir, protocol_files[0])
        with open(protocol_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_schema(self, schema_name):
        schema_path = os.path.join("schemas", self.biz_type, schema_name)
        with open(schema_path, encoding="utf-8") as f:
            return json.load(f)

    def _log(self, message, level="INFO"):
        # 美化日志输出，带颜色和分隔符
        prefix = f"\033[94m[Orchestrator][{level}]\033[0m "
        print(f"{prefix}{message}", file=sys.stderr)

    def _load_tool_definitions(self, session_id: Optional[str] = None):
        """从 JSON 文件加载工具定义，并将其描述添加到 SSKG 的向量数据库。"""
        from src.config import get_tool_definitions_path

        tool_path = get_tool_definitions_path(session_id)
        try:
            self._log(f"正在从 '{tool_path}' 加载工具定义...", "INFO")
            with open(tool_path, encoding="utf-8") as f:
                data = json.load(f)
                self.all_loaded_tool_definitions = data.get("tools", [])
                self._log(
                    f"成功加载 {len(self.all_loaded_tool_definitions)} 个工具定义。",
                    "SUCCESS",
                )

                # 只输出一次注册日志
                registered = set()
                for tool_def in self.all_loaded_tool_definitions:
                    name = tool_def["function"]["name"]
                    if name not in registered:
                        self._log(f"已注册工具：{name}", "SUCCESS")
                        registered.add(name)
                    # 注意：每次加载都保存可能导致重复，但 SSKG 的实现应该是幂等的
                    self.sskg_instance.save_tool_definition_to_vector_db(
                        tool_def,
                        session_id=session_id,
                    )

        except FileNotFoundError:
            self._log(f"警告: 找不到工具定义文件: {tool_path}。将使用空工具列表。", "WARN")
            self.all_loaded_tool_definitions = []
        except json.JSONDecodeError as e:
            self._log(f"错误: 解析工具定义文件失败: {e}", "ERROR")
            self.all_loaded_tool_definitions = []
        except Exception as e:
            self._log(f"加载工具定义时发生意外错误: {e}", "ERROR")
            self.all_loaded_tool_definitions = []

    async def process_command(
        self,
        user_input: str,
        use_all_tools: bool = False,
        session_id: Optional[str] = None,
        summary_threshold: Optional[float] = None,
    ) -> dict[str, Any]:  # <--- 标记为 async
        self._log(f"开始处理命令，会话 ID: {session_id}")
        self._load_tool_definitions(session_id)  # 在处理命令前加载工具

        self._log(f"用户输入: {user_input}")
        # Token计数与动态摘要节点插入
        token_count = count_tokens(user_input)
        threshold = (
            summary_threshold
            if summary_threshold is not None
            else self.summary_threshold
        )
        self._log(
            f"当前输入token数: {token_count} / 上下文限制: {self.context_limit} / 阈值: {threshold}",
        )
        if token_count > int(self.context_limit * threshold):
            self._log(f"输入超出{int(threshold*100)}%上下文限制，自动插入摘要任务节点。", "WARN")
            # 构造摘要任务节点
            summary_prompt = "当前输入内容过长，请将其摘要为更短的内容，保留关键信息。"
            summary_result = await self.llm_interaction_module.get_llm_response(
                summary_prompt + user_input,
                [],
            )
            if summary_result["type"] == "text":
                user_input = summary_result["content"]
                self._log(f"摘要后token数: {count_tokens(user_input)}")
            else:
                self._log("摘要任务失败，继续使用原始输入。", "ERROR")
        try:
            if use_all_tools:
                selected_tools_definitions = self.all_loaded_tool_definitions
                self._log(f"使用所有工具定义（禁用动态筛选）: {len(selected_tools_definitions)} 个工具")
            else:
                # 使用智能工具调用优化器
                decision = self.tool_optimizer.should_use_tools(user_input)
                self._log(f"工具调用决策: {decision.reasoning}")

                if decision.should_call_tools:
                    # 优化工具选择
                    selected_tools_definitions = (
                        self.tool_optimizer.optimize_tool_selection(
                            self.all_loaded_tool_definitions,
                            user_input,
                        )
                    )

                    # 如果优化器没有找到合适的工具，回退到原有的向量搜索
                    if not selected_tools_definitions:
                        TOOL_SEARCH_K = tool_config.calling.tool_search_k
                        relevant_tool_names = self.sskg_instance.search_tools_by_query(
                            user_input,
                            k=TOOL_SEARCH_K,
                        )
                        self._log(f"回退到向量搜索，相关工具: {relevant_tool_names}")
                        selected_tools_definitions = [
                            tool
                            for tool in self.all_loaded_tool_definitions
                            if tool["function"]["name"] in relevant_tool_names
                        ]

                    if (
                        not selected_tools_definitions
                        and self.all_loaded_tool_definitions
                    ):
                        self._log("未找到相关工具，发送所有工具定义（作为备用）。", "WARN")
                        selected_tools_definitions = self.all_loaded_tool_definitions
                else:
                    # 决策不使用工具，直接进行对话
                    selected_tools_definitions = []
                    self._log("智能决策：不使用工具，直接对话")

                if (
                    not selected_tools_definitions
                    and not self.all_loaded_tool_definitions
                ):
                    self._log("未加载任何工具定义。", "ERROR")
                else:
                    self._log(
                        f"向LLM发送 {len(selected_tools_definitions)} 个精选工具。",
                        "INFO",
                    )

                # 日志体现本轮动态加载工具
                if selected_tools_definitions:
                    loaded_names = [
                        tool["function"]["name"] for tool in selected_tools_definitions
                    ]
                    self._log(f"本轮动态加载工具: {loaded_names}", "INFO")
            self._log("获取 LLM 响应 ...")
            llm_response = await self.llm_interaction_module.get_llm_response(
                user_input,
                selected_tools_definitions,
            )
            self._log(f"LLM 响应: {llm_response}")
            if llm_response["type"] == "tool_calls":
                tool_calls = llm_response["tool_calls"]
                self._log(f"AI 提议调用工具: {tool_calls}")
                tool_outputs = []
                for tool_call_item in tool_calls:
                    function_name = tool_call_item["function"]["name"]
                    function_args = tool_call_item["function"]["arguments"]
                    tool_call_id = tool_call_item.get("id", str(uuid.uuid4()))
                    self._log(f"正在执行工具 '{function_name}' 参数: {function_args}")
                    output = self.tool_manager.execute_tool(
                        function_name,
                        function_args,
                    )
                    tool_outputs.append(
                        {"tool_call_id": tool_call_id, "output": output},
                    )
                    self._log(f"工具 '{function_name}' 输出: {output}")
                    self.llm_interaction_module.process_tool_output(
                        tool_call_id,
                        output,
                    )
                self._log("工具执行完毕，再次调用 LLM 以获取最终回复 ...")
                final_llm_response = await self.llm_interaction_module.get_llm_response(
                    "",
                    selected_tools_definitions,
                )
                self._log(f"最终 LLM 响应: {final_llm_response}")
                return final_llm_response
            elif llm_response["type"] == "text":
                self._log(f"AI: {llm_response['content']}")
                return llm_response
            elif llm_response["type"] == "error":
                self._log(f"AI (错误): {llm_response['content']}", "ERROR")
                return llm_response
            else:
                self._log(f"AI (未知响应类型): {llm_response}", "ERROR")
                return {"type": "error", "content": "LLM 返回未知响应类型。"}
        except Exception as e:
            self._log(f"[ERROR] 处理命令异常: {e}", "ERROR")
            import traceback

            traceback.print_exc()
            return {"type": "error", "content": f"Orchestrator 处理异常: {e}"}
