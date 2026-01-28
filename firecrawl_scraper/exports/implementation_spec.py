"""
Implementation Spec Generator - Technical build instructions

Generates detailed technical specifications for builder agents
and development teams.

Enhanced with research integration for conversion optimization insights.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from ..models import (
    Client,
    OutputSpec,
    IntentGeoMatrix,
    InsightReport,
    PageSpec,
    PageType,
    Vertical,
    ENTERTAINMENT_VERTICALS,
    BLUE_COLLAR_VERTICALS,
    HEALTHCARE_VERTICALS,
)

if TYPE_CHECKING:
    from ..integrations.research_integration import ResearchIntegration


class ImplementationSpecGenerator:
    """Generate implementation specification markdown"""

    def __init__(
        self,
        client: Client,
        output_spec: Optional[OutputSpec] = None,
        matrix: Optional[IntentGeoMatrix] = None,
        insights: Optional[InsightReport] = None,
        research_integration: Optional['ResearchIntegration'] = None,
    ):
        self.client = client
        self.output_spec = output_spec
        self.matrix = matrix
        self.insights = insights
        self.research = research_integration

    def generate(self) -> str:
        """Generate complete implementation spec markdown"""
        sections = [
            self._header(),
            self._tech_stack(),
            self._site_architecture(),
            self._page_map(),
        ]

        # Add research-based insights
        if self.research:
            priorities = self._implementation_priorities()
            if priorities:
                sections.append(priorities)

        sections.extend([
            self._component_specs(),
            self._schema_requirements(),
            self._internal_linking(),
            self._conversion_elements(),
        ])

        # Add trust signals requirements from research
        if self.research:
            trust = self._trust_signal_requirements()
            if trust:
                sections.append(trust)

        sections.extend([
            self._mobile_requirements(),
            self._deployment_checklist(),
        ])

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate header section"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        total_pages = len(self.output_spec.page_map) if self.output_spec else 0

        return f"""# Implementation Spec: {self.client.name}

**Document Type:** Technical Build Specification
**Generated:** {timestamp}
**Total Pages:** {total_pages}
**Target Framework:** Next.js / React

---

> **Purpose:** Detailed technical specifications for building the site.
> Builder agents should follow these specs exactly.

---"""

    def _tech_stack(self) -> str:
        """Generate tech stack section"""
        return """## Recommended Tech Stack

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Forms:** React Hook Form + Zod

### Performance
- **Images:** Next/Image with optimization
- **Fonts:** next/font with variable fonts
- **Analytics:** Google Analytics 4

### SEO
- **Metadata:** Next.js Metadata API
- **Sitemap:** next-sitemap
- **Schema:** JSON-LD via script tags

