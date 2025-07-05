# src/lim.py
import json
import re
from typing import Any, Optional, Union

import ollama
import tiktoken

from src.config import (
    OLLAMA_MODEL_NAME,
    SUMMARY_RAG_K,
    SUPPORTED_MODELS,
    TOKEN_COUNT_THRESHOLD,
)
from src.models import DialogueMessage, LLMSummary
from src.sskg import SSKG

# Import cloud API functions from utils.py - 暂时注释掉，避免导入错误
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils import call_qiniu_deepseek, call_togetherai, call_openrouter, call_siliconflow, call_multi_cloud


# 提供默认的空实现，避免导入错误
def call_qiniu_deepseek(
    messages,
    options=None,
    max_retries=3,
    model_name="deepseek-v3",
):
    """默认实现，避免导入错误"""
    print("警告: call_qiniu_deepseek 未实现，使用默认响应")
    return "默认响应", {"role": "assistant", "content": "默认响应"}


def call_togetherai(
    messages,
    options=None,
    max_retries=3,
    model_name="meta-llama/Llama-2-70b-chat-hf",
):
    """默认实现，避免导入错误"""
    print("警告: call_togetherai 未实现，使用默认响应")
    return "默认响应", {"role": "assistant", "content": "默认响应"}


def call_openrouter(
    messages,
    options=None,
    max_retries=3,
    model_name="openai/gpt-3.5-turbo",
):
    """默认实现，避免导入错误"""
    print("警告: call_openrouter 未实现，使用默认响应")
    return "默认响应", {"role": "assistant", "content": "默认响应"}


def call_siliconflow(
    messages,
    options=None,
    max_retries=3,
    model_name="internlm/internlm2_5-7b-chat",
):
    """默认实现，避免导入错误"""
    print("警告: call_siliconflow 未实现，使用默认响应")
    return "默认响应", {"role": "assistant", "content": "默认响应"}


def call_multi_cloud(messages, options=None, max_retries=3, model_name="auto"):
    """默认实现，避免导入错误"""
    print("警告: call_multi_cloud 未实现，使用默认响应")
    return "默认响应", {"role": "assistant", "content": "默认响应"}


