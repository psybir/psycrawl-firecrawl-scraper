"""
Firecrawl Scraper - Professional web scraping system built on Firecrawl API v2

A comprehensive, production-ready web scraping solution with:
- 3 scraping strategies (CRAWL, MAP, EXTRACT)
- Smart URL validation and stealth mode
- Checkpoint/resume system for reliability
- Batch processing with orchestration
- Quality validation and deduplication
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

For detailed usage, see README.md and DATA_FORMAT.md
"""

__version__ = '1.0.0'
__author__ = 'Firecrawl Scraper Contributors'
__license__ = 'MIT'

# Import configuration
from .config import Config

# Import core components
from .extraction.universal_scraper import UniversalScraper
from .core.firecrawl_client import EnhancedFirecrawlClient

# Define public API
__all__ = [
    'Config',
    'UniversalScraper',
    'EnhancedFirecrawlClient',
]
