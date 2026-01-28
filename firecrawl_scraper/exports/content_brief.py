"""
Content Brief Generator - For content creators and AI writers

Generates detailed content requirements for each page type,
including LLM answer blocks and keyword targets.

Enhanced with optional research integration for keyword targets and content gaps.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from ..models import (
    Client,
    OutputSpec,
    IntentGeoMatrix,
    PageSpec,
    LLMAnswerBlock,
    Service,
    Vertical,
    ENTERTAINMENT_VERTICALS,
    BLUE_COLLAR_VERTICALS,
    HEALTHCARE_VERTICALS,
)

if TYPE_CHECKING:
    from ..integrations.research_integration import ResearchIntegration


class ContentBriefGenerator:
    """Generate content brief markdown"""

    def __init__(
        self,
        client: Client,
        output_spec: Optional[OutputSpec] = None,
        matrix: Optional[IntentGeoMatrix] = None,
        research_integration: Optional['ResearchIntegration'] = None,
    ):
        self.client = client
        self.output_spec = output_spec
        self.matrix = matrix
        self.research = research_integration

    def generate(self) -> str:
        """Generate complete content brief markdown"""
        sections = [
            self._header(),
            self._brand_voice(),
        ]

        # Add keyword strategy from research
        if self.research:
            keywords = self._keyword_targeting()
            if keywords:
                sections.append(keywords)

        sections.extend([
            self._content_principles(),
            self._homepage_content(),
            self._service_page_content(),
            self._service_area_content(),
            self._llm_answer_blocks(),
        ])

        # Add content gaps from research
        if self.research:
            gaps = self._content_gaps()
            if gaps:
                sections.append(gaps)

        sections.extend([
            self._faq_content(),
            self._about_content(),
            self._metadata_guidelines(),
        ])

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate header section"""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        return f"""# Content Brief: {self.client.name}

**Document Type:** Content Requirements Specification
**Generated:** {timestamp}
**Vertical:** {self.client.vertical.value.replace('_', ' ').title()}

---

> **Purpose:** Detailed content requirements for each page type.
> Content agents should follow these specifications to generate copy.

---"""

    def _brand_voice(self) -> str:
        """Generate brand voice section"""
        lines = [
            "## Brand Voice & Tone",
            "",
        ]

        if self.client.brand:
            tone = self.client.brand.tone.value if self.client.brand.tone else "professional"
            lines.append(f"**Primary Tone:** {tone.title()}")
            lines.append("")

            if self.client.brand.tagline:
                lines.append(f"**Tagline:** \"{self.client.brand.tagline}\"")
                lines.append("")

            if self.client.brand.differentiators:
                lines.append("**Key Messages to Reinforce:**")
                for diff in self.client.brand.differentiators:
                    lines.append(f"- {diff}")
                lines.append("")

        # Vertical-specific voice guidance
        lines.append("### Voice Guidelines")
        lines.append("")

        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "- **Exciting but not hyperbolic** - Build anticipation authentically",
                "- **Mystery-preserving** - Hint at experience without spoilers",
                "- **Inclusive** - All skill levels welcome",
                "- **Action-oriented** - Drive bookings naturally",
                "",
                "**Do Say:**",
                "- \"Experience the adventure\"",
                "- \"Multiple endings await\"",
                "- \"Perfect for groups\"",
                "",
                "**Don't Say:**",
                "- \"You won't believe what happens\" (too clickbait)",
                "- Specific puzzle details (spoilers)",
                "- \"Easy\" or \"Hard\" without context",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "- **Trustworthy and competent** - Expertise without arrogance",
                "- **Clear and direct** - No jargon confusion",
                "- **Reassuring** - Address anxieties proactively",
                "- **Local** - Emphasize community connection",
                "",
                "**Do Say:**",
                "- \"Licensed and insured\"",
                "- \"Same-day service available\"",
                "- \"Serving [City] for X years\"",
                "",
                "**Don't Say:**",
                "- \"Best in the business\" (unsubstantiated)",
                "- Complex technical jargon",
                "- \"Cheap\" (use \"affordable\")",
                "",
            ])
        elif self.client.vertical in HEALTHCARE_VERTICALS:
            lines.extend([
                "- **Caring and professional** - Empathy with expertise",
                "- **Clear and informative** - Educate without overwhelming",
                "- **Reassuring** - Address health anxieties",
                "- **Credentialed** - Highlight qualifications appropriately",
                "",
                "**Do Say:**",
                "- \"Board-certified\"",
                "- \"Personalized care\"",
                "- \"Comfortable environment\"",
                "",
                "**Don't Say:**",
                "- Medical claims without evidence",
                "- \"Guaranteed results\"",
                "- Competitor comparisons",
                "",
            ])

        return "\n".join(lines)

    def _content_principles(self) -> str:
        """Generate content principles section"""
        return """## Content Principles

### LLM-SEO Content Standards
All content should be **entity-clear, quotable, and unambiguous** for LLM consumption.

1. **Entity Clarity**
   - Start paragraphs with the subject
   - Use consistent entity naming
   - Define relationships explicitly

2. **Quotable Answers**
   - Lead with the answer, then explain
   - Use tight, direct language
   - Include specific numbers/timeframes

3. **Structured Information**
   - Use lists for processes
   - Use tables for comparisons
   - Use FAQs for common questions

### Content Length Guidelines
| Page Type | Word Count | Sections |
|-----------|------------|----------|
| Homepage | 800-1200 | 5-7 |
| Service Page | 1200-2000 | 6-8 |
| Service-Area | 600-1000 | 4-6 |
| About | 600-1000 | 4-5 |
| FAQ | 1500-2500 | 15-25 Q&As |"""

    def _homepage_content(self) -> str:
        """Generate homepage content requirements"""
        lines = [
            "## Homepage Content",
            "",
            "### Hero Section",
            "",
            f"**Headline Formula:** [Value Prop] + [Location/Differentiator]",
            "",
        ]

        # Generate example headlines
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "**Example Headlines:**",
                f"- \"{self.client.name}: Where Every Choice Changes the Story\"",
                f"- \"Bethlehem's Most Immersive Escape Room Experience\"",
                f"- \"Not Just Puzzles. An Interactive Movie You Control.\"",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            service = self.client.money_services[0].name if self.client.money_services else "Service"
            lines.extend([
                "**Example Headlines:**",
                f"- \"Expert {service} in the Lehigh Valley\"",
                f"- \"5-Star Rated {service} • Same-Day Service\"",
                f"- \"Your Local {service} Specialists Since [Year]\"",
                "",
            ])

        lines.extend([
            "**Subheadline:** Support headline with key differentiator or social proof",
            "",
            "**CTA Text:**",
        ])

        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.append("- Primary: \"Book Your Adventure\"")
            lines.append("- Secondary: \"Check Availability\"")
        else:
            lines.append("- Primary: \"Get Free Quote\"")
            lines.append("- Secondary: \"Call Now: [Phone]\"")

        lines.extend([
            "",
            "### Services Section",
            "",
            "**Section Headline:** \"Our [Services/Experiences]\" or \"What We Offer\"",
            "",
            "**For Each Service:**",
            "- Service name (H3)",
            "- 2-3 sentence description",
            "- Key benefit bullet points",
            "- Learn more link",
            "",
            "### Trust Section",
            "",
            "**Include:**",
        ])

        if self.client.gbp_profile:
            lines.append(f"- Google rating: {self.client.gbp_profile.rating} ({self.client.gbp_profile.review_count} reviews)")

        lines.extend([
            "- Key differentiators",
            "- Trust badges/certifications",
            "- Brief testimonial quote",
            "",
            "### CTA Section",
            "",
            "**Headline:** Action-oriented with urgency",
            "**Body:** 2-3 sentences reinforcing value prop",
            "**Form/Button:** Clear next step",
            "",
        ])

        return "\n".join(lines)

    def _service_page_content(self) -> str:
        """Generate service page content requirements"""
        lines = [
            "## Service Page Content",
            "",
            "### Content for Each Service",
            "",
        ]

        for service in self.client.services:
            if service.is_money_service:
                lines.extend([
                    f"### {service.name}",
                    "",
                    f"**URL:** `/services/{service.slug}`",
                    "",
                    "#### Hero Section",
                    f"- Headline: \"{service.name}\" + location/benefit",
                    f"- Subheadline: {service.short_description or 'Key value proposition'}",
                    "",
                    "#### Overview Section (200-300 words)",
                    "",
                ])

                if service.description:
                    lines.append(f"**Starting Point:**")
                    lines.append(f"> {service.description[:200]}...")
                    lines.append("")

                lines.append("**Must Include:**")
                lines.append("- What the service is (definition)")
                lines.append("- Who it's for (audience)")
                lines.append("- Why choose this provider (differentiator)")
                lines.append("")

                if service.defined_variables:
                    dv = service.defined_variables
                    lines.append("#### Key Information")
                    lines.append("")
                    if dv.time_range:
                        lines.append(f"- **Duration:** {dv.time_range}")
                    if dv.cost_range:
                        lines.append(f"- **Price Range:** {dv.cost_range}")
                    if dv.process_steps:
                        lines.append("- **Process:**")
                        for i, step in enumerate(dv.process_steps, 1):
                            lines.append(f"  {i}. {step}")
                    if dv.best_for:
                        lines.append("- **Best For:**")
                        for item in dv.best_for:
                            lines.append(f"  - {item}")
                    lines.append("")

                if service.faq_topics:
                    lines.append("#### FAQ Topics to Address")
                    for topic in service.faq_topics:
                        lines.append(f"- {topic}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _service_area_content(self) -> str:
        """Generate service-area page content requirements"""
        lines = [
            "## Service-Area Page Content",
            "",
            "### Template Structure",
            "",
            "**URL Pattern:** `/services/[service]/[location]`",
            "",
            "#### Required Sections",
            "",
            "1. **Hero**",
            "   - Headline: \"[Service] in [City], [State]\"",
            "   - Subheadline: Local relevance statement",
            "",
            "2. **Local Introduction (150-200 words)**",
            "   - Mention city name 2-3 times naturally",
            "   - Reference local landmarks or areas",
            "   - Establish service area coverage",
            "",
            "3. **Service Overview**",
            "   - Brief service description (can reuse from main page)",
            "   - Local-specific considerations",
            "",
            "4. **Why Choose Us for [City]**",
            "   - Proximity/response time",
            "   - Local experience/testimonials",
            "   - Community involvement",
            "",
            "5. **Service Area Map**",
            "   - Embedded map showing coverage",
            "   - List of nearby areas served",
            "",
            "6. **Local CTA**",
            "   - \"Get [Service] in [City] Today\"",
            "   - Phone number",
            "   - Contact form",
            "",
            "### Location-Specific Content Variations",
            "",
        ]

        for location in self.client.locations[:5]:
            lines.append(f"**{location.name}:**")
            lines.append(f"- Geo Bucket: {location.geo_bucket.value} miles")
            if location.travel_time_minutes:
                lines.append(f"- Travel Time: ~{location.travel_time_minutes} min from primary")
            if location.location_cluster:
                lines.append(f"- Region: {location.location_cluster}")
            lines.append("")

        if len(self.client.locations) > 5:
            lines.append(f"*...and {len(self.client.locations) - 5} more locations*")
            lines.append("")

        return "\n".join(lines)

    def _llm_answer_blocks(self) -> str:
        """Generate LLM answer blocks section"""
        lines = [
            "## LLM Answer Blocks",
            "",
            "These blocks provide entity-clear, quotable content for LLM SEO.",
            "",
        ]

        # Generate for each service
        if self.output_spec and self.output_spec.llm_answer_blocks:
            for block in self.output_spec.llm_answer_blocks:
                lines.extend(self._format_answer_block(block))
        else:
            # Generate templates from services
            for service in self.client.money_services[:3]:
                lines.extend(self._generate_answer_block_template(service))

        return "\n".join(lines)

    def _format_answer_block(self, block: LLMAnswerBlock) -> List[str]:
        """Format a single LLM answer block"""
        lines = [
            f"### {block.service}",
            "",
            "#### Definition",
            f"> {block.definition}",
            "",
        ]

        if block.triggers:
            lines.append("#### When You Need It")
            for trigger in block.triggers:
                lines.append(f"- {trigger}")
            lines.append("")

        if block.cost_range:
            lines.append("#### Cost Range")
            lines.append(f"**Range:** {block.cost_range.range}")
            if block.cost_range.variables:
                lines.append("**Factors affecting price:**")
                for var in block.cost_range.variables:
                    lines.append(f"- {var}")
            lines.append("")

        if block.timeline:
            lines.append(f"#### Timeline")
            lines.append(f"{block.timeline}")
            lines.append("")

        if block.process_steps:
            lines.append("#### Process")
            for i, step in enumerate(block.process_steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")

        if block.faqs:
            lines.append("#### FAQs")
            for faq in block.faqs[:3]:
                lines.append(f"**Q: {faq.question}**")
                lines.append(f"A: {faq.answer}")
                lines.append("")

        lines.append("---")
        lines.append("")

        return lines

    def _generate_answer_block_template(self, service: Service) -> List[str]:
        """Generate template answer block for a service"""
        lines = [
            f"### {service.name}",
            "",
            "#### Definition (2 sentences)",
            f"> [Define what {service.name} is and what problem it solves]",
            "",
            "#### When You Need It",
            "- [Trigger situation 1]",
            "- [Trigger situation 2]",
            "- [Trigger situation 3]",
            "",
        ]

        if service.defined_variables:
            dv = service.defined_variables
            if dv.cost_range:
                lines.extend([
                    "#### Cost Range",
                    f"**Range:** {dv.cost_range}",
                    "**Factors:** [List 2-3 variables]",
                    "",
                ])
            if dv.time_range:
                lines.extend([
                    "#### Timeline",
                    f"{dv.time_range}",
                    "",
                ])
            if dv.process_steps:
                lines.append("#### Process")
                for i, step in enumerate(dv.process_steps, 1):
                    lines.append(f"{i}. {step}")
                lines.append("")

        lines.extend([
            "#### NAP Statement",
            f"> {self.client.name} provides {service.name.lower()} services",
        ])

        if self.client.primary_location:
            lines.append(f"> in {self.client.primary_location.name} and surrounding areas.")
        else:
            lines.append("> in our service area.")

        if self.client.contact and self.client.contact.phone:
            lines.append(f"> Call {self.client.contact.phone} for service.")

        lines.extend(["", "---", ""])

        return lines

    def _faq_content(self) -> str:
        """Generate FAQ content requirements"""
        lines = [
            "## FAQ Content",
            "",
            "### FAQ Page Structure",
            "",
            "Organize FAQs by category:",
            "",
        ]

        # Generate category suggestions based on vertical
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "1. **Booking & Availability**",
                "   - How do I book?",
                "   - How far in advance should I book?",
                "   - Can I reschedule?",
                "",
                "2. **The Experience**",
                "   - How long does it take?",
                "   - What's the difficulty level?",
                "   - Is it scary?",
                "",
                "3. **Groups & Events**",
                "   - What's the maximum group size?",
                "   - Do you offer party packages?",
                "   - Corporate team building options?",
                "",
                "4. **Practical Info**",
                "   - Where are you located?",
                "   - Is there parking?",
                "   - Age requirements?",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "1. **Services**",
                "   - What services do you offer?",
                "   - Do you offer emergency service?",
                "   - What areas do you serve?",
                "",
                "2. **Pricing**",
                "   - How much does [service] cost?",
                "   - Do you offer free estimates?",
                "   - Do you offer financing?",
                "",
                "3. **Process**",
                "   - How long does [service] take?",
                "   - What should I expect?",
                "   - Do you guarantee your work?",
                "",
                "4. **Credentials**",
                "   - Are you licensed and insured?",
                "   - What certifications do you have?",
                "   - How long have you been in business?",
                "",
            ])

        lines.extend([
            "### FAQ Writing Guidelines",
            "",
            "- Answer in the first sentence",
            "- Keep answers 2-4 sentences",
            "- Include specific numbers when possible",
            "- Link to relevant pages where appropriate",
            "",
        ])

        return "\n".join(lines)

    def _about_content(self) -> str:
        """Generate about page content requirements"""
        return f"""## About Page Content

### Story Section
- Business origin story
- Mission statement
- Years of experience
- Team introduction

### Trust Signals
- Certifications and licenses
- Industry associations
- Awards and recognition
- Insurance information

### Community Section
- Local involvement
- Service area commitment
- Customer testimonials

### Team Section (if applicable)
- Owner/founder bio
- Key team member profiles
- Professional photos

### Contact Information
- Full NAP details
- Business hours
- Service area description"""

    def _metadata_guidelines(self) -> str:
        """Generate metadata guidelines"""
        lines = [
            "## Metadata Guidelines",
            "",
            "### Title Tag Formula",
            "",
            "**Homepage:** `{self.client.name} | [Primary Service] in [City], [State]`",
            "**Service:** `[Service Name] | {self.client.name} [City]`",
            "**Service-Area:** `[Service] in [City], [State] | {self.client.name}`",
            "",
            "### Meta Description Formula",
            "",
            "**Format:** [Value prop] + [Key differentiator] + [CTA]. 150-160 characters.",
            "",
            "**Homepage Example:**",
        ]

        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.append(f"> {self.client.name} offers immersive escape room experiences with AI-powered storytelling. Book your adventure today!")
        else:
            service = self.client.money_services[0].name if self.client.money_services else "services"
            lines.append(f"> {self.client.name} provides expert {service.lower()} in the Lehigh Valley. Licensed, insured, 5-star rated. Get your free quote!")

        lines.extend([
            "",
            "### Open Graph",
            "",
            "- Include OG image for every page (1200x630)",
            "- Match OG title to page title",
            "- Match OG description to meta description",
            "",
            "---",
            "",
            "*End of Content Brief*",
        ])

        return "\n".join(lines)

    def _keyword_targeting(self) -> Optional[str]:
        """Generate keyword targeting section from research"""
        if not self.research:
            return None

        seo_opps = self.research.get_seo_opportunities()
        if not seo_opps:
            return None

        lines = [
            "## Keyword Targeting Strategy",
            "",
            "### Primary Keywords (Content Priority)",
            "",
        ]

        primary = [k for k in seo_opps if k.get('tier') == 'primary']
        if primary:
            lines.extend([
                "| Keyword | Current Rank | Content Action |",
                "|---------|--------------|----------------|",
            ])
            for kw in primary[:6]:
                rank = f"#{kw['current_rank']}" if kw.get('current_rank') else "Not ranking"
                action = "Optimize existing" if kw.get('current_rank') else "Create new page"
                lines.append(f"| {kw['keyword']} | {rank} | {action} |")
            lines.append("")

        # Secondary/opportunity keywords
        secondary = [k for k in seo_opps if k.get('tier') != 'primary' or not k.get('current_rank')]
        if secondary:
            lines.extend([
                "### Keyword Opportunities (New Content)",
                "",
            ])
            for kw in secondary[:8]:
                lines.append(f"- **{kw['keyword']}**: {kw.get('opportunity', 'Create targeted content')}")
            lines.append("")

        return "\n".join(lines)

    def _content_gaps(self) -> Optional[str]:
        """Generate content gaps section from research"""
        if not self.research:
            return None

        # Get findings about content gaps
        findings = self.research.build_findings()
        content_gaps = [f for f in findings.findings
                       if 'content' in f.observation.lower()
                       or 'page' in f.observation.lower()
                       or 'blog' in f.observation.lower()]

        if not content_gaps:
            return None

        lines = [
            "## Content Gaps Identified",
            "",
            "### Pages to Create",
            "",
        ]

        for gap in content_gaps[:8]:
            lines.append(f"- **{gap.observation}**")
            if gap.details:
                lines.append(f"  - {gap.details[:100]}...")

        lines.extend([
            "",
            "### Recommended New Pages",
            "",
            "Based on research analysis:",
            "",
            "1. Individual experience/room pages (dedicated content)",
            "2. Location landing pages (Allentown, Easton, Poconos, Philadelphia)",
            "3. Corporate team building page",
            "4. Birthday/party packages page",
            "5. Blog with long-tail keyword targeting",
            "",
        ])

        return "\n".join(lines)
