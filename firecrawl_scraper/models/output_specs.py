"""
Output Spec models - Build instructions for Next.js site generation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .geo import GeoTag, GeoBucket


class PageType(str, Enum):
    """Page types for site generation"""
    HOME = "home"
    SERVICE = "service"
    SERVICE_AREA = "service-area"
    PROOF_HUB = "proof-hub"
    GALLERY = "gallery"
    FAQ = "faq"
    BLOG = "blog"
    BLOG_POST = "blog-post"
    ABOUT = "about"
    CONTACT = "contact"
    PRICING = "pricing"
    REVIEWS = "reviews"
    CAREERS = "careers"
    LANDING = "landing"


class ComponentType(str, Enum):
    """Component types"""
    TRUST = "trust"
    CONVERSION = "conversion"
    CONTENT = "content"
    SEO = "seo"
    NAVIGATION = "navigation"
    FOOTER = "footer"
    HERO = "hero"
    GALLERY = "gallery"


class UrgencyLevel(str, Enum):
    """CTA urgency levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============ LLM Answer Block Models ============

class CostRange(BaseModel):
    """Cost/pricing information"""
    range: Optional[str] = None
    average: Optional[str] = None
    variables: List[str] = Field(default_factory=list)
    disclaimers: Optional[str] = None
    comparison_anchor: Optional[str] = None


class FAQ(BaseModel):
    """Single FAQ item"""
    question: str
    answer: str
    follow_up: Optional[str] = None


class VsAlternative(BaseModel):
    """Comparison to alternative service"""
    alternative: str
    comparison: str
    when_to_choose: Optional[str] = None


class QuotableFact(BaseModel):
    """Quotable fact for LLM SEO"""
    fact: str
    source: Optional[str] = None
    cite_as: Optional[str] = None


class LLMAnswerBlock(BaseModel):
    """Unambiguous, quotable, entity-clear content block for LLM SEO"""
    service: str
    service_slug: Optional[str] = None
    geo_context: Optional[GeoTag] = None
    definition: str = Field(..., description="2-sentence 'what it is'")
    entity_statement: Optional[str] = None
    triggers: List[str] = Field(default_factory=list, description="When you need it")
    cost_range: Optional[CostRange] = None
    timeline: Optional[str] = None
    process_steps: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    vs_alternatives: List[VsAlternative] = Field(default_factory=list)
    how_to_choose: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    faqs: List[FAQ] = Field(default_factory=list)
    nap_statement: Optional[str] = None
    local_proof_points: List[str] = Field(default_factory=list)
    schema_data: Optional[Dict[str, Any]] = None
    quotable_facts: List[QuotableFact] = Field(default_factory=list)
    content_hash: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)


# ============ Page Map Models ============

class InternalLink(BaseModel):
    """Internal link specification"""
    anchor: str
    target: str
    placement: Optional[str] = None


class CTARules(BaseModel):
    """CTA rules for a page"""
    primary_cta: Optional[str] = None
    secondary_cta: Optional[str] = None
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM


class PageSpec(BaseModel):
    """Single page specification"""
    route: str
    page_type: PageType
    template: str
    title: Optional[str] = None
    meta_description: Optional[str] = Field(None, max_length=160)
    h1: Optional[str] = None
    geo_target: Optional[GeoTag] = None
    service_target: Optional[str] = None
    components: List[str] = Field(default_factory=list)
    content_requirements: List[str] = Field(default_factory=list)
    schema_types: List[str] = Field(default_factory=list)
    internal_links: List[InternalLink] = Field(default_factory=list)
    cta_rules: Optional[CTARules] = None
    priority: int = Field(10, description="Build priority (1=highest)")
    keyword_targets: List[str] = Field(default_factory=list)
    word_count_target: Optional[int] = None
    llm_answer_block_id: Optional[str] = None


# ============ Component Set Models ============

class ComponentSpec(BaseModel):
    """Reusable component specification"""
    name: str
    type: ComponentType
    description: Optional[str] = None
    required_data: List[str] = Field(default_factory=list)
    placement_rules: Optional[str] = None
    variants: List[str] = Field(default_factory=list)
    props_schema: Optional[Dict[str, Any]] = None


# ============ Internal Linking Models ============

class InternalLinkingRule(BaseModel):
    """Site-wide linking rule"""
    from_page_type: str
    to_page_type: str
    anchor_pattern: Optional[str] = None
    placement: Optional[str] = None
    max_links: Optional[int] = None
    priority: int = 5


# ============ Schema Requirements Models ============

class SchemaRequirement(BaseModel):
    """Structured data requirement"""
    page_type: str
    schema_types: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)
    template: Optional[Dict[str, Any]] = None


# ============ Content Calendar Models ============

class ContentCalendarItem(BaseModel):
    """Blog/content publication item"""
    title: str
    topic: Optional[str] = None
    target_keyword: Optional[str] = None
    publish_date: Optional[str] = None
    content_type: Optional[str] = None
    word_count_target: Optional[int] = None


# ============ Backlink Target Models ============

class BacklinkTarget(BaseModel):
    """Backlink acquisition target"""
    domain: str
    type: Optional[str] = None
    priority: Optional[str] = None
    approach: Optional[str] = None
    status: Optional[str] = None


# ============ Site Config Models ============

class SiteConfig(BaseModel):
    """Global site configuration"""
    domain: Optional[str] = None
    site_name: Optional[str] = None
    tagline: Optional[str] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None
    address: Optional[str] = None
    service_area_text: Optional[str] = None
    business_hours: Optional[str] = None
    gtm_id: Optional[str] = None
    ga4_id: Optional[str] = None


