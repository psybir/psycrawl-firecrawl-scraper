"""
Competitor Profile models - Structured competitor analysis
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .geo import GeoTag
from .sources import Source


class PhotoType(str, Enum):
    """Photo authenticity types"""
    REAL = "real"
    STOCK = "stock"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class ReviewRecency(str, Enum):
    """Review freshness"""
    RECENT = "recent"    # < 30 days
    STALE = "stale"      # > 30 days
    UNKNOWN = "unknown"


class PriceTransparency(str, Enum):
    """Price transparency levels"""
    NONE = "none"
    RANGES = "ranges"
    CALCULATOR = "calculator"
    EXACT = "exact"


class ContentFreshness(str, Enum):
    """Content freshness levels"""
    FRESH = "fresh"      # Updated within 90 days
    MODERATE = "moderate"  # 90-180 days
    STALE = "stale"      # > 180 days


class ThreatLevel(str, Enum):
    """Competitive threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrustSignals(BaseModel):
    """Trust indicators found on competitor site - universal + vertical-specific"""
    # Universal signals
    review_count: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_recency: ReviewRecency = ReviewRecency.UNKNOWN
    review_sources: Optional[List[str]] = None
    years_in_business: Optional[int] = None
    real_photos_vs_stock: PhotoType = PhotoType.UNKNOWN
    team_photos: bool = False
    team_bios: bool = False
    owner_visible: bool = False
    video_content: bool = False
    video_count: Optional[int] = None
    badges_associations: List[str] = Field(default_factory=list)
    trust_score: Optional[float] = Field(None, ge=0, le=100)

    # Blue Collar / Service Trades specific
    licenses_shown: bool = False
    licenses_location: Optional[str] = None
    insurance_shown: bool = False
    insurance_details: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)
    warranty_guarantee_language: Optional[str] = None
    warranty_duration: Optional[str] = None
    truck_photos: bool = False
    job_photos: bool = False
    before_after_gallery: bool = False
    gallery_count: Optional[int] = None
    manufacturer_partnerships: List[str] = Field(default_factory=list)

    # Entertainment / Experience specific
    experience_photos: bool = False           # Room/venue photos
    experience_photo_count: Optional[int] = None
    promo_video: bool = False                 # Trailer/preview video
    immersion_indicators: List[str] = Field(default_factory=list)  # "Award-winning", "Custom-built"
    awards_shown: List[str] = Field(default_factory=list)          # Industry awards
    press_mentions: List[str] = Field(default_factory=list)        # Media coverage
    unique_features: List[str] = Field(default_factory=list)       # Differentiators (AI, multiple endings)
    experience_count: Optional[int] = None    # Number of rooms/experiences

    # Healthcare specific
    credentials_shown: List[str] = Field(default_factory=list)
    board_certifications: List[str] = Field(default_factory=list)
    patient_testimonials: bool = False
    hipaa_compliant: bool = False

    def calculate_trust_score(self, vertical: str = None) -> float:
        """Calculate trust score based on signals - vertical-aware weighting"""
        score = 0

        # Universal weights (applies to all)
        universal_weights = {
            'review_count': min((self.review_count or 0) / 10, 10),  # up to 10 points
            'rating': ((self.rating or 0) - 3) * 10 if self.rating and self.rating > 3 else 0,  # up to 20 points
            'real_photos': 10 if self.real_photos_vs_stock == PhotoType.REAL else 0,
            'team': 5 if self.team_photos else 0,
            'video': 5 if self.video_content else 0,
            'badges': min(len(self.badges_associations) * 2, 10),
        }

        # Vertical-specific weights
        if vertical in ('pdr', 'plumbing', 'hvac', 'roofing', 'auto_body', 'landscaping', 'electrical'):
            # Blue collar weights
            vertical_weights = {
                'licenses': 10 if self.licenses_shown else 0,
                'insurance': 5 if self.insurance_shown else 0,
                'certifications': min(len(self.certifications) * 3, 15),
                'warranty': 5 if self.warranty_guarantee_language else 0,
                'gallery': 10 if self.before_after_gallery else 0,
            }
        elif vertical in ('escape_room', 'entertainment_venue', 'amusement', 'events'):
            # Entertainment weights
            vertical_weights = {
                'experience_photos': 10 if self.experience_photos else 0,
                'promo_video': 10 if self.promo_video else 0,
                'awards': min(len(self.awards_shown) * 5, 15),
                'press': min(len(self.press_mentions) * 3, 10),
                'unique_features': min(len(self.unique_features) * 3, 15),
                'immersion': min(len(self.immersion_indicators) * 2, 10),
            }
        elif vertical in ('dental', 'medspa', 'chiropractic'):
            # Healthcare weights
            vertical_weights = {
                'credentials': min(len(self.credentials_shown) * 3, 15),
                'certifications': min(len(self.board_certifications) * 5, 15),
                'testimonials': 10 if self.patient_testimonials else 0,
            }
        else:
            # Default weights (professional services, hospitality)
            vertical_weights = {
                'experience_photos': 5 if self.experience_photos else 0,
                'awards': min(len(self.awards_shown) * 3, 10),
            }

        score = min(sum(universal_weights.values()) + sum(vertical_weights.values()), 100)
        self.trust_score = score
        return score