class LLMInteractionModule:
    def __init__(self, sskg_instance: SSKG):
        self.model_name = OLLAMA_MODEL_NAME
        self.model_config = SUPPORTED_MODELS.get(
            self.model_name,
            SUPPORTED_MODELS["qwen3:30b-a3b"],
        )
        self.base_url = self.model_config["base_url"]
        self.temperature = self.model_config["temperature"]
        self.sskg = sskg_instance
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        print(f"DEBUG(LIM): Initializing ollama.Client with host: {self.base_url}")
        print(
            f"DEBUG(LIM): Using model {self.model_name} ({self.model_config['description']})",
        )
        self.ollama_client = ollama.Client(host=self.base_url)
        print("DEBUG(LIM): ollama.Client initialized.")

        self.full_message_history: list[DialogueMessage] = []
        self.last_summarized_message_id: Optional[str] = None

        self._load_history_from_db()

        print(
            f"DEBUG(LIM): LLMInteractionModule initialized with model: {self.model_name}",
        )

    def _load_history_from_db(self):
        """从 SSKG 加载完整的对话历史和总结。"""
        all_messages = self.sskg.get_all_dialogue_messages()
        all_summaries = self.sskg.get_all_summaries()

        combined_history: list[Union[DialogueMessage, LLMSummary]] = []
        combined_history.extend(all_messages)
        combined_history.extend(all_summaries)
        combined_history.sort(key=lambda x: x.timestamp)

        last_summary_end_message_id = None
        for item in combined_history:
            if isinstance(item, DialogueMessage):
                self.full_message_history.append(item)
            elif isinstance(item, LLMSummary):
                if item.summarized_message_ids_list:
                    last_summary_end_message_id = item.summarized_message_ids_list[-1]

        if last_summary_end_message_id:
            idx = -1
            for i, msg in enumerate(self.full_message_history):
                if msg.message_id == last_summary_end_message_id:
                    idx = i
                    break
            if idx != -1:
                self.full_message_history = self.full_message_history[idx + 1 :]
                self.last_summarized_message_id = last_summary_end_message_id
                print(
                    f"Loaded history. Last summarized message ID: {self.last_summarized_message_id}. Remaining raw messages: {len(self.full_message_history)}",
                )
            else:
                print(
                    f"Loaded history. Last summarized message ID '{last_summary_end_message_id}' not found in current history. Keeping all messages.",
                )
        else:
            print(
                f"Loaded history. No previous summary found. Total raw messages: {len(self.full_message_history)}",
            )

    def add_message_to_history(self, message: DialogueMessage):
        """将 DialogueMessage 添加到完整的历史中并持久化到 SSKG。过滤掉 LLM 响应中的 think 内容。"""
        # 过滤 assistant 的 think 内容
        if message.role == "assistant" and message.content:
            filtered = self._filter_think_tags(message.content)
            if not filtered.strip():
                print("[LIM] 跳过记录 LLM think 内容")
                return
            message.content = filtered
        self.full_message_history.append(message)
        self.sskg.save_dialogue_message(message)

    def _build_contextual_messages(
        self,
        current_raw_messages: list[DialogueMessage],
        relevant_summaries: list[str],
    ) -> list[dict[str, Any]]:
        contextual_messages: list[dict[str, Any]] = []
        system_prompt_content = "你是一个 DAIP-L.I.V.E.，一个乐于助人、富有同理心的 AI 助手。\n"

        if relevant_summaries:
            system_prompt_content += "\n以下是与当前对话高度相关的历史记忆 (RAG 检索):\n"
            for s in relevant_summaries:
                system_prompt_content += f"- {s}\n"
            system_prompt_content += "请利用这些信息来辅助你的回答和决策。\n"

        all_past_summaries = self.sskg.get_all_summaries()
        unique_past_summaries_text = [
            s.text
            for s in all_past_summaries
            if s.text not in relevant_summaries and s.text != ""
        ]
        if unique_past_summaries_text:
            system_prompt_content += "\n以下是更早的对话历史总结 (上下文压缩):\n"
            for s in unique_past_summaries_text:
                system_prompt_content += f"- {s}\n"
            system_prompt_content += "请根据所有这些信息进行判断。\n"

        system_prompt_content += "\n请简洁、有帮助地回应，并善用你拥有的工具。"

        contextual_messages.append({"role": "system", "content": system_prompt_content})

        for msg in current_raw_messages:
            if msg.role == "user":
                if msg.content is not None:
                    contextual_messages.append({"role": "user", "content": msg.content})
            elif msg.role == "assistant":
                if msg.tool_calls_json:
                    try:
                        tool_calls_list = json.loads(msg.tool_calls_json)
                        contextual_messages.append(
                            {"role": "assistant", "tool_calls": tool_calls_list},
                        )
                    except json.JSONDecodeError:
                        print(
                            f"警告: 助手的 tool_calls_json 格式无效: {msg.tool_calls_json}. 将作为普通内容处理。",
                        )
                        contextual_messages.append(
                            {
                                "role": "assistant",
                                "content": msg.content
                                if msg.content
                                else "(工具调用数据解析失败，原始内容缺失)",
                            },
                        )
                elif msg.content is not None:
                    contextual_messages.append(
                        {"role": "assistant", "content": msg.content},
                    )
            elif msg.role == "tool":
                if msg.tool_call_id and msg.content is not None:
                    contextual_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": msg.tool_call_id,
                            "content": msg.content,
                        },
                    )
                else:
                    print(f"警告: 忽略了不完整的工具消息: {msg}")
            else:
                print(f"警告: 忽略了无法识别的消息角色或缺少内容: {msg}")
        return contextual_messages

    def _count_tokens(self, messages: list[dict[str, Any]]) -> int:
        total_tokens = 0
        for msg in messages:
            if "content" in msg and msg["content"] is not None:
                total_tokens += len(self.tokenizer.encode(msg["content"]))
            if "tool_calls" in msg and msg["tool_calls"] is not None:
                total_tokens += len(
                    self.tokenizer.encode(json.dumps(msg["tool_calls"])),
                )
            if "tool_call_id" in msg and msg["tool_call_id"] is not None:
                total_tokens += len(self.tokenizer.encode(msg["tool_call_id"]))
        return total_tokens

    def _get_current_context_token_count(self) -> int:
        text_to_count = ""
        start_index = 0
        if self.last_summarized_message_id:
            for i, msg in enumerate(self.full_message_history):
                if msg.message_id == self.last_summarized_message_id:
                    start_index = i + 1
                    break

        for msg in self.full_message_history[start_index:]:
            if msg.content:
                text_to_count += msg.content + " "
            if msg.tool_calls_json:
                try:
                    tool_calls = json.loads(msg.tool_calls_json)
                    for tc in tool_calls:
                        func_name = tc.get("function", {}).get("name", "")
                        args = tc.get("function", {}).get("arguments", "")
                        text_to_count += f"{func_name} {json.dumps(args)} "
                except json.JSONDecodeError:
                    text_to_count += "(invalid_tool_calls_json)"

        return len(self.tokenizer.encode(text_to_count))

    async def _summarize_context(self) -> Optional[LLMSummary]:
        print("AI 正在为您整理记忆: 正在总结对话历史...")

        messages_to_summarize: list[DialogueMessage] = []
        start_index = 0
        if self.last_summarized_message_id:
            for i, msg in enumerate(self.full_message_history):
                if msg.message_id == self.last_summarized_message_id:
                    start_index = i + 1
                    break
        messages_to_summarize = self.full_message_history[start_index:]

        if not messages_to_summarize:
            print("没有新的消息可以总结。")
            return None

        ollama_summary_messages = [
            {
                "role": "system",
                "content": "你是一个乐于助人的助手。请简洁地总结以下对话，捕捉关键信息，如任务、决策和重要事实。重点关注可操作项和讨论的主要主题。总结将用于重建未来对话的上下文。",
            },
        ]
        ollama_summary_messages.extend(
            self._build_contextual_messages(messages_to_summarize, []),
        )

        ollama_summary_messages.append({"role": "user", "content": "请总结上面的对话。"})

        try:
            print(
                f"DEBUG(LIM): Calling ollama.client.chat for summary with model='{self.model_name}'",
            )
            summary_response = self.ollama_client.chat(
                model=self.model_name,
                messages=ollama_summary_messages,
                stream=False,
            )
        except ollama.ResponseError as e:
            print(f"调用 Ollama API 进行总结时出错: {e}")
            return None
        except Exception as e:
            print(f"总结时发生意外错误: {e}")
            return None

        if (
            summary_response
            and "message" in summary_response
            and "content" in summary_response["message"]
        ):
            summary_text = summary_response["message"]["content"]
            summarized_ids = [msg.message_id for msg in messages_to_summarize]
            if not summarized_ids:
                print("警告: 总结生成但没有关联到任何消息ID。")
                return None

            new_summary = LLMSummary(
                text=summary_text,
                summarized_message_ids=json.dumps(
                    summarized_ids,
                ),  # Fix: Convert list to JSON string
                embedding_present=False,
            )
            self.sskg.save_summary(new_summary)
            print(f"对话已总结。总结 ID: {new_summary.summary_id}")

            self.last_summarized_message_id = summarized_ids[-1]

            idx_to_remove_up_to = -1
            for i, msg in enumerate(self.full_message_history):
                if msg.message_id == self.last_summarized_message_id:
                    idx_to_remove_up_to = i
                    break
            if idx_to_remove_up_to != -1:
                self.full_message_history = self.full_message_history[
                    idx_to_remove_up_to + 1 :
                ]
                print(
                    f"Cleaned full_message_history. Remaining messages: {len(self.full_message_history)}",
                )

            return new_summary
        else:
            print("未能从 LLM 获取总结。")
            return None

    def _get_relevant_summaries(self, query: str) -> list[str]:
        try:
            if query.strip():
                results = self.sskg.search_vector(query, k=SUMMARY_RAG_K)
                relevant_summaries = [r["document"] for r in results if "document" in r]
                print(
                    f"RAG retrieved {len(relevant_summaries)} summaries for query '{query[:50]}'.",
                )
                return relevant_summaries
            else:
                return []
        except Exception as e:
            print(f"RAG 检索总结时出错: {e}")
            return []

    def _filter_think_tags(self, text: str) -> str:
        if not text:
            return text
        # 移除所有 <think>...</think> 标签及内容
        return re.sub(r"<think>[\s\S]*?</think>", "", text)

    async def get_llm_response(
        self,
        user_input: str,
        tool_definitions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        user_message = DialogueMessage(role="user", content=user_input)
        self.add_message_to_history(user_message)

        current_token_count = self._get_current_context_token_count()
        print(f"当前未总结上下文 token 计数 (近似): {current_token_count}")
        if current_token_count >= TOKEN_COUNT_THRESHOLD:
            await self._summarize_context()

        rag_summaries = self._get_relevant_summaries(user_input)

        contextual_messages = self._build_contextual_messages(
            self.full_message_history,
            rag_summaries,
        )

        print("\n--- 发送给 LLM 的消息 ---")
        print(json.dumps(contextual_messages, indent=2, ensure_ascii=False))
        print("\n--- 发送给 LLM 的工具定义 ---")
        print(json.dumps(tool_definitions, indent=2, ensure_ascii=False))
        print(
            f"DEBUG(LIM): Using model '{self.model_name}' ({self.model_config['description']}) for chat request",
        )
        print(f"DEBUG(LIM): Temperature: {self.temperature}")
        print("--------------------------\n")

        try:
            # --- Cloud API Routing Logic using existing utils.py functions ---
            if self.model_name.startswith("auto/"):
                actual_model_name = self.model_name.split("/", 1)[1]
                print(f"    Auto-trying all cloud APIs for model: {actual_model_name}")
                content, response_message = call_multi_cloud(
                    actual_model_name,
                    contextual_messages,
                    {"temperature": self.temperature},
                )
                if content == "[API Error: All cloud APIs failed]":
                    print("所有云API均失败，回退到本地Ollama")
                    # Fallback to local Ollama
                    ollama_response = self.ollama_client.chat(
                        model="qwen3:30b-a3b",  # Fallback model
                        messages=contextual_messages,
                        tools=tool_definitions,
                        stream=False,
                        options={"temperature": self.temperature},
                    )
                    response_message = ollama_response.get("message", {})
                else:
                    # Convert cloud API response to Ollama format
                    ollama_response = {"message": response_message}
            elif self.model_name.startswith("siliconflow/"):
                actual_model_name = self.model_name.split("/", 1)[1]
                print(f"    Routing to SiliconFlow with model: {actual_model_name}")
                content, response_message = call_siliconflow(
                    actual_model_name,
                    contextual_messages,
                    {"temperature": self.temperature},
                )
                if content and not str(content).startswith("[API Error"):
                    ollama_response = {"message": response_message}
                else:
                    raise Exception(f"SiliconFlow API failed: {content}")
            elif self.model_name.startswith("openrouter/"):
                actual_model_name = self.model_name.split("/", 1)[1]
                print(f"    Routing to OpenRouter with model: {actual_model_name}")
                content, response_message = call_openrouter(
                    actual_model_name,
                    contextual_messages,
                    {"temperature": self.temperature},
                )
                if content and not str(content).startswith("[API Error"):
                    ollama_response = {"message": response_message}
                else:
                    raise Exception(f"OpenRouter API failed: {content}")
            elif self.model_name.startswith("together/"):
                actual_model_name = self.model_name.split("/", 1)[1]
                print(f"    Routing to Together.ai with model: {actual_model_name}")
                content, response_message = call_togetherai(
                    actual_model_name,
                    contextual_messages,
                    {"temperature": self.temperature},
                )
                if content and not str(content).startswith("[API Error"):
                    ollama_response = {"message": response_message}
                else:
                    raise Exception(f"Together.ai API failed: {content}")
            elif self.model_name == "deepseek-v3-qiniu":
                print("    Routing to Qiniu DeepSeek API")
                content, response_message = call_qiniu_deepseek(
                    contextual_messages,
                    {"temperature": self.temperature},
                )
                if content and not str(content).startswith("[API Error"):
                    ollama_response = {"message": response_message}
                else:
                    raise Exception(f"Qiniu DeepSeek API failed: {content}")
            else:
                # Local Ollama
                print("    Routing to local Ollama")
                ollama_response = self.ollama_client.chat(
                    model=self.model_name,
                    messages=contextual_messages,
                    tools=tool_definitions,
                    stream=False,
                    options={"temperature": self.temperature},
                )
            # --- END Cloud API Routing Logic ---

            print("DEBUG(LIM): LLM API call successful for main response.")

            assistant_ollama_message = ollama_response.get("message", {})

            if (
                "tool_calls" in assistant_ollama_message
                and assistant_ollama_message["tool_calls"]
            ):
                tool_calls = assistant_ollama_message["tool_calls"]
                tool_calls_json = json.dumps(tool_calls)
                assistant_tool_call_message = DialogueMessage(
                    role="assistant",
                    content=None,
                    tool_calls_json=tool_calls_json,
                )
                self.add_message_to_history(assistant_tool_call_message)
                print(f"LLM proposed tool calls: {tool_calls_json}")
                return {"message_type": "tool_calls", "tool_calls": tool_calls}

            if (
                "content" in assistant_ollama_message
                and assistant_ollama_message["content"] is not None
            ):
                assistant_content = assistant_ollama_message["content"]
                assistant_content = self._filter_think_tags(assistant_content)
                assistant_message = DialogueMessage(
                    role="assistant",
                    content=assistant_content,
                )
                self.add_message_to_history(assistant_message)
                print(f"LLM responded with text: {assistant_content[:100]}...")
                return {"message_type": "text", "content": assistant_content}

            print(f"警告: LLM 响应既没有内容也没有工具调用: {ollama_response}")
            assistant_message = DialogueMessage(
                role="assistant",
                content="LLM 未能提供有效响应。",
            )
            self.add_message_to_history(assistant_message)
            return {"message_type": "error", "content": "LLM 未能提供有效响应或响应格式未知。"}

        except ollama.ResponseError as e:
            error_message = f"调用 Ollama API 时出错: {e}"
            print(error_message)
            assistant_message = DialogueMessage(role="assistant", content=error_message)
            self.add_message_to_history(assistant_message)
            return {"message_type": "error", "content": error_message}
        except Exception as e:
            error_message = f"获取 LLM 响应时发生意外错误: {e}"
            print(error_message)
            import traceback

            traceback.print_exc()
            assistant_message = DialogueMessage(role="assistant", content=error_message)
            self.add_message_to_history(assistant_message)
            return {"message_type": "error", "content": error_message}

    def process_tool_output(self, tool_call_id: str, tool_output: dict[str, Any]):
        tool_output_json_str = json.dumps(tool_output, ensure_ascii=False)
        tool_output_message = DialogueMessage(
            role="tool",
            content=tool_output_json_str,
            tool_call_id=tool_call_id,
            tool_calls_json=None,
        )
        self.add_message_to_history(tool_output_message)
        print(
            f"Tool output for {tool_call_id} processed: {tool_output_json_str[:100]}...",
        )