# ============ Metrics Targets Models ============

class MetricsTargets(BaseModel):
    """Success metrics"""
    organic_traffic_target: Optional[int] = None
    conversion_rate_target: Optional[float] = None
    ranking_targets: Dict[str, int] = Field(default_factory=dict)
    backlink_target: Optional[int] = None
    authority_target: Optional[int] = None


# ============ Main Output Spec ============

class OutputSpec(BaseModel):
    """Direct build instructions for Next.js site generation"""
    client_id: str
    client_name: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"

    site_config: Optional[SiteConfig] = None
    page_map: List[PageSpec] = Field(default_factory=list)
    component_set: List[ComponentSpec] = Field(default_factory=list)
    internal_linking_rules: List[InternalLinkingRule] = Field(default_factory=list)
    schema_requirements: List[SchemaRequirement] = Field(default_factory=list)
    llm_answer_blocks: List[LLMAnswerBlock] = Field(default_factory=list)
    content_calendar: List[ContentCalendarItem] = Field(default_factory=list)
    backlink_targets: List[BacklinkTarget] = Field(default_factory=list)
    insights_applied: List[str] = Field(default_factory=list)
    metrics_targets: Optional[MetricsTargets] = None

    @property
    def total_pages(self) -> int:
        return len(self.page_map)

    @property
    def service_pages(self) -> List[PageSpec]:
        return [p for p in self.page_map if p.page_type == PageType.SERVICE]

    @property
    def service_area_pages(self) -> List[PageSpec]:
        return [p for p in self.page_map if p.page_type == PageType.SERVICE_AREA]

    def get_pages_by_type(self, page_type: PageType) -> List[PageSpec]:
        return [p for p in self.page_map if p.page_type == page_type]

    def get_page_by_route(self, route: str) -> Optional[PageSpec]:
        for page in self.page_map:
            if page.route == route:
                return page
        return None


# ============ Intent/Geo Matrix Models ============

class MatrixRow(BaseModel):
    """Service row in matrix"""
    service_id: str
    service_name: str
    is_money_service: bool = True
    priority: int = 1


class MatrixColumn(BaseModel):
    """Geo bucket column in matrix"""
    geo_bucket: GeoBucket
    label: str
    locations: List[str] = Field(default_factory=list)
    priority: int = 1


class PageStrategy(str, Enum):
    """Page creation strategy for matrix cell"""
    DEDICATED = "dedicated"
    MERGED = "merged"
    SECTION = "section"
    NONE = "none"


class MatrixCTARules(BaseModel):
    """CTA rules for matrix cell"""
    primary: Optional[str] = None
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    phone_prominent: bool = True


class MatrixCell(BaseModel):
    """Single cell in Intent/Geo Matrix"""
    service_id: str
    geo_bucket: str
    page_strategy: PageStrategy = PageStrategy.DEDICATED
    page_type: Optional[str] = None
    merge_with: Optional[str] = None
    keyword_cluster: List[str] = Field(default_factory=list)
    search_volume: Optional[Dict[str, int]] = None
    competition_level: Optional[str] = None
    current_rank: Optional[float] = None
    target_rank: Optional[int] = None
    proof_requirements: List[str] = Field(default_factory=list)
    cta_rules: Optional[MatrixCTARules] = None
    schema_types: List[str] = Field(default_factory=list)
    content_notes: Optional[str] = None
    priority_score: float = Field(50, ge=0, le=100)


class MatrixSummary(BaseModel):
    """Summary statistics for matrix"""
    total_pages_needed: int = 0
    service_pages: int = 0
    service_area_pages: int = 0
    merged_pages: int = 0
    blog_content_needed: int = 0
    total_keywords: int = 0
    total_search_volume: int = 0


class IntentGeoMatrix(BaseModel):
    """Service x Geo matrix artifact"""
    client_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    rows: List[MatrixRow] = Field(default_factory=list)
    columns: List[MatrixColumn] = Field(default_factory=list)
    cells: List[MatrixCell] = Field(default_factory=list)
    summary: Optional[MatrixSummary] = None

    def get_cell(self, service_id: str, geo_bucket: str) -> Optional[MatrixCell]:
        """Get cell by service and geo bucket"""
        for cell in self.cells:
            if cell.service_id == service_id and cell.geo_bucket == geo_bucket:
                return cell
        return None

    def get_cells_by_service(self, service_id: str) -> List[MatrixCell]:
        """Get all cells for a service"""
        return [c for c in self.cells if c.service_id == service_id]

    def get_cells_by_geo(self, geo_bucket: str) -> List[MatrixCell]:
        """Get all cells for a geo bucket"""
        return [c for c in self.cells if c.geo_bucket == geo_bucket]

    def calculate_summary(self):
        """Calculate summary statistics"""
        self.summary = MatrixSummary(
            total_pages_needed=sum(1 for c in self.cells if c.page_strategy == PageStrategy.DEDICATED),
            service_pages=sum(1 for c in self.cells if c.page_type == "service"),
            service_area_pages=sum(1 for c in self.cells if c.page_type == "service-area"),
            merged_pages=sum(1 for c in self.cells if c.page_strategy == PageStrategy.MERGED),
            blog_content_needed=sum(1 for c in self.cells if c.page_type == "blog"),
            total_keywords=sum(len(c.keyword_cluster) for c in self.cells),
            total_search_volume=sum(
                (c.search_volume or {}).get('total', 0) for c in self.cells
            )
        )