class ConversionMechanics(BaseModel):
    """Conversion optimization elements - universal + vertical-specific"""
    # Universal conversion elements
    phone_visible: bool = False
    phone_clickable: bool = False
    sticky_header: bool = False
    sticky_cta: bool = False
    form_present: bool = False
    form_length: Optional[int] = None
    form_friction_score: Optional[float] = Field(None, ge=0, le=1)
    chat_widget: bool = False
    chat_provider: Optional[str] = None
    price_transparency: PriceTransparency = PriceTransparency.NONE
    what_happens_next_clarity: bool = False
    multiple_cta_types: bool = False
    cta_types: List[str] = Field(default_factory=list)
    conversion_score: Optional[float] = Field(None, ge=0, le=100)

    # Blue Collar / Service specific
    sticky_call: bool = False
    emergency_language: bool = False
    emergency_supported_by_copy: bool = False
    financing_shown: bool = False
    financing_providers: List[str] = Field(default_factory=list)
    price_anchors: bool = False
    free_quote_language: bool = False

    # Entertainment / Experience specific
    online_booking: bool = False              # Direct booking system
    booking_provider: Optional[str] = None    # FareHarbor, Bookeo, etc.
    availability_calendar: bool = False       # Real-time availability
    group_booking_options: bool = False       # Private room, party packages
    party_packages: bool = False              # Birthday/event packages
    corporate_booking: bool = False           # Team building packages
    gift_cards: bool = False                  # Gift card purchase option
    waiver_online: bool = False               # Online waiver signing
    experience_urgency: bool = False          # "Only 2 spots left!"

    # Healthcare specific
    online_scheduling: bool = False           # Appointment booking
    insurance_checker: bool = False           # Check insurance coverage
    patient_portal: bool = False              # Patient portal access
    telehealth_option: bool = False           # Virtual consultations

    def calculate_conversion_score(self, vertical: str = None) -> float:
        """Calculate conversion optimization score - vertical-aware"""
        score = 0

        # Universal conversion factors
        if self.phone_visible:
            score += 5
        if self.phone_clickable:
            score += 5
        if self.sticky_cta:
            score += 10
        if self.form_present:
            score += 5
            if self.form_friction_score is not None:
                score += (1 - self.form_friction_score) * 10
        if self.chat_widget:
            score += 5
        if self.what_happens_next_clarity:
            score += 10
        if self.price_transparency != PriceTransparency.NONE:
            score += 5

        # Vertical-specific scoring
        if vertical in ('pdr', 'plumbing', 'hvac', 'roofing', 'auto_body', 'landscaping', 'electrical'):
            # Blue collar - emergency and financing matter
            if self.sticky_call:
                score += 10
            if self.emergency_language:
                score += 10
            if self.financing_shown:
                score += 5
            if self.free_quote_language:
                score += 5

        elif vertical in ('escape_room', 'entertainment_venue', 'amusement', 'events'):
            # Entertainment - booking and packages matter
            if self.online_booking:
                score += 15
            if self.availability_calendar:
                score += 10
            if self.group_booking_options:
                score += 5
            if self.party_packages:
                score += 5
            if self.corporate_booking:
                score += 5
            if self.gift_cards:
                score += 5
            if self.experience_urgency:
                score += 5

        elif vertical in ('dental', 'medspa', 'chiropractic'):
            # Healthcare - scheduling and portals matter
            if self.online_scheduling:
                score += 15
            if self.insurance_checker:
                score += 10
            if self.patient_portal:
                score += 5
            if self.telehealth_option:
                score += 5

        self.conversion_score = min(score, 100)
        return self.conversion_score


