"""
SEO Data Models - Pydantic models for SEO analysis

Comprehensive data models for:
- SERP rankings and results
- Keyword research and metrics
- Backlink analysis
- On-page technical SEO
- Competitor analysis
- Full SEO reports

Usage:
    from firecrawl_scraper.models import SEOReport, KeywordData, BacklinksSummary

    report = SEOReport(
        domain="example.com",
        seo_score=SEOScore(overall=78, technical=85, content=72, authority=77)
    )
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


# ========== Enums ==========

class IssueSeverity(str, Enum):
    """Severity levels for SEO issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Categories for SEO issues"""
    TECHNICAL = "technical"
    CONTENT = "content"
    PERFORMANCE = "performance"
    MOBILE = "mobile"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    INDEXING = "indexing"


class DeviceType(str, Enum):
    """Device types for SERP queries"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


# ========== Base Models ==========

class SEOScore(BaseModel):
    """SEO score breakdown"""
    overall: int = Field(ge=0, le=100, description="Overall SEO score 0-100")
    technical: Optional[int] = Field(None, ge=0, le=100, description="Technical SEO score")
    content: Optional[int] = Field(None, ge=0, le=100, description="Content quality score")
    authority: Optional[int] = Field(None, ge=0, le=100, description="Domain authority score")
    performance: Optional[int] = Field(None, ge=0, le=100, description="Performance score")

    def to_grade(self) -> str:
        """Convert overall score to letter grade"""
        if self.overall >= 90:
            return "A"
        elif self.overall >= 80:
            return "B"
        elif self.overall >= 70:
            return "C"
        elif self.overall >= 60:
            return "D"
        else:
            return "F"


# ========== SERP Models ==========

class SERPResult(BaseModel):
    """Single SERP result item"""
    position: int = Field(..., description="Ranking position (1-100)")
    url: str = Field(..., description="Result URL")
    title: str = Field(..., description="Result title")
    description: Optional[str] = Field(None, description="Meta description")
    domain: str = Field(..., description="Domain name")
    is_featured_snippet: bool = Field(False, description="Is this a featured snippet")
    is_local_pack: bool = Field(False, description="Is this in local pack")
    is_knowledge_panel: bool = Field(False, description="Is this knowledge panel")
    breadcrumb: Optional[str] = Field(None, description="Breadcrumb trail")
    cached_url: Optional[str] = Field(None, description="Google cached URL")
    related_search_queries: Optional[List[str]] = Field(None, description="Related searches")


class SERPRankingData(BaseModel):
    """SERP ranking data for a keyword"""
    keyword: str = Field(..., description="Target keyword")
    search_volume: Optional[int] = Field(None, description="Monthly search volume")
    location: str = Field(..., description="Search location")
    language: str = Field(..., description="Search language")
    device: DeviceType = Field(DeviceType.DESKTOP, description="Device type")
    results_count: int = Field(..., description="Total results in SERP")
    se_type: str = Field("google", description="Search engine type")

    # Rankings
    our_position: Optional[int] = Field(None, description="Our domain's position")
    results: List[SERPResult] = Field(default_factory=list, description="Top SERP results")

    # Features
    has_featured_snippet: bool = Field(False)
    has_local_pack: bool = Field(False)
    has_knowledge_panel: bool = Field(False)
    has_people_also_ask: bool = Field(False)
    has_video_results: bool = Field(False)
    has_image_results: bool = Field(False)

    # Metadata
    checked_at: datetime = Field(default_factory=datetime.now)
    cost: float = Field(0.0, description="API cost for this query")


# ========== Keyword Models ==========

class KeywordMetrics(BaseModel):
    """Keyword metrics from Google Ads / DataForSEO"""
    search_volume: int = Field(..., description="Monthly search volume")
    cpc: Optional[float] = Field(None, description="Cost per click in USD")
    competition: Optional[float] = Field(None, ge=0, le=1, description="Competition level 0-1")
    competition_level: Optional[str] = Field(None, description="LOW, MEDIUM, HIGH")
    low_top_of_page_bid: Optional[float] = Field(None, description="Low bid for top of page")
    high_top_of_page_bid: Optional[float] = Field(None, description="High bid for top of page")


