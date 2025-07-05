import logging
import unittest

from src.kernel.tool_executor import ToolExecutor


# Dummy functions to be used as tools
def get_weather(location: str, unit: str = "celsius") -> str:
    """A dummy function to get weather."""
    return f"The weather in {location} is 25 degrees {unit}."


def calculator(a: int, b: int) -> int:
    """A dummy calculator that only adds."""
    return a + b


def tool_that_fails():
    """A dummy tool that always raises an exception."""
    raise ValueError("This tool failed intentionally.")


# Dummy tool definitions matching the function calling spec
GET_WEATHER_DEF = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather in a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },
}

CALCULATOR_DEF = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "A simple calculator.",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
    },
}

FAILING_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "tool_that_fails",
        "description": "A tool designed to fail.",
        "parameters": {"type": "object", "properties": {}},
    },
}


class TestToolExecutor(unittest.TestCase):
    def setUp(self):
        """Set up a new ToolExecutor for each test."""
        self.executor = ToolExecutor()
        # Suppress logging output during tests to keep the test output clean
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Re-enable logging after tests."""
        logging.disable(logging.NOTSET)

    def test_initialization(self):
        """Tests that the executor initializes with empty registries."""
        self.assertEqual(self.executor.get_tool_definitions(), [])
        self.assertEqual(self.executor._tools, {})

    def test_register_tool_successfully(self):
        """Tests that a tool can be registered correctly."""
        self.executor.register_tool(get_weather, GET_WEATHER_DEF)
        self.assertIn("get_weather", self.executor._tools)
        self.assertEqual(len(self.executor.get_tool_definitions()), 1)
        self.assertEqual(self.executor.get_tool_definitions()[0], GET_WEATHER_DEF)

    def test_register_tool_with_invalid_definition(self):
        """Tests that registering with a malformed definition raises ValueError."""
        with self.assertRaises(ValueError):
            self.executor.register_tool(get_weather, {"invalid": "definition"})

    def test_register_tool_overwrite_warning(self):
        """Tests that re-registering a tool logs a warning."""
        self.executor.register_tool(get_weather, GET_WEATHER_DEF)
        with self.assertLogs("root", level="WARNING"):
            self.executor.register_tool(calculator, GET_WEATHER_DEF)  # Using same name
        self.assertEqual(self.executor._tools["get_weather"], calculator)

    def test_get_tool_definitions(self):
        """Tests retrieval of tool definitions."""
        self.executor.register_tool(get_weather, GET_WEATHER_DEF)
        self.executor.register_tool(calculator, CALCULATOR_DEF)
        definitions = self.executor.get_tool_definitions()
        self.assertEqual(len(definitions), 2)
        self.assertIn(GET_WEATHER_DEF, definitions)
        self.assertIn(CALCULATOR_DEF, definitions)

    def test_execute_tool_successfully(self):
        """Tests successful execution of a registered tool."""
        self.executor.register_tool(get_weather, GET_WEATHER_DEF)
        result = self.executor.execute("get_weather", location="London")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "The weather in London is 25 degrees celsius.")

    def test_execute_nonexistent_tool(self):
        """Tests executing a tool that has not been registered."""
        result = self.executor.execute("nonexistent_tool")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])

    def test_execute_tool_that_raises_exception(self):
        """Tests that exceptions during tool execution are caught and reported."""
        self.executor.register_tool(tool_that_fails, FAILING_TOOL_DEF)
        result = self.executor.execute("tool_that_fails")
        self.assertEqual(result["status"], "error")
        self.assertIn("This tool failed intentionally.", result["message"])


if __name__ == "__main__":
    unittest.main()