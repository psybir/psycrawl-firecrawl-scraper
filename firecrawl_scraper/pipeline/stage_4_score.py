"""
Stage 4: SCORE - Generate Findings and Actionable Insights

Input: Competitor Profiles + Client context
Output: Findings → Actionable Insights (THE BRIDGE)

This stage analyzes competitor profiles against the client to generate:
- Findings: Raw observations (gaps, strengths, opportunities)
- Actionable Insights: The bridge between findings and specs

VERTICAL-AWARE: Uses appropriate rules based on client's industry vertical.
"""

import logging
from typing import List, Dict, Optional, Any
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
    FindingsReport,
    ActionableInsight,
    InsightReport,
    InsightType,
    ImpactLevel,
    EffortLevel,
    Evidence,
    ExpectedImpact,
    SpecDetails,
    GeoTag,
    Vertical,
    ENTERTAINMENT_VERTICALS,
    HEALTHCARE_VERTICALS,
    BLUE_COLLAR_VERTICALS,
)
from ..analysis.insight_rules import RuleEngine, get_rules_for_vertical

logger = logging.getLogger(__name__)


class ScoreStage:
    """Generate Findings and Actionable Insights from competitor analysis"""

    def __init__(
        self,
        client: Client,
        competitor_profiles: List[CompetitorProfile]
    ):
        self.client = client
        self.competitors = competitor_profiles
        self.findings: List[Finding] = []
        self.insights: List[ActionableInsight] = []

    def run(self) -> tuple[FindingsReport, InsightReport]:
        """Execute Stage 4: Score and generate insights"""
        logger.info(f"Stage 4: Scoring {len(self.competitors)} competitors against {self.client.name}")
        logger.info(f"Client vertical: {self.client.vertical}")

        # Use vertical-aware rule engine if competitors exist
        if self.competitors:
            rule_engine = RuleEngine(self.client, self.competitors)
            rule_findings = rule_engine.run_all_rules()
            self.findings.extend(rule_findings)
            logger.info(f"Vertical-aware rules generated {len(rule_findings)} findings")
        else:
            # Fallback to built-in rules when no competitor data
            logger.info("No competitors - using built-in baseline rules")
            self._run_baseline_rules()

        # Run universal rules that don't require competitors
        self._run_universal_rules()

        # Convert findings to actionable insights (vertical-aware)
        self._generate_insights()

        # Calculate priority scores
        for insight in self.insights:
            insight.calculate_priority()

        # Create reports
        findings_report = FindingsReport(
            client_id=self.client.id,
            findings=self.findings
        )
        findings_report.group_findings()

        insights_report = InsightReport(
            client_id=self.client.id,
            insights=self.insights
        )

        logger.info(f"Stage 4 Complete: {len(self.findings)} findings, {len(self.insights)} insights")
        return findings_report, insights_report

    def _run_baseline_rules(self):
        """Run baseline rules when no competitor data available"""
        # Generate findings based on client config alone
        self._rule_certification_visibility()
        self._rule_gallery_presence()
        self._rule_warranty_guarantee()
        self._rule_team_visibility()
        self._rule_sticky_cta()

    def _run_universal_rules(self):
        """Run rules that apply regardless of competitor data"""
        # Client self-assessment rules
        if self.client.gbp_profile:
            if self.client.gbp_profile.review_count and self.client.gbp_profile.review_count >= 100:
                self._add_finding(
                    finding_type=FindingType.STRENGTH,
                    category=FindingCategory.TRUST,
                    observation=f"Strong review presence ({self.client.gbp_profile.review_count} reviews)",
                    severity=Severity.LOW,
                    rule_id="client_review_strength"
                )
            if self.client.gbp_profile.rating and self.client.gbp_profile.rating >= 4.8:
                self._add_finding(
                    finding_type=FindingType.STRENGTH,
                    category=FindingCategory.TRUST,
                    observation=f"Excellent rating ({self.client.gbp_profile.rating})",
                    severity=Severity.LOW,
                    rule_id="client_rating_strength"
                )

    # ==================== TRUST RULES ====================

    def _run_trust_rules(self):
        """Run trust-related analysis rules"""
        self._rule_review_gap()
        self._rule_certification_visibility()
        self._rule_gallery_presence()
        self._rule_warranty_guarantee()
        self._rule_team_visibility()

    def _rule_review_gap(self):
        """Check for review count/rating gaps"""
        client_reviews = self.client.gbp_profile.review_count if self.client.gbp_profile else 0
        client_rating = self.client.gbp_profile.rating if self.client.gbp_profile else 0

        competitor_reviews = []
        competitor_ratings = []

        for comp in self.competitors:
            if comp.trust_signals.review_count:
                competitor_reviews.append(comp.trust_signals.review_count)
            if comp.trust_signals.rating:
                competitor_ratings.append(comp.trust_signals.rating)

        # Review count analysis
        if competitor_reviews:
            avg_reviews = sum(competitor_reviews) / len(competitor_reviews)
            max_reviews = max(competitor_reviews)

            if client_reviews < avg_reviews:
                self._add_finding(
                    finding_type=FindingType.GAP,
                    category=FindingCategory.TRUST,
                    observation=f"Review count ({client_reviews}) below competitor average ({avg_reviews:.0f})",
                    severity=Severity.HIGH if client_reviews < avg_reviews * 0.5 else Severity.MEDIUM,
                    data_points=DataPoints(
                        our_value=client_reviews,
                        benchmark=avg_reviews,
                        delta=client_reviews - avg_reviews
                    ),
                    rule_id="review_count_gap"
                )
            elif client_reviews > max_reviews:
                self._add_finding(
                    finding_type=FindingType.STRENGTH,
                    category=FindingCategory.TRUST,
                    observation=f"Review count ({client_reviews}) leads all competitors (max: {max_reviews})",
                    severity=Severity.LOW,
                    data_points=DataPoints(our_value=client_reviews, benchmark=max_reviews),
                    rule_id="review_count_lead"
                )

    def _rule_certification_visibility(self):
        """Check certification/license visibility gaps"""
        competitors_with_certs = sum(
            1 for c in self.competitors
            if c.trust_signals.certifications or c.trust_signals.licenses_shown
        )

        if competitors_with_certs >= len(self.competitors) * 0.6:
            self._add_finding(
                finding_type=FindingType.PATTERN,
                category=FindingCategory.TRUST,
                observation=f"{competitors_with_certs}/{len(self.competitors)} competitors display certifications/licenses",
                severity=Severity.MEDIUM,
                details="Industry standard to show credentials prominently",
                rule_id="cert_visibility_pattern"
            )

    def _rule_gallery_presence(self):
        """Check before/after gallery presence"""
        competitors_with_gallery = sum(
            1 for c in self.competitors
            if c.trust_signals.before_after_gallery
        )

        if competitors_with_gallery >= len(self.competitors) * 0.5:
            self._add_finding(
                finding_type=FindingType.PATTERN,
                category=FindingCategory.TRUST,
                observation=f"{competitors_with_gallery}/{len(self.competitors)} competitors have before/after galleries",
                severity=Severity.HIGH,
                details="Visual proof is table stakes in this industry",
                rule_id="gallery_pattern"
            )

    def _rule_warranty_guarantee(self):
        """Check warranty/guarantee language"""
        competitors_with_warranty = sum(
            1 for c in self.competitors
            if c.trust_signals.warranty_guarantee_language
        )

        if competitors_with_warranty >= len(self.competitors) * 0.5:
            self._add_finding(
                finding_type=FindingType.OPPORTUNITY,
                category=FindingCategory.TRUST,
                observation="Warranty/guarantee language is common among competitors",
                severity=Severity.MEDIUM,
                rule_id="warranty_opportunity"
            )

    def _rule_team_visibility(self):
        """Check team/owner visibility"""
        competitors_with_team = sum(
            1 for c in self.competitors
            if c.trust_signals.team_photos or c.trust_signals.owner_visible
        )

        if competitors_with_team >= len(self.competitors) * 0.4:
            self._add_finding(
                finding_type=FindingType.PATTERN,
                category=FindingCategory.TRUST,
                observation=f"{competitors_with_team}/{len(self.competitors)} competitors show team/owner photos",
                severity=Severity.LOW,
                rule_id="team_visibility_pattern"
            )

    # ==================== CONVERSION RULES ====================

    def _run_conversion_rules(self):
        """Run conversion-related analysis rules"""
        self._rule_sticky_cta()
        self._rule_chat_widget()
        self._rule_form_friction()
        self._rule_phone_prominence()

    def _rule_sticky_cta(self):
        """Check sticky CTA presence"""
        competitors_with_sticky = sum(
            1 for c in self.competitors
            if c.conversion_mechanics.sticky_cta or c.conversion_mechanics.sticky_call
        )

        if competitors_with_sticky >= len(self.competitors) * 0.5:
            self._add_finding(
                finding_type=FindingType.PATTERN,
                category=FindingCategory.CONVERSION,
                observation=f"{competitors_with_sticky}/{len(self.competitors)} competitors use sticky CTAs",
                severity=Severity.HIGH,
                details="Sticky CTAs improve conversion by keeping action visible",
                rule_id="sticky_cta_pattern"
            )

    def _rule_chat_widget(self):
        """Check chat widget adoption"""
        competitors_with_chat = sum(
            1 for c in self.competitors
            if c.conversion_mechanics.chat_widget
        )

        if competitors_with_chat >= 2:
            self._add_finding(
                finding_type=FindingType.OPPORTUNITY,
                category=FindingCategory.CONVERSION,
                observation=f"{competitors_with_chat} competitors offer live chat",
                severity=Severity.MEDIUM,
                rule_id="chat_opportunity"
            )

    def _rule_form_friction(self):
        """Analyze form friction across competitors"""
        form_lengths = [
            c.conversion_mechanics.form_length
            for c in self.competitors
            if c.conversion_mechanics.form_length
        ]

        if form_lengths:
            avg_length = sum(form_lengths) / len(form_lengths)
            self._add_finding(
                finding_type=FindingType.PATTERN,
                category=FindingCategory.CONVERSION,
                observation=f"Average form length: {avg_length:.1f} fields across competitors",
                severity=Severity.LOW,
                data_points=DataPoints(benchmark=avg_length),
                rule_id="form_length_benchmark"
            )

    def _rule_phone_prominence(self):
        """Check phone prominence patterns"""
        competitors_phone_clickable = sum(
            1 for c in self.competitors
            if c.conversion_mechanics.phone_clickable
        )

        if competitors_phone_clickable >= len(self.competitors) * 0.8:
            self._add_finding(
                finding_type=FindingType.PATTERN,
                category=FindingCategory.CONVERSION,
                observation="Clickable phone numbers are standard practice",
                severity=Severity.HIGH,
                rule_id="phone_clickable_standard"
            )

    # ==================== CONTENT RULES ====================

    def _run_content_rules(self):
        """Run content-related analysis rules"""
        self._rule_service_page_depth()
        self._rule_blog_activity()

    def _rule_service_page_depth(self):
        """Analyze service page content depth"""
        for comp in self.competitors:
            for page in comp.seo_structure.service_pages:
                if page.word_count and page.word_count > 1500:
                    self._add_finding(
                        finding_type=FindingType.PATTERN,
                        category=FindingCategory.CONTENT,
                        observation=f"{comp.domain} has in-depth service page ({page.word_count} words)",
                        severity=Severity.MEDIUM,
                        competitor_refs=[comp.id],
                        rule_id="content_depth_pattern"
                    )

    def _rule_blog_activity(self):
        """Check blog activity patterns"""
        active_blogs = sum(
            1 for c in self.competitors
            if c.seo_structure.blog_active
        )

        if active_blogs >= len(self.competitors) * 0.3:
            self._add_finding(
                finding_type=FindingType.OPPORTUNITY,
                category=FindingCategory.CONTENT,
                observation=f"{active_blogs}/{len(self.competitors)} competitors maintain active blogs",
                severity=Severity.MEDIUM,
                rule_id="blog_opportunity"
            )

    # ==================== BACKLINK RULES ====================

    def _run_backlink_rules(self):
        """Run backlink-related analysis rules"""
        self._rule_authority_gap()
        self._rule_backlink_sources()

    def _rule_authority_gap(self):
        """Check domain authority gaps"""
        authorities = [
            c.backlinks.domain_authority
            for c in self.competitors
            if c.backlinks.domain_authority
        ]

        if authorities:
            avg_authority = sum(authorities) / len(authorities)
            self._add_finding(
                finding_type=FindingType.PATTERN,
                category=FindingCategory.BACKLINKS,
                observation=f"Average competitor domain authority: {avg_authority:.0f}",
                severity=Severity.HIGH,
                data_points=DataPoints(benchmark=avg_authority),
                rule_id="authority_benchmark"
            )

    def _rule_backlink_sources(self):
        """Identify backlink source patterns"""
        # This would analyze top backlink sources across competitors
        pass

    # ==================== LOCAL SEO RULES ====================

    def _run_local_seo_rules(self):
        """Run local SEO analysis rules"""
        self._rule_service_area_coverage()
        self._rule_grid_rankings()

    def _rule_service_area_coverage(self):
        """Check service area page coverage"""
        for comp in self.competitors:
            if comp.seo_structure.service_area_pages:
                count = len(comp.seo_structure.service_area_pages)
                if count >= 5:
                    self._add_finding(
                        finding_type=FindingType.PATTERN,
                        category=FindingCategory.LOCAL_SEO,
                        observation=f"{comp.domain} has {count} service area pages",
                        severity=Severity.HIGH,
                        competitor_refs=[comp.id],
                        rule_id="service_area_coverage"
                    )

    def _rule_grid_rankings(self):
        """Analyze grid/local pack rankings"""
        for comp in self.competitors:
            if comp.grid_performance:
                avg_rank = sum(comp.grid_performance.values()) / len(comp.grid_performance)
                if avg_rank <= 3:
                    self._add_finding(
                        finding_type=FindingType.THREAT,
                        category=FindingCategory.LOCAL_SEO,
                        observation=f"{comp.domain} dominates local pack (avg rank: {avg_rank:.1f})",
                        severity=Severity.CRITICAL,
                        competitor_refs=[comp.id],
                        data_points=DataPoints(competitor_values={comp.domain: avg_rank}),
                        rule_id="grid_threat"
                    )

    # ==================== STRUCTURE RULES ====================

    def _run_structure_rules(self):
        """Run site structure analysis rules"""
        self._rule_page_type_coverage()
        self._rule_schema_usage()

    def _rule_page_type_coverage(self):
        """Check page type coverage patterns"""
        page_types_count = {}
        for comp in self.competitors:
            for pt in comp.seo_structure.page_types_present:
                page_types_count[pt] = page_types_count.get(pt, 0) + 1

        for pt, count in page_types_count.items():
            if count >= len(self.competitors) * 0.6:
                self._add_finding(
                    finding_type=FindingType.PATTERN,
                    category=FindingCategory.STRUCTURE,
                    observation=f"{count}/{len(self.competitors)} competitors have '{pt}' pages",
                    severity=Severity.MEDIUM,
                    rule_id=f"page_type_{pt}"
                )

    def _rule_schema_usage(self):
        """Check schema markup usage"""
        for comp in self.competitors:
            if comp.seo_structure.schema_markup:
                self._add_finding(
                    finding_type=FindingType.PATTERN,
                    category=FindingCategory.STRUCTURE,
                    observation=f"{comp.domain} uses structured data: {list(comp.seo_structure.schema_markup.keys())}",
                    severity=Severity.LOW,
                    competitor_refs=[comp.id],
                    rule_id="schema_usage"
                )

    # ==================== INSIGHT GENERATION ====================

    def _generate_insights(self):
        """Convert findings into actionable insights - VERTICAL-AWARE"""
        # Group findings by rule_id for insight generation
        findings_by_rule = {}
        for finding in self.findings:
            if finding.rule_id:
                if finding.rule_id not in findings_by_rule:
                    findings_by_rule[finding.rule_id] = []
                findings_by_rule[finding.rule_id].append(finding)

        # Universal insights (all verticals)
        self._insight_from_review_gap(findings_by_rule.get("review_count_gap", []))
        self._insight_from_sticky_cta(findings_by_rule.get("sticky_cta_pattern", []))
        self._insight_from_authority_gap(findings_by_rule.get("authority_benchmark", []))
        self._insight_from_chat_opportunity(findings_by_rule.get("chat_opportunity", []))
        self._insight_from_blog_opportunity(findings_by_rule.get("blog_opportunity", []))

        # Vertical-specific insight generation
        if self.client.vertical in BLUE_COLLAR_VERTICALS:
            # Blue collar insights
            self._insight_from_gallery_pattern(findings_by_rule.get("gallery_pattern", []))
            self._insight_from_service_areas(findings_by_rule.get("service_area_coverage", []))

        elif self.client.vertical in ENTERTAINMENT_VERTICALS:
            # Entertainment insights
            self._insight_from_online_booking(findings_by_rule.get("online_booking", []))
            self._insight_from_experience_photos(findings_by_rule.get("experience_photo", []))
            self._insight_from_group_packages(findings_by_rule.get("group_packages", []))

        elif self.client.vertical in HEALTHCARE_VERTICALS:
            # Healthcare insights
            self._insight_from_online_scheduling(findings_by_rule.get("online_scheduling", []))
            self._insight_from_credentials(findings_by_rule.get("credential_display", []))

    def _insight_from_review_gap(self, findings: List[Finding]):
        """Generate insight from review gap findings"""
        if not findings:
            return

        finding = findings[0]
        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Improve Review Visibility",
            problem="Review count below competitive benchmark",
            hypothesis="Higher review visibility builds trust and improves conversion rate",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=finding.observation,
                data_point=finding.data_points.benchmark if finding.data_points else None
            )],
            finding_refs=[finding.id],
            spec_change="Add prominent review widget above fold on all service pages",
            spec_details=SpecDetails(
                component="ReviewWidget",
                placement="Above fold, after hero",
                content_requirements=[
                    "Show aggregate rating",
                    "Show review count",
                    "Link to Google reviews"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.LOW,
                cvr_impact=ImpactLevel.HIGH,
                trust_impact=ImpactLevel.HIGH,
                speed_impact=ImpactLevel.HIGH
            ),
            effort_estimate=EffortLevel.LOW,
            insight_type=InsightType.TRUST_GAP
        ))

    def _insight_from_gallery_pattern(self, findings: List[Finding]):
        """Generate insight from gallery pattern findings"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Add Before/After Gallery",
            problem="Missing visual proof of work that competitors display",
            hypothesis="Before/after photos build trust and demonstrate expertise",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Create dedicated gallery page and embed galleries on service pages",
            spec_details=SpecDetails(
                page_type="gallery",
                component="BeforeAfterGallery",
                content_requirements=[
                    "Minimum 10 before/after pairs",
                    "Organized by service type",
                    "Location tags for local relevance"
                ],
                design_requirements=[
                    "Slider comparison view",
                    "Lightbox for full-size viewing"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.MEDIUM,
                cvr_impact=ImpactLevel.HIGH,
                trust_impact=ImpactLevel.HIGH,
                speed_impact=ImpactLevel.MEDIUM
            ),
            effort_estimate=EffortLevel.MEDIUM,
            insight_type=InsightType.TRUST_GAP
        ))

    def _insight_from_sticky_cta(self, findings: List[Finding]):
        """Generate insight from sticky CTA pattern"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Implement Sticky CTA",
            problem="No persistent call-to-action as users scroll",
            hypothesis="Sticky CTAs keep conversion action visible and reduce friction",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Add sticky header or mobile sticky bar with click-to-call",
            spec_details=SpecDetails(
                component="StickyCTA",
                placement="Fixed header on scroll",
                design_requirements=[
                    "Phone number always visible",
                    "Click-to-call on mobile",
                    "Contrasting CTA button"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.NONE,
                cvr_impact=ImpactLevel.HIGH,
                trust_impact=ImpactLevel.LOW,
                speed_impact=ImpactLevel.HIGH
            ),
            effort_estimate=EffortLevel.LOW,
            insight_type=InsightType.CONVERSION_GAP
        ))

    def _insight_from_service_areas(self, findings: List[Finding]):
        """Generate insight from service area coverage"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Expand Service Area Pages",
            problem="Competitors have dedicated service area pages we're missing",
            hypothesis="Location-specific pages improve local rankings for each area",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation,
                source_url=None
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Create service-area pages for each target location",
            spec_details=SpecDetails(
                page_type="service-area",
                content_requirements=[
                    "Location-specific content",
                    "Local testimonials",
                    "Service area map",
                    "Travel time from primary location"
                ],
                schema_requirements=["LocalBusiness", "GeoCircle"]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.HIGH,
                cvr_impact=ImpactLevel.MEDIUM,
                trust_impact=ImpactLevel.MEDIUM,
                speed_impact=ImpactLevel.MEDIUM
            ),
            effort_estimate=EffortLevel.MEDIUM,
            insight_type=InsightType.LOCAL_SEO_FIX
        ))

    def _insight_from_authority_gap(self, findings: List[Finding]):
        """Generate insight from authority gap"""
        if not findings:
            return

        finding = findings[0]
        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Build Domain Authority",
            problem="Domain authority below competitive benchmark",
            hypothesis="Higher authority improves organic rankings across all keywords",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=finding.observation,
                data_point=finding.data_points.benchmark if finding.data_points else None
            )],
            finding_refs=[finding.id],
            spec_change="Implement backlink acquisition strategy targeting local directories and industry sites",
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.HIGH,
                cvr_impact=ImpactLevel.LOW,
                trust_impact=ImpactLevel.MEDIUM,
                speed_impact=ImpactLevel.LOW
            ),
            effort_estimate=EffortLevel.HIGH,
            insight_type=InsightType.BACKLINK_OPPORTUNITY
        ))

    def _insight_from_chat_opportunity(self, findings: List[Finding]):
        """Generate insight from chat widget opportunity"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Add Live Chat",
            problem="Missing live chat option that competitors offer",
            hypothesis="Chat provides immediate engagement for high-intent visitors",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Implement chat widget (e.g., Intercom, Tawk.to)",
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.NONE,
                cvr_impact=ImpactLevel.MEDIUM,
                trust_impact=ImpactLevel.LOW,
                speed_impact=ImpactLevel.HIGH
            ),
            effort_estimate=EffortLevel.LOW,
            insight_type=InsightType.CONVERSION_GAP
        ))

    def _insight_from_blog_opportunity(self, findings: List[Finding]):
        """Generate insight from blog opportunity"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Start Content Marketing",
            problem="No active blog while competitors publish content",
            hypothesis="Content marketing builds authority and captures informational queries",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Create blog and publish 2-4 articles per month",
            spec_details=SpecDetails(
                page_type="blog",
                content_requirements=[
                    "Educational content about services",
                    "Local/seasonal content",
                    "FAQ articles",
                    "How-to guides"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.MEDIUM,
                cvr_impact=ImpactLevel.LOW,
                trust_impact=ImpactLevel.MEDIUM,
                speed_impact=ImpactLevel.LOW
            ),
            effort_estimate=EffortLevel.HIGH,
            insight_type=InsightType.CONTENT_GAP
        ))

    # ==================== ENTERTAINMENT VERTICAL INSIGHTS ====================

    def _insight_from_online_booking(self, findings: List[Finding]):
        """Generate insight from online booking opportunity (entertainment)"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Implement Online Booking System",
            problem="Missing or suboptimal online booking that competitors offer",
            hypothesis="Seamless online booking reduces friction and increases conversion rate",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Implement robust online booking with real-time availability",
            spec_details=SpecDetails(
                component="BookingWidget",
                placement="Above fold on all pages",
                content_requirements=[
                    "Real-time availability calendar",
                    "Group size selection",
                    "Date and time picker",
                    "Instant confirmation"
                ],
                design_requirements=[
                    "Mobile-optimized",
                    "2-3 step booking flow",
                    "Clear pricing display"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.NONE,
                cvr_impact=ImpactLevel.HIGH,
                trust_impact=ImpactLevel.MEDIUM,
                speed_impact=ImpactLevel.HIGH
            ),
            effort_estimate=EffortLevel.MEDIUM,
            insight_type=InsightType.CONVERSION_GAP
        ))

    def _insight_from_experience_photos(self, findings: List[Finding]):
        """Generate insight from experience photo opportunity (entertainment)"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Showcase Experience Photos & Videos",
            problem="Missing visual content that showcases the experience",
            hypothesis="Immersive photos and videos build anticipation and drive bookings",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Create immersive photo gallery and promo video for each experience",
            spec_details=SpecDetails(
                component="ExperienceGallery",
                page_type="service",
                content_requirements=[
                    "Atmospheric room photos",
                    "Teaser video trailer",
                    "No spoilers - maintain mystery",
                    "Group photos with permission"
                ],
                design_requirements=[
                    "Full-screen gallery option",
                    "Video autoplay on hero",
                    "Carousel for multiple experiences"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.MEDIUM,
                cvr_impact=ImpactLevel.HIGH,
                trust_impact=ImpactLevel.HIGH,
                speed_impact=ImpactLevel.MEDIUM
            ),
            effort_estimate=EffortLevel.MEDIUM,
            insight_type=InsightType.TRUST_GAP
        ))

    def _insight_from_group_packages(self, findings: List[Finding]):
        """Generate insight from group booking opportunity (entertainment)"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Promote Group & Corporate Packages",
            problem="Missing or hidden group booking and corporate options",
            hypothesis="Group/corporate bookings have higher average order value",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Create dedicated pages for birthday parties and corporate team building",
            spec_details=SpecDetails(
                page_type="service",
                content_requirements=[
                    "Party package details and pricing",
                    "Corporate booking inquiry form",
                    "Group size options",
                    "Catering/add-on options"
                ],
                design_requirements=[
                    "Clear package comparison",
                    "Easy inquiry flow",
                    "Corporate testimonials"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.MEDIUM,
                cvr_impact=ImpactLevel.HIGH,
                trust_impact=ImpactLevel.MEDIUM,
                speed_impact=ImpactLevel.MEDIUM
            ),
            effort_estimate=EffortLevel.MEDIUM,
            insight_type=InsightType.CONVERSION_GAP
        ))

    # ==================== HEALTHCARE VERTICAL INSIGHTS ====================

    def _insight_from_online_scheduling(self, findings: List[Finding]):
        """Generate insight from online scheduling opportunity (healthcare)"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Implement Online Scheduling",
            problem="Missing online appointment scheduling that competitors offer",
            hypothesis="Online scheduling reduces phone friction and increases bookings",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Implement online appointment scheduling with calendar integration",
            spec_details=SpecDetails(
                component="SchedulingWidget",
                content_requirements=[
                    "Real-time availability",
                    "Service type selection",
                    "Provider selection",
                    "New/existing patient flow"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.NONE,
                cvr_impact=ImpactLevel.HIGH,
                trust_impact=ImpactLevel.MEDIUM,
                speed_impact=ImpactLevel.HIGH
            ),
            effort_estimate=EffortLevel.MEDIUM,
            insight_type=InsightType.CONVERSION_GAP
        ))

    def _insight_from_credentials(self, findings: List[Finding]):
        """Generate insight from credential display opportunity (healthcare)"""
        if not findings:
            return

        self.insights.append(ActionableInsight(
            id=str(uuid.uuid4()),
            title="Display Provider Credentials",
            problem="Provider credentials not prominently displayed",
            hypothesis="Visible credentials build trust and reduce decision anxiety",
            evidence=[Evidence(
                source_type="competitor_analysis",
                observation=f.observation
            ) for f in findings],
            finding_refs=[f.id for f in findings],
            spec_change="Create provider profile pages with credentials and certifications",
            spec_details=SpecDetails(
                page_type="about",
                content_requirements=[
                    "Provider photos and bios",
                    "Board certifications",
                    "Years of experience",
                    "Education background"
                ]
            ),
            expected_impact=ExpectedImpact(
                rank_impact=ImpactLevel.LOW,
                cvr_impact=ImpactLevel.MEDIUM,
                trust_impact=ImpactLevel.HIGH,
                speed_impact=ImpactLevel.MEDIUM
            ),
            effort_estimate=EffortLevel.LOW,
            insight_type=InsightType.TRUST_GAP
        ))

    # ==================== HELPERS ====================

    def _add_finding(
        self,
        finding_type: FindingType,
        category: FindingCategory,
        observation: str,
        severity: Severity,
        details: str = None,
        data_points: DataPoints = None,
        competitor_refs: List[str] = None,
        geo_context: GeoTag = None,
        service_context: str = None,
        rule_id: str = None
    ):
        """Add a finding to the collection"""
        finding = Finding(
            id=str(uuid.uuid4()),
            finding_type=finding_type,
            category=category,
            observation=observation,
            severity=severity,
            details=details,
            data_points=data_points,
            source_refs=[],
            competitor_refs=competitor_refs or [],
            geo_context=geo_context,
            service_context=service_context,
            rule_id=rule_id,
            discovered_at=datetime.now()
        )
        self.findings.append(finding)
