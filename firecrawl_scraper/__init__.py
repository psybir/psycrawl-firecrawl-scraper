"""
Firecrawl Scraper v2.0 - Professional web scraping system built on Firecrawl API v2

A comprehensive, production-ready web scraping solution with:
- 5 scraping strategies (CRAWL, MAP, EXTRACT, BATCH, DYNAMIC)
- Batch scraping for 1000+ URLs in parallel
- Actions support (click, scroll, wait, screenshot)
- Real-time monitoring with WebSocket
- Change tracking for website monitoring
- Media extraction (PDF, DOCX, images)
- Smart URL validation and stealth mode
- Checkpoint/resume system for reliability
- Cost management and estimation
- 100% configurable via environment variables

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

__version__ = '2.0.0'
__author__ = 'Firecrawl Scraper Contributors'
__license__ = 'MIT'

# Import configuration
from .config import Config

# Import core components
from .extraction.universal_scraper import UniversalScraper
from .core.firecrawl_client import EnhancedFirecrawlClient, ActionSequences

# Import new v2.0 components
from .core.change_tracker import ChangeTracker
from .core.websocket_monitor import WebSocketMonitor
from .core.media_extractor import MediaExtractor

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
]
