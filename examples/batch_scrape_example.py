#!/usr/bin/env python3
"""
Batch Scraping Example - Large-Scale URL Processing

Demonstrates the new batch scraping capabilities in Firecrawl API v2:
- Scrape 100+ URLs in parallel
- Progress tracking with callbacks
- Efficient credit usage

Usage:
    python examples/batch_scrape_example.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper import UniversalScraper, Config


async def batch_scrape_demo():
    """
    Demonstrate batch scraping with the new v2 API.

    Batch scraping is ideal when you have:
    - A known list of URLs to scrape
    - Need maximum throughput
    - Want to minimize API overhead
    """

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    BATCH SCRAPING DEMO - API v2                              ║
║                 Scrape 100+ URLs in Parallel                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize scraper
    scraper = UniversalScraper(Config.API_KEY)

    # Example: Batch scrape multiple documentation pages
    urls_to_scrape = [
        'https://docs.python.org/3/tutorial/introduction.html',
        'https://docs.python.org/3/tutorial/controlflow.html',
        'https://docs.python.org/3/tutorial/datastructures.html',
        'https://docs.python.org/3/tutorial/modules.html',
        'https://docs.python.org/3/tutorial/inputoutput.html',
        'https://docs.python.org/3/tutorial/errors.html',
        'https://docs.python.org/3/tutorial/classes.html',
        'https://docs.python.org/3/tutorial/stdlib.html',
        'https://docs.python.org/3/tutorial/venv.html',
        'https://docs.python.org/3/tutorial/whatnow.html',
    ]

    print(f"📋 URLs to scrape: {len(urls_to_scrape)}")
    print(f"💰 Estimated credits: {len(urls_to_scrape)} (1 per URL)")
    print()

    # Configure batch scrape
    source_config = {
        'urls': urls_to_scrape,
        'strategy': 'batch',  # Use new batch strategy
        'category': 'python-docs-batch'
    }

    print("🚀 Starting batch scrape...")
    print("-" * 60)

    # Execute batch scrape
    result = await scraper.scrape_source(source_config)

    print("-" * 60)

    if result['success']:
        print(f"""
✅ BATCH SCRAPE COMPLETE!

📊 Results:
   URLs requested: {result.get('urls_requested', len(urls_to_scrape))}
   URLs scraped:   {result.get('urls_scraped', 0)}
   Total content:  {result.get('total_chars', 0):,} characters
   Credits used:   {result.get('credits_used', 0)}

📁 Data saved to: {Config.OUTPUT_DIR}/python-docs-batch/
        """)

        # Show sample of scraped content
        if result.get('data'):
            print("\n📄 Sample content (first 500 chars):")
            print("-" * 40)
            sample = result['data'][0]
            if isinstance(sample, dict):
                content = sample.get('markdown', '')[:500]
            else:
                content = str(sample)[:500]
            print(content + "...")

    else:
        print(f"\n❌ BATCH SCRAPE FAILED: {result.get('error', 'Unknown error')}")

    return result


async def batch_with_progress_callback():
    """
    Batch scrape with custom progress callback.

    Shows how to track progress in real-time.
    """
    print("\n" + "=" * 60)
    print("📊 BATCH SCRAPE WITH PROGRESS TRACKING")
    print("=" * 60 + "\n")

    from firecrawl_scraper.core.firecrawl_client import EnhancedFirecrawlClient

    client = EnhancedFirecrawlClient(api_key=Config.API_KEY)

    urls = [
        'https://example.com/page1',
        'https://example.com/page2',
        'https://example.com/page3',
    ]

    def progress_callback(completed: int, total: int):
        percent = (completed / total * 100) if total > 0 else 0
        bar_width = 30
        filled = int(bar_width * completed / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"\r[{bar}] {completed}/{total} ({percent:.1f}%)", end="", flush=True)

    print("🔄 Starting batch with progress tracking...")

    try:
        result = await client.batch_scrape(
            urls=urls,
            formats=['markdown'],
            on_progress=progress_callback
        )
        print()  # New line after progress bar

        if result['success']:
            print(f"✅ Completed: {result.get('completed', 0)}/{result.get('total', 0)} URLs")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Run batch scraping examples"""

    print("Choose an example:")
    print("1. Basic batch scrape (10 URLs)")
    print("2. Batch with progress callback")
    print("3. Run both")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == '1':
        await batch_scrape_demo()
    elif choice == '2':
        await batch_with_progress_callback()
    elif choice == '3':
        await batch_scrape_demo()
        await batch_with_progress_callback()
    else:
        print("Invalid choice. Running basic demo...")
        await batch_scrape_demo()


if __name__ == '__main__':
    asyncio.run(main())
