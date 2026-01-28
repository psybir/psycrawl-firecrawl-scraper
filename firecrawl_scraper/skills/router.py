"""
Skill Router - Natural Language + Slash Command Routing

Routes user input to the appropriate skill:
1. Slash commands: /competitor-intel, /seo-audit, etc.
2. Natural language: "analyze competitors in Pittsburgh"
3. Entity extraction: URLs, locations, industries from query
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

from . import find_skill_by_trigger, get_skill, list_skills, SkillInfo

logger = logging.getLogger(__name__)


@dataclass
class RoutingResult:
    """Result of routing user input to a skill"""
    skill_info: Optional[SkillInfo]
    confidence: float  # 0-1
    extracted_entities: Dict[str, str]
    original_query: str
    is_slash_command: bool = False

    @property
    def matched(self) -> bool:
        return self.skill_info is not None and self.confidence > 0


@dataclass
class EntityExtraction:
    """Extracted entities from user query"""
    urls: List[str]
    locations: List[str]
    industries: List[str]
    keywords: List[str]


class SkillRouter:
    """
    Routes user input to appropriate skills.

    Supports:
    - Slash commands: /competitor-intel https://example.com --geo "Pittsburgh"
    - Natural language: "analyze competitors in Pittsburgh for virtual tours"
    - Mixed: "run /seo-audit for mysite.com"
    """

    # Location patterns for geo extraction
    LOCATION_PATTERNS = [
        r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:,\s*[A-Z]{2})?)',  # "in Pittsburgh, PA"
        r'near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # "near Pittsburgh"
        r'around\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'(?:--geo|--location)\s+"?([^"]+)"?',  # --geo "Pittsburgh Metro"
        r'for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:area|market|region)',
    ]

    # URL pattern
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'

    # Industry keywords (can be extended)
    INDUSTRY_KEYWORDS = {
        'virtual tours': ['virtual tour', '360', 'matterport', 'vr tour'],
        'real estate': ['real estate', 'realtor', 'property', 'housing'],
        'restaurants': ['restaurant', 'dining', 'food service', 'cafe'],
        'hospitality': ['hotel', 'hospitality', 'lodging', 'inn'],
        'retail': ['retail', 'store', 'shop', 'e-commerce'],
        'plumbing': ['plumber', 'plumbing', 'hvac', 'contractor'],
        'legal': ['lawyer', 'attorney', 'legal', 'law firm'],
        'medical': ['medical', 'healthcare', 'doctor', 'clinic', 'dental'],
    }

    def __init__(self):
        self.skills = list_skills()

    def route(self, query: str) -> RoutingResult:
        """
        Route user query to appropriate skill.

        Args:
            query: User input (slash command or natural language)

        Returns:
            RoutingResult with matched skill and extracted entities
        """
        query = query.strip()

        # Check for slash command first
        slash_result = self._parse_slash_command(query)
        if slash_result.matched:
            return slash_result

        # Fall back to natural language routing
        return self._route_natural_language(query)

    def _parse_slash_command(self, query: str) -> RoutingResult:
        """Parse slash command format: /skill-name [args]"""
        # Match /skill-name pattern
        slash_match = re.match(r'^/?(\w+[-_]?\w*)', query)

        if not slash_match:
            return RoutingResult(
                skill_info=None,
                confidence=0,
                extracted_entities={},
                original_query=query,
            )

        skill_name = slash_match.group(1).replace('-', '_')

        # Try to find the skill
        skill_info = get_skill(skill_name)

        if skill_info:
            # Extract entities from the rest of the command
            remaining = query[slash_match.end():].strip()
            entities = self._extract_entities(remaining)

            return RoutingResult(
                skill_info=skill_info,
                confidence=1.0,
                extracted_entities=entities,
                original_query=query,
                is_slash_command=True,
            )

        return RoutingResult(
            skill_info=None,
            confidence=0,
            extracted_entities={},
            original_query=query,
        )

    def _route_natural_language(self, query: str) -> RoutingResult:
        """Route natural language query to best matching skill"""
        # Extract entities first
        entities = self._extract_entities(query)

        # Find best matching skill by trigger phrases
        skill_info = find_skill_by_trigger(query)

        if skill_info:
            # Calculate confidence based on trigger matches
            confidence = self._calculate_confidence(query, skill_info)

            return RoutingResult(
                skill_info=skill_info,
                confidence=confidence,
                extracted_entities=entities,
                original_query=query,
            )

        # No skill matched - return with entities only
        return RoutingResult(
            skill_info=None,
            confidence=0,
            extracted_entities=entities,
            original_query=query,
        )

    def _extract_entities(self, text: str) -> Dict[str, str]:
        """Extract URLs, locations, and other entities from text"""
        entities = {}

        # Extract URLs
        urls = re.findall(self.URL_PATTERN, text)
        if urls:
            entities['url'] = urls[0]
            entities['urls'] = urls

        # Extract locations
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, text)
            if match:
                entities['location'] = match.group(1)
                break

        # Extract industries
        text_lower = text.lower()
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                entities['industry'] = industry
                break

        # Extract focus/scope if mentioned
        focus_patterns = [
            (r'focus(?:ing)?\s+on\s+(\w+)', 'focus'),
            (r'(?:--focus|--type)\s+"?(\w+)"?', 'focus'),
            (r'(comprehensive|quick|detailed)\s+(?:analysis|audit|review)', 'depth'),
        ]
        for pattern, key in focus_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities[key] = match.group(1).lower()

        return entities

    def _calculate_confidence(self, query: str, skill_info: SkillInfo) -> float:
        """Calculate routing confidence based on trigger matches"""
        query_lower = query.lower()
        confidence = 0.5  # Base confidence for any match

        # Boost for trigger phrase matches
        for trigger in skill_info.trigger_phrases:
            if trigger.lower() in query_lower:
                confidence += 0.15

        # Boost for skill name in query
        name_normalized = skill_info.name.replace('_', ' ').replace('-', ' ')
        if name_normalized.lower() in query_lower:
            confidence += 0.2

        # Boost for multiple word matches
        skill_words = set(name_normalized.lower().split())
        query_words = set(query_lower.split())
        overlap = len(skill_words & query_words) / len(skill_words)
        confidence += overlap * 0.15

        return min(confidence, 1.0)

    def suggest_skills(self, query: str, limit: int = 3) -> List[Tuple[SkillInfo, float]]:
        """
        Suggest multiple skills that might be relevant.

        Useful for ambiguous queries.
        """
        suggestions = []
        entities = self._extract_entities(query)

        for skill_info in self.skills:
            confidence = self._calculate_confidence(query, skill_info)
            if confidence > 0.3:
                suggestions.append((skill_info, confidence))

        # Sort by confidence and return top matches
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:limit]


def parse_skill_args(args_string: str) -> Dict[str, str]:
    """
    Parse skill arguments from command line format.

    Supports:
    - Positional: https://example.com
    - Named: --geo "Pittsburgh" --focus pricing
    - Flags: --deep --comprehensive
    """
    args = {}
    tokens = args_string.split()
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token.startswith('--'):
            key = token[2:].replace('-', '_')
            # Check if next token is a value or another flag
            if i + 1 < len(tokens) and not tokens[i + 1].startswith('--'):
                value = tokens[i + 1]
                # Handle quoted values
                if value.startswith('"'):
                    # Find closing quote
                    end_quote = i + 1
                    while end_quote < len(tokens) and not tokens[end_quote].endswith('"'):
                        end_quote += 1
                    value = ' '.join(tokens[i + 1:end_quote + 1]).strip('"')
                    i = end_quote
                args[key] = value
                i += 1
            else:
                args[key] = True
        elif re.match(r'https?://', token):
            args['url'] = token
        else:
            # Positional argument
            if 'positional' not in args:
                args['positional'] = []
            args['positional'].append(token)

        i += 1

    return args


# Singleton router instance
_router: Optional[SkillRouter] = None


def get_router() -> SkillRouter:
    """Get the singleton router instance"""
    global _router
    if _router is None:
        _router = SkillRouter()
    return _router


__all__ = [
    'SkillRouter',
    'RoutingResult',
    'EntityExtraction',
    'get_router',
    'parse_skill_args',
]
