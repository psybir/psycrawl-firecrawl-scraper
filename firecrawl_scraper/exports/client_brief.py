"""
Client Brief Generator - Executive summary for stakeholders

Generates a high-level overview suitable for strategy discussions
and AI agent context-setting.

Enhanced with optional research integration for richer context.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from ..models import (
    Client,
    IntentGeoMatrix,
    InsightReport,
    FindingsReport,
    Vertical,
    ENTERTAINMENT_VERTICALS,
    HEALTHCARE_VERTICALS,
    BLUE_COLLAR_VERTICALS,
)
from ..models.entities import get_business_model, BusinessModel

if TYPE_CHECKING:
    from ..integrations.research_integration import ResearchIntegration


class ClientBriefGenerator:
    """Generate executive client brief markdown"""

    def __init__(
        self,
        client: Client,
        matrix: Optional[IntentGeoMatrix] = None,
        insights: Optional[InsightReport] = None,
        findings: Optional[FindingsReport] = None,
        research_integration: Optional['ResearchIntegration'] = None,
    ):
        self.client = client
        self.matrix = matrix
        self.insights = insights
        self.findings = findings
        self.research = research_integration

    def generate(self) -> str:
        """Generate complete client brief markdown"""
        sections = [
            self._header(),
            self._business_overview(),
        ]

        # Add research-enhanced sections
        if self.research:
            review_sentiment = self._review_sentiment()
            if review_sentiment:
                sections.append(review_sentiment)

        sections.extend([
            self._current_state(),
            self._market_position(),
        ])

        # Add competitive moats from research
        if self.research:
            moats = self._competitive_moats()
            if moats:
                sections.append(moats)

        sections.extend([
            self._key_opportunities(),
            self._priority_recommendations(),
            self._success_metrics(),
            self._next_steps(),
        ])

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate header section"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        business_model = get_business_model(self.client.vertical)

        return f"""# Client Brief: {self.client.name}

**Document Type:** Executive Strategy Summary
**Generated:** {timestamp}
**Vertical:** {self.client.vertical.value.replace('_', ' ').title()}
**Business Model:** {business_model.value.replace('_', ' ').title()}

---

> **Purpose:** This brief provides strategic context for AI agents and human teams
> working on {self.client.name}'s digital presence. Start here before diving into
> detailed specifications.

