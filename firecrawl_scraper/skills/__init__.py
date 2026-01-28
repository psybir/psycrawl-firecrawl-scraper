"""
PsyCrawl Skills System - Psybir Evidence Engine

Skills are modular analysis capabilities that follow the Psybir methodology:
Evidence -> Hypothesis -> Design -> Build -> Measure -> Iterate

Each skill provides:
- Assessment-first workflow (check context, gather info)
- Framework-based analysis (prioritized, structured)
- Decision-grade output (geo-tagged, actionable findings)
- Cross-skill routing (related skills for follow-up)

Pattern inspired by marketingskills: YAML frontmatter, <400 line SKILL.md,
reference files for lookup tables, templates, and worked examples.
"""

import importlib
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Type
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Skill registry - populated by discover_skills()
_SKILL_REGISTRY: Dict[str, 'SkillInfo'] = {}


@dataclass
class SkillInfo:
    """Metadata about a registered skill"""
    name: str
    version: str
    description: str
    trigger_phrases: List[str]
    related_skills: List[str]
    skill_class: Optional[Type] = None
    skill_path: Optional[Path] = None

    @classmethod
    def from_skill_md(cls, skill_path: Path) -> 'SkillInfo':
        """Parse SKILL.md frontmatter to extract skill metadata"""
        skill_md = skill_path / 'SKILL.md'
        if not skill_md.exists():
            raise FileNotFoundError(f"No SKILL.md found at {skill_md}")

        content = skill_md.read_text()

        # Extract YAML frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError(f"No YAML frontmatter in {skill_md}")

        frontmatter = yaml.safe_load(frontmatter_match.group(1))

        # Extract trigger phrases from description
        description = frontmatter.get('description', '')
        trigger_phrases = cls._extract_triggers(description)

        # Extract related skills from content
        related_skills = cls._extract_related_skills(content)

        return cls(
            name=frontmatter.get('name', skill_path.name),
            version=frontmatter.get('version', '1.0.0'),
            description=description,
            trigger_phrases=trigger_phrases,
            related_skills=related_skills,
            skill_path=skill_path
        )

    @staticmethod
    def _extract_triggers(description: str) -> List[str]:
        """Extract trigger phrases from skill description"""
        triggers = []

        # Look for quoted phrases
        quoted = re.findall(r'"([^"]+)"', description)
        triggers.extend(quoted)

        # Common trigger patterns
        patterns = [
            r'when (?:the user |they )?(?:want|mention|ask|say)s?\s+"?([^".,]+)"?',
            r'Also use when.*?(?:mention|say)s?\s+"?([^".,]+)"?',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            triggers.extend(matches)

        return list(set(triggers))

    @staticmethod
    def _extract_related_skills(content: str) -> List[str]:
        """Extract related skill references from content"""
        # Match patterns like `/skill-name` or `skill-name skill`
        related = re.findall(r'[`/]([a-z][a-z0-9-_]+)(?:`| skill)', content, re.IGNORECASE)
        return list(set(related))


def discover_skills(skills_dir: Optional[Path] = None) -> Dict[str, SkillInfo]:
    """
    Discover all available skills by scanning the skills directory.

    Each skill must have:
    - A directory under skills/ (e.g., skills/competitor_intel/)
    - A SKILL.md file with YAML frontmatter
    - A skill.py file with the skill implementation

    Returns:
        Dict mapping skill names to SkillInfo objects
    """
    global _SKILL_REGISTRY

    if skills_dir is None:
        skills_dir = Path(__file__).parent

    discovered = {}

    for path in skills_dir.iterdir():
        if not path.is_dir():
            continue
        if path.name.startswith('_') or path.name.startswith('.'):
            continue

        skill_md = path / 'SKILL.md'
        skill_py = path / 'skill.py'

        if not skill_md.exists():
            continue

        try:
            info = SkillInfo.from_skill_md(path)

            # Try to load the skill class if skill.py exists
            if skill_py.exists():
                try:
                    module_name = f"firecrawl_scraper.skills.{path.name}.skill"
                    module = importlib.import_module(module_name)
                    if hasattr(module, 'Skill'):
                        info.skill_class = module.Skill
                except ImportError as e:
                    logger.warning(f"Could not import skill {path.name}: {e}")

            discovered[info.name] = info
            logger.debug(f"Discovered skill: {info.name} v{info.version}")

        except Exception as e:
            logger.warning(f"Failed to load skill from {path}: {e}")

    _SKILL_REGISTRY = discovered
    return discovered


def get_skill(name: str) -> Optional[SkillInfo]:
    """Get a skill by name"""
    if not _SKILL_REGISTRY:
        discover_skills()

    # Try exact match first
    if name in _SKILL_REGISTRY:
        return _SKILL_REGISTRY[name]

    # Try with underscores/dashes normalized
    normalized = name.replace('-', '_')
    if normalized in _SKILL_REGISTRY:
        return _SKILL_REGISTRY[normalized]

    normalized = name.replace('_', '-')
    for skill_name, info in _SKILL_REGISTRY.items():
        if skill_name.replace('_', '-') == normalized:
            return info

    return None


def list_skills() -> List[SkillInfo]:
    """List all available skills"""
    if not _SKILL_REGISTRY:
        discover_skills()
    return list(_SKILL_REGISTRY.values())


def find_skill_by_trigger(query: str) -> Optional[SkillInfo]:
    """Find a skill that matches the given natural language query"""
    if not _SKILL_REGISTRY:
        discover_skills()

    query_lower = query.lower()
    best_match = None
    best_score = 0

    for info in _SKILL_REGISTRY.values():
        score = 0

        # Check trigger phrases
        for trigger in info.trigger_phrases:
            if trigger.lower() in query_lower:
                score += 10
            elif any(word in query_lower for word in trigger.lower().split()):
                score += 2

        # Check skill name
        name_words = info.name.replace('_', ' ').replace('-', ' ').split()
        for word in name_words:
            if word.lower() in query_lower:
                score += 5

        if score > best_score:
            best_score = score
            best_match = info

    return best_match if best_score > 0 else None


# Auto-discover skills on import
try:
    discover_skills()
except Exception as e:
    logger.debug(f"Initial skill discovery failed (this is normal during setup): {e}")


__all__ = [
    'SkillInfo',
    'discover_skills',
    'get_skill',
    'list_skills',
    'find_skill_by_trigger',
]