class KeywordData(BaseModel):
    """Complete keyword data"""
    keyword: str = Field(..., description="The keyword")
    metrics: Optional[KeywordMetrics] = Field(None, description="Keyword metrics")
    location_code: int = Field(2840, description="Location code")
    language_code: str = Field("en", description="Language code")

    # Trend data
    monthly_searches: Optional[List[Dict[str, Any]]] = Field(
        None, description="Monthly search volume trend"
    )

    # SERP features
    serp_info: Optional[Dict[str, Any]] = Field(None, description="SERP feature info")

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)


class KeywordIdea(BaseModel):
    """Keyword idea from research"""
    keyword: str = Field(..., description="Suggested keyword")
    search_volume: int = Field(..., description="Monthly search volume")
    cpc: Optional[float] = Field(None, description="Cost per click")
    competition: Optional[float] = Field(None, description="Competition level")
    keyword_difficulty: Optional[int] = Field(None, ge=0, le=100, description="KD score 0-100")
    relevance: Optional[float] = Field(None, description="Relevance to seed keyword")
    intent: Optional[str] = Field(None, description="Search intent: informational, transactional, etc.")


# ========== Backlink Models ==========

class BacklinkData(BaseModel):
    """Single backlink data"""
    url_from: str = Field(..., description="Source URL")
    url_to: str = Field(..., description="Target URL")
    domain_from: str = Field(..., description="Source domain")
    anchor: Optional[str] = Field(None, description="Anchor text")
    is_dofollow: bool = Field(True, description="Is dofollow link")
    is_new: bool = Field(False, description="Is new backlink")
    is_lost: bool = Field(False, description="Is lost backlink")
    page_from_rank: Optional[int] = Field(None, description="Source page rank")
    domain_from_rank: Optional[int] = Field(None, description="Source domain rank")
    first_seen: Optional[datetime] = Field(None, description="First seen date")
    last_seen: Optional[datetime] = Field(None, description="Last seen date")
    link_type: Optional[str] = Field(None, description="Link type: anchor, image, redirect, etc.")
    link_attribute: Optional[List[str]] = Field(None, description="Link attributes: nofollow, sponsored, etc.")


class ReferringDomain(BaseModel):
    """Referring domain data"""
    domain: str = Field(..., description="Referring domain")
    rank: Optional[int] = Field(None, description="Domain rank")
    backlinks_count: int = Field(..., description="Number of backlinks from this domain")
    dofollow_backlinks: int = Field(0, description="Dofollow backlinks count")
    first_seen: Optional[datetime] = Field(None, description="First seen date")
    broken_pages: int = Field(0, description="Broken pages count")


class BacklinksSummary(BaseModel):
    """Backlinks summary for a domain"""
    target: str = Field(..., description="Target domain/URL")

    # Counts
    total_backlinks: int = Field(0, description="Total backlinks count")
    referring_domains: int = Field(0, description="Unique referring domains")
    referring_main_domains: int = Field(0, description="Main referring domains")
    referring_ips: int = Field(0, description="Unique referring IPs")
    referring_subnets: int = Field(0, description="Unique referring subnets")

    # Link types
    dofollow_backlinks: int = Field(0, description="Dofollow backlinks")
    nofollow_backlinks: int = Field(0, description="Nofollow backlinks")
    sponsored_backlinks: int = Field(0, description="Sponsored links")
    ugc_backlinks: int = Field(0, description="UGC links")

    # Ranks
    domain_rank: Optional[int] = Field(None, description="Domain rank score")
    page_rank: Optional[int] = Field(None, description="Page rank score")

    # New/Lost
    new_backlinks: int = Field(0, description="New backlinks (last 30 days)")
    lost_backlinks: int = Field(0, description="Lost backlinks (last 30 days)")
    new_referring_domains: int = Field(0, description="New referring domains")
    lost_referring_domains: int = Field(0, description="Lost referring domains")

    # Metrics
    dofollow_ratio: float = Field(0.0, description="Dofollow/total ratio")
    backlinks_spam_score: Optional[float] = Field(None, description="Spam score")

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)
    cost: float = Field(0.0, description="API cost")


