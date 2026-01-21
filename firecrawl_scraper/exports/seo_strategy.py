"""
SEO Strategy Generator - For SEO execution

Generates comprehensive SEO strategy including keyword targeting,
schema implementation, and technical requirements.
"""

from datetime import datetime
from typing import Optional, List

from ..models import (
    Client,
    IntentGeoMatrix,
    InsightReport,
    OutputSpec,
    Vertical,
    ENTERTAINMENT_VERTICALS,
    BLUE_COLLAR_VERTICALS,
    HEALTHCARE_VERTICALS,
)


class SEOStrategyGenerator:
    """Generate SEO strategy markdown"""

    def __init__(
        self,
        client: Client,
        matrix: Optional[IntentGeoMatrix] = None,
        insights: Optional[InsightReport] = None,
        output_spec: Optional[OutputSpec] = None
    ):
        self.client = client
        self.matrix = matrix
        self.insights = insights
        self.output_spec = output_spec

    def generate(self) -> str:
        """Generate complete SEO strategy markdown"""
        sections = [
            self._header(),
            self._strategy_overview(),
            self._keyword_strategy(),
            self._local_seo_strategy(),
            self._schema_strategy(),
            self._content_strategy(),
            self._backlink_strategy(),
            self._technical_seo(),
            self._measurement_plan(),
            self._execution_timeline(),
        ]

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate header section"""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        return f"""# SEO Strategy: {self.client.name}

**Document Type:** SEO Execution Plan
**Generated:** {timestamp}
**Vertical:** {self.client.vertical.value.replace('_', ' ').title()}

---

> **Purpose:** Comprehensive SEO strategy for organic growth.
> SEO agents should execute this plan systematically.

