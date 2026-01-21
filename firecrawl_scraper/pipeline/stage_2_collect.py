"""
Stage 2: COLLECT - DataForSEO + Firecrawl data collection

Input: Intent/Geo Matrix
Output: Source entities (SERP results, competitor URLs, GBP data)

This stage collects competitive intelligence data from:
- DataForSEO: SERP rankings, local pack, keyword data
- Firecrawl: Competitor website content
"""

import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from ..models import (
    IntentGeoMatrix,
    MatrixCell,
    Source,
    SourceType,
    ScrapeStatus,
    DataFreshness,
    SERPFeature,
    GeoTag,
    SERPData,
    SERPResult,
)

logger = logging.getLogger(__name__)


class CollectStage:
    """Collect competitive data from DataForSEO and Firecrawl"""

    def __init__(
        self,
        matrix: IntentGeoMatrix,
        dataforseo_client=None,
        firecrawl_client=None
    ):
        self.matrix = matrix
        self.dataforseo = dataforseo_client
        self.firecrawl = firecrawl_client
        self.sources: List[Source] = []
        self.competitor_urls: Dict[str, str] = {}  # domain -> url

    async def run(self) -> List[Source]:
        """Execute Stage 2: Collect competitive data"""
        logger.info(f"Stage 2: Collecting data for {len(self.matrix.cells)} matrix cells")

        # Collect SERP data for each cell's keyword cluster
        await self._collect_serp_data()

        # Collect local pack data
        await self._collect_local_pack_data()

        # Collect competitor website data
        await self._collect_competitor_data()

        # Update source freshness
        for source in self.sources:
            source.update_freshness()

        logger.info(f"Stage 2 Complete: Collected {len(self.sources)} sources")
        return self.sources

    async def _collect_serp_data(self):
        """Collect SERP rankings for keyword clusters"""
        logger.info("Collecting SERP data...")

        # Get unique keyword/location combinations
        keyword_locations = self._get_keyword_location_pairs()

        for keyword, geo_tag in keyword_locations:
            try:
                serp_data = await self._fetch_serp(keyword, geo_tag)
                if serp_data:
                    self._process_serp_results(serp_data, keyword, geo_tag)
            except Exception as e:
                logger.error(f"Error fetching SERP for '{keyword}': {e}")

    async def _collect_local_pack_data(self):
        """Collect local pack/maps data"""
        logger.info("Collecting local pack data...")

        # Get primary locations
        primary_cells = [c for c in self.matrix.cells if c.geo_bucket == "0-10"]

        for cell in primary_cells:
            keywords = cell.keyword_cluster[:3]  # Top 3 keywords
            for keyword in keywords:
                try:
                    local_data = await self._fetch_local_finder(keyword)
                    if local_data:
                        self._process_local_results(local_data, keyword)
                except Exception as e:
                    logger.error(f"Error fetching local pack for '{keyword}': {e}")

    async def _collect_competitor_data(self):
        """Collect competitor website content via Firecrawl"""
        logger.info("Collecting competitor website data...")

        # Get unique competitor domains
        competitor_domains = list(set(self.competitor_urls.keys()))

        for domain in competitor_domains[:10]:  # Limit to top 10 competitors
            try:
                await self._scrape_competitor(domain, self.competitor_urls[domain])
            except Exception as e:
                logger.error(f"Error scraping competitor {domain}: {e}")

    def _get_keyword_location_pairs(self) -> List[tuple]:
        """Get unique keyword/location pairs from matrix"""
        pairs = []
        seen = set()

        for cell in self.matrix.cells:
            # Get locations for this geo bucket
            col = next((c for c in self.matrix.columns if c.geo_bucket.value == cell.geo_bucket), None)
            if not col:
                continue

            # Create pairs for top keywords and locations
            for keyword in cell.keyword_cluster[:5]:
                for location in col.locations[:3]:
                    pair_key = f"{keyword}|{location}"
                    if pair_key not in seen:
                        seen.add(pair_key)
                        geo_tag = GeoTag(
                            city=location.split(",")[0].strip(),
                            state=location.split(",")[1].strip() if "," in location else "PA"
                        )
                        pairs.append((keyword, geo_tag))

        return pairs[:50]  # Limit to 50 pairs

    async def _fetch_serp(self, keyword: str, geo_tag: GeoTag) -> Optional[Dict]:
        """Fetch SERP data from DataForSEO"""
        if not self.dataforseo:
            logger.warning("DataForSEO client not configured")
            return None

        try:
            # Use DataForSEO organic search endpoint
            result = await self.dataforseo.serp_google_organic(
                keyword=keyword,
                location_name=f"{geo_tag.city}, {geo_tag.state}",
                language_code="en",
                device="desktop"
            )
            return result
        except Exception as e:
            logger.error(f"DataForSEO SERP error: {e}")
            return None

    async def _fetch_local_finder(self, keyword: str) -> Optional[Dict]:
        """Fetch local finder/maps data from DataForSEO"""
        if not self.dataforseo:
            return None

        try:
            result = await self.dataforseo.serp_google_local_finder(
                keyword=keyword,
                language_code="en"
            )
            return result
        except Exception as e:
            logger.error(f"DataForSEO local finder error: {e}")
            return None

    def _process_serp_results(self, serp_data: Dict, keyword: str, geo_tag: GeoTag):
        """Process SERP results into Source entities"""
        items = serp_data.get("items", []) or serp_data.get("result", [])

        for item in items[:20]:  # Top 20 results
            url = item.get("url") or item.get("link")
            if not url:
                continue

            domain = self._extract_domain(url)

            # Track competitor domains
            if domain not in self.competitor_urls:
                self.competitor_urls[domain] = url

            # Create source entity
            source = Source(
                id=str(uuid.uuid4()),
                source_type=SourceType.SERP_ORGANIC,
                url=url,
                domain=domain,
                scraped_at=datetime.now(),
                scrape_status=ScrapeStatus.SUCCESS,
                data_freshness=DataFreshness.CURRENT,
                geo_tags=[geo_tag],
                keywords_targeted=[keyword],
                serp_position=item.get("position") or item.get("rank_absolute"),
                raw_data={
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "breadcrumb": item.get("breadcrumb"),
                }
            )
            self.sources.append(source)

    def _process_local_results(self, local_data: Dict, keyword: str):
        """Process local pack results into Source entities"""
        items = local_data.get("items", []) or local_data.get("result", [])

        for item in items[:10]:
            # Create source for local pack result
            source = Source(
                id=str(uuid.uuid4()),
                source_type=SourceType.SERP_LOCAL_PACK,
                url=item.get("url", ""),
                domain=self._extract_domain(item.get("url", "")),
                scraped_at=datetime.now(),
                scrape_status=ScrapeStatus.SUCCESS,
                data_freshness=DataFreshness.CURRENT,
                keywords_targeted=[keyword],
                serp_position=item.get("position"),
                serp_features=[SERPFeature.LOCAL_PACK],
                raw_data={
                    "title": item.get("title"),
                    "rating": item.get("rating"),
                    "reviews_count": item.get("reviews_count"),
                    "address": item.get("address"),
                    "phone": item.get("phone"),
                }
            )
            self.sources.append(source)

    async def _scrape_competitor(self, domain: str, url: str):
        """Scrape competitor website via Firecrawl"""
        if not self.firecrawl:
            logger.warning("Firecrawl client not configured")
            return

        try:
            # Scrape main page
            result = await self.firecrawl.scrape(
                url=url,
                formats=["markdown", "html"],
                only_main_content=True
            )

            source = Source(
                id=str(uuid.uuid4()),
                source_type=SourceType.COMPETITOR_WEBSITE,
                url=url,
                domain=domain,
                scraped_at=datetime.now(),
                scrape_status=ScrapeStatus.SUCCESS,
                data_freshness=DataFreshness.CURRENT,
                raw_data=result,
                extraction_schema="website_full"
            )
            self.sources.append(source)

            # Also crawl key pages
            await self._crawl_competitor_pages(domain, url)

        except Exception as e:
            logger.error(f"Firecrawl error for {domain}: {e}")
            # Create failed source
            source = Source(
                id=str(uuid.uuid4()),
                source_type=SourceType.COMPETITOR_WEBSITE,
                url=url,
                domain=domain,
                scrape_status=ScrapeStatus.FAILED,
            )
            self.sources.append(source)

    async def _crawl_competitor_pages(self, domain: str, base_url: str):
        """Crawl additional competitor pages"""
        if not self.firecrawl:
            return

        try:
            # Use Firecrawl crawl mode to get multiple pages
            result = await self.firecrawl.crawl(
                url=base_url,
                max_depth=2,
                limit=20,
                formats=["markdown"]
            )

            pages = result.get("data", []) if isinstance(result, dict) else result

            for page in pages:
                page_url = page.get("url") or page.get("sourceURL")
                if not page_url:
                    continue

                source = Source(
                    id=str(uuid.uuid4()),
                    source_type=SourceType.COMPETITOR_PAGE,
                    url=page_url,
                    domain=domain,
                    scraped_at=datetime.now(),
                    scrape_status=ScrapeStatus.SUCCESS,
                    data_freshness=DataFreshness.CURRENT,
                    raw_data={
                        "markdown": page.get("markdown"),
                        "metadata": page.get("metadata"),
                    },
                    extraction_schema="page_content"
                )
                self.sources.append(source)

        except Exception as e:
            logger.error(f"Crawl error for {domain}: {e}")

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except:
            return ""

    def get_competitor_domains(self) -> List[str]:
        """Get list of discovered competitor domains"""
        return list(self.competitor_urls.keys())

    def get_sources_by_domain(self, domain: str) -> List[Source]:
        """Get all sources for a specific domain"""
        return [s for s in self.sources if s.domain == domain]

    def get_sources_by_type(self, source_type: SourceType) -> List[Source]:
        """Get sources by type"""
        return [s for s in self.sources if s.source_type == source_type]
