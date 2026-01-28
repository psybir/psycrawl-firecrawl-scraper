#!/usr/bin/env python3
"""
PsyCrawl CLI - Intelligent Web Research & Data Extraction System

Built on Firecrawl v2.7 with Spark 1 Pro for quality-first extraction.
Primary use cases: Competitor analysis, SEO research, market intelligence.
Also supports: App dev research, psychology, UI/UX, AI tools, best practices.

CORE COMMANDS:
    psycrawl scrape <url>              # Single URL with Spark 1 Pro
    psycrawl crawl <url>               # Full site crawl
    psycrawl map <url>                 # 15x faster URL discovery (100k limit)
    psycrawl extract <url>             # Deep extraction with Pro model
    psycrawl batch <file>              # Batch processing from CSV/JSON

RESEARCH COMMANDS:
    psycrawl research <topic>          # Deep research on any topic
    psycrawl stockpile <topic>         # Build knowledge base on a topic
    psycrawl analyze <url>             # Deep content analysis

BUSINESS INTELLIGENCE:
    psycrawl seo-audit <domain>        # Full SEO audit + DataForSEO
    psycrawl competitor <domain>       # Competitor analysis
    psycrawl leads <industry>          # Lead generation

UTILITIES:
    psycrawl status                    # Show credit usage and stats
"""

import argparse
import asyncio
import json
import sys
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

from tqdm import tqdm

from .config import Config
from .core.firecrawl_client import EnhancedFirecrawlClient

# Skills system imports
try:
    from .skills import list_skills, get_skill, find_skill_by_trigger
    from .skills.router import get_router, parse_skill_args
    from .skills.context import get_context_manager
    from .skills.output import OutputFormatter, save_report, print_summary
    SKILLS_AVAILABLE = True
except ImportError as e:
    SKILLS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.debug(f"Skills system not fully available: {e}")

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# LEAD GENERATION SCHEMAS
# ============================================================================

LEAD_SCHEMAS = {
    'wineries': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "has_event_space": {"type": "boolean"},
            "offers_tastings": {"type": "boolean"},
            "wedding_venue": {"type": "boolean"},
            "google_rating": {"type": "number"},
            "wine_varieties": {"type": "array", "items": {"type": "string"}},
            "owner_info": {"type": "string"},
            "social_media": {"type": "object"}
        }
    },
    'auto_dealerships': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_showroom": {"type": "boolean"},
            "brands_sold": {"type": "array", "items": {"type": "string"}},
            "inventory_size": {"type": "string"},
            "google_rating": {"type": "number"},
            "review_count": {"type": "integer"},
            "services_offered": {"type": "array", "items": {"type": "string"}},
            "owner_info": {"type": "string"}
        }
    },
    'senior_living': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "care_types": {"type": "array", "items": {"type": "string"}},
            "amenities": {"type": "array", "items": {"type": "string"}},
            "capacity": {"type": "string"},
            "google_rating": {"type": "number"},
            "pricing_info": {"type": "string"},
            "decision_maker": {"type": "string"}
        }
    },
    'wedding_venues': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "venue_type": {"type": "string"},
            "capacity": {"type": "integer"},
            "indoor_outdoor": {"type": "string"},
            "google_rating": {"type": "number"},
            "packages_offered": {"type": "array", "items": {"type": "string"}},
            "price_range": {"type": "string"},
            "catering_options": {"type": "string"}
        }
    },
    'fitness_centers': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "gym_type": {"type": "string"},
            "amenities": {"type": "array", "items": {"type": "string"}},
            "class_types": {"type": "array", "items": {"type": "string"}},
            "membership_info": {"type": "string"},
            "google_rating": {"type": "number"},
            "hours": {"type": "string"}
        }
    },
    'medical_dental': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "practice_type": {"type": "string"},
            "services": {"type": "array", "items": {"type": "string"}},
            "accepts_insurance": {"type": "boolean"},
            "google_rating": {"type": "number"},
            "doctor_names": {"type": "array", "items": {"type": "string"}},
            "new_patient_status": {"type": "string"}
        }
    },
    'general': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "business_type": {"type": "string"},
            "google_rating": {"type": "number"},
            "review_count": {"type": "integer"},
            "services": {"type": "array", "items": {"type": "string"}},
            "owner_info": {"type": "string"},
            "social_media": {"type": "object"},
            "marketing_gaps": {"type": "array", "items": {"type": "string"}}
        }
    }
}

INDUSTRY_ALIASES = {
    'wineries': 'wineries',
    'winery': 'wineries',
    'wine': 'wineries',
    'auto': 'auto_dealerships',
    'dealership': 'auto_dealerships',
    'dealerships': 'auto_dealerships',
    'car': 'auto_dealerships',
    'senior': 'senior_living',
    'senior_living': 'senior_living',
    'assisted': 'senior_living',
    'wedding': 'wedding_venues',
    'weddings': 'wedding_venues',
    'venue': 'wedding_venues',
    'venues': 'wedding_venues',
    'fitness': 'fitness_centers',
    'gym': 'fitness_centers',
    'gyms': 'fitness_centers',
    'medical': 'medical_dental',
    'dental': 'medical_dental',
    'doctor': 'medical_dental',
    'dentist': 'medical_dental',
    'general': 'general'
}


# ============================================================================
# RESEARCH SCHEMAS (Generic for any topic)
# ============================================================================

