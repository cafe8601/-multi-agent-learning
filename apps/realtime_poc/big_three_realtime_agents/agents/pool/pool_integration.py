"""
Pool Integration Manager - Main integration layer for Agent Pool system.

Coordinates agent pool with Claude Code agentic coder and provides
unified interface for agent management based on refactoring.md design.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from .agent_pool import AgentPoolManager
from .expert_selector import ExpertSelector
from .instance_executor import InstanceExecutor


logger = logging.getLogger(__name__)


class PoolIntegrationManager:
    """
    Main integration layer for Agent Pool system.

    Coordinates:
    - Agent Pool Manager (lifecycle management)
    - Expert Selector (intelligent selection)
    - Instance Executor (task execution)
    - Claude Code Agentic Coder (execution backend)
    """

    def __init__(
        self,
        pool_dir: Path,
        claude_coder,
        pool_definition_path: str = None,
        logger_instance=None,
    ):
        """
        Initialize pool integration manager.

        Args:
            pool_dir: Path to agentpool directory
            claude_coder: ClaudeCodeAgenticCoder instance
            pool_definition_path: Optional path to expert_agents.json
            logger_instance: Logger instance
        """
        self.pool_dir = Path(pool_dir)
        self.claude_coder = claude_coder
        self.logger = logger_instance or logger

        # Initialize agent pool manager
        self.pool_manager = AgentPoolManager(
            pool_definition_path=pool_definition_path, logger_instance=self.logger
        )

        # Initialize expert selector
        self.selector = ExpertSelector(
            pool_manager=self.pool_manager, logger_instance=self.logger
        )

        # Initialize instance executor
        self.executor = InstanceExecutor(
            pool_manager=self.pool_manager,
            claude_coder=claude_coder,
            logger_instance=self.logger,
        )

        self.logger.info(
            f"PoolIntegrationManager initialized with {len(self.pool_manager.expert_definitions)} experts"
        )

    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get comprehensive pool status.

        Returns:
            Dict with pool statistics and status
        """
        stats = self.pool_manager.get_stats()
        expert_types = self.pool_manager.list_expert_types()
        active_instances = self.pool_manager.list_active_instances()

        return {
            "stats": stats,
            "expert_types_count": len(expert_types),
            "active_instances_count": len(active_instances),
            "expert_types": expert_types[:10],  # First 10
            "active_instances": active_instances,
        }

    async def create_pool_agent(
        self, task: str, agent_id: Optional[str] = None, prefer_reuse: bool = True
    ) -> Dict[str, Any]:
        """
        Create or reuse pool agent for task.

        Args:
            task: Task description
            agent_id: Optional specific expert ID
            prefer_reuse: Whether to prefer reusing idle instances

        Returns:
            Dict with instance info
        """
        try:
            # Select expert if not specified
            if not agent_id:
                agent_id = await self.selector.select_expert(task)

            if not agent_id:
                return {"ok": False, "error": "No suitable expert found"}

            # Acquire expert instance
            instance = await self.pool_manager.acquire_expert(
                expert_id=agent_id, task_description=task, prefer_reuse=prefer_reuse
            )

            if not instance:
                return {
                    "ok": False,
                    "error": f"Could not acquire instance for {agent_id}",
                }

            self.logger.info(
                f"Created pool agent: {instance.instance_id} for task: {task[:50]}..."
            )

            return {
                "ok": True,
                "instance_id": instance.instance_id,
                "expert_id": agent_id,
                "session_id": instance.session_id,
                "is_reused": len(instance.task_history) > 0,
            }

        except Exception as exc:
            self.logger.error(f"Failed to create pool agent: {exc}")
            return {"ok": False, "error": str(exc)}

    async def execute_agent_task(
        self, instance_id: str, task: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute task on agent instance.

        Args:
            instance_id: Instance ID (e.g., "BackendExpert#1")
            task: Task description
            context: Additional context

        Returns:
            Execution result
        """
        result = await self.executor.execute_task(instance_id, task, context)
        return result

    def release_agent(self, instance_id: str, task_result: str = "") -> Dict[str, Any]:
        """
        Release agent back to pool.

        Args:
            instance_id: Instance ID
            task_result: Task result summary

        Returns:
            Release status
        """
        self.pool_manager.release_instance(instance_id, task_result)
        return {"ok": True, "instance_id": instance_id, "status": "released"}

    def terminate_agent(self, instance_id: str) -> Dict[str, Any]:
        """
        Permanently terminate agent instance.

        Args:
            instance_id: Instance ID

        Returns:
            Termination status
        """
        self.pool_manager.terminate_instance(instance_id)
        return {"ok": True, "instance_id": instance_id, "status": "terminated"}

    def cleanup_idle_instances(self, max_idle_minutes: int = 30) -> int:
        """
        Cleanup idle instances.

        Args:
            max_idle_minutes: Maximum idle time in minutes

        Returns:
            Number of instances cleaned
        """
        max_idle_seconds = max_idle_minutes * 60
        cleaned_count = self.pool_manager.cleanup_idle_instances(max_idle_seconds)

        self.logger.info(f"Cleaned up {cleaned_count} idle instances")
        return cleaned_count

    def list_expert_types(self) -> List[Dict[str, Any]]:
        """List all available expert types."""
        return self.pool_manager.list_expert_types()

    def list_active_instances(self) -> List[Dict[str, Any]]:
        """List currently active instances."""
        return self.pool_manager.list_active_instances()

    async def create_expert_type(
        self,
        expert_id: str,
        name: str,
        specialization: str,
        description: str,
        skills: List[str],
    ) -> Dict[str, Any]:
        """
        Create new expert type dynamically.

        Args:
            expert_id: Unique identifier
            name: Human-readable name
            specialization: Area of expertise
            description: Detailed description
            skills: List of skills

        Returns:
            Creation result
        """
        from .agent_pool import ExpertDefinition

        # Create expert definition
        new_expert = ExpertDefinition(
            expert_id=expert_id,
            name=name,
            specialization=specialization,
            description=description,
            skills=skills,
            system_prompt_template=f"prompts/experts/{expert_id.lower()}_expert.md",
            allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
            working_directory="./",
            max_instances=2,
            session_config={"model": "claude-sonnet-4-5-20250929", "temperature": 0.7},
        )

        # Add to pool
        self.pool_manager.expert_definitions[expert_id] = new_expert

        self.logger.info(f"Created new expert type: {expert_id}")

        return {"ok": True, "expert_id": expert_id, "name": name}

    async def suggest_experts_for_workflow(
        self, workflow_steps: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Suggest experts for multi-step workflow.

        Args:
            workflow_steps: List of workflow steps

        Returns:
            Expert suggestions
        """
        suggestions = self.selector.suggest_experts_for_workflow(workflow_steps)
        return suggestions
