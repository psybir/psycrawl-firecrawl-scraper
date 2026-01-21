"""
Source models - Data source entities
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .geo import GeoTag


class SourceType(str, Enum):
    """Types of data sources"""
    SERP_ORGANIC = "serp_organic"
    SERP_LOCAL_PACK = "serp_local_pack"
    SERP_MAPS = "serp_maps"
    COMPETITOR_WEBSITE = "competitor_website"
    COMPETITOR_PAGE = "competitor_page"
    GBP_PROFILE = "gbp_profile"
    DIRECTORY_LISTING = "directory_listing"
    REVIEW_SITE = "review_site"
    SOCIAL_MEDIA = "social_media"
    CHAMBER_COMMERCE = "chamber_commerce"
    INDUSTRY_PUBLICATION = "industry_publication"
    JOB_BOARD = "job_board"
    CITATION_SITE = "citation_site"
    FORUM = "forum"
    YOUTUBE = "youtube"


class ScrapeStatus(str, Enum):
    """Scrape operation status"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class DataFreshness(str, Enum):
    """Data freshness levels"""
    CURRENT = "current"  # < 7 days
    RECENT = "recent"    # 7-30 days
    STALE = "stale"      # > 30 days


class SERPFeature(str, Enum):
    """SERP features"""
    FEATURED_SNIPPET = "featured_snippet"
    LOCAL_PACK = "local_pack"
    KNOWLEDGE_PANEL = "knowledge_panel"
    PEOPLE_ALSO_ASK = "people_also_ask"
    IMAGES = "images"
    VIDEOS = "videos"
    NEWS = "news"


class Source(BaseModel):
    """Data source entity - where competitive intelligence comes from"""
    id: str
    source_type: SourceType
    url: str = Field(..., description="Source URL")
    domain: Optional[str] = None
    scraped_at: Optional[datetime] = None
    scrape_status: ScrapeStatus = ScrapeStatus.PENDING
    data_freshness: DataFreshness = DataFreshness.CURRENT
    freshness_days: Optional[int] = None
    geo_tags: List[GeoTag] = Field(default_factory=list)
    keywords_targeted: Optional[List[str]] = None
    serp_position: Optional[int] = None
    serp_features: Optional[List[SERPFeature]] = None
    competitor_id: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    extraction_schema: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0, le=1)

    @property
    def is_fresh(self) -> bool:
        """Check if data is still fresh"""
        return self.data_freshness == DataFreshness.CURRENT

    @property
    def needs_refresh(self) -> bool:
        """Check if data needs refresh"""
        return self.data_freshness == DataFreshness.STALE

    def update_freshness(self):
        """Update freshness based on scraped_at"""
        if not self.scraped_at:
            self.data_freshness = DataFreshness.STALE
            return

        days_old = (datetime.now() - self.scraped_at).days
        self.freshness_days = days_old

        if days_old < 7:
            self.data_freshness = DataFreshness.CURRENT
        elif days_old < 30:
            self.data_freshness = DataFreshness.RECENT
        else:
            self.data_freshness = DataFreshness.STALE


class SERPResult(BaseModel):
    """Single SERP result for collection"""
    position: int
    url: str
    title: str
    description: Optional[str] = None
    domain: str
    is_local_pack: bool = False
    is_featured_snippet: bool = False
    rich_snippet_type: Optional[str] = None


class SERPData(BaseModel):
    """SERP data for a keyword/location combo"""
    keyword: str
    location: GeoTag
    device: str = "desktop"
    results: List[SERPResult] = Field(default_factory=list)
    local_pack: List[SERPResult] = Field(default_factory=list)
    features_present: List[SERPFeature] = Field(default_factory=list)
    total_results: Optional[int] = None
    scraped_at: datetime = Field(default_factory=datetime.now)
