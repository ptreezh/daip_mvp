import asyncio
import re
import ast
from typing import Any, Dict, List, Tuple, Optional, AsyncGenerator

from src.daip_live.memory.session_manager import SessionManager
from src.daip_live.memory.service import MemoryService
from src.daip_live.core.models import (
    AgentState, AgentEvent, ThoughtEvent, ToolCallEvent, ToolOutputEvent,
    FinalResponseEvent, ErrorEvent, SessionContext, DialogueTurn, Session, AgentStatus
)


class AgentExecutor:
    TOOL_CALL_PATTERN = re.compile(r"Use Tool:\s*(\w+)\s*\((.*)\)")
    CONFIDENCE_PATTERN = re.compile(r"Confidence: (\d\.\d+)")

    def __init__(
        self,
        session_manager: SessionManager,
        memory_service: MemoryService,
        knowledge_manager: Any,
        model_provider: Any,
        tool_manager: Any,
        user_input_queue: asyncio.Queue,
        max_reflections: int = 3,
    ):
        self.session_manager = session_manager
        self.memory_service = memory_service
        self.knowledge_manager = knowledge_manager
        self.model_provider = model_provider
        self.tool_manager = tool_manager
        self.user_input_queue = user_input_queue
        self.max_reflections = max_reflections
        
        self.state: AgentState = AgentState.IDLE
        self.session: Optional[Session] = None
        self.llm_response: str = ""
        self.last_tool_result: Optional[str] = None
        self.last_final_response: Optional[FinalResponseEvent] = None
        self.reflection_count: int = 0
        self.session_context = SessionContext()
        self.tokens_used: int = 0
        self.tokens_total: int = 8192 # Default, should be updated based on model

    def get_status(self) -> AgentStatus:
        """Returns a snapshot of the agent's current state."""
        return AgentStatus(
            state=self.state,
            model_name=self.model_provider.config.model,
            tokens_used=self.tokens_used,
            tokens_total=self.tokens_total,
        )

    async def run(self, goal: str) -> AsyncGenerator[AgentEvent, None]:
        """Main execution loop, driven by a Todo list and delegating steps to _execute_step."""
        self.session = self.session_manager.create_session(
            goal=goal, session_type="workflow", participant_ids=["agent", "system", "user"]
        )
        self._change_state(AgentState.RUNNING)
        self.session.status = self.state

        todo_list = await self.memory_service.get_todo_list()
        current_task_index = 0
        self.last_final_response = None

        try:
            while not await self.memory_service.is_todo_list_complete():
                # --- Outer loop: Get next task and delegate execution ---
                current_task = todo_list[current_task_index]
                
                # Reset context for the new step
                self.llm_response = ""
                self.last_tool_result = None
                self._change_state(AgentState.THINKING)

                # Delegate the entire step execution to the helper method
                async for event in self._execute_step(current_task):
                    yield event

                if self.state == AgentState.FAILED:
                    break # Exit outer loop on failure

                await self.memory_service.update_todo_status(current_task_index)
                current_task_index += 1

            if self.state != AgentState.FAILED:
                self._change_state(AgentState.COMPLETED)
                if not self.last_final_response:
                     yield FinalResponseEvent(content="Plan completed successfully.")

        finally:
            if self.session:
                self.session.status = self.state
                self.session_manager.save_session(self.session)
                yield ThoughtEvent(content=f"Session {self.session.session_id} saved with status {self.state.name}.")

    async def _execute_step(self, current_task: Any) -> AsyncGenerator[AgentEvent, None]:
        """Executes a single step from the Todo list using a state machine."""
        step_completed = False

        while not step_completed:
            # 1. OBSERVE & STEER
            try:
                user_command = self.user_input_queue.get_nowait()
                yield ThoughtEvent(content=f"Received steering command: {user_command}")
                self.session.history.append(DialogueTurn(participant_id="user", content=user_command))
                self.last_tool_result = f"User steering command: {user_command}"
                self.user_input_queue.task_done()
                self._change_state(AgentState.THINKING) # Force re-thinking
            except asyncio.QueueEmpty:
                pass # No user command

            # 2. ACT based on current state
            if self.state == AgentState.THINKING:
                yield ThoughtEvent(content=f"Thinking about task: {current_task.description}")
                prompt = await self.memory_service.construct_prompt(
                    current_task.description, self.last_tool_result, self.llm_response
                )
                self.llm_response, usage = await self.model_provider.generate(prompt)
                if usage:
                    self.tokens_used += usage.total_tokens
                self.session.history.append(DialogueTurn(participant_id="agent", content=self.llm_response))
                self._change_state(AgentState.EVALUATING)

            elif self.state == AgentState.EVALUATING:
                confidence_match = self.CONFIDENCE_PATTERN.search(self.llm_response)
                confidence = float(confidence_match.group(1)) if confidence_match else 1.0

                if confidence < 0.7 and self.reflection_count < self.max_reflections:
                    self.reflection_count += 1
                    yield ThoughtEvent(content=f"Confidence is low ({confidence}). Reflecting... ({self.reflection_count}/{self.max_reflections})")
                    self.last_tool_result = f"Self-reflection: The previous response had low confidence ({confidence}). I need to reconsider my approach to be more certain."
                    self._change_state(AgentState.THINKING)
                else:
                    tool_call = self._parse_tool_call(self.llm_response)
                    if tool_call:
                        self._change_state(AgentState.EXECUTING_TOOL)
                    else:
                        self._change_state(AgentState.RESPONDING)

            elif self.state == AgentState.EXECUTING_TOOL:
                tool_name, tool_args = self._parse_tool_call(self.llm_response)
                yield ToolCallEvent(tool_name=tool_name, args=tool_args)
                try:
                    self.last_tool_result = self.tool_manager.execute_tool(
                        tool_name, tool_args, session_context=self.session_context
                    )
                    yield ToolOutputEvent(tool_name=tool_name, status="success", output=self.last_tool_result)
                    self._change_state(AgentState.THINKING) # Re-think after getting tool result
                except ToolError as e:
                    self.last_tool_result = f"Error: {e}"
                    yield ToolOutputEvent(tool_name=tool_name, status="error", output=self.last_tool_result)
                    self._change_state(AgentState.FAILED)
                    step_completed = True # Break inner loop on error

            elif self.state == AgentState.RESPONDING:
                final_answer = self.CONFIDENCE_PATTERN.sub("", self.llm_response).strip()
                final_answer = self.TOOL_CALL_PATTERN.sub("", final_answer).strip()
                self.last_final_response = FinalResponseEvent(content=final_answer)
                yield self.last_final_response
                step_completed = True # This step is done

    def _change_state(self, new_state: AgentState):
        self.state = new_state

    def _parse_tool_call(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        match = self.TOOL_CALL_PATTERN.search(text)
        if not match: return None
        tool_name, args_str = match.groups()
        try:
            # A slightly more robust arg parser
            args = dict(re.findall(r'(\w+)=([^,)]+)', args_str))
            for key, value in args.items():
                try:
                    args[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    args[key] = value # Keep as string if it's not a literal
            return tool_name, args
        except Exception: return None
