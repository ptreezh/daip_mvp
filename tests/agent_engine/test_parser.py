# tests/agent_engine/test_parser.py

import pytest
from typing import Dict, Any, Optional, Tuple

# We need to import the class to test its method
from daip_live.agent_engine.step_executor import StepExecutor

# A dummy StepExecutor instance to call the method on.
# We don't need its dependencies for this static method test.
dummy_executor = StepExecutor(None, None, None, None, None)

def test_vanilla_parse_tool_call():
    """
    A simple, synchronous, isolated test for the _parse_tool_call method.
    This test has no dependencies on fixtures or mocks.
    """
    text_to_parse = "Use Tool: search_web(query='test')"
    
    # Directly call the method we want to test
    result: Optional[Tuple[str, Dict[str, Any]]] = dummy_executor._parse_tool_call(text_to_parse)
    
    # Assertions
    assert result is not None, "The parser should not return None for a valid tool call string."
    
    tool_name, args = result
    assert tool_name == "search_web"
    assert isinstance(args, dict)
    assert args == {"query": "test"}
