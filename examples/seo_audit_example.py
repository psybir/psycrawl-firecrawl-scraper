#!/usr/bin/env python3
"""
SEO Audit Example - Comprehensive SEO Analysis

Demonstrates the Ultimate SEO Machine capabilities:
- Full domain SEO audit
- Content analysis with Firecrawl
- Backlinks analysis with DataForSEO
- Technical SEO audit
- Automated recommendations

Usage:
    python examples/seo_audit_example.py

Requirements:
    - FIRECRAWL_API_KEY in .env
    - DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in .env
    - DATAFORSEO_ENABLED=true in .env
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper import SEOOrchestrator, Config


async def quick_audit_demo():
    """
    Quick audit - fast check of domain metrics.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         QUICK SEO AUDIT                                       ║
║              Fast Domain Metrics Check (< 5 seconds)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    seo = SEOOrchestrator()

    # Show API status
    status = seo.get_api_status()
    print("📡 API Status:")
    print(f"   Firecrawl: {'✅ Configured' if status['firecrawl']['configured'] else '❌ Not configured'}")
    print(f"   DataForSEO: {'✅ Configured' if status['dataforseo']['configured'] else '❌ Not configured'}")
    print()

    domain = input("Enter domain to audit (e.g., example.com): ").strip()
    if not domain:
        domain = "example.com"

    print(f"\n🔍 Running quick audit for {domain}...")
    print("-" * 60)

    result = await seo.quick_audit(domain)

    print(f"""
📊 QUICK AUDIT RESULTS: {domain}
{'-' * 40}
   Domain Rank:       {result.get('domain_rank') or 'N/A'}
   Total Backlinks:   {result.get('backlinks') or 'N/A':,}
   Referring Domains: {result.get('referring_domains') or 'N/A'}
   Organic Keywords:  {result.get('organic_keywords') or 'N/A'}
   API Cost:          ${result.get('cost', 0):.4f}
{'-' * 40}
    """)


async def full_audit_demo():
    """
    Full SEO audit with all modules.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        FULL SEO AUDIT                                         ║
║          Comprehensive Analysis with Firecrawl + DataForSEO                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    seo = SEOOrchestrator()

    domain = input("Enter domain to audit (e.g., example.com): ").strip()
    if not domain:
        domain = "docs.python.org"

    # Optional: Track specific keywords
    keywords_input = input("Enter keywords to track (comma-separated, or press Enter to skip): ").strip()
    keywords = [k.strip() for k in keywords_input.split(',')] if keywords_input else None

    max_pages = int(input("Max pages to crawl (default 50): ").strip() or "50")

    print(f"\n🚀 Starting full SEO audit for {domain}")
    print(f"   Keywords: {keywords or 'None'}")
    print(f"   Max pages: {max_pages}")
    print("-" * 60)
    print("⏳ This may take 2-5 minutes depending on site size...")
    print()

    report = await seo.full_seo_audit(
        domain=domain,
        keywords=keywords,
        max_pages=max_pages,
        include_modules=['content', 'backlinks', 'onpage'] + (['serp'] if keywords else []),
        save_report=True
    )

    # Print summary
    print("\n" + "=" * 60)
    print(report.generate_summary())
    print("=" * 60)

    # Print top recommendations
    if report.recommendations:
        print("\n🎯 TOP RECOMMENDATIONS:")
        print("-" * 40)
        for i, rec in enumerate(report.recommendations[:5], 1):
            print(f"{i}. [{rec.priority.value.upper()}] {rec.issue}")
            print(f"   → {rec.recommendation}")
            print()

    print(f"\n📁 Full report saved to: {Config.SEO_OUTPUT_DIR}")


async def batch_audit_demo():
    """
    Batch quick audit for multiple domains.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      BATCH DOMAIN AUDIT                                       ║
║            Compare Multiple Domains Side by Side                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    seo = SEOOrchestrator()

    domains_input = input("Enter domains (comma-separated): ").strip()
    if not domains_input:
        domains_input = "google.com, amazon.com, github.com"

    domains = [d.strip() for d in domains_input.split(',')]

    print(f"\n🔍 Auditing {len(domains)} domains...")
    print("-" * 60)

    results = await seo.batch_quick_audit(domains, max_concurrent=3)

    # Print comparison table
    print(f"\n{'Domain':<25} {'Rank':<10} {'Backlinks':<15} {'Ref Domains':<15}")
    print("-" * 65)

    for r in sorted(results, key=lambda x: x.get('domain_rank') or 999):
        domain = r.get('domain', 'N/A')[:24]
        rank = r.get('domain_rank') or 'N/A'
        backlinks = f"{r.get('backlinks') or 0:,}"
        ref_domains = r.get('referring_domains') or 'N/A'
        print(f"{domain:<25} {str(rank):<10} {backlinks:<15} {str(ref_domains):<15}")

    total_cost = sum(r.get('cost', 0) for r in results)
    print("-" * 65)
    print(f"Total API Cost: ${total_cost:.4f}")


async def check_configuration():
    """
    Check if API keys are configured.
    """
    print("\n📋 Configuration Check")
    print("-" * 40)

    # Check Firecrawl
    if Config.API_KEY:
        print(f"✅ Firecrawl API Key: ...{Config.API_KEY[-8:]}")
    else:
        print("❌ Firecrawl API Key: NOT SET")

    # Check DataForSEO
    if Config.DATAFORSEO_LOGIN and Config.DATAFORSEO_PASSWORD:
        print(f"✅ DataForSEO Login: {Config.DATAFORSEO_LOGIN}")
        print(f"✅ DataForSEO Enabled: {Config.DATAFORSEO_ENABLED}")
    else:
        print("❌ DataForSEO: NOT CONFIGURED")
        print("   Add DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD to .env")

    # Check modules
    print("\n📦 SEO Modules:")
    print(f"   SERP: {'✅' if Config.SEO_SERP_ENABLED else '❌'}")
    print(f"   Keywords: {'✅' if Config.SEO_KEYWORDS_ENABLED else '❌'}")
    print(f"   Backlinks: {'✅' if Config.SEO_BACKLINKS_ENABLED else '❌'}")
    print(f"   OnPage: {'✅' if Config.SEO_ONPAGE_ENABLED else '❌'}")
    print(f"   Labs: {'✅' if Config.SEO_LABS_ENABLED else '❌'}")

    print(f"\n📁 Output Directory: {Config.SEO_OUTPUT_DIR}")
    print("-" * 40)


async def main():
    """Run SEO audit examples"""

    await check_configuration()

    print("""
Choose an example:
1. Quick audit (fast domain metrics)
2. Full SEO audit (comprehensive analysis)
3. Batch audit (compare multiple domains)
4. Check configuration
    """)

    choice = input("Enter choice (1-4): ").strip()

    if choice == '1':
        await quick_audit_demo()
    elif choice == '2':
        await full_audit_demo()
    elif choice == '3':
        await batch_audit_demo()
    elif choice == '4':
        await check_configuration()
    else:
        print("Invalid choice. Running quick audit...")
        await quick_audit_demo()


if __name__ == '__main__':
    asyncio.run(main())
