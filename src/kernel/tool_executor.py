import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List

# To avoid circular imports, use a type-checking block
if TYPE_CHECKING:
    from src.protocols.consensus_strategies import (
        ConsensusStrategyFactory,
    )

class ToolExecutor:
    """
    Manages the registration and execution of tools.

    This class provides a registry for tools, allowing them to be dynamically
    added and executed in a safe manner. It is designed to integrate with
    LLMs that support function calling by providing tool definitions and
    a secure execution entry point.
    """

    def __init__(self) -> None:
        """Initializes the ToolExecutor with empty registries."""
        self._tools: Dict[str, Callable] = {}
        self._tool_definitions: Dict[str, Dict[str, Any]] = {}
        logging.info("ToolExecutor initialized.")

    def register_tool(self, func: Callable, definition: Dict[str, Any]) -> None:
        """
        Registers a tool, making it available for execution.

        Args:
            func (Callable): The function to be executed for the tool.
            definition (Dict[str, Any]): The JSON Schema definition of the tool,
                                         as expected by the LLM.

        Raises:
            ValueError: If the tool definition is invalid or the name is missing.
        """
        try:
            tool_name = definition["function"]["name"]
        except (KeyError, TypeError):
            raise ValueError(
                "Invalid tool definition: must be a dictionary with a 'function' key, which contains a 'name' key."
            )

        if tool_name in self._tools:
            logging.warning(
                f"Tool '{tool_name}' is already registered. It will be overwritten."
            )

        self._tools[tool_name] = func
        self._tool_definitions[tool_name] = definition
        logging.info(f"Tool '{tool_name}' registered successfully.")

    def register_strategies_from_factory(
        self, factory: "ConsensusStrategyFactory"
    ) -> None:
        """
        Registers all consensus strategies from a factory as callable tools.

        Args:
            factory (ConsensusStrategyFactory): The factory containing the strategies.
        """
        logging.info("Registering consensus strategies from factory...")
        strategies = factory.get_all_strategies()
        for name, strategy_class in strategies.items():
            instance = strategy_class()
            # The tool definition is for LLM consumption, describing how to call it.
            definition = {
                "function": {
                    "name": name,
                    "description": (
                        strategy_class.__doc__
                        or f"Executes the {name} consensus strategy."
                    ).strip(),
                    "parameters": {
                        "type": "object",
                        "properties": {"history": {"type": "array"}},
                        "required": ["history"],
                    },
                }
            }
            self.register_tool(instance.execute, definition)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Retrieves the list of all registered tool definitions.

        This list can be directly passed to an LLM that supports native
        function calling.

        Returns:
            List[Dict[str, Any]]: A list of tool definitions.
        """
        return list(self._tool_definitions.values())

    def execute(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Executes a registered tool by its name.

        This method safely looks up the tool and calls it with the provided
        arguments, capturing any exceptions that occur during execution.

        Args:
            tool_name (str): The name of the tool to execute.
            **kwargs (Any): The arguments to pass to the tool's function.

        Returns:
            Dict[str, Any]: A dictionary containing the execution status
                            ('success' or 'error') and the result or an
                            error message.
        """
        logging.info(f"Attempting to execute tool: '{tool_name}' with args: {kwargs}")
        tool_func = self._tools.get(tool_name)

        if not tool_func:
            error_msg = f"Tool '{tool_name}' not found."
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}

        try:
            result = tool_func(**kwargs)
            logging.info(f"Tool '{tool_name}' executed successfully.")
            return {"status": "success", "result": result}
        except Exception as e:
            error_msg = f"An error occurred while executing tool '{tool_name}': {e}"
            logging.exception(error_msg)  # Logs the full traceback
            return {"status": "error", "message": error_msg}