# ========== OnPage Models ==========

class OnPageIssue(BaseModel):
    """Single on-page SEO issue"""
    issue_type: str = Field(..., description="Type of issue")
    severity: IssueSeverity = Field(..., description="Issue severity")
    category: IssueCategory = Field(..., description="Issue category")
    pages_affected: int = Field(1, description="Number of pages affected")
    description: str = Field(..., description="Issue description")
    recommendation: str = Field(..., description="How to fix")
    affected_urls: Optional[List[str]] = Field(None, description="Sample affected URLs")


class OnPageSummary(BaseModel):
    """On-page crawl summary"""
    target: str = Field(..., description="Crawled domain/URL")
    pages_crawled: int = Field(0, description="Total pages crawled")
    pages_in_queue: int = Field(0, description="Pages remaining in queue")

    # Counts by status
    pages_with_errors: int = Field(0, description="Pages with errors")
    pages_with_warnings: int = Field(0, description="Pages with warnings")
    pages_with_duplicates: int = Field(0, description="Duplicate content pages")
    pages_with_redirects: int = Field(0, description="Redirected pages")
    pages_blocked: int = Field(0, description="Blocked pages")

    # HTTP status codes
    status_2xx: int = Field(0, description="2xx responses")
    status_3xx: int = Field(0, description="3xx responses")
    status_4xx: int = Field(0, description="4xx responses")
    status_5xx: int = Field(0, description="5xx responses")

    # Resources
    total_links: int = Field(0, description="Total links found")
    internal_links: int = Field(0, description="Internal links")
    external_links: int = Field(0, description="External links")
    broken_links: int = Field(0, description="Broken links")
    images_count: int = Field(0, description="Total images")
    images_without_alt: int = Field(0, description="Images missing alt text")

    # Performance metrics
    avg_load_time: Optional[float] = Field(None, description="Average page load time (ms)")
    avg_page_size: Optional[int] = Field(None, description="Average page size (bytes)")

    # Metadata
    crawl_started: Optional[datetime] = Field(None)
    crawl_completed: Optional[datetime] = Field(None)


class OnPageResult(BaseModel):
    """Complete on-page SEO analysis result"""
    target: str = Field(..., description="Analyzed domain")
    task_id: str = Field(..., description="DataForSEO task ID")
    summary: OnPageSummary = Field(..., description="Crawl summary")
    issues: List[OnPageIssue] = Field(default_factory=list, description="Issues found")
    score: int = Field(ge=0, le=100, description="On-page SEO score")

    # Pages data
    pages: Optional[List[Dict[str, Any]]] = Field(None, description="Individual page data")

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)
    cost: float = Field(0.0, description="Total API cost")


# ========== Competitor Models ==========

class CompetitorData(BaseModel):
    """Single competitor data"""
    domain: str = Field(..., description="Competitor domain")
    rank: Optional[int] = Field(None, description="Domain rank")
    organic_traffic: Optional[int] = Field(None, description="Estimated organic traffic")
    organic_keywords: Optional[int] = Field(None, description="Number of ranking keywords")
    backlinks: Optional[int] = Field(None, description="Total backlinks")
    referring_domains: Optional[int] = Field(None, description="Referring domains")
    common_keywords: int = Field(0, description="Keywords in common with target")
    keyword_intersection: Optional[float] = Field(None, description="Keyword overlap %")


class CompetitorAnalysis(BaseModel):
    """Competitor analysis result"""
    target: str = Field(..., description="Target domain being analyzed")
    competitors: List[CompetitorData] = Field(..., description="Competitor data")

    # Gap analysis
    keyword_gaps: Optional[List[KeywordData]] = Field(None, description="Keywords competitors rank for")
    backlink_gaps: Optional[List[ReferringDomain]] = Field(None, description="Domains linking to competitors")

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)


# ========== Comprehensive Report Models ==========

