#!/usr/bin/env python3
"""
WebSocket Monitoring Example - Real-Time Crawl Progress

Demonstrates real-time monitoring of crawl jobs:
- Live progress updates
- Per-page callbacks
- Progress bar display
- Event handling

Usage:
    python examples/websocket_monitoring_example.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper.core.websocket_monitor import WebSocketMonitor, ProgressDisplay
from firecrawl_scraper.config import Config


async def crawl_with_live_progress():
    """
    Crawl a website with live progress updates.
    """

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    REAL-TIME CRAWL MONITORING                                 ║
║                Live Progress Updates During Crawl                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    monitor = WebSocketMonitor(api_key=Config.API_KEY)

    # Callbacks for real-time events
    pages_scraped = []

    def on_page_scraped(doc):
        """Called for each page as it's scraped"""
        url = doc.get('metadata', {}).get('sourceURL', doc.get('url', 'Unknown'))
        content_len = len(doc.get('markdown', ''))
        pages_scraped.append(url)
        print(f"\n   📄 Scraped: {url[:60]}...")
        print(f"      Content: {content_len:,} chars")

    def on_progress(completed, total):
        """Called on progress updates"""
        # Progress is shown via tqdm bar
        pass

    def on_error(error):
        """Called on errors"""
        print(f"\n   ❌ Error: {error}")

    def on_complete(progress):
        """Called when crawl completes"""
        print(f"\n\n✅ CRAWL COMPLETE!")
        print(f"   Duration: {progress.elapsed_time:.1f}s")
        print(f"   Pages: {progress.completed}/{progress.total}")
        print(f"   Credits: {progress.credits_used}")

    # Start crawl with monitoring
    url = 'https://docs.python.org/3/tutorial/'
    limit = 10

    print(f"🎯 Target: {url}")
    print(f"📊 Limit: {limit} pages")
    print(f"📡 Real-time monitoring enabled")
    print("\n" + "-" * 60)

    result = await monitor.crawl_and_watch(
        url=url,
        limit=limit,
        on_page=on_page_scraped,
        on_progress=on_progress,
        on_error=on_error,
        on_complete=on_complete,
        show_progress_bar=True
    )

    print("-" * 60)

    # Summary
    print(f"""
📊 CRAWL SUMMARY:
   Status:    {result.get('status', 'unknown')}
   Completed: {result.get('completed', 0)}/{result.get('total', 0)} pages
   Content:   {sum(len(d.get('markdown', '')) for d in result.get('data', [])):,} chars
   Duration:  {result.get('elapsed_seconds', 0):.1f}s
   Credits:   {result.get('creditsUsed', 0)}
    """)

    return result


async def batch_with_live_progress():
    """
    Batch scrape with live progress updates.
    """

    print("\n" + "=" * 60)
    print("📊 BATCH SCRAPE WITH LIVE PROGRESS")
    print("=" * 60)

    monitor = WebSocketMonitor(api_key=Config.API_KEY)

    urls = [
        'https://example.com',
        'https://httpbin.org/html',
        'https://httpbin.org/robots.txt',
    ]

    def on_page(doc):
        url = doc.get('metadata', {}).get('sourceURL', 'Unknown')
        print(f"\n   ✓ Scraped: {url}")

    print(f"\n📋 URLs to scrape: {len(urls)}")
    print("-" * 40)

    result = await monitor.batch_scrape_and_watch(
        urls=urls,
        on_page=on_page,
        show_progress_bar=True
    )

    print("-" * 40)

    print(f"""
✅ BATCH COMPLETE:
   Status:    {result.get('status', 'unknown')}
   Completed: {result.get('completed', 0)}/{result.get('total', 0)}
   Duration:  {result.get('elapsed_seconds', 0):.1f}s
    """)

    return result


async def progress_display_demo():
    """
    Demonstrate manual progress display.
    """

    print("\n" + "=" * 60)
    print("📊 MANUAL PROGRESS DISPLAY DEMO")
    print("=" * 60 + "\n")

    # Create progress display
    total = 20
    display = ProgressDisplay(total=total, description="Processing")

    print("Simulating progress...")

    for i in range(total + 1):
        display.update(i)
        await asyncio.sleep(0.1)

    display.complete()


async def main():
    """Run WebSocket monitoring examples"""

    print("Choose an example:")
    print("1. Crawl with live progress")
    print("2. Batch scrape with live progress")
    print("3. Progress display demo")
    print("4. Run all")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == '1':
        await crawl_with_live_progress()
    elif choice == '2':
        await batch_with_live_progress()
    elif choice == '3':
        await progress_display_demo()
    elif choice == '4':
        await progress_display_demo()
        await batch_with_live_progress()
        await crawl_with_live_progress()
    else:
        print("Invalid choice. Running progress demo...")
        await progress_display_demo()


if __name__ == '__main__':
    asyncio.run(main())
