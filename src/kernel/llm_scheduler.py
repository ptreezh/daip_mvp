"""@Time    : 2024-07-16 10:30:00
@Author  : DAIP-LIVE Team
@File    : llm_scheduler.py
@Description:
    Manages and serializes access to the LLM resource.
    This scheduler implements a FIFO queue to handle concurrent requests from
    different parts of the system (e.g., multiple AI roles), ensuring that
    LLM interactions are processed one at a time.
"""

import asyncio
import json
import logging
from collections.abc import Coroutine
from dataclasses import dataclass
from typing import Any, Dict, List

from .interaction_manager import InteractionManager
from .llm_interface import LLMInterface
from .tool_executor import ToolExecutor


@dataclass
class LLMRequest:
    """Represents a single request to be processed by the LLM."""

    history: List[Dict[str, Any]]
    future: asyncio.Future


class LLMScheduler:
    """A scheduler that manages a queue of requests for an LLM.

    This class ensures that only one request is processed by the LLM at a time,
    which is critical for managing single-instance LLM resources in a concurrent
    environment.
    """

    def __init__(
        self,
        llm_interface: LLMInterface,
        tool_executor: ToolExecutor,
        interaction_manager: InteractionManager,
    ):
        """Initializes the LLMScheduler.

        Args:
            llm_interface: The interface to the language model.
            tool_executor: The executor for running tools.
            interaction_manager: The engine for preparing conversational context.

        """
        self.llm_interface = llm_interface
        self.tool_executor = tool_executor
        self.interaction_manager = interaction_manager
        self._queue: asyncio.Queue[LLMRequest] = asyncio.Queue()
        self._worker_task: Coroutine[Any, Any, None] | None = None
        logging.info("LLMScheduler initialized.")

    async def start(self) -> None:
        """Starts the background worker task."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
            logging.info("LLMScheduler worker started.")

    async def stop(self) -> None:
        """Stops the background worker task gracefully."""
        if self._worker_task:
            self._queue.put_nowait(None)  # Sentinel value to stop the worker
            await self._worker_task
            self._worker_task = None
            logging.info("LLMScheduler worker stopped.")

    async def submit_request(self, history: List[Dict[str, Any]]) -> str:
        """Submits a request to the LLM and waits for the final response.

        This method handles the entire lifecycle of a request, including
        potential multi-turn tool calls.

        Args:
            history: The conversation history to send to the LLM.

        Returns:
            The final text response from the assistant.

        """
        future = asyncio.get_running_loop().create_future()
        request = LLMRequest(history=history, future=future)
        await self._queue.put(request)
        return await future

    async def _worker(self) -> None:
        """The background worker that processes requests from the queue."""
        logging.info("LLM worker is running and waiting for requests.")
        while True:
            request = await self._queue.get()
            if request is None:  # Sentinel check
                logging.info("Sentinel received, LLM worker shutting down.")
                break

            history, future = request.history, request.future
            try:
                # This loop manages the conversation turn, including tool calls.
                while True:
                    # Use InteractionManager to prepare the full context for the LLM
                    messages_for_llm = await self.interaction_manager.prepare_context(history)

                    tool_defs = self.tool_executor.get_tool_definitions()
                    response = await self.llm_interface.generate(
                        messages=messages_for_llm, tools=tool_defs
                    )

                    if response.get("tool_calls"):
                        history.append(response)
                        for tool_call in response["tool_calls"]:
                            name = tool_call["function"]["name"]
                            args = json.loads(tool_call["function"]["arguments"])
                            result = self.tool_executor.execute(name, **args)
                            history.append(
                                {"role": "tool", "tool_call_id": tool_call["id"], "content": json.dumps(result)}
                            )
                        continue  # Go back to the LLM with tool results
                    else:
                        final_content = response.get("content", "Error: No content.")
                        future.set_result(final_content)
                        break  # End of this turn
            except Exception as e:
                logging.exception("Error processing LLM request in worker.")
                future.set_exception(e)
            finally:
                self._queue.task_done()
