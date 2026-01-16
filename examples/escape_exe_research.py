#!/usr/bin/env python3
"""
escape.exe Local SEO Research - Comprehensive Market Analysis

This script performs comprehensive local SEO research for escape.exe (escapeexe.com):
1. Scrapes all website content (experiences, booking, about, contact)
2. Gets Google Business Profile data and 400+ reviews
3. Runs 10x10 local search grid analysis (100 points, 60-mile radius)
4. Discovers and analyzes all competitors in the area
5. Performs keyword research for escape room terms
6. Web research for awards, news, and third-party reviews
7. Generates comprehensive reports

Target Business:
- Name: escape.exe
- Website: escapeexe.com
- Location: Bethlehem, PA 18020 (Lehigh Valley)
- Specialty: Next-Gen Immersive Escape Room Experience
- Awards: Top Escape Room Nominee

Usage:
    python examples/escape_exe_research.py

    # Run specific module only:
    python examples/escape_exe_research.py --module scrape
    python examples/escape_exe_research.py --module gbp
    python examples/escape_exe_research.py --module grid
    python examples/escape_exe_research.py --module competitors
    python examples/escape_exe_research.py --module keywords
    python examples/escape_exe_research.py --module web

Estimated runtime: ~30 minutes
Estimated cost: ~$3.50 DataForSEO + 20 Firecrawl credits
"""

import asyncio
import json
import logging
import os
import sys
import time
import re
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
    """Create a standardized error response structure."""
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }


def wrap_with_metadata(data: Dict, schema_name: str = "escape_exe_research_v1") -> Dict:
    """Wrap data with metadata for LLM analysis."""
    return {
        "_meta": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "schema": schema_name,
            "source": "psycrawl-firecrawl-scraper",
            "generator": "escape_exe_research.py",
            "business": "escape.exe",
            "purpose": "local_seo_research_website_redesign"
        },
        "data": data
    }


# ============================================================================
# CONFIGURATION
# ============================================================================

# Target Business
TARGET_BUSINESS = {
    "name": "escape.exe",
    "domain": "escapeexe.com",
    "url": "https://escapeexe.com/",
    "address": "Bethlehem, PA 18020",
    "description": "Next-Gen Immersive Escape Room Experience",
    "features": [
        "GAVIN AI Character",
        "KT AI Character",
        "Multiple Narrative Pathways",
        "Adaptive Difficulty",
        "Top Escape Room Nominee"
    ],
    "booking_system": "Resova"
}

# Grid Configuration - 60-mile radius centered on Bethlehem, PA
# Covers: Lehigh Valley, Reading, Pocono edge, NJ border, Philadelphia metro edge
GRID_CONFIG = {
    "center_lat": 40.6259,   # Bethlehem, PA
    "center_lng": -75.3705,
    "grid_size": 10,         # 10x10 = 100 points
    "spacing_miles": 6.0,    # ~60 mile coverage
    "zoom": 17
}

# Service Keywords (escape room industry)
SERVICES = [
    "escape room",
    "immersive escape room",
    "team building escape room",
    "puzzle room",
    "escape game",
    "horror escape room",
    "adventure escape room",
    "VR escape room",
    "interactive escape room",
    "mystery room"
]

# Location Variations
LOCATIONS = [
    "Bethlehem PA",
    "Lehigh Valley",
    "Allentown PA",
    "Easton PA",
    "near me",
    "Reading PA",
    "Philadelphia area",
    "Poconos"
]

# Primary grid keywords (for 60-mile analysis)
PRIMARY_GRID_KEYWORDS = [
    "escape room near me",
    "escape room Lehigh Valley",
    "immersive escape room",
    "team building escape room",
    "best escape room PA"
]

# Web research queries
WEB_RESEARCH_QUERIES = [
    "escape.exe Bethlehem reviews",
    "escape.exe award winning",
    "best escape rooms Pennsylvania 2024 2025",
    "Lehigh Valley escape room news",
    "escape.exe morty.app",
    "top escape rooms northeast",
    "escape.exe GAVIN KT"
]

# Output directory
OUTPUT_DIR = Path(Config.OUTPUT_DIR) / "escape_exe_research"


