#!/usr/bin/env python3
"""
Local SEO Research Template - Reusable for Any Business

A parameterized version of local_seo_research.py that accepts command-line
arguments for easy customization across different projects.

Usage:
    # Basic usage
    python local_seo_template.py --name "Business Name" --domain "example.com"

    # With grid coordinates
    python local_seo_template.py \
        --name "My Business" \
        --domain "mybusiness.com" \
        --lat 40.6259 \
        --lng -75.3705 \
        --keywords "service 1" "service 2" "service 3"

    # Full options
    python local_seo_template.py \
        --name "Dent Sorcery" \
        --domain "dentsorcery.com" \
        --address "123 Main St, City, ST 12345" \
        --phone "555-123-4567" \
        --lat 40.6259 \
        --lng -75.3705 \
        --grid-size 5 \
        --spacing 2.0 \
        --keywords "paintless dent repair" "PDR" "dent removal" \
        --locations "Bethlehem PA" "Allentown PA" "near me" \
        --output ./data/custom_research \
        --module all
"""

import argparse
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
    """Create standardized error response."""
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }


def wrap_with_metadata(data: Dict, schema_name: str = "local_seo_template_v1") -> Dict:
    """Wrap data with metadata for LLM analysis."""
    return {
        "_meta": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "schema": schema_name,
            "source": "psycrawl-firecrawl-scraper",
            "generator": "local_seo_template.py"
        },
        "data": data
    }


