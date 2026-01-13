#!/usr/bin/env python3
"""
Keyword Research Example - Comprehensive Keyword Analysis

Demonstrates keyword research capabilities:
- Expand seed keywords into ideas
- Get search volume and CPC data
- Analyze keyword difficulty
- Find keywords a domain ranks for

Usage:
    python examples/keyword_research_example.py

Requirements:
    - DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in .env
    - DATAFORSEO_ENABLED=true in .env
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper import SEOOrchestrator, DataForSEOClient, Config


async def keyword_ideas_demo():
    """
    Expand seed keywords into ideas.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      KEYWORD IDEAS                                            ║
║            Expand Seed Keywords Into Hundreds of Ideas                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    seo = SEOOrchestrator()

    seeds_input = input("Enter seed keywords (comma-separated): ").strip()
    if not seeds_input:
        seeds_input = "python tutorial, learn python"

    seeds = [s.strip() for s in seeds_input.split(',')]

    domain = input("Enter domain to check rankings (optional, press Enter to skip): ").strip() or None

    print(f"\n🔍 Researching keywords from seeds: {seeds}")
    print("-" * 60)

    results = await seo.keyword_research(
        seed_keywords=seeds,
        domain=domain,
        max_ideas_per_seed=30,
        save_report=True
    )

    # Print keyword ideas
    print(f"\n📊 KEYWORD IDEAS ({results['total_keywords']} found)")
    print("-" * 70)
    print(f"{'Keyword':<40} {'Search Vol':<12} {'CPC':<10} {'KD':<8}")
    print("-" * 70)

    for idea in results.get('keyword_ideas', [])[:20]:
        kw = idea.keyword[:39]
        vol = f"{idea.search_volume:,}"
        cpc = f"${idea.cpc:.2f}" if idea.cpc else 'N/A'
        kd = str(idea.keyword_difficulty) if idea.keyword_difficulty else 'N/A'
        print(f"{kw:<40} {vol:<12} {cpc:<10} {kd:<8}")

    # Print domain keywords if provided
    if domain and results.get('domain_keywords'):
        print(f"\n🎯 KEYWORDS {domain.upper()} RANKS FOR")
        print("-" * 60)
        for kw in results['domain_keywords'][:10]:
            keyword = kw.get('keyword', '')[:39]
            position = kw.get('position', 'N/A')
            vol = kw.get('search_volume', 0)
            print(f"   #{position}: {keyword} ({vol:,} searches/mo)")

    print(f"\n📁 Report saved to: {Config.SEO_OUTPUT_DIR}")
    print(f"💰 API cost: ${results.get('cost', 0):.4f}")


async def domain_keywords_demo():
    """
    Find all keywords a domain ranks for.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DOMAIN KEYWORDS                                            ║
║              Find Keywords Any Domain Ranks For                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    client = DataForSEOClient(
        login=Config.DATAFORSEO_LOGIN,
        password=Config.DATAFORSEO_PASSWORD
    )

    domain = input("Enter domain (e.g., example.com): ").strip()
    if not domain:
        domain = "python.org"

    print(f"\n🔍 Finding keywords for {domain}...")
    print("-" * 60)

    # Get ranked keywords
    result = await client.labs_ranked_keywords(
        target=domain,
        location_code=Config.SEO_DEFAULT_LOCATION_CODE,
        language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
        limit=50
    )

    if result.get('success'):
        items = result.get('data', {}).get('items', [])
        total = result.get('data', {}).get('total_count', 0)

        print(f"\n📊 {domain.upper()} RANKS FOR {total:,} KEYWORDS")
        print(f"   Showing top 50:")
        print("-" * 75)
        print(f"{'Position':<10} {'Keyword':<40} {'Search Vol':<12} {'Traffic':<12}")
        print("-" * 75)

        for item in items[:50]:
            pos = item.get('position', 'N/A')
            kw = item.get('keyword', '')[:39]
            vol = f"{item.get('search_volume', 0):,}"
            traffic = item.get('etv', 0)  # Estimated traffic value
            print(f"{str(pos):<10} {kw:<40} {vol:<12} {traffic:<12.0f}")

        print(f"\n💰 API cost: ${result.get('cost', 0):.4f}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def search_volume_demo():
    """
    Get search volume for specific keywords.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   SEARCH VOLUME CHECK                                         ║
