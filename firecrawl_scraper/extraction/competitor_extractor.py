"""
Competitor Extractor - Firecrawl EXTRACT strategy for competitor profiles

Uses Firecrawl's EXTRACT mode to pull structured data from competitor websites
matching the CompetitorProfile schema.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CompetitorExtractor:
    """Extract structured competitor data using Firecrawl EXTRACT strategy"""

    # Extraction schema for competitor websites
    EXTRACTION_SCHEMA = {
        "type": "object",
        "properties": {
            "business_info": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Business name"},
                    "phone": {"type": "string", "description": "Primary phone number"},
                    "address": {"type": "string", "description": "Business address"},
                    "email": {"type": "string", "description": "Contact email"},
                    "hours": {"type": "string", "description": "Business hours"}
                }
            },
            "trust_signals": {
                "type": "object",
                "properties": {
                    "has_reviews": {"type": "boolean"},
                    "review_count_text": {"type": "string"},
                    "rating_text": {"type": "string"},
                    "certifications": {"type": "array", "items": {"type": "string"}},
                    "licenses_mentioned": {"type": "boolean"},
                    "insurance_mentioned": {"type": "boolean"},
                    "warranty_text": {"type": "string"},
                    "years_in_business": {"type": "string"},
                    "has_gallery": {"type": "boolean"},
                    "has_team_photos": {"type": "boolean"},
                    "badges": {"type": "array", "items": {"type": "string"}}
                }
            },
            "conversion_elements": {
                "type": "object",
                "properties": {
                    "has_form": {"type": "boolean"},
                    "form_fields_count": {"type": "integer"},
                    "has_chat": {"type": "boolean"},
                    "chat_provider": {"type": "string"},
                    "cta_text": {"type": "array", "items": {"type": "string"}},
                    "phone_clickable": {"type": "boolean"},
                    "emergency_language": {"type": "boolean"},
                    "free_quote_text": {"type": "string"},
                    "financing_mentioned": {"type": "boolean"}
                }
            },
            "services": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "url": {"type": "string"},
                        "description": {"type": "string"}
                    }
                }
            },
            "service_areas": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Cities or areas mentioned as service areas"
            },
            "social_links": {
                "type": "object",
                "properties": {
                    "facebook": {"type": "string"},
                    "instagram": {"type": "string"},
                    "youtube": {"type": "string"},
                    "linkedin": {"type": "string"},
                    "tiktok": {"type": "string"}
                }
            },
            "pricing_info": {
                "type": "object",
                "properties": {
                    "has_pricing": {"type": "boolean"},
                    "pricing_text": {"type": "string"},
                    "price_range": {"type": "string"}
                }
            }
        }
    }

    def __init__(self, firecrawl_client=None):
        self.firecrawl = firecrawl_client

    async def extract(self, url: str) -> Dict[str, Any]:
        """Extract structured data from a competitor URL"""
        if not self.firecrawl:
            logger.warning("Firecrawl client not configured")
            return {}

        try:
            result = await self.firecrawl.scrape(
                url=url,
                formats=["extract"],
                extract_schema=self.EXTRACTION_SCHEMA,
                only_main_content=False  # Need full page for trust signals
            )

            extracted = result.get("extract", {})
            logger.info(f"Extracted data from {url}")
            return self._normalize_extracted_data(extracted)

        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            return {}

    def _normalize_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize extracted data to match our models"""
        normalized = {
            "business_info": data.get("business_info", {}),
            "trust_signals": self._normalize_trust_signals(data.get("trust_signals", {})),
            "conversion_elements": data.get("conversion_elements", {}),
            "services": data.get("services", []),
            "service_areas": data.get("service_areas", []),
            "social_links": data.get("social_links", {}),
            "pricing_info": data.get("pricing_info", {}),
            "extracted_at": datetime.now().isoformat()
        }
        return normalized

    def _normalize_trust_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize trust signals"""
        # Parse review count from text
        review_count = None
        if signals.get("review_count_text"):
            import re
            match = re.search(r'\d+', signals["review_count_text"])
            if match:
                review_count = int(match.group())

        # Parse rating from text
        rating = None
        if signals.get("rating_text"):
            import re
            match = re.search(r'(\d+\.?\d*)', signals["rating_text"])
            if match:
                rating = float(match.group())

        return {
            **signals,
            "review_count": review_count,
            "rating": rating
        }

    @staticmethod
    def get_extraction_prompt() -> str:
        """Get the extraction prompt for LLM-based extraction"""
        return """
        Extract the following information from this business website:

        1. Business Info: Name, phone, address, email, hours
        2. Trust Signals:
           - Reviews (count, rating, sources)
           - Certifications and licenses
           - Insurance mentioned
           - Warranty/guarantee language
           - Years in business
           - Photo gallery presence
           - Team/owner photos
           - Industry badges/associations
        3. Conversion Elements:
           - Contact form (fields count)
           - Live chat (provider)
           - CTA buttons text
           - Click-to-call
           - Emergency/24-7 language
           - Free quote offers
           - Financing options
        4. Services: List of services with URLs
        5. Service Areas: Cities/areas served
        6. Social Links: Facebook, Instagram, YouTube, LinkedIn, TikTok
        7. Pricing: Any pricing information shown

        Return structured JSON matching the schema.
        """


class GeoTagger:
    """Tag data with geographic information"""

    def __init__(self, primary_location: Optional[Dict] = None):
        self.primary_location = primary_location

    def tag_source(self, source_data: Dict, location_hints: List[str] = None) -> Dict:
        """Add geo tags to source data based on content and hints"""
        geo_tags = []

        # Check content for location mentions
        content = source_data.get("content", "") or source_data.get("markdown", "")

        # Simple city detection (would use NER in production)
        location_patterns = [
            "Bethlehem", "Easton", "Allentown", "Northampton",
            "Quakertown", "Doylestown", "Stroudsburg"
        ]

        for loc in location_patterns:
            if loc.lower() in content.lower():
                geo_tags.append({
                    "city": loc,
                    "state": "PA",
                    "detected_from": "content"
                })

        # Add hints as tags
        if location_hints:
            for hint in location_hints:
                if "," in hint:
                    city, state = hint.split(",")
                    geo_tags.append({
                        "city": city.strip(),
                        "state": state.strip(),
                        "detected_from": "hint"
                    })

        source_data["geo_tags"] = geo_tags
        return source_data


class SourceClassifier:
    """Classify source types from URLs and content"""

    SOURCE_PATTERNS = {
        "serp_organic": ["google.com/search"],
        "serp_local_pack": ["google.com/maps", "google.com/local"],
        "gbp_profile": ["business.google.com", "g.page"],
        "directory_listing": [
            "yelp.com", "yellowpages.com", "bbb.org",
            "angieslist.com", "homeadvisor.com", "thumbtack.com"
        ],
        "review_site": ["trustpilot.com", "sitejabber.com"],
        "social_media": [
            "facebook.com", "instagram.com", "linkedin.com",
            "twitter.com", "tiktok.com", "youtube.com"
        ],
        "chamber_commerce": ["chamber", "chamberof"],
        "industry_publication": ["pdrnation.com", "dentcraft.com"],
    }

    @classmethod
    def classify(cls, url: str) -> str:
        """Classify source type from URL"""
        url_lower = url.lower()

        for source_type, patterns in cls.SOURCE_PATTERNS.items():
            for pattern in patterns:
                if pattern in url_lower:
                    return source_type

        # Default to competitor website if no match
        return "competitor_website"

    @classmethod
    def is_competitor_site(cls, url: str, known_domains: List[str] = None) -> bool:
        """Check if URL is a competitor website"""
        from urllib.parse import urlparse

        if not known_domains:
            known_domains = []

        try:
            domain = urlparse(url).netloc.replace("www.", "")
            return domain in known_domains
        except:
            return False
