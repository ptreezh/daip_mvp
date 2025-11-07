import pytest

from daip_live.core.interfaces import IKnowledgeManager, IModelProvider, ITool


def test_cannot_instantiate_incomplete_model_provider():
    """Tests that an incomplete implementation of IModelProvider raises TypeError."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        class IncompleteProvider(IModelProvider):
            # Missing the 'embed' method
            async def generate(self, prompt: str, params: dict):
                yield "token"

        IncompleteProvider() # This should fail


def test_cannot_instantiate_incomplete_knowledge_manager():
    """Tests that an incomplete implementation of IKnowledgeManager raises TypeError."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        class IncompleteManager(IKnowledgeManager):
            # Missing the 'sync_knowledge_base' method
            def search(self, query_text: str, top_k: int):
                return []

        IncompleteManager() # This should fail


def test_cannot_instantiate_incomplete_tool():
    """Tests that an incomplete implementation of ITool raises TypeError."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        class IncompleteTool(ITool):
            # Missing name and description properties
            def execute(self, **kwargs):
                return "executed"

        IncompleteTool() # This should fail