RESEARCH_SCHEMAS = {
    'general': {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Main topic/title"},
            "summary": {"type": "string", "description": "Brief summary"},
            "key_concepts": {"type": "array", "items": {"type": "string"}},
            "key_insights": {"type": "array", "items": {"type": "string"}},
            "best_practices": {"type": "array", "items": {"type": "string"}},
            "tools_mentioned": {"type": "array", "items": {"type": "string"}},
            "resources": {"type": "array", "items": {"type": "string"}},
            "quotes": {"type": "array", "items": {"type": "string"}},
            "action_items": {"type": "array", "items": {"type": "string"}}
        }
    },
    'competitor': {
        "type": "object",
        "properties": {
            "company_name": {"type": "string"},
            "tagline": {"type": "string"},
            "value_proposition": {"type": "string"},
            "target_audience": {"type": "string"},
            "pricing_model": {"type": "string"},
            "pricing_tiers": {"type": "array", "items": {"type": "object"}},
            "key_features": {"type": "array", "items": {"type": "string"}},
            "differentiators": {"type": "array", "items": {"type": "string"}},
            "weaknesses": {"type": "array", "items": {"type": "string"}},
            "technology_stack": {"type": "array", "items": {"type": "string"}},
            "integrations": {"type": "array", "items": {"type": "string"}},
            "team_size": {"type": "string"},
            "funding": {"type": "string"},
            "customer_reviews": {"type": "array", "items": {"type": "object"}},
            "market_position": {"type": "string"}
        }
    },
    'uiux': {
        "type": "object",
        "properties": {
            "design_patterns": {"type": "array", "items": {"type": "string"}},
            "color_scheme": {"type": "object"},
            "typography": {"type": "object"},
            "layout_approach": {"type": "string"},
            "navigation_patterns": {"type": "array", "items": {"type": "string"}},
            "micro_interactions": {"type": "array", "items": {"type": "string"}},
            "accessibility_features": {"type": "array", "items": {"type": "string"}},
            "mobile_responsive": {"type": "boolean"},
            "ux_best_practices": {"type": "array", "items": {"type": "string"}},
            "improvement_opportunities": {"type": "array", "items": {"type": "string"}}
        }
    },
    'psychology': {
        "type": "object",
        "properties": {
            "concepts": {"type": "array", "items": {"type": "string"}},
            "principles": {"type": "array", "items": {"type": "string"}},
            "cognitive_biases": {"type": "array", "items": {"type": "string"}},
            "behavioral_patterns": {"type": "array", "items": {"type": "string"}},
            "persuasion_techniques": {"type": "array", "items": {"type": "string"}},
            "research_findings": {"type": "array", "items": {"type": "string"}},
            "applications": {"type": "array", "items": {"type": "string"}},
            "sources": {"type": "array", "items": {"type": "string"}}
        }
    },
    'app_dev': {
        "type": "object",
        "properties": {
            "technology": {"type": "string"},
            "architecture_patterns": {"type": "array", "items": {"type": "string"}},
            "best_practices": {"type": "array", "items": {"type": "string"}},
            "code_examples": {"type": "array", "items": {"type": "object"}},
            "libraries": {"type": "array", "items": {"type": "string"}},
            "frameworks": {"type": "array", "items": {"type": "string"}},
            "tools": {"type": "array", "items": {"type": "string"}},
            "common_pitfalls": {"type": "array", "items": {"type": "string"}},
            "performance_tips": {"type": "array", "items": {"type": "string"}},
            "security_considerations": {"type": "array", "items": {"type": "string"}}
        }
    },
    'ai_tools': {
        "type": "object",
        "properties": {
            "tool_name": {"type": "string"},
            "category": {"type": "string"},
            "description": {"type": "string"},
            "pricing": {"type": "string"},
            "key_features": {"type": "array", "items": {"type": "string"}},
            "use_cases": {"type": "array", "items": {"type": "string"}},
            "api_available": {"type": "boolean"},
            "integrations": {"type": "array", "items": {"type": "string"}},
            "limitations": {"type": "array", "items": {"type": "string"}},
            "alternatives": {"type": "array", "items": {"type": "string"}}
        }
    },
    'seo': {
        "type": "object",
        "properties": {
            "title_tag": {"type": "string"},
            "meta_description": {"type": "string"},
            "h1_headings": {"type": "array", "items": {"type": "string"}},
            "keyword_density": {"type": "object"},
            "internal_links": {"type": "integer"},
            "external_links": {"type": "integer"},
            "images_with_alt": {"type": "integer"},
            "page_speed_issues": {"type": "array", "items": {"type": "string"}},
            "mobile_friendly": {"type": "boolean"},
            "structured_data": {"type": "boolean"},
            "canonical_url": {"type": "string"},
            "seo_score": {"type": "integer"},
            "recommendations": {"type": "array", "items": {"type": "string"}}
        }
    },
    'market': {
        "type": "object",
        "properties": {
            "market_size": {"type": "string"},
            "growth_rate": {"type": "string"},
            "key_players": {"type": "array", "items": {"type": "string"}},
            "trends": {"type": "array", "items": {"type": "string"}},
            "opportunities": {"type": "array", "items": {"type": "string"}},
            "challenges": {"type": "array", "items": {"type": "string"}},
            "customer_segments": {"type": "array", "items": {"type": "string"}},
            "pricing_trends": {"type": "string"},
            "technology_trends": {"type": "array", "items": {"type": "string"}},
            "regulatory_factors": {"type": "array", "items": {"type": "string"}}
        }
    }
}

RESEARCH_TYPE_ALIASES = {
    'general': 'general',
    'default': 'general',
    'competitor': 'competitor',
    'competition': 'competitor',
    'uiux': 'uiux',
    'ui': 'uiux',
    'ux': 'uiux',
    'design': 'uiux',
    'psychology': 'psychology',
    'psych': 'psychology',
    'behavior': 'psychology',
    'app': 'app_dev',
    'app_dev': 'app_dev',
    'dev': 'app_dev',
    'development': 'app_dev',
    'code': 'app_dev',
    'ai': 'ai_tools',
    'ai_tools': 'ai_tools',
    'tools': 'ai_tools',
    'seo': 'seo',
    'search': 'seo',
    'market': 'market',
    'market_research': 'market',
    'industry': 'market'
}