def generate_keywords() -> List[str]:
    """Generate all keyword combinations for research"""
    keywords = []

    # Service + Location combinations
    for service in SERVICES:
        for location in LOCATIONS:
            keywords.append(f"{service} {location}")

    # Standalone searches
    keywords.extend([
        "escape room near me",
        "best escape room near me",
        "scary escape room near me",
        "fun escape room near me",
        "corporate team building escape room",
        "birthday party escape room",
        "group activities near me",
        "date night ideas Lehigh Valley",
        "things to do Bethlehem PA",
        "entertainment Lehigh Valley"
    ])

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for kw in keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique.append(kw)

    return unique


# ============================================================================
# DATA COLLECTION FUNCTIONS
# ============================================================================

async def scrape_website(client: EnhancedFirecrawlClient) -> Dict:
    """Scrape all pages from escapeexe.com"""
    logger.info("=" * 60)
    logger.info("TASK 1: SCRAPING ESCAPEEXE.COM")
    logger.info("=" * 60)

    output_dir = OUTPUT_DIR / "site_content"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "pages": [],
        "experiences": [],
        "structure": {},
        "total_pages": 0,
        "total_words": 0,
        "media_inventory": [],
        "success": False
    }

    try:
        # Map site structure
        logger.info("Mapping site structure...")
        map_result = await client.map(
            url=TARGET_BUSINESS["url"],
            limit=50
        )

        if not map_result.get('success'):
            logger.error(f"Map failed: {map_result.get('error')}")
            return result

        # Extract URLs
        raw_links = map_result.get('links', [])
        urls = []
        for link in raw_links:
            if isinstance(link, dict):
                url = link.get('url', '')
            else:
                url = str(link)
            if url and not url.endswith('.xml'):
                urls.append(url)

        logger.info(f"Found {len(urls)} URLs to scrape")

        # Batch scrape all URLs
        if urls:
            logger.info("Batch scraping all pages...")
            scrape_result = await client.batch_scrape(
                urls=urls[:50],
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

                    # Categorize pages
                    if '/experience' in url.lower() or '/room' in url.lower():
                        result["experiences"].append(page_info)
                        # Save experience page
                        exp_dir = output_dir / "experiences"
                        exp_dir.mkdir(exist_ok=True)
                        slug = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                        with open(exp_dir / f"{slug}.md", 'w') as f:
                            f.write(f"# {title}\n\n")
                            f.write(f"URL: {url}\n\n")
                            f.write(markdown or '')
                    else:
                        result["pages"].append(page_info)
                        # Save page
                        pages_dir = output_dir / "pages"
                        pages_dir.mkdir(exist_ok=True)
                        slug = url.replace('https://', '').replace('/', '_').rstrip('_')[:80]
                        with open(pages_dir / f"{slug}.md", 'w') as f:
                            f.write(f"# {title}\n\n")
                            f.write(f"URL: {url}\n\n")
                            f.write(markdown or '')

                    # Extract media references from HTML
                    if html:
                        img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
                        video_matches = re.findall(r'<video[^>]+src=["\']([^"\']+)["\']', html)
                        result["media_inventory"].extend([
                            {"type": "image", "src": img, "page": url} for img in img_matches
                        ])
                        result["media_inventory"].extend([
                            {"type": "video", "src": vid, "page": url} for vid in video_matches
                        ])

                    result["total_words"] += page_info["word_count"]

                result["total_pages"] = len(pages_data)
                result["success"] = True

                # Save structure
                result["structure"] = {
                    "total_urls": len(urls),
                    "scraped_pages": result["total_pages"],
                    "experiences": len(result["experiences"]),
                    "main_pages": len(result["pages"]),
                    "media_assets": len(result["media_inventory"]),
                    "urls": urls
                }

                with open(output_dir / "structure.json", 'w') as f:
                    json.dump(result["structure"], f, indent=2)

                # Save media inventory
                with open(output_dir / "media_inventory.json", 'w') as f:
                    json.dump(result["media_inventory"], f, indent=2)

        logger.info(f"Scraped {result['total_pages']} pages, {result['total_words']:,} words")
        logger.info(f"Experiences: {len(result['experiences'])}, Main pages: {len(result['pages'])}")
        logger.info(f"Media assets found: {len(result['media_inventory'])}")

    except Exception as e:
        logger.error(f"Website scrape failed: {e}")
        result.update(create_error_response(e, "scrape_website"))

    return result


async def get_gbp_data(client: DataForSEOClient) -> Dict:
    """Get Google Business Profile data for escape.exe (400+ reviews)"""
    logger.info("=" * 60)
    logger.info("TASK 2: GETTING GOOGLE BUSINESS PROFILE DATA")
    logger.info("=" * 60)

    output_dir = OUTPUT_DIR / "local_seo"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "profile": None,
        "reviews": [],
        "review_summary": {},
        "qa": [],
        "success": False
    }

    location = "Bethlehem,Pennsylvania,United States"
    search_term = "escape.exe Bethlehem"

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

        # Get reviews - fetch up to 500 to capture all 400+
        logger.info("Fetching reviews (targeting 400+)...")
        reviews_result = await client.business_data_google_reviews(
            keyword=search_term,
            location_name=location,
            depth=500,  # Get more to ensure we capture all 400+
            sort_by="newest"
        )

        if reviews_result.get('success'):
            for task in reviews_result.get('data') or []:
                for res in task.get('result') or []:
                    items = res.get('items') or []
                    result["reviews"] = items
                    logger.info(f"Found {len(items)} reviews")

            # Analyze reviews
            if result["reviews"]:
                ratings = [r.get('rating', {}).get('value', 0) for r in result["reviews"]]
                result["review_summary"] = {
                    "total_reviews": len(result["reviews"]),
                    "average_rating": sum(ratings) / len(ratings) if ratings else 0,
                    "rating_distribution": {
                        "5_star": sum(1 for r in ratings if r == 5),
                        "4_star": sum(1 for r in ratings if r == 4),
                        "3_star": sum(1 for r in ratings if r == 3),
                        "2_star": sum(1 for r in ratings if r == 2),
                        "1_star": sum(1 for r in ratings if r == 1)
                    },
                    # Extract common themes from review text
                    "sample_positive": [
                        r.get('review_text', '')[:200]
                        for r in result["reviews"][:5]
                        if r.get('rating', {}).get('value', 0) >= 4
                    ]
                }

            with open(output_dir / "reviews.json", 'w') as f:
                json.dump(result["reviews"], f, indent=2, default=str)

            with open(output_dir / "review_summary.json", 'w') as f:
                json.dump(result["review_summary"], f, indent=2, default=str)

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
    """Run 10x10 local search grid analysis (60-mile radius)"""
    logger.info("=" * 60)
    logger.info("TASK 3: RUNNING LOCAL SEARCH GRID ANALYSIS (60-MILE RADIUS)")
    logger.info("=" * 60)

    output_dir = OUTPUT_DIR / "local_seo"
    output_dir.mkdir(parents=True, exist_ok=True)

    if keywords is None:
        keywords = PRIMARY_GRID_KEYWORDS

    # Build grid
    grid = client.build_geo_grid(
        center_lat=GRID_CONFIG["center_lat"],
        center_lng=GRID_CONFIG["center_lng"],
        grid_size=GRID_CONFIG["grid_size"],
        spacing_miles=GRID_CONFIG["spacing_miles"]
    )

    logger.info(f"Grid built: {len(grid)} points")
    logger.info(f"Coverage: ~{GRID_CONFIG['grid_size'] * GRID_CONFIG['spacing_miles']} mile radius")
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
                    "address": comp.get("address"),
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

        await asyncio.sleep(1)

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

    # Generate heatmap data
    heatmap_data = generate_heatmap_data(all_results)
    with open(output_dir / "grid_heatmap.json", 'w') as f:
        json.dump(heatmap_data, f, indent=2)

    logger.info(f"\nGrid analysis complete!")
    logger.info(f"Total competitors discovered: {len(all_results['all_competitors'])}")
    logger.info(f"Top competitor: {sorted_competitors[0]['name'] if sorted_competitors else 'N/A'}")

    return all_results


