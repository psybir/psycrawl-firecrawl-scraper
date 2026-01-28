"""
Research Integration - Transform research data into pipeline models

Converts loaded research data from ResearchDataLoader into canonical
pipeline models (CompetitorProfile, Finding, ActionableInsight, etc.)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib

from ..loaders.research_data_loader import (
    ResearchData,
    CompetitorData,
    GBPData,
    SEOKeywordData,
    MarketGap,
    CompetitiveMoat,
    ExecutiveSummary,
)
from ..models import (
    CompetitorProfile,
    TrustSignals,
    ConversionMechanics,
    SEOStructure,
    BacklinkProfile,
    ThreatLevel,
    Finding,
    FindingType,
    FindingCategory,
    Severity,
    DataPoints,
    FindingsReport,
    ActionableInsight,
    InsightType,
    InsightStatus,
    Evidence,
    ExpectedImpact,
    ImpactLevel,
    EffortLevel,
    InsightReport,
    Client,
    GBPProfile,
)


def _generate_id(prefix: str, name: str) -> str:
    """Generate a consistent ID from name"""
    slug = name.lower().replace(' ', '-').replace('.', '')[:20]
    hash_suffix = hashlib.md5(name.encode()).hexdigest()[:6]
    return f"{prefix}-{slug}-{hash_suffix}"


class ResearchIntegration:
    """Transform research data into pipeline models"""

    def __init__(self, research_data: ResearchData):
        self.research = research_data
        self._competitor_profiles: Optional[List[CompetitorProfile]] = None
        self._findings: Optional[FindingsReport] = None
        self._insights: Optional[InsightReport] = None

    def build_competitor_profiles(self) -> List[CompetitorProfile]:
        """Build CompetitorProfile models from research competitors"""
        if self._competitor_profiles is not None:
            return self._competitor_profiles

        profiles = []

        for comp in self.research.competitors:
            profile = CompetitorProfile(
                id=_generate_id("comp", comp.name),
                domain=self._guess_domain(comp.name),
                name=comp.name,
                trust_signals=TrustSignals(
                    review_count=comp.review_count,
                    rating=comp.rating,
                ),
                conversion_mechanics=ConversionMechanics(),
                seo_structure=SEOStructure(),
                backlinks=BacklinkProfile(),
                overall_threat_level=self._map_threat_level(comp.threat_level),
                strengths=comp.strengths,
                weaknesses=comp.weaknesses,
            )

            # Calculate scores
            profile.trust_signals.calculate_trust_score('escape_room')
            profile.conversion_mechanics.calculate_conversion_score('escape_room')
            profiles.append(profile)

        # Add competitors from GBP "people_also_search" if available
        if self.research.gbp_profile:
            for also_search in self.research.gbp_profile.people_also_search:
                # Skip if already in list
                if any(p.name.lower() == also_search.get('title', '').lower() for p in profiles):
                    continue

                rating_info = also_search.get('rating', {})
                profile = CompetitorProfile(
                    id=_generate_id("comp", also_search.get('title', 'unknown')),
                    domain=self._guess_domain(also_search.get('title', '')),
                    name=also_search.get('title', 'Unknown'),
                    trust_signals=TrustSignals(
                        review_count=rating_info.get('votes_count'),
                        rating=rating_info.get('value'),
                    ),
                    conversion_mechanics=ConversionMechanics(),
                    seo_structure=SEOStructure(),
                    backlinks=BacklinkProfile(),
                    overall_threat_level=self._determine_threat_from_reviews(
                        rating_info.get('votes_count', 0),
                        rating_info.get('value', 0)
                    ),
                )
                profile.trust_signals.calculate_trust_score('escape_room')
                profiles.append(profile)

        self._competitor_profiles = profiles
        return profiles

    def build_findings(self) -> FindingsReport:
        """Build findings from research analysis"""
        if self._findings is not None:
            return self._findings

        findings = []

        # Finding: Review Gap (if GBP data available)
        if self.research.gbp_profile:
            our_reviews = self.research.gbp_profile.review_count
            for comp in self.research.competitors:
                if comp.review_count and comp.review_count > our_reviews:
                    gap_ratio = comp.review_count / our_reviews
                    findings.append(Finding(
                        id=_generate_id("find", f"review-gap-{comp.name}"),
                        finding_type=FindingType.GAP,
                        category=FindingCategory.TRUST,
                        observation=f"Review volume gap: {comp.name} has {comp.review_count} reviews vs our {our_reviews} ({gap_ratio:.1f}x more)",
                        details=f"{comp.name} has significantly more review volume, potentially impacting local pack visibility and social proof",
                        severity=Severity.HIGH if gap_ratio > 1.5 else Severity.MEDIUM,
                        source_refs=[comp.name],
                        competitor_refs=[comp.name],
                        confidence=0.9,
                        data_points=DataPoints(
                            our_value=str(our_reviews),
                            competitor_values={comp.name: str(comp.review_count)},
                            delta=float(comp.review_count - our_reviews)
                        )
                    ))

        # Findings from market gaps
        for gap in self.research.market_gaps:
            findings.append(Finding(
                id=_generate_id("find", f"market-gap-{gap.segment}"),
                finding_type=FindingType.OPPORTUNITY,
                category=FindingCategory.MARKET,
                observation=f"Market gap identified: {gap.segment}",
                details=f"{gap.description}. Opportunity: {gap.opportunity}",
                severity=Severity.MEDIUM,
                source_refs=["competitive_analysis"],
                confidence=0.8,
            ))

        # Findings from moats
        for moat in self.research.moats:
            findings.append(Finding(
                id=_generate_id("find", f"moat-{moat.feature}"),
                finding_type=FindingType.STRENGTH,
                category=FindingCategory.POSITIONING,
                observation=f"Competitive moat: {moat.feature}",
                details=moat.description,
                severity=Severity.LOW,  # Strengths don't have severity
                source_refs=["competitive_analysis"],
                confidence=0.95,
            ))

        # Findings from SEO keywords
        for kw in self.research.seo_keywords:
            if kw.current_rank and kw.current_rank > 1:
                findings.append(Finding(
                    id=_generate_id("find", f"seo-rank-{kw.keyword}"),
                    finding_type=FindingType.OPPORTUNITY,
                    category=FindingCategory.SEO,
                    observation=f"SEO opportunity: Currently #{kw.current_rank} for '{kw.keyword}'",
                    details=f"Top ranker: {kw.top_ranker}. Target: #1 position.",
                    severity=Severity.MEDIUM if kw.tier == "primary" else Severity.LOW,
                    source_refs=["seo_analysis"],
                    confidence=0.85,
                ))
            elif kw.current_rank is None and kw.tier == "secondary":
                findings.append(Finding(
                    id=_generate_id("find", f"seo-missing-{kw.keyword}"),
                    finding_type=FindingType.GAP,
                    category=FindingCategory.SEO,
                    observation=f"Not ranking for '{kw.keyword}'",
                    details=f"Opportunity: {kw.opportunity or 'Create content targeting this keyword'}",
                    severity=Severity.MEDIUM,
                    source_refs=["seo_analysis"],
                    confidence=0.8,
                ))

        # Findings from executive summary
        if self.research.executive_summary:
            exec_sum = self.research.executive_summary
            for weakness in exec_sum.weaknesses[:5]:
                findings.append(Finding(
                    id=_generate_id("find", f"weakness-{weakness[:20]}"),
                    finding_type=FindingType.GAP,
                    category=FindingCategory.CONVERSION,
                    observation=weakness,
                    severity=Severity.HIGH if "CRITICAL" in weakness.upper() else Severity.MEDIUM,
                    source_refs=["executive_summary"],
                    confidence=0.9,
                ))

        self._findings = FindingsReport(
            client_id=self.research.client_name,
            findings=findings,
            generated_at=datetime.now()
        )
        return self._findings

    def build_insights(self) -> InsightReport:
        """Build actionable insights from findings"""
        if self._insights is not None:
            return self._insights

        insights = []
        findings = self.build_findings()

        # Insight: Close review gap
        review_gap_findings = [f for f in findings.findings
                               if f.finding_type == FindingType.GAP
                               and f.category == FindingCategory.TRUST
                               and "review" in f.observation.lower()]
        if review_gap_findings:
            insights.append(ActionableInsight(
                id=_generate_id("insight", "review-acceleration"),
                problem="Review volume significantly behind primary competitor",
                hypothesis="Increasing review velocity will improve local pack ranking and social proof",
                evidence=[Evidence(
                    source_type="competitive_analysis",
                    source_id=f.id,
                    observation=f.observation
                ) for f in review_gap_findings],
                spec_change="Implement review generation campaign: QR codes, post-experience emails, staff training",
                expected_impact=ExpectedImpact(
                    rank_impact=ImpactLevel.HIGH,
                    cvr_impact=ImpactLevel.MEDIUM,
                    trust_impact=ImpactLevel.HIGH,
                ),
                priority_score=85,
                effort_estimate=EffortLevel.MEDIUM,
                insight_type=InsightType.QUICK_WIN,
                status=InsightStatus.PROPOSED,
            ))

        # Insight: Content expansion
        seo_gaps = [f for f in findings.findings
                    if f.category == FindingCategory.SEO
                    and (f.finding_type == FindingType.GAP or f.finding_type == FindingType.OPPORTUNITY)]
        if seo_gaps:
            insights.append(ActionableInsight(
                id=_generate_id("insight", "content-expansion"),
                problem="Insufficient content depth for keyword targeting",
                hypothesis="Creating dedicated pages for experiences and locations will capture more organic traffic",
                evidence=[Evidence(
                    source_type="seo_analysis",
                    source_id=f.id,
                    observation=f.observation
                ) for f in seo_gaps[:5]],
                spec_change="Create: (1) Individual experience pages for each room, (2) Location landing pages (Allentown, Easton), (3) Blog content targeting long-tail keywords",
                expected_impact=ExpectedImpact(
                    rank_impact=ImpactLevel.HIGH,
                    cvr_impact=ImpactLevel.MEDIUM,
                    trust_impact=ImpactLevel.LOW,
                ),
                priority_score=80,
                effort_estimate=EffortLevel.HIGH,
                insight_type=InsightType.STRATEGIC,
                status=InsightStatus.PROPOSED,
            ))

        # Insight: Leverage moats
        moat_findings = [f for f in findings.findings if f.finding_type == FindingType.STRENGTH]
        if moat_findings:
            insights.append(ActionableInsight(
                id=_generate_id("insight", "moat-messaging"),
                problem="Unique differentiators not prominently communicated",
                hypothesis="Emphasizing GAVIN AI, multiple endings, and adaptive difficulty will increase conversion and justify premium positioning",
                evidence=[Evidence(
                    source_type="competitive_analysis",
                    source_id=f.id,
                    observation=f.observation
                ) for f in moat_findings],
                spec_change="Update homepage hero, experience pages, and all CTAs to prominently feature: (1) GAVIN AI character, (2) Multiple story endings, (3) Adaptive difficulty system",
                expected_impact=ExpectedImpact(
                    rank_impact=ImpactLevel.LOW,
                    cvr_impact=ImpactLevel.HIGH,
                    trust_impact=ImpactLevel.MEDIUM,
                ),
                priority_score=75,
                effort_estimate=EffortLevel.LOW,
                insight_type=InsightType.QUICK_WIN,
                status=InsightStatus.PROPOSED,
            ))

        # Insight: Target underserved segments
        market_gaps = [f for f in findings.findings
                       if f.category == FindingCategory.MARKET
                       and f.finding_type == FindingType.OPPORTUNITY]
        if market_gaps:
            insights.append(ActionableInsight(
                id=_generate_id("insight", "market-segments"),
                problem="Underserved market segments not being targeted",
                hypothesis="Creating dedicated landing pages for corporate team building and tech enthusiasts will capture new customer segments",
                evidence=[Evidence(
                    source_type="market_analysis",
                    source_id=f.id,
                    observation=f.observation
                ) for f in market_gaps],
                spec_change="Create: (1) /team-building page with corporate packages, (2) /tech-experience page for gamers/tech enthusiasts, (3) Consider expanding weekday hours for corporate bookings",
                expected_impact=ExpectedImpact(
                    rank_impact=ImpactLevel.MEDIUM,
                    cvr_impact=ImpactLevel.HIGH,
                    trust_impact=ImpactLevel.LOW,
                ),
                priority_score=70,
                effort_estimate=EffortLevel.MEDIUM,
                insight_type=InsightType.STRATEGIC,
                status=InsightStatus.PROPOSED,
            ))

        self._insights = InsightReport(
            client_id=self.research.client_name,
            insights=insights,
            generated_at=datetime.now()
        )
        return self._insights

    def get_market_gaps(self) -> List[str]:
        """Get list of market gap descriptions"""
        return [f"{gap.segment}: {gap.description}" for gap in self.research.market_gaps]

    def get_moat_identification(self) -> List[str]:
        """Get list of competitive moats"""
        return [f"{moat.feature}: {moat.description}" for moat in self.research.moats]

    def get_seo_opportunities(self) -> List[Dict[str, Any]]:
        """Get SEO keyword opportunities"""
        return [
            {
                "keyword": kw.keyword,
                "current_rank": kw.current_rank,
                "top_ranker": kw.top_ranker,
                "opportunity": kw.opportunity,
                "tier": kw.tier,
            }
            for kw in self.research.seo_keywords
        ]

    def get_positioning_map(self) -> Optional[str]:
        """Get ASCII competitive positioning map"""
        return self.research.positioning_map

    def build_client_gbp_profile(self) -> Optional[GBPProfile]:
        """Build GBPProfile model from research data"""
        if not self.research.gbp_profile:
            return None

        gbp = self.research.gbp_profile
        return GBPProfile(
            place_id=gbp.place_id,
            rating=gbp.rating,
            review_count=gbp.review_count,
            categories=gbp.categories,
        )

    def _guess_domain(self, name: str) -> str:
        """Guess domain from competitor name"""
        name_lower = name.lower()
        if "captured" in name_lower:
            return "capturedlv.com"
        elif "off-center" in name_lower or "off center" in name_lower:
            return "offcenterescaperooms.com"
        elif "twisted" in name_lower:
            return "twistedescapes.com"
        elif "amazing" in name_lower:
            return "amazingescape.com"
        elif "cyber quest" in name_lower:
            return "windcreekbethlehem.com"
        else:
            slug = name_lower.replace(' ', '').replace('.', '')
            return f"{slug}.com"

    def _map_threat_level(self, level: str) -> ThreatLevel:
        """Map string threat level to enum"""
        mapping = {
            "high": ThreatLevel.HIGH,
            "medium": ThreatLevel.MEDIUM,
            "low": ThreatLevel.LOW,
            "critical": ThreatLevel.CRITICAL,
        }
        return mapping.get(level.lower(), ThreatLevel.MEDIUM)

    def _determine_threat_from_reviews(self, review_count: int, rating: float) -> ThreatLevel:
        """Determine threat level from review metrics"""
        if not self.research.gbp_profile:
            return ThreatLevel.MEDIUM

        our_reviews = self.research.gbp_profile.review_count

        # If they have significantly more reviews, they're a higher threat
        if review_count > our_reviews * 2:
            return ThreatLevel.HIGH
        elif review_count > our_reviews * 1.5:
            return ThreatLevel.MEDIUM
        elif review_count > our_reviews:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