# ============================================================================
# CLI COMMANDS
# ============================================================================

async def cmd_scrape(args):
    """Scrape single URL with Spark 1 Pro"""
    client = EnhancedFirecrawlClient()

    print(f"\n{'='*60}")
    print(f"PSYCRAWL SCRAPE - Spark 1 Pro")
    print(f"{'='*60}")
    print(f"URL: {args.url}")
    print(f"Model: {Config.FIRECRAWL_LLM_MODEL}")
    print(f"{'='*60}\n")

    formats = ['markdown']
    if args.html:
        formats.append('html')
    if args.screenshot:
        formats.append('screenshot@fullPage')

    result = await client.scrape(
        url=args.url,
        formats=formats,
        only_main_content=not args.full,
        wait_for=args.wait or 0
    )

    if result.get('success'):
        data = result.get('data', {})

        # Save output
        output_dir = Config.OUTPUT_DIR / 'scrapes'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scrape_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"SUCCESS!")
        print(f"Credits used: {result.get('creditsUsed', 1)}")
        print(f"Content length: {len(data.get('markdown', ''))} chars")
        print(f"Saved to: {output_path}")

        if args.output:
            # Also save markdown to specified file
            md_content = data.get('markdown', '')
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"Markdown saved to: {args.output}")
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        return 1

    # Show stats
    stats = client.get_stats()
    print(f"\nSession stats: {stats['total_credits_used']} credits used")
    return 0


async def cmd_crawl(args):
    """Crawl entire site"""
    client = EnhancedFirecrawlClient()

    print(f"\n{'='*60}")
    print(f"PSYCRAWL CRAWL")
    print(f"{'='*60}")
    print(f"URL: {args.url}")
    print(f"Limit: {args.limit} pages")
    print(f"{'='*60}\n")

    result = await client.crawl(
        url=args.url,
        limit=args.limit,
        max_depth=args.depth,
        scrape_options={
            'formats': ['markdown'],
            'onlyMainContent': True
        }
    )

    if result.get('success'):
        data = result.get('data', [])

        output_dir = Config.OUTPUT_DIR / 'crawls'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"crawl_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"SUCCESS!")
        print(f"Pages crawled: {len(data)}")
        print(f"Credits used: {result.get('creditsUsed', len(data))}")
        print(f"Saved to: {output_path}")
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        return 1

    return 0


async def cmd_map(args):
    """15x faster URL mapping with 100k limit"""
    client = EnhancedFirecrawlClient()

    print(f"\n{'='*60}")
    print(f"PSYCRAWL MAP - 15x Faster (v2.7)")
    print(f"{'='*60}")
    print(f"URL: {args.url}")
    print(f"Limit: {args.limit:,} URLs")
    print(f"{'='*60}\n")

    urls = await client.map_fast(
        url=args.url,
        limit=args.limit,
        search=args.search
    )

    if urls:
        output_dir = Config.OUTPUT_DIR / 'maps'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"map_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'base_url': args.url,
                'search': args.search,
                'total_urls': len(urls),
                'urls': urls
            }, f, indent=2)

        print(f"SUCCESS!")
        print(f"URLs discovered: {len(urls):,}")
        print(f"Credits used: 1")
        print(f"Saved to: {output_path}")

        if args.preview:
            print(f"\nFirst 10 URLs:")
            for url in urls[:10]:
                print(f"  - {url}")
    else:
        print("No URLs found or mapping failed")
        return 1

    return 0


async def cmd_extract(args):
    """Deep extraction with Spark 1 Pro"""
    client = EnhancedFirecrawlClient()

    print(f"\n{'='*60}")
    print(f"PSYCRAWL EXTRACT - Spark 1 Pro")
    print(f"{'='*60}")
    print(f"URL: {args.url}")
    print(f"Model: spark-1-pro")
    print(f"{'='*60}\n")

    # Load schema if provided
    schema = LEAD_SCHEMAS.get('general')
    if args.schema:
        schema_path = Path(args.schema)
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = json.load(f)

    result = await client.extract_with_pro(
        urls=[args.url],
        schema=schema,
        prompt=args.prompt
    )

    if result.get('success'):
        data = result.get('data', {})

        output_dir = Config.OUTPUT_DIR / 'extracts'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"extract_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"SUCCESS!")
        print(f"Credits used: {result.get('creditsUsed', 5)}")
        print(f"Saved to: {output_path}")
        print(f"\nExtracted data:")
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        return 1

    return 0


async def cmd_batch(args):
    """Batch processing from file"""
    client = EnhancedFirecrawlClient()

    # Load URLs from file
    urls = []
    file_path = Path(args.file)

    if file_path.suffix == '.csv':
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get('url') or row.get('URL') or row.get('website')
                if url:
                    urls.append(url)
    elif file_path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                urls = [item.get('url', item) if isinstance(item, dict) else item for item in data]
            elif isinstance(data, dict):
                urls = data.get('urls', [])
    else:
        # Assume text file with one URL per line
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("No URLs found in file")
        return 1

    print(f"\n{'='*60}")
    print(f"PSYCRAWL BATCH - {len(urls)} URLs")
    print(f"{'='*60}")
    print(f"File: {args.file}")
    print(f"Model: spark-1-pro")
    print(f"{'='*60}\n")

    def on_progress(completed, total):
        print(f"Progress: {completed}/{total} ({completed/total*100:.1f}%)")

    result = await client.batch_scrape(
        urls=urls,
        formats=['markdown'],
        only_main_content=True,
        on_progress=on_progress
    )

    if result.get('success'):
        data = result.get('data', [])

        output_dir = Config.OUTPUT_DIR / 'batches'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"batch_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\nSUCCESS!")
        print(f"URLs processed: {len(data)}")
        print(f"Credits used: {result.get('creditsUsed', len(data))}")
        print(f"Saved to: {output_path}")
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        return 1

    return 0


