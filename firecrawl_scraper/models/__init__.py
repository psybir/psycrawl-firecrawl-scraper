"""
Firecrawl Scraper Models

Pydantic data models for SEO analysis, competitor research, and site generation.
"""

# Original SEO models
from .seo_models import (
    SEOScore,
    SERPResult,
    SERPRankingData,
    KeywordData,
    KeywordMetrics,
    KeywordIdea,
    BacklinkData,
    BacklinksSummary,
    ReferringDomain,
    OnPageIssue,
    OnPageSummary,
    OnPageResult,
    CompetitorData,
    CompetitorAnalysis,
    SEOReport,
    ContentAnalysis,
    TechnicalSEO,
    SEORecommendation,
)

# Geo models
from .geo import (
    GeoScope,
    GeoBucket,
    Coordinates,
    GeoTag,
    Location,
)

# Core entities
from .entities import (
    Vertical,
    BusinessModel,
    BrandTone,
    ServiceDefinedVariables,
    SeasonalRelevance,
    Service,
    OperationalConstraints,
    Brand,
    Contact,
    GBPProfile,
    Client,
    # Vertical classification helpers
    BLUE_COLLAR_VERTICALS,
    ENTERTAINMENT_VERTICALS,
    HEALTHCARE_VERTICALS,
    PROFESSIONAL_VERTICALS,
    HOSPITALITY_VERTICALS,
    get_business_model,
)

# Source models
from .sources import (
    SourceType,
    ScrapeStatus,
    DataFreshness,
    SERPFeature,
    Source,
    SERPData,
)

# Competitor profile models
from .competitor_profile import (
    PhotoType,
    ReviewRecency,
    PriceTransparency,
    ContentFreshness,
    ThreatLevel,
    TrustSignals,
    ConversionMechanics,
    ServicePage,
    ServiceAreaPage,
    SEOStructure,
    TechnicalSEO as CompetitorTechnicalSEO,
    BacklinkProfile,
    SocialPresence,
    CompetitorProfile,
)

# Finding models
from .findings import (
    FindingType,
    FindingCategory,
    Severity,
    DataPoints,
    Finding,
    FindingGroup,
    FindingsReport,
)

# Insight models
from .insights import (
    ImpactLevel,
    EffortLevel,
    InsightType,
    InsightStatus,
    Evidence,
    ExpectedImpact,
    SpecDetails,
    ActionableInsight,
    InsightReport,
)

# Output spec models
from .output_specs import (
    PageType,
    ComponentType,
    UrgencyLevel,
    CostRange,
    FAQ,
    VsAlternative,
    QuotableFact,
    LLMAnswerBlock,
    InternalLink,
    CTARules,
    PageSpec,
    ComponentSpec,
    InternalLinkingRule,
    SchemaRequirement,
    ContentCalendarItem,
    BacklinkTarget,
    SiteConfig,
    MetricsTargets,
    OutputSpec,
    MatrixRow,
    MatrixColumn,
    PageStrategy,
    MatrixCTARules,
    MatrixCell,
    MatrixSummary,
    IntentGeoMatrix,
)

__all__ = [
    # Original SEO models
    'SEOScore',
    'SERPResult',
    'SERPRankingData',
    'KeywordData',
    'KeywordMetrics',
    'KeywordIdea',
    'BacklinkData',
    'BacklinksSummary',
    'ReferringDomain',
    'OnPageIssue',
    'OnPageSummary',
    'OnPageResult',
    'CompetitorData',
    'CompetitorAnalysis',
    'SEOReport',
    'ContentAnalysis',
    'TechnicalSEO',
    'SEORecommendation',
    # Geo models
    'GeoScope',
    'GeoBucket',
    'Coordinates',
    'GeoTag',
    'Location',
    # Core entities
    'Vertical',
    'BusinessModel',
    'BrandTone',
    'ServiceDefinedVariables',
    'SeasonalRelevance',
    'Service',
    'OperationalConstraints',
    'Brand',
    'Contact',
    'GBPProfile',
    'Client',
    # Vertical classification helpers
    'BLUE_COLLAR_VERTICALS',
    'ENTERTAINMENT_VERTICALS',
    'HEALTHCARE_VERTICALS',
    'PROFESSIONAL_VERTICALS',
    'HOSPITALITY_VERTICALS',
    'get_business_model',
    # Source models
    'SourceType',
    'ScrapeStatus',
    'DataFreshness',
    'SERPFeature',
    'Source',
    'SERPData',
    # Competitor profile models
    'PhotoType',
    'ReviewRecency',
    'PriceTransparency',
    'ContentFreshness',
    'ThreatLevel',
    'TrustSignals',
    'ConversionMechanics',
    'ServicePage',
    'ServiceAreaPage',
    'SEOStructure',
    'CompetitorTechnicalSEO',
    'BacklinkProfile',
    'SocialPresence',
    'CompetitorProfile',
    # Finding models
    'FindingType',
    'FindingCategory',
    'Severity',
    'DataPoints',
    'Finding',
    'FindingGroup',
    'FindingsReport',
    # Insight models
    'ImpactLevel',
    'EffortLevel',
    'InsightType',
    'InsightStatus',
    'Evidence',
    'ExpectedImpact',
    'SpecDetails',
    'ActionableInsight',
    'InsightReport',
    # Output spec models
    'PageType',
    'ComponentType',
    'UrgencyLevel',
    'CostRange',
    'FAQ',
    'VsAlternative',
    'QuotableFact',
    'LLMAnswerBlock',
    'InternalLink',
    'CTARules',
    'PageSpec',
    'ComponentSpec',
    'InternalLinkingRule',
    'SchemaRequirement',
    'ContentCalendarItem',
    'BacklinkTarget',
    'SiteConfig',
    'MetricsTargets',
    'OutputSpec',
    'MatrixRow',
    'MatrixColumn',
    'PageStrategy',
    'MatrixCTARules',
    'MatrixCell',
    'MatrixSummary',
    'IntentGeoMatrix',
]
