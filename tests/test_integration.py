"""Integration test to verify the models work with actual simulation code."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add paths for imports
sys.path.insert(0, 'reverie/backend_server')
sys.path.insert(0, 'reverie/backend_server/persona/prompt_template')


@pytest.fixture
def mock_env():
    """Set up mock environment variables."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "KEY_OWNER": "test-owner"
    }):
        yield


def test_gpt_structure_functions_use_configured_models(mock_env):
    """Test that GPT functions actually use the configured models."""
    from gpt_structure import ChatGPT_request, GPT4_request, get_embedding
    from gpt_structure import MODEL_PLAN, MODEL_REFLECT, MODEL_RETRIEVE_EMBEDDING

    # Mock the OpenAI client
    with patch('gpt_structure.client') as mock_client:
        # Setup mock responses
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="test response"))]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test ChatGPT_request uses MODEL_PLAN
        result = ChatGPT_request("test prompt")
        mock_client.chat.completions.create.assert_called_with(
            model=MODEL_PLAN,
            messages=[{"role": "user", "content": "test prompt"}]
        )
        assert result == "test response"

        # Test GPT4_request uses MODEL_REFLECT
        result = GPT4_request("test prompt")
        mock_client.chat.completions.create.assert_called_with(
            model=MODEL_REFLECT,
            messages=[{"role": "user", "content": "test prompt"}]
        )
        assert result == "test response"

        # Test get_embedding uses MODEL_RETRIEVE_EMBEDDING
        mock_embedding = MagicMock()
        mock_embedding.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_embedding

        result = get_embedding("test text")
        mock_client.embeddings.create.assert_called_with(
            input=["test text"],
            model=MODEL_RETRIEVE_EMBEDDING
        )
        assert result == [0.1, 0.2, 0.3]


@pytest.fixture
def clean_imports():
    """Clean up imports before and after test."""
    modules_to_clean = ['config', 'utils', 'gpt_structure']
    # Clean before test
    for module in modules_to_clean:
        sys.modules.pop(module, None)
    yield
    # Clean after test
    for module in modules_to_clean:
        sys.modules.pop(module, None)


def test_model_preset_configuration(clean_imports):
    """Test that MODEL_PRESET environment variable is respected on fresh import."""
    # This test verifies that if you start the application with MODEL_PRESET set,
    # it will use the correct preset. In production, you'd restart the server.

    # Set economy preset BEFORE importing
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "KEY_OWNER": "test-owner",
        "MODEL_PRESET": "economy"
    }, clear=True):
        # Now import with economy preset
        from config import model_config

        # Verify economy models are loaded
        assert model_config.PLAN == "gpt-4o-mini"  # Economy uses gpt-4o-mini for planning
        assert model_config.RETRIEVE_EMBEDDING == "text-embedding-3-small"  # Economy uses small embeddings
        assert model_config.REFLECT == "gpt-4o"  # Even economy keeps reflection high quality