║            Get Metrics for Specific Keywords                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    client = DataForSEOClient(
        login=Config.DATAFORSEO_LOGIN,
        password=Config.DATAFORSEO_PASSWORD
    )

    keywords_input = input("Enter keywords to check (comma-separated): ").strip()
    if not keywords_input:
        keywords_input = "python programming, javascript tutorial, web development, coding bootcamp"

    keywords = [k.strip() for k in keywords_input.split(',')]

    print(f"\n🔍 Checking search volume for {len(keywords)} keywords...")
    print("-" * 60)

    result = await client.keywords_google_ads(
        keywords=keywords,
        location_code=Config.SEO_DEFAULT_LOCATION_CODE,
        language_code=Config.SEO_DEFAULT_LANGUAGE_CODE
    )

    if result.get('success'):
        items = result.get('data', {}).get('items', [])

        print(f"\n📊 KEYWORD METRICS")
        print("-" * 85)
        print(f"{'Keyword':<30} {'Search Vol':<12} {'CPC':<10} {'Competition':<15} {'Level':<10}")
        print("-" * 85)

        for item in items:
            kw = item.get('keyword', '')[:29]
            vol = f"{item.get('search_volume', 0):,}"
            cpc = f"${item.get('cpc', 0):.2f}"
            comp = f"{item.get('competition', 0):.2f}"
            level = item.get('competition_level', 'N/A')
            print(f"{kw:<30} {vol:<12} {cpc:<10} {comp:<15} {level:<10}")

        print(f"\n💰 API cost: ${result.get('cost', 0):.4f}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def serp_check_demo():
    """
    Check SERP rankings for a keyword.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      SERP CHECK                                               ║
║             See Top 10 Results for Any Keyword                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    client = DataForSEOClient(
        login=Config.DATAFORSEO_LOGIN,
        password=Config.DATAFORSEO_PASSWORD
    )

    keyword = input("Enter keyword to check SERP: ").strip()
    if not keyword:
        keyword = "best python tutorials"

    print(f"\n🔍 Checking SERP for '{keyword}'...")
    print("-" * 60)

    result = await client.serp_google_organic(
        keyword=keyword,
        location_name=Config.SEO_DEFAULT_LOCATION,
        language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
        device='desktop',
        depth=20
    )

    if result.get('success'):
        data = result.get('data', {})
        items = data.get('items', [])

        print(f"\n📊 SERP RESULTS FOR: {keyword}")
        print("-" * 75)

        for i, item in enumerate(items[:10], 1):
            url = item.get('url', '')[:60]
            title = item.get('title', '')[:50]
            print(f"\n{i}. {title}")
            print(f"   {url}")

        print(f"\n💰 API cost: ${result.get('cost', 0):.4f}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    """Run keyword research examples"""

    # Check configuration
    if not Config.DATAFORSEO_LOGIN:
        print("⚠️  Warning: DataForSEO not configured")
        print("   Add DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD to .env")
        print()

    print("""
Choose an example:
1. Keyword ideas (expand seeds)
2. Domain keywords (find what a domain ranks for)
3. Search volume check (get metrics for keywords)
4. SERP check (see top 10 results)
5. Run all demos
    """)

    choice = input("Enter choice (1-5): ").strip()

    if choice == '1':
        await keyword_ideas_demo()
    elif choice == '2':
        await domain_keywords_demo()
    elif choice == '3':
        await search_volume_demo()
    elif choice == '4':
        await serp_check_demo()
    elif choice == '5':
        await keyword_ideas_demo()
        await domain_keywords_demo()
        await search_volume_demo()
        await serp_check_demo()
    else:
        print("Invalid choice. Running keyword ideas demo...")
        await keyword_ideas_demo()


if __name__ == '__main__':
    asyncio.run(main())
