"""
Unit tests for configuration module.
"""

import pytest
import os
from pathlib import Path


def test_api_keys_loaded(all_api_keys):
    """Test that API keys are properly loaded from environment."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        OPENAI_API_KEY,
        ANTHROPIC_API_KEY,
        GEMINI_API_KEY,
    )

    assert OPENAI_API_KEY == all_api_keys["OPENAI_API_KEY"]
    assert ANTHROPIC_API_KEY == all_api_keys["ANTHROPIC_API_KEY"]
    assert GEMINI_API_KEY == all_api_keys["GEMINI_API_KEY"]


def test_model_configurations():
    """Test that model configurations are properly set."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        REALTIME_MODEL_DEFAULT,
        REALTIME_MODEL_MINI,
        GEMINI_MODEL,
        DEFAULT_CLAUDE_MODEL,
    )

    assert isinstance(REALTIME_MODEL_DEFAULT, str)
    assert isinstance(REALTIME_MODEL_MINI, str)
    assert isinstance(GEMINI_MODEL, str)
    assert isinstance(DEFAULT_CLAUDE_MODEL, str)

    assert "gpt" in REALTIME_MODEL_DEFAULT.lower()
    assert "gemini" in GEMINI_MODEL.lower()
    assert "claude" in DEFAULT_CLAUDE_MODEL.lower()


def test_directory_paths():
    """Test that directory paths are properly configured."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        BASE_DIR,
        AGENT_WORKING_DIRECTORY,
        PROMPTS_DIR,
    )

    assert isinstance(BASE_DIR, Path)
    assert isinstance(AGENT_WORKING_DIRECTORY, Path)
    assert isinstance(PROMPTS_DIR, Path)

    assert BASE_DIR.exists()


def test_screen_dimensions():
    """Test screen dimensions are valid."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
    )

    assert isinstance(SCREEN_WIDTH, int)
    assert isinstance(SCREEN_HEIGHT, int)
    assert SCREEN_WIDTH > 0
    assert SCREEN_HEIGHT > 0


def test_claude_mode_detection():
    """Test Claude mode detection logic."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        get_claude_mode,
        is_api_mode,
        is_max_mode,
    )

    mode = get_claude_mode()
    assert mode in ["auto", "api", "max"]

    # Test mode checking functions
    assert isinstance(is_api_mode(), bool)
    assert isinstance(is_max_mode(), bool)


def test_feature_flags():
    """Test advanced feature flags."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        ENABLE_AGENT_POOL,
        ENABLE_WORKFLOW,
        ENABLE_MEMORY,
        ENABLE_LEARNING,
        ENABLE_SECURITY,
    )

    # All should be boolean
    assert isinstance(ENABLE_AGENT_POOL, bool)
    assert isinstance(ENABLE_WORKFLOW, bool)
    assert isinstance(ENABLE_MEMORY, bool)
    assert isinstance(ENABLE_LEARNING, bool)
    assert isinstance(ENABLE_SECURITY, bool)


def test_agent_pool_configuration():
    """Test agent pool settings."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        AGENT_POOL_DIR,
        MAX_INSTANCES_PER_EXPERT,
        AGENT_IDLE_TIMEOUT_MINUTES,
    )

    assert isinstance(AGENT_POOL_DIR, Path)
    assert isinstance(MAX_INSTANCES_PER_EXPERT, int)
    assert isinstance(AGENT_IDLE_TIMEOUT_MINUTES, int)

    assert MAX_INSTANCES_PER_EXPERT > 0
    assert AGENT_IDLE_TIMEOUT_MINUTES > 0
