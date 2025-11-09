"""
Unit tests for Agent Pool system (from refactoring.md).
"""

import pytest
from pathlib import Path


def test_agent_pool_manager_initialization(temp_working_dir):
    """Test AgentPoolManager initialization."""
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
        AgentPoolManager,
    )

    # Initialize without definition file (uses markdown agents)
    manager = AgentPoolManager()

    # Should have loaded agents from markdown files
    assert len(manager.expert_definitions) > 0
    assert manager.active_instances == {}


def test_agent_status_enum():
    """Test AgentStatus enum values."""
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
        AgentStatus,
    )

    assert AgentStatus.IDLE.value == "idle"
    assert AgentStatus.WORKING.value == "working"
    assert AgentStatus.RESERVED.value == "reserved"
    assert AgentStatus.TERMINATED.value == "terminated"


def test_expert_definition():
    """Test ExpertDefinition dataclass."""
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
        ExpertDefinition,
    )

    expert = ExpertDefinition(
        expert_id="TestExpert",
        name="Test Expert",
        specialization="testing",
        description="Test expert for unit tests",
        skills=["testing", "pytest"],
        system_prompt_template="prompts/test_expert.md",
        allowed_tools=["Read", "Write"],
        working_directory="./",
        max_instances=3,
        session_config={"model": "claude-sonnet", "temperature": 0.7},
    )

    assert expert.expert_id == "TestExpert"
    assert expert.max_instances == 3


def test_list_expert_types(temp_working_dir):
    """Test listing expert types."""
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
        AgentPoolManager,
    )

    manager = AgentPoolManager()
    expert_types = manager.list_expert_types()

    assert isinstance(expert_types, list)
    assert len(expert_types) > 0

    # Check structure
    if expert_types:
        first = expert_types[0]
        assert "expert_id" in first
        assert "name" in first
        assert "description" in first
        assert "skills" in first


@pytest.mark.asyncio
async def test_expert_selector():
    """Test ExpertSelector intelligent selection."""
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
        AgentPoolManager,
    )
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.expert_selector import (
        ExpertSelector,
    )

    manager = AgentPoolManager()
    selector = ExpertSelector(pool_manager=manager)

    # Test selection
    task = "Create FastAPI backend with JWT authentication"
    selected = await selector.select_expert(task)

    assert selected is not None
    # Should select backend-related expert or general
    assert isinstance(selected, str)


@pytest.mark.asyncio
async def test_pool_integration_manager(temp_working_dir):
    """Test PoolIntegrationManager."""
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.pool_integration import (
        PoolIntegrationManager,
    )
    from unittest.mock import Mock

    # Mock Claude coder
    mock_claude = Mock()
    mock_claude.execute_task = Mock(
        return_value={"output": "Task completed", "files_modified": []}
    )

    # Initialize integration manager
    pool_dir = Path("agentpool")
    integration = PoolIntegrationManager(
        pool_dir=pool_dir, claude_coder=mock_claude
    )

    # Test pool status
    status = integration.get_pool_status()
    assert status is not None
    assert "stats" in status
    assert "expert_types_count" in status


def test_pool_stats():
    """Test pool statistics retrieval."""
    from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
        AgentPoolManager,
    )

    manager = AgentPoolManager()
    stats = manager.get_stats()

    assert "total_instances" in stats
    assert "expert_types" in stats
    assert "by_status" in stats

    # Initially should be empty
    assert stats["total_instances"] == 0
    assert stats["expert_types"] > 0
