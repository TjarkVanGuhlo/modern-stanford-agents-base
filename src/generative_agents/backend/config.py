"""
Configuration for Generative Agents cognitive models.

This module defines the language models used for different cognitive functions
in the generative agents architecture, based on the paper:
"Generative Agents: Interactive Simulacra of Human Behavior" (Park et al., 2023)

Model configuration is NOT a secret - these are just configuration choices
that determine which OpenAI models to use for different cognitive tasks.

Model Selection (December 2025):
- GPT-5 family: Current flagship models (gpt-5, gpt-5-mini, gpt-5-nano)
- GPT-4o family: Scheduled for API retirement in February 2026
- text-embedding-3-large: Still the best embedding model available
"""

import os
from typing import Dict


class ModelConfig:
    """Configuration for cognitive models used by generative agents.

    Each model corresponds to a specific cognitive function:
    - PERCEIVE: Environment observation and perception
    - RETRIEVE_EMBEDDING: Memory retrieval and similarity search
    - PLAN: Action planning and decision making
    - REFLECT: Memory synthesis and reflection generation
    - EXECUTE: Action execution and task completion
    - CONVERSE: Dialogue and social interaction
    """

    # Default model configuration (balanced performance/cost)
    PERCEIVE: str = "gpt-5-mini"
    RETRIEVE_EMBEDDING: str = "text-embedding-3-large"
    PLAN: str = "gpt-5"
    REFLECT: str = "gpt-5"
    EXECUTE: str = "gpt-5-mini"
    CONVERSE: str = "gpt-5"

    @classmethod
    def from_preset(cls, preset: str = "balanced") -> "ModelConfig":
        """Create a ModelConfig from a preset configuration.

        Available presets:
        - 'performance': Maximum quality, uses gpt-5 for all tasks
        - 'balanced': Mix of gpt-5 and gpt-5-mini (default)
        - 'economy': Cost-optimized, primarily uses gpt-5-mini and gpt-5-nano

        Args:
            preset: Name of the preset configuration

        Returns:
            ModelConfig instance with the specified preset
        """
        config = cls()

        if preset == "performance":
            # Maximum quality for all cognitive functions
            config.PERCEIVE = "gpt-5"
            config.RETRIEVE_EMBEDDING = "text-embedding-3-large"
            config.PLAN = "gpt-5"
            config.REFLECT = "gpt-5"
            config.EXECUTE = "gpt-5"
            config.CONVERSE = "gpt-5"

        elif preset == "economy":
            # Cost-optimized configuration
            config.PERCEIVE = "gpt-5-nano"
            config.RETRIEVE_EMBEDDING = "text-embedding-3-small"
            config.PLAN = "gpt-5-mini"
            config.REFLECT = "gpt-5-mini"
            config.EXECUTE = "gpt-5-nano"
            config.CONVERSE = "gpt-5-mini"

        elif preset != "balanced":
            raise ValueError(
                f"Unknown preset: {preset}. Available: performance, balanced, economy"
            )

        return config

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Create a ModelConfig from environment variables.

        Allows overriding specific models via environment variables:
        - MODEL_PERCEIVE
        - MODEL_RETRIEVE_EMBEDDING
        - MODEL_PLAN
        - MODEL_REFLECT
        - MODEL_EXECUTE
        - MODEL_CONVERSE

        Also supports MODEL_PRESET to load a preset configuration.

        Returns:
            ModelConfig instance with environment overrides
        """
        # Start with preset if specified, otherwise use balanced
        preset = os.getenv("MODEL_PRESET", "balanced")
        config = cls.from_preset(preset)

        # Override individual models if specified in environment
        model_attributes = [
            "PERCEIVE",
            "RETRIEVE_EMBEDDING",
            "PLAN",
            "REFLECT",
            "EXECUTE",
            "CONVERSE",
        ]

        for attr in model_attributes:
            env_var = f"MODEL_{attr}"
            if os.getenv(env_var):
                setattr(config, attr, os.getenv(env_var))

        return config

    def get_model_for_task(self, task_type: str) -> str:
        """Get the appropriate model for a cognitive task.

        Args:
            task_type: Type of cognitive task (perceive, plan, reflect, etc.)

        Returns:
            Model name for the specified task
        """
        # Handle None and empty string by defaulting to PLAN
        if not task_type:
            return self.PLAN

        task_map = {
            "perceive": self.PERCEIVE,
            "perception": self.PERCEIVE,
            "observe": self.PERCEIVE,
            "plan": self.PLAN,
            "planning": self.PLAN,
            "reflect": self.REFLECT,
            "reflection": self.REFLECT,
            "execute": self.EXECUTE,
            "execution": self.EXECUTE,
            "converse": self.CONVERSE,
            "conversation": self.CONVERSE,
            "dialogue": self.CONVERSE,
            "embed": self.RETRIEVE_EMBEDDING,
            "embedding": self.RETRIEVE_EMBEDDING,
            "retrieve": self.RETRIEVE_EMBEDDING,
        }
        return task_map.get(task_type.lower(), self.PLAN)  # Default to PLAN model

    def to_dict(self) -> Dict[str, str]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary of model configurations
        """
        return {
            "perceive": self.PERCEIVE,
            "retrieve_embedding": self.RETRIEVE_EMBEDDING,
            "plan": self.PLAN,
            "reflect": self.REFLECT,
            "execute": self.EXECUTE,
            "converse": self.CONVERSE,
        }

    def __str__(self) -> str:
        """String representation of the configuration."""
        return (
            f"ModelConfig:\n"
            f"  PERCEIVE: {self.PERCEIVE}\n"
            f"  RETRIEVE_EMBEDDING: {self.RETRIEVE_EMBEDDING}\n"
            f"  PLAN: {self.PLAN}\n"
            f"  REFLECT: {self.REFLECT}\n"
            f"  EXECUTE: {self.EXECUTE}\n"
            f"  CONVERSE: {self.CONVERSE}"
        )


# Create global configuration instance
# This will check for MODEL_PRESET env var and individual model overrides
model_config = ModelConfig.from_env()

# Export individual models for backward compatibility
MODEL_PERCEIVE = model_config.PERCEIVE
MODEL_RETRIEVE_EMBEDDING = model_config.RETRIEVE_EMBEDDING
MODEL_PLAN = model_config.PLAN
MODEL_REFLECT = model_config.REFLECT
MODEL_EXECUTE = model_config.EXECUTE
MODEL_CONVERSE = model_config.CONVERSE
