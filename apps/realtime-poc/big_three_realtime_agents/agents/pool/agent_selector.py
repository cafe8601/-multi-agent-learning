"""
Intelligent agent selector using AI-powered matching.

Analyzes tasks and selects the most appropriate expert agent
from the pool based on triggers, specialization, and context.
"""

import logging
from typing import List, Dict, Optional
import re

from .expert_definition import ExpertDefinition

logger = logging.getLogger(__name__)


class IntelligentAgentSelector:
    """
    AI-powered agent selection from expert pool.

    Analyzes task requirements and selects optimal expert agent
    using keyword matching, trigger patterns, and semantic similarity.

    Example:
        >>> selector = IntelligentAgentSelector(expert_definitions)
        >>> agent_id = selector.select_best_agent("Build REST API")
        >>> print(agent_id)  # "backend-architect"
    """

    def __init__(self, expert_definitions: Dict[str, ExpertDefinition]):
        """
        Initialize selector.

        Args:
            expert_definitions: Available expert definitions
        """
        self.experts = expert_definitions

    def select_best_agent(
        self,
        task: str,
        context: Optional[str] = None,
        top_n: int = 1
    ) -> Optional[str]:
        """
        Select best expert agent for task.

        Args:
            task: Task description
            context: Optional additional context
            top_n: Number of candidates to return (default 1)

        Returns:
            Agent ID of best match, or None if no match
        """
        if not self.experts:
            logger.warning("No expert definitions available")
            return None

        # Score all experts
        scores = self._score_all_experts(task, context)

        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if not ranked or ranked[0][1] == 0:
            logger.warning(f"No suitable expert found for task: {task[:50]}")
            return None

        best_agent_id = ranked[0][0]
        best_score = ranked[0][1]

        logger.info(f"Selected '{best_agent_id}' with score {best_score:.2f}")

        return best_agent_id

    def select_multiple_agents(
        self,
        task: str,
        max_agents: int = 3,
        min_score: float = 0.3
    ) -> List[str]:
        """Select multiple agents for complex tasks."""
        if not self.experts:
            return []

        scores = self._score_all_experts(task)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Filter by minimum score and max count
        selected = [
            agent_id for agent_id, score in ranked[:max_agents]
            if score >= min_score
        ]

        logger.info(f"Selected {len(selected)} agents for task")
        return selected

    def _score_all_experts(
        self,
        task: str,
        context: Optional[str] = None
    ) -> Dict[str, float]:
        """Score all experts for task relevance."""
        scores = {}
        task_lower = task.lower()
        context_lower = (context or "").lower()

        for agent_id, expert in self.experts.items():
            score = 0.0

            # Score trigger keywords (weight: 3.0)
            for trigger in expert.triggers:
                trigger_lower = trigger.lower()
                if trigger_lower in task_lower:
                    score += 3.0
                elif any(word in task_lower for word in trigger_lower.split()):
                    score += 1.0

            # Score description match (weight: 2.0)
            desc_words = set(expert.description.lower().split())
            task_words = set(task_lower.split())
            overlap = len(desc_words & task_words)
            score += overlap * 0.5

            # Score category match (weight: 1.0)
            if expert.category.lower() in task_lower:
                score += 1.0

            # Score focus areas (weight: 2.0)
            for area in expert.focus_areas:
                area_lower = area.lower()
                if area_lower in task_lower:
                    score += 2.0

            # Context scoring if provided
            if context:
                for trigger in expert.triggers:
                    if trigger.lower() in context_lower:
                        score += 1.0

            scores[agent_id] = score

        return scores

    def explain_selection(self, agent_id: str, task: str) -> str:
        """Explain why an agent was selected."""
        expert = self.experts.get(agent_id)
        if not expert:
            return "Agent not found"

        matched_triggers = [
            t for t in expert.triggers
            if t.lower() in task.lower()
        ]

        explanation = f"Selected '{expert.name}' because:\n"
        if matched_triggers:
            explanation += f"- Matched triggers: {', '.join(matched_triggers[:3])}\n"
        explanation += f"- Specialization: {expert.description}\n"
        explanation += f"- Tier: {expert.tier.value}\n"

        return explanation