### Deployment
- **Platform:** Vercel (recommended)
- **CDN:** Automatic via Vercel
- **Preview:** Branch deployments enabled"""

    def _site_architecture(self) -> str:
        """Generate site architecture section"""
        lines = [
            "## Site Architecture",
            "",
            "### Directory Structure",
            "",
            "```",
            "app/",
            "├── page.tsx                    # Homepage",
            "├── layout.tsx                  # Root layout",
            "├── globals.css                 # Global styles",
            "│",
            "├── services/",
            "│   ├── page.tsx               # Services overview",
            "│   └── [service]/",
            "│       ├── page.tsx           # Service detail",
            "│       └── [location]/",
            "│           └── page.tsx       # Service-area page",
            "│",
            "├── about/",
            "│   └── page.tsx               # About page",
            "│",
            "├── contact/",
            "│   └── page.tsx               # Contact page",
            "│",
        ]

        # Vertical-specific pages
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "├── book/",
                "│   └── page.tsx               # Booking page",
                "│",
                "├── parties/",
                "│   └── page.tsx               # Party packages",
                "│",
                "├── corporate/",
                "│   └── page.tsx               # Corporate booking",
                "│",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "├── gallery/",
                "│   └── page.tsx               # Before/after gallery",
                "│",
                "├── service-areas/",
                "│   └── page.tsx               # Service areas overview",
                "│",
            ])
        elif self.client.vertical in HEALTHCARE_VERTICALS:
            lines.extend([
                "├── providers/",
                "│   └── page.tsx               # Provider profiles",
                "│",
                "├── schedule/",
                "│   └── page.tsx               # Online scheduling",
                "│",
            ])

        lines.extend([
            "└── faq/",
            "    └── page.tsx               # FAQ page",
            "",
            "components/",
            "├── ui/                          # shadcn components",
            "├── layout/                      # Layout components",
            "│   ├── Header.tsx",
            "│   ├── Footer.tsx",
            "│   └── StickyBar.tsx",
            "├── sections/                    # Page sections",
            "│   ├── Hero.tsx",
            "│   ├── Services.tsx",
            "│   ├── Testimonials.tsx",
            "│   └── CTA.tsx",
            "└── seo/                         # SEO components",
            "    ├── JsonLd.tsx",
            "    └── Breadcrumbs.tsx",
            "```",
            "",
        ])

        return "\n".join(lines)

    def _page_map(self) -> str:
        """Generate page map section"""
        lines = [
            "## Page Map",
            "",
            "### All Pages to Build",
            "",
            "| Route | Page Type | Priority | Template |",
            "|-------|-----------|----------|----------|",
        ]

        if self.output_spec and self.output_spec.page_map:
            # Sort by priority
            sorted_pages = sorted(
                self.output_spec.page_map,
                key=lambda p: p.priority or 99
            )

            for page in sorted_pages:
                priority = f"P{page.priority}" if page.priority else "P9"
                template = page.template or page.page_type.value
                lines.append(f"| `{page.route}` | {page.page_type.value} | {priority} | {template} |")
        else:
            lines.append("| *Page map will be generated from pipeline* | | | |")

        lines.append("")

        # Group pages by type
        if self.output_spec and self.output_spec.page_map:
            lines.extend([
                "### Pages by Type",
                "",
            ])

            page_types = {}
            for page in self.output_spec.page_map:
                pt = page.page_type.value
                if pt not in page_types:
                    page_types[pt] = []
                page_types[pt].append(page)

            for pt, pages in sorted(page_types.items()):
                lines.append(f"**{pt}:** {len(pages)} pages")

            lines.append("")

        return "\n".join(lines)

    def _component_specs(self) -> str:
        """Generate component specifications"""
        lines = [
            "## Component Specifications",
            "",
        ]

        # Universal components
        lines.extend([
            "### Core Components (All Pages)",
            "",
            "#### Header",
            "```typescript",
            "interface HeaderProps {",
            "  logo: string;",
            "  navigation: NavItem[];",
            "  phone: string;",
            "  ctaText: string;",
            "  ctaLink: string;",
            "  sticky?: boolean;",
            "}",
            "```",
            "- Logo left, navigation center, CTA right",
            "- Sticky on scroll (after 100px)",
            "- Mobile hamburger menu",
            "- Click-to-call phone number",
            "",
            "#### Footer",
            "- Business info with NAP",
            "- Service links",
            "- Location links",
            "- Social links",
            "- Copyright with schema",
            "",
            "#### StickyBar (Mobile)",
            "- Fixed bottom bar on mobile",
            "- Click-to-call button",
            "- Book/Contact CTA",
            "- Only shows on scroll",
            "",
        ])

        # Vertical-specific components
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "### Entertainment Components",
                "",
                "#### BookingWidget",
                "```typescript",
                "interface BookingWidgetProps {",
                "  experiences: Experience[];",
                "  provider?: 'fareharbor' | 'bookeo' | 'custom';",
                "  showPricing: boolean;",
                "  showAvailability: boolean;",
                "}",
                "```",
                "- Real-time availability calendar",
                "- Group size selector",
                "- Date/time picker",
                "- Embedded or modal",
                "",
                "#### ExperienceCard",
                "- Large hero image",
                "- Experience name",
                "- Difficulty indicator",
                "- Duration",
                "- Price per person",
                "- Book CTA",
                "",
                "#### ExperienceGallery",
                "- Atmospheric photos (no spoilers)",
                "- Lightbox view",
                "- Optional video embed",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "### Service Trade Components",
                "",
                "#### BeforeAfterGallery",
                "```typescript",
                "interface BeforeAfterProps {",
                "  images: BeforeAfterPair[];",
                "  service?: string;",
                "  location?: string;",
                "}",
                "```",
                "- Slider comparison view",
                "- Filter by service type",
                "- Location tags",
                "- Lightbox for full view",
                "",
                "#### TrustBadges",
                "- License badge with number",
                "- Insurance badge",
                "- Certification logos",
                "- Years in business",
                "",
                "#### ServiceAreaMap",
                "- Google Maps embed",
                "- Service radius overlay",
                "- Clickable area pins",
                "",
            ])
        elif self.client.vertical in HEALTHCARE_VERTICALS:
            lines.extend([
                "### Healthcare Components",
                "",
                "#### ProviderCard",
                "- Professional photo",
                "- Name and credentials",
                "- Specialties",
                "- Schedule CTA",
                "",
                "#### SchedulingWidget",
                "- Service type selection",
                "- Provider selection",
                "- Available times",
                "- Patient info form",
                "",
            ])

        return "\n".join(lines)

    def _schema_requirements(self) -> str:
        """Generate schema requirements section"""
        lines = [
            "## Schema Requirements",
            "",
            "### Required Schema by Page Type",
            "",
        ]

        schema_map = {
            'home': ['Organization', 'LocalBusiness', 'WebSite'],
            'service': ['Service', 'FAQPage', 'BreadcrumbList'],
            'service-area': ['LocalBusiness', 'GeoCircle', 'Service', 'BreadcrumbList'],
            'about': ['Organization', 'Person', 'BreadcrumbList'],
            'contact': ['LocalBusiness', 'ContactPage', 'BreadcrumbList'],
            'faq': ['FAQPage', 'BreadcrumbList'],
        }

        # Add vertical-specific schema
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            schema_map['service'] = ['TouristAttraction', 'Event', 'FAQPage', 'BreadcrumbList']
            schema_map['booking'] = ['TouristAttraction', 'Offer']

        for page_type, schemas in schema_map.items():
            lines.append(f"**{page_type}:**")
            for schema in schemas:
                lines.append(f"- `{schema}`")
            lines.append("")

        lines.extend([
            "### Schema Implementation",
            "",
            "```tsx",
            "// components/seo/JsonLd.tsx",
            "export function JsonLd({ schema }: { schema: object }) {",
            "  return (",
            "    <script",
            "      type=\"application/ld+json\"",
            "      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}",
            "    />",
            "  );",
            "}",
            "```",
            "",
        ])

        return "\n".join(lines)

    def _internal_linking(self) -> str:
        """Generate internal linking section"""
        lines = [
            "## Internal Linking Rules",
            "",
            "### Link Architecture",
            "",
            "```",
            "Homepage",
            "    │",
            "    ├── Service Pages (link from services section)",
            "    │       │",
            "    │       └── Service-Area Pages (link from within service)",
            "    │",
            "    ├── About (footer, trust section)",
            "    │",
            "    └── Contact (header CTA, all CTAs)",
            "```",
            "",
            "### Linking Rules",
            "",
            "| From | To | Anchor Pattern | Placement |",
            "|------|------|----------------|-----------|",
            "| Homepage | Service | \"[Service Name]\" | Services section |",
            "| Service | Service-Area | \"[Service] in [City]\" | Near content |",
            "| Service-Area | Service | \"Learn more about [Service]\" | Content body |",
            "| All Pages | Contact | \"Get a Quote\" / \"Book Now\" | CTA areas |",
            "| Footer | All Services | Service names | Footer nav |",
            "| Footer | Key Locations | City names | Footer nav |",
            "",
            "### Contextual Links",
            "",
            "- Link services to related services within content",
            "- Cross-link nearby service areas",
            "- Link FAQ answers to relevant service pages",
            "",
        ]

        return "\n".join(lines)

    def _conversion_elements(self) -> str:
        """Generate conversion elements section"""
        lines = [
            "## Conversion Elements",
            "",
            "### Required on Every Page",
            "",
            "- [ ] Clickable phone number in header",
            "- [ ] Primary CTA button in header",
            "- [ ] Mobile sticky bar with call/book buttons",
            "- [ ] Contact form or booking widget",
            "",
            "### Page-Specific CTAs",
            "",
        ]

        # Vertical-specific CTAs
        if self.client.vertical in ENTERTAINMENT_VERTICALS:
            lines.extend([
                "| Page Type | Primary CTA | Secondary CTA |",
                "|-----------|-------------|---------------|",
                "| Homepage | \"Book Your Adventure\" | \"View Experiences\" |",
                "| Experience | \"Book Now\" | \"Check Availability\" |",
                "| Parties | \"Plan Your Party\" | \"Get Quote\" |",
                "| Corporate | \"Request Quote\" | \"Call Us\" |",
                "",
            ])
        elif self.client.vertical in BLUE_COLLAR_VERTICALS:
            lines.extend([
                "| Page Type | Primary CTA | Secondary CTA |",
                "|-----------|-------------|---------------|",
                "| Homepage | \"Get Free Quote\" | \"Call Now\" |",
                "| Service | \"Request Estimate\" | \"Call Now\" |",
                "| Service-Area | \"Get Quote in [City]\" | \"Call Now\" |",
                "| Gallery | \"Get Your Quote\" | \"See More Work\" |",
                "",
            ])
        else:
            lines.extend([
                "| Page Type | Primary CTA | Secondary CTA |",
                "|-----------|-------------|---------------|",
                "| Homepage | \"Schedule Appointment\" | \"Call Now\" |",
                "| Service | \"Book This Service\" | \"Learn More\" |",
                "| Provider | \"Book with [Name]\" | \"View All Providers\" |",
                "",
            ])

        lines.extend([
            "### Form Specifications",
            "",
            "**Contact Form (3-5 fields max):**",
            "- Name (required)",
            "- Phone (required)",
            "- Email (required)",
            "- Service interested in (dropdown)",
            "- Message (optional)",
            "",
            "**Success State:**",
            "- Clear confirmation message",
            "- Expected response time",
            "- Alternative contact options",
            "",
        ])

        return "\n".join(lines)

    def _mobile_requirements(self) -> str:
        """Generate mobile requirements section"""
        return """## Mobile Requirements