---"""

    def _strategy_overview(self) -> str:
        """Generate strategy overview"""
        lines = [
            "## Strategy Overview",
            "",
            "### Primary Objectives",
            "",
        ]

        # Vertical-specific objectives
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "1. **Local Pack Dominance** - Top 3 for \"escape room [city]\" queries",
                "2. **Geographic Expansion** - Visibility in 60+ mile radius",
                "3. **Experience Keywords** - Rank for unique differentiators",
                "4. **Conversion Optimization** - Booking-focused landing pages",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "1. **Local Pack Dominance** - Top 3 in all target service areas",
                "2. **Service Keywords** - Rank for all money services",
                "3. **Emergency Queries** - Capture urgent search intent",
                "4. **Trust Building** - Reviews and authority signals",
                "",
            ])
        else:
            lines.extend([
                "1. **Local Pack Visibility** - Consistent top 3 presence",
                "2. **Service Keywords** - Rank for all offered services",
                "3. **Provider Keywords** - Individual provider visibility",
                "4. **Conversion** - Appointment-focused pages",
                "",
            ])

        lines.extend([
            "### Strategic Pillars",
            "",
            "| Pillar | Focus | Timeline |",
            "|--------|-------|----------|",
            "| Technical Foundation | Site speed, schema, crawlability | Month 1 |",
            "| Content Expansion | Service & location pages | Months 1-3 |",
            "| Local SEO | GBP optimization, citations | Ongoing |",
            "| Authority Building | Backlinks, mentions | Months 2-6 |",
            "",
        ])

        return "\n".join(lines)

    def _keyword_strategy(self) -> str:
        """Generate keyword strategy section"""
        lines = [
            "## Keyword Strategy",
            "",
            "### Keyword Categories",
            "",
        ]

        # Generate keyword categories by service
        lines.append("#### Money Keywords (High Intent)")
        lines.append("")

        for service in self.client.money_services[:4]:
            lines.append(f"**{service.name}:**")
            if service.keywords:
                for kw in service.keywords[:5]:
                    lines.append(f"- {kw}")
            else:
                lines.append(f"- {service.name.lower()}")
                lines.append(f"- {service.name.lower()} near me")
                lines.append(f"- {service.name.lower()} {self.client.primary_location.name if self.client.primary_location else 'local'}")
            lines.append("")

        # Location keywords
        lines.extend([
            "#### Location Keywords",
            "",
        ])

        for location in self.client.locations[:5]:
            city = location.name.split(',')[0] if ',' in location.name else location.name
            lines.append(f"**{location.name}:** (Bucket: {location.geo_bucket.value})")

            service_name = self.client.money_services[0].name.lower() if self.client.money_services else "service"
            lines.append(f"- {service_name} {city.lower()}")
            lines.append(f"- {service_name} near {city.lower()}")
            lines.append(f"- best {service_name} in {city.lower()}")
            lines.append("")

        # Intent/Geo Matrix Summary
        if self.matrix:
            lines.extend([
                "### Intent/Geo Matrix Summary",
                "",
                f"**Total Combinations:** {len(self.matrix.cells)}",
                "",
                "| Geo Bucket | Pages | Priority |",
                "|------------|-------|----------|",
            ])

            # Count by geo bucket
            buckets = {}
            for cell in self.matrix.cells:
                bucket = cell.geo_bucket
                if bucket not in buckets:
                    buckets[bucket] = 0
                buckets[bucket] += 1

            for bucket, count in sorted(buckets.items()):
                priority = "High" if bucket in ["0-10", "10-30"] else "Medium" if bucket == "30-60" else "Low"
                lines.append(f"| {bucket} mi | {count} | {priority} |")

            lines.append("")

        return "\n".join(lines)

    def _local_seo_strategy(self) -> str:
        """Generate local SEO strategy section"""
        lines = [
            "## Local SEO Strategy",
            "",
            "### Google Business Profile Optimization",
            "",
            "#### Current State",
            "",
        ]

        if self.client.gbp_profile:
            gbp = self.client.gbp_profile
            lines.append(f"- **Rating:** {gbp.rating or 'N/A'}")
            lines.append(f"- **Reviews:** {gbp.review_count or 'N/A'}")
            if gbp.categories:
                lines.append(f"- **Categories:** {', '.join(gbp.categories[:3])}")
        else:
            lines.append("*GBP data not collected*")

        lines.append("")

        lines.extend([
            "#### GBP Optimization Checklist",
            "",
            "- [ ] Complete all business information fields",
            "- [ ] Add all services with descriptions",
            "- [ ] Upload 10+ high-quality photos monthly",
            "- [ ] Add Q&A with keyword-rich questions",
            "- [ ] Enable messaging",
            "- [ ] Post weekly updates",
            "- [ ] Respond to all reviews within 24 hours",
            "",
            "### Local Citation Strategy",
            "",
            "#### Priority Citations (Build First)",
            "",
            "1. Google Business Profile",
            "2. Yelp",
            "3. Facebook Business",
            "4. Apple Maps",
            "5. Bing Places",
            "",
            "#### Industry Citations",
            "",
        ])

        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "- TripAdvisor",
                "- Yelp Activities",
                "- Groupon (if applicable)",
                "- Local event listings",
                "- Tourism board listings",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "- Angi (formerly Angie's List)",
                "- HomeAdvisor",
                "- Thumbtack",
                "- BBB",
                "- Industry associations",
                "",
            ])
        elif self.client.vertical in HEALTHCARE_VERTICALS:
            lines.extend([
                "- Healthgrades",
                "- Zocdoc",
                "- Vitals",
                "- WebMD",
                "- Specialty directories",
                "",
            ])

        lines.extend([
            "### Review Strategy",
            "",
            "**Target:** +10-20 reviews per month",
            "",
            "**Tactics:**",
            "- Post-service review request (email/SMS)",
            "- QR code in-location",
            "- Review link on receipts",
            "- Respond to all reviews",
            "",
            "**Review Response Templates:**",
            "",
            "**Positive Review:**",
            "> Thank you [Name]! We're thrilled you enjoyed [specific mention from review].",
            "> We appreciate you choosing {self.client.name} and look forward to seeing you again!",
            "",
            "**Negative Review:**",
            "> [Name], we're sorry to hear about your experience. Your feedback matters to us.",
            "> Please reach out to [contact] so we can make this right.",
            "",
        ])

        return "\n".join(lines)

    def _schema_strategy(self) -> str:
        """Generate schema strategy section"""
        lines = [
            "## Schema Markup Strategy",
            "",
            "### Schema by Page Type",
            "",
        ]

        # Schema recommendations by page type
        schema_recs = [
            ("Homepage", ["Organization", "LocalBusiness", "WebSite"]),
            ("Service Pages", ["Service", "FAQPage", "BreadcrumbList"]),
            ("Service-Area Pages", ["LocalBusiness", "Service", "GeoCircle", "BreadcrumbList"]),
            ("About Page", ["Organization", "Person", "BreadcrumbList"]),
            ("Contact Page", ["LocalBusiness", "ContactPage"]),
            ("FAQ Page", ["FAQPage", "BreadcrumbList"]),
        ]

        # Add vertical-specific
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            schema_recs.insert(1, ("Experience Pages", ["TouristAttraction", "Event", "Offer", "FAQPage"]))

        for page_type, schemas in schema_recs:
            lines.append(f"**{page_type}:**")
            for schema in schemas:
                lines.append(f"- `{schema}`")
            lines.append("")

        lines.extend([
            "### LocalBusiness Schema Template",
            "",
            "```json",
            "{",
            '  "@context": "https://schema.org",',
            '  "@type": "LocalBusiness",',
            f'  "name": "{self.client.name}",',
        ])

        if self.client.domain:
            lines.append(f'  "url": "https://{self.client.domain}",')

        if self.client.contact:
            if self.client.contact.phone:
                lines.append(f'  "telephone": "{self.client.contact.phone}",')
            if self.client.contact.address:
                lines.append(f'  "address": {{ "@type": "PostalAddress", "streetAddress": "{self.client.contact.address}" }},')

        if self.client.gbp_profile:
            if self.client.gbp_profile.rating:
                lines.extend([
                    '  "aggregateRating": {',
                    '    "@type": "AggregateRating",',
                    f'    "ratingValue": "{self.client.gbp_profile.rating}",',
                    f'    "reviewCount": "{self.client.gbp_profile.review_count}"',
                    '  }',
                ])

        lines.extend([
            "}",
            "```",
            "",
            "### Schema Validation",
            "",
            "- [ ] Test all schema with Google Rich Results Test",
            "- [ ] Validate JSON-LD syntax",
            "- [ ] Monitor in Search Console",
            "",
        ])

        return "\n".join(lines)

    def _content_strategy(self) -> str:
        """Generate content strategy section"""
        lines = [
            "## Content Strategy",
            "",
            "### Content Pillars",
            "",
        ]

        if self.matrix:
            lines.append(f"**Total Pages to Create:** {len(self.matrix.cells)}")
            lines.append("")

        lines.extend([
            "#### Pillar 1: Service Pages",
            "One comprehensive page per service with:",
            "- 1500+ words",
            "- FAQ section (5+ questions)",
            "- Process/steps section",
            "- Pricing guidance",
            "- Trust signals",
            "",
            "#### Pillar 2: Service-Area Pages",
            "Location-specific landing pages with:",
            "- 600-1000 words",
            "- Local mentions and landmarks",
            "- Service area map",
            "- Local testimonials",
            "",
            "#### Pillar 3: Supporting Content",
            "- FAQ page (15-25 questions)",
            "- About page",
            "- Gallery/portfolio page",
            "",
            "### Content Calendar",
            "",
            "| Week | Content Focus | Pages |",
            "|------|--------------|-------|",
            "| 1-2 | Homepage + Core Service Pages | 5-6 |",
            "| 3-4 | Primary Location Pages (0-10 mi) | 4-6 |",
            "| 5-6 | Secondary Location Pages (10-30 mi) | 4-8 |",
            "| 7-8 | Extended Location Pages (30-60 mi) | 4-6 |",
            "| 9-10 | Supporting Pages (FAQ, About, Contact) | 3-4 |",
            "| 11-12 | Content Optimization + Internal Linking | - |",
            "",
        ])

        return "\n".join(lines)

    def _backlink_strategy(self) -> str:
        """Generate backlink strategy section"""
        lines = [
            "## Backlink Strategy",
            "",
            "### Current Baseline",
            "",
            "*Backlink data from competitor analysis*",
            "",
            "### Target Metrics (6 Months)",
            "",
            "- **Total Backlinks:** 50+ (from baseline)",
            "- **Referring Domains:** 30+",
            "- **Domain Authority:** 15+ points increase",
            "",
            "### Link Building Tactics",
            "",
            "#### Tier 1: Foundation Links",
            "- Local business directories",
            "- Industry associations",
            "- Chamber of Commerce",
            "- BBB listing",
            "",
            "#### Tier 2: Content-Driven Links",
            "- Guest posts on local blogs",
            "- Expert quotes for journalists (HARO)",
            "- Resource page link building",
            "- Broken link building",
            "",
            "#### Tier 3: Relationship Links",
            "- Partner/vendor mentions",
            "- Supplier directories",
            "- Sponsorship opportunities",
            "- Local event participation",
            "",
            "### Link Targets by Category",
            "",
        ]

        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "| Category | Target Sites | Est. Links |",
                "|----------|--------------|------------|",
                "| Tourism | Visit PA, local tourism boards | 3-5 |",
                "| Events | Local event calendars, Eventbrite | 5-10 |",
                "| Media | Local news, lifestyle blogs | 3-5 |",
                "| Business | Chamber, local business orgs | 2-3 |",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "| Category | Target Sites | Est. Links |",
                "|----------|--------------|------------|",
                "| Directories | Angi, HomeAdvisor, Thumbtack | 5-10 |",
                "| Industry | Trade associations, manufacturer sites | 3-5 |",
                "| Local | Chamber, local business directories | 3-5 |",
                "| Media | Local news (weather damage stories) | 2-3 |",
                "",
            ])

        return "\n".join(lines)

    def _technical_seo(self) -> str:
        """Generate technical SEO section"""
        return """## Technical SEO

