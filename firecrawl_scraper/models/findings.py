"""
Finding models - Raw observations from analysis
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

from .geo import GeoTag


class FindingType(str, Enum):
    """Types of findings"""
    GAP = "gap"
    STRENGTH = "strength"
    OPPORTUNITY = "opportunity"
    THREAT = "threat"
    PATTERN = "pattern"
    ANOMALY = "anomaly"


class FindingCategory(str, Enum):
    """Finding categories"""
    TRUST = "trust"
    CONVERSION = "conversion"
    CONTENT = "content"
    TECHNICAL = "technical"
    BACKLINKS = "backlinks"
    LOCAL_SEO = "local_seo"
    STRUCTURE = "structure"
    UX = "ux"
    # Added for research integration
    MARKET = "market"
    SEO = "seo"
    POSITIONING = "positioning"


class Severity(str, Enum):
    """Finding severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DataPoints(BaseModel):
    """Supporting data for a finding"""
    our_value: Optional[Union[str, int, float, bool]] = None
    competitor_values: Optional[Dict[str, Union[str, int, float, bool]]] = None
    benchmark: Optional[Union[str, int, float]] = None
    delta: Optional[float] = None
    percentile: Optional[float] = None


class Finding(BaseModel):
    """Raw observation from analysis - input to Actionable Insight generation"""
    id: str
    finding_type: FindingType
    category: FindingCategory
    observation: str = Field(..., description="What was observed - the raw fact")
    details: Optional[str] = None
    source_refs: List[str] = Field(default_factory=list)
    competitor_refs: List[str] = Field(default_factory=list)
    geo_context: Optional[GeoTag] = None
    service_context: Optional[str] = None
    confidence: float = Field(0.8, ge=0, le=1)
    data_points: Optional[DataPoints] = None
    severity: Severity = Severity.MEDIUM
    discovered_at: datetime = Field(default_factory=datetime.now)
    rule_id: Optional[str] = None

    @property
    def is_actionable(self) -> bool:
        """Check if finding is actionable"""
        return self.finding_type in [FindingType.GAP, FindingType.OPPORTUNITY, FindingType.THREAT]

    @property
    def priority_score(self) -> float:
        """Calculate priority based on severity and confidence"""
        severity_weights = {
            Severity.CRITICAL: 1.0,
            Severity.HIGH: 0.75,
            Severity.MEDIUM: 0.5,
            Severity.LOW: 0.25
        }
        return severity_weights[self.severity] * self.confidence * 100


class FindingGroup(BaseModel):
    """Group of related findings"""
    category: FindingCategory
    findings: List[Finding] = Field(default_factory=list)
    summary: Optional[str] = None

    @property
    def highest_severity(self) -> Severity:
        """Get highest severity in group"""
        if not self.findings:
            return Severity.LOW
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        for severity in severity_order:
            if any(f.severity == severity for f in self.findings):
                return severity
        return Severity.LOW

    @property
    def total_count(self) -> int:
        return len(self.findings)


class FindingsReport(BaseModel):
    """Complete findings report"""
    client_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    findings: List[Finding] = Field(default_factory=list)
    grouped_by_category: Dict[str, FindingGroup] = Field(default_factory=dict)
    grouped_by_type: Dict[str, List[Finding]] = Field(default_factory=dict)

    def group_findings(self):
        """Organize findings by category and type"""
        self.grouped_by_category = {}
        self.grouped_by_type = {}

        for finding in self.findings:
            # Group by category
            cat = finding.category.value
            if cat not in self.grouped_by_category:
                self.grouped_by_category[cat] = FindingGroup(category=finding.category)
            self.grouped_by_category[cat].findings.append(finding)

            # Group by type
            ftype = finding.finding_type.value
            if ftype not in self.grouped_by_type:
                self.grouped_by_type[ftype] = []
            self.grouped_by_type[ftype].append(finding)

    @property
    def gaps(self) -> List[Finding]:
        return [f for f in self.findings if f.finding_type == FindingType.GAP]

    @property
    def opportunities(self) -> List[Finding]:
        return [f for f in self.findings if f.finding_type == FindingType.OPPORTUNITY]

    @property
    def critical_findings(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    @property
    def actionable_findings(self) -> List[Finding]:
        return [f for f in self.findings if f.is_actionable]