class LocalSEOResearch:
    """Configurable Local SEO Research class."""

    def __init__(
        self,
        business_name: str,
        domain: str,
        address: str = "",
        phone: str = "",
        center_lat: float = 40.0,
        center_lng: float = -75.0,
        grid_size: int = 5,
        spacing_miles: float = 2.0,
        services: List[str] = None,
        locations: List[str] = None,
        output_dir: str = None
    ):
        self.business = {
            "name": business_name,
            "domain": domain,
            "url": f"https://{domain}/",
            "address": address,
            "phone": phone
        }

        self.grid_config = {
            "center_lat": center_lat,
            "center_lng": center_lng,
            "grid_size": grid_size,
            "spacing_miles": spacing_miles,
            "zoom": 17
        }

        self.services = services or ["service"]
        self.locations = locations or ["near me"]

        # Set output directory
        safe_name = business_name.lower().replace(' ', '_')[:30]
        self.output_dir = Path(output_dir) if output_dir else Path(Config.OUTPUT_DIR) / f"{safe_name}_research"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize clients
        self.firecrawl = None
        self.dataforseo = None

    def initialize_clients(self):
        """Initialize API clients."""
        logger.info("Initializing API clients...")

        self.firecrawl = EnhancedFirecrawlClient(Config.API_KEY)

        try:
            self.dataforseo = DataForSEOClient(
                login=Config.DATAFORSEO_LOGIN,
                password=Config.DATAFORSEO_PASSWORD
            )
        except Exception as e:
            logger.warning(f"DataForSEO not available: {e}")
            self.dataforseo = None

    def generate_keywords(self) -> List[str]:
        """Generate keyword combinations."""
        keywords = []

        for service in self.services:
            for location in self.locations:
                keywords.append(f"{service} {location}")

        # Add standalone searches
        for service in self.services[:3]:
            keywords.append(f"{service} near me")

        # Deduplicate
        seen = set()
        unique = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique.append(kw)

        return unique

    async def scrape_website(self) -> Dict:
        """Scrape target website."""
        logger.info(f"Scraping {self.business['domain']}...")

        result = {
            "pages": [],
            "total_pages": 0,
            "total_words": 0,
            "success": False
        }

        try:
            # Map site
            map_result = await self.firecrawl.map(
                url=self.business["url"],
                limit=30
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

            logger.info(f"Found {len(urls)} URLs")

            # Batch scrape
            if urls:
                scrape_result = await self.firecrawl.batch_scrape(
                    urls=urls[:30],
                    formats=['markdown']
                )

                if scrape_result.get('success'):
                    for page in scrape_result.get('data', []):
                        markdown = page.get('markdown', '')
                        result["pages"].append({
                            "url": page.get('metadata', {}).get('sourceURL', ''),
                            "title": page.get('metadata', {}).get('title', ''),
                            "word_count": len(markdown.split()) if markdown else 0
                        })
                        result["total_words"] += len(markdown.split()) if markdown else 0

                    result["total_pages"] = len(scrape_result.get('data', []))
                    result["success"] = True

            # Save
            output_file = self.output_dir / "website_content.json"
            with open(output_file, 'w') as f:
                json.dump(wrap_with_metadata(result, "website_scrape_v1"), f, indent=2)

            logger.info(f"Scraped {result['total_pages']} pages, {result['total_words']:,} words")

        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            result.update(create_error_response(e, "scrape_website"))

        return result

    async def run_grid_analysis(self, keywords: List[str] = None) -> Dict:
        """Run local search grid analysis."""
        if not self.dataforseo:
            logger.warning("DataForSEO not available for grid analysis")
            return {"success": False, "error": "DataForSEO not configured"}

        logger.info("Running grid analysis...")

        keywords = keywords or self.generate_keywords()[:3]

        # Build grid
        grid = self.dataforseo.build_geo_grid(
            center_lat=self.grid_config["center_lat"],
            center_lng=self.grid_config["center_lng"],
            grid_size=self.grid_config["grid_size"],
            spacing_miles=self.grid_config["spacing_miles"]
        )

        logger.info(f"Grid: {len(grid)} points, Keywords: {len(keywords)}")

        all_results = {
            "grid_config": self.grid_config,
            "keywords": keywords,
            "keyword_results": {},
            "all_competitors": {},
            "success": True
        }

        for keyword in keywords:
            logger.info(f"  Analyzing: '{keyword}'")

            grid_result = await self.dataforseo.query_local_search_grid(
                keyword=keyword,
                grid_coords=grid,
                depth=15,
                delay_between_requests=0.15
            )

            all_results["keyword_results"][keyword] = {
                "competitors": grid_result.get("competitors", []),
                "total_competitors": grid_result.get("total_competitors_found", 0)
            }

            # Track competitors
            for comp in grid_result.get("competitors", []):
                name = comp.get("name", "Unknown")
                if name not in all_results["all_competitors"]:
                    all_results["all_competitors"][name] = {
                        "name": name,
                        "rating": comp.get("rating"),
                        "reviews_count": comp.get("reviews_count"),
                        "domain": comp.get("domain"),
                        "total_visibility": 0
                    }
                all_results["all_competitors"][name]["total_visibility"] += comp.get("grid_presence", 0)

            await asyncio.sleep(1)

        # Sort competitors
        all_results["top_competitors"] = sorted(
            all_results["all_competitors"].values(),
            key=lambda x: -x.get("total_visibility", 0)
        )[:15]

        # Save
        output_file = self.output_dir / "grid_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(wrap_with_metadata(all_results, "grid_analysis_v1"), f, indent=2)

        logger.info(f"Found {len(all_results['all_competitors'])} competitors")

        return all_results

    async def run_keyword_research(self, keywords: List[str] = None) -> Dict:
        """Run keyword research."""
        if not self.dataforseo:
            logger.warning("DataForSEO not available for keyword research")
            return {"success": False, "error": "DataForSEO not configured"}

        logger.info("Running keyword research...")

        keywords = keywords or self.generate_keywords()

        result = {
            "keywords": [],
            "success": False
        }

        try:
            volume_result = await self.dataforseo.keywords_google_ads(
                keywords=keywords[:50],
                location_code=2840,
                language_code="en"
            )

            if volume_result.get('success'):
                for task in volume_result.get('data', []):
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

            # Save
            output_file = self.output_dir / "keyword_research.json"
            with open(output_file, 'w') as f:
                json.dump(wrap_with_metadata(result, "keyword_research_v1"), f, indent=2)

            logger.info(f"Researched {len(result['keywords'])} keywords")

        except Exception as e:
            logger.error(f"Keyword research failed: {e}")
            result.update(create_error_response(e, "keyword_research"))

        return result

    async def run_full_analysis(self, module: str = "all") -> Dict:
        """Run full or partial analysis."""
        self.initialize_clients()

        all_data = {
            "business": self.business,
            "generated_at": datetime.now().isoformat()
        }

        if module in ["all", "scrape"]:
            all_data["website"] = await self.scrape_website()

        if module in ["all", "grid"]:
            all_data["grid"] = await self.run_grid_analysis()

        if module in ["all", "keywords"]:
            all_data["keywords"] = await self.run_keyword_research()

        # Save full report
        output_file = self.output_dir / "full_report.json"
        with open(output_file, 'w') as f:
            json.dump(wrap_with_metadata(all_data, "full_report_v1"), f, indent=2, default=str)

        # Print summary
        if self.dataforseo:
            logger.info(f"DataForSEO cost: ${self.dataforseo.stats.total_cost:.4f}")

        logger.info(f"Results saved to: {self.output_dir}")

        return all_data


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Local SEO Research Template',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required
    parser.add_argument('--name', required=True, help='Business name')
    parser.add_argument('--domain', required=True, help='Business domain (e.g., example.com)')

    # Optional business info
    parser.add_argument('--address', default='', help='Business address')
    parser.add_argument('--phone', default='', help='Business phone')

    # Grid configuration
    parser.add_argument('--lat', type=float, default=40.0, help='Center latitude')
    parser.add_argument('--lng', type=float, default=-75.0, help='Center longitude')
    parser.add_argument('--grid-size', type=int, default=5, help='Grid size (e.g., 5 for 5x5)')
    parser.add_argument('--spacing', type=float, default=2.0, help='Grid spacing in miles')

    # Keywords and locations
    parser.add_argument('--keywords', nargs='+', help='Service keywords')
    parser.add_argument('--locations', nargs='+', help='Location variations')

    # Output
    parser.add_argument('--output', help='Output directory')

    # Module selection
    parser.add_argument('--module', choices=['all', 'scrape', 'grid', 'keywords'],
                        default='all', help='Run specific module')

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LOCAL SEO RESEARCH - {args.name[:30]:<30} ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    research = LocalSEOResearch(
        business_name=args.name,
        domain=args.domain,
        address=args.address,
        phone=args.phone,
        center_lat=args.lat,
        center_lng=args.lng,
        grid_size=args.grid_size,
        spacing_miles=args.spacing,
        services=args.keywords,
        locations=args.locations,
        output_dir=args.output
    )

    start_time = time.time()
    results = await research.run_full_analysis(module=args.module)
    elapsed = time.time() - start_time

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              COMPLETE                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Time: {elapsed:.1f}s
║  Output: {research.output_dir}
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == '__main__':
    asyncio.run(main())
