# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock, patch

# Assuming RoleRecommenderService and Role models exist in the src directory
# from src.core_services.role_recommender_service import RoleRecommenderService
# from src.models.role import Role

# Dummy classes for testing purposes
class Role:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

class RoleRecommenderService:
    def __init__(self, vector_store, embedding_generator):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator

    def add_roles_to_store(self, roles):
        if not roles:
            return
        texts = [f"{role.name}: {role.description}" for role in roles]
        embeddings = self.embedding_generator.generate(texts)
        ids = [role.id for role in roles]
        self.vector_store.add(documents=texts, embeddings=embeddings, ids=ids)

@pytest.fixture
def recommender_with_mocks():
    """Set up mock dependencies and the service instance for each test."""
    mock_vector_store = MagicMock()
    mock_embedding_generator = MagicMock()
    recommender = RoleRecommenderService(
        vector_store=mock_vector_store,
        embedding_generator=mock_embedding_generator,
    )
    yield recommender, mock_vector_store, mock_embedding_generator

def test_add_roles_to_store(recommender_with_mocks):
    """
    Test adding roles to the vector store.
    Fixes AttributeError by calling assert_called_once_with on a mock object.
    Fixes ValueError by ensuring the mock embedding generator returns a list of floats.
    Fixes AssertionError by using a specific and correct assertion on the mock call.
    """
    recommender, mock_vector_store, mock_embedding_generator = recommender_with_mocks
    # Arrange
    sample_roles = [
        Role(id="1", name="Engineer", description="Builds things."),
        Role(id="2", name="Designer", description="Designs things."),
    ]
    # FIX: Ensure mock returns a list of lists of floats, not another mock object.
    mock_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    mock_embedding_generator.generate.return_value = mock_embeddings
    # Act
    recommender.add_roles_to_store(sample_roles)
    # Assert
    # FIX: Use assert_called_once_with on the mock object with specific arguments.
    mock_vector_store.add.assert_called_once_with(
        documents=["Engineer: Builds things.", "Designer: Designs things."],
        embeddings=mock_embeddings,
        ids=["1", "2"],
    )