---"""

    def _business_overview(self) -> str:
        """Generate business overview section"""
        lines = [
            "## Business Overview",
            "",
        ]

        # Basic info
        lines.append(f"**Business Name:** {self.client.name}")
        if self.client.domain:
            lines.append(f"**Domain:** {self.client.domain}")

        # Location info
        primary_loc = self.client.primary_location
        if primary_loc:
            lines.append(f"**Primary Location:** {primary_loc.name}")

        # Services
        money_services = self.client.money_services
        if money_services:
            lines.append(f"**Core Services:** {', '.join([s.name for s in money_services])}")

        # GBP data
        if self.client.gbp_profile:
            gbp = self.client.gbp_profile
            if gbp.rating and gbp.review_count:
                lines.append(f"**Google Rating:** {gbp.rating} ({gbp.review_count} reviews)")

        # Brand
        if self.client.brand:
            if self.client.brand.tagline:
                lines.append(f"**Tagline:** \"{self.client.brand.tagline}\"")
            if self.client.brand.differentiators:
                lines.append("")
                lines.append("**Key Differentiators:**")
                for diff in self.client.brand.differentiators[:5]:
                    lines.append(f"- {diff}")

        return "\n".join(lines)

    def _current_state(self) -> str:
        """Generate current state analysis"""
        lines = [
            "## Current State Analysis",
            "",
        ]

        # Matrix summary
        if self.matrix:
            lines.append(f"**Service/Geo Coverage:** {len(self.matrix.cells)} target combinations")
            lines.append("")

            # Services breakdown
            lines.append("### Services")
            lines.append("")
            for service in self.client.services:
                money_flag = "💰" if service.is_money_service else ""
                lines.append(f"- **{service.name}** {money_flag}")
                if service.short_description:
                    lines.append(f"  - {service.short_description[:100]}...")

            lines.append("")

            # Locations breakdown
            lines.append("### Geographic Coverage")
            lines.append("")
            lines.append("| Location | Geo Bucket | Priority | Current Rank |")
            lines.append("|----------|------------|----------|--------------|")

            for loc in self.client.locations[:10]:
                rank = f"{loc.current_rank:.1f}" if loc.current_rank else "N/A"
                priority = loc.priority or "standard"
                lines.append(f"| {loc.name} | {loc.geo_bucket.value} | {priority} | {rank} |")

            if len(self.client.locations) > 10:
                lines.append(f"| ... | +{len(self.client.locations) - 10} more | | |")

        return "\n".join(lines)

    def _market_position(self) -> str:
        """Generate market position section"""
        lines = [
            "## Market Position",
            "",
        ]

        # Vertical-specific context
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "### Entertainment Market Context",
                "",
                "**Business Model:** Destination - customers travel TO you",
                "",
                "**Key Success Factors:**",
                "- Seamless online booking experience",
                "- Compelling visual content (photos/videos)",
                "- Strong review presence and social proof",
                "- Group/party package offerings",
                "- Geographic reach beyond local area",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "### Service Trade Market Context",
                "",
                "**Business Model:** Service Delivery - you travel TO customers",
                "",
                "**Key Success Factors:**",
                "- Immediate response capability (click-to-call)",
                "- Trust signals (licenses, insurance, warranties)",
                "- Before/after proof galleries",
                "- Service area page coverage",
                "- Emergency availability messaging",
                "",
            ])
        elif self.client.vertical in HEALTHCARE_VERTICALS:
            lines.extend([
                "### Healthcare Market Context",
                "",
                "**Business Model:** Hybrid - primarily in-office",
                "",
                "**Key Success Factors:**",
                "- Provider credential visibility",
                "- Online scheduling capability",
                "- Patient testimonials and reviews",
                "- Insurance/payment transparency",
                "",
            ])

        # Findings summary
        if self.findings and self.findings.findings:
            lines.append("### Key Findings from Analysis")
            lines.append("")

            # Group by type
            gaps = [f for f in self.findings.findings if f.finding_type.value == "gap"]
            opportunities = [f for f in self.findings.findings if f.finding_type.value == "opportunity"]
            threats = [f for f in self.findings.findings if f.finding_type.value == "threat"]

            if gaps:
                lines.append(f"**Gaps Identified:** {len(gaps)}")
            if opportunities:
                lines.append(f"**Opportunities Found:** {len(opportunities)}")
            if threats:
                lines.append(f"**Competitive Threats:** {len(threats)}")

        return "\n".join(lines)

    def _key_opportunities(self) -> str:
        """Generate key opportunities section"""
        lines = [
            "## Key Opportunities",
            "",
        ]

        if self.insights and self.insights.insights:
            # Sort by priority
            sorted_insights = sorted(
                self.insights.insights,
                key=lambda x: x.priority_score or 0,
                reverse=True
            )

            for i, insight in enumerate(sorted_insights[:5], 1):
                impact_emoji = self._get_impact_emoji(insight)
                lines.append(f"### {i}. {insight.title} {impact_emoji}")
                lines.append("")
                lines.append(f"**Problem:** {insight.problem}")
                lines.append("")
                lines.append(f"**Hypothesis:** {insight.hypothesis}")
                lines.append("")
                lines.append(f"**Recommended Action:** {insight.spec_change}")
                lines.append("")

                if insight.expected_impact:
                    impacts = []
                    if insight.expected_impact.cvr_impact:
                        impacts.append(f"CVR: {insight.expected_impact.cvr_impact.value}")
                    if insight.expected_impact.rank_impact:
                        impacts.append(f"Rank: {insight.expected_impact.rank_impact.value}")
                    if insight.expected_impact.trust_impact:
                        impacts.append(f"Trust: {insight.expected_impact.trust_impact.value}")
                    if impacts:
                        lines.append(f"**Expected Impact:** {' | '.join(impacts)}")

                if insight.effort_estimate:
                    lines.append(f"**Effort:** {insight.effort_estimate.value}")

                lines.append("")
                lines.append("---")
                lines.append("")
        else:
            lines.append("*Opportunities will be identified once competitor data is collected.*")

        return "\n".join(lines)

    def _priority_recommendations(self) -> str:
        """Generate priority recommendations"""
        lines = [
            "## Priority Recommendations",
            "",
            "### Quick Wins (Do First)",
            "",
        ]

        if self.insights:
            quick_wins = self.insights.quick_wins[:3] if hasattr(self.insights, 'quick_wins') else []

            if quick_wins:
                for win in quick_wins:
                    lines.append(f"- [ ] **{win.title}:** {win.spec_change}")
            else:
                lines.append("- [ ] Implement sticky CTA (universal quick win)")
                lines.append("- [ ] Add prominent review widget above fold")
                lines.append("- [ ] Ensure click-to-call on mobile")

        lines.extend([
            "",
            "### Strategic Priorities (Plan Next)",
            "",
        ])

        # Vertical-specific priorities
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "- [ ] Implement/optimize online booking system",
                "- [ ] Create compelling experience photo galleries",
                "- [ ] Develop group/corporate booking pages",
                "- [ ] Build service-area pages for extended reach",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "- [ ] Create service-area landing pages",
                "- [ ] Build before/after gallery",
                "- [ ] Add trust badges and certifications",
                "- [ ] Implement backlink acquisition strategy",
            ])
        elif self.client.vertical in HEALTHCARE_VERTICALS:
            lines.extend([
                "- [ ] Implement online scheduling",
                "- [ ] Create provider profile pages",
                "- [ ] Add patient testimonials section",
                "- [ ] Build service-specific landing pages",
            ])

        return "\n".join(lines)

    def _success_metrics(self) -> str:
        """Generate success metrics section"""
        lines = [
            "## Success Metrics",
            "",
            "### 30-Day Targets",
            "",
        ]

        if self.matrix:
            lines.append(f"- [ ] {len(self.matrix.cells)} priority pages published")

        lines.extend([
            "- [ ] Core conversion elements implemented",
            "- [ ] Mobile experience optimized",
            "- [ ] Schema markup deployed",
            "",
            "### 90-Day Targets",
            "",
            "- [ ] Service-area pages indexed and ranking",
            "- [ ] Review count growing (+10% baseline)",
            "- [ ] Backlink acquisition started",
            "- [ ] Content calendar executing",
            "",
            "### 6-Month Goals",
            "",
        ])

        # Vertical-specific goals
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "- [ ] Online booking conversion rate > 3%",
                "- [ ] Geographic reach expanded to 60+ mile radius",
                "- [ ] Corporate/group bookings increased 25%",
            ])
        else:
            lines.extend([
                "- [ ] Local pack top 3 in primary locations",
                "- [ ] Authority score doubled",
                "- [ ] Organic traffic +50% from baseline",
            ])

        return "\n".join(lines)

    def _next_steps(self) -> str:
        """Generate next steps section"""
        return """## Next Steps for AI Agents