### Core Web Vitals Targets
| Metric | Target | Tool |
|--------|--------|------|
| LCP | < 2.5s | PageSpeed Insights |
| FID | < 100ms | PageSpeed Insights |
| CLS | < 0.1 | PageSpeed Insights |
| Mobile Score | > 90 | PageSpeed Insights |

### Technical Checklist

#### Crawlability
- [ ] XML sitemap generated and submitted
- [ ] Robots.txt properly configured
- [ ] No orphan pages
- [ ] Internal linking structure optimized

#### Indexability
- [ ] Canonical tags on all pages
- [ ] No duplicate content issues
- [ ] Proper use of noindex where needed
- [ ] Hreflang (if multilingual)

#### Performance
- [ ] Images optimized (WebP, lazy loading)
- [ ] CSS/JS minified
- [ ] Caching enabled
- [ ] CDN configured

#### Mobile
- [ ] Mobile-responsive design
- [ ] Touch targets sized appropriately
- [ ] No horizontal scroll
- [ ] Text readable without zoom

#### Security
- [ ] HTTPS enabled
- [ ] Mixed content resolved
- [ ] Security headers configured"""

    def _measurement_plan(self) -> str:
        """Generate measurement plan section"""
        return """## Measurement Plan

### Key Performance Indicators

| KPI | Baseline | 30 Day | 90 Day | 6 Month |
|-----|----------|--------|--------|---------|
| Organic Traffic | TBD | +10% | +30% | +100% |
| Keyword Rankings (Top 10) | TBD | +5 | +15 | +30 |
| Local Pack Rankings | TBD | Top 5 | Top 3 | Top 3 |
| GBP Actions | TBD | +20% | +50% | +100% |
| Conversions | TBD | +10% | +25% | +50% |