def generate_heatmap_data(grid_results: Dict) -> Dict:
    """Generate heatmap visualization data from grid results"""
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
                color = "red"
                score = 0
            elif target_position <= 3:
                color = "dark_green"
                score = 100
            elif target_position <= 7:
                color = "light_green"
                score = 70
            elif target_position <= 10:
                color = "yellow"
                score = 50
            else:
                color = "orange"
                score = 30

            keyword_heatmap.append({
                "lat": lat,
                "lng": lng,
                "position": target_position,
                "color": color,
                "score": score,
                "top_3": [r.get("title") for r in rankings[:3]]
            })

        # Calculate metrics
        positions_with_values = [p.get("position") for p in keyword_heatmap if p.get("position") is not None]
        avg_position = sum(positions_with_values) / len(positions_with_values) if positions_with_values else None
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
    """Deep analysis of top escape room competitors"""
    logger.info("=" * 60)
    logger.info("TASK 4: ANALYZING COMPETITORS")
    logger.info("=" * 60)

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
            "address": comp.get("address"),
            "grid_presence": comp.get("total_grid_presence", 0),
            "gbp_profile": None,
            "reviews": [],
            "review_themes": [],
            "website_scraped": False
        }

        # Get GBP profile
        if name:
            try:
                logger.info(f"  Getting GBP profile...")
                gbp_result = await dataforseo_client.business_data_google_my_business_info(
                    keyword=name,
                    location_name="Pennsylvania,United States"
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
                    keyword=name,
                    location_name="Pennsylvania,United States",
                    depth=30
                )

                if reviews_result.get('success'):
                    for task in reviews_result.get('data', []):
                        for res in task.get('result', []):
                            comp_data["reviews"] = res.get('items', [])

                await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"  GBP data failed: {e}")

        # Scrape competitor website
        if domain:
            try:
                logger.info(f"  Scraping website: {domain}...")
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
                logger.error(f"  Website scrape failed: {e}")

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
    """Generate side-by-side competitor comparison"""
    valid_ratings = [c for c in competitors if c.get("rating")]
    valid_reviews = [c for c in competitors if c.get("reviews_count")]

    comparison = {
        "by_rating": sorted(valid_ratings, key=lambda x: x.get("rating") or 0, reverse=True),
        "by_reviews": sorted(valid_reviews, key=lambda x: x.get("reviews_count") or 0, reverse=True),
        "by_visibility": sorted(competitors, key=lambda x: x.get("grid_presence") or 0, reverse=True),
        "summary": {
            "total_analyzed": len(competitors),
            "avg_rating": sum(c.get("rating") or 0 for c in valid_ratings) / len(valid_ratings) if valid_ratings else 0,
            "avg_reviews": sum(c.get("reviews_count") or 0 for c in valid_reviews) / len(valid_reviews) if valid_reviews else 0,
            "with_websites": sum(1 for c in competitors if c.get("domain")),
        },
        "opportunities": []
    }

    # Identify opportunities (low-rated competitors in high-visibility areas)
    for comp in competitors:
        rating = comp.get("rating") or 5
        visibility = comp.get("grid_presence") or 0
        if rating < 4.0 and visibility > 10:
            comparison["opportunities"].append({
                "competitor": comp.get("name"),
                "rating": rating,
                "visibility": visibility,
                "weakness": "Low rating but high visibility - potential to capture their market"
            })

    return comparison


