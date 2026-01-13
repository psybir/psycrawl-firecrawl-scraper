"""
Firecrawl Scraper Models

Pydantic data models for SEO analysis and reporting.
"""

from .seo_models import (
    # Base models
    SEOScore,

    # SERP models
    SERPResult,
    SERPRankingData,

    # Keyword models
    KeywordData,
    KeywordMetrics,
    KeywordIdea,

    # Backlink models
    BacklinkData,
    BacklinksSummary,
    ReferringDomain,

    # OnPage models
    OnPageIssue,
    OnPageSummary,
    OnPageResult,

    # Competitor models
    CompetitorData,
    CompetitorAnalysis,

    # Comprehensive reports
    SEOReport,
    ContentAnalysis,
    TechnicalSEO,
    SEORecommendation,
)

__all__ = [
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
]
