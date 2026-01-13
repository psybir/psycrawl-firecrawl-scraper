#!/usr/bin/env python3
"""
Competitor Analysis Example - SEO Competitive Intelligence

Demonstrates competitor analysis capabilities:
- Auto-discover competitors
- Compare domain metrics
- Find content gaps
- Identify keyword opportunities

Usage:
    python examples/competitor_analysis_example.py

Requirements:
    - DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in .env
    - DATAFORSEO_ENABLED=true in .env
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper import SEOOrchestrator, Config


async def discover_competitors():
    """
    Auto-discover competitors for a domain.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPETITOR DISCOVERY                                       ║
║           Find Your Top Organic Search Competitors                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    seo = SEOOrchestrator()

    domain = input("Enter your domain (e.g., mysite.com): ").strip()
    if not domain:
        domain = "shopify.com"

    print(f"\n🔍 Discovering competitors for {domain}...")
    print("-" * 60)

    analysis = await seo.competitor_analysis(
        domain=domain,
        competitors=None,  # Auto-discover
        find_competitors=True,
        max_competitors=5,
        save_report=True
    )

    print(f"\n📊 COMPETITORS FOUND FOR {domain.upper()}")
    print("-" * 60)

    if analysis.competitors:
        print(f"\n{'Competitor':<30} {'Rank':<10} {'Traffic':<15} {'Keywords':<12} {'Common KW':<10}")
        print("-" * 77)

        for comp in analysis.competitors:
            name = comp.domain[:29]
            rank = comp.rank or 'N/A'
            traffic = f"{comp.organic_traffic:,}" if comp.organic_traffic else 'N/A'
            keywords = f"{comp.organic_keywords:,}" if comp.organic_keywords else 'N/A'
            common = comp.common_keywords or 0
            print(f"{name:<30} {str(rank):<10} {traffic:<15} {keywords:<12} {common:<10}")

    # Show keyword gaps
    if analysis.keyword_gaps:
        print(f"\n🎯 KEYWORD GAPS ({len(analysis.keyword_gaps)} found)")
        print("Keywords your competitors rank for, but you don't:")
        print("-" * 40)
        for kw in analysis.keyword_gaps[:10]:
            print(f"   • {kw.keyword}")

    print(f"\n📁 Full report saved to: {Config.SEO_OUTPUT_DIR}")


async def compare_domains():
    """
    Compare specific domains side by side.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DOMAIN COMPARISON                                          ║
║              Compare Multiple Domains Side by Side                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    seo = SEOOrchestrator()

    your_domain = input("Enter your domain: ").strip()
    if not your_domain:
        your_domain = "mysite.com"

    competitors_input = input("Enter competitor domains (comma-separated): ").strip()
    if not competitors_input:
        competitors_input = "competitor1.com, competitor2.com"

    competitors = [c.strip() for c in competitors_input.split(',')]
    all_domains = [your_domain] + competitors

    print(f"\n🔍 Comparing {len(all_domains)} domains...")
    print("-" * 60)

    # Get metrics for all domains
    results = await seo.batch_quick_audit(all_domains, max_concurrent=3)

    # Print comparison
    print(f"\n{'Domain':<25} {'Rank':<10} {'Backlinks':<15} {'Ref Domains':<15}")
    print("=" * 65)

    # Find your domain's position
    your_result = next((r for r in results if r.get('domain') == your_domain), None)

    for r in sorted(results, key=lambda x: x.get('domain_rank') or 999):
        domain = r.get('domain', 'N/A')[:24]
        rank = r.get('domain_rank') or 'N/A'
        backlinks = f"{r.get('backlinks') or 0:,}"
        ref_domains = r.get('referring_domains') or 'N/A'

        # Highlight your domain
        prefix = "→ " if r.get('domain') == your_domain else "  "
        print(f"{prefix}{domain:<23} {str(rank):<10} {backlinks:<15} {str(ref_domains):<15}")

    # Analysis
    if your_result:
        your_rank = your_result.get('domain_rank') or 999
        better_count = sum(1 for r in results if (r.get('domain_rank') or 999) < your_rank)
        print(f"\n📊 Analysis:")
        print(f"   Your rank: {your_rank}")
        print(f"   Competitors with better rank: {better_count}/{len(competitors)}")


async def content_gap_demo():
    """
    Find content gaps between domains.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONTENT GAP ANALYSIS                                       ║
║         Find Keywords Competitors Rank For That You Don't                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    seo = SEOOrchestrator()

    your_domain = input("Enter your domain: ").strip()
    if not your_domain:
        your_domain = "mysite.com"

    competitors_input = input("Enter competitor domains (comma-separated, max 3): ").strip()
    if not competitors_input:
        competitors_input = "competitor1.com, competitor2.com"

    competitors = [c.strip() for c in competitors_input.split(',')][:3]

    print(f"\n🔍 Analyzing content gaps...")
    print(f"   Your domain: {your_domain}")
    print(f"   Competitors: {', '.join(competitors)}")
    print("-" * 60)

    results = await seo.content_gap_analysis(
        domain=your_domain,
        competitors=competitors,
        save_report=True
    )

    # Content Gaps
    print(f"\n🎯 CONTENT GAPS ({len(results.get('content_gaps', []))} keywords)")
    print("Keywords competitors rank for, but you don't:")
    print("-" * 60)
    print(f"{'Keyword':<40} {'Search Vol':<12} {'Comp Position':<15}")
    print("-" * 67)

    for gap in results.get('content_gaps', [])[:15]:
        kw = gap.get('keyword', '')[:39]
        vol = f"{gap.get('search_volume', 0):,}"
        pos = gap.get('competitor_position') or 'N/A'
        print(f"{kw:<40} {vol:<12} {str(pos):<15}")

    # Quick Wins
    print(f"\n⚡ QUICK WINS ({len(results.get('quick_wins', []))} keywords)")
    print("Keywords where you rank but could rank higher:")
    print("-" * 60)

    for qw in results.get('quick_wins', [])[:10]:
        kw = qw.get('keyword', '')[:39]
        your_pos = qw.get('our_position') or 'N/A'
        comp_pos = qw.get('competitor_position') or 'N/A'
        print(f"   {kw}: Your position {your_pos} vs competitor {comp_pos}")

    print(f"\n📁 Full report saved to: {Config.SEO_OUTPUT_DIR}")
    print(f"💰 Total API cost: ${results.get('cost', 0):.4f}")


async def main():
    """Run competitor analysis examples"""

    # Check configuration
    if not Config.DATAFORSEO_LOGIN:
        print("⚠️  Warning: DataForSEO not configured")
        print("   Add DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD to .env")
        print()

    print("""
Choose an example:
1. Discover competitors (auto-find competitors)
2. Compare specific domains
3. Content gap analysis
4. Run all demos
    """)

    choice = input("Enter choice (1-4): ").strip()

    if choice == '1':
        await discover_competitors()
    elif choice == '2':
        await compare_domains()
    elif choice == '3':
        await content_gap_demo()
    elif choice == '4':
        await discover_competitors()
        await compare_domains()
        await content_gap_demo()
    else:
        print("Invalid choice. Running competitor discovery...")
        await discover_competitors()


if __name__ == '__main__':
    asyncio.run(main())