async def run_keyword_research(client: DataForSEOClient, keywords: List[str]) -> Dict:
    """Perform escape room keyword research"""
    logger.info("=" * 60)
    logger.info("TASK 5: KEYWORD RESEARCH")
    logger.info("=" * 60)

    output_dir = OUTPUT_DIR / "keywords"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "target_keywords": [],
        "keyword_ideas": [],
        "search_volumes": {},
        "success": False
    }

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

        # Get keyword ideas from escape room seed keywords
        logger.info("Getting keyword ideas...")
        seed_keywords = [
            "escape room",
            "escape game",
            "puzzle room",
            "team building activities",
            "immersive experience"
        ]

        for seed in seed_keywords:
            ideas_result = await client.labs_keyword_ideas(
                keyword=seed,
                location_code=2840,
                language_code="en",
                limit=30
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

        # Identify high-opportunity keywords
        result["high_opportunity"] = [
            kw for kw in result["target_keywords"]
            if (kw.get("search_volume") or 0) >= 100
            and (kw.get("competition_level") or "HIGH") in ["LOW", "MEDIUM"]
        ]

        # Save results
        with open(output_dir / "target_keywords.json", 'w') as f:
            json.dump(result["target_keywords"], f, indent=2)

        with open(output_dir / "keyword_ideas.json", 'w') as f:
            json.dump(result["keyword_ideas"], f, indent=2)

        with open(output_dir / "high_opportunity_keywords.json", 'w') as f:
            json.dump(result["high_opportunity"], f, indent=2)

        logger.info(f"Keyword research complete!")
        logger.info(f"Target keywords: {len(result['target_keywords'])}")
        logger.info(f"Keyword ideas: {len(result['keyword_ideas'])}")
        logger.info(f"High opportunity: {len(result['high_opportunity'])}")

    except Exception as e:
        logger.error(f"Keyword research failed: {e}")
        result.update(create_error_response(e, "run_keyword_research"))

    return result


async def run_web_research(firecrawl_client: EnhancedFirecrawlClient) -> Dict:
    """Web research for awards, news, and third-party reviews"""
    logger.info("=" * 60)
    logger.info("TASK 6: WEB RESEARCH (Awards, News, Reviews)")
    logger.info("=" * 60)

    output_dir = OUTPUT_DIR / "web_research"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "awards": [],
        "news": [],
        "third_party_reviews": [],
        "success": False
    }

    # Key URLs to fetch for third-party reviews and awards
    target_urls = [
        "https://morty.app/escape-rooms/escape-exe-bethlehem",
        "https://www.escaperoomers.com/escape-room/escape-exe-bethlehem",
    ]

    logger.info("Fetching third-party review sites...")

    for url in target_urls:
        try:
            logger.info(f"  Scraping: {url}")
            scrape_result = await firecrawl_client.scrape(
                url=url,
                formats=['markdown']
            )

            if scrape_result.get('success'):
                result["third_party_reviews"].append({
                    "url": url,
                    "title": scrape_result.get('metadata', {}).get('title'),
                    "content_preview": scrape_result.get('markdown', '')[:1000]
                })

            await asyncio.sleep(1)

        except Exception as e:
            logger.warning(f"  Failed to scrape {url}: {e}")

    # Save results
    with open(output_dir / "awards_news.json", 'w') as f:
        json.dump({
            "awards": result["awards"],
            "news": result["news"]
        }, f, indent=2)

    with open(output_dir / "review_platforms.json", 'w') as f:
        json.dump(result["third_party_reviews"], f, indent=2)

    result["success"] = True
    logger.info(f"Web research complete!")

    return result