class ServicePage(BaseModel):
    """Service page info"""
    url: str
    service: str
    word_count: Optional[int] = None


class ServiceAreaPage(BaseModel):
    """Service area page info"""
    url: str
    location: str


class SEOStructure(BaseModel):
    """Site structure and SEO elements"""
    page_count: Optional[int] = None
    page_types_present: List[str] = Field(default_factory=list)
    service_pages: List[ServicePage] = Field(default_factory=list)
    service_area_pages: List[ServiceAreaPage] = Field(default_factory=list)
    internal_linking_score: Optional[float] = Field(None, ge=0, le=1)
    internal_linking_patterns: Optional[str] = None
    nav_structure: Optional[str] = None
    breadcrumbs: bool = False
    headings_intent_match: Optional[float] = Field(None, ge=0, le=1)
    schema_markup: Dict[str, List[str]] = Field(default_factory=dict)
    blog_active: bool = False
    blog_frequency: Optional[str] = None
    last_blog_post: Optional[str] = None
    content_freshness: ContentFreshness = ContentFreshness.STALE


class TechnicalSEO(BaseModel):
    """Technical SEO metrics"""
    mobile_friendly: bool = False
    page_speed_score: Optional[int] = Field(None, ge=0, le=100)
    core_web_vitals: Optional[Dict[str, float]] = None
    ssl: bool = False
    sitemap: bool = False
    robots_txt: bool = False


class BacklinkProfile(BaseModel):
    """Backlink data"""
    total_backlinks: Optional[int] = None
    referring_domains: Optional[int] = None
    domain_authority: Optional[int] = Field(None, ge=0, le=100)
    authority_score: Optional[int] = Field(None, ge=0, le=100)
    top_backlinks: List[Dict[str, Any]] = Field(default_factory=list)


class SocialPresence(BaseModel):
    """Social media presence"""
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None
    tiktok: Optional[str] = None
    activity_level: Optional[str] = None  # active, moderate, inactive, none


class CompetitorProfile(BaseModel):
    """Structured competitor profile - not vibes, structured analysis"""
    id: str
    domain: str
    name: str
    url: Optional[str] = None
    sources_scraped: List[Source] = Field(default_factory=list)
    geo_tags: List[GeoTag] = Field(default_factory=list)
    services_offered: List[str] = Field(default_factory=list)

    trust_signals: TrustSignals = Field(default_factory=TrustSignals)
    conversion_mechanics: ConversionMechanics = Field(default_factory=ConversionMechanics)
    seo_structure: SEOStructure = Field(default_factory=SEOStructure)
    technical_seo: TechnicalSEO = Field(default_factory=TechnicalSEO)
    grid_performance: Dict[str, float] = Field(default_factory=dict)
    backlinks: BacklinkProfile = Field(default_factory=BacklinkProfile)
    social_presence: SocialPresence = Field(default_factory=SocialPresence)

    overall_threat_level: ThreatLevel = ThreatLevel.MEDIUM
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

    analyzed_at: datetime = Field(default_factory=datetime.now)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)

    def calculate_threat_level(self) -> ThreatLevel:
        """Calculate overall threat level based on metrics"""
        score = 0

        # Trust score contribution
        if self.trust_signals.trust_score:
            score += self.trust_signals.trust_score * 0.3

        # Conversion score contribution
        if self.conversion_mechanics.conversion_score:
            score += self.conversion_mechanics.conversion_score * 0.2

        # Backlinks contribution
        if self.backlinks.domain_authority:
            score += self.backlinks.domain_authority * 0.3

        # Grid performance contribution (lower = better for them = higher threat)
        avg_rank = sum(self.grid_performance.values()) / len(self.grid_performance) if self.grid_performance else 10
        grid_score = max(0, 100 - (avg_rank - 1) * 10)
        score += grid_score * 0.2

        if score >= 70:
            self.overall_threat_level = ThreatLevel.CRITICAL
        elif score >= 50:
            self.overall_threat_level = ThreatLevel.HIGH
        elif score >= 30:
            self.overall_threat_level = ThreatLevel.MEDIUM
        else:
            self.overall_threat_level = ThreatLevel.LOW

        return self.overall_threat_level
