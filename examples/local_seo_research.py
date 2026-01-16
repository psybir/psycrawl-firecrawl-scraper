#!/usr/bin/env python3
"""
Local SEO Research Script - Dent Sorcery Comprehensive Analysis

This script performs comprehensive local SEO research for Dent Sorcery (dentsorcery.com):
1. Scrapes all website content (16 pages)
2. Gets Google Business Profile data and reviews
3. Runs 8x8 local search grid analysis (~64 points)
4. Discovers and analyzes all competitors
5. Performs keyword research
6. Generates comprehensive reports

Target Business:
- Name: Dent Sorcery
- Address: 3005 Brodhead Rd, Bethlehem, PA 18020
- Service Area: Lehigh Valley (Bethlehem, Allentown, Easton)

Usage:
    python examples/local_seo_research.py

    # Run specific module only:
    python examples/local_seo_research.py --module scrape
    python examples/local_seo_research.py --module grid
    python examples/local_seo_research.py --module competitors
    python examples/local_seo_research.py --module keywords

Estimated runtime: ~30 minutes
Estimated cost: ~$90 DataForSEO + 66 Firecrawl credits
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper import Config, EnhancedFirecrawlClient
from firecrawl_scraper.core.dataforseo_client import DataForSEOClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_error_response(error: Exception, context: str = "") -> Dict:
    """
    Create a standardized error response structure.

    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred

    Returns:
        Dict with standardized error structure
    """
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# CONFIGURATION
# ============================================================================

# Target Business
TARGET_BUSINESS = {
    "name": "Dent Sorcery",
    "domain": "dentsorcery.com",
    "url": "https://dentsorcery.com/",
    "address": "3005 Brodhead Rd, Bethlehem, PA 18020",
    "phone": "610-533-7531",
    "owner": "Michael Acevedo"
}

# Grid Configuration - Centered on Bethlehem, PA
GRID_CONFIG = {
    "center_lat": 40.6259,
    "center_lng": -75.3705,
    "grid_size": 8,  # 8x8 = 64 points
    "spacing_miles": 2.0,  # ~16 mile coverage across Lehigh Valley
    "zoom": 17
}

# Service Keywords (from dentsorcery.com services)
SERVICES = [
    "paintless dent repair",
    "PDR",
    "dent repair",
    "dent removal",
    "door ding repair",
    "hail damage repair",
    "acorn damage repair",
    "mobile dent repair",
    "car dent removal",
    "auto dent repair"
]

# Location Variations
LOCATIONS = [
    "Bethlehem PA",
    "Allentown PA",
    "Easton PA",
    "Lehigh Valley",
    "near me"
]

# Generate keyword combinations
def generate_keywords() -> List[str]:
    """Generate all keyword combinations for research"""
    keywords = []

    # Service + Location combinations
    for service in SERVICES:
        for location in LOCATIONS:
            keywords.append(f"{service} {location}")

    # Standalone searches
    keywords.extend([
        "PDR near me",
        "dent repair near me",
        "paintless dent repair near me",
        "mobile dent repair near me",
        "hail damage repair near me",
        "car dent removal near me"
    ])

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for kw in keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique.append(kw)

    return unique

# Output directory
OUTPUT_DIR = Path(Config.OUTPUT_DIR) / "dentsorcery_research"


# ============================================================================
# DATA COLLECTION FUNCTIONS
# ============================================================================

async def scrape_website(client: EnhancedFirecrawlClient) -> Dict:
    """
    Scrape all pages from dentsorcery.com
    """
    logger.info("="*60)
    logger.info("TASK 1: SCRAPING DENTSORCERY.COM")
    logger.info("="*60)

    output_dir = OUTPUT_DIR / "site_content"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "pages": [],
        "blog_posts": [],
        "structure": {},
        "total_pages": 0,
        "total_words": 0,
        "success": False
    }

    try:
        # Use map strategy to get all URLs first
        logger.info("Mapping site structure...")
        map_result = await client.map(
            url=TARGET_BUSINESS["url"],
            limit=50
        )

        if not map_result.get('success'):
            logger.error(f"Map failed: {map_result.get('error')}")
            return result

        # Get all URLs (links may be dicts with 'url' key or plain strings)
        raw_links = map_result.get('links', [])
        urls = []
        for link in raw_links:
            if isinstance(link, dict):
                url = link.get('url', '')
            else:
                url = str(link)
            # Filter out sitemaps and only include actual pages
            if url and not url.endswith('.xml'):
                urls.append(url)
        logger.info(f"Found {len(urls)} URLs to scrape (filtered from {len(raw_links)} raw links)")

        # Batch scrape all URLs
        if urls:
            logger.info("Batch scraping all pages...")
            scrape_result = await client.batch_scrape(
                urls=urls[:50],  # Limit to 50 pages
                formats=['markdown', 'html']
            )

            if scrape_result.get('success'):
                pages_data = scrape_result.get('data', [])

                for page in pages_data:
                    url = page.get('metadata', {}).get('sourceURL', '')
                    markdown = page.get('markdown', '')
                    html = page.get('html', '')
                    title = page.get('metadata', {}).get('title', '')
                    description = page.get('metadata', {}).get('description', '')

                    page_info = {
                        "url": url,
                        "title": title,
                        "description": description,
                        "word_count": len(markdown.split()) if markdown else 0,
                        "markdown_length": len(markdown) if markdown else 0,
                        "html_length": len(html) if html else 0
                    }

                    # Categorize page
                    if '/blog/' in url:
                        result["blog_posts"].append(page_info)
                        # Save blog post
                        slug = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                        blog_dir = output_dir / "blog"
                        blog_dir.mkdir(exist_ok=True)
                        with open(blog_dir / f"{slug}.md", 'w') as f:
                            f.write(f"# {title}\n\n")
                            f.write(f"URL: {url}\n\n")
                            f.write(markdown or '')
                    else:
                        result["pages"].append(page_info)
                        # Save page
                        pages_dir = output_dir / "pages"
                        pages_dir.mkdir(exist_ok=True)
                        slug = url.replace('https://', '').replace('/', '_').rstrip('_')
                        with open(pages_dir / f"{slug}.md", 'w') as f:
                            f.write(f"# {title}\n\n")
                            f.write(f"URL: {url}\n\n")
                            f.write(markdown or '')

                    result["total_words"] += page_info["word_count"]

                result["total_pages"] = len(pages_data)
                result["success"] = True

                # Save structure
                result["structure"] = {
                    "total_urls": len(urls),
                    "scraped_pages": result["total_pages"],
                    "blog_posts": len(result["blog_posts"]),
                    "main_pages": len(result["pages"]),
                    "urls": urls
                }

                with open(output_dir / "structure.json", 'w') as f:
                    json.dump(result["structure"], f, indent=2)

        logger.info(f"Scraped {result['total_pages']} pages, {result['total_words']:,} words")
        logger.info(f"Blog posts: {len(result['blog_posts'])}, Main pages: {len(result['pages'])}")

    except Exception as e:
        logger.error(f"Website scrape failed: {e}")
        result.update(create_error_response(e, "scrape_website"))

    return result


async def get_gbp_data(client: DataForSEOClient) -> Dict:
    """
    Get Google Business Profile data for Dent Sorcery
    """
    logger.info("="*60)
    logger.info("TASK 2: GETTING GOOGLE BUSINESS PROFILE DATA")
    logger.info("="*60)

    output_dir = OUTPUT_DIR / "local_seo"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "profile": None,
        "reviews": [],
        "qa": [],
        "success": False
    }

    location = "Bethlehem,Pennsylvania,United States"
    search_term = "Dent Sorcery Bethlehem"

    try:
        # Get business profile
        logger.info("Fetching GBP profile...")
        profile_result = await client.business_data_google_my_business_info(
            keyword=search_term,
            location_name=location
        )

        if profile_result.get('success'):
            for task in profile_result.get('data') or []:
                for res in task.get('result') or []:
                    items = res.get('items') or []
                    if items:
                        result["profile"] = items[0]
                        logger.info(f"Found profile: {items[0].get('title', 'Unknown')}")

            with open(output_dir / "gbp_profile.json", 'w') as f:
                json.dump(result["profile"], f, indent=2, default=str)

        await asyncio.sleep(0.5)

        # Get reviews
        logger.info("Fetching reviews...")
        reviews_result = await client.business_data_google_reviews(
            keyword=search_term,
            location_name=location,
            depth=100,
            sort_by="newest"
        )

        if reviews_result.get('success'):
            for task in reviews_result.get('data') or []:
                for res in task.get('result') or []:
                    items = res.get('items') or []
                    result["reviews"] = items
                    logger.info(f"Found {len(items)} reviews")

            with open(output_dir / "reviews.json", 'w') as f:
                json.dump(result["reviews"], f, indent=2, default=str)

        await asyncio.sleep(0.5)

        # Get Q&A
        logger.info("Fetching Q&A...")
        qa_result = await client.business_data_google_questions_answers(
            keyword=search_term,
            location_name=location,
            depth=50
        )

        if qa_result.get('success'):
            for task in qa_result.get('data') or []:
                for res in task.get('result') or []:
                    items = res.get('items') or []
                    result["qa"] = items
                    logger.info(f"Found {len(items)} Q&A items")

            with open(output_dir / "qa.json", 'w') as f:
                json.dump(result["qa"], f, indent=2, default=str)

        result["success"] = True

    except Exception as e:
        logger.error(f"GBP data fetch failed: {e}")
        result.update(create_error_response(e, "get_gbp_data"))

    return result


async def run_local_search_grid(client: DataForSEOClient, keywords: List[str] = None) -> Dict:
    """
    Run 8x8 local search grid analysis
    """
    logger.info("="*60)
    logger.info("TASK 3: RUNNING LOCAL SEARCH GRID ANALYSIS")
    logger.info("="*60)

    output_dir = OUTPUT_DIR / "local_seo"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use top keywords only for grid (to manage costs)
    if keywords is None:
        keywords = [
            "paintless dent repair near me",
            "PDR near me",
            "dent repair near me",
            "mobile dent repair Bethlehem",
            "hail damage repair Lehigh Valley"
        ]

    # Build grid
    grid = client.build_geo_grid(
        center_lat=GRID_CONFIG["center_lat"],
        center_lng=GRID_CONFIG["center_lng"],
        grid_size=GRID_CONFIG["grid_size"],
        spacing_miles=GRID_CONFIG["spacing_miles"]
    )

    logger.info(f"Grid built: {len(grid)} points")
    logger.info(f"Keywords to analyze: {len(keywords)}")
    logger.info(f"Total queries: {len(grid) * len(keywords)}")

    all_results = {
        "grid_config": GRID_CONFIG,
        "grid_points": grid,
        "keywords": keywords,
        "keyword_results": {},
        "all_competitors": {},
        "target_performance": {
            "name": TARGET_BUSINESS["name"],
            "keyword_rankings": {}
        }
    }

    for keyword in keywords:
        logger.info(f"\nAnalyzing keyword: '{keyword}'")

        grid_result = await client.query_local_search_grid(
            keyword=keyword,
            grid_coords=grid,
            language_code="en",
            depth=20,
            delay_between_requests=0.15
        )

        all_results["keyword_results"][keyword] = {
            "grid_results": grid_result.get("grid_results", []),
            "competitors": grid_result.get("competitors", []),
            "total_competitors": grid_result.get("total_competitors_found", 0)
        }

        # Track competitors across all keywords
        for comp in grid_result.get("competitors", []):
            name = comp.get("name", "Unknown")
            if name not in all_results["all_competitors"]:
                all_results["all_competitors"][name] = {
                    "name": name,
                    "rating": comp.get("rating"),
                    "reviews_count": comp.get("reviews_count"),
                    "domain": comp.get("domain"),
                    "phone": comp.get("phone"),
                    "keywords_visible": [],
                    "total_grid_presence": 0,
                    "avg_position_all_keywords": 0
                }

            all_results["all_competitors"][name]["keywords_visible"].append(keyword)
            all_results["all_competitors"][name]["total_grid_presence"] += comp.get("grid_presence", 0)

        # Track target business performance
        for comp in grid_result.get("competitors", []):
            if TARGET_BUSINESS["name"].lower() in comp.get("name", "").lower():
                all_results["target_performance"]["keyword_rankings"][keyword] = {
                    "grid_presence": comp.get("grid_presence"),
                    "avg_position": comp.get("avg_position"),
                    "positions": comp.get("positions", [])
                }
                break

        logger.info(f"  Found {grid_result.get('total_competitors_found', 0)} competitors")

        await asyncio.sleep(1)  # Pause between keywords

    # Calculate aggregate competitor stats
    for name, data in all_results["all_competitors"].items():
        if data["keywords_visible"]:
            data["avg_position_all_keywords"] = data["total_grid_presence"] / len(data["keywords_visible"])

    # Sort competitors by total visibility
    sorted_competitors = sorted(
        all_results["all_competitors"].values(),
        key=lambda x: -x["total_grid_presence"]
    )

    all_results["top_competitors"] = sorted_competitors[:20]

    # Save results
    with open(output_dir / "grid_results.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    # Generate heatmap data for visualization
    heatmap_data = generate_heatmap_data(all_results)
    with open(output_dir / "grid_heatmap.json", 'w') as f:
        json.dump(heatmap_data, f, indent=2)

    logger.info(f"\nGrid analysis complete!")
    logger.info(f"Total competitors discovered: {len(all_results['all_competitors'])}")
    logger.info(f"Top competitor: {sorted_competitors[0]['name'] if sorted_competitors else 'N/A'}")

    return all_results


def generate_heatmap_data(grid_results: Dict) -> Dict:
    """
    Generate heatmap visualization data from grid results
    """
    heatmap = {
        "target_business": TARGET_BUSINESS["name"],
        "keywords": {},
        "grid_config": grid_results.get("grid_config", {})
    }

    for keyword, data in grid_results.get("keyword_results", {}).items():
        keyword_heatmap = []

        for point in data.get("grid_results", []):
            lat = point.get("lat")
            lng = point.get("lng")
            rankings = point.get("rankings", [])

            # Find target business position
            target_position = None
            for rank in rankings:
                if TARGET_BUSINESS["name"].lower() in rank.get("title", "").lower():
                    target_position = rank.get("position")
                    break

            # Color code based on position
            if target_position is None:
                color = "red"  # Not visible
                score = 0
            elif target_position <= 3:
                color = "dark_green"  # Top 3
                score = 100
            elif target_position <= 7:
                color = "light_green"  # Position 4-7
                score = 70
            elif target_position <= 10:
                color = "yellow"  # Position 8-10
                score = 50
            else:
                color = "orange"  # Position 11+
                score = 30

            keyword_heatmap.append({
                "lat": lat,
                "lng": lng,
                "position": target_position,
                "color": color,
                "score": score,
                "top_3": [r.get("title") for r in rankings[:3]]
            })

        # Calculate average position safely (filter out None/missing positions)
        positions_with_values = [p.get("position") for p in keyword_heatmap if p.get("position") is not None]
        avg_position = sum(positions_with_values) / len(positions_with_values) if positions_with_values else None

        # Calculate visibility score safely
        visibility_scores = [p.get("score", 0) for p in keyword_heatmap]
        visibility_score = sum(visibility_scores) / len(visibility_scores) if visibility_scores else 0

        heatmap["keywords"][keyword] = {
            "points": keyword_heatmap,
            "avg_position": avg_position,
            "visibility_score": visibility_score,
            "points_with_visibility": len(positions_with_values),
            "total_points": len(keyword_heatmap)
        }

    return heatmap


async def analyze_competitors(
    dataforseo_client: DataForSEOClient,
    firecrawl_client: EnhancedFirecrawlClient,
    competitors: List[Dict]
) -> Dict:
    """
    Deep analysis of top competitors
    """
    logger.info("="*60)
    logger.info("TASK 4: ANALYZING COMPETITORS")
    logger.info("="*60)

    output_dir = OUTPUT_DIR / "competitors"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "competitors": [],
        "comparison": {},
        "success": False
    }

    # Analyze top 10 competitors
    top_competitors = competitors[:10]
    logger.info(f"Analyzing {len(top_competitors)} top competitors...")

    for i, comp in enumerate(top_competitors, 1):
        name = comp.get("name", "Unknown")
        domain = comp.get("domain")

        logger.info(f"\n[{i}/{len(top_competitors)}] Analyzing: {name}")

        comp_data = {
            "name": name,
            "domain": domain,
            "rating": comp.get("rating"),
            "reviews_count": comp.get("reviews_count"),
            "grid_presence": comp.get("total_grid_presence", 0),
            "gbp_profile": None,
            "reviews": [],
            "backlinks": None,
            "website_scraped": False
        }

        # Get GBP profile
        if name:
            try:
                logger.info(f"  Getting GBP profile...")
                gbp_result = await dataforseo_client.business_data_google_my_business_info(
                    keyword=f"{name} Bethlehem PA",
                    location_name="Bethlehem,Pennsylvania,United States"
                )

                if gbp_result.get('success'):
                    for task in gbp_result.get('data', []):
                        for res in task.get('result', []):
                            items = res.get('items', [])
                            if items:
                                comp_data["gbp_profile"] = items[0]

                await asyncio.sleep(0.3)

                # Get reviews
                logger.info(f"  Getting reviews...")
                reviews_result = await dataforseo_client.business_data_google_reviews(
                    keyword=f"{name} Bethlehem PA",
                    location_name="Bethlehem,Pennsylvania,United States",
                    depth=50
                )

                if reviews_result.get('success'):
                    for task in reviews_result.get('data', []):
                        for res in task.get('result', []):
                            comp_data["reviews"] = res.get('items', [])

                await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"  GBP data failed: {e}")

        # Get backlinks summary if domain available
        if domain:
            try:
                logger.info(f"  Getting backlinks for {domain}...")
                backlinks_result = await dataforseo_client.backlinks_summary(target=domain)

                if backlinks_result.get('success'):
                    for task in backlinks_result.get('data', []):
                        for res in task.get('result', []):
                            comp_data["backlinks"] = res

                await asyncio.sleep(0.3)

                # Scrape website (first 5 pages only to save credits)
                logger.info(f"  Scraping website...")
                scrape_result = await firecrawl_client.scrape(
                    url=f"https://{domain}",
                    formats=['markdown']
                )

                if scrape_result.get('success'):
                    comp_data["website_scraped"] = True
                    comp_data["website_content"] = {
                        "title": scrape_result.get('metadata', {}).get('title'),
                        "description": scrape_result.get('metadata', {}).get('description'),
                        "word_count": len(scrape_result.get('markdown', '').split())
                    }

            except Exception as e:
                logger.error(f"  Website analysis failed: {e}")

        result["competitors"].append(comp_data)

        # Save individual competitor data
        safe_name = name.replace(' ', '_').replace('/', '_')[:50]
        profiles_dir = output_dir / "competitor_profiles"
        profiles_dir.mkdir(exist_ok=True)
        with open(profiles_dir / f"{safe_name}.json", 'w') as f:
            json.dump(comp_data, f, indent=2, default=str)

    # Generate comparison
    result["comparison"] = generate_competitor_comparison(result["competitors"])
    result["success"] = True

    # Save results
    with open(output_dir / "competitor_list.json", 'w') as f:
        json.dump([c.get("name") for c in result["competitors"]], f, indent=2)

    with open(output_dir / "comparison.json", 'w') as f:
        json.dump(result["comparison"], f, indent=2, default=str)

    logger.info(f"\nCompetitor analysis complete!")

    return result


def generate_competitor_comparison(competitors: List[Dict]) -> Dict:
    """
    Generate side-by-side competitor comparison
    """
    comparison = {
        "by_rating": sorted(competitors, key=lambda x: x.get("rating") or 0, reverse=True),
        "by_reviews": sorted(competitors, key=lambda x: x.get("reviews_count") or 0, reverse=True),
        "by_visibility": sorted(competitors, key=lambda x: x.get("grid_presence") or 0, reverse=True),
        "summary": {
            "total_analyzed": len(competitors),
            "avg_rating": sum(c.get("rating") or 0 for c in competitors) / len(competitors) if competitors else 0,
            "avg_reviews": sum(c.get("reviews_count") or 0 for c in competitors) / len(competitors) if competitors else 0,
            "with_websites": sum(1 for c in competitors if c.get("domain")),
        }
    }

    return comparison


async def run_keyword_research(client: DataForSEOClient, keywords: List[str]) -> Dict:
    """
    Perform keyword research
    """
    logger.info("="*60)
    logger.info("TASK 5: KEYWORD RESEARCH")
    logger.info("="*60)

    output_dir = OUTPUT_DIR / "keywords"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "target_keywords": [],
        "keyword_ideas": [],
        "search_volumes": {},
        "success": False
    }

    # Get search volumes for all keywords
    logger.info(f"Getting search volumes for {len(keywords)} keywords...")

    try:
        # Batch in groups of 100
        for i in range(0, len(keywords), 100):
            batch = keywords[i:i+100]

            volume_result = await client.keywords_google_ads(
                keywords=batch,
                location_code=2840,  # USA
                language_code="en"
            )

            if volume_result.get('success'):
                for task in volume_result.get('data', []):
                    for res in task.get('result', []):
                        for item in res.get('items', []) or []:
                            keyword = item.get('keyword', '')
                            result["search_volumes"][keyword] = {
                                "search_volume": item.get('search_volume'),
                                "cpc": item.get('cpc'),
                                "competition": item.get('competition'),
                                "competition_level": item.get('competition_level')
                            }
                            result["target_keywords"].append({
                                "keyword": keyword,
                                **result["search_volumes"][keyword]
                            })

            await asyncio.sleep(0.5)

        # Get keyword ideas from seed keywords
        logger.info("Getting keyword ideas...")
        seed_keywords = ["paintless dent repair", "PDR", "dent repair", "hail damage repair"]

        for seed in seed_keywords:
            ideas_result = await client.labs_keyword_ideas(
                keyword=seed,
                location_code=2840,
                language_code="en",
                limit=50
            )

            if ideas_result.get('success'):
                for task in ideas_result.get('data', []):
                    for res in task.get('result', []):
                        for item in res.get('items', []) or []:
                            result["keyword_ideas"].append({
                                "seed": seed,
                                "keyword": item.get('keyword'),
                                "search_volume": item.get('keyword_info', {}).get('search_volume'),
                                "cpc": item.get('keyword_info', {}).get('cpc'),
                                "competition": item.get('keyword_info', {}).get('competition'),
                                "keyword_difficulty": item.get('keyword_properties', {}).get('keyword_difficulty')
                            })

            await asyncio.sleep(0.5)

        result["success"] = True

        # Sort by search volume
        result["target_keywords"] = sorted(
            result["target_keywords"],
            key=lambda x: x.get("search_volume") or 0,
            reverse=True
        )

        result["keyword_ideas"] = sorted(
            result["keyword_ideas"],
            key=lambda x: x.get("search_volume") or 0,
            reverse=True
        )

        # Save results
        with open(output_dir / "target_keywords.json", 'w') as f:
            json.dump(result["target_keywords"], f, indent=2)

        with open(output_dir / "keyword_ideas.json", 'w') as f:
            json.dump(result["keyword_ideas"], f, indent=2)

        logger.info(f"Keyword research complete!")
        logger.info(f"Target keywords: {len(result['target_keywords'])}")
        logger.info(f"Keyword ideas: {len(result['keyword_ideas'])}")

    except Exception as e:
        logger.error(f"Keyword research failed: {e}")
        result.update(create_error_response(e, "run_keyword_research"))

    return result


def wrap_with_metadata(data: Dict, schema_name: str = "local_seo_research_v1") -> Dict:
    """
    Wrap data with metadata for LLM analysis and versioning.

    Args:
        data: The data to wrap
        schema_name: Schema identifier for the data structure

    Returns:
        Dict with _meta wrapper containing version, timestamp, schema info
    """
    return {
        "_meta": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "schema": schema_name,
            "source": "psycrawl-firecrawl-scraper",
            "generator": "local_seo_research.py"
        },
        "data": data
    }


async def generate_reports(all_data: Dict) -> Dict:
    """
    Generate comprehensive reports from all collected data
    """
    logger.info("="*60)
    logger.info("GENERATING REPORTS")
    logger.info("="*60)

    reports_dir = OUTPUT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Full JSON report with metadata wrapper
    wrapped_data = wrap_with_metadata(all_data, "local_seo_full_report_v1")
    with open(reports_dir / "full_report.json", 'w') as f:
        json.dump(wrapped_data, f, indent=2, default=str)

    # Generate Markdown summary
    md_report = generate_markdown_report(all_data)
    with open(reports_dir / "full_report.md", 'w') as f:
        f.write(md_report)

    # Executive summary
    exec_summary = generate_executive_summary(all_data)
    with open(reports_dir / "executive_summary.md", 'w') as f:
        f.write(exec_summary)

    logger.info(f"Reports saved to {reports_dir}")

    return {"reports_dir": str(reports_dir)}


def generate_markdown_report(data: Dict) -> str:
    """Generate full markdown report"""
    report = []
    report.append("# Dent Sorcery Local SEO Research Report")
    report.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Website Analysis
    if "website" in data:
        report.append("## Website Analysis\n")
        website = data["website"]
        report.append(f"- **Total Pages**: {website.get('total_pages', 0)}")
        report.append(f"- **Total Words**: {website.get('total_words', 0):,}")
        report.append(f"- **Blog Posts**: {len(website.get('blog_posts', []))}")
        report.append("")

    # GBP Data
    if "gbp_data" in data:
        report.append("## Google Business Profile\n")
        gbp = data["gbp_data"]
        if gbp.get("profile"):
            profile = gbp["profile"]
            report.append(f"- **Rating**: {profile.get('rating', {}).get('value', 'N/A')}")
            report.append(f"- **Reviews**: {profile.get('rating', {}).get('votes_count', 'N/A')}")
        report.append(f"- **Total Reviews Retrieved**: {len(gbp.get('reviews', []))}")
        report.append(f"- **Q&A Items**: {len(gbp.get('qa', []))}")
        report.append("")

    # Grid Analysis
    if "grid_results" in data:
        report.append("## Local Search Grid Analysis\n")
        grid = data["grid_results"]
        report.append(f"- **Grid Size**: {grid.get('grid_config', {}).get('grid_size', 0)}x{grid.get('grid_config', {}).get('grid_size', 0)}")
        report.append(f"- **Keywords Analyzed**: {len(grid.get('keywords', []))}")
        report.append(f"- **Total Competitors Found**: {len(grid.get('all_competitors', {}))}")
        report.append("")

        # Top Competitors
        report.append("### Top Competitors by Visibility\n")
        report.append("| Rank | Business | Grid Presence | Rating | Reviews |")
        report.append("|------|----------|---------------|--------|---------|")
        for i, comp in enumerate(grid.get("top_competitors", [])[:10], 1):
            report.append(f"| {i} | {comp.get('name', 'N/A')[:30]} | {comp.get('total_grid_presence', 0)} | {comp.get('rating', 'N/A')} | {comp.get('reviews_count', 'N/A')} |")
        report.append("")

    # Keyword Research
    if "keyword_research" in data:
        report.append("## Keyword Research\n")
        keywords = data["keyword_research"]
        report.append(f"- **Target Keywords**: {len(keywords.get('target_keywords', []))}")
        report.append(f"- **Keyword Ideas**: {len(keywords.get('keyword_ideas', []))}")
        report.append("")

        # Top Keywords
        report.append("### Top Keywords by Search Volume\n")
        report.append("| Keyword | Search Volume | CPC | Competition |")
        report.append("|---------|---------------|-----|-------------|")
        for kw in keywords.get("target_keywords", [])[:15]:
            report.append(f"| {kw.get('keyword', 'N/A')[:40]} | {kw.get('search_volume', 'N/A')} | ${kw.get('cpc', 0) or 0:.2f} | {kw.get('competition_level', 'N/A')} |")
        report.append("")

    return "\n".join(report)


def generate_executive_summary(data: Dict) -> str:
    """Generate executive summary"""
    summary = []
    summary.append("# Executive Summary: Dent Sorcery Local SEO")
    summary.append(f"\n*{datetime.now().strftime('%Y-%m-%d')}*\n")

    summary.append("## Key Findings\n")

    # Visibility
    if "grid_results" in data:
        grid = data["grid_results"]
        target_perf = grid.get("target_performance", {})
        summary.append("### Local Search Visibility")
        summary.append(f"- Analyzed {len(grid.get('keywords', []))} keywords across {grid.get('grid_config', {}).get('grid_size', 0)**2} geographic points")
        summary.append(f"- Discovered {len(grid.get('all_competitors', {}))} competing businesses")
        summary.append("")

    # Competition
    if "competitors" in data:
        comps = data["competitors"].get("competitors", [])
        if comps:
            summary.append("### Competition Analysis")
            summary.append(f"- Analyzed {len(comps)} top competitors in detail")
            avg_rating = sum(c.get("rating") or 0 for c in comps) / len(comps) if comps else 0
            summary.append(f"- Average competitor rating: {avg_rating:.1f}")
            summary.append("")

    # Content
    if "website" in data:
        website = data["website"]
        summary.append("### Content Analysis")
        summary.append(f"- {website.get('total_pages', 0)} pages scraped")
        summary.append(f"- {website.get('total_words', 0):,} total words")
        summary.append(f"- {len(website.get('blog_posts', []))} blog posts")
        summary.append("")

    summary.append("## Recommendations\n")
    summary.append("1. **Expand local content** - Create location-specific pages for each service area")
    summary.append("2. **Review generation** - Implement systematic review request process")
    summary.append("3. **Blog optimization** - Target identified keyword opportunities")
    summary.append("4. **Technical SEO** - Ensure schema markup and local signals are optimized")
    summary.append("")

    summary.append("---")
    summary.append(f"\n*Full data available in `/data/dentsorcery_research/`*")

    return "\n".join(summary)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Run complete local SEO research"""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DENT SORCERY LOCAL SEO RESEARCH                           ║