### Responsive Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### Mobile-Specific Features
- [ ] Sticky bottom bar with CTA
- [ ] Click-to-call all phone numbers
- [ ] Hamburger navigation
- [ ] Touch-friendly tap targets (min 44px)
- [ ] Optimized images (WebP, lazy loading)
- [ ] Fast load time (< 3s LCP)

### Performance Targets
- **LCP:** < 2.5s
- **FID:** < 100ms
- **CLS:** < 0.1
- **Mobile PageSpeed:** > 90"""

    def _implementation_priorities(self) -> Optional[str]:
        """Generate implementation priorities from research insights"""
        if not self.research:
            return None

        insights = self.research.build_insights()
        if not insights.insights:
            return None

        lines = [
            "## Implementation Priorities (Research-Based)",
            "",
            "### Quick Wins (Implement First)",
            "",
        ]

        # Quick wins (high impact, low effort)
        quick_wins = [i for i in insights.insights
                     if i.effort_estimate.value == 'low'
                     and i.expected_impact.cvr_impact.value in ['high', 'medium']]
        for win in quick_wins[:3]:
            lines.append(f"- [ ] **{win.problem[:50]}**")
            lines.append(f"      Action: {win.spec_change[:100]}...")
            lines.append("")

        # Strategic (high effort, high impact)
        strategic = [i for i in insights.insights
                    if i.effort_estimate.value in ['medium', 'high']
                    and i.expected_impact.rank_impact.value == 'high']

        if strategic:
            lines.extend([
                "### Strategic Priorities (Plan for Later)",
                "",
            ])
            for strat in strategic[:3]:
                lines.append(f"- [ ] **{strat.problem[:50]}**")
                lines.append(f"      Action: {strat.spec_change[:100]}...")
                lines.append("")

        return "\n".join(lines)

    def _trust_signal_requirements(self) -> Optional[str]:
        """Generate trust signal requirements from research"""
        if not self.research:
            return None

        gbp = self.research.research.gbp_profile
        if not gbp:
            return None

        lines = [
            "## Trust Signal Requirements",
            "",
            "### Must-Have Trust Elements",
            "",
            f"- [ ] Display rating: **{gbp.rating}** ({gbp.review_count} reviews)",
            "- [ ] Google Reviews widget/integration",
            "- [ ] Rating badges above fold on homepage",
            "- [ ] Trust badges on booking/contact pages",
            "",
        ]

        # Add moats as differentiator signals
        moats = self.research.get_moat_identification()
        if moats:
            lines.extend([
                "### Differentiator Messaging (Feature Prominently)",
                "",
            ])
            for moat in moats[:4]:
                lines.append(f"- [ ] {moat}")
            lines.append("")

        # Review sentiment highlights
        if gbp.place_topics:
            top_topics = sorted(gbp.place_topics.items(), key=lambda x: x[1], reverse=True)[:5]
            lines.extend([
                "### Review Topic Highlights (Use in Copy)",
                "",
            ])
            for topic, count in top_topics:
                lines.append(f"- **{topic}** ({count} mentions)")
            lines.append("")

        return "\n".join(lines)

    def _deployment_checklist(self) -> str:
        """Generate deployment checklist"""
        return """## Deployment Checklist

### Pre-Launch
- [ ] All pages rendering correctly
- [ ] Schema markup validated (Google Rich Results Test)
- [ ] Mobile responsiveness tested
- [ ] Forms submitting correctly
- [ ] Analytics tracking configured
- [ ] Sitemap generated
- [ ] Robots.txt configured
- [ ] Favicon and meta images

### Launch Day
- [ ] DNS configured
- [ ] SSL certificate active
- [ ] 301 redirects in place (if migrating)
- [ ] Google Search Console verified
- [ ] Analytics verified

### Post-Launch
- [ ] Monitor Core Web Vitals
- [ ] Check for crawl errors
- [ ] Verify indexing
- [ ] Test all conversion paths

---

*End of Implementation Spec*"""
