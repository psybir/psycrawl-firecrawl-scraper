"""
Context Manager - Persistent context for skill sessions

Manages .psycrawl/ directory for:
- product-context.md: Reusable business context
- data/: Cached analysis results
- data/competitors/: Centralized competitor YAML

Context reuse reduces redundant questions by 50%+.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages persistent context in .psycrawl/ directory.

    Product context is stored in YAML-friendly markdown format
    for easy reading and editing by users.
    """

    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            # Default to current working directory
            base_path = Path.cwd()

        self.base_path = base_path
        self.psycrawl_dir = base_path / '.psycrawl'
        self.context_file = self.psycrawl_dir / 'product-context.md'
        self.data_dir = self.psycrawl_dir / 'data'
        self.competitors_dir = self.data_dir / 'competitors'

        # Ensure directories exist
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create .psycrawl directory structure if needed"""
        self.psycrawl_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.competitors_dir.mkdir(exist_ok=True)

    async def load_context(self) -> Dict[str, Any]:
        """
        Load product context from .psycrawl/product-context.md

        Returns parsed YAML sections from the markdown file.
        """
        if not self.context_file.exists():
            return {}

        content = self.context_file.read_text()
        return self._parse_context_md(content)

    def _parse_context_md(self, content: str) -> Dict[str, Any]:
        """Parse product-context.md into structured data"""
        context = {}

        # Find YAML code blocks
        yaml_blocks = re.findall(r'```yaml\s*(.*?)```', content, re.DOTALL)

        for block in yaml_blocks:
            try:
                parsed = yaml.safe_load(block)
                if isinstance(parsed, dict):
                    context.update(parsed)
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse YAML block: {e}")

        # Also try to parse frontmatter if present
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            try:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                if isinstance(frontmatter, dict):
                    context.update(frontmatter)
            except yaml.YAMLError:
                pass

        return context

    async def save_context(self, context: Dict[str, Any]):
        """Save context to product-context.md"""
        content = self._format_context_md(context)
        self.context_file.write_text(content)

    def _format_context_md(self, context: Dict[str, Any]) -> str:
        """Format context as readable markdown with YAML blocks"""
        sections = []

        # Header
        sections.append("# PsyCrawl Product Context")
        sections.append("")
        sections.append("_This file stores reusable context for skill analyses._")
        sections.append("_Edit directly or let skills update it automatically._")
        sections.append("")

        # Business section
        if 'business' in context:
            sections.append("## Business")
            sections.append("```yaml")
            sections.append(yaml.dump({'business': context['business']}, default_flow_style=False))
            sections.append("```")
            sections.append("")

        # Geography section
        if 'geography' in context:
            sections.append("## Geography")
            sections.append("```yaml")
            sections.append(yaml.dump({'geography': context['geography']}, default_flow_style=False))
            sections.append("```")
            sections.append("")

        # Competitors section
        if 'competitors_known' in context:
            sections.append("## Known Competitors")
            sections.append("```yaml")
            sections.append(yaml.dump({'competitors_known': context['competitors_known']}, default_flow_style=False))
            sections.append("```")
            sections.append("")

        # Previous analyses
        if 'previous_analyses' in context:
            sections.append("## Previous Analyses")
            sections.append("```yaml")
            sections.append(yaml.dump({'previous_analyses': context['previous_analyses']}, default_flow_style=False))
            sections.append("```")
            sections.append("")

        # Any remaining keys
        remaining = {k: v for k, v in context.items()
                     if k not in ('business', 'geography', 'competitors_known', 'previous_analyses')}
        if remaining:
            sections.append("## Additional Context")
            sections.append("```yaml")
            sections.append(yaml.dump(remaining, default_flow_style=False))
            sections.append("```")

        return '\n'.join(sections)

    async def update_context(self, updates: Dict[str, Any]):
        """Update specific fields in context without overwriting"""
        context = await self.load_context()
        self._deep_merge(context, updates)
        await self.save_context(context)

    def _deep_merge(self, base: Dict, updates: Dict):
        """Deep merge updates into base dict"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    async def record_analysis(self, skill_name: str, file_path: str, metadata: Optional[Dict] = None):
        """Record an analysis in previous_analyses"""
        context = await self.load_context()

        if 'previous_analyses' not in context:
            context['previous_analyses'] = []

        analysis_record = {
            'skill': skill_name,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'file': file_path,
        }
        if metadata:
            analysis_record.update(metadata)

        context['previous_analyses'].append(analysis_record)

        # Keep only last 20 analyses
        context['previous_analyses'] = context['previous_analyses'][-20:]

        await self.save_context(context)

    # Competitor data management

    async def save_competitor(self, competitor_name: str, data: Dict[str, Any]):
        """Save competitor data to centralized YAML"""
        slug = self._slugify(competitor_name)
        file_path = self.competitors_dir / f"{slug}.yaml"

        # Add metadata
        data['_slug'] = slug
        data['_last_updated'] = datetime.now().isoformat()

        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

        # Update known competitors in context
        await self._add_known_competitor(competitor_name, data.get('website', ''))

    async def load_competitor(self, competitor_name: str) -> Optional[Dict[str, Any]]:
        """Load competitor data from YAML"""
        slug = self._slugify(competitor_name)
        file_path = self.competitors_dir / f"{slug}.yaml"

        if not file_path.exists():
            return None

        with open(file_path) as f:
            return yaml.safe_load(f)

    async def list_competitors(self) -> List[Dict[str, Any]]:
        """List all saved competitors"""
        competitors = []
        for file_path in self.competitors_dir.glob('*.yaml'):
            with open(file_path) as f:
                data = yaml.safe_load(f)
                if data:
                    competitors.append(data)
        return competitors

    async def _add_known_competitor(self, name: str, url: str):
        """Add to known competitors list if not present"""
        context = await self.load_context()

        if 'competitors_known' not in context:
            context['competitors_known'] = []

        # Check if already present
        existing = next(
            (c for c in context['competitors_known'] if c.get('name') == name),
            None
        )

        if not existing:
            context['competitors_known'].append({
                'name': name,
                'url': url,
            })
            await self.save_context(context)

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug.strip('-')

    # Skill result caching

    async def cache_result(self, skill_name: str, target: str, result: Dict[str, Any]):
        """Cache a skill result for reuse"""
        slug = self._slugify(target)
        cache_dir = self.data_dir / skill_name
        cache_dir.mkdir(exist_ok=True)

        file_path = cache_dir / f"{slug}-{datetime.now().strftime('%Y%m%d')}.json"

        with open(file_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return str(file_path)

    async def get_cached_result(
        self,
        skill_name: str,
        target: str,
        max_age_days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """Get cached result if fresh enough"""
        slug = self._slugify(target)
        cache_dir = self.data_dir / skill_name

        if not cache_dir.exists():
            return None

        # Find most recent cache file for this target
        pattern = f"{slug}-*.json"
        cache_files = sorted(cache_dir.glob(pattern), reverse=True)

        if not cache_files:
            return None

        # Check age
        latest = cache_files[0]
        # Extract date from filename
        date_match = re.search(r'(\d{8})\.json$', str(latest))
        if date_match:
            file_date = datetime.strptime(date_match.group(1), '%Y%m%d')
            age_days = (datetime.now() - file_date).days
            if age_days > max_age_days:
                return None

        with open(latest) as f:
            return json.load(f)


# Default context manager
_context_manager: Optional[ContextManager] = None


def get_context_manager(base_path: Optional[Path] = None) -> ContextManager:
    """Get or create the context manager"""
    global _context_manager
    if _context_manager is None or base_path is not None:
        _context_manager = ContextManager(base_path)
    return _context_manager


__all__ = [
    'ContextManager',
    'get_context_manager',
]
