"""Test suite for model configuration (Issue #11)."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock


class TestModelConfig:
    """Test ModelConfig class functionality."""

    def test_default_configuration(self):
        """Test that default configuration loads with balanced preset."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig()
        assert config.PERCEIVE == "gpt-4o-mini"
        assert config.RETRIEVE_EMBEDDING == "text-embedding-3-large"
        assert config.PLAN == "gpt-4o"
        assert config.REFLECT == "gpt-4o"
        assert config.EXECUTE == "gpt-4o-mini"
        assert config.CONVERSE == "gpt-4o"

    def test_performance_preset(self):
        """Test performance preset uses all high-end models."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig.from_preset("performance")
        assert config.PERCEIVE == "gpt-4o"
        assert config.RETRIEVE_EMBEDDING == "text-embedding-3-large"
        assert config.PLAN == "gpt-4o"
        assert config.REFLECT == "gpt-4o"
        assert config.EXECUTE == "gpt-4o"
        assert config.CONVERSE == "gpt-4o"

    def test_economy_preset(self):
        """Test economy preset uses cost-optimized models."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig.from_preset("economy")
        assert config.PERCEIVE == "gpt-4o-mini"
        assert config.RETRIEVE_EMBEDDING == "text-embedding-3-small"
        assert config.PLAN == "gpt-4o-mini"
        assert config.REFLECT == "gpt-4o"  # Should remain high quality
        assert config.EXECUTE == "gpt-4o-mini"
        assert config.CONVERSE == "gpt-4o-mini"

    def test_balanced_preset(self):
        """Test balanced preset (default configuration)."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig.from_preset("balanced")
        assert config.PERCEIVE == "gpt-4o-mini"
        assert config.PLAN == "gpt-4o"
        assert config.REFLECT == "gpt-4o"
        assert config.EXECUTE == "gpt-4o-mini"

    def test_invalid_preset_raises_error(self):
        """Test that invalid preset name raises ValueError."""
        from generative_agents.backend.config import ModelConfig

        with pytest.raises(ValueError, match="Unknown preset"):
            ModelConfig.from_preset("invalid_preset")

    def test_env_preset_override(self):
        """Test loading configuration from MODEL_PRESET env var."""
        from generative_agents.backend.config import ModelConfig

        with patch.dict(os.environ, {"MODEL_PRESET": "performance"}):
            config = ModelConfig.from_env()
            assert config.PERCEIVE == "gpt-4o"
            assert config.EXECUTE == "gpt-4o"

    def test_invalid_preset_env_var(self):
        """Test that invalid MODEL_PRESET raises an error."""
        from generative_agents.backend.config import ModelConfig

        with patch.dict(os.environ, {"MODEL_PRESET": "invalid_preset"}):
            with pytest.raises(ValueError, match="Unknown preset"):
                ModelConfig.from_env()

    def test_individual_env_override(self):
        """Test individual model override via environment variables."""
        from generative_agents.backend.config import ModelConfig

        env_vars = {
            "MODEL_PRESET": "economy",
            "MODEL_PLAN": "gpt-3.5-turbo",
            "MODEL_PERCEIVE": "gpt-4-turbo"
        }

        with patch.dict(os.environ, env_vars):
            config = ModelConfig.from_env()
            assert config.PLAN == "gpt-3.5-turbo"  # Overridden
            assert config.PERCEIVE == "gpt-4-turbo"  # Overridden
            assert config.EXECUTE == "gpt-4o-mini"  # From economy preset

    def test_get_model_for_task(self):
        """Test task-to-model mapping."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig()

        # Test various task names
        assert config.get_model_for_task("perceive") == config.PERCEIVE
        assert config.get_model_for_task("perception") == config.PERCEIVE
        assert config.get_model_for_task("plan") == config.PLAN
        assert config.get_model_for_task("planning") == config.PLAN
        assert config.get_model_for_task("reflect") == config.REFLECT
        assert config.get_model_for_task("converse") == config.CONVERSE
        assert config.get_model_for_task("dialogue") == config.CONVERSE
        assert config.get_model_for_task("embed") == config.RETRIEVE_EMBEDDING

        # Test default fallback
        assert config.get_model_for_task("unknown") == config.PLAN

    def test_get_model_for_task_edge_cases(self):
        """Test edge cases for get_model_for_task."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig()

        # Test empty string - should default to PLAN
        assert config.get_model_for_task("") == config.PLAN

        # Test None - should default to PLAN
        assert config.get_model_for_task(None) == config.PLAN

        # Test case insensitivity
        assert config.get_model_for_task("PERCEIVE") == config.PERCEIVE
        assert config.get_model_for_task("PlAn") == config.PLAN

    def test_to_dict(self):
        """Test conversion to dictionary."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["perceive"] == config.PERCEIVE
        assert config_dict["plan"] == config.PLAN
        assert config_dict["reflect"] == config.REFLECT
        assert len(config_dict) == 6  # All 6 cognitive functions

    def test_string_representation(self):
        """Test string representation of config."""
        from generative_agents.backend.config import ModelConfig

        config = ModelConfig()
        str_repr = str(config)

        assert "ModelConfig:" in str_repr
        assert "PERCEIVE:" in str_repr
        assert "PLAN:" in str_repr
        assert "gpt-4o" in str_repr