async def generate_reports(all_data: Dict) -> Dict:
    """Generate comprehensive reports from all collected data"""
    logger.info("=" * 60)
    logger.info("GENERATING REPORTS")
    logger.info("=" * 60)

    reports_dir = OUTPUT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Full JSON report with metadata
    wrapped_data = wrap_with_metadata(all_data, "escape_exe_full_report_v1")
    with open(reports_dir / "full_report.json", 'w') as f:
        json.dump(wrapped_data, f, indent=2, default=str)

    # Generate markdown summary
    md_report = generate_markdown_report(all_data)
    with open(reports_dir / "full_report.md", 'w') as f:
        f.write(md_report)

    # Executive summary
    exec_summary = generate_executive_summary(all_data)
    with open(reports_dir / "executive_summary.md", 'w') as f:
        f.write(exec_summary)

    # SEO strategy document
    seo_strategy = generate_seo_strategy(all_data)
    with open(reports_dir / "seo_strategy.md", 'w') as f:
        f.write(seo_strategy)

    # Website redesign requirements
    redesign_brief = generate_redesign_brief(all_data)
    with open(reports_dir / "website_redesign_brief.md", 'w') as f:
        f.write(redesign_brief)

    logger.info(f"Reports saved to {reports_dir}")

    return {"reports_dir": str(reports_dir)}


