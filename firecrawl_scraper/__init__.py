"""
Firecrawl Scraper v2.1 - Ultimate SEO Machine

A comprehensive, production-ready web scraping and SEO solution with:
- 6 scraping strategies (CRAWL, MAP, EXTRACT, BATCH, DYNAMIC, SEO)
- Batch scraping for 1000+ URLs in parallel
- Actions support (click, scroll, wait, screenshot)
- Real-time monitoring with WebSocket
- Change tracking for website monitoring
- Media extraction (PDF, DOCX, images)
- Smart URL validation and stealth mode
- Checkpoint/resume system for reliability
- Cost management and estimation
- 100% configurable via environment variables

NEW in v2.1 - Ultimate SEO Machine:
- DataForSEO integration for SERP, keywords, backlinks, on-page analysis
- SEO orchestrator for comprehensive audits
- Competitor analysis and content gap detection
- Keyword research with search volume and difficulty

Quick Start:
    >>> import asyncio
    >>> from firecrawl_scraper import UniversalScraper, Config
    >>>
    >>> async def main():
    ...     scraper = UniversalScraper(Config.API_KEY)
    ...     result = await scraper.scrape_source({
    ...         'url': 'https://docs.python.org/3/tutorial/',
    ...         'strategy': 'map',
    ...         'max_pages': 10
    ...     })
    ...     print(f"Scraped {len(result['data'])} pages!")
    >>>
    >>> asyncio.run(main())

NEW in v2.0 - Batch Scraping:
    >>> result = await scraper.scrape_source({
    ...     'urls': ['https://example.com/1', 'https://example.com/2'],
    ...     'strategy': 'batch'
    ... })

NEW in v2.0 - Dynamic Scraping with Actions:
    >>> result = await scraper.scrape_source({
    ...     'url': 'https://spa-example.com',
    ...     'strategy': 'dynamic',
    ...     'action_preset': 'infinite_scroll'
    ... })

For detailed usage, see README.md and DATA_FORMAT.md
"""

__version__ = '2.1.0'
__author__ = 'Firecrawl Scraper Contributors'
__license__ = 'MIT'

# Import configuration
from .config import Config

# Import core components
from .extraction.universal_scraper import UniversalScraper
from .core.firecrawl_client import EnhancedFirecrawlClient, ActionSequences

# Import v2.0 components
from .core.change_tracker import ChangeTracker
from .core.websocket_monitor import WebSocketMonitor
from .core.media_extractor import MediaExtractor

# Import v2.1 SEO components
from .core.dataforseo_client import DataForSEOClient
from .orchestrators.seo_orchestrator import SEOOrchestrator
from .extraction.seo_enrichment import SEOEnrichmentStrategy

# Define public API
__all__ = [
    # Configuration
    'Config',

    # Main scraper
    'UniversalScraper',

    # Core client
    'EnhancedFirecrawlClient',
    'ActionSequences',

    # v2.0 features
    'ChangeTracker',
    'WebSocketMonitor',
    'MediaExtractor',

    # v2.1 SEO features
    'DataForSEOClient',
    'SEOOrchestrator',
    'SEOEnrichmentStrategy',
]