class TestUtilsIntegration:
    """Test utils module integration with config."""

    def test_utils_imports_from_config(self):
        """Test that utils correctly imports models from config."""
        # Mock the required environment variables
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "KEY_OWNER": "test-owner"}):
            import importlib
            import generative_agents.backend.utils as utils
            importlib.reload(utils)

            from generative_agents.backend.utils import (
                MODEL_PERCEIVE,
                MODEL_RETRIEVE_EMBEDDING,
                MODEL_PLAN,
                MODEL_REFLECT,
                MODEL_EXECUTE,
                MODEL_CONVERSE,
                model_config
            )

            # Check that models are imported
            assert MODEL_PERCEIVE is not None
            assert MODEL_PLAN is not None
            assert MODEL_REFLECT is not None

            # Check that model_config is available
            assert model_config is not None
            assert hasattr(model_config, 'get_model_for_task')

    def test_utils_backward_compatibility(self):
        """Test backward compatibility with existing code."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "KEY_OWNER": "test-owner"}):
            import importlib
            import generative_agents.backend.utils as utils
            importlib.reload(utils)

            from generative_agents.backend.utils import MODEL_PLAN, MODEL_REFLECT, MODEL_RETRIEVE_EMBEDDING

            # These should still be strings (model names)
            assert isinstance(MODEL_PLAN, str)
            assert isinstance(MODEL_REFLECT, str)
            assert isinstance(MODEL_RETRIEVE_EMBEDDING, str)


@pytest.fixture
def clean_modules():
    """Clean up module imports for testing."""
    modules = [
        'generative_agents.backend.utils',
        'generative_agents.backend.persona.prompt_template.gpt_structure',
        'generative_agents.backend.config',
    ]
    for module in modules:
        sys.modules.pop(module, None)
    yield
    for module in modules:
        sys.modules.pop(module, None)


class TestGPTStructureIntegration:
    """Test gpt_structure module integration."""

    def test_gpt_structure_imports_all_models(self, clean_modules):
        """Test that gpt_structure imports all 6 cognitive models."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "KEY_OWNER": "test-owner"}):

            from generative_agents.backend.persona.prompt_template.gpt_structure import (
                MODEL_PERCEIVE,
                MODEL_RETRIEVE_EMBEDDING,
                MODEL_PLAN,
                MODEL_REFLECT,
                MODEL_EXECUTE,
                MODEL_CONVERSE,
                model_config
            )

            # Verify all models are imported and are strings
            assert isinstance(MODEL_PERCEIVE, str)
            assert isinstance(MODEL_RETRIEVE_EMBEDDING, str)
            assert isinstance(MODEL_PLAN, str)
            assert isinstance(MODEL_REFLECT, str)
            assert isinstance(MODEL_EXECUTE, str)
            assert isinstance(MODEL_CONVERSE, str)

            # Verify model_config is available
            assert model_config is not None

    def test_gpt_functions_use_correct_models(self, clean_modules):
        """Test that GPT functions use the appropriate cognitive models."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "KEY_OWNER": "test-owner"}):

            from generative_agents.backend.persona.prompt_template.gpt_structure import (
                MODEL_PLAN,
                MODEL_REFLECT,
                MODEL_RETRIEVE_EMBEDDING,
            )
            import generative_agents.backend.persona.prompt_template.gpt_structure as gpt_structure

            # Check that functions reference the correct models
            # This verifies the models are available for use in the functions
            assert hasattr(gpt_structure, 'ChatGPT_request')
            assert hasattr(gpt_structure, 'GPT4_request')
            assert hasattr(gpt_structure, 'get_embedding')

            # Verify models are the expected values (from default config)
            assert MODEL_PLAN == "gpt-4o"
            assert MODEL_REFLECT == "gpt-4o"


class TestEnvironmentOverrides:
    """Test environment-based configuration overrides."""

    def test_full_env_configuration(self):
        """Test complete configuration via environment variables."""
        env_vars = {
            "MODEL_PRESET": "performance",
            "MODEL_PLAN": "custom-plan-model",
            "MODEL_REFLECT": "custom-reflect-model",
            "MODEL_PERCEIVE": "custom-perceive-model",
            "MODEL_EXECUTE": "custom-execute-model",
            "MODEL_CONVERSE": "custom-converse-model",
            "MODEL_RETRIEVE_EMBEDDING": "custom-embedding-model"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Need to reimport to get fresh config with env vars
            import importlib
            import generative_agents.backend.config as config
            importlib.reload(config)

            from generative_agents.backend.config import model_config

            assert model_config.PLAN == "custom-plan-model"
            assert model_config.REFLECT == "custom-reflect-model"
            assert model_config.PERCEIVE == "custom-perceive-model"
            assert model_config.EXECUTE == "custom-execute-model"
            assert model_config.CONVERSE == "custom-converse-model"
            assert model_config.RETRIEVE_EMBEDDING == "custom-embedding-model"

    def test_partial_env_override(self):
        """Test partial override leaves other models unchanged."""
        with patch.dict(os.environ, {"MODEL_PLAN": "gpt-3.5-turbo"}):
            import importlib
            import generative_agents.backend.config as config
            importlib.reload(config)

            from generative_agents.backend.config import model_config

            assert model_config.PLAN == "gpt-3.5-turbo"
            assert model_config.REFLECT == "gpt-4o"  # Unchanged from default