async def cmd_seo_audit(args):
    """Full SEO audit with DataForSEO integration"""
    client = EnhancedFirecrawlClient()

    print(f"\n{'='*60}")
    print(f"PSYCRAWL SEO AUDIT")
    print(f"{'='*60}")
    print(f"Domain: {args.domain}")
    print(f"{'='*60}\n")

    # First, map the site
    print("Step 1: Mapping site structure...")
    urls = await client.map_fast(url=f"https://{args.domain}", limit=1000)
    print(f"  Found {len(urls)} pages")

    # Crawl key pages
    print("\nStep 2: Crawling for SEO data...")
    key_pages = urls[:50]  # Top 50 pages

    results = []
    for url in tqdm(key_pages, desc="Crawling"):
        result = await client.scrape(
            url=url,
            formats=['markdown'],
            only_main_content=True
        )
        if result.get('success'):
            results.append(result.get('data', {}))

    # Save audit report
    output_dir = Config.SEO_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"seo_audit_{args.domain}_{timestamp}.json"
    output_path = output_dir / filename

    audit_report = {
        'domain': args.domain,
        'timestamp': datetime.now().isoformat(),
        'pages_found': len(urls),
        'pages_audited': len(results),
        'results': results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, indent=2, default=str)

    print(f"\nSUCCESS!")
    print(f"Pages audited: {len(results)}")
    print(f"Saved to: {output_path}")

    return 0


async def cmd_competitor(args):
    """Competitor analysis"""
    client = EnhancedFirecrawlClient()

    print(f"\n{'='*60}")
    print(f"PSYCRAWL COMPETITOR ANALYSIS")
    print(f"{'='*60}")
    print(f"Domain: {args.domain}")
    print(f"{'='*60}\n")

    schema = {
        "type": "object",
        "properties": {
            "company_name": {"type": "string"},
            "tagline": {"type": "string"},
            "services": {"type": "array", "items": {"type": "string"}},
            "pricing_info": {"type": "string"},
            "unique_selling_points": {"type": "array", "items": {"type": "string"}},
            "target_audience": {"type": "string"},
            "technologies_used": {"type": "array", "items": {"type": "string"}},
            "social_proof": {"type": "object"},
            "contact_info": {"type": "object"},
            "weaknesses": {"type": "array", "items": {"type": "string"}}
        }
    }

    result = await client.extract(
        urls=[f"https://{args.domain}/*"],
        schema=schema,
        prompt="Analyze this competitor website. Extract all business intelligence including pricing, services, unique selling points, and identify potential weaknesses.",
        model='spark-1-pro',
        allow_external_links=False
    )

    if result.get('success'):
        data = result.get('data', {})

        output_dir = Config.OUTPUT_DIR / 'competitors'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"competitor_{args.domain}_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"SUCCESS!")
        print(f"Credits used: {result.get('creditsUsed', 10)}")
        print(f"Saved to: {output_path}")
        print(f"\nCompetitor Analysis:")
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        return 1

    return 0


async def cmd_leads(args):
    """Lead generation for 360 virtual tour business"""
    client = EnhancedFirecrawlClient()

    # Resolve industry
    industry = INDUSTRY_ALIASES.get(args.industry.lower(), 'general')
    schema = LEAD_SCHEMAS.get(industry, LEAD_SCHEMAS['general'])

    print(f"\n{'='*60}")
    print(f"PSYCRAWL LEAD GENERATION")
    print(f"{'='*60}")
    print(f"Industry: {industry}")
    print(f"Region: {args.region or 'Not specified'}")
    print(f"Model: spark-1-pro (quality first)")
    print(f"{'='*60}\n")

    # Build search query
    search_query = f"{industry.replace('_', ' ')} businesses"
    if args.region:
        search_query += f" in {args.region}"

    print(f"Search query: {search_query}")

    # Search for businesses
    print("\nStep 1: Searching for businesses...")
    search_result = await client.search(
        query=search_query,
        limit=10,
        scrape_options={'formats': ['markdown']}
    )

    if not search_result.get('success'):
        print(f"Search failed: {search_result.get('error')}")
        return 1

    search_data = search_result.get('data', [])
    urls = [item.get('url') for item in search_data if item.get('url')]

    print(f"Found {len(urls)} potential leads")

    if not urls:
        print("No URLs found. Try a different query.")
        return 1

    # Extract lead data
    print("\nStep 2: Extracting lead data with Spark 1 Pro...")

    all_leads = []
    for url in tqdm(urls, desc="Extracting"):
        result = await client.extract(
            urls=[url],
            schema=schema,
            prompt=f"Extract business lead information for a 360 virtual tour sales team. Industry: {industry}. Focus on contact info, whether they have virtual tours, and potential marketing gaps.",
            model='spark-1-pro'
        )

        if result.get('success'):
            lead_data = result.get('data', {})
            lead_data['source_url'] = url
            lead_data['extraction_timestamp'] = datetime.now().isoformat()
            all_leads.append(lead_data)

    # Save leads
    output_dir = Config.LEAD_OUTPUT_DIR / industry
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"leads_{industry}_{timestamp}.json"
    output_path = output_dir / filename

    report = {
        'industry': industry,
        'region': args.region,
        'search_query': search_query,
        'timestamp': datetime.now().isoformat(),
        'total_leads': len(all_leads),
        'leads': all_leads
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    # Also save as CSV for easy viewing
    csv_path = output_dir / f"leads_{industry}_{timestamp}.csv"
    if all_leads:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_leads[0].keys())
            writer.writeheader()
            for lead in all_leads:
                # Flatten nested objects for CSV
                flat_lead = {}
                for k, v in lead.items():
                    if isinstance(v, (dict, list)):
                        flat_lead[k] = json.dumps(v)
                    else:
                        flat_lead[k] = v
                writer.writerow(flat_lead)

    print(f"\nSUCCESS!")
    print(f"Leads extracted: {len(all_leads)}")
    print(f"JSON saved to: {output_path}")
    print(f"CSV saved to: {csv_path}")

    # Show summary
    print(f"\nLead Summary:")
    for lead in all_leads:
        name = lead.get('name') or lead.get('business_name', 'Unknown')
        has_tour = lead.get('has_virtual_tour', 'Unknown')
        print(f"  - {name} (Virtual Tour: {has_tour})")

    stats = client.get_stats()
    print(f"\nTotal credits used: {stats['total_credits_used']}")

    return 0