### For Strategy Agent
1. Review this brief for context
2. Validate priorities against business goals
3. Approve implementation sequence

### For Builder Agent
1. Read `_implementation.md` for technical specs
2. Start with homepage and core service pages
3. Implement conversion elements first

### For Content Agent
1. Read `_content.md` for page-by-page requirements
2. Generate LLM answer blocks for services
3. Create location-specific content variations

### For SEO Agent
1. Read `_seo.md` for optimization strategy
2. Implement schema markup
3. Execute internal linking plan

---

*End of Client Brief*"""

    def _review_sentiment(self) -> Optional[str]:
        """Generate review sentiment section from research data"""
        if not self.research or not self.research.research.gbp_profile:
            return None

        gbp = self.research.research.gbp_profile
        if not gbp.place_topics:
            return None

        lines = [
            "## Customer Voice (Review Analysis)",
            "",
            "### What Customers Mention Most",
            "",
            "```",
        ]

        for topic, count in sorted(gbp.place_topics.items(), key=lambda x: x[1], reverse=True)[:8]:
            bar = "█" * min(count, 30)
            lines.append(f"{topic:15} {bar} ({count})")

        lines.extend([
            "```",
            "",
        ])

        # Highlight differentiators
        diff_topics = ['storyline', 'movie', 'immersive', 'ai', 'tech', 'skills']
        found_diffs = [t for t in gbp.place_topics.keys() if any(d in t.lower() for d in diff_topics)]
        if found_diffs:
            lines.extend([
                "### Differentiator Signals",
                "",
                "Review topics that validate your unique positioning:",
                "",
            ])
            for topic in found_diffs:
                lines.append(f"- **{topic}**: {gbp.place_topics[topic]} mentions")
            lines.append("")

        return "\n".join(lines)

    def _competitive_moats(self) -> Optional[str]:
        """Generate competitive moats section from research"""
        if not self.research:
            return None

        moats = self.research.get_moat_identification()
        if not moats:
            return None

        lines = [
            "## Competitive Moat",
            "",
            "### Defensible Advantages",
            "",
        ]

        for i, moat in enumerate(moats, 1):
            lines.append(f"{i}. **{moat}**")

        lines.extend([
            "",
            "*These advantages are difficult for competitors to replicate.*",
            "",
        ])

        return "\n".join(lines)

    def _get_impact_emoji(self, insight) -> str:
        """Get emoji indicator for insight impact"""
        if insight.effort_estimate and insight.expected_impact:
            effort = insight.effort_estimate.value
            cvr = insight.expected_impact.cvr_impact.value if insight.expected_impact.cvr_impact else "none"

            if effort == "low" and cvr == "high":
                return "🔥"  # Quick win
            elif cvr == "high":
                return "⭐"  # High impact
            elif effort == "low":
                return "✅"  # Easy
        return ""
