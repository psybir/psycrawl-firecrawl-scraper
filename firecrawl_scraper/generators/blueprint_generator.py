"""
Blueprint Generator - Generate OutputSpec from insights and matrix

Creates the complete build blueprint for Next.js site generation.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

from ..models import (
    Client,
    IntentGeoMatrix,
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
    CTARules,
    UrgencyLevel,
    MetricsTargets,
    PageStrategy,
    GeoTag,
)

logger = logging.getLogger(__name__)


class BlueprintGenerator:
    """Generate complete site blueprint from pipeline outputs"""

    def __init__(
        self,
        client: Client,
        matrix: IntentGeoMatrix,
        insights: InsightReport
    ):
        self.client = client
        self.matrix = matrix
        self.insights = insights

    def generate(self) -> OutputSpec:
        """Generate complete OutputSpec"""
        logger.info(f"Generating blueprint for {self.client.name}")

        return OutputSpec(
            client_id=self.client.id,
            client_name=self.client.name,
            generated_at=datetime.now(),
            version="1.0.0",
            site_config=self._generate_site_config(),
            page_map=self._generate_page_map(),
            component_set=self._generate_components(),
            internal_linking_rules=self._generate_linking_rules(),
            schema_requirements=self._generate_schema_requirements(),
            insights_applied=[i.id for i in self.insights.insights if i.status.value == "approved"],
            metrics_targets=self._generate_metrics_targets()
        )

    def _generate_site_config(self) -> SiteConfig:
        """Generate site configuration"""
        contact = self.client.contact
        primary = self.client.primary_location

        return SiteConfig(
            domain=self.client.domain,
            site_name=self.client.name,
            tagline=self.client.brand.tagline if self.client.brand else None,
            primary_phone=contact.phone if contact else None,
            primary_email=contact.email if contact else None,
            address=contact.address if contact else None,
            service_area_text=self._generate_service_area_text()
        )

    def _generate_service_area_text(self) -> str:
        """Generate service area description"""
        primary = self.client.primary_location
        areas = [loc.name for loc in self.client.locations[:5]]

        if primary:
            return f"Proudly serving {primary.name} and surrounding areas including {', '.join(areas[1:4])}"
        return f"Serving {', '.join(areas)}"

    def _generate_page_map(self) -> List[PageSpec]:
        """Generate complete page map"""
        pages = []
        priority = 1

        # Core pages
        pages.extend(self._generate_core_pages(priority))
        priority += len(pages)

        # Service pages
        pages.extend(self._generate_service_pages(priority))
        priority += len([p for p in pages if p.page_type == PageType.SERVICE])

        # Service area pages from matrix
        pages.extend(self._generate_service_area_pages(priority))

        return pages

    def _generate_core_pages(self, start_priority: int) -> List[PageSpec]:
        """Generate core site pages"""
        pages = []
        priority = start_priority

        # Home
        pages.append(PageSpec(
            route="/",
            page_type=PageType.HOME,
            template="home",
            title=f"{self.client.name} | {self.client.brand.tagline if self.client.brand else 'Professional Services'}",
            h1=self.client.name,
            components=["Hero", "TrustBar", "ServicesGrid", "ReviewsWidget", "CTASection"],
            schema_types=["LocalBusiness", "Organization"],
            priority=priority
        ))
        priority += 1

        # About
        pages.append(PageSpec(
            route="/about",
            page_type=PageType.ABOUT,
            template="about",
            title=f"About {self.client.name}",
            h1=f"About {self.client.name}",
            components=["AboutHero", "OwnerStory", "TeamSection", "CTASection"],
            schema_types=["AboutPage"],
            priority=priority
        ))
        priority += 1

        # Contact
        pages.append(PageSpec(
            route="/contact",
            page_type=PageType.CONTACT,
            template="contact",
            title=f"Contact {self.client.name}",
            h1="Contact Us",
            components=["ContactForm", "LocationMap", "BusinessHours"],
            schema_types=["ContactPage", "LocalBusiness"],
            priority=priority
        ))
        priority += 1

        # Gallery
        pages.append(PageSpec(
            route="/gallery",
            page_type=PageType.GALLERY,
            template="gallery",
            title=f"Our Work | {self.client.name}",
            h1="Our Work",
            components=["GalleryHero", "BeforeAfterGrid"],
            schema_types=["ImageGallery"],
            priority=priority
        ))
        priority += 1

        # FAQ
        pages.append(PageSpec(
            route="/faq",
            page_type=PageType.FAQ,
            template="faq",
            title=f"FAQ | {self.client.name}",
            h1="Frequently Asked Questions",
            components=["FAQAccordion"],
            schema_types=["FAQPage"],
            priority=priority
        ))
        priority += 1

        # Reviews
        pages.append(PageSpec(
            route="/reviews",
            page_type=PageType.REVIEWS,
            template="reviews",
            title=f"Reviews | {self.client.name}",
            h1="Customer Reviews",
            components=["AggregateRating", "ReviewsGrid"],
            schema_types=["AggregateRating"],
            priority=priority
        ))

        return pages

    def _generate_service_pages(self, start_priority: int) -> List[PageSpec]:
        """Generate service pages"""
        pages = []
        priority = start_priority

        for service in self.client.services:
            if service.is_money_service:
                pages.append(PageSpec(
                    route=f"/services/{service.slug}",
                    page_type=PageType.SERVICE,
                    template="service",
                    title=f"{service.name} | {self.client.name}",
                    meta_description=service.short_description,
                    h1=service.name,
                    service_target=service.id,
                    components=["ServiceHero", "TrustBar", "ProcessSteps", "BeforeAfterGallery", "FAQAccordion", "CTASection"],
                    schema_types=["Service", "FAQPage"],
                    cta_rules=CTARules(primary_cta="Get Free Quote", urgency_level=UrgencyLevel.HIGH),
                    priority=priority,
                    keyword_targets=service.keywords or [service.name.lower()],
                    word_count_target=1500
                ))
                priority += 1

        return pages

    def _generate_service_area_pages(self, start_priority: int) -> List[PageSpec]:
        """Generate service area pages from matrix"""
        pages = []
        priority = start_priority

        for cell in self.matrix.cells:
            if cell.page_strategy != PageStrategy.DEDICATED:
                continue
            if cell.page_type != "service-area":
                continue

            service = self._get_service(cell.service_id)
            col = self._get_column(cell.geo_bucket)

            if not service or not col:
                continue

            # Create page for each location in bucket
            for location in col.locations[:3]:
                city = location.split(",")[0].strip()
                state = location.split(",")[1].strip() if "," in location else "PA"

                pages.append(PageSpec(
                    route=f"/services/{service.slug}/{city.lower().replace(' ', '-')}",
                    page_type=PageType.SERVICE_AREA,
                    template="service-area",
                    title=f"{service.name} in {city} | {self.client.name}",
                    meta_description=f"Expert {service.name.lower()} in {city}, {state}. {self.client.name} provides fast, quality service.",
                    h1=f"{service.name} in {city}",
                    geo_target=GeoTag(city=city, state=state),
                    service_target=service.id,
                    components=["ServiceAreaHero", "LocalTrustBar", "ServiceAreaMap", "CTASection"],
                    schema_types=cell.schema_types,
                    cta_rules=cell.cta_rules,
                    priority=priority,
                    keyword_targets=cell.keyword_cluster[:5]
                ))
                priority += 1

        return pages

    def _generate_components(self) -> List[ComponentSpec]:
        """Generate component specifications"""
        return [
            ComponentSpec(name="Hero", type=ComponentType.HERO, required_data=["title", "cta_text"]),
            ComponentSpec(name="TrustBar", type=ComponentType.TRUST, required_data=["rating", "review_count"]),
            ComponentSpec(name="ServicesGrid", type=ComponentType.CONTENT, required_data=["services"]),
            ComponentSpec(name="ReviewsWidget", type=ComponentType.TRUST, required_data=["place_id"]),
            ComponentSpec(name="BeforeAfterGallery", type=ComponentType.GALLERY, required_data=["images"]),
            ComponentSpec(name="FAQAccordion", type=ComponentType.CONTENT, required_data=["faqs"]),
            ComponentSpec(name="CTASection", type=ComponentType.CONVERSION, required_data=["headline", "phone"]),
            ComponentSpec(name="ServiceAreaMap", type=ComponentType.CONTENT, required_data=["coordinates"]),
            ComponentSpec(name="ProcessSteps", type=ComponentType.CONTENT, required_data=["steps"]),
        ]

    def _generate_linking_rules(self) -> List[InternalLinkingRule]:
        """Generate internal linking rules"""
        return [
            InternalLinkingRule(from_page_type="home", to_page_type="service", anchor_pattern="{service_name}", priority=1),
            InternalLinkingRule(from_page_type="service", to_page_type="service-area", anchor_pattern="{service_name} in {city}", priority=2),
            InternalLinkingRule(from_page_type="service-area", to_page_type="service", anchor_pattern="Learn more about {service_name}", priority=3),
            InternalLinkingRule(from_page_type="service", to_page_type="gallery", anchor_pattern="See our work", priority=4),
        ]

    def _generate_schema_requirements(self) -> List[SchemaRequirement]:
        """Generate schema requirements"""
        return [
            SchemaRequirement(page_type="home", schema_types=["LocalBusiness", "Organization"]),
            SchemaRequirement(page_type="service", schema_types=["Service", "FAQPage"]),
            SchemaRequirement(page_type="service-area", schema_types=["Service", "LocalBusiness", "GeoCircle"]),
            SchemaRequirement(page_type="faq", schema_types=["FAQPage"]),
        ]

    def _generate_metrics_targets(self) -> MetricsTargets:
        """Generate success metrics targets"""
        return MetricsTargets(
            organic_traffic_target=1000,
            conversion_rate_target=0.05,
            backlink_target=50,
            authority_target=20
        )

    def _get_service(self, service_id: str):
        for s in self.client.services:
            if s.id == service_id:
                return s
        return None

    def _get_column(self, geo_bucket: str):
        for c in self.matrix.columns:
            if c.geo_bucket.value == geo_bucket:
                return c
        return None