# ============================================================================
# RESEARCH COMMANDS (Generic for any topic)
# ============================================================================

async def cmd_research(args):
    """Deep research on any topic using web search and extraction"""
    client = EnhancedFirecrawlClient()

    # Resolve research type
    research_type = RESEARCH_TYPE_ALIASES.get(args.type.lower(), 'general')
    schema = RESEARCH_SCHEMAS.get(research_type, RESEARCH_SCHEMAS['general'])

    print(f"\n{'='*60}")
    print(f"PSYCRAWL RESEARCH")
    print(f"{'='*60}")
    print(f"Topic: {args.topic}")
    print(f"Type: {research_type}")
    print(f"Depth: {args.depth} sources")
    print(f"Model: spark-1-pro")
    print(f"{'='*60}\n")

    # Step 1: Web search for sources
    print("Step 1: Searching for authoritative sources...")
    search_result = await client.search(
        query=args.topic,
        limit=10,
        scrape_options={'formats': ['markdown']}
    )

    if not search_result.get('success'):
        print(f"Search failed: {search_result.get('error')}")
        return 1

    sources = search_result.get('data', [])
    urls = [item.get('url') for item in sources if item.get('url')][:args.depth]

    print(f"Found {len(urls)} sources to analyze")

    # Step 2: Deep extraction from each source
    print("\nStep 2: Extracting insights with Spark 1 Pro...")

    all_insights = []
    for url in tqdm(urls, desc="Researching"):
        result = await client.extract(
            urls=[url],
            schema=schema,
            prompt=f"Extract key insights, best practices, and actionable information about: {args.topic}. Focus on practical, valuable knowledge.",
            model='spark-1-pro'
        )

        if result.get('success'):
            data = result.get('data', {})
            data['source_url'] = url
            data['extracted_at'] = datetime.now().isoformat()
            all_insights.append(data)

    # Step 3: Save research
    output_dir = Config.OUTPUT_DIR / 'research' / research_type
    output_dir.mkdir(parents=True, exist_ok=True)

    topic_slug = args.topic.lower().replace(' ', '_')[:30]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"research_{topic_slug}_{timestamp}.json"
    output_path = output_dir / filename

    report = {
        'topic': args.topic,
        'research_type': research_type,
        'timestamp': datetime.now().isoformat(),
        'sources_analyzed': len(all_insights),
        'insights': all_insights
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    # Also save markdown summary
    md_path = output_dir / f"research_{topic_slug}_{timestamp}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Research: {args.topic}\n\n")
        f.write(f"**Type:** {research_type}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Sources:** {len(all_insights)}\n\n")

        for i, insight in enumerate(all_insights, 1):
            f.write(f"## Source {i}\n\n")
            f.write(f"**URL:** {insight.get('source_url', 'Unknown')}\n\n")
            if insight.get('key_insights'):
                f.write("### Key Insights\n")
                for item in insight.get('key_insights', []):
                    f.write(f"- {item}\n")
            if insight.get('best_practices'):
                f.write("\n### Best Practices\n")
                for item in insight.get('best_practices', []):
                    f.write(f"- {item}\n")
            f.write("\n---\n\n")

    print(f"\nSUCCESS!")
    print(f"Sources analyzed: {len(all_insights)}")
    print(f"JSON saved to: {output_path}")
    print(f"Markdown saved to: {md_path}")

    stats = client.get_stats()
    print(f"\nCredits used: {stats['total_credits_used']}")

    return 0


