"""
Agent Pool System - Dynamic expert agent management.

Provides intelligent agent selection and lifecycle management using
pre-defined expert templates from the agentpool directory.

Modules:
    agent_loader: Parse and load agent definitions from markdown
    pool_manager: Manage agent instances and lifecycle
    agent_selector: AI-powered agent selection
    expert_definition: Agent template data structures

Example:
    >>> from .pool_manager import AgentPoolManager
    >>> manager = AgentPoolManager(pool_dir="agentpool/")
    >>> agent = await manager.get_or_create_agent("backend-architect", task)
"""

from .agent_loader import AgentDefinitionLoader
from .pool_manager import AgentPoolManager
from .agent_selector import IntelligentAgentSelector
from .expert_definition import ExpertDefinition, AgentInstance

__all__ = [
    "AgentDefinitionLoader",
    "AgentPoolManager",
    "IntelligentAgentSelector",
    "ExpertDefinition",
    "AgentInstance",
]