def generate_markdown_report(data: Dict) -> str:
    """Generate full markdown report"""
    report = []
    report.append("# escape.exe Local SEO Research Report")
    report.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    report.append(f"**Business:** {TARGET_BUSINESS['name']}")
    report.append(f"**Website:** {TARGET_BUSINESS['domain']}")
    report.append(f"**Location:** {TARGET_BUSINESS['address']}")
    report.append("")

    # Website Analysis
    if "website" in data:
        report.append("## 1. Website Analysis\n")
        website = data["website"]
        report.append(f"- **Total Pages**: {website.get('total_pages', 0)}")
        report.append(f"- **Total Words**: {website.get('total_words', 0):,}")
        report.append(f"- **Experience Pages**: {len(website.get('experiences', []))}")
        report.append(f"- **Media Assets**: {len(website.get('media_inventory', []))}")
        report.append("")

    # GBP Data
    if "gbp_data" in data:
        report.append("## 2. Google Business Profile\n")
        gbp = data["gbp_data"]
        if gbp.get("profile"):
            profile = gbp["profile"]
            report.append(f"- **Rating**: {profile.get('rating', {}).get('value', 'N/A')}")
            report.append(f"- **Reviews**: {profile.get('rating', {}).get('votes_count', 'N/A')}")
        if gbp.get("review_summary"):
            summary = gbp["review_summary"]
            report.append(f"- **Total Reviews Retrieved**: {summary.get('total_reviews', 0)}")
            report.append(f"- **Average Rating**: {summary.get('average_rating', 0):.2f}")
        report.append("")

    # Grid Analysis
    if "grid_results" in data:
        report.append("## 3. Local Search Grid Analysis (60-mile radius)\n")
        grid = data["grid_results"]
        report.append(f"- **Grid Size**: {grid.get('grid_config', {}).get('grid_size', 0)}x{grid.get('grid_config', {}).get('grid_size', 0)} ({len(grid.get('grid_points', []))} points)")
        report.append(f"- **Coverage**: ~{grid.get('grid_config', {}).get('grid_size', 0) * grid.get('grid_config', {}).get('spacing_miles', 0)} mile radius")
        report.append(f"- **Keywords Analyzed**: {len(grid.get('keywords', []))}")
        report.append(f"- **Total Competitors Found**: {len(grid.get('all_competitors', {}))}")
        report.append("")

        # Top Competitors
        report.append("### Top Competitors by Visibility\n")
        report.append("| Rank | Business | Grid Presence | Rating | Reviews |")
        report.append("|------|----------|---------------|--------|---------|")
        for i, comp in enumerate(grid.get("top_competitors", [])[:10], 1):
            report.append(f"| {i} | {comp.get('name', 'N/A')[:35]} | {comp.get('total_grid_presence', 0)} | {comp.get('rating', 'N/A')} | {comp.get('reviews_count', 'N/A')} |")
        report.append("")

    # Keyword Research
    if "keyword_research" in data:
        report.append("## 4. Keyword Research\n")
        keywords = data["keyword_research"]
        report.append(f"- **Target Keywords**: {len(keywords.get('target_keywords', []))}")
        report.append(f"- **Keyword Ideas**: {len(keywords.get('keyword_ideas', []))}")
        report.append(f"- **High Opportunity Keywords**: {len(keywords.get('high_opportunity', []))}")
        report.append("")

        report.append("### Top Keywords by Search Volume\n")
        report.append("| Keyword | Search Volume | CPC | Competition |")
        report.append("|---------|---------------|-----|-------------|")
        for kw in keywords.get("target_keywords", [])[:15]:
            report.append(f"| {kw.get('keyword', 'N/A')[:45]} | {kw.get('search_volume', 'N/A')} | ${kw.get('cpc', 0) or 0:.2f} | {kw.get('competition_level', 'N/A')} |")
        report.append("")

    return "\n".join(report)


