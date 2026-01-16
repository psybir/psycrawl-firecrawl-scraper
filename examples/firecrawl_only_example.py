#!/usr/bin/env python3
"""
Mode 1: Firecrawl Only Example

Demonstrates website scraping capabilities without DataForSEO.
Use this when you only need to extract content from websites.

Features:
- Single page scraping
- Site mapping (URL discovery)
- Batch scraping multiple URLs
- Content extraction with markdown/HTML formats

Cost: ~1 credit per page (5 credits for map)

Usage:
    python examples/firecrawl_only_example.py

    # Or with a specific URL:
    python examples/firecrawl_only_example.py --url https://example.com
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper import Config, EnhancedFirecrawlClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def wrap_with_metadata(data: Dict, schema_name: str) -> Dict:
    """Wrap data with metadata."""
    return {
        "_meta": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "schema": schema_name,
            "source": "psycrawl-firecrawl-scraper",
            "generator": "firecrawl_only_example.py"
        },
        "data": data
    }


async def scrape_single_page(client: EnhancedFirecrawlClient, url: str) -> Dict:
    """
    Scrape a single page.

    Args:
        client: Firecrawl client
        url: URL to scrape

    Returns:
        Dict with scraped content
    """
    logger.info(f"Scraping: {url}")

    result = await client.scrape(
        url=url,
        formats=['markdown', 'html']
    )

    if result.get('success'):
        logger.info(f"  Title: {result.get('metadata', {}).get('title', 'N/A')}")
        logger.info(f"  Words: {len(result.get('markdown', '').split())}")
        return {
            "url": url,
            "title": result.get('metadata', {}).get('title'),
            "description": result.get('metadata', {}).get('description'),
            "word_count": len(result.get('markdown', '').split()),
            "markdown": result.get('markdown', ''),
            "html_length": len(result.get('html', '')),
            "success": True
        }
    else:
        logger.error(f"  Failed: {result.get('error')}")
        return {"url": url, "success": False, "error": result.get('error')}


async def map_site(client: EnhancedFirecrawlClient, url: str, limit: int = 50) -> List[str]:
    """
    Discover all URLs on a site.

    Args:
        client: Firecrawl client
        url: Base URL to map
        limit: Maximum URLs to discover

    Returns:
        List of discovered URLs
    """
    logger.info(f"Mapping site: {url}")

    result = await client.map(url=url, limit=limit)

    if not result.get('success'):
        logger.error(f"Map failed: {result.get('error')}")
        return []

    # Extract URLs (handles both dict and string formats)
    raw_links = result.get('links', [])
    urls = []
    for link in raw_links:
        if isinstance(link, dict):
            url = link.get('url', '')
        else:
            url = str(link)
        # Filter out sitemaps
        if url and not url.endswith('.xml'):
            urls.append(url)

    logger.info(f"Found {len(urls)} URLs")
    return urls


async def batch_scrape_urls(
    client: EnhancedFirecrawlClient,
    urls: List[str],
    formats: List[str] = None
) -> List[Dict]:
    """
    Scrape multiple URLs in batch.

    Args:
        client: Firecrawl client
        urls: List of URLs to scrape
        formats: Output formats (default: markdown)

    Returns:
        List of scraped page data
    """
    formats = formats or ['markdown']
    logger.info(f"Batch scraping {len(urls)} URLs...")

    result = await client.batch_scrape(
        urls=urls,
        formats=formats
    )

    if result.get('success'):
        pages = result.get('data', [])
        logger.info(f"Successfully scraped {len(pages)} pages")
        return pages
    else:
        logger.error(f"Batch scrape failed: {result.get('error')}")
        return []


async def full_site_scrape(client: EnhancedFirecrawlClient, url: str, max_pages: int = 20) -> Dict:
    """
    Complete workflow: map site then scrape all pages.

    Args:
        client: Firecrawl client
        url: Base URL
        max_pages: Maximum pages to scrape

    Returns:
        Dict with all scraped content
    """
    logger.info(f"Full site scrape: {url}")

    # Step 1: Map site
    urls = await map_site(client, url, limit=max_pages)

    if not urls:
        return {"success": False, "error": "No URLs found"}

    # Step 2: Batch scrape
    pages = await batch_scrape_urls(client, urls[:max_pages])

    # Process results
    result = {
        "base_url": url,
        "total_urls_found": len(urls),
        "pages_scraped": len(pages),
        "total_words": 0,
        "pages": [],
        "success": True
    }

    for page in pages:
        markdown = page.get('markdown', '')
        word_count = len(markdown.split()) if markdown else 0
        result["total_words"] += word_count

        result["pages"].append({
            "url": page.get('metadata', {}).get('sourceURL', ''),
            "title": page.get('metadata', {}).get('title', ''),
            "description": page.get('metadata', {}).get('description', ''),
            "word_count": word_count
        })

    logger.info(f"Total: {result['pages_scraped']} pages, {result['total_words']:,} words")

    return result


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Firecrawl Only Example')
    parser.add_argument('--url', default='https://example.com',
                        help='URL to scrape')
    parser.add_argument('--mode', choices=['single', 'map', 'batch', 'full'],
                        default='full', help='Scraping mode')
    parser.add_argument('--max-pages', type=int, default=20,
                        help='Maximum pages for full scrape')
    parser.add_argument('--output', help='Output file path')
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  MODE 1: FIRECRAWL ONLY - Website Scraping                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize client
    client = EnhancedFirecrawlClient(Config.API_KEY)

    # Run selected mode
    if args.mode == 'single':
        result = await scrape_single_page(client, args.url)
    elif args.mode == 'map':
        urls = await map_site(client, args.url)
        result = {"urls": urls, "count": len(urls)}
    elif args.mode == 'batch':
        urls = await map_site(client, args.url, limit=10)
        pages = await batch_scrape_urls(client, urls[:10])
        result = {"pages": len(pages)}
    else:  # full
        result = await full_site_scrape(client, args.url, args.max_pages)

    # Save output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(Config.OUTPUT_DIR) / "firecrawl_example_output.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(wrap_with_metadata(result, "firecrawl_scrape_v1"), f, indent=2)

    print(f"\nOutput saved to: {output_path}")


if __name__ == '__main__':
    asyncio.run(main())