class ContentAnalysis(BaseModel):
    """Content analysis from Firecrawl scraping"""
    pages_scraped: int = Field(0, description="Total pages scraped")
    total_words: int = Field(0, description="Total word count")
    avg_word_count: float = Field(0.0, description="Average words per page")
    total_chars: int = Field(0, description="Total character count")
    avg_reading_time: float = Field(0.0, description="Average reading time (minutes)")

    # Quality metrics
    pages_with_thin_content: int = Field(0, description="Pages under 300 words")
    pages_with_duplicate_content: int = Field(0, description="Duplicate content pages")

    # Structure
    pages_with_h1: int = Field(0, description="Pages with H1 tag")
    pages_with_meta_description: int = Field(0, description="Pages with meta description")
    pages_with_images: int = Field(0, description="Pages with images")

    # Top pages
    top_pages: Optional[List[Dict[str, Any]]] = Field(None, description="Top performing pages")


class TechnicalSEO(BaseModel):
    """Technical SEO analysis"""
    score: int = Field(ge=0, le=100, description="Technical SEO score")

    # Core Web Vitals (if available)
    lcp: Optional[float] = Field(None, description="Largest Contentful Paint (s)")
    fid: Optional[float] = Field(None, description="First Input Delay (ms)")
    cls: Optional[float] = Field(None, description="Cumulative Layout Shift")

    # Crawlability
    has_robots_txt: bool = Field(False)
    has_sitemap: bool = Field(False)
    sitemap_urls: int = Field(0)
    indexed_pages: int = Field(0)

    # Security
    has_ssl: bool = Field(False)
    ssl_valid: bool = Field(False)
    has_hsts: bool = Field(False)

    # Mobile
    is_mobile_friendly: bool = Field(False)
    has_viewport_meta: bool = Field(False)

    # Issues
    critical_issues: int = Field(0)
    high_issues: int = Field(0)
    medium_issues: int = Field(0)
    low_issues: int = Field(0)

    issues: List[OnPageIssue] = Field(default_factory=list)


class SEORecommendation(BaseModel):
    """Single SEO recommendation"""
    priority: IssueSeverity = Field(..., description="Priority level")
    category: IssueCategory = Field(..., description="Issue category")
    issue: str = Field(..., description="Issue description")
    recommendation: str = Field(..., description="Recommended fix")
    impact: str = Field(..., description="Expected impact")
    effort: str = Field(..., description="Implementation effort: low, medium, high")
    affected_pages: int = Field(0, description="Number of pages affected")


