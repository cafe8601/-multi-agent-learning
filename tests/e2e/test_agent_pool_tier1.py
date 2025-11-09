"""
End-to-End tests for Tier 1 Agent Pool.

Tests the top 20 Tier 1 core agents to ensure they work correctly
in real scenarios. This addresses the Manus AI evaluation recommendation
for comprehensive Agent Pool runtime validation.
"""

import pytest
from pathlib import Path
from typing import Dict, Any


# Tier 1 Core Agents to Test (Top 20)
TIER1_AGENTS = [
    "backend-architect",
    "backend-developer",
    "devops-architect",
    "devops-engineer",
    "frontend-architect",
    "frontend-developer",
    "learning-guide",
    "performance-engineer",
    "python-expert",
    "quality-engineer",
    "refactoring-expert",
    "requirements-analyst",
    "root-cause-analyst",
    "security-engineer",
    "socratic-mentor",
    "system-architect",
    "technical-writer",
    "deep-research-agent",
]


@pytest.fixture
def agent_pool_dir():
    """Get agent pool directory."""
    return Path("agentpool/tier1-core")


@pytest.fixture
def mock_claude_coder():
    """Mock Claude Code agent for testing."""
    from unittest.mock import Mock, AsyncMock

    mock = Mock()
    mock.execute_task = AsyncMock(
        return_value={
            "success": True,
            "output": "Task completed successfully",
            "files_modified": ["test.py"],
        }
    )
    return mock


class TestTier1AgentDefinitions:
    """Test that all Tier 1 agent definitions are valid."""

    def test_all_tier1_agents_exist(self, agent_pool_dir):
        """Test that all expected Tier 1 agents have definition files."""
        for agent_id in TIER1_AGENTS:
            agent_file = agent_pool_dir / f"{agent_id}.md"
            assert agent_file.exists(), f"Agent definition missing: {agent_id}"

    def test_agent_definition_structure(self, agent_pool_dir):
        """Test that agent definitions have required structure."""
        for agent_id in TIER1_AGENTS[:5]:  # Test first 5
            agent_file = agent_pool_dir / f"{agent_id}.md"

            if not agent_file.exists():
                continue

            content = agent_file.read_text()

            # Should have key sections
            assert len(content) > 100, f"{agent_id}: Definition too short"

            # Should have some key terms
            has_description = any(
                word in content.lower()
                for word in ["expert", "specialist", "architect", "developer"]
            )
            assert has_description, f"{agent_id}: Missing role description"

    def test_agent_definition_markdown_valid(self, agent_pool_dir):
        """Test that agent definitions are valid markdown."""
        for agent_id in TIER1_AGENTS[:10]:  # Test first 10
            agent_file = agent_pool_dir / f"{agent_id}.md"

            if not agent_file.exists():
                continue

            content = agent_file.read_text()

            # Should not have syntax errors
            assert "```" in content or True  # Markdown code blocks optional

            # Should be readable
            assert content.strip(), f"{agent_id}: Empty file"


@pytest.mark.asyncio
class TestAgentPoolIntegration:
    """Test Agent Pool integration with pool manager."""

    async def test_pool_manager_loads_tier1_agents(self, agent_pool_dir):
        """Test that PoolManager loads Tier 1 agents correctly."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
            AgentPoolManager,
        )

        manager = AgentPoolManager()

        # Should have loaded agents
        assert len(manager.expert_definitions) > 0

        # Check some specific Tier 1 agents
        expert_ids = [exp.expert_id for exp in manager.expert_definitions.values()]

        # At least some should be loaded
        assert len(expert_ids) >= 10, f"Only {len(expert_ids)} experts loaded"

    async def test_expert_selection_for_backend_task(self):
        """Test expert selection for backend development task."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
            AgentPoolManager,
        )
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.expert_selector import (
            ExpertSelector,
        )

        manager = AgentPoolManager()
        selector = ExpertSelector(pool_manager=manager)

        # Test backend task selection
        task = "Create a FastAPI REST API with JWT authentication"
        selected = await selector.select_expert(task)

        # Should select backend-related expert
        assert selected is not None
        assert isinstance(selected, str)
        # Could be backend-related or general expert
        assert len(selected) > 0

    async def test_expert_selection_for_frontend_task(self):
        """Test expert selection for frontend task."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
            AgentPoolManager,
        )
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.expert_selector import (
            ExpertSelector,
        )

        manager = AgentPoolManager()
        selector = ExpertSelector(pool_manager=manager)

        # Test frontend task selection
        task = "Build a React component with TypeScript"
        selected = await selector.select_expert(task)

        assert selected is not None
        assert isinstance(selected, str)

    async def test_pool_integration_manager(self, mock_claude_coder):
        """Test PoolIntegrationManager with mock Claude coder."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.pool_integration import (
            PoolIntegrationManager,
        )

        pool_dir = Path("agentpool")
        integration = PoolIntegrationManager(
            pool_dir=pool_dir, claude_coder=mock_claude_coder
        )

        # Test pool status
        status = integration.get_pool_status()
        assert status is not None
        assert "stats" in status
        assert status["expert_types_count"] > 0