### Tracking Setup

#### Google Analytics 4
- [ ] Property created
- [ ] Conversions configured (calls, forms, bookings)
- [ ] Events tracking key actions
- [ ] eCommerce (if applicable)

#### Google Search Console
- [ ] Property verified
- [ ] Sitemap submitted
- [ ] Performance monitored weekly

#### Rank Tracking
- [ ] Track top 50 keywords
- [ ] Local pack positions
- [ ] Competitor tracking

### Reporting Schedule
- **Weekly:** Rankings check, GSC crawl errors
- **Monthly:** Full performance report
- **Quarterly:** Strategy review and adjustment"""

    def _execution_timeline(self) -> str:
        """Generate execution timeline"""
        return f"""## Execution Timeline

### Month 1: Foundation
- [ ] Technical SEO audit and fixes
- [ ] Core page content creation (Homepage, Services)
- [ ] Schema markup implementation
- [ ] GBP optimization
- [ ] Analytics/tracking setup

### Month 2: Expansion
- [ ] Service-area page rollout (primary locations)
- [ ] Local citation building
- [ ] Review acquisition program launch
- [ ] Internal linking optimization

### Month 3: Authority
- [ ] Service-area page completion
- [ ] Backlink outreach begins
- [ ] Content optimization based on data
- [ ] FAQ page expansion

### Months 4-6: Scale
- [ ] Continued link building
- [ ] Content gap analysis and filling
- [ ] Conversion optimization
- [ ] Strategy refinement based on results

---

*End of SEO Strategy*"""
