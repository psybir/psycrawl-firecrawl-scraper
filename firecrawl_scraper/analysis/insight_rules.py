"""
Insight Rules - Pattern-based rules for generating findings from competitor analysis

Each rule analyzes specific aspects of competitor data and client context
to generate findings that feed into actionable insights.

Vertical-aware: Rules are dispatched based on client vertical type.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type
from datetime import datetime
import uuid

from ..models import (
    Client,
    CompetitorProfile,
    Finding,
    FindingType,
    FindingCategory,
    Severity,
    DataPoints,
    Vertical,
)
from ..models.entities import (
    BLUE_COLLAR_VERTICALS,
    ENTERTAINMENT_VERTICALS,
    HEALTHCARE_VERTICALS,
)

logger = logging.getLogger(__name__)


class InsightRule(ABC):
    """Base class for insight rules"""

    rule_id: str = "base_rule"
    category: FindingCategory = FindingCategory.TRUST
    description: str = "Base insight rule"

    def __init__(self, client: Client, competitors: List[CompetitorProfile]):
        self.client = client
        self.competitors = competitors
        self.findings: List[Finding] = []

    @abstractmethod
    def evaluate(self) -> List[Finding]:
        """Evaluate the rule and return findings"""
        pass

    def _create_finding(
        self,
        finding_type: FindingType,
        observation: str,
        severity: Severity = Severity.MEDIUM,
        details: str = None,
        data_points: DataPoints = None,
        competitor_refs: List[str] = None,
    ) -> Finding:
        """Create a finding from this rule"""
        return Finding(
            id=str(uuid.uuid4()),
            finding_type=finding_type,
            category=self.category,
            observation=observation,
            severity=severity,
            details=details,
            data_points=data_points,
            source_refs=[],
            competitor_refs=competitor_refs or [],
            rule_id=self.rule_id,
            discovered_at=datetime.now()
        )


class BacklinkGapRule(InsightRule):
    """Analyze backlink/authority gaps"""

    rule_id = "backlink_gap"
    category = FindingCategory.BACKLINKS
    description = "Compare domain authority and backlink profiles"

    def evaluate(self) -> List[Finding]:
        findings = []

        authorities = [
            c.backlinks.domain_authority
            for c in self.competitors
            if c.backlinks.domain_authority
        ]

        if authorities:
            avg_authority = sum(authorities) / len(authorities)
            max_authority = max(authorities)

            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"Competitor average domain authority: {avg_authority:.0f}/100",
                severity=Severity.HIGH,
                data_points=DataPoints(benchmark=avg_authority)
            ))

            # Find authority leader
            leader = max(self.competitors, key=lambda c: c.backlinks.domain_authority or 0)
            if leader.backlinks.domain_authority:
                findings.append(self._create_finding(
                    finding_type=FindingType.THREAT,
                    observation=f"{leader.domain} leads with authority {leader.backlinks.domain_authority}/100",
                    severity=Severity.HIGH,
                    competitor_refs=[leader.id]
                ))

        return findings


class ReviewVisibilityRule(InsightRule):
    """Analyze review count and visibility patterns"""

    rule_id = "review_visibility"
    category = FindingCategory.TRUST
    description = "Compare review counts and ratings across competitors"

    def evaluate(self) -> List[Finding]:
        findings = []

        reviews = [
            (c, c.trust_signals.review_count)
            for c in self.competitors
            if c.trust_signals.review_count
        ]

        if reviews:
            review_counts = [r[1] for r in reviews]
            avg_reviews = sum(review_counts) / len(review_counts)

            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"Average competitor review count: {avg_reviews:.0f}",
                severity=Severity.MEDIUM,
                data_points=DataPoints(benchmark=avg_reviews)
            ))

            # Check for review leaders
            leader = max(reviews, key=lambda x: x[1])
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{leader[0].domain} leads with {leader[1]} reviews",
                severity=Severity.MEDIUM,
                competitor_refs=[leader[0].id]
            ))

        # Check rating patterns
        ratings = [
            c.trust_signals.rating
            for c in self.competitors
            if c.trust_signals.rating
        ]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating >= 4.5:
                findings.append(self._create_finding(
                    finding_type=FindingType.PATTERN,
                    observation=f"High rating standard in market (avg: {avg_rating:.1f})",
                    severity=Severity.MEDIUM,
                    data_points=DataPoints(benchmark=avg_rating)
                ))

        return findings


class CertificationCheckRule(InsightRule):
    """Check certification and license visibility"""

    rule_id = "certification_check"
    category = FindingCategory.TRUST
    description = "Analyze certification and license display patterns"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_certs = [c for c in self.competitors if c.trust_signals.certifications]
        with_licenses = [c for c in self.competitors if c.trust_signals.licenses_shown]
        with_insurance = [c for c in self.competitors if c.trust_signals.insurance_shown]

        total = len(self.competitors)

        if len(with_certs) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_certs)}/{total} competitors display certifications",
                severity=Severity.MEDIUM,
                details="Certification visibility is industry standard"
            ))

        if len(with_licenses) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_licenses)}/{total} competitors show licenses",
                severity=Severity.MEDIUM
            ))

        if len(with_insurance) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_insurance)}/{total} competitors mention insurance",
                severity=Severity.LOW
            ))

        return findings


class GalleryPresenceRule(InsightRule):
    """Check before/after gallery presence"""

    rule_id = "gallery_presence"
    category = FindingCategory.TRUST
    description = "Analyze visual proof and gallery usage"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_gallery = [c for c in self.competitors if c.trust_signals.before_after_gallery]
        total = len(self.competitors)

        if len(with_gallery) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_gallery)}/{total} competitors have before/after galleries",
                severity=Severity.HIGH,
                details="Visual proof is table stakes in this industry"
            ))
        elif len(with_gallery) < total * 0.3:
            findings.append(self._create_finding(
                finding_type=FindingType.OPPORTUNITY,
                observation="Few competitors have before/after galleries",
                severity=Severity.HIGH,
                details="Opportunity to differentiate with visual proof"
            ))

        return findings


class ServiceAreaCoverageRule(InsightRule):
    """Analyze service area page coverage"""

    rule_id = "service_area_coverage"
    category = FindingCategory.LOCAL_SEO
    description = "Compare service area page strategies"

    def evaluate(self) -> List[Finding]:
        findings = []

        area_counts = [
            (c, len(c.seo_structure.service_area_pages))
            for c in self.competitors
        ]

        if area_counts:
            max_count = max(area_counts, key=lambda x: x[1])
            if max_count[1] >= 5:
                findings.append(self._create_finding(
                    finding_type=FindingType.PATTERN,
                    observation=f"{max_count[0].domain} has {max_count[1]} service area pages",
                    severity=Severity.HIGH,
                    competitor_refs=[max_count[0].id],
                    details="Strong local SEO strategy"
                ))

            avg_pages = sum(a[1] for a in area_counts) / len(area_counts)
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"Average service area pages: {avg_pages:.1f}",
                severity=Severity.MEDIUM,
                data_points=DataPoints(benchmark=avg_pages)
            ))

        return findings


class StickyCTARule(InsightRule):
    """Check sticky CTA/conversion patterns"""

    rule_id = "sticky_cta"
    category = FindingCategory.CONVERSION
    description = "Analyze sticky CTA and conversion element usage"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_sticky = [
            c for c in self.competitors
            if c.conversion_mechanics.sticky_cta or c.conversion_mechanics.sticky_call
        ]
        total = len(self.competitors)

        if len(with_sticky) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_sticky)}/{total} competitors use sticky CTAs",
                severity=Severity.HIGH,
                details="Sticky CTAs are conversion standard"
            ))

        return findings


class ChatWidgetRule(InsightRule):
    """Check live chat adoption"""

    rule_id = "chat_widget"
    category = FindingCategory.CONVERSION
    description = "Analyze live chat and instant communication adoption"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_chat = [c for c in self.competitors if c.conversion_mechanics.chat_widget]

        if len(with_chat) >= 2:
            chat_providers = [c.conversion_mechanics.chat_provider for c in with_chat if c.conversion_mechanics.chat_provider]
            findings.append(self._create_finding(
                finding_type=FindingType.OPPORTUNITY,
                observation=f"{len(with_chat)} competitors offer live chat",
                severity=Severity.MEDIUM,
                details=f"Chat providers used: {', '.join(set(chat_providers)) if chat_providers else 'various'}"
            ))

        return findings


class ContentDepthRule(InsightRule):
    """Analyze content depth and quality"""

    rule_id = "content_depth"
    category = FindingCategory.CONTENT
    description = "Compare content depth across service pages"

    def evaluate(self) -> List[Finding]:
        findings = []

        for comp in self.competitors:
            deep_pages = [
                p for p in comp.seo_structure.service_pages
                if p.word_count and p.word_count > 1500
            ]
            if deep_pages:
                findings.append(self._create_finding(
                    finding_type=FindingType.PATTERN,
                    observation=f"{comp.domain} has {len(deep_pages)} in-depth service pages (>1500 words)",
                    severity=Severity.MEDIUM,
                    competitor_refs=[comp.id]
                ))

        return findings


class GridRankingRule(InsightRule):
    """Analyze local pack/grid rankings"""

    rule_id = "grid_ranking"
    category = FindingCategory.LOCAL_SEO
    description = "Identify local pack dominators and threats"

    def evaluate(self) -> List[Finding]:
        findings = []

        for comp in self.competitors:
            if comp.grid_performance:
                avg_rank = sum(comp.grid_performance.values()) / len(comp.grid_performance)
                if avg_rank <= 3:
                    findings.append(self._create_finding(
                        finding_type=FindingType.THREAT,
                        observation=f"{comp.domain} dominates local pack (avg rank: {avg_rank:.1f})",
                        severity=Severity.CRITICAL,
                        competitor_refs=[comp.id],
                        data_points=DataPoints(competitor_values={comp.domain: avg_rank})
                    ))

        return findings


# ============================================================================
# ENTERTAINMENT VERTICAL RULES
# ============================================================================

class ExperiencePhotoRule(InsightRule):
    """Check experience/venue photo presence for entertainment verticals"""

    rule_id = "experience_photo"
    category = FindingCategory.TRUST
    description = "Analyze experience/room photo quality and coverage"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_photos = [c for c in self.competitors if c.trust_signals.experience_photos]
        total = len(self.competitors)

        if len(with_photos) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_photos)}/{total} competitors showcase experience photos",
                severity=Severity.HIGH,
                details="Experience photos are table stakes for entertainment venues"
            ))

        # Check for promo videos
        with_video = [c for c in self.competitors if c.trust_signals.promo_video]
        if len(with_video) >= total * 0.3:
            findings.append(self._create_finding(
                finding_type=FindingType.OPPORTUNITY,
                observation=f"{len(with_video)}/{total} competitors have promo videos",
                severity=Severity.HIGH,
                details="Video content drives higher engagement and conversions"
            ))

        return findings


class OnlineBookingRule(InsightRule):
    """Check online booking system presence"""

    rule_id = "online_booking"
    category = FindingCategory.CONVERSION
    description = "Analyze online booking adoption and quality"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_booking = [c for c in self.competitors if c.conversion_mechanics.online_booking]
        total = len(self.competitors)

        if len(with_booking) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_booking)}/{total} competitors have online booking",
                severity=Severity.CRITICAL,
                details="Online booking is essential for entertainment businesses"
            ))

            # Check booking providers
            providers = [c.conversion_mechanics.booking_provider for c in with_booking
                        if c.conversion_mechanics.booking_provider]
            if providers:
                findings.append(self._create_finding(
                    finding_type=FindingType.PATTERN,
                    observation=f"Booking providers used: {', '.join(set(providers))}",
                    severity=Severity.LOW
                ))

        # Check availability calendar
        with_calendar = [c for c in self.competitors if c.conversion_mechanics.availability_calendar]
        if len(with_calendar) >= 2:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_calendar)} competitors show real-time availability",
                severity=Severity.HIGH,
                details="Real-time availability reduces booking friction"
            ))

        return findings


class GroupPackagesRule(InsightRule):
    """Check group booking and party package offerings"""

    rule_id = "group_packages"
    category = FindingCategory.CONVERSION
    description = "Analyze group booking and event package offerings"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_group = [c for c in self.competitors if c.conversion_mechanics.group_booking_options]
        with_party = [c for c in self.competitors if c.conversion_mechanics.party_packages]
        with_corporate = [c for c in self.competitors if c.conversion_mechanics.corporate_booking]
        total = len(self.competitors)

        if len(with_party) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_party)}/{total} competitors offer birthday/party packages",
                severity=Severity.HIGH,
                details="Party packages are a major revenue stream for entertainment venues"
            ))

        if len(with_corporate) >= 2:
            findings.append(self._create_finding(
                finding_type=FindingType.OPPORTUNITY,
                observation=f"{len(with_corporate)} competitors target corporate team building",
                severity=Severity.HIGH,
                details="Corporate bookings = higher ticket value, weekday revenue"
            ))

        # Check gift cards
        with_giftcards = [c for c in self.competitors if c.conversion_mechanics.gift_cards]
        if len(with_giftcards) >= total * 0.3:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_giftcards)} competitors sell gift cards",
                severity=Severity.MEDIUM,
                details="Gift cards = prepaid revenue + new customer acquisition"
            ))

        return findings


class UniqueExperienceRule(InsightRule):
    """Analyze unique experience features and differentiators"""

    rule_id = "unique_experience"
    category = FindingCategory.TRUST
    description = "Identify unique experience features that drive competitive advantage"

    def evaluate(self) -> List[Finding]:
        findings = []

        for comp in self.competitors:
            if comp.trust_signals.unique_features:
                findings.append(self._create_finding(
                    finding_type=FindingType.THREAT,
                    observation=f"{comp.domain} differentiators: {', '.join(comp.trust_signals.unique_features[:3])}",
                    severity=Severity.MEDIUM,
                    competitor_refs=[comp.id]
                ))

            if comp.trust_signals.awards_shown:
                findings.append(self._create_finding(
                    finding_type=FindingType.THREAT,
                    observation=f"{comp.domain} displays {len(comp.trust_signals.awards_shown)} awards",
                    severity=Severity.HIGH,
                    competitor_refs=[comp.id],
                    details=f"Awards: {', '.join(comp.trust_signals.awards_shown[:3])}"
                ))

        # Check experience counts
        exp_counts = [(c, c.trust_signals.experience_count) for c in self.competitors
                     if c.trust_signals.experience_count]
        if exp_counts:
            max_exp = max(exp_counts, key=lambda x: x[1])
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{max_exp[0].domain} leads with {max_exp[1]} experiences",
                severity=Severity.MEDIUM,
                competitor_refs=[max_exp[0].id]
            ))

        return findings


class RepeatVisitRule(InsightRule):
    """Check for repeat visit incentives (multiple endings, new experiences)"""

    rule_id = "repeat_visit"
    category = FindingCategory.CONVERSION
    description = "Analyze repeat visit and replay value features"

    def evaluate(self) -> List[Finding]:
        findings = []

        # Check for multiple endings/replay value in unique features
        replay_indicators = ['multiple endings', 'replay', 'different outcomes', 'new experience']
        for comp in self.competitors:
            has_replay = any(
                any(ind in feat.lower() for ind in replay_indicators)
                for feat in comp.trust_signals.unique_features
            )
            if has_replay:
                findings.append(self._create_finding(
                    finding_type=FindingType.THREAT,
                    observation=f"{comp.domain} promotes replay value/multiple outcomes",
                    severity=Severity.HIGH,
                    competitor_refs=[comp.id],
                    details="Multiple endings increase customer lifetime value"
                ))

        return findings


# ============================================================================
# HEALTHCARE VERTICAL RULES
# ============================================================================

class CredentialDisplayRule(InsightRule):
    """Check healthcare credential visibility"""

    rule_id = "credential_display"
    category = FindingCategory.TRUST
    description = "Analyze credential and certification display patterns"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_creds = [c for c in self.competitors if c.trust_signals.credentials_shown]
        with_certs = [c for c in self.competitors if c.trust_signals.board_certifications]
        total = len(self.competitors)

        if len(with_creds) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_creds)}/{total} competitors display practitioner credentials",
                severity=Severity.HIGH,
                details="Credential visibility is essential for healthcare trust"
            ))

        if len(with_certs) >= total * 0.3:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_certs)}/{total} competitors highlight board certifications",
                severity=Severity.MEDIUM
            ))

        return findings


class OnlineSchedulingRule(InsightRule):
    """Check healthcare online scheduling adoption"""

    rule_id = "online_scheduling"
    category = FindingCategory.CONVERSION
    description = "Analyze online scheduling and patient portal adoption"

    def evaluate(self) -> List[Finding]:
        findings = []

        with_scheduling = [c for c in self.competitors if c.conversion_mechanics.online_scheduling]
        with_portal = [c for c in self.competitors if c.conversion_mechanics.patient_portal]
        total = len(self.competitors)

        if len(with_scheduling) >= total * 0.5:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_scheduling)}/{total} competitors offer online scheduling",
                severity=Severity.CRITICAL,
                details="Online scheduling is expected in modern healthcare"
            ))

        if len(with_portal) >= 2:
            findings.append(self._create_finding(
                finding_type=FindingType.PATTERN,
                observation=f"{len(with_portal)} competitors have patient portals",
                severity=Severity.MEDIUM
            ))

        return findings


# ============================================================================
# RULE ENGINE - VERTICAL-AWARE
# ============================================================================

# Universal rules that apply to all verticals
UNIVERSAL_RULES: List[Type[InsightRule]] = [
    BacklinkGapRule,
    ReviewVisibilityRule,
    ContentDepthRule,
    GridRankingRule,
    ChatWidgetRule,
]

# Blue collar specific rules
BLUE_COLLAR_RULES: List[Type[InsightRule]] = [
    CertificationCheckRule,
    GalleryPresenceRule,
    ServiceAreaCoverageRule,
    StickyCTARule,
]

# Entertainment specific rules
ENTERTAINMENT_RULES: List[Type[InsightRule]] = [
    ExperiencePhotoRule,
    OnlineBookingRule,
    GroupPackagesRule,
    UniqueExperienceRule,
    RepeatVisitRule,
]

# Healthcare specific rules
HEALTHCARE_RULES: List[Type[InsightRule]] = [
    CredentialDisplayRule,
    OnlineSchedulingRule,
]


def get_rules_for_vertical(vertical: Vertical) -> List[Type[InsightRule]]:
    """Get the appropriate rules for a given vertical"""
    rules = list(UNIVERSAL_RULES)

    if vertical in BLUE_COLLAR_VERTICALS:
        rules.extend(BLUE_COLLAR_RULES)
    elif vertical in ENTERTAINMENT_VERTICALS:
        rules.extend(ENTERTAINMENT_RULES)
    elif vertical in HEALTHCARE_VERTICALS:
        rules.extend(HEALTHCARE_RULES)
    else:
        # Default: use a mix of common rules
        rules.extend([ServiceAreaCoverageRule, StickyCTARule])

    return rules


class RuleEngine:
    """Run insight rules and collect findings - vertical-aware"""

    # Legacy: all rules for backward compatibility
    ALL_RULES: List[Type[InsightRule]] = [
        BacklinkGapRule,
        ReviewVisibilityRule,
        CertificationCheckRule,
        GalleryPresenceRule,
        ServiceAreaCoverageRule,
        StickyCTARule,
        ChatWidgetRule,
        ContentDepthRule,
        GridRankingRule,
        # Entertainment
        ExperiencePhotoRule,
        OnlineBookingRule,
        GroupPackagesRule,
        UniqueExperienceRule,
        RepeatVisitRule,
        # Healthcare
        CredentialDisplayRule,
        OnlineSchedulingRule,
    ]

    def __init__(self, client: Client, competitors: List[CompetitorProfile]):
        self.client = client
        self.competitors = competitors
        # Get rules appropriate for this client's vertical
        self.rules = get_rules_for_vertical(client.vertical)

    def run_all_rules(self) -> List[Finding]:
        """Run vertical-appropriate rules and return findings"""
        all_findings = []

        for rule_class in self.rules:
            try:
                rule = rule_class(self.client, self.competitors)
                findings = rule.evaluate()
                all_findings.extend(findings)
                logger.info(f"Rule {rule.rule_id}: {len(findings)} findings")
            except Exception as e:
                logger.error(f"Rule {rule_class.rule_id} failed: {e}")

        return all_findings

    def run_rule(self, rule_id: str) -> List[Finding]:
        """Run a specific rule by ID"""
        for rule_class in self.ALL_RULES:
            if rule_class.rule_id == rule_id:
                rule = rule_class(self.client, self.competitors)
                return rule.evaluate()
        return []

    def run_all_rules_universal(self) -> List[Finding]:
        """Run all rules regardless of vertical (legacy behavior)"""
        all_findings = []

        for rule_class in self.ALL_RULES:
            try:
                rule = rule_class(self.client, self.competitors)
                findings = rule.evaluate()
                all_findings.extend(findings)
                logger.info(f"Rule {rule.rule_id}: {len(findings)} findings")
            except Exception as e:
                logger.error(f"Rule {rule_class.rule_id} failed: {e}")

        return all_findings