class SEOReport(BaseModel):
    """Comprehensive SEO report combining Firecrawl + DataForSEO data"""
    # Target
    domain: str = Field(..., description="Analyzed domain")
    analyzed_at: datetime = Field(default_factory=datetime.now)

    # Overall score
    seo_score: SEOScore = Field(..., description="SEO scores")

    # Content (from Firecrawl)
    content_analysis: Optional[ContentAnalysis] = Field(None)

    # SERP rankings (from DataForSEO)
    serp_data: Optional[Dict[str, SERPRankingData]] = Field(None, description="SERP data by keyword")
    keywords_tracked: int = Field(0)
    keywords_in_top_10: int = Field(0)
    keywords_in_top_100: int = Field(0)
    avg_position: Optional[float] = Field(None)

    # Backlinks (from DataForSEO)
    backlinks_summary: Optional[BacklinksSummary] = Field(None)

    # Technical SEO (from DataForSEO OnPage)
    technical_seo: Optional[TechnicalSEO] = Field(None)

    # Competitor analysis
    competitors: Optional[CompetitorAnalysis] = Field(None)

    # Recommendations
    recommendations: List[SEORecommendation] = Field(default_factory=list)

    # Metadata
    firecrawl_credits_used: float = Field(0.0)
    dataforseo_cost: float = Field(0.0)
    total_cost: float = Field(0.0)
    processing_time: float = Field(0.0, description="Total processing time in seconds")

    def generate_summary(self) -> str:
        """Generate a text summary of the SEO report"""
        lines = [
            f"SEO Report for {self.domain}",
            f"Generated: {self.analyzed_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            f"Overall Score: {self.seo_score.overall}/100 (Grade: {self.seo_score.to_grade()})",
            "",
        ]

        if self.content_analysis:
            lines.extend([
                "Content Analysis:",
                f"  - Pages scraped: {self.content_analysis.pages_scraped}",
                f"  - Total words: {self.content_analysis.total_words:,}",
                f"  - Avg word count: {self.content_analysis.avg_word_count:.0f}",
                "",
            ])

        if self.backlinks_summary:
            lines.extend([
                "Backlinks:",
                f"  - Total backlinks: {self.backlinks_summary.total_backlinks:,}",
                f"  - Referring domains: {self.backlinks_summary.referring_domains}",
                f"  - Domain rank: {self.backlinks_summary.domain_rank or 'N/A'}",
                "",
            ])

        if self.technical_seo:
            lines.extend([
                "Technical SEO:",
                f"  - Score: {self.technical_seo.score}/100",
                f"  - Critical issues: {self.technical_seo.critical_issues}",
                f"  - SSL: {'Yes' if self.technical_seo.has_ssl else 'No'}",
                "",
            ])

        lines.extend([
            f"Keywords tracked: {self.keywords_tracked}",
            f"  - In top 10: {self.keywords_in_top_10}",
            f"  - In top 100: {self.keywords_in_top_100}",
            f"  - Avg position: {self.avg_position:.1f}" if self.avg_position else "  - Avg position: N/A",
            "",
            f"Recommendations: {len(self.recommendations)}",
            f"  - Critical: {sum(1 for r in self.recommendations if r.priority == IssueSeverity.CRITICAL)}",
            f"  - High: {sum(1 for r in self.recommendations if r.priority == IssueSeverity.HIGH)}",
            "",
            f"Total cost: ${self.total_cost:.4f}",
        ])

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Export report as markdown"""
        md = [
            f"# SEO Report: {self.domain}",
            f"*Generated: {self.analyzed_at.strftime('%Y-%m-%d %H:%M')}*",
            "",
            f"## Overall Score: {self.seo_score.overall}/100 ({self.seo_score.to_grade()})",
            "",
            "| Metric | Score |",
            "|--------|-------|",
            f"| Technical | {self.seo_score.technical or 'N/A'} |",
            f"| Content | {self.seo_score.content or 'N/A'} |",
            f"| Authority | {self.seo_score.authority or 'N/A'} |",
            "",
        ]

        if self.content_analysis:
            md.extend([
                "## Content Analysis",
                f"- **Pages Scraped:** {self.content_analysis.pages_scraped}",
                f"- **Total Words:** {self.content_analysis.total_words:,}",
                f"- **Avg Word Count:** {self.content_analysis.avg_word_count:.0f}",
                f"- **Thin Content Pages:** {self.content_analysis.pages_with_thin_content}",
                "",
            ])

        if self.backlinks_summary:
            md.extend([
                "## Backlinks",
                f"- **Total Backlinks:** {self.backlinks_summary.total_backlinks:,}",
                f"- **Referring Domains:** {self.backlinks_summary.referring_domains}",
                f"- **Domain Rank:** {self.backlinks_summary.domain_rank or 'N/A'}",
                f"- **Dofollow Ratio:** {self.backlinks_summary.dofollow_ratio:.1%}",
                "",
            ])

        if self.recommendations:
            md.extend([
                "## Recommendations",
                "",
            ])
            for i, rec in enumerate(self.recommendations[:10], 1):
                md.append(f"### {i}. {rec.issue}")
                md.append(f"**Priority:** {rec.priority.value.upper()}")
                md.append(f"**Category:** {rec.category.value}")
                md.append(f"**Recommendation:** {rec.recommendation}")
                md.append(f"**Impact:** {rec.impact}")
                md.append("")

        md.extend([
            "---",
            f"*Processing time: {self.processing_time:.1f}s | Cost: ${self.total_cost:.4f}*",
        ])

        return "\n".join(md)
