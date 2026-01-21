"""
Stage 3: NORMALIZE - Map raw scrape to Competitor Profile fields

Input: Raw Source data
Output: Competitor Profiles (structured, not vibes)

This stage transforms raw scraped data into structured competitor profiles
using Firecrawl EXTRACT strategy and normalization logic.
"""

import logging
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from ..models import (
    Source,
    SourceType,
    GeoTag,
    CompetitorProfile,
    TrustSignals,
    ConversionMechanics,
    SEOStructure,
    TechnicalSEO,
    BacklinkProfile,
    SocialPresence,
    ServicePage,
    ServiceAreaPage,
    PhotoType,
    ReviewRecency,
    PriceTransparency,
    ContentFreshness,
    ThreatLevel,
)

logger = logging.getLogger(__name__)


class NormalizeStage:
    """Normalize raw data into structured Competitor Profiles"""

    def __init__(self, sources: List[Source], firecrawl_client=None):
        self.sources = sources
        self.firecrawl = firecrawl_client
        self.profiles: Dict[str, CompetitorProfile] = {}

    async def run(self) -> List[CompetitorProfile]:
        """Execute Stage 3: Normalize into Competitor Profiles"""
        logger.info(f"Stage 3: Normalizing {len(self.sources)} sources into profiles")

        # Group sources by domain
        sources_by_domain = self._group_sources_by_domain()

        # Build profile for each competitor domain
        for domain, domain_sources in sources_by_domain.items():
            try:
                profile = await self._build_competitor_profile(domain, domain_sources)
                self.profiles[domain] = profile
            except Exception as e:
                logger.error(f"Error building profile for {domain}: {e}")

        # Calculate threat levels
        for profile in self.profiles.values():
            profile.calculate_threat_level()

        logger.info(f"Stage 3 Complete: Built {len(self.profiles)} competitor profiles")
        return list(self.profiles.values())

    def _group_sources_by_domain(self) -> Dict[str, List[Source]]:
        """Group sources by domain"""
        grouped = {}
        for source in self.sources:
            if source.domain:
                if source.domain not in grouped:
                    grouped[source.domain] = []
                grouped[source.domain].append(source)
        return grouped

    async def _build_competitor_profile(
        self,
        domain: str,
        sources: List[Source]
    ) -> CompetitorProfile:
        """Build a competitor profile from sources"""

        # Get main website source
        website_source = next(
            (s for s in sources if s.source_type == SourceType.COMPETITOR_WEBSITE),
            None
        )

        # Get page sources
        page_sources = [s for s in sources if s.source_type == SourceType.COMPETITOR_PAGE]

        # Get SERP sources
        serp_sources = [s for s in sources if s.source_type in [
            SourceType.SERP_ORGANIC, SourceType.SERP_LOCAL_PACK
        ]]

        # Extract structured data
        trust_signals = await self._extract_trust_signals(website_source, page_sources)
        conversion_mechanics = await self._extract_conversion_mechanics(website_source, page_sources)
        seo_structure = self._extract_seo_structure(page_sources)
        technical_seo = self._extract_technical_seo(website_source)
        grid_performance = self._extract_grid_performance(serp_sources)
        backlinks = self._extract_backlink_data(sources)
        social_presence = self._extract_social_presence(website_source, page_sources)

        # Get geo tags from sources
        geo_tags = []
        for source in sources:
            geo_tags.extend(source.geo_tags)
        geo_tags = list({gt.full_name: gt for gt in geo_tags}.values())

        # Identify services offered
        services_offered = self._identify_services(page_sources)

        # Identify strengths and weaknesses
        strengths, weaknesses = self._analyze_strengths_weaknesses(
            trust_signals, conversion_mechanics, seo_structure, backlinks
        )

        profile = CompetitorProfile(
            id=str(uuid.uuid4()),
            domain=domain,
            name=self._extract_business_name(website_source),
            url=f"https://{domain}",
            sources_scraped=sources,
            geo_tags=geo_tags,
            services_offered=services_offered,
            trust_signals=trust_signals,
            conversion_mechanics=conversion_mechanics,
            seo_structure=seo_structure,
            technical_seo=technical_seo,
            grid_performance=grid_performance,
            backlinks=backlinks,
            social_presence=social_presence,
            strengths=strengths,
            weaknesses=weaknesses,
            analyzed_at=datetime.now(),
            confidence_score=self._calculate_confidence(sources),
        )

        # Calculate scores
        profile.trust_signals.calculate_trust_score()
        profile.conversion_mechanics.calculate_conversion_score()

        return profile

    async def _extract_trust_signals(
        self,
        website_source: Optional[Source],
        page_sources: List[Source]
    ) -> TrustSignals:
        """Extract trust signals from sources"""
        signals = TrustSignals()

        if not website_source or not website_source.raw_data:
            return signals

        raw = website_source.raw_data
        content = raw.get("markdown", "") or raw.get("content", "")
        metadata = raw.get("metadata", {})

        # Extract reviews from local pack data
        local_sources = [s for s in page_sources if s.source_type == SourceType.SERP_LOCAL_PACK]
        for source in local_sources:
            if source.raw_data:
                signals.review_count = source.raw_data.get("reviews_count") or signals.review_count
                signals.rating = source.raw_data.get("rating") or signals.rating

        # Check for certifications/licenses
        cert_patterns = [
            r"certified", r"licensed", r"insured", r"bonded",
            r"warranty", r"guarantee", r"certification", r"accredited"
        ]
        for pattern in cert_patterns:
            if re.search(pattern, content, re.I):
                if "certif" in pattern or "accredit" in pattern:
                    signals.certifications.append(pattern)
                elif "license" in pattern:
                    signals.licenses_shown = True
                elif "insur" in pattern:
                    signals.insurance_shown = True
                elif "warrant" in pattern or "guarant" in pattern:
                    signals.warranty_guarantee_language = "present"

        # Check for gallery/photos
        if re.search(r"before\s*(and|&)\s*after|gallery|portfolio", content, re.I):
            signals.before_after_gallery = True

        # Check for team/about content
        if re.search(r"our\s*team|meet\s*the|about\s*us|our\s*story", content, re.I):
            signals.team_bios = True

        # Check photo authenticity (simplified heuristic)
        if re.search(r"shutterstock|stock\s*photo|istock|unsplash", content, re.I):
            signals.real_photos_vs_stock = PhotoType.STOCK
        elif re.search(r"our\s*work|our\s*team|our\s*shop", content, re.I):
            signals.real_photos_vs_stock = PhotoType.REAL
        else:
            signals.real_photos_vs_stock = PhotoType.MIXED

        # Check for badges/associations
        badge_patterns = [
            r"bbb", r"better\s*business", r"chamber\s*of\s*commerce",
            r"angi|angie", r"home\s*advisor", r"yelp", r"google\s*partner"
        ]
        for pattern in badge_patterns:
            if re.search(pattern, content, re.I):
                signals.badges_associations.append(pattern.replace(r"\s*", " "))

        return signals

    async def _extract_conversion_mechanics(
        self,
        website_source: Optional[Source],
        page_sources: List[Source]
    ) -> ConversionMechanics:
        """Extract conversion mechanics from sources"""
        mechanics = ConversionMechanics()

        if not website_source or not website_source.raw_data:
            return mechanics

        raw = website_source.raw_data
        content = raw.get("markdown", "") or raw.get("content", "")
        html = raw.get("html", "")

        # Check for phone visibility
        phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        if re.search(phone_pattern, content):
            mechanics.phone_visible = True

        # Check for clickable phone (tel: link)
        if "tel:" in html.lower() if html else False:
            mechanics.phone_clickable = True

        # Check for sticky elements
        if re.search(r"sticky|fixed", html, re.I) if html else False:
            mechanics.sticky_header = True

        # Check for forms
        if re.search(r"<form|contact\s*form|get\s*a?\s*quote|request\s*estimate", content, re.I):
            mechanics.form_present = True

        # Check for chat widgets
        chat_patterns = [
            r"livechat|intercom|drift|hubspot|zendesk|tawk|crisp|freshchat"
        ]
        for pattern in chat_patterns:
            if re.search(pattern, html or content, re.I):
                mechanics.chat_widget = True
                mechanics.chat_provider = pattern.replace("|", "/").split("/")[0]
                break

        # Check for emergency language
        if re.search(r"24/7|same\s*day|emergency|urgent|immediate", content, re.I):
            mechanics.emergency_language = True

        # Check for financing
        if re.search(r"financing|payment\s*plan|affirm|klarna|afterpay", content, re.I):
            mechanics.financing_shown = True

        # Check for pricing
        if re.search(r"\$\d+|starting\s*at|prices?\s*from|cost", content, re.I):
            mechanics.price_anchors = True
            if re.search(r"\$\d+\s*-\s*\$\d+", content):
                mechanics.price_transparency = PriceTransparency.RANGES

        # Check for free quote language
        if re.search(r"free\s*(quote|estimate|consultation)", content, re.I):
            mechanics.free_quote_language = True

        # Check CTA types
        cta_patterns = {
            "call": r"call\s*us|call\s*now|phone",
            "form": r"contact\s*form|get\s*quote|submit",
            "chat": r"chat\s*with|live\s*chat",
            "schedule": r"schedule|book\s*online|appointment",
        }
        for cta_type, pattern in cta_patterns.items():
            if re.search(pattern, content, re.I):
                mechanics.cta_types.append(cta_type)

        mechanics.multiple_cta_types = len(mechanics.cta_types) > 1

        return mechanics

    def _extract_seo_structure(self, page_sources: List[Source]) -> SEOStructure:
        """Extract SEO structure from page sources"""
        structure = SEOStructure()
        structure.page_count = len(page_sources)

        page_types_found = set()
        service_pages = []
        service_area_pages = []

        for source in page_sources:
            url = source.url.lower()
            raw = source.raw_data or {}

            # Detect page type from URL
            if "/service" in url or "/what-we-do" in url:
                page_types_found.add("service")
                service_pages.append(ServicePage(
                    url=source.url,
                    service=self._extract_service_from_url(url),
                    word_count=len(raw.get("markdown", "").split()) if raw.get("markdown") else None
                ))
            elif "/area" in url or "/location" in url or "/city" in url:
                page_types_found.add("service-area")
                service_area_pages.append(ServiceAreaPage(
                    url=source.url,
                    location=self._extract_location_from_url(url)
                ))
            elif "/about" in url:
                page_types_found.add("about")
            elif "/contact" in url:
                page_types_found.add("contact")
            elif "/blog" in url or "/news" in url:
                page_types_found.add("blog")
                structure.blog_active = True
            elif "/faq" in url:
                page_types_found.add("faq")
            elif "/gallery" in url or "/portfolio" in url:
                page_types_found.add("gallery")
            elif "/review" in url or "/testimonial" in url:
                page_types_found.add("reviews")

        structure.page_types_present = list(page_types_found)
        structure.service_pages = service_pages
        structure.service_area_pages = service_area_pages

        return structure

    def _extract_technical_seo(self, website_source: Optional[Source]) -> TechnicalSEO:
        """Extract technical SEO data"""
        tech = TechnicalSEO()

        if not website_source or not website_source.raw_data:
            return tech

        raw = website_source.raw_data
        metadata = raw.get("metadata", {})

        # SSL check
        tech.ssl = website_source.url.startswith("https")

        # Mobile friendly (assume if viewport is present)
        if metadata.get("viewport"):
            tech.mobile_friendly = True

        return tech

    def _extract_grid_performance(self, serp_sources: List[Source]) -> Dict[str, float]:
        """Extract grid/ranking performance by location"""
        performance = {}

        for source in serp_sources:
            if source.serp_position and source.geo_tags:
                for geo_tag in source.geo_tags:
                    location = geo_tag.city
                    if location not in performance:
                        performance[location] = []
                    performance[location].append(source.serp_position)

        # Average rankings per location
        return {loc: sum(ranks)/len(ranks) for loc, ranks in performance.items()}

    def _extract_backlink_data(self, sources: List[Source]) -> BacklinkProfile:
        """Extract backlink data (requires DataForSEO backlinks API)"""
        # This would be populated from DataForSEO backlinks API
        return BacklinkProfile()

    def _extract_social_presence(
        self,
        website_source: Optional[Source],
        page_sources: List[Source]
    ) -> SocialPresence:
        """Extract social media presence"""
        social = SocialPresence()

        if not website_source or not website_source.raw_data:
            return social

        content = website_source.raw_data.get("html", "") or ""

        # Find social links
        social_patterns = {
            "facebook": r"facebook\.com/[^\"'\s]+",
            "instagram": r"instagram\.com/[^\"'\s]+",
            "youtube": r"youtube\.com/[^\"'\s]+",
            "linkedin": r"linkedin\.com/[^\"'\s]+",
            "tiktok": r"tiktok\.com/@[^\"'\s]+",
        }

        for platform, pattern in social_patterns.items():
            match = re.search(pattern, content, re.I)
            if match:
                setattr(social, platform, f"https://{match.group()}")

        return social

    def _identify_services(self, page_sources: List[Source]) -> List[str]:
        """Identify services offered from page URLs and content"""
        services = set()

        for source in page_sources:
            url = source.url.lower()
            if "/service" in url:
                service = self._extract_service_from_url(url)
                if service:
                    services.add(service)

        return list(services)

    def _extract_service_from_url(self, url: str) -> str:
        """Extract service name from URL"""
        # Get last path segment
        parts = url.rstrip("/").split("/")
        if parts:
            return parts[-1].replace("-", " ").replace("_", " ").title()
        return ""

    def _extract_location_from_url(self, url: str) -> str:
        """Extract location from URL"""
        parts = url.rstrip("/").split("/")
        if parts:
            return parts[-1].replace("-", " ").replace("_", " ").title()
        return ""

    def _extract_business_name(self, source: Optional[Source]) -> str:
        """Extract business name from source"""
        if not source or not source.raw_data:
            return source.domain if source else "Unknown"

        metadata = source.raw_data.get("metadata", {})
        return metadata.get("title", source.domain).split("|")[0].strip()

    def _analyze_strengths_weaknesses(
        self,
        trust: TrustSignals,
        conversion: ConversionMechanics,
        seo: SEOStructure,
        backlinks: BacklinkProfile
    ) -> tuple:
        """Analyze strengths and weaknesses"""
        strengths = []
        weaknesses = []

        # Trust analysis
        if trust.review_count and trust.review_count > 50:
            strengths.append(f"Strong review presence ({trust.review_count} reviews)")
        elif not trust.review_count or trust.review_count < 10:
            weaknesses.append("Low review count")

        if trust.rating and trust.rating >= 4.5:
            strengths.append(f"Excellent rating ({trust.rating})")
        elif trust.rating and trust.rating < 4.0:
            weaknesses.append(f"Rating below 4.0 ({trust.rating})")

        if trust.before_after_gallery:
            strengths.append("Has before/after gallery")
        else:
            weaknesses.append("No visual proof of work")

        if trust.certifications:
            strengths.append("Displays certifications")

        # Conversion analysis
        if conversion.sticky_cta or conversion.sticky_call:
            strengths.append("Sticky CTA present")
        else:
            weaknesses.append("No sticky CTA")

        if conversion.chat_widget:
            strengths.append("Live chat available")

        if not conversion.phone_visible:
            weaknesses.append("Phone not prominently displayed")

        if conversion.multiple_cta_types:
            strengths.append("Multiple contact methods")

        # SEO analysis
        if seo.service_area_pages:
            strengths.append(f"{len(seo.service_area_pages)} service area pages")
        else:
            weaknesses.append("No service area pages")

        if seo.blog_active:
            strengths.append("Active blog")
        else:
            weaknesses.append("No active blog content")

        return strengths, weaknesses

    def _calculate_confidence(self, sources: List[Source]) -> float:
        """Calculate confidence score based on data quality"""
        if not sources:
            return 0.0

        # More sources = higher confidence
        source_score = min(len(sources) / 20, 0.5)

        # Successful scrapes = higher confidence
        successful = sum(1 for s in sources if s.scrape_status.value == "success")
        success_score = (successful / len(sources)) * 0.3

        # Fresh data = higher confidence
        fresh = sum(1 for s in sources if s.data_freshness.value == "current")
        freshness_score = (fresh / len(sources)) * 0.2

        return min(source_score + success_score + freshness_score, 1.0)
