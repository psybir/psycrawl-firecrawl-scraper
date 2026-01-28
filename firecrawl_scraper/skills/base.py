"""
BaseSkill - Foundation for all PsyCrawl skills

Implements the Psybir methodology: Evidence -> Hypothesis -> Design -> Build -> Measure -> Iterate

Skills follow the marketingskills pattern:
1. Assessment-first (check context, gather info)
2. Framework-based analysis (prioritized, structured)
3. Decision-grade output (geo-tagged, actionable findings)
4. Cross-skill routing (related skills for follow-up)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
import yaml

from ..models.geo import GeoScope, GeoBucket, GeoTag, Location

logger = logging.getLogger(__name__)


class FindingImpact(str, Enum):
    """Impact level for findings"""
    CRITICAL = "critical"  # Blocking issues
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingPriority(str, Enum):
    """Priority ranking for findings"""
    P1 = "P1"  # Fix immediately
    P2 = "P2"  # Fix soon
    P3 = "P3"  # Plan to fix
    P4 = "P4"  # Nice to have
    P5 = "P5"  # Future consideration


@dataclass
class GeoContext:
    """
    Psybir geo-tagging context for all skill outputs.

    Every finding, entity, and analysis must be tagged with geographic context
    to enable the 3D scoring system (Local Pack + Organic Local + Domestic).
    """
    geo_scope: GeoScope = GeoScope.LOCAL_RADIUS
    geo_bucket: GeoBucket = GeoBucket.BUCKET_0_10
    location_cluster: str = ""
    confidence_score: float = 0.0  # 0-1 based on data freshness/source
    last_verified: datetime = field(default_factory=datetime.now)
    primary_location: Optional[GeoTag] = None
    service_areas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "geo_scope": self.geo_scope.value,
            "geo_bucket": self.geo_bucket.value,
            "location_cluster": self.location_cluster,
            "confidence_score": self.confidence_score,
            "last_verified": self.last_verified.isoformat(),
            "primary_location": self.primary_location.model_dump() if self.primary_location else None,
            "service_areas": self.service_areas,
        }


@dataclass
class Finding:
    """
    A single evidence-based finding from a skill analysis.

    Follows the Psybir evidence chain:
    Issue -> Evidence -> Impact -> Fix -> Priority
    """
    issue: str
    evidence: str  # How discovered (tool, method, URL)
    impact: FindingImpact
    fix: str  # Specific, actionable recommendation
    priority: FindingPriority
    geo_context: Optional[GeoContext] = None
    category: str = ""  # Finding category (e.g., "local_seo", "technical", "content")
    confidence: float = 1.0  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue": self.issue,
            "evidence": self.evidence,
            "impact": self.impact.value,
            "fix": self.fix,
            "priority": self.priority.value,
            "geo_context": self.geo_context.to_dict() if self.geo_context else None,
            "category": self.category,
            "confidence": self.confidence,
        }


@dataclass
class DecisionStatement:
    """
    Decision-grade output statement.

    Instead of vague findings, provide actionable decisions:
    "Choose X if you need Y in [location]"
    """
    choose_option: str
    if_condition: str
    context: str = ""
    geo_context: Optional[GeoContext] = None

    def __str__(self) -> str:
        return f"**Choose {self.choose_option} if**: {self.if_condition}"


@dataclass
class ThreeDScore:
    """
    Psybir 3D Scoring System for local lead generation.

    Scores entities on three dimensions:
    1. Local Pack Probability - Chance of appearing in Google's local 3-pack
    2. Organic Local Probability - Chance of ranking for local intent queries
    3. Domestic Organic Probability - Chance of ranking nationally
    """
    local_pack_probability: float = 0.0  # 0-100%
    local_pack_evidence: str = ""
    organic_local_probability: float = 0.0  # 0-100%
    organic_local_evidence: str = ""
    domestic_organic_probability: float = 0.0  # 0-100%
    domestic_organic_evidence: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "local_pack_probability": self.local_pack_probability,
            "local_pack_evidence": self.local_pack_evidence,
            "organic_local_probability": self.organic_local_probability,
            "organic_local_evidence": self.organic_local_evidence,
            "domestic_organic_probability": self.domestic_organic_probability,
            "domestic_organic_evidence": self.domestic_organic_evidence,
        }


@dataclass
class AssessmentQuestion:
    """A question to ask during skill assessment phase"""
    question: str
    category: str  # e.g., "target", "geography", "focus"
    options: Optional[List[str]] = None
    default: Optional[str] = None
    required: bool = True


@dataclass
class SkillResult:
    """
    Complete output from a skill execution.

    Contains all Psybir-aligned components:
    - Geo context
    - 3D scoring
    - Decision statements
    - Prioritized findings
    - Recommended actions (Evidence -> Hypothesis -> Design -> Measure)
    """
    skill_name: str
    executed_at: datetime
    geo_context: GeoContext
    three_d_score: Optional[ThreeDScore] = None
    decision_statements: List[DecisionStatement] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    related_skills: List[str] = field(default_factory=list)

    # Psybir Pipeline Recommendations
    evidence_summary: str = ""
    hypothesis: str = ""
    design_recommendation: str = ""
    measure_plan: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "executed_at": self.executed_at.isoformat(),
            "geo_context": self.geo_context.to_dict(),
            "three_d_score": self.three_d_score.to_dict() if self.three_d_score else None,
            "decision_statements": [str(ds) for ds in self.decision_statements],
            "findings": [f.to_dict() for f in self.findings],
            "raw_data": self.raw_data,
            "related_skills": self.related_skills,
            "psybir_pipeline": {
                "evidence": self.evidence_summary,
                "hypothesis": self.hypothesis,
                "design": self.design_recommendation,
                "measure": self.measure_plan,
            },
        }

    def get_findings_by_priority(self) -> Dict[str, List[Finding]]:
        """Group findings by priority level"""
        grouped = {p.value: [] for p in FindingPriority}
        for finding in self.findings:
            grouped[finding.priority.value].append(finding)
        return grouped

    def get_critical_findings(self) -> List[Finding]:
        """Get all critical/blocking findings"""
        return [f for f in self.findings if f.impact == FindingImpact.CRITICAL]


class BaseSkill(ABC):
    """
    Base class for all PsyCrawl skills.

    Implements the Psybir methodology pattern:
    1. assess() - Check context, gather information
    2. execute() - Run framework-based analysis
    3. synthesize() - Produce decision-grade output

    Subclasses must implement these methods.
    """

    def __init__(self, context_manager=None):
        self.context_manager = context_manager
        self.skill_path = Path(__file__).parent / self._get_skill_dir()
        self._metadata = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Skill name (e.g., 'competitor-intel')"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Skill version (e.g., '1.0.0')"""
        pass

    @abstractmethod
    def _get_skill_dir(self) -> str:
        """Return the skill directory name"""
        pass

    @abstractmethod
    def get_assessment_questions(self, existing_context: Dict) -> List[AssessmentQuestion]:
        """
        Return assessment questions for this skill.

        Should check existing_context and skip questions that are already answered.
        """
        pass

    @abstractmethod
    async def execute(self, context: Dict, answers: Dict) -> Dict[str, Any]:
        """
        Execute the skill analysis.

        Args:
            context: Existing context from .psycrawl/
            answers: User answers to assessment questions

        Returns:
            Raw analysis data
        """
        pass

    @abstractmethod
    def synthesize(self, data: Dict[str, Any], geo_context: GeoContext) -> SkillResult:
        """
        Synthesize raw data into decision-grade output.

        Args:
            data: Raw data from execute()
            geo_context: Geographic context for tagging

        Returns:
            Complete SkillResult with findings, scores, decisions
        """
        pass

    def load_reference(self, name: str) -> str:
        """Load a reference file from the skill's references/ directory"""
        ref_path = self.skill_path / 'references' / name
        if ref_path.exists():
            return ref_path.read_text()
        raise FileNotFoundError(f"Reference not found: {ref_path}")

    def load_reference_yaml(self, name: str) -> Dict:
        """Load a YAML reference file"""
        content = self.load_reference(name)
        return yaml.safe_load(content)

    def get_related_skills(self) -> List[str]:
        """Return list of related skill names for cross-routing"""
        return []

    async def run(
        self,
        target: Optional[str] = None,
        geo: Optional[str] = None,
        focus: Optional[str] = None,
        **kwargs
    ) -> SkillResult:
        """
        Full skill execution pipeline.

        1. Load existing context
        2. Run assessment (gather missing info)
        3. Execute analysis
        4. Synthesize decision-grade output
        """
        # Load existing context
        context = {}
        if self.context_manager:
            context = await self.context_manager.load_context()

        # Build geo context from parameters or context
        geo_context = self._build_geo_context(geo, context)

        # Prepare answers from kwargs and existing context
        answers = {
            'target': target,
            'geo': geo,
            'focus': focus or 'comprehensive',
            **kwargs,
            **context.get('answers', {}),
        }

        # Execute analysis
        raw_data = await self.execute(context, answers)

        # Synthesize results
        result = self.synthesize(raw_data, geo_context)
        result.related_skills = self.get_related_skills()

        return result

    def _build_geo_context(self, geo: Optional[str], context: Dict) -> GeoContext:
        """Build GeoContext from parameters or existing context"""
        geo_config = context.get('geography', {})

        # Parse geo string if provided (e.g., "Pittsburgh, PA" or "Pittsburgh Metro")
        location_cluster = geo or geo_config.get('primary_market', '')
        geo_scope_str = geo_config.get('geo_scope', 'local_radius')
        geo_bucket_str = geo_config.get('geo_bucket', '0-10')

        try:
            geo_scope = GeoScope(geo_scope_str)
        except ValueError:
            geo_scope = GeoScope.LOCAL_RADIUS

        try:
            geo_bucket = GeoBucket(geo_bucket_str)
        except ValueError:
            geo_bucket = GeoBucket.BUCKET_0_10

        return GeoContext(
            geo_scope=geo_scope,
            geo_bucket=geo_bucket,
            location_cluster=location_cluster,
            confidence_score=1.0 if geo else 0.8,
            service_areas=geo_config.get('service_areas', []),
        )


__all__ = [
    'BaseSkill',
    'GeoContext',
    'Finding',
    'FindingImpact',
    'FindingPriority',
    'DecisionStatement',
    'ThreeDScore',
    'AssessmentQuestion',
    'SkillResult',
]
