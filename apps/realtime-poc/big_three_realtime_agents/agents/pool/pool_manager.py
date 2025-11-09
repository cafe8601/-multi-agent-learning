"""
Agent pool manager - Instance lifecycle and coordination.

Manages active agent instances, handles creation/reuse/cleanup,
and coordinates with the intelligent selector.
"""

import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .expert_definition import ExpertDefinition, AgentInstance, AgentStatus
from .agent_loader import AgentDefinitionLoader

logger = logging.getLogger(__name__)


class AgentPoolManager:
    """
    Manage agent pool instances and lifecycle.

    Handles agent creation, reuse, and cleanup based on expert templates.

    Attributes:
        pool_dir: Path to agentpool directory
        loader: Agent definition loader
        active_instances: Currently active agent instances
        max_instances_per_type: Maximum instances per expert type

    Example:
        >>> manager = AgentPoolManager(pool_dir="agentpool/")
        >>> instance = manager.get_or_create_instance("backend-architect", task)
        >>> manager.release_instance(instance.instance_id)
    """

    def __init__(
        self,
        pool_dir: Path,
        max_instances_per_type: int = 3,
        idle_timeout_minutes: int = 30
    ):
        """
        Initialize pool manager.

        Args:
            pool_dir: Path to agentpool directory
            max_instances_per_type: Max instances per expert type
            idle_timeout_minutes: Minutes before idle cleanup
        """
        self.pool_dir = Path(pool_dir)
        self.loader = AgentDefinitionLoader(pool_dir)
        self.active_instances: Dict[str, AgentInstance] = {}
        self.max_instances_per_type = max_instances_per_type
        self.idle_timeout = timedelta(minutes=idle_timeout_minutes)

        # Load all expert definitions
        self.expert_definitions: Dict[str, ExpertDefinition] = {}
        self._load_all_experts()

    def _load_all_experts(self) -> None:
        """Load all expert definitions from pool."""
        experts = self.loader.load_all_agents()
        for expert in experts:
            self.expert_definitions[expert.agent_id] = expert
        logger.info(f"Loaded {len(self.expert_definitions)} expert definitions")

    def get_expert_definition(self, agent_id: str) -> Optional[ExpertDefinition]:
        """Get expert definition by ID."""
        return self.expert_definitions.get(agent_id)

    def list_available_experts(self) -> List[Dict]:
        """List all available expert types."""
        return [
            {
                "agent_id": exp.agent_id,
                "name": exp.name,
                "description": exp.description,
                "tier": exp.tier.value,
                "category": exp.category,
            }
            for exp in self.expert_definitions.values()
        ]

    def get_or_create_instance(
        self,
        agent_id: str,
        task: str,
        session_id: Optional[str] = None
    ) -> Optional[AgentInstance]:
        """
        Get idle instance or create new one.

        Args:
            agent_id: Expert type ID
            task: Task description
            session_id: Optional session ID for new instance

        Returns:
            AgentInstance or None if creation fails
        """
        # Check for idle instance
        idle_instance = self._find_idle_instance(agent_id)
        if idle_instance:
            logger.info(f"Reusing idle instance: {idle_instance.instance_id}")
            idle_instance.mark_active(task)
            return idle_instance

        # Create new instance if under limit
        if not self._can_create_instance(agent_id):
            logger.warning(f"Max instances reached for {agent_id}")
            return None

        # Get expert definition
        expert_def = self.expert_definitions.get(agent_id)
        if not expert_def:
            logger.error(f"Expert '{agent_id}' not found in pool")
            return None

        # Create new instance
        instance_id = f"{agent_id}_{uuid.uuid4().hex[:8]}"
        session_id = session_id or f"session_{uuid.uuid4().hex[:16]}"

        instance = AgentInstance(
            instance_id=instance_id,
            expert_def=expert_def,
            session_id=session_id,
            status=AgentStatus.ACTIVE,
            current_task=task,
        )

        self.active_instances[instance_id] = instance
        logger.info(f"Created new instance: {instance_id} for {agent_id}")

        return instance

    def release_instance(self, instance_id: str) -> None:
        """Mark instance as idle and available for reuse."""
        instance = self.active_instances.get(instance_id)
        if instance:
            instance.mark_idle()
            logger.info(f"Released instance: {instance_id}")

    def cleanup_idle_instances(self) -> int:
        """Remove instances idle beyond timeout."""
        cutoff = datetime.now() - self.idle_timeout
        to_remove = [
            inst_id for inst_id, inst in self.active_instances.items()
            if inst.status == AgentStatus.IDLE and inst.last_used < cutoff
        ]

        for inst_id in to_remove:
            del self.active_instances[inst_id]
            logger.info(f"Cleaned up idle instance: {inst_id}")

        return len(to_remove)

    def _find_idle_instance(self, agent_id: str) -> Optional[AgentInstance]:
        """Find idle instance of specified expert type."""
        for instance in self.active_instances.values():
            if (instance.expert_def.agent_id == agent_id and
                instance.status == AgentStatus.IDLE):
                return instance
        return None

    def _can_create_instance(self, agent_id: str) -> bool:
        """Check if we can create another instance."""
        count = sum(
            1 for inst in self.active_instances.values()
            if inst.expert_def.agent_id == agent_id
        )
        return count < self.max_instances_per_type

    def get_instance_status(self) -> List[Dict]:
        """Get status of all active instances."""
        return [inst.to_dict() for inst in self.active_instances.values()]
