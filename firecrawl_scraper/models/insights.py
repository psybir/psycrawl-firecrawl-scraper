"""
Actionable Insight models - THE MISSING BRIDGE between findings and specs
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .geo import GeoTag


class ImpactLevel(str, Enum):
    """Impact level for outcomes"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class EffortLevel(str, Enum):
    """Implementation effort"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InsightType(str, Enum):
    """Types of actionable insights"""
    TRUST_GAP = "trust_gap"
    CONVERSION_GAP = "conversion_gap"
    CONTENT_GAP = "content_gap"
    TECHNICAL_FIX = "technical_fix"
    BACKLINK_OPPORTUNITY = "backlink_opportunity"
    LOCAL_SEO_FIX = "local_seo_fix"
    STRUCTURE_IMPROVEMENT = "structure_improvement"
    COMPETITIVE_RESPONSE = "competitive_response"


class InsightStatus(str, Enum):
    """Insight workflow status"""
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class Evidence(BaseModel):
    """Evidence supporting an insight"""
    source_type: str
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    observation: str
    data_point: Optional[Any] = None


class ExpectedImpact(BaseModel):
    """Predicted outcomes from implementing insight"""
    rank_impact: ImpactLevel = ImpactLevel.MEDIUM
    cvr_impact: ImpactLevel = ImpactLevel.MEDIUM
    trust_impact: ImpactLevel = ImpactLevel.LOW
    speed_impact: ImpactLevel = ImpactLevel.MEDIUM
    traffic_estimate: Optional[str] = None
    conversion_estimate: Optional[str] = None


class SpecDetails(BaseModel):
    """Detailed implementation spec"""
    page_type: Optional[str] = None
    component: Optional[str] = None
    content_requirements: List[str] = Field(default_factory=list)
    design_requirements: List[str] = Field(default_factory=list)
    placement: Optional[str] = None
    copy_guidelines: Optional[str] = None
    schema_requirements: List[str] = Field(default_factory=list)


class ActionableInsight(BaseModel):
    """THE MISSING BRIDGE - translates findings into spec changes with clear rationale"""
    id: str
    title: Optional[str] = None
    problem: str = Field(..., description="What's missing/weak")
    hypothesis: str = Field(..., description="Why it matters")
    evidence: List[Evidence] = Field(default_factory=list)
    finding_refs: List[str] = Field(default_factory=list)
    spec_change: str = Field(..., description="What to build/change")
    spec_details: Optional[SpecDetails] = None
    expected_impact: ExpectedImpact = Field(default_factory=ExpectedImpact)
    priority_score: float = Field(50, ge=0, le=100)
    effort_estimate: EffortLevel = EffortLevel.MEDIUM
    dependencies: List[str] = Field(default_factory=list)
    geo_context: Optional[GeoTag] = None
    service_context: Optional[str] = None
    insight_type: InsightType = InsightType.CONTENT_GAP
    status: InsightStatus = InsightStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None

    def calculate_priority(self) -> float:
        """Calculate priority score based on impact and effort"""
        # Impact weights
        impact_weights = {ImpactLevel.HIGH: 3, ImpactLevel.MEDIUM: 2, ImpactLevel.LOW: 1, ImpactLevel.NONE: 0}
        effort_weights = {EffortLevel.LOW: 3, EffortLevel.MEDIUM: 2, EffortLevel.HIGH: 1}

        impact_score = (
            impact_weights[self.expected_impact.rank_impact] +
            impact_weights[self.expected_impact.cvr_impact] +
            impact_weights[self.expected_impact.trust_impact]
        ) / 9 * 100  # Normalize to 0-100

        effort_multiplier = effort_weights[self.effort_estimate] / 3

        # Speed bonus - faster results = higher priority
        speed_bonus = impact_weights[self.expected_impact.speed_impact] * 5

        self.priority_score = (impact_score * effort_multiplier) + speed_bonus
        return self.priority_score

    @property
    def is_quick_win(self) -> bool:
        """Check if this is a quick win (high impact, low effort)"""
        high_impact = (
            self.expected_impact.rank_impact == ImpactLevel.HIGH or
            self.expected_impact.cvr_impact == ImpactLevel.HIGH
        )
        return high_impact and self.effort_estimate == EffortLevel.LOW

    @property
    def summary(self) -> str:
        """Generate a summary line"""
        return f"[{self.insight_type.value}] {self.title or self.problem[:50]} (Priority: {self.priority_score:.0f})"


class InsightReport(BaseModel):
    """Complete insights report"""
    client_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    insights: List[ActionableInsight] = Field(default_factory=list)

    @property
    def pending_insights(self) -> List[ActionableInsight]:
        return [i for i in self.insights if i.status == InsightStatus.PENDING]

    @property
    def quick_wins(self) -> List[ActionableInsight]:
        return [i for i in self.insights if i.is_quick_win]

    @property
    def by_priority(self) -> List[ActionableInsight]:
        return sorted(self.insights, key=lambda x: x.priority_score, reverse=True)

    @property
    def by_type(self) -> Dict[str, List[ActionableInsight]]:
        grouped = {}
        for insight in self.insights:
            key = insight.insight_type.value
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(insight)
        return grouped

    def get_top_priorities(self, n: int = 10) -> List[ActionableInsight]:
        """Get top N priority insights"""
        return self.by_priority[:n]

    def filter_by_service(self, service: str) -> List[ActionableInsight]:
        """Filter insights by service context"""
        return [i for i in self.insights if i.service_context == service]

    def filter_by_type(self, insight_type: InsightType) -> List[ActionableInsight]:
        """Filter insights by type"""
        return [i for i in self.insights if i.insight_type == insight_type]
