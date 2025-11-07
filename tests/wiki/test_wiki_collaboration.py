
import pytest

import os

import shutil

from pathlib import Path

from unittest.mock import MagicMock, AsyncMock



from daip_live.wiki.manager import WikiManager

from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

from daip_live.p4_role_manager_tools.role_model_config import RoleModelMapping, RoleModelConfig

from daip_live.model_provider.provider import LiteLLMProvider



@pytest.fixture

def wiki_test_env():

    """Pytest fixture to set up a test environment for the WikiManager."""

    test_dir = Path(__file__).parent / "temp_wiki"

    if test_dir.exists():

        shutil.rmtree(test_dir)

    test_dir.mkdir()



    # Mock dependencies

    mock_role_model_manager = MagicMock(spec=RoleModelManager)

    mock_model_provider = MagicMock(spec=LiteLLMProvider)



    # Instantiate WikiManager and inject mocks

    wiki_manager = WikiManager(

        wiki_root=test_dir,

        role_model_manager=mock_role_model_manager,

        model_provider=mock_model_provider

    )

    

    # Yield the manager and mocks to the test

    yield wiki_manager, mock_role_model_manager, mock_model_provider

    

    # Teardown: clean up the directory

    if test_dir.exists():

        shutil.rmtree(test_dir)



@pytest.mark.asyncio

async def test_add_content_by_role_uses_role_specific_models(wiki_test_env):

    """

    [GREEN] Test that add_content_by_role calls the model provider with the

    correct model for each respective role.

    """

    # --- Arrange ---

    wiki_manager, mock_role_model_manager, mock_model_provider = wiki_test_env

    page_title = "Test Page"

    wiki_manager.create_page(page_title, "Initial content.")



    # Configure mock RoleModelManager to return different models for different roles

    role_a_config = RoleModelConfig(model_name="model-for-role-a", provider="ollama")

    role_b_config = RoleModelConfig(model_name="model-for-role-b", provider="ollama")



    mock_role_model_manager.get_role_model_mapping.side_effect = [

        RoleModelMapping(role_name="role_A", role_model_config=role_a_config),

        RoleModelMapping(role_name="role_B", role_model_config=role_b_config)

    ]



    # Configure the mock model provider to return some content

    mock_model_provider.generate = AsyncMock(return_value=("Generated content.", {}))



    # --- Act ---

    # Simulate two different roles contributing to the page, now correctly awaited

    await wiki_manager.add_content_by_role(page_title, "role_A", "Write about topic A.")

    await wiki_manager.add_content_by_role(page_title, "role_B", "Write about topic B.")



    # --- Assert ---

    # This assertion will FAIL because the placeholder method doesn't call the provider.

    # Our goal in the GREEN phase is to make this pass.

    assert mock_model_provider.generate.call_count == 2



    # Check that the generate method was called with the correct model for each role

    calls = mock_model_provider.generate.call_args_list

    

    # Check call for role_A

    # The call object is a tuple (args, kwargs). We check the kwargs for 'model'.

    assert calls[0].kwargs['model'] == 'model-for-role-a'

    

    # Check call for role_B

    assert calls[1].kwargs['model'] == 'model-for-role-b'


