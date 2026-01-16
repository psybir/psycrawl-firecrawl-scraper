#!/usr/bin/env python3
"""
Mode 2: DataForSEO Only Example

Demonstrates SEO research capabilities without website scraping.
Use this when you need keyword data, backlinks, or local search analysis.

Features:
- Keyword search volume and CPC data
- Backlinks analysis
- Local search grid analysis
- Google Business Profile data
- Competitor discovery

Cost: ~$0.03-0.10 per query (varies by endpoint)

Usage:
    python examples/dataforseo_only_example.py

    # Specific features:
    python examples/dataforseo_only_example.py --feature keywords
    python examples/dataforseo_only_example.py --feature backlinks --domain example.com
    python examples/dataforseo_only_example.py --feature grid --lat 40.6259 --lng -75.3705
    python examples/dataforseo_only_example.py --feature gbp --business "Business Name"
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

from firecrawl_scraper import Config
from firecrawl_scraper.core.dataforseo_client import DataForSEOClient

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
            "generator": "dataforseo_only_example.py"
        },
        "data": data
    }


async def keyword_research(client: DataForSEOClient, keywords: List[str]) -> Dict:
    """
    Get keyword search volumes and competition data.

    Args:
        client: DataForSEO client
        keywords: List of keywords to research

    Returns:
        Dict with keyword data
    """
    logger.info(f"Researching {len(keywords)} keywords...")

    result = {
        "keywords": [],
        "success": False
    }

    volume_result = await client.keywords_google_ads(
        keywords=keywords,
        location_code=2840,  # USA
        language_code="en"
    )

    if volume_result.get('success'):
        for task in volume_result.get('data') or []:
            for res in task.get('result') or []:
                for item in res.get('items') or []:
                    result["keywords"].append({
                        "keyword": item.get('keyword', ''),
                        "search_volume": item.get('search_volume'),
                        "cpc": item.get('cpc'),
                        "competition": item.get('competition'),
                        "competition_level": item.get('competition_level')
                    })

        result["keywords"] = sorted(
            result["keywords"],
            key=lambda x: x.get("search_volume") or 0,
            reverse=True
        )
        result["success"] = True
        logger.info(f"Found data for {len(result['keywords'])} keywords")

    return result


async def backlinks_analysis(client: DataForSEOClient, domain: str) -> Dict:
    """
    Analyze backlinks for a domain.

    Args:
        client: DataForSEO client
        domain: Domain to analyze

    Returns:
        Dict with backlinks data
    """
    logger.info(f"Analyzing backlinks for: {domain}")

    result = {
        "domain": domain,
        "summary": None,
        "top_backlinks": [],
        "success": False
    }

    # Get summary
    summary_result = await client.backlinks_summary(target=domain)

    if summary_result.get('success'):
        for task in summary_result.get('data') or []:
            for res in task.get('result') or []:
                result["summary"] = {
                    "total_backlinks": res.get('backlinks'),
                    "referring_domains": res.get('referring_domains'),
                    "referring_main_domains": res.get('referring_main_domains'),
                    "rank": res.get('rank'),
                    "spam_score": res.get('backlinks_spam_score'),
                    "broken_backlinks": res.get('broken_backlinks')
                }
                logger.info(f"  Backlinks: {res.get('backlinks', 0):,}")
                logger.info(f"  Referring domains: {res.get('referring_domains', 0):,}")

    await asyncio.sleep(0.3)

    # Get top backlinks
    backlinks_result = await client.backlinks_backlinks(
        target=domain,
        limit=20,
        order_by="rank,desc"
    )

    if backlinks_result.get('success'):
        for task in backlinks_result.get('data') or []:
            for res in task.get('result') or []:
                for item in res.get('items') or []:
                    result["top_backlinks"].append({
                        "url_from": item.get('url_from'),
                        "url_to": item.get('url_to'),
                        "anchor": item.get('anchor'),
                        "rank": item.get('rank'),
                        "domain_from": item.get('domain_from'),
                        "is_new": item.get('is_new'),
                        "is_lost": item.get('is_lost')
                    })

    result["success"] = True
    return result


async def local_search_grid(
    client: DataForSEOClient,
    keyword: str,
    lat: float,
    lng: float,
    grid_size: int = 3
) -> Dict:
    """
    Run local search grid analysis.

    Args:
        client: DataForSEO client
        keyword: Search keyword
        lat: Center latitude
        lng: Center longitude
        grid_size: Grid size (e.g., 3 for 3x3)

    Returns:
        Dict with grid results
    """
    logger.info(f"Running {grid_size}x{grid_size} grid for: '{keyword}'")

    # Build grid
    grid = client.build_geo_grid(
        center_lat=lat,
        center_lng=lng,
        grid_size=grid_size,
        spacing_miles=2.0
    )

    logger.info(f"Grid has {len(grid)} points")

    # Query grid
    grid_result = await client.query_local_search_grid(
        keyword=keyword,
        grid_coords=grid,
        depth=15,
        delay_between_requests=0.1
    )

    result = {
        "keyword": keyword,
        "center": {"lat": lat, "lng": lng},
        "grid_size": grid_size,
        "total_points": len(grid),
        "total_competitors": grid_result.get("total_competitors_found", 0),
        "top_competitors": grid_result.get("competitors", [])[:10],
        "success": True
    }

    logger.info(f"Found {result['total_competitors']} competitors")

    return result


async def gbp_data(client: DataForSEOClient, business_name: str, location: str) -> Dict:
    """
    Get Google Business Profile data.

    Args:
        client: DataForSEO client
        business_name: Business name to search
        location: Location string

    Returns:
        Dict with GBP data
    """
    logger.info(f"Getting GBP data for: {business_name}")

    result = {
        "business_name": business_name,
        "profile": None,
        "reviews": [],
        "qa": [],
        "success": False
    }

    # Get profile
    profile_result = await client.business_data_google_my_business_info(
        keyword=business_name,
        location_name=location
    )

    if profile_result.get('success'):
        for task in profile_result.get('data') or []:
            for res in task.get('result') or []:
                items = res.get('items') or []
                if items:
                    result["profile"] = items[0]
                    logger.info(f"  Found: {items[0].get('title', 'N/A')}")

    await asyncio.sleep(0.3)

    # Get reviews
    reviews_result = await client.business_data_google_reviews(
        keyword=business_name,
        location_name=location,
        depth=50,
        sort_by="newest"
    )

    if reviews_result.get('success'):
        for task in reviews_result.get('data') or []:
            for res in task.get('result') or []:
                result["reviews"] = res.get('items') or []
                logger.info(f"  Reviews: {len(result['reviews'])}")

    await asyncio.sleep(0.3)

    # Get Q&A
    qa_result = await client.business_data_google_questions_answers(
        keyword=business_name,
        location_name=location,
        depth=20
    )

    if qa_result.get('success'):
        for task in qa_result.get('data') or []:
            for res in task.get('result') or []:
                result["qa"] = res.get('items') or []
                logger.info(f"  Q&A: {len(result['qa'])}")

    result["success"] = True
    return result


async def run_all_features(client: DataForSEOClient) -> Dict:
    """Run a demo of all features."""
    logger.info("Running all feature demo...")

    result = {
        "keywords": None,
        "backlinks": None,
        "grid": None,
        "gbp": None
    }

    # Keywords
    result["keywords"] = await keyword_research(
        client,
        ["paintless dent repair", "PDR near me", "dent removal", "hail damage repair"]
    )

    await asyncio.sleep(0.5)

    # Backlinks (using example domain)
    result["backlinks"] = await backlinks_analysis(client, "example.com")

    await asyncio.sleep(0.5)

    # Local grid (small for demo)
    result["grid"] = await local_search_grid(
        client,
        keyword="dent repair near me",
        lat=40.6259,
        lng=-75.3705,
        grid_size=3
    )

    await asyncio.sleep(0.5)

    # GBP (example search)
    result["gbp"] = await gbp_data(
        client,
        "Dent Sorcery",
        "Bethlehem,Pennsylvania,United States"
    )

    return result


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='DataForSEO Only Example')
    parser.add_argument('--feature', choices=['all', 'keywords', 'backlinks', 'grid', 'gbp'],
                        default='all', help='Feature to demonstrate')
    parser.add_argument('--keywords', nargs='+',
                        default=['paintless dent repair', 'PDR', 'dent removal'],
                        help='Keywords for research')
    parser.add_argument('--domain', default='example.com',
                        help='Domain for backlinks analysis')
    parser.add_argument('--lat', type=float, default=40.6259,
                        help='Latitude for grid')
    parser.add_argument('--lng', type=float, default=-75.3705,
                        help='Longitude for grid')
    parser.add_argument('--grid-size', type=int, default=3,
                        help='Grid size')
    parser.add_argument('--business', default='Dent Sorcery',
                        help='Business name for GBP')
    parser.add_argument('--location', default='Bethlehem,Pennsylvania,United States',
                        help='Location for GBP search')
    parser.add_argument('--output', help='Output file path')
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  MODE 2: DATAFORSEO ONLY - SEO Research                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize client
    client = DataForSEOClient(
        login=Config.DATAFORSEO_LOGIN,
        password=Config.DATAFORSEO_PASSWORD
    )

    # Run selected feature
    if args.feature == 'keywords':
        result = await keyword_research(client, args.keywords)
    elif args.feature == 'backlinks':
        result = await backlinks_analysis(client, args.domain)
    elif args.feature == 'grid':
        result = await local_search_grid(
            client, args.keywords[0], args.lat, args.lng, args.grid_size
        )
    elif args.feature == 'gbp':
        result = await gbp_data(client, args.business, args.location)
    else:  # all
        result = await run_all_features(client)

    # Print cost stats
    stats = client.get_stats()
    print(f"\nAPI Usage:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Success rate: {stats['success_rate']}")
    print(f"  Total cost: {stats['total_cost']}")

    # Save output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(Config.OUTPUT_DIR) / "dataforseo_example_output.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(wrap_with_metadata(result, f"dataforseo_{args.feature}_v1"), f, indent=2, default=str)

    print(f"\nOutput saved to: {output_path}")


if __name__ == '__main__':
    asyncio.run(main())
