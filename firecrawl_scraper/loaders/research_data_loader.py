"""
Research Data Loader - Load research data from external repositories

Parses markdown and JSON files from research repos like escapeexe-research
and transforms them into structured data for pipeline integration.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CompetitorData:
    """Raw competitor data from research"""
    name: str
    location: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_level: Optional[str] = None
    threat_level: str = "medium"  # low, medium, high
    notes: Optional[str] = None
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class GBPData:
    """Google Business Profile data"""
    title: str
    rating: float
    review_count: int
    address: str
    place_id: str
    categories: List[str] = field(default_factory=list)
    place_topics: Dict[str, int] = field(default_factory=dict)
    rating_distribution: Dict[str, int] = field(default_factory=dict)
    people_also_search: List[Dict[str, Any]] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    work_hours: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    phone: Optional[str] = None
    domain: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class SEOKeywordData:
    """SEO keyword ranking data"""
    keyword: str
    current_rank: Optional[int] = None
    target_rank: Optional[int] = None
    top_ranker: Optional[str] = None
    opportunity: Optional[str] = None
    tier: str = "secondary"  # primary, secondary, tertiary


@dataclass
class MarketGap:
    """Identified market gap/opportunity"""
    segment: str
    description: str
    opportunity: str
    geographic: bool = False


@dataclass
class CompetitiveMoat:
    """Defensible competitive advantage"""
    feature: str
    description: str
    competitors_have: bool = False


@dataclass
class ExecutiveSummary:
    """Executive summary data"""
    bottom_line: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    priorities: Dict[str, List[str]] = field(default_factory=dict)  # immediate, medium, long
    metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ResearchData:
    """Complete research data package"""
    client_name: str
    research_date: datetime
    gbp_profile: Optional[GBPData] = None
    competitors: List[CompetitorData] = field(default_factory=list)
    seo_keywords: List[SEOKeywordData] = field(default_factory=list)
    market_gaps: List[MarketGap] = field(default_factory=list)
    moats: List[CompetitiveMoat] = field(default_factory=list)
    executive_summary: Optional[ExecutiveSummary] = None
    positioning_map: Optional[str] = None  # ASCII art positioning
    raw_data: Dict[str, Any] = field(default_factory=dict)


class ResearchDataLoader:
    """Load research data from escapeexe-research repository"""

    def __init__(self, research_path: str):
        """
        Initialize loader with path to research repo.

        Args:
            research_path: Path to escapeexe-research repo root
        """
        self.research_path = Path(research_path)
        if not self.research_path.exists():
            raise ValueError(f"Research path does not exist: {research_path}")

    def load_competitive_landscape(self) -> Dict[str, Any]:
        """Load competitive landscape markdown"""
        path = self.research_path / "consultant_analysis" / "competitive_intel" / "COMPETITIVE_LANDSCAPE.md"
        return self._parse_competitive_landscape(path)

    def load_executive_summary(self) -> ExecutiveSummary:
        """Load and parse executive summary"""
        path = self.research_path / "consultant_analysis" / "01_EXECUTIVE_SUMMARY.md"
        return self._parse_executive_summary(path)

    def load_local_seo_analysis(self) -> Dict[str, Any]:
        """Load local SEO analysis"""
        path = self.research_path / "consultant_analysis" / "02_LOCAL_SEO_ANALYSIS.md"
        if path.exists():
            return {"raw": path.read_text(), "parsed": True}
        return {}

    def load_seo_keywords(self) -> List[SEOKeywordData]:
        """Load SEO keyword rankings"""
        path = self.research_path / "website" / "escape-intel" / "analysis" / "seo-keyword-rankings.md"
        return self._parse_seo_keywords(path)

    def load_gbp_profile(self) -> GBPData:
        """Load Google Business Profile JSON"""
        path = self.research_path / "local_seo" / "gbp_profile.json"
        return self._parse_gbp_profile(path)

    def load_design_analysis(self) -> Dict[str, Any]:
        """Load design analysis JSON files"""
        base_path = self.research_path / "website" / "escape-intel" / "analysis" / "visual_design"
        result = {}

        # Load summary
        summary_path = base_path / "design_analysis_summary.json"
        if summary_path.exists():
            with open(summary_path) as f:
                result["summary"] = json.load(f)

        # Load aggregated data
        agg_path = base_path / "target" / "aggregated"
        if agg_path.exists():
            for json_file in agg_path.glob("*.json"):
                with open(json_file) as f:
                    result[json_file.stem] = json.load(f)

        return result

    def load_all(self) -> ResearchData:
        """Load all research data into unified structure"""
        research = ResearchData(
            client_name="escape.exe",
            research_date=datetime.now()
        )

        # Load GBP Profile
        try:
            research.gbp_profile = self.load_gbp_profile()
        except Exception as e:
            print(f"Warning: Could not load GBP profile: {e}")

        # Load competitive landscape
        try:
            landscape = self.load_competitive_landscape()
            research.competitors = landscape.get("competitors", [])
            research.market_gaps = landscape.get("market_gaps", [])
            research.moats = landscape.get("moats", [])
            research.positioning_map = landscape.get("positioning_map")
        except Exception as e:
            print(f"Warning: Could not load competitive landscape: {e}")

        # Load executive summary
        try:
            research.executive_summary = self.load_executive_summary()
        except Exception as e:
            print(f"Warning: Could not load executive summary: {e}")

        # Load SEO keywords
        try:
            research.seo_keywords = self.load_seo_keywords()
        except Exception as e:
            print(f"Warning: Could not load SEO keywords: {e}")

        # Load design analysis into raw_data
        try:
            research.raw_data["design_analysis"] = self.load_design_analysis()
        except Exception as e:
            print(f"Warning: Could not load design analysis: {e}")

        return research

    def _parse_competitive_landscape(self, path: Path) -> Dict[str, Any]:
        """Parse competitive landscape markdown"""
        if not path.exists():
            return {}

        content = path.read_text()
        result = {
            "competitors": [],
            "market_gaps": [],
            "moats": [],
            "positioning_map": None
        }

        # Extract competitors from table
        table_pattern = r'\|\s*\*\*?([^|*]+)\*?\*?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|[^|]*\|[^|]*\|'
        for match in re.finditer(table_pattern, content):
            name = match.group(1).strip()
            if name.lower() in ['competitor', 'escape.exe', '']:
                continue

            rating_str = match.group(3).strip()
            reviews_str = match.group(4).strip().replace(',', '')

            # Parse rating
            rating = None
            try:
                rating = float(rating_str)
            except:
                pass

            # Parse review count
            review_count = None
            try:
                review_count = int(reviews_str)
            except:
                pass

            # Determine threat level from emoji/text
            threat_level = "medium"
            if "HIGH" in content[match.start():match.end()+50].upper():
                threat_level = "high"
            elif "LOW" in content[match.start():match.end()+50].upper():
                threat_level = "low"

            result["competitors"].append(CompetitorData(
                name=name,
                location=match.group(2).strip(),
                rating=rating,
                review_count=review_count,
                threat_level=threat_level
            ))

        # Extract positioning map (ASCII art between triple backticks)
        map_pattern = r'```\s*([\s\S]*?PREMIUM[\s\S]*?STANDARD[\s\S]*?)```'
        map_match = re.search(map_pattern, content)
        if map_match:
            result["positioning_map"] = map_match.group(1).strip()

        # Extract market gaps
        gaps_section = re.search(r'### Underserved Segments([\s\S]*?)(?=###|---|\Z)', content)
        if gaps_section:
            gap_pattern = r'\d+\.\s*\*\*([^*]+)\*\*\s*\n([^\n]+)\n([^\n]+)'
            for gap in re.finditer(gap_pattern, gaps_section.group(1)):
                result["market_gaps"].append(MarketGap(
                    segment=gap.group(1).strip(),
                    description=gap.group(2).strip().lstrip('- '),
                    opportunity=gap.group(3).strip().lstrip('- ')
                ))

        # Extract geographic gaps
        geo_gaps = re.search(r'### Geographic Gaps([\s\S]*?)(?=###|---|\Z)', content)
        if geo_gaps:
            for line in geo_gaps.group(1).strip().split('\n'):
                if line.strip().startswith('-'):
                    result["market_gaps"].append(MarketGap(
                        segment="Geographic",
                        description=line.strip().lstrip('- '),
                        opportunity="Expand market presence",
                        geographic=True
                    ))

        # Extract moats (What ONLY escape.exe Can Claim)
        moats_section = re.search(r'### What ONLY escape\.exe Can Claim([\s\S]*?)(?=###|---|\Z)', content)
        if moats_section:
            moat_pattern = r'\d+\.\s*\*\*([^*]+)\*\*\s*[-–]\s*([^\n]+)'
            for moat in re.finditer(moat_pattern, moats_section.group(1)):
                result["moats"].append(CompetitiveMoat(
                    feature=moat.group(1).strip(),
                    description=moat.group(2).strip(),
                    competitors_have=False
                ))

        return result

    def _parse_executive_summary(self, path: Path) -> ExecutiveSummary:
        """Parse executive summary markdown"""
        if not path.exists():
            return ExecutiveSummary(bottom_line="")

        content = path.read_text()

        # Extract bottom line
        bottom_line = ""
        bl_match = re.search(r'\*\*([^*]+5-star[^*]+3-star[^*]+)\*\*', content)
        if bl_match:
            bottom_line = bl_match.group(1)

        summary = ExecutiveSummary(bottom_line=bottom_line)

        # Extract strengths
        strengths_section = re.search(r'## Strengths[^\n]*\n([\s\S]*?)(?=\n## |\Z)', content)
        if strengths_section:
            summary.strengths = self._extract_list_items(strengths_section.group(1))

        # Extract weaknesses
        weaknesses_section = re.search(r'## Weaknesses[^\n]*\n([\s\S]*?)(?=\n## |\Z)', content)
        if weaknesses_section:
            summary.weaknesses = self._extract_list_items(weaknesses_section.group(1))

        # Extract opportunities
        opportunities_section = re.search(r'## Opportunities[^\n]*\n([\s\S]*?)(?=\n## |\Z)', content)
        if opportunities_section:
            summary.opportunities = self._extract_list_items(opportunities_section.group(1))

        # Extract threats
        threats_section = re.search(r'## Threats[^\n]*\n([\s\S]*?)(?=\n## |\Z)', content)
        if threats_section:
            summary.threats = self._extract_list_items(threats_section.group(1))

        # Extract priorities
        priorities_section = re.search(r'## Strategic Priorities([\s\S]*?)(?=\n## |\Z)', content)
        if priorities_section:
            for period in ['Immediate', 'Medium-Term', 'Long-Term']:
                period_match = re.search(f'### {period}[^\n]*\n([\s\S]*?)(?=###|\Z)', priorities_section.group(1))
                if period_match:
                    items = []
                    for line in period_match.group(1).split('\n'):
                        if re.match(r'^\d+\.', line.strip()):
                            items.append(re.sub(r'^\d+\.\s*', '', line.strip()))
                    summary.priorities[period.lower().replace('-', '_')] = items

        # Extract metrics
        metrics_section = re.search(r'## Success Metrics([\s\S]*?)(?=\n## |\Z)', content)
        if metrics_section:
            table_rows = re.findall(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', metrics_section.group(1))
            for row in table_rows:
                metric_name = row[0].strip().lower().replace(' ', '_')
                if metric_name not in ['metric', '------', '']:
                    summary.metrics[metric_name] = {
                        "current": row[1].strip(),
                        "target": row[2].strip()
                    }

        return summary

    def _parse_seo_keywords(self, path: Path) -> List[SEOKeywordData]:
        """Parse SEO keyword rankings markdown"""
        if not path.exists():
            return []

        content = path.read_text()
        keywords = []

        # Parse primary keywords table
        primary_section = re.search(r'### Primary Keywords([\s\S]*?)(?=###|\Z)', content)
        if primary_section:
            rows = re.findall(
                r'\|\s*"?([^"|]+)"?\s*\|\s*#?(\d+|~#?\d+|Unknown|Not ranking)\s*\|\s*([^|]+)\s*\|',
                primary_section.group(1)
            )
            for row in rows:
                if row[0].strip().lower() not in ['keyword', '------']:
                    rank = None
                    rank_str = row[1].strip().replace('~', '').replace('#', '')
                    try:
                        rank = int(rank_str)
                    except:
                        pass
                    keywords.append(SEOKeywordData(
                        keyword=row[0].strip(),
                        current_rank=rank,
                        top_ranker=row[2].strip(),
                        tier="primary"
                    ))

        # Parse secondary keywords
        secondary_section = re.search(r'### Secondary Keywords[^\n]*\n([\s\S]*?)(?=###|---|\Z)', content)
        if secondary_section:
            rows = re.findall(r'\|\s*"?([^"|]+)"?\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', secondary_section.group(1))
            for row in rows:
                if row[0].strip().lower() not in ['keyword', '------', 'current status']:
                    keywords.append(SEOKeywordData(
                        keyword=row[0].strip(),
                        current_rank=None,
                        opportunity=row[2].strip(),
                        tier="secondary"
                    ))

        return keywords

    def _parse_gbp_profile(self, path: Path) -> GBPData:
        """Parse GBP profile JSON"""
        if not path.exists():
            raise FileNotFoundError(f"GBP profile not found: {path}")

        with open(path) as f:
            data = json.load(f)

        # Extract rating info
        rating_info = data.get("rating", {})

        return GBPData(
            title=data.get("title", ""),
            rating=rating_info.get("value", 0),
            review_count=rating_info.get("votes_count", 0),
            address=data.get("address", ""),
            place_id=data.get("place_id", ""),
            categories=data.get("category_ids", []),
            place_topics=data.get("place_topics", {}),
            rating_distribution=data.get("rating_distribution", {}),
            people_also_search=data.get("people_also_search", []),
            attributes=data.get("attributes", {}),
            work_hours=data.get("work_time", {}).get("work_hours", {}),
            description=data.get("description"),
            phone=data.get("phone"),
            domain=data.get("domain"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude")
        )

    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from markdown section"""
        items = []
        # Match numbered items (1. Item) and bullet points (- Item, * Item)
        patterns = [
            r'^\s*\d+\.\s*\*\*([^*]+)\*\*',  # 1. **Bold item**
            r'^\s*\d+\.\s*([^\n]+)',          # 1. Item
            r'^\s*[-*]\s*\*\*([^*]+)\*\*',    # - **Bold item**
            r'^\s*[-*]\s*([^\n]+)',           # - Item
        ]

        for line in text.split('\n'):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    item = match.group(1).strip()
                    if item and item not in items:
                        items.append(item)
                    break

        return items[:10]  # Limit to 10 items
