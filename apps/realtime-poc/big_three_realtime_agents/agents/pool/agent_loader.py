"""
Agent definition loader from markdown files.

Parses agent definition markdown files from agentpool directory
and converts them to ExpertDefinition objects.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

from .expert_definition import ExpertDefinition, AgentTier

logger = logging.getLogger(__name__)


class AgentDefinitionLoader:
    """
    Load and parse agent definitions from markdown files.

    Parses markdown files with frontmatter and structured sections
    to create ExpertDefinition objects.

    Example:
        >>> loader = AgentDefinitionLoader(pool_dir="agentpool/")
        >>> expert = loader.load_agent("backend-architect")
        >>> print(expert.description)
    """

    def __init__(self, pool_dir: Path):
        """
        Initialize loader.

        Args:
            pool_dir: Path to agentpool directory
        """
        self.pool_dir = Path(pool_dir)
        self._cache: Dict[str, ExpertDefinition] = {}

    def load_agent(self, agent_id: str) -> Optional[ExpertDefinition]:
        """
        Load a single agent definition.

        Args:
            agent_id: Agent identifier (e.g., "backend-architect")

        Returns:
            ExpertDefinition if found, None otherwise
        """
        if agent_id in self._cache:
            return self._cache[agent_id]

        # Search for agent file
        agent_file = self._find_agent_file(agent_id)
        if not agent_file:
            logger.warning(f"Agent '{agent_id}' not found in pool")
            return None

        # Parse and cache
        expert = self._parse_markdown(agent_file)
        if expert:
            self._cache[agent_id] = expert

        return expert

    def load_all_agents(self) -> List[ExpertDefinition]:
        """Load all agent definitions from pool directory."""
        experts = []
        for md_file in self.pool_dir.rglob("*.md"):
            # Skip documentation files
            if md_file.name.upper().startswith(("README", "GUIDE", "COMPLETE", "FINAL")):
                continue

            expert = self._parse_markdown(md_file)
            if expert:
                experts.append(expert)
                self._cache[expert.agent_id] = expert

        logger.info(f"Loaded {len(experts)} agent definitions from pool")
        return experts

    def _find_agent_file(self, agent_id: str) -> Optional[Path]:
        """Find markdown file for agent ID."""
        # Try exact match
        exact_match = self.pool_dir / f"{agent_id}.md"
        if exact_match.exists():
            return exact_match

        # Search in subdirectories
        for md_file in self.pool_dir.rglob(f"{agent_id}.md"):
            return md_file

        return None

    def _parse_markdown(self, file_path: Path) -> Optional[ExpertDefinition]:
        """
        Parse markdown file to ExpertDefinition.

        Args:
            file_path: Path to markdown file

        Returns:
            ExpertDefinition or None if parsing fails
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.error(f"Failed to read {file_path}: {exc}")
            return None

        # Parse frontmatter
        frontmatter = self._parse_frontmatter(content)
        if not frontmatter:
            return None

        # Determine tier from path
        tier = self._determine_tier(file_path)

        # Parse sections
        sections = self._parse_sections(content)

        # Build ExpertDefinition
        expert = ExpertDefinition(
            agent_id=frontmatter.get("name", file_path.stem),
            name=frontmatter.get("name", file_path.stem).replace("-", " ").title(),
            description=frontmatter.get("description", ""),
            category=frontmatter.get("category", "general"),
            tier=tier,
            triggers=self._parse_list_section(sections.get("Triggers", "")),
            behavioral_mindset=sections.get("Behavioral Mindset", "").strip(),
            focus_areas=self._parse_list_section(sections.get("Focus Areas", "")),
            key_actions=self._parse_list_section(sections.get("Key Actions", "")),
            outputs=self._parse_list_section(sections.get("Outputs", "")),
            boundaries=self._parse_boundaries(sections.get("Boundaries", "")),
            file_path=str(file_path),
        )

        return expert

    def _parse_frontmatter(self, content: str) -> Optional[Dict[str, str]]:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown sections (## Headers)."""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _parse_list_section(self, section_text: str) -> List[str]:
        """Parse bulleted list section."""
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line.startswith(('-', '*', '•')):
                # Remove bullet and markdown formatting
                item = re.sub(r'^[-*•]\s*', '', line)
                item = re.sub(r'\*\*(.*?)\*\*:?', r'\1', item)  # Remove bold
                items.append(item.strip())
        return items

    def _parse_boundaries(self, section_text: str) -> Dict[str, List[str]]:
        """Parse boundaries section (Will/Will Not)."""
        boundaries = {"will": [], "will_not": []}
        current_list = None

        for line in section_text.split('\n'):
            line = line.strip()
            if "**Will:**" in line or "**Will**:" in line:
                current_list = "will"
            elif "**Will Not:**" in line or "**Will not:**" in line:
                current_list = "will_not"
            elif line.startswith(('-', '*', '•')) and current_list:
                item = re.sub(r'^[-*•]\s*', '', line).strip()
                boundaries[current_list].append(item)

        return boundaries

    def _determine_tier(self, file_path: Path) -> AgentTier:
        """Determine agent tier from file path."""
        path_str = str(file_path)
        if "tier1-core" in path_str:
            return AgentTier.TIER1_CORE
        elif "tier2-specialized" in path_str:
            return AgentTier.TIER2_SPECIALIZED
        elif "tier3-experimental" in path_str:
            return AgentTier.TIER3_EXPERIMENTAL
        else:
            # Root level agents are tier1
            return AgentTier.TIER1_CORE