async def cmd_stockpile(args):
    """Build knowledge base by deep-crawling sources on a topic"""
    client = EnhancedFirecrawlClient()

    print(f"\n{'='*60}")
    print(f"PSYCRAWL STOCKPILE - Knowledge Base Builder")
    print(f"{'='*60}")
    print(f"Topic: {args.topic}")
    print(f"Max Pages: {args.pages}")
    print(f"{'='*60}\n")

    # Step 1: Search for seed URLs
    print("Step 1: Finding authoritative sources...")
    search_result = await client.search(
        query=args.topic,
        limit=10,
        scrape_options={'formats': ['markdown']}
    )

    if not search_result.get('success'):
        print(f"Search failed: {search_result.get('error')}")
        return 1

    seed_urls = [item.get('url') for item in search_result.get('data', []) if item.get('url')]
    print(f"Found {len(seed_urls)} seed sources")

    all_content = []

    # Step 2: Deep crawl each source
    print("\nStep 2: Deep crawling sources...")
    pages_per_source = max(1, args.pages // len(seed_urls)) if seed_urls else 10

    for seed_url in seed_urls[:5]:  # Limit to 5 main sources
        print(f"\nCrawling: {seed_url}")

        # Map the site first
        urls = await client.map_fast(url=seed_url, limit=pages_per_source * 2)

        # Filter relevant URLs
        relevant_urls = [u for u in urls if any(kw in u.lower() for kw in args.topic.lower().split())][:pages_per_source]

        if not relevant_urls:
            relevant_urls = urls[:pages_per_source]

        # Scrape each page
        for url in tqdm(relevant_urls, desc="Scraping"):
            result = await client.scrape(
                url=url,
                formats=['markdown'],
                only_main_content=True
            )

            if result.get('success'):
                content = result.get('data', {})
                all_content.append({
                    'url': url,
                    'markdown': content.get('markdown', ''),
                    'metadata': content.get('metadata', {}),
                    'scraped_at': datetime.now().isoformat()
                })

    # Step 3: Save knowledge base
    output_dir = Config.OUTPUT_DIR / 'stockpile'
    output_dir.mkdir(parents=True, exist_ok=True)

    topic_slug = args.topic.lower().replace(' ', '_')[:30]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save JSON
    json_path = output_dir / f"kb_{topic_slug}_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'topic': args.topic,
            'timestamp': datetime.now().isoformat(),
            'total_pages': len(all_content),
            'pages': all_content
        }, f, indent=2, default=str)

    # Save combined markdown
    md_path = output_dir / f"kb_{topic_slug}_{timestamp}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Knowledge Base: {args.topic}\n\n")
        f.write(f"**Pages:** {len(all_content)}\n")
        f.write(f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")

        for page in all_content:
            f.write(f"## {page.get('url', 'Unknown')}\n\n")
            f.write(page.get('markdown', '')[:5000])  # Truncate very long pages
            f.write("\n\n---\n\n")

    print(f"\nSUCCESS!")
    print(f"Pages collected: {len(all_content)}")
    print(f"JSON saved to: {json_path}")
    print(f"Markdown saved to: {md_path}")

    stats = client.get_stats()
    print(f"\nCredits used: {stats['total_credits_used']}")

    return 0


async def cmd_analyze(args):
    """Deep analysis of a single URL"""
    client = EnhancedFirecrawlClient()

    # Resolve analysis type
    analysis_type = RESEARCH_TYPE_ALIASES.get(args.type.lower(), 'general') if args.type else 'general'
    schema = RESEARCH_SCHEMAS.get(analysis_type, RESEARCH_SCHEMAS['general'])

    print(f"\n{'='*60}")
    print(f"PSYCRAWL ANALYZE")
    print(f"{'='*60}")
    print(f"URL: {args.url}")
    print(f"Type: {analysis_type}")
    print(f"Model: spark-1-pro")
    print(f"{'='*60}\n")

    # For competitor analysis, use the competitor schema
    if analysis_type == 'competitor':
        prompt = f"""Analyze this as a competitor website. Extract:
- Company positioning and value proposition
- Pricing and business model
- Key features and differentiators
- Target audience
- Strengths and weaknesses
- Technology used
Be thorough and objective."""
    elif analysis_type == 'uiux':
        prompt = f"""Analyze the UI/UX of this website. Focus on:
- Design patterns and visual hierarchy
- Color scheme and typography
- Navigation and user flow
- Accessibility features
- Mobile responsiveness
- Areas for improvement"""
    elif analysis_type == 'seo':
        prompt = f"""Analyze the SEO aspects of this page:
- Title and meta tags
- Heading structure
- Content quality and keyword usage
- Internal/external links
- Technical SEO factors
- Recommendations for improvement"""
    else:
        prompt = f"""Extract comprehensive insights from this page:
- Main topic and key points
- Best practices mentioned
- Tools or resources referenced
- Actionable takeaways
- Notable quotes or statistics"""

    result = await client.extract(
        urls=[args.url],
        schema=schema,
        prompt=prompt,
        model='spark-1-pro',
        allow_external_links=False
    )

    if result.get('success'):
        data = result.get('data', {})

        output_dir = Config.OUTPUT_DIR / 'analysis' / analysis_type
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analysis_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'url': args.url,
                'type': analysis_type,
                'timestamp': datetime.now().isoformat(),
                'analysis': data
            }, f, indent=2, default=str)

        print(f"SUCCESS!")
        print(f"Credits used: {result.get('creditsUsed', 5)}")
        print(f"Saved to: {output_path}")
        print(f"\nAnalysis Results:")
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        return 1

    return 0


async def cmd_status(args):
    """Show credit usage and stats"""
    print(f"\n{'='*60}")
    print(f"PSYCRAWL STATUS")
    print(f"{'='*60}")
    print(f"\nCredit Usage:")
    print(f"  Monthly Limit: {Config.CREDITS_MONTHLY_LIMIT:,}")
    print(f"  Credits Used: {Config.CREDITS_USED:,}")
    print(f"  Credits Available: {Config.CREDITS_AVAILABLE:,}")
    print(f"  Daily Target: {Config.DAILY_CREDIT_TARGET:,}")

    print(f"\nConfiguration:")
    print(f"  LLM Model: {Config.FIRECRAWL_LLM_MODEL}")
    print(f"  Spark Pro: {Config.SPARK_PRO_ENABLED}")
    print(f"  Fast Mapping: {Config.FAST_MAPPING_ENABLED}")
    print(f"  Lead Gen: {Config.LEAD_GEN_ENABLED}")

    print(f"\nOutput Directories:")
    print(f"  Data: {Config.OUTPUT_DIR}")
    print(f"  SEO: {Config.SEO_OUTPUT_DIR}")
    print(f"  Leads: {Config.LEAD_OUTPUT_DIR}")

    print(f"\n{'='*60}")

    return 0


