#!/usr/bin/env python3
"""
Change Tracking Example - Monitor Websites for Updates

Demonstrates the change tracking feature:
- Register URLs for monitoring
- Detect content changes
- View change history
- Diff generation

Usage:
    python examples/change_tracking_example.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper.core.change_tracker import ChangeTracker, ChangeRecord
from firecrawl_scraper.config import Config


def on_change_detected(change: ChangeRecord):
    """Callback when changes are detected"""
    print(f"\n🔔 CHANGE DETECTED!")
    print(f"   URL: {change.url}")
    print(f"   Time: {change.detected_at}")
    print(f"   Content change: {change.content_length_change:+d} characters")
    print(f"   {change.diff_summary}")


async def basic_tracking_demo():
    """
    Basic change tracking demonstration.
    """

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CHANGE TRACKING DEMO                                       ║
║               Monitor Websites for Content Changes                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize tracker with callback
    tracker = ChangeTracker(
        api_key=Config.API_KEY,
        on_change=on_change_detected
    )

    # URLs to track
    urls_to_track = [
        'https://news.ycombinator.com/',
        'https://httpbin.org/uuid',  # Changes every request (for demo)
    ]

    print("📋 Registering URLs for tracking...")
    for url in urls_to_track:
        tracker.track_url(url, check_interval=3600)  # Check every hour
        print(f"   ✓ {url}")

    print(f"\n📊 Total tracked URLs: {len(tracker.get_tracked_urls())}")

    # First check (establishes baseline)
    print("\n🔄 First check (establishing baseline)...")
    print("-" * 60)

    changes = await tracker.check_all_tracked(force=True)

    print("-" * 60)
    print(f"Baseline established. Changes detected: {len(changes)}")

    # Second check (detect changes)
    print("\n🔄 Second check (detecting changes)...")
    print("-" * 60)

    await asyncio.sleep(2)  # Wait a moment
    changes = await tracker.check_all_tracked(force=True)

    print("-" * 60)
    print(f"Changes detected: {len(changes)}")

    # Show tracking stats
    stats = tracker.get_tracking_stats()
    print(f"""
📊 TRACKING STATISTICS:
   Total tracked URLs: {stats['total_tracked']}
   URLs with changes:  {stats['urls_with_changes']}
   Total changes:      {stats['total_changes_detected']}
    """)

    return tracker


async def view_history_demo():
    """
    View change history for a URL.
    """

    print("\n" + "=" * 60)
    print("📜 VIEW CHANGE HISTORY")
    print("=" * 60)

    tracker = ChangeTracker(api_key=Config.API_KEY)

    # Get tracked URLs
    tracked = tracker.get_tracked_urls()

    if not tracked:
        print("No URLs being tracked. Run basic demo first.")
        return

    print(f"\nTracked URLs: {len(tracked)}")
    for i, url in enumerate(tracked, 1):
        print(f"   {i}. {url}")

    # Show history for first URL
    url = tracked[0]
    print(f"\n📜 Change history for: {url}")
    print("-" * 40)

    history = tracker.get_change_history(url, limit=10)

    if history:
        for change in history:
            print(f"   {change['detected_at']}")
            print(f"   Change: {change['content_length_change']:+d} chars")
            print(f"   Hash: {change['current_hash'][:16]}...")
            print()
    else:
        print("   No changes recorded yet.")

    # Show snapshots
    print(f"\n📸 Content snapshots for: {url}")
    print("-" * 40)

    snapshots = tracker.get_snapshots(url, limit=5)

    if snapshots:
        for snap in snapshots:
            print(f"   {snap['timestamp']}")
            print(f"   Length: {snap['content_length']:,} chars")
            print(f"   Preview: {snap['markdown_preview'][:100]}...")
            print()
    else:
        print("   No snapshots recorded yet.")


async def continuous_monitoring_demo():
    """
    Demonstrate continuous monitoring (limited iterations).
    """

    print("\n" + "=" * 60)
    print("🔄 CONTINUOUS MONITORING DEMO")
    print("=" * 60)

    tracker = ChangeTracker(
        api_key=Config.API_KEY,
        on_change=on_change_detected
    )

    # Track a URL that changes frequently (for demo)
    tracker.track_url('https://httpbin.org/uuid')

    print("\n🔄 Starting continuous monitoring (3 cycles, 5s interval)...")
    print("   Press Ctrl+C to stop")
    print("-" * 60)

    try:
        await tracker.monitor_continuously(
            interval=5,  # Check every 5 seconds
            max_iterations=3  # Stop after 3 cycles
        )
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")

    print("-" * 60)
    print("✅ Monitoring complete")


async def main():
    """Run change tracking examples"""

    print("Choose an example:")
    print("1. Basic change tracking")
    print("2. View change history")
    print("3. Continuous monitoring (3 cycles)")
    print("4. Run all")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == '1':
        await basic_tracking_demo()
    elif choice == '2':
        await view_history_demo()
    elif choice == '3':
        await continuous_monitoring_demo()
    elif choice == '4':
        await basic_tracking_demo()
        await view_history_demo()
        await continuous_monitoring_demo()
    else:
        print("Invalid choice. Running basic demo...")
        await basic_tracking_demo()


if __name__ == '__main__':
    asyncio.run(main())
