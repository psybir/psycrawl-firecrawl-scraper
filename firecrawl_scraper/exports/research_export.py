"""
Research Export - One-command export with all research data merged

Generates comprehensive competitive analysis from research repo data.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from ..loaders.research_data_loader import ResearchDataLoader
from ..integrations.research_integration import ResearchIntegration
from ..models import (
    Client,
    Vertical,
    Service,
    Location,
    GBPProfile,
    Brand,
    BrandTone,
    GeoBucket,
    GeoScope,
    ServiceDefinedVariables,
    ThreatLevel,
)
from .client_brief import ClientBriefGenerator
from .content_brief import ContentBriefGenerator
from .implementation_spec import ImplementationSpecGenerator
from .seo_strategy import SEOStrategyGenerator


# Default paths
DEFAULT_RESEARCH_PATH = "/Volumes/Samsung 990 Pro/Firecrawl Scraper/escapeexe-research"
DEFAULT_OUTPUT_DIR = "/Volumes/Samsung 990 Pro/Firecrawl Scraper/psycrawl-firecrawl-scraper/output/escape-exe/deliverables"


def create_escape_exe_client(research_integration: ResearchIntegration) -> Client:
    """Create escape.exe client from research data"""

    # Experiences as services
    gavin_experience = Service(
        id="exp-gavin",
        name="GAVIN AI Experience",
        slug="gavin-ai-experience",
        is_money_service=True,
        description="Interactive AI-powered escape room featuring GAVIN, our custom AI character who guides your journey through multiple story paths.",
        keywords=["ai escape room", "interactive escape room", "tech escape room", "gavin escape room"],
        synonyms=["GAVIN room", "AI room"],
        defined_variables=ServiceDefinedVariables(
            time_range="60-90 minutes",
            cost_range="$35-$45 per person",
            process_steps=[
                "Book online - select date, time, group size",
                "Arrive 15 min early for briefing",
                "Enter immersive environment",
                "Interact with GAVIN AI throughout",
                "Experience one of multiple endings"
            ],
            best_for=[
                "Date nights with a twist",
                "Tech enthusiasts and gamers",
                "Corporate team building",
                "Groups seeking narrative experiences"
            ],
        )
    )

    team_building = Service(
        id="exp-team",
        name="Corporate Team Building",
        slug="team-building",
        is_money_service=True,
        description="Premium escape room experience designed for corporate teams. Build communication, leadership, and problem-solving skills.",
        keywords=["team building escape room", "corporate escape room", "team building activities bethlehem"],
        defined_variables=ServiceDefinedVariables(
            time_range="60-90 minutes plus debrief",
            cost_range="$40-$50 per person",
            process_steps=[
                "Contact us for group booking",
                "Choose experience level",
                "Book private room time",
                "Complete team challenge",
                "Optional debrief session"
            ],
            best_for=[
                "Corporate teams 6-12 people",
                "Leadership development",
                "New team bonding",
                "Quarterly team events"
            ],
        )
    )

    birthday_events = Service(
        id="exp-birthday",
        name="Birthday & Events",
        slug="birthday-parties",
        is_money_service=True,
        description="Celebrate with an unforgettable escape room experience. Perfect for birthdays, bachelor/bachelorette parties, and special occasions.",
        keywords=["escape room birthday party", "birthday party venues bethlehem", "unique birthday ideas"],
        defined_variables=ServiceDefinedVariables(
            time_range="2-3 hours total",
            cost_range="$35-$45 per person",
            process_steps=[
                "Book party package online",
                "Customize experience",
                "Arrive for check-in",
                "Complete escape challenge",
                "Celebrate in lobby area"
            ],
            best_for=[
                "Birthday celebrations",
                "Bachelor/bachelorette parties",
                "Anniversary celebrations",
                "Friend group outings"
            ],
        )
    )

    # Locations (90-mile radius for destination business)
    locations = [
        Location(id="loc-bethlehem", name="Bethlehem, PA", is_primary=True, geo_bucket=GeoBucket.BUCKET_0_10, geo_scope=GeoScope.LOCAL_RADIUS),
        Location(id="loc-allentown", name="Allentown, PA", geo_bucket=GeoBucket.BUCKET_10_30, geo_scope=GeoScope.LOCAL_RADIUS),
        Location(id="loc-easton", name="Easton, PA", geo_bucket=GeoBucket.BUCKET_10_30, geo_scope=GeoScope.LOCAL_RADIUS),
        Location(id="loc-reading", name="Reading, PA", geo_bucket=GeoBucket.BUCKET_30_60, geo_scope=GeoScope.LOCAL_RADIUS),
        Location(id="loc-poconos", name="Poconos, PA", geo_bucket=GeoBucket.BUCKET_60_90, geo_scope=GeoScope.LOCAL_RADIUS),
        Location(id="loc-philadelphia", name="Philadelphia, PA", geo_bucket=GeoBucket.BUCKET_60_90, geo_scope=GeoScope.LOCAL_RADIUS),
    ]

    # GBP Profile from research
    gbp_profile = research_integration.build_client_gbp_profile()

    return Client(
        id="escape-exe",
        name="escape.exe",
        domain="escapeexe.com",
        vertical=Vertical.ESCAPE_ROOM,
        services=[gavin_experience, team_building, birthday_events],
        locations=locations,
        gbp_profile=gbp_profile,
        brand=Brand(
            tagline="Interactive Movie Escape Rooms",
            differentiators=[
                "GAVIN AI character - proprietary technology",
                "Multiple story endings - unique to escape.exe",
                "Adaptive difficulty system",
                "Custom-built tech puzzles",
                "Gaming industry expertise"
            ],
            tone=BrandTone.FRIENDLY,
        ),
    )


class ResearchCompetitiveAnalysisGenerator:
    """Generate comprehensive competitive analysis from research data"""

    def __init__(
        self,
        research_integration: ResearchIntegration,
        client: Client,
    ):
        self.ri = research_integration
        self.client = client
        self.competitors = research_integration.build_competitor_profiles()
        self.findings = research_integration.build_findings()
        self.insights = research_integration.build_insights()

    def generate(self) -> str:
        """Generate complete competitive analysis markdown"""
        sections = [
            self._header(),
            self._executive_summary(),
            self._competitive_positioning_map(),
            self._competitor_profiles(),
            self._escape_exe_moats(),
            self._market_gaps_section(),
            self._seo_opportunities(),
            self._threat_assessment(),
            self._findings_summary(),
            self._actionable_insights(),
            self._recommendations(),
        ]

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate header section"""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        return f"""# Competitive Analysis: {self.client.name}

**Document Type:** Comprehensive Competitive Intelligence Report
**Generated:** {timestamp}
**Source:** escapeexe-research repository + pipeline analysis
**Competitors Analyzed:** {len(self.competitors)}

---

> **Purpose:** Strategic competitive analysis for website revamp and SEO/marketing strategy.
> Based on 29MB of research data including GBP analysis, competitor research, and market intelligence.

---"""

    def _executive_summary(self) -> str:
        """Generate executive summary with key metrics"""
        lines = [
            "## Executive Summary",
            "",
        ]

        # Get research data
        gbp = self.ri.research.gbp_profile
        exec_sum = self.ri.research.executive_summary

        if exec_sum and exec_sum.bottom_line:
            lines.extend([
                f"**{exec_sum.bottom_line}**",
                "",
            ])

        if gbp:
            # Find main competitor for comparison
            main_competitor = None
            for comp in self.competitors:
                if comp.trust_signals.review_count and comp.trust_signals.review_count > gbp.review_count:
                    main_competitor = comp
                    break

            lines.extend([
                "### Key Metrics",
                "",
                f"- **Rating:** {gbp.rating} ({gbp.review_count} reviews)",
                f"- **99% 5-star reviews** ({gbp.rating_distribution.get('5', 0)} out of {gbp.review_count})",
            ])

            if main_competitor:
                gap_ratio = main_competitor.trust_signals.review_count / gbp.review_count
                lines.append(f"- **Review gap:** {gbp.review_count} vs {main_competitor.name}'s {main_competitor.trust_signals.review_count} ({gap_ratio:.1f}x behind)")

            lines.append("")

        # Top topics from reviews
        if gbp and gbp.place_topics:
            lines.extend([
                "### Review Sentiment (What Customers Love)",
                "",
                "```",
            ])
            for topic, count in sorted(gbp.place_topics.items(), key=lambda x: x[1], reverse=True)[:6]:
                indicator = " <-- YOUR DIFFERENTIATOR" if topic in ['storyline', 'movie', 'immersive'] else ""
                lines.append(f"{topic:15} {count:3} mentions{indicator}")
            lines.extend(["```", ""])

        # Threat distribution
        if self.competitors:
            critical = sum(1 for c in self.competitors if c.overall_threat_level == ThreatLevel.CRITICAL)
            high = sum(1 for c in self.competitors if c.overall_threat_level == ThreatLevel.HIGH)
            medium = sum(1 for c in self.competitors if c.overall_threat_level == ThreatLevel.MEDIUM)
            low = sum(1 for c in self.competitors if c.overall_threat_level == ThreatLevel.LOW)

            lines.extend([
                "### Threat Distribution",
                "",
            ])
            if critical:
                lines.append(f"- CRITICAL: {critical}")
            if high:
                lines.append(f"- HIGH: {high}")
            if medium:
                lines.append(f"- MEDIUM: {medium}")
            if low:
                lines.append(f"- LOW: {low}")
            lines.append("")

        return "\n".join(lines)

    def _competitive_positioning_map(self) -> str:
        """Generate ASCII positioning map"""
        lines = [
            "## Competitive Positioning Map",
            "",
        ]

        positioning_map = self.ri.get_positioning_map()
        if positioning_map:
            lines.extend([
                "```",
                positioning_map,
                "```",
                "",
                "**escape.exe's defensible position:** Upper-right quadrant (Premium + Innovative)",
                "",
            ])
        else:
            # Generate default map
            lines.extend([
                "```",
                "                 PREMIUM EXPERIENCE",
                "                        |",
                "                        |",
                "    escape.exe *--------+--------",
                "    (tech + narrative)  |",
                "                        |",
                "    --------------------+--------------------",
                "    TRADITIONAL         |           INNOVATIVE",
                "    PUZZLES             |           TECH",
                "                        |",
                "                        |",
                "         Captured LV o--+",
                "         (traditional)  |",
                "                        |",
                "                 STANDARD EXPERIENCE",
                "```",
                "",
            ])

        return "\n".join(lines)

    def _competitor_profiles(self) -> str:
        """Generate competitor profiles section"""
        lines = [
            "## Competitor Profiles",
            "",
        ]

        # Sort by threat level
        sorted_comps = sorted(
            self.competitors,
            key=lambda c: ['low', 'medium', 'high', 'critical'].index(c.overall_threat_level.value),
            reverse=True
        )

        for i, comp in enumerate(sorted_comps, 1):
            threat_emoji = self._threat_emoji(comp.overall_threat_level)
            threat_label = "PRIMARY THREAT" if comp.overall_threat_level == ThreatLevel.HIGH else comp.overall_threat_level.value.upper()

            lines.extend([
                f"### {i}. {comp.name} {threat_emoji} ({threat_label})",
                "",
            ])

            if comp.trust_signals.review_count:
                lines.append(f"- **Reviews:** {comp.trust_signals.review_count}")
            if comp.trust_signals.rating:
                lines.append(f"- **Rating:** {comp.trust_signals.rating}")

            # Compare to us
            if self.ri.research.gbp_profile:
                our_reviews = self.ri.research.gbp_profile.review_count
                if comp.trust_signals.review_count:
                    if comp.trust_signals.review_count > our_reviews:
                        ratio = comp.trust_signals.review_count / our_reviews
                        lines.append(f"- **Gap:** {ratio:.1f}x more reviews than us")
                    else:
                        ratio = our_reviews / comp.trust_signals.review_count
                        lines.append(f"- **Advantage:** We have {ratio:.1f}x more reviews")

            if comp.strengths:
                lines.append(f"- **Strengths:** {', '.join(comp.strengths[:3])}")
            if comp.weaknesses:
                lines.append(f"- **Weaknesses:** {', '.join(comp.weaknesses[:3])}")

            lines.append("")

        return "\n".join(lines)

    def _escape_exe_moats(self) -> str:
        """Generate competitive moats section"""
        lines = [
            "## escape.exe Competitive Moat",
            "",
            "### What ONLY escape.exe Can Claim",
            "",
        ]

        moats = self.ri.get_moat_identification()
        if moats:
            for i, moat in enumerate(moats, 1):
                lines.append(f"{i}. **{moat}**")
        else:
            # Use brand differentiators
            for i, diff in enumerate(self.client.brand.differentiators, 1):
                lines.append(f"{i}. **{diff}**")

        lines.extend([
            "",
            "### Why Competitors Can't Match",
            "",
            "| Feature | escape.exe | Industry Standard |",
            "|---------|------------|-------------------|",
            "| AI Characters | GAVIN (proprietary) | No |",
            "| Branching Narratives | Multiple endings | Single outcome |",
            "| Adaptive Systems | Real-time difficulty | Fixed difficulty |",
            "| Tech Integration | Deep custom tech | Surface-level props |",
            "| Gaming Expertise | Founders' background | Varies |",
            "",
        ])

        return "\n".join(lines)

    def _market_gaps_section(self) -> str:
        """Generate market gaps section"""
        lines = [
            "## Market Gaps & Opportunities",
            "",
            "### Underserved Segments",
            "",
        ]

        market_gaps = self.ri.research.market_gaps
        if market_gaps:
            for i, gap in enumerate(market_gaps, 1):
                if not gap.geographic:
                    lines.extend([
                        f"**{i}. {gap.segment}**",
                        f"- Current state: {gap.description}",
                        f"- Opportunity: {gap.opportunity}",
                        "",
                    ])

            # Geographic gaps
            geo_gaps = [g for g in market_gaps if g.geographic]
            if geo_gaps:
                lines.extend([
                    "### Geographic Expansion Opportunities",
                    "",
                ])
                for gap in geo_gaps:
                    lines.append(f"- {gap.description}")
                lines.append("")
        else:
            lines.extend([
                "1. **Corporate Daytime** - Most rooms evening-only, opportunity for earlier hours",
                "2. **Tech Enthusiasts** - Nobody targeting gamers/tech crowd specifically",
                "3. **Film/Narrative Buffs** - \"Interactive cinema\" positioning unique",
                "4. **Repeat Visitors** - Multiple endings create replay value competitors can't match",
                "",
            ])

        return "\n".join(lines)

    def _seo_opportunities(self) -> str:
        """Generate SEO opportunities section"""
        lines = [
            "## SEO Opportunities",
            "",
        ]

        seo_opps = self.ri.get_seo_opportunities()
        if seo_opps:
            # Primary keywords (currently ranking)
            primary = [k for k in seo_opps if k['current_rank'] and k['tier'] == 'primary']
            if primary:
                lines.extend([
                    "### Primary Keywords (Currently Ranking)",
                    "",
                    "| Keyword | Current Rank | Top Ranker | Target |",
                    "|---------|--------------|------------|--------|",
                ])
                for kw in primary:
                    lines.append(f"| {kw['keyword']} | #{kw['current_rank']} | {kw['top_ranker'] or 'N/A'} | #1 |")
                lines.append("")

            # Keywords not ranking
            missing = [k for k in seo_opps if not k['current_rank']]
            if missing:
                lines.extend([
                    "### Keywords Not Ranking (Opportunities)",
                    "",
                    "| Keyword | Opportunity |",
                    "|---------|-------------|",
                ])
                for kw in missing[:10]:
                    lines.append(f"| {kw['keyword']} | {kw['opportunity'] or 'Create targeted content'} |")
                lines.append("")

            lines.extend([
                "### Content Recommendations",
                "",
                "1. Create individual experience/room pages",
                "2. Build location-based landing pages (Allentown, Easton, Poconos)",
                "3. Launch blog for long-tail keyword targeting",
                "4. Add LocalBusiness + Event schema markup",
                "",
            ])
        else:
            lines.extend([
                "*SEO keyword data not available. Run keyword analysis to populate.*",
                "",
            ])

        return "\n".join(lines)

    def _threat_assessment(self) -> str:
        """Generate threat assessment matrix"""
        lines = [
            "## Threat Assessment Matrix",
            "",
            "| Competitor | Threat | Reviews | Rating | Review Gap |",
            "|------------|--------|---------|--------|------------|",
        ]

        our_reviews = self.ri.research.gbp_profile.review_count if self.ri.research.gbp_profile else 0

        for comp in sorted(self.competitors, key=lambda c: c.overall_threat_level.value, reverse=True):
            threat_emoji = self._threat_emoji(comp.overall_threat_level)
            reviews = comp.trust_signals.review_count or "-"
            rating = f"{comp.trust_signals.rating:.1f}" if comp.trust_signals.rating else "-"

            gap = "-"
            if comp.trust_signals.review_count and our_reviews:
                if comp.trust_signals.review_count > our_reviews:
                    gap = f"+{comp.trust_signals.review_count - our_reviews}"
                else:
                    gap = f"-{our_reviews - comp.trust_signals.review_count}"

            lines.append(f"| {comp.name[:25]} | {threat_emoji} {comp.overall_threat_level.value} | {reviews} | {rating} | {gap} |")

        lines.append("")
        return "\n".join(lines)

    def _findings_summary(self) -> str:
        """Generate findings summary"""
        lines = [
            "## Key Findings",
            "",
        ]

        if self.findings.findings:
            # Group by type
            gaps = [f for f in self.findings.findings if f.finding_type.value == "gap"]
            opportunities = [f for f in self.findings.findings if f.finding_type.value == "opportunity"]
            strengths = [f for f in self.findings.findings if f.finding_type.value == "strength"]

            if gaps:
                lines.extend([
                    "### Gaps to Address",
                    "",
                ])
                for gap in gaps[:5]:
                    lines.append(f"- **{gap.observation}**")
                    if gap.details:
                        lines.append(f"  - {gap.details[:100]}...")
                lines.append("")

            if opportunities:
                lines.extend([
                    "### Opportunities to Capture",
                    "",
                ])
                for opp in opportunities[:5]:
                    lines.append(f"- **{opp.observation}**")
                lines.append("")

            if strengths:
                lines.extend([
                    "### Strengths to Leverage",
                    "",
                ])
                for strength in strengths[:5]:
                    lines.append(f"- **{strength.observation}**")
                lines.append("")
        else:
            lines.append("*No findings generated. Run analysis pipeline to populate.*")
            lines.append("")

        return "\n".join(lines)

    def _actionable_insights(self) -> str:
        """Generate actionable insights section"""
        lines = [
            "## Actionable Insights",
            "",
        ]

        if self.insights.insights:
            for i, insight in enumerate(sorted(self.insights.insights, key=lambda x: x.priority_score, reverse=True), 1):
                lines.extend([
                    f"### {i}. {insight.problem[:60]}",
                    "",
                    f"**Priority Score:** {insight.priority_score}/100",
                    f"**Effort:** {insight.effort_estimate.value}",
                    f"**Type:** {insight.insight_type.value}",
                    "",
                    f"**Hypothesis:** {insight.hypothesis}",
                    "",
                    f"**Recommended Action:** {insight.spec_change}",
                    "",
                    "**Expected Impact:**",
                    f"- Rank: {insight.expected_impact.rank_impact.value}",
                    f"- Conversion: {insight.expected_impact.cvr_impact.value}",
                    f"- Trust: {insight.expected_impact.trust_impact.value}",
                    "",
                    "---",
                    "",
                ])
        else:
            lines.append("*No insights generated. Run analysis pipeline to populate.*")
            lines.append("")

        return "\n".join(lines)

    def _recommendations(self) -> str:
        """Generate recommendations section"""
        exec_sum = self.ri.research.executive_summary

        lines = [
            "## Strategic Recommendations",
            "",
        ]

        if exec_sum and exec_sum.priorities:
            if exec_sum.priorities.get('immediate'):
                lines.extend([
                    "### Immediate (30 Days)",
                    "",
                ])
                for item in exec_sum.priorities['immediate']:
                    lines.append(f"1. {item}")
                lines.append("")

            if exec_sum.priorities.get('medium_term'):
                lines.extend([
                    "### Medium-Term (60-90 Days)",
                    "",
                ])
                for item in exec_sum.priorities['medium_term']:
                    lines.append(f"1. {item}")
                lines.append("")

            if exec_sum.priorities.get('long_term'):
                lines.extend([
                    "### Long-Term (90+ Days)",
                    "",
                ])
                for item in exec_sum.priorities['long_term']:
                    lines.append(f"1. {item}")
                lines.append("")
        else:
            lines.extend([
                "### Immediate (30 Days)",
                "",
                "1. Create individual experience pages for each room",
                "2. Add trust signals to booking page (reviews, badges)",
                "3. Standardize CTAs to 2-3 consistent options",
                "4. Launch review generation campaign (QR codes, follow-up emails)",
                "",
                "### Medium-Term (60-90 Days)",
                "",
                "1. Build location-based landing pages (Allentown, Easton)",
                "2. Develop content marketing strategy (blog, guides)",
                "3. Implement schema markup across site",
                "4. Consider expanding operating hours for corporate bookings",
                "",
                "### Long-Term (90+ Days)",
                "",
                "1. Video content strategy (room teasers, testimonials)",
                "2. Partnership marketing (hotels, ArtsQuest, universities)",
                "3. PR/press coverage campaign",
                "4. Community building and loyalty program",
                "",
            ])

        lines.extend([
            "---",
            "",
            "*End of Competitive Analysis*",
            "",
            f"*Generated by Firecrawl Scraper Pipeline on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        ])

        return "\n".join(lines)

    def _threat_emoji(self, level: ThreatLevel) -> str:
        """Get emoji for threat level"""
        return {
            ThreatLevel.CRITICAL: "[CRITICAL]",
            ThreatLevel.HIGH: "[HIGH]",
            ThreatLevel.MEDIUM: "[MEDIUM]",
            ThreatLevel.LOW: "[LOW]",
        }.get(level, "[?]")


def export_escape_exe_competitive_analysis(
    research_path: str = DEFAULT_RESEARCH_PATH,
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> str:
    """
    One-command export: Load research data and generate competitive analysis.

    Args:
        research_path: Path to escapeexe-research repo
        output_dir: Directory to write output

    Returns:
        Path to generated markdown file
    """
    # Load research data
    print(f"Loading research data from: {research_path}")
    loader = ResearchDataLoader(research_path)
    research_data = loader.load_all()

    print(f"  - GBP Profile: {research_data.gbp_profile.title if research_data.gbp_profile else 'Not found'}")
    print(f"  - Competitors: {len(research_data.competitors)}")
    print(f"  - SEO Keywords: {len(research_data.seo_keywords)}")
    print(f"  - Market Gaps: {len(research_data.market_gaps)}")
    print(f"  - Moats: {len(research_data.moats)}")

    # Create integration
    integration = ResearchIntegration(research_data)

    # Build profiles
    competitors = integration.build_competitor_profiles()
    print(f"  - Competitor Profiles Built: {len(competitors)}")

    findings = integration.build_findings()
    print(f"  - Findings Generated: {len(findings.findings)}")

    insights = integration.build_insights()
    print(f"  - Insights Generated: {len(insights.insights)}")

    # Create client
    client = create_escape_exe_client(integration)
    print(f"  - Client: {client.name} ({client.vertical.value})")

    # Generate analysis
    generator = ResearchCompetitiveAnalysisGenerator(integration, client)
    markdown = generator.generate()

    # Write output
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "escape-exe_competitive.md"

    with open(output_file, 'w') as f:
        f.write(markdown)

    print(f"\nCompetitive analysis written to: {output_file}")
    print(f"File size: {len(markdown):,} characters")

    return str(output_file)


def export_all_escape_exe_deliverables(
    research_path: str = DEFAULT_RESEARCH_PATH,
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> dict:
    """
    Export ALL deliverables for escape.exe with research data integration.

    Generates:
    - Competitive Analysis (escape-exe_competitive.md)
    - Client Brief (escape-exe_client_brief.md)
    - Content Brief (escape-exe_content_brief.md)
    - Implementation Spec (escape-exe_implementation.md)
    - SEO Strategy (escape-exe_seo_strategy.md)

    Args:
        research_path: Path to escapeexe-research repo
        output_dir: Directory to write outputs

    Returns:
        Dict with paths to all generated files
    """
    # Load research data
    print("=" * 60)
    print("ESCAPE.EXE DELIVERABLES EXPORT")
    print("=" * 60)
    print(f"\nLoading research data from: {research_path}")

    loader = ResearchDataLoader(research_path)
    research_data = loader.load_all()

    print(f"  - GBP Profile: {research_data.gbp_profile.title if research_data.gbp_profile else 'Not found'}")
    print(f"  - Competitors: {len(research_data.competitors)}")
    print(f"  - SEO Keywords: {len(research_data.seo_keywords)}")
    print(f"  - Market Gaps: {len(research_data.market_gaps)}")
    print(f"  - Moats: {len(research_data.moats)}")

    # Create integration
    integration = ResearchIntegration(research_data)

    # Build common data
    competitors = integration.build_competitor_profiles()
    findings = integration.build_findings()
    insights = integration.build_insights()

    print(f"\n  - Competitor Profiles Built: {len(competitors)}")
    print(f"  - Findings Generated: {len(findings.findings)}")
    print(f"  - Insights Generated: {len(insights.insights)}")

    # Create client
    client = create_escape_exe_client(integration)
    print(f"  - Client: {client.name} ({client.vertical.value})")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = {}

    # 1. Competitive Analysis
    print("\n" + "-" * 40)
    print("Generating: Competitive Analysis")
    comp_gen = ResearchCompetitiveAnalysisGenerator(integration, client)
    comp_md = comp_gen.generate()
    comp_file = output_path / "escape-exe_competitive.md"
    with open(comp_file, 'w') as f:
        f.write(comp_md)
    generated_files['competitive_analysis'] = str(comp_file)
    print(f"  Written: {comp_file} ({len(comp_md):,} chars)")

    # 2. Client Brief
    print("\n" + "-" * 40)
    print("Generating: Client Brief")
    client_gen = ClientBriefGenerator(
        client=client,
        matrix=None,  # No matrix for now
        insights=insights,
        findings=findings,
        research_integration=integration,
    )
    client_md = client_gen.generate()
    client_file = output_path / "escape-exe_client_brief.md"
    with open(client_file, 'w') as f:
        f.write(client_md)
    generated_files['client_brief'] = str(client_file)
    print(f"  Written: {client_file} ({len(client_md):,} chars)")

    # 3. Content Brief
    print("\n" + "-" * 40)
    print("Generating: Content Brief")
    content_gen = ContentBriefGenerator(
        client=client,
        output_spec=None,
        matrix=None,
        research_integration=integration,
    )
    content_md = content_gen.generate()
    content_file = output_path / "escape-exe_content_brief.md"
    with open(content_file, 'w') as f:
        f.write(content_md)
    generated_files['content_brief'] = str(content_file)
    print(f"  Written: {content_file} ({len(content_md):,} chars)")

    # 4. Implementation Spec
    print("\n" + "-" * 40)
    print("Generating: Implementation Spec")
    impl_gen = ImplementationSpecGenerator(
        client=client,
        output_spec=None,
        matrix=None,
        insights=insights,
        research_integration=integration,
    )
    impl_md = impl_gen.generate()
    impl_file = output_path / "escape-exe_implementation.md"
    with open(impl_file, 'w') as f:
        f.write(impl_md)
    generated_files['implementation_spec'] = str(impl_file)
    print(f"  Written: {impl_file} ({len(impl_md):,} chars)")

    # 5. SEO Strategy
    print("\n" + "-" * 40)
    print("Generating: SEO Strategy")
    seo_gen = SEOStrategyGenerator(
        client=client,
        matrix=None,
        insights=insights,
        output_spec=None,
        research_integration=integration,
    )
    seo_md = seo_gen.generate()
    seo_file = output_path / "escape-exe_seo_strategy.md"
    with open(seo_file, 'w') as f:
        f.write(seo_md)
    generated_files['seo_strategy'] = str(seo_file)
    print(f"  Written: {seo_file} ({len(seo_md):,} chars)")

    # Summary
    total_chars = len(comp_md) + len(client_md) + len(content_md) + len(impl_md) + len(seo_md)
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"\nTotal deliverables: 5")
    print(f"Total content: {total_chars:,} characters")
    print(f"Output directory: {output_dir}")
    print("\nFiles generated:")
    for name, path in generated_files.items():
        print(f"  - {name}: {Path(path).name}")

    return generated_files


if __name__ == "__main__":
    export_all_escape_exe_deliverables()
