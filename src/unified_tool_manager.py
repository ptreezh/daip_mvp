import logging
from typing import Any

logger = logging.getLogger(__name__)

class UnifiedToolManager:
    """Unified tool manager for registering, managing, and executing various tools.
    This class is responsible for registering, managing, and executing various tools
    based on a provided configuration.
    """
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.available_tools = {}
        self._register_tools()
        logger.info("UnifiedToolManager initialized.")

    def _register_tools(self):
        """Registers tools based on the provided configuration.
        In a real scenario, this would dynamically load tool implementations.
        """
        for tool_name, tool_info in self.config.items():
            self.available_tools[tool_name] = tool_info
            logger.debug(f"Registered tool: {tool_name}")

    def get_tool(self, tool_name: str) -> Any:
        """Retrieves a registered tool."""
        return self.available_tools.get(tool_name)

    def register_tool(self, tool_name: str, tool_class: Any, description: str = None):
        """Registers a new tool with the manager.
        
        Args:
            tool_name: The name of the tool
            tool_class: The class or function implementing the tool
            description: Optional description of the tool
        """
        self.available_tools[tool_name] = {
            "type": "custom_tool",
            "class": tool_class,
            "description": description or f"Tool: {tool_name}"
        }
        logger.info(f"Registered tool: {tool_name}")
        return True

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Executes a registered tool. Supports both synchronous and asynchronous tools.
        
        Args:
            tool_name: The name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            The result of the tool execution
        """
        if tool_name not in self.available_tools:
            logger.warning(f"Tool '{tool_name}' not found.")
            return None
            
        logger.info(f"Executing tool: {tool_name} with args: {kwargs}")
        
        tool_info = self.available_tools[tool_name]
        tool_class = tool_info.get("class")
        
        if not tool_class:
            logger.error(f"Tool '{tool_name}' has no implementation class.")
            return None
            
        try:
            # If it's a class, instantiate it with kwargs and call execute
            if isinstance(tool_class, type):
                tool_instance = tool_class(**kwargs)
                
                # Check if execute method is async
                import inspect
                if hasattr(tool_instance, 'execute'):
                    if inspect.iscoroutinefunction(tool_instance.execute):
                        return await tool_instance.execute()
                    else:
                        return tool_instance.execute()
                else:
                    logger.error(f"Tool instance for '{tool_name}' has no execute method.")
                    return None
            # If it's a function, call it directly with kwargs
            else:
                if inspect.iscoroutinefunction(tool_class):
                    return await tool_class(**kwargs)
                else:
                    return tool_class(**kwargs)
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return {"error": str(e)}

    def register_strategies_from_factory(self, consensus_factory):
        """Registers consensus strategies from a factory as available tools.
        
        Args:
            consensus_factory: A ConsensusStrategyFactory instance containing registered strategies
        """
        try:
            strategies = consensus_factory.get_all_strategies()
            for strategy_name, strategy_class in strategies.items():
                self.register_tool(
                    f"consensus.{strategy_name}",
                    strategy_class,
                    description=f"{strategy_name.replace('_', ' ').title()} consensus strategy"
                )
        except Exception as e:
            logger.error(f"Failed to register strategies from factory: {e}")
            # Don't fail the startup, just log the error