def generate_executive_summary(data: Dict) -> str:
    """Generate executive summary"""
    summary = []
    summary.append("# Executive Summary: escape.exe Local SEO Research")
    summary.append(f"\n*{datetime.now().strftime('%Y-%m-%d')}*\n")

    summary.append("## Overview\n")
    summary.append(f"This report analyzes the local SEO landscape for **{TARGET_BUSINESS['name']}**, ")
    summary.append(f"a next-generation immersive escape room experience located in {TARGET_BUSINESS['address']}.\n")

    summary.append("## Key Findings\n")

    # Website
    if "website" in data:
        website = data["website"]
        summary.append("### Website Content")
        summary.append(f"- {website.get('total_pages', 0)} pages with {website.get('total_words', 0):,} words")
        summary.append(f"- {len(website.get('experiences', []))} experience/room pages")
        summary.append("")

    # Reviews
    if "gbp_data" in data and data["gbp_data"].get("review_summary"):
        review_sum = data["gbp_data"]["review_summary"]
        summary.append("### Customer Reviews")
        summary.append(f"- **{review_sum.get('total_reviews', 0)}** total reviews collected")
        summary.append(f"- **{review_sum.get('average_rating', 0):.2f}** average rating")
        summary.append("")

    # Competition
    if "grid_results" in data:
        grid = data["grid_results"]
        summary.append("### Competitive Landscape")
        summary.append(f"- {len(grid.get('all_competitors', {}))} competitors in 60-mile radius")
        top = grid.get("top_competitors", [])
        if top:
            summary.append(f"- Top competitor: {top[0].get('name', 'N/A')}")
        summary.append("")

    summary.append("## Strategic Recommendations\n")
    summary.append("1. **Leverage 400+ Reviews** - Showcase rating prominently on redesigned site")
    summary.append("2. **Target High-Opportunity Keywords** - Focus on terms with volume but lower competition")
    summary.append("3. **Differentiate with AI Characters** - GAVIN and KT are unique selling points")
    summary.append("4. **Expand Local Content** - Create pages targeting surrounding cities")
    summary.append("5. **Optimize for 'near me' Searches** - Critical for escape room discovery")
    summary.append("")

    summary.append("---")
    summary.append(f"\n*Full data available in `{OUTPUT_DIR}/`*")

    return "\n".join(summary)


def generate_seo_strategy(data: Dict) -> str:
    """Generate SEO strategy document"""
    strategy = []
    strategy.append("# escape.exe SEO Strategy")
    strategy.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    strategy.append("## On-Page SEO Priorities\n")
    strategy.append("1. **Title Tags**: Include primary keyword + location + brand")
    strategy.append("   - Example: \"Immersive Escape Rooms Bethlehem PA | escape.exe\"")
    strategy.append("")
    strategy.append("2. **Meta Descriptions**: Highlight reviews, uniqueness, CTA")
    strategy.append("   - Mention 400+ reviews, AI characters, award nominations")
    strategy.append("")
    strategy.append("3. **Schema Markup**: Implement LocalBusiness + Event schemas")
    strategy.append("   - Reviews, hours, booking availability")
    strategy.append("")

    strategy.append("## Content Strategy\n")
    strategy.append("1. **Experience Pages**: Rich descriptions with keywords")
    strategy.append("2. **Location Pages**: Target Allentown, Easton, Reading, Poconos")
    strategy.append("3. **Blog Content**: Escape room tips, team building guides")
    strategy.append("4. **FAQ Section**: Answer common booking questions")
    strategy.append("")

    strategy.append("## Local SEO Actions\n")
    strategy.append("1. **GBP Optimization**: Keep profile complete, respond to reviews")
    strategy.append("2. **Citations**: Ensure NAP consistency across directories")
    strategy.append("3. **Review Generation**: Systematic request after each experience")
    strategy.append("4. **Local Backlinks**: Partner with Lehigh Valley tourism sites")
    strategy.append("")

    return "\n".join(strategy)