# ============================================================================
# SKILLS COMMANDS (Psybir Evidence Engine)
# ============================================================================

async def cmd_skills(args):
    """List or run skills"""
    if not SKILLS_AVAILABLE:
        print("Skills system not available. Check installation.")
        return 1

    if args.action == 'list':
        # List all available skills
        skills = list_skills()
        print(f"\n{'='*60}")
        print("PSYCRAWL SKILLS - Psybir Evidence Engine")
        print(f"{'='*60}\n")

        if not skills:
            print("No skills found. Check skills directory.")
            return 1

        for skill in skills:
            print(f"  /{skill.name}")
            print(f"    Version: {skill.version}")
            # Show first trigger phrase
            if skill.trigger_phrases:
                print(f"    Triggers: {', '.join(skill.trigger_phrases[:3])}")
            if skill.related_skills:
                print(f"    Related: {', '.join(skill.related_skills[:3])}")
            print()

        print(f"Total: {len(skills)} skills available")
        print(f"\nUsage:")
        print(f"  psycrawl skill run <skill-name> <url> [--geo <location>]")
        print(f"  psycrawl skill info <skill-name>")
        print(f"  psycrawl \"natural language query\"")
        print(f"{'='*60}\n")

    elif args.action == 'info':
        if not args.name:
            print("Usage: psycrawl skill info <skill-name>")
            return 1

        skill = get_skill(args.name)
        if not skill:
            print(f"Skill not found: {args.name}")
            return 1

        print(f"\n{'='*60}")
        print(f"SKILL: {skill.name}")
        print(f"{'='*60}\n")
        print(f"Version: {skill.version}")
        print(f"\nDescription:")
        print(f"  {skill.description[:500]}...")
        print(f"\nTrigger Phrases:")
        for trigger in skill.trigger_phrases[:10]:
            print(f"  - \"{trigger}\"")
        print(f"\nRelated Skills:")
        for related in skill.related_skills:
            print(f"  - /{related}")

        # Show SKILL.md content if available
        if skill.skill_path:
            skill_md = skill.skill_path / 'SKILL.md'
            if skill_md.exists():
                print(f"\n--- SKILL.md Preview ---\n")
                content = skill_md.read_text()
                # Show first 1000 chars
                print(content[:1000])
                if len(content) > 1000:
                    print("\n... (truncated)")

        print(f"\n{'='*60}\n")

    elif args.action == 'run':
        if not args.name:
            print("Usage: psycrawl skill run <skill-name> <target> [--geo <location>]")
            return 1

        skill_info = get_skill(args.name)
        if not skill_info:
            print(f"Skill not found: {args.name}")
            return 1

        if not skill_info.skill_class:
            print(f"Skill {args.name} has no executable implementation")
            return 1

        # Initialize context manager
        context_manager = get_context_manager()

        # Instantiate and run skill
        skill = skill_info.skill_class(context_manager=context_manager)

        print(f"\n{'='*60}")
        print(f"RUNNING SKILL: {skill.name}")
        print(f"{'='*60}")
        print(f"Target: {args.target or 'None'}")
        print(f"Location: {args.geo or 'Default'}")
        print(f"{'='*60}\n")

        try:
            result = await skill.run(
                target=args.target,
                geo=args.geo,
                focus=args.focus,
            )

            # Print summary
            print_summary(result)

            # Save report
            output_dir = Config.OUTPUT_DIR / 'skills' / skill.name
            report_path = save_report(result, output_dir, format='markdown')
            print(f"Report saved: {report_path}")

            # Also save JSON
            json_path = save_report(result, output_dir, format='json')
            print(f"JSON saved: {json_path}")

            # Cache result for reuse
            if args.target:
                await context_manager.cache_result(skill.name, args.target, result.to_dict())
                await context_manager.record_analysis(skill.name, str(report_path), {
                    'target': args.target,
                    'geo': args.geo,
                })

        except Exception as e:
            print(f"Skill execution failed: {e}")
            logger.exception("Skill error")
            return 1

    else:
        print("Usage: psycrawl skill <list|info|run> [args]")
        return 1

    return 0


async def cmd_nlp(args):
    """Route natural language query to appropriate skill"""
    if not SKILLS_AVAILABLE:
        print("Skills system not available.")
        return 1

    query = args.query
    router = get_router()
    result = router.route(query)

    if not result.matched:
        print(f"No skill matched query: {query}")
        print("\nSuggestions:")
        suggestions = router.suggest_skills(query)
        for skill, confidence in suggestions:
            print(f"  /{skill.name} ({confidence:.0%} confidence)")
        return 1

    print(f"\n{'='*60}")
    print(f"ROUTED TO: {result.skill_info.name}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Extracted: {result.extracted_entities}")
    print(f"{'='*60}\n")

    # Run the skill
    skill_info = result.skill_info
    if not skill_info.skill_class:
        print(f"Skill {skill_info.name} has no executable implementation")
        return 1

    context_manager = get_context_manager()
    skill = skill_info.skill_class(context_manager=context_manager)

    try:
        skill_result = await skill.run(
            target=result.extracted_entities.get('url'),
            geo=result.extracted_entities.get('location'),
            focus=result.extracted_entities.get('focus'),
        )

        print_summary(skill_result)

        # Save report
        output_dir = Config.OUTPUT_DIR / 'skills' / skill.name
        report_path = save_report(skill_result, output_dir, format='markdown')
        print(f"Report saved: {report_path}")

    except Exception as e:
        print(f"Skill execution failed: {e}")
        return 1

    return 0


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='psycrawl',
        description='PsyCrawl - Intelligent Web Research & Data Extraction System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CORE EXAMPLES:
  psycrawl scrape https://example.com
  psycrawl map https://example.com --limit 10000
  psycrawl crawl https://example.com --limit 50