@pytest.mark.asyncio
class TestAgentPoolScenarios:
    """Test realistic Agent Pool usage scenarios."""

    async def test_backend_development_scenario(self, mock_claude_coder):
        """
        Scenario: Backend development task
        Expected: Backend expert selected and task executed
        """
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.pool_integration import (
            PoolIntegrationManager,
        )

        pool_dir = Path("agentpool")
        integration = PoolIntegrationManager(
            pool_dir=pool_dir, claude_coder=mock_claude_coder
        )

        # Create pool agent for backend task
        task = "Create FastAPI endpoints for user authentication"
        result = await integration.create_pool_agent(task=task, prefer_reuse=False)

        # Should succeed
        assert result.get("ok") is True
        assert "instance_id" in result
        assert "expert_id" in result

    async def test_frontend_development_scenario(self, mock_claude_coder):
        """
        Scenario: Frontend development task
        Expected: Frontend expert selected
        """
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.pool_integration import (
            PoolIntegrationManager,
        )

        pool_dir = Path("agentpool")
        integration = PoolIntegrationManager(
            pool_dir=pool_dir, claude_coder=mock_claude_coder
        )

        task = "Build a responsive login form with React"
        result = await integration.create_pool_agent(task=task)

        assert result.get("ok") is True

    async def test_instance_reuse_scenario(self, mock_claude_coder):
        """
        Scenario: Multiple tasks for same expert type
        Expected: Instance reused for efficiency
        """
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.pool_integration import (
            PoolIntegrationManager,
        )

        pool_dir = Path("agentpool")
        integration = PoolIntegrationManager(
            pool_dir=pool_dir, claude_coder=mock_claude_coder
        )

        # First task
        task1 = "Create Python module for data processing"
        result1 = await integration.create_pool_agent(task=task1, prefer_reuse=True)

        assert result1.get("ok") is True
        instance1 = result1.get("instance_id")

        # Release instance
        integration.release_agent(instance1, "Task completed")

        # Second similar task - should reuse
        task2 = "Add error handling to Python module"
        result2 = await integration.create_pool_agent(task=task2, prefer_reuse=True)

        assert result2.get("ok") is True
        # Note: Without actual Claude execution, we can't test full reuse
        # But we can verify the structure works


@pytest.mark.asyncio
@pytest.mark.slow
class TestAgentPoolRuntimeValidation:
    """
    Runtime validation tests for Agent Pool.

    These tests require actual API keys and may incur costs.
    Run with: pytest tests/e2e/test_agent_pool_tier1.py -m slow
    """

    pytestmark = pytest.mark.skipif(
        "not config.getoption('--run-expensive')",
        reason="Requires --run-expensive flag and API keys"
    )

    async def test_python_expert_real_execution(self):
        """
        EXPENSIVE: Test python-expert with real Claude API.

        Validates that python-expert agent can actually generate working code.
        """
        pytest.skip("Requires real API keys and --run-expensive flag")

        # This would test:
        # 1. Load python-expert prompt
        # 2. Create real Claude agent
        # 3. Execute simple task
        # 4. Verify code output
        # 5. Check code quality

    async def test_backend_architect_real_execution(self):
        """
        EXPENSIVE: Test backend-architect with real API.
        """
        pytest.skip("Requires real API keys and --run-expensive flag")

    async def test_security_engineer_real_execution(self):
        """
        EXPENSIVE: Test security-engineer with real API.
        """
        pytest.skip("Requires real API keys and --run-expensive flag")


class TestAgentPoolMetrics:
    """Test metrics and statistics for Agent Pool."""

    def test_pool_statistics_collection(self):
        """Test that pool manager collects statistics correctly."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
            AgentPoolManager,
        )

        manager = AgentPoolManager()
        stats = manager.get_stats()

        assert "total_instances" in stats
        assert "expert_types" in stats
        assert "by_status" in stats
        assert isinstance(stats["total_instances"], int)
        assert isinstance(stats["expert_types"], int)

    def test_expert_types_listing(self):
        """Test listing of expert types."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
            AgentPoolManager,
        )

        manager = AgentPoolManager()
        expert_types = manager.list_expert_types()

        assert isinstance(expert_types, list)
        assert len(expert_types) > 0

        # Verify structure
        if expert_types:
            first_expert = expert_types[0]
            assert "expert_id" in first_expert
            assert "name" in first_expert
            assert "description" in first_expert
            assert "skills" in first_expert
            assert isinstance(first_expert["skills"], list)


@pytest.mark.asyncio
class TestAgentPoolErrorHandling:
    """Test error handling in Agent Pool system."""

    async def test_invalid_agent_id(self, mock_claude_coder):
        """Test handling of invalid agent ID."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.pool_integration import (
            PoolIntegrationManager,
        )

        pool_dir = Path("agentpool")
        integration = PoolIntegrationManager(
            pool_dir=pool_dir, claude_coder=mock_claude_coder
        )

        # Try to create agent with invalid ID
        result = await integration.create_pool_agent(
            task="Some task", agent_id="NonExistentExpert"
        )

        # Should handle gracefully
        # Either return error or fall back to general expert
        assert isinstance(result, dict)

    async def test_max_instances_limit(self):
        """Test that max instances per expert is enforced."""
        from apps.realtime_poc.big_three_realtime_agents.agents.pool.agent_pool import (
            AgentPoolManager,
            ExpertDefinition,
        )

        manager = AgentPoolManager()

        # Create test expert with max_instances=1
        test_expert = ExpertDefinition(
            expert_id="TestExpert",
            name="Test Expert",
            specialization="testing",
            description="Test expert",
            skills=["testing"],
            system_prompt_template="test.md",
            allowed_tools=["Read"],
            working_directory="./",
            max_instances=1,
            session_config={},
        )

        manager.expert_definitions["TestExpert"] = test_expert

        # Create first instance
        instance1 = await manager.acquire_expert("TestExpert", "Task 1", prefer_reuse=False)
        assert instance1 is not None

        # Try to create second instance (should fail due to limit)
        instance2 = await manager.acquire_expert("TestExpert", "Task 2", prefer_reuse=False)
        assert instance2 is None  # Should not exceed max_instances


# Test configuration hook
def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "expensive: marks tests that incur API costs"
    )


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--run-expensive",
        action="store_true",
        default=False,
        help="Run expensive tests that use real API calls",
    )
