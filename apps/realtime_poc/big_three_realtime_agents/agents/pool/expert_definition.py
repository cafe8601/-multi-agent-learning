"""
Expert definition data structures.

Defines the structure for agent templates loaded from markdown files
and active agent instances.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent instance status."""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"


class AgentTier(Enum):
    """Agent expertise tier."""
    TIER1_CORE = "tier1-core"
    TIER2_SPECIALIZED = "tier2-specialized"
    TIER3_EXPERIMENTAL = "tier3-experimental"


@dataclass
class ExpertDefinition:
    """
    Expert agent template definition.

    Loaded from markdown files in agentpool directory.

    Attributes:
        agent_id: Unique identifier (e.g., "backend-architect")
        name: Display name
        description: Brief description of expertise
        category: Category (e.g., "engineering", "quality")
        tier: Expertise tier (core/specialized/experimental)
        triggers: List of trigger patterns
        behavioral_mindset: Core behavioral principles
        focus_areas: List of expertise areas
        key_actions: Steps the agent takes
        outputs: Types of deliverables
        boundaries: What agent will/won't do
        file_path: Source markdown file path
    """
    agent_id: str
    name: str
    description: str
    category: str
    tier: AgentTier
    triggers: List[str] = field(default_factory=list)
    behavioral_mindset: str = ""
    focus_areas: List[str] = field(default_factory=list)
    key_actions: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    boundaries: Dict[str, List[str]] = field(default_factory=dict)
    file_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tier": self.tier.value,
            "triggers": self.triggers,
            "behavioral_mindset": self.behavioral_mindset,
            "focus_areas": self.focus_areas,
            "key_actions": self.key_actions,
            "outputs": self.outputs,
            "boundaries": self.boundaries,
        }


@dataclass
class AgentInstance:
    """
    Active agent instance.

    Represents a running agent based on an expert template.

    Attributes:
        instance_id: Unique instance identifier
        expert_def: Template this instance is based on
        session_id: Claude SDK session ID
        status: Current status
        created_at: Creation timestamp
        last_used: Last activity timestamp
        task_count: Number of tasks completed
        current_task: Currently executing task description
    """
    instance_id: str
    expert_def: ExpertDefinition
    session_id: str
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    task_count: int = 0
    current_task: Optional[str] = None

    def mark_active(self, task: str) -> None:
        """Mark instance as actively working on a task."""
        self.status = AgentStatus.ACTIVE
        self.current_task = task
        self.last_used = datetime.now()

    def mark_idle(self) -> None:
        """Mark instance as idle and ready for new tasks."""
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.task_count += 1
        self.last_used = datetime.now()

    def mark_error(self) -> None:
        """Mark instance as in error state."""
        self.status = AgentStatus.ERROR
        self.last_used = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "instance_id": self.instance_id,
            "agent_id": self.expert_def.agent_id,
            "session_id": self.session_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "task_count": self.task_count,
            "current_task": self.current_task,
        }
