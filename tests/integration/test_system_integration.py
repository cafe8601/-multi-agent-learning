"""
Integration tests for Big Three Agents system.
"""

import pytest
import asyncio
from pathlib import Path


@pytest.mark.asyncio
async def test_system_initialization(all_api_keys, temp_working_dir):
    """Test that the system initializes correctly with all components."""
    from apps.realtime_poc.big_three_realtime_agents.config import (
        OPENAI_API_KEY,
        GEMINI_API_KEY,
    )

    # Verify API keys are configured
    assert OPENAI_API_KEY, "OPENAI_API_KEY not set"
    assert GEMINI_API_KEY, "GEMINI_API_KEY not set"

    # Test basic imports
    from apps.realtime_poc.big_three_realtime_agents import (
        setup_logging,
        config,
    )

    logger = setup_logging()
    assert logger is not None


@pytest.mark.asyncio
async def test_memory_manager_integration(temp_working_dir):
    """Test memory manager integration."""
    from apps.realtime_poc.big_three_realtime_agents.memory.memory_manager import (
        MemoryManager,
    )

    storage_dir = temp_working_dir / "memory"
    storage_dir.mkdir()

    manager = MemoryManager(storage_dir=storage_dir)

    # Test session creation
    session_id = "test_session_001"
    manager.create_session(session_id, metadata={"test": "data"})

    # Test message addition
    manager.add_message("user", "Hello", session_id)
    manager.add_message("assistant", "Hi there", session_id)

    # Test session retrieval
    session = manager.get_session(session_id)
    assert session is not None
    assert len(session["messages"]) == 2

    # Test context retrieval
    context = manager.get_recent_context(session_id, last_n=2)
    assert "Hello" in context
    assert "Hi there" in context


@pytest.mark.asyncio
async def test_learning_manager_integration(temp_working_dir):
    """Test learning manager integration."""
    from apps.realtime_poc.big_three_realtime_agents.learning.learning_manager import (
        LearningManager,
    )

    storage_dir = temp_working_dir / "learning"
    storage_dir.mkdir()

    manager = LearningManager(storage_dir=storage_dir)

    # Test outcome recording
    manager.record_task_outcome(
        task="Create hello world",
        agent_id="claude-code",
        result={"output": "Success"},
        success=True,
    )

    manager.record_task_outcome(
        task="Debug error",
        agent_id="claude-code",
        result={"output": "Success"},
        success=True,
    )

    # Test agent suggestion
    suggested_agent = manager.suggest_agent_for_task(
        task="Write code", available_agents=["claude-code", "gemini-browser"]
    )
    assert suggested_agent == "claude-code"  # Should suggest most successful

    # Test learning stats
    stats = manager.get_learning_stats()
    assert stats["total_outcomes"] == 2
    assert stats["success_rate"] == 1.0


@pytest.mark.asyncio
async def test_security_manager_integration(temp_working_dir):
    """Test security manager integration."""
    from apps.realtime_poc.big_three_realtime_agents.security.security_manager import (
        SecurityManager,
    )

    storage_dir = temp_working_dir / "security"
    storage_dir.mkdir()

    manager = SecurityManager(storage_dir=storage_dir)

    # Initialize permissions
    manager.initialize_default_permissions()

    # Test permission checks
    assert manager.check_permission("agent_creation") is True
    assert manager.check_permission("file_system_access") is True

    # Test audit logging
    manager.audit_log("test_event", {"user": "test", "action": "read"})

    # Test security summary
    summary = manager.get_security_summary()
    assert summary["total_events"] > 0
    assert "permissions" in summary


@pytest.mark.asyncio
async def test_registry_management(temp_working_dir):
    """Test agent registry management."""
    from apps.realtime_poc.big_three_realtime_agents.utils.registry import (
        RegistryManager,
    )

    registry_dir = temp_working_dir / "registry"
    registry_dir.mkdir()

    manager = RegistryManager()

    # Test agent registration
    agent_data = {
        "agent_id": "test_agent_001",
        "type": "claude-code",
        "created_at": "2025-11-09T10:00:00",
        "status": "active",
    }

    manager.register_agent("test_agent_001", agent_data)

    # Test agent retrieval
    retrieved = manager.get_agent("test_agent_001")
    assert retrieved is not None
    assert retrieved["type"] == "claude-code"

    # Test agent listing
    agents = manager.list_agents()
    assert len(agents) > 0
    assert "test_agent_001" in agents


@pytest.mark.asyncio
async def test_workflow_integration(temp_working_dir, all_api_keys):
    """Test workflow system integration."""
    from apps.realtime_poc.big_three_realtime_agents.workflow.workflow_planner import (
        WorkflowPlanner,
    )
    from apps.realtime_poc.big_three_realtime_agents.workflow.workflow_models import (
        WorkflowTask,
    )

    planner = WorkflowPlanner()

    # Create sample workflow task
    task = WorkflowTask(
        task_id="test_workflow_001",
        description="Create a simple web application",
        priority="high",
        estimated_duration=3600,
    )

    # Test workflow planning
    workflow = planner.plan_workflow(task)
    assert workflow is not None
    assert len(workflow.steps) > 0


@pytest.mark.asyncio
async def test_complete_system_flow(all_api_keys, temp_working_dir):
    """Test complete system flow with all components."""
    from apps.realtime_poc.big_three_realtime_agents.memory.memory_manager import (
        MemoryManager,
    )
    from apps.realtime_poc.big_three_realtime_agents.learning.learning_manager import (
        LearningManager,
    )
    from apps.realtime_poc.big_three_realtime_agents.security.security_manager import (
        SecurityManager,
    )

    # Initialize all managers
    memory = MemoryManager(storage_dir=temp_working_dir / "memory")
    learning = LearningManager(storage_dir=temp_working_dir / "learning")
    security = SecurityManager(storage_dir=temp_working_dir / "security")

    # Create session
    session_id = "integration_test_001"
    memory.create_session(session_id, metadata={"test": "integration"})

    # Check permission
    security.initialize_default_permissions()
    assert security.check_permission("agent_creation")

    # Record task outcome
    learning.record_task_outcome(
        task="Integration test",
        agent_id="test_agent",
        result={"status": "success"},
        success=True,
    )

    # Add messages to session
    memory.add_message("user", "Test message", session_id)

    # Verify all components worked
    assert memory.get_session(session_id) is not None
    assert learning.get_learning_stats()["total_outcomes"] == 1
    assert security.get_security_summary()["total_events"] > 0
