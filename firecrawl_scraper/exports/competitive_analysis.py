"""
Competitive Analysis Generator - Detailed competitor breakdown

Generates comprehensive competitor analysis for research agents
and strategic planning.

Enhanced with optional research integration for richer analysis
including positioning maps, moat identification, and market gaps.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from ..models import (
    Client,
    CompetitorProfile,
    FindingsReport,
    Finding,
    ThreatLevel,
    InsightReport,
)

if TYPE_CHECKING:
    from ..integrations.research_integration import ResearchIntegration


class CompetitiveAnalysisGenerator:
    """Generate competitive analysis markdown"""

    def __init__(
        self,
        client: Client,
        competitors: List[CompetitorProfile],
        findings: Optional[FindingsReport] = None,
        insights: Optional[InsightReport] = None,
        research_integration: Optional['ResearchIntegration'] = None,
    ):
        self.client = client
        self.competitors = competitors or []
        self.findings = findings
        self.insights = insights
        self.research = research_integration

    def generate(self) -> str:
        """Generate complete competitive analysis markdown"""
        sections = [
            self._header(),
            self._executive_summary(),
        ]

        # Add research-enhanced sections if research integration available
        if self.research:
            positioning_map = self._competitive_positioning()
            if positioning_map:
                sections.append(positioning_map)

        sections.extend([
            self._competitor_profiles(),
            self._comparative_analysis(),
            self._threat_assessment(),
        ])

        # Add research-enhanced sections
        if self.research:
            moats = self._moat_identification()
            if moats:
                sections.append(moats)

            market_gaps = self._market_gaps_section()
            if market_gaps:
                sections.append(market_gaps)

            seo_opps = self._seo_opportunities()
            if seo_opps:
                sections.append(seo_opps)

        sections.extend([
            self._gap_analysis(),
            self._opportunities(),
        ])

        # Add insights section if available
        if self.insights:
            sections.append(self._actionable_insights())

        sections.append(self._recommendations())

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate header section"""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        return f"""# Competitive Analysis: {self.client.name}

**Document Type:** Competitive Intelligence Report
**Generated:** {timestamp}
**Competitors Analyzed:** {len(self.competitors)}
**Confidence Level:** {'High' if len(self.competitors) >= 3 else 'Medium' if len(self.competitors) >= 1 else 'Low'}

---

> **Purpose:** Detailed breakdown of competitive landscape for strategic planning.
> Use this document for deep-dive research and competitive positioning.

---"""

    def _executive_summary(self) -> str:
        """Generate executive summary"""
        lines = [
            "## Executive Summary",
            "",
        ]

        if self.competitors:
            # Count threat levels
            critical = sum(1 for c in self.competitors if c.overall_threat_level == ThreatLevel.CRITICAL)
            high = sum(1 for c in self.competitors if c.overall_threat_level == ThreatLevel.HIGH)
            medium = sum(1 for c in self.competitors if c.overall_threat_level == ThreatLevel.MEDIUM)

            lines.extend([
                f"**Total Competitors Analyzed:** {len(self.competitors)}",
                "",
                "### Threat Distribution",
                "",
                f"- 🔴 Critical: {critical}",
                f"- 🟠 High: {high}",
                f"- 🟡 Medium: {medium}",
                f"- 🟢 Low: {len(self.competitors) - critical - high - medium}",
                "",
            ])

            # Top threats
            critical_comps = [c for c in self.competitors if c.overall_threat_level == ThreatLevel.CRITICAL]
            if critical_comps:
                lines.append("### Critical Threats")
                lines.append("")
                for comp in critical_comps:
                    lines.append(f"- **{comp.name}** ({comp.domain})")
                lines.append("")
        else:
            lines.extend([
                "*No competitor data collected yet. Run pipeline Stage 2 (COLLECT) to gather competitor information.*",
                "",
                "### What We'd Analyze",
                "",
                "Once competitor data is available, this section will include:",
                "- Competitor threat levels and rankings",
                "- Trust signal comparison",
                "- Conversion mechanics comparison",
                "- SEO structure analysis",
                "- Backlink profile comparison",
                "",
            ])

        return "\n".join(lines)

    def _competitor_profiles(self) -> str:
        """Generate individual competitor profiles"""
        lines = [
            "## Competitor Profiles",
            "",
        ]

        if not self.competitors:
            lines.append("*Competitor profiles will be generated after data collection.*")
            return "\n".join(lines)

        for i, comp in enumerate(self.competitors, 1):
            threat_emoji = self._threat_emoji(comp.overall_threat_level)

            lines.extend([
                f"### {i}. {comp.name} {threat_emoji}",
                "",
                f"**Domain:** {comp.domain}",
                f"**Threat Level:** {comp.overall_threat_level.value.upper()}",
                "",
            ])

            # Trust Signals
            lines.append("#### Trust Signals")
            lines.append("")
            ts = comp.trust_signals
            if ts.review_count:
                lines.append(f"- Reviews: {ts.review_count} ({ts.rating or 'N/A'} rating)")
            if ts.certifications:
                lines.append(f"- Certifications: {', '.join(ts.certifications[:3])}")
            if ts.licenses_shown:
                lines.append("- Licenses: Displayed")
            if ts.insurance_shown:
                lines.append("- Insurance: Displayed")
            if ts.before_after_gallery:
                lines.append(f"- Gallery: Yes ({ts.gallery_count or 'N/A'} images)")
            if ts.video_content:
                lines.append(f"- Video: Yes ({ts.video_count or 'N/A'} videos)")
            if ts.trust_score:
                lines.append(f"- **Trust Score: {ts.trust_score:.0f}/100**")
            lines.append("")

            # Conversion Mechanics
            lines.append("#### Conversion Mechanics")
            lines.append("")
            cm = comp.conversion_mechanics
            if cm.sticky_cta or cm.sticky_call:
                lines.append("- Sticky CTA: Yes")
            if cm.phone_clickable:
                lines.append("- Click-to-call: Yes")
            if cm.chat_widget:
                lines.append(f"- Live Chat: Yes ({cm.chat_provider or 'unknown provider'})")
            if cm.form_present:
                lines.append(f"- Contact Form: Yes ({cm.form_length or 'N/A'} fields)")
            if cm.online_booking:
                lines.append(f"- Online Booking: Yes ({cm.booking_provider or 'unknown provider'})")
            if cm.emergency_language:
                lines.append("- Emergency Language: Yes")
            if cm.conversion_score:
                lines.append(f"- **Conversion Score: {cm.conversion_score:.0f}/100**")
            lines.append("")

            # SEO Structure
            lines.append("#### SEO Structure")
            lines.append("")
            seo = comp.seo_structure
            if seo.page_count:
                lines.append(f"- Total Pages: {seo.page_count}")
            if seo.service_area_pages:
                lines.append(f"- Service Area Pages: {len(seo.service_area_pages)}")
            if seo.blog_active:
                lines.append(f"- Active Blog: Yes ({seo.blog_frequency or 'unknown frequency'})")
            if seo.schema_markup:
                lines.append(f"- Schema: {', '.join(seo.schema_markup.keys())}")
            lines.append("")

            # Strengths/Weaknesses
            if comp.strengths:
                lines.append("#### Strengths")
                for s in comp.strengths[:3]:
                    lines.append(f"- {s}")
                lines.append("")

            if comp.weaknesses:
                lines.append("#### Weaknesses")
                for w in comp.weaknesses[:3]:
                    lines.append(f"- {w}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _comparative_analysis(self) -> str:
        """Generate comparative analysis table"""
        lines = [
            "## Comparative Analysis",
            "",
        ]

        if not self.competitors:
            lines.append("*Comparative data will be available after competitor analysis.*")
            return "\n".join(lines)

        # Trust signals comparison
        lines.extend([
            "### Trust Signal Comparison",
            "",
            "| Competitor | Reviews | Rating | Certs | Gallery | Video |",
            "|------------|---------|--------|-------|---------|-------|",
        ])

        for comp in self.competitors:
            ts = comp.trust_signals
            reviews = str(ts.review_count) if ts.review_count else "-"
            rating = f"{ts.rating:.1f}" if ts.rating else "-"
            certs = "Yes" if ts.certifications else "No"
            gallery = "Yes" if ts.before_after_gallery else "No"
            video = "Yes" if ts.video_content else "No"
            lines.append(f"| {comp.name[:20]} | {reviews} | {rating} | {certs} | {gallery} | {video} |")

        # Client row
        if self.client.gbp_profile:
            gbp = self.client.gbp_profile
            lines.append(f"| **{self.client.name}** | {gbp.review_count or '-'} | {gbp.rating or '-'} | TBD | TBD | TBD |")

        lines.append("")

        # Conversion comparison
        lines.extend([
            "### Conversion Mechanics Comparison",
            "",
            "| Competitor | Sticky CTA | Chat | Booking | Emergency |",
            "|------------|------------|------|---------|-----------|",
        ])

        for comp in self.competitors:
            cm = comp.conversion_mechanics
            sticky = "Yes" if (cm.sticky_cta or cm.sticky_call) else "No"
            chat = "Yes" if cm.chat_widget else "No"
            booking = "Yes" if cm.online_booking else "No"
            emergency = "Yes" if cm.emergency_language else "No"
            lines.append(f"| {comp.name[:20]} | {sticky} | {chat} | {booking} | {emergency} |")

        lines.append("")

        return "\n".join(lines)

    def _threat_assessment(self) -> str:
        """Generate threat assessment section"""
        lines = [
            "## Threat Assessment",
            "",
        ]

        if not self.competitors:
            lines.append("*Threat assessment requires competitor data.*")
            return "\n".join(lines)

        # Sort by threat level
        sorted_comps = sorted(
            self.competitors,
            key=lambda c: ['low', 'medium', 'high', 'critical'].index(c.overall_threat_level.value),
            reverse=True
        )

        lines.extend([
            "### Threat Matrix",
            "",
            "| Competitor | Threat | Trust Score | CVR Score | Authority |",
            "|------------|--------|-------------|-----------|-----------|",
        ])

        for comp in sorted_comps:
            threat_emoji = self._threat_emoji(comp.overall_threat_level)
            trust = f"{comp.trust_signals.trust_score:.0f}" if comp.trust_signals.trust_score else "-"
            cvr = f"{comp.conversion_mechanics.conversion_score:.0f}" if comp.conversion_mechanics.conversion_score else "-"
            auth = str(comp.backlinks.domain_authority) if comp.backlinks.domain_authority else "-"
            lines.append(f"| {comp.name[:20]} | {threat_emoji} {comp.overall_threat_level.value} | {trust} | {cvr} | {auth} |")

        lines.append("")

        return "\n".join(lines)

    def _gap_analysis(self) -> str:
        """Generate gap analysis section"""
        lines = [
            "## Gap Analysis",
            "",
            "### Areas Where Competitors Outperform",
            "",
        ]

        if self.findings:
            gaps = [f for f in self.findings.findings if f.finding_type.value == "gap"]
            if gaps:
                for gap in gaps[:5]:
                    lines.append(f"- **{gap.observation}**")
                    if gap.details:
                        lines.append(f"  - {gap.details}")
            else:
                lines.append("*No significant gaps identified.*")
        else:
            lines.append("*Gap analysis requires findings data.*")

        lines.append("")

        return "\n".join(lines)

    def _opportunities(self) -> str:
        """Generate opportunities section"""
        lines = [
            "## Opportunities",
            "",
            "### Competitive Gaps to Exploit",
            "",
        ]

        if self.findings:
            opps = [f for f in self.findings.findings if f.finding_type.value == "opportunity"]
            if opps:
                for opp in opps[:5]:
                    lines.append(f"- **{opp.observation}**")
                    if opp.details:
                        lines.append(f"  - {opp.details}")
            else:
                lines.append("*Opportunities will be identified from competitive analysis.*")
        else:
            lines.append("*Opportunity analysis requires competitor data.*")

        lines.append("")

        return "\n".join(lines)

    def _competitive_positioning(self) -> Optional[str]:
        """Generate ASCII competitive positioning map from research"""
        if not self.research:
            return None

        positioning_map = self.research.get_positioning_map()
        if not positioning_map:
            return None

        lines = [
            "## Competitive Positioning Map",
            "",
            "```",
            positioning_map,
            "```",
            "",
            f"**{self.client.name}'s defensible position:** Upper-right quadrant (Premium + Innovative)",
            "",
        ]

        return "\n".join(lines)

    def _moat_identification(self) -> Optional[str]:
        """Generate competitive moats section from research"""
        if not self.research:
            return None

        moats = self.research.get_moat_identification()
        if not moats:
            return None

        lines = [
            f"## {self.client.name} Competitive Moat",
            "",
            f"### What ONLY {self.client.name} Can Claim",
            "",
        ]

        for i, moat in enumerate(moats, 1):
            lines.append(f"{i}. **{moat}**")

        lines.extend([
            "",
            "### Why Competitors Can't Match",
            "",
        ])

        # Add brand differentiators if available
        if self.client.brand and self.client.brand.differentiators:
            lines.extend([
                "| Feature | Us | Competitors |",
                "|---------|-------|-------------|",
            ])
            for diff in self.client.brand.differentiators[:5]:
                lines.append(f"| {diff[:40]} | Yes | No/Rarely |")
            lines.append("")

        return "\n".join(lines)

    def _market_gaps_section(self) -> Optional[str]:
        """Generate market gaps section from research"""
        if not self.research:
            return None

        market_gaps = self.research.get_market_gaps()
        if not market_gaps:
            return None

        lines = [
            "## Market Gaps & Opportunities",
            "",
            "### Underserved Segments",
            "",
        ]

        for i, gap in enumerate(market_gaps[:6], 1):
            lines.append(f"{i}. **{gap}**")

        lines.append("")
        return "\n".join(lines)

    def _seo_opportunities(self) -> Optional[str]:
        """Generate SEO opportunities section from research"""
        if not self.research:
            return None

        seo_opps = self.research.get_seo_opportunities()
        if not seo_opps:
            return None

        lines = [
            "## SEO Opportunities",
            "",
        ]

        # Primary keywords (currently ranking)
        primary = [k for k in seo_opps if k.get('current_rank') and k.get('tier') == 'primary']
        if primary:
            lines.extend([
                "### Primary Keywords (Currently Ranking)",
                "",
                "| Keyword | Current Rank | Top Ranker | Target |",
                "|---------|--------------|------------|--------|",
            ])
            for kw in primary[:5]:
                lines.append(f"| {kw['keyword']} | #{kw['current_rank']} | {kw.get('top_ranker', 'N/A')} | #1 |")
            lines.append("")

        # Keywords not ranking
        missing = [k for k in seo_opps if not k.get('current_rank')]
        if missing:
            lines.extend([
                "### Keywords Not Ranking (Opportunities)",
                "",
                "| Keyword | Opportunity |",
                "|---------|-------------|",
            ])
            for kw in missing[:8]:
                lines.append(f"| {kw['keyword']} | {kw.get('opportunity', 'Create targeted content')} |")
            lines.append("")

        return "\n".join(lines)

    def _actionable_insights(self) -> str:
        """Generate actionable insights section"""
        lines = [
            "## Actionable Insights",
            "",
        ]

        if self.insights and self.insights.insights:
            for i, insight in enumerate(sorted(self.insights.insights, key=lambda x: x.priority_score, reverse=True)[:5], 1):
                lines.extend([
                    f"### {i}. {insight.problem[:60]}",
                    "",
                    f"**Priority:** {insight.priority_score}/100 | **Effort:** {insight.effort_estimate.value}",
                    "",
                    f"**Action:** {insight.spec_change[:200]}",
                    "",
                ])
        else:
            lines.append("*Insights will be generated after full pipeline analysis.*")

        return "\n".join(lines)

    def _recommendations(self) -> str:
        """Generate recommendations section"""
        return """## Recommendations

### Immediate Actions
1. Address critical gaps identified in analysis
2. Match table-stakes features competitors have
3. Implement differentiation opportunities

### Strategic Positioning
1. Focus on unique value propositions
2. Build on existing strengths
3. Target competitor weaknesses

### Monitoring Plan
1. Track competitor changes monthly
2. Monitor new market entrants
3. Update analysis quarterly

---

*End of Competitive Analysis*"""

    def _threat_emoji(self, level: ThreatLevel) -> str:
        """Get emoji for threat level"""
        return {
            ThreatLevel.CRITICAL: "🔴",
            ThreatLevel.HIGH: "🟠",
            ThreatLevel.MEDIUM: "🟡",
            ThreatLevel.LOW: "🟢",
        }.get(level, "⚪")