║                  Comprehensive Analysis for Website Rebuild                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    start_time = time.time()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize clients
    logger.info("Initializing API clients...")
    firecrawl = EnhancedFirecrawlClient(Config.API_KEY)

    try:
        dataforseo = DataForSEOClient(
            login=Config.DATAFORSEO_LOGIN,
            password=Config.DATAFORSEO_PASSWORD
        )
    except Exception as e:
        logger.error(f"DataForSEO initialization failed: {e}")
        logger.info("Continuing with Firecrawl only...")
        dataforseo = None

    # Generate keywords
    keywords = generate_keywords()
    logger.info(f"Generated {len(keywords)} target keywords")

    # Collect all data
    all_data = {
        "target_business": TARGET_BUSINESS,
        "generated_at": datetime.now().isoformat(),
        "keywords": keywords
    }

    # Task 1: Scrape website
    logger.info("\n" + "="*60)
    all_data["website"] = await scrape_website(firecrawl)

    if dataforseo:
        # Task 2: Get GBP data
        all_data["gbp_data"] = await get_gbp_data(dataforseo)

        # Task 3: Run grid analysis (with subset of keywords to manage costs)
        grid_keywords = [
            "paintless dent repair near me",
            "PDR near me",
            "dent repair Bethlehem PA",
            "hail damage repair Lehigh Valley",
            "mobile dent repair near me"
        ]
        all_data["grid_results"] = await run_local_search_grid(dataforseo, grid_keywords)

        # Task 4: Analyze competitors
        top_competitors = all_data["grid_results"].get("top_competitors", [])
        if top_competitors:
            all_data["competitors"] = await analyze_competitors(
                dataforseo, firecrawl, top_competitors
            )

        # Task 5: Keyword research
        all_data["keyword_research"] = await run_keyword_research(dataforseo, keywords[:50])

        # Get API stats
        all_data["api_stats"] = {
            "dataforseo": dataforseo.get_stats(),
            "firecrawl": firecrawl.get_stats() if hasattr(firecrawl, 'get_stats') else {}
        }

    # Generate reports
    await generate_reports(all_data)

    # Summary
    elapsed = time.time() - start_time
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           RESEARCH COMPLETE                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Total Time: {elapsed/60:.1f} minutes
║  Output Directory: {OUTPUT_DIR}
║
║  Data Collected:
║    - Website pages: {all_data.get('website', {}).get('total_pages', 0)}
║    - Competitors found: {len(all_data.get('grid_results', {}).get('all_competitors', {}))}
║    - Keywords researched: {len(all_data.get('keyword_research', {}).get('target_keywords', []))}
║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    if dataforseo:
        print(f"DataForSEO Cost: ${dataforseo.stats.total_cost:.4f}")


if __name__ == '__main__':
    # Check for command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Dent Sorcery Local SEO Research')
    parser.add_argument('--module', choices=['scrape', 'grid', 'competitors', 'keywords', 'all'],
                        default='all', help='Run specific module only')
    args = parser.parse_args()

    asyncio.run(main())
