"""
Core entities - Client, Service models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

from .geo import Location, GeoScope, GeoTag


class Vertical(str, Enum):
    """Industry verticals"""
    # Blue Collar / Home Services
    PDR = "pdr"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    ROOFING = "roofing"
    AUTO_BODY = "auto_body"
    LANDSCAPING = "landscaping"
    ELECTRICAL = "electrical"

    # Entertainment / Experience
    ESCAPE_ROOM = "escape_room"
    ENTERTAINMENT_VENUE = "entertainment_venue"
    AMUSEMENT = "amusement"
    EVENTS = "events"

    # Healthcare
    DENTAL = "dental"
    MEDSPA = "medspa"
    CHIROPRACTIC = "chiropractic"

    # Professional Services
    LAW = "law"
    ACCOUNTING = "accounting"
    REAL_ESTATE = "real_estate"

    # Hospitality
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    TOURISM = "tourism"


class BusinessModel(str, Enum):
    """How customers interact geographically"""
    SERVICE_DELIVERY = "service_delivery"  # Provider travels TO customer (PDR, plumbing)
    DESTINATION = "destination"            # Customer travels TO provider (escape room, restaurant)
    HYBRID = "hybrid"                      # Both (dental with mobile service)


# Vertical classification helpers
BLUE_COLLAR_VERTICALS = {
    Vertical.PDR, Vertical.PLUMBING, Vertical.HVAC, Vertical.ROOFING,
    Vertical.AUTO_BODY, Vertical.LANDSCAPING, Vertical.ELECTRICAL
}

ENTERTAINMENT_VERTICALS = {
    Vertical.ESCAPE_ROOM, Vertical.ENTERTAINMENT_VENUE,
    Vertical.AMUSEMENT, Vertical.EVENTS
}

HEALTHCARE_VERTICALS = {
    Vertical.DENTAL, Vertical.MEDSPA, Vertical.CHIROPRACTIC
}

PROFESSIONAL_VERTICALS = {
    Vertical.LAW, Vertical.ACCOUNTING, Vertical.REAL_ESTATE
}

HOSPITALITY_VERTICALS = {
    Vertical.RESTAURANT, Vertical.HOTEL, Vertical.TOURISM
}


def get_business_model(vertical: Vertical) -> BusinessModel:
    """Return default business model for a vertical"""
    if vertical in BLUE_COLLAR_VERTICALS:
        return BusinessModel.SERVICE_DELIVERY
    elif vertical in ENTERTAINMENT_VERTICALS or vertical in HOSPITALITY_VERTICALS:
        return BusinessModel.DESTINATION
    elif vertical in HEALTHCARE_VERTICALS:
        return BusinessModel.HYBRID
    else:
        return BusinessModel.DESTINATION  # Default for professional services


class BrandTone(str, Enum):
    """Brand voice tone"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    CASUAL = "casual"


class ServiceDefinedVariables(BaseModel):
    """Factual data for LLM SEO content"""
    time_range: Optional[str] = Field(None, description="e.g., '30 minutes to 2 hours'")
    cost_range: Optional[str] = Field(None, description="e.g., '$75-$300'")
    process_steps: Optional[List[str]] = Field(None, description="Ordered list of steps")
    tools_used: Optional[List[str]] = None
    best_for: Optional[List[str]] = None
    not_suitable_for: Optional[List[str]] = None


class SeasonalRelevance(BaseModel):
    """Seasonal patterns for a service"""
    peak_months: Optional[List[int]] = Field(None, description="Months 1-12")
    triggers: Optional[List[str]] = Field(None, description="Seasonal triggers")


class Service(BaseModel):
    """Service/Product entity - what the client sells"""
    id: str
    name: str = Field(..., description="Service name")
    slug: str = Field(..., description="URL-safe slug")
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=160)
    is_money_service: bool = Field(..., description="Primary revenue driver")
    parent_service_id: Optional[str] = Field(None, description="For sub-services")
    keywords: Optional[List[str]] = Field(None, description="Primary keywords")
    synonyms: Optional[List[str]] = Field(None, description="Alternative terms")
    geo_applicability: GeoScope = Field(GeoScope.LOCAL_RADIUS, description="Geographic scope")
    defined_variables: Optional[ServiceDefinedVariables] = None
    seasonal_relevance: Optional[SeasonalRelevance] = None
    schema_type: str = Field("Service", description="Schema.org type")
    faq_topics: Optional[List[str]] = None


class OperationalConstraints(BaseModel):
    """Business operational constraints"""
    max_travel_radius_miles: Optional[float] = None
    service_hours: Optional[str] = None
    capacity_per_day: Optional[int] = None
    seasonal_factors: Optional[List[str]] = None
    insurance_partnerships: Optional[List[str]] = None
    certifications: Optional[List[str]] = None


class Brand(BaseModel):
    """Brand identity"""
    tagline: Optional[str] = None
    differentiators: Optional[List[str]] = None
    tone: BrandTone = BrandTone.PROFESSIONAL
    colors: Optional[Dict[str, str]] = None
    logo_url: Optional[str] = None


class Contact(BaseModel):
    """Contact information"""
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class GBPProfile(BaseModel):
    """Google Business Profile data"""
    place_id: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = None
    categories: Optional[List[str]] = None


class Client(BaseModel):
    """Client entity - the business being optimized"""
    id: str
    name: str = Field(..., description="Business name")
    domain: Optional[str] = None
    vertical: Vertical
    services: List[Service] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    constraints: Optional[OperationalConstraints] = None
    brand: Optional[Brand] = None
    contact: Optional[Contact] = None
    gbp_profile: Optional[GBPProfile] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def primary_location(self) -> Optional[Location]:
        """Get primary business location"""
        for loc in self.locations:
            if loc.is_primary:
                return loc
        return self.locations[0] if self.locations else None

    @property
    def money_services(self) -> List[Service]:
        """Get primary revenue services"""
        return [s for s in self.services if s.is_money_service]

    def get_service_by_slug(self, slug: str) -> Optional[Service]:
        """Find service by slug"""
        for service in self.services:
            if service.slug == slug:
                return service
        return None

    def get_locations_by_bucket(self, bucket: str) -> List[Location]:
        """Get locations in a geo bucket"""
        return [loc for loc in self.locations if loc.geo_bucket.value == bucket]