def generate_redesign_brief(data: Dict) -> str:
    """Generate website redesign requirements"""
    brief = []
    brief.append("# escape.exe Website Redesign Brief")
    brief.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    brief.append("## Tech Stack\n")
    brief.append("- **Framework**: Next.js 14 (App Router)")
    brief.append("- **Styling**: Tailwind CSS")
    brief.append("- **Language**: TypeScript")
    brief.append("- **3D/Animation**: Three.js")
    brief.append("- **Booking**: Resova integration (current)")
    brief.append("")

    brief.append("## Required Features\n")
    brief.append("1. **Immersive 3D Homepage** - Establish atmosphere immediately")
    brief.append("2. **GAVIN/KT AI Characters** - Interactive elements featuring AI guides")
    brief.append("3. **Multiple Narrative Pathways** - Reflect adaptive experience")
    brief.append("4. **Award Badges** - Prominently display nominations/wins")
    brief.append("5. **Review Social Proof** - Integrate 400+ review count and rating")
    brief.append("6. **Adaptive Difficulty Explainer** - Unique selling point")
    brief.append("7. **Corporate/Team Building Section** - B2B market segment")
    brief.append("8. **Seamless Booking Integration** - Resova or replacement")
    brief.append("")

    brief.append("## SEO Requirements\n")
    brief.append("- Server-side rendering for all pages")
    brief.append("- LocalBusiness schema on all pages")
    brief.append("- Event schema for booking availability")
    brief.append("- Review schema integration")
    brief.append("- Optimized Core Web Vitals")
    brief.append("- Mobile-first responsive design")
    brief.append("")

    brief.append("## Content Requirements\n")

    if "website" in data:
        website = data["website"]
        brief.append(f"- Current content: {website.get('total_words', 0):,} words")
        brief.append(f"- Experience pages: {len(website.get('experiences', []))}")

    brief.append("- Maintain or improve current content depth")
    brief.append("- Add location-specific landing pages")
    brief.append("- Create blog/resource section")
    brief.append("")

    return "\n".join(brief)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main(module: str = "all"):
    """Run complete local SEO research"""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       escape.exe LOCAL SEO RESEARCH                          ║
║              Comprehensive Analysis for Website Redesign                      ║
║                                                                               ║
║  Business: escape.exe - Next-Gen Immersive Escape Room                       ║
║  Location: Bethlehem, PA (Lehigh Valley)                                     ║
║  Grid: 10x10 (100 points) - 60 mile radius                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    start_time = time.time()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize clients
    logger.info("Initializing API clients...")
    firecrawl = EnhancedFirecrawlClient(Config.API_KEY)

    dataforseo = None
    try:
        dataforseo = DataForSEOClient(
            login=Config.DATAFORSEO_LOGIN,
            password=Config.DATAFORSEO_PASSWORD
        )
    except Exception as e:
        logger.warning(f"DataForSEO initialization failed: {e}")
        logger.info("Continuing with Firecrawl only...")

    # Generate keywords
    keywords = generate_keywords()
    logger.info(f"Generated {len(keywords)} target keywords")

    # Collect all data
    all_data = {
        "target_business": TARGET_BUSINESS,
        "generated_at": datetime.now().isoformat(),
        "keywords": keywords
    }

    # Run modules based on selection
    if module in ["all", "scrape"]:
        all_data["website"] = await scrape_website(firecrawl)

    if dataforseo:
        if module in ["all", "gbp"]:
            all_data["gbp_data"] = await get_gbp_data(dataforseo)

        if module in ["all", "grid"]:
            all_data["grid_results"] = await run_local_search_grid(dataforseo, PRIMARY_GRID_KEYWORDS)

        if module in ["all", "competitors"]:
            top_competitors = all_data.get("grid_results", {}).get("top_competitors", [])
            if top_competitors:
                all_data["competitors"] = await analyze_competitors(
                    dataforseo, firecrawl, top_competitors
                )

        if module in ["all", "keywords"]:
            all_data["keyword_research"] = await run_keyword_research(dataforseo, keywords[:50])

        # Get API stats
        all_data["api_stats"] = {
            "dataforseo": dataforseo.get_stats(),
            "firecrawl": firecrawl.get_stats() if hasattr(firecrawl, 'get_stats') else {}
        }

    if module in ["all", "web"]:
        all_data["web_research"] = await run_web_research(firecrawl)

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
║    - Reviews: {all_data.get('gbp_data', {}).get('review_summary', {}).get('total_reviews', 0)}
║    - Competitors found: {len(all_data.get('grid_results', {}).get('all_competitors', {}))}
║    - Keywords researched: {len(all_data.get('keyword_research', {}).get('target_keywords', []))}
║
║  Reports Generated:
║    - full_report.json / full_report.md
║    - executive_summary.md
║    - seo_strategy.md
║    - website_redesign_brief.md
║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    if dataforseo:
        print(f"DataForSEO Cost: ${dataforseo.stats.total_cost:.4f}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='escape.exe Local SEO Research')
    parser.add_argument('--module',
                        choices=['scrape', 'gbp', 'grid', 'competitors', 'keywords', 'web', 'all'],
                        default='all',
                        help='Run specific module only')
    args = parser.parse_args()

    asyncio.run(main(module=args.module))
