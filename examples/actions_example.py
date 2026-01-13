#!/usr/bin/env python3
"""
Actions Example - Dynamic Site Scraping

Demonstrates the new Actions feature in Firecrawl API v2:
- Click elements
- Scroll pages
- Wait for content
- Handle JavaScript-heavy sites
- Screenshot capture

Usage:
    python examples/actions_example.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper import UniversalScraper, Config
from firecrawl_scraper.core.firecrawl_client import ActionSequences


async def basic_actions_demo():
    """
    Basic demonstration of Actions for dynamic content.
    """

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ACTIONS DEMO - API v2                                   ║
║               Browser Automation for Dynamic Sites                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    scraper = UniversalScraper(Config.API_KEY)

    # Example 1: Wait and scroll for lazy-loaded content
    print("\n📌 Example 1: Infinite Scroll Page")
    print("-" * 40)

    config_scroll = {
        'url': 'https://news.ycombinator.com/',  # Example of dynamic content
        'strategy': 'dynamic',
        'action_preset': 'infinite_scroll',  # Pre-built scroll sequence
        'category': 'dynamic-scroll-example'
    }

    print(f"URL: {config_scroll['url']}")
    print(f"Preset: {config_scroll['action_preset']}")
    print("Actions: 5x scroll + wait to load lazy content")
    print()

    result = await scraper.scrape_source(config_scroll)

    if result['success']:
        print(f"✅ Success!")
        print(f"   Actions executed: {result.get('actions_executed', 0)}")
        print(f"   Content: {result.get('total_chars', 0):,} characters")
        print(f"   Credits: {result.get('credits_used', 0)}")
    else:
        print(f"❌ Failed: {result.get('error')}")

    return result


async def custom_actions_demo():
    """
    Custom actions for specific site interactions.
    """

    print("\n" + "=" * 60)
    print("📌 Example 2: Custom Actions")
    print("=" * 60)

    scraper = UniversalScraper(Config.API_KEY)

    # Custom actions: wait, click cookie banner, then scroll
    custom_actions = [
        {"type": "wait", "milliseconds": 2000},  # Wait for page load
        {"type": "click", "selector": ".cookie-accept, #accept-cookies"},  # Dismiss cookies
        {"type": "wait", "milliseconds": 1000},  # Wait for banner to close
        {"type": "scroll", "direction": "down", "amount": 500},  # Scroll down
        {"type": "wait", "milliseconds": 1000},  # Wait for content
    ]

    config_custom = {
        'url': 'https://example.com',  # Replace with actual target
        'strategy': 'dynamic',
        'actions': custom_actions,
        'category': 'custom-actions-example'
    }

    print(f"URL: {config_custom['url']}")
    print(f"Custom actions: {len(custom_actions)}")
    for action in custom_actions:
        print(f"   - {action['type']}: {action.get('selector', action.get('direction', action.get('milliseconds', '')))}")
    print()

    result = await scraper.scrape_source(config_custom)

    if result['success']:
        print(f"✅ Success!")
        print(f"   Content: {result.get('total_chars', 0):,} characters")
    else:
        print(f"❌ Failed: {result.get('error')}")

    return result


async def screenshot_demo():
    """
    Take screenshots of pages after executing actions.
    """

    print("\n" + "=" * 60)
    print("📌 Example 3: Screenshot Capture")
    print("=" * 60)

    scraper = UniversalScraper(Config.API_KEY)

    config_screenshot = {
        'url': 'https://example.com',
        'strategy': 'dynamic',
        'action_preset': 'wait_for_content',
        'take_screenshot': True,  # Enable screenshot
        'category': 'screenshot-example'
    }

    print(f"URL: {config_screenshot['url']}")
    print("Screenshot: Full page capture enabled")
    print()

    result = await scraper.scrape_source(config_screenshot)

    if result['success']:
        print(f"✅ Success!")
        print(f"   Screenshot: {'Captured' if result.get('has_screenshot') else 'Not captured'}")
        print(f"   Content: {result.get('total_chars', 0):,} characters")
    else:
        print(f"❌ Failed: {result.get('error')}")

    return result


async def mobile_emulation_demo():
    """
    Scrape with mobile device emulation.
    """

    print("\n" + "=" * 60)
    print("📌 Example 4: Mobile Emulation")
    print("=" * 60)

    scraper = UniversalScraper(Config.API_KEY)

    config_mobile = {
        'url': 'https://example.com',
        'strategy': 'dynamic',
        'mobile': True,  # Enable mobile emulation
        'action_preset': 'wait_for_content',
        'category': 'mobile-example'
    }

    print(f"URL: {config_mobile['url']}")
    print("Mode: Mobile device emulation")
    print()

    result = await scraper.scrape_source(config_mobile)

    if result['success']:
        print(f"✅ Success!")
        print(f"   Content: {result.get('total_chars', 0):,} characters")
    else:
        print(f"❌ Failed: {result.get('error')}")

    return result


async def action_presets_info():
    """
    Show available action presets.
    """

    print("\n" + "=" * 60)
    print("📋 AVAILABLE ACTION PRESETS")
    print("=" * 60)

    presets = {
        'infinite_scroll': 'Scroll 5 times with waits - for lazy-loaded content',
        'load_more_3x': 'Click "Load More" button 3 times',
        'accept_cookies': 'Try to dismiss cookie consent banners',
        'wait_for_content': 'Wait 5 seconds for dynamic content',
    }

    for preset, description in presets.items():
        print(f"\n📌 {preset}")
        print(f"   {description}")

    print("\n" + "-" * 60)
    print("Usage:")
    print("  config = {")
    print("      'url': 'https://example.com',")
    print("      'strategy': 'dynamic',")
    print("      'action_preset': 'infinite_scroll'")
    print("  }")
    print("-" * 60)


async def main():
    """Run actions examples"""

    print("Choose an example:")
    print("1. Basic scroll actions")
    print("2. Custom actions")
    print("3. Screenshot capture")
    print("4. Mobile emulation")
    print("5. View action presets")
    print("6. Run all demos")
    print()

    choice = input("Enter choice (1-6): ").strip()

    if choice == '1':
        await basic_actions_demo()
    elif choice == '2':
        await custom_actions_demo()
    elif choice == '3':
        await screenshot_demo()
    elif choice == '4':
        await mobile_emulation_demo()
    elif choice == '5':
        await action_presets_info()
    elif choice == '6':
        await basic_actions_demo()
        await custom_actions_demo()
        await screenshot_demo()
        await mobile_emulation_demo()
        await action_presets_info()
    else:
        print("Invalid choice. Showing action presets...")
        await action_presets_info()


if __name__ == '__main__':
    asyncio.run(main())