RESEARCH EXAMPLES:
  psycrawl research "react best practices" --type dev --depth 5
  psycrawl stockpile "ui design patterns" --pages 50
  psycrawl analyze https://competitor.com --type competitor
  psycrawl analyze https://example.com --type uiux

BUSINESS INTELLIGENCE:
  psycrawl seo-audit example.com
  psycrawl competitor competitor.com
  psycrawl leads wineries --region "Lehigh Valley PA"

Available research types: general, competitor, uiux, psychology, app_dev, ai_tools, seo, market
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape single URL')
    scrape_parser.add_argument('url', help='URL to scrape')
    scrape_parser.add_argument('--html', action='store_true', help='Include HTML output')
    scrape_parser.add_argument('--screenshot', action='store_true', help='Take screenshot')
    scrape_parser.add_argument('--full', action='store_true', help='Include full page content')
    scrape_parser.add_argument('--wait', type=int, help='Wait time in ms before scraping')
    scrape_parser.add_argument('--output', '-o', help='Output file for markdown')

    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Crawl entire site')
    crawl_parser.add_argument('url', help='Base URL to crawl')
    crawl_parser.add_argument('--limit', type=int, default=100, help='Max pages to crawl')
    crawl_parser.add_argument('--depth', type=int, help='Max crawl depth')

    # Map command
    map_parser = subparsers.add_parser('map', help='15x faster URL discovery')
    map_parser.add_argument('url', help='Base URL to map')
    map_parser.add_argument('--limit', type=int, default=100000, help='Max URLs (up to 100k)')
    map_parser.add_argument('--search', help='Keyword filter')
    map_parser.add_argument('--preview', action='store_true', help='Show first 10 URLs')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Deep extraction with Spark 1 Pro')
    extract_parser.add_argument('url', help='URL to extract from')
    extract_parser.add_argument('--schema', help='Path to JSON schema file')
    extract_parser.add_argument('--prompt', help='Extraction prompt')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process from file')
    batch_parser.add_argument('file', help='CSV/JSON/TXT file with URLs')

    # SEO Audit command
    seo_parser = subparsers.add_parser('seo-audit', help='Full SEO audit')
    seo_parser.add_argument('domain', help='Domain to audit')

    # Competitor command
    competitor_parser = subparsers.add_parser('competitor', help='Competitor analysis')
    competitor_parser.add_argument('domain', help='Competitor domain')

    # Leads command
    leads_parser = subparsers.add_parser('leads', help='Lead generation')
    leads_parser.add_argument('industry', help='Industry (wineries, auto, senior, wedding, fitness, medical)')
    leads_parser.add_argument('--region', help='Geographic region')
    leads_parser.add_argument('--deep', action='store_true', help='Deep extraction mode')

    # Research command (NEW - Generic research)
    research_parser = subparsers.add_parser('research', help='Deep research on any topic')
    research_parser.add_argument('topic', help='Topic to research')
    research_parser.add_argument('--type', default='general',
        help='Research type: general, competitor, uiux, psychology, app_dev, ai_tools, seo, market')
    research_parser.add_argument('--depth', type=int, default=5, help='Number of sources to analyze')

    # Stockpile command (NEW - Knowledge base builder)
    stockpile_parser = subparsers.add_parser('stockpile', help='Build knowledge base on a topic')
    stockpile_parser.add_argument('topic', help='Topic to stockpile knowledge on')
    stockpile_parser.add_argument('--pages', type=int, default=25, help='Max pages to collect')

    # Analyze command (NEW - Single URL deep analysis)
    analyze_parser = subparsers.add_parser('analyze', help='Deep analysis of a single URL')
    analyze_parser.add_argument('url', help='URL to analyze')
    analyze_parser.add_argument('--type', default='general',
        help='Analysis type: general, competitor, uiux, psychology, app_dev, ai_tools, seo, market')

    # Status command
    subparsers.add_parser('status', help='Show credit usage and stats')

    # Skill command (NEW - Psybir Evidence Engine)
    skill_parser = subparsers.add_parser('skill', help='Run skills (Psybir Evidence Engine)')
    skill_parser.add_argument('action', choices=['list', 'info', 'run'],
        help='Action: list, info <name>, or run <name> <target>')
    skill_parser.add_argument('name', nargs='?', help='Skill name')
    skill_parser.add_argument('target', nargs='?', help='Target URL or identifier')
    skill_parser.add_argument('--geo', help='Geographic location/market')
    skill_parser.add_argument('--focus', default='comprehensive',
        help='Analysis focus: comprehensive, positioning, pricing, local_presence, features')

    # NLP command (NEW - Natural language skill routing)
    nlp_parser = subparsers.add_parser('nlp', help='Route natural language to skills')
    nlp_parser.add_argument('query', help='Natural language query')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to command
    commands = {
        # Core commands
        'scrape': cmd_scrape,
        'crawl': cmd_crawl,
        'map': cmd_map,
        'extract': cmd_extract,
        'batch': cmd_batch,
        # Research commands
        'research': cmd_research,
        'stockpile': cmd_stockpile,
        'analyze': cmd_analyze,
        # Business intelligence
        'seo-audit': cmd_seo_audit,
        'competitor': cmd_competitor,
        'leads': cmd_leads,
        # Utilities
        'status': cmd_status,
        # Skills (Psybir Evidence Engine)
        'skill': cmd_skills,
        'nlp': cmd_nlp,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        return asyncio.run(cmd_func(args))
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
