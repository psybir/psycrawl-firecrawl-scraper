"""
Stage 5: EXPORT - Generate Output Specs for Next.js

Input: Actionable Insights + Client config + Intent/Geo Matrix
Output: Output Spec (page map, components, linking rules, schema, LLM SEO)

This stage generates the build instructions for creating the Next.js site.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import hashlib

from ..models import (
    Client,
    Service,
    Location,
    IntentGeoMatrix,
    MatrixCell,
    PageStrategy,
    InsightReport,
    ActionableInsight,
    OutputSpec,
    SiteConfig,
    PageSpec,
    PageType,
    ComponentSpec,
    ComponentType,
    InternalLinkingRule,
    SchemaRequirement,
    LLMAnswerBlock,
    CostRange,
    FAQ,
    VsAlternative,
    CTARules,
    UrgencyLevel,
    MetricsTargets,
    ContentCalendarItem,
    BacklinkTarget,
    GeoTag,
)

logger = logging.getLogger(__name__)


class ExportStage:
    """Generate Output Specs for Next.js site generation"""

    def __init__(
        self,
        client: Client,
        matrix: IntentGeoMatrix,
        insights: InsightReport
    ):
        self.client = client
        self.matrix = matrix
        self.insights = insights

    def run(self) -> OutputSpec:
        """Execute Stage 5: Generate Output Spec"""
        logger.info(f"Stage 5: Generating Output Spec for {self.client.name}")

        # Build site config
        site_config = self._build_site_config()

        # Build page map from matrix
        page_map = self._build_page_map()

        # Build component set
        component_set = self._build_component_set()

        # Build internal linking rules
        linking_rules = self._build_linking_rules()

        # Build schema requirements
        schema_requirements = self._build_schema_requirements()

        # Build LLM answer blocks
        llm_blocks = self._build_llm_answer_blocks()

        # Build content calendar
        content_calendar = self._build_content_calendar()

        # Build backlink targets
        backlink_targets = self._build_backlink_targets()

        # Build metrics targets
        metrics_targets = self._build_metrics_targets()

        # Create output spec
        output_spec = OutputSpec(
            client_id=self.client.id,
            client_name=self.client.name,
            generated_at=datetime.now(),
            version="1.0.0",
            site_config=site_config,
            page_map=page_map,
            component_set=component_set,
            internal_linking_rules=linking_rules,
            schema_requirements=schema_requirements,
            llm_answer_blocks=llm_blocks,
            content_calendar=content_calendar,
            backlink_targets=backlink_targets,
            insights_applied=[i.id for i in self.insights.insights],
            metrics_targets=metrics_targets,
        )

        logger.info(f"Stage 5 Complete: Generated spec with {len(page_map)} pages")
        return output_spec

    def _build_site_config(self) -> SiteConfig:
        """Build global site configuration"""
        contact = self.client.contact
        primary_loc = self.client.primary_location

        service_areas = [loc.name for loc in self.client.locations[:5]]

        return SiteConfig(
            domain=self.client.domain,
            site_name=self.client.name,
            tagline=self.client.brand.tagline if self.client.brand else None,
            primary_phone=contact.phone if contact else None,
            primary_email=contact.email if contact else None,
            address=contact.address if contact else None,
            service_area_text=f"Serving {', '.join(service_areas)} and surrounding areas",
            business_hours="Mon-Fri 8am-6pm, Sat 9am-3pm",
        )

    def _build_page_map(self) -> List[PageSpec]:
        """Build page map from Intent/Geo Matrix"""
        pages = []
        priority = 1

        # Home page
        pages.append(self._create_home_page(priority))
        priority += 1

        # Service pages
        for service in self.client.services:
            if service.is_money_service:
                pages.append(self._create_service_page(service, priority))
                priority += 1

        # Service area pages from matrix
        for cell in self.matrix.cells:
            if cell.page_strategy == PageStrategy.DEDICATED:
                if cell.page_type == "service-area":
                    service = self._get_service(cell.service_id)
                    if service:
                        col = self._get_column(cell.geo_bucket)
                        if col:
                            for location in col.locations[:3]:  # Top 3 per bucket
                                pages.append(self._create_service_area_page(
                                    service, location, cell, priority
                                ))
                                priority += 1

        # About page
        pages.append(self._create_about_page(priority))
        priority += 1

        # Contact page
        pages.append(self._create_contact_page(priority))
        priority += 1

        # Gallery/proof page
        pages.append(self._create_gallery_page(priority))
        priority += 1

        # FAQ page
        pages.append(self._create_faq_page(priority))
        priority += 1

        # Reviews page
        pages.append(self._create_reviews_page(priority))

        return pages

    def _create_home_page(self, priority: int) -> PageSpec:
        """Create home page spec"""
        primary_service = self.client.money_services[0] if self.client.money_services else None

        return PageSpec(
            route="/",
            page_type=PageType.HOME,
            template="home",
            title=f"{self.client.name} | {self.client.brand.tagline if self.client.brand else 'Professional Services'}",
            meta_description=f"{self.client.name} provides expert {primary_service.name if primary_service else 'services'} in {self.client.primary_location.name if self.client.primary_location else 'your area'}.",
            h1=self.client.name,
            components=[
                "Hero",
                "TrustBar",
                "ServicesGrid",
                "ReviewsWidget",
                "ServiceAreaMap",
                "CTASection"
            ],
            schema_types=["LocalBusiness", "Organization"],
            cta_rules=CTARules(
                primary_cta="Get Free Quote",
                urgency_level=UrgencyLevel.HIGH
            ),
            priority=priority,
            keyword_targets=[
                primary_service.name.lower() if primary_service else self.client.vertical.value,
                self.client.primary_location.name.lower() if self.client.primary_location else ""
            ]
        )

    def _create_service_page(self, service: Service, priority: int) -> PageSpec:
        """Create service page spec"""
        primary_loc = self.client.primary_location

        return PageSpec(
            route=f"/services/{service.slug}",
            page_type=PageType.SERVICE,
            template="service",
            title=f"{service.name} | {self.client.name}",
            meta_description=service.short_description or f"Expert {service.name} services by {self.client.name}. {service.description[:100] if service.description else ''}",
            h1=service.name,
            service_target=service.id,
            components=[
                "ServiceHero",
                "TrustBar",
                "ProcessSteps",
                "BeforeAfterGallery",
                "PricingBlock",
                "FAQAccordion",
                "RelatedServices",
                "CTASection"
            ],
            content_requirements=[
                "Service definition",
                "When you need it",
                "Process steps",
                "Pricing range",
                "FAQs",
                "Before/after examples"
            ],
            schema_types=["Service", "FAQPage"],
            cta_rules=CTARules(
                primary_cta="Get Free Quote",
                urgency_level=UrgencyLevel.HIGH
            ),
            priority=priority,
            keyword_targets=service.keywords or [service.name.lower()],
            word_count_target=1500,
            llm_answer_block_id=service.id
        )

    def _create_service_area_page(
        self,
        service: Service,
        location: str,
        cell: MatrixCell,
        priority: int
    ) -> PageSpec:
        """Create service area page spec"""
        city = location.split(",")[0].strip()
        state = location.split(",")[1].strip() if "," in location else "PA"

        # Convert MatrixCTARules to CTARules
        cta_rules = None
        if cell.cta_rules:
            cta_rules = CTARules(
                primary_cta=cell.cta_rules.primary,
                urgency_level=cell.cta_rules.urgency
            )

        return PageSpec(
            route=f"/services/{service.slug}/{city.lower().replace(' ', '-')}",
            page_type=PageType.SERVICE_AREA,
            template="service-area",
            title=f"{service.name} in {city} | {self.client.name}",
            meta_description=f"Looking for {service.name.lower()} in {city}, {state}? {self.client.name} provides expert service. Call today!",
            h1=f"{service.name} in {city}",
            geo_target=GeoTag(city=city, state=state),
            service_target=service.id,
            components=[
                "ServiceAreaHero",
                "LocalTrustBar",
                "ServiceDescription",
                "LocalTestimonials",
                "ServiceAreaMap",
                "CTASection"
            ],
            content_requirements=[
                "Location-specific intro",
                "Service description",
                "Local testimonials",
                "Travel time from shop",
                "Service area map"
            ],
            schema_types=cell.schema_types,
            cta_rules=cta_rules,
            priority=priority,
            keyword_targets=cell.keyword_cluster[:5]
        )

    def _create_about_page(self, priority: int) -> PageSpec:
        """Create about page spec"""
        return PageSpec(
            route="/about",
            page_type=PageType.ABOUT,
            template="about",
            title=f"About {self.client.name}",
            meta_description=f"Learn about {self.client.name}, serving {self.client.primary_location.name if self.client.primary_location else 'your area'} with expert {self.client.vertical.value} services.",
            h1=f"About {self.client.name}",
            components=[
                "AboutHero",
                "OwnerStory",
                "TeamSection",
                "CertificationsGrid",
                "TimelineHistory",
                "CTASection"
            ],
            content_requirements=[
                "Owner/founder story",
                "Years in business",
                "Team photos and bios",
                "Certifications and training",
                "Company values"
            ],
            schema_types=["AboutPage", "Organization"],
            priority=priority
        )

    def _create_contact_page(self, priority: int) -> PageSpec:
        """Create contact page spec"""
        return PageSpec(
            route="/contact",
            page_type=PageType.CONTACT,
            template="contact",
            title=f"Contact {self.client.name}",
            meta_description=f"Contact {self.client.name} for a free quote. Call {self.client.contact.phone if self.client.contact else ''} or fill out our contact form.",
            h1="Contact Us",
            components=[
                "ContactHero",
                "ContactForm",
                "PhoneBlock",
                "LocationMap",
                "BusinessHours"
            ],
            schema_types=["ContactPage", "LocalBusiness"],
            cta_rules=CTARules(
                primary_cta="Send Message",
                urgency_level=UrgencyLevel.MEDIUM
            ),
            priority=priority
        )

    def _create_gallery_page(self, priority: int) -> PageSpec:
        """Create gallery page spec"""
        return PageSpec(
            route="/gallery",
            page_type=PageType.GALLERY,
            template="gallery",
            title=f"Our Work | {self.client.name}",
            meta_description=f"See our {self.client.vertical.value} work. Before and after photos, project gallery, and more.",
            h1="Our Work",
            components=[
                "GalleryHero",
                "BeforeAfterGrid",
                "FilterTabs",
                "CTASection"
            ],
            content_requirements=[
                "Before/after photos",
                "Service type categorization",
                "Location tags"
            ],
            schema_types=["ImageGallery"],
            priority=priority
        )

    def _create_faq_page(self, priority: int) -> PageSpec:
        """Create FAQ page spec"""
        return PageSpec(
            route="/faq",
            page_type=PageType.FAQ,
            template="faq",
            title=f"FAQ | {self.client.name}",
            meta_description=f"Frequently asked questions about our {self.client.vertical.value} services. Get answers before you call.",
            h1="Frequently Asked Questions",
            components=[
                "FAQHero",
                "FAQAccordion",
                "CTASection"
            ],
            schema_types=["FAQPage"],
            priority=priority
        )

    def _create_reviews_page(self, priority: int) -> PageSpec:
        """Create reviews page spec"""
        return PageSpec(
            route="/reviews",
            page_type=PageType.REVIEWS,
            template="reviews",
            title=f"Reviews | {self.client.name}",
            meta_description=f"See what our customers say. {self.client.gbp_profile.review_count if self.client.gbp_profile else 'Hundreds of'} 5-star reviews.",
            h1="Customer Reviews",
            components=[
                "ReviewsHero",
                "AggregateRating",
                "ReviewsGrid",
                "CTASection"
            ],
            schema_types=["Review", "AggregateRating"],
            priority=priority
        )

    def _build_component_set(self) -> List[ComponentSpec]:
        """Build reusable component specifications"""
        return [
            ComponentSpec(
                name="Hero",
                type=ComponentType.HERO,
                description="Main hero section with headline and CTA",
                required_data=["title", "subtitle", "cta_text", "cta_link", "background_image"],
                placement_rules="Top of page, full width"
            ),
            ComponentSpec(
                name="TrustBar",
                type=ComponentType.TRUST,
                description="Trust signals bar with reviews, badges, certifications",
                required_data=["rating", "review_count", "certifications", "badges"],
                placement_rules="Below hero or in header"
            ),
            ComponentSpec(
                name="ReviewsWidget",
                type=ComponentType.TRUST,
                description="Embedded Google reviews widget",
                required_data=["place_id", "display_count"],
                placement_rules="Above fold on service pages"
            ),
            ComponentSpec(
                name="BeforeAfterGallery",
                type=ComponentType.GALLERY,
                description="Interactive before/after comparison gallery",
                required_data=["images"],
                placement_rules="Service pages, proof sections"
            ),
            ComponentSpec(
                name="FAQAccordion",
                type=ComponentType.CONTENT,
                description="Expandable FAQ section",
                required_data=["faqs"],
                placement_rules="Service pages, dedicated FAQ page"
            ),
            ComponentSpec(
                name="ServiceAreaMap",
                type=ComponentType.CONTENT,
                description="Interactive map showing service areas",
                required_data=["center_coordinates", "service_radius", "highlighted_cities"],
                placement_rules="Home page, service area pages"
            ),
            ComponentSpec(
                name="CTASection",
                type=ComponentType.CONVERSION,
                description="Call-to-action section with phone and form",
                required_data=["headline", "phone", "form_id"],
                placement_rules="Bottom of every page"
            ),
            ComponentSpec(
                name="StickyCTA",
                type=ComponentType.CONVERSION,
                description="Fixed CTA bar that appears on scroll",
                required_data=["phone", "cta_text"],
                placement_rules="Fixed position header on scroll"
            ),
            ComponentSpec(
                name="ProcessSteps",
                type=ComponentType.CONTENT,
                description="Visual process/timeline steps",
                required_data=["steps"],
                placement_rules="Service pages"
            ),
            ComponentSpec(
                name="PricingBlock",
                type=ComponentType.CONTENT,
                description="Price range and factors display",
                required_data=["price_range", "factors"],
                placement_rules="Service pages"
            ),
        ]

    def _build_linking_rules(self) -> List[InternalLinkingRule]:
        """Build internal linking rules"""
        return [
            InternalLinkingRule(
                from_page_type="home",
                to_page_type="service",
                anchor_pattern="{service_name}",
                placement="Services grid",
                max_links=6,
                priority=1
            ),
            InternalLinkingRule(
                from_page_type="service",
                to_page_type="service-area",
                anchor_pattern="{service_name} in {city}",
                placement="Service area section",
                max_links=5,
                priority=2
            ),
            InternalLinkingRule(
                from_page_type="service-area",
                to_page_type="service",
                anchor_pattern="Learn more about {service_name}",
                placement="Content body",
                max_links=2,
                priority=3
            ),
            InternalLinkingRule(
                from_page_type="service",
                to_page_type="gallery",
                anchor_pattern="See our {service_name} work",
                placement="Gallery section",
                max_links=1,
                priority=4
            ),
            InternalLinkingRule(
                from_page_type="service",
                to_page_type="reviews",
                anchor_pattern="Read customer reviews",
                placement="Trust section",
                max_links=1,
                priority=5
            ),
        ]

    def _build_schema_requirements(self) -> List[SchemaRequirement]:
        """Build structured data requirements"""
        return [
            SchemaRequirement(
                page_type="home",
                schema_types=["LocalBusiness", "Organization"],
                required_fields=["name", "address", "telephone", "openingHours", "geo", "areaServed"]
            ),
            SchemaRequirement(
                page_type="service",
                schema_types=["Service", "FAQPage"],
                required_fields=["name", "description", "provider", "areaServed", "mainEntity"]
            ),
            SchemaRequirement(
                page_type="service-area",
                schema_types=["Service", "LocalBusiness", "GeoCircle"],
                required_fields=["name", "areaServed", "geo", "geoMidpoint", "geoRadius"]
            ),
            SchemaRequirement(
                page_type="faq",
                schema_types=["FAQPage"],
                required_fields=["mainEntity"]
            ),
            SchemaRequirement(
                page_type="reviews",
                schema_types=["AggregateRating", "Review"],
                required_fields=["ratingValue", "reviewCount", "bestRating"]
            ),
        ]

    def _build_llm_answer_blocks(self) -> List[LLMAnswerBlock]:
        """Build LLM SEO content blocks for each service"""
        blocks = []

        for service in self.client.services:
            if service.is_money_service:
                block = self._create_llm_block(service)
                blocks.append(block)

        return blocks

    def _create_llm_block(self, service: Service) -> LLMAnswerBlock:
        """Create LLM answer block for a service"""
        defined = service.defined_variables

        # Build FAQs from topics
        faqs = []
        if service.faq_topics:
            for topic in service.faq_topics[:5]:
                faqs.append(FAQ(
                    question=f"What is the {topic.lower()} for {service.name.lower()}?",
                    answer=f"[Answer about {topic} for {service.name}]"
                ))

        # Build triggers - handle both dict and model
        if defined:
            if hasattr(defined, 'best_for'):
                triggers = defined.best_for or [f"When you need {service.name.lower()}"]
            elif isinstance(defined, dict):
                triggers = defined.get('best_for') or [f"When you need {service.name.lower()}"]
            else:
                triggers = [f"When you need {service.name.lower()}"]
        else:
            triggers = [f"When you need {service.name.lower()}"]

        # Build process steps - handle both dict and model
        if defined:
            if hasattr(defined, 'process_steps'):
                steps = defined.process_steps
            elif isinstance(defined, dict):
                steps = defined.get('process_steps')
            else:
                steps = None
        else:
            steps = None

        if not steps:
            steps = [
                "Inspection and assessment",
                "Preparation",
                "Service execution",
                "Quality check",
                "Final walkthrough"
            ]

        # Create hash for change detection
        content_str = f"{service.name}{service.description}{str(triggers)}"
        content_hash = hashlib.md5(content_str.encode()).hexdigest()[:8]

        # Get cost_range and timeline - handle both dict and model
        cost_range_val = None
        timeline_val = None
        if defined:
            if hasattr(defined, 'cost_range'):
                cost_range_val = defined.cost_range
                timeline_val = defined.time_range
            elif isinstance(defined, dict):
                cost_range_val = defined.get('cost_range')
                timeline_val = defined.get('time_range')

        return LLMAnswerBlock(
            service=service.name,
            service_slug=service.slug,
            definition=service.description or f"{service.name} is a professional service that...",
            entity_statement=f"{self.client.name} provides {service.name} services in {self.client.primary_location.name if self.client.primary_location else 'your area'}.",
            triggers=triggers,
            cost_range=CostRange(
                range=cost_range_val,
                variables=["Size/severity", "Location", "Time required"],
                disclaimers="Actual costs may vary. Contact us for a free quote."
            ) if cost_range_val else None,
            timeline=timeline_val,
            process_steps=steps,
            benefits=[
                f"Expert {service.name} service",
                "Satisfaction guaranteed",
                "Competitive pricing"
            ],
            how_to_choose=[
                "Check reviews and ratings",
                "Verify licensing and insurance",
                "Ask about warranties",
                "Compare quotes from multiple providers",
                "Look for before/after examples"
            ],
            red_flags=[
                "No physical address or phone number",
                "Pressure to decide immediately",
                "Cash-only payment",
                "No warranty or guarantee offered"
            ],
            faqs=faqs,
            nap_statement=f"{self.client.name} | {self.client.contact.phone if self.client.contact else ''} | {self.client.contact.address if self.client.contact else ''}",
            local_proof_points=[
                f"Serving {self.client.primary_location.name if self.client.primary_location else 'your area'} since [year]",
                f"{self.client.gbp_profile.review_count if self.client.gbp_profile else 'Many'} satisfied customers"
            ],
            content_hash=content_hash,
            last_updated=datetime.now()
        )

    def _build_content_calendar(self) -> List[ContentCalendarItem]:
        """Build content calendar for blog strategy"""
        calendar = []

        # Generate content ideas based on services
        for service in self.client.money_services[:3]:
            # Educational content
            calendar.append(ContentCalendarItem(
                title=f"Complete Guide to {service.name}",
                topic=service.name,
                target_keyword=f"what is {service.name.lower()}",
                content_type="guide",
                word_count_target=2000
            ))

            # FAQ content
            calendar.append(ContentCalendarItem(
                title=f"{service.name} FAQ: Your Questions Answered",
                topic=service.name,
                target_keyword=f"{service.name.lower()} faq",
                content_type="faq",
                word_count_target=1500
            ))

            # Comparison content
            calendar.append(ContentCalendarItem(
                title=f"{service.name} vs [Alternative]: Which is Right for You?",
                topic=service.name,
                target_keyword=f"{service.name.lower()} vs",
                content_type="comparison",
                word_count_target=1500
            ))

        return calendar

    def _build_backlink_targets(self) -> List[BacklinkTarget]:
        """Build backlink acquisition targets"""
        targets = []

        # Local directories
        local_targets = [
            ("Local Chamber of Commerce", "chamber", "high", "membership"),
            ("BBB", "trust_badge", "high", "accreditation"),
            ("Yelp Business", "directory", "medium", "claim listing"),
            ("Local news site", "press", "medium", "press release"),
        ]

        for name, target_type, priority, approach in local_targets:
            targets.append(BacklinkTarget(
                domain=name,
                type=target_type,
                priority=priority,
                approach=approach,
                status="pending"
            ))

        return targets

    def _build_metrics_targets(self) -> MetricsTargets:
        """Build success metrics targets"""
        return MetricsTargets(
            organic_traffic_target=1000,  # Monthly visitors
            conversion_rate_target=0.05,  # 5%
            ranking_targets={
                "primary_keyword": 3,
                "secondary_keyword": 5,
            },
            backlink_target=50,
            authority_target=20
        )

    def _get_service(self, service_id: str) -> Optional[Service]:
        """Get service by ID"""
        for service in self.client.services:
            if service.id == service_id:
                return service
        return None

    def _get_column(self, geo_bucket: str):
        """Get matrix column by geo bucket"""
        for col in self.matrix.columns:
            if col.geo_bucket.value == geo_bucket:
                return col
        return